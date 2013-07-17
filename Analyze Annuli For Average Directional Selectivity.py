import os
import matplotlib.pyplot as plt
from random import randint 
import matplotlib.image as mpimg
import numpy as np
import matplotlib

def createFigure(long_side_size, rows, cols):
    width, height = long_side_size, long_side_size
    if rows > cols:
        width *= float(cols)/float(rows)
    elif cols > rows:
        height *= float(rows)/float(cols)
    return plt.figure(figsize=(width, height))


def calculateData(retina_paths, number_stimulus_variations, proximal_distance, distal_distance):
    
    number_retinas  = len(retina_paths)
    number_trials   = number_retinas * number_stimulus_variations
    
    trial_centroids = []
    trial_compartment_lengths = []
    trial_compartment_headings = []
    trial_directional_preferences_from_max = []
    trial_directional_preferences_from_min = []
    
    trial_proxmial_dp_max  = []
    trial_proxmial_dp_min  = []
    trial_distal_dp_max    = []
    trial_distal_dp_min    = []
    
    # Display variables
    pygame.init()    
    max_size            = Vector2D(1000.0, 1000.0)  
    background_color    = (25, 25, 25)
    morphology_color    = (255, 255, 255)
    distal_color        = (255, 25, 25)
    interm_color        = (25, 255, 255)
    proximal_color      = (25, 255, 25)
    
    for retina_path in retina_paths:
        retina = Retina.loadRetina(retina_path)
        starburst = retina.on_starburst_layer.neurons[0]
        number_compartments = len(starburst.compartments)
        
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
        morphology_path = os.path.join(retina_path, "Morphology.jpg")
        pygame.image.save(display, morphology_path)
        
        for trial_number in range(number_stimulus_variations):            
            retina.loadActivities(retina_path, str(trial_number)+"_centripetal")
            cp_activities = retina.on_starburst_activities[:, 0, 0, :]        
            retina.loadActivities(retina_path, str(trial_number)+"_centrifugal")
            cf_activities = retina.on_starburst_activities[:, 0, 0, :]
            
            timesteps = np.shape(cf_activities)[0]
            half_time = int(timesteps / 2)
            
            # Only look at activities after the model has been given time to settle
            cp_maxes    = np.max(cp_activities[half_time:,:], axis=0)
            cf_maxes    = np.max(cf_activities[half_time:,:], axis=0)            
            cp_mins     = np.min(cp_activities[half_time:,:], axis=0)
            cf_mins     = np.min(cf_activities[half_time:,:], axis=0)
                
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
            directional_preferences_from_max = []
            directional_preferences_from_min = []
            for compartment_index in range(number_compartments):
                cp = float(cp_maxes[compartment_index])
                cf = float(cf_maxes[compartment_index])
                directional_preference_from_max = (cf - cp)/(cf + cp)
                directional_preferences_from_max.append(directional_preference_from_max)
                
                cp = float(cp_mins[compartment_index])
                cf = float(cf_mins[compartment_index])
                directional_preference_from_min = (cf - cp)/(cf + cp)
                directional_preferences_from_min.append(directional_preference_from_min)
            trial_directional_preferences_from_max.append(directional_preferences_from_max)
            trial_directional_preferences_from_min.append(directional_preferences_from_min)    
            
          
            # Calculate the average dp for proximal and distal parts of cell
            proxmial_dp_max  = []
            proxmial_dp_min  = []
            distal_dp_max    = []
            distal_dp_min    = []
            
            for compartment_index in range(number_compartments):
                compartment_length = compartment_lengths[compartment_index]
                if compartment_length <= proximal_distance:        
                    proxmial_dp_max.append(directional_preferences_from_max[compartment_index])
                    proxmial_dp_min.append(directional_preferences_from_min[compartment_index])
                    
                elif compartment_length >= distal_distance:       
                    distal_dp_max.append(directional_preferences_from_max[compartment_index])
                    distal_dp_min.append(directional_preferences_from_min[compartment_index])
                
            trial_proxmial_dp_max.append(proxmial_dp_max)
            trial_proxmial_dp_min.append(proxmial_dp_min)
            trial_distal_dp_max.append(distal_dp_max)
            trial_distal_dp_min.append(distal_dp_min)
            
            
            # Draw the vector averages over the morphology
            def drawDirectionalPreferences(display, use_max=True):
                if use_max: preferences = directional_preferences_from_max
                else:       preferences = directional_preferences_from_min
                max_preference = float(max(abs(max(preferences)), abs(min(preferences))))
                    
                for index in range(number_compartments):
                    
                    # Find the centroid of the compartment
                    centroid = centroids[index]   
                    centroid = scale * (centroid + starburst.morphology.location)
                    
                    # Draw a vector in the CF/CP direction with magnitude set by DP
                    magnitude           = preferences[index]/max_preference * 50.0
                    cf_heading          = compartment_headings[index]
                    direction_vector    = Vector2D.generateHeadingFromAngle(cf_heading) * magnitude 
                    
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
                label = font.render("{0:.3}".format(max_preference), True, (255,255,255))
                label_rectangle = label.get_rect()
                label_rectangle.center  = (810,825)
                display.blit(label, label_rectangle)
            
            image_path = os.path.join(retina_path, str(trial_number)+" Max Directional Preferences Morphology.jpg")
            display.fill(background_color)
            drawDirectionalPreferences(display, True)     
            pygame.image.save(display, image_path)
            image_path = os.path.join(retina_path, str(trial_number)+" Min Directional Preferences Morphology.jpg")
            display.fill(background_color)
            drawDirectionalPreferences(display, False)     
            pygame.image.save(display, image_path)
            
    results = [trial_centroids, trial_compartment_lengths, trial_compartment_headings,
               trial_directional_preferences_from_max, trial_directional_preferences_from_min,
               trial_proxmial_dp_max, trial_proxmial_dp_min, trial_distal_dp_max, trial_distal_dp_max]
    return results
                

