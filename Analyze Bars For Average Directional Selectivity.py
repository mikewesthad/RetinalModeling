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
    
    trial_proxmial_DSIs                         = []
    trial_distal_DSIs                           = []
    trial_proxmial_vector_magnitudes            = []
    trial_distal_vector_magnitudes              = []
    trial_proxmial_preferred_centrifigualities  = []
    trial_distal_preferred_centrifigualities    = []
    trial_proxmial_vector_centrifigualities     = []
    trial_distal_vector_centrifigualities       = []
    
    
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
                
            trial_proxmial_DSIs.append(proximal_DSIs)
            trial_distal_DSIs.append(distal_DSIs)
            trial_proxmial_vector_magnitudes.append(proximal_vector_magnitudes)
            trial_distal_vector_magnitudes.append(distal_vector_magnitudes)
            trial_proxmial_preferred_centrifigualities.append(proximal_preferred_centrifugalities)
            trial_distal_preferred_centrifigualities.append(distal_preferred_centrifugalities)
            trial_proxmial_vector_centrifigualities.append(proximal_vector_centrifugalities)
            trial_distal_vector_centrifigualities.append(distal_vector_centrifugalities)
                    
    results = [trial_proxmial_DSIs, trial_distal_DSIs, 
               trial_proxmial_vector_magnitudes, trial_distal_vector_magnitudes, 
               trial_proxmial_preferred_centrifigualities, trial_distal_preferred_centrifigualities,
               trial_proxmial_vector_centrifigualities, trial_distal_vector_centrifigualities,
               trial_DSIs]
    return results
                
    

def analyze(trial_path, retina_paths, number_stimulus_variations, number_bars):
            
    results = calculateData(retina_paths, number_stimulus_variations, number_bars) 
    trial_proxmial_DSIs                         = results[0]
    trial_distal_DSIs                           = results[1]
    trial_proxmial_vector_magnitudes            = results[2]
    trial_distal_vector_magnitudes              = results[3]
    trial_proxmial_preferred_centrifigualities  = results[4]
    trial_distal_preferred_centrifigualities    = results[5]
    trial_proxmial_vector_centrifigualities     = results[6]
    trial_distal_vector_centrifigualities       = results[7]
#    trial_DSIs                                  = results[8]
    
    number_retinas  = len(retina_paths)
