from Constants import *

directory_name = "6"
stimulus_name = "26"

retina = Retina.loadRetina(directory_name)
retina.loadActivities(directory_name, stimulus_name)

v = Visualizer(retina)