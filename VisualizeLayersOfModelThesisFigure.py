from Constants import *
from CreateStimulus import createManyBars
import matplotlib.pyplot as plt
import os
import pygame
import matplotlib
from pygame.constants import *
import matplotlib.image as mpimg
import numpy as np

# Set up all these parameters correctly - load a retina, it's paramaters and the first stimulus
retina_directory_path       = os.path.join("Analyzed for Thesis", "Bar_Euler_Results")
retina_directory_full_path  = os.path.join(os.getcwd(), "Saved Retinas", "Analyzed for Thesis", "Bar_Euler_Results")
retina_path                 = os.path.join(retina_directory_path, "0")
stimulus_name               = "0_0"
parameter_filename          = os.path.join(retina_directory_full_path, "Bar_Euler_Results Parameters.txt")




def createFigure(long_side_size, rows, cols):
    width, height = long_side_size, long_side_size
    if rows > cols:
        width *= float(cols)/float(rows)
    elif cols > rows:
        height *= float(rows)/float(cols)
    return plt.figure(figsize=(width, height))

###############################################################################
# Reading in Parameters from a given text file given the filename
#   The file needs to have the following format:
#       The "#" character indicates that a line should be ignored 
#       If the setting is a tuple or a numeric value, it is a single value
#       If the setting is a list, it is a collection of single values
#       If the setting is either a list or a tuple, the elements must be 
#           strings with single quotations
###############################################################################
def processTextParameters(filename):
    parameters = []
    fh = open(filename,"r")
    for line in fh:
        # Disregard blank lines
        line = line.strip()
        if line != "":
            # Disregard comment lines (that start with #) 
            if line[0] != "#":
                parameter_name, parameter_values    = line.split("=")
                parameter_name                      = parameter_name.strip()
                parameter_values                    = parameter_values.strip()  
            
                if parameter_values[0] == "[":
                    new_parameter_values = processList(eval(parameter_values))
                elif parameter_values[0] == "(":
                    new_parameter_values = processTuple(eval(parameter_values))
                else:
                    new_parameter_values = processNumeric(parameter_values)
                
                parameters.append(new_parameter_values)
    return parameters
def processList(string_list):
    new_list = []
    for string_element in string_list:
        if isinstance(string_element, tuple):
            new_element = processTuple(string_element)
        else:
            new_element = processNumeric(string_element)
        new_list.append(new_element)
    return new_list        
def processTuple(string_tuple):
    processed_values = []
    for string_element in string_tuple:
        # Check if the new element is a list (diffusion parameters)
        if string_element[0] == "[":
            new_element = processTuple(eval(string_element))
        else:
            # Check if the new element is a numeric
            try:
                new_element = processNumeric(string_element)
            # The element was supposed to stay as a string
            except NameError:
                new_element = string_element
        processed_values.append(new_element)
    return tuple(processed_values)
def processNumeric(string_numeric):
    unitless_numeric, factor = stripUnits(string_numeric)
    unitless_numeric.strip()
    return eval(unitless_numeric) * factor
def stripUnits(string):
    factor = 1.0
    for unit, conversion in zip(["um", "ms"], [UM_TO_M, MS_TO_S]):
        if unit in string:
            string_position_unit = string.find(unit)
            string = string[:string_position_unit]
            factor = conversion
    return string, factor

###############################################################################
# Combination Generator
#   Given a list of values where the each value is either a:
#       A single value - numeric, boolean, string
#       A collection of values - list, tuple or numpy array
#   This function returns a list of all possible combinations
###############################################################################

