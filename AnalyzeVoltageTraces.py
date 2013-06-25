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
                
    

def analyze(trial_path, retina_paths, number_stimulus_variations, parameter, values, number_bars=12):
            
    voltage_traces, max_timesteps = calculateData(retina_paths, number_stimulus_variations, number_bars) 
    
    number_retinas  = len(retina_paths)
    number_trials = number_retinas * number_stimulus_variations

    for retina_number in range(number_retinas):
                
        fig1_rows, fig1_cols, fig1_index = number_trials, 3, 1
        fig1 = createFigure(4.0*number_trials, fig1_rows, fig1_cols)   
        
        for (stimulus_number, value) in zip(range(number_stimulus_variations), values):
            
            index = retina_number * number_stimulus_variations + stimulus_number
            
            timesteps = max_timesteps[index]            
            
            # Figure 3 - Voltage Traces     
            directions = [0.0, 90.0, 180.0, 270.0]
            labels = [str(int(d)) for d in directions]
            linestyles = ['-', '--', '-', '--']
            colors = ['r', 'g', 'b', 'm']
            
            for (compartment_index, compartment_name) in zip([0,1,2], ["Proximal", "Intermediate", "Distal"]):
                ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
                handles = []
                for (heading_index, label, ls, c) in zip(range(4), labels, linestyles, colors):
                    y_axis = voltage_traces[index][compartment_index][heading_index]
                    h,  = ax.plot(range(len(y_axis)), y_axis, c=c, ls=ls, label=label)
                    handles.append(h)
                    textstr = "{0} = {1}".format(parameter, value)
                    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
                    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=18,
                            verticalalignment='top', bbox=props)
                    ax.set_xlim([0, timesteps])
                    max_activity = np.max(y_axis)
                    time_of_max = np.argmax(y_axis)
                    ax.axhline(max_activity, xmin=0, xmax=time_of_max/float(len(y_axis)), ls=ls, c=c)
                ax.set_title(compartment_name)
                ax.set_ylabel("Activity")
                ax.set_xlabel("Timesteps")
                ax.set_ylim([0, 1])
                
                fig1_index += 1
             
        
#        fig1.legend(handles, labels, bbox_to_anchor=(3.0/12.0, 1.0/7.0), loc='center', fontsize=20)
            
        fig1.tight_layout()
        fig1_path = os.path.join(trial_path, str(retina_number), "Voltage Trace Results.jpg")
        fig1.savefig(fig1_path)    
  
        
    
from Constants import *
trial_name = "Bar_Conductance_Wide_Bar"
number_bars = 12
number_stimulus_variations = 10

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
entries = os.listdir(trial_path)
retina_paths = []
for entry in entries:
    path_to_entry = os.path.join(trial_path, entry)
    if os.path.isdir(path_to_entry):
        retina_paths.append(path_to_entry)

#retina_paths = []
#for x in range(2):
#    path_to_entry = os.path.join(trial_path, str(x))
#    retina_paths.append(path_to_entry)

#selected_variations = [(float(x/10.0), x-1) for x in range(1,11,1)]

parameter = "Conductance"
values = [x/10.0 for x in range(1, 11, 1)]
analyze(trial_path, retina_paths, number_stimulus_variations, parameter, values, number_bars)