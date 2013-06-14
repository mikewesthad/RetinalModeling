import math as m
import pygame
import numpy as np
from Vector2D import Vector2D
from Constants import *

class RuntimeAnnulusGenerator:

    def __init__(self, framerate=30.0, movie_size=(400,400), 
                 duration=10000*MS_TO_S, direction="Centrifugal", 
                 stimulus_frequency=2.0, max_radius=192, radius_filter_factor=0.5,
                 width_filter_factor=0.562, minimize=False):       

        # Initialize class variables
        self.framerate          = framerate
        self.frame_duration     = 1.0/self.framerate
        self.movie_width        = movie_size[0]
        self.movie_height       = movie_size[1]
        
        if direction.lower() == "centrifugal":
            self.direction = 1.0
        elif direction.lower() == "centripetal":
            self.direction = -1.0
        else:
            print "Unknown direction parameter; defaulting to centrifugal"
            self.direction = 1.0
    
        self.center = Vector2D(self.movie_width/2.0, self.movie_height/2.0) 
        self.duration = duration
        
        self.stimulus_frequency = stimulus_frequency
        self.frame = 0.0
        self.max_radius = max_radius
        
        self.radius_filter = radius_filter_factor * self.max_radius
        self.width_filter = width_filter_factor * self.max_radius
        
        self.max_intensity = 1.0
        self.min_intensity = 0.0
        
        self.background_color = [((self.max_intensity - self.min_intensity)/2.0 + self.min_intensity) * 255,
                                 ((self.max_intensity - self.min_intensity)/2.0 + self.min_intensity) * 255,
                                 ((self.max_intensity - self.min_intensity)/2.0 + self.min_intensity) * 255]
        
        # Initialize the pygame module
        pygame.init()

        # Create a pygame display surface
        self.display = pygame.display.set_mode(movie_size)
        self.screen = pygame.Surface(movie_size)
        if minimize: pygame.display.iconify()

        # Initialize run timing variables
        self.time   = 0.0

        # Initialize the numpy array representing the screen
        self.update(0.0)
        
    def drawBackground(self):
        self.display.fill(self.background_color)
       
    """
    Store the intensity values of the current screen into a np array
    """    
    def updateScreenArray(self):        
        # The pygame array returned by pygame is of size (rows=width x cols=height) 
        screen_RGB = pygame.surfarray.pixels3d(self.display).copy()                
        self.screen_array = np.average(screen_RGB, 2) / 255.0
        
    def play(self, speed=1.0):
        clock = pygame.time.Clock()
        elapsed = 0.0
        is_running = True
        while is_running:
            is_running = self.update(elapsed)
            elapsed = clock.tick(self.framerate) / 1000.0 * speed
            
    def update(self, timestep):
        
        self.time += timestep

        # Find the elapsed frame time since last update and set the new frame number
            # Must ask it to round in order to avoid floating point inaccuracies 
        elapsed_time        = 0.0
        frame_from_time     = int(round(self.time,10) * self.framerate)
        if frame_from_time != self.frame:
            frame_difference    = frame_from_time - self.frame
            elapsed_time        = frame_difference * self.frame_duration
            self.frame          = frame_from_time
        
        if elapsed_time > 0:    
            self.screen.fill(self.background_color)
            parray = pygame.PixelArray(self.screen)
            for row in range(self.movie_height):
                for col in range(row, self.movie_width):
                    distance = Vector2D(float(row), float(col)).distanceTo(self.center)
                    intensity = m.sin(2.0*m.pi*(distance/self.max_radius + self.frame*self.direction*self.stimulus_frequency/self.framerate)) * m.exp(-(2.0*(distance-self.radius_filter)/self.width_filter)**4.0)
                    intensity = (intensity + 1.0) / 2.0 * (self.max_intensity-self.min_intensity) + self.min_intensity
                    color = pygame.Color(int(intensity*255), int(intensity*255), int(intensity*255))
                    parray[row, col] = color
                    parray[col, row] = color
            del parray
            self.display.blit(self.screen, (0,0))
            pygame.display.update()
            self.updateScreenArray()
        
        if self.time > self.duration:
            return False
        else:
            return True
        


    def removeDisplay(self):
        self.display = None
        
    def __str__(self):
        string = ""
        string += "\nFramerate\t\t\t\t"+str(self.framerate)
        return string
