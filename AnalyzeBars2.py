import os
import matplotlib.pyplot as plt
from random import randint 
import numpy as np
import matplotlib

def createFigure(long_side_size, rows, cols):
    width, height = long_side_size, long_side_size
    if rows > cols:
        width *= float(cols)/float(rows)
    elif cols > rows:
        height *= float(rows)/float(cols)
    return plt.figure(figsize=(width, height))


def calculateData(retina_paths, number_stimulus_variations, number_bars):
    number_retinas  = len(retina_paths)
    number_trials   = number_retinas * number_stimulus_variations
    headings        = np.arange(0.0, 360.0, 360.0/number_bars)
    
    trial_centroids = []
    trial_compartment_lengths = []
    trial_compartment_headings = []
    trial_preferred_headings = []
    trial_preferred_centrifigualities = []
    trial_vector_averages = []
    trial_vector_average_magnitudes = []
    trial_vector_average_centrifigualities = []
    trial_DSIs = []
    trial_voltage_traces = []
        
    # Display variables
    pygame.init()    
    max_size = Vector2D(1000.0, 1000.0)  
    background_color = (25, 25, 25)
    morphology_color = (255, 255, 255)
    line_color = (243, 134, 48)
    circle_color = (250, 105, 0)
    
    
    for retina_path in retina_paths:
        retina = Retina.loadRetina(retina_path)
        for trial_number in range(number_stimulus_variations):
            
            
            stored_activities = []
            max_timesteps = 0     
            for heading in headings:
                # Load the retina with activities from one of the headings
                trial_name = str(trial_number) +"_"+ str(int(heading))
                retina.loadActivities(retina_path, trial_name)
                
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
                
            # Calculate the centroids of each compartment
            centroids = []
            for compartment in starburst.compartments:
                centroid = Vector2D()
                num_positions = len(compartment.gridded_locations)
                for position in compartment.gridded_locations: 
                    centroid = centroid + position
                centroid = centroid / num_positions
                centroids.append(centroid)
            trial_centroids.append(centroids)
                
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
            trial_compartment_lengths.append(compartment_lengths)
            
            # Calculate angular heading from soma for each compartment (based on centroid)
            compartment_headings = []
            for i in range(number_compartments):
                centroid = centroids[i]
                compartment_heading = Vector2D().angleHeadingTo(centroid)
                compartment_headings.append(compartment_heading)
            trial_compartment_headings.append(compartment_headings)
            
            # Calculate the preferred heading for each compartment - as defined by the 
            # direction with the greatest maximum response
            preferred_headings = []
            preferred_centrifigualities = []
            for compartment_index in range(number_compartments):
                preferred_heading_index = 0
                preferred_response = 0.0
                for heading_index in range(number_headings):
                    max_response = np.max(all_activities[heading_index, :, compartment_index])
                    if max_response > preferred_response:
                        preferred_heading_index = heading_index
                        preferred_response = max_response
                preferred_heading = headings[preferred_heading_index]
                angle_from_soma = compartment_headings[compartment_index]
                preferred_centrifiguality = 1.0 - abs(preferred_heading-angle_from_soma)/180.0
                preferred_headings.append(preferred_heading_index)
                preferred_centrifigualities.append(preferred_centrifiguality)
            trial_preferred_headings.append(preferred_headings)
            trial_preferred_centrifigualities.append(preferred_centrifigualities)    
            
            # Calculate the vector average heading for each compartment - as defined by
            # the maximum response in each direction
            vector_averages = []
            vector_average_magnitudes = []
            vector_average_centrifigualities = []
            for compartment_index in range(number_compartments):
                vector_average = Vector2D()
                for heading_index in range(number_headings):
                    heading = float(headings[heading_index])
                    max_response = np.max(all_activities[heading_index, :, compartment_index])
                    vector_average = vector_average + max_response * Vector2D.generateHeadingFromAngle(heading)
                vector_average = vector_average / float(len(headings))
                vector_averages.append(vector_average)
                vector_average_magnitudes.append(vector_average.length())
                vector_angle = Vector2D().angleHeadingTo(vector_average)
                angle_from_soma = compartment_headings[compartment_index]
                vector_average_centrifiguality = 1.0 - abs(vector_angle-angle_from_soma)/180.0
                vector_average_centrifigualities.append(vector_average_centrifiguality)
            trial_vector_averages.append(vector_averages)
            trial_vector_average_magnitudes.append(vector_average_magnitudes)
            trial_vector_average_centrifigualities.append(vector_average_centrifigualities)     
            
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
            trial_DSIs.append(DSIs)
            
            voltage_traces = []
            proximal, intermediate, distal = selectStarburstCompartmentsAlongDendrite(retina, 0)
            directions = [0.0, 90.0, 180.0, 270.0]
            heading_indices = [int(d/(360.0/number_bars)) for d in directions]  
            for compartment_index in [proximal, intermediate, distal]:
                compartment_traces = []
                for heading_index in heading_indices:
                    trace = all_activities[heading_index, :, compartment_index]
                    compartment_traces.append(trace)
                voltage_traces.append(compartment_traces)
            trial_voltage_traces.append(voltage_traces)   
            
            # Create a (scaled) pygame display     
            width_scale = max_size.x / float(retina.grid_width)
            height_scale = max_size.y / float(retina.grid_height)
            scale = min(width_scale, height_scale)   
            starburst.morphology.location = max_size/scale/2.0
            display = pygame.display.set_mode(max_size.toIntTuple())
            pygame.display.iconify()    
            
            # Draw the morphology
            if trial_number == 0:
                display.fill(background_color)     
                for compartment in starburst.compartments:
                    compartment.draw(display, color=morphology_color, scale=scale)
                morphology_path = os.path.join(retina_path, "Morphology.jpg")
                pygame.image.save(display, morphology_path)
                    
            # Draw the DSI over the morphology
            def drawDSI(display, draw_morphology, morphology_color, line_color, circle_color):
                for compartment, index in zip(starburst.compartments, range(number_compartments)):            
                    # Draw the compartment
                    if draw_morphology: compartment.draw(display, color=morphology_color, scale=scale)
                    
                    # Draw a vector in the direction of the preferred heading with magnitude 
                    # set by DSI
                    preferred_heading   = float(headings[preferred_headings[index]])
                    magnitude           = DSIs[index]/max(DSIs) * 50.0
                    
                    # Find the centroid of the compartment
                    centroid = centroids[index]   
                    centroid = scale * (centroid + starburst.morphology.location)
                    
                    # Find the vector that represents the DSI and preferred heading
                    direction_vector = Vector2D.generateHeadingFromAngle(preferred_heading) * magnitude
                    
                    # Find the start and end of the line
                    start_point = centroid.toTuple()
                    end_point = (centroid + direction_vector).toTuple()
                    pygame.draw.line(display, line_color, start_point, end_point, 4)
                    pygame.draw.circle(display, circle_color, centroid.toIntTuple(), 5)
            
            # Save the DSI drawings
            DSI_no_morphology_path = os.path.join(retina_path, str(trial_number)+" DSI Without Morphology.jpg")
            display.fill(background_color)
            drawDSI(display, False, morphology_color, line_color, circle_color)     
            pygame.image.save(display, DSI_no_morphology_path)
            
            # Draw the vector averages over the morphology
            def drawVectorAverages(display, draw_morphology, morphology_color, line_color, circle_color):
                for compartment, index in zip(starburst.compartments, range(number_compartments)):            
                    # Draw the compartment
                    if draw_morphology: compartment.draw(display, color=morphology_color, scale=scale)
                    
                    # Draw a vector in the direction of the preferred heading with magnitude 
                    # set by DSI
                    if vector_averages[index].length() != 0:
                        vector_average = vector_averages[index].copy().normalize()
                        magnitude = vector_average_magnitudes[index]/max(vector_average_magnitudes)
                        vector_average = vector_average * magnitude * 50.0
                        
                        # Find the centroid of the compartment
                        centroid = centroids[index]   
                        centroid = scale * (centroid + starburst.morphology.location)
                        
                        # Find the start and end of the line
                        start_point = centroid.toTuple()
                        end_point = (centroid + vector_average).toTuple()
                        pygame.draw.line(display, line_color, start_point, end_point, 4)
                        pygame.draw.circle(display, circle_color, centroid.toIntTuple(), 5)
            
            # Save the vector average drawings
            average_no_morphology_path = os.path.join(retina_path, str(trial_number)+" Vector Average Without Morphology.jpg")
            display.fill(background_color)
            drawVectorAverages(display, False, morphology_color, line_color, circle_color)     
            pygame.image.save(display, average_no_morphology_path)
            
            
    
    results = [trial_centroids, trial_compartment_lengths, 
               trial_compartment_headings, trial_preferred_headings, 
               trial_preferred_centrifigualities, trial_vector_averages,
               trial_vector_average_magnitudes, trial_vector_average_centrifigualities,
               trial_DSIs, trial_voltage_traces]
    return results
                
    

