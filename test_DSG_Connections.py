# Test DSG inputs
# jfarina
# 5/2/2013

from Constants import *

#Build a display
background  = (255, 255, 255)
screen_size = Vector2D(600,600)
display     = pygame.display.set_mode(screen_size.toIntTuple())

#Build a retina
width       = 600 * UM_TO_M
height      = 600 * UM_TO_M
grid_size   = 1 * UM_TO_M
timestep    = 100 * MS_TO_S
retina      = Retina(width, height, grid_size, display)

#Build starburst morphologies
scale = 1.0
screen_mid = screen_size/(2.0 * scale)
screen_third = screen_size/(3.0 * scale)

starburst_morphology1 = StarburstMorphology(retina,
                                            visualize_growth=True,
                                            color_palette=REDS,
                                            display=display,
                                            draw_location=screen_third,
                                            scale=scale)
                                           
starburst_morphology2 = StarburstMorphology(retina,
                                            visualize_growth=True,
                                            color_palette=BLUES,
                                            display=display,
                                            draw_location=2*screen_third,
                                            scale=scale)

#Instantiate layers
on_sac_layer = StarburstLayer(retina, 
                            ON, #on_off_type
                            0, #layer_depth
                            0, #history_size
                            1, #input delay
                            width/2, #nearest_neighbor_distance
                            1/(retina.area/retina.density_area)) #min_req_density
off_sac_layer = StarburstLayer(retina, 
                            OFF, #on_off_type
                            0, #layer_depth
                            0, #history_size
                            1, #input delay
                            width/2, #nearest_neighbor_distance
                            1/(retina.area/retina.density_area)) #min_req_density
dsg_layer     = StarburstLayer(retina, 
                            None, #on_off_type
                            0, #layer_depth
                            0, #history_size
                            1, #input delay
                            width/2, #nearest_neighbor_distance
                            1/(retina.area/retina.density_area)) #min_req_density                                                                                                                       


#Build unique starburst cells using above morphologies
starburst1 = Starburst(on_sac_layer,
                       starburst_morphology1, 
                       screen_third, 
                       ON)
starburst2 = Starburst(off_sac_layer, 
                       starburst_morphology2,
                       2*screen_third,
                       OFF)                    
SACs = [starburst1, starburst2]

for sac in SACs:
    sac.registerWithRetina()

for sac in SACs:
    sac.establishInputs()

for i in range(len(SACs)):
    SACs[i].location = (i+1)*screen_third
                       
#Build a unique DSG using the above dendritic (starburst) morphologies
dsg1 = DSG(dsg_layer, starburst_morphology1, starburst_morphology2, screen_mid, RIGHT)

dsg1.establishInputs()



#Interactive drawing
#switch between views with d/c/p; change scale with left/right
running             = True
draw_segments       = True
draw_compartments   = False
draw_points         = False
while running:
    display.fill(background)
    for event in pygame.event.get():
        if event.type ==QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_d:
                draw_segments       = True
                draw_compartments   = False
                draw_points         = False
            if event.key == K_c:
                draw_segments       = False
                draw_compartments   = True
                draw_points         = False
            if event.key == K_p:
                draw_segments       = False
                draw_compartments   = False
                draw_points         = True
            if event.key == K_LEFT:
                scale /= 1.5
            if event.key == K_RIGHT:
                scale *= 1.5
    screen_third = screen_size/(3.0 * scale)
    for i in range(len(SACs)):       
        SACs[i].draw(display, 
                    scale = scale,
                    draw_segments = draw_segments,
                    draw_compartments = draw_compartments,
                    draw_points = draw_points)
    dsg1.draw(display, 
            scale = scale,
            draw_segments = draw_segments,
            draw_compartments = draw_compartments,
            draw_points = draw_points)
    ON_inputs = dsg1.ON_arbor.compartment_inputs
    index = random.randint(0, len(ON_inputs)-1)
    print "Current DSG compartment index =", index
    inputs_to_one_comp = ON_inputs[index]
    receiving_comp = dsg1.ON_arbor.morphology.compartments[index]
    print "Current DSG compartment is", receiving_comp
    dot_loc = (receiving_comp.centroid + dsg1.location).toIntTuple()    
    print receiving_comp.centroid.toIntTuple()
    print dsg1.location.toIntTuple()    
    print "at location", dot_loc
    pygame.draw.circle(display,
                GREEN,
                dot_loc,
                5,
                0)
    receiving_comp.draw(display, GREEN)
    print "ON inputs", ON_inputs[index]
    for neuro_comp_freq in ON_inputs[index]: #for all ON inputs to one dsg compartment
        print("neuro_comp_freq", neuro_comp_freq)
        input_comp = neuro_comp_freq[0][1]
        input_neuron = neuro_comp_freq[0][0]
        start_abs = input_neuron.location
        stop_rel = input_comp.centroid        
        print("at location", (start_abs + stop_rel).toIntTuple())        
        pygame.draw.line(display,                       #surface
                  GREEN,                                #color 
                  start_abs.toIntTuple(),                 #start
                  (start_abs + stop_rel).toIntTuple(),  #stop
                  5)   

    OFF_inputs = dsg1.OFF_arbor.compartment_inputs
    index = random.randint(0, len(OFF_inputs)-1)
    print "Current DSG compartment index =", index
    inputs_to_one_comp = OFF_inputs[index]
    receiving_comp = dsg1.OFF_arbor.morphology.compartments[index]
    print "Current DSG compartment is", receiving_comp
    dot_loc = (receiving_comp.centroid + dsg1.location).toIntTuple()    
    print receiving_comp.centroid.toIntTuple()
    print dsg1.location.toIntTuple()    
    print "at location", dot_loc
    pygame.draw.circle(display,
                YELLOW,
                dot_loc,
                5,
                0)
    receiving_comp.draw(display, GREEN)
    print "OFF inputs", OFF_inputs[index]
    for neuro_comp_freq in OFF_inputs[index]: #for all OFF inputs to one dsg compartment
        print("neuro_comp_freq", neuro_comp_freq)
        input_comp = neuro_comp_freq[0][1]
        input_neuron = neuro_comp_freq[0][0]
        start_abs = input_neuron.location
        stop_rel = input_comp.centroid        
        print("at location", (start_abs + stop_rel).toIntTuple())        
        pygame.draw.line(display,                       #surface
                  YELLOW,                                #color 
                  start_abs.toIntTuple(),                 #start
                  (start_abs + stop_rel).toIntTuple(),  #stop
                  5)    
                                 #width  
    pygame.display.update()
    raw_input()
