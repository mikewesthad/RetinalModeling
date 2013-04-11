import random
import numpy as np
from Constants import *

import pygame
from pygame.locals import *

class Neuron(object):
    
    def __init__(self, retina, location, average_wirelength=300*UM_TO_M, radius_deviation=.1,
                 min_branches=10, max_branches=10, heading_deviation=45, step_size=20*UM_TO_M,
                 dendrite_vision_radius=50*UM_TO_M):
        
        self.retina     = retina
        self.location   = np.array(location) / self.retina.grid_size
        
        self.heading_deviation  = heading_deviation
        self.step_size          = step_size / self.retina.grid_size
        
        average_wirelength  = average_wirelength / self.retina.grid_size
        max_wirelength      = average_wirelength * (1.0+radius_deviation)
        min_wirelength      = average_wirelength * (1.0-radius_deviation)
        
        self.bounding_radius = max_wirelength
        
        dendrite_vision_radius = dendrite_vision_radius / self.retina.grid_size
        
        number_dendrites    = random.randint(min_branches, max_branches)
        heading_spacing     = 360.0 / number_dendrites
        heading             = 0.0
        active_dendrites    = []
        self.all_dendrites  = []
        for i in range(number_dendrites):
            wirelength = random.uniform(min_wirelength, max_wirelength)
            dendrite = DendriteSegment(self, self.location, heading, wirelength, wirelength,
                                       dendrite_vision_radius)
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
                clock.tick(60)
            if not(running): break
        
        while running:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            
    
    
    def branchProbability(self, wirelength):
        return 0
#        return -2 * wirelength/self.bounding_radius + 0.5
        
        
        
        
class DendriteSegment(object):
            
    def __init__(self, neuron, location, heading, resources, original_resources,
                 vision_radius):
        self.neuron             = neuron
        self.heading            = heading
        self.locations          = [location]
        self.circle_bounds      = []
        self.children           = []     
        self.resources          = resources
        self.original_resources = original_resources
        self.is_growing         = True
        self.vision_radius      = vision_radius
        
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
        
        # Calculate the headings to which you cannot travel
        allowable_range = self.buildAllowableHeadingRange()
        
        if allowable_range == []:
            self.is_growing = False
            return self.is_growing, []
            

        # Successful growth
        print allowable_range,
        self.heading = generateRandomInAllowableRanges(allowable_range)
        print self.heading
        print
        old_location = self.locations[-1] 
        new_location = old_location + np.array([np.cos(np.deg2rad(self.heading)), np.sin(np.deg2rad(self.heading))]) * self.step_size
        new_location = np.around(new_location)
        distance = linearDistance(old_location, new_location)
        self.resources -= distance
        self.locations.append(new_location)
        self.circle_bounds.append([distance/2.0, (old_location+new_location)/2.0])
        
        pygame.draw.line(self.neuron.display, self.color, old_location, new_location, 1)
        
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
        

    def buildAllowableHeadingRange(self):
        # What if someone else is just a point?  Should they be ignored?
            
        # Get the circular bounding box that describes the locations I will avoid
        vision_radius = self.vision_radius
        vision_center = self.locations[-1]
        
        allowable_headings = calculateHeadingRange(self.heading, self.heading_deviation)        
        
        # For each dendrite in the neuron
        for other in self.neuron.all_dendrites:
            
            number_other_locations = len(other.locations)
            
            # If the other neuron is myself, then do not check the last pair of 
            # points because they will not cause a collision conflict
            start_index = 0
            if other == self:
                end_index = number_other_locations - 3
            else:
                end_index = number_other_locations - 2
                        
            # Loop through all the line segments that make up the other dendrite
            for i in range(start_index, end_index+1): 
                
                # Get the circular bounding box that contains the line segment
                line_segment_radius = other.circle_bounds[i][0]
                line_segment_center = other.circle_bounds[i][1]
                
                
                # Check if circular bounding box defined by the other line
                # segment intersects with bounding box defined by my visual range                
                collision_circle_distance   = vision_radius + line_segment_radius
                distance_between_circles    = linearDistance(vision_center, line_segment_center)
                
                if distance_between_circles <= collision_circle_distance:
                    
                    # Now check if the line segment collides with the pie-shapped
                    # visual range
                    a = other.locations[i]
                    b = other.locations[i+1]
                                        
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
                    
                    if (angle_max - angle_min) > 180:
                        angles = [[0.0, angle_min], [angle_max, 360.0]]
                    else:
                        angles = [[angle_min, angle_max]]
            
                     
                    for angle_min, angle_max in angles:
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
                        if angle_in_range: 
                            allowable_headings = excludeRange(allowable_headings, [angle_min, angle_max])
        return allowable_headings
    
    def spawnChildren(self):
        last_location   = self.locations[-1]
        child_1_heading = self.heading - self.heading_deviation 
        child_2_heading = self.heading + self.heading_deviation
        child_1 = DendriteSegment(self.neuron, last_location, child_1_heading,
                                  self.resources, self.original_resources, self.vision_radius)
        child_2 = DendriteSegment(self.neuron, last_location, child_2_heading,
                                  self.resources, self.original_resources, self.vision_radius)
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

def excludeRange(allowableRanges, excludeRange):
    eStart  = excludeRange[0]
    eEnd    = excludeRange[1]

    newAllowableRanges = []

    for allowableRange in allowableRanges:
        aStart  = allowableRange[0]
        aEnd    = allowableRange[1]

        # The exclusion range is contained within the allowable range
        if aStart < eStart and aEnd > eEnd:
            newAllowableRanges.append([aStart, eStart])
            newAllowableRanges.append([eEnd, aEnd])

        # The exlusion range does not overlap with the allowable range
        elif aStart > eEnd or aEnd < eStart:
            newAllowableRanges.append([aStart, aEnd])
        
        # The allowable range is contained within the exlusion range
        elif aStart >= eStart and aEnd <= eEnd:
            pass

        # There is a partial overlap between the allowable range and the exclusion range
        else:
            if aStart >= eStart:
                newAllowableRanges.append([eEnd, aEnd])
            elif aEnd <= eEnd:
                newAllowableRanges.append([aStart, eStart])
    return newAllowableRanges

def generateRandomInAllowableRanges(allowableRanges):
    totalAngle = 0.0
    for i in allowableRanges:
        totalAngle += i[1] - i[0]

    rand = random.uniform(0, totalAngle)
    totalAngle = 0.0
    for i in allowableRanges:
        if totalAngle < rand < totalAngle + i[1] - i[0]:
            return i[0]+rand-totalAngle
        totalAngle += i[1] - i[0]        
