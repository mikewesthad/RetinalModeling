from Constants import *

def createBarStimulus(framerate, movie_width, movie_height, bar_orientation,
                       bar_width, bar_height, bar_speed, bar_movement_distance, 
                       pixel_size_in_rgu):
                                 
    bar_position            = (int(movie_width/2.0), int(movie_height/2.0))        
    bar_color               = (0, 0, 0)         
    background_color        = (255, 255, 255) 
    bar_movie = RuntimeBarGenerator(framerate=framerate, movie_size=(movie_width, movie_height),
                                    bar_orientation=bar_orientation, 
                                    bar_size=(bar_width, bar_height), bar_speed=bar_speed, 
                                    bar_movement_distance=bar_movement_distance,
                                    bar_position=bar_position, bar_color=bar_color,
                                    background_color=background_color)
    
    position_on_retina      = (0.0, 0.0)                # rgu
    stimulus = Stimulus(position_on_retina=position_on_retina,
                        pixel_size_in_rgu=pixel_size_in_rgu, movie=bar_movie)
                        
    stimulus_string = ""
    stimulus_string += "\tMovie Size (pixels)\t({0:.1f}, {1:.1f})\n".format(movie_width, movie_height) 
    stimulus_string += "\tBar Size (pixels)\t({0:.1f}, {1:.1f})\n".format(bar_width, bar_height)   
    stimulus_string += "\tBar Speed (p/s)\t\t{0:.1f}\n".format(bar_speed)             
    stimulus_string += "\tPixel Size (rgu)\t{0:.3f}\n".format(pixel_size_in_rgu)                        

    return stimulus, stimulus_string     


