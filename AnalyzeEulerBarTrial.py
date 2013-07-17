import os
import matplotlib.pyplot as plt
from random import randint 
import numpy as np
import matplotlib.image as mpimg
from Constants import *
import math

def createFigure(long_side_size, rows, cols):
    width, height = long_side_size, long_side_size
    if rows > cols:
        width *= float(cols)/float(rows)
    elif cols > rows:
        height *= float(rows)/float(cols)
    return plt.figure(figsize=(width, height))

def loadData(centroid_file_path, length_file_path, heading_file_path,
             preferred_heading_file_path,  preferred_centrif_file_path,
             vector_magnitude_file_path, vector_centrif_file_path, 
             DSI_file_path, DPI_file_path, voltage_trace_path):
                 
    centroid_file               = open(centroid_file_path, 'r')
    length_file                 = open(length_file_path, 'r')
    heading_file                = open(heading_file_path, 'r')
    preferred_heading_file      = open(preferred_heading_file_path, 'r')
    preferred_centrif_file      = open(preferred_centrif_file_path, 'r')
    vector_magnitude_file       = open(vector_magnitude_file_path, 'r')
    vector_centrif_file         = open(vector_centrif_file_path, 'r')
    DSI_file                    = open(DSI_file_path, 'r')
    DPI_file                    = open(DPI_file_path, 'r')
    voltage_trace_file          = open(voltage_trace_path, 'r')
    
    files = [centroid_file, length_file, heading_file, preferred_heading_file,
             preferred_centrif_file, vector_magnitude_file, vector_centrif_file,
             DSI_file, DPI_file, voltage_trace_file]    
    data = [[] for i in range(len(files))]    
    
    line = centroid_file.readline().rstrip()
    while line != '':
        x, y = line.split(",")
        centroid = Vector2D(float(x), float(y))
        data[0].append(centroid)        
        for i in range(1, 9):
            value = float(files[i].readline().rstrip())
            data[i].append(value)
        line = centroid_file.readline().rstrip()
    
    data[9] = eval(voltage_trace_file.readline().rstrip())
    
    for f in files: f.close()
    
    return data


def selectDistalCompartment(display, starburst, scale, background_color, morphology_color, highlight_color):
    running = True
    selected = None
    while running:
        display.fill(background_color)     
        for compartment in starburst.compartments:
            if compartment.index == selected:
                compartment.draw(display, color=highlight_color, scale=scale)
            else:
                compartment.draw(display, color=morphology_color, scale=scale)
        

        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                x, y = event.pos
                pos = Vector2D(float(x), float(y))
                selected = findNearestCompartment(pos, starburst, scale)
            elif event.type == MOUSEBUTTONDOWN:
                distal = selected
                proximal, intermediate = findProximalAndIntermediateAlongPath(starburst, starburst.compartments[distal])
                return proximal, intermediate, distal
        
        pygame.display.flip()
    
def findNearestCompartment(pos, starburst, scale):
    min_dist = 10000000.0
    min_comp = None
    for compartment in starburst.compartments:
        loc_a = (compartment.neuron.location + compartment.line_points[0]) * scale
        loc_b = (compartment.neuron.location + compartment.line_points[1]) * scale
        loc = (loc_a + loc_b) / 2.0
        dist = loc.distanceTo(pos)
        if dist < min_dist:
            min_comp = compartment.index
            min_dist = dist
    return min_comp
  
    
def findProximalAndIntermediateAlongPath(starburst, distal):
    dendrite_path = [distal]
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
    
    return proximal.index, interm.index       

