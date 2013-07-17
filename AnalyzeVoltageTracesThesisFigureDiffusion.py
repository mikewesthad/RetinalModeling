import os
import matplotlib.pyplot as plt
from random import randint 
import numpy as np
import matplotlib
import matplotlib.image as mpimg

def createFigure(long_side_size, rows, cols):
    width, height = long_side_size, long_side_size
    if rows > cols:
        width *= float(cols)/float(rows)
    elif cols > rows:
        height *= float(rows)/float(cols)
    return plt.figure(figsize=(width, height))


def selectDistalCompartment(display, starburst, scale, background_color, morphology_color, highlight_color):
    running = True
    selected = None
    while running:
        display.fill(background_color)     
        for compartment in starburst.compartments:
            if compartment.index == selected:
                compartment.draw(display, color=highlight_color, scale=scale)
            else:
                compartment.draw(display, color=morphology_color, scale=scale)
        

        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                x, y = event.pos
                pos = Vector2D(float(x), float(y))
                selected = findNearestCompartment(pos, starburst, scale)
            elif event.type == MOUSEBUTTONDOWN:
                distal = selected
                proximal, intermediate = findProximalAndIntermediateAlongPath(starburst, starburst.compartments[distal])
                return proximal, intermediate, distal
        
        pygame.display.flip()
    
def findNearestCompartment(pos, starburst, scale):
    min_dist = 10000000.0
    min_comp = None
    for compartment in starburst.compartments:
        loc_a = (compartment.neuron.location + compartment.line_points[0]) * scale
        loc_b = (compartment.neuron.location + compartment.line_points[1]) * scale
        loc = (loc_a + loc_b) / 2.0
        dist = loc.distanceTo(pos)
        if dist < min_dist:
            min_comp = compartment.index
            min_dist = dist
    return min_comp
  
    
def findProximalAndIntermediateAlongPath(starburst, distal):
    dendrite_path = [distal]
    has_reached_soma = False
    while not(has_reached_soma):
        most_proximal_compartment = dendrite_path[0]
        proximal_neighbors = most_proximal_compartment.proximal_neighbors
        
        new_proximal_compartment = proximal_neighbors[0]
        dendrite_path.insert(0, new_proximal_compartment)
        
        if new_proximal_compartment in starburst.morphology.master_compartments:
            has_reached_soma = True
        
    number_compartments = len(dendrite_path)
    proximal = dendrite_path[0]
    interm   = dendrite_path[int(round(number_compartments/2.0))]
    
    return proximal.index, interm.index            
    

def calculateData(retina_paths, number_stimulus_variations, number_bars):
    number_retinas  = len(retina_paths)
    number_trials   = number_retinas * number_stimulus_variations
    headings        = np.arange(0.0, 360.0, 360.0/number_bars)
    trial_max_timesteps = []
    trial_voltage_traces = []
        
    # Display variables
    pygame.init()    
    max_size = Vector2D(1000.0, 1000.0)  
    background_color = (25, 25, 25)
    morphology_color = (255, 255, 255)
    highlight_color = (255, 0, 0)
    
    retina_name = 0
    for retina_path in retina_paths:
        retina = Retina.loadRetina(retina_path)
        
        starburst = retina.on_starburst_layer.neurons[0]
        number_compartments = starburst.number_compartments
        number_headings = len(headings)
                
         # Create a (scaled) pygame display     
        width_scale = max_size.x / float(retina.grid_width)
        height_scale = max_size.y / float(retina.grid_height)
        scale = min(width_scale, height_scale)   
        starburst.morphology.location = max_size/scale/2.0
        display = pygame.display.set_mode(max_size.toIntTuple())
        
        proximal, intermediate, distal = selectDistalCompartment(display, starburst, scale, background_color, morphology_color, highlight_color)
        
        # Draw the morphology with the selected compartments highlighted
        display.fill(background_color)     
        for compartment in starburst.compartments:
            if compartment.index in [distal]:#[proximal, intermediate, distal]:
                compartment.draw(display, color=highlight_color, scale=scale)
            else:
                compartment.draw(display, color=morphology_color, scale=scale)
        morphology_path = os.path.join(retina_path, "Selected Morphology.jpg")
        pygame.image.save(display, morphology_path)
        
        retina_name += 1
        
        for trial_number in range(number_stimulus_variations):
            
            stored_activities = []
            max_timesteps = 0     
            for heading in headings:
                # Load the retina with activities from one of the headings
                trial_name = str(trial_number) +"_"+ str(int(heading))
                retina.loadActivities(retina_path, trial_name)
                
                # Pull the starburst activity for this particular trial and store it
                activities = retina.on_starburst_activities
                timesteps = len(activities)
                max_timesteps = max(max_timesteps, timesteps)
                stored_activities.append(activities)
                
            # For graphing purposes, it is easier if everything is stored in a giant
            # numpy array.  Since not every run had the same number of timesteps, we
            # must pad with zeros when appropriate
            all_activities = np.zeros((number_headings, max_timesteps, number_compartments))
            
            for heading_index in range(number_headings):
                activities = stored_activities[heading_index]
                timesteps = len(activities)
                all_activities[heading_index, :timesteps, :] = activities[:, 0, 0, :]
                           
            voltage_traces = []
            directions = [0.0, 90.0, 180.0, 270.0]
            heading_indices = [int(d/(360.0/number_bars)) for d in directions]  
            for compartment_index in [proximal, intermediate, distal]:
                compartment_traces = []
                for heading_index in heading_indices:
                    trace = all_activities[heading_index, :, compartment_index]
                    compartment_traces.append(trace)
                voltage_traces.append(compartment_traces)
            trial_voltage_traces.append(voltage_traces)   
            
            trial_max_timesteps.append(max_timesteps)
            
            
    return trial_voltage_traces, trial_max_timesteps
                
    

