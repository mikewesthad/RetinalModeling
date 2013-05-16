import math as m
import pygame
import numpy as np
from Constants import *



"""
The RunTimeBarGenerator class using pygame and numpy to create a moving bar stimulus.

Inputs:
    framerate - frames/second
    movie_size - (w x h) in pixels
    bar_orientation - degrees clockwise around unit cirle
    bar_size - (w x h) in pixels; w is length in direction of motion, and h is length in
              direction perpendicular to motion
    bar_speed - pixels/second
    bar_movement_distance - distance the bar should move from its initial position
    bar_color - (R,G,B) color
    background_color - (R,G,B) color
    bar_position - (x, y) position in pixels with (0,0) being the upper left

Methods:
    update(deltaTime) - this will update the frame if necessary

"""
class RuntimeBarGenerator:

    def __init__(self, framerate=30.0, movie_size=(800,800), 
                 flash_shape="Rectangle", flash_size=(20.0,60.0),
                 background_color=(255,255,255), flash_color=(0,0,0),
                 flash_position=(100,100), flash_duration=1000*MS_TO_S,
                 delay_before_flash=10*MS_TO_S, delay_after_flash=10*MS_TO_S,
                 minimize=True):       

        # Initialize class variables
        self.framerate          = framerate
        self.frame_duration     = 1.0/self.framerate
        self.movie_width        = movie_size[0]
        self.movie_height       = movie_size[1]
        self.flash_color        = flash_color    
        self.background_color   = background_color
        self.flash_position     = flash_position
        self.flash_size         = flash_size
        self.flash_shape        = flash_shape.lower()
        self.flash_duration     = flash_duration
        self.delay_before_flash = delay_before_flash
        self.delay_after_flash  = delay_after_flash
        
        # Initialize the pygame module
        pygame.init()

        # Create a pygame display surface
        self.display = pygame.display.set_mode(movie_size)
        if minimize: pygame.display.iconify()

        # Initialize run timing variables
        self.time   = 0.0

        # Initialize the numpy array representing the screen
        self.update(0.0)
        self.screen_array = pygame.surfarray.pixels3d(self.display)
        
    def drawBackground(self):
        self.display.fill(self.background_color)
        
    def drawFlash(self):
        if self.flash_shape == "rectangle":
            rect = self.flash_position + self.flash_size
            pygame.draw.rect(self.display, self.flash_color, rect)
        elif self.flash_shape == "circle":
            pos     = self.flash_position
            radius  = self.flash_size
            pygame.draw.circle(self.display, self.flash_color, pos, radius)
        else:
            print "Flash shape not defined"
        
    """
    Store the intensity values of the current screen into a np array
    """    
    def updateScreenArray(self):        
        # The pygame array returned by pygame is of size (rows=width x cols=height) 
        screen_RGB = pygame.surfarray.pixels3d(self.display)                   
        self.screen_array = np.average(screen_RGB, 2) / 255.0
        
    def play(self, speed=1.0):
        clock = pygame.time.Clock()
        elapsed = 0.0
        is_running = True
        while is_running:
            is_running = self.update(elapsed)
            elapsed = clock.tick(self.framerate) / 1000.0 * speed
            
    """
    Given a specified change in world time, update the bar flash.
    """   
    def update(self, timestep):

        is_running = True
        
        self.time += timestep
        
        self.drawBackground()
        if self.time >= self.delay_before_flash:
            if self.time <= (self.delay_before_flash + self.flash_duration):
                self.drawFlash()
            elif self.time > (self.delay_before_flash + self.flash_duration + self.delay_after_flash):
                is_running = False
        
        pygame.display.update()
        self.updateScreenArray()
        
        return is_running
        


    def removeDisplay(self):
        self.display = None
        
    def __str__(self):
        string = ""
        string += "\nFramerate\t\t\t\t"+str(self.framerate)
        string += "\nFlash Size\t\t\t\t"+str(self.flash_size)
        string += "\nFlash Color\t\t\t\t"+str(self.flash_color)
        string += "\nBackground Color\t\t\t"+str(self.background_color)        
        string += "\nFlash Position\t\t\t"+str(self.flash_position)       
        string += "\nFlash Duration\t\t\t\t"+str(self.flash_duration)    
        string += "\nDelay Before Flash\t\t\t\t"+str(self.delay_before_flash)
        string += "\nDelay After Flash\t\t\t\t"+str(self.delay_after_flash)
        return string






"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5
