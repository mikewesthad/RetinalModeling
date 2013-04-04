from BarStimulus import BarStimulus
from RuntimeBarGenerator import RuntimeBarGenerator
from Retina import Retina
from Constants import *


from time import clock


stimBuildTime = 0.0



# Build Stimulus
start = clock()
barMovie    = RuntimeBarGenerator()
barStimulus = BarStimulus((0.0,0.0), 1.0, barMovie)
print "Stimulus Build Time",clock()-start

# Build Retina
retinaWidth     = 1000 * UM_TO_M
retinaHeight    = 1000 * UM_TO_M
retinaGridSize  = 2 * UM_TO_M
start = clock()
retina          = Retina(retinaWidth, retinaHeight, retinaGridSize, barStimulus)
print "Retina Build Time",clock()-start

# Build Cone Layer
minimumDistance = 10 * UM_TO_M
minimumDensity  = 10000.0
inputFieldSize  = 10 * UM_TO_M
start = clock()
retina.buildConeLayer(minimumDistance, minimumDensity, inputFieldSize)
print "Cone Layer Build Time",clock()-start


start = clock()
retina.updateActivity()
print "Update Activity Time",clock()-start

retina.visualizeConeActivity()
##retina.visualizeConeWeights()
