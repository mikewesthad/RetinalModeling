import numpy as np
cimport numpy as np

cdef class Retina:
    cdef double width
    cdef double height
    cdef double area
    cdef double grid_size
    cdef int grid_width
    cdef int grid_height
    cdef double time
    cdef double timestep
    cdef int history_size
    cdef double density_area 
    cdef ConeLayer cone_layer
    
    def __init__(self, double retina_width, double retina_height, double grid_size, double timestep):
        self.width  = retina_width
        self.height = retina_height
        self.area   = retina_width * retina_height
        
        self.grid_size      = grid_size
        self.grid_width     = int(retina_width / grid_size)
        self.grid_height    = int(retina_height / grid_size)
        
        self.time       = 0.0
        self.timestep   = timestep
        
        self.history_size = 3
            
    
    def buildConeLayer(self, double minimum_distance, int minimum_cells):
        
        self.cone_layer = ConeLayer(self, minimum_distance / self.grid_size, 
                                    minimum_cells, self.history_size)



cdef class ConeLayer:
    cdef Retina retina
    cdef list locations
    cdef int number_neurons
    cdef int history_size
    cdef np.ndarray activities
    
    
    def __init__(self, Retina retina, double nearest_neighbor_distance, int number_cells, int history_size):

        self.retina = retina        
        
        self.locations = placeNeurons(retina.grid_width, retina.grid_height, number_cells, nearest_neighbor_distance)
        self.number_neurons = len(self.locations)
        
        self.history_size = history_size
        self.initializeActivities()
        print self.number_neurons
        
        
    cdef initializeActivities(self):
        self.activities = np.zeros((self.history_size, 1, self.number_neurons))
        
        
        
        
from libc.math cimport ceil
from libc.math cimport sqrt
from numpy.random import randint as rint


cdef int int_max(int a, int b): 
    return a if a >= b else b
cdef int int_min(int a, int b): 
    return a if a <= b else b
    
cdef double linearDistance(double x1, double y1, double x2, double y2):
    return sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))

def placeNeurons(int retina_width, int retina_height, int required_cells, double gridded_distance, int max_rand_tries=1000):
    # Set the bounds on the positions
    cdef int xmin = 0
    cdef int ymin = 0
    cdef int xmax = retina_width
    cdef int ymax = retina_height

    # Convert the minimum distance from world units to grid units
    cdef int ceil_gridded_distance = int(ceil(gridded_distance))

    # Calculate the number of cells to place
    cdef int current_cells  = 0

    # Create empty sets to hold the selected positions and the excluded positions
    excluded_positions = set()
    locations = []

    cdef int rand_tries
    cdef int left, right, up, down
    cdef int x2, y2
    cdef tuple loc
    while current_cells < required_cells:

        # Pick a random point
        x = rint(xmin, xmax)
        y = rint(ymin, ymax)
        loc = (x, y)
        
        # Regenerate random point until a valid point is found
        rand_tries = 0
        while loc in excluded_positions:
            x = rint(xmin, xmax)
            y = rint(ymin, ymax)
            loc = (x, y)
            
            rand_tries += 1
            if rand_tries > max_rand_tries: break

        # If too many attempts were made to generate a new point, exit loop
        if rand_tries > max_rand_tries: break    

        # Update the sets with the newly selected point
        excluded_positions.add(loc)
        locations.append(loc)

        # Find the bounding box of excluded coordinates surrounding the new point
        left    = max(x - ceil_gridded_distance, xmin)
        right   = min(x + ceil_gridded_distance, xmax)
        up      = max(y - ceil_gridded_distance, ymin)
        down    = min(y + ceil_gridded_distance, ymax)

        # Check if each point in the bounding box is within the minimum distance radius
        # If so, add it to the exclusion set
        for x2 in range(left, right+1):
            for y2 in range(up, down+1):
                if linearDistance(x, y, x2, y2) < gridded_distance:
                    loc = (x2, y2)
                    excluded_positions.add(loc)

        current_cells += 1  
        
    return locations