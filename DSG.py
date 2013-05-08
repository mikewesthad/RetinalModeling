# Directionally Selective Ganglion Cells
# jfarina
# 5/2/2013

from Constants import * 

class DSG(object):
    
    def __init__(self, layer, ON_morphology, OFF_morphology, location, 
                 preferred_dir=None, history_size=1, input_delay=1, layer_depth=0):
    
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
        self.null_dir           = (preferred_dir + 180) % 360
        self.connection_heading_delta = 180
        
        self.ON_arbor = Starburst(self.layer,
                                  self.ON_morphology,
                                  self.location,
                                  ON,
                                  self.input_delay,
                                  self.layer_depth)
        self.OFF_arbor = Starburst(self.layer,
                                  self.OFF_morphology,
                                  self.location,
                                  OFF,
                                  self.input_delay,
                                  self.layer_depth)
                                  
    def establishInputs(self, mode=DIFFUSION):
        if mode==DIFFUSION:
            self.ON_arbor.establishInputs(self.isAppropriateInputON)  
            self.OFF_arbor.establishInputs(self.isAppropriateInputOFF)
#        if mode==RADIUS:
#            radius = self.ON_morphology.average_wire_length
#            x_loc = int(self.ON_morphology.location.x)
#            y_loc = int(self.ON_morphology.location.y)
#            x_locations_box = range(x_loc - radius , x_loc + radius + 1)
#            y_locations_box = range(y_loc - radius , y_loc + radius + 1)
#            for x in x_locations_box:
#                for y in y_locations_box:
#                    location = Vector2D(x, y)
#                    
#                    for neuron, compartment in self.retina.getOverlappingNeurons(self, location):
#                        if self.isAppropriateInput(neuron, compartment):

                
    def isAppropriateInputON(self, neuron, compartment):
        is_correct_neuron = isinstance(neuron, Starburst)
        is_correct_on_off = neuron.layer.on_off_type==self.ON_arbor.on_off_type            
        def isAppropriateHeading():
            heading_max = (self.null_dir + self.connection_heading_delta - 1) % 360
            heading_min = (self.null_dir - self.connection_heading_delta) % 360
            print "heading_min =", heading_min, ":", "heading_max =", heading_max
            print "compartment.heading =" , compartment.heading
            if heading_max >= heading_min:            
                return compartment.heading <= heading_max and compartment.heading >= heading_min
            else:            
                return compartment.heading < heading_max or compartment.heading > heading_min
        is_correct_heading = isAppropriateHeading()
        is_appropriate = is_correct_neuron and is_correct_on_off and is_correct_heading     
        print "Inside isAppropriateInputON", is_correct_neuron, is_correct_on_off, is_correct_heading      
        if is_appropriate:
            print is_appropriate   
        return is_appropriate
                   
    def isAppropriateInputOFF(self, neuron, compartment):
        is_correct_neuron = isinstance(neuron, Starburst)
        is_correct_on_off = neuron.layer.on_off_type==self.OFF_arbor.on_off_type            
        def isAppropriateHeading():
            heading_max = (self.null_dir + self.connection_heading_delta - 1) % 360
            heading_min = (self.null_dir - self.connection_heading_delta) % 360
            if heading_max >= heading_min:            
                return compartment.heading <= heading_max and compartment.heading >= heading_min
            else:            
                return compartment.heading < heading_max or compartment.heading > heading_min
        is_correct_heading = isAppropriateHeading()
        is_appropriate = is_correct_neuron and is_correct_on_off and is_correct_heading     
        print "Inside isAppropriateInputOFF", is_correct_neuron, is_correct_on_off, is_correct_heading      
        if is_appropriate:
            print is_appropriate   
        return is_appropriate 
        
    def draw(self, surface, scale=1.0, draw_segments=False, draw_points=False, 
             draw_compartments=False):
        self.ON_arbor.draw(surface, scale, draw_segments, draw_points, draw_compartments)
        self.OFF_arbor.draw(surface, scale, draw_segments, draw_points, draw_compartments)
            
            
            
        
    
        
        