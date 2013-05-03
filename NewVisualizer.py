from Constants import *

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
        visualization_types = ["Stimulus", "Input Weights", "Soma Placement", "Activity"]
        buttons = []
        width, height = 200, 40
        dy = 40 + 20
        x, y = int(self.controls_width/2.0-width/2.0), dy
        for vis_type in visualization_types:
            button = Button(self.controls_surface, text=vis_type, name=vis_type,
                            x=x, y=y)
            y += dy
            buttons.append(button)            
        self.visualization_type_button_group = LinkedButtons(buttons)
        
        # Create a set of linked buttons to determine the cell type
        cell_types = ["Cone", "Horizontal", "On Bipolar", "Off Bipolar", "On Starburst", "Off Starburst"]
        buttons = []
        width, height = 200, 40
        dy = 40 + 20
        x, y = int(self.controls_width/2.0-width/2.0), 400
        for cell_type in cell_types:
            button = Button(self.controls_surface, text=cell_type, name=cell_type,
                            x=x, y=y)
            y += dy
            buttons.append(button)            
        self.cell_type_button_group = LinkedButtons(buttons)
        
        # Create a set of linked buttons to change the timestep
        width   = 90
        height  = 40        
        x1  = button.button_rectangle.left
        x2  = button.button_rectangle.right - width
        y1  = 800
        y2  = 800        
        left    = Button(self.controls_surface, text="<-", name="Left", 
                         x=x1, y=y1, width=width, height=height)
        x, y = x+30, 800
        right   = Button(self.controls_surface, text="->", name="Right", 
                         x=x2, y=y2, width=width, height=height)
        self.direction_arrows_button_group = LinkedButtons([left, right])
        
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
            self.updateVisualizationSurface(buttons_pressed, mouse_x, mouse_y)
            
            pygame.display.update()
    
    
    
    def preloadRetina(self):
        
        r = self.retina   
        
        self.cone_layer             = r.cone_layer
        self.horizontal_layer       = r.horizontal_layer
        self.on_bipolar_layer       = r.on_bipolar_layer
        self.off_bipolar_layer      = r.off_bipolar_layer
        self.on_starburst_layer     = r.on_starburst_layer
        self.off_starburst_layer    = r.off_starburst_layer
        
        self.cone_color             = r.cone_color
        self.horizontal_color       = r.horizontal_color
        self.on_bipolar_color       = r.on_bipolar_color
        self.off_bipolar_color      = r.off_bipolar_color
        self.on_starburst_color     = r.on_starburst_color
        self.off_starburst_color    = r.off_starburst_color
        
        self.cone_color_deselected          = lerpColors(self.cone_color, self.visualization_background_color, 0.85)
        self.horizontal_color_deselected    = lerpColors(self.horizontal_color, self.visualization_background_color, 0.85)
        self.on_bipolar_color_deselected    = lerpColors(self.on_bipolar_color, self.visualization_background_color, 0.85)
        self.off_bipolar_color_deselected   = lerpColors(self.off_bipolar_color, self.visualization_background_color, 0.85)
        self.on_starburst_color_deselected  = lerpColors(self.on_starburst_color, self.visualization_background_color, 0.85)
        self.off_starburst_color_deselected = lerpColors(self.off_starburst_color, self.visualization_background_color, 0.85)
        
        self.cone_activities            = r.cone_activities
        self.horizontal_activities      = r.horizontal_activities
        self.on_bipolar_activities      = r.on_bipolar_activities
        self.off_bipolar_activities     = r.off_bipolar_activities
        self.on_starburst_activities    = r.on_starburst_activities
        self.off_starburst_activities   = r.off_starburst_activities
        
        self.cone_activity_bounds           = self.findActivityBounds(self.cone_activities, -1, 1, True)
        self.horizontal_activity_bounds     = self.findActivityBounds(self.horizontal_activities, -1, 1, True)
        self.on_bipolar_activity_bounds     = self.findActivityBounds(self.cone_activities, -1, 1, True)
        self.off_bipolar_activity_bounds    = self.findActivityBounds(self.cone_activities, -1, 1, True)
        self.on_starburst_activity_bounds   = self.findActivityBounds(self.on_starburst_activities, -1, 1, True)
        self.off_starburst_activity_bounds  = self.findActivityBounds(self.off_starburst_activities, -1, 1, True)
        
        info = [["Cone", self.cone_activity_bounds], ["Horizontal", self.horizontal_activity_bounds],
                ["On Bipolar", self.on_bipolar_activity_bounds], ["Off Bipolar", self.off_bipolar_activity_bounds],
                ["On Starburst", self.on_starburst_activity_bounds], ["Off Starburst", self.off_starburst_activity_bounds]]
        for cell_name, [min_bound, max_bound] in info:
            print cell_name,"Activity Bounds: ({0:.3f}, {1:.3f})".format(min_bound, max_bound)
            
        self.color_bounds = [pygame.Color(0,0,255), pygame.Color(255,0,0)]
        
        self.timestep       = 0
        self.end_timestep   = len(self.cone_activities) - 1    
    
    def visualizeCellPlacement(self, surface, cell_type):
        
        scale = self.visualization_scale        
        if cell_type == "None":
            self.on_starburst_layer.draw(surface, scale=scale)
            self.off_starburst_layer.draw(surface, scale=scale)
            self.on_bipolar_layer.draw(surface, scale=scale) 
            self.off_bipolar_layer.draw(surface, scale=scale) 
            self.horizontal_layer.draw(surface, inflate_radius=1.0, scale=scale)  
            self.cone_layer.draw(surface, scale=self.visualization_scale)
        else:            
            self.on_starburst_layer.draw(surface, color=self.on_starburst_color_deselected, scale=scale)
            self.off_starburst_layer.draw(surface, color=self.off_starburst_color_deselected, scale=scale)
            self.on_bipolar_layer.draw(surface, color=self.on_bipolar_color_deselected, scale=scale) 
            self.off_bipolar_layer.draw(surface, color=self.off_bipolar_color_deselected, scale=scale) 
            self.horizontal_layer.draw(surface, color=self.horizontal_color_deselected, inflate_radius=1.0, scale=scale)  
            self.cone_layer.draw(surface, color=self.cone_color_deselected, scale=self.visualization_scale)
            if cell_type == "Cone":
                 self.cone_layer.draw(surface, scale=self.visualization_scale)
            elif cell_type == "Horizontal":
                 self.horizontal_layer.draw(surface, scale=self.visualization_scale)
            elif cell_type == "On Bipolar":
                self.on_bipolar_layer.draw(surface, scale=scale) 
            elif cell_type == "Off Bipolar":
                self.off_bipolar_layer.draw(surface, scale=scale) 
            elif cell_type == "On Starburst":
                 self.on_starburst_layer.draw(surface, scale=scale)
            elif cell_type == "Off Starburst":
                 self.off_starburst_layer.draw(surface, scale=scale)
    
                
    def findActivityBounds(self, activities, estimated_min, estimated_max, activity_centered_on_zero):
        # Find the real max/min activity values
        max_activity = np.amax(activities)
        min_activity = np.amin(activities)
        
        # Impose an estimated max/min
        max_activity    = max(max_activity, estimated_max)
        min_activity    = min(min_activity, estimated_min)
        
        # If the range of activity values is expected to be symmetric and
        # centered on zero, then the max and min values should be equal
        if activity_centered_on_zero:
            bound           = max(abs(max_activity), abs(min_activity))
            max_activity    = bound
            min_activity    = -bound
        
        return [min_activity, max_activity] 
             
    def mapActivityToColor(self, activity, min_activity, max_activity, activity_centered_on_zero):
        positive_activity_color         = pygame.Color(255, 0, 0)
        zero_positive_activity_color    = pygame.Color(0, 0, 0)
        negative_activity_color         = pygame.Color(0, 0, 255)
        zero_negative_activity_color    = pygame.Color(0, 0, 0)
        
        if activity_centered_on_zero:
            if activity < 0:
                percent_from_zero_to_min = activity/min_activity
                color = lerpColors(zero_negative_activity_color, negative_activity_color, percent_from_zero_to_min)
            else:
                percent_from_zero_to_max = activity/max_activity
                color = lerpColors(zero_positive_activity_color, positive_activity_color, percent_from_zero_to_max)
        else:
            percent_from_min_to_max = (activity-min_activity) / (max_activity-min_activity)
            color = self.lerpColors(zero_positive_activity_color, positive_activity_color, percent_from_min_to_max)
            
        return color
                    
    def playLayerActivity(self, surface, activities, locations, radius,
                          min_activity, max_activity, activity_centered_on_zero=True):
                             
        number_neurons = activities[0].shape[1]
        for n in range(number_neurons):
            x, y        = locations[n]
            activity    = activities[self.timestep][0,n]
            color       = self.mapActivityToColor(activity, min_activity, max_activity, 
                                                  activity_centered_on_zero)
            pygame.draw.circle(surface, color, (x,y), radius) 
            
        
    def updateVisualizationSurface(self, buttons_pressed, mouse_x, mouse_y):
        self.visualization_surface.fill(self.visualization_background_color)
        
        vis_button_pressed  = buttons_pressed[0]
        cell_button_pressed = buttons_pressed[1]
        
        if not(vis_button_pressed==None):
            vis_type = vis_button_pressed.name
                        
            if cell_button_pressed != None:     cell_type = cell_button_pressed.name
            else:                               cell_type = "None"
            
            if vis_type == "Soma Placement":
                pygame.display.set_caption(vis_type + " " + cell_type)
                self.visualizeCellPlacement(self.visualization_surface, cell_type)
            elif vis_type == "Activity":
                pygame.display.set_caption(vis_type + " " + cell_type + " " + str(self.timestep))
                if cell_type == "Cone":
                    self.retina.loadPast(self.timestep)
                    self.cone_layer.drawActivity(self.visualization_surface,
                                                 self.color_bounds,
                                                 self.cone_activity_bounds,
                                                 scale=self.visualization_scale)
                
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
        self.direction_arrows_button_group.update(mouse_x, mouse_y, mouse_click)
        
        # Draw the buttons
        self.visualization_type_button_group.draw()
        self.cell_type_button_group.draw()
        self.direction_arrows_button_group.draw()
        
        # Draw the control surface to the screen
        self.screen_surface.blit(self.controls_surface, self.controls_position)
        
        # Hack to reset the directional arrows after using them to change the current timestep
        direction_button_pressed = self.direction_arrows_button_group.getPressedButton()
        if direction_button_pressed == None:
            pass
        elif direction_button_pressed.name == "Left":
            self.timestep -= 1
            if self.timestep < 0: self.timestep = self.end_timestep
        elif direction_button_pressed.name == "Right":
            self.timestep += 1
            if self.timestep > self.end_timestep: self.timestep = 0
        self.direction_arrows_button_group.resetButtons(mouse_x, mouse_y, False)
        
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
            
    def resetButtons(self, mouse_x, mouse_y, mouse_clicked):
        for button in self.buttons:
            button.reset()
            button.update(mouse_x, mouse_y, mouse_clicked)
        
    
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
                    button.reset()
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
        
    def reset(self):
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

"""
Linear distance between two points
"""
def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5


