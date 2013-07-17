import os
import matplotlib.pyplot as plt
from random import randint 
import numpy as np
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

def analyzeStarburstWithinRetians(retina_paths):
    
    pygame.init()    
    max_size = Vector2D(1000.0, 1000.0)       
    width_scale = max_size.x / 400.0
    height_scale = max_size.y / 400.0
    scale = min(width_scale, height_scale)
    display = pygame.display.set_mode(max_size.toIntTuple())
    
    background_color = (25, 25, 25)
    morphology_color = (255, 255, 255)
    selected_morphology_color = (255, 0, 0)
    
    for retina_path in retina_paths:
        retina = Retina.loadRetina(retina_path)
        retina_name = retina_path   
        
        entries = os.listdir(retina_name)
        number_trials = 0
        for entry in entries:
            if entry.split(".")[-1] == "npz":
                number_trials += 1
        number_trials /= 2
        
        rows, cols, index = number_trials, 3, 1
        fig = createFigure(20.0, rows, cols)
        
        starburst = retina.on_starburst_layer.neurons[0]        
        starburst.morphology.location = max_size/scale/2.0
        
        p, i, d = selectDistalCompartment(display, starburst, scale, background_color, morphology_color, selected_morphology_color)
        display.fill(background_color)
        for compartment in starburst.compartments:
            if compartment.index in [p, i, d]: 
                compartment.draw(display, color=selected_morphology_color, scale=scale)
            else:
                compartment.draw(display, color=morphology_color, scale=scale)
        save_path = os.path.join(retina_name, "Highlighted Morphology.jpg")
        pygame.image.save(display, save_path)
        
        cp_maxes    = np.zeros((3,number_trials))
        cf_maxes    = np.zeros((3,number_trials))
        
        for trial_number in range(number_trials):
            retina.loadActivities(retina_name, str(trial_number)+"_centripetal")
            cp_activities = retina.on_starburst_activities[:, 0, 0, :]        
            retina.loadActivities(retina_name, str(trial_number)+"_centrifugal")
            cf_activities = retina.on_starburst_activities[:, 0, 0, :]
            
            timesteps = len(cp_activities)
            x_axis = range(timesteps)
            
            for (c_index, compartment) in zip(range(3), [p,i,d]):
                cp_maxes[c_index, trial_number]   = max([a[compartment] for a in cp_activities])
                cf_maxes[c_index, trial_number]   = max([a[compartment] for a in cf_activities])
            
            for (compartment, compartment_name) in zip([p, i, d], ["Proximal", "Intermediate", "Distal"]):
                ax = fig.add_subplot(rows, cols, index)
                y_axis = [a[compartment] for a in cf_activities]
                cf_max = max(y_axis)
                cf_line, = ax.plot(x_axis, y_axis, linewidth=2, color='r')
                y_axis = [a[compartment] for a in cp_activities]
                cp_max = max(y_axis)
                cp_line, = ax.plot(x_axis, y_axis, linewidth=2, color='b')
                DSI = (cf_max - cp_max)/(cf_max + cp_max)
                ax.set_title("{0}, DSI {1:.3}".format(compartment_name, round(DSI,3)))
                ax.set_xlabel("Timesteps")
                ax.set_ylabel("Activity")
                ax.set_ylim([0.0, 1.0])
                index += 1
        
        fig.legend((cf_line, cp_line), ('Outward', 'Inward'), loc=(.075,.675), prop={'size':16})
        fig.tight_layout()
        save_path = os.path.join(retina_name, "Activity Traces.jpg")
        fig.savefig(save_path)
        
        
