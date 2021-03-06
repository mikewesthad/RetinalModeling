from random import uniform, randint, shuffle, choice
from igraph import Graph, ADJ_UNDIRECTED
import matplotlib.pyplot as plt
import numpy as np
import pygame
from pygame.locals import *
from Vector2D import Vector2D
from StarburstDendrite import DendriteSegment
from Compartment import Compartment
from Constants import *


class StarburstMorphology(object):
    
    def __init__(self, retina, location=Vector2D(0.0, 0.0), average_wirelength=150*UM_TO_M, 
                 radius_deviation=.1, min_branches=6, max_branches=6, heading_deviation=10, 
                 step_size=10*UM_TO_M, max_segment_length=35*UM_TO_M, children_deviation=20, 
                 dendrite_vision_radius=30*UM_TO_M, diffusion_width=0.5,
                 decay_rate=0.1, input_strength=0.0, color_palette=GOLDFISH, 
                 draw_location=Vector2D(0.0,0.0), visualize_growth=True, scale=1.0,
                 display=None):
        
        # General neuron variables
        self.retina             = retina
        self.display            = display
        self.location           = location
        
        # Visualization variables
        self.visualize_growth   = visualize_growth
        self.display            = display 
        self.background_color   = color_palette[0]
        self.draw_location      = draw_location
        self.scale              = scale
            
        grid_size               = retina.grid_size
    
        # Wirelength variables
        average_wirelength      = average_wirelength / grid_size
        max_wirelength          = average_wirelength * (1.0+radius_deviation)
        min_wirelength          = average_wirelength * (1.0-radius_deviation)
        self.bounding_radius    = max_wirelength
        
        # Dendrite variables
        self.heading_deviation      = heading_deviation
        self.step_size              = step_size / grid_size
        self.max_segment_length     = max_segment_length / grid_size
        self.dendrite_vision_radius = dendrite_vision_radius / grid_size
        
        # Initialize the first branches
        number_dendrites    = randint(min_branches, max_branches)
        heading_spacing     = 360.0 / number_dendrites
        heading             = 0.0
        
        self.dendrites = []
        for i in range(number_dendrites):
            wirelength = uniform(min_wirelength, max_wirelength)
            dendrite = DendriteSegment(self, self.location, heading, wirelength, wirelength,
                                       children_deviation, self.dendrite_vision_radius)
            self.dendrites.append(dendrite)
            heading += heading_spacing
        
        # Slicing needed to force a copy of the elements (instead of creating a reference to a list)
        # Note: this only works if the lists are not nested (if they are, use deepcopy)
        self.master_dendrites = self.dendrites[:]  
            
        self.grow()      
        self.colorDendrites(color_palette[1:])  
        self.discretize(1.0)
        self.createPoints()
        self.establishPointSynapses()
        self.compartmentalize(30)
        self.colorCompartments(color_palette[1:])
        self.establishCompartmentSynapses()
        self.buildCompartmentBoundingPolygons()
        
        
        self.decay_rate         = decay_rate
        self.input_strength     = input_strength
        self.diffusion_width    = diffusion_width #Units
        self.establisthDiffusionWeights()
    
    def grow(self):
        active_dendrites = self.master_dendrites[:]
        running = True
        i = 0
        clock = pygame.time.Clock()
        while running and active_dendrites != []:
            
            # Grab a dendrite and update it
            dendrite = active_dendrites[i]
            is_growing, children = dendrite.grow()
            
            # If it isn't growing, delete it and adjust index
            if not(is_growing):
                del active_dendrites[i]
                i -= 1
            
            # If it had children, add them to the active list                 
            if children != []:
                for child in children: 
                    active_dendrites.insert(0, child)
                    self.dendrites.append(child)
            
            # Increment index
            i += 1
            if i >= len(active_dendrites): i=0
            
            if self.visualize_growth:
                self.display.fill(self.background_color)
                self.draw(self.display, new_location=self.draw_location,
                          draw_segments=True, scale=self.scale)
                pygame.display.update()
                clock.tick(30)
                    
                # Check for close button signal from pygame window
                for event in pygame.event.get():
                    if event.type == QUIT: running = False
                    
    def colorCompartments(self, palette):
        colors = palette
        
        index = 0
        for compartment in self.master_compartments:
            compartment.colorCompartments(colors, index)
            index += 1
            if index >= len(colors): index = 0
            
    def colorDendrites(self, palette):
        colors = palette
        
        index = 0
        for dendrite in self.master_dendrites:
            dendrite.colorDendrites(colors, index)
            index += 1
            if index >= len(colors): index = 0
            
    def establisthDiffusionWeights(self):
        self.buildGraph()
        self.distances = self.findShortestPathes()
        
        # Perform e^(-distance**2/width) on each element in the distance matrix
        sigma = self.diffusion_width
        self.diffusion_weights = np.exp(-(self.distances)**2/(2.0*sigma**2.0))
        
        # Get the sum of each row
        row_sum = np.sum(self.diffusion_weights, 1)
        
        # Reshape the rowSum into a column vector since sum removes a dimension
        row_sum.shape = (len(self.compartments), 1)
        
        # Normalize the weight matrix
        self.diffusion_weights = self.diffusion_weights / row_sum
        
    def findShortestPathes(self):
        shortest_pathes = np.array(self.graph.shortest_paths())
        # Directly connect each compartment with itself (0 distance)
        for i in range(len(self.compartments)):
            shortest_pathes[i, i] = 0
        return shortest_pathes
    
    def buildGraph(self):
        adjacency = []
        for compartment in self.compartments:
            row = []
            for other_compartment in self.compartments:
                proximal_neighbors  = (compartment in other_compartment.proximal_neighbors)
                distal_neighbors    = (compartment in other_compartment.distal_neighbors)
                if proximal_neighbors or distal_neighbors:
                    row.append(1)
                else:
                    row.append(0)
            adjacency.append(row)
        self.adjacency  = adjacency
        self.graph      = Graph.Adjacency(adjacency, mode=ADJ_UNDIRECTED)
    
    def buildCompartmentBoundingPolygons(self):
        for compartment in self.compartments:
            compartment.buildBoundingPolgyon()
            
    def establishCompartmentSynapses(self):
        for compartment in self.compartments:
            compartment.buildNeurotransmitterWeights()
    
    def establishPointSynapses(self):
        inputs  = set([GLU])
        outputs = set([GABA, ACH])
        
        output_threshold_wirelength = 2.0/3.0 * self.bounding_radius
        
        for point in self.points:
            if point.wirelength >= output_threshold_wirelength:
                point.neurotransmitters_released = outputs.copy() # SHALLOW COPY!
            point.neurotransmitters_accepted = inputs.copy() # SHALLOW COPY!
        
    

    def compartmentalize(self, compartment_size):
        self.compartments = []
        
        # Build the master compartments recursively
        self.master_compartments = []
        for dendrite in self.master_dendrites:            
            compartment = Compartment(self)
            self.master_compartments.append(compartment)

        # Recursively compartmentalize starting from the master compartments
        for index in range(len(self.master_compartments)):
            compartment = self.master_compartments[index]
            
            proximal_compartments = []
            for other_compartment in self.master_compartments:
                if compartment != other_compartment: 
                    proximal_compartments.append(other_compartment)
            
            dendrite = self.master_dendrites[index]
            dendrite.compartmentalize(compartment, compartment_size, compartment_size,
                                      prior_compartments=proximal_compartments)
    
    def discretize(self, delta):
        for dendrite in self.master_dendrites:
            dendrite.discretize(delta=delta)
    
    def createPoints(self):
        self.points = []
        for dendrite in self.master_dendrites:
            dendrite.createPoints(self.location, 0.0)
            
    def draw(self, surface, scale=1.0, new_location=None, draw_segments=False,
             draw_compartments=False, draw_points=False):
        
        # Shift the cell's location
        if new_location == None: 
            new_location = self.location
        old_location = self.location
        self.location = new_location   
        
        if draw_segments:
            for dendrite in self.dendrites:
                dendrite.draw(surface, scale=scale)
        elif draw_compartments:
            for compartment in self.compartments:
                compartment.draw(surface, scale=scale)
        elif draw_points:
            for point in self.points:
                point.draw(surface, scale=scale)
                
        # Shift the cell's location back to the original
        self.location = old_location
    
    def plotBranchProbability(self):
        xs = np.arange(0, self.max_segment_length, 0.1)
        ys = [self.branchProbability(x) for x in xs]
        plt.plot(xs,ys)
        plt.title("Branching as a Function of Wirelength")
        plt.xlabel("Fraction of Max Wirelength")
        plt.ylabel("Branch Probability")
        plt.grid(True)
        plt.show()
    
    def branchProbability(self, segment_length):
        return 1.05**(segment_length-self.max_segment_length)
        
  



