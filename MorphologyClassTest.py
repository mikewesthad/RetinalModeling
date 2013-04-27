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
retina      = Retina(width, height, grid_size, None, None, display)

# Build a starburst morphology
scale = 2.0
screen_mid = screen_size/(2.0 * scale)
starburst_morphology = StarburstMorphology(retina, visualize_growth=False, color_palette=palette,
                                           display=display, draw_location=screen_mid,
                                           scale=scale,
                                           average_wirelength=150*UM_TO_M)

# Build a unique starburst cell using the morphology
scale = 2.0
screen_mid = screen_size/(2.0 * scale)
starburst = Starburst(retina, None, starburst_morphology, screen_mid, 0, 0)
#starburst.registerWithRetina()

## Interactive drawing (switch between views with d/c/p; change scale with left/right)
#running             = True
#draw_segments       = True
#draw_compartments   = False
#draw_points         = False
#while running:
#    display.fill(palette[0])
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False
#        if event.type == KEYDOWN:
#            if event.key == K_d:
#                draw_segments       = True
#                draw_compartments   = False
#                draw_points         = False
#            elif event.key == K_c:
#                draw_segments       = False
#                draw_compartments   = True
#                draw_points         = False
#            elif event.key == K_p:
#                draw_segments       = False
#                draw_compartments   = False
#                draw_points         = True
#            elif event.key == K_c:
#                draw_segments       = False
#                draw_compartments   = True
#                draw_points         = False
#            elif event.key == K_LEFT:
#                scale -= 1.0
#                screen_mid = screen_size/(2.0 * scale)
#                starburst.location = screen_mid
#            elif event.key == K_RIGHT:
#                scale += 1.0
#                screen_mid = screen_size/(2.0 * scale)
#                starburst.location = screen_mid
#
#    starburst.draw(display, scale=scale, draw_segments=draw_segments,
#                   draw_compartments=draw_compartments, draw_points=draw_points)   
#    pygame.display.update()
#    
#    
#    
#
#

## Investigate the shortest path distances
## Pick a random compartment and recolor all other compartments based on their 
## distance from the choosen compartment
#display.fill(palette[0])
#number_compartments     = len(starburst.morphology.compartments)
#selected_compartment    = randint(0, number_compartments-1)
#starburst.morphology.drawDiffusionWeights(display, selected_compartment, new_location=starburst.location, scale=scale)
#        
#running = True
#while running:
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False
#        if event.type == KEYDOWN:
#            selected_compartment = randint(0, number_compartments-1)
#            display.fill(palette[0])
#            starburst.morphology.drawDiffusionWeights(display, selected_compartment, new_location=starburst.location, scale=scale)
#    pygame.display.update()


# Watch activity propagate
starburst.history_size  = 200
starburst.decay_rate    = 0.0
starburst.input_stength = 0.0
starburst.initializeActivties()

compartments = starburst.morphology.compartments
number_compartments = len(compartments)
#for i in range(number_compartments):
#    starburst.activities[0][0, i] = 1.0
    
starburst.activities[0][0, 0] = 1.0
starburst.activities[0][0, 300] = 1.0
starburst.activities[0][0, 301] = 1.0
starburst.activities[0][0, 302] = 1.0
starburst.activities[0][0, 303] = 1.0
starburst.activities[0][0, 400] = 1.0
starburst.activities[0][0, 401] = 1.0
starburst.activities[0][0, 402] = 1.0
starburst.activities[0][0, 403] = 1.0

for i in range(starburst.history_size-1):
    starburst.updateActivity()
    
#    starburst.activities[0][0, 0] = 1.0
#    starburst.activities[0][0, 300] = 1.0
#    starburst.activities[0][0, 301] = 1.0
#    starburst.activities[0][0, 302] = 1.0
#    starburst.activities[0][0, 303] = 1.0
#    starburst.activities[0][0, 400] = 1.0
#    starburst.activities[0][0, 401] = 1.0
#    starburst.activities[0][0, 402] = 1.0
#    starburst.activities[0][0, 403] = 1.0
    
    
max_time = starburst.history_size - 1
time = max_time

compartments = starburst.morphology.compartments
number_compartments = len(compartments)

max_activity = np.amax(starburst.activities)
        
running = True
auto = True
clock = pygame.time.Clock()
while running:
    display.fill((0,0,255))
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                time += 1
                if time > max_time: time = 0
            if event.key == K_RIGHT:
                time -= 1
                if time < 0: time = max_time
            if event.key == K_SPACE:
                auto = not(auto)
            for i in range(number_compartments):
                compartment = compartments[i]
                activity    = starburst.activities[time][0, i]
                percent     = activity/float(max_activity)
                new_color = (int(percent*255),int(percent*255),int(percent*255))
                compartment.color = new_color
        
                
    if auto:
        print "Timestep\t{0}\n".format(max_time-time),
        print "Total Activity\t{0:.3f}\n".format(np.sum(starburst.activities[time])),
        print "Max Activity\t{0:.3f}\n".format(max_activity)
        
        for i in range(number_compartments):
            compartment = compartments[i]
            activity    = starburst.activities[time][0, i]
            percent     = activity/float(max_activity)
            new_color = (int(percent*255),int(percent*255),int(percent*255))
            compartment.color = new_color
        
        time -= 1
        if time < 0: time = max_time
        
        clock.tick(5)
        
    
    starburst.draw(display, scale=scale, draw_compartments=True)   
    pygame.display.update()