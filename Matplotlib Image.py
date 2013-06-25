import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os


image_path = os.path.join(os.getcwd(), "Directionally Selective Analysis","12 Direction - 100 FPS Remove Stutter From Floating Point Inaccuracies Increased Diffusion Radius (Longer stimulus time)_0","DSI_Morphology.jpg")

img=mpimg.imread(image_path)

imgplot = plt.imshow(img)

plt.show()