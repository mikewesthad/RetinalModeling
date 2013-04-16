class Compartment:

    def __init__(self, neighbor, neuron):
        self.neighbor_proximal = neighbor
        self.neighbor_distal = []
        self.neuron = neuron
        self.points = []   
        self.inputs = []       
        
        self.neuron.compartments.append(self)
        
    def addPoint(self, point):
        self.points.append(point)