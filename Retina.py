from time import clock
import numpy as np
import pygame
from pygame.locals import *
from ConeLayer import ConeLayer
from HorizontalLayer import HorizontalLayer
from BipolarLayer import BipolarLayer
from StarburstLayer import StarburstLayer
from Vector2D import *
from Constants import *


"""
Retina class
"""
class Retina:
    def __init__(self, retina_width, retina_height, grid_size, timestep, stimulus, display):
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
        
        self.cone_layer         = None
        self.horizontal_layer   = None
        self.on_bipolar_layer   = None
        self.off_bipolar_layer  = None
        
        self.cone_activities        = []
        self.horizontal_activities  = []
        self.on_bipolar_activities  = []
        self.off_bipolar_activities = []
        
        
        self.background_color   = pygame.Color(255, 255, 255)
        self.cone_color         = pygame.Color("#FFCF87")
        self.horizontal_color   = pygame.Color("#FFA722")
        self.on_bipolar_color   = pygame.Color("#5CCAE7")
        self.off_bipolar_color  = pygame.Color("#007DFF")
        
        self.layers = []
        for depth in range(1):
            grid = {}
            self.layers.append(grid)
        
    def isPointWithinBounds(self, point):
        if point.x < 0: return False
        if point.y < 0: return False
        if point.x > self.grid_width: return False
        if point.y > self.grid_height: return False
        return True      
    
    def register(self, neuron, compartment, depth, location):
        if not(self.isPointWithinBounds(location)):
            return
            
        key = location.toIntTuple()
        if key in self.layers[depth]:
            self.layers[depth][key].append((neuron, compartment))
        else:
            self.layers[depth][key] = [(neuron, compartment)]
            
    def getOverlappingNeurons(self, neuron, location):
        key = location.toIntTuple()
        depth = neuron.layer_depth
        if key in self.layers[depth]:
            overlap = []
            for (other_neuron, other_compartment) in self.layers[depth][key]:
                if neuron != other_neuron:
                    overlap.append((other_neuron, other_compartment))
            return overlap 
        return []
        
        
    def __str__(self):
        string = ""
        string += "Stimulus\n" + str(self.stimulus)
        
        string += "\n\n\nRetina\n"
        string += "\nWidth (um)\t\t\t\t"+str(self.width * M_TO_UM)
        string += "\nHeight (um)\t\t\t\t"+str(self.height * M_TO_UM)
        string += "\nArea (um)\t\t\t\t"+str(self.area * M_TO_UM)
        string += "\nGrid Size (um)\t\t\t\t"+str(self.grid_size * M_TO_UM)
        string += "\nGrid Width (rgu)\t\t\t"+str(self.grid_width)
        string += "\nGrid Height (rgu)\t\t\t"+str(self.grid_height)
        string += "\nTimestep (ms)\t\t\t\t"+str(self.timestep * S_TO_MS)
        string += "\nTime (ms)\t\t\t\t"+str(self.time * S_TO_MS)
        
        string += "\n\n\n" + str(self.cone_layer)
        string += "\n\n\n" + str(self.horizontal_layer)
        string += "\n\n\n" + str(self.on_bipolar_layer)
        string += "\n\n\n" + str(self.off_bipolar_layer)
        return string  
       
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

    def addStarburst(self):       
        from StarburstMorphology import StarburstMorphology
        from Starburst import Starburst
        starburst_morphology = StarburstMorphology(self)
        starburst = Starburst(None, starburst_morphology, Vector2D(200.0,200.0))
        starburst.registerWithRetina()
        starburst.initializeInputs()
        return starburst

    """
    This function runs the retina model for a specified duration
    """
    def runModel(self, duration):
        end_time = self.time + duration
        
        while self.time <= end_time:
            self.updateActivity()
            self.time += self.timestep
    
        
    """
    This function updates each of the layers of the retina in turn
    """
    def updateActivity(self):
        print self.time
        
        self.stimulus.update(self.timestep)
        
        if self.cone_layer != None:
            cone_activity = self.cone_layer.updateActivity()
            self.cone_activities.append(cone_activity)
        
        if self.horizontal_layer != None:
            horizontal_activity = self.horizontal_layer.updateActivity()
            self.horizontal_activities.append(horizontal_activity)
        
        if self.on_bipolar_layer != None:
            on_bipolar_activity = self.on_bipolar_layer.updateActivity()
            self.on_bipolar_activities.append(on_bipolar_activity)
        
        if self.off_bipolar_layer != None:
            off_bipolar_activity = self.off_bipolar_layer.updateActivity()
            self.off_bipolar_activities.append(off_bipolar_activity)

    def buildConeLayer(self, minimum_distance, minimum_density, input_field_size):
        start_time = clock()
        self.cone_layer = ConeLayer(self, minimum_distance, minimum_density,
                                    input_field_size, self.history_size, self.stimulus)
        print "Cone Layer Construction Time:", clock() - start_time

    def buildHorizontalLayer(self, input_strength, decay_rate, diffusion_radius):
        input_delay = 1
        start_time = clock()
        self.horizontal_layer = HorizontalLayer(self, self.cone_layer, input_delay,
                                                self.history_size, input_strength,
                                                decay_rate, diffusion_radius)
        print "Horizontal Layer Construction Time:", clock() - start_time

    def buildBipolarLayer(self, minimum_distance, minimum_density, input_field_radius, output_field_radius):
        input_delay = 1
        layer_depth = 0
        start_time = clock()
        self.on_bipolar_layer = BipolarLayer(self, "On", self.cone_layer, self.horizontal_layer,
                                             self.history_size, input_delay, layer_depth,
                                             minimum_distance, minimum_density,
                                             input_field_radius, output_field_radius)
        self.off_bipolar_layer = BipolarLayer(self, "Off", self.cone_layer, self.horizontal_layer,
                                              self.history_size, input_delay, layer_depth,
                                              minimum_distance, minimum_density,
                                              input_field_radius, output_field_radius)
        print "On and Off Bipolar Layers Construction Time:", clock() - start_time
    
    def buildStarburstLayer(self, minimum_distance, minimum_density):
        input_delay = 1
        layer_depth = 0
        start_time = clock()
        self.on_starburst_layer = StarburstLayer(self, "On", layer_depth, 
                                                 self.history_size, input_delay, 
                                                 minimum_distance, minimum_density)
                                                 
        
#        self.off_starburst_layer = StarburstLayer(self, "Off", None, layer_depth, 
#                                                 self.history_size, input_delay,  
#                                                 minimum_distance,
#                                                 minimum_density,
#                                                 visualize_growth = False,
#                                                 display=None)
        print "On and Off Starburst Layers Construction Time", clock() - start_time