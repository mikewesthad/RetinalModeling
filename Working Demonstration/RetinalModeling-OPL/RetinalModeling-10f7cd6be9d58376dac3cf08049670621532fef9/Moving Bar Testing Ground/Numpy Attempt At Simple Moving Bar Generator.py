import numpy as np

"""
Builds a simple moving bar movie - the bar appears on one side of the screen and moves until it reaches the
opposite side.

It has parameters:
    movieWidth, movieHeight - size of movie in pixels
    framerate - frames per second
    orientation - the direction of the bar motion (restricted to 0, 90, 180, 270 degrees)
    barWidth, barHeight - size of the bar in pixels
    barSpeed - pixels per second that the bar moves
    

The function outputs an 3D array of intensity values over frames
"""

def buildMovingBarMovie(framerate, movieWidth, movieHeight,
                        barOrientation, barWidth, barHeight, barSpeed):


    x, y            = 0.0, 0.0      # the upper left coordinates of the box
    dx, dy          = 0.0, 0.0      # the change in x and y positions per frame
    numberFrames    = 0
    
    if barOrientation >= 0 and barOrientation < 90:
        dx              = barSpeed
        x               = -barWidth
        y               = int((movieHeight-barHeight)/2.0)
        numberFrames    = (movieWidth+1+barWidth) / barSpeed * framerate
    else:
        return -1

    movieFrames = np.zeros((numberFrames, movieHeight, movieWidth))
    for f in numberFrames:
        movieFrames[f, 0:5, 0:5] = 


buildMovingBarMovie(30.0, 20, 20, 0, 2, 5, 1.0)
    
    
