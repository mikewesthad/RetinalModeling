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


#decay = 0.1
#input_amount = 1.0
#equilibrium_potential = 1.0
#
#conductance = input_amount/8.0
#
#
#y_axis = [0.0]
#y_axis2 = [0.1]
#for x in x_axis[:-1]: 
#    last_activity = y_axis[-1]
#    new_activity = (1 - decay) * (1 - np.abs(conductance)) * last_activity + (conductance) * equilibrium_potential 
#    y_axis.append(new_activity)
    
       

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1,1,1)

x_axis, y_axis = runModel(0.0, 0.0, 1.0, 1.0) 
ax.plot(x_axis, y_axis)

x_axis, y_axis = runModel(0.5, 0.0, 1.0, 1.0) 
ax.plot(x_axis, y_axis)


ax.set_xlabel("Time")
ax.set_ylabel("Charge")

plt.show()