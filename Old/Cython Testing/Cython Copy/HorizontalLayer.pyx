import math
import random
from Constants import *

import numpy as np
from time import clock


"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5

class HorizontalLayer:

    def __init__(self, retina, cone_layer, input_delay, history_size, stimulus, diffusionDistance):

        self.retina = retina

        self.history_size = history_size
        self.input_delay = input_delay

        self.diffusionDistance = diffusionDistance/retina.gridSize
    
        self.locations = cone_layer.locations
        self.neurons = len(self.locations)
        self.initializeActivties()

        self.establishLateralConnections()


    def establishLateralConnections(self):
        self.lateralWeights = np.zeros((self.neurons, self.neurons))
        
        for n1 in range(self.neurons):
            x1, y1 = self.locations[n1]
            for n2 in range(n1, self.neurons):
                x2, y2 = self.locations[n2]
                distance = linearDistance(x1, y1, x2, y2)
                self.lateralWeights[n1, n2] = distance
                if n1 != n2: self.lateralWeights[n2, n1] = distance
                
        self.lateralWeights = np.exp(-(self.lateralWeights)**2/(self.diffusionDistance))
        self.lateralWeights /= np.sum(self.lateralWeights, 0)


    def initializeActivties(self):
        self.activities = []
        for i in range(self.history_size):
            self.activities.append(np.zeros((self.neurons,1)))
            