def analyze(trial_path, retina_paths, number_stimulus_variations, number_bars):
            
    results = calculateData(retina_paths, number_stimulus_variations, number_bars) 
    compartment_lengths                 = results[1]
    preferred_centrifigualities         = results[4]
    vector_average_magnitudes           = results[6]
    vector_average_centrifigualities    = results[7]
    DSIs                                = results[8]
    voltage_traces                      = results[9]
    
    number_retinas  = len(retina_paths)
    number_trials   = number_retinas * number_stimulus_variations
    
    max_DSI = max([max(x) for x in DSIs])
    max_vector = max([max(x) for x in vector_average_magnitudes])

    for retina_number in range(number_retinas):
        fig1_rows, fig1_cols, fig1_index = number_stimulus_variations, 4+4+3, 1
        fig1 = createFigure(10.0*number_stimulus_variations, fig1_rows, fig1_cols)
        matplotlib.rc('xtick', labelsize=12)
        matplotlib.rc('ytick', labelsize=12)
        for stimulus_number in range(number_stimulus_variations):
            index = retina_number * number_stimulus_variations + stimulus_number
    
            # Figure 1 - Vector Averages
            ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
            ax.hist(vector_average_centrifigualities[index], bins=20, range=(-1.0, 1.0))
            ax.set_title("Average Heading")
            ax.set_xlabel("Centrifugality Index")
            ax.set_ylabel("Frequency")
            fig1_index += 1    
            
            ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
            ax.scatter(vector_average_centrifigualities[index], vector_average_magnitudes[index], alpha=0.25)
            ax.set_title("Average Heading")
            ax.set_ylabel("Magnitude of Vector Average")
            ax.set_xlabel("Centrifugality Index")  
