from ConeLayer import ConeLayer
from HorizontalLayer import HorizontalLayer
import random
import pygame
from pygame.locals import *

from time import clock



"""
Small Retina class to keep hold of the dimensions in real world space and in grid space
"""
class Retina:
    def __init__(self, retinaWidth, retinaHeight, gridSize, timestep, stimulus):

        self.width  = float(retinaWidth)
        self.height = float(retinaHeight)
        self.area   = retinaWidth * retinaHeight
        
        self.gridSize = float(gridSize)
        
        self.gridWidth  = int(self.width / self.gridSize)
        self.gridHeight = int(self.height / self.gridSize)

        self.stimulus = stimulus

        self.time       = 0.0 
        self.timestep   = timestep


    def runModel(self, duration):
        endTime = self.time + duration
        while self.time < endTime:
            self.updateActivity()
            self.time += self.timestep
        

    def updateActivity(self):
        print self.time
        
        self.stimulus.update(self.time)
        self.coneLayer.updateActivity()


    def buildHorizontalLayer(self, diffusionDistance):
        s = clock()
        self.horizontalLayer = HorizontalLayer(self, self.coneLayer,
                                               1, 5, self.stimulus, diffusionDistance)
        print "Horizontal Construction Time:",clock() - s
    
    def buildConeLayer(self, minimum_distance, minimum_density, input_field_size):
        s = clock()
        self.coneLayer = ConeLayer(self, minimum_distance, minimum_density,
                                   input_field_size, 5, self.stimulus)
        print "Cone Construction Time:",clock() - s


    def visualizeConeActivity(self):
        pygame.init()
        displaySurface = pygame.display.set_mode((self.gridWidth, self.gridHeight))
        displaySurface.fill((255,255,255))

        cl = self.coneLayer
        radius = int(cl.nearest_neighbor_distance_gridded/2.0) 
        for n in range(cl.neurons):
            cID = cl.locations[n]
            cActivity = cl.activities[0][n]
            x, y = cID.split(".")
            x, y = int(x), int(y)
            color = 255 * ((cActivity+1.0)/2.0)
            pygame.draw.circle(displaySurface, (0,color,color), (x,y), radius, 1)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            pygame.display.update()


    def visualizeConeWeights(self):
        
        pygame.init()
        displaySurface = pygame.display.set_mode((self.gridWidth, self.gridHeight))
        displaySurface.fill((0,0,0))
        
        cl = self.coneLayer
        
        locID   = random.choice(cl.locations)
        

        rectx = self.stimulus.position[0]
        recty = self.stimulus.position[1]        
        rectw = self.stimulus.size[0]      
        recth = self.stimulus.size[1]
        pygame.draw.rect(displaySurface, (255,255,255), (rectx, recty, rectw, recth))

        
        
        connectedPixels = cl.inputs[locID]
        for p in connectedPixels:
            pID, w = p
            x, y = pID.split(".")
            x, y = float(x), float(y)
            rectx = self.stimulus.position[0] + x * self.stimulus.pixelSize
            recty = self.stimulus.position[1] + y * self.stimulus.pixelSize
            rects = self.stimulus.pixelSize
            pygame.draw.rect(displaySurface, (w*255,0,0), (rectx, recty, rects, rects))
            


        # Get cone rectangle
        x, y    = locID.split(".")
        x, y    = float(x), float(y)
        rectx = x - cl.input_field_radius_gridded
        recty = y - cl.input_field_radius_gridded
        rects = 2 * cl.input_field_radius_gridded
        pygame.draw.rect(displaySurface, (0,0,255), (rectx, recty, rects, rects), 1)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            pygame.display.update()

            

        

        
