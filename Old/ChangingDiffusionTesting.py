import matplotlib.pyplot as plt
import numpy as np


# Take a compartment's distance from the soma, a curve type and curve parameters
# and calculate the diffusion width (sigma) for that compartment
def changingDiffusionSigma(distance, curve_type, curve_parameters):
    
    if curve_type.lower() == "linear":
        start_sigma, end_sigma = curve_parameters
        min_distance = 0.0
        max_distance = 150.0
        percent_distance = (distance - min_distance) / (max_distance - min_distance)
        sigma = percent_distance * (end_sigma - start_sigma) + start_sigma
        
    elif curve_type.lower() == "exponential":
        start_sigma, base = curve_parameters
        sigma = start_sigma * base ** distance
        
    elif curve_type.lower() == "sigmoidal":
        center, width, start_sigma, end_sigma = curve_parameters
        sigma = (end_sigma - start_sigma) * 1.0 / (1.0 + np.exp(-(distance-center)/width)) + start_sigma
        
    return sigma
    
    
x_axis = np.arange(0, 150, 1)

y_axis = []
for x in x_axis: 
#    y_axis.append(changingDiffusionSigma(x, "Linear", [0.0, 200.0]))
#    y_axis.append(changingDiffusionSigma(x, "Linear", [150.0, 1.0]))
    y_axis.append(changingDiffusionSigma(x, "Exponential", [150.0, 0.96]))
#    y_axis.append(changingDiffusionSigma(x, "Sigmoidal", [75.0, 15.0, 150.0, 1.0]))



fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1,1,1)

ax.plot(x_axis, y_axis)
ax.set_xlabel("Distance")
ax.set_ylabel("Sigma")
plt.show()