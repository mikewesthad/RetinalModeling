import numpy as np
from Constants import *


class Starburst(object):
    
    def __init__(self, retina, layer, morphology, location, input_delay, 
                 layer_depth):
        
        # General neuron variables
        self.retina             = retina
        self.layer              = layer
        self.morphology         = morphology
        self.location           = location
        self.input_delay        = input_delay
        self.layer_depth        = layer_depth 
        
        self.diffusion_weights  = np.zeros(0)

    def registerWithRetina(self):
        for compartment in self.morphology.compartments:
            compartment.registerWithRetina(self, self.layer_depth)
    
    def draw(self, surface, draw_grid=False):
        self.morphology.draw(surface, new_location=self.location)

       
        



