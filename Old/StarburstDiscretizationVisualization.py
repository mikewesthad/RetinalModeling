import pygame
from pygame.locals import *
from Retina import Retina
from Starburst import Starburst
from Vector2D import Vector2D
from Constants import *


# Build Retina
width       = 1000 * UM_TO_M
height      = 1000 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S


pygame.init()
screen_size = (1000, 1000)
display = pygame.display.set_mode(screen_size)     
background_color = (255,255,255)
display.fill(background_color)


retina      = Retina(width, height, grid_size)
location    = Vector2D(175 * UM_TO_M, 175 * UM_TO_M)
starburst   = Starburst(retina, location, display=display, visualize_growth=True)

display.fill(background_color)
scale = 5

for i in range(0,1000,scale):
    pygame.draw.line(display, (200,200,200), (i,0), (i,1000))
    pygame.draw.line(display, (200,200,200), (0,i), (1000,i))

starburst.moveTo(Vector2D(500,500))
starburst.rescale(scale)
starburst.draw(display, True)
        
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    pygame.display.update()


numberPoints = 0
overlaps = 0
for a in range(len(starburst.dendrites)):
    numberPoints += len(starburst.dendrites[a].gridded_locations)
    for b in range(a+1, len(starburst.dendrites)):
        dendrite_a = starburst.dendrites[a]
        dendrite_b = starburst.dendrites[b]
        for location_a in dendrite_a.gridded_locations:
            for location_b in dendrite_b.gridded_locations:
                if location_a == location_b:
                    overlaps += 1
                        
print "After discretization, there are {0} overlapping dendrite points out of a total {1} points".format(overlaps, numberPoints)