def analyzeStarburstOneTrial(retina_paths):
    import matplotlib as mpl

    mpl.rcParams['xtick.major.pad'] = 10
    mpl.rcParams['ytick.major.pad'] = 10
    
    plot_label_props    = dict(boxstyle='round', facecolor='white', alpha=1.0)
    plot_label_x        = 0.05
    plot_label_y        = 0.95
    plot_label_size     = 20
    
    x_tick_size         = 12
    x_label_size        = 16
    y_label_size        = 16
    y_tick_size         = 12
    title_size          = 20
    
    pygame.init()    
    max_size = Vector2D(1000.0, 1000.0)       
    width_scale = max_size.x / 400.0
    height_scale = max_size.y / 400.0
    scale = min(width_scale, height_scale)
    display = pygame.display.set_mode(max_size.toIntTuple())
    
    background_color = (25, 25, 25)
    morphology_color = (255, 255, 255)
    selected_morphology_color = (255, 0, 0)
    
    for retina_path in retina_paths:
        retina = Retina.loadRetina(retina_path)
        retina_name = retina_path   
                
        rows, cols = 3, 2
        fig = createFigure(17.0, rows, cols)
        grid_size = (rows, cols)
        
        starburst = retina.on_starburst_layer.neurons[0]        
        starburst.morphology.location = max_size/scale/2.0
        
        proximal_color      = (0, 134, 52)
        distal_color        = (255, 25, 25)
        p, i, d = selectDistalCompartment(display, starburst, scale, background_color, morphology_color, selected_morphology_color)
        display.fill(background_color)
        for compartment in starburst.compartments:
            if compartment.index == p: 
                compartment.draw(display, color=proximal_color, scale=scale)
            elif compartment.index == d:
                compartment.draw(display, color=distal_color, scale=scale)                
            else:
                compartment.draw(display, color=morphology_color, scale=scale)
        save_path = os.path.join(retina_name, "Highlighted Morphology.jpg")
        pygame.image.save(display, save_path)
        
            
        morphology_path  = save_path
        morphology_image = mpimg.imread(morphology_path)
        morphology_image = morphology_image[100:900, 100:900]
        ax = plt.subplot2grid(grid_size, (0,0), colspan=2, rowspan=2)
        ax.imshow(morphology_image)
        ax.set_title("Morphology With Proximal and Distal Compartments Hightlighted", size=title_size)
        ax.axis('off') 
        plt.text(plot_label_x, plot_label_y, "A", transform=ax.transAxes, 
                 fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
        
        trial_number = 0
        retina.loadActivities(retina_name, str(trial_number)+"_centripetal")
        cp_activities = retina.on_starburst_activities[:, 0, 0, :]        
        retina.loadActivities(retina_name, str(trial_number)+"_centrifugal")
        cf_activities = retina.on_starburst_activities[:, 0, 0, :]
            
        timesteps = len(cp_activities)
        half_time = int(timesteps/2)
        x_axis = range(timesteps)
            
        ax = plt.subplot2grid(grid_size, (2,0))  
        y_axis = [a[p] for a in cf_activities]     
        cf_max = max(y_axis[half_time:])
        cf_line, = ax.plot(x_axis, y_axis, linewidth=2, color='r')  
        y_axis = [a[p] for a in cp_activities]   
        cp_max = max(y_axis[half_time:])
        cp_line, = ax.plot(x_axis, y_axis, linewidth=2, color='b')
        DP = (cf_max - cp_max)/(cf_max + cp_max)
        ax.set_title("{0}, DP {1:.3}".format("Proximal", round(DP,3)), size=title_size)
        ax.set_xlabel("Timesteps", size=x_label_size)
        ax.set_ylabel("Activity", size=y_label_size)
        ax.set_ylim([0.0, 1.0])
        ax.set_xticklabels(ax.get_xticks(), size=x_tick_size)
        ax.set_yticklabels(ax.get_yticks(), size=y_tick_size)
        ax.legend((cf_line, cp_line), ('Outward', 'Inward'), loc=1, fontsize=24)
        
        plt.text(plot_label_x, plot_label_y, "B", transform=ax.transAxes, 
                 fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
        
        ax = plt.subplot2grid(grid_size, (2,1))  
        y_axis = [a[d] for a in cf_activities]     
        cf_max = max(y_axis[half_time:])
        cf_line, = ax.plot(x_axis, y_axis, linewidth=2, color='r')  
        y_axis = [a[d] for a in cp_activities]   
        cp_max = max(y_axis[half_time:])
        cp_line, = ax.plot(x_axis, y_axis, linewidth=2, color='b')
        DP = (cf_max - cp_max)/(cf_max + cp_max)
        ax.set_title("{0}, DP {1:.3}".format("Distal", round(DP,3)), size=title_size)
        ax.set_xlabel("Timesteps", size=x_label_size)
        ax.set_ylabel("Activity", size=y_label_size)
        ax.set_ylim([0.0, 1.0])
        fig.tight_layout()
        save_path = os.path.join(retina_name, "Activity Traces.jpg")
        ax.set_xticklabels(ax.get_xticks(), size=x_tick_size)
        ax.set_yticklabels(ax.get_yticks(), size=y_tick_size)
        plt.text(plot_label_x, plot_label_y, "C", transform=ax.transAxes, 
                 fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
        fig.savefig(save_path)        
    
from Constants import *
trial_name = "Annuli_Test_Batch_6"

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
entries = os.listdir(trial_path)
retina_paths = []
for entry in entries:
    path_to_entry = os.path.join(trial_path, entry)
    if os.path.isdir(path_to_entry):
        retina_paths.append(path_to_entry)

analyzeStarburstOneTrial(retina_paths)