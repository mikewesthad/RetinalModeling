import os
import matplotlib.pyplot as plt
from random import randint 
import numpy as np
import matplotlib

def createFigure(long_side_size, rows, cols):
    width, height = long_side_size, long_side_size
    if rows > cols:
        width *= float(cols)/float(rows)
    elif cols > rows:
        height *= float(rows)/float(cols)
    return plt.figure(figsize=(width, height))
    

def analyze(trial_path, retina_paths, number_stimulus_variations, number_bars):
    number_retinas  = len(retina_paths)
    number_trials   = number_retinas * number_stimulus_variations
    fig3_rows, fig3_cols, fig3_index = number_trials, 3, 1
    fig3 = createFigure(20.0*number_trials/4.0, fig3_rows, fig3_cols)
    matplotlib.rc('xtick', labelsize=12)
    matplotlib.rc('ytick', labelsize=12)

    headings = np.arange(0.0, 360.0, 360.0/number_bars)
    
    for retina_path in retina_paths:
        retina = Retina.loadRetina(retina_path)
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
            starburst = retina.on_starburst_layer.neurons[0]
            number_compartments = starburst.number_compartments
            number_headings = len(headings)
            all_activities = np.zeros((number_headings, max_timesteps, number_compartments))
            
            for heading_index in range(number_headings):
                activities = stored_activities[heading_index]
                timesteps = len(activities)
                all_activities[heading_index, :timesteps, :] = activities[:, 0, 0, :]            
            
            # Figure 3 - Voltage Traces
            p, i, d = selectStarburstCompartmentsAlongDendrite(retina, 0)
            x_axis = range(max_timesteps)            
            directions = [0.0, 90.0, 180.0, 270.0]
            heading_indices = [int(direction/(360.0/number_bars)) for direction in directions]  
            print headings
            print heading_indices
            labels = [str(int(direction)) for direction in directions]
            linestyles = ['-', '--', '--', '-']
            colors = ['r', 'g', 'm', 'b']
            
            for (compartment_index, compartment_name) in zip([p, i, d], ("Proximal", "Intermediate", "Distal")):
                ax = fig3.add_subplot(fig3_rows, fig3_cols, fig3_index)
                for heading_index in range(number_headings):
                    y_axis = all_activities[heading_index, :, compartment_index]
                    ax.plot(x_axis, y_axis, label=str(int(headings[heading_index])))
#                    ax.axhline(max(y_axis), xmin=0, xmax=0.25, ls=ls, c=c)
                ax.set_title(compartment_name)
                ax.set_ylabel("Activity")
                ax.set_xlabel("Timesteps")
                ax.set_ylim([0, 1])
                ax.legend(loc=1)
                fig3_index += 1
                
    fig3.tight_layout()
    fig3_path = os.path.join(trial_path, "Voltage Trace Results.jpg")
    fig3.savefig(fig3_path)
    
    
def selectStarburstCompartmentsAlongDendrite(retina, angle):
    starburst = retina.on_starburst_layer.neurons[0]
    
    acceptable_deviation = 10
    min_angle = angle - acceptable_deviation
    max_angle = angle + acceptable_deviation
    if max_angle > 360: max_angle -= 360
    if min_angle < 0: min_angle = 360 + min_angle    
        
    starburst_center = Vector2D()
       
    acceptable_compartment = False
    number_tries = 0
    max_tries = 1000
    while not(acceptable_compartment):        
        random_compartment_index = randint(0, starburst.number_compartments-1)
        random_compartment = starburst.compartments[random_compartment_index]
        
        # Check if terminal compartment        
        if random_compartment.distal_neighbors == []:
            
            # Check angle heading
            terminal_point = random_compartment.line_points[-1]
            compartment_heading = starburst_center.angleHeadingTo(terminal_point)
            is_angle_acceptable = False            
            
            if max_angle < min_angle:
                is_angle_acceptable = compartment_heading <= max_angle or compartment_heading >= min_angle
            else:
                is_angle_acceptable = compartment_heading <= max_angle and compartment_heading >= min_angle
                
            if is_angle_acceptable:
                terminal_compartment = random_compartment
                acceptable_compartment = True
        
        number_tries += 1
        if number_tries > max_tries:
            print "Increased acceptable deviation", acceptable_deviation
            number_tries = 0
            acceptable_deviation += 10
            min_angle = angle - acceptable_deviation
            max_angle = angle + acceptable_deviation
            if max_angle > 360: max_angle -= 360
            if min_angle < 0: min_angle = 360 + min_angle
            
    dendrite_path = [terminal_compartment]
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
    distal   = dendrite_path[-1]
    
    return proximal.index, interm.index, distal.index                 
    
        
    
from Constants import *
trial_name = "Bar_Batch_1"
number_bars = 8
number_stimulus_variations = 1

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
#entries = os.listdir(trial_path)
#retina_paths = []
#for entry in entries:
#    path_to_entry = os.path.join(trial_path, entry)
#    if os.path.isdir(path_to_entry):
#        retina_paths.append(path_to_entry)

retina_paths = []
for x in range(4):
    path_to_entry = os.path.join(trial_path, str(x))
    retina_paths.append(path_to_entry)
    

analyze(trial_path, retina_paths, number_stimulus_variations, number_bars)