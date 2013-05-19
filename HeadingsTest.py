import math
import numpy as np
from Constants import *


def generateBarStimulus(framerate=60, movie_size=(400,400), bar_orientation=0,
                       bar_size=(20, 600), bar_speed=100, bar_movement_distance=600,
                       bar_position=(0,0), bar_color=(0,0,0), background_color=(255,255,255), 
                       position_on_retina=(0,0), pixel_size_in_rgu=1):
    
    bar_movie = RuntimeBarGenerator(framerate=framerate, movie_size=movie_size,
                                    bar_orientation=bar_orientation, 
                                    bar_size=bar_size, bar_speed=bar_speed, 
                                    bar_movement_distance=bar_movement_distance,
                                    bar_position=bar_position, bar_color=bar_color,
                                    background_color=background_color,
                                    minimize=False)
    
    stimulus = Stimulus(position_on_retina=position_on_retina,
                        pixel_size_in_rgu=pixel_size_in_rgu, movie=bar_movie)

    return stimulus                           
    pass

bars = 8
w = 400
h = 400

bar_headings = np.arange(0.0, 360.0, 360.0/bars) 

# Find the circle that contains the screen
radius = ((w/2.0)**2.0+(h/2.0)**2.0)**0.5

bar_positions = []
for heading in bar_headings:
    opposite_heading = heading - 180
    if opposite_heading < 0: opposite_heading = heading + 180
    
    print heading,opposite_heading,
    y = radius * math.sin(opposite_heading*math.pi/180.0) + h/2.0
    x = radius * math.cos(opposite_heading*math.pi/180.0) + w/2.0
    print x,y
    bar_positions.append((x,y))
print bar_positions

hw = int(w/2.0)
hh = int(h/2.0)
print [(0, hh), (hw, 0), (w, hh), (hw, h)]     


for heading, position in zip(bar_headings, bar_positions):
    stimulus = generateBarStimulus(bar_orientation = heading, 
                                   bar_position = position)
    stimulus.play()

