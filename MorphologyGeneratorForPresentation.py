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
                         

pygame.init()
max_size = Vector2D(1000.0, 1000.0)       
width_scale = max_size.x / float(retina.grid_width)
height_scale = max_size.y / float(retina.grid_height)
scale = min(width_scale, height_scale) * 1.25  
display = pygame.display.set_mode(max_size.toIntTuple())


index = 0
for heading_deviation in [1, 15, 30]:
    for max_segment_length in [10*UM_TO_M, 30*UM_TO_M, 60*UM_TO_M]:
    
        s = StarburstMorphology(retina, average_wirelength=150,
                                heading_deviation=heading_deviation, step_size=10, max_segment_length=max_segment_length,
                                children_deviation=10, visualize_growth=False)  
                                
                                
        display.fill((0,0,0))
        s.draw(display, draw_compartments=True,new_location=max_size/2.0/scale, scale=scale, color=(255,255,255))
        pygame.image.save(display, str(index)+".jpg")
        index += 1
