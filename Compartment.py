from random import randint
import pygame
from ConvexHull import convexHull
from NumpyConvexHull import convex_hull
import numpy as np
from Vector2D import Vector2D
from Constants import *
from math import pi

class Compartment:

    def __init__(self, morphology):
        self.morphology = morphology
        self.retina     = morphology.retina
        
        self.proximal_neighbors = []
        self.distal_neighbors   = []
        self.points             = [] 
        
        self.neurotransmitters_input_weights    = {}
        self.neurotransmitters_output_weights   = {}
        
        self.bounding_polygon = []
        
        self.index = len(self.morphology.compartments)
        self.morphology.compartments.append(self)
        
        self.color = (randint(100,255),randint(100,255),randint(100,255))
    
    def buildBoundingPolgyon(self):
        points_list = [pt.location.toTuple() for pt in self.points]
        
        centroid = Vector2D(0.0, 0.0)
        for point in self.points:
            centroid += point.location
        centroid /= len(self.points)
        
        # The convex hull script requires at least 5 points, so let's add plenty
        delta = 0.0
        while len(points_list) <= 5:
            for dx, dy in [(0.0,delta),(delta,0.0),(delta,delta)]:
                for xsign, ysign in [(1.0,1.0),(-1.0,1.0),(1.0,-1.0),(-1.0,-1.0)]:
                    new_point = centroid + Vector2D(dx*xsign, dy*ysign)
                    if new_point.toTuple() not in points_list:
                        points_list.append(new_point.toTuple())
                        if len(points_list) > 5: break
                if len(points_list) > 5: break
            delta += 1.0
            
        # Create a (2 x m) array to be used by the numpy function        
        points_array    = np.array(points_list).T
        hull_array      = convex_hull(points_array)
        hull_points     = hull_array.tolist()
        
        self.bounding_polygon   = hull_points
        self.centroid           = centroid
    
    def buildNeurotransmitterWeights(self):
        for point in self.points:
            for nt in point.neurotransmitters_accepted:
                if nt in self.neurotransmitters_input_weights:
                    self.neurotransmitters_input_weights[nt] += 1.0
                else:
                    self.neurotransmitters_input_weights[nt] = 1.0
                    
            for nt in point.neurotransmitters_released:
                if nt in self.neurotransmitters_output_weights:
                    self.neurotransmitters_output_weights[nt] += 1.0
                else:
                    self.neurotransmitters_output_weights[nt] = 1.0
        
        number_points = len(self.points)
        for nt in self.neurotransmitters_input_weights:
            self.neurotransmitters_input_weights[nt] /= number_points
        for nt in self.neurotransmitters_output_weights:
            self.neurotransmitters_output_weights[nt] /= number_points
            
    def draw(self, surface, scale=1.0, draw_bounding_box=False, draw_neurotransmitters=True):
        if draw_bounding_box:
            if self.bounding_polygon != []:
                moved_polygon = []
                for point in self.bounding_polygon:
                    new_x = (point[0] + self.morphology.location.x) * scale
                    new_y = (point[1] + self.morphology.location.y) * scale
                    moved_polygon.append([new_x, new_y])
                pygame.draw.polygon(surface, self.color, moved_polygon)
                
                color_key = {GABA:[-2.0, -2.0, (255,0,0)], 
                             ACH:[0.0, 0.0, (0,255,0)], 
                             GLU:[-2.0, 0.0, (0,0,255)], 
                             GLY:[0.0, -2.0, (0,0,0)]}   
                width   = 2.0   
                height  = 2.0
                             
                if draw_neurotransmitters:
                        loc  = self.morphology.location + self.centroid
                                              
                        for nt in color_key:                        
                            dx, dy, color = color_key[nt]
                            nt_rect = pygame.Rect((loc.x+dx)*scale, 
                                                  (loc.y+dy)*scale, 
                                                  width*scale, 
                                                  height*scale) 
                            if nt in self.neurotransmitters_output_weights:
                                border = 0
                            else:
                                border = 1
                                color = [color[0]+200,color[1]+200,color[2]+200]
                                color[0] = min(color[0], 255)
                                color[1] = min(color[1], 255)
                                color[2] = min(color[2], 255)
                            pygame.draw.rect(surface, color, nt_rect, border)
                        
        else:
            for point in self.points:
                world_location = (self.morphology.location + point.location) * scale
                pygame.draw.circle(surface, self.color, world_location.toIntTuple(), 2)            
    
    def registerWithRetina(self, neuron, layer_depth):
        for point in self.points:
            location = point.location + neuron.location
            self.retina.register(neuron, self, layer_depth, location)
    
    def getSize(self):
        return len(self.points)