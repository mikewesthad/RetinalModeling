import random
import numpy as np
import pygame
from pygame.locals import *
from Retina import Retina
from Constants import *

class Neuron(object):
    
    def __init__(self, retina, location, average_wirelength=150*UM_TO_M, radius_deviation=.1,
                 min_branches=6, max_branches=6, heading_deviation=30, step_size=10*UM_TO_M,
                 dendrite_vision_radius=30*UM_TO_M):
        
        self.retina     = retina
        self.location   = np.array(location) / self.retina.grid_size
        
        self.heading_deviation  = heading_deviation
        self.step_size          = step_size / self.retina.grid_size
        
        average_wirelength  = average_wirelength / self.retina.grid_size
        max_wirelength      = average_wirelength * (1.0+radius_deviation)
        min_wirelength      = average_wirelength * (1.0-radius_deviation)
        
        self.bounding_radius = max_wirelength
        
        self.dendrite_vision_radius = dendrite_vision_radius / self.retina.grid_size
        
        number_dendrites    = random.randint(min_branches, max_branches)
        heading_spacing     = 360.0 / number_dendrites
        heading             = 0.0
        active_dendrites    = []
        self.all_dendrites  = []
        for i in range(number_dendrites):
            wirelength = random.uniform(min_wirelength, max_wirelength)
            dendrite = DendriteSegment(self, self.location, heading, wirelength, wirelength,
                                       self.dendrite_vision_radius)
            active_dendrites.append(dendrite)
            self.all_dendrites.append(dendrite)
            heading += heading_spacing
        
        
        # Update the dendrites, but let's visualize it using pygame
        pygame.init()
        self.display = pygame.display.set_mode((self.retina.grid_width, self.retina.grid_height))
        
        # Mainloop!
        next_move   = True
        running     = True
        i           = 0
        while active_dendrites != []:
            self.display.fill((255,255,255))
            
            if next_move:
#                next_move = False
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
                
                if i >= len(active_dendrites): i=0
                if len(active_dendrites) == 0: break
            

            
            for dendrite in self.all_dendrites:
                draw_allowable = False
                if dendrite == active_dendrites[i]: draw_allowable = True
                dendrite.draw(draw_allowable)
                
            for event in pygame.event.get():
                if event.type == QUIT: running = False
                if event.type == KEYDOWN: next_move = True
            if not(running): break
        
            pygame.display.update()


        self.checkDendritesForCollisions()
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            for dendrite in self.all_dendrites:
                dendrite.draw()
            pygame.display.update()
            if not(running): break
    
    
    
    def checkDendritesForCollisions(self):
        for dendrite in self.all_dendrites:
            for other in self.all_dendrites:
                for s in range(len(dendrite.locations)-2):
                    for o in range(len(other.locations)-2):
                        a = dendrite.locations[s]
                        b = dendrite.locations[s+1]
                        c = other.locations[o]
                        d = other.locations[o+1]
                        
                        if not(np.allclose(a,c) or np.allclose(a,d) or np.allclose(b,c) or np.allclose(b,d)):
                            collide, point = collisionDetect(a, b, c, d)
                            if collide:
                                print point
                                print a,b
                                print c,d
                                print
        print "Done"
    
    def branchProbability(self, wirelength):
