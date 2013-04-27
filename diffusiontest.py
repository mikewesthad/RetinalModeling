import numpy as np

activities  = np.array([0, 0, 0, 0, 10, 0, 0, 0], dtype=np.float64)
components  = np.shape(activities)[0]

# Create a distance matrix where nearest neighbors have a distance of 0
distance = np.zeros((components, components))
for x in range(components):
    for y in range(components):
        distance[x,y] = abs(x-y) - 1

# Create a weight matrix...
#   Each row represents a components output weights
#   Each row is a gaussian over distance where the nearest neighbor has a distance of 0
#   The guassian is normalized so that the sum is 1.0
width           = 0.25
weights         = np.exp(-distance**2.0/(2.0*width**2.0))
row_sum         = np.sum(weights, 1)
row_sum.shape   = (components, 1)
weights         /= row_sum

np.set_printoptions(precision=3, suppress=True, linewidth=300)
print weights
print activities, np.sum(activities)

diffusion_strength = 0.5
debug = False
for x in range(10):
    
    new_activities = np.zeros(activities.shape)
    for component in range(components):
        
        # Current component's activity
        component_activity = activities[component]
        
        # Difference in activity between current component and everyone else
        differences = (component_activity - activities) 
        differences *= diffusion_strength  
        differences *= weights[component, :]          
        
        # Zero out negative differences
        negative_difference_indicies = differences < 0
        differences[negative_difference_indicies] = 0
        
        # Update the activity values
        total_differences = np.sum(differences)
        if (total_differences > 0):            
            new_activities += differences
            new_activities[component] += component_activity - total_differences
        else:
            new_activities[component] += component_activity
        
    activities = new_activities
    print activities, sum(activities)
            



            

# Generate a larger activities list for time testing
#components = 1000
#lst = []
#import random
#for x in range(components):
#    lst.append(random.randint(0,1))
#activities = np.array(lst, dtype=np.float64)
            

## Current component's activity
#component_activity      = activities[component]   
#
## Indicies of connected components and their activities
#connected_components    = connections[component]
#num_connected           = np.shape(connected_components)[0]
#connected_activities    = activities[connections[component]]
#
## Difference in activity between current and connections
#connected_differences = component_activity - connected_activities 
#
## Zero out negative differences
#negative_difference_indicies = connected_differences < 0
#connected_differences[negative_difference_indicies] = 0
#
## Normalize differences
#connected_differences /= num_connected
#
## Adjust the strength of diffusion
#connected_differences *= diffusion_strength
#
## Total the outgoing diffusion
#total_outgoing = sum(connected_differences)
#
#new_activities[connected_components]    += connected_differences
#new_activities[component]               += component_activity - total_outgoing
#
#if debug:
#    print activities
#    print new_activities
#    print component
#    print component_activity
#    print connected_components
#    print num_connected
#    print connected_activities
#    print connected_differences
#    raw_input()
#    