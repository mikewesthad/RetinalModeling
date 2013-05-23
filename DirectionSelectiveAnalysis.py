import matplotlib.pyplot as plt
from random import randint 
import numpy as np

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
            self.set_thetagrids(theta * 180/np.pi, labels)

        def _gen_axes_patch(self):
            return plt.Circle((0.5, 0.5), 0.5)

        def _gen_axes_spines(self):
            return PolarAxes._gen_axes_spines(self)

    register_projection(RadarAxes)
    return theta


def radar_plot(data):
    spoke_labels = data.pop(0)[1]
    N = len(spoke_labels)
    theta = radar_factory(N)
    fig = plt.figure(figsize=(9, 9))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    color = 'r'
    
    # Plot the four cases from the example data on separate axes
    for index in range(len(data)):
        title, datum = data[index]
        ax = fig.add_subplot(2, 2, index, projection='radar')
        plt.rgrids([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        ax.plot(theta, datum, color=color)
        ax.fill(theta, datum, facecolor=color, alpha=0.25)
        ax.set_varlabels(spoke_labels)

    plt.figtext(0.5, 0.965, 'Title Title Title',
                ha='center', color='black', weight='bold', size='large')
    plt.show()

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
        pygame.draw.line(display, (255,0,0), start_point, end_point, 3)
        pygame.draw.circle(display, (255,0,0), average_compartment_position.toIntTuple(), 4)
        
    pygame.display.update()
    
    running=True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                 running = False
        pygame.display.update()
        
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
        
        # Draw the vector average of the responses in each direction
        index = compartment.index
        vector_average = Vector2D()
        for heading, heading_index in zip(headings, range(len(headings))):
            vector_average = vector_average + Vector2D.generateHeadingFromAngle(float(heading)) * np.max(all_activities[heading_index,:,index])
        vector_average = vector_average / float(len(headings))
            
        vector_average = vector_average * 1000.0
        
        # Find the centroid of the compartment
        average_compartment_position = Vector2D()
        num_positions = len(compartment.gridded_locations)
        for pos in compartment.gridded_locations: 
            average_compartment_position = average_compartment_position + (pos * scale)
        average_compartment_position = max_size/2.0 + (average_compartment_position / num_positions) 
        
        # Find the start and end of the line
        start_point = average_compartment_position.toTuple()
        end_point = (average_compartment_position + vector_average).toTuple()
        pygame.draw.line(display, (255,0,0), start_point, end_point, 3)
        pygame.draw.circle(display, (255,0,0), average_compartment_position.toIntTuple(), 4)
        
    pygame.display.update()
    
    running=True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                 running = False
        pygame.display.update()     
        
        
        
        
    proximal, intermediate, distal = selectStarburstCompartmentsAlongDendrite(retina, 0)
    
#    compartment = compartment_lengths.index(max(compartment_lengths))
    compartment = distal
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x_axis = range(max_timesteps)
    for i in range(number_headings):
        y_axis = all_activities[i, :, compartment]
        ax.plot(x_axis, y_axis)
    ax.legend(headings)
    plt.show()
    
    
    data = [['column names', headings],
            ['Proximal', [np.max(all_activities[i,:,proximal]) for i in range(number_headings)]],
            ['Intermedate', [np.max(all_activities[i,:,intermediate]) for i in range(number_headings)]],
            ['Distal', [np.max(all_activities[i,:,distal]) for i in range(number_headings)]]]
            
    radar_plot(data)
    
    
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
retina_name = "0"
retina = Retina.loadRetina(retina_name)

analyzeStarburst(retina, retina_name, np.arange(0.0, 360.0, 360.0/12.0) , "0")