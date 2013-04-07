import math as m
import pygame
import numpy as np



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
                 background_color=(255,255,255), bar_orientation=45.0,
                 bar_size=(20.0,60.0), bar_speed=20.0, bar_movement_distance=500.0,
                 bar_color=(0,0,0), bar_position=(100,100)):       

        # Initialize class variables
        self.framerate          = framerate
        self.frame_duration     = 1.0/self.framerate
        self.movie_width        = movie_size[0]
        self.movie_height       = movie_size[1]
        self.bar_color          = bar_color    
        self.background_color   = background_color

        # Create the vertices of the bar
        self.bar_vertices = []
        self.num_vertices = 4
        self.initBarVertices(bar_size[0], bar_size[1], bar_orientation, bar_position)
        
        # Calculate the movement direction of the bar from the orientation
        self.heading_x = m.cos(bar_orientation * m.pi/180.0)
        self.heading_y = m.sin(bar_orientation * m.pi/180.0)
        self.bar_speed = bar_speed

        # Track a vertex on the bar to calculate distance traveled
        self.start_vertex_position  = [self.bar_vertices[0][0], self.bar_vertices[0][1]]  # Deep copy
        self.distance_traveled      = 0.0
        self.max_distance           = bar_movement_distance

        # Initialize the pygame module
        pygame.init()

        # Create a pygame display surface
        self.display = pygame.display.set_mode(movie_size)
        self.drawBar()

        # Initialize run timing variables
        self.time   = 0.0
        self.frame  = 0

        # Initialize the numpy array representing the screen
        self.screen_array = pygame.surfarray.pixels3d(self.display)

        self.drawBar()
        self.updateScreenArray()

    
    """
    Create a list of bar vertices, [ul, ur, lr, ll], defining a rotated
    rectangle centered on a position
    """    
    def initBarVertices(self, width, height, orientation, position):
        # The unrotated upper left vertex would be (1/2 width, 1/2 height)
        # Rotating that vertex becomes (x*cos(a)-y*sin(a), x*cos(a)-y*sin(a))
        half_width      = width/2.0
        half_height     = height/2.0
        cos_orientation = m.cos(orientation * m.pi/180.0)
        sin_orientation = m.sin(orientation * m.pi/180.0)

        # Find the position of rotated vertices if the bar were centered on (0,0)
        ulx = (-half_width) * cos_orientation - half_height * sin_orientation
        uly = (-half_width) * sin_orientation + half_height * cos_orientation
        urx = half_width * cos_orientation - half_height * sin_orientation
        ury = half_width * sin_orientation + half_height * cos_orientation
        lrx = half_width * cos_orientation - (-half_height) * sin_orientation
        lry = half_width * sin_orientation + (-half_height) * cos_orientation
        llx = (-half_width) * cos_orientation - (-half_height) * sin_orientation
        lly = (-half_width) * sin_orientation + (-half_height) * cos_orientation

        # Create vertex list in clockwise order
        self.bar_vertices = [[ulx, uly], [urx, ury], [lrx, lry], [llx, lly]]

        # Shift the bar vertices so that it is now centered on startBarPosition
        self.moveBar(position[0], position[1])


    """
    Move all the vertices of the bar by a dx and a dy
    """    
    def moveBar(self, dx, dy):
        for i in range(self.num_vertices):
            self.bar_vertices[i][0] += dx
            self.bar_vertices[i][1] += dy

    """
    Calculate the distance from the starting ul  vertex position to the current
    ul vertex position
    """    
    def updateDistanceTraveled(self):
        x1, y1 = self.bar_vertices[0]
        x2, y2 = self.start_vertex_position
        self.distance_traveled = linearDistance(x1, y1, x2, y2)
        
    """
    Draw the bar to screen (including erasing what was previously there)
    """    
    def drawBar(self):
        self.display.fill(self.background_color)
        pygame.draw.polygon(self.display, self.bar_color, self.bar_vertices, 0)
        pygame.display.update()
        
    """
    Store the intensity values of the current screen into a np array
    """    
    def updateScreenArray(self):        
        # The pygame array returned by pygame is of size (rows=width x cols=height) 
        screen_RGB = pygame.surfarray.pixels3d(self.display)                   
        self.screen_array = np.average(screen_RGB, 2) / 255.0
    
    """
    Given a specified change in world time, move the bar forward to the
    appropriate position.  If the bar has moved it's maximum distance, return
    false; otherwise, return true.
    """   
    def update(self, timestep):

        self.time += timestep

        # Find the elapsed frame time since last update and set the new frame number
        elapsed_time        = 0.0
        frame_from_time     = int(self.time * self.framerate)
        if frame_from_time != self.frame:
            frame_difference    = frame_from_time - self.frame
            elapsed_time        = frame_difference * self.frame_duration
            self.frame          = frame_from_time

        # Move the bar
        dx = self.heading_x * (elapsed_time * self.bar_speed)
        dy = self.heading_y * (elapsed_time * self.bar_speed)
        self.moveBar(dx, dy)

        # Check bar movement distance
        self.updateDistanceTraveled()
        if self.distance_traveled >= self.max_distance: return False

        # If the bar has moved, redraw
        if elapsed_time>0:
            self.drawBar()
            self.updateScreenArray()
            
        return True
        
    
    def removeDisplay(self):
        self.display = None








"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5
