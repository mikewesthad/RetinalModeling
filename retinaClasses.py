"""
Retinal Class Definitions

Jason Farina
2013/04/04
"""
import random
import math
import collections

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
        if class_type:        
            return self.grid[key][index]
        else:
            return self.grid[key]

#instantiates a retinal grid 100x100um with 1um spacing
r = RetinalGrid(100,100,1)


neurotransmitters = ['gly', 'glu', 'gab', 'ach']

class Outputs(object):
    """This class specifies methods for handling the neurotransmitters that are
    output from a particular object in retinal space."""
    
    outputs = {}   
    
    def __init__(self, neurotransmitters):
        self.nt_types = neurotransmitters
        for nt in neurotransmitters:
            self.outputs[nt] = [False, 0]
         
    def isOutput(self, nt_type):
        assert nt_type in self.nt_types, "Invalid neurotransmitter."
        return self.outputs[nt_type][0]

    def getAmount(self, nt_type):
        assert nt_type in self.nt_types, "Invalid neurotransmitter."
        return self.outputs[nt_type][1]
        
    def setAmount(self, nt_type, amount):
        self.outputs[nt_type][1] = amount

"""
# dictionary = {n.t.:  [isOutput, amount]}
outputs = {'gly':  [False, 0],
           'glu':  [False, 0],
           'gab':  [False, 0],
           'ach':  [False, 0]} 
nt_types = [k for k in outputs.keys()]
"""

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
        
    def distFrom(self, location):
        x1 = location.x
        y1 = location.y
        x2 = self.x
        y2 = self.y
        return math.sqrt( (x2-x1)**2 + (y2-y1)**2 )
        

class Neuron(object):
    """A Neuron is a soma_location in conjunction with a host of individual
    dendrites or a more general dendritic field (and possibly axonal) field.
    """
    
    def __init__(self, location):
        """Creates a new neuron at the location given."""
        self.soma_location = location
        
    

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
        def isAppropriateInput(point):
            return True
                        
        for point in self.points:
            present = self.grid.whosHere(point.location, 'DendritePoint')
            present = filter(lambda x:  x is not point, present)
            connections = filter(isAppropriateInput, present)
            new_connections = filter(lambda x:  x not in point.inputs, connections)            
            point.inputs.extend(new_connections)

    def calculateHeadingFromSoma(self, pos):
        """Given a LocationID, calculates a heading from its neuron's soma to
        that location.  Returns an angle.
        """
        return pos.distFrom(self.neuron.soma_location)
        
    
        


class DendritePoint(object):
    """A DendritePoint is a dendrite location on the retinal grid."""

    def __init__(self, dendrite, location):
        """Create a point along a dendrite.
        """
        self.dendrite = dendrite
        self.compartment = None
        self.location = location
        self.is_output_zone = True
        self.outputs = Outputs(neurotransmitters)
        self.inputs = []
        self.nt_accepted = neurotransmitters


class Compartment(object):
    """A collection of points along a dendrite.  The compartment is the
    fundamental unit of analysis in the model.
    """ 
    grid = r    #Hardcoding this instance of the retinal grid as being associated
                #with all dendrites

    def __init__(self, neighbor):
        """Create a new compartment."""
        self.neighbor_proximal = neighbor
        self.neighbor_distal = None        
        self.points = []   
        self.inputs = []            #other compartments
                                    #will be recast as dict = {elem: freq}
        self.outputs = Outputs(neurotransmitters)
        self.center = None
        self.nt_accepted = []

    def registerWithGrid(self):
        """Lets all of the corresponding retinal grid points know that he
        is here.
        """
        for point in self.points:
            self.grid.registerLocation(point.location, self)

    def getInputs(self):
        """Updates self.inputs to contain all other compartments which input
        to this one.
        
        QUESTION:  This list may have duplicates.  Do we want to prevent 
        duplicates and instead note how many times each appears?
        
        ANSWER:  Yes, that's what Mike wants.  Implemented below.        
        
        Possible implementation sketch:
        import collections
        inputs = collections.Counter(inputs)    #dictionary with freq value
        inputs.keys()                           #items in list
        inputs.values()                         #frequencies
        
        """
        for point in self.points:                       #my DendritePoints
            for input in point.inputs:                  #their inputs (other DendritePoints)
                self.inputs.append(input.compartment)   #their associated compartment
        self.inputs = collections.Counter(self.inputs)  #dict = {elem: freq}
        #need to update self.nt_accepted based on constituent DendritePoints

    def updateActivity(self):
        """Based on the current inputs, this method updates the internal
        potential and thus the levels of neurotransmitters to be output.
        """
        def nt_in_2_potential(totals_in):
            amount = sum(totals_in.values())            
            potential = amount
            return potential
            
        def potential_2_nt_out(nt_type, potential):
            amount = potential
            return amount
        
        totals_in = {}
        #for each neurotransmitter accepted
        for nt in self.nt_accepted:  
            totals_in[nt] = 0.0
            #for each input
            for input in self.inputs:
                #retrieve input amount
                totals_in[nt] += input.getOutput(nt)
            #Now calculate new potential
            potential = nt_in_2_potential(totals_in)
        #Then calculate each new output amout
        #for each nt output
        for nt in self.outputs.keys():            
            new_amount = potential_2_nt_out(nt, potential)
            self.outputs.setAmount(nt, new_amount)
        #update outputs
            
        

    def getOutput(self, nt_type):
        """Given a type of neurotransmitter, return the amount (per retinal 
        grid location) released from this compartment.
        """  
        if self.outputs.isOutput(nt_type):            
                return self.outputs.amount[nt_type]
        
            
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
  


###############
# Test Script #
###############
          
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
c = Compartment(None)
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
    
#dendrite establishes inputs
d.estInputs()
#and should come up empty...
for i in range(len(d.points)):
    print input

#instantiate another dendrite, d1, that crosses the first dendrite, d
locations = [LocationID(10,12), LocationID(11,11), LocationID(12,10)]
d1 = Dendrite("None", locations)
d1.initPoints()
d1.registerWithGrid()

#have dendrite d establish inputs again
d.estInputs()
#and this time should have one
for point in d.points:
    print point.inputs
 
#Instantiate a Neuron n   
n = Neuron(LocationID(10,10))
#assign to dendrite d
d.neuron = n
#calculate distance from soma for all dendrite poionts
for point in d.points:
    print'Soma Distance =', d.calculateHeadingFromSoma(point.location)