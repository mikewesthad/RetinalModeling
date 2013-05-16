import os
import math
from random import randint, choice
import matplotlib.pyplot as plt
import pyPdf
from Constants import *

def mergePDFs(output_path, filepaths):
    output      = pyPdf.PdfFileWriter()

    filehandles = []
    for filepath in filepaths:
        fh  = file(filepath, "rb")
        pdf = pyPdf.PdfFileReader(fh)
        output.addPage(pdf.getPage(0))
        filehandles.append(fh)
    
    outputStream = file(output_path, "wb")
    output.write(outputStream)
    outputStream.close()
    
    for (fh, filepath) in zip(filehandles, filepaths): 
        fh.close()
        os.remove(filepath)

def generateHistogramPlotsOfWeights(retina, retina_name, runtime_name, proximal, intermediate, distal):
    morphology          = retina.on_starburst_layer.morphologies[0]
    num_compartments    = len(morphology.compartments)
    distances           = morphology.distances
    weights             = morphology.diffusion_weights
    step_size           = morphology.step_size
    
    max_distance = np.max(distances)
    bins = max_distance/step_size * 2.0
    
    p_histogram, b = np.histogram(distances[proximal, :], bins=bins, range=(0, max_distance))
    i_histogram, b = np.histogram(distances[intermediate, :], bins=bins, range=(0, max_distance))
    d_histogram, b = np.histogram(distances[distal, :], bins=bins, range=(0, max_distance))
    max_frequency = np.max(np.concatenate((p_histogram, i_histogram, d_histogram))) + 5
    
    fig = plt.figure(figsize=(10, 10))
    rows, cols, index = 3, 3, 1
    
    for (location, location_name) in [(proximal, "Proximal"), (intermediate, "Intermediate"), (distal, "Distal")]:
        ax = fig.add_subplot(rows, cols, index)
        ax.hist(distances[location, :], bins=bins, range=(0, max_distance))
        ax.set_ylim([0, max_frequency])
        ax.set_xlabel("Distance", size='xx-small')
        ax.set_ylabel("Frequency", size='xx-small')
        ax.set_title("Neighbor Distances for {0} Compartment".format(location_name), size='xx-small')
        ax.tick_params(labelsize='xx-small')
        index += 1
        
    
    for (location, location_name) in [(proximal, "Proximal"), (intermediate, "Intermediate"), (distal, "Distal")]:
        compartment_distances   = distances[location, :]
        compartment_weights     = weights[location, :]
        
        x_axis, y_axis = [], []
        for i in range(num_compartments):
            weight              = compartment_weights[i]
            distance            = compartment_distances[i]
            if distance not in x_axis:
                x_axis.append(distance)
                y_axis.append(weight)
        
        ax = fig.add_subplot(rows, cols, index)
        ax.bar(x_axis, y_axis, 8)
        ax.set_ylim([0, 1])
        ax.set_xlim([0, max_distance])
        ax.set_xlabel("Distance From Compartment", size='xx-small')
        ax.set_ylabel("Output Diffusion Weight", size='xx-small')
        ax.set_title("Neighbor Weights for {0} Compartment".format(location_name), size='xx-small')
        ax.tick_params(labelsize='xx-small')
        index += 1
        
        
        
    for (location, location_name) in [(proximal, "Proximal"), (intermediate, "Intermediate"), (distal, "Distal")]:
        compartment_distances   = distances[location, :]
        compartment_weights     = weights[location, :]
        
        x_axis, y_axis = [], []
        for i in range(num_compartments):
            weight              = compartment_weights[i]
            distance            = compartment_distances[i]
            if distance not in x_axis:
                x_axis.append(distance)
                y_axis.append(weight)
            else:
                loc = x_axis.index(distance)
                y_axis[loc] += weight
        
        ax = fig.add_subplot(rows, cols, index)
        ax.bar(x_axis, y_axis, 8)
        ax.set_ylim([0, 1])
        ax.set_xlim([0, max_distance])
        ax.set_xlabel("Distance From Compartment", size='xx-small')
        ax.set_ylabel("Sum Output Diffusion Weights", size='xx-small')
        ax.set_title("Sum Neighbor Weights for {0} Compartment".format(location_name), size='xx-small')
        ax.tick_params(labelsize='xx-small')
        index += 1
        
    fig.tight_layout()
    fig_path = os.path.join("Saved Retinas", retina_name, runtime_name+"_Starburst Output Weights.pdf")
    fig.savefig(fig_path)


