import math
import random
import numpy as np
import pygame
from pygame.locals import *
from Constants import *



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
        
        self.nearest_neighbor_distance  = cone_layer.nearest_neighbor_distance
        self.nearest_neighbor_distance_gridded  = cone_layer.nearest_neighbor_distance_gridded
        
        self.activities[0][0,20] = 1.0
        self.activities[0][0,21] = 1.0
        self.activities[0][0,22] = 1.0


    def establishLateralConnections(self):
        # An (n x n) array
        self.lateralWeights = np.zeros((self.neurons, self.neurons))
        
        # Fill the array with distances between each neuron
        for n1 in range(self.neurons):
            x1, y1 = self.locations[n1]
            for n2 in range(n1, self.neurons):
                x2, y2 = self.locations[n2]
                distance = linearDistance(x1, y1, x2, y2)
                self.lateralWeights[n1, n2] = distance
                if n1 != n2: self.lateralWeights[n2, n1] = distance
        
        # Perform e^(-distance**2/width) on each element in the distance matrix
        self.lateralWeights = np.exp(-(self.lateralWeights)**2/(2.0*self.diffusionDistance**2.0))
        
        # Get the sum of each row
        rowSum = np.sum(self.lateralWeights, 1)
        
        # Reshape the rowSum into a column vector since sum removes a dimension
        rowSum.shape = (self.neurons, 1)
        
        # Normalize the weight matrix
        self.lateralWeights = self.lateralWeights / rowSum

    def initializeActivties(self):
        self.activities = []
        for i in range(self.history_size):
            self.activities.append(np.zeros((1, self.neurons)))
    
    
    def playHistory(self):
        
        pygame.init()
        screenSize = (self.retina.gridWidth, self.retina.gridHeight)
        displaySurface = pygame.display.set_mode(screenSize)
        
        backgroundColor = (255,255,255)
        horizontalColor = (255,0,0)
        maxActivity = np.max(self.activities)
        radius = int(self.nearest_neighbor_distance_gridded/2)
        
        time = len(self.activities) - 1
        
        minDist = 1000000.0
        minLoc = (0,0)
        centerx = self.retina.gridWidth/2.0
        centery = self.retina.gridHeight/2.0
        for n in range(self.neurons):
            x, y = self.locations[n]
            d = linearDistance(x,y,centerx,centery)
            if d < minDist:
                minDist = d
                minLoc = (x,y)
            

            
        running = True
        while running:
            displaySurface.fill(backgroundColor)
        
            for n in range(self.neurons):
                x, y            = self.locations[n]
                activity        = self.activities[time][0,n]
                percentOfMax    = activity/maxActivity
                horizontalColor = (percentOfMax*255,0,0)
                
                thickness       = 1
                if percentOfMax > 0.00001: thickness = 0
                pygame.draw.circle(displaySurface, horizontalColor, (x,y), radius, thickness) 
                
            
            
            pygame.draw.circle(displaySurface, (0,0,255), minLoc, 2) 
            pygame.draw.circle(displaySurface, (0,0,255), minLoc, int(self.diffusionDistance), 5) 
            
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        time -= 1
                        if time == -1: time = len(self.activities) - 1
                    elif event.key == K_LEFT:
                        time += 1
                        if time == len(self.activities): time = 0
                        
            pygame.display.update()
        
    
    def drawActivities(self):
        
        pygame.init()
        screenSize = (self.retina.gridWidth, self.retina.gridHeight)
        displaySurface = pygame.display.set_mode(screenSize)
        
        backgroundColor = (255,255,255)
        horizontalColor = (255,0,0)
        displaySurface.fill(backgroundColor)
        
        maxActivity = np.max(self.activities)
        radius = int(self.nearest_neighbor_distance_gridded/2)
        
        for n in range(self.neurons):
            x, y            = self.locations[n]
            activity        = self.activities[0][0,n]
            percentOfMax    = activity/maxActivity
            horizontalColor = (percentOfMax*255,0,0)
            
            thickness       = 1
            if percentOfMax > 0.01: thickness = 0
            pygame.draw.circle(displaySurface, horizontalColor, (x,y), radius, thickness)
            
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            pygame.display.update()


    def updateActivity(self):
        del self.activities[-1]
        lastActivity = self.activities[0]
        newActivity = np.dot(lastActivity, self.lateralWeights)
        self.activities.insert(0, newActivity)
        
    def drawLocations(self):
        
        pygame.init()
        screenSize = (self.retina.gridWidth, self.retina.gridHeight)
        displaySurface = pygame.display.set_mode(screenSize)
        
        backgroundColor = (255,255,255)
        horizontalColor = (255,0,0)
        displaySurface.fill(backgroundColor)
        
        for loc in self.locations:
            x, y = loc
            pygame.draw.circle(displaySurface, horizontalColor, (x,y), int(self.diffusionDistance), 1)
            
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            pygame.display.update()
            
