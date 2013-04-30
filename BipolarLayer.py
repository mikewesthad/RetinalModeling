import random
import math as m
import numpy as np
import pygame
from Constants import *
from Compartment import Compartment
from Bipolar import Bipolar
from Vector2D import Vector2D

class BipolarLayer:
    
    def __init__(self, retina, bipolar_type, cone_layer, horizontal_layer, history_size,
                 input_delay, layer_depth, nearest_neighbor_distance, minimum_required_density,
                 input_field_radius, output_field_radius):
                     
        self.retina             = retina
        self.cone_layer         = cone_layer
        self.horizontal_layer   = horizontal_layer
        self.bipolar_type       = bipolar_type

        self.history_size   = history_size
        self.input_delay    = input_delay
        self.layer_depth    = layer_depth
    
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
        self.number_neurons = len(self.locations)
        self.neurons = []
        for location in self.locations:
            neuron = Bipolar(self, Vector2D(location[0], location[1]))            
            self.neurons.append(neuron)
        
        self.calculateReceptiveFieldPoints()
        self.compartmentalize()
        
        # Hack to keep the structure of IDs = "x.y" (current visualization needs IDs of this structure)
        self.triad_locations = {}
        self.number_triads = len(self.cone_layer.locations)        
        for triad_number in range(self.number_triads):                
            triad_x, triad_y    = self.cone_layer.locations[triad_number]
            triad_ID            = str(triad_x)+"."+str(triad_y)
            self.triad_locations[triad_ID] = triad_number 
        
        self.compartmentalize()
        self.establishInputs()
    
    
    def establishInputs(self):
        for neuron in self.neurons:
            neuron.establishInputs()
            
    def calculateReceptiveFieldPoints(self):
        self.receptive_field_points = set()
        center = Vector2D(0.0, 0.0)
        radius = self.output_field_radius_gridded
        for dx in range(-int(radius),int(radius)+1):
            for dy in range(-int(radius),int(radius)+1):
                new_position = Vector2D(dx, dy)
                if center.distanceTo(new_position) < radius:
                    self.receptive_field_points.add(new_position)
                    
    def compartmentalize(self):
        self.compartment = Compartment(self)
        self.compartment.neurotransmitters_output_weights = {GLU:1.0}
        self.compartment.gridded_locations = self.receptive_field_points
        for neuron in self.neurons:
            neuron.compartmentalize(self.compartment)
            
    def draw(self, surface, scale=1.0):
        for neuron in range(self.neurons):
            loc = self.locations[neuron]
            pygame.draw.circle(surface, (100,0,0), loc, int(self.nearest_neighbor_distance_gridded/2.0))
#        for compartment in self.compartments:
#            compartment.draw(surface, scale=scale)
            
    def __str__(self):
        string = ""
        string += "Bipolar " + self.bipolar_type + " Layer\n"
        string += "\nNearest Neightbor Distance (um)\t\t"+str(self.nearest_neighbor_distance * M_TO_UM)
        string += "\nInput Field Radius\t\t\t"+str(self.input_field_radius * M_TO_UM)
        string += "\nMinimum Required Density (cells/mm^2)\t"+str(self.minimum_required_density)
        string += "\nNumber of Neurons\t\t\t"+str(self.neurons)
        string += "\nInput Delay (timesteps)\t\t\t"+str(self.input_delay)
        return string
        
    def neurotransmitterToPotential(self, nt):
        if nt < 0: return -1.0
        if nt > 1: return 1.0
        return (nt*2.0)-1.0
    def potentialToNeurotransmitter(self, pt):
        if pt < -1: return 0.0
        if pt > 1: return 1.0
        return (pt+1.0)/2.0
            
    def update(self):
        cone_activities         = self.cone_layer.activities[self.input_delay]
        horizontal_activities   = self.horizontal_layer.activities[self.input_delay]
        
        for neuron in self.neurons:
            neuron.update(cone_activities, horizontal_activities)
        
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