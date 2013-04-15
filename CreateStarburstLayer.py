import pygame
from pygame.locals import *
from Retina import Retina
from StarburstLayer import StarburstLayer
from Vector2D import Vector2D
from Constants import *


# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina      = Retina(width, height, grid_size)
location    = Vector2D(175 * UM_TO_M, 175 * UM_TO_M)


pygame.init()
screen_size = (retina.grid_width, retina.grid_height)
display = pygame.display.set_mode(screen_size)     
background_color = (255,255,255)
display.fill(background_color)

nearest_neighbor_distance = 30 * UM_TO_M
minimum_required_density = 100
sl = StarburstLayer(retina, "On", None, 3, 1, nearest_neighbor_distance, minimum_required_density,
                    visualize_growth=True, display=display)



        
running = True
while running:
    sl.draw(display)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    pygame.display.update()