def analyzeEffectsOfRuntimeParameter(retina, retina_name, runtime_parameter_name, runtime_parameter_settings, headings, stimulus_name):
    if isinstance(runtime_parameter_settings, np.ndarray):
        runtime_parameter_settings = runtime_parameter_settings.tolist()
           
    starburst_activities = {heading:{} for heading in headings}
    
    max_timesteps = 0
        
    for i in range(len(runtime_parameter_settings)):
        for heading in headings:            
            directory_name = retina_name
            trial_name = str(i) + "_" + stimulus_name + "_" + str(int(heading))
            retina.loadActivities(directory_name, trial_name)
            
            # Pull the starburst activity for this particular trial and store it
            activities = retina.on_starburst_activities
            max_timesteps = max(max_timesteps, len(activities))
            starburst_activities[heading][i] = activities
            
    # Same stimulus for all runs, so common x-axis
    x_axis = range(max_timesteps)
    
    # Create y-axes for three selected comparments
    proximal, intermediate, distal = selectStarburstCompartmentsAlongDendrite(retina, 0) 
    proximal_y_axes     = {heading:[] for heading in headings}
    intermediate_y_axes = {heading:[] for heading in headings}
    distal_y_axes       = {heading:[] for heading in headings}
    for i in range(len(runtime_parameter_settings)):
        for heading in headings:    
            
            activities = starburst_activities[heading][i]
            timesteps = len(activities)
            
            # Grab data for all available existing timesteps
            p_y_axis = [activities[t][0, 0, proximal] for t in range(timesteps)]
            i_y_axis = [activities[t][0, 0, intermediate] for t in range(timesteps)]
            d_y_axis = [activities[t][0, 0, distal] for t in range(timesteps)]
            
            # Padd the data to have a common number of data points
            p_y_axis = p_y_axis + [activities[-1][0, 0, proximal] for t in range(max_timesteps-timesteps)]
            i_y_axis = i_y_axis + [activities[-1][0, 0, proximal] for t in range(max_timesteps-timesteps)]
            d_y_axis = d_y_axis + [activities[-1][0, 0, proximal] for t in range(max_timesteps-timesteps)]
            
            proximal_y_axes[heading].append(p_y_axis)
            intermediate_y_axes[heading].append(i_y_axis)
            distal_y_axes[heading].append(d_y_axis)          
             
             
    # Summary plot
    
    fig = plt.figure(figsize=(11,3/4.0*11.0))
    
    rows, cols, index = 3, 4, 1  
    y_lim = [-1.1, 1.1]
    x_label = "Timesteps"
    y_label = "Activity"
    
    # Rearrange headings so that they display in the order [0, 180, 90, 270]
    headings = [headings[0], headings[2], headings[1], headings[3]]
    for (location_name, data) in [("Proximal", proximal_y_axes), ("Intermediate", intermediate_y_axes), ("Distal", distal_y_axes)]:
        for heading in headings:
            y_axes = data[heading]            
            title = "{0} Degrees, {1} Location".format(int(heading), location_name)
            
            ax = fig.add_subplot(rows, cols, index)
            ax.set_ylim(y_lim)
            ax.set_xlabel(x_label, size='xx-small')
            ax.set_ylabel(y_label, size='xx-small')
            ax.set_title(title, size='xx-small')
            ax.tick_params(labelsize='xx-small')
            lines = []       
            for y_axis in y_axes:
                line, = ax.plot(x_axis, y_axis)
                lines.append(line)
            ax.grid()    
            
            index += 1
            
    ax.legend(lines, runtime_parameter_settings, loc='lower left', prop={'size': 10})

    fig.tight_layout()
    fig_path = os.path.join("Saved Retinas", retina_name, runtime_parameter_name+"_Summary_"+"Activity.pdf")
    fig.savefig(fig_path)
    
    
    # Details moving along a dendrite    
    
    rows, cols, index = len(runtime_parameter_settings), len(headings), 1  
    fig = plt.figure(figsize=(11,float(rows)/cols*11.0))
    
    y_lim = [-1.1, 1.1]
    x_label = "Timesteps"
    y_label = "Activity"
    
    
    for i in range(len(runtime_parameter_settings)):
        for heading in headings:    
            title = "{0} {1}, {2} Degrees".format(runtime_parameter_settings[i], runtime_parameter_name, int(heading))
            ax = fig.add_subplot(rows, cols, index)
            ax.set_ylim(y_lim)
            ax.set_xlabel(x_label, size='xx-small')
            ax.set_ylabel(y_label, size='xx-small')
            ax.set_title(title, size='xx-small')
            ax.tick_params(labelsize='xx-small')
            
            line1, = ax.plot(x_axis, proximal_y_axes[heading][i])
            line2, = ax.plot(x_axis, intermediate_y_axes[heading][i])
            line3, = ax.plot(x_axis, distal_y_axes[heading][i])
            ax.grid()    
            
            index += 1
            
    
    ax.legend(lines, ["Proximal", "Intermediate", "Distal"], loc='lower left', prop={'size': 10})

    fig.tight_layout()
    fig_path = os.path.join("Saved Retinas", retina_name, runtime_parameter_name+"_Along Dendrite_"+"Activity.pdf")
    fig.savefig(fig_path)
    
    
     # Distal Compartments   
    
    rows, cols, index = len(runtime_parameter_settings), 3, 1 
    fig = plt.figure(figsize=(11.0, float(rows)/cols*11.0))
    
    y_lim = [-1.1, 1.1]
    x_label = "Timesteps"
    y_label = "Activity"
    
    
    for i in range(len(runtime_parameter_settings)):
        for (location_name, data) in [("Proximal", proximal_y_axes), ("Intermediate", intermediate_y_axes), ("Distal", distal_y_axes)]:
            title = "{0} {1}, {2} Location".format(runtime_parameter_settings[i], runtime_parameter_name, location_name)
            ax = fig.add_subplot(rows, cols, index)
            ax.set_ylim(y_lim)
            ax.set_xlabel(x_label, size='xx-small')
            ax.set_ylabel(y_label, size='xx-small')
            ax.set_title(title, size='xx-small')
            ax.tick_params(labelsize='xx-small')
            
            lines = []
            for heading in headings:    
                line, = ax.plot(x_axis, data[heading][i])
                lines.append(line)
            ax.grid()    
            
            index += 1
            
    
    ax.legend(lines, headings, loc='lower left', prop={'size': 10})

    fig.tight_layout()
    fig_path = os.path.join("Saved Retinas", retina_name, runtime_parameter_name+"_Distal Compartment_"+"Activity.pdf")
    fig.savefig(fig_path)
    

