import pickle, os

save_directory  = os.path.join("Saved Retinas", "Diffuse Bipolar")
saved_path      = os.path.join(os.getcwd(), save_directory, "retina.p")
retina = pickle.load(open(saved_path, "rb"))

from Visualizer import Visualizer

v = Visualizer(retina)