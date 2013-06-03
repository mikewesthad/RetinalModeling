import matplotlib.pyplot as plt
import numpy as np
   


def runModel(starting_activity, decay, input_amount, equilibrium_potential,
             timesteps=30):
    conductance = input_amount/8.0
    
    x_axis = range(timesteps)
    y_axis = [starting_activity]
    for x in x_axis[:-1]:
        last_activity = y_axis[-1]
        new_activity = (1 - decay) * (1 - np.abs(conductance)) * last_activity + (conductance) * equilibrium_potential 
        y_axis.append(new_activity)
    
    return x_axis, y_axis
    
def explicitFormulae(time, start_activity, conductance):
    activity = (1.0-conductance)**time * start_activity
    for t in range(0, time):
        activity += (1.0-conductance)**t * conductance
    return activity


decay = 0.0
input_amount = 1.0
equilibrium_potential = 1.0
conductance = input_amount/8.0
starting_activity = 0.0

x_axis, y_axis = runModel(starting_activity, decay, input_amount, 1.0)

print y_axis
print explicitFormulae(0, 0.25, conductance) - explicitFormulae(0, 0.0, conductance)
print explicitFormulae(1, 0.25, conductance) - explicitFormulae(1, 0.0, conductance)
print explicitFormulae(2, 0.25, conductance) - explicitFormulae(2, 0.0, conductance)
print explicitFormulae(29, 0.25, conductance) - explicitFormulae(29, 0.0, conductance)

#fig = plt.figure(figsize=(10, 10))
#ax = fig.add_subplot(1,1,1)
#
#x_axis, y_axis = runModel(0.0, 0.0, 1.0, 1.0) 
#ax.plot(x_axis, y_axis)
#
#x_axis, y_axis = runModel(0.5, 0.0, 1.0, 1.0) 
#ax.plot(x_axis, y_axis)
#
#
#ax.set_xlabel("Time")
#ax.set_ylabel("Charge")
#
#plt.show()