def calculateData(trial_path, retina_path):
    
    centroid_file_path              = os.path.join(trial_path, "Centroids.txt")
    length_file_path                = os.path.join(trial_path, "Compartment Lengths.txt")
    heading_file_path               = os.path.join(trial_path, "Compartment Headings.txt")
    preferred_heading_file_path     = os.path.join(trial_path, "Preferred Headings.txt")
    preferred_centrif_file_path     = os.path.join(trial_path, "Preferred Centrifigualities.txt")
    vector_magnitude_file_path      = os.path.join(trial_path, "Vector Magnitudes.txt")
    vector_centrif_file_path        = os.path.join(trial_path, "Vector Centrigualities.txt")
    DSI_file_path                   = os.path.join(trial_path, "DSI.txt")
    DPI_file_path                   = os.path.join(trial_path, "DPI.txt")
    voltage_trace_file_path         = os.path.join(trial_path, "Voltage Traces.txt")
    
    centroid_file_exists            = os.path.exists(centroid_file_path)  
    length_file_exists              = os.path.exists(length_file_path)
    heading_file_exists             = os.path.exists(heading_file_path)  
    preferred_heading_file_exists   = os.path.exists(preferred_heading_file_path)  
    preferred_centrif_file_exists   = os.path.exists(preferred_centrif_file_path)    
    vector_magnitude_file_exists    = os.path.exists(vector_magnitude_file_path)  
    vector_centrif_file_exists      = os.path.exists(vector_centrif_file_path)  
    DSI_file_exists                 = os.path.exists(DSI_file_path)  
    DPI_file_exists                 = os.path.exists(DPI_file_path) 
    voltage_trace_file_exists       = os.path.exists(voltage_trace_file_path)        
    
    if centroid_file_exists and length_file_exists and heading_file_exists \
       and preferred_heading_file_exists and preferred_centrif_file_exists \
       and vector_magnitude_file_exists and vector_centrif_file_exists \
       and DSI_file_exists and DPI_file_exists and voltage_trace_file_exists:
        data = loadData(centroid_file_path, length_file_path, heading_file_path,
                        preferred_heading_file_path,  preferred_centrif_file_path,
                        vector_magnitude_file_path, vector_centrif_file_path, 
                        DSI_file_path, DPI_file_path, voltage_trace_file_path)
                        
        centroids                           = data[0]
        compartment_lengths                 = data[1]
        compartment_headings                = data[2]
        preferred_headings                  = data[3]
        preferred_centrifigualities         = data[4]
        vector_average_magnitudes           = data[5]
        vector_average_centrifigualities    = data[6]
        DSIs                                = data[7]
        DPIs                                = data[8]
        voltage_traces                      = data[9]
        number_compartments = len(centroids)
               
    else:
        # General variables             
        headings            = np.arange(0.0, 360.0, 360.0/12.0)
        number_headings     = len(headings)
        retina              = Retina.loadRetina(retina_path)
        starburst           = retina.on_starburst_layer.neurons[0]
        number_compartments = starburst.number_compartments
        trial_number        = 0
        max_timesteps       = 0     
        stored_activities   = []
        
        # Display variables
        pygame.init()    
        max_size            = Vector2D(1000.0, 1000.0)  
        background_color    = (25, 25, 25)
        morphology_color    = (255, 255, 255)
        distal_color        = (255, 25, 25)
        interm_color        = (25, 255, 255)
        proximal_color      = (25, 255, 25)
        
        # Create a (scaled) pygame display     
        width_scale                     = max_size.x / float(retina.grid_width)
        height_scale                    = max_size.y / float(retina.grid_height)
        scale                           = min(width_scale, height_scale)   
        starburst.morphology.location   = max_size/scale/2.0
        display                         = pygame.display.set_mode(max_size.toIntTuple())
        
        # Draw the morphology
        display.fill(background_color)     
        for compartment in starburst.compartments:
            compartment.draw(display, color=morphology_color, scale=scale)
        morphology_path = os.path.join(trial_path, "Morphology.jpg")
        pygame.image.save(display, morphology_path)
                 
    
        # Store activities from the headings
        for heading in headings:
            # Load the retina with activities from one of the headings
            trial_name = str(trial_number) +"_"+ str(int(heading))
            retina.loadActivities(retina_path, trial_name)
            
            # Pull the starburst activity for this particular trial and store it
            activities      = retina.on_starburst_activities
            timesteps       = len(activities)
            max_timesteps   = max(max_timesteps, timesteps)
            stored_activities.append(activities)
            
            
        # For graphing purposes, it is easier if everything is stored in a giant
        # numpy array.  Since not every run had the same number of timesteps, we
        # must pad with zeros when appropriate
        all_activities = np.zeros((number_headings, max_timesteps, number_compartments))
        for heading_index in range(number_headings):
            activities  = stored_activities[heading_index]
            timesteps   = len(activities)
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
            
                
        # Calculate angular heading from soma for each compartment (based on centroid)
        compartment_headings = []
        for i in range(number_compartments):
            centroid = centroids[i]
            compartment_heading = Vector2D().angleHeadingTo(centroid)
            compartment_headings.append(compartment_heading)
        
                
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
        
        
        DPIs = []
        for compartment_index in range(number_compartments):
            up      = 9
            down    = 3
            left    = 6
            right   = 0
            up_response     = np.max(all_activities[up, :, compartment_index])
            down_response   = np.max(all_activities[down, :, compartment_index])
            left_response   = np.max(all_activities[left, :, compartment_index])
            right_response  = np.max(all_activities[right, :, compartment_index])
            total_response  = up_response + down_response + left_response + right_response
            DPI = math.sqrt((left_response - right_response)**2.0 + (up_response - down_response)**2.0) / total_response
            DPIs.append(DPI)
       

        # Draw the DSI over the morphology
        def drawDSI(display, draw_morphology, morphology_color):
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
                
                if compartment_lengths[index] <= 150.0/3.0: color = proximal_color 
                elif compartment_lengths[index] < 2.0*150.0/3.0: color = interm_color
                else: color = distal_color
                
                pygame.draw.line(display, color, start_point, end_point, 4)
                pygame.draw.circle(display, color, centroid.toIntTuple(), 5)
                
            # Scale Bar
            preferred_heading = 270.0
            magnitude = 1.0 * 50.0
            direction_vector = Vector2D.generateHeadingFromAngle(preferred_heading) * magnitude
            start_point = Vector2D(750.0, 850.0)
            end_point = start_point + direction_vector
            pygame.draw.line(display, (255,255,255), start_point.toTuple(), end_point.toTuple(), 4)
            pygame.draw.circle(display, (255,255,255), start_point.toIntTuple(), 5)
            
            font = pygame.font.Font(None, 40)
            label = font.render("{0:.3}".format(max(DSIs)), True, (255,255,255))
            label_rectangle = label.get_rect()
            label_rectangle.center  = (810,825)
            display.blit(label, label_rectangle)
        
        # Save the DSI drawings
        DSI_no_morphology_path = os.path.join(trial_path, "DSI Without Morphology.jpg")
        display.fill(background_color)
        drawDSI(display, False, morphology_color)     
        pygame.image.save(display, DSI_no_morphology_path)
        
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
        average_no_morphology_path = os.path.join(trial_path, "Vector Average Without Morphology.jpg")
        display.fill(background_color)
        drawVectorAverages(display, False, morphology_color)     
        pygame.image.save(display, average_no_morphology_path)
        
        
        # Select an upward path
        upward_compartments = selectDistalCompartment(display, starburst, scale, background_color, morphology_color, (255,0,0))
        # Select a  rightward path
        rightward_compartments = selectDistalCompartment(display, starburst, scale, background_color, morphology_color, (255,0,0))
        # Select a downward path
        downward_compartments = selectDistalCompartment(display, starburst, scale, background_color, morphology_color, (255,0,0))    
        # Select a leftward path
        leftward_compartments = selectDistalCompartment(display, starburst, scale, background_color, morphology_color, (255,0,0))
        
        # Draw the highlighted morphology
        display.fill(background_color)
        selected_proximals = [upward_compartments[0], rightward_compartments[0], downward_compartments[0], leftward_compartments[0]]
        selected_distals = [upward_compartments[2], rightward_compartments[2], downward_compartments[2], leftward_compartments[2]]
        for compartment in starburst.compartments:
            if compartment.index in selected_proximals:
                compartment.draw(display, color=proximal_color, scale=scale)
            elif compartment.index in selected_distals:
                compartment.draw(display, color=distal_color, scale=scale)
            else:
                compartment.draw(display, color=morphology_color, scale=scale)
        morphology_path = os.path.join(trial_path, "Morphology Highlighted.jpg")
        pygame.image.save(display, morphology_path)
        pygame.quit()
        
        directions = [0.0, 90.0, 180.0, 270.0]
        heading_indices = [int(d/(360.0/12.0)) for d in directions]  
        upward_traces = [[], []]
        rightward_traces = [[], []]
        downward_traces = [[], []]
        leftward_traces = [[], []]
        for heading_index in heading_indices:
            upward_traces[0].append(all_activities[heading_index, :, upward_compartments[0]].tolist())
            upward_traces[1].append(all_activities[heading_index, :, upward_compartments[2]].tolist())
            rightward_traces[0].append(all_activities[heading_index, :, rightward_compartments[0]].tolist())
            rightward_traces[1].append(all_activities[heading_index, :, rightward_compartments[2]].tolist())
            downward_traces[0].append(all_activities[heading_index, :, downward_compartments[0]].tolist())
            downward_traces[1].append(all_activities[heading_index, :, downward_compartments[2]].tolist())
            leftward_traces[0].append(all_activities[heading_index, :, leftward_compartments[0]].tolist())
            leftward_traces[1].append(all_activities[heading_index, :, leftward_compartments[2]].tolist())
        voltage_traces = [upward_traces, rightward_traces, downward_traces, leftward_traces]
        
         
        
        # Save the data to text files
        centroid_file               = open(centroid_file_path, 'w')
        length_file                 = open(length_file_path, 'w')
        heading_file                = open(heading_file_path, 'w')
        preferred_heading_file      = open(preferred_heading_file_path, 'w')
        preferred_centrif_file      = open(preferred_centrif_file_path, 'w')
        vector_magnitude_file       = open(vector_magnitude_file_path, 'w')
        vector_centrif_file         = open(vector_centrif_file_path, 'w')
        DSI_file                    = open(DSI_file_path, 'w')
        DPI_file                    = open(DPI_file_path, 'w')
        voltage_trace_file          = open(voltage_trace_file_path, 'w')
        files = [centroid_file, length_file, heading_file, preferred_heading_file,
                 preferred_centrif_file, vector_magnitude_file, vector_centrif_file,
                 DSI_file, DPI_file, voltage_trace_file]
        for i in range(number_compartments):
            centroid_file.write("{0},{1}\n".format(centroids[i].x, centroids[i].y))  
            length_file.write("{0}\n".format(compartment_lengths[i]))    
            heading_file.write("{0}\n".format(compartment_headings[i]))  
            preferred_heading_file.write("{0}\n".format(preferred_headings[i]))   
            preferred_centrif_file.write("{0}\n".format(preferred_centrifigualities[i]))   
            vector_magnitude_file.write("{0}\n".format(vector_average_magnitudes[i]))   
            vector_centrif_file.write("{0}\n".format(vector_average_centrifigualities[i]))   
            DSI_file.write("{0}\n".format(DSIs[i]))   
            DPI_file.write("{0}\n".format(DPIs[i]))    
        voltage_trace_file.write(str(voltage_traces))
        for f in files: f.close()
            
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
            
        elif compartment_length >= 135.0:       
            distal_DSIs.append(DSIs[compartment_index])
            distal_preferred_centrifugalities.append(preferred_centrifigualities[compartment_index])
            distal_vector_magnitudes.append(vector_average_magnitudes[compartment_index])
            distal_vector_centrifugalities.append(vector_average_centrifigualities[compartment_index])
    

        
    return voltage_traces, DSIs, vector_average_magnitudes, compartment_lengths, preferred_centrifigualities, vector_average_centrifigualities
                
    

