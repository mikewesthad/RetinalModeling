from time import clock
from Constants import *


"""
Retina class
"""
class Retina:
    def __init__(self, retina_width, retina_height, grid_size, timestep, 
                 stimulus=None, display=None):
        self.display    = display
        self.stimulus   = None
        
        self.width  = float(retina_width)
        self.height = float(retina_height)
        self.area   = retina_width * retina_height
        
        self.grid_size      = float(grid_size)
        self.grid_width     = int(self.width / self.grid_size)
        self.grid_height    = int(self.height / self.grid_size)
        
        self.time       = 0.0
        self.timestep   = timestep
        
        self.history_size = 3
    
        self.density_area = 1 * MM_TO_M * MM_TO_M
        
        self.cone_layer             = None
        self.horizontal_layer       = None
        self.on_bipolar_layer       = None
        self.off_bipolar_layer      = None
        self.on_starburst_layer     = None
        self.off_starburst_layer    = None
        self.layers = [self.cone_layer, self.horizontal_layer, self.on_bipolar_layer,
                       self.off_bipolar_layer, self.on_starburst_layer, self.off_starburst_layer]
        self.layer_names = ["Cone", "Horizontal", "On Bipolar", "Off Bipolar", "On Starburst", "Off Starburst"]
        self.number_layers = len(self.layers)
        
        self.cone_activities            = []
        self.horizontal_activities      = []
        self.on_bipolar_activities      = []
        self.off_bipolar_activities     = []
        self.on_starburst_activities    = []
        self.off_starburst_activities   = []
        self.activities = [self.cone_activities, self.horizontal_activities, self.on_bipolar_activities,
                           self.off_bipolar_activities, self.on_starburst_activities, self.off_starburst_activities]
        self.activity_bounds = [[], [], [], [], [], []]
        
        self.background_color       = pygame.Color(255, 255, 255)
        self.cone_color             = pygame.Color("#FFCF87")
        self.horizontal_color       = pygame.Color("#FFA722")
        self.on_bipolar_color       = pygame.Color("#5CCAE7")
        self.off_bipolar_color      = pygame.Color("#007DFF")
        self.on_starburst_color     = pygame.Color(255, 0, 0)
        self.off_starburst_color    = pygame.Color(0, 0, 255)
        
        self.grid_layers = []
        for depth in range(1):
            grid = {}
            self.grid_layers.append(grid)
    
    def loadMovieIntoStimulus(self, movie):
        self.stimulus.loadMovie(movie)
         
        
    def isPointWithinBounds(self, point):
        if point.x < 0: return False
        if point.y < 0: return False
        if point.x > self.grid_width: return False
        if point.y > self.grid_height: return False
        return True      
    
    def register(self, neuron, compartment, compartment_index, location):
        if not(self.isPointWithinBounds(location)):
            return
            
        depth   = neuron.layer.layer_depth    
        key     = location.toIntTuple()
        if key in self.grid_layers[depth]:
            self.grid_layers[depth][key].append((neuron, compartment, compartment_index))
        else:
            self.grid_layers[depth][key] = [(neuron, compartment, compartment_index)]
            
    def getOverlappingNeurons(self, neuron, location):
        key = location.toIntTuple()
        depth = neuron.layer_depth
        if key in self.grid_layers[depth]:
            overlap = []
            for (other_neuron, other_compartment, other_index) in self.grid_layers[depth][key]:
                if neuron != other_neuron:
                    overlap.append((other_neuron, other_compartment, other_index))
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
    def saveRetina(self, name):
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
        
    def saveActivities(self):
        import pickle, os
        name = "File_Size_Test"
        directory_name = os.path.join("Saved Retinas", name)
        
        for layer_index in range(self.number_layers):
            layer           = self.layers[layer_index]
            layer_name      = self.layer_names[layer_index]
            if layer != None:
                activities      = self.activities[layer_index]
                
                fh = os.path.join(directory_name, "np_save_"+layer_name)
                np.save(fh, activities)
