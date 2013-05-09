from Constants import *



###############################################################################
# Combination Generator
#   Given a list of values where the each value is either a:
#       A single value - numeric, boolean, string
#       A collection of values - list, tuple or numpy array
#   This function returns a list of all possible combinations
###############################################################################

def generateCombinations(physical_parameters, current_parameter_index=0, 
                         current_parameter_combination=[], combinations=[]):
    
    # Base case - no more parameters to check
    if current_parameter_index >= len(physical_parameters):
        combinations.append(current_parameter_combination)
        return combinations
    
    # Get the next collection of parameter values
    #   If a paramter is a single value, then add it to the current combination
    parameter_options = physical_parameters[current_parameter_index]
    while not(isinstance(parameter_options, (np.ndarray, list, tuple))):
        current_parameter_combination.append(parameter_options) 
        current_parameter_index += 1
        if current_parameter_index >= len(physical_parameters): break
        parameter_options = physical_parameters[current_parameter_index]
    
    # A secondary base case - all available parameters were exhausted by the
    # above loop and the last parameter was a single value
    if current_parameter_index >= len(physical_parameters):
        combinations.append(current_parameter_combination)
        return combinations
    
    # Iterate through all the values in the current collection of parameter values
    for option in parameter_options:
         combinations = generateCombinations(physical_parameters, current_parameter_index+1,
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
horizontal_input_strength   = [.3, .6, .9]
hoirzontal_decay_rate       = [0.01, 0.1]
horizontal_diffusion_radius = np.arange(5, 45, 10) * UM_TO_M
horizontal_parameters = [horizontal_input_strength, hoirzontal_decay_rate, horizontal_diffusion_radius]

# Bipolar layer
bipolar_distance        = 10 * UM_TO_M
bipolar_density         = 10000.0
bipolar_input_radius    = 10 * UM_TO_M
bipolar_output_radius   = 10 * UM_TO_M
bipolar_parameters = [bipolar_distance, bipolar_density, bipolar_input_radius, bipolar_output_radius]

# Starburst layer
starburst_distance              = 50 * UM_TO_M
starburst_density               = None
starburst_average_wirelength    = 150 * UM_TO_M
starburst_step_size             = 15
starburst_input_strength        = [.3, .6, .9]
starburst_decay_rate            = [0.01, 0.1]
starburst_diffusion_radius      = np.arange(5, 45, 10) * UM_TO_M
starburst_parameters = [starburst_distance, starburst_density, starburst_average_wirelength, 
                        starburst_step_size, starburst_input_strength, starburst_decay_rate,
                        starburst_diffusion_radius]


physical_parameters = retina_parameters + cone_parameters + \
                      horizontal_parameters + bipolar_parameters + \
                      starburst_parameters
                      
number_combinations = 1
for parameter in physical_parameters:
    if isinstance(parameter, np.ndarray):
        number_combinations *= parameter.shape[0]
    elif isinstance(parameter, (list, tuple)):
        number_combinations *= len(parameter)
print number_combinations
    
                      
generateCombinations(physical_parameters)
        

#all_conditions_run = False
#while not(all_conditions_run):
#    
#    # Get the current set of parameters for this run
#    physical_parameters_combination = []
#    for parameter_number in range(number_physical_parameters):
#        parameter = physical_parameters[parameter_number]
#        if isinstance(parameter, np.ndarray):
#            index = current_indices_in_physical_parameters[parameter_number]
#            physical_parameters_combination.append(parameter[index])
#        else:
#            physical_parameters_combination.append(parameter)
#    
#    # Increment one of the parameters to generate a new combination 
#    parameter       = physical_parameters[current_parameter_to_increment]
#    parameter_index = current_indices_in_physical_parameters[current_parameter_to_increment]
#    parameter_index += 1
#    if isinstance(parameter, np.ndarray): parameter_length = size(parameter)
#    else: parameter_length = 0
#    
#    while parameter_index >= parameter_length:
#        current_parameter_to_increment += 1
#        
#        parameter = physical_parameters[parameter_increment_index] 
#        if isinstance(parameter, np.ndarray): parameter_length = size(parameter)
#        else: parameter_length = 0
#    
#    # Check if you've all ready processesed all combinations
#    if parmater_increment_index == number_physical_parameters:    
#        all_conditions_run = True
#    
#print current_physical_parameters
#            
            
    