def analyzeMultipleBarsInOnePage(retina, retina_name, stimulus_name, headings):
    
    retina.loadActivities(retina_name, stimulus_name+"_"+str(int(headings[0])))
    
    center_bipolar_index, center_triad_index = selectCenterOPLCells(retina)
    
    preferred_indicies  = selectStarburstCompartmentsAlongDendrite(retina, 0) 
    null_indicies       = selectStarburstCompartmentsAlongDendrite(retina, 180)
    
    cone_activities             = retina.cone_activities
    horizontal_activities       = retina.horizontal_activities
    bipolar_activities          = retina.on_bipolar_activities 
    center_cone_activity        = []
    center_horizontal_activity  = []
    center_bipolar_activity     = [] 
    
    timesteps = len(cone_activities)
    for t in range(timesteps):
        center_cone_activity.append(cone_activities[t][0, center_triad_index])
        center_horizontal_activity.append(horizontal_activities[t][0, center_triad_index])
        center_bipolar_activity.append(bipolar_activities[t][0, center_bipolar_index])    
    
    preferred_activities        = []
    null_activities             = []
    
    fig     = plt.figure(figsize=(8,8))
    x_axis  = range(timesteps)
    
    drawSingleLineSubplot(fig, 4, 3, 1, x_axis, center_cone_activity, 'Center Photoreceptor Cell')
    drawSingleLineSubplot(fig, 4, 3, 4, x_axis, center_horizontal_activity, 'Center Horizontal Cell')
    drawSingleLineSubplot(fig, 4, 3, 7, x_axis, center_bipolar_activity, 'Center On Bipolar Cell')
    
    for heading in headings:
        retina.loadActivities(retina_name, stimulus_name+"_"+str(int(heading)))
        preferred_activities.append([[],[],[]])
        null_activities.append([[],[],[]])
        for t in range(len(retina.cone_activities)):
            for i in range(3):
                preferred_activities[-1][i].append( retina.on_starburst_activities[t][0][0, preferred_indicies[i]] )
                null_activities[-1][i].append( retina.on_starburst_activities[t][0][0, null_indicies[i]] )
    
    colors = [(.75,0,0),"b","k"]  
    rows = 4
    cols = 3
    for i in range(4):
        y_axes = preferred_activities[i]
        x_axis = range(len(y_axes[0]))
        title = "Preferred "+str(int(headings[i]))
        drawMultilineSubplot(fig, rows, cols, 2+(cols*i), x_axis, y_axes, title, colors)
        
        y_axes = null_activities[i]
        x_axis = range(len(y_axes[0]))
        title = "Null "+str(int(headings[i]))
        drawMultilineSubplot(fig, rows, cols, 3+(cols*i), x_axis, y_axes, title, colors)
    fig.tight_layout()
    fig_path = os.path.join("Saved Retinas", retina_name, stimulus_name+"_"+"Activity Plots.pdf")
    fig.savefig(fig_path)

    saveMorphology(retina, retina_name, stimulus_name, center_triad_index, center_bipolar_index, preferred_indicies, null_indicies)
  
 
