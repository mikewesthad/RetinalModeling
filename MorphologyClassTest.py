import pygame
from pygame.locals import *
from Retina import Retina
from Starburst import Starburst
from StarburstMorphology import StarburstMorphology
from Vector2D import Vector2D
from Constants import *

screen_size = (1000, 1000)
display = pygame.display.set_mode(screen_size)

# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina = Retina(width, height, grid_size, display)

starburst_morphology = StarburstMorphology(retina, Vector2D(0.0,0.0), visualize_growth=False)
  
#starburst_morphology.rescale(3)
#starburst_morphology.animateCompartments(display)  

starburst = Starburst(retina, None, starburst_morphology, Vector2D(500.0,500.0), 0, 0)
starburst.registerWithRetina()
#starburst.draw(display)

running = True
while running:
    display.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
    retina.drawGrid(display, 0)
#    starburst.draw(display, False)
    pygame.display.update()



        
#running = True
#while running:
#    display.fill((255,255,255))
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False
#    unique_starburst.draw(display, False)
#    pygame.display.update()
#    
#    
#running = True
#while running:
#    display.fill((255,255,255))
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False
#    unique_starburst.draw(display, True)
#    pygame.display.update()
#    
#
#running = True
#while running:
#    display.fill((255,255,255))
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False
#    unique_starburst.draw(display, draw_compartments=True)
#    pygame.display.update()