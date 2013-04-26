import numpy as np 

import pygame
from pygame.locals import *
 
 
def linearDistance(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5


def calculateHeadingRange(heading, heading_deviation):
    # Find the heading bounds (assuming heading deviation is positive)
    heading_max = heading + heading_deviation
    heading_min = heading - heading_deviation
    
    # Unwrap the heading bounds into the range [0-360]
    if heading_max > 360: heading_max -= 360.0
    if heading_min < 0: heading_min = 360.0 + heading_min
    
    # If the max and min switched places during unwrapping, switch them back
    if heading_min > heading_max:
        heading_max, heading_min = heading_min, heading_max
    
    # Find the set(s) that define the heading bounds
    if heading_max - heading_min > 180:
        allowable_headings = [[0.0, heading_min], [heading_max, 360.0]]
    else:
        allowable_headings = [[heading_min, heading_max]]
    
    return allowable_headings
    

pygame.init()
display = pygame.display.set_mode((1000,1000))
display.fill((255,255,255))
clock = pygame.time.Clock()    

# Get the circular bounding box that describes the locations I will avoid
vision_radius = 100
vision_center = np.array([500, 500])
heading = 30
heading_deviation = 30

allowable_headings = calculateHeadingRange(heading, heading_deviation)

points = []

dheading = 1
running = True
while running:
    
    display.fill((255,255,255))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.circle(display, (0,0,0), (mouse_x, mouse_y), 3)
    
    for event in pygame.event.get():
        
        if event.type == QUIT:
            running = False
        else:
            if event.type == MOUSEBUTTONUP:
                if len(points)>0 and linearDistance(points[-1], [mouse_x, mouse_y])<10:
                    pass
                else:
                    points.append(np.array([mouse_x, mouse_y]))
                
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    heading_deviation += 10
                    allowable_headings = calculateHeadingRange(heading, heading_deviation)
                elif event.key == K_RIGHT:
                    heading_deviation -= 10                   
                    allowable_headings = calculateHeadingRange(heading, heading_deviation)
                if event.key == K_UP:
                    heading += 10
                    if heading > 360: heading -= 360.0
                    if heading < 0: heading = 360.0 + heading
                    allowable_headings = calculateHeadingRange(heading, heading_deviation)
                elif event.key == K_DOWN:
                    heading -= 10
                    if heading > 360: heading -= 360.0
                    if heading < 0: heading = 360.0 + heading
                    allowable_headings = calculateHeadingRange(heading, heading_deviation)
                    
    for p in points:
        pygame.draw.circle(display, (0,0,0), p, 3)
    
    for i in range(len(points)-1):
        line_color = (0,0,0)
        circle_color = (0,0,0)
        
        a = points[i]
        b = points[i+1]
        line_segment_center = (a+b)/2.0
        line_segment_radius = linearDistance(a, line_segment_center)
               
        collision_circle_distance   = vision_radius + line_segment_radius
        distance_between_circles    = linearDistance(vision_center, line_segment_center)
        
        if distance_between_circles <= collision_circle_distance:
            circle_color = (255,0,0)
            vector_to_a = a - vision_center
            vector_to_b = b - vision_center
            angle_to_a = np.arctan2(vector_to_a[1], vector_to_a[0]) * 180.0/np.pi
            angle_to_b = np.arctan2(vector_to_b[1], vector_to_b[0]) * 180.0/np.pi
            if angle_to_a < 0: angle_to_a += 360   
            if angle_to_b < 0: angle_to_b += 360
            
            if angle_to_a > angle_to_b: 
                angle_max = angle_to_a
                angle_min = angle_to_b
            else:
                angle_max = angle_to_b
                angle_min = angle_to_a
            
            angle_in_range = False
            for heading_min, heading_max in allowable_headings:
                if heading_min <= angle_min and angle_min <= heading_max:
                    angle_in_range = True
                    break
                if heading_min <= angle_max and angle_max <= heading_max:
                    angle_in_range = True
                    break
                if angle_min <= heading_min and heading_min <= angle_max:
                    angle_in_range = True
                    break
                if angle_min <= heading_max and heading_max <= angle_max:
                    angle_in_range = True
                    break
            if angle_in_range: line_color = (255,0,0)
            
        
        pygame.draw.line(display, line_color, points[i], points[i+1], 1)            
        pygame.draw.circle(display, circle_color, line_segment_center.astype(int), line_segment_radius.astype(int), 1)
    
    pygame.draw.circle(display, (0,0,255), vision_center, 3)
    pygame.draw.circle(display, (0,0,155), vision_center, vision_radius, 1)
    for heading_min, heading_max in allowable_headings:
        rad_min = np.deg2rad(heading_min)
        rad_max = np.deg2rad(heading_max)
        heading_min_point = vision_center + np.array([np.cos(rad_min)*vision_radius, np.sin(rad_min)*vision_radius])
        heading_max_point = vision_center + np.array([np.cos(rad_max)*vision_radius, np.sin(rad_max)*vision_radius])
        pygame.draw.line(display, (0,0,255), vision_center, heading_min_point)
        pygame.draw.line(display, (0,0,255), vision_center, heading_max_point)
    
               
    pygame.display.update()
                    
    

        

        