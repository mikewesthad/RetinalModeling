from Constants import *
from time import clock

def createBipolarRetina(width, height, grid_size, timestep,
                        cone_distance, cone_density, cone_input_size,
                        horizontal_input_strength, horizontal_decay, horizontal_diffusion_radius,
                        bipolar_distance, bipolar_density, bipolar_input_radius, 
                        retina_name):
                            
    start = clock()                            
    
    # Construct the layers of the retina
    retina = Retina(width, height, grid_size, timestep)
    retina.buildConeLayer(cone_distance, cone_density, cone_input_size, verbose=False)
    retina.buildHorizontalLayer(horizontal_input_strength, horizontal_decay, 
                                horizontal_diffusion_radius, verbose=False)
    retina.buildBipolarLayer(bipolar_distance, bipolar_density, bipolar_input_radius, 
                             build_on_and_off=False, verbose=False)
    
    # Save the morphology
    retina.saveRetina(retina_name)    
    
    # Create a string representation of the retina
    retina_string = ""
    retina_string += "Retina Width (um)\t\t\t{0:.3f}\n".format(width * M_TO_UM)
    retina_string += "Retina Grid Size (um)\t\t\t{0:.3f}\n".format(grid_size * M_TO_UM)
    retina_string += "Retina Timestep (ms)\t\t\t{0:.3f}\n".format(timestep * S_TO_MS)
    
    retina_string += "Cone Distance (um)\t\t\t{0:.3f}\n".format(cone_distance * M_TO_UM)
    retina_string += "Cone Density\t\t\t\t{0:.3f}\n".format(cone_density)
    retina_string += "Cone Input Size (um)\t\t\t{0:.3f}\n".format(cone_input_size * M_TO_UM)
    
    retina_string += "Horizontal Input Strength (um)\t\t{0:.3f}\n".format(horizontal_input_strength)
    retina_string += "Horizontal Decay\t\t\t{0:.3f}\n".format(horizontal_decay)
    retina_string += "Horizontal Diffusion Radius (um)\t{0:.3f}\n".format(horizontal_diffusion_radius * M_TO_UM)
    
    retina_string += "Bipolar Distance (um)\t\t\t{0:.3f}\n".format(bipolar_distance * M_TO_UM)
    retina_string += "Bipolar Density\t\t\t\t{0:.3f}\n".format(bipolar_density)
    retina_string += "Bipolar Input Size (um)\t\t\t{0:.3f}\n".format(bipolar_input_radius * M_TO_UM)
    
    
    elapsed = clock() - start
    print "Retina '{0}' generated in {1} seconds".format(retina_name, elapsed)
    
    return retina, retina_string
    
    
    
    
def createStarburstRetina(width, height, grid_size, timestep,
                          cone_distance, cone_density, cone_input_size,
                          horizontal_input_strength, horizontal_decay, horizontal_diffusion_radius,
                          bipolar_distance, bipolar_density, bipolar_input_radius, bipolar_output_radius,
                          starburst_distance, starburst_density, starburst_wirelength,
                          starburst_step_size, starburst_decay_rate, starburst_diffusion, 
                          heading_deviation, children_deviation, max_segment_length,
                          conductance_factor, retina_name):
    a = [width, height, grid_size, timestep,
          cone_distance, cone_density, cone_input_size,
          horizontal_input_strength, horizontal_decay, horizontal_diffusion_radius,
          bipolar_distance, bipolar_density, bipolar_input_radius, bipolar_output_radius,
          starburst_distance, starburst_density, starburst_wirelength,
          starburst_step_size, starburst_decay_rate, starburst_diffusion, 
          heading_deviation, children_deviation, max_segment_length,
          conductance_factor, retina_name]
    for i in a: print i                       
    
    
    start = clock()                            
    
    diffusion_method, diffusion_parameters = starburst_diffusion
    
    # Construct the layers of the retina
    retina = Retina(width, height, grid_size, timestep)
    retina.buildConeLayer(cone_distance, cone_density, cone_input_size, verbose=False)
    retina.buildHorizontalLayer(horizontal_input_strength, horizontal_decay, 
                                horizontal_diffusion_radius, verbose=False)
    retina.buildBipolarLayer(bipolar_distance, bipolar_density, bipolar_input_radius,
                             bipolar_output_radius, build_on_and_off=False, verbose=False)
    retina.buildStarburstLayer(starburst_distance, starburst_density,
                               starburst_wirelength, starburst_step_size, starburst_decay_rate, 
                               diffusion_method, diffusion_parameters, heading_deviation, 
                               children_deviation, max_segment_length, 
                               conductance_factor, build_on_and_off=False, 
                               verbose=False) 
    
    elapsed = clock() - start
    print "Retina '{0}' generated in {1} seconds".format(retina_name, elapsed)
    
    return retina