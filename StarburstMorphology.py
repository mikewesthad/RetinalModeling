from random import uniform, randint, shuffle
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
                 dendrite_vision_radius=30*UM_TO_M, visualize_growth=True, display=None):
        
        # General neuron variables
        self.retina             = retina
        self.display            = display
        self.location           = location
        
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
        colors = [[0,0,0], [255,0,0],[0,255,0],[0,0,255],[50,255,255],[0,255,255]]
        shuffle(colors)
        for i in range(number_dendrites):
            wirelength = uniform(min_wirelength, max_wirelength)
            dendrite = DendriteSegment(self, self.location, heading, wirelength, wirelength,
                                       children_deviation, self.dendrite_vision_radius)
            dendrite.color = colors.pop()
            self.dendrites.append(dendrite)
            heading += heading_spacing
        
        # Slicing needed to force a copy of the elements (instead of creating a reference to a list)
        # Note: this only works if the lists are not nested (if they are, use deepcopy)
        self.master_dendrites = self.dendrites[:]  
            
        self.visualize_growth = visualize_growth
        if visualize_growth:
            self.display = display 
            self.background_color = (255,255,255)
            
        self.grow()
        
        self.discretize(1.0)
        self.createPoints()
        self.compartmentalize(20)
        
        for c in self.compartments:
            print c.getSize()


    def grow(self):
        # Slicing needed to force a copy of the elements (instead of creating a reference to a list)
        # Note: this only works if the lists are not nested (if they are, use deepcopy)
        active_dendrites = self.master_dendrites[:]
        
        running = True
        i = 0
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
                self.draw(self.display)
                pygame.display.update()
                    
                # Check for close button signal from pygame window
                for event in pygame.event.get():
                    if event.type == QUIT: running = False


    def compartmentalize(self, compartment_size):
        self.compartments = []
        
        # Build all the compartments recursively
        self.master_compartments = []
        for dendrite in self.master_dendrites:            
            new_compartment = Compartment(self)
            self.master_compartments.append(new_compartment)            
            dendrite.compartmentalize(new_compartment, compartment_size, compartment_size)
        
        # Connect all the master compartments together
        for compartment_a in self.master_compartments:
            for compartment_b in self.master_compartments:
                if compartment_a != compartment_b:
                    compartment_a.neighbors.append(compartment_b)
            
    
    def discretize(self, delta):
        for dendrite in self.master_dendrites:
            dendrite.discretize(delta=delta)
    
    def createPoints(self):
        for dendrite in self.dendrites:
            dendrite.createPoints()
            
    def draw(self, surface, draw_grid=False, draw_compartments=False):
        if draw_compartments:
            for compartment in self.compartments:
                compartment.draw(surface)
        else:
            for dendrite in self.dendrites:
                dendrite.draw(surface, draw_grid)
    
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
     
    def loopUntilExit(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            pygame.display.update()
            
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
        
        
 

       
        



