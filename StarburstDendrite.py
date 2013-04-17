import numpy as np
import pygame
from copy import deepcopy
from pygame.locals import *
from random import random, uniform
from math import atan2
from DendritePoint import DendritePoint
from Vector2D import Vector2D


class DendriteSegment:
            
    def __init__(self, neuron, location, heading, resources, original_resources,
                 children_deviation, vision_radius):
        self.neuron             = neuron
        self.retina             = neuron.retina
        self.heading            = heading
        self.locations          = [location]
        self.gridded_locations  = []
        self.points             = []
        self.circle_bounds      = []
        self.children           = []     
        self.resources          = resources
        self.original_resources = original_resources
        self.is_growing         = True
        self.vision_radius      = vision_radius
        self.children_deviation = children_deviation
        
        self.length             = 0.0
        self.step_size          = self.neuron.step_size
        self.heading_deviation  = self.neuron.heading_deviation
        
        self.color = (0, 0, 0)

    def createCopy(self, new_starburst, parent_dendrite=None):
        new_dendrite = DendriteSegment(new_starburst, None, self.heading, 
                                       self.resources, self.original_resources, 
                                       self.children_deviation, self.vision_radius)
        new_dendrite.locations          = deepcopy(self.locations)        
        new_dendrite.gridded_locations  = deepcopy(self.gridded_locations)
        new_dendrite.color              = deepcopy(self.color)
        
        new_starburst.dendrites.append(new_dendrite)
        
        if parent_dendrite != None:
            parent_dendrite.children.append(new_dendrite)
        
        if self.children != []:
            for child in self.children:
                child.createCopy(new_starburst, new_dendrite)
        
        return new_dendrite
        
        

    def eraseReferences(self):
        del self.neuron
        del self.retina
        
    def reinitReferences(self, retina, neuron):
        self.retina = retina
        self.neuron = neuron
    
    def compartmentalize(self, compartment, compartment_size_total, compartment_size,
                         dendrite, index):
        pass    
