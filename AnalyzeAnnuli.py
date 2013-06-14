import os
import matplotlib.pyplot as plt
from random import randint 
import numpy as np

def createFigure(long_side_size, rows, cols):
    width, height = long_side_size, long_side_size
    if rows > cols:
        width *= float(cols)/float(rows)
    elif cols > rows:
        height *= float(rows)/float(cols)
    return plt.figure(figsize=(width, height))
    

def analyzeStarburst(retina, retina_name):
    
    entries = os.listdir(retina_name)
    number_trials = 0
    for entry in entries:
        if entry.split(".")[-1] == "npz":
            number_trials += 1
    number_trials /= 2
    
    rows, cols, index = number_trials, 3, 1
    fig = createFigure(13.0, rows, cols)
    
    p, i, d = selectStarburstCompartmentsAlongDendrite(retina, 0)
    
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
    
    save_path = os.path.join(retina_name, "Highlighted Morphology.jpg")
    drawMorphology(retina, [p, i, d], save_path)

 
def drawMorphology(retina, selected_compartments, save_path):
    
    starburst = retina.on_starburst_layer.neurons[0]
    number_compartments = starburst.number_compartments
    
    # Create a (scaled) pygame display
    pygame.init()    
    max_size = Vector2D(1000.0, 1000.0)       
    width_scale = max_size.x / float(retina.grid_width)
    height_scale = max_size.y / float(retina.grid_height)
    scale = min(width_scale, height_scale)   
    starburst.morphology.location = max_size/scale/2.0
    display = pygame.display.set_mode(max_size.toIntTuple())
    background_color = (25, 25, 25)
    morphology_color = (255, 255, 255)
    selected_morphology_color = (255, 0, 0)
    
    display.fill(background_color)
    
    for compartment, index in zip(starburst.compartments, range(number_compartments)):            
        # Draw the compartment
        if index in selected_compartments: 
            compartment.draw(display, color=selected_morphology_color, scale=scale)
        else:
            compartment.draw(display, color=morphology_color, scale=scale)
    
    pygame.image.save(display, save_path)
    
    
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
trial_name = "Annuli_Test_6"

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
entries = os.listdir(trial_path)
retina_paths = []
for entry in entries:
    path_to_entry = os.path.join(trial_path, entry)
    if os.path.isdir(path_to_entry):
        retina_paths.append(path_to_entry)


for retina_path in retina_paths:
    retina = Retina.loadRetina(retina_path)
    analyzeStarburst(retina, retina_path)