#    number_trials   = number_retinas * number_stimulus_variations
    
    fig1_rows, fig1_cols, fig1_index = 2, 2, 1
    fig1 = createFigure(12.0, fig1_rows, fig1_cols)
    diffusion_radii         = [180, 210, 240, 270, 300, 330, 360, 390]
    diffusion_radii_ticks   = [diffusion_radii[0]-10] + diffusion_radii + [diffusion_radii[-1]+10] 
    DSI_ticks               = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
    DSI_tick_labels         = ["{0:.2}".format(x) for x in DSI_ticks]    
    CI_ticks                = [-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    CI_tick_labels          = ["{0:.2}".format(x) for x in CI_ticks]
    AVM_ticks               = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]
    AVM_tick_labels         = ["{0:.2}".format(x) for x in AVM_ticks] 
    
    
        
    average_proximal_DSIs = []
    stdev_proximal_DSIs = []
    average_proximal_preferred_centrifugalities = []
    stdev_proximal_preferred_centrifugalities = []
    
    average_distal_DSIs = []
    stdev_distal_DSIs = []
    average_distal_preferred_centrifugalities = []
    stdev_distal_preferred_centrifugalities = []
    
    average_proximal_vector_magnitudes = []
    stdev_proximal_vector_magnitudes = []
    average_proximal_vector_centrifugalities = []
    stdev_proximal_vector_centrifugalities = []
    
    average_distal_vector_magnitudes = []
    stdev_distal_vector_magnitudes = []
    average_distal_vector_centrifugalities = []
    stdev_distal_vector_centrifugalities = []
    
    stimulus_number = 0
    for retina_number in range(number_retinas):
        
        index = retina_number * number_stimulus_variations + stimulus_number
        
        ave = np.mean(trial_proxmial_DSIs[index])
        stdv = np.std(trial_proxmial_DSIs[index])
        average_proximal_DSIs.append(ave)
        stdev_proximal_DSIs.append(stdv)
        
        ave = np.mean(trial_proxmial_preferred_centrifigualities[index])
        stdv = np.std(trial_proxmial_preferred_centrifigualities[index])
        average_proximal_preferred_centrifugalities.append(ave)
        stdev_proximal_preferred_centrifugalities.append(stdv)
        
        ave = np.mean(trial_distal_DSIs[index])
        stdv = np.std(trial_distal_DSIs[index])
        average_distal_DSIs.append(ave)
        stdev_distal_DSIs.append(stdv)
        
        ave = np.mean(trial_distal_preferred_centrifigualities[index])
        stdv = np.std(trial_distal_preferred_centrifigualities[index])
        average_distal_preferred_centrifugalities.append(ave)
        stdev_distal_preferred_centrifugalities.append(stdv)
        
        
        ave = np.mean(trial_proxmial_vector_magnitudes[index])
        stdv = np.std(trial_proxmial_vector_magnitudes[index])
        average_proximal_vector_magnitudes.append(ave)
        stdev_proximal_vector_magnitudes.append(stdv)
        
        ave = np.mean(trial_proxmial_vector_centrifigualities[index])
        stdv = np.std(trial_proxmial_vector_centrifigualities[index])
        average_proximal_vector_centrifugalities.append(ave)
        stdev_proximal_vector_centrifugalities.append(stdv)
        
        ave = np.mean(trial_distal_vector_magnitudes[index])
        stdv = np.std(trial_distal_vector_magnitudes[index])
        average_distal_vector_magnitudes.append(ave)
        stdev_distal_vector_magnitudes.append(stdv)
        
        ave = np.mean(trial_distal_vector_centrifigualities[index])
        stdv = np.std(trial_distal_vector_centrifigualities[index])
        average_distal_vector_centrifugalities.append(ave)
        stdev_distal_vector_centrifugalities.append(stdv)
            
    y1_color        = (0,0,1)
    y1_err_color    = (0,0,1,0.3)
    y2_color        = (1,0,0)
    y2_err_color    = (1,0,0,0.3)
#        dot_size        = 6
#        error_width     = 1.5
    
    x = diffusion_radii
    
    
    # Plot one - proximal DSIs and CIs
    y1      = average_proximal_DSIs
    y1_err  = stdev_proximal_DSIs
    y1_max  = np.array(y1) + np.array(y1_err)
    y1_min  = np.array(y1) - np.array(y1_err)
    y2      = average_proximal_preferred_centrifugalities
    y2_err  = stdev_proximal_preferred_centrifugalities
    y2_max  = np.array(y2) + np.array(y2_err)
    y2_min  = np.array(y2) - np.array(y2_err)
    
    print x
    print y1
    
    ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
    ax.plot(x, y1, ls='-', color=y1_color)
    ax.fill_between(x, y1_min, y1_max, color=y1_err_color)        
    ax.set_title("Proximal Compartments", size=14)
    ax.set_xlabel("Diffusion Radius (um)", size=12)
    ax.set_ylabel("DSI", color='b', size=12)
    ax2 = ax.twinx()
    ax2.plot(x, y2, ls='-', color=y2_color)
    ax2.fill_between(x, y2_min, y2_max, color=y2_err_color)        
    ax2.set_ylabel("Centrifugality Index", color='r', size=12)
    
