import matplotlib.pyplot as plt
import numpy as np
   
    
x_axis = range(50)


decay = 0.5
input_amount = 1.0
equilibrium_potential = 1.0


decay_2 = 0.5


# ((1 - decay_2) + x) = 1 - np.abs(input_amount)



y_axis_1 = [0.0]
y_axis_2 = [0.0]
for x in x_axis[:-1]: 
    y_axis_1.append( (1 - decay) * (1 - np.abs(input_amount)) * y_axis_1[-1] + (input_amount) * equilibrium_potential )
    y_axis_2.append( ((1 - decay) * (1 - np.abs(input_amount)) * y_axis_1[-1] + (input_amount) * equilibrium_potential)/((1 - decay) * (1 - np.abs(input_amount))  + input_amount))


fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1,1,1)

ax.plot(x_axis, y_axis_1)
ax.plot(x_axis, y_axis_2)
ax.set_xlabel("Time")
ax.set_ylabel("Charge")

plt.show()