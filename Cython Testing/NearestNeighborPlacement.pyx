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
    
    
    
import math   
import random 
    
def linearDistancePython(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5
    
def placeNeuronsPython(retina_width, retina_height, required_cells, retina_size, gridded_distance, max_rand_tries=1000):
    # Set the bounds on the positions
    xmin = 0
    ymin = 0
    xmax = retina_width
    ymax = retina_height

    # Convert the minimum distance from world units to grid units
    ceil_gridded_distance = int(math.ceil(gridded_distance))

    # Calculate the number of cells to place
    current_cells  = 0

    # Create empty sets to hold the selected positions and the excluded positions
    excluded_positions = set()
    locations = []

    while current_cells < required_cells:

        # Pick a random point
        x = random.randint(xmin, xmax)
        y = random.randint(ymin, ymax)
        loc_ID  = str(x) + "." + str(y)
        
        # Regenerate random point until a valid point is found
        rand_tries = 0
        while loc_ID in excluded_positions:
            x = random.randint(xmin, xmax)
            y = random.randint(ymin, ymax)
            loc_ID = str(x) + "." + str(y)
            
            rand_tries += 1
            if rand_tries > max_rand_tries: break

        # If too many attempts were made to generate a new point, exit loop
        if rand_tries > max_rand_tries: break    

        # Update the sets with the newly selected point
        excluded_positions.add(loc_ID)
        locations.append([x, y])

        # Find the bounding box of excluded coordinates surrounding the new point
        left    = int_max(x - ceil_gridded_distance, xmin)
        right   = int_min(x + ceil_gridded_distance, xmax)
        up      = int_max(y - ceil_gridded_distance, ymin)
        down    = int_min(y + ceil_gridded_distance, ymax)

        # Check if each point in the bounding box is within the minimum distance radius
        # If so, add it to the exclusion set
        for x2 in range(left, right+1):
            for y2 in range(up, down+1):
                if linearDistancePython(x, y, x2, y2) < gridded_distance:
                    loc_ID = str(x2) + "." + str(y2)
                    excluded_positions.add(loc_ID)

        current_cells += 1    
        
    
    return locations
    
    