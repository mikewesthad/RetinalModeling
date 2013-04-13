import random
import matplotlib.pyplot as plt
import numpy as np
import pygame
from pygame.locals import *
from Retina import Retina
from Vector2D import Vector2D
from StarburstDendrite import DendriteSegment
from Constants import *


class Starburst(object):
    
    def __init__(self, retina, location, average_wirelength=150*UM_TO_M, radius_deviation=.1,
                 min_branches=6, max_branches=6, heading_deviation=10, step_size=10*UM_TO_M,
                 max_segment_length=35*UM_TO_M, children_deviation=20, dendrite_vision_radius=30*UM_TO_M):
        
        # General neuron variables
        self.retina             = retina
        self.location           = location / self.retina.grid_size
        
        # Wirelength variables
        average_wirelength      = average_wirelength / self.retina.grid_size
        max_wirelength          = average_wirelength * (1.0+radius_deviation)
        min_wirelength          = average_wirelength * (1.0-radius_deviation)
        self.bounding_radius    = max_wirelength
        
        # Dendrite variables
        self.heading_deviation  = heading_deviation
        self.step_size          = step_size / self.retina.grid_size
        self.max_segment_length = max_segment_length / self.retina.grid_size
        self.dendrite_vision_radius = dendrite_vision_radius / self.retina.grid_size
        
        # Initialize the first branches
        number_dendrites    = random.randint(min_branches, max_branches)
        heading_spacing     = 360.0 / number_dendrites
        heading             = 0.0
        
        self.dendrites          = []
        self.active_dendrites   = []
        colors = [[0,0,0], [255,0,0],[0,255,0],[0,0,255],[50,255,255],[0,255,255]]
        for i in range(number_dendrites):
            wirelength = random.uniform(min_wirelength, max_wirelength)
            dendrite = DendriteSegment(self, self.location, heading, wirelength, wirelength,
                                       children_deviation, self.dendrite_vision_radius)
            dendrite.color = colors.pop()
            self.dendrites.append(dendrite)
            self.active_dendrites.append(dendrite)
            heading += heading_spacing
        
        # Plot the branching probability function
        self.plotBranchProbability()
        
        # Create a pygame display
        pygame.init()
        screen_size = (self.retina.grid_width, self.retina.grid_height)
        self.display = pygame.display.set_mode(screen_size)     
        self.background_color = (255,255,255)
        
        self.grow()
        
        self.findCentroid()
            
        # So that the display window will stay open,
        self.loopUntilExit()

        
        
    def findCentroid(self):
        average_location = Vector2D(0.0, 0.0)
        number_locations = 0.0
        for dendrite in self.dendrites:
            for location in dendrite.locations:
                average_location += location
                number_locations += 1.0
        average_location /= number_locations
        soma_to_average = average_location.distanceTo(self.location)
        soma_to_average_fraction = soma_to_average / self.bounding_radius
        print "Cell Centroid:\t\t\t\t\t", average_location
        print "Number of Dendrite Points:\t\t\t\t{0:,.0f}".format(number_locations)
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
        
    def grow(self):
        running = True
        i = 0
        while running and self.active_dendrites != []:
            
            # Grab a dendrite and update it
            dendrite = self.active_dendrites[i]
            is_growing, children = dendrite.grow()
            
            # If it isn't growing, delete it and adjust index
            if not(is_growing):
                del self.active_dendrites[i]
                i -= 1
            
            # If it had children, add them to the active list                 
            if children != []:
                for child in children: 
                    self.active_dendrites.insert(0, child)
                    self.dendrites.append(child)
            
            # Increment index
            i += 1
            if i >= len(self.active_dendrites): i=0
            
            # Draw the current dendrites
            self.display.fill(self.background_color)
            for dendrite in self.dendrites:
                dendrite.draw()
            pygame.display.update()
                
            # Check for close button signal from pygame window
            for event in pygame.event.get():
                if event.type == QUIT: running = False
        
    
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
        
        
 

       
        




# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina      = Retina(width, height, grid_size)
location    = Vector2D(500 * UM_TO_M, 500 * UM_TO_M)
startburst  = Starburst(retina, location)