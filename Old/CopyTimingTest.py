import pygame
from pygame.locals import *
from Starburst import Starburst
from Retina import Retina
from StarburstLayer import StarburstLayer
from Vector2D import Vector2D
from Constants import *
from time import time


# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina      = Retina(width, height, grid_size)
location    = Vector2D(175 * UM_TO_M, 175 * UM_TO_M)


s = Starburst(retina, location, visualize_growth=False)

start = time()
s.createCopy()
print time() - start


start = time()
s.customCopy()
print time() - start