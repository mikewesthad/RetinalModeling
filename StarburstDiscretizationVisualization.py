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

retina      = Retina(width, height, grid_size)
location    = Vector2D(175 * UM_TO_M, 175 * UM_TO_M)
starburst   = Starburst(retina, location)

pygame.init()
screen_size = (1000, 1000)
scale = 3
display = pygame.display.set_mode(screen_size)     
background_color = (255,255,255)

display.fill(background_color)

for i in range(0,1000,scale):
    pygame.draw.line(display, (200,200,200), (i,0), (i,1000))
    pygame.draw.line(display, (200,200,200), (0,i), (1000,i))

for dendrite in starburst.dendrites:
    color = list(dendrite.color)
    import random
    color[0] += random.randint(-50,50)
    color[1] += random.randint(-50,50)
    color[2] += random.randint(-50,50)
    color[0] = min(255, color[0])
    color[0] = max(0, color[0])
    color[1] = min(255, color[1])
    color[1] = max(0, color[1])
    color[2] = min(255, color[2])
    color[2] = max(0, color[2])
    for location in dendrite.gridded_locations:
        scaled_location = location * scale
        pygame.draw.circle(display, color, scaled_location.toIntTuple(), 2)
        
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    pygame.display.update()

numberPoints = 0
overlaps = 0
for a in range(len(starburst.dendrites)):
    for b in range(a+1, len(starburst.dendrites)):
        dendrite_a = starburst.dendrites[a]
        dendrite_b = starburst.dendrites[b]
        for location_a in dendrite_a.gridded_locations:
            numberPoints += 1
            for location_b in dendrite_b.gridded_locations:
                if location_a == location_b:
                    overlaps += 1
                        
print "After discretization, there are {0} overlapping dendrite points out of a total {1} points".format(overlaps, numberPoints)