#        ax.errorbar(bar_speeds, average_proximal_DSIs, yerr=stdev_proximal_DSIs, fmt='.', color=y1_color, ls='-', markersize=dot_size, ecolor=y1_err_color, elinewidth=error_width)
#        ax2.errorbar(bar_speeds_shifted, average_proximal_preferred_centrifugalities, yerr=stdev_proximal_preferred_centrifugalities, fmt='.', color=y2_color, ls='-', markersize=dot_size, ecolor=y2_err_color, elinewidth=error_width)

    ax.set_xticks(diffusion_radii_ticks)
    ax.set_xticklabels(diffusion_radii_ticks, rotation=70, size=10)
    ax2.set_xticks(diffusion_radii_ticks)
    ax2.set_xticklabels(diffusion_radii_ticks, rotation=70, size=10)
    ax.set_yticks(DSI_ticks)
    ax.set_yticklabels(DSI_tick_labels, size=11, color='b')
    ax2.set_yticks(CI_ticks)
    ax2.set_yticklabels(CI_tick_labels, size=11, color='r')
    ax.set_xlim([diffusion_radii_ticks[0], diffusion_radii_ticks[-1]])
    ax.set_ylim([DSI_ticks[0], DSI_ticks[-1]])
    ax2.set_ylim([CI_ticks[0], CI_ticks[-1]])
    fig1_index += 1  
    
    
    
    # Plot two - distal DSIs and CIs
    y1      = average_distal_DSIs
    y1_err  = stdev_distal_DSIs
    y1_max  = np.array(y1) + np.array(y1_err)
    y1_min  = np.array(y1) - np.array(y1_err)
    y2      = average_distal_preferred_centrifugalities
    y2_err  = stdev_distal_preferred_centrifugalities
    y2_max  = np.array(y2) + np.array(y2_err)
    y2_min  = np.array(y2) - np.array(y2_err)
    ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
    ax.plot(x, y1, ls='-', color=y1_color)
    ax.fill_between(x, y1_min, y1_max, color=y1_err_color)    
    ax.set_title("Distal Compartments", size=14)
    ax.set_xlabel("Diffusion Radius (um)", size=12)
    ax.set_ylabel("DSI", color='b', size=12)
    ax2 = ax.twinx()
    ax2.plot(x, y2, ls='-', color=y2_color)
    ax2.fill_between(x, y2_min, y2_max, color=y2_err_color)   
    ax2.set_ylabel("Centrifugality Index", color='r', size=12)
    
#        ax.errorbar(bar_speeds_shifted, average_distal_DSIs, yerr=stdev_distal_DSIs, fmt='.', color=y1_color, ls='-', markersize=dot_size, ecolor=y1_err_color, elinewidth=error_width)
#        ax2.errorbar(bar_speeds, average_distal_preferred_centrifugalities, yerr=stdev_distal_preferred_centrifugalities, fmt='.', color=y2_color, ls='-', markersize=dot_size, ecolor=y2_err_color, elinewidth=error_width)

    ax.set_xticks(diffusion_radii_ticks)
    ax.set_xticklabels(diffusion_radii_ticks, rotation=70, size=10)
    ax2.set_xticks(diffusion_radii_ticks)
    ax2.set_xticklabels(diffusion_radii_ticks, rotation=70, size=10)
    ax.set_yticks(DSI_ticks)
    ax.set_yticklabels(DSI_tick_labels, size=11, color='b')
    ax2.set_yticks(CI_ticks)
    ax2.set_yticklabels(CI_tick_labels, size=11, color='r')
    ax.set_xlim([diffusion_radii_ticks[0], diffusion_radii_ticks[-1]])
    ax.set_ylim([DSI_ticks[0], DSI_ticks[-1]])
    ax2.set_ylim([CI_ticks[0], CI_ticks[-1]])
    fig1_index += 1  
            
    
    # Plot three - proximal AVMs and CIs
    y1      = average_proximal_vector_magnitudes
    y1_err  = stdev_proximal_vector_magnitudes
    y1_max  = np.array(y1) + np.array(y1_err)
    y1_min  = np.array(y1) - np.array(y1_err)
    y2      = average_proximal_vector_centrifugalities
    y2_err  = stdev_proximal_vector_centrifugalities
    y2_max  = np.array(y2) + np.array(y2_err)
    y2_min  = np.array(y2) - np.array(y2_err)
    ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
    ax.plot(x, y1, ls='-', color=y1_color)
    ax.fill_between(x, y1_min, y1_max, color=y1_err_color)   
    ax.set_title("Proximal Compartments", size=14)
    ax.set_xlabel("Diffusion Radius (um)", size=12)
    ax.set_ylabel("AVM", color='b', size=12)
    ax2 = ax.twinx()
    ax2.plot(x, y2, ls='-', color=y2_color)
    ax2.fill_between(x, y2_min, y2_max, color=y2_err_color)   
    ax2.set_ylabel("Centrifugality Index", color='r', size=12)
    
