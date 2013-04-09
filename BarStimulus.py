import math as m
from RuntimeBarGenerator import RuntimeBarGenerator




class BarStimulus:

    def __init__(self, position_on_retina=(0.0, 0.0), pixel_size=1.0, 
                 bar_movie=RuntimeBarGenerator()):

        self.position_on_retina     = position_on_retina
        self.pixel_size             = pixel_size
        self.bar_movie              = bar_movie
        self.width_in_pixels        = bar_movie.movie_width
        self.height_in_pixels       = bar_movie.movie_height
        self.width_on_retina        = bar_movie.movie_width * pixel_size
        self.height_on_retina       = bar_movie.movie_height * pixel_size

        left    = position_on_retina[0]
        right   = position_on_retina[0] + self.width_on_retina
        up      = position_on_retina[1]
        down    = position_on_retina[1] + self.height_on_retina
        self.bounding_box = [left, right, up, down]
        
    def __str__(self):
        string = ""
        string += "\nPosition (rgu):\t\t\t\t"+str(self.position_on_retina)
        string += "\nPixel size (rgu):\t\t\t"+str(self.pixel_size)
        string += "\nWidth (pixels):\t\t\t\t"+str(self.width_in_pixels)
        string += "\nHeight (pixels):\t\t\t"+str(self.height_in_pixels)
        string += "\nWidth (rgu):\t\t\t\t"+str(self.width_on_retina)
        string += "\nHeight (rgu):\t\t\t\t"+str(self.height_on_retina)
        string += str(self.bar_movie)
        return string
        
    """
    The module used for saving (pickle) can't handle pygame's surface, so it must
    be unloaded before saving
    """
    def unloadStimulusForSaving(self):
        self.bar_movie.removeDisplay()
        
    
    """
    Update the bar_movie
    """
    def update(self, timestep):
        self.bar_movie.update(timestep)
    
    """
    Get the intensity of a pixel with name pixel_ID from the bar_movie
    """
    def getPixelIntensity(self, pixel_ID):
        x, y = pixel_ID.split(".")
        x, y = int(x), int(y)
        intensity = self.bar_movie.screen_array[x, y]
        return intensity

    """
    Given a cone's bounding box, [L, R, U, D], find the overlapping pixels on
    the retina and return a list [[pixel_ID, overlap_percentage], ...]
    """
    def getPixelOverlaps(self, cone_bounding_box):        
        # Find the overlap between the cone and the entire movie
        overlap_box, overlap_area = overlapBetweenRectangles(cone_bounding_box, self.bounding_box)

        # If there is no overlap with movie, no overlapping pixels
        if overlap_area == -1: return []

        # Now to find the overlap between the cone and the overlapping pixels
        overlapping_pixels  = []
        total_pixel_area    = self.pixel_size**2.0
        
        # First, convert the overlapBox from retinal space to pixel space by:
        #   Subtracting the movie's position in retinal space
        #   Dividing by the pixel size
        left, right, up, down = overlap_box
        left    = int(m.floor((left-self.position_on_retina[0]) / self.pixel_size))
        right   = int(m.ceil((right-self.position_on_retina[0]) / self.pixel_size))
        up      = int(m.floor((up-self.position_on_retina[1]) / self.pixel_size))
        down    = int(m.ceil((down-self.position_on_retina[1]) / self.pixel_size))

        left    = max(0, left)
        right   = min(self.width_in_pixels-1, right)
        up      = max(0, up)
        down    = min(self.height_in_pixels-1, down)

        # Now that we have the pixel ranges, we can iterate through them and
        # check each pixel's retinal space bounding box for overlap with the cone
        for pixel_x in range(left, right+1):
            for pixel_y in range(up, down+1):
                pixel_left  = pixel_x * self.pixel_size + self.position_on_retina[0]
                pixel_right = pixel_left + self.pixel_size
                pixel_up    = pixel_y * self.pixel_size + self.position_on_retina[1]
                pixel_down  = pixel_up + self.pixel_size
                pixel_box   = [pixel_left, pixel_right, pixel_up, pixel_down]
                
                overlap_box, overlap_area = overlapBetweenRectangles(cone_bounding_box, pixel_box)

                if overlap_area != -1:
                    overlap_percent = overlap_area/total_pixel_area
                    pixel_ID        = str(pixel_x)+"."+str(pixel_y) 
                    overlapping_pixels.append([pixel_ID, overlap_percent])

        return overlapping_pixels

                    


                
                

"""
Given two bounding boxes, [L, R, U, D], find the rectangle of overlap and the
area of overlap
"""
def overlapBetweenRectangles(bbox1, bbox2):
    left1, right1, up1, down1 = bbox1
    left2, right2, up2, down2 = bbox2

    left            = max(left1, left2)
    right           = min(right1, right2) 
    overlap_width   = right - left
    
    down            = min(down1, down2)  
    up              = max(up1, up2)
    overlap_height  = down - up

    if overlap_width>0 and overlap_height>0:
        return [left, right, up, down], overlap_width*overlap_height
    else:
        return -1, -1
        
        