def analyze(trial_path, retina_paths, number_stimulus_variations, parameter, selected_variations, number_bars=12):
            
    voltage_traces, max_timesteps = calculateData(retina_paths, number_stimulus_variations, number_bars) 
    
    number_retinas  = len(retina_paths)
    number_trials = number_retinas * len(selected_variations)

    
    plot_label_props    = dict(boxstyle='round', facecolor='white', alpha=1.0)
    plot_label_x        = 0.05
    plot_label_y        = 0.95
    plot_label_size     = 20
    
    x_tick_size         = 12
    x_label_size        = 16
    y_label_size        = 16
    y_tick_size         = 12
    title_size          = 20
        
    matplotlib.rcParams['xtick.major.pad'] = 8
    matplotlib.rcParams['ytick.major.pad'] = 8
    for retina_number in range(number_retinas):
                
        fig1_rows, fig1_cols, fig1_index = 3, 3, 1
        fig1 = createFigure(15.0, fig1_rows, fig1_cols)   
        
        morphology_path = os.path.join(retina_paths[retina_number], "Selected Morphology.jpg")
        morphology_image = mpimg.imread(morphology_path)
        morphology_image = morphology_image[100:900, 100:900]
        
        fig1_index = 1
        ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
        ax.imshow(morphology_image)
        ax.axis('off')
        plt.text(plot_label_x, plot_label_y, "A", transform=ax.transAxes, 
                 fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
             
        fig1_index += 1
        
                 
        for ((value, stimulus_number), fig1_index, fig_letter) in zip(selected_variations, (4, 5, 6, 7, 8, 9), ("C", "D", "E", "F", "G", "H")):
            
            index = retina_number * number_stimulus_variations + stimulus_number
            
            timesteps = max_timesteps[index]            
            
            # Figure 3 - Voltage Traces     
            directions = [0.0, 90.0, 180.0, 270.0]
            labels = [str(int(d)) for d in directions]
            linestyles = ['-', '--', '-', '--']
            colors = ['r', 'g', 'b', 'm']
            
            for (compartment_index, compartment_name) in zip([2], ["Distal"]):
                ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
                handles = []
                for (heading_index, label, ls, c) in zip(range(4), labels, linestyles, colors):
                    y_axis = voltage_traces[index][compartment_index][heading_index]
                    h,  = ax.plot(range(len(y_axis)), y_axis, c=c, ls=ls, label=label)
                    handles.append(h)
                    textstr = "{0} = {1} um".format(parameter, value)
                    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
                    
                    if fig1_index > 6:      
                        ax.text(0.2, 0.95, textstr, transform=ax.transAxes, fontsize=16,
                                verticalalignment='top', bbox=props)
                    else:
                        ax.text(0.25, 0.95, textstr, transform=ax.transAxes, fontsize=16,
                                verticalalignment='top', bbox=props)
                                
                    ax.set_xlim([0, timesteps])
                    max_activity = np.max(y_axis)
                    time_of_max = np.argmax(y_axis)
                    ax.axhline(max_activity, xmin=0, xmax=time_of_max/float(len(y_axis)), ls=ls, c=c)
#                ax.set_title(compartment_name)
                ax.set_ylabel("Activity", size=y_label_size)    
                ax.set_xlabel("Timesteps", size=x_label_size)
                ax.set_ylim([0, 1])
                ax.set_xticklabels(ax.get_xticks(), size=x_tick_size)
                ax.set_yticklabels(ax.get_yticks(), size=y_tick_size)
            plt.text(plot_label_x, plot_label_y, fig_letter, transform=ax.transAxes, 
                     fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
             
        
        fig1_index = 3
        ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
        ax.axis('off')
        row_names = ["Conductance Factor",
                     "Decay Rate", 
                     "Wirelength (um)",
                     "Step Size (um)",
                     "Heading Deviation (deg)",
                     "Child Deviation (deg)",
                     "Branching Length (um)"]
        cell_values = [["0.5"], ["0.1"], ["150"], ["15"], ["10"], ["20"], ["35"]]                    
        
        plt.table(cellText=cell_values, rowLabels=row_names, bbox=(0.65,0.45,0.22,0.4), colWidths=[0.2])
        leg = ax.legend(handles, labels, loc='lower center', fontsize=18)
        leg.legendHandles[0].set_linewidth(2.5)
        plt.text(plot_label_x, plot_label_y, "B", transform=ax.transAxes, 
                 fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
            
        fig1.tight_layout()
        fig1_path = os.path.join(trial_path, str(retina_number), "Voltage Trace Results.jpg")
        fig1.savefig(fig1_path)    
  
        
    
from Constants import *
trial_name = "Bar_Diffusion_Batch_Large_Same_Morphology"
number_bars = 12
number_stimulus_variations = 42

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
entries = os.listdir(trial_path)
retina_paths = []
for entry in entries:
    path_to_entry = os.path.join(trial_path, entry)
    if os.path.isdir(path_to_entry):
        retina_paths.append(path_to_entry)

selected_variations = [[10, 1+0], [40, 1+2*1], [70, 1+2*2], [100, 1+2*3], [220, 1+2*7], [400, 1+2*13]]

parameter = "Diffusion Radius"
analyze(trial_path, retina_paths, number_stimulus_variations, parameter, selected_variations, number_bars)