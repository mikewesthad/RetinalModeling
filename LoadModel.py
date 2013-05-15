from Constants import *

directory_name = "No Horizontals\In Str .5 Diff 30"
stimulus_name = "0_0"

retina = Retina.loadRetina(directory_name)
retina.loadActivities(directory_name, stimulus_name)


#from Analysis import analyzeMultipleBars
#analyzeMultipleBars(retina)

v = Visualizer(retina)