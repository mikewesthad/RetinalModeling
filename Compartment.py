from random import randint
import pygame

class Compartment:

    def __init__(self, morphology):
        self.morphology = morphology
        self.retina     = morphology.retina
        
        self.proximal_neighbors = []
        self.distal_neighbors   = []
        self.points             = []   
        self.inputs             = []   
        
        self.index = len(self.morphology.compartments)
        self.morphology.compartments.append(self)
        
        self.color = (randint(100,255),randint(100,255),randint(100,255))
    
    def draw(self, surface):
        for point in self.points:
            world_location = self.morphology.location + point.location
            pygame.draw.circle(surface, self.color, world_location.toIntTuple(), 2)
    
    def registerWithRetina(self, neuron, layer_depth):
        for point in self.points:
            location = point.location + neuron.location
            self.retina.register(neuron, self, layer_depth, location)
    
    def getSize(self):
        return len(self.points)