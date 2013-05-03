# Directionally Selective Ganglion Cells
# jfarina
# 5/2/2013

from Constants import * 

class DSG(object):
    
    def __init__(self, layer, ON_morphology, OFF_morphology, location, 
                 preferred_dir=UP, history_size=1, input_delay=1, layer_depth=0):
    
        # General neuron variables
        self.layer              = layer
        self.ON_morphology      = ON_morphology
        self.OFF_morphology     = OFF_morphology
        self.location           = location
        self.input_delay        = input_delay
        self.layer_depth        = layer_depth
        self.retina             = ON_morphology.retina
        self.history_size       = history_size
        self.preferred_dir      = preferred_dir
        self.null_dir           = preferred_dir + 180
        self.connection_heading_delta = 90
        
        self.ON_arbor = Starburst(self.layer,
                                  self.ON_morphology,
                                  self.soma_location,
                                  ON,
                                  self.input_delay,
                                  self.layer_depth)
        self.OFF_arbor = Starburst(self.layer,
                                  self.OFF_morphology,
                                  self.soma_location,
                                  OFF,
                                  self.input_delay,
                                  self.layer_depth)
                                  
        def establishInputs(self, mode=DIFFUSION):
#            if mode==RADIUS:
#                radius = self.ON_morphology.average_wire_length
#                x_loc = int(self.ON_morphology.location.x)
#                y_loc = int(self.ON_morphology.location.y)
#                x_locations_box = range(x_loc - radius , x_loc + radius + 1)
#                y_locations_box = range(y_loc - radius , y_loc + radius + 1)
#                for x in x_locations_box:
#                    for y in y_locations_box:
#                        location = Vector2D(x, y)
#                        
#                        for neuron, compartment in self.retina.getOverlappingNeurons(self, location):
#                            if self.isAppropriateInput(neuron, compartment):

            
            if mode==DIFFUSION:
                self.ON_arbor.establishInputs(self.isAppropriateInputON)  
                self.OFF_arbor.establishInputs(self.isAppropriateInputOFF)
                
        def isAppropriateInputON(self, neuron, compartment):
            isCorrectNeuron = isinstance(neuron, Starburst)
            isCorrectType = neuron.layer.on_off_type==self.ON_arbor.on_off_type            
            def isAppropriateHeading(self):
                heading_max = self.null_dir + self.connection_heading_delta
                heading_min = self.null_dir - self.connection_heading_delta            
                return compartment.heading < heading_max and compartment.heading > heading_min
            return isCorrectNeuron and isCorrectType and isAppropriateHeading()     
                                  
        def isAppropriateInputOFF(self, neuron, compartment):
            isCorrectNeuron = isinstance(neuron, Starburst)
            isCorrectType = neuron.layer.on_off_type==self.OFF_arbor.on_off_type            
            def isAppropriateHeading(self):
                heading_max = self.null_dir + self.connection_heading_delta
                heading_min = self.null_dir - self.connection_heading_delta            
                return compartment.heading < heading_max and compartment.heading > heading_min
            return isCorrectNeuron and isCorrectType and isAppropriateHeading()          

            
            
            
        
    
        
        