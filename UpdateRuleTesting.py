import matplotlib
import matplotlib.pyplot as plt
import numpy as np
   


def runModel(starting_activity, decay, input_amount, equilibrium_potential,
             timesteps=30, conductance_factor=1.0/8.0):
    conductance = input_amount * conductance_factor
    
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
#
#print y_axis
#print explicitFormulae(0, 0.25, conductance) - explicitFormulae(0, 0.0, conductance)
#print explicitFormulae(1, 0.25, conductance) - explicitFormulae(1, 0.0, conductance)
#print explicitFormulae(2, 0.25, conductance) - explicitFormulae(2, 0.0, conductance)
#print explicitFormulae(29, 0.25, conductance) - explicitFormulae(29, 0.0, conductance)

x_tick_size         = 12
x_label_size        = 16
y_label_size        = 16
y_tick_size         = 12
title_size          = 20


matplotlib.rcParams['xtick.major.pad'] = 9
matplotlib.rcParams['ytick.major.pad'] = 9
fig = plt.figure(figsize=(18, 9))
ax = fig.add_subplot(1,2,1)


conductance_factors = [0.1, 0.3, 0.5, 0.7, 0.9]
colors = [(20.0/255.0,0,100/255.0), (20.0/255.0,50/255.0,100/255.0), (20.0/255.0,100/255.0,150/255.0), (20.0/255.0,150/255.0,200/255.0), (20.0/255.0,200/255.0,250/255.0)]
colors.reverse()
handles = []
for (conductance_factor, color) in zip(conductance_factors, colors): 
    x_axis, y_axis = runModel(0.0, 0.1, 1.0, 1.0, 30, conductance_factor) 
    
    _, max_value = runModel(0.0, 0.1, 1.0, 1.0, 30000, conductance_factor)
    max_value = max_value[-1]
    
    fraction = 0.99
    target_value = fraction * max_value
    timestep_of_target = 0
    for i in range(len(y_axis)):
        if y_axis[i] >= target_value:
            timestep_of_target = x_axis[i]
            actual_target_value = y_axis[i]
            break
    
    line, = ax.plot(x_axis, y_axis, color=color, lw=2)
    ax.axvline(x=timestep_of_target, ymin=0, ymax=actual_target_value/1.0, color=color, ls='--', lw=1.0, zorder=0)
    handles.append(line)

leg = ax.legend(handles, ["Conductance = {0}".format(x) for x in conductance_factors], loc="lower right", fontsize=16)
leg.legendHandles[0].set_linewidth(2.5)

ax.set_title("Varying Conductance", size=title_size)
ax.set_ylim([0, 1])
ax.set_xlim([0, 29])
ax.set_xticklabels(ax.get_xticks(), size=x_tick_size)
ax.set_yticklabels(ax.get_yticks(), size=y_tick_size)
ax.set_xlabel("Timesteps", size=x_label_size)
ax.set_ylabel("Activity", size=y_label_size)

plot_label_props    = dict(boxstyle='round', facecolor='white', alpha=0.9)
plot_label_x        = 0.025
plot_label_y        = 0.975
plot_label_size     = 20
plt.text(plot_label_x, plot_label_y, "A", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)


ax = fig.add_subplot(1,2,2)
conductance_factor = 0.5
start_activities = [0.0, 0.4, 0.8]
colors = [(20.0/255.0,0,100/255.0), (20.0/255.0,100/255.0,150/255.0), (20.0/255.0,200/255.0,250/255.0)]
colors.reverse()
handles = []
for (start_activity, color) in zip(start_activities, colors): 
    x_axis, y_axis = runModel(start_activity, 0.1, 1.0, 1.0, 8, conductance_factor) 
    line, = ax.plot(x_axis, y_axis, color=color, lw=2)
    handles.append(line)

leg = ax.legend(handles, ["Starting Activity = {0}".format(x) for x in start_activities], loc="lower right", fontsize=16)
leg.legendHandles[0].set_linewidth(2.5)

ax.set_title("Varying Initital Activity Level", size=title_size)
ax.set_ylim([0, 1])
ax.set_xlim([0, 7])
ax.set_xticklabels(ax.get_xticks(), size=x_tick_size)
ax.set_yticklabels(ax.get_yticks(), size=y_tick_size)
ax.set_xlabel("Timesteps", size=x_label_size)
ax.set_ylabel("Activity", size=y_label_size)

plt.text(plot_label_x, plot_label_y, "B", transform=ax.transAxes, 
         fontsize=plot_label_size, verticalalignment="top", bbox=plot_label_props)

fig_path = "Varying Conductance in Lone Compartment.jpg"
fig.savefig(fig_path)    