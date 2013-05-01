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
from StarburstLayer import StarburstLayer
from Starburst import Starburst
from Retina import Retina



