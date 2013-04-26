from Retina import Retina
from Starburst import Neuron
from Constants import *

# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina = Retina(width, height, grid_size)

for x in range(20):
    startburst = Neuron(retina, (500 * UM_TO_M, 500 * UM_TO_M))