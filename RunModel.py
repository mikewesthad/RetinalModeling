from Retina import Retina
from Constants import *

# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina = Retina(width, height, grid_size)


nearest_neighbor_distance = 30 * UM_TO_M
minimum_required_density = 100
retina.buildStarburstLayer(nearest_neighbor_distance, minimum_required_density)