# .............................................................................
# Old functions that may not be used?
# .............................................................................
    def rescale(self, scale_factor):
        for dendrite in self.dendrites:
            dendrite.rescale(scale_factor)
            
    def findCentroid(self):
        average_location = Vector2D(0.0, 0.0)
        number_locations = 0.0
        for dendrite in self.dendrites:
            for location in dendrite.locations:
                average_location += location
                number_locations += 1.0
        average_location /= number_locations
        soma_to_average = average_location.distanceTo(Vector2D(0.0,0.0))
        soma_to_average_fraction = soma_to_average / self.bounding_radius
        print "Cell Centroid:\t\t\t\t\t", average_location
        print "Number of Dendrite Points (before discretization):\t\t{0:,.0f}".format(number_locations)
        print "Linear Distance from Soma to Centroid:\t\t\t{0:.3f}".format(soma_to_average)
        print "Linear Distance from Soma to Centroid Normalized by Radius:\t{0:.3%}".format(soma_to_average_fraction)
        print

    def animateCompartments(self, surface):
        compartments_to_draw = self.master_compartments[:]
#        compartments_to_draw = [choice(self.compartments)]
            
        
        running = True
        next_iteration = False
        while running:
            surface.fill((255,255,255))
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    next_iteration = True
        
            for c in self.compartments:
                old_color = c.color
                c.color = (0,0,0)
                c.draw(surface)
                c.color = old_color
            for c in compartments_to_draw:
                c.draw(surface)
            
            pygame.display.update()
                
                
            if next_iteration:
                
                print "<<<<<<<<<<<<<<<<<<<"
                for c in compartments_to_draw:
                    print c.index,
                print
                
                distal_neighbors = []
                for c in compartments_to_draw:
                    distal_neighbors.extend(c.distal_neighbors)
#                    distal_neighbors.extend(c.proximal_neighbors)
                compartments_to_draw = distal_neighbors
                
                print "==================="
                for c in compartments_to_draw:
                    print c.index,
                print                
                print ">>>>>>>>>>>>>>>>>>>"
                
                next_iteration = False
       
        



