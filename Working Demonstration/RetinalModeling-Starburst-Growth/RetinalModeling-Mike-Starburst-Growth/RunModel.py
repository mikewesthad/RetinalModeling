import pygame
from Retina import Retina
from Constants import *

screen_size = (1000, 1000)
display = pygame.display.set_mode(screen_size)

# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina = Retina(width, height, grid_size, display)



nearest_neighbor_distance = 30 * UM_TO_M
minimum_required_density = 10
retina.buildStarburstLayer(nearest_neighbor_distance, minimum_required_density)