"""
Example of creating a radar chart (a.k.a. a spider or star chart) [1]_.

Although this example allows a frame of either 'circle' or 'polygon', polygon
frames don't have proper gridlines (the lines are circles instead of polygons).
It's possible to get a polygon grid by setting GRIDLINE_INTERPOLATION_STEPS in
matplotlib.axis to the desired number of vertices, but the orientation of the
polygon is not aligned with the radial axes.

.. [1] http://en.wikipedia.org/wiki/Radar_chart
"""
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection


def radar_factory(num_vars):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    """
    
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


def example_data():    
    # Create the string names for the different headings    
    division    = int(360/9)
    angle_names = [str(angle) for angle in range(0, 360, division)]
    
    data = [['column names', angle_names],
            ['Compartment 1', [0.88, 0.01, 0.03, 0.03, 0.00, 0.06, 0.01, 0.00, 0.00]],
            ['Compartment 2', [0.02, 0.02, 0.11, 0.47, 0.69, 0.58, 0.88, 0.00, 0.00]],
            ['Compartment 3', [0.01, 0.02, 0.86, 0.27, 0.16, 0.19, 0.00, 0.00, 0.00]],
            ['Compartment 4', [1.5, 0.95, 0.02, 0.03, 0.00, 0.01, 0.13, 0.06, 0.00]]]
            
    return data


if __name__ == '__main__':
    N = 9
    theta = radar_factory(N)

    data = example_data()
    spoke_labels = data.pop(0)[1]

    fig = plt.figure(figsize=(9, 9))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    color = 'r'
    
    # Plot the four cases from the example data on separate axes
    for index in range(len(data)):
        title, datum = data[index]
        ax = fig.add_subplot(2, 2, index, projection='radar', )
        plt.rgrids([0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        ax.plot(theta, datum, color=color)
        ax.fill(theta, datum, facecolor=color, alpha=0.25)
        ax.set_varlabels(spoke_labels)

    plt.figtext(0.5, 0.965, '5-Factor Solution Profiles Across Four Scenarios',
                ha='center', color='black', weight='bold', size='large')
    plt.show()