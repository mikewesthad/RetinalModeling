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

#Build a starburst morphology
scale = 1.0
screen_mid = screen_size/(2.0 * scale)
screen_third = screen_size/(3.0 * scale)
#draw_location = screen_mid
starburst_morphology1 = StarburstMorphology(retina,
                                            visualize_growth=True,
                                            color_palette=BLUES,
                                            display=display,
                                            draw_location=screen_third,
                                            scale=scale)
                                           
starburst_morphology2 = StarburstMorphology(retina,
                                            visualize_growth=True,
                                            color_palette=REDS,
                                            display=display,
                                            draw_location=2*screen_third,
                                            scale=scale)

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
                                                                                                                        





#Build a unique starburst cells using above morphologies
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

for sac in SACs:
    for compartment in sac.morphology.compartments:
        total_inputs = 0       
        for comp, freq in compartment.inputs.items():
            total_inputs += freq
        num_points = len(compartment.points)
        if num_points != total_inputs:
            print"Compartment number =", sac.morphology.compartments.index(compartment)            
            print("num_comp_points {0} != {1} total_inputs".format(num_points, total_inputs))           

comp = starburst1.morphology.compartments[0]
point = comp.points[0]

point_locations = []
for point in comp.points:
    others = starburst1.retina.getOverlappingNeurons(starburst1, point.location)
    if len(others) != 1:
        print(point.location.toIntTuple())
        print(others)
    if point.location not in point_locations:
        point_locations.append(point.location)
    else:
        print point.location.toIntTuple()




#Interactive drawing
#switch between views with d/c/p; change scale with left/right
running             = False
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
        SACs[i].location = (i+1)*screen_third        
        #SACs[i].location = draw_location        
        SACs[i].draw(display, 
                            scale = scale,
                            draw_segments = draw_segments,
                            draw_compartments = draw_compartments,
                            draw_points = draw_points)
    pygame.display.update()

