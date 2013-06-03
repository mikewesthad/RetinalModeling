from Constants import *
from random import randint


###############################################################################
# Build Retina
###############################################################################

width       = 400 * UM_TO_M
height      = 400 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 10 * MS_TO_S
retina      = Retina(width, height, grid_size, timestep)
                         
# Build the cone Layer
cone_distance       = 10 * UM_TO_M
cone_density        = 10000.0
cone_input_size     = 10 * UM_TO_M
retina.buildConeLayer(cone_distance, cone_density, cone_input_size)

# Build the horizontal Layer
input_strength      = 0.25
decay_rate          = 0.01
diffusion_radius    = 1 * UM_TO_M
retina.buildHorizontalLayer(input_strength, decay_rate, diffusion_radius)

# Build the bipolar layer
bipolar_distance    = 10 * UM_TO_M
bipolar_density     = 10000.0
input_field_radius  = 10 * UM_TO_M
output_field_radius = 10 * UM_TO_M
retina.buildBipolarLayer(bipolar_distance, bipolar_density, input_field_radius, 
                         output_field_radius, build_on_and_off=False)
                         
# Build the starburst layer
starburst_distance  = 50 * UM_TO_M
starburst_density   = 1000.0
average_wirelength  = 150 * UM_TO_M
step_size           = 15 * UM_TO_M
input_strength      = 0.5
decay_rate          = 0.0
diffusion           = ("Flat", [10 * UM_TO_M / grid_size])
retina.buildStarburstLayer(starburst_distance, starburst_density,
                           average_wirelength, step_size,
                           input_strength, decay_rate, diffusion[0], diffusion[1],
                           build_on_and_off=False)

# Build a moving bar stimulus
framerate               = 60.0              # Fps
movie_size              = (400, 400)        # pixels
flash_shape             = "Circle"
flash_size              = (30.0)  
flash_position          = (200, 200)        # Pixels
flash_color             = (255, 255, 255)   # (R,G,B)
background_color        = (0, 0, 0)         # (R,G,B)
flash_duration          = 4000*MS_TO_S
delay_before_flash      = 0*MS_TO_S
delay_after_flash       = 4000*MS_TO_S

bar_movie = RuntimeFlashGenerator(framerate=framerate, movie_size=movie_size,
                                  flash_shape=flash_shape, 
                                  flash_size=flash_size, flash_position=flash_position, 
                                  flash_duration=flash_duration,
                                  delay_before_flash=delay_before_flash,
                                  delay_after_flash=delay_after_flash,  
                                  background_color=background_color, flash_color=flash_color,
                                  minimize=False)

position_on_retina  = (0.0, 0.0)        # rgu
pixel_size_in_rgu   = 1.0               # rgu
stimulus = Stimulus(position_on_retina=position_on_retina,
                    pixel_size_in_rgu=pixel_size_in_rgu, movie=bar_movie)
retina.loadStimulus(stimulus)                           

retina.runModelForStimulus()

retina_name = "Test"
runtime_name = "0"
retina.saveRetina(retina_name)    
retina.saveActivities(retina_name, runtime_name)  

#
from Visualizer import Visualizer
v = Visualizer(retina)
