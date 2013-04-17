# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 15:37:44 2013

@author: jfarina
"""

test = True
print 'test =', test

from retinaClasses import *
import pygame
from pygame import *

display = pygame.display.set_mode( (800,800) )

def compartmentalize(compartment, num_points_tot, num_points_left, 
                     dendrite_segment, index):
    
    comp = compartment 

    while (num_points_left > 0) and (index < len(dendrite_segment.points)):
            comp.addDendritePoint(dendrite_segment.points[index])
            index += 1
            num_points_left -= 1
    
    if (num_points_left > 0) and (index == len(dendrite_segment.points)):
        #proceed to compartmentalize the children.
        num_children = len(dendrite_segment.children)        
        if num_children > 0:
            #apportion num_points_left over children in integer values.
            num_needed_each = num_points_left // num_children
            num_extras_left = num_points_left % num_children            
            for child in dendrite_segment.children:
                if num_extras_left > 0:
                    extra = 1
                    num_extras_left -= 1
                else:
                    extra = 0
                compartmentalize(comp, num_points_tot, 
                                 num_needed_each + extra,
                                 child, 0)
        return None
              
    if num_points_left == 0:
        if index < len(dendrite_segment.points):
            new_comp = Compartment(comp, comp.neuron, comp.grid) 
            comp.neighbor_distal.append(new_comp)
            compartmentalize(new_comp, num_points_tot, num_points_tot,
                             dendrite_segment, index)
        else:
            for child in dendrite_segment.children:
                new_comp = Compartment(comp, comp.neuron, comp.grid)
                comp.neighbor_distal.append(new_comp)                
                compartmentalize(new_comp, num_points_tot, num_points_tot,
                                 child, 0)
        return None
            
##########
## Test ##
##########

#___d1______ ___d11____
#          |
#      d12 |
#          |____d121___
#          |
#     d122 |
#          |

n = 10
m = 10

scale = 10

d1_loc = []
for i in range(n):
    d1_loc.append(Location(i*scale, 0))

d11_loc = []
for i in range(n):
    d11_loc.append(Location((n+i)*scale, 0))

d12_loc = []
for i in range(m):
    d12_loc.append(Location(n*scale, (1+i)*scale))
    
d121_loc = []
for i in range(n):
    d121_loc.append(Location((1+n+i)*scale, (1+m)*scale))
    
d122_loc = []
for i in range(m):
    d122_loc.append(Location(n*scale, (1+m+i)*scale))
    
d123_loc = []
for i in range(m):
    d123_loc.append(Location((1+n+i)*scale, (2+m+i)*scale))


r = RetinalGrid(800, 800, 1)    
n = Neuron(Location(0,0), r)    

d1 = DendriteSegment(n, d1_loc)
d11 = DendriteSegment(n, d11_loc)
d12 = DendriteSegment(n, d12_loc)
d121 = DendriteSegment(n, d121_loc)
d122 = DendriteSegment(n, d122_loc)
d123 = DendriteSegment(n, d123_loc)

dendrites = [d1, d11, d12, d121, d122, d123]

for d in dendrites:
    d.initPoints()

d1.children.append(d11)
d1.children.append(d12)
d12.children.append(d121)
d12.children.append(d122)
d12.children.append(d123)

c = Compartment(None, n, r)
comp_size = 7
compartmentalize(c, comp_size, comp_size , d1, 0)


#############
## Display ##
#############
running = test

color_dict = {'red':    (255,   0,      0),
              'orange': (255,   200,    0),
              'yellow': (255,   255,    0),
              'green':  (0,     255,    0),
              'cyan':   (0,     255,    255),
              'blue':   (0,     0,      255),
              'purple': (255,   0,      255)}
colors = ('red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple')
black = (0, 0, 0)

circle_radius = 3
circle_line_width = 0

line_width = 2

while running:
    
    display.fill((255, 255, 255))
    
    for d in dendrites:
        pygame.draw.line(display,
                         black,
                         d.points[0].location.ID,
                         d.points[-1].location.ID,
                         line_width)                    
    
    i = 0
    for comp in n.compartments:
        #print comp, 'num_elem =', len(comp.points)
        color = color_dict[colors[i % len(colors)]]
        i += 1
        for point in comp.points:
            #print point.location.ID
            pygame.draw.circle(display,
                               color,
                               point.location.ID,
                               circle_radius,
                               circle_line_width)
            
    
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:

            running = False


point_count = 0
for comp1 in n.compartments:
    for point1 in comp1.points:
        for comp2 in n.compartments:
            for point2 in comp2.points:
                if point1 is point2:
                    point_count += 1
print 'Number of unique compartments =', point_count
        
    