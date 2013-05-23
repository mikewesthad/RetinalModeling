from Constants import *

retina_name = "4 Directions - 100 FPS"
stimulus_name = "0_270"
retina = Retina.loadRetina(retina_name)

retina.loadActivities(retina_name, stimulus_name)

#from Analysis import analyzeMultipleBars
#analyzeMultipleBars(retina)

v = Visualizer(retina)