def generateCombinations(parameters, current_parameter_index, 
                         current_parameter_combination, combinations):
    
    # Base case - no more parameters to check
    if current_parameter_index >= len(parameters):
        combinations.append(current_parameter_combination)
        return combinations
    
    # Get the next collection of parameter values
    #   If a paramter is a single value, then add it to the current combination
    parameter_options = parameters[current_parameter_index]
    while not(isinstance(parameter_options, (np.ndarray, list))):
        current_parameter_combination.append(parameter_options) 
        current_parameter_index += 1
        if current_parameter_index >= len(parameters): break
        parameter_options = parameters[current_parameter_index]
    
    # A secondary base case - all available parameters were exhausted by the
    # above loop and the last parameter was a single value
    if current_parameter_index >= len(parameters):
        combinations.append(current_parameter_combination)
        return combinations
    
    # Iterate through all the values in the current collection of parameter values
    for option in parameter_options:
         combinations = generateCombinations(parameters, current_parameter_index+1,
                                             current_parameter_combination + [option], combinations)
        
    return combinations

def selectDistalCompartment(display, starburst, scale, background_color, morphology_color, highlight_color):
    running = True
    selected = None
    while running:
        display.fill(background_color)     
        for compartment in starburst.compartments:
            if compartment.index == selected:
                compartment.draw(display, color=highlight_color, scale=scale)
            else:
                compartment.draw(display, color=morphology_color, scale=scale)
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                x, y = event.pos
                pos = Vector2D(float(x), float(y))
                selected = findNearestCompartment(pos, starburst, scale)
            elif event.type == MOUSEBUTTONDOWN:
                distal = selected
                return distal        
        pygame.display.flip()
    
def findNearestCompartment(pos, starburst, scale):
    min_dist = 10000000.0
    min_comp = None
    for compartment in starburst.compartments:
        loc_a = (compartment.neuron.location + compartment.line_points[0]) * scale
        loc_b = (compartment.neuron.location + compartment.line_points[1]) * scale
        loc = (loc_a + loc_b) / 2.0
        dist = loc.distanceTo(pos)
        if dist < min_dist:
            min_comp = compartment.index
            min_dist = dist
    return min_comp


# Read in the parameters and recreate the first stimulus
parameters              = processTextParameters(parameter_filename)
stimulus_parameters     = parameters[24:]  
stimulus_combinations   = generateCombinations(stimulus_parameters, 0, [], [])
stimulus_combination    = stimulus_combinations[0]
stimuli, headings       = createManyBars(*stimulus_combination)
stimulus, heading       = stimuli[0], headings[0]

# Grab a frame from the beginning of the stimulus
retina_beginning_timestep = 8
stimulus.movie.update(retina_beginning_timestep * 10/1000.0)
stimulus_beginning_path = os.path.join(retina_directory_full_path, "Stimulus Beginning.jpg")
pygame.image.save(stimulus.movie.display, stimulus_beginning_path)
stimulus_beginning_image    = mpimg.imread(stimulus_beginning_path)
stimulus_beginning_frame    = stimulus.movie.frame
stimulus_beginning_time     = stimulus.movie.time

# Grab a frame from the middle of the stimulus
retina_middle_timestep = 13
stimulus.movie.update((retina_middle_timestep-retina_beginning_timestep) * 10/1000.0)
stimulus_middle_path = os.path.join(retina_directory_full_path, "Stimulus Middle.jpg")
pygame.image.save(stimulus.movie.display, stimulus_middle_path)
stimulus_middle_image   = mpimg.imread(stimulus_middle_path)
stimulus_middle_frame   = stimulus.movie.frame
stimulus_middle_time    = stimulus.movie.time
                 
# Grab a frame from the end of the stimulus
retina_ending_timestep = 18
stimulus.movie.update((retina_ending_timestep-retina_middle_timestep) * 10/1000.0)
stimulus_ending_path = os.path.join(retina_directory_full_path, "Stimulus Ending.jpg")
pygame.image.save(stimulus.movie.display, stimulus_ending_path)
stimulus_ending_image   = mpimg.imread(stimulus_ending_path)
stimulus_ending_frame   = stimulus.movie.frame
stimulus_ending_time    = stimulus.movie.time

# Grab some stimulus parameters
stimulus_speed = stimulus.movie.bar_speed
stimulus_width = stimulus.movie.bar_size

