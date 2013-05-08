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

ON      = "On"
OFF     = "Off"

RADIUS  = "Radius"
DIFFUSION = "Diffusion"

UP      = 270.0 #degrees of rotation on retinal grid
DOWN    = 90.0
LEFT    = 180.0
RIGHT   = 0.0

NEUROTRANSMITTERS = set([GLY, GLU, GABA, ACH])

# Color palettes (first color is suggested background color)
GOLDFISH            = [(224,228,204),(105,210,231),(167,219,216),(243,134,48),(250,105,0)]
OCEAN_FIVE          = [(224,228,204),(0,160,176),(106,74,60),(204,51,63),(235,104,65),(237,201,81)]
PAPUA_NEW_GUINEA    = [(252,235,182),(94,65,47),(120,192,168),(240,120,24),(240,168,48)]
ICED_COFFEE         = [(231,243,239),(140,100,41),(85,195,220),(226,75,44),(115,114,109)]

#Monochromatic color palettes
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
background = WHITE
num_steps = 5
light_cutoff = 1.0  #0.0 - 1.0, 1 is full scale
dark_cutoff = .5    #0.0 - 1.0, 0 is full scale
step = 255*(light_cutoff - dark_cutoff)/num_steps
REDS, GREENS, BLUES = [], [], []
darkest = round(255 * dark_cutoff)
for i in range(num_steps):
    value = int(round(i*step+darkest))
    REDS.append((value, 0, 0))
    GREENS.append((0, value, 0))
    BLUES.append((0, 0, value))
REDS.append(background)
GREENS.append(background)
BLUES.append(background)
#reverse to put background at the head of the list,
#because convention is palette[0] = background.
REDS.reverse()
GREENS.reverse()
BLUES.reverse()

import random
import pygame
from pygame.locals import *
import numpy as np

from BarStimulus import BarStimulus
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

from DSG import DSG

