import pygame
from pygame.locals import *
from Retina import Retina
from Starburst import Starburst
from StarburstMorphology import StarburstMorphology
from Vector2D import Vector2D
from Constants import *

# Build a display
palette     = GOLDFISH
background  = palette[0]
screen_size = Vector2D(1000, 1000)
display     = pygame.display.set_mode(screen_size.toIntTuple())

# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S
retina      = Retina(width, height, grid_size, display)

# Build a starburst morphology
screen_mid = screen_size/2.0
starburst_morphology = StarburstMorphology(retina, visualize_growth=False, color_palette=palette,
                                           display=display, draw_location=screen_mid)

# Build a unique starburst cell using the morphology
scale = 3.0
screen_mid = screen_size/(2.0 * scale)
starburst = Starburst(retina, None, starburst_morphology, screen_mid, 0, 0)
starburst.registerWithRetina()

# Interactive drawing (switch between views with d/c/p; change scale with left/right)
running             = True
draw_segments       = True
draw_compartments   = False
draw_points         = False
while running:
    display.fill(GOLDFISH[0])
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_d:
                draw_segments       = True
                draw_compartments   = False
                draw_points         = False
            elif event.key == K_c:
                draw_segments       = False
                draw_compartments   = True
                draw_points         = False
            elif event.key == K_p:
                draw_segments       = False
                draw_compartments   = False
                draw_points         = True
            elif event.key == K_c:
                draw_segments       = False
                draw_compartments   = True
                draw_points         = False
            elif event.key == K_LEFT:
                scale -= 1.0
                screen_mid = screen_size/(2.0 * scale)
                starburst.location = screen_mid
            elif event.key == K_RIGHT:
                scale += 1.0
                screen_mid = screen_size/(2.0 * scale)
                starburst.location = screen_mid
                
            
    starburst.draw(display, scale=scale, draw_segments=draw_segments,
                   draw_compartments=draw_compartments, draw_points=draw_points)   
    pygame.display.update()
    
    
    

# Investigate the shortest path distances
running = True
while running:
    display.fill(GOLDFISH[0])
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
    starburst.draw(display, scale=scale, draw_compartments=True)   
    pygame.display.update()