# Display variables
pygame.init()    
max_size                        = Vector2D(1000.0, 1000.0)  
background_color                = (255, 255, 255)
width_scale                     = max_size.x / float(400)
height_scale                    = max_size.y / float(400)
scale                           = min(width_scale, height_scale)   
display                         = pygame.display.set_mode(max_size.toIntTuple())
colormap                        = [[-1.0, pygame.Color(0,0,255)], [0.0, pygame.Color(0,0,0)], [1.0, pygame.Color(255,0,0)]]

# Load the retina and activities from the first stimulus
retina = Retina.loadRetina(retina_path)
retina.loadActivities(retina_path, stimulus_name)
retina.loadPast(retina_ending_timestep)

starburst                       = retina.on_starburst_layer.neurons[0]
starburst.morphology.location   = max_size/scale/2.0

cone_index          = retina.cone_layer.findConeNear(Vector2D(300, 200))
bipolar_index       = retina.on_bipolar_layer.findBipolarNear(Vector2D(300, 200))
starburst_index     = selectDistalCompartment(display, starburst, scale, (0,0,0), (255,255,255), (255,0,0))
cone_activity       = retina.cone_activities[:, 0, cone_index]
bipolar_activity    = retina.on_bipolar_activities[:, 0, bipolar_index]
starburst_activity  = retina.on_starburst_activities[:, 0, 0, starburst_index]
timesteps           = len(cone_activity)

# Save the cone layer activities
display.fill(background_color)
retina.drawLayerActivity(display, "Cone", colormap, scale)
cone_layer_path = os.path.join(retina_directory_full_path, "Cone Layer.jpg")
pygame.image.save(display, cone_layer_path)
cone_layer_image = mpimg.imread(cone_layer_path)

# Save the cone cell location
display.fill(background_color)
retina.cone_layer.drawWithSelected(display, cone_index, scale)
cone_location_path = os.path.join(retina_directory_full_path, "Cone Location.jpg")
pygame.image.save(display, cone_location_path)
cone_location_image = mpimg.imread(cone_location_path)
    
# Save the bipolar layer activities
display.fill(background_color)
retina.drawLayerActivity(display, "On Bipolar", colormap, scale)
bipolar_layer_path = os.path.join(retina_directory_full_path, "Bipolar Layer.jpg")
pygame.image.save(display, bipolar_layer_path)
bipolar_layer_image = mpimg.imread(bipolar_layer_path)

# Save the bipolar cell location
display.fill(background_color)
retina.on_bipolar_layer.drawWithSelected(display, bipolar_index, scale)
bipolar_location_path = os.path.join(retina_directory_full_path, "Bipolar Location.jpg")
pygame.image.save(display, bipolar_location_path)
bipolar_location_image = mpimg.imread(bipolar_location_path)

# Save the starburst layer activities
display.fill(background_color)
retina.drawLayerActivity(display, "On Starburst", colormap, scale)
starburst_layer_path = os.path.join(retina_directory_full_path, "Starburst Layer.jpg")
pygame.image.save(display, starburst_layer_path)
starburst_layer_image = mpimg.imread(starburst_layer_path)

# Save the starburst compartment location
display.fill(background_color)
starburst.morphology.drawWithSelected(display, starburst_index, scale)
starburst_location_path = os.path.join(retina_directory_full_path, "Starburst Location.jpg")
pygame.image.save(display, starburst_location_path)
starburst_location_image = mpimg.imread(starburst_location_path)

# Create a matplotlib figure
fig_rows, fig_cols  = 4, 3
fig                 = createFigure(25.0, fig_rows, fig_cols)
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

