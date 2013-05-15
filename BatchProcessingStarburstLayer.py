from Constants import *
from CreateRetina import createStarburstRetina
from CreateStimulus import createMultipleBars
from Analysis import analyzeMultipleBars, analyzeMultipleBarsInOnePage, saveMorphology
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
retina_width        = 400 * UM_TO_M
retina_height       = 400 * UM_TO_M
retina_grid_size    = 1 * UM_TO_M
retina_timestep     = 10 * MS_TO_S
retina_parameters = [retina_width, retina_height, retina_grid_size, retina_timestep]
   
# Cone Layer
cone_distance   = 10 * UM_TO_M
cone_density    = 10000.0
cone_input_size = 10 * UM_TO_M
cone_parameters = [cone_distance, cone_density, cone_input_size]

# Horizontal Layer
horizontal_input_strength   = 0.25
hoirzontal_decay_rate       = 0.01
horizontal_diffusion_radius = 1 * UM_TO_M
horizontal_parameters = [horizontal_input_strength, hoirzontal_decay_rate, horizontal_diffusion_radius]

# Bipolar layer
bipolar_distance        = 10 * UM_TO_M
bipolar_density         = 10000.0
bipolar_input_radius    = 10 * UM_TO_M
bipolar_output_radius   = 10 * UM_TO_M
bipolar_parameters = [bipolar_distance, bipolar_density, bipolar_input_radius, bipolar_output_radius]

# Build the starburst layer
starburst_distance  = 50 * UM_TO_M
starburst_density   = 10000.0
average_wirelength  = 150 * UM_TO_M
step_size           = 15 * UM_TO_M
input_strength      = 0.5
decay_rate          = 0.01
diffusion_radius    = 100 * UM_TO_M
starburst_parameters = [starburst_distance, starburst_density, average_wirelength,
                        step_size, input_strength, decay_rate, diffusion_radius]

# Bar paramters
framerate               = 30.0           
movie_width             = 400        
movie_height            = 400               
bar_width               = 100.0       # Pixels (width = size in direction of motion)
bar_height              = 400
bar_speed               = 250.0    
bar_movement_distance   = 400.0         
pixel_size_in_rgu       = 1.0                       # rgu
stimulus_parameters = [framerate, movie_width, movie_height,
                       bar_width, bar_height, bar_speed, bar_movement_distance,
                       pixel_size_in_rgu]

retina_parameters = retina_parameters + cone_parameters + horizontal_parameters + bipolar_parameters + starburst_parameters
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
    retina, retina_string = createStarburstRetina(*retina_combination)
    retina_index += 1
    
    fh = open("output.txt", "a")
    fh.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    fh.write("\n\nRetina {0}\n".format(retina_name))
    fh.write("\n{0}".format(retina_string))
    fh.close()
    
    # Build the structure to hold the results data
    layer_names     = ["Cone", "Horizontal", "Bipolar", "Starburst"]
    directions      = ["0", "90", "180", "270"]
    activities      = {}
    for name in layer_names:    
        activities[name] = {}
        for direction in directions:
            activities[name][direction] = []
                        
    stimulus_index = 0
    for stimulus_combination in stimulus_combinations:
        
        start = clock()
        
        stimuli, headings, stimulus_string = createMultipleBars(*stimulus_combination)
        
        stimulus_name = str(stimulus_index)
        fh = open("output.txt", "a")
        fh.write("\n\n--------Stimulus {0}\n\n{1}\n".format(stimulus_name, stimulus_string))
        fh.close()
        
        for i in range(len(stimuli)):
            stimulus = stimuli[i]
            heading = headings[i]
            
            retina.loadStimulus(stimulus)  
            retina.runModelForStimulus()
            retina.saveActivities(retina_name, stimulus_name+"_"+str(int(heading))) 
            stimulus_index += 1                           
            
#            analyzeMultipleBars(retina, retina_name, stimulus_name, heading)
            retina.clearActivity()       
        
        analyzeMultipleBarsInOnePage(retina, retina_name, stimulus_name, headings)
        
        elapsed = clock() - start
        print "Retina '{0}' stimulated in {1} seconds".format(retina_name, elapsed)

    