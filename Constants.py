import pygame
from pygame.locals import *
import numpy as np

"""
Linearly interpolate between color1 and color2
"""
def lerpColors(color1, color2, fraction):
    r = color1.r + fraction * (color2.r - color1.r)
    g = color1.g + fraction * (color2.g - color1.g)
    b = color1.b + fraction * (color2.b - color1.b)
    return pygame.Color(int(r),int(g),int(b))
    
def getColorFromActivity(colormap, activity):
    
    for index in range(len(colormap)-1):
        value1, color1 = colormap[index]
        value2, color2 = colormap[index+1]
        if activity <= value2:      # This implicitly handles cases when activity < colormap
            fraction = (activity - value1) / (value2 - value1)
            new_color = lerpColors(color1, color2, fraction)
            return new_color
    
    # Value above the maximum of the colormap
    print "Activity value above maximum of colormap", activity
    return color2
            
            
BLUE_RED_COLORMAP = [[-1.0, pygame.Color(0,0,255)], [0.0, pygame.Color(0,0,0)], [1.0, pygame.Color(255,0,0)]]


UM_TO_M = 1/1000000.0
M_TO_UM = 1/UM_TO_M

MM_TO_M = 1/1000.0
M_TO_MM = 1/MM_TO_M

MS_TO_S = 1/1000.0
S_TO_MS = 1/MS_TO_S

GLY     = "Gly"
GLU     = "Glu"
GABA    = "GABA"
ACH     = "ACh"

NEUROTRANSMITTERS = set([GLY, GLU, GABA, ACH])

# Color palettes (first color is suggested background color)
GOLDFISH            = [(224,228,204),(105,210,231),(167,219,216),(243,134,48),(250,105,0)]
OCEAN_FIVE          = [(224,228,204),(0,160,176),(106,74,60),(204,51,63),(235,104,65),(237,201,81)]
PAPUA_NEW_GUINEA    = [(252,235,182),(94,65,47),(120,192,168),(240,120,24),(240,168,48)]
ICED_COFFEE         = [(231,243,239),(140,100,41),(85,195,220),(226,75,44),(115,114,109)]



from Stimulus import Stimulus
from RuntimeBarGenerator import RuntimeBarGenerator

from Vector2D import Vector2D

from ConeLayer import ConeLayer
from HorizontalLayer import HorizontalLayer

from DendritePoint import DendritePoint
from Compartment import Compartment
from Bipolar import Bipolar
from BipolarLayer import BipolarLayer

from Compartment import Compartment
from Compartment import GrowingCompartment
from StarburstDendrite import DendriteSegment
from StarburstMorphology import StarburstMorphology
from Starburst import Starburst
from StarburstLayer import StarburstLayer
from Retina import Retina
from Visualizer import Visualizer


        