#            ax.set_ylim([0, max_vector])
            fig1_index += 1      
            
            ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
            ax.scatter(compartment_lengths[index], vector_average_centrifigualities[index], alpha=0.25)
            ax.set_title("Average Heading")
            ax.set_xlabel("Distance from Soma")
            ax.set_ylabel("Centrifugality Index")
#            ax.set_ylim([0, max_vector])
            fig1_index += 1                
            
            ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
            ax.scatter(compartment_lengths[index], vector_average_magnitudes[index], alpha=0.25)
            ax.set_title("Average Heading")
            ax.set_ylabel("Magnitude of Vector Average")
            ax.set_xlabel("Distance from soma")
#            ax.set_ylim([0, max_vector])
            fig1_index += 1    
            
           
            # Figure 2 - DSI
            ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
            ax.hist(preferred_centrifigualities[index], bins=20, range=(-1.0, 1.0))
            ax.set_title("Preferred Heading")
            ax.set_xlabel("Centrifugality Index")
            ax.set_ylabel("Frequency")
            fig1_index += 1    
            
            ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
            ax.scatter(preferred_centrifigualities[index], DSIs[index], alpha=0.25)
            ax.set_title("Preferred Heading")
            ax.set_ylabel("Magnitude of DSI")
            ax.set_xlabel("Centrifugality Index")
#            ax.set_ylim([0, max_DSI])
            fig1_index += 1    
            
            ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
            ax.scatter(compartment_lengths[index], preferred_centrifigualities[index], alpha=0.25)
            ax.set_title("Preferred Heading")
            ax.set_xlabel("Distance from Soma")
            ax.set_ylabel("Centrifugality Index")
#            ax.set_ylim([0, max_DSI])
            fig1_index += 1    
            
            ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
            ax.scatter(compartment_lengths[index], DSIs[index], alpha=0.25)
            ax.set_title("Preferred Heading")
            ax.set_ylabel("Magnitude of DSI")
            ax.set_xlabel("Distance from soma")
