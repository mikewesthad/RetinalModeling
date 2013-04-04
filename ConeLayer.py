import math
import random
from Constants import *

from time import clock


"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5

class ConeLayer:

    def __init__(self, retina, nearest_neighbor_distance, minimum_required_density,
                 input_field_radius, stimulus):

        self.retina = retina
        
        self.nearest_neighbor_distance  = nearest_neighbor_distance
        self.nearest_neighbor_distance_gridded  = nearest_neighbor_distance / retina.gridSize
        
        self.minimum_required_density   = minimum_required_density

        density_area                    = 1 * MM_TO_M * MM_TO_M
        self.minimum_required_cells     = int(minimum_required_density * (retina.area/density_area))

        self.locations  = []
        self.activities = {}
        self.inputs     = {}

        self.placeNeurons()

        self.input_field_radius         = input_field_radius
        self.input_field_radius_gridded = input_field_radius / retina.gridSize
        
        self.stimulus           = stimulus
        self.establishInputs()  


    def updateActivity(self):
        
        
        s1 = clock()
        t = 0.0
        for locID in self.locations:
            connectedPixels = self.inputs[locID]
            coneActivity = 0.0
            for pixel in connectedPixels:
                pixelID, pixelWeight = pixel
                st = clock()
                pixelActivity = self.stimulus.getPixelIntensity(pixelID)
                t += clock()-st
                coneActivity += (pixelActivity*-2.0 + 1.0) * pixelWeight
            self.activities[locID] = coneActivity

        print "Cone Total Update Time",clock()-s1
        print "Cone Accessing Stimulus Time",t
            
            
    
    def establishInputs(self):
        for locID in self.locations:
            x, y = locID.split(".")
            x, y = float(x), float(y)

            griddedRadius = self.input_field_radius / self.retina.gridSize
            left    = x - griddedRadius
            right   = x + griddedRadius
            up      = y - griddedRadius
            down    = y + griddedRadius
            coneBox = [left, right, up, down]

            connectedPixels = self.stimulus.getPixelOverlaps(coneBox)
            connectedPixels = self.inputWeightingFunction(connectedPixels)
            self.inputs[locID] = connectedPixels


    def inputWeightingFunction(self, inputs):
        weightSum = 0.0
        for i in range(len(inputs)):
            inputID, inputWeight = inputs[i]
            weightSum += inputWeight
        for i in range(len(inputs)):
            inputWeight = inputs[i][1]
            inputWeight /= weightSum
            inputs[i][1] = inputWeight
        return inputs
        
            
        

        

    """
    Nearest neighbor distance constrained placement of points
        The method involves tracking point locations and tracking exclusion zones around those points
        Random points are generated until:
            A valid point is found (one that is within the bounds and not located within an exclusion zone
            A maximum number of tries has been exhausted
    """
    def placeNeurons(self, maxRandTries=1000):
        # Set the bounds on the positions
        xmin = 0
        ymin = 0
        xmax = self.retina.gridWidth-1
        ymax = self.retina.gridHeight-1

        # Convert the minimum distance from world units to grid units
        griddedDistance     = self.nearest_neighbor_distance / self.retina.gridSize
        ceilGriddedDistance = int(math.ceil(griddedDistance))

        # Calculate the number of cells to place
        requiredNumberCells = self.minimum_required_cells
        currentNumberCells  = 0

        # Create empty sets to hold the selected positions and the excluded positions
        positions           = set()
        excludedPositions   = set()

        while currentNumberCells < requiredNumberCells:

            # Pick a random point
            x       = random.randint(xmin, xmax)
            y       = random.randint(ymin, ymax)
            locID   = str(x) + "." + str(y)

            # Regenerate random point until a valid point is found
            randTries = 0
            while locID in excludedPositions:
                x = random.randint(xmin, xmax)
                y = random.randint(ymin, ymax)
                locID = str(x) + "." + str(y)
                
                randTries += 1
                if randTries > maxRandTries: break

            # If too many attempts were made to generate a new point, exit loop
            if randTries > maxRandTries: break    

            # Update the sets with the newly selected point
            excludedPositions.add(locID)
            positions.add(locID) 

            # Find the bounding box of excluded coordinates surrounding the new point
            left            = max(x - ceilGriddedDistance, xmin)
            right           = min(x + ceilGriddedDistance, xmax)
            up              = max(y - ceilGriddedDistance, ymin)
            down            = min(y + ceilGriddedDistance, ymax)

            # Check if each point in the bounding box is within the minimum distance radius
            # If so, add it to the exclusion set
            for x2 in range(left, right+1):
                for y2 in range(up, down+1):
                    if linearDistance(x, y, x2, y2) < griddedDistance:
                        locID = str(x2) + "." + str(y2)
                        excludedPositions.add(locID)

            currentNumberCells += 1

        self.locations = list(positions)
        print "Generated", currentNumberCells, "Neurons"
