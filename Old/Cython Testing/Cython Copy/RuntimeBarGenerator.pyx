import pygame, math
from pygame.locals import *
import numpy as np



"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5


"""
The RunTimeBarGenerator class using pygame and numpy to create a moving bar stimulus.

Inputs:
    framerate - frames/second
    movieSize - (w x h) in pixels
    barOrientation - degrees clockwise around unit cirle
    barSize - (w x h) in pixels; w is length in direction of motion, and h is length in
              direction perpendicular to motion
    barSpeed - pixels/second
    barMovementDistance - distance the bar should move from its initial position
    barColor - (R,G,B) color
    backgroundColor - (R,G,B) color
    startBarPosition - (x, y) position in pixels with (0,0) being the upper left

Methods:
    update(deltaTime) - this will update the frame if necessary
    getArray() - this will return a numpy array representing the screen

"""
class RuntimeBarGenerator:

    def __init__(self, framerate=30.0, movieSize=(300,300),
                 barOrientation=20.0, barSize=(20.0,60.0), barSpeed=20.0, barMovementDistance=500.0,
                 barColor=(0,0,0), backgroundColor=(255,255,255),
                 startBarPosition=(0,0)):       

        # Initialize class variables
        self.framerate          = framerate
        self.frameDuration      = 1.0/self.framerate
        self.barColor           = barColor    
        self.backgroundColor    = backgroundColor
        self.movieWidth         = movieSize[0]
        self.movieHeight        = movieSize[1]

        # Create the vertices of the bar
        self.barVertices = []
        self.numVertices = 4
        self.initBarVertices(barSize[0], barSize[1], barOrientation, startBarPosition)
        
        # Calculate the movement direction of the bar from the orientation
        self.headingx = math.cos(barOrientation * math.pi/180.0)
        self.headingy = math.sin(barOrientation * math.pi/180.0)
        self.barSpeed = barSpeed

        # Track a vertex on the bar to calculate distance traveled
        self.startPos           = [self.barVertices[0][0], self.barVertices[0][1]]  # Deep copy
        self.distanceTraveled   = 0.0
        self.maxDistance        = barMovementDistance

        # Initialize the pygame module
        pygame.init()

        # Create a pygame display surface
        self.displaySurface = pygame.display.set_mode(movieSize)
        self.drawBar()

        # Initialize run timing variables
        self.time   = 0.0
        self.frame  = 0

        # Initialize the numpy array representing the screen
        self.npScreen = pygame.surfarray.pixels3d(self.displaySurface)

        self.drawBar()
        self.updateScreenArray()
        pygame.display.update()

    
        
    def initBarVertices(self, width, height, orientation, position):
        # Create a list of bar vertices centered around startBarPosition
        # The unrotated upper left vertex would be (1/2 width, 1/2 height)
        # Rotating that vertex becomes (x*cos(a)-y*sin(a), x*cos(a)-y*sin(a))
        halfWidth  = width/2.0
        halfHeight = height/2.0
        cosOrientation = math.cos(orientation * math.pi/180.0)
        sinOrientation = math.sin(orientation * math.pi/180.0)

        # Find the position of rotated vertices if the bar were centered on (0,0)
        ulx = (-halfWidth) * cosOrientation - halfHeight * sinOrientation
        uly = (-halfWidth) * sinOrientation + halfHeight * cosOrientation
        urx = halfWidth * cosOrientation - halfHeight * sinOrientation
        ury = halfWidth * sinOrientation + halfHeight * cosOrientation
        lrx = halfWidth * cosOrientation - (-halfHeight) * sinOrientation
        lry = halfWidth * sinOrientation + (-halfHeight) * cosOrientation
        llx = (-halfWidth) * cosOrientation - (-halfHeight) * sinOrientation
        lly = (-halfWidth) * sinOrientation + (-halfHeight) * cosOrientation

        # Create vertex list in clockwise order
        self.barVertices = [[ulx, uly], [urx, ury], [lrx, lry], [llx, lly]]

        # Shift the bar vertices so that it is now centered on startBarPosition
        self.moveBar(position[0], position[1])


    def moveBar(self, dx, dy):
        for i in range(self.numVertices):
            self.barVertices[i][0] += dx
            self.barVertices[i][1] += dy

    def updateDistanceTraveled(self):
        x1, y1 = self.barVertices[0]
        x2, y2 = self.startPos
        self.distanceTraveled = linearDistance(x1, y1, x2, y2)

    def drawBar(self):
        self.displaySurface.fill(self.backgroundColor)
        pygame.draw.polygon(self.displaySurface, self.barColor, self.barVertices, 0)
        pygame.display.update()

    def updateScreenArray(self):        
        # The pygame array returned by pygame is of size (rows=width x cols=height) 
        screenRGB = pygame.surfarray.pixels3d(self.displaySurface)                   
        self.npScreen = np.average(screenRGB, 2) / 255.0
    
    def update(self, timestep):

        self.time += timestep

        # Find the elapsed frame time since last update and set the new frame number
        elapsedTime     = 0.0
        frameFromTime   = int(self.time * self.framerate)
        if frameFromTime != self.frame:
            frameDifference = frameFromTime - self.frame
            elapsedTime     = frameDifference * self.frameDuration
            self.frame      = frameFromTime

        # Move the bar
        dx = self.headingx * (elapsedTime * self.barSpeed)
        dy = self.headingy * (elapsedTime * self.barSpeed)
        self.moveBar(dx, dy)

        # Check bar movement distance
        self.updateDistanceTraveled()
        if self.distanceTraveled >= self.maxDistance: return False

        # If the bar has moved, redraw
        if elapsedTime>0:
            self.drawBar()
            self.updateScreenArray()
            pygame.display.update()
            
       
        return True
