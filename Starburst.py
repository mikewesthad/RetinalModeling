from Constants import *

class Starburst(object):
    
    def __init__(self, layer, morphology, location, starburst_type="On", input_delay=1, layer_depth=0):
    
        # General neuron variables
        self.layer              = layer
        self.morphology         = morphology
        self.location           = location
        self.input_delay        = input_delay
        self.layer_depth        = layer_depth
        self.retina             = morphology.retina
        self.history_size       = morphology.history_size
        self.starburst_type     = starburst_type
        
        self.number_compartments    = len(self.morphology.compartments)
        self.input_strength         = self.morphology.input_strength
        self.decay_rate             = self.morphology.decay_rate
        self.diffusion_weights      = self.morphology.diffusion_weights
        self.diffusion_strength     = self.morphology.diffusion_strength
        self.initializeActivties()
        
        self.compartment_inputs = []
        self.initializeInputs()
        
    
    def drawInputs(self, surface, selected_compartment, scale=1.0):
        for (info, weight) in self.compartment_inputs[selected_compartment]:
            neuron, compartment = info
            compartment.draw(surface, neuron, color=(0,0,0), scale=scale)
        
        self.morphology.location = self.location
        self.morphology.compartments[selected_compartment].color = (255,255,255)
        self.morphology.compartments[selected_compartment].draw(surface, scale=scale)
        self.morphology.location = Vector2D(0.0,0.0)
    
    def initializeInputs(self):
        self.compartment_inputs = []        
        for compartment in self.morphology.compartments:
            self.compartment_inputs.append([])
            for location in compartment.gridded_locations:
                location = location + self.location
                for neuron, compartment in self.retina.getOverlappingNeurons(self, location):
                    if self.isAppropriateInput(neuron, compartment):
                        booleans = [(neuron, compartment) == i[0] for i in self.compartment_inputs[-1]]
                        if any(booleans):
                            index = booleans.index(True)
                            self.compartment_inputs[-1][index][1] += 1
                        else:
                            self.compartment_inputs[-1].append([(neuron, compartment), 1.0])
                        
    def isAppropriateInput(self, neuron, compartment):
        if isinstance(neuron, Bipolar) and neuron.layer.bipolar_type == self.starburst_type:
            return True
        return False
            
    def registerWithRetina(self):
        for compartment in self.morphology.compartments:
            compartment.registerWithRetina(self, self.layer_depth)
    
    def draw(self, surface, scale=1.0, draw_segments=False, draw_points=False, 
             draw_compartments=False):
        self.morphology.draw(surface, scale=scale, new_location=self.location,
                             draw_points=draw_points, draw_segments=draw_segments,
                             draw_compartments=draw_compartments)

    def initializeActivties(self):
        self.activities = []
        for i in range(self.history_size):
            blank_activity = np.zeros((1, self.number_compartments))
            self.activities.append(blank_activity)

    def updateActivity(self):
        # Delete the oldest activity and get the current activity
        del self.activities[-1]
        last_activity = self.activities[0]
        
        # Create the activity difference matrix where:
        #   Dij = compartment i activity - compartment j activity
        #   This matrix describes the concentration gradient
        differences = last_activity.T - last_activity
        
        # Weight the difference matrix according to the distance between compartments
        # This amounts to multiplying each compartment's differences with a 
        # gaussian defined by distance between compartments.  The gaussian has 
        # been normalized so that its integral is 1.0.  This ensures that each 
        # compartment can only send as much concentration as it currently has.
        differences = differences * self.diffusion_weights
        
        # Zero out any elements in the difference matrix that are less than zero.
        # The upper triangle of the matrix is equal to the negative of the lower
        # triangle, so we only need to worry about the positive half of the matrix.
        negative_difference_indicies = differences < 0
        differences[negative_difference_indicies] = 0
        
        # Find the amount of concentration that each compartment has left after
        # this step of diffusion
        self_activities = last_activity - np.sum(differences, 1)
        
        # Add the up the concentration passed to each compartment and the amount 
        # of charge left after diffusion 
        diffusionActivity = np.sum(differences, 0) + self_activities
        
        # np.sum removes a dimension, so let's restore it.
        diffusionActivity.shape = (1, self.number_compartments) 
        
#        # Calculate the diffusion
        d = self.decay_rate
        diffusionActivity = (1.0-d) * diffusionActivity
#        
#        # Get the bipolar activity
#        
#        # Find the new activity
        i = self.input_strength
        new_activity = (1.0-i) * diffusionActivity #+ i * bipolar_inputs
        
        # Add the most recent activity to the front of the list
        self.activities.insert(0, new_activity)
        
        return new_activity