import pygame
from pygame.locals import *


class Visualizer:
    
    def __init__(self, retina, visualization_width=1000, visualization_height=1000,
                 visualization_background_color=pygame.Color(255,255,255), controls_width=250, 
                 controls_background_color=pygame.Color(245,245,245)):
                     

        
        self.visualization_background_color     = visualization_background_color
        self.controls_background_color          = controls_background_color
        
        # The screen real estate (pixels) used for displaying visuals
        self.visualization_width    = visualization_width
        self.visualization_height   = visualization_height
        self.visualization_size     = (self.visualization_width, self.visualization_height)
        self.visualization_position = (0, 0)
        
        # The screen real estate (pixels) used for adding controls
        self.controls_width     = controls_width
        self.controls_height    = visualization_height
        self.controls_size      = (self.controls_width, self.controls_height)
        self.controls_position  = (self.visualization_width, 0)
        
        # Total screen size for the pygame window
        self.screen_width       = self.visualization_width + self.controls_width
        self.screen_height      = self.visualization_height
        self.screen_size        = (self.screen_width, self.screen_height)
        
        # Calculate the scaling from retina to the visualization size
        self.retina = retina
        self.visualization_scale = self.calculateVisualizationScaling()        
        # Load and convert a bunch of retina stuff to display coordinates
        self.preloadRetina()
        
        # Start pygame        
        pygame.init()
        
        # Create the pygame surfaces
        self.screen_surface         = pygame.display.set_mode(self.screen_size)
        self.visualization_surface  = pygame.Surface(self.visualization_size)
        self.controls_surface       = pygame.Surface(self.controls_size)
        self.screen_surface.fill((255,255,255))        
        
        # Create a set of linked buttons to determine the visualization type
        visualization_types = ["Input Weights", "Soma Placement", "Activity"]
        buttons = []
        width, height = 200, 50
        dy = int(height + height/2.0)
        x, y = int(self.controls_width/2.0-width/2.0), dy
        for vis_type in visualization_types:
            button = Button(self.controls_surface, text=vis_type, name=vis_type,
                            x=x, y=y)
            y += dy
            buttons.append(button)            
        self.visualization_type_button_group = LinkedButtons(buttons)
        
        # Create a set of linked buttons to determine the cell type
        cell_types = ["Cone", "Horizontal", "On Bipolar", "Off Bipolar"]
        buttons = []
        width, height = 200, 50
        dy = int(height + height/2.0)
        x, y = int(self.controls_width/2.0-width/2.0), 400
        for cell_type in cell_types:
            button = Button(self.controls_surface, text=cell_type, name=cell_type,
                            x=x, y=y)
            y += dy
            buttons.append(button)            
        self.cell_type_button_group = LinkedButtons(buttons)
        
        
        self.mainloop()
        
    
    
    def mainloop(self):  
        running = True
        while running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_click = False   
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                else:
                    if event.type == MOUSEBUTTONUP:
                        if event.button == 1:
                            mouse_click = True
                            
            buttons_pressed = self.updateControlSurface(mouse_x, mouse_y, mouse_click)
            self.updateVisualizationSurface(buttons_pressed)
            
            pygame.display.update()
    
    
    
    def preloadRetina(self):
        
        retina = self.retina
        
        self.cone_color         = retina.cone_color
        self.horizontal_color   = retina.horizontal_color
        self.on_bipolar_color   = retina.on_bipolar_color
        self.off_bipolar_color  = retina.off_bipolar_color
        
        self.cone_radius         = int(round(retina.cone_layer.nearest_neighbor_distance_gridded/2.0 * self.visualization_scale))
        self.horizontal_radius   = int(round((retina.horizontal_layer.nearest_neighbor_distance_gridded/2.0 + 3) * self.visualization_scale)) # Add 3 so you can see behind cones
        self.on_bipolar_radius   = int(round(retina.on_bipolar_layer.nearest_neighbor_distance_gridded/2.0 * self.visualization_scale))
        self.off_bipolar_radius  = int(round(retina.off_bipolar_layer.nearest_neighbor_distance_gridded/2.0 * self.visualization_scale))
        
        self.cone_locations          = [[int(round(x * self.visualization_scale)), int(round(y * self.visualization_scale))] for x, y in retina.cone_layer.locations]
        self.horizontal_locations    = [[int(round(x * self.visualization_scale)), int(round(y * self.visualization_scale))] for x, y in retina.horizontal_layer.locations]        
        self.on_bipolar_locations    = [[int(round(x * self.visualization_scale)), int(round(y * self.visualization_scale))] for x, y in retina.on_bipolar_layer.locations] 
        self.off_bipolar_locations   = [[int(round(x * self.visualization_scale)), int(round(y * self.visualization_scale))] for x, y in retina.off_bipolar_layer.locations] 
    
    
    
    def visualizeCellPlacement(self, surface, cell_type):
        
            if cell_type == "None":    
                cone_color          = self.cone_color
                horizontal_color    = self.horizontal_color
                on_bipolar_color    = self.on_bipolar_color
                off_bipolar_color   = self.off_bipolar_color
                drawOrder           = [[self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_radius],
                                       [self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_radius],
                                       [self.horizontal_locations, horizontal_color, self.horizontal_radius],
                                       [self.cone_locations, cone_color, self.cone_radius]] 
            elif cell_type == "Cone":     
                cone_color          = self.cone_color
                horizontal_color    = lerpColors(self.horizontal_color, self.visualization_background_color, 0.85)
                on_bipolar_color    = lerpColors(self.on_bipolar_color, self.visualization_background_color, 0.85)
                off_bipolar_color   = lerpColors(self.off_bipolar_color, self.visualization_background_color, 0.85)
                drawOrder           = [[self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_radius],
                                       [self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_radius],
                                       [self.horizontal_locations, horizontal_color, self.horizontal_radius],
                                       [self.cone_locations, cone_color, self.cone_radius]] 
            elif cell_type == "Horizontal":     
                cone_color          = lerpColors(self.cone_color, self.visualization_background_color, 0.85)
                horizontal_color    = self.horizontal_color
                on_bipolar_color    = lerpColors(self.on_bipolar_color, self.visualization_background_color, 0.85)
                off_bipolar_color   = lerpColors(self.off_bipolar_color, self.visualization_background_color, 0.85)
                drawOrder           = [[self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_radius],
                                       [self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_radius],
                                       [self.cone_locations, cone_color, self.cone_radius],
                                       [self.horizontal_locations, horizontal_color, self.horizontal_radius]] 
            elif cell_type == "On Bipolar":  
                cone_color          = lerpColors(self.cone_color, self.visualization_background_color, 0.85)
                horizontal_color    = lerpColors(self.horizontal_color, self.visualization_background_color, 0.85)
                on_bipolar_color    = self.on_bipolar_color
                off_bipolar_color   = lerpColors(self.off_bipolar_color, self.visualization_background_color, 0.85)
                drawOrder           = [[self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_radius],
                                       [self.horizontal_locations, horizontal_color, self.horizontal_radius],
                                       [self.cone_locations, cone_color, self.cone_radius],
                                       [self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_radius]] 
            else:     
                cone_color          = lerpColors(self.cone_color, self.visualization_background_color, 0.85)
                horizontal_color    = lerpColors(self.horizontal_color, self.visualization_background_color, 0.85)
                on_bipolar_color    = lerpColors(self.on_bipolar_color, self.visualization_background_color, 0.85)
                off_bipolar_color   = self.off_bipolar_color
                drawOrder           = [[self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_radius],
                                       [self.horizontal_locations, horizontal_color, self.horizontal_radius],
                                       [self.cone_locations, cone_color, self.cone_radius],
                                       [self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_radius]] 
            
            for locations, color, radius in drawOrder:
                for x, y in locations:
                    pygame.draw.circle(surface, color, (x, y), radius)
                    
                    
    
    def updateVisualizationSurface(self, buttons_pressed):
        self.visualization_surface.fill(self.visualization_background_color)
        
        vis_button_pressed  = buttons_pressed[0]
        cell_button_pressed = buttons_pressed[1]
        
        if not(vis_button_pressed==None):
            vis_type = vis_button_pressed.name
                        
            if cell_button_pressed != None:     cell_type = cell_button_pressed.name
            else:                               cell_type = "None"
            
            if vis_type == "Soma Placement":
                self.visualizeCellPlacement(self.visualization_surface, cell_type)
                
        self.screen_surface.blit(self.visualization_surface, self.visualization_position)
        
    
    def updateControlSurface(self, mouse_x, mouse_y, mouse_click):
        # Shift the mouse coordinates into the coordinate system of the controls surface 
        mouse_x -= self.controls_position[0]
        mouse_y -= self.controls_position[1]
        
        # Erase the surface
        self.controls_surface.fill(self.controls_background_color)
        
        # Update the buttons
        self.visualization_type_button_group.update(mouse_x, mouse_y, mouse_click)
        self.cell_type_button_group.update(mouse_x, mouse_y, mouse_click)
        
        # Draw the buttons
        self.visualization_type_button_group.draw()
        self.cell_type_button_group.draw()
        
        # Draw the control surface to the screen
        self.screen_surface.blit(self.controls_surface, self.controls_position)
        
        # Determine if any buttons have been pressed
        vis_button_pressed  = self.visualization_type_button_group.getPressedButton()
        cell_button_pressed = self.cell_type_button_group.getPressedButton()
        buttons_pressed     = [vis_button_pressed, cell_button_pressed]
        
        return buttons_pressed
        
    
            
    def calculateVisualizationScaling(self):        
        width_scale         = self.visualization_width / float(self.retina.grid_width)
        height_scale        = self.visualization_height / float(self.retina.grid_height)
        return min(width_scale, height_scale)
            
            
