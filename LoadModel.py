from Constants import *

retina_name = "0"
stimulus_name = "0_0_0"
retina = Retina.loadRetina(retina_name)

retina.loadActivities(retina_name, stimulus_name)

#from Analysis import analyzeMultipleBars
#analyzeMultipleBars(retina)

v = Visualizer(retina)