#        ax.errorbar(bar_speeds, average_proximal_vector_magnitudes, yerr=stdev_proximal_vector_magnitudes, fmt='.', color=y1_color, ls='-', markersize=dot_size, ecolor=y1_err_color, elinewidth=error_width)
#        ax2.errorbar(bar_speeds_shifted, average_proximal_vector_centrifugalities, yerr=stdev_proximal_vector_centrifugalities, fmt='.', color=y2_color, ls='-', markersize=dot_size, ecolor=y2_err_color, elinewidth=error_width)
    
    ax.set_xticks(diffusion_radii_ticks)
    ax.set_xticklabels(diffusion_radii_ticks, rotation=70, size=10)
    ax2.set_xticks(diffusion_radii_ticks)
    ax2.set_xticklabels(diffusion_radii_ticks, rotation=70, size=10)
    ax.set_yticks(AVM_ticks)
    ax.set_yticklabels(AVM_tick_labels, size=11, color='b')
    ax2.set_yticks(CI_ticks)
    ax2.set_yticklabels(CI_tick_labels, size=11, color='r')
    ax.set_xlim([diffusion_radii_ticks[0], diffusion_radii_ticks[-1]])
    ax.set_ylim([AVM_ticks[0], AVM_ticks[-1]])
    ax2.set_ylim([CI_ticks[0], CI_ticks[-1]])
    fig1_index += 1  
    
    
    
    # Plot three - distal AVMs and CIs
    y1      = average_distal_vector_magnitudes
    y1_err  = stdev_distal_vector_magnitudes
    y1_max  = np.array(y1) + np.array(y1_err)
    y1_min  = np.array(y1) - np.array(y1_err)
    y2      = average_distal_vector_centrifugalities
    y2_err  = stdev_distal_vector_centrifugalities
    y2_max  = np.array(y2) + np.array(y2_err)
    y2_min  = np.array(y2) - np.array(y2_err)
    ax = fig1.add_subplot(fig1_rows, fig1_cols, fig1_index)
    ax.plot(x, y1, ls='-', color=y1_color)
    ax.fill_between(x, y1_min, y1_max, color=y1_err_color) 
    ax.set_title("Distal Compartments", size=14)
    ax.set_xlabel("Diffusion Radius (um)", size=12)
    ax.set_ylabel("AVM", color='b', size=12)
    ax2 = ax.twinx()
    ax2.plot(x, y2, ls='-', color=y2_color)
    ax2.fill_between(x, y2_min, y2_max, color=y2_err_color)  
    ax2.set_ylabel("Centrifugality Index", color='r', size=12)
    
#        ax.errorbar(bar_speeds_shifted, average_distal_vector_magnitudes, yerr=stdev_distal_vector_magnitudes, fmt='.', color=y1_color, ls='-', markersize=dot_size, ecolor=y1_err_color, elinewidth=error_width)
#        ax2.errorbar(bar_speeds, average_distal_vector_centrifugalities, yerr=stdev_distal_vector_centrifugalities, fmt='.', color=y2_color, ls='-', markersize=dot_size, ecolor=y2_err_color, elinewidth=error_width)
    
    ax.set_xticks(diffusion_radii_ticks)
    ax.set_xticklabels(diffusion_radii_ticks, rotation=70, size=10)
    ax2.set_xticks(diffusion_radii_ticks)
    ax2.set_xticklabels(diffusion_radii_ticks, rotation=70, size=10)
    ax.set_yticks(AVM_ticks)
    ax.set_yticklabels(AVM_tick_labels, size=11, color='b')
    ax2.set_yticks(CI_ticks)
    ax2.set_yticklabels(CI_tick_labels, size=11, color='r')
    ax.set_xlim([diffusion_radii_ticks[0], diffusion_radii_ticks[-1]])
    ax.set_ylim([AVM_ticks[0], AVM_ticks[-1]])
    ax2.set_ylim([CI_ticks[0], CI_ticks[-1]])
    fig1_index += 1  
    

    fig1.tight_layout(pad=2.0, w_pad=6.0, h_pad=3.0)
    fig1_path = os.path.join(trial_path, "Directional Selectivity Results.jpg")
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
trial_name = "Bar_Diffusion_Batch_Large"
number_bars = 12
number_stimulus_variations = 1

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