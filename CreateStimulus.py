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


def createMultipleBars(framerate, movie_width, movie_height,
                       bar_width, bar_height, bar_speed, bar_movement_distance, 
                       pixel_size_in_rgu):
              
    bars = 4
    bar_headings = np.arange(0.0, 360.0, 90.0) 
    
    w = movie_width
    h = movie_height
    hw = int(movie_width/2.0)
    hh = int(movie_height/2.0)
    bar_positions = [(0, hh), (hw, 0), (w, hh), (hw, h)]                
                            
    bar_color               = (255, 255, 255)          
    background_color        = (0, 0, 0)
    position_on_retina      = (0.0, 0.0)                # rgu
    
    stimuli = []
    for i in range(bars):
        bar_heading     = bar_headings[i]   
        bar_position    = bar_positions[i]  
        
        bar_movie = RuntimeBarGenerator(framerate=framerate, movie_size=(movie_width, movie_height),
                                        bar_orientation=bar_heading, 
                                        bar_size=(bar_width, bar_height), bar_speed=bar_speed, 
                                        bar_movement_distance=bar_movement_distance,
                                        bar_position=bar_position, bar_color=bar_color,
                                        background_color=background_color)
        
        stimulus = Stimulus(position_on_retina=position_on_retina,
                            pixel_size_in_rgu=pixel_size_in_rgu, movie=bar_movie)
                            
        stimuli.append(stimulus)
        
                        
    stimulus_string = ""
    stimulus_string += "\tMovie Size (pixels)\t({0:.1f}, {1:.1f})\n".format(movie_width, movie_height)    
    stimulus_string += "\tBar Position (pixels)\t({0:.1f}, {1:.1f})\n".format(bar_position[0], bar_position[1])             
    stimulus_string += "\tBar Size (pixels)\t({0:.1f}, {1:.1f})\n".format(bar_width, bar_height)   
    stimulus_string += "\tBar Speed (p/s)\t\t{0:.1f}\n".format(bar_speed)                     
    stimulus_string += "\tBar Color (rgb)\t({0:.1f}, {1:.1f}, {2:.1f})\n".format(*bar_color)  
    stimulus_string += "\tBackground Color (rgb)\t({0:.1f}, {1:.1f}, {2:.1f})\n".format(*background_color)    
    stimulus_string += "\tPixel Size (rgu)\t{0:.3f}\n".format(pixel_size_in_rgu)                        
        
        
    return stimuli, bar_headings, stimulus_string