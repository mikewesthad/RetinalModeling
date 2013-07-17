from Constants import *
from CreateRetina import createStarburstRetina
from CreateStimulus import createAnnulus
from Analysis import *
from time import clock

import shutil
import os



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



def run(trial_name, retina_parameters, stimulus_parameters):

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
                
        retina.saveRetina(os.path.join(trial_name, retina_name))        
            
        stimulus_index = 0
        for stimulus_combination in stimulus_combinations:
            
            
            start = clock()
            # SOMETHING STRANGE HAPPENS WHERE THE DIRECTION FLIPS...SO PASS IN OPPOSITE
            centripetal_annulus = createAnnulus("Centrifugal", *stimulus_combination)
            stimulus_name = str(stimulus_index)+"_centripetal"
            retina.loadStimulus(centripetal_annulus)  
            retina.runModelForStimulus()
            retina.saveActivities(os.path.join(trial_name, retina_name), stimulus_name) 
            retina.clearActivity()                   
            
            centrifugal_annulus = createAnnulus("Centripetal", *stimulus_combination)
            stimulus_name = str(stimulus_index)+"_centrifugal"
            retina.loadStimulus(centrifugal_annulus)  
            retina.runModelForStimulus()
            retina.saveActivities(os.path.join(trial_name, retina_name), stimulus_name) 
            retina.clearActivity()       
                       
            stimulus_index += 1                
            elapsed = clock() - start
            print "Retina '{0}' stimulated in {1} seconds".format(retina_name, elapsed)
    




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


# User controlled variables
trial_name = "Annuli_Test_Batch_6"
parameter_filename = "BatchProcessingParameters.txt"

# Create a directory to store this trial run
trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
os.mkdir(trial_path)

# Copy the parameter text file into the new directory
parameter_path = os.path.join(trial_path, trial_name+" Parameters.txt")
shutil.copy(parameter_filename, parameter_path)

# Read in the parameters
parameters = processTextParameters(parameter_filename)
retina_parameters = parameters[0:24] 
stimulus_parameters = parameters[24:]  

# Start the trial
run(trial_path, retina_parameters, stimulus_parameters)