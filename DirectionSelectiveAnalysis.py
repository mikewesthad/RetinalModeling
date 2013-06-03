import os
import matplotlib.pyplot as plt
from random import randint 
import numpy as np
import matplotlib 
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection


def radar_factory(num_vars):    
    # calculate evenly-spaced axis angles
    theta = 2*np.pi * np.linspace(0, 1-1./num_vars, num_vars)
    
    class RadarAxes(PolarAxes):
        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(theta * 180/np.pi, labels, size='xx-small')

        def _gen_axes_patch(self):
            return plt.Circle((0.5, 0.5), 0.5)

        def _gen_axes_spines(self):
            return PolarAxes._gen_axes_spines(self)

    register_projection(RadarAxes)
    return theta


def radar_plot(headings, compartment_data):
    spoke_labels = headings
    N = len(headings)
    theta = radar_factory(N)
    fig = plt.figure(figsize=(11, 11))
    fig.subplots_adjust(wspace=0.25, hspace=0.25, top=0.85, bottom=0.05)
    matplotlib.rc('ytick', labelsize=6)
    color = 'r'
    
    rows = len(compartment_data)
    cols = 3
    index = 1
    
    for row in range(rows):
        for col in range(cols):
            title, datum = compartment_data[row][col]
            ax = fig.add_subplot(rows, cols, index, projection='radar')
            ax.set_ylim([0.0, 1.0])
            ax.set_title(title, weight='bold', size='xx-small', position=(0.5, 1.1),
                         horizontalalignment='center', verticalalignment='center')
            ax.plot(theta, datum, color=color)
            ax.fill(theta, datum, facecolor=color, alpha=0.25)
            ax.set_varlabels(spoke_labels)
            index += 1
            
#    plt.figtext(0.5, 0.965, 'Title Title Title',
#                ha='center', color='black', weight='bold', size='large')
    return fig

def analyzeStarburst(retina, retina_name, headings, stimulus_name):
    
    # Create a save folder for this retina and stimulus    
    save_path = os.path.join("Directionally Selective Analysis", retina_name+"_"+stimulus_name)
    if not(os.path.exists(save_path)): os.mkdir(save_path)
    
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
        while not(has_reached_soma):
            proximal_neighbors = last_compartment.proximal_neighbors
            last_compartment = proximal_neighbors[0]
            if last_compartment in starburst.morphology.master_compartments:
                has_reached_soma = True
            length += step_size
        compartment_lengths.append(length)
        
    # Calculate angular heading from soma for each compartment (based on centroid)
    compartment_headings = []
    for index in range(number_compartments):
        centroid = centroids[index]
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
        
        
        
    # Create a (scaled) pygame display
    pygame.init()    
    max_size = Vector2D(1000.0, 1000.0)       
    width_scale = max_size.x / float(retina.grid_width)
    height_scale = max_size.y / float(retina.grid_height)
    scale = min(width_scale, height_scale)   
    starburst.morphology.location = max_size/scale/2.0
    display = pygame.display.set_mode(max_size.toIntTuple())
    background_color = (25, 25, 25)
    morphology_color = (255, 255, 255)
    line_color = (243, 134, 48)
    circle_color = (250, 105, 0)
        
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
    
#    running=True
#    draw_morphology = True
#    while running:
#        for event in pygame.event.get():
#            if event.type == QUIT:
#                 running = False
#            if event.type == KEYDOWN:
#                draw_morphology = not(draw_morphology)
#                
#        display.fill(background_color)
#        drawDSI(display, draw_morphology, morphology_color, line_color, circle_color)            
#        pygame.display.update()
    
    # Save the DSI drawings
    DSI_morphology_path = os.path.join(save_path, "DSI_Morphology.jpg")
    display.fill(background_color)
    drawDSI(display, True, morphology_color, line_color, circle_color)     
    pygame.image.save(display, DSI_morphology_path)
    DSI_no_morphology_path = os.path.join(save_path, "DSI_No_Morphology.jpg")
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
        
