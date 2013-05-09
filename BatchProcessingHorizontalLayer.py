from Constants import *
from CreateRetina import createBipolarRetina
from CreateStimulus import createBarStimulus
from time import clock



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
    while not(isinstance(parameter_options, (np.ndarray, list, tuple))):
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


###############################################################################
# Retina Parameters
###############################################################################

# General retina
retina_width        = 200 * UM_TO_M
retina_height       = 200 * UM_TO_M
retina_grid_size    = 1 * UM_TO_M
retina_timestep     = 10 * MS_TO_S
retina_parameters = [retina_width, retina_height, retina_grid_size, retina_timestep]
   
# Cone Layer
cone_distance   = 10 * UM_TO_M
cone_density    = 100000.0
cone_input_size = 10 * UM_TO_M
cone_parameters = [cone_distance, cone_density, cone_input_size]

# Horizontal Layer
horizontal_input_strength   = [.3, .9]
hoirzontal_decay_rate       = [0.01, 0.1]
horizontal_diffusion_radius = np.arange(10, 40, 10) * UM_TO_M
horizontal_parameters = [horizontal_input_strength, hoirzontal_decay_rate, horizontal_diffusion_radius]

# Bipolar layer
bipolar_distance        = 10 * UM_TO_M
bipolar_density         = 100000.0
bipolar_input_radius    = 10 * UM_TO_M
bipolar_parameters = [bipolar_distance, bipolar_density, bipolar_input_radius]

# Bar paramters
framerate               = 30.0           
movie_width             = 200        
movie_height            = 200               
bar_orientation         = 45.0                      # Degrees clockwise on circle
bar_width               = (10.0, 30.0, 60.0)        # Pixels (width = size in direction of motion)
bar_height              = (10.0, 30.0, 60.0)
bar_speed               = (100.0, 300.0, 600.0)       
bar_movement_distance   = 200.0         
pixel_size_in_rgu       = 1.0                       # rgu
stimulus_parameters = [framerate, movie_width, movie_height, bar_orientation,
                       bar_width, bar_height, bar_speed, bar_movement_distance,
                       pixel_size_in_rgu]


retina_parameters = retina_parameters + cone_parameters + horizontal_parameters + bipolar_parameters
retina_combinations = generateCombinations(retina_parameters, 0, [], [])
stimulus_combinations = generateCombinations(stimulus_parameters, 0, [], [])

print "Retina Combinations", len(retina_combinations)
print "Stimulus Combinations", len(stimulus_combinations)
print "Combined Combinations", len(retina_combinations) * len(stimulus_combinations)

fh = open("output.txt", "w")
fh.close()
                      
retina_index = 0
for retina_combination in retina_combinations:
    
    retina_name = str(retina_index)
    retina_combination.append(retina_name)    
    retina, retina_string = createBipolarRetina(*retina_combination)
    retina_index += 1
    
    
    fh = open("output.txt", "a")
    fh.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    fh.write("\n\nRetina {0}\n".format(retina_name))
    fh.write("\n{0}".format(retina_string))
    fh.close()
    
    stimulus_index = 0
    for stimulus_combination in stimulus_combinations:
        
        start = clock()
        
        stimulus, stimulus_string = createBarStimulus(*stimulus_combination)
        stimulus_name = str(stimulus_index)
        retina.loadStimulus(stimulus)  
        retina.runModel(1000 * MS_TO_S)
        retina.saveActivities(retina_name, stimulus_name) 
        stimulus_index += 1                           
        
        
        fh = open("output.txt", "a")
        fh.write("\n\n--------Stimulus {0}\n\n{1}".format(stimulus_name, stimulus_string))
        
        results_string = ""
        cone_max, cone_min = np.max(retina.cone_activities), np.min(retina.cone_activities)
        results_string += "\n\tCone Bounds\t\t({0:.3f}, {1:.3f})".format(cone_min, cone_max)
        horizontal_max, horizontal_min = np.max(retina.horizontal_activities), np.min(retina.horizontal_activities)
        results_string += "\n\tHorizontal Bounds\t({0:.3f}, {1:.3f})".format(horizontal_min, horizontal_max)
        bipolar_max, bipolar_min = np.max(retina.on_bipolar_activities), np.min(retina.on_bipolar_activities)
        results_string += "\n\tBipolar Bounds\t\t({0:.3f}, {1:.3f})".format(bipolar_min, bipolar_max)
        
        fh.write("{0}\n\n".format(results_string))
        fh.close()
        
        retina.clearActivity()
        
        elapsed = clock() - start
        print "Retina '{0}' stimulated in {1} seconds".format(retina_name, elapsed)

    