def saveMorphology(retina, retina_name, stimulus_name, center_triad_index, center_bipolar_index, preferred_indicies, null_indicies):
     # Draw the morphology with the cells that were graphed highlighted in black
    pygame.init()    
    
    # Figure out scaling
    max_size = Vector2D(1000.0, 1000.0)       
    width_scale = max_size.x / float(retina.grid_width)
    height_scale = max_size.y / float(retina.grid_height)
    scale = min(width_scale, height_scale)    
    
    # Create a minimized display
    display = pygame.display.set_mode(max_size.toIntTuple())
    pygame.display.iconify()
    
    # Print the cone layer to a file
    display.fill((255,255,255))
    color = (0,0,0)
    retina.cone_layer.draw(display, scale=scale)
    radius = int(scale*retina.cone_layer.nearest_neighbor_distance_gridded/2.0)
    x,y = retina.cone_layer.locations[center_triad_index]
    x, y = int(x*scale), int(y*scale)
    pygame.draw.circle(display, color, (x, y), radius) 
    cone_path = os.path.join("Saved Retinas", retina_name, stimulus_name+"_Cone Plot.jpg")
    pygame.image.save(display, cone_path)
    
    # Print the horizontal layer to a file
    display.fill((255,255,255))
    retina.horizontal_layer.draw(display, scale=scale)
    radius = int(scale*retina.horizontal_layer.nearest_neighbor_distance_gridded/2.0)
    x,y = retina.horizontal_layer.locations[center_triad_index]
    x, y = int(x*scale), int(y*scale)
    pygame.draw.circle(display, color, (x, y), radius) 
    horizontal_path = os.path.join("Saved Retinas", retina_name, stimulus_name+"_Horizontal Plot.jpg")
    pygame.image.save(display, horizontal_path)
    
    # Print the bipolar layer to a file
    display.fill((255,255,255))
    retina.on_bipolar_layer.draw(display, scale=scale)
    retina.on_bipolar_layer.neurons[center_bipolar_index].draw(display, retina.on_bipolar_layer.nearest_neighbor_distance_gridded/2.0, color=(0,0,0), scale=scale)
    bipolar_path = os.path.join("Saved Retinas", retina_name, stimulus_name+"_Bipolar Plot.jpg")
    pygame.image.save(display, bipolar_path)
    
    # Print the starburst cell to a file
    display.fill((255,255,255))
    starburst = retina.on_starburst_layer.neurons[0]
    starburst.draw(display, draw_compartments=True, scale=scale)
    transparent_surf = pygame.Surface(max_size.toIntTuple())
    transparent_surf.set_alpha(150)
    transparent_surf.fill((255,255,255))
    display.blit(transparent_surf, (0,0))
    starburst.morphology.location = starburst.location
    for i in range(3):
        starburst.compartments[preferred_indicies[i]].draw(display, color=(255,0,0), scale=scale)
        starburst.compartments[null_indicies[i]].draw(display, color=(0,0,255), scale=scale)
    starburst.morphology.location = Vector2D()
    starburst_path = os.path.join("Saved Retinas", retina_name, stimulus_name+"_Starburst Plot.jpg")
    pygame.image.save(display, starburst_path)