#            ax.set_ylim([0, max_DSI])
            fig1_index += 1    
            
            
            # Figure 3 - Voltage Traces     
            directions = [0.0, 90.0, 180.0, 270.0]
            labels = [str(int(d)) for d in directions]
            linestyles = ['-', '--', '-', '--']
            colors = ['r', 'g', 'b', 'm']
            
            for (compartment_index, compartment_name) in zip([0,1,2], ["Proximal", "Intermediate", "Distal"]):
                ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
                for (heading_index, label, ls, c) in zip(range(4), labels, linestyles, colors):
                    y_axis = voltage_traces[index][compartment_index][heading_index]
                    ax.plot(range(len(y_axis)), y_axis, c=c, ls=ls, label=label)
                    max_activity = np.max(y_axis)
                    time_of_max = np.argmax(y_axis)
                    ax.axhline(max_activity, xmin=0, xmax=(time_of_max-1.0)/float(len(y_axis)), ls=ls, c=c)
                ax.set_title(compartment_name)
                ax.set_ylabel("Activity")
                ax.set_xlabel("Timesteps")
                ax.set_ylim([0, 1])
                ax.legend(loc=1)
                fig1_index += 1
            
            
        
            
        fig1.tight_layout()
        fig1_path = os.path.join(trial_path, str(retina_number)+" Results.jpg")
        fig1.savefig(fig1_path)    
    
    
def selectStarburstCompartmentsAlongDendrite(retina, angle):
    starburst = retina.on_starburst_layer.neurons[0]
    
    acceptable_deviation = 10
    min_angle = angle - acceptable_deviation
    max_angle = angle + acceptable_deviation
    if max_angle > 360: max_angle -= 360
    if min_angle < 0: min_angle = 360 + min_angle    
        
    starburst_center = Vector2D()
       
    acceptable_compartment = False
    number_tries = 0
    max_tries = 1000
    while not(acceptable_compartment):        
        random_compartment_index = randint(0, starburst.number_compartments-1)
        random_compartment = starburst.compartments[random_compartment_index]
        
        # Check if terminal compartment        
        if random_compartment.distal_neighbors == []:
            
            # Check angle heading
            terminal_point = random_compartment.line_points[-1]
            compartment_heading = starburst_center.angleHeadingTo(terminal_point)
            is_angle_acceptable = False            
            
            if max_angle < min_angle:
                is_angle_acceptable = compartment_heading <= max_angle or compartment_heading >= min_angle
            else:
                is_angle_acceptable = compartment_heading <= max_angle and compartment_heading >= min_angle
                
            if is_angle_acceptable:
                terminal_compartment = random_compartment
                acceptable_compartment = True
        
        number_tries += 1
        if number_tries > max_tries:
            print "Increased acceptable deviation", acceptable_deviation
            number_tries = 0
            acceptable_deviation += 10
            min_angle = angle - acceptable_deviation
            max_angle = angle + acceptable_deviation
            if max_angle > 360: max_angle -= 360
            if min_angle < 0: min_angle = 360 + min_angle
            
    dendrite_path = [terminal_compartment]
    has_reached_soma = False
    while not(has_reached_soma):
        most_proximal_compartment = dendrite_path[0]
        proximal_neighbors = most_proximal_compartment.proximal_neighbors
        
        new_proximal_compartment = proximal_neighbors[0]
        dendrite_path.insert(0, new_proximal_compartment)
        
        if new_proximal_compartment in starburst.morphology.master_compartments:
            has_reached_soma = True
        
    number_compartments = len(dendrite_path)
    proximal = dendrite_path[0]
    interm   = dendrite_path[int(round(number_compartments/2.0))]
    distal   = dendrite_path[-1]
    
    return proximal.index, interm.index, distal.index                 
    
        
    
from Constants import *
trial_name = "Bar_Diffusion_Batch_Large_Same_Morphology"
number_bars = 12
number_stimulus_variations = len(range(10,640,30))

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
entries = os.listdir(trial_path)
retina_paths = []
for entry in entries:
    path_to_entry = os.path.join(trial_path, entry)
    if os.path.isdir(path_to_entry):
        retina_paths.append(path_to_entry)

#retina_paths = []
#for x in range(2):
#    path_to_entry = os.path.join(trial_path, str(x))
#    retina_paths.append(path_to_entry)
    

analyze(trial_path, retina_paths, number_stimulus_variations, number_bars)