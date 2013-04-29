import random
import math as m
import numpy as np
from Constants import *
from Vector2D import Vector2D

class BipolarLayer:
    
    def __init__(self, retina, bipolar_type, cone_layer, horizontal_layer, history_size,
                 input_delay, nearest_neighbor_distance, minimum_required_density,
                 input_field_radius, output_field_radius):
                     
        self.retina             = retina
        self.cone_layer         = cone_layer
        self.horizontal_layer   = horizontal_layer
        self.bipolar_type       = bipolar_type

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
        
        # Hack to keep the structure of IDs = "x.y" (current visualization needs IDs of this structure)
        self.triad_locations = {}
        
#        self.calculateReceptiveFieldPoints()
#        print len(self.receptive_field_points)
#        dfs
        self.initializeActivties()
        self.establishInputs()
    
    
    def calculateReceptiveFieldPoints(self):
        self.receptive_field_points = set()
        center = Vector2D(0.0, 0.0)
        radius = self.output_field_radius_gridded
        for dx in range(int(radius)):
            for dy in range(int(radius)):
                new_position = Vector2D(dx, dy)
                if center.distanceTo(new_position) < radius:
                    self.receptive_field_points.add(new_position.toTuple())
                    
                    
    
    def registerWithRetina(self):
        for loc_ID in self.triad_locations:
            neuron_x, neuron_y = map(float, loc_ID.split("."))
            compartment.registerWithRetina(self, self.layer_depth)
            
    def __str__(self):
        string = ""
        string += "Bipolar " + self.bipolar_type + " Layer\n"
        string += "\nNearest Neightbor Distance (um)\t\t"+str(self.nearest_neighbor_distance * M_TO_UM)
        string += "\nInput Field Radius\t\t\t"+str(self.input_field_radius * M_TO_UM)
        string += "\nMinimum Required Density (cells/mm^2)\t"+str(self.minimum_required_density)
        string += "\nNumber of Neurons\t\t\t"+str(self.neurons)
        string += "\nInput Delay (timesteps)\t\t\t"+str(self.input_delay)
        return string    
            
    def updateActivity(self):

        del self.activities[-1]
        currentActivities = np.zeros((1, self.neurons))
        
        cone_activities         = self.cone_layer.activities[self.input_delay]
        horizontal_activities   = self.horizontal_layer.activities[self.input_delay]
        
        for n in range(self.neurons):
            x, y                = self.locations[n]
            loc_ID              = str(x)+"."+str(y)
            connected_triads    = self.inputs[loc_ID]
            bipolar_activity    = 0.0
            
            for triad in connected_triads:
                triad_ID, triad_weight  = triad
                triad_number            = self.triad_locations[triad_ID]
                cone_activity           = cone_activities[0, triad_number]
                horizontal_activity     = horizontal_activities[0, triad_number]
                
                if self.bipolar_type == "On":
                    triad_activity = -(cone_activity - horizontal_activity)/2.0  
                else: 
                    triad_activity = (cone_activity - horizontal_activity)/2.0
                
                bipolar_activity += triad_weight * triad_activity
            
            currentActivities[0, n] = bipolar_activity
        
        self.activities.insert(0, currentActivities)
        
        return currentActivities
    
    """
    Hacked
    """
    def establishInputs(self):
        self.inputs = {}
        radius = self.input_field_radius_gridded
        number_triads = len(self.cone_layer.locations)
        for x, y in self.locations:
            
            connected_triads = []
            for triad_number in range(number_triads):                
                triad_x, triad_y = self.cone_layer.locations[triad_number]
                if linearDistance(x, y, triad_x, triad_y) < radius:
                    triad_ID        = str(triad_x)+"."+str(triad_y)
                    triad_weight    = 1.0
                    self.triad_locations[triad_ID] = triad_number                    
                    connected_triads.append([triad_ID, triad_weight])
            
            loc_ID = str(x)+"."+str(y)
            if connected_triads == []: 
                self.inputs[loc_ID] = []
            else:
                connected_triads    = self.inputWeightingFunction(connected_triads)
                self.inputs[loc_ID] = connected_triads

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
        
        
    def initializeActivties(self):
        self.activities = []
        for i in range(self.history_size):
            self.activities.append(np.zeros((1, self.neurons)))   
        
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