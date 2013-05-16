import os
import matplotlib.pyplot as plt
import numpy as np
from Constants import *
from random import randint


def selectStarburstCompartmentsAlongDendrite(morphology):
    
    acceptable_compartment = False
    while not(acceptable_compartment):        
        random_compartment_index = randint(0, len(morphology.compartments)-1)
        random_compartment = morphology.compartments[random_compartment_index]
        
        # Check if terminal compartment        
        if random_compartment.distal_neighbors == []:
            acceptable_compartment = True
            terminal_compartment = random_compartment
            
    dendrite_path = [terminal_compartment]
    has_reached_soma = False
    while not(has_reached_soma):
        most_proximal_compartment = dendrite_path[0]
        proximal_neighbors = most_proximal_compartment.proximal_neighbors
        new_proximal_compartment = proximal_neighbors[0]
        dendrite_path.insert(0, new_proximal_compartment)        
        if new_proximal_compartment in morphology.master_compartments:
            has_reached_soma = True
        
    number_compartments = len(dendrite_path)
    
    proximal        = dendrite_path[0]
    intermediate    = dendrite_path[int(round(number_compartments/2.0))]
    distal          = dendrite_path[-1]
    return proximal.index, intermediate.index, distal.index           

directory_name = "0"

retina = Retina.loadRetina(directory_name)

morphology  = retina.on_starburst_layer.morphologies[0]
distances   = morphology.distances
weights     = morphology.diffusion_weights
step_size   = morphology.step_size

proximal, intermediate, distal = selectStarburstCompartmentsAlongDendrite(morphology)

max_distance = np.max(distances)
bins = max_distance/step_size * 2.0

p_histogram, b = np.histogram(distances[proximal, :], bins=bins, range=(0, max_distance))
i_histogram, b = np.histogram(distances[intermediate, :], bins=bins, range=(0, max_distance))
d_histogram, b = np.histogram(distances[distal, :], bins=bins, range=(0, max_distance))
max_frequency = np.max(np.concatenate((p_histogram, i_histogram, d_histogram))) + 5

fig = plt.figure(figsize=(8,8))
rows, cols, index = 3, 3, 1

ax = fig.add_subplot(rows, cols, index)
ax.hist(distances[proximal, :], bins=bins, range=(0, max_distance))
ax.set_ylim([0, max_frequency])
ax.set_xlabel("Distance", size='small')
ax.set_ylabel("Frequency", size='small')
ax.set_title("Proximal", size='small')
ax.tick_params(labelsize='small')
index += 1

ax = fig.add_subplot(rows, cols, index)
ax.hist(distances[intermediate, :], bins=bins, range=(0, max_distance))
ax.set_ylim([0, max_frequency])
ax.set_xlabel("Distance", size='small')
ax.set_ylabel("Frequency", size='small')
ax.set_title("Intermediate", size='small')
ax.tick_params(labelsize='small')
index += 1

ax = fig.add_subplot(rows, cols, index)
ax.hist(distances[distal, :], bins=bins, range=(0, max_distance))
ax.set_ylim([0, max_frequency])
ax.set_xlabel("Distance", size='small')
ax.set_ylabel("Frequency", size='small')
ax.set_title("Distal", size='small')
ax.tick_params(labelsize='small')
index += 1


plt.show()




# Vertical Lines

#fig = plt.figure(figsize=(8,8))
#
#ax = fig.add_subplot(1,1,1)
#x = np.arange(0,50,1)
#y = np.sin(x)
#ax.plot(x, y)
#ax.axvline(15, -1.1, 1.1, color='k', linestyle="--")
#ax.axvline(25, -1.1, 1.1, color='k', linestyle="--")
#
#plt.show()
   
   