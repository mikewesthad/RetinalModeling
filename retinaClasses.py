"""
Retinal Class Definitions

Jason Farina
2013/04/04
"""
import random

class RetinalGrid(object):
    """The RetinalGrid keeps track of all neuron classes that are located at 
    each of its locations.
    """
    grid = {}    
    types_accepted = ['Neuron', 'Dendrite', 'DendritePoint', 'Compartment']    
    type_index = {'Neuron': 0, 'Dendrite': 1, 'DendritePoint': 2, 'Compartment': 3}    
    
    def __init__(self, width, height, spacing):
        """Creates retinal_grid dictionary by taking in the grid width, grid 
        height, and grid spacing in micrometers.
        """
        width = width/spacing   #convert from um to rgu's (retinal grid units)
        height = height/spacing #convert from um to rgu's
        for w in range(width+1):
            for h in range(height+1):
                self.grid[(w,h)] = [ [], [], [], [] ]
                
    def registerLocation(self, member):
        """Registers member with the grid at the single point specified in the
        'location' attribute.  Cannot handle members that have a multiple
        'locations' attribute.
        """
        type_info = str(type(member)).split(".")
        type_info = type_info[1].split("'")
        print(type_info)
        type_tag = type_info[0]        
        assert type_tag in self.types_accepted, '{0} not accepted.'.format(member)
        assert hasattr(member, 'location'), 'Can only register objects with single "location."'        
        index = self.type_index[type_tag]
        key = member.location.x, member.location.y
        self.grid[key][index].append(member)

r = RetinalGrid(100,100,1)

outputs = {'gly':  False,
           'glu':  False,
           'gab':  False,
           'ach':  False}

class locationID(object):
    """This class specifies methods for handling retinal grid locations.
    """
    def __init__(self, x, y):
        self.x = int(round(x))
        self.y = int(round(y))
        
    @property
    def xfloat(self):
        return float(self.x)
    
    @property
    def yfloat(self):
        return float(self.y)
        

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
    

class Dendrite(object):
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
        """Instantiates a DendritePoint object at each location in self.locations.
        """
        for loc in self.locations:
	    p = DendritePoint(self, loc)
            self.points.append(p)            
        
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
        x_sum = 0.0
        y_sum = 0.0        
        n = len(self.dendrite_points)        
        for p in self.dendrite_points:
            x_sum += p.location.x
            y_sum += p.location.y
        centroid_x = x_sum/n
        centroid_y = y_sum/n
        self.center = locationID(centroid_x, centroid_y)
            

d = Dendrite("None", dendrite)
d.initPoints()   
c = Compartment()
c.dendrite_points = d.points
c.calculateCenter()