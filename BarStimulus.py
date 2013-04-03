import math as m
import numpy as np
from RuntimeBarGenerator import RuntimeBarGenerator


def overlapBetweenRectangles(bbox1, bbox2):
    left1, right1, up1, down1 = bbox1
    left2, right2, up2, down2 = bbox2

    left            = max(left1, left2)
    right           = min(right1, right2) 
    overlapWidth    = right - left
    
    down            = min(down1, down2)  
    up              = max(up1, up2)
    overlapHeight   = down - up

    if overlapWidth>0 and overlapHeight>0:
        return [left, right, up, down], overlapWidth*overlapHeight
    else:
        return -1, -1

    

class BarStimulus:

    def __init__(self, position, pixelSize, barGenerator):

        self.position       = position
        self.pixelSize      = pixelSize
        self.barGenerator   = barGenerator

        left    = position[0]
        right   = position[0] + barGenerator.movieWidth * pixelSize
        up      = position[1]
        down    = position[1] + barGenerator.movieHeight * pixelSize
        self.movieBoundingBox = [left, right, up, down]

    def update(self, timestep):
        self.barGenerator.update(timestep)

    def getPixelIntensity(self, pixelID):
        x, y = pixelID.split(".")
        x, y = int(x), int(y)

        rgbArray    = self.barGenerator.getScreenArray()
        rgb         = rgbArray[x, y, :]
        intensity   = np.average(rgb)/255.0

        return intensity

    def getPixelOverlaps(self, coneBoundingBox):        
        # Find the overlap between the cone and the entire movie
        overlapBox, overlapArea = overlapBetweenRectangles(coneBoundingBox, self.movieBoundingBox)

        # If there is no overlap with movie, no overlapping pixels
        if overlapArea == -1: return []

        # Now to find the overlap between the cone and the overlapping pixels
        overlappingPixels   = []
        totalPixelArea      = self.pixelSize**2
        
        # First, convert the overlapBox from retinal space to pixel space by:
        #   Subtracting the movie's position in retinal space
        #   Dividing by the pixel size
        left, right, up, down = overlapBox
        left    = int(m.floor((left-self.position[0]) / self.pixelSize))
        right   = int(m.ceil((right-self.position[0]) / self.pixelSize))
        up      = int(m.floor((up-self.position[1]) / self.pixelSize))
        down    = int(m.ceil((down-self.position[1]) / self.pixelSize))

        # Now that we have the pixel ranges, we can iterate through them and
        # check each pixel's retinal space bounding box for overlap with the cone
        for pixelx in range(left, right+1):
            for pixely in range(up, down+1):
                pixelLeft   = pixelx * self.pixelSize + self.position[0]
                pixelRight  = pixelLeft + self.pixelSize
                pixelUp     = pixely * self.pixelSize + self.position[1]
                pixelDown   = pixelUp + self.pixelSize
                pixelBox    = [pixelLeft, pixelRight, pixelUp, pixelDown]
                
                overlapBox, overlapArea = overlapBetweenRectangles(coneBoundingBox, pixelBox)

                if overlapArea != -1:
                    overlapPercent  = overlapArea/totalPixelArea
                    pixelID         = str(pixelx)+"."+str(pixely) 
                    overlappingPixels.append([pixelID, overlapPercent])

        return overlappingPixels

                    


                
                

        
        
