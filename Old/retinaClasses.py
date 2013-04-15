"""
Retinal Class Definitions

Jason Farina
2013/04/04
"""
import random
import collections
import numpy

test = False
###############
## Constants ##
###############

NEUROTRANSMITTERS = set(['gly', 'glu', 'gab', 'ach'])


#####################
## Data Structures ##
#####################

class Outputs(object):
    """This class specifies methods for handling the neurotransmitters that are
    output from a particular object in retinal space."""
    
    outputs = {}   
    
    def __init__(self):
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


#############
## Classes ##
#############

class RetinalGrid(object):
    """The RetinalGrid keeps track of all neuron classes that are located at 
    each of its locations.
    """
    grid = {}    
    types_accepted = ['Neuron', 'Dendrite', 'DendritePoint', 'Compartment']    
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
    

class NeuronLayer(object):
    """A NeuronLayer is a two-dimensional sheet of neurons of a particular 
    type.
    """  
    def __init__(self, grid):
        self.grid = grid
        self.neurons = []
        
    def placeNeurons(self):
        pass
    
    def initPoints(self):
        for neuron in self.neurons:
            neuron.initPoints()
    
    def estInputs(self):
        for neuron in self.neurons:
            neuron.estInputs()

    def updateActivity(self):
        for neuron in self.neurons:
            neuron.updateActivity()

      

class Neuron(object):
    """A Neuron is a soma_location in conjunction with a host of individual
    dendrites or a more general dendritic field (and possibly axonal) field.
    """

    nt_accepted = NEUROTRANSMITTERS #This should probably be [], or empty set
    nt_out = NEUROTRANSMITTERS      #This should probably be [], or empty set
    
    def __init__(self, location, grid):
        """Creates a new neuron at the location given."""
        self.soma_location = location
        self.grid = grid
        self.dendrites = []
        self.compartments = []        
        
    def grow(self):
        pass
        
    def initPoints(self):
        self.grid.registerLocation(self.soma_location, self)
        for dendrite in self.dendrites:
            dendrite.initPoints()
        
    def estInputs(self):
        """Establishes inputs to all dendrites of the neuron.
        """
        for dendrite in self.dendrites:
            dendrite.estInputs()   
            
    def compartmentalize(self):
        pass
    
    def updateActivity(self):
        #needs to talk to compartments
        pass
    



class DendriteSegment(object):
    """A Dendrite is a set of sequential locations on the retinal grid that
    does not bifurcate.  In essence it is a section of a full, bifurcating
    dendrite.  The order is from most proximal to most distal location.
    """
            
    def __init__(self, neuron, locations):
        """Creates a new dendrite."""
        self.neuron = neuron    #The neuron object to which this dendrite belongs
        self.locations = locations
        self.grid = neuron.grid
        self.points = []
        self.parent = None      #The dendrite from whose end this one starts
        self.children = []      #The dendrites that branch from the end of this one
        
    def grow(self):
        pass
        
    def initPoints(self):
        """Instantiates a DendritePoint object at each location in self.locations.
        """
        for loc in self.locations:
            p = DendritePoint(self, loc)
            self.points.append(p)  
        for child in self.children:
            child.initPoints()
                             
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
        for child in self.children():
            child.estInputs()
            


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
            
    def estNeurotransmittersIn(self):
        for point in self.points:         
            self.nt_accepted = self.nt_accepted.union(point.nt_accepted)
            
            
    def estNeurotransmittersOut(self):
        for point in self.points:
            for nt in NEUROTRANSMITTERS:
                if point.outputs.isOutput(nt):
                    self.outputs.setIsOutput(nt, True)

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
        for point in self.points:                           #my DendritePoints
            for input_point in point.inputs:                #their inputs (other DendritePoints)
                self.inputs.append(input_point.compartment) #their associated compartment
        self.inputs = collections.Counter(self.inputs)      #dict = {elem: freq}
        

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
            print 'Right before Counter forloop.'
            for compartment in self.inputs.keys():
                if compartment:                
                    w = self.inputs[compartment]                
                    print 'compartment:', compartment
                    print 'freq/weight:', w
                    #retrieve input amount
                    output = compartment.getOutput(nt)
                    print 'output:',nt,'is', output                    
                    if output:
                        print 'Updating totals_in.'
                        totals_in[nt] += w*compartment.getOutput(nt)
                        print 'totals_in:', totals_in[nt]
            #scale total input to input/point
            totals_in[nt] = totals_in[nt]/len(self.points)
            #Now calculate new potential per point
            potential = nt_in_2_potential(totals_in)
        #Then calculate each new output amout
        #for each nt output
        for nt in NEUROTRANSMITTERS:
            if self.outputs.isOutput(nt):            
                new_amount = potential_2_nt_out(nt, potential)
                self.outputs.setAmount(nt, new_amount)
        #update outputs
        

    def getOutput(self, nt_type):
        """Given a type of neurotransmitter, return the amount (per retinal 
        grid location) released from this compartment.
        """  
        if self.outputs.isOutput(nt_type):            
            return self.outputs.getAmount(nt_type)
        else:
            return None
        
            
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
  


#################
## Test Script ##
#################
          
if test:        
    #instantiates a retinal grid 100x100um with 1um spacing
    r = RetinalGrid(100,100,1)          
              
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
    
    #Instantiate a Neuron n   
    n = Neuron(Location(10,10), r)
    
    #instantiate a Dendrite of n with the locations contained in 'dendrite'
    for d in dendrite:
        print d.x, d.y
    d = DendriteSegment(n, dendrite)
    
    #who initializes his points
    d.initPoints()   
    
    for point in d.points:
        for nt in   NEUROTRANSMITTERS:
            print point.outputs.isOutput(nt)
    #associates them with a compartment
    c = Compartment(None, r)
    for point in d.points:
        c.addDendritePoint(point)
        
    c.calculateCenter()
    #registers them with the Retinal Grid
    d.registerWithGrid()
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
    n1 = Neuron(locations[0], r)
    d1 = DendriteSegment(n1, locations)
    d1.initPoints()
    d1.registerWithGrid()
    c1 = Compartment(None, r)
    for point in d1.points:
        point.outputs.setIsOutput('glu', True)
        c1.addDendritePoint(point)
    c1.estNeurotransmittersIn()
    c1.estNeurotransmittersOut()
    
    #have dendrite d establish inputs again
    d.estInputs()
    #and this time should have one in the middle location.
    for point in d.points:
        print point.inputs
     
    
    #calculate distance from soma for all dendrite poionts
    for point in d.points:
        print'Soma Distance =', point.heading_from_soma
    
    #have c (the compartment that is coextensive with dendrite d) get Inputs.
    #There should be one, the compartment coextensive with d1.
    c.getInputs()
    print "c.inputs: ", c.inputs
    
    c.estNeurotransmittersIn()
    c.estNeurotransmittersOut()
    
    #update and output activity.  Should be None b/c inputs' outputs are all None
    c.updateActivity()
    for nt in NEUROTRANSMITTERS:
        print "c.getOutput for", nt, "is", c.getOutput(nt)
    
    #update the output amount of the compartment that inputs to this compartment.
    c1.outputs.setAmount('glu', 10)
    print "c1's output is:", c1.outputs.getAmount('glu')
    
    
    #update and output activity.  Should be the average of the activities.
    c.updateActivity()
    for nt in NEUROTRANSMITTERS:
        print "c.getOutput for", nt, "is", c.getOutput(nt)   