#    running=True
#    draw_morphology = True
#    while running:
#        for event in pygame.event.get():
#            if event.type == QUIT:
#                 running = False
#            if event.type == KEYDOWN:
#                draw_morphology = not(draw_morphology)
#                
#        display.fill(background_color)
#        drawVectorAverages(display, draw_morphology, morphology_color, line_color, circle_color)            
#        pygame.display.update()
    
    # Save the vector average drawings
    average_morphology_path = os.path.join(save_path, "Vector_Average_Morphology.jpg")
    display.fill(background_color)
    drawVectorAverages(display, True, morphology_color, line_color, circle_color)     
    pygame.image.save(display, average_morphology_path)
    average_no_morphology_path = os.path.join(save_path, "Vector_Average_No_Morphology.jpg")
    display.fill(background_color)
    drawVectorAverages(display, False, morphology_color, line_color, circle_color)     
    pygame.image.save(display, average_no_morphology_path)
        
        
        

    fig = plt.figure(figsize=(20, 20))
    rows = 4
    cols = 3
    index = 1
    
    data = []
    max_response = 0.0
    for angle in [0, 90, 180, 270]:    
        proximal, intermediate, distal = selectStarburstCompartmentsAlongDendrite(retina, angle)
        data.append([['Proximal', [np.max(all_activities[i,:,proximal]) for i in range(number_headings)]],
                    ['Intermedate', [np.max(all_activities[i,:,intermediate]) for i in range(number_headings)]],
                    ['Distal', [np.max(all_activities[i,:,distal]) for i in range(number_headings)]]])
        
        for compartment in [proximal, intermediate, distal]:
            ax = fig.add_subplot(rows, cols, index)
            x_axis = range(max_timesteps)
            for i in range(number_headings):
                y_axis = all_activities[i, :, compartment]
                ax.plot(x_axis, y_axis)
            ax.legend(headings, loc=1, prop={'size':12})
            index += 1
            
            
    fig.tight_layout()
    fig_path = os.path.join(save_path, "Traces.jpg")
    fig.savefig(fig_path)
            
    fig2 = radar_plot(headings, data)
    fig2_path = os.path.join(save_path, "Radar.jpg")
    fig2.savefig(fig2_path)
    
    rows, cols, index = 2, 4, 1
    fig3 = plt.figure(figsize=(20, 2.0*20/4.0))
    matplotlib.rc('xtick', labelsize=12)
    matplotlib.rc('ytick', labelsize=12)
    
    ax = fig3.add_subplot(rows, cols, index)
    ax.hist(preferred_centrifigualities, bins=20, range=(-1.0, 1.0))
    ax.set_title("Preferred Heading")
    ax.set_xlabel("Centrifugality Index")
    ax.set_ylabel("Frequency")
    index += 1    
    
    ax = fig3.add_subplot(rows, cols, index)
    ax.scatter(preferred_centrifigualities, compartment_lengths, alpha=0.25)
    ax.set_title("Preferred Heading")
    ax.set_ylabel("Distance from Soma")
    ax.set_xlabel("Centrifugality Index")
    index += 1    
    
    ax = fig3.add_subplot(rows, cols, index)
    ax.scatter(preferred_centrifigualities, DSIs, alpha=0.25)
    ax.set_title("Preferred Heading")
    ax.set_ylabel("Magnitude of DSI")
    ax.set_xlabel("Centrifugality Index")
    index += 1    
    
    ax = fig3.add_subplot(rows, cols, index)
    ax.scatter(compartment_lengths, DSIs, alpha=0.25)
    ax.set_title("Preferred Heading")
    ax.set_ylabel("Magnitude of DSI")
    ax.set_xlabel("Distance from soma")
    index += 1    
    
    ax = fig3.add_subplot(rows, cols, index)
    ax.hist(vector_average_centrifigualities, bins=20, range=(-1.0, 1.0))
    ax.set_title("Average Heading")
    ax.set_xlabel("Centrifugality Index")
    ax.set_ylabel("Frequency")
    index += 1    
    
    ax = fig3.add_subplot(rows, cols, index)
    ax.scatter(vector_average_centrifigualities, compartment_lengths, alpha=0.25)
    ax.set_title("Average Heading")
    ax.set_ylabel("Distance from Soma")
    ax.set_xlabel("Centrifugality Index")
    index += 1    
    
    ax = fig3.add_subplot(rows, cols, index)
    ax.scatter(vector_average_centrifigualities, vector_average_magnitudes, alpha=0.25)
    ax.set_title("Average Heading")
    ax.set_ylabel("Magnitude of Vector Average")
    ax.set_xlabel("Centrifugality Index")  
    index += 1      
    
    ax = fig3.add_subplot(rows, cols, index)
    ax.scatter(compartment_lengths, vector_average_magnitudes, alpha=0.25)
    ax.set_title("Average Heading")
    ax.set_ylabel("Magnitude of Vector Average")
    ax.set_xlabel("Distance from soma")
    index += 1    
    
    fig3.tight_layout()
    fig3_path = os.path.join(save_path, "Centrifiguality.jpg")
    fig3.savefig(fig3_path)
    
    
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
#retina_name = "12 Direction - 100 FPS Remove Stutter From Floating Point Inaccuracies Increased Diffusion Radius (Best DS 5-22-13)"
#retina_name = "12 Direction - 100 FPS Remove Stutter From Floating Point Inaccuracies Increased Diffusion Radius (Longer stimulus time)"
retina_name = "2"
retina = Retina.loadRetina(retina_name)

for stim_name in ["0","12","24","36","48","60"]:
    analyzeStarburst(retina, retina_name, np.arange(0.0, 360.0, 360.0/12.0) , stim_name)