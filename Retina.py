from time import clock
import numpy as np
import pygame
from pygame.locals import *
from ConeLayer import ConeLayer
from HorizontalLayer import HorizontalLayer



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
        cone_input_delay = 1
        start_time = clock()
        self.horizontal_layer = HorizontalLayer(self, self.cone_layer, cone_input_delay,
                                                self.history_size, input_strength,
                                                decay_rate, diffusion_radius)
        print "Horizontal Layer Construction Time:", clock() - start_time





###############################################################################
# Visualization functions
###############################################################################


    def visualizeConePlacement(self):
        pygame.init()
        
        screen_size = (self.grid_width, self.grid_height)
        display     = pygame.display.set_mode(screen_size)
        
        background_color    = (255, 255, 255)
        cone_color          = (233, 122, 68)
        
        display.fill(background_color)

        cl      = self.coneLayer
        radius  = int(cl.nearest_neighbor_distance_gridded/2.0) 
        for n in range(cl.neurons):
            x, y = cl.locations[n]
            pygame.draw.circle(display, cone_color, (x,y), radius)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            pygame.display.update()
            
            
            
    def playConeActivity(self):
        pygame.init()
        
        screen_size = (self.grid_width, self.grid_height)
        display     = pygame.display.set_mode(screen_size)
        
        background_color = (255, 255, 255)
        
        cl              = self.cone_layer
        radius          = int(cl.nearest_neighbor_distance_gridded/2)
        
        timestep        = 0
        end_timestep    = len(self.cone_activities)-1
        print "Cone Activity Timestep", timestep
            
        running = True
        while running:
            
            display.fill(background_color)
        
            for n in range(cl.neurons):
                x, y       = cl.locations[n]
                activity   = self.cone_activities[timestep][0,n]
                if activity < 0:
                    color = (0,0,-1*activity*255)
                else: 
                    color = (activity*255,0,0)
                pygame.draw.circle(display, color, (x,y), radius) 
                
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        timestep += 1
                        if timestep > end_timestep: timestep = 0
                        print "Cone Activity Timestep", timestep
                    elif event.key == K_LEFT:
                        timestep -= 1
                        if timestep < 0: timestep = end_timestep
                        print "Cone Activity Timestep", timestep
                        
            pygame.display.update()
            
    def playHorizontalActivity(self):
        pygame.init()
        
        screen_size = (self.grid_width, self.grid_height)
        display     = pygame.display.set_mode(screen_size)
        
        background_color = (255, 255, 255)
        
        hl              = self.horizontal_layer
        radius          = int(hl.nearest_neighbor_distance_gridded/2)
        max_activity    = np.amax(self.horizontal_activities)
        min_activity    = np.amin(self.horizontal_activities)
        max_activity    = max(max_activity, 1.0)
        min_activity    = min(min_activity, -1.0)
        print "Max Horizontal Activity Value", max_activity
        print "Min Horizontal Activity Value", min_activity
        
        timestep        = 0
        end_timestep    = len(self.horizontal_activities)-1
        print "Horizontal Activity Timestep", timestep
            
        running = True
        while running:
            
            display.fill(background_color)
        
            for n in range(hl.neurons):
                x, y        = hl.locations[n]
                activity    = self.horizontal_activities[timestep][0,n]                
                percent     = (activity-min_activity) / (max_activity-min_activity)
                if percent < 0.5:
                    color = (0,0,2*percent*255)
                else: 
                    color = (2*(percent-0.5)*255,0,0)
                    
                try:
                    pygame.draw.circle(display, color, (x,y), radius) 
                except:
                    print activity
                    print percent
                    print color
                    asds
                
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        timestep += 1
                        if timestep > end_timestep: timestep = 0
                        print "Horizontal Activity Timestep", timestep
                    elif event.key == K_LEFT:
                        timestep -= 1
                        if timestep < 0: timestep = end_timestep
                        print "Horizontal Activity Timestep", timestep
                        
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

            

        

        
