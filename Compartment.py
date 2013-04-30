from random import randint
import pygame
from NumpyConvexHull import convex_hull
import numpy as np
from Vector2D import Vector2D
from DendritePoint import DendritePoint
from Constants import *

class Compartment:

    def __init__(self, neuron):
        self.neuron     = neuron
        self.retina     = neuron.retina
        
        self.gridded_locations  = []
        self.points             = [] 
        
        self.neurotransmitters_input_weights    = {}
        self.neurotransmitters_output_weights   = {}
        
        self.bounding_polygon = []
        
        self.index = len(self.neuron.compartments)
        self.neuron.compartments.append(self)
        
        self.color = (randint(100,255),randint(100,255),randint(100,255))
        
    def updateActivity(self):
        pass
    
    """
    Finds the convex hull that bounds the points of the compartment
    """
    def buildBoundingPolgyon(self):
        # Create a list of point locations
        points_list = [pt.location.toTuple() for pt in self.points]
        
        # Calculate the centroid of the points
        centroid = Vector2D(0.0, 0.0)
        for point in self.points:
            centroid += point.location
        centroid /= len(self.points)
        
        # Before creating the convex hull, we need to make sure we have at least
        # least 5 points
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
        
        # Calculate the hull points
        hull_array      = convex_hull(points_array)
        hull_points     = hull_array.tolist()
        
        # Store the results
        self.bounding_polygon   = hull_points
        self.centroid           = centroid   
        
    
    """
    Find the per-point amount of neurotransmitter accepted/released - essentially
    smearing out the synapse properties of the points in the compartment
    """
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

    
    def draw(self, surface, scale=1.0, draw_points=False, draw_text=False):
        # This function assumes compartments are 1 line segment - check bottom 
        # of file for old draw command
        
        if draw_points:
            for point in self.points:
                point.draw(surface, scale=scale)
            return        
            
        # Draw convex hull
        moved_polygon = []
        for point in self.bounding_polygon:
            new_x = (point[0] + self.morphology.location.x) * scale
            new_y = (point[1] + self.morphology.location.y) * scale
            moved_polygon.append([new_x, new_y])
        pygame.draw.polygon(surface, self.color, moved_polygon)
              
    
    def registerWithRetina(self, neuron, layer_depth):
        for point in self.points:
            location = point.location + neuron.location
            self.retina.register(neuron, self, layer_depth, location)
    
    def getSize(self):
        return len(self.points)
        
    

class GrowingCompartment(Compartment):
    def __init__(self, neuron):
        Compartment.__init__(self, neuron)
        
        self.proximal_neighbors = []
        self.distal_neighbors   = []
        self.line_points        = []
        
    def discretize(self, delta=1.0, range_deltas=[], parent_locations=[]):        
        if range_deltas == []:
            range_deltas = np.arange(0.0, self.neuron.step_size, delta) 
            
        for i in range(len(self.line_points)-1):
            p1 = self.line_points[i]
            p2 = self.line_points[i+1]
        
            heading_vector = p1.unitHeadingTo(p2)
            
            for d in range_deltas:
                p = p1 + heading_vector * d
                p = p.roundedIntCopy()
                if (p not in self.gridded_locations) and (p not in parent_locations): 
                    self.gridded_locations.append(p)
                    
        for child in self.distal_neighbors:
            child.discretize(delta, range_deltas, self.gridded_locations)
    
    def createPoints(self, last_location, wirelength_to_last):
        for gridded_location in self.gridded_locations:
            additional_wirelength   = last_location.distanceTo(gridded_location)
            current_wirelength      = wirelength_to_last + additional_wirelength            
            point = DendritePoint(self.retina, self, gridded_location, current_wirelength)
            self.points.append(point)            
            last_location       = gridded_location
            wirelength_to_last  = current_wirelength
        
        for child in self.distal_neighbors:
            child.createPoints(last_location, wirelength_to_last)
            
    def colorCompartments(self, colors, index):
        self.color = colors[index]
        index += 1
        if index >= len(colors): index = 0
        for child in self.distal_neighbors:
            child.colorCompartments(colors, index)
            
    def buildQuadFromLine(self, a, b, width):
        angle       = a.angleHeadingTo(b)
        left_perp   = Vector2D.generateHeadingFromAngle(angle + 90.0)
        right_perp  = Vector2D.generateHeadingFromAngle(angle - 90.0)
        
        v1 = a+left_perp*width
        v2 = a+right_perp*width
        v3 = b+left_perp*width
        v4 = b+right_perp*width
        
        vertices = [v1.toTuple(), v2.toTuple(), v4.toTuple(), v3.toTuple()]
        return vertices
        
    def draw(self, surface, scale=1.0, draw_points=False, draw_text=False):
        # This function assumes compartments are 1 line segment - check bottom 
        # of file for old draw command
        
        if draw_points:
            for point in self.points:
                point.draw(surface, scale=scale)
            return        
        
        a           = (self.neuron.location + self.line_points[0]) * scale
        b           = (self.neuron.location + self.line_points[1]) * scale
        vertices    = self.buildQuadFromLine(a, b, 2.0/3.0 * scale)
        pygame.draw.polygon(surface, self.color, vertices)  
            
        if draw_text:
            pygame.init()
            fontObj = pygame.font.Font(None, 18)
            fontSurfObj = fontObj.render(str(self.index), False, (0,0,0))
            fontSurfRect = fontSurfObj.get_rect()
            fontSurfRect.center = ((a+b)/2.0).toIntTuple()
            surface.blit(fontSurfObj, fontSurfRect)
            
            
            
            
            
            
            
  
