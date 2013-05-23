import numpy as np
import matplotlib.pyplot as plt
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
        plt.rgrids([0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        ax.plot(theta, datum, color=color)
        ax.fill(theta, datum, facecolor=color, alpha=0.25)
        ax.set_varlabels(spoke_labels)

    plt.figtext(0.5, 0.965, 'Title Title Title',
                ha='center', color='black', weight='bold', size='large')
    plt.show()
    
    
def activity_plot(data, x_axis, labels):
    fig     = plt.figure()
    ax      = fig.add_subplot(111)
    colors  = [(.75,0,0),"b","k"]
    
    for datum, color in zip(data, colors):
        ax.plot(x_axis*100,datum,color=color)
        
    leg = ax.legend(labels, 'lower left', shadow=True)
    
    min_y = np.min(data) - 1
    max_y = np.max(data) + 1
    ax.set_ylim([min_y, max_y])
    
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Activity')
    ax.set_title('Activity Over Time')
        
    # matplotlib.text.Text instances
    for t in leg.get_texts():
        t.set_fontsize('small')    # the legend text fontsize
    
    # matplotlib.lines.Line2D instances
    for l in leg.get_lines():
        l.set_linewidth(1.5)  # the legend line width
        
    plt.show()

def example_radar_data(number_directions):    
    # Create the string names for the different headings    
    division    = int(360/number_directions)
    angle_names = [str(angle) for angle in range(0, 360, division)]
    import random
    data = [['column names', angle_names],
            ['Compartment 1', [random.random() for i in range(number_directions)]],
            ['Compartment 2', [random.random() for i in range(number_directions)]],
            ['Compartment 3', [random.random() for i in range(number_directions)]],
            ['Compartment 4', [random.random() for i in range(number_directions)]]]
    return data


def example_activity_data():
    labels = ["Proximal 10 um", "Intermediate 75 um", "Distal 135 um"]
    max_time = .150
    x_axis = np.arange(0, max_time, 0.001)
    
    proximal        = np.sin(x_axis*100)*5
    intermediate    = np.exp(x_axis*15)-4
    distal          = np.log(x_axis*100+0.1)
    
    data = [proximal, intermediate, distal]
    
    return data, x_axis, labels
    
    
    
    

if __name__ == '__main__':
    
    number_directions = 9    
    
    data = example_radar_data(number_directions)
    radar_plot(data)
    
    data, x_axis, labels = example_activity_data()
    activity_plot(data, x_axis, labels)
    
    
    