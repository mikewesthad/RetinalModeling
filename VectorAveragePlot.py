import os
import matplotlib.pyplot as plt
from random import randint 
import matplotlib.image as mpimg
import numpy as np
import matplotlib
import math;

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
    
    trial_proxmial_DSIs                         = []
    trial_distal_DSIs                           = []
    trial_proxmial_vector_magnitudes            = []
    trial_distal_vector_magnitudes              = []
    trial_proxmial_preferred_centrifigualities  = []
    trial_distal_preferred_centrifigualities    = []
    trial_proxmial_vector_centrifigualities     = []
    trial_distal_vector_centrifigualities       = []
    
    # Display variables
    pygame.init()    
    max_size            = Vector2D(1000.0, 1000.0)  
    background_color    = (25, 25, 25)
    morphology_color    = (255, 255, 255)
    distal_color        = (255, 25, 25)
    interm_color        = (25, 255, 255)
    proximal_color      = (25, 255, 25)
    
    # Create a (scaled) pygame display     
    width_scale                     = max_size.x / float(400)
    height_scale                    = max_size.y / float(400)
    scale                           = min(width_scale, height_scale)   
    display                         = pygame.display.set_mode(max_size.toIntTuple())
            
    
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
            starburst.morphology.location   = max_size/scale/2.0
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
                while not(has_reached_soma) and compartment not in starburst.morphology.master_compartments:
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
            norm = 1.0/12.0
            angle = 360.0/number_headings
            for i in range(1, int(math.ceil(90/angle))): norm += 2.0/12.0 * math.cos(math.radians(i*angle)) 
            for compartment_index in range(number_compartments):
                vector_average = Vector2D()
                for heading_index in range(number_headings):
                    heading = float(headings[heading_index])
                    max_response = np.max(all_activities[heading_index, :, compartment_index])
                    vector_average = vector_average + max_response * Vector2D.generateHeadingFromAngle(heading)
                vector_average = vector_average / number_headings / norm
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
#                DSI = (preferred_response - null_response)
                DSIs.append(DSI)
            trial_DSIs.append(DSIs)
            
            # Calculate the average DSI, vector magnitude and centrifugality for
            # the proximal part of the cell and the distal part of the cell
            proximal_DSIs                       = []
            distal_DSIs                         = []
            proximal_vector_magnitudes          = []
            distal_vector_magnitudes            = []
            proximal_preferred_centrifugalities = []
            distal_preferred_centrifugalities   = []
            proximal_vector_centrifugalities    = []
            distal_vector_centrifugalities      = []
            
            for compartment_index in range(number_compartments):
                compartment_length = compartment_lengths[compartment_index]
                if compartment_length <= 0.0:        
                    proximal_DSIs.append(DSIs[compartment_index])
                    proximal_preferred_centrifugalities.append(preferred_centrifigualities[compartment_index])
                    proximal_vector_magnitudes.append(vector_average_magnitudes[compartment_index])
                    proximal_vector_centrifugalities.append(vector_average_centrifigualities[compartment_index])
                    
                elif compartment_length >= 100.0:       
                    distal_DSIs.append(DSIs[compartment_index])
                    distal_preferred_centrifugalities.append(preferred_centrifigualities[compartment_index])
                    distal_vector_magnitudes.append(vector_average_magnitudes[compartment_index])
                    distal_vector_centrifugalities.append(vector_average_centrifigualities[compartment_index])
                
            trial_proxmial_DSIs.append(proximal_DSIs)
            trial_distal_DSIs.append(distal_DSIs)
            trial_proxmial_vector_magnitudes.append(proximal_vector_magnitudes)
            trial_distal_vector_magnitudes.append(distal_vector_magnitudes)
            trial_proxmial_preferred_centrifigualities.append(proximal_preferred_centrifugalities)
            trial_distal_preferred_centrifigualities.append(distal_preferred_centrifugalities)
            trial_proxmial_vector_centrifigualities.append(proximal_vector_centrifugalities)
            trial_distal_vector_centrifigualities.append(distal_vector_centrifugalities)
            
            # Draw the morphology
            display.fill(background_color)     
            for compartment in starburst.compartments:
                compartment.draw(display, color=morphology_color, scale=scale)
            morphology_path = os.path.join(retina_path, "Morphology.jpg")
            pygame.image.save(display, morphology_path)
            
            # Draw the vector averages over the morphology
            def drawVectorAverages(display, draw_morphology, morphology_color):
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
                            
                        if compartment_lengths[index] <= 150.0/3.0: color = proximal_color 
                        elif compartment_lengths[index] < 2.0*150.0/3.0: color = interm_color
                        else: color = distal_color
                        
                        # Find the start and end of the line
                        start_point = centroid.toTuple()
                        end_point = (centroid + vector_average).toTuple()
                        pygame.draw.line(display, color, start_point, end_point, 4)
                        pygame.draw.circle(display, color, centroid.toIntTuple(), 5)
                    
                # Scale Bar
                vector_average = Vector2D(0.0, -1.0)
                magnitude = 1.0
                vector_average = vector_average * magnitude * 50.0
                start_point = Vector2D(750.0, 850.0)
                end_point = start_point + vector_average
                pygame.draw.line(display, (255,255,255), start_point.toTuple(), end_point.toTuple(), 4)
                pygame.draw.circle(display, (255,255,255), start_point.toIntTuple(), 5)
                
                font = pygame.font.Font(None, 40)
                label = font.render("{0:.3}".format(max(vector_average_magnitudes)), True, (255,255,255))
                label_rectangle = label.get_rect()
                label_rectangle.center  = (820,825)
                display.blit(label, label_rectangle)
            
            # Save the vector average drawings
            average_no_morphology_path = os.path.join(retina_path, "Vector Average Without Morphology.jpg")
            display.fill(background_color)
            drawVectorAverages(display, False, morphology_color)     
            pygame.image.save(display, average_no_morphology_path)
    pygame.quit()
                
    
    
    
def drawMorphology(trial_path, retina_paths):
    pygame.init()    
    max_size            = Vector2D(1000.0, 1000.0)  
    background_color    = (25, 25, 25)
    morphology_color    = (255, 255, 255)
    width_scale         = max_size.x / 400.0
    height_scale        = max_size.y / 400.0
    scale               = min(width_scale, height_scale)   
    display             = pygame.display.set_mode(max_size.toIntTuple())
    pygame.display.iconify()
    
    retina_number = 0
    for retina_path in retina_paths:
        retina = Retina.loadRetina(retina_path)
        starburst = retina.on_starburst_layer.neurons[0]
        starburst.morphology.location   = max_size/scale/2.0
        
        # Draw the morphology
        display.fill(background_color)     
        for compartment in starburst.compartments:
            compartment.draw(display, color=morphology_color, scale=scale)
        morphology_path = os.path.join(trial_path, str(retina_number)+" Morphology.jpg")
        pygame.image.save(display, morphology_path)
        retina_number += 1
    pygame.quit()
    
from Constants import *
trial_name = "110_Degree_Kink"
number_bars = 12

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
entries = os.listdir(trial_path)
retina_paths = []
for entry in entries:
    path_to_entry = os.path.join(trial_path, entry)
    if os.path.isdir(path_to_entry):
        retina_paths.append(path_to_entry)

drawMorphology(trial_path, retina_paths)
calculateData(retina_paths, 1, number_bars)