"""
LinkedButtons are a group of buttons where at maximum one can be depressed at a time
"""        
class LinkedButtons:
    def __init__(self, buttons):
        self.buttons = buttons
        self.number_buttons = len(buttons)
        
    def getPressedButton(self): 
        for button in self.buttons:
            if button.isPressed(): return button 
        return None
        
    def draw(self):
        for button in self.buttons:
            button.draw()
    
    def update(self, mouse_x, mouse_y, mouse_clicked):
        # Update the buttons and stop if a button just became pressed
        for button_index in range(self.number_buttons):
            button = self.buttons[button_index]
            just_pressed = button.update(mouse_x, mouse_y, mouse_clicked)
            if just_pressed: 
                pressed_button_index = button_index
                break
        
        # If a button was just pressed, make sure all the other buttons in the
        # group are not pressed        
        if just_pressed:
            for button_index in range(self.number_buttons):
                if button_index  != pressed_button_index:
                    button = self.buttons[button_index]
                    button.unpress()
                    button.update(mouse_x, mouse_y, False)
                    
"""
Button is a little button class that has a couple visual flourishes
"""
class Button:

    def __init__(self, display, x=100, y=100, width=200, height=50, 
                 button_normal_color=(0,197,234), 
                 button_pressed_color=(0,149,219),
                 button_hover_color=(0,180,229),
                 button_shadow_color=(13,105,146),
                 text="Test String", text_color=(255,255,255), fontName=None,
                 fontSize=24, antialias=True, name="Test"):
        
        self.display = display
        
        self.name = name
        
        self.button_rectangle = pygame.Rect(x, y, width, height) 
        
        self.font = pygame.font.Font(fontName, fontSize)
        self.label = self.font.render(text, antialias, text_color)
        self.label_rectangle = self.label.get_rect()
        self.label_rectangle.center  = self.button_rectangle.center
        
        self.button_normal_color    = pygame.Color(button_normal_color[0], button_normal_color[1], button_normal_color[2])
        self.button_hover_color     = pygame.Color(button_hover_color[0], button_hover_color[1], button_hover_color[2])
        self.button_pressed_color   = pygame.Color(button_pressed_color[0], button_pressed_color[1], button_pressed_color[2])
        self.button_shadow_color    = pygame.Color(button_shadow_color[0], button_shadow_color[1], button_shadow_color[2])
        self.button_color           = self.button_normal_color
        
        self.button_pressed = False
        
    def unpress(self):
        self.button_pressed = False
    def isPressed(self):
        return self.button_pressed
    
    def draw(self):
        # Draw the button
        pygame.draw.rect(self.display, self.button_color, self.button_rectangle)
        
        # Draw the button shadow if necessary
        if self.button_pressed: pygame.draw.rect(self.display, self.button_shadow_color, self.button_rectangle, 1)
        
        # Draw the text on top
        self.display.blit(self.label, self.label_rectangle)
        
        
    def update(self, mouse_x, mouse_y, mouse_click):
        mouse_within_button = self.button_rectangle.collidepoint(mouse_x, mouse_y)
        
        if self.button_pressed:
            if mouse_within_button and mouse_click:
                self.button_color = self.button_normal_color
                self.button_pressed = False
            else:
                self.button_color = self.button_pressed_color
                
        elif self.button_rectangle.collidepoint(mouse_x, mouse_y):
            if mouse_click:
                self.button_color = self.button_pressed_color
                self.button_pressed = True
                return True
            else:
                self.button_color = self.button_hover_color
                
        else:
            self.button_color = self.button_normal_color
            
        return False
            
        
        
"""
Linearly interpolate between color1 and color2
"""
def lerpColors(color1, color2, fraction):
    r = color1.r + fraction * (color2.r - color1.r)
    g = color1.g + fraction * (color2.g - color1.g)
    b = color1.b + fraction * (color2.b - color1.b)
    return pygame.Color(int(r),int(g),int(b))



# Build Retina
import pickle
import os
save_directory  = os.path.join("Saved Retinas", "Morphology")
saved_path      = os.path.join(os.getcwd(), save_directory, "retina.p")
retina = pickle.load(open(saved_path, "rb"))

v = Visualizer(retina)
