from time import clock
import numpy as np
import pygame
from pygame.locals import *
from ConeLayer import ConeLayer
from HorizontalLayer import HorizontalLayer
from BipolarLayer import BipolarLayer
from StarburstLayer import StarburstLayer
from Constants import *

"""
Retina class
"""
class Retina:
    def __init__(self, retina_width, retina_height, grid_size, timestep, simtulus, display):
        self.display = display        
        
        self.width  = float(retina_width)
        self.height = float(retina_height)
        self.area   = retina_width * retina_height
        
        self.grid_size      = float(grid_size)
        self.grid_width     = int(self.width / self.grid_size)
        self.grid_height    = int(self.height / self.grid_size)
            
        self.stimulus = stimulus
        
        self.time       = 0.0
        self.timestep   = timestep
        
        self.history_size = 3
        
        self.density_area = 1 * MM_TO_M * MM_TO_M
        
        self.layers = []
        grid = {}
        self.layers.append(grid)
    
    def drawGrid(self, surface, depth):
        for x in range(self.grid_width):
            for y in range(self.grid_width):
                key = (x, y)
                if key in self.layers[depth]:
                    elements = self.layers[depth][key]
                    for neuron, compartment in elements:
                        surface.set_at(key, compartment.color)        
    
    def register(self, neuron, compartment, depth, location):
        key = location.toIntTuple()
        if key in self.layers[depth]:
            self.layers[depth][key].append((neuron, compartment))
        else:
            self.layers[depth][key] = [(neuron, compartment)]
            
    def getOverlappingNeurons(self, neuron, location):
        key = location.toIntTuple()
        if key in self.layers[depth]:
            overlap = []
            for (other_neuron, other_compartment) in self.layers[depth][key]:
                if neuron != other_neuron:
                    overlap.append((other_neuron, other_compartment))
            return overlap 
        return []
        
        
    
    def buildStarburstLayer(self, nearest_neighbor_distance, minimum_required_density):
        input_delay = 1
        layer_depth = 0
        start_time = clock()
        self.on_starburst_layer = StarburstLayer(self, "On", None, layer_depth, 
                                                 self.history_size, input_delay, 
                                                 nearest_neighbor_distance,
                                                 minimum_required_density,
                                                 visualize_growth = True,
                                                 display=self.display)
                                                 
        
#        self.off_starburst_layer = StarburstLayer(self, "Off", None, layer_depth, 
#                                                 self.history_size, input_delay,  
#                                                 nearest_neighbor_distance,
#                                                 minimum_required_density,
#                                                 visualize_growth = False,
#                                                 display=None)
        print "On and Off Starburst Layers Construction Time", clock() - start_time
        
    
    def __str__(self):
        return ""
       
    """
    This function saves the current retina object using the Pickle module
    """ 
    def saveModel(self, name):
        import pickle, os
        
        if not(os.path.exists("Saved Retinas")):
            os.mkdir("Saved Retinas")
        
        # Create a new directory with run_name
        directory_name = os.path.join("Saved Retinas", name)
        
        # Add underscores to the name until it is unique
        while os.path.exists(directory_name):
            directory_name += "_"    
            
        # Make the directory
        os.mkdir(directory_name)
        
        # Get the path information
        current_path    = os.getcwd()
        save_path       = os.path.join(current_path, directory_name)
        
        # Create the save file where the retina object will be stored
        save_file   = os.path.join(save_path, "retina.p")
        fh          = open(save_file, "wb") 
        
        # Unload pygame surface which cannot be handled by pickle
        self.stimulus.unloadStimulusForSaving()
        
        # Pickle the retina!
        pickle.dump(self, fh)
        
        parameterPath = os.path.join(save_path, "parameters.txt")
        parameterFile = open(parameterPath, "w")
        parameterFile.write(str(self))
        parameterFile.close()
