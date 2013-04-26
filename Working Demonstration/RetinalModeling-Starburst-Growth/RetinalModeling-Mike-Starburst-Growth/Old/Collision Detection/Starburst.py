import random
import numpy as np
from Constants import *

import pygame
from pygame.locals import *

class Neuron(object):
    
    def __init__(self, retina, location, average_wirelength=300*UM_TO_M, radius_deviation=.1,
                 min_branches=4, max_branches=6, heading_deviation=20, step_size=10*UM_TO_M):
        
        self.retina     = retina
        self.location   = np.array(location) / self.retina.grid_size
        
        self.heading_deviation  = heading_deviation
        self.step_size          = step_size / self.retina.grid_size
        
        average_wirelength  = average_wirelength / self.retina.grid_size
        max_wirelength      = average_wirelength * (1.0+radius_deviation)
        min_wirelength      = average_wirelength * (1.0-radius_deviation)
        
        self.bounding_radius = max_wirelength
        
        number_dendrites    = random.randint(min_branches, max_branches)
        heading_spacing     = 360.0 / number_dendrites
        heading             = 0.0
        active_dendrites    = []
        self.all_dendrites  = []
        for i in range(number_dendrites):
            wirelength = random.uniform(min_wirelength, max_wirelength)
            dendrite = DendriteSegment(self, self.location, heading, wirelength, wirelength)
            active_dendrites.append(dendrite)
            self.all_dendrites.append(dendrite)
            heading += heading_spacing
        
        
        # Update the dendrites, but let's visualize it using pygame
        pygame.init()
        self.display = pygame.display.set_mode((self.retina.grid_width, self.retina.grid_height))
        self.display.fill((255,255,255))
        clock = pygame.time.Clock()
        
        running = True
        while active_dendrites != []:
            i = 0
            while i < len(active_dendrites):
                dendrite = active_dendrites[i]
                is_growing, children = dendrite.grow()
                
                if not(is_growing):
                    del active_dendrites[i]
                    i -= 1
                    
                if children != []:
                    for child in children: 
                        active_dendrites.append(child)
                        self.all_dendrites.append(child)
                    
                i += 1
                
                
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                if not(running): break
                pygame.display.update()
#                clock.tick(30)
            if not(running): break
        
        while running:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            
    
    
    def branchProbability(self, wirelength):
        return -1 * wirelength/self.bounding_radius + 1
        
        
        
        
class DendriteSegment(object):
            
    def __init__(self, neuron, location, heading, resources, original_resources):
        self.neuron             = neuron
        self.heading            = heading
        self.locations          = [location]
        self.collision_info     = []
        self.children           = []     
        self.resources          = resources
        self.original_resources = original_resources
        self.is_growing         = True
        
        self.step_size          = self.neuron.step_size
        self.heading_deviation  = self.neuron.heading_deviation
        
        self.max_growth_attempts = 100
        
