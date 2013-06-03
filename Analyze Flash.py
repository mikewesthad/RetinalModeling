import os
import matplotlib.pyplot as plt
from random import randint 
import numpy as np

def analyzeStarburst(retina, retina_name, stimulus_name):
    
    retina.loadActivities(retina_name, stimulus_name)
    
    activities = retina.on_starburst_activities[:, 0, 0, :]
    timesteps = len(activities)
    x_axis = range(timesteps)
    
    p, i, d = selectStarburstCompartmentsAlongDendrite(retina, 0)
        
    fig = plt.figure(figsize=(11, 11))
    rows, cols, index = 1, 1, 1
    
    ax = fig.add_subplot(rows, cols, index)
    y_axis = [a[p] for a in activities]
    ax.plot(x_axis, y_axis, linewidth=2, color='r')
    y_axis = [a[d] for a in activities]
    ax.plot(x_axis, y_axis, linewidth=2, color='b')
    index += 1
    
#    ax.set_title("Flash Response", fontsize=36)
    ax.set_xlabel("Timesteps", fontsize=24)
    ax.set_ylabel("Activity", fontsize=24)
    ax.set_ylim([0.0, 1.0])
    ax.legend(["Proximal","Distal"], loc="lower right", prop={'size':24})

    fig.tight_layout()
    fig.savefig("Traces.jpg")
    
    drawMorphology(retina, p, d)

 
def drawMorphology(retina, p, d):
    
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
    p_color = (255, 0, 0)
    d_color = (0, 0, 255)
    
    display.fill(background_color)
    
    for compartment, index in zip(starburst.compartments, range(number_compartments)):            
        # Draw the compartment
        if index == p: 
            compartment.draw(display, color=p_color, scale=scale)
        elif index == d:
            compartment.draw(display, color=d_color, scale=scale)
        else:
            compartment.draw(display, color=morphology_color, scale=scale)
    
    pygame.image.save(display, "Selected Morphology.jpg")
    
    
    
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
retina_name = "Flash_Center_No_Decay"
retina = Retina.loadRetina(retina_name)

analyzeStarburst(retina, retina_name, "0")