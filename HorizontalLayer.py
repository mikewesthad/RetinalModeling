import numpy as np
from Constants import *



class HorizontalLayer:

    def __init__(self, retina, cone_layer, input_delay, history_size, 
                 input_strength, decay_rate, diffusion_width):

        self.retina     = retina
        self.cone_layer = cone_layer

        self.history_size   = history_size
        self.input_delay    = input_delay
    
        self.nearest_neighbor_distance          = cone_layer.nearest_neighbor_distance
        self.nearest_neighbor_distance_gridded  = cone_layer.nearest_neighbor_distance_gridded
        
        self.diffusion_width            = diffusion_width
        self.diffusion_width_gridded    = diffusion_width / retina.grid_size
        
        self.locations  = cone_layer.locations
        self.neurons    = len(self.locations)
        self.initializeActivties()

        self.establishLateralConnections()
        
        self.decay_rate         = decay_rate
        self.input_strength     = input_strength
        
        
    def loadPast(self, activity):
        self.activities[0] = activity
    
    def drawActivity(self, surface, colormap, activity_bounds, radius=None, scale=1.0):
        if radius == None: radius = self.nearest_neighbor_distance_gridded/2.0
        min_activity, max_activity = activity_bounds
        
        radius  = int(radius*scale)
        for n in range(self.neurons):
            activity = self.activities[0][0, n]
            color = getColorFromActivity(colormap, activity)    
            x, y = self.locations[n]
            x, y = int(x*scale), int(y*scale)
            pygame.draw.circle(surface, color, (x, y), radius) 
    
    def draw(self, surface, inflate_radius=0.0, radius=None, color=None, scale=1.0):     
        if radius == None: radius = self.nearest_neighbor_distance_gridded/2.0
        if color == None: color = self.retina.horizontal_color
        
        radius  = int((radius+inflate_radius)*scale)
        for x, y in self.locations:
            x, y = int(x*scale), int(y*scale)
            pygame.draw.circle(surface, color, (x, y), radius)     
        
    def __str__(self):
        string = ""
        string += "Horizontal Layer\n"
        string += "\nNearest Neightbor Distance (um)\t\t"+str(self.nearest_neighbor_distance * M_TO_UM)
        string += "\nNumber of Neurons\t\t\t"+str(self.neurons)
        string += "\nInput Delay (timesteps)\t\t\t"+str(self.input_delay)
        string += "\nDiffusion Width (um)\t\t\t"+str(self.diffusion_width * M_TO_UM)
        string += "\nDecay Rate\t\t\t\t"+str(self.decay_rate)
        string += "\nInput Strength:\t\t\t\t"+str(self.input_strength)
        return string    

    """
    This function creates the weight matrix that defines diffusion.  It calculates
    the distances from each horizontal cell to all other horizontal cells, applies
    a gaussian to those distances and then normalizes the sum of each row to 1
    """
    def establishLateralConnections(self):
        # An (n x n) array
        distances = np.zeros((self.neurons, self.neurons))
        
        # Fill the array with distances between each neuron
        for n1 in range(self.neurons):
            x1, y1 = self.locations[n1]
            for n2 in range(n1, self.neurons):
                x2, y2 = self.locations[n2]
                distance = linearDistance(x1, y1, x2, y2)
                distances[n1, n2] = distance
                if n1 != n2: distances[n2, n1] = distance
        
        # Perform e^(-distance**2/width) on each element in the distance matrix
        sigma = self.diffusion_width_gridded
        self.lateral_weights = np.exp(-(distances)**2/(2.0*sigma**2.0))
        
        # Get the sum of each row
        row_sum = np.sum(self.lateral_weights, 1)
        
        # Reshape the rowSum into a column vector since sum removes a dimension
        row_sum.shape = (self.neurons, 1)
        
        # Normalize the weight matrix
        self.lateral_weights = self.lateral_weights / row_sum
        
        
    """
    Initialize a zero-filled history activity 
    """
    def initializeActivties(self):
        self.activities = []
        for i in range(self.history_size):
            blank_activity = np.zeros((1, self.neurons))
            self.activities.append(blank_activity)
            
    """
    Update the horizontal cell activity based on diffusion, decay and cone activity 
    """      
    def update(self):
        # Delete the oldest activity and get the current activity
        del self.activities[-1]
        last_activity = self.activities[0]
        
        # Calculate the diffusion
        d = self.decay_rate
        diffusionActivity = (1.0-d) * np.dot(last_activity, self.lateral_weights)
        
        # Get the cone activity
        cone_activity   = self.cone_layer.activities[self.input_delay]
        
        # Find the new activity
        i = self.input_strength
        new_activity = (1.0-i) * diffusionActivity + i * cone_activity
        
        # Alternative method of updating, no weighted average with cone input
#        new_activity = diffusionActivity + i * cone_activity
#        new_activity = np.clip(new_activity, -1.0, 1.0)        
        
        # Add the most recent activity to the front of the list
        self.activities.insert(0, new_activity)
        
        return new_activity
    


"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5
