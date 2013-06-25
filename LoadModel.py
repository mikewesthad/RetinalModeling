from Constants import *

retina_name = "Annuli_Test_Batch\\0"
stimulus_name = "4_centripetal"
#retina_name = "Test"
#stimulus_name = "0_0"
retina = Retina.loadRetina(retina_name)
retina.loadActivities(retina_name, stimulus_name)


#from Analysis import analyzeMultipleBars
#analyzeMultipleBars(retina)

v = Visualizer(retina)
