import random as r
import numpy as np

import pygame
from pygame.locals import *


def linearDistance(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5
    
def solveLine(p1, p2):
    delta_x = p2[0] - p1[0]
    delta_y = p2[1] - p1[1]
    if delta_x == 0: 
        slope       = None
        y_intercept = None
    else:
        slope       = delta_y/delta_x
        y_intercept = p1[1] - slope * p1[0]
    return slope, y_intercept
    

def collisionDetect(surface, point_a, point_b, point_c, point_d):    
    r_ab        = linearDistance(point_a, point_b) / 2.0
    mid_ab      = (point_a + point_b) / 2.0
    m_ab, b_ab  = solveLine(point_a, point_b)
    
    r_cd        = linearDistance(point_c, point_d) / 2.0
    mid_cd      = (point_c + point_d) / 2.0
    m_cd, b_cd  = solveLine(point_c, point_d)
    
    pygame.draw.circle(surface, (155,0,0), mid_ab.astype(int), r_ab.astype(int), 1)
    pygame.draw.circle(surface, (0,0,155), mid_cd.astype(int), r_cd.astype(int), 1)
    
    min_circle_distance     = r_ab + r_cd
    dist_between_circles    = linearDistance(mid_ab, mid_cd)
    if dist_between_circles <= min_circle_distance:
        
        # Not parallel
        if m_ab != m_cd:
            # I am a vertical line                            
            if m_ab == None:
                # My equation is x = c, so the x coord of intersection
                # has to be equal to the x coord of either of my points
                x = point_a[0]
                # Other equation is y=mx+b, so plug x in and solve
                y = m_cd * x + b_cd
                
            # Other is a vertical line
            elif m_cd == None:
                # Other equation is x = c, so the x coord of intersection
                # has to be equal to the x coord of either of my points
                x = point_c[0]
                # My equation is y=mx+b, so plug x in and solve
                y = m_ab * x + b_ab
                                    
            else:
                # Find the intersection
                x = (b_cd - b_ab) / (m_ab - m_cd)
                y = m_ab * x + b_ab
        
            intersection_point = np.array((x,y))
            
            if linearDistance(mid_ab, intersection_point) <= r_ab and \
               linearDistance(mid_cd, intersection_point) <= r_cd:
                return True, intersection_point
            return False, None
        return False, None            
    return False, None
        
        




# Update the dendrites, but let's visualize it using pygame
pygame.init()
display = pygame.display.set_mode((1000,1000))
display.fill((255,255,255))

clock = pygame.time.Clock()


point_a = np.array([r.uniform(100, 800), r.uniform(100, 800)])
point_b = np.array([point_a[0]+r.uniform(50, 100), 
                    point_a[1]+r.uniform(50, 100)])


heading = 10
dheading = 10
length = 100

running = True
while running:
    
    display.fill((255,255,255))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        
        if event.type == QUIT:
            running = False
        else:
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    heading += dheading
                elif event.key == K_RIGHT:
                    heading -= dheading
                if event.key == K_UP:
                    dheading += 1
                elif event.key == K_DOWN:
                    dheading -= 1
    
    point_mid = np.array([mouse_x, mouse_y])                  
    vector_heading = np.array([np.cos(np.deg2rad(heading)), np.sin(np.deg2rad(heading))])                
    point_c = point_mid + vector_heading * length/2.0                
    point_d = point_mid + vector_heading * -length/2.0
                        
    collision, intersect = collisionDetect(display, point_a, point_b, point_c, point_d)
    if collision:
        display.fill((0,0,0))
        
        
    pygame.draw.line(display, (255,0,0), point_a, point_b, 1)
    pygame.draw.line(display, (0,0,255), point_c, point_d, 1)
    if collision: 
        pygame.draw.circle(display, (255,0,255), intersect.astype(int), 2)
    
    
        
    pygame.display.update()
    
