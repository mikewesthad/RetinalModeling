from Constants import *
from CreateRetina import createStarburstRetina
from CreateStimulus import createManyBars
from Analysis import *
from time import clock
from fpdf import FPDF



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


def run(retina_parameters, stimulus_parameters):

    retina_combinations = generateCombinations(retina_parameters, 0, [], [])
    stimulus_combinations = generateCombinations(stimulus_parameters, 0, [], [])
    
    print "Retina Combinations", len(retina_combinations)
    print "Stimulus Combinations", len(stimulus_combinations)
    print "Combined Combinations", len(retina_combinations) * len(stimulus_combinations)
                     
    retina_index = 0
    for retina_combination in retina_combinations:
        
        retina_name = str(retina_index)
        retina_combination.append(retina_name)    
        retina = createStarburstRetina(*retina_combination)
        retina_index += 1
            
        stimulus_index = 0
        for stimulus_combination in stimulus_combinations:
            
            
            stimuli, headings = createManyBars(*stimulus_combination)
            stimulus_name = str(stimulus_index)        
            for stimulus, heading in zip(stimuli, headings):
                
                start = clock()
                
                retina.loadStimulus(stimulus)  
                retina.runModelForStimulus()
                trial_name = stimulus_name+"_"+str(int(heading))
                retina.saveActivities(retina_name, trial_name) 
                stimulus_index += 1                           
                retina.clearActivity()       
            
                elapsed = clock() - start
                print "Retina '{0}' stimulated in {1} seconds".format(retina_name, elapsed)
        

###############################################################################
# Retina Parameters
###############################################################################
'print_start'
# General retina
retina_width        = 400 * UM_TO_M
retina_height       = 400 * UM_TO_M
retina_grid_size    = 1 * UM_TO_M
retina_timestep     = 10 * MS_TO_S
   
# Cone Layer
cone_distance   = 10 * UM_TO_M
cone_density    = 10000.0
cone_input_size = 10 * UM_TO_M

# Horizontal Layer
horizontal_input_strength   = 0.25
hoirzontal_decay_rate       = 0.01
horizontal_diffusion_radius = 1 * UM_TO_M

# Bipolar layer
bipolar_distance        = 10 * UM_TO_M
bipolar_density         = 10000.0
bipolar_input_radius    = 10 * UM_TO_M
bipolar_output_radius   = 10 * UM_TO_M

# Build the starburst layer
starburst_distance  = 50 * UM_TO_M
starburst_density   = 1000.0
average_wirelength  = 150 * UM_TO_M
step_size           = 15 * UM_TO_M
decay_rate          = 0.2
input_strength      = 0.5
diffusion           = [("Flat", [20 * UM_TO_M / retina_grid_size]),
                       ("Flat", [40 * UM_TO_M / retina_grid_size]),
                       ("Flat", [60 * UM_TO_M / retina_grid_size])]

# Bar paramters
bars                    = 12
framerate               = 100.0           
movie_width             = 400        
movie_height            = 400               
bar_width               = [50.0, 100.0, 200.0]
bar_height              = 400
bar_speed               = [1000.0, 2000.0]    
bar_movement_distance   = 1000.0         
pixel_size_in_rgu       = 1.0
'print_stop'    

stimulus_parameters = [bars, framerate, movie_width, movie_height,
                       bar_width, bar_height, bar_speed, bar_movement_distance,
                       pixel_size_in_rgu]


# Put parameters into lists
retina_parameters = [retina_width, retina_height, retina_grid_size, retina_timestep]
cone_parameters = [cone_distance, cone_density, cone_input_size]
horizontal_parameters = [horizontal_input_strength, hoirzontal_decay_rate, horizontal_diffusion_radius]
bipolar_parameters = [bipolar_distance, bipolar_density, bipolar_input_radius, bipolar_output_radius]
starburst_parameters = [starburst_distance, starburst_density, average_wirelength, step_size, input_strength, decay_rate, diffusion]
retina_parameters = retina_parameters + cone_parameters + horizontal_parameters + bipolar_parameters + starburst_parameters

run(retina_parameters, stimulus_parameters)