#        comp = compartment 
#    
#        while (num_points_left > 0) and (index < len(dendrite_segment.points)):
#                comp.addDendritePoint(dendrite_segment.points[index])
#                index += 1
#                num_points_left -= 1
#        
#        if (num_points_left > 0) and (index == len(dendrite_segment.points)):
#            #proceed to compartmentalize the children.
#            num_children = len(dendrite_segment.children)        
#            if num_children > 0:
#                #apportion num_points_left over children in integer values.
#                num_needed_each = num_points_left // num_children
#                num_extras_left = num_points_left % num_children            
#                for child in dendrite_segment.children:
#                    if num_extras_left > 0:
#                        extra = 1
#                        num_extras_left -= 1
#                    else:
#                        extra = 0
#                    compartmentalize(comp, num_points_tot, 
#                                     num_needed_each + extra,
#                                     child, 0)
#                    # add to neigh                                     
#            return None
#                  
#        if num_points_left == 0:
#            if index < len(dendrite_segment.points):
#                new_comp = Compartment(comp, comp.neuron, comp.grid)  
#                    # add to neigh          
#                compartmentalize(new_comp, num_points_tot, num_points_tot,
#                                 dendrite_segment, index)
#            else:
#                for child in dendrite_segment.children:
#                    new_comp = Compartment(comp, comp.neuron, comp.grid)      
#                    # add to neigh           
#                    compartmentalize(new_comp, num_points_tot, num_points_tot,
#                                     child, 0)
#            return None
    
    """
    Do one of three things:
        Die.
        Spawn Children. (and die.)
        Grow a little bit. (and die another day.)    
    Returns True/False depending on whether you died and a list of your children
    """ 
    def grow(self):
        # Check if the dendrite segment has resources left for growth
        if self.resources<self.step_size:
            # No resources left, you should die.
            self.is_growing = False
            return self.is_growing, []
            
        # Calculate the headings to which you can travel
        allowable_range = self.buildAllowableHeadingRange(self.heading, self.heading_deviation)
        
        # If you can't travel anywhere, die.
        if allowable_range == []:
            self.is_growing = False
            return self.is_growing, []
            
            
        children = self.attemptToSpawnChildren()
        if children != []:
            self.children = children
            self.is_growing = False
            return self.is_growing, children
        

        # Okay, you didn't die or procreate, so you can grow.
        self.heading = generateRandomInAllowableRanges(allowable_range)
        vector_direction = Vector2D.generateHeadingFromAngle(self.heading)
        old_location = self.locations[-1] 
        new_location = old_location + vector_direction * self.step_size
        distance = self.step_size
        
        # Update your internals
        self.resources -= distance
        self.length += distance
        self.locations.append(new_location)
        
        # Find your circle bounding box
        radius = distance/2.0
        center = (old_location+new_location)/2.0
        self.circle_bounds.append([radius, center])
        
        return self.is_growing, []
        
        
        
    """
    Find the directions the dendrite can safely grow without causing a collision.
    Given a visual range, I want to avoid moving in the direction of any line
    segments of any dendrites.  To accomplish this, generate a list of ranges 
    of allowable headings (defined by my allowed heading_deviation).  Check all 
    other line segments, and as possible collisions are detected, remove the 
    offending headings from the allowable headings list.
        Check if a circle defined by my visual range overlaps with a the
        circular bounding box that defines the other line segments
        If so, then find the angle from my center to each of the points of a
        line segment (the range of angles to exlude)
        If my allowable heading range overlaps with the range of angles to exlude
        then remove them from my allowable heading list      
    """
    def buildAllowableHeadingRange(self, heading, heading_deviation):            
        # Get the circular bounding box that describes the locations I will avoid
        vision_radius = self.vision_radius
        vision_center = self.locations[-1]
        
        # Find my allowed heading ranges (based on my ability to turn as defined by heading_deviation)
        allowable_headings = calculateHeadingRange(heading, heading_deviation)        
        
        # For each dendrite in the neuron
        for other in self.neuron.dendrites:
            
            number_other_locations = len(other.locations)
            
            # If the other neuron is myself, then do not check the last pair of 
            # points because they will not cause a collision conflict
            start_index = 0
            if other == self:   end_index = number_other_locations - 3
            else:               end_index = number_other_locations - 2
                        
            # Loop through all the line segments that make up the other dendrite
            for i in range(start_index, end_index+1): 
                
                # Get the circular bounding box that contains the line segment
                line_segment_radius = other.circle_bounds[i][0]
                line_segment_center = other.circle_bounds[i][1]
                
                # Check if circular bounding box defined by the other line
                # segment intersects with bounding box defined by my visual range                
                collision_circle_distance   = vision_radius + line_segment_radius
                distance_between_circles    = vision_center.distanceTo(line_segment_center)
                if distance_between_circles <= collision_circle_distance:
                    
                    # Now find the angle from myself to each of the line segment endpoints
                    a = other.locations[i]
                    b = other.locations[i+1]
                    
                    # CAVEAT: If one of my points is also one of the line segment
                    # endpoints, then the atan2 will return 0 which will throw off
                    # the range of exluded angles.
                    # WORKAROUND: Hacky, but just use the midpoint of the line
                    # segment.
                    if a == vision_center: a = line_segment_center
                    if b == vision_center: b = line_segment_center
                    
                    # Calculate the angles (angleHeadingTo returns an angle from 0-360)
                    angle_to_a = vision_center.angleHeadingTo(a)
                    angle_to_b = vision_center.angleHeadingTo(b)
                    
                    # Find the range
                    if angle_to_a > angle_to_b: 
                        angle_max, angle_min  = angle_to_a, angle_to_b
                    else:
                        angle_min, angle_max  = angle_to_a, angle_to_b
                    
                    # Find the set(s) that define the exlusion bounds
                    if (angle_max - angle_min) > 180:
                        # The unwrapping process can create discontinuities in the heading range
                        #   If the original range was (10 to -10), the unwrapped range is (10 to 350)
                        #   This is really two ranges [0 to 10] and [350, 360]
                        angles = [[0.0, angle_min], [angle_max, 360.0]]
                    else:
                        angles = [[angle_min, angle_max]]
                    
                    # Check each set of exluded angles against each set of allowable
                    # headings.  If there is any overlap, remove the exluded angles
                    # from the allowable headings list
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
    
    
    
    def attemptToSpawnChildren(self):
        # If you haven't grown a line segment (2 points), then you can't have children
        if len(self.locations) < 2: return []
        
        # If you don't have enough resources left, then you can't have children 
        # but this check has already been performed
        
        # Find the probability of branching based on your current segment length
        random_number           = random()
        probability_threshold   = self.neuron.branchProbability(self.length)
        
        # The odds aren't in your favor...
        if random_number > probability_threshold: return []
        
        # Now let's make sure that your children would be able to grow
        location = self.locations[-1]
        
        # Spawn the first child
        child_1_heading = self.heading - self.children_deviation
        
        # Unwrap the heading bounds into the range [0-360]
        if child_1_heading > 360:   child_1_heading -= 360.0
        if child_1_heading < 0:     child_1_heading += 360.0
        
        child_1 = DendriteSegment(self.neuron, location, child_1_heading, self.resources, 
                                  self.original_resources, self.children_deviation, self.vision_radius)
        child_1.color = self.color                
        # Have the first child take its first step
        is_growing, children = child_1.grow()
        # If the child couldn't take a step, then you don't have room for children
        if not(is_growing):
            return []

        # Repeat the same procedure with a second child
        child_2_heading = self.heading + self.children_deviation

        # Unwrap the heading bounds into the range [0-360]
        if child_2_heading > 360:   child_2_heading -= 360.0
        if child_2_heading < 0:     child_2_heading += 360.0        
        
        child_2 = DendriteSegment(self.neuron, location, child_2_heading, self.resources, 
                                  self.original_resources, self.children_deviation, self.vision_radius)
        child_2.color = self.color
        # Have the second child take its first step
        is_growing, children = child_2.grow()     
        # If the child couldn't take a step, then you don't have room for children
        if not(is_growing):
            return []
            
        # Babies R Us
        return [child_1, child_2]
        
        

    """
    Sample the continuous-regime line segments onto the retinal grid
    Recursively move from dendrite to children to children's children...
    """
    def discretize(self, delta=1.0, range_deltas=[], parent_locations=[]):   
        self.gridded_locations = []
        
        if range_deltas == []:
            range_deltas = np.arange(0.0, self.step_size, delta) 
            
        for i in range(len(self.locations)-1):
            p1 = self.locations[i]
            p2 = self.locations[i+1]
        
            heading_vector = p1.unitHeadingTo(p2)
            
            for d in range_deltas:
                p = p1 + heading_vector * d
                p = p.roundedIntCopy()
                if (p not in self.gridded_locations) and (p not in parent_locations): 
                    self.gridded_locations.append(p)
                    
        for child in self.children:
            child.discretize(delta, range_deltas, self.gridded_locations)
            
            
    def rescale(self, scale_factor):
        for i in range(len(self.locations)):
            self.locations[i] *= scale_factor
        for i in range(len(self.points)):
            self.points[i].location = self.points[i].location * scale_factor
    
    """
    Visualization function
    """
    def draw(self, surface, draw_grid=False):
        if draw_grid:
            for loc in self.gridded_locations:
                world_loc = self.neuron.location + loc
                pygame.draw.circle(surface, self.color, world_loc.toIntTuple(), 2)   
        else:            
            start_index = 0
            end_index = len(self.locations) - 2
            for i in range(start_index, end_index+1): 
                a = self.neuron.location + self.locations[i]
                b = self.neuron.location + self.locations[i+1]
                pygame.draw.line(surface, self.color, a.toIntTuple(), b.toIntTuple(), 1)    
                
             
             
             
