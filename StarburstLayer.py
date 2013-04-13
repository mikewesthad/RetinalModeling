from random import randint, choice
import math as m
import numpy as np
import pygame
from pygame import *
from Starburst import Starburst
from Constants import *
from Vector2D import *


class StarburstLayer:
    
    def __init__(self, retina, starburst_type, bipolar_layer, history_size,
                 input_delay, nearest_neighbor_distance, minimum_required_density,
                 number_morphologies=10, visualize_growth=True, display=None):
                     
        self.retina             = retina
        self.bipolar_layer      = bipolar_layer
        self.starburst_type     = starburst_type

        self.history_size   = history_size
        self.input_delay    = input_delay
    
        self.nearest_neighbor_distance = nearest_neighbor_distance / retina.grid_size
        
        self.minimum_required_density   = minimum_required_density
        self.minimum_required_cells     = int(minimum_required_density * (retina.area/retina.density_area))
        
        print "Placing somas..."
        self.placeNeurons()
        self.neurons = len(self.locations)
        print "Placed"
        
        print "Growing cells..."
        unique_morphologies = []
        for i in range(number_morphologies):
            unique_starburst = Starburst(retina, self.locations[i], visualize_growth=False)
            unique_morphologies.append(unique_starburst)
            print "Generated {0} of {1} unique cells".format(i+1, number_morphologies)
        print "Grown"
        
        print "Copying cells..."
        self.starburst_cells = set()
        for i in range(self.neurons):
            unique_starburst = choice(unique_morphologies)
            starburst_copy = unique_starburst.createCopy()
            new_location = self.locations[i]
            starburst_copy.moveTo(new_location)
            self.starburst_cells.add(starburst_copy)
        print "Copied"
        
        
        self.inputs = {}
        
        self.initializeActivties()
        self.establishInputs()
    
    def draw(self, display):
        for starburst in self.starburst_cells:
            starburst.draw(display)
    
    def initializeActivties(self):
        self.activities = []
        for i in range(self.history_size):
            self.activities.append(np.zeros((1, self.neurons)))   
            
    def updateActivity(self):
        pass
    
    def establishInputs(self):
        pass

    def inputWeightingFunction(self, inputs):
        pass
        
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
        xmax = self.retina.grid_width
        ymax = self.retina.grid_height

        # Convert the minimum distance from world units to grid units
        gridded_distance        = self.nearest_neighbor_distance
        ceil_gridded_distance   = int(m.ceil(gridded_distance))
        
        # Calculate the number of cells to place
        required_cells = self.minimum_required_cells
        current_cells  = 0

        # Create empty sets to hold the selected positions and the excluded positions
        excluded_positions = set()
        self.locations = []

        while current_cells < required_cells:

            # Pick a random point
            x = randint(xmin, xmax)
            y = randint(ymin, ymax)
            p = Vector2D(x, y)
            p_ID = p.toTuple()
            
            # Regenerate random point until a valid point is found
            rand_tries = 0
            while p_ID in excluded_positions:
                x = randint(xmin, xmax)
                y = randint(ymin, ymax)
                p = Vector2D(x, y)
                p_ID = p.toTuple()
                
                rand_tries += 1
                if rand_tries > max_rand_tries: break

            # If too many attempts were made to generate a new point, exit loop
            if rand_tries > max_rand_tries: break    

            # Update the sets with the newly selected point
            excluded_positions.add(p_ID)
            self.locations.append(p)

            # Find the bounding box of excluded coordinates surrounding the new point
            left    = max(x - ceil_gridded_distance, xmin)
            right   = min(x + ceil_gridded_distance, xmax)
            up      = max(y - ceil_gridded_distance, ymin)
            down    = min(y + ceil_gridded_distance, ymax)

            # Check if each point in the bounding box is within the minimum distance radius
            # If so, add it to the exclusion set
            for x2 in range(left, right+1):
                for y2 in range(up, down+1):
                    p2 = Vector2D(x2, y2)
                    if p.distanceTo(p2) < gridded_distance:
                        excluded_positions.add(p2.toTuple())

            current_cells += 1

        
    def __str__(self):
        string = ""
        string += "Starburst {0} Layer\n".format(self.starburst_type)
        string += "\nNearest Neightbor Distance (um)\t\t{0}".format(self.nearest_neighbor_distance * M_TO_UM)
        string += "\nMinimum Required Density (cells/mm^2)\t{0}".format(self.minimum_required_density)
        string += "\nNumber of Neurons\t\t\t{0}".format(self.neurons)
        string += "\nInput Delay (timesteps)\t\t\t{0}".format(self.input_delay)
        return string