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
        
        self.cone_activities        = []
        self.horizontal_activities  = []
        self.on_bipolar_activities  = []
        self.off_bipolar_activities = []
        

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
        
        self.stimulus.update(self.time)
        
        cone_activity = self.cone_layer.updateActivity()
        self.cone_activities.append(cone_activity)
        
        horizontal_activity = self.horizontal_layer.updateActivity()
        self.horizontal_activities.append(horizontal_activity)
        
        on_bipolar_activity = self.on_bipolar_layer.updateActivity()
        self.on_bipolar_activities.append(on_bipolar_activity)
        
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
        self.on_bipolar_layer = BipolarLayer(self, self.cone_layer, self.horizontal_layer,
                                             self.history_size, input_delay,
                                             minimum_distance, minimum_density,
                                             input_field_radius, output_field_radius)
        self.off_bipolar_layer = BipolarLayer(self, self.cone_layer, self.horizontal_layer,
                                              self.history_size, input_delay,
                                              minimum_distance, minimum_density,
                                              input_field_radius, output_field_radius)
        print "On and Off Bipolar Layers Construction Time:", clock() - start_time







###############################################################################
# Visualization functions
###############################################################################
    
    def visualizeOPLCellPlacement(self):
        pygame.init()
        
        screen_size = (self.grid_width, self.grid_height)
        display     = pygame.display.set_mode(screen_size)
        
        background_color                = pygame.Color(255, 255, 255)
        cone_highlighted_color          = pygame.Color("#FFCF87")
        horizontal_highlighted_color    = pygame.Color("#FFA722")
        on_bipolar_highlighted_color    = pygame.Color("#5CCAE7")
        off_bipolar_highlighted_color   = pygame.Color("#007DFF")
        
        display.fill(background_color)

        cone_radius         = int(self.cone_layer.nearest_neighbor_distance_gridded/2.0)
        horizontal_radius   = cone_radius + 3
        on_bipolar_radius   = int(self.on_bipolar_layer.nearest_neighbor_distance_gridded/2.0)
        off_bipolar_radius  = int(self.off_bipolar_layer.nearest_neighbor_distance_gridded/2.0)
        
        cone_locations          = self.cone_layer.locations
        horizontal_locations    = self.horizontal_layer.locations        
        on_bipolar_locations    = self.on_bipolar_layer.locations      
        off_bipolar_locations   = self.off_bipolar_layer.locations

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
                horizontal_color    = self.lerpColors(horizontal_highlighted_color, background_color, 0.85)
                on_bipolar_color    = self.lerpColors(on_bipolar_highlighted_color, background_color, 0.85)
                off_bipolar_color   = self.lerpColors(off_bipolar_highlighted_color, background_color, 0.85)
                drawOrder           = [[on_bipolar_locations, on_bipolar_color, on_bipolar_radius],
                                       [off_bipolar_locations, off_bipolar_color, off_bipolar_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius],
                                       [cone_locations, cone_color, cone_radius]] 
            elif highlightedLayer == 2:
                pygame.display.set_caption("Horizontal Layer")      
                cone_color          = self.lerpColors(cone_highlighted_color, background_color, 0.85)
                horizontal_color    = horizontal_highlighted_color
                on_bipolar_color    = self.lerpColors(on_bipolar_highlighted_color, background_color, 0.85)
                off_bipolar_color   = self.lerpColors(off_bipolar_highlighted_color, background_color, 0.85)
                drawOrder           = [[on_bipolar_locations, on_bipolar_color, on_bipolar_radius],
                                       [off_bipolar_locations, off_bipolar_color, off_bipolar_radius],
                                       [cone_locations, cone_color, cone_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius]] 
            elif highlightedLayer == 3:
                pygame.display.set_caption("On Bipolar Layer")      
                cone_color          = self.lerpColors(cone_highlighted_color, background_color, 0.85)
                horizontal_color    = self.lerpColors(horizontal_highlighted_color, background_color, 0.85)
                on_bipolar_color    = on_bipolar_highlighted_color
                off_bipolar_color   = self.lerpColors(off_bipolar_highlighted_color, background_color, 0.85)
                drawOrder           = [[off_bipolar_locations, off_bipolar_color, off_bipolar_radius],
                                       [cone_locations, cone_color, cone_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius],
                                       [on_bipolar_locations, on_bipolar_color, on_bipolar_radius]] 
            else:
                pygame.display.set_caption("Off Bipolar Layer")      
                cone_color          = self.lerpColors(cone_highlighted_color, background_color, 0.85)
                horizontal_color    = self.lerpColors(horizontal_highlighted_color, background_color, 0.85)
                on_bipolar_color    = self.lerpColors(on_bipolar_highlighted_color, background_color, 0.85)
                off_bipolar_color   = off_bipolar_highlighted_color
                drawOrder           = [[on_bipolar_locations, on_bipolar_color, on_bipolar_radius],
                                       [cone_locations, cone_color, cone_radius],
                                       [horizontal_locations, horizontal_color, horizontal_radius],
                                       [off_bipolar_locations, off_bipolar_color, off_bipolar_radius]] 
            
            for locations, color, radius in drawOrder:
                for x, y in locations:
                    pygame.draw.circle(display, color, (x,y), radius)
                    
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
                          estimated_maximum_activity=1.0):
        pygame.init()        
        screen_size = (self.grid_width, self.grid_height)
        display     = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(layer_name+" Activity Timestep 0")
        
        background_color = (255, 255, 255)
        
        radius          = int(layer.nearest_neighbor_distance_gridded/2)
        max_activity    = np.amax(activities)
        min_activity    = np.amin(activities)
        max_activity    = max(max_activity, estimated_maximum_activity)
        min_activity    = min(min_activity, estimated_minimum_activity)
        print "Max",layer_name,"Activity Value:", max_activity
        print "Min",layer_name,"Activity Value:", min_activity
        
        timestep        = 0
        end_timestep    = len(activities)-1
        
        running = True
        while running:
            display.fill(background_color)
        
            for n in range(layer.neurons):
                x, y        = layer.locations[n]
                activity    = activities[timestep][0,n]                
                percent     = (activity-min_activity) / (max_activity-min_activity)
                if percent < 0.5:   color = (0,0,2*percent*255)
                else:               color = (2*(percent-0.5)*255,0,0)
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



#    def visualizeCellPlacement(self, layer, cell_color=(0,0,0)):
#        pygame.init()
#        
#        screen_size = (self.grid_width, self.grid_height)
#        display = pygame.display.set_mode(screen_size)
#        background_color = (255, 255, 255)
#        
#        display.fill(background_color)
#
#        radius  = int(layer.nearest_neighbor_distance_gridded/2.0) 
#        for n in range(layer.neurons):
#            x, y = layer.locations[n]
#            pygame.draw.circle(display, cell_color, (x,y), radius)
#            pygame.display.update()
#            
#        running = True
#        while running:
#            for event in pygame.event.get():
#                if event.type == QUIT: running = False
#            
#
#    def visualizeConePlacement(self):
#        self.visualizeCellPlacement(self.cone_layer, pygame.Color("#FFCF87"))
#    
#    def visualizeHorizontalPlacement(self):
#        self.visualizeCellPlacement(self.horizontal_layer, pygame.Color("#FFA722"))
#        
#    def visualizeBipolarPlacement(self):
#        self.visualizeCellPlacement(self.bipolar_layer, pygame.Color("#007DFF"))



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

            

        

        
