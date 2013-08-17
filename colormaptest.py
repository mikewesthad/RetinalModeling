from Constants import *
from CreateStimulus import createManyBars
import matplotlib.pyplot as plt
import os
import pygame
import matplotlib
from pygame.constants import *
import matplotlib.image as mpimg
import numpy as np


def createFigure(long_side_size, rows, cols):
    width, height = long_side_size, long_side_size
    if rows > cols:
        width *= float(cols)/float(rows)
    elif cols > rows:
        height *= float(rows)/float(cols)
    return plt.figure(figsize=(width, height))
# Set up all these parameters correctly - load a retina, it's paramaters and the first stimulus
retina_directory_path       = os.path.join("Analyzed for Thesis", "Bar_Euler_Results")
retina_directory_full_path  = os.path.join(os.getcwd(), "Saved Retinas", "Analyzed for Thesis", "Bar_Euler_Results")
retina_path                 = os.path.join(retina_directory_path, "0")
stimulus_name               = "0_0"
parameter_filename          = os.path.join(retina_directory_full_path, "Bar_Euler_Results Parameters.txt")

# Save the cone layer activities
cone_layer_path = os.path.join(retina_directory_full_path, "Cone Layer.jpg")
cone_layer_image = mpimg.imread(cone_layer_path)


# Create a matplotlib figure
fig_rows, fig_cols  = 1, 1
fig                 = createFigure(5.0, fig_rows, fig_cols)
grid_size           = (fig_rows, fig_cols)
plot_label_props    = dict(boxstyle='round', facecolor='white', alpha=1.0)
plot_label_x        = 0.05
plot_label_y        = 0.95
plot_label_size     = 20
x_tick_size         = 12
x_label_size        = 16
y_label_size        = 16
y_tick_size         = 12
title_size          = 18


         
# Cone row of figure
#ax = plt.subplot2grid(grid_size, (0, 0))  
#im = ax.imshow(cone_layer_image)
#ax.axis('off')                     
#plt.text(plot_label_x, plot_label_y, "D", transform=ax.transAxes, 
#         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
#ax.set_title("Cone Layer Activity at ms", size=title_size)
#plt.colorbar(im, cmap=my_cmap)


cdict = {'red': ((0.0, 0, 0),
                 (0.5, 0, 0),
                 (1.0, 1, 1)),
         'green': ((0.0, 0, 0),
                 (0.5, 0, 0),
                 (1.0, 0, 0)),
         'blue': ((0.0, 1, 1),
                 (0.5, 0, 0),
                 (1.0, 0, 0))}
my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict)
ax = fig.add_axes([0.05, 0.1, 0.025, 0.8])
norm = matplotlib.colors.Normalize(vmin=-1.0, vmax=1.0)
cb1 = matplotlib.colorbar.ColorbarBase(ax, cmap=my_cmap,
                                   norm=norm,
                                   orientation='vertical')

plt.show()