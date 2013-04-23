from Constants import *
from Vector2D import Vector2D
import pygame
from pygame.locals import *
from Retina import Retina
from Starburst import Starburst
from StarburstMorphology import StarburstMorphology






#Build a display
background  = (255, 255, 255)
screen_size = Vector2D(1000,1000)
display     = pygame.display.set_mode(screen_size.toIntTuple())

#Build a retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S
retina      = Retina(width, height, grid_size, display)

#Build a starburst morphology
scale = 2.0
screen_third = screen_size/(3.0 * scale)
starburst_morphology1 = StarburstMorphology(retina,
                                            visualize_growth=True,
                                            color_palette=BLUES,
                                            display=display,
                                            draw_location=screen_third,
                                            scale=scale)
                                           
starburst_morphology2 = StarburstMorphology(retina,
                                            visualize_growth=True,
                                            color_palette=REDS,
                                            display=display,
                                            draw_location=2*screen_third,
                                            scale=scale)

#Build a unique starburst cells using above morphologies
starburst1 = Starburst(retina, None, starburst_morphology1, 
                       screen_third, 0, 0)
starburst2 = Starburst(retina, None, starburst_morphology2,
                       2 * screen_third, 0, 0)
                       
SACs = [starburst1, starburst2]
                       
for sac in SACs:
    sac.registerWithRegina()













#Interactive drawing
#switch between views with d/c/p; change scale with left/right
running             = True
draw_segments       = True
draw_compartments   = False
draw_points         = False
while running:
    display.fill(background)
    for event in pygame.event.get():
        if event.type ==QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_d:
                draw_segments       = True
                draw_compartments   = False
                draw_points         = False
            if event.key == K_c:
                draw_segments       = False
                draw_compartments   = True
                draw_points         = False
            if event.key == K_p:
                draw_segments       = False
                draw_compartments   = False
                draw_points         = True
            if event.key == K_LEFT:
                scale /= 1.5
            if event.key == K_RIGHT:
                scale *= 1.5
    screen_third = screen_size/(3.0 * scale)
    for i in range(len(SACs)):
        SACs[i].location = (i+1)*screen_third        
        SACs[i].draw(display, 
                            scale = scale,
                            draw_segments = draw_segments,
                            draw_compartments = draw_compartments,
                            draw_points = draw_points)
    pygame.display.update()
            
                       
