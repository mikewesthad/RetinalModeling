from Constants import *

retina_name = "12 Direction - 100 FPS Remove Stutter From Floating Point Inaccuracies Increased Diffusion Radius (Best DS 5-22-13)"
stimulus_name = "0_0"
retina = Retina.loadRetina(retina_name)

pygame.init()
max_size = Vector2D(1000.0, 1000.0)       
width_scale = max_size.x / float(retina.grid_width)
height_scale = max_size.y / float(retina.grid_height)
scale = min(width_scale, height_scale)   
display = pygame.display.set_mode(max_size.toIntTuple())

display.fill(GOLDFISH[0])
starburst = retina.on_starburst_layer.neurons[0]
starburst.draw(display, draw_compartments=True, scale=scale)    
pygame.image.save(display, "Colored Starburst.jpg")

display.fill((0,0,0))
starburst = retina.on_starburst_layer.neurons[0]
starburst.draw(display, color=(255,255,255), draw_compartments=True, scale=scale)    
pygame.image.save(display, "White Starburst.jpg")

display.fill((0,0,0))
starburst = retina.on_starburst_layer.neurons[0]
starburst.draw(display, color=(255,255,255), draw_compartments=True, scale=scale)    
starburst.morphology.location = max_size/scale/2.0
for compartment in starburst.compartments:
    if compartment.neurotransmitters_output_weights != {}:
        compartment.draw(display, color=(255,0,0), scale=scale)
pygame.image.save(display, "White Starburst Outputs.jpg")


display.fill((0,0,0))
starburst = retina.on_starburst_layer.neurons[0]   
starburst.morphology.location = Vector2D()
starburst.draw(display, color=(255,255,255), draw_compartments=True, scale=scale)    
starburst.morphology.location = max_size/scale/2.0
compartment = starburst.compartments[-2]
has_reached_soma = False
while not(has_reached_soma):
    compartment.draw(display, color=(255,0,0), scale=scale)
    compartment = compartment.proximal_neighbors[0]
    if compartment in starburst.morphology.master_compartments:
        compartment.draw(display, color=(255,0,0), scale=scale)
        has_reached_soma = True
pygame.image.save(display, "White Starburst Dendrite Path.jpg")

            
            
#retina.loadActivities(retina_name, stimulus_name)

#from Analysis import analyzeMultipleBars
#analyzeMultipleBars(retina)

#v = Visualizer(retina)