#        return 0
        return -1.5 * wirelength/self.bounding_radius + 1
        
        
        
        
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
        
        self.color = (random.randint(100,255), 0, random.randint(100,255))
        
        
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
            # No resources left, time to die.
            self.is_growing = False
            return self.is_growing, []
            
        # Calculate the headings to which you can travel
        allowable_range = self.buildAllowableHeadingRange()
        
        # If you can't travel anywhere, die.
        if allowable_range == []:
            self.is_growing = False
            return self.is_growing, []
            
        # So, you've got enough resources to grow AND you have some possible 
        # directions you can grow.  Hot stuff.
        # We should check you should branch and have children.
        if len(self.locations) >= 2:
            # You should also have grown a step before being allowed to branch,
            # otherwise dendrites could start piling up in one location without moving
            wirelength      = self.original_resources - self.resources
            rand            = random.random()
            probabilitiy    = self.neuron.branchProbability(wirelength)
            if rand<probabilitiy:
                # Babies R Us
                self.children   = self.spawnChildren()
                self.is_growing = False
                return self.is_growing, self.children

        # Okay, whatever, you didn't die or procreate, so you can grow. (alone.)
        
        # Pick a new heading angle
        self.heading = generateRandomInAllowableRanges(allowable_range)
        # Find the unit vector that represents that angle
        cos_heading         = np.cos(np.deg2rad(self.heading))
        sin_heading         = np.sin(np.deg2rad(self.heading))
        vector_direction    = np.array([cos_heading, sin_heading])
        # Move in that vector direction by your step_size
        old_location = self.locations[-1] 
        new_location = old_location + vector_direction * self.step_size
        # Find the distance you traveled
        distance = linearDistance(old_location, new_location)
        # Update your internals
        self.resources -= distance
        self.locations.append(new_location)
        self.circle_bounds.append([distance/2.0, (old_location+new_location)/2.0])
        
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
    def buildAllowableHeadingRange(self):            
        # Get the circular bounding box that describes the locations I will avoid
        vision_radius = self.vision_radius
        vision_center = self.locations[-1]
        
        # Find my allowed heading ranges (based on my ability to turn as defined by heading_deviation)
        allowable_headings = calculateHeadingRange(self.heading, self.heading_deviation)        
        
        # For each dendrite in the neuron
        for other in self.neuron.all_dendrites:
            
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
                distance_between_circles    = linearDistance(vision_center, line_segment_center)
                if distance_between_circles <= collision_circle_distance:
                    
                    # Now find the angle from myself to each of the line segment endpoints
                    a = other.locations[i]
                    b = other.locations[i+1]
                    
                    # CAVEAT: If one of my points is also one of the line segment
                    # endpoints, then the atan2 will return 0 which will throw off
                    # the range of exluded angles.
                    # WORKAROUND: Hacky, but just use the midpoint of the line
                    # segment.
                    if np.array_equal(a, vision_center): a = line_segment_center
                    if np.array_equal(b, vision_center): b = line_segment_center
                    
                    # Calculate the angles
                    vector_to_a = a - vision_center
                    vector_to_b = b - vision_center
                    angle_to_a = np.arctan2(vector_to_a[1], vector_to_a[0]) * 180.0/np.pi
                    angle_to_b = np.arctan2(vector_to_b[1], vector_to_b[0]) * 180.0/np.pi
                    
                    # Unwrap the angles into [0-360]                    
                    if angle_to_a < 0: angle_to_a += 360   
                    if angle_to_b < 0: angle_to_b += 360
                    
                    # Find the range
                    if angle_to_a > angle_to_b: 
                        angle_max = angle_to_a
                        angle_min = angle_to_b
                    else:
                        angle_max = angle_to_b
                        angle_min = angle_to_a
                    
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
    
    """
    Create two children DendriteSegments that:
        Have the same resources as the parent DendriteSegment
        That have initial headings separated by 2*heading_deviation
    """
    def spawnChildren(self):
        last_location   = self.locations[-1]
        child_1_heading = self.heading - self.heading_deviation 
        child_2_heading = self.heading + self.heading_deviation
        child_1 = DendriteSegment(self.neuron, last_location, child_1_heading,
                                  self.resources, self.original_resources, self.vision_radius)
        child_2 = DendriteSegment(self.neuron, last_location, child_2_heading,
                                  self.resources, self.original_resources, self.vision_radius)
        return [child_1, child_2]
      
    """
    Visualization function
    """
    def draw(self, draw_allowable=False):
        if (draw_allowable):
            last = self.locations[-1]
            pygame.draw.circle(self.neuron.display, (255,0,0), last.astype(int), int(self.vision_radius), 1)
            allowable_range = self.buildAllowableHeadingRange()
            for heading_min, heading_max in allowable_range:
                rad_min = np.deg2rad(heading_min)
                rad_max = np.deg2rad(heading_max)
                heading_min_point = last + np.array([np.cos(rad_min)*self.vision_radius, np.sin(rad_min)*self.vision_radius])
                heading_max_point = last + np.array([np.cos(rad_max)*self.vision_radius, np.sin(rad_max)*self.vision_radius])
                pygame.draw.polygon(self.neuron.display, (200,200,255), [last, heading_min_point, heading_max_point]) 
                
        start_index = 0
        end_index = len(self.locations) - 2
        for i in range(start_index, end_index+1): 
            a = self.locations[i]
            b = self.locations[i+1]
            pygame.draw.line(self.neuron.display, self.color, a, b, 1)       
             
             
             
             
"""
Straight line distance in 2D
(Faster than using numpy and faster than using math module)
"""
def linearDistance(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5

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
    rand = random.uniform(0, totalAngle)
    
    # Loop back through the input ranges and find where that randomly 
    # generate degree "lives"
    totalAngle = 0.0
    for i in allowableRanges:
        if totalAngle < rand < totalAngle + i[1] - i[0]:
            return i[0]+rand-totalAngle
        totalAngle += i[1] - i[0]        
    
"""
Solve the line equation for two given points
If the line is vertical, set the slope and intercept to None
"""
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
    
    
"""
Perform a two-level collision detection on two line segments, AB and CD
    Check if circles that bound AB and CD collide
    If so, then check if the segments AB and CD collide
        Find the lines defined by AB and CD
        Check if slopes are parallel
        If not, find the intersection point of the lines
        If the intersection point is within the circles defined by AB and CD,
            then you have a collision
"""
def collisionDetect(point_a, point_b, point_c, point_d):    
    r_ab        = linearDistance(point_a, point_b) / 2.0
    mid_ab      = (point_a + point_b) / 2.0
    m_ab, b_ab  = solveLine(point_a, point_b)
    
    r_cd        = linearDistance(point_c, point_d) / 2.0
    mid_cd      = (point_c + point_d) / 2.0
    m_cd, b_cd  = solveLine(point_c, point_d)
    
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



# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina      = Retina(width, height, grid_size)
startburst  = Neuron(retina, (500 * UM_TO_M, 500 * UM_TO_M))