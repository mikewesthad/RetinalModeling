import pygame
from pygame.locals import *
from Retina import Retina
from Starburst import Starburst
from Vector2D import Vector2D
from Constants import *

import random
from copy import deepcopy

def randomColorPerturbation(color, delta):    
    color[0] += random.randint(-delta,delta)
    color[1] += random.randint(-delta,delta)
    color[2] += random.randint(-delta,delta)
    color[0] = min(255, color[0])
    color[0] = max(0, color[0])
    color[1] = min(255, color[1])
    color[1] = max(0, color[1])
    color[2] = min(255, color[2])
    color[2] = max(0, color[2])
    return color

# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina      = Retina(width, height, grid_size)
location    = Vector2D(175 * UM_TO_M, 175 * UM_TO_M)
starburst   = Starburst(retina, location)

starburst_copy = deepcopy(starburst)
starburst_copy.moveTo(Vector2D(600,800))


pygame.init()
screen_size = (1000, 1000)
display = pygame.display.set_mode(screen_size)     
background_color = (255,255,255)
display.fill(background_color)


starburst.draw(display)
        
starburst_copy.draw(display)
        
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    pygame.display.update()