import pygame, math
from pygame.locals import *
import numpy as np


"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5



pygame.init()
fpsClock = pygame.time.Clock()


framerate   = 30.0  # Frames per second
movieWidth  = 800   # Width (pixels) of the movie frame
movieHeight = 600   # Height (pixels) of the movie frame

barOrientation      = 0.0       # Orientation measured in degrees (on a circle)
barWidth            = 20.0      # Size (pixels) in direction of motion
barHeight           = 60.0      # Size (pixels) in direction perpendicular to motion
barSpeed            = 10.0      # Speed (pixels/second)
barMovementDistance = 400       # Pixels the bar should travel before stopping
barColor            = (0,0,0)       
backgroundColor     = (255,255,255)
startBarPosition    = (400,300)



# Create a list of bar vertices centered around startBarPosition
# The unrotated upper left vertex would be (1/2 width, 1/2 height)
# Rotating that vertex becomes (x*cos(a)-y*sin(a), x*cos(a)-y*sin(a))
halfWidth  = barWidth/2.0
halfHeight = barHeight/2.0
cosOrientation = math.cos(barOrientation * math.pi/180.0)
sinOrientation = math.sin(barOrientation * math.pi/180.0)

# Find the position of rotated vertices if the bar were centered on (0,0)
ulx = (-halfWidth) * cosOrientation - halfHeight * sinOrientation
uly = (-halfWidth) * sinOrientation + halfHeight * cosOrientation
urx = halfWidth * cosOrientation - halfHeight * sinOrientation
ury = halfWidth * sinOrientation + halfHeight * cosOrientation
lrx = halfWidth * cosOrientation - (-halfHeight) * sinOrientation
lry = halfWidth * sinOrientation + (-halfHeight) * cosOrientation
llx = (-halfWidth) * cosOrientation - (-halfHeight) * sinOrientation
lly = (-halfWidth) * sinOrientation + (-halfHeight) * cosOrientation
barVertices = [[ulx, uly], [urx, ury], [lrx, lry], [llx, lly]]

# Shift the bar vertices so that it is now centered on startBarPosition
for i in range(len(barVertices)):
    barVertices[i][0] += startBarPosition[0]
    barVertices[i][1] += startBarPosition[1]


displaySurface = pygame.display.set_mode((movieWidth, movieHeight))


# Calculate the movement direction of the bar from the orientation
dx = cosOrientation
dy = sinOrientation
startPos = [barVertices[0][0], barVertices[0][1]]

frameTime = 1.0/framerate
frameNumber = 0

distanceTraveled = 0.0

chunkStart = True
framesInChunk = 0
chunkSize = 1

while distanceTraveled < barMovementDistance:

    # Erase the screen and draw the bar
    displaySurface.fill(backgroundColor)
    pygame.draw.polygon(displaySurface, barColor, barVertices, 0)

    # Update the display
    pygame.display.update()
    pygame.image.save(displaySurface, str(frameNumber)+".png")

##    # Get the display in the form of a numpy array
##    # Each element is an integer corresponding to the RGB value
##    # Bitshift to get one of the color channels (& 255 = red)
####    frame = pygame.surfarray.pixels2d(displaySurface) & 255
##
##    if framesInChunk == 0:
##        frame = pygame.surfarray.pixels2d(displaySurface) & 255
##        frame.flatten()
##    else:
##        newFrame = pygame.surfarray.pixels2d(displaySurface) & 255
##        newFrame.flatten()
##        frame = np.vstack((frame, newFrame))
##        
##    framesInChunk += 1
##
##    # Save the numpy frame to a file
##    if framesInChunk >= chunkSize:
##        np.savetxt("Frame"+str(frameNumber)+".gz", frame)
##        framesInChunk = 0
    

    # Increment time to step to the next frame
    frameNumber += 1

    # Move the bar
    for i in range(len(barVertices)):
        barVertices[i][0] += dx * frameTime * barSpeed
        barVertices[i][1] += dy * frameTime * barSpeed

    # Update the distance the bar has traveled
    currentPos          = barVertices[i][:]
    distanceTraveled    = linearDistance(currentPos[0], currentPos[1], startPos[0], startPos[1])
