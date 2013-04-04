from BarStimulus import BarStimulus
from RuntimeBarGenerator import RuntimeBarGenerator
from Retina import Retina
from Constants import *




# Build Stimulus
barMovie    = RuntimeBarGenerator()
barStimulus = BarStimulus((0.0,0.0), 1.0, barMovie)

# Build Retina
retinaWidth     = 1000 * UM_TO_M
retinaHeight    = 1000 * UM_TO_M
retinaGridSize  = 2 * UM_TO_M
retina          = Retina(retinaWidth, retinaHeight, retinaGridSize, barStimulus)

# Build Cone Layer
minimumDistance = 10 * UM_TO_M
minimumDensity  = 10000.0
inputFieldSize  = 10 * UM_TO_M
retina.buildConeLayer(minimumDistance, minimumDensity, inputFieldSize)


retina.updateActivity()

##retina.visualizeConeActivity()
##retina.visualizeConeWeights()
