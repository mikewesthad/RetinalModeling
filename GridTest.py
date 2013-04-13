import numpy as np
import pygame
from pygame.locals import *
from Vector2D import Vector2D


def snapToNearestGrid(locations, grid_size, step_size, delta, last_points=[]):
    gridded_locations = []
    
    range_deltas = np.arange(0, step_size/grid_size, delta)
    for i in range(len(locations)-1):
        p1 = locations[i]
        p2 = locations[i+1]
        
        heading_vector = p1.unitHeadingTo(p2)
        
        for d in range_deltas:
            p = p1 + heading_vector * d
            p = p.roundedIntCopy()
            
            if not(p in last_points or p in gridded_locations): 
                gridded_locations.append(p)
                
    return gridded_locations
                
                
                    

pygame.init()
display = pygame.display.set_mode((1000,1000))       

grid_size = 10

import random
heading = 0.0
heading_deviation = 65.0
step_size = 50
steps = 5

locations = [Vector2D(500,500)]  
grid_locations = [locations[0]/grid_size]       

for i in range(steps):
    last_location = locations[-1]   
    
    angle               = heading + random.uniform(-heading_deviation, heading_deviation)
    vector_direction    = Vector2D.generateHeadingFromAngle(angle)
    new_location        = last_location + vector_direction * step_size
    locations.append(new_location)
    grid_locations.append(new_location/grid_size)
    
gridded_locations = snapToNearestGrid(grid_locations, grid_size, step_size, .1)

locations2 = [locations[-1]]  
grid_locations = [locations2[0]/grid_size]   
for i in range(steps):
    last_location = locations2[-1]       
    angle               = heading + random.uniform(-heading_deviation, heading_deviation)
    vector_direction    = Vector2D.generateHeadingFromAngle(angle)
    new_location        = last_location + vector_direction * step_size
    locations2.append(new_location)
    grid_locations.append(new_location/grid_size)
    

gridded_locations2 =snapToNearestGrid(grid_locations, grid_size, step_size, .1, gridded_locations)


clock = pygame.time.Clock()
running = True
while running:
    display.fill((255,255,255))
    
    for i in range(0,1000,grid_size):
        pygame.draw.line(display, (200,200,200), (i,0), (i,1000), 1) 
        pygame.draw.line(display, (200,200,200), (0,i), (1000,i), 1) 
        
    
    for i in range(len(locations)-1): 
        a = locations[i]
        b = locations[i+1]                
        pygame.draw.line(display, (0,0,0), a.toIntTuple(), b.toIntTuple(), 1)
        
    for i in range(len(locations2)-1): 
        a = locations2[i]
        b = locations2[i+1]                
        pygame.draw.line(display, (0,0,0), a.toIntTuple(), b.toIntTuple(), 1) 
    
    
    for grid_loc in gridded_locations:
        pixel_loc = grid_loc * grid_size
        pygame.draw.circle(display, (0,0,255), pixel_loc.toIntTuple(), 5)
        
    
    for grid_loc in gridded_locations2:
        pixel_loc = grid_loc * grid_size
        pygame.draw.circle(display, (255,0,0), pixel_loc.toIntTuple(), 3)
    
    
        
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == QUIT: running = False
    pygame.display.update()
    
    