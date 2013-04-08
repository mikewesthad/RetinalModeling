import pickle, os

save_directory  = "Fast Bar Slow Horizontal"
saved_path      = os.path.join(os.getcwd(), save_directory, "retina.p")
retina = pickle.load(open(saved_path, "rb"))


#Delete the first few timesteps
#retina.cone_activities = retina.cone_activities[3:]
#retina.horizontal_activities = retina.horizontal_activities[3:]
#retina.on_bipolar_activities = retina.on_bipolar_activities[3:]
#retina.off_bipolar_activities = retina.off_bipolar_activities[3:]

retina.visualizeOnBipolarWeights()
retina.visualizeOffBipolarWeights()
retina.visualizeOPLCellPlacement()
retina.playConeActivity()
retina.playHorizontalActivity()
retina.playOnBipolarActivity()
retina.playOffBipolarActivity()