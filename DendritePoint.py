import pygame

class DendritePoint:

    def __init__(self, retina, dendrite, location, wirelength):
        self.retina     = retina    
        self.dendrite   = dendrite       
        self.location   = location
        self.wirelength = wirelength
        
        if location != dendrite.neuron.location:
            self.heading = dendrite.neuron.location.unitHeadingTo(location)
        else:
            self.heading = None
        
        self.index = len(self.dendrite.neuron.points)
        self.dendrite.neuron.points.append(self)
        
        self.neurotransmitters_accepted = set()
        self.neurotransmitters_released = set()
        
    def __eq__(self, other):
        if self.location == other.location and self.dendrite == other.dendrite:
            return True
        return False
        
    def draw(self, surface):
        world_location = self.dendrite.neuron.location + self.location
        c = int(self.wirelength / (self.dendrite.neuron.bounding_radius) * 255)
        c = min(c, 255)
        
        if self.neurotransmitters_released != set():
            pygame.draw.circle(surface, (255-c,0,0), world_location.toIntTuple(), 2)
        else:
            pygame.draw.circle(surface, (0,0,255-c), world_location.toIntTuple(), 2)
            