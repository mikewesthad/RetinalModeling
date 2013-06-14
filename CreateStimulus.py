from Constants import *
import math

def createAnnulus(direction, pixel_size_in_rgu, framerate, duration, stimulus_frequency,
                 max_radius, radius_filter_factor, width_filter_factor):
    annulus = RuntimeAnnulusGenerator(framerate=framerate, duration=duration, 
                                      direction=direction,
                                      stimulus_frequency=stimulus_frequency,
                                      max_radius=max_radius,
                                      radius_filter_factor=radius_filter_factor,
                                      width_filter_factor=width_filter_factor) 
    annulus_stimulus = Stimulus(position_on_retina=(0,0), pixel_size_in_rgu=pixel_size_in_rgu, movie=annulus)
    return annulus_stimulus

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

def createManyBars(bars, framerate, movie_width, movie_height,
                   bar_width, bar_height, bar_speed, bar_movement_distance, 
                   pixel_size_in_rgu):
            
    bar_headings = np.arange(0.0, 360.0, 360.0/bars) 
    
    # Find the circle that contains the screen
    w = movie_width
    h = movie_height
    radius = ((w/2.0)**2.0+(h/2.0)**2.0)**0.5
    
    # Calculate the bar starting positions based on their heading by
    # finding the point on the circle opposite the direction of motion
    bar_positions = []
    for heading in bar_headings:
        opposite_heading = heading - 180
        if opposite_heading < 0: opposite_heading = heading + 180
        y = radius * math.sin(opposite_heading*math.pi/180.0) + h/2.0
        x = radius * math.cos(opposite_heading*math.pi/180.0) + w/2.0
        bar_positions.append((x,y))            
                            
    bar_color               = (255, 255, 255)          
    background_color        = (0, 0, 0)
    position_on_retina      = (0.0, 0.0)                # rgu
    
    stimuli = []
    for i in range(int(bars)):
        bar_heading     = bar_headings[i]   
        bar_position    = bar_positions[i]  
        
#        print "Generating bar at ({0},{1})".format(bar_position[0], bar_position[1])
        bar_movie = RuntimeBarGenerator(framerate=framerate, 
                                        movie_size=(int(movie_width), int(movie_height)),
                                        bar_orientation=bar_heading, 
                                        bar_size=(bar_width, bar_height), bar_speed=bar_speed, 
                                        bar_movement_distance=bar_movement_distance,
                                        bar_position=bar_position, bar_color=bar_color,
                                        background_color=background_color,
                                        minimize=False)
#        bar_movie.playFrameByFrame()
        stimulus = Stimulus(position_on_retina=position_on_retina,
                            pixel_size_in_rgu=pixel_size_in_rgu, movie=bar_movie)
                            
        
        stimuli.append(stimulus)
        
    return stimuli, bar_headings


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
                                        background_color=background_color,
                                        minimize=True)
        
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