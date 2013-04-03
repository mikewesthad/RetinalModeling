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
