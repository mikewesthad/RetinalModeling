import pickle, os

save_directory  = os.path.join("Saved Retinas", "Diffuse Bipolar")
saved_path      = os.path.join(os.getcwd(), save_directory, "retina.p")
retina = pickle.load(open(saved_path, "rb"))


#Delete the first few timesteps
#retina.cone_activities = retina.cone_activities[3:]
#retina.horizontal_activities = retina.horizontal_activities[3:]
#retina.on_bipolar_activities = retina.on_bipolar_activities[3:]
#retina.off_bipolar_activities = retina.off_bipolar_activities[3:]

retina.visualizeOPLCellPlacement()
retina.visualizeOnBipolarWeights()
retina.visualizeOffBipolarWeights()
retina.playConeActivity()
retina.playHorizontalActivity()
retina.playOnBipolarActivity()
retina.playOffBipolarActivity()