###############################################################################
# Old code that might get retired
###############################################################################  
  
#def draw(self, surface, scale=1.0, draw_neurotransmitters=False, draw_text=False):
#    if len(self.line_points) == 2:
#        # Draw quads
#        start_index = 0
#        end_index = len(self.line_points)-2
#        for i in range(start_index, end_index+1): 
#            a = (self.morphology.location + self.line_points[i])*scale
#            b = (self.morphology.location + self.line_points[i+1])*scale
#            vertices = self.buildRectangeFromLine(a, b, 2.0/3.0 * scale)
#            pygame.draw.polygon(surface, self.color, vertices)  
#            
#        if draw_text:
#            pygame.init()
#            fontObj = pygame.font.Font(None, 18)
#            fontSurfObj = fontObj.render(str(self.index), False, (0,0,0))
#            fontSurfRect = fontSurfObj.get_rect()
#            fontSurfRect.center = ((a+b)/2.0).toIntTuple()
#            surface.blit(fontSurfObj, fontSurfRect)
#        
#    else:
#        # Draw convex hull
#        moved_polygon = []
#        for point in self.bounding_polygon:
#            new_x = (point[0] + self.morphology.location.x) * scale
#            new_y = (point[1] + self.morphology.location.y) * scale
#            moved_polygon.append([new_x, new_y])
#        pygame.draw.polygon(surface, self.color, moved_polygon)
#        
#        color_key = {GABA:[-2.0, -2.0, (255,0,0)], 
#                     ACH:[0.0, 0.0, (0,255,0)], 
#                     GLU:[-2.0, 0.0, (0,0,255)], 
#                     GLY:[0.0, -2.0, (0,0,0)]}   
#        width   = 2.0   
#        height  = 2.0
#                     
#        if draw_neurotransmitters:
#                loc  = self.morphology.location + self.centroid
#                                      
#                for nt in color_key:                        
#                    dx, dy, color = color_key[nt]
#                    nt_rect = pygame.Rect((loc.x+dx)*scale, 
#                                          (loc.y+dy)*scale, 
#                                          width*scale, 
#                                          height*scale) 
#                    if nt in self.neurotransmitters_output_weights:
#                        border = 0
#                    else:
#                        border = 1
#                        color = [color[0]+200,color[1]+200,color[2]+200]
#                        color[0] = min(color[0], 255)
#                        color[1] = min(color[1], 255)
#                        color[2] = min(color[2], 255)
#                    pygame.draw.rect(surface, color, nt_rect, border)