def drawMorphology(trial_path, retina_paths):
    pygame.init()    
    max_size            = Vector2D(1000.0, 1000.0)  
    background_color    = (25, 25, 25)
    morphology_color    = (255, 255, 255)
    width_scale         = max_size.x / 400.0
    height_scale        = max_size.y / 400.0
    scale               = min(width_scale, height_scale)   
    display             = pygame.display.set_mode(max_size.toIntTuple())
    pygame.display.iconify()
    
    retina_number = 0
    for retina_path in retina_paths:
        retina = Retina.loadRetina(retina_path)
        starburst = retina.on_starburst_layer.neurons[0]
        starburst.morphology.location   = max_size/scale/2.0
        
        # Draw the morphology
        display.fill(background_color)     
        for compartment in starburst.compartments:
            compartment.draw(display, color=morphology_color, scale=scale)
        morphology_path = os.path.join(trial_path, str(retina_number)+" Morphology.jpg")
        pygame.image.save(display, morphology_path)
        retina_number += 1
    pygame.quit()

import os
import pygame
from pygame.constants import *
from Constants import *
trial_name = "110_Degree_Kink"
number_bars = 12

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
entries = os.listdir(trial_path)
retina_paths = []
for entry in entries:
    path_to_entry = os.path.join(trial_path, entry)
    if os.path.isdir(path_to_entry):
        retina_paths.append(path_to_entry)

drawMorphology(trial_path, retina_paths)