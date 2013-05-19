def analyzeStarburst(retina, retina_name, headings, stimulus_name):
    
    stored_activities = []
    max_timesteps = 0        
    for heading in headings:          
        # Load the retina with activities from one of the headings
        trial_name = stimulus_name +"_"+ str(int(heading))
        retina.loadActivities(retina_name, trial_name)
        
        # Pull the starburst activity for this particular trial and store it
        activities = retina.on_starburst_activities
        timesteps = len(activities)
        max_timesteps = max(max_timesteps, timesteps)
        stored_activities.append(activities)
    
    
    # For graphing purposes, it is easier if everything is stored in a giant
    # numpy array.  Since not every run had the same number of timesteps, we
    # must pad with zeros when appropriate
    starburst = retina.on_starburst_layer.neurons[0]
    number_compartments = starburst.number_compartments
    number_headings = len(headings)
    all_activities = np.zeros((number_headings, max_timesteps, number_compartments))
    
    for heading_index in range(number_headings):
        activities = stored_activities[heading_index]
        timesteps = len(activities)
        all_activities[heading_index, :timesteps, :] = activities[:, 0, 0, :]
        
        
    # If we want to graph anything using distance from soma, we need to calculate
    # distance (this assumes all compartments are of size step_size)
    compartment_lengths = []
    step_size = starburst.morphology.step_size    
    for compartment in starburst.compartments:
        length = 0
        has_reached_soma = False
        last_compartment = compartment
        while not(has_reached_soma):
            proximal_neighbors = last_compartment.proximal_neighbors
            last_compartment = proximal_neighbors[0]
            if last_compartment in starburst.morphology.master_compartments:
                has_reached_soma = True
            length += step_size
        compartment_lengths.append(length)
        
        
    # Calculate the preferred heading for each compartment - as defined by the 
    # direction with the greatest maximum response
    preferred_headings = []
    for compartment_index in range(number_compartments):
        preferred_heading_index = 0
        preferred_response = 0.0
        for heading_index in range(number_headings):
            max_response = np.max(all_activities[heading_index, :, compartment_index])
            if max_response > preferred_response:
                preferred_heading_index = heading_index
                preferred_response = max_response
        preferred_headings.append(preferred_heading_index)
        
    
    # Calculate DSI for each compartment as defined by:
    #   preferred_response = greatest response from heading that generated greatest maximum activity
    #   null_response = greatest response from heading opposite the preferred heading
    #   DSI = (preferred_response - null_response) / (preferred_response + null_response)
    DSIs = []
    for compartment_index in range(number_compartments):
        preferred_heading_index = preferred_headings[compartment_index]
        null_heading_index = preferred_heading_index - int(number_headings/2.0)
        preferred_response = np.max(all_activities[preferred_heading_index, :, compartment_index])
        null_response = np.max(all_activities[null_heading_index, :, compartment_index])
        DSI = (preferred_response - null_response) / (preferred_response + null_response)
        DSIs.append(DSI)
        
    
    pygame.init()    
    
    # Figure out scaling
    max_size = Vector2D(1000.0, 1000.0)       
    width_scale = max_size.x / float(retina.grid_width)
    height_scale = max_size.y / float(retina.grid_height)
    scale = min(width_scale, height_scale)   
    starburst.morphology.location = max_size/scale/2.0
    
    # Create a minimized display
    display = pygame.display.set_mode(max_size.toIntTuple())
    for compartment in starburst.compartments:
        # Draw the compartment
        compartment.draw(display, color=(255,255,255), scale=scale)
        
        # Draw a vector in the direction of the preferred heading with magnitude 
        # set by DSI
        index = compartment.index
        preferred_heading = float(headings[preferred_headings[index]])
        magnitude = DSIs[index]/max(DSIs) * 30.0
        
        # Find the centroid of the compartment
        average_compartment_position = Vector2D()
        num_positions = len(compartment.gridded_locations)
        for pos in compartment.gridded_locations: 
            average_compartment_position = average_compartment_position + (pos * scale)
        average_compartment_position = max_size/2.0 + (average_compartment_position / num_positions) 
        
        # Find the vector that represents the DSI and preferred heading
        direction_vector = Vector2D.generateHeadingFromAngle(preferred_heading) * magnitude
        
        # Find the start and end of the line
        start_point = average_compartment_position.toTuple()
        end_point = (average_compartment_position + direction_vector).toTuple()
        pygame.draw.line(display, (255,0,0), start_point, end_point, 5)
        
    pygame.display.update()
    
    while True:
        pygame.display.update()
        
        
    
from Constants import *
retina_name = "12 Directions"
retina = Retina.loadRetina(retina_name)

analyzeStarburst(retina, retina_name, np.arange(0.0, 360.0, 360.0/12.0) , "0")