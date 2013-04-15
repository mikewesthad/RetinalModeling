from time import clock
import numpy as np
from Constants import *
from StarburstLayer import StarburstLayer

"""
Retina class
"""
class Retina:
    def __init__(self, retina_width, retina_height, grid_size):

        self.width  = float(retina_width)
        self.height = float(retina_height)
        self.area   = retina_width * retina_height
        
        self.grid_size      = float(grid_size)
        self.grid_width     = int(self.width / self.grid_size)
        self.grid_height    = int(self.height / self.grid_size)
        
        self.density_area = 1 * MM_TO_M * MM_TO_M
        
        self.layers = []
        grid = {}
        self.layers.append(grid)
        
    
    def buildStarburstLayer(self, nearest_neighbor_distance, minimum_required_density):
        input_delay = 1
        start_time = clock()
        self.on_starburst_layer = StarburstLayer(self, "On", None, 3, 1, 
                                                 nearest_neighbor_distance,
                                                 minimum_required_density,
                                                 visualize_growth = False,
                                                 display=None)
        self.off_starburst_layer = StarburstLayer(self, "Off", None, 3, 1, 
                                                 nearest_neighbor_distance,
                                                 minimum_required_density,
                                                 visualize_growth = False,
                                                 display=None)
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