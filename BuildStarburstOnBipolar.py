from Constants import *
from random import randint



# Build a moving bar stimulus
framerate               = 30.0              # Fps
movie_size              = (400, 400)        # Pixels
bar_orientation         = 45.0              # Degrees clockwise on circle
bar_size                = (20.0, 120.0)     # Pixels (width = size in direction of motion)
bar_speed               = 1.0              # Pixels/second
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
                         
## Build the starburst layer
#starburst_distance  = 50 * UM_TO_M
#starburst_density   = 1.0 / (retina.area/retina.density_area)
#average_wirelength  = 150 * UM_TO_M
#step_size           = 15 * UM_TO_M
#input_strength      = 1.0
#decay_rate          = 0.0
#diffusion_radius    = 15 * UM_TO_M
#
#retina.buildStarburstLayer(starburst_distance, starburst_density,
#                           average_wirelength, step_size,
#                           input_strength, decay_rate, diffusion_radius) 
    
retina.runModel(20*timestep)

from NewVisualizer import Visualizer
v = Visualizer(retina)

                        
## Build a display
#palette     = OCEAN_FIVE
#background  = palette[0]
#screen_size = Vector2D(800, 800)
#display     = pygame.display.set_mode(screen_size.toIntTuple()) 
#    
#s = retina.on_starburst_layer.neurons[0]
#s.drawInputs(display, 0, scale=2.0)
#
#running = True
#next_frame = True
#while running:
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False  
#        if event.type == KEYDOWN:
#            next_frame = True
#            
#    if next_frame:
#        scale = 2.0
#        display.fill(background)
#        retina.on_bipolar_layer.draw(display, scale=2.0)
#        for i in s.morphology.compartments:
#            i.color = (0,0,0)
#        s.draw(display, draw_compartments=True, scale=2.0)
#        s.drawInputs(display, randint(0, len(s.morphology.compartments)-1), scale=2.0)
#        next_frame = False
#        
#    
#    pygame.display.update()

                     
    
#compartments = retina.on_bipolar_layer.compartments
#number_compartments = len(compartments)
#time = 0
#running = True
#next_frame = True
#while running:
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            running = False
#        if event.type == KEYDOWN:
#            next_frame = True
#    if next_frame:    
#        retina.runModel(timestep)
#        display.fill((0,0,0))
#        time+=1
#        print "Timestep\t{0}\n".format(time)
#        for i in range(number_compartments):
#            compartment         = compartments[i]
#            activity            = compartment.potentials[0]
#            percent             = (activity+1.0)/2.0
#            new_color           = (int(percent*255),int(percent*255),int(percent*255))
#            compartment.color   = new_color
#        
#        retina.on_bipolar_layer.draw(display, scale=2.0)  
#        next_frame = False
#        
#     
#    pygame.display.update()