import numpy as np
from Constants import *
import collections

class Starburst(object):
    
    def __init__(self, retina, layer, morphology, location, input_delay, 
                 layer_depth, history_size=4):
        
        # General neuron variables
        self.retina             = retina
        self.layer              = layer
        self.morphology         = morphology
        self.location           = location
        self.input_delay        = input_delay
        self.layer_depth        = layer_depth
        self.history_size       = history_size
        
        self.number_compartments    = len(self.morphology.compartments)
        self.input_strength         = self.morphology.input_strength
        self.decay_rate             = self.morphology.decay_rate
        self.diffusion_weights      = self.morphology.diffusion_weights
        self.initializeActivties()
        
        
    def registerWithRetina(self):
        for compartment in self.morphology.compartments:
            compartment.registerWithRetina(self, self.layer_depth)
    
    def initInputs(self):
        isAppropriateToConnect = True
        for compartment in self.morphology.compartments:
            inputs = []            
            for point in compartment.points:
                location = self.location + point.location #abs = abs + rel
                neurons_comps = self.retina.getOverlappingNeurons(self, location)
                for neuron_comp in neurons_comps: #tuples = (neuron, comp)
                    if isAppropriateToConnect:
                        inputs.append(neuron_comp[1])   #appends the compartment
            compartment.inputs = collections.Counter(inputs)               
                        
    
    def draw(self, surface, scale=1.0, draw_segments=False, draw_points=False, 
             draw_compartments=False):
        self.morphology.draw(surface, scale=scale, new_location=self.location,
                             draw_points=draw_points, draw_segments=draw_segments,
                             draw_compartments=draw_compartments)

    def initializeActivties(self):
        self.activities = []
        for i in range(self.history_size):
            blank_activity = np.zeros((1, self.number_compartments))
            self.activities.append(blank_activity)


    def updateActivity(self):
        # Delete the oldest activity and get the current activity
        del self.activities[-1]
        last_activity = self.activities[0]
        
        # Calculate the diffusion
        d = self.decay_rate
        diffusionActivity = (1.0-d) * np.dot(last_activity, self.diffusion_weights)
        
        # Get the bipolar activity
        
        # Find the new activity
        i = self.input_strength
        new_activity = (1.0-i) * diffusionActivity #+ i * bipolar_inputs
        
        # Add the most recent activity to the front of the list
        self.activities.insert(0, new_activity)
        
        return new_activity