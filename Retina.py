from time import clock
import numpy as np
import pygame
from pygame.locals import *
from ConeLayer import ConeLayer
from HorizontalLayer import HorizontalLayer
from BipolarLayer import BipolarLayer



"""
Retina class
"""
class Retina:
    def __init__(self, retina_width, retina_height, grid_size, timestep, stimulus):

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
        
        
        self.display_width  = 1000
        self.display_height = 1000
        self.calculateDisplay()
    
    def __str__(self):
        string = ""
        string += "Retina\n"
        string += "\nwidth:\t\t\t\t"+str(self.width)
        string += "\nheight:\t\t\t\t"+str(self.height)
        string += "\narea:\t\t\t\t"+str(self.area)
        string += "\ngrid_size:\t\t\t"+str(self.grid_size)
        string += "\ngrid_width:\t\t\t"+str(self.grid_width)
        string += "\ngrid_height:\t\t\t"+str(self.grid_height)
        string += "\ntimestep:\t\t\t"+str(self.timestep)
        string += "\ntime:\t\t\t\t"+str(self.time)
        
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

    """
    Build the cone layer 
    """
    def buildConeLayer(self, minimum_distance, minimum_density, input_field_size):
        start_time = clock()
        self.cone_layer = ConeLayer(self, minimum_distance, minimum_density,
                                    input_field_size, self.history_size, self.stimulus)
        print "Cone Layer Construction Time:", clock() - start_time


    """
    Build the horizontal layer 
    """
    def buildHorizontalLayer(self, input_strength, decay_rate, diffusion_radius):
        input_delay = 1
        start_time = clock()
        self.horizontal_layer = HorizontalLayer(self, self.cone_layer, input_delay,
                                                self.history_size, input_strength,
                                                decay_rate, diffusion_radius)
        print "Horizontal Layer Construction Time:", clock() - start_time

    """
    Build the bipolar layer 
    """
    def buildBipolarLayer(self, minimum_distance, minimum_density, input_field_radius, output_field_radius):
        input_delay = 1
        start_time = clock()
        self.on_bipolar_layer = BipolarLayer(self, "On", self.cone_layer, self.horizontal_layer,
                                             self.history_size, input_delay,
                                             minimum_distance, minimum_density,
                                             input_field_radius, output_field_radius)
        self.off_bipolar_layer = BipolarLayer(self, "Off", self.cone_layer, self.horizontal_layer,
                                              self.history_size, input_delay,
                                              minimum_distance, minimum_density,
                                              input_field_radius, output_field_radius)
        print "On and Off Bipolar Layers Construction Time:", clock() - start_time