def drawSingleLineSubplot(fig, rows, cols, index, x_axis, y_axis, title, grid=True,
                          y_lim=[-1.1, 1.1], x_label='Timesteps', y_label='Activity'):
    ax = fig.add_subplot(rows, cols, index)
    ax.plot(x_axis, y_axis)
    ax.set_ylim(y_lim)
    ax.set_xlabel(x_label, size='xx-small')
    ax.set_ylabel(y_label, size='xx-small')
    ax.set_title(title, size='xx-small')
    ax.tick_params(labelsize='xx-small')
    if grid: ax.grid()
    
def drawMultilineSubplot(fig, rows, cols, index, x_axis, y_axes, title, colors, grid=True,
                          y_lim=[-1.1, 1.1], x_label='Timesteps', y_label='Activity'):
    ax = fig.add_subplot(rows, cols, index)
    ax.set_ylim(y_lim)
    ax.set_xlabel(x_label, size='xx-small')
    ax.set_ylabel(y_label, size='xx-small')
    ax.set_title(title, size='xx-small')
    ax.tick_params(labelsize='xx-small')
    for y_axis, color in zip(y_axes, colors):
        ax.plot(x_axis, y_axis, color=color)
    if grid: ax.grid()                   
    
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
    
def selectCenterOPLCells(retina):
    w, h = retina.grid_width,retina.grid_height
    retina_center = Vector2D(w/2.0, h/2.0)
    
    bipolar_layer   = retina.on_bipolar_layer
    number_bipolars = bipolar_layer.number_neurons
    
    index_closest_to_center     = -1
    index_distance_to_center    = w*h
    number_tries                = 0
    max_tries                   = 200
    while number_tries < max_tries:
        random_bipolar_index    = randint(0, number_bipolars-1)
        random_bipolar          = bipolar_layer.neurons[random_bipolar_index]
        if len(random_bipolar.inputs) != 0:
            new_distance = random_bipolar.location.distanceTo(retina_center)
            if new_distance < index_distance_to_center:
                index_closest_to_center = random_bipolar_index
                index_distance_to_center = new_distance
        number_tries += 1
    
    center_bipolar_index = index_closest_to_center
    if index_closest_to_center == -1: 
        center_triad_index = randint(0, retina.cone_layer.neurons-1)
        print "No valid bipolars found that have inputs from triads"
    else:
        center_bipolar          = bipolar_layer.neurons[center_bipolar_index]
        center_triad_ID         = center_bipolar.inputs[0][0]
        center_triad_x          = int(center_triad_ID.split('.')[0])
        center_triad_y          = int(center_triad_ID.split('.')[1])
        
        for i in range(retina.cone_layer.neurons):
            if retina.cone_layer.locations[i] == [center_triad_x, center_triad_y]:
                center_triad_index = i
                break
    
    return center_bipolar_index, center_triad_index
