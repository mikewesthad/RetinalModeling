from Constants import *
from CreateRetina import createStarburstRetina
from CreateStimulus import createMultipleBars
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


def generatePDF(retina_name):
    cone_path       = os.path.join("Saved Retinas", retina_name, "Cone.jpg")
    bipolar_path    = os.path.join("Saved Retinas", retina_name, "Horizontal.jpg")
    horizontal_path = os.path.join("Saved Retinas", retina_name, "Bipolar.jpg")
    starburst_path  = os.path.join("Saved Retinas", retina_name, "Starburst.jpg")
    output_path = os.path.join("Saved Retinas", retina_name, "Parameters.pdf")     
    
    lines = open("BatchPRocessingStarburstLayerV2.py").readlines()
    
    # A4 is 210mm by 297mm
    w, h = 210, 297
    
    pdf = FPDF(orientation = 'P', unit = 'mm', format = 'A4')
    pdf.add_page()
    
    # Image is draw as a square
    image_size  = w/3.0
    offset      = (w/2.0 - image_size) / 2.0
    pdf.image(cone_path, offset, 0, w=image_size, h=image_size)
    pdf.image(bipolar_path, w/2.0+offset, 0, w=image_size, h=image_size)
    pdf.image(horizontal_path, offset,  image_size, w=image_size, h=image_size)
    pdf.image(starburst_path, w/2.0+offset, image_size, w=image_size, h=image_size)
    
    # Default margin is 10cm
    pdf.set_xy(10, 2*image_size)
    pdf.set_font('Arial', size=10)
    start_printing = False 
    left_column = True
    for line in lines:
        line = line.rstrip()
        if not(left_column):
            pdf.set_x(w/2.0)
        if line == "'print_stop'":
            start_printing = False        
        if start_printing:
            pdf.cell(0, 5, line, 0, 1)
        if line == "'print_start'":
            start_printing = True
        if pdf.get_y() > h - 30:
            left_column = False
            pdf.set_xy(w/2.0, 2*image_size)
    pdf.output(output_path, 'F')
    return output_path

def run(retina_parameters, runtime_parameters, stimulus_parameters, parameter_name, parameter_settings):

    # Tuples consitute a single item
    retina_parameters = retina_parameters + cone_parameters + horizontal_parameters + bipolar_parameters + starburst_parameters
    retina_combinations = generateCombinations(retina_parameters, 0, [], [])
    runtime_combinations = generateCombinations(runtime_starburst_parameters, 0, [], [])
    stimulus_combinations = generateCombinations(stimulus_parameters, 0, [], [])
    
    print "Retina Combinations", len(retina_combinations)
    print "Runtime Combinations", len(runtime_combinations)
    print "Stimulus Combinations", len(stimulus_combinations)
    print "Combined Combinations", len(retina_combinations) * len(runtime_combinations) * len(stimulus_combinations)
                     
    retina_index = 0
    for retina_combination in retina_combinations:
        
        retina_name = str(retina_index)
        retina_combination.append(retina_name)    
        retina = createStarburstRetina(*retina_combination)
        retina_index += 1
        
        proximal, intermediate, distal = selectStarburstCompartmentsAlongDendrite(retina, 0)
          
        weight_paths = []
        runtime_index = 0
        for runtime_combination in runtime_combinations: 
            
            runtime_name = str(runtime_index)
            retina.on_starburst_layer.changeInputStrength(runtime_combination[0])
            retina.on_starburst_layer.changeDecayRate(runtime_combination[1])
            retina.on_starburst_layer.changeDiffusion(runtime_combination[2][0], runtime_combination[2][1])
            runtime_index += 1
            
            retina.stimulus = None
            retina.saveParameters(retina_name, runtime_name)
                
            path = generateHistogramPlotsOfWeights(retina, retina_name, runtime_name, proximal, intermediate, distal)   
            weight_paths.append(path)
            
            stimulus_index = 0
            for stimulus_combination in stimulus_combinations:
                
                start = clock()
                
                stimuli, headings, stimulus_string = createMultipleBars(*stimulus_combination)
                stimulus_name = str(stimulus_index)        
                for stimulus, heading in zip(stimuli, headings):
                    retina.loadStimulus(stimulus)  
                    retina.runModelForStimulus()
                    trial_name = runtime_name+"_"+stimulus_name+"_"+str(int(heading))
                    retina.saveActivities(retina_name, trial_name) 
                    stimulus_index += 1                           
                    retina.clearActivity()       
                
    #            analyzeMultipleBarsInOnePage(retina, retina_name, stimulus_name, headings)
                
                elapsed = clock() - start
                print "Retina '{0}' stimulated in {1} seconds".format(retina_name, elapsed)
        
        
        saveMorphology(retina, retina_name, proximal, intermediate, distal)
        
        paths = []
        p = generatePDF(retina_name)
        paths.append(p)
        paths.extend(weight_paths)
        ps = analyzeEffectsOfRuntimeParameter(retina, retina_name, parameter_name, parameter_settings, headings, stimulus_name)
        paths.extend(ps)        
        
        retina_output_path = os.path.join("Saved Retinas", retina_name, parameter_name+"_Results.pdf")
        mergePDFs(retina_output_path, paths)


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
diffusion           = [("Flat", [30 * UM_TO_M / retina_grid_size]),
                       ("Linear", [70 * UM_TO_M / retina_grid_size, 10 * UM_TO_M / retina_grid_size]),
                       ("Linear", [150 * UM_TO_M / retina_grid_size, 10 * UM_TO_M / retina_grid_size]),
                       ("Linear", [70 * UM_TO_M / retina_grid_size, 1 * UM_TO_M / retina_grid_size])]   

# Bar paramters
framerate               = 60.0           
movie_width             = 400        
movie_height            = 400               
bar_width               = 50.0
bar_height              = 400
bar_speed               = 2000.0    
bar_movement_distance   = 400.0         
pixel_size_in_rgu       = 1.0
'print_stop'    

stimulus_parameters = [framerate, movie_width, movie_height,
                       bar_width, bar_height, bar_speed, bar_movement_distance,
                       pixel_size_in_rgu]


# Put parameters into lists
retina_parameters = [retina_width, retina_height, retina_grid_size, retina_timestep]
cone_parameters = [cone_distance, cone_density, cone_input_size]
horizontal_parameters = [horizontal_input_strength, hoirzontal_decay_rate, horizontal_diffusion_radius]
bipolar_parameters = [bipolar_distance, bipolar_density, bipolar_input_radius, bipolar_output_radius]
starburst_parameters = [starburst_distance, starburst_density, average_wirelength, step_size]
runtime_starburst_parameters = [input_strength, decay_rate, diffusion]

# Set some default values in starburst parameters for the runtime parameters (so that the initial build retina will work)
for parameter in runtime_starburst_parameters:
    if isinstance(parameter, (list, np.ndarray)): 
        starburst_parameters.append(parameter[0])
    else:
        starburst_parameters.append(parameter)


run(retina_parameters, runtime_starburst_parameters, stimulus_parameters, "Diffusion", diffusion)