###############################################################################
# Visualization functions
###############################################################################

    def calculateDisplay(self):        
        width_scale         = self.display_width / float(self.grid_width)
        height_scale        = self.display_height / float(self.grid_height)
        self.display_scale  = min(width_scale, height_scale)
        self.display_size   = (self.display_width, self.display_height) 
        
    
    def visualizeOPLCellPlacement(self):
        pygame.init()
        
        display     = pygame.display.set_mode(self.display_size)
        
        cone_highlighted_color          = self.cone_color
        horizontal_highlighted_color    = self.horizontal_color
        on_bipolar_highlighted_color    = self.on_bipolar_color
        off_bipolar_highlighted_color   = self.off_bipolar_color
        
        display.fill(self.background_color)
        
        cone_radius         = int(round(self.cone_layer.nearest_neighbor_distance_gridded/2.0 * self.display_scale))
        horizontal_radius   = int(round((self.horizontal_layer.nearest_neighbor_distance_gridded/2.0 + 3) * self.display_scale)) # Add 3 so you can see behind cones
        on_bipolar_radius   = int(round(self.on_bipolar_layer.nearest_neighbor_distance_gridded/2.0 * self.display_scale))
        off_bipolar_radius  = int(round(self.off_bipolar_layer.nearest_neighbor_distance_gridded/2.0 * self.display_scale))
        
        cone_locations          = [[int(round(x * self.display_scale)),int(round(y * self.display_scale))] for x, y in self.cone_layer.locations]
        horizontal_locations    = [[int(round(x * self.display_scale)),int(round(y * self.display_scale))] for x, y in self.horizontal_layer.locations]        
        on_bipolar_locations    = [[int(round(x * self.display_scale)),int(round(y * self.display_scale))] for x, y in self.on_bipolar_layer.locations] 
        off_bipolar_locations   = [[int(round(x * self.display_scale)),int(round(y * self.display_scale))] for x, y in self.off_bipolar_layer.locations]

        running = True
        highlightedLayer = 0
        while running:
            for event in pygame.event.get():
                if event.type == QUIT: 
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:                        
                        highlightedLayer -= 1
                        if highlightedLayer < 0: highlightedLayer = 4
                    if event.key == K_RIGHT:                    
                        highlightedLayer += 1
                        if highlightedLayer > 4: highlightedLayer = 0
                
            if highlightedLayer == 0:
                pygame.display.set_caption("All Layers")      
                cone_color          = cone_highlighted_color
                horizontal_color    = horizontal_highlighted_color
                on_bipolar_color    = on_bipolar_highlighted_color
                off_bipolar_color   = off_bipolar_highlighted_color
                drawOrder           = [[on_bipolar_locations, on_bipolar_color, on_bipolar_radius],
                                       [off_bipolar_locations, off_bipolar_color, off_bipolar_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius],
                                       [cone_locations, cone_color, cone_radius]]                
            elif highlightedLayer == 1:
                pygame.display.set_caption("Cone Layer")      
                cone_color          = cone_highlighted_color
                horizontal_color    = self.lerpColors(horizontal_highlighted_color, self.background_color, 0.85)
                on_bipolar_color    = self.lerpColors(on_bipolar_highlighted_color, self.background_color, 0.85)
                off_bipolar_color   = self.lerpColors(off_bipolar_highlighted_color, self.background_color, 0.85)
                drawOrder           = [[on_bipolar_locations, on_bipolar_color, on_bipolar_radius],
                                       [off_bipolar_locations, off_bipolar_color, off_bipolar_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius],
                                       [cone_locations, cone_color, cone_radius]] 
            elif highlightedLayer == 2:
                pygame.display.set_caption("Horizontal Layer")      
                cone_color          = self.lerpColors(cone_highlighted_color, self.background_color, 0.85)
                horizontal_color    = horizontal_highlighted_color
                on_bipolar_color    = self.lerpColors(on_bipolar_highlighted_color, self.background_color, 0.85)
                off_bipolar_color   = self.lerpColors(off_bipolar_highlighted_color, self.background_color, 0.85)
                drawOrder           = [[on_bipolar_locations, on_bipolar_color, on_bipolar_radius],
                                       [off_bipolar_locations, off_bipolar_color, off_bipolar_radius],
                                       [cone_locations, cone_color, cone_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius]] 
            elif highlightedLayer == 3:
                pygame.display.set_caption("On Bipolar Layer")      
                cone_color          = self.lerpColors(cone_highlighted_color, self.background_color, 0.85)
                horizontal_color    = self.lerpColors(horizontal_highlighted_color, self.background_color, 0.85)
                on_bipolar_color    = on_bipolar_highlighted_color
                off_bipolar_color   = self.lerpColors(off_bipolar_highlighted_color, self.background_color, 0.85)
                drawOrder           = [[off_bipolar_locations, off_bipolar_color, off_bipolar_radius],
                                       [cone_locations, cone_color, cone_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius],
                                       [on_bipolar_locations, on_bipolar_color, on_bipolar_radius]] 
            else:
                pygame.display.set_caption("Off Bipolar Layer")      
                cone_color          = self.lerpColors(cone_highlighted_color, self.background_color, 0.85)
                horizontal_color    = self.lerpColors(horizontal_highlighted_color, self.background_color, 0.85)
                on_bipolar_color    = self.lerpColors(on_bipolar_highlighted_color, self.background_color, 0.85)
                off_bipolar_color   = off_bipolar_highlighted_color
                drawOrder           = [[on_bipolar_locations, on_bipolar_color, on_bipolar_radius],
                                       [cone_locations, cone_color, cone_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius],
                                       [off_bipolar_locations, off_bipolar_color, off_bipolar_radius]] 
            
            for locations, color, radius in drawOrder:
                for x, y in locations:
                    pygame.draw.circle(display, color, (x, y), radius)
                    
            pygame.display.update()      
                    
    """
    Linearly interpolate between color1 and color2
    """
    def lerpColors(self, color1, color2, fraction):
        r = color1.r + fraction * (color2.r - color1.r)
        g = color1.g + fraction * (color2.g - color1.g)
        b = color1.b + fraction * (color2.b - color1.b)
        return pygame.Color(int(r),int(g),int(b))


            
    def playOnBipolarActivity(self):
        self.playLayerActivity("On Bipolar", self.on_bipolar_layer, self.on_bipolar_activities)
        
    def playOffBipolarActivity(self):
        self.playLayerActivity("Off Bipolar", self.off_bipolar_layer, self.off_bipolar_activities)
    
    def playConeActivity(self):
        self.playLayerActivity("Cone", self.cone_layer, self.cone_activities)
    
    def playHorizontalActivity(self):
        self.playLayerActivity("Horizontal", self.horizontal_layer, self.horizontal_activities)
            
    def playLayerActivity(self, layer_name, layer, activities, 
                          estimated_minimum_activity=-1.0, 
                          estimated_maximum_activity=1.0,
                          activity_centered_on_zero=True):
        pygame.init()        
        display = pygame.display.set_mode(self.display_size)
        pygame.display.set_caption(layer_name+" Activity Timestep 0")
        print "Visualizing Activity For",layer_name,"..."
        
        radius = int(round(layer.nearest_neighbor_distance_gridded/2.0 * self.display_scale))
        
        min_activity, max_activity = self.findActivityBounds(activities, 
                                                             estimated_minimum_activity,
                                                             estimated_maximum_activity,
                                                             activity_centered_on_zero)

        timestep        = 0
        end_timestep    = len(activities)-1
        
        running = True
        while running:
            display.fill(self.background_color)
        
            for n in range(layer.neurons):
                x, y        = layer.locations[n]
                x, y        = int(round(x * self.display_scale)), int(round(y * self.display_scale))
                activity    = activities[timestep][0,n]
                color       = self.mapActivityToColor(activity, min_activity, max_activity, 
                                                      activity_centered_on_zero)
                pygame.draw.circle(display, color, (x,y), radius) 
                
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        timestep += 1
                        if timestep > end_timestep: timestep = 0
                        pygame.display.set_caption(layer_name+" Activity Timestep "+str(timestep))
                    elif event.key == K_LEFT:
                        timestep -= 1
                        if timestep < 0: timestep = end_timestep
                        pygame.display.set_caption(layer_name+" Activity Timestep "+str(timestep))
                        
            pygame.display.update()

    def mapActivityToColor(self, activity, min_activity, max_activity, activity_centered_on_zero):
        positive_activity_color         = pygame.Color(255, 0, 0)
        zero_positive_activity_color    = pygame.Color(0, 0, 0)
        negative_activity_color         = pygame.Color(0, 0, 255)
        zero_negative_activity_color    = pygame.Color(0, 0, 0)
        
        if activity_centered_on_zero:
            if activity < 0:
                percent_from_zero_to_min = activity/min_activity
                color = self.lerpColors(zero_negative_activity_color, negative_activity_color, percent_from_zero_to_min)
            else:
                percent_from_zero_to_max = activity/max_activity
                color = self.lerpColors(zero_positive_activity_color, positive_activity_color, percent_from_zero_to_max)
        else:
            percent_from_min_to_max = (activity-min_activity) / (max_activity-min_activity)
            color = self.lerpColors(zero_positive_activity_color, positive_activity_color, percent_from_min_to_max)
            
        return color
        
    def findActivityBounds(self, activities, estimated_min, estimated_max, activity_centered_on_zero):
        # Find the real max/min activity values
        max_activity = np.amax(activities)
        min_activity = np.amin(activities)
        
        print "\tTrue Max Activity Value:", max_activity
        print "\tTrue Min Activity Value:", min_activity
        
        # Impose an estimated max/min
        max_activity    = max(max_activity, estimated_max)
        min_activity    = min(min_activity, estimated_min)
        
        # If the range of activity values is expected to be symmetric and
        # centered on zero, then the max and min values should be equal
        if activity_centered_on_zero:
            bound           = max(abs(max_activity), abs(min_activity))
            max_activity    = bound
            min_activity    = -bound
            
        print "\tAdjusted Max Activity Value For Color Scale:", max_activity
        print "\tAdjusted Min Activity Value For Color Scale:", min_activity
        
        return min_activity, max_activity
        

    def visualizeOnBipolarWeights(self):
        self.visualizeInputWeights(self.on_bipolar_layer, self.cone_layer, 
                                   self.on_bipolar_color, self.cone_color,
                                   "On Bipolar", "Cone/Horizontal")
                                   
    def visualizeOffBipolarWeights(self):
        self.visualizeInputWeights(self.off_bipolar_layer, self.cone_layer, 
                                   self.off_bipolar_color, self.cone_color,
                                   "Off Bipolar", "Cone/Horizontal")

    def visualizeInputWeights(self, layer, input_layer, layer_color, 
                              input_layer_color, layer_name, input_layer_name):
        pygame.init()        
        display = pygame.display.set_mode(self.display_size)
        pygame.display.set_caption(layer_name+" Inputs From "+input_layer_name+" Layer")
        
        location_index  = 0
        last_location   = len(layer.locations) - 1         
        
        radius          = int(round(layer.input_field_radius_gridded*self.display_scale))
        input_radius    = int(round(input_layer.nearest_neighbor_distance_gridded*self.display_scale))
        
        background_layer_radius = int(round(layer.nearest_neighbor_distance_gridded*self.display_scale))
        background_layer_color  = self.lerpColors(layer_color, self.background_color, 0.85)
        
        running = True
        while running:
            display.fill(self.background_color)                
            
            for x, y in layer.locations:
                display_x, display_y = int(round(x * self.display_scale)), int(round(y * self.display_scale))
                pygame.draw.circle(display, background_layer_color, (display_x, display_y), background_layer_radius)
            
            x, y    = layer.locations[location_index]
            loc_ID  = str(x)+"."+str(y)
            display_x, display_y = int(round(x * self.display_scale)), int(round(y * self.display_scale))
            pygame.draw.circle(display, layer_color, (display_x, display_y), radius)
        
            connected_inputs = layer.inputs[loc_ID]
            for i in connected_inputs:
                ID, w   = i
                ix, iy  = ID.split(".")
                ix, iy  = int(ix), int(iy)
                display_x, display_y = int(round(ix * self.display_scale)), int(round(iy * self.display_scale))
                color   = self.lerpColors(self.background_color, input_layer_color, w)
                pygame.draw.circle(display, color, (display_x, display_y), input_radius)
                
            for event in pygame.event.get():
                if event.type == QUIT: 
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        location_index += 1
                        if location_index > last_location: location_index = 0
                    elif event.key == K_LEFT:
                        location_index -= 1
                        if location_index < 0: location_index = last_location
                
            pygame.display.update()
            
        