# Stimulus row of figure
ax = plt.subplot2grid(grid_size, (0, 0))  
ax.imshow(stimulus_beginning_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "A", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("Stimulus at Timestep {0}".format(retina_beginning_timestep), size=title_size)
         
ax = plt.subplot2grid(grid_size, (0, 1))  
ax.imshow(stimulus_middle_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "B", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("Stimulus at Timestep {0}".format(retina_middle_timestep), size=title_size)

ax = plt.subplot2grid(grid_size, (0, 2))  
ax.imshow(stimulus_ending_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "C", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("Stimulus at Timestep {0}".format(retina_ending_timestep), size=title_size)
         
         
# Cone row of figure
ax = plt.subplot2grid(grid_size, (1, 0))  
im = ax.imshow(cone_layer_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "D", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("Cone Layer Activity at Timestep {0}".format(retina_ending_timestep), size=title_size)

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
ax = fig.add_axes([0.05, 0.25, 0.1, 0.25])
norm = matplotlib.colors.Normalize(vmin=-1.0, vmax=1.0)
cb1 = matplotlib.colorbar.ColorbarBase(ax, cmap=my_cmap,
                                   norm=norm,
                                   orientation='vertical')
                                   
ax = plt.subplot2grid(grid_size, (1, 1))  
ax.imshow(cone_location_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "E", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("Selected Cone Location", size=title_size)

ax = plt.subplot2grid(grid_size, (1, 2))  
ax.plot(range(timesteps), cone_activity)
ax.set_title("Selected Cone Activity", size=title_size)
ax.set_xlim([0, timesteps-1])
ax.set_ylim([-1.1, 1.1])
ax.set_ylabel("Activity", size=y_label_size)
ax.set_xlabel("Timesteps", size=x_label_size) 
ax.set_yticklabels(plt.yticks()[0], size=x_tick_size)
ax.set_xticklabels(plt.xticks()[0], size=y_tick_size)
plt.text(plot_label_x, plot_label_y, "F", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
         
         
# Bipolar row of figure
ax = plt.subplot2grid(grid_size, (2, 0))  
ax.imshow(bipolar_layer_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "G", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("On Bipolar Layer Activity at Timestep {0}".format(retina_ending_timestep), size=title_size)
         
ax = plt.subplot2grid(grid_size, (2, 1))  
ax.imshow(bipolar_location_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "H", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("Selected On Bipolar Location", size=title_size)

ax = plt.subplot2grid(grid_size, (2, 2))  
ax.plot(range(timesteps), bipolar_activity)
ax.set_title("Selected On Bipolar Activity", size=title_size)
ax.set_xlim([0, timesteps-1])
ax.set_ylim([-0.1, 1.1])
ax.set_ylabel("Activity", size=y_label_size)
ax.set_xlabel("Timesteps", size=x_label_size) 
ax.set_yticklabels(plt.yticks()[0], size=x_tick_size)
ax.set_xticklabels(plt.xticks()[0], size=y_tick_size)
plt.text(plot_label_x, plot_label_y, "I", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
         
         
# Starburst row of figure
ax = plt.subplot2grid(grid_size, (3, 0))  
ax.imshow(starburst_layer_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "J", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("On Starburst Cell Activity at Timestep {0}".format(retina_ending_timestep), size=title_size)
         
ax = plt.subplot2grid(grid_size, (3, 1))  
ax.imshow(starburst_location_image)
ax.axis('off')                     
plt.text(plot_label_x, plot_label_y, "K", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
ax.set_title("Selected Compartment Location", size=title_size)

ax = plt.subplot2grid(grid_size, (3, 2))
ax.plot(range(timesteps), starburst_activity)
ax.set_title("Compartment Activity", size=title_size)
ax.set_xlim([0, timesteps-1])
ax.set_ylim([-0.1, 1.1])
ax.set_ylabel("Activity", size=y_label_size)
ax.set_xlabel("Timesteps", size=x_label_size) 
ax.set_yticklabels(plt.yticks()[0], size=x_tick_size)
ax.set_xticklabels(plt.xticks()[0], size=y_tick_size)
plt.text(plot_label_x, plot_label_y, "L", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
         
         

fig.tight_layout(pad=3.0, w_pad=0.15, h_pad=0.15)
fig_path = os.path.join(retina_directory_full_path, "Layer Visualization.jpg")
fig.savefig(fig_path)  