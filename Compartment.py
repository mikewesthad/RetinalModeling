from random import randint
import pygame

class Compartment:

    def __init__(self, neuron):
        self.neuron = neuron
        
        self.proximal_neighbors = []
        self.distal_neighbors   = []
        self.points             = []   
        self.inputs             = []   
        
        self.index = len(self.neuron.compartments)
        self.neuron.compartments.append(self)
        
        self.color = (randint(100,255),randint(100,255),randint(100,255))
    
    def draw(self, surface):
        for point in self.points:
            world_location = self.neuron.location + point.location
            pygame.draw.circle(surface, self.color, world_location.toIntTuple(), 2)
    
    def getSize(self):
        return len(self.points)