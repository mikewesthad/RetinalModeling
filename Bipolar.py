import random
import math as m
from Constants import *

class Bipolar:
    
    def __init__(self, layer, location):
        self.location = location
        
        self.layer  = layer
        self.retina = layer.retina
        
        self.history_size   = layer.history_size           
        
        self.activities = []
        self.neurotransmitter_ouputs = []
        for step in range(self.history_size):
            self.activities.append(0.0)
            self.neurotransmitter_ouputs.append({})
            
        self.inputs = []
        
        
    def draw(self, surface, scale=1.0):
        self.compartment.draw(surface, self, scale=scale)
        
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
                triad_activity = -(cone_activity - horizontal_activity)/2.0  
            else: 
                triad_activity = (cone_activity - horizontal_activity)/2.0
            
            new_activity += triad_weight * triad_activity
        
        # Update the neurotransmitter amounts that are output
        new_neurotransmitter_outputs = self.compartment.calculateNeurotransmitterOutputs(new_activity)
        
        # Store the new activity and nt output
        self.activities.insert(0, new_activity)
        self.neurotransmitter_ouputs.insert(0, new_neurotransmitter_outputs)
        
        return new_activity
        
    def compartmentalize(self, compartment):
        self.compartment = compartment
        self.compartment.registerWithRetina(self, self.layer.layer_depth)
        
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
        
        