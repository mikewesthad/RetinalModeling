class DendritePoint(object):

    def __init__(self, retina, dendrite, location):
        self.retina     = None    
        self.dendrite   = None       
        self.location   = location
        self.heading    = None  
        self.inputs     = []
        
        self.registerPointWithGrid()
        
        
    def registerPointWithGrid(self):
        pass
#        self.retina.registerPointWithGrid(self, self.dendrite.neuron)
        
    def __eq__(self, other):
        if self.location == other.location and self.dendrite == other.dendrite:
            return True
        return False