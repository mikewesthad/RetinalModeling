class Compartment:
    """A collection of points along a dendrite.  The compartment is the
    fundamental unit of analysis in the model.
    """ 

    def __init__(self, neighbor, neuron, grid):
        """Create a new compartment."""
        self.neighbor_proximal = neighbor
        self.neighbor_distal = []
        self.grid = grid 
        self.neuron = neuron
        self.points = []   
        self.inputs = []            #other compartments
                                    #will be recast as dict = {elem: freq}
        self.outputs = Outputs()
        self.center = None
        self.nt_accepted = set()
        
        self.neuron.compartments.append(self)
        
    def addDendritePoint(self, dendrite_point):
        self.points.append(dendrite_point)
        dendrite_point.compartment = self
        


class DendritePoint(object):
    """A DendritePoint is a dendrite location on the retinal grid."""

    def __init__(self, dendrite, location):
        """Create a point along a dendrite.
        """
        self.dendrite = dendrite
        self.grid = dendrite.neuron.grid         
        self.location = location
        self.registerWithGrid()
        self.heading = None
        self.compartment = None       

        self.inputs = []
        self.nt_accepted = self.dendrite.neuron.nt_accepted 
        
        self.is_output_zone = True
        self.outputs = Outputs()
        self.initOutputs()
        
        
    def initOutputs(self):
        for nt in self.dendrite.neuron.nt_out:
            self.outputs.setIsOutput(nt, True)
            
    def registerWithGrid(self):
        """Informs the retinal grid at all corresponding locations of the
        dendrite's presence.
        """
        self.grid.registerLocation(self.location, self)