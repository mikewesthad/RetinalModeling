import random
import math as m
from Constants import *

class Bipolar:
    
    def __init__(self, layer, location, rectified=True):
        self.location = location
        
        self.layer  = layer
        self.retina = layer.retina
        self.rectified = rectified    
        
        self.history_size   = layer.history_size           
        
        self.activities = []
        self.neurotransmitter_ouputs = []
        for step in range(self.history_size):
            self.activities.append([0.0])
            self.neurotransmitter_ouputs.append([{}])
            
        self.inputs = []
    
    def loadPast(self, activity):
        self.activities[0] = activity
    
    def drawActivity(self, surface, radius, colormap, activity_bounds, scale=1.0):
        min_activity, max_activity = activity_bounds  
        activity = self.activities[0]
        color = getColorFromActivity(colormap, activity) 
        location = (self.location * scale).toIntTuple()
        pygame.draw.circle(surface, color, location, radius)      
        
    def draw(self, surface, radius, color, scale=1.0):            
        location = (self.location * scale).toIntTuple()        
        radius = int(radius * scale)
        pygame.draw.circle(surface, color, location, radius)
        
    def update(self, cone_activities, horizontal_activities):
        # Delete the oldest history
        del self.activities[-1]
        del self.neurotransmitter_ouputs[-1]
        
        # Update the internal activity
        new_activity = 0
        for triad_ID, triad_weight in self.inputs:
            triad_number            = self.layer.triad_locations[triad_ID]
            cone_activity           = cone_activities[0, triad_number]
            horizontal_activity     = horizontal_activities[0, triad_number]
            
            if self.layer.bipolar_type == "On":
                if self.layer.recieves_input_from_horizontal:
                    triad_activity = -(cone_activity - horizontal_activity)/2.0  
                else:
                    triad_activity = -cone_activity 
            else: 
                if self.layer.recieves_input_from_horizontal:
                    triad_activity = (cone_activity - horizontal_activity)/2.0
                else: 
                    triad_activity = cone_activity
            
            new_activity += triad_weight * triad_activity
            
        if self.rectified: 
#            new_activity = 1.0 / (1.0 + m.exp(1.54 - 7.0*new_activity))
            if new_activity < 0.0: new_activity = 0.0
        
        # Update the neurotransmitter amounts that are output
        new_neurotransmitter_outputs = self.compartments[0].calculateNeurotransmitterOutputsFromPotential(self, new_activity)
        
        # Store the new activity and nt output
        self.activities.insert(0, [new_activity])
        self.neurotransmitter_ouputs.insert(0, [new_neurotransmitter_outputs])
        
        return new_activity
        
    def compartmentalize(self, compartment):
        self.compartments = [compartment]
        compartment_index = 0
        compartment.registerWithRetina(self, compartment_index)
        
    def establishInputs(self):
        radius = self.layer.input_field_radius_gridded
        
        weight_sum = 0.0
        connected_triads = []
        for triad_ID in self.layer.triad_locations:                
            triad_x, triad_y = map(float, triad_ID.split('.'))
            triad_position = Vector2D(triad_x, triad_y)
            if self.location.distanceTo(triad_position) < radius:
                triad_weight = 1.0               
                connected_triads.append([triad_ID, triad_weight])
                weight_sum += triad_weight
        
        # Normalize the sum of the weights to 1
        self.inputs = [[triad_ID, triad_weight/weight_sum] for triad_ID, triad_weight in connected_triads]
        
        