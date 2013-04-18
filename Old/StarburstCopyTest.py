import pygame
from pygame.locals import *
from Retina import Retina
from Starburst import Starburst
from Vector2D import Vector2D
from Constants import *
from random import randint

screen_size = (1000, 1000)
display = pygame.display.set_mode(screen_size)

# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina = Retina(width, height, grid_size, display)



unique_starburst = Starburst(retina, Vector2D(500.0,500.0), layer=None, 
                             visualize_growth=True,
                             display=display)
            

starburst_copy = unique_starburst.createCopy()
starburst_copy.moveTo(Vector2D(200.0,200.0))

for d in starburst_copy.dendrites:
    for i in range(10):
       d.locations[randint(0,len(d.locations)-1)].x += randint(-20,20)
       d.locations[randint(0,len(d.locations)-1)].y += randint(-20,20)

for d in starburst_copy.dendrites:
    for i in range(100):
       d.gridded_locations[randint(0,len(d.gridded_locations)-1)].x += randint(-10,10)
       d.gridded_locations[randint(0,len(d.gridded_locations)-1)].y += randint(-10,10)

running = True
while running:
    display.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    unique_starburst.draw(display, False)
    starburst_copy.draw(display, False)
    pygame.display.update()
    
    
running = True
while running:
    display.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    unique_starburst.draw(display, True)
    starburst_copy.draw(display, True)
    pygame.display.update()