def analyzeIndividualTrials(retina_paths, number_stimulus_variations, proximal_distance=150.0/3.0, distal_distance=2.0/3.0*150.0):
    
    results = calculateData(retina_paths, number_stimulus_variations, proximal_distance, distal_distance)
    
    plot_label_props    = dict(boxstyle='round', facecolor='white', alpha=1.0)
    plot_label_x        = 0.05
    plot_label_y        = 0.95
    plot_label_size     = 20
    
    x_tick_size         = 12
    x_label_size        = 16
    y_label_size        = 16
    y_tick_size         = 12
    title_size          = 20
    
    retina_number = 0
    for retina_path in retina_paths:
        
        for trial_number in range(number_stimulus_variations):     
    
            index = retina_number * number_stimulus_variations + trial_number
            
            lengths = results[1][index]
            DPs     = results[3][index]
            
            proximal_DPs    = []
            distal_DPs      = []
            
            number_compartments = len(lengths)    
            for i in range(number_compartments):
                length = lengths[i]
                if length <= proximal_distance:        
                    proximal_DPs.append(DPs[i])
                elif length >= distal_distance:       
                    distal_DPs.append(DPs[i])
            
            abs_max_DP = max(abs(max(DPs)), abs(min(DPs)))
            
            fig_rows, fig_cols = 3, 2
            fig = createFigure(17.0, fig_rows, fig_cols)
            grid_size = (fig_rows, fig_cols)
            
            DP_morphology_path  = os.path.join(retina_path, str(trial_number)+" Max Directional Preferences Morphology.jpg")
            DP_morphology_image = mpimg.imread(DP_morphology_path)
            DP_morphology_image = DP_morphology_image[100:900, 100:900]
            ax = plt.subplot2grid(grid_size, (0,0), colspan=2, rowspan=2)
            ax.imshow(DP_morphology_image)
            ax.set_title("Directional Preference in Response to Annuli",size=title_size)
            ax.axis('off')          
            plt.text(plot_label_x, plot_label_y, "A", transform=ax.transAxes, 
                     fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
            
            proximal_color      = (25/255.0, 1.0, 25/255.0)
            distal_color        = (1.0, 25/255.0, 25/255.0)
            
            ax = plt.subplot2grid(grid_size, (2, 0))
            ax.hist(proximal_DPs, bins=20, color=proximal_color, range=[-abs_max_DP, abs_max_DP])
            ax.set_title("{0} {1} Histogram".format("Proximal", "DP"),size=title_size)
            ax.set_xlabel("DP",size=x_label_size)
            ax.set_ylabel("Frequency",size=y_label_size)
            ax.set_ylim([0, 30])
            ax.set_yticklabels(plt.yticks()[0], rotation=0, size=x_tick_size)
            ax.set_xticklabels(plt.xticks()[0], rotation=70, size=y_tick_size)
            plt.text(plot_label_x, plot_label_y, "B", transform=ax.transAxes, 
                     fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
            
            ax = plt.subplot2grid(grid_size, (2, 1))
            ax.hist(distal_DPs, bins=20, color=distal_color, range=[-abs_max_DP, abs_max_DP])
            ax.set_title("{0} {1} Histogram".format("Distal", "DP"),size=title_size)
            ax.set_xlabel("DP",size=x_label_size)
            ax.set_ylabel("Frequency",size=y_label_size)
            ax.set_ylim([0, 30])
            ax.set_yticklabels(plt.yticks()[0], rotation=0, size=y_tick_size)
            ax.set_xticklabels(plt.xticks()[0], rotation=70, size=x_tick_size)
            plt.text(plot_label_x, plot_label_y, "C", transform=ax.transAxes, 
                     fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)
                        
            fig.tight_layout()
            fig_path = os.path.join(retina_path, str(trial_number)+" Histogram Results.jpg")
            fig.savefig(fig_path)  
            
            
                
        retina_number += 1
        
        
def analyzeAcrossTrials(trial_name, retina_paths, number_stimulus_variations, proximal_distance=150.0/3.0, distal_distance=2.0/3.0*150.0):
    
    results = calculateData(retina_paths, number_stimulus_variations, proximal_distance, distal_distance)

    number_trials = len(retina_paths)*number_stimulus_variations
    fig_rows, fig_cols, fig_index = 1, 1, 1
    fig = createFigure(10.0, fig_rows, fig_cols)
    
    ave_proximal_DPs = []
    sd_proximal_DPs = []
    ave_distal_DPs = []
    sd_distal_DPs = []                
    
    retina_number = 0
    for retina_path in retina_paths:
        for trial_number in range(number_stimulus_variations):         
            index = retina_number * number_stimulus_variations + trial_number
            
            lengths = results[1][index]
            DPs = results[3][index]
            
            proximal_DPs    = []
            distal_DPs      = []
            
            number_compartments = len(lengths)    
            for i in range(number_compartments):
                length = lengths[i]
                if length <= proximal_distance:        
                    proximal_DPs.append(DPs[i])
                elif length >= distal_distance:       
                    distal_DPs.append(DPs[i])
        
            ave_proximal_DPs.append(np.mean(proximal_DPs))
            sd_proximal_DPs.append(np.std(proximal_DPs))
            ave_distal_DPs.append(np.mean(distal_DPs))
            sd_distal_DPs.append(np.std(distal_DPs))
        
        retina_number += 1    
            
    proximal_color      = (25/255.0, 1.0, 25/255.0)
    proximal_err_color  = (25/255.0, 1.0, 25/255.0, 0.3)
    distal_color        = (1.0, 25/255.0, 25/255.0)
    distal_err_color    = (1.0, 25/255.0, 25/255.0, 0.3)
    
    x = range(number_trials) 
    
    y1      = ave_proximal_DPs
    y1_err  = sd_proximal_DPs
    y1_max  = np.array(y1) + np.array(y1_err)
    y1_min  = np.array(y1) - np.array(y1_err)
    y2      = ave_distal_DPs
    y2_err  = sd_distal_DPs
    y2_max  = np.array(y2) + np.array(y2_err)
    y2_min  = np.array(y2) - np.array(y2_err)  
    
    ax = fig.add_subplot(fig_rows, fig_cols, fig_index)
    ax.plot(x, y1, ls='-', color=proximal_color)
    ax.fill_between(x, y1_min, y1_max, color=proximal_err_color)        
    ax.set_title("Proximal and Distal DP", size=14)
    ax.set_xlabel("Trial Number", size=12)
    ax.set_ylabel("DP", size=12)
    ax.plot(x, y2, ls='-', color=distal_color)
    ax.fill_between(x, y2_min, y2_max, color=distal_err_color)   
    
    ax.set_ylim([-0.25, 0.25])
    ax.set_xticklabels(plt.xticks()[0], rotation=70, size=10)
    ax.set_yticklabels(plt.yticks()[0], size=10)
                
    fig.tight_layout()
    fig_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name, "Across Trial DP Results.jpg")
    fig.savefig(fig_path)  
            
    
    


from Constants import *
trial_name = "Annuli_Test_Batch_6"
number_stimulus_variations = 1

trial_path = os.path.join(os.getcwd(), "Saved Retinas", trial_name)
entries = os.listdir(trial_path)
retina_paths = []
for entry in entries:
    path_to_entry = os.path.join(trial_path, entry)
    if os.path.isdir(path_to_entry):
        retina_paths.append(path_to_entry)

        
analyzeIndividualTrials(retina_paths, number_stimulus_variations)