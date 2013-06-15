from Constants import *

retina_name = "Bar_Speed_Batch_3_12_Directions\\1"
stimulus_name = "4_0"
#retina_name = "Test"
#stimulus_name = "0_0"
retina = Retina.loadRetina(retina_name)
retina.loadActivities(retina_name, stimulus_name)


#from Analysis import analyzeMultipleBars
#analyzeMultipleBars(retina)

v = Visualizer(retina)
