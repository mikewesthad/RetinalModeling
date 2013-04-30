import pygame

class DendritePoint:

    def __init__(self, retina, compartment, location, wirelength):
        self.retina         = retina
        self.neuron         = compartment.neuron
        self.compartment    = compartment       
        self.location       = location
        self.wirelength     = wirelength
        
        if location != self.neuron.location:
            self.heading = self.neuron.location.unitHeadingTo(location)
        else:
            self.heading = None
        
        self.index = len(self.neuron.points)
        self.neuron.points.append(self)
        
        self.neurotransmitters_accepted = set()
        self.neurotransmitters_released = set()
        
    def __eq__(self, other):
        if self.location == other.location and self.dendrite == other.dendrite:
            return True
        return False
        
    def draw(self, surface, scale=1.0):
        screen_location = (self.neuron.location + self.location) * scale
        screen_location = screen_location.toIntTuple()
        screen_radius   = int(0.5 * scale)
        color           = self.compartment.color
        pygame.draw.circle(surface, color, screen_location, screen_radius)        