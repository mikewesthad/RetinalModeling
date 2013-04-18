from random import randint
import numpy as np
import pygame
from pygame.locals import *
from Retina import Retina
from Starburst import Starburst
from StarburstMorphology import StarburstMorphology
from Vector2D import Vector2D
from Constants import *

# Build a display
palette     = OCEAN_FIVE
background  = palette[0]
screen_size = Vector2D(1000, 1000)
display     = pygame.display.set_mode(screen_size.toIntTuple())

# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S
retina      = Retina(width, height, grid_size, display)

# Build a starburst morphology
scale = 2.0
screen_mid = screen_size/(2.0 * scale)
starburst_morphology = StarburstMorphology(retina, visualize_growth=True, color_palette=palette,
                                           display=display, draw_location=screen_mid,
                                           scale=scale)

# Build a unique starburst cell using the morphology
scale = 2.0
screen_mid = screen_size/(2.0 * scale)
starburst = Starburst(retina, None, starburst_morphology, screen_mid, 0, 0)
starburst.registerWithRetina()

# Interactive drawing (switch between views with d/c/p; change scale with left/right)
running             = True
draw_segments       = True
draw_compartments   = False
draw_points         = False
while running:
    display.fill(palette[0])
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_d:
                draw_segments       = True
                draw_compartments   = False
                draw_points         = False
            elif event.key == K_c:
                draw_segments       = False
                draw_compartments   = True
                draw_points         = False
            elif event.key == K_p:
                draw_segments       = False
                draw_compartments   = False
                draw_points         = True
            elif event.key == K_c:
                draw_segments       = False
                draw_compartments   = True
                draw_points         = False
            elif event.key == K_LEFT:
                scale -= 1.0
                screen_mid = screen_size/(2.0 * scale)
                starburst.location = screen_mid
            elif event.key == K_RIGHT:
                scale += 1.0
                screen_mid = screen_size/(2.0 * scale)
                starburst.location = screen_mid
                
            
    starburst.draw(display, scale=scale, draw_segments=draw_segments,
                   draw_compartments=draw_compartments, draw_points=draw_points)   
    pygame.display.update()
    
    
    


# Investigate the shortest path distances
# Pick a random compartment and recolor all other compartments based on their 
# distance from the choosen compartment
compartments    = starburst.morphology.compartments
pathlengths     = starburst.morphology.distances
colors          = [c.color for c in compartments]
number_compartments = len(compartments)
max_pathlength = 0
for i in range(number_compartments):
    max_in_row = max(pathlengths[i])
    if max_in_row > max_pathlength:
        max_pathlength = max_in_row
selected_compartment = randint(0, number_compartments-1)
        
grayscale = False
running = True
while running:
    display.fill(palette[0])
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONUP:
            grayscale = not(grayscale)
        if event.type == KEYDOWN:
            selected_compartment = randint(0, number_compartments-1)
        if event.type in [KEYDOWN, MOUSEBUTTONUP]:
            for i in range(number_compartments):
                compartment = compartments[i]
                pathlength  = pathlengths[selected_compartment][i]
                percent     = (max_pathlength-pathlength)/float(max_pathlength)
                if grayscale:
                    new_color = (int(percent*255),int(percent*255),int(percent*255))
                else:
                    new_color       = list(colors[i])
                    new_color[0]    = int(new_color[0] * percent)
                    new_color[1]    = int(new_color[1] * percent)
                    new_color[2]    = int(new_color[2] * percent)
                    new_color       = tuple(colors[i])
                compartment.color = new_color
            compartment = compartments[selected_compartment]
            compartment.color = (255,255,255)
    
    starburst.draw(display, scale=scale, draw_compartments=True)   
    pygame.display.update()



## Investigate the diffusion weight
## Pick a random compartment and recolor all other compartments based on their 
## weights from the choosen compartment
#compartments        = starburst.morphology.compartments
#weights             = starburst.morphology.diffusion_weights
#colors              = [c.color for c in compartments]
#number_compartments = len(compartments)
#max_weight = np.max(np.max(weights))
#print max_weight
#
#selected_compartment = randint(0, number_compartments-1)
#        
#grayscale = False
#running = True
#while running:
#    display.fill(palette[0])
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False
#        if event.type == MOUSEBUTTONUP:
#            grayscale = not(grayscale)
#        if event.type == KEYDOWN:
#            selected_compartment = randint(0, number_compartments-1)
#        if event.type in [KEYDOWN, MOUSEBUTTONUP]:
#            for i in range(number_compartments):
#                compartment = compartments[i]
#                weight      = weights[selected_compartment][i]
#                percent     = weight/float(max_weight)
#                if grayscale:
#                    new_color = (int(percent*255),int(percent*255),int(percent*255))
#                else:
#                    new_color       = list(colors[i])
#                    new_color[0]    = int(new_color[0] * percent)
#                    new_color[1]    = int(new_color[1] * percent)
#                    new_color[2]    = int(new_color[2] * percent)
#                    new_color       = tuple(colors[i])
#                compartment.color = new_color
#            compartment = compartments[selected_compartment]
#            compartment.color = (255,255,255)
#    
#    starburst.draw(display, scale=scale, draw_compartments=True)   
#    pygame.display.update()
#    
    


## Watch activity propagate
#starburst.history_size = 30
#starburst.decay_rate = 0.0
#starburst.input_stength = 0.0
#starburst.initializeActivties()
#starburst.activities[0][0, 0] = 1.0
#starburst.activities[0][0, 1] = 1.0
#starburst.activities[0][0, 2] = 1.0
#
#for i in range(starburst.history_size-1):
#    starburst.updateActivity()
#    
#    
#max_time = starburst.history_size - 1
#time = max_time
#
#compartments = starburst.morphology.compartments
#colors = [c.color for c in compartments]
#number_compartments = len(compartments)
#
#max_activity = np.amax(starburst.activities)
#        
#grayscale = False
#running = True
#while running:
#    display.fill(palette[0])
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False
#        if event.type == MOUSEBUTTONUP:
#            grayscale = not(grayscale)
#        if event.type == KEYDOWN:
#            if event.key == K_LEFT:
#                time += 1
#                if time > max_time: time = 0
#            if event.key == K_RIGHT:
#                time -= 1
#                if time < 0: time = max_time
#        if event.type in [KEYDOWN, MOUSEBUTTONUP]:
#            for i in range(number_compartments):
#                compartment = compartments[i]
#                activity    = starburst.activities[time][0, i]
#                percent     = activity/float(max_activity)
#                if grayscale:
#                    new_color = (int(percent*255),int(percent*255),int(percent*255))
#                else:
#                    new_color       = list(colors[i])
#                    new_color[0]    = int(new_color[0] * percent)
#                    new_color[1]    = int(new_color[1] * percent)
#                    new_color[2]    = int(new_color[2] * percent)
#                    new_color       = tuple(colors[i])
#                compartment.color = new_color
#                
#            print np.asum(starburst.activities[time])
#            
#    
#    starburst.draw(display, scale=scale, draw_compartments=True)   
#    pygame.display.update()