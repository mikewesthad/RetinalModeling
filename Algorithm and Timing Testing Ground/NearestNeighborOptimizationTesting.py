class Retina:
    
    def __init__(self, retinaWidth, retinaHeight, gridSize):
        self.width  = float(retinaWidth)
        self.height = float(retinaHeight)
        self.area   = retinaWidth * retinaHeight
        
        self.gridSize = float(gridSize)
        
        self.gridWidth  = int(self.width / self.gridSize)
        self.gridHeight = int(self.height / self.gridSize)


import random
import math


def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5


def nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=1000, graph=False):
    if graph:
        import matplotlib.pyplot as plt
        xs = []
        ys = []
        xsExcluded = []
        ysExcluded = []

    xmin = 0
    xmax = retina.gridWidth - 1
    ymin = 0
    ymax = retina.gridHeight - 1
    
    requiredNumberCells = int(density * (retina.area/densityArea))
    currentNumberCells  = 0

    excludedPositions = set()

    while currentNumberCells < requiredNumberCells:

        x = random.randint(xmin, xmax)
        y = random.randint(ymin, ymax)
        locID = str(x) + "." + str(y)
        randTries = 0
        while locID in excludedPositions:
            x = random.randint(xmin, xmax)
            y = random.randint(ymin, ymax)
            locID = str(x) + "." + str(y)
            randTries += 1
            if randTries > maxRandTries: break
        if randTries > maxRandTries: break    
            
        excludedPositions.add(locID)
        if graph:
            xs.append(x)
            ys.append(y)
        

        griddedDistance = minDistance / retina.gridSize
        ceilGriddedDistance = int(math.ceil(griddedDistance))

        left            = max(x - ceilGriddedDistance, xmin)
        right           = min(x + ceilGriddedDistance, xmax)
        up              = max(y - ceilGriddedDistance, ymin)
        down            = min(y + ceilGriddedDistance, ymax)

        for x2 in range(left, right+1):
            for y2 in range(up, down+1):
                if linearDistance(x, y, x2, y2) < griddedDistance:
                    locID = str(x2) + "." + str(y2)
                    excludedPositions.add(locID)
                    if graph:
                        xsExcluded.append(x2)
                        ysExcluded.append(y2)

        currentNumberCells += 1

    if graph:
        plt.scatter(xs,ys, c="b", edgecolors='none')
##        plt.scatter(xsExcluded,ysExcluded,c="r", edgecolors='none')
        plt.show()

    return currentNumberCells



def nearestNeighbor(retina, minDistance, density, densityArea, graph=False):

    if graph:
        import matplotlib.pyplot as plt
        xs = []
        ys = []
        xsExcluded = []
        ysExcluded = []



    allowablePositions = {}
    for gw in range(retina.gridWidth):
        for gh in range(retina.gridHeight):
            locationID = str(gw)+"."+str(gh)
            allowablePositions[locationID] = True

    requiredNumberCells = int(density * (retina.area/densityArea))
    currentNumberCells  = 0

    while currentNumberCells < requiredNumberCells:
        keys = list(allowablePositions.keys())
        if len(keys) == 0: break
        
        locID = random.choice(keys)
        del allowablePositions[locID]
        gx, gy = locID.split(".")
        gx = int(gx)
        gy = int(gy)
        
        if graph:
            xs.append(gx)
            ys.append(gy)

        griddedDistance = minDistance / retina.gridSize
        ceilGriddedDistance = int(math.ceil(griddedDistance))

        left            = max(gx - ceilGriddedDistance, 0)
        right           = min(gx + ceilGriddedDistance, retina.gridWidth-1)
        up              = max(gy - ceilGriddedDistance, 0)
        down            = min(gy + ceilGriddedDistance, retina.gridHeight-1)

        for x in range(left, right+1):
            for y in range(up, down+1):
                if linearDistance(x, y, gx, gy) < griddedDistance:
                    locID = str(x) + "." + str(y)
                    if allowablePositions.has_key(locID):
                        del allowablePositions[locID]
                        if graph:
                            xsExcluded.append(x)
                            ysExcluded.append(y)

        currentNumberCells += 1

    if graph:
        plt.scatter(xs,ys, c="b", edgecolors='none')
        plt.scatter(xsExcluded,ysExcluded,c="r", edgecolors='none')
        plt.show()

    return currentNumberCells


def nearestNeighborSet(retina, minDistance, density, densityArea, graph=False):

    if graph:
        import matplotlib.pyplot as plt
        xs = []
        ys = []
        xsExcluded = []
        ysExcluded = []



    allowablePositions = set()
    for gw in range(retina.gridWidth):
        for gh in range(retina.gridHeight):
            locID = str(gw)+"."+str(gh)
            allowablePositions.add(locID)

    requiredNumberCells = int(density * (retina.area/densityArea))
    currentNumberCells  = 0

    while currentNumberCells < requiredNumberCells:
        if len(allowablePositions) == 0: break
        
        locID = random.choice(list(allowablePositions))
        allowablePositions.remove(locID)
        gx, gy = locID.split(".")
        gx = int(gx)
        gy = int(gy)
        
        if graph:
            xs.append(gx)
            ys.append(gy)

        griddedDistance = minDistance / retina.gridSize
        ceilGriddedDistance = int(math.ceil(griddedDistance))

        left            = max(gx - ceilGriddedDistance, 0)
        right           = min(gx + ceilGriddedDistance, retina.gridWidth-1)
        up              = max(gy - ceilGriddedDistance, 0)
        down            = min(gy + ceilGriddedDistance, retina.gridHeight-1)

        for x in range(left, right+1):
            for y in range(up, down+1):
                if linearDistance(x, y, gx, gy) < griddedDistance:
                    locID = str(x) + "." + str(y)
                    if locID in allowablePositions:
                        allowablePositions.remove(locID)
                        if graph:
                            xsExcluded.append(x)
                            ysExcluded.append(y)

        currentNumberCells += 1

    if graph:
        plt.scatter(xs,ys, c="b", edgecolors='none')
        plt.scatter(xsExcluded,ysExcluded,c="r", edgecolors='none')
        plt.show()

    return currentNumberCells

    
    


um_to_m = 1/1000000.0
m_to_um = 1/1000000.0



retinaWidth     = 1000 *  um_to_m
retinaHeight    = 1000 *  um_to_m
retinaGridSize  = 1 * um_to_m
retina = Retina(retinaWidth, retinaHeight, retinaGridSize)


minDistance     = 10 * um_to_m
density         = 10000.0
densityArea     = retinaWidth * retinaHeight

import cProfile
cProfile.run("print nearestNeighbor(retina, minDistance, density, densityArea)")
cProfile.run("print nearestNeighborSet(retina, minDistance, density, densityArea)")
cProfile.run("print nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=100)")
cProfile.run("print nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=1000)")
cProfile.run("print nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=10000)")




##print nearestNeighborRandom(retina, minDistance, density, densityArea, maxRandTries=1000, graph=True)