#                fh = os.path.join(directory_name, "np_savetxt_default_"+layer_name+".txt")
#                np.savetxt(fh, activities)
#                fh = os.path.join(directory_name, "np_savetxt_default_"+layer_name+".gz")
#                np.savetxt(fh, activities)
#                fh = os.path.join(directory_name, "np_savetxt_lessprecision_"+layer_name+".txt")
#                np.savetxt(fh, activities, fmt="%.5f")
#                fh = os.path.join(directory_name, "np_savetxt_lessprecision_"+layer_name+".gz")
#                np.savetxt(fh, activities, fmt="%.5f")
                fh = os.path.join(directory_name, "py_pickle_"+layer_name)
                fh = open(fh, "wb")
                pickle.dump(activities, fh)
                
        fh = os.path.join(directory_name, "np_savez_alllayers")
        np.savez(fh, self.cone_activities, self.horizontal_activities,
                 self.on_bipolar_activities, self.off_bipolar_activities,
                 self.on_starburst_activities, self.off_starburst_activities)
                 
        self.saveModel(name)


    """
    This function runs the retina model for a specified duration
    """
    def runModel(self, duration):
        end_time = self.time + duration       
        
        while self.time <= end_time:
            self.updateActivity()
            self.time += self.timestep
    
        self.findRetinaActivityBounds()
        
    """
    This function updates each of the layers of the retina in turn
    """
    def updateActivity(self):
        print self.time
        
        self.stimulus.update(self.timestep) 
        
        for layer_index in range(self.number_layers):
            layer           = self.layers[layer_index]
            if layer != None:
                activities      = self.activities[layer_index]
                new_activity    = layer.update()
                activities.append(new_activity)


    def buildConeLayer(self, minimum_distance, minimum_density, input_field_size):
        start_time = clock()
        self.cone_layer = ConeLayer(self, minimum_distance, minimum_density,
                                    input_field_size, self.history_size, self.stimulus)
        print "Cone Layer Construction Time:", clock() - start_time
        self.layers[0] = self.cone_layer

    def buildHorizontalLayer(self, input_strength, decay_rate, diffusion_radius):
        input_delay = 1
        start_time = clock()
        self.horizontal_layer = HorizontalLayer(self, self.cone_layer, input_delay,
                                                self.history_size, input_strength,
                                                decay_rate, diffusion_radius)
        print "Horizontal Layer Construction Time:", clock() - start_time
        self.layers[1] = self.horizontal_layer

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
        self.layers[2] = self.on_bipolar_layer
        self.layers[3] = self.off_bipolar_layer
    
    def buildStarburstLayer(self, minimum_distance, minimum_density, 
                            average_wirelength, step_size, 
                            input_strength, decay_rate, diffusion_width):
        input_delay = 1
        layer_depth = 0
        minimum_distance    /= self.grid_size
        diffusion_width     /= self.grid_size
        average_wirelength  /= self.grid_size
        step_size           /= self.grid_size
        start_time = clock()
        self.on_starburst_layer = StarburstLayer(self, "On", layer_depth, 
                                                 self.history_size, input_delay, 
                                                 minimum_distance, minimum_density,
                                                 average_wirelength, step_size,
                                                 diffusion_width, decay_rate,
                                                 input_strength)                                                    
        self.off_starburst_layer = StarburstLayer(self, "Off", layer_depth, 
                                                 self.history_size, input_delay, 
                                                 minimum_distance, minimum_density,
                                                 average_wirelength, step_size,
                                                 diffusion_width, decay_rate,
                                                 input_strength)              
        print "On and Off Starburst Layers Construction Time", clock() - start_time
        self.layers[4] = self.on_starburst_layer
        self.layers[5] = self.off_starburst_layer
    
    
    
    ###########################################################################
    # Visualization Related Methods
    ###########################################################################
    
    def loadPast(self, timestep):
        for layer_index in range(self.number_layers):
            layer       = self.layers[layer_index]
            activities  = self.activities[layer_index]
            if layer != None:
                layer.loadPast(activities[timestep])       
    
    def drawLayerActivity(self, surface, layer_name, colormap, scale=1.0):
        if layer_name != None:
            layer_index     = self.layer_names.index(layer_name)
            layer           = self.layers[layer_index]
            activity_bounds = self.activity_bounds[layer_index]
            layer.drawActivity(surface, colormap, activity_bounds, scale=scale)
    
    def findRetinaActivityBounds(self):
        for layer_index in range(self.number_layers):
            layer       = self.layers[layer_index]
            activities  = self.activities[layer_index]
            layer_name  = self.layer_names[layer_index]
            if layer != None:
                bounds = self.findActivityBounds(activities, -1, 1, True)
                self.activity_bounds[layer_index] = bounds
                print "{0} Activity Bounds: ({1:.3f}, {2:.3f})".format(layer_name, bounds[0], bounds[1])
        
    def findActivityBounds(self, activities, estimated_min, estimated_max, activity_centered_on_zero):
        # Find the real max/min activity values
        max_activity = np.amax(activities)
        min_activity = np.amin(activities)
        print "Activity Bounds: ({0:.3f}, {1:.3f})".format(min_activity, max_activity)
        
        # Impose an estimated max/min
        max_activity    = max(max_activity, estimated_max)
        min_activity    = min(min_activity, estimated_min)
        
        # If the range of activity values is expected to be symmetric and
        # centered on zero, then the max and min values should be equal
        if activity_centered_on_zero:
            bound           = max(abs(max_activity), abs(min_activity))
            max_activity    = bound
            min_activity    = -bound
        
        return [min_activity, max_activity] 