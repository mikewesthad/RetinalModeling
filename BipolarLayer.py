import random
import math as m
import numpy as np
from Constants import *


class BipolarLayer:
    
    def __init__(self, retina, cone_layer, horizontal_layer, history_size,
                 input_delay, nearest_neighbor_distance, minimum_required_density,
                 input_field_radius, output_field_radius):
                     
        self.retina             = retina
        self.cone_layer         = cone_layer
        self.horizontal_layer   = horizontal_layer

        self.history_size   = history_size
        self.input_delay    = input_delay
    
        self.nearest_neighbor_distance          = nearest_neighbor_distance
        self.nearest_neighbor_distance_gridded  = nearest_neighbor_distance / retina.grid_size
        
        self.minimum_required_density   = minimum_required_density
        density_area                    = 1 * MM_TO_M * MM_TO_M
        self.minimum_required_cells     = int(minimum_required_density * (retina.area/density_area))
        
        self.input_field_radius             = input_field_radius
        self.input_field_radius_gridded     = input_field_radius / retina.grid_size
        self.output_field_radius            = output_field_radius
        self.output_field_radius_gridded    = output_field_radius / retina.grid_size
        
        self.placeNeurons()
        self.neurons = len(self.locations)
        
        self.initializeActivties()
        

            
    def updateActivity(self):

        del self.activities[-1]
        currentActivities = np.zeros((1, self.neurons))
        
#        for n in range(self.neurons):
#            x, y = self.locations[n]
#            locID = str(x)+"."+str(y)
#            connectedPixels = self.inputs[locID]
#            coneActivity = 0.0
#            for pixel in connectedPixels:
#                pixelID, pixelWeight = pixel
#                intensity = self.stimulus.getPixelIntensity(pixelID)
#                coneActivity += (intensity*-2.0 + 1.0) * pixelWeight
#            currentActivities[0, n] = coneActivity
            
        self.activities.insert(0, currentActivities)
        
        return currentActivities
            
            
            
            
            

    def initializeActivties(self):
        self.activities = []
        for i in range(self.history_size):
            self.activities.append(np.zeros((1, self.neurons)))
            
    def establishInputs(self):
        for loc_ID in self.locations:
            x, y = loc_ID

            gridded_radius = self.input_field_radius_gridded
            
            left        = x - gridded_radius
            right       = x + gridded_radius
            up          = y - gridded_radius
            down        = y + gridded_radius
            cone_box    = [left, right, up, down]

            connected_pixels = self.stimulus.getPixelOverlaps(cone_box)
            connected_pixels = self.inputWeightingFunction(connected_pixels)
            
            loc_ID = str(x)+"."+str(y)
            self.inputs[loc_ID] = connected_pixels

    def inputWeightingFunction(self, inputs):
        weight_sum = 0.0
        
        for i in range(len(inputs)):
            input_ID, input_weight = inputs[i]
            weight_sum += input_weight
            
        for i in range(len(inputs)):
            input_weight = inputs[i][1]
            input_weight /= weight_sum
            inputs[i][1] = input_weight
        return inputs
        
        
        
    """
    Nearest neighbor distance constrained placement of points
        The method involves tracking point locations and tracking exclusion zones around those points
        Random points are generated until:
            A valid point is found (one that is within the bounds and not located within an exclusion zone
            A maximum number of tries has been exhausted
    """
    def placeNeurons(self, max_rand_tries=1000):
        # Set the bounds on the positions
        xmin = 0
        ymin = 0
        xmax = self.retina.grid_width-1
        ymax = self.retina.grid_height-1

        # Convert the minimum distance from world units to grid units
        gridded_distance        = self.nearest_neighbor_distance_gridded
        ceil_gridded_distance   = int(m.ceil(gridded_distance))

        # Calculate the number of cells to place
        required_cells = self.minimum_required_cells
        current_cells  = 0

        # Create empty sets to hold the selected positions and the excluded positions
        excluded_positions = set()
        self.locations = []

        while current_cells < required_cells:

            # Pick a random point
            x       = random.randint(xmin, xmax)
            y       = random.randint(ymin, ymax)
            loc_ID  = str(x) + "." + str(y)
            
            # Regenerate random point until a valid point is found
            rand_tries = 0
            while loc_ID in excluded_positions:
                x = random.randint(xmin, xmax)
                y = random.randint(ymin, ymax)
                loc_ID = str(x) + "." + str(y)
                
                rand_tries += 1
                if rand_tries > max_rand_tries: break

            # If too many attempts were made to generate a new point, exit loop
            if rand_tries > max_rand_tries: break    

            # Update the sets with the newly selected point
            excluded_positions.add(loc_ID)
            self.locations.append([x, y])

            # Find the bounding box of excluded coordinates surrounding the new point
            left    = max(x - ceil_gridded_distance, xmin)
            right   = min(x + ceil_gridded_distance, xmax)
            up      = max(y - ceil_gridded_distance, ymin)
            down    = min(y + ceil_gridded_distance, ymax)

            # Check if each point in the bounding box is within the minimum distance radius
            # If so, add it to the exclusion set
            for x2 in range(left, right+1):
                for y2 in range(up, down+1):
                    if linearDistance(x, y, x2, y2) < gridded_distance:
                        loc_ID = str(x2) + "." + str(y2)
                        excluded_positions.add(loc_ID)

            current_cells += 1




"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5