def analyze(trial_path, retina_path):
            
    voltage_traces, DSIs, vector_magnitudes, lengths, DSI_CIs, AVM_CIs = calculateData(trial_path, retina_path) 

    morphology_highlighted_path     = os.path.join(trial_path, "Morphology Highlighted.jpg")
    morphology_highlighted_image    = mpimg.imread(morphology_highlighted_path)
    morphology_highlighted_image    = morphology_highlighted_image[100:850, 100:850]
    
    fig_rows, fig_cols = 4, 4
    fig = createFigure(20.0, fig_rows, fig_cols)
    grid_size = (fig_rows, fig_cols)
    
    plot_label_props    = dict(boxstyle='round', facecolor='white', alpha=1.0)
    plot_label_x        = 0.05
    plot_label_y        = 0.95
    plot_label_size     = 20
    
    # Highlighted morphology
    ax = plt.subplot2grid(grid_size, (1, 1), colspan=2, rowspan=2)  
    ax.imshow(morphology_highlighted_image)
    ax.axis('off')                     
    plt.text(plot_label_x, plot_label_y, "A", transform=ax.transAxes, 
             fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
             
    # Voltage trace plotting variables     
    directions = [0.0, 90.0, 180.0, 270.0]
    labels = ["Rightward Motion", "Downward Motion", "Leftward Motion", "Upward Motion"]
    linestyles = ['-', '--', '-', '--']
    colors = ['r', 'g', 'b', 'm']    
    
    morphology_direction = ['Upward', 'Rightward', 'Downward', 'Leftward']         
    trace_positions = [[(0,1), (0,2)],
                       [(1,3), (2,3)],
                       [(3,1), (3,2)],
                       [(1,0), (2,0)]]
    subplot_letters = [("B", "C"),
                       ("E", "G"),
                       ("H", "I"),
                       ("D", "F")]                   
             
    for (morphology_direction_index, morphology_direction, (proximal_pos, distal_pos), letters) in zip(range(4), morphology_direction, trace_positions, subplot_letters):
        handles         = []    
        proximal_axis   = plt.subplot2grid(grid_size, proximal_pos) 
        plt.text(plot_label_x, plot_label_y, letters[0], transform=proximal_axis.transAxes, 
                 fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
        distal_axis     = plt.subplot2grid(grid_size, distal_pos) 
        plt.text(plot_label_x, plot_label_y, letters[1], transform=distal_axis.transAxes, 
                 fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
            
        for (heading_index, ls, c) in zip(range(4), linestyles, colors):
            # Proximal Plot
            y_axis = voltage_traces[morphology_direction_index][0][heading_index]
            h, = proximal_axis.plot(range(len(y_axis)), y_axis, c=c, ls=ls)
            max_activity = np.max(y_axis)
            time_of_max = np.argmax(y_axis)
            proximal_axis.axhline(max_activity, xmin=0, xmax=time_of_max/float(len(y_axis)), ls=ls, c=c, linewidth=2)
            handles.append(h)
            proximal_axis.set_xlim([0, len(y_axis)])
            proximal_axis.set_ylim([0, 1])
            proximal_axis.set_title("{0} {1} Compartment".format(morphology_direction, "Proximal"))
            proximal_axis.set_ylabel("Activity")
            proximal_axis.set_xlabel("Timesteps")    
            # Distal plot
            y_axis = voltage_traces[morphology_direction_index][1][heading_index]
            max_activity = np.max(y_axis)
            time_of_max = np.argmax(y_axis)
            distal_axis.axhline(max_activity, xmin=0, xmax=time_of_max/float(len(y_axis)), ls=ls, c=c, linewidth=2)
            distal_axis.plot(range(len(y_axis)), y_axis, c=c, ls=ls)
            distal_axis.set_xlim([0, len(y_axis)])
            distal_axis.set_ylim([0, 1])
            distal_axis.set_title("{0} {1} Compartment".format(morphology_direction, "Distal"))
            distal_axis.set_ylabel("Activity")
            distal_axis.set_xlabel("Timesteps")
            
    
    # Table
    ax = plt.subplot2grid(grid_size, (3,3))
    ax.axis('off')
    row_names = ["Diffusion Radius (um)",
                 "Decay Rate", 
                 "Conductance Factor", 
                 "Wirelength (um)",
                 "Step Size (um)",
                 "Heading Deviation (deg)",
                 "Child Deviation (deg)",
                 "Branching Length (um)"]
    cell_values = [["70"], ["0.05"], ["0.4"], ["150"], ["15"], ["10"], ["20"], ["35"]]                    
    ax.table(cellText=cell_values, rowLabels=row_names,
             bbox=(0.55, 0.275, 0.25, 0.5), colWidths=[0.2])             
    plt.text(plot_label_x, plot_label_y, "J", transform=ax.transAxes, 
             fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
    
    # Legend
    leg = fig.legend(handles, labels, bbox_to_anchor=(1-0.88, 0.135), loc='center', fontsize=20)
    for line in leg.legendHandles: line.set_linewidth(3.5)    
    
    fig.tight_layout()
    fig_path = os.path.join(trial_path, "Euler Bar Results.jpg")
    fig.savefig(fig_path)  
    
    proximal_DSIs = []
    distal_DSIs = []
    proximal_vector_magnitudes = []
    distal_vector_magnitudes = []
    proximal_DSI_CIs = []
    distal_DSI_CIs = []
    proximal_AVM_CIs = []
    distal_AVM_CIs = []
    
    proximal_cutoff = 150.0/3.0
    distal_cutoff = 2*150.0/3.0
    
    number_compartments = len(lengths)    
    for i in range(number_compartments):
        length = lengths[i]
        if length <= proximal_cutoff:        
            proximal_DSIs.append(DSIs[i])
            proximal_vector_magnitudes.append(vector_magnitudes[i])
            proximal_DSI_CIs.append(DSI_CIs[i])
            proximal_AVM_CIs.append(AVM_CIs[i])
        elif length >= distal_cutoff:       
            distal_DSIs.append(DSIs[i])
            distal_vector_magnitudes.append(vector_magnitudes[i])
            distal_DSI_CIs.append(DSI_CIs[i])
            distal_AVM_CIs.append(AVM_CIs[i])
    
    print "Proximal DSIs:", np.average(proximal_DSIs), np.std(proximal_DSIs), len(proximal_DSIs)
    print "Proximal DSI CIs:", np.average(proximal_DSI_CIs), np.std(proximal_DSI_CIs), len(proximal_DSI_CIs)
    print "Proximal AVMs:", np.average(proximal_vector_magnitudes), np.std(proximal_vector_magnitudes), len(proximal_vector_magnitudes)
    print "Proximal AVM CIs:", np.average(proximal_AVM_CIs), np.std(proximal_AVM_CIs), len(proximal_AVM_CIs)
    print "Distal DSIs:", np.average(distal_DSIs), np.std(distal_DSIs), len(distal_DSIs)
    print "Distal DSI CIs:", np.average(distal_DSI_CIs), np.std(distal_DSI_CIs), len(distal_DSI_CIs)
    print "Distal AVMs:", np.average(distal_vector_magnitudes), np.std(distal_vector_magnitudes), len(distal_vector_magnitudes)
    print "Distal AVM CIs:", np.average(distal_AVM_CIs), np.std(distal_AVM_CIs), len(distal_AVM_CIs)
        
    fig_rows, fig_cols = 4, 4
    fig = createFigure(20.0, fig_rows, fig_cols)
    grid_size = (fig_rows, fig_cols)
    
    
    DSI_morphology_path     = os.path.join(trial_path, "DSI Without Morphology.jpg")
    DSI_morphology_image    = mpimg.imread(DSI_morphology_path)
    DSI_morphology_image    = DSI_morphology_image[100:900, 100:900]
    ax = plt.subplot2grid(grid_size, (0,0), colspan=2, rowspan=2)
    ax.imshow(DSI_morphology_image)
    ax.set_title("DSI", size=25)
    ax.axis('off')     
    plt.text(plot_label_x, plot_label_y, "A", transform=ax.transAxes, 
             fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
    
    vector_morphology_path  = os.path.join(trial_path, "Vector Average Without Morphology.jpg")
    vector_morphology_image = mpimg.imread(vector_morphology_path)
    vector_morphology_image = vector_morphology_image[100:900, 100:900]
    ax = plt.subplot2grid(grid_size, (0,2), colspan=2, rowspan=2)
    ax.imshow(vector_morphology_image)
    ax.set_title("Average Vector", size=25)
    ax.axis('off')           
    plt.text(plot_label_x, plot_label_y, "F", transform=ax.transAxes, 
             fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
    
    proximal_color      = (25/255.0, 1.0, 25/255.0)
    distal_color        = (1.0, 25/255.0, 25/255.0)
    
    positions           = [(2,0), (2,1), (3,0), (3,1), (2, 2), (2, 3), (3, 2), (3, 3)]
    compartment_names   = ["Proximal", "Proximal", "Distal", "Distal", "Proximal", "Proximal", "Distal", "Distal"]
    colors              = [proximal_color, proximal_color, distal_color, distal_color, proximal_color, proximal_color, distal_color, distal_color]
    metric_names        = ["DSI", "CI From DSI", "DSI", "CI From DSI", "AVM", "CI From AVM", "AVM", "CI From AVM"]
    range_CI              = [-1.0, 1.0]
    range_DSI             = [0, 0.35]
    range_AVM             = [0, 0.35]
    range_values          = [range_DSI, range_CI, range_DSI, range_CI, range_AVM, range_CI, range_AVM, range_CI]
    data                = [proximal_DSIs, proximal_DSI_CIs, distal_DSIs, distal_DSI_CIs,
                           proximal_vector_magnitudes, proximal_AVM_CIs, distal_vector_magnitudes, distal_AVM_CIs]
    subplot_letters     = ["B", "C", "D", "E", "G", "H", "I", "J"]
    for (pos, comp_name, metric_name, (min_val, max_val), datum, color, letter) in zip(positions, compartment_names, metric_names, range_values, data, colors, subplot_letters):
        ax = plt.subplot2grid(grid_size, pos)
        ax.hist(datum, bins=30, color=color, range=[min_val, max_val])
        ax.set_title("{0} {1} Histogram".format(comp_name, metric_name))
        ax.set_xlabel(metric_name)
        ax.set_ylabel("Frequency")
        ax.set_ylim([0, 40])
        ax.set_yticklabels(plt.yticks()[0], rotation=0, size=10)
        ax.set_xticklabels(plt.xticks()[0], rotation=70, size=10)
        plt.text(plot_label_x, plot_label_y, letter, transform=ax.transAxes, 
                 fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
    
    fig.tight_layout()
    fig_path = os.path.join(trial_path, "Histogram Results.jpg")
    fig.savefig(fig_path)  
    
        
        
    
trial_name = "Bar_Euler_Results"

trial_path  = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
retina      = "0"
retina_path = os.path.join(trial_path, "0")
    
analyze(trial_path, retina_path)