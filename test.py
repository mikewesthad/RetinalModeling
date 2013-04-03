from BarStimulus import BarStimulus
from RuntimeBarGenerator import RuntimeBarGenerator
from ConeLayer import ConeLayer
from Retina import Retina
from Constants import *





retinaWidth     = 1000 * UM_TO_M
retinaHeight    = 1000 * UM_TO_M
retinaGridSize  = 1 * UM_TO_M
retina          = Retina(retinaWidth, retinaHeight, retinaGridSize)

barMovie    = RuntimeBarGenerator()
barStimulus = BarStimulus((0.0,0.0), 1.0, barMovie)

minDistance     = 10 * UM_TO_M
density         = 1000.0
inputField      = 10 * UM_TO_M
coneLayer       = ConeLayer(retina, minDistance, density, inputField, barStimulus)
