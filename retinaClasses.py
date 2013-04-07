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
    width = None
    height = None
    spacing = None    
    
    def __init__(self, width, height, spacing=1):
        """Creates retinal_grid dictionary by taking in the grid width, grid 
        height, and grid spacing in micrometers.
        """
        self.width = width/spacing   #convert from um to rgu's (retinal grid units)
        self.height = height/spacing #convert from um to rgu's
        self.spacing            
            
        for w in range(width+1):
            for h in range(height+1):
                self.grid[(w,h)] = [ [], [], [], [] ]
                
    @property
    def widthWorld(self):
        return self.width*self.spacing
        
    @property
    def heightWorld(self):
        return self.height*self.spacing
    
    def registerLocation(self, location, member):
        """Registers 'member' object with the grid at the 'location'.
        """
        type_info = str(type(member)).split(".")
        type_info = type_info[1].split("'")
        print(type_info)
        type_tag = type_info[0]        
        assert type_tag in self.types_accepted, '{0} not accepted.'.format(member)
        index = self.type_index[type_tag]        
        self.grid[location.key][index].append(member)
        
        
        """        
        if hasattr(member, 'location'): #for 'members' that exist at a single location        
            key = member.location.x, member.location.y
            self.grid[key][index].append(member)
        elif hasattr(member, 'points'): #for 'members' that exist at multiple locations
            for point in member.points:                 #for all points
                key = point.location.x, point.location.y#at the location of the point
                self.grid[key][index].append(member)    #register the member
        """
            
        
    def whosHere(self, location, class_type=None):
        """Returns a list of all of the members of a particular class who are
        present at the specified retinal grid location.
        
        types_accepted = ['Neuron', 'Dendrite', 'DendritePoint', 'Compartment']
        """
        key = location.key
        #assert class_type in self.types_accepted, "That class_type is not accepted."
        index = self.type_index[class_type]
        return self.grid[key][index]

#instantiates a retinal grid 100x100um with 1um spacing
r = RetinalGrid(100,100,1)


outputs = {'gly':  False,
           'glu':  False,
           'gab':  False,
           'ach':  False}

class LocationID(object):
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
        
    @property
    def key(self):
        return self.x, self.y
        

    

class Dendrite(object):
    """A Dendrite is a set of sequential locations on the retinal grid that
    does not bifurcate.  In essence it is a section of a full, bifurcating
    dendrite.  The order is from most proximal to most distal location.
    """
    grid = r    #Hardcoding this instance of the retinal grid as being associated
                #with all dendrites

    def __init__(self, neuron, locations):
        """Creates a new dendrite."""
        self.neuron = neuron    #The neuron object to which this dendrite belongs
        self.locations = locations
        self.points = []
        self.parent = None      #The dendrite from whose end this one starts
        self.children = []      #The dendrites that branch from the end of this one
        
    def registerWithGrid(self):
        """Informs the retinal grid at all corresponding locations of the
        dendrite's presence.
        """
        for point in self.points:
            self.grid.registerLocation(point.location, point)
        
    def initPoints(self):
        """Instantiates a DendritePoint object at each location in self.locations.
        """
        for loc in self.locations:
	    p = DendritePoint(self, loc)
            self.points.append(p)            
        
    def estInputs(self):
        """Searches through all dendritic locations for other neurons present
        and updates self.inputs to include those that satisfy the connection
        requirements.
        """
        #RetinalGrid needs to be defined

    def calculateSomaPointHeading(pos):
        """Given a LocationID, calculates a heading from its neuron's soma to
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
    grid = r    #Hardcoding this instance of the retinal grid as being associated
                #with all dendrites

    def __init__(self):
        """Create a new compartment."""
        self.points = []   
        self.inputs = []            #other compartments
        self.outputs = outputs
        self.center = None

    def registerWithGrid(self):
        """Lets all of the corresponding retinal grid points know that he
        is here.
        """
        for point in self.points:
            self.grid.registerLocation(point.location, self)

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
        n = len(self.points)        
        for p in self.points:
            x_sum += p.location.x
            y_sum += p.location.y
        centroid_x = x_sum/n
        centroid_y = y_sum/n
        self.center = LocationID(centroid_x, centroid_y)
            
#This code creates a random set of sequential locations
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
        pos = LocationID(x,y)
        locations.append(pos)
    return locations
#assignes them to a dendrite
dendrite = generateLocations(5)
#but don't use them
#overwrite random locations with hardcoded ones
locations = []
locations = [LocationID(10,10), LocationID(11,11), LocationID(12,12)]
dendrite = locations

#instantiate a Dendrite with the locations contained in 'dendrite'
for d in dendrite:
    print d.x, d.y
d = Dendrite("None", dendrite)

#who initializes his points
d.initPoints()   
#associates them with a compartment
c = Compartment()
c.points = d.points
c.calculateCenter()
#registers them with the Retinal Grid
d.registerWithGrid()
#then the compartment registers its locations with the grid
c.registerWithGrid()
#who prints out everyone who's present at each of those locations.
for i in range(len(d.points)):
    #print(r.whosHere(d.points[i].location, 'DendritePoint'))
    print(r.grid[d.points[i].location.key])