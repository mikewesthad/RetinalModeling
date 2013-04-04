"""
Retinal Class Definitions

Jason Farina
2013/04/04
"""
import random

outputs = {'gly':  False,
           'glu':  False,
           'gab':  False,
           'ach':  False}

class locationID(object):
    """This class specifies methods for handling retinal grid locations.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

def generateLocations(n):
    locations = []
    x = random.randint(0,100)
    y = random.randint(0,100)
    for i in range(n):
        axis = random.randint(0,1)
        power = random.randint(0,1)
        if axis:
            x += pow(-1,power)
        else:
            y += pow(-1,power)
        pos = locationID(x,y)
        locations.append(pos)
    return locations

dendrite = generateLocations(5)
for d in dendrite:
    print d.x, d.y

class Dendrite(object)
    """A Dendrite is a set of sequential locations on the retinal grid that
    does not bifurcate.  In essence it is a section of a full, bifurcating
    dendrite.  The order is from most proximal to most distal location.
    """

    def __init__(self, neuron, locations):
        """Creates a new dendrite."""
        self.neuron = neuron    #The neuron object to which this dendrite belongs
        self.locations = locations
        self.points = []
        self.parent = None      #The dendrite from whose end this one starts
        self.children = []      #The dendrites that branch from the end of this one
        
    def registerWithRetinalGrid(self):
        """Informs the retinal grid at all corresponding locations of the
        dendrite's presence.
        """
        #RetinalGrid needs to be defined
        
    def initPoints(self):
        """Intantiates a DendritePoint object at each location in self.locations.
        """
        #Can do
        
    def estInputs(self):
        """Searches through all dendritic locations for other neurons present
        and updates self.inputs to include those that satisfy the conection
        requirements.
        """
        #RetinalGrid needs to be defined

    def calculateSomaPointHeading(pos):
        """Given a locationID, calculates a heading from its neuron's soma to
        that location.  Returns an angle.
        """
        #Needs Neuron class
        
    
        


class DendritePoint(object):
    """A DendritePoint is a dendrite location on the retinal grid."""

    def __init__(self, dendrite, location):
        """Create a point along a dendrite.
        """
        self.dendrite = dendrite
        self.compartment = None
        self.location = location
        self.is_output_zone = True
        self.outputs = outputs
        self.inputs = []


class Compartment(object):
    """A collection of points along a dendrite.  The compartment is the
    fundamental unit of analysis in the model.
    """ 

    def __init__(self):
        """Create a new compartment."""
        self.dendrite_points = []   
        self.inputs = []            #other compartments
        self.outputs = outputs
        self.center = None

    def registerWithGrid(self):
        """Lets all of the corresponding retinal grid points know that he
        is here.
        """
        #RetinalGrid needs to be defined

    def getInputs(self):
        """Updates self.inputs to contain all other compartments which input
        to this one.
        """
        #Can do once two dendrites have overlapping compartments

    def updateActivity(self):
        """Based onthe current inputs, this method updates the internal
        potential and thus the levels of neurotransmitters to be output.
        """
        #Need inputs

    def getOutputs(self, nt_type):
        """Given a type of neurotransmitter, returns the amount released
        from this compartment per retinal grid location.
        """
        #Can do

    def calculateCenter(self):
        """Determines the retinal grid location that represents the "center"
        of the compartment.  Used for purpose of calculating distances from
        this compartment.
        """
        #Can do

    


        
