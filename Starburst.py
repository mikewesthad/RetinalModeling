from Constants import *

class Starburst(object):
    
    def __init__(self, layer, morphology, location, starburst_type="On", input_delay=1, layer_depth=0):
    
        # General neuron variables
        self.layer              = layer
        self.morphology         = morphology
        self.location           = location
        self.input_delay        = input_delay
        self.layer_depth        = layer_depth
        self.retina             = layer.retina
        self.history_size       = layer.history_size
        self.starburst_type     = starburst_type
        
        self.compartments           = self.morphology.compartments
        self.number_compartments    = len(self.compartments)
        self.input_strength         = layer.input_strength
        self.decay_rate             = layer.decay_rate
        self.diffusion_weights      = self.morphology.diffusion_weights
        
        self.activities = []
        self.neurotransmitter_ouputs = []
        for i in range(self.history_size):
            blank_activity = np.zeros((1, self.number_compartments))
            self.activities.append(blank_activity)
            
            self.neurotransmitter_ouputs.append([])
            for c in range(self.number_compartments):
                self.neurotransmitter_ouputs[-1].append({})
        
    def loadPast(self, activity):
        self.activities[0] = activity
        
    def drawInputs(self, surface, selected_compartment, scale=1.0):
        for (info, weight) in self.compartment_inputs[selected_compartment]:
            neuron, compartment, compartment_index = info
            compartment.draw(surface, neuron, color=(0,0,0), scale=scale)
        
        self.morphology.location = self.location
        self.compartments[selected_compartment].color = (255,255,255)
        self.compartments[selected_compartment].draw(surface, scale=scale)
        self.morphology.location = Vector2D(0.0,0.0)
    
    def draw(self, surface, color=None, scale=1.0, draw_segments=False, draw_points=False, 
             draw_compartments=False):
        self.morphology.draw(surface, color=color, scale=scale, new_location=self.location,
                             draw_points=draw_points, draw_segments=draw_segments,
                             draw_compartments=draw_compartments)
    
    def drawActivity(self, surface, colormap, activity_bounds, scale=1.0):
        activities = self.activities[0]
        self.morphology.drawActivity(surface, colormap, activity_bounds, 
                                     activities, scale=scale, 
                                     new_location=self.location)
    
    def establishInputs(self):
        self.compartment_inputs = []        
        for compartment in self.compartments:
            self.compartment_inputs.append([])
            for location in compartment.gridded_locations:
                location = location + self.location
                for neuron, compartment, compartment_index in self.retina.getOverlappingNeurons(self, location):
                    if self.isAppropriateInput(neuron, compartment):
                        booleans = [(neuron, compartment, compartment_index) == i[0] for i in self.compartment_inputs[-1]]
                        if any(booleans):
                            index = booleans.index(True)
                            self.compartment_inputs[-1][index][1] += 1
                        else:
                            self.compartment_inputs[-1].append([(neuron, compartment, compartment_index), 1.0])
                        
    def isAppropriateInput(self, neuron, compartment):
        if isinstance(neuron, Bipolar) and neuron.layer.bipolar_type == self.starburst_type:
            return True
        return False
            
    def registerWithRetina(self):
        for compartment_index in range(self.number_compartments):
            compartment = self.compartments[compartment_index]
            compartment.registerWithRetina(self, compartment_index)
    

    def update(self):
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
        diffusion_activity = np.sum(differences, 0) + self_activities
        
        # np.sum removes a dimension, so let's restore it.
        diffusion_activity.shape = (1, self.number_compartments) 
        
        
        input_activity = np.zeros((1, self.number_compartments))    
        for compartment_index in range(self.number_compartments):
            compartment = self.compartments[compartment_index]
            inputs      = self.compartment_inputs[compartment_index]
            
            input_potential = 0.0
            nt_inputs   = {}
            nt_maxes    = {}
            for [other_neuron, other_compartment, other_index], points_overlap in inputs: 
                other_nt_outputs = other_neuron.neurotransmitter_ouputs[self.input_delay][other_index]
                for nt, nt_amount in other_nt_outputs.iteritems():
                    # This might be hacked and may need to be re-evaluated
                    # Normalzing by the max amount of input nt I could have recieved
                    # Only works when nt amounts scale between 0 and 1
                    if nt in nt_inputs:
                        nt_inputs[nt]   += nt_amount * points_overlap
                        nt_maxes[nt]    += other_compartment.neurotransmitters_output_weights[nt] * points_overlap
                    else:
                        nt_inputs[nt]   = nt_amount * points_overlap
                        nt_maxes[nt]    = other_compartment.neurotransmitters_output_weights[nt] * points_overlap
            for nt in nt_inputs:
                nt_inputs[nt] /= nt_maxes[nt]
            input_potential = compartment.calculatePotentialFromNeurotransmitterInputs(self, nt_inputs)
             
            input_activity[0, compartment_index] = input_potential
            
            
        
        # Calcualte the new activity
        d = self.decay_rate
        i = self.input_strength
        new_activity = i * input_activity + (1.0-i) * (1.0-d) * diffusion_activity
        
        
#        np.set_printoptions(precision=3, suppress=True, linewidth=300)
#        print diffusion_activity
#        print input_activity
#        print new_activity
            
        # Add the most recent activity to the front of the list
        self.activities.insert(0, new_activity)
        return new_activity