from random import randint, choice
from time import clock
import math as m
from Constants import *


class StarburstLayer:
    
    def __init__(self, retina, starburst_type, layer_depth, history_size,
                 input_delay, nearest_neighbor_distance, minimum_required_density,
                 number_morphologies=1, visualize_growth=False, display=None):
                     
        self.retina             = retina
        self.starburst_type     = starburst_type
        self.layer_depth        = layer_depth
        self.history_size       = history_size
        self.input_delay        = input_delay
    
        # Generate unique morphologies
        self.morphologies = []
        for i in range(number_morphologies):
            morphology = StarburstMorphology(retina, history_size=history_size,
                                             visualize_growth=visualize_growth,
                                             display=display)
            self.morphologies.append(morphology)    
        
        # Generate soma locations
        self.nearest_neighbor_distance  = nearest_neighbor_distance / retina.grid_size
        self.minimum_required_density   = minimum_required_density
        self.minimum_required_cells     = int(minimum_required_density * (retina.area/retina.density_area))
        self.placeNeurons()
        self.number_neurons = len(self.locations)
        
        # Instantiate starbursts
        self.neurons = []
        for i in range(self.number_neurons):
            location    = self.locations[i]
            morphology  = choice(self.morphologies)
            starburst   = Starburst(self, morphology, location, starburst_type, input_delay, layer_depth)
            self.neurons.append(starburst)
    
        self.inputs = {}
        
        self.establishInputs()
    
    def draw(self, surface, color=None, scale=1.0):
        if color==None: 
            if self.starburst_type == "On": color = self.retina.on_starburst_color
            if self.starburst_type == "Off": color = self.retina.off_starburst_color
        for neuron in self.neurons:
            neuron.draw(surface, color=color, scale=scale, draw_compartments=True)
            
    def update(self):
        layer_activity = []
        for neuron in self.neurons:
            neuron_activity = neuron.update()
            layer_activity.append(neuron_activity)
        return layer_activity 
    
    def establishInputs(self):
        for neuron in self.neurons:
            neuron.establishInputs()

    def inputWeightingFunction(self, inputs):
        pass
    
    def neurotransmitterToPotential(self, nt):
        if nt < 0: return -1.0
        if nt > 1: return 1.0
        return (nt*2.0)-1.0
    def potentialToNeurotransmitter(self, pt):
        if pt < -1: return 0.0
        if pt > 1: return 1.0
        return (pt+1.0)/2.0
        
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