#        self.color = (random.randint(100,255), random.randint(100,255), random.randint(100,255))
        self.color = (0,0,0)
        
        
    def grow(self):
        # Check if the dendrite segment has resources left for growth
        if self.resources<self.step_size:
            self.is_growing = False
            return self.is_growing, []
        
        # Check if the dendrite segment should branch
        # It can't branch if it hasn't grown a step (otherwise children could
        # pile up in the same location)
        if len(self.locations) >= 2:
            wirelength      = self.original_resources - self.resources
            rand            = random.random()
            probabilitiy    = self.neuron.branchProbability(wirelength)
            if rand<probabilitiy:
                self.children   = self.spawnChildren()
                self.is_growing = False
                return self.is_growing, self.children
        
        # Attempt to grow dendrite segment
        last_location       = self.locations[-1]
        collision_exists    = True
        number_attempts     = 0                                                    
        while collision_exists:
            # Generate a new location
            new_heading     = self.heading + random.uniform(-self.heading_deviation, self.heading_deviation)
            vector_heading  = np.array([np.cos(np.deg2rad(new_heading)), np.sin(np.deg2rad(new_heading))])
            new_location    = last_location + vector_heading * self.step_size
            new_location    = np.around(new_location)   # Snap to retinal grid
            
            # Calculate collision detection information
            radius = linearDistance(new_location, last_location) / 2.0
            midpoint = (new_location + last_location) / 2.0
            slope, y_intercept = self.solveLine(last_location, new_location)
            
            # Check for collisions
            collision_exists = self.checkCollisions(last_location, new_location,
                                                    radius, midpoint, slope,
                                                    y_intercept)
            
            number_attempts += 1
            if number_attempts >= self.max_growth_attempts:
                self.is_growing = False
                return self.is_growing, []
                
        # Successful growth
        self.heading = new_heading
        self.resources -= self.step_size
        self.locations.append(new_location)
        self.collision_info.append([radius, midpoint, slope, y_intercept])
        
        pygame.draw.line(self.neuron.display, self.color, last_location, new_location, 1)
        
        return self.is_growing, []
    
    
    # Solve the line equation for two given points
    # If the line is vertical, set the slope and intercept to None
    def solveLine(self, p1, p2):
        delta_x = p2[0] - p1[0]
        delta_y = p2[1] - p1[1]
        if delta_x == 0: 
            slope       = None
            y_intercept = None
        else:
            slope       = delta_y/delta_x
            y_intercept = p1[1] - slope * p1[0]
        return slope, y_intercept
        
    # Given a dendrite segment (defined by two points), check to see if it will
    # intersect with any existing dendrite segments
    def checkCollisions(self, point_a, point_b, radius, midpoint, slope, y_intercept):
    
        # Check each other dendrite segment
        for other in self.neuron.all_dendrites:
            
            # If the other has more than 1 location, check each consecutive pair of locations
            number_other_locations = len(other.locations)
            if number_other_locations >= 2:
                            
                # If the other neuron is myself, then do not check the last pair of points
                # (These will always show a collision since they share a point)
                start_index = 0
                if other == self:
                    end_index = number_other_locations - 3
                else:
                    end_index = number_other_locations - 2
                
                for i in range(start_index, end_index+1): 
                    
                    # Check whether circle bounding boxes intersect
                    other_collision_info    = other.collision_info[i]
                    other_radius            = other_collision_info[0]
                    other_midpoint          = other_collision_info[1]
                    min_circle_distance     = radius + other_radius
                    dist_between_circles    = linearDistance(midpoint, other_midpoint)
                    if dist_between_circles <= min_circle_distance:
                        
                        # Check whether the line segments intersect
                        other_point_a        = other.locations[i]
                        other_point_b        = other.locations[i+1]
                        other_slope          = other_collision_info[2]
                        other_y_intercept    = other_collision_info[3]
                        
                        # Not parallel
                        if slope != other_slope:
                            # I am a vertical line                            
                            if slope == None:
                                # My equation is x = c, so the x coord of intersection
                                # has to be equal to the x coord of either of my points
                                x = point_a[0]
                                # Other equation is y=mx+b, so plug x in and solve
                                y = other_slope * x + other_y_intercept
                                
                            # Other is a vertical line
                            elif other_slope == None:
                                # Other equation is x = c, so the x coord of intersection
                                # has to be equal to the x coord of either of my points
                                x = other_point_a[0]
                                # My equation is y=mx+b, so plug x in and solve
                                y = slope * x + y_intercept
                                                    
                            else:
                                # Find the intersection
                                x = (other_y_intercept - y_intercept) / (slope - other_slope)
                                y = slope * x + y_intercept
                            
                            intersection_point = np.array((x,y))
                            
                            intersect_on_self = linearDistance(midpoint, intersection_point) <= radius
                            if intersect_on_self:
                                intersect_on_other = linearDistance(other_midpoint, intersection_point) <= other_radius
                            
                                if intersect_on_other:
                                    return True
        return False    
    
    def spawnChildren(self):
        last_location   = self.locations[-1]
        child_1_heading = self.heading - self.heading_deviation 
        child_2_heading = self.heading + self.heading_deviation
        child_1 = DendriteSegment(self.neuron, last_location, child_1_heading,
                                  self.resources, self.original_resources)
        child_2 = DendriteSegment(self.neuron, last_location, child_2_heading,
                                  self.resources, self.original_resources)
        return [child_1, child_2]
        
    def __str__(self):
        string = ""
        string += "\n"+str(self.heading)
        string += "\n"+str(self.original_resources)
        for loc in self.locations:
            string += "\n"+str(loc)
        return string
              
def linearDistance(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5
       
class Location(object):
    """This class specifies methods for handling retinal grid locations.
    """
    def __init__(self, x, y):
        self.x = int(round(x))
        self.y = int(round(y))
        
    @property
    def xfloat(self):
        return float(self.x)
    
    @property
    def yfloat(self):
        return float(self.y)
        
    @property
    def ID(self):
        return self.x, self.y        
        
    def distFrom(self, location):
        x1 = location.x
        y1 = location.y
        x2 = self.x
        y2 = self.y
        return ((x2-x1)**2 + (y2-y1)**2)**0.5
        
