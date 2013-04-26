
import random
import math


"""
Small Retina class to keep hold of the dimensions in real world space and in grid space
"""
class Retina:
    def __init__(self, retinaWidth, retinaHeight, gridSize):
        self.width  = float(retinaWidth)
        self.height = float(retinaHeight)
        self.area   = retinaWidth * retinaHeight
        
        self.gridSize = float(gridSize)
        
        self.gridWidth  = int(self.width / self.gridSize)
        self.gridHeight = int(self.height / self.gridSize)



"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5



"""
Nearest neighbor distance constrained placement of points
    The method involves tracking point locations and tracking exclusion zones around those points
    Random points are generated until:
        A valid point is found (one that is within the bounds and not located within an exclusion zone
        A maximum number of tries has been exhausted
        
    Note: this isn't the most accurate algorithm, but it is *MUCH* faster than the other algorithms I tried
"""
def nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=1000):

    # Set the bounds on the positions
    xmin = 0
    ymin = 0
    xmax = retina.gridWidth - 1
    ymax = retina.gridHeight - 1

    # Convert the minimum distance from world units to grid units
    griddedDistance = minDistance / retina.gridSize
    ceilGriddedDistance = int(math.ceil(griddedDistance))

    # Calculate the number of cells to place
    requiredNumberCells = int(density * (retina.area/densityArea))
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

    return currentNumberCells, positions
        

def densityStatistics(retina, positions):
    lstPositions    = list(positions)
    numberPositions = len(lstPositions)

    distanceSum         = 0.0
    maxDistance         = 0.0
    minDistance         = 9999999999999.9

    distances = []

    for a in range(numberPositions):
        aLocID = lstPositions[a]
        ax, ay = aLocID.split(".")     # Could also use map(int, a.split("."))
        ax, ay = int(ax), int(ay)
        for b in range(a+1, numberPositions):
            bLocID = lstPositions[b]
            bx, by = bLocID.split(".")
            bx, by = int(bx), int(by)

            distance = linearDistance(ax, ay, bx, by)
            distances.append(distance)
            
    meanDistance    = sum(distances)/len(distances)
    maxDistance     = max(distances)
    minDistance     = min(distances)

    varianceSquared = 0.0
    for d in distances:
        varianceSquared += (d - meanDistance)**2
    stdev = (varianceSquared/len(distances))**0.5

    meanDistance    *= retina.gridSize
    maxDistance     *= retina.gridSize
    minDistance     *= retina.gridSize
    stdev           *= retina.gridSize
    
    return meanDistance, maxDistance, minDistance, stdev
    

            
        
    


um_to_m = 1/1000000.0
m_to_um = 1/um_to_m

retinaWidth     = 1000 *  um_to_m
retinaHeight    = 1000 *  um_to_m
retinaGridSize  = 100 * um_to_m
retina          = Retina(retinaWidth, retinaHeight, retinaGridSize)


minDistance     = 10 * um_to_m
density         = 1000.0
densityArea     = retinaWidth * retinaHeight
numberCells,ps  = nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=10000)

print numberCells
m, ma, mi, sd = densityStatistics(retina, ps)
print m*m_to_um, ma*m_to_um, mi*m_to_um, sd*m_to_um


##import cProfile
##cProfile.run("print nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=100)")
##cProfile.run("print nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=1000)")
##cProfile.run("print nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=10000)")



