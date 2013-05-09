from Constants import *
from random import randint



###############################################################################
# Build Retina
###############################################################################

width       = 400 * UM_TO_M
height      = 400 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S
retina      = Retina(width, height, grid_size, timestep)
                         
# Build the cone Layer
cone_distance       = 10 * UM_TO_M
cone_density        = 10000.0
cone_input_size     = 10 * UM_TO_M
retina.buildConeLayer(cone_distance, cone_density, cone_input_size)

# Build the horizontal Layer
input_strength      = 0.25
decay_rate          = 0.01
diffusion_radius    = 10 * UM_TO_M
retina.buildHorizontalLayer(input_strength, decay_rate, diffusion_radius)

# Build the bipolar layer
bipolar_distance    = 10 * UM_TO_M
bipolar_density     = 10000.0
input_field_radius  = 10 * UM_TO_M
output_field_radius = 10 * UM_TO_M
retina.buildBipolarLayer(bipolar_distance, bipolar_density, input_field_radius, 
                         output_field_radius)
                         
# Build the starburst layer
starburst_distance  = 50 * UM_TO_M
starburst_density   = 1.0 / (retina.area/retina.density_area)
average_wirelength  = 150 * UM_TO_M
step_size           = 15 * UM_TO_M
input_strength      = 1.0
decay_rate          = 0.0
diffusion_radius    = 15 * UM_TO_M
retina.buildStarburstLayer(starburst_distance, starburst_density,
                           average_wirelength, step_size,
                           input_strength, decay_rate, diffusion_radius) 

# Save the morphology
retina.saveRetina("Test")                           
                           



# Build a moving bar stimulus
framerate               = 30.0              # Fps
movie_size              = (400, 400)        # pixels
bar_orientation         = 45.0              # Degrees clockwise on circle
bar_size                = (20.0, 120.0)     # Pixels (width = size in direction of motion)
bar_speed               = 50.0              # Pixels/second
bar_movement_distance   = 500.0             # Pixels
bar_position            = (100, 100)        # Pixels
bar_color               = (0, 0, 0)         # (R,G,B)
background_color        = (255, 255, 255)   # (R,G,B)

bar_movie = RuntimeBarGenerator(framerate=framerate, movie_size=movie_size,
                                bar_orientation=bar_orientation, 
                                bar_size=bar_size, bar_speed=bar_speed, 
                                bar_movement_distance=bar_movement_distance,
                                bar_position=bar_position, bar_color=bar_color,
                                background_color=background_color)

position_on_retina  = (0.0, 0.0)        # rgu
pixel_size_in_rgu   = 1.0               # rgu
stimulus = Stimulus(position_on_retina=position_on_retina,
                    pixel_size_in_rgu=pixel_size_in_rgu, movie=bar_movie)
retina.loadStimulus(stimulus)                           


                           
retina.runModel(50*timestep)
retina.saveActivities("Test")    


loaded_retina = Retina.loadRetina("Test")
loaded_retina.loadActivities("Test")

from Visualizer import Visualizer
v = Visualizer(retina)
