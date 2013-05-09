from Constants import *

def generateBarStimulus(framerate, movie_width, movie_height, bar_orientation,
                       bar_width, bar_height, bar_speed, bar_movement_distance,
                       bar_position, bar_color, background_color, 
                       position_on_retina, pixel_size_in_rgu):
    
    bar_movie = RuntimeBarGenerator(framerate=framerate, movie_size=movie_size,
                                    bar_orientation=bar_orientation, 
                                    bar_size=bar_size, bar_speed=bar_speed, 
                                    bar_movement_distance=bar_movement_distance,
                                    bar_position=bar_position, bar_color=bar_color,
                                    background_color=background_color)
    
    stimulus = Stimulus(position_on_retina=position_on_retina,
                        pixel_size_in_rgu=pixel_size_in_rgu, movie=bar_movie)

    return stimulus                           
    pass