"""
Given a heading (0-360) and a maximum heading deviation (0-180; but likely <45),
return a list of continuous [min, max] ranges of headings that fall within that
maximum heading deviation criteria.
"""
def calculateHeadingRange(heading, heading_deviation):
    # Find the heading bounds (assuming heading deviation is positive)
    heading_max = heading + heading_deviation
    heading_min = heading - heading_deviation
    
    # Unwrap the heading bounds into the range [0-360]
    if heading_max > 360:   heading_max -= 360.0
    if heading_min < 0:     heading_min += 360.0
    
    # If the max and min switched places during unwrapping, switch them back
    if heading_min > heading_max:
        heading_max, heading_min = heading_min, heading_max
    
    # Find the set(s) that define the heading bounds
    if heading_max - heading_min > 180:
        # The unwrapping process can create discontinuities in the heading range
        #   If the original range was (10 to -10), the unwrapped range is (10 to 350)
        #   This is really two ranges [0 to 10] and [350, 360]
        allowable_headings = [[0.0, heading_min], [heading_max, 360.0]]
    else:
        allowable_headings = [[heading_min, heading_max]]
    
    return allowable_headings
    
"""
Given a list of continuous [min, max] ranges of headings (allowableRanges) and
a [min, max] (excludeRange), return a new list of headings where the angles 
within the excludeRange have been removed
"""
def excludeRange(allowableRanges, excludeRange):
    
    newAllowableRanges = []
    eStart, eEnd = excludeRange
    
    for aStart, aEnd in allowableRanges:
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

"""
Given a list of continuous [min, max] ranges of headings (allowableRanges), pick
a value from within the combined ranges given.
"""
def generateRandomInAllowableRanges(allowableRanges):
    # Find the total degrees spanned from the combination of all ranges
    totalAngle = 0.0
    for i in allowableRanges:
        totalAngle += i[1] - i[0]
        
    # Generate a random degree from 0 to that total degree
    rand = uniform(0, totalAngle)
    
    # Loop back through the input ranges and find where that randomly 
    # generate degree "lives"
    totalAngle = 0.0
    for i in allowableRanges:
        if totalAngle < rand < totalAngle + i[1] - i[0]:
            return i[0]+rand-totalAngle
        totalAngle += i[1] - i[0]        