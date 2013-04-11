"""
Retinal Class Definitions

Jason Farina
2013/04/04
"""
import random
import collections
import numpy

class RetinalGrid(object):
    """The RetinalGrid keeps track of all neuron classes that are located at 
    each of its locations.
    """
    grid = {}    
    types_accepted = ['Neuron', 'Dendrite', 'DendritePoint', 'Compartment']    
#    type_index = {'Neuron':         0, 
#                  'Dendrite':       1, 
#                  'DendritePoint':  2, 
#                  'Compartment':    3} 
    width = None    #retinal grid units
    height = None   #retinal grid units  
    spacing = None  #retinal grid units   
    
    def __init__(self, width, height, spacing=1):
        """Creates retinal_grid dictionary by taking in the grid width, grid 
        height, and grid spacing in micrometers.
        """
        self.width = width/spacing   #convert from um to rgu's (retinal grid units)
        self.height = height/spacing #convert from um to rgu's
        self.spacing            
            
        for w in range(width+1):
            for h in range(height+1):
                self.grid[(w,h)] = {}
                for type_tag in self.types_accepted:
                    self.grid[(w,h)][type_tag] = []
                
    @property
    def widthWorld(self):
        return self.width*self.spacing
        
    @property
    def heightWorld(self):
        return self.height*self.spacing
    
    def registerLocation(self, location, member):
        """Registers 'member' object with the grid at the 'location'.
        """
        type_tag = type(member).__name__        
        assert type_tag in self.types_accepted, '{0} not accepted.'.format(member)
        if type_tag in self.grid[location.ID]:
            self.grid[location.ID][type_tag].append(member)
        else:
            self.grid[location.ID][type_tag] = [].append(member)
        
       
        
    def whosHere(self, location, class_type):
        """Returns a list of all of the members of a particular class who are
        present at the specified retinal grid location.
        
        types_accepted = ['Neuron', 'Dendrite', 'DendritePoint', 'Compartment']
        """
        return self.grid[location.ID][class_type]


#instantiates a retinal grid 100x100um with 1um spacing
r = RetinalGrid(100,100,1)


NEUROTRANSMITTERS = ['gly', 'glu', 'gab', 'ach']

class Outputs(object):
    """This class specifies methods for handling the neurotransmitters that are
    output from a particular object in retinal space."""
    
    outputs = {}   
    
    def __init__(self, NEUROTRANSMITTERS):
        self.nt_types = NEUROTRANSMITTERS
        for nt in NEUROTRANSMITTERS:
            self.outputs[nt] = [False, 0]
         
    def isOutput(self, nt_type):
        assert nt_type in self.nt_types, "Invalid neurotransmitter."
        return self.outputs[nt_type][0]

    def setIsOutput(self, nt_type, is_output):
        self.outputs[nt_type][0] = is_output

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

class Location(object):
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
    def ID(self):
        return self.x, self.y
        
    def distFrom(self, location):
        x1 = location.x
        y1 = location.y
        x2 = self.x
        y2 = self.y
        return ((x2-x1)**2 + (y2-y1)**2)**0.5
        
        

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
        def isAppropriateInput(point): #this should not live here.
            return True
                                            
        for point in self.points:
            present = self.grid.whosHere(point.location, 'DendritePoint')
            if present != None:            
                present = filter(lambda x:  x is not point, present) #remove "me"
                connections = filter(isAppropriateInput, present)
                new_connections = filter(lambda x:  x not in point.inputs, 
                                         connections)            
                point.inputs.extend(new_connections)
    


class DendritePoint(object):
    """A DendritePoint is a dendrite location on the retinal grid."""

    def __init__(self, dendrite, location):
        """Create a point along a dendrite.
        """
        self.dendrite = dendrite
        self.compartment = None
        self.location = location
        self.is_output_zone = True
        self.outputs = Outputs(NEUROTRANSMITTERS)
        self.inputs = []
        self.nt_accepted = NEUROTRANSMITTERS
        self.heading = None
        
    @property    
    def heading_from_soma(self):
        """Returns (or calculates if not already calculated) the heading from soma to DendritePoint.  Returns an angle in radians [-pi, pi].
        """
        if self.heading:
            return self.heading
        else:
            delta_x = self.location.x - self.dendrite.neuron.soma_location.x
            delta_y = self.location.y - self.dendrite.neuron.soma_location.y
            self.heading = numpy.arctan2(delta_y, delta_x)
            return self.heading
     
    @property       
    def headingWorld(self):
        """Retinal Grid dimensions/distances are labeled positive to the right
        and positive down (a reflection across the x-axis from normal
        convention).  This method provides access to the "real-world" heading.
        """        
        return -1*self.heading
            
class Compartment(object):
    """A collection of points along a dendrite.  The compartment is the
    fundamental unit of analysis in the model.
    """ 
    grid = r    #Hardcoding this instance of the retinal grid as being associated
                #with all dendrites

    def __init__(self, neighbor):
        """Create a new compartment."""
        self.neighbor_proximal = neighbor
        self.neighbor_distal = []        
        self.points = []   
        self.inputs = []            #other compartments
                                    #will be recast as dict = {elem: freq}
        self.outputs = Outputs(NEUROTRANSMITTERS)
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
        for point in self.points:                             #my DendritePoints
            for input_point in point.inputs:                  #their inputs (other DendritePoints)
                self.inputs.append(input_point.compartment)   #their associated compartment
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
            for compartment, w in self.inputs:  
                #retrieve input amount
                totals_in[nt] += w*compartment.getOutput(nt)
            #scale total input to input/point
            totals_in[nt] = totals_in[nt]/len(self.points)
            #Now calculate new potential per point
            potential = nt_in_2_potential(totals_in)
        #Then calculate each new output amout
        #for each nt output
        for nt in self.outputs.key():            
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
        self.center = Location(centroid_x, centroid_y)
  


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
        pos = Location(x,y)
        locations.append(pos)
    return locations
#assignes them to a dendrite
dendrite = generateLocations(5)
#but don't use them
#overwrite random locations with hardcoded ones
locations = []
locations = [Location(10,10), Location(11,11), Location(12,12)]
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
    print(r.grid[d.points[i].location.ID])
    
#dendrite establishes inputs
d.estInputs()
#and should come up empty...
for i in range(len(d.points)):
    print d.points[i].inputs

#instantiate another dendrite, d1, that crosses the first dendrite, d
locations = [Location(10,12), Location(11,11), Location(12,10)]
d1 = Dendrite("None", locations)
d1.initPoints()
d1.registerWithGrid()

#have dendrite d establish inputs again
d.estInputs()
#and this time should have one
for point in d.points:
    print point.inputs
 
#Instantiate a Neuron n   
n = Neuron(Location(10,10))
#assign to dendrite d
d.neuron = n
#calculate distance from soma for all dendrite poionts
for point in d.points:
    print'Soma Distance =', point.heading_from_soma