#    def visualizeConeWeights(self):
#        
#        pygame.init()
#        displaySurface = pygame.display.set_mode((self.gridWidth, self.gridHeight))
#        displaySurface.fill((0,0,0))
#        
#        cl = self.coneLayer
#        
#        locID   = random.choice(cl.locations)
#        
#
#        rectx = self.stimulus.position[0]
#        recty = self.stimulus.position[1]        
#        rectw = self.stimulus.size[0]      
#        recth = self.stimulus.size[1]
#        pygame.draw.rect(displaySurface, (255,255,255), (rectx, recty, rectw, recth))
#
#        
#        
#        connectedPixels = cl.inputs[locID]
#        for p in connectedPixels:
#            pID, w = p
#            x, y = pID.split(".")
#            x, y = float(x), float(y)
#            rectx = self.stimulus.position[0] + x * self.stimulus.pixelSize
#            recty = self.stimulus.position[1] + y * self.stimulus.pixelSize
#            rects = self.stimulus.pixelSize
#            pygame.draw.rect(displaySurface, (w*255,0,0), (rectx, recty, rects, rects))
#            
#
#
#        # Get cone rectangle
#        x, y    = locID.split(".")
#        x, y    = float(x), float(y)
#        rectx = x - cl.input_field_radius_gridded
#        recty = y - cl.input_field_radius_gridded
#        rects = 2 * cl.input_field_radius_gridded
#        pygame.draw.rect(displaySurface, (0,0,255), (rectx, recty, rects, rects), 1)
#
#        running = True
#        while running:
#            for event in pygame.event.get():
#                if event.type == QUIT:
#                    running = False
#            pygame.display.update()

        
