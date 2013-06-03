from Constants import *

retina_name = "Flash_Center_No_Decay"
stimulus_name = "0"
retina = Retina.loadRetina(retina_name)
retina.loadActivities(retina_name, stimulus_name)

#from Analysis import analyzeMultipleBars
#analyzeMultipleBars(retina)

v = Visualizer(retina)
