import pickle, os

save_directory  = "Test_"
saved_path      = os.path.join(os.getcwd(), save_directory, "retina.p")
retina = pickle.load(open(saved_path, "rb"))

retina.visualizeOnBipolarWeights()
retina.visualizeOffBipolarWeights()
retina.visualizeOPLCellPlacement()
retina.playConeActivity()
retina.playHorizontalActivity()
retina.playOnBipolarActivity()
retina.playOffBipolarActivity()