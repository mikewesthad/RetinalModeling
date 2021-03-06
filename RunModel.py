from BarStimulus import BarStimulus
from RuntimeBarGenerator import RuntimeBarGenerator
from Retina import Retina
from Constants import *



# Build a moving bar stimulus
framerate               = 30.0              # Fps
movie_size              = (400, 400)        # Pixels
bar_orientation         = 45.0              # Degrees clockwise on circle
bar_size                = (40.0, 120.0)     # Pixels (width = size in direction of motion)
bar_speed               = 20.0              # Pixels/second
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

# Place that bar stimulus on the retina in grid units
position_on_retina  = (0.0, 0.0)
pixel_size          = 1.0
                            
bar_stimulus = BarStimulus(position_on_retina=position_on_retina, 
                           pixel_size=pixel_size, 
                           bar_movie=bar_movie)

 

# Build Retina
width       = 400 * UM_TO_M
height      = 400 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S

retina = Retina(width, height, grid_size, timestep, bar_stimulus, None)
                         
# Build the cone Layer
cone_distance       = 10 * UM_TO_M
cone_density        = 10000.0
cone_input_size     = 10 * UM_TO_M
retina.buildConeLayer(cone_distance, cone_density, cone_input_size)

# Build the horizontal Layer
input_strength      = 0.1
decay_rate          = 0.1
diffusion_radius    = 1 * UM_TO_M

retina.buildHorizontalLayer(input_strength, decay_rate, diffusion_radius)

# Build the bipolar layer
bipolar_distance    = 20 * UM_TO_M
bipolar_density     = 10000.0
input_field_radius  = 50 * UM_TO_M
output_field_radius = 10 * UM_TO_M

retina.buildBipolarLayer(bipolar_distance, bipolar_density, input_field_radius, 
                         output_field_radius)

# Run the model
duration = 0*timestep
retina.runModel(duration)


retina.saveModel("Diffuse Bipolar")

from Visualizer import Visualizer
v = Visualizer(retina)