from BarStimulus import BarStimulus
from RuntimeBarGenerator import RuntimeBarGenerator
from Retina import Retina
from Constants import *




# Build Stimulus
barMovie    = RuntimeBarGenerator()
barStimulus = BarStimulus((0.0,0.0), 1.0, barMovie)

# Build Retina
retinaWidth     = 2000 * UM_TO_M
retinaHeight    = 2000 * UM_TO_M
retinaGridSize  = 1 * UM_TO_M
retinaTimestep  = 1000 * MS_TO_S
retina          = Retina(retinaWidth, retinaHeight, retinaGridSize,
                         retinaTimestep, barStimulus)

# Cone Layer
coneDistance    = 10 * UM_TO_M
coneDensity     = 10000000000.0
coneInputSize   = 10 * UM_TO_M

# Horizontal Layer
diffusionDistance = 40 * UM_TO_M
retina.buildConeLayer(coneDistance, coneDensity, coneInputSize)
##retina.buildHorizontalLayer(diffusionDistance)


##duration = 2*retinaTimestep
##retina.runModel(duration)
