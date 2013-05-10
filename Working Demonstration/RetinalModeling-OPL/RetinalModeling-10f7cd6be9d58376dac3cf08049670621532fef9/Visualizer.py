import numpy as np
import pygame
from pygame.locals import *


class Visualizer:
    
    def __init__(self, retina, visualization_width=700, visualization_height=700,
                 visualization_background_color=pygame.Color(255,255,255), controls_width=175, 
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
        
        # The screen real estate (pixels) used for the legend
        self.legend_width       = 250
        self.legend_height      = 250
        self.legend_position    = (0, self.visualization_height-self.legend_height)
        self.legend             = Legend(self, self.legend_position, self.legend_width, self.legend_height)
        
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
        cell_types = ["Cone", "Horizontal", "On Bipolar", "Off Bipolar"]
        buttons = []
        width, height = 200, 40
        dy = 40 + 20
        x, y = int(self.controls_width/2.0-width/2.0), 300 #400
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
        y1  = 600 #800
        y2  = 600 #800        
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
            
            self.legend.draw(self.screen_surface)
            
            pygame.display.update()
    
    
    
    def preloadRetina(self):
        
        r = self.retina   
        
        self.cone_color         = r.cone_color
        self.horizontal_color   = r.horizontal_color
        self.on_bipolar_color   = r.on_bipolar_color
        self.off_bipolar_color  = r.off_bipolar_color
        
        self.cone_color_deselected          = lerpColors(self.cone_color, self.visualization_background_color, 0.85)
        self.horizontal_color_deselected    = lerpColors(self.horizontal_color, self.visualization_background_color, 0.85)
        self.on_bipolar_color_deselected    = lerpColors(self.on_bipolar_color, self.visualization_background_color, 0.85)
        self.off_bipolar_color_deselected   = lerpColors(self.off_bipolar_color, self.visualization_background_color, 0.85)
        
        self.cone_neighbor_radius           = int(round(r.cone_layer.nearest_neighbor_distance_gridded/2.0 * self.visualization_scale))
        self.horizontal_neighbor_radius     = int(round(r.horizontal_layer.nearest_neighbor_distance_gridded/2.0 * self.visualization_scale))
        self.on_bipolar_neighbor_radius     = int(round(r.on_bipolar_layer.nearest_neighbor_distance_gridded/2.0 * self.visualization_scale))
        self.off_bipolar_neighbor_radius    = int(round(r.off_bipolar_layer.nearest_neighbor_distance_gridded/2.0 * self.visualization_scale))
        
        self.cone_input_radus           = int(round(r.cone_layer.input_field_radius_gridded * self.visualization_scale))
        self.horizontal_input_radius    = int(round(r.cone_layer.input_field_radius_gridded * self.visualization_scale))
        self.on_bipolar_input_radius    = int(round(r.on_bipolar_layer.input_field_radius_gridded * self.visualization_scale))
        self.off_bipolar_input_radius   = int(round(r.off_bipolar_layer.input_field_radius_gridded * self.visualization_scale))
        
        self.cone_locations          = [[int(round(x * self.visualization_scale)), int(round(y * self.visualization_scale))] for x, y in r.cone_layer.locations]
        self.horizontal_locations    = [[int(round(x * self.visualization_scale)), int(round(y * self.visualization_scale))] for x, y in r.horizontal_layer.locations]        
        self.on_bipolar_locations    = [[int(round(x * self.visualization_scale)), int(round(y * self.visualization_scale))] for x, y in r.on_bipolar_layer.locations] 
        self.off_bipolar_locations   = [[int(round(x * self.visualization_scale)), int(round(y * self.visualization_scale))] for x, y in r.off_bipolar_layer.locations] 
        
        self.cone_layer         = r.cone_layer
        self.horizontal_layer   = r.horizontal_layer
        self.on_bipolar_layer   = r.on_bipolar_layer
        self.off_bipolar_layer  = r.off_bipolar_layer
        
        print "Cone Activities"
        self.cone_activities = r.cone_activities
        self.cone_activity_bounds = self.findActivityBounds(self.cone_activities, -1, 1, True)
        
        print "Horizontal Activities"
        self.horizontal_activities = r.horizontal_activities
        self.horizontal_activity_bounds = self.findActivityBounds(self.horizontal_activities, -1, 1, True)
        
        print "On Bipolar Activities"
        self.on_bipolar_activities = r.on_bipolar_activities
        self.on_bipolar_activity_bounds = self.findActivityBounds(self.cone_activities, -1, 1, True)
        
        print "Off Bipolar Activities"
        self.off_bipolar_activities = r.off_bipolar_activities
        self.off_bipolar_activity_bounds = self.findActivityBounds(self.cone_activities, -1, 1, True)
        
        self.timestep       = 0
        self.end_timestep   = len(self.cone_activities) - 1
    
    
    
    """
    HACKED THIS ONLY WORKS FOR ON BIPOLAR CELLS
    """
    def visualizeInputWeights(self, surface, layer_locations, layer_neighbor_radius,
                              layer_input_radius, input_locations, input_neighbor_radius,
                              layer_selected_color, layer_deselected_color,
                              input_color, mouse_x, mouse_y):
        
        # Find if the mouse is hovering over a cell
        selected_cell = None        
        number_neurons = len(layer_locations)
        for n in range(number_neurons):
            x, y = layer_locations[n]
            if linearDistance(x, y, mouse_x, mouse_y) < layer_neighbor_radius:
                selected_cell = n
                break
        
        # Draw the cells in the layer
        for n in range(number_neurons):
            if n != selected_cell:
                x, y = layer_locations[n]
                pygame.draw.circle(surface, layer_deselected_color, (x, y), layer_neighbor_radius)
        
        # Draw the selected cell and its inputs
        if selected_cell != None:
            x, y = layer_locations[selected_cell]
            pygame.draw.circle(surface, layer_selected_color, (x, y), layer_input_radius)
                      
            x, y = self.on_bipolar_layer.locations[selected_cell]
            loc_ID  = str(x)+"."+str(y)
            connected_inputs = self.on_bipolar_layer.inputs[loc_ID]
            
            for i in connected_inputs:
                ID, w   = i
                ix, iy  = ID.split(".")
                ix, iy  = int(ix), int(iy)
                display_x, display_y = int(round(ix * self.visualization_scale)), int(round(iy * self.visualization_scale))
                color = lerpColors(self.visualization_background_color, input_color, w)
                pygame.draw.circle(surface, color, (display_x, display_y), input_neighbor_radius)
                
    
    
    
    def visualizeCellPlacement(self, surface, cell_type):
        
            if cell_type == "None":    
                cone_color          = self.cone_color
                horizontal_color    = self.horizontal_color
                horizontal_radius   = int(round(self.horizontal_neighbor_radius + 3*self.visualization_scale))  # Inflate the radius so they are visible behind cones
                on_bipolar_color    = self.on_bipolar_color
                off_bipolar_color   = self.off_bipolar_color
                drawOrder           = [[self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_neighbor_radius],
                                       [self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_neighbor_radius],
                                       [self.horizontal_locations, horizontal_color, horizontal_radius],
                                       [self.cone_locations, cone_color, self.cone_neighbor_radius]] 
            elif cell_type == "Cone":     
                cone_color          = self.cone_color
                horizontal_color    = self.horizontal_color_deselected
                horizontal_radius   = int(round(self.horizontal_neighbor_radius + 3*self.visualization_scale))
                on_bipolar_color    = self.on_bipolar_color_deselected
                off_bipolar_color   = self.off_bipolar_color_deselected
                drawOrder           = [[self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_neighbor_radius],
                                       [self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_neighbor_radius],
                                       [self.horizontal_locations, horizontal_color, horizontal_radius],
                                       [self.cone_locations, cone_color, self.cone_neighbor_radius]] 
            elif cell_type == "Horizontal":     
                cone_color          = self.cone_color_deselected 
                horizontal_color    = self.horizontal_color
                horizontal_radius   = int(round(self.horizontal_neighbor_radius + 3*self.visualization_scale))
                on_bipolar_color    = self.on_bipolar_color_deselected
                off_bipolar_color   = self.off_bipolar_color_deselected
                drawOrder           = [[self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_neighbor_radius],
                                       [self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_neighbor_radius],
                                       [self.cone_locations, cone_color, self.cone_neighbor_radius],
                                       [self.horizontal_locations, horizontal_color, horizontal_radius]] 
            elif cell_type == "On Bipolar":  
                cone_color          = self.cone_color_deselected 
                horizontal_color    = self.horizontal_color_deselected
                horizontal_radius   = int(round(self.horizontal_neighbor_radius + 3*self.visualization_scale))
                on_bipolar_color    = self.on_bipolar_color
                off_bipolar_color   = self.off_bipolar_color_deselected
                drawOrder           = [[self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_neighbor_radius],
                                       [self.horizontal_locations, horizontal_color, horizontal_radius],
                                       [self.cone_locations, cone_color, self.cone_neighbor_radius],
                                       [self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_neighbor_radius]] 
            else:     
                cone_color          = self.cone_color_deselected 
                horizontal_color    = self.horizontal_color_deselected
                horizontal_radius   = int(round(self.horizontal_neighbor_radius + 3*self.visualization_scale))
                on_bipolar_color    = self.on_bipolar_color_deselected
                off_bipolar_color   = self.off_bipolar_color
                drawOrder           = [[self.on_bipolar_locations, on_bipolar_color, self.on_bipolar_neighbor_radius],
                                       [self.horizontal_locations, horizontal_color, horizontal_radius],
                                       [self.cone_locations, cone_color, self.cone_neighbor_radius],
                                       [self.off_bipolar_locations, off_bipolar_color, self.off_bipolar_neighbor_radius]] 
            
            for locations, color, radius in drawOrder:
                for x, y in locations:
                    pygame.draw.circle(surface, color, (x, y), radius)
    
                
    def findActivityBounds(self, activities, estimated_min, estimated_max, activity_centered_on_zero):
        # Find the real max/min activity values
        max_activity = np.amax(activities)
        min_activity = np.amin(activities)
        
        print "\tTrue Max Activity Value:", max_activity
        print "\tTrue Min Activity Value:", min_activity
        
        # Impose an estimated max/min
        max_activity    = max(max_activity, estimated_max)
        min_activity    = min(min_activity, estimated_min)
        
        # If the range of activity values is expected to be symmetric and
        # centered on zero, then the max and min values should be equal
        if activity_centered_on_zero:
            bound           = max(abs(max_activity), abs(min_activity))
            max_activity    = bound
            min_activity    = -bound
            
        print "\tAdjusted Max Activity Value For Color Scale:", max_activity
        print "\tAdjusted Min Activity Value For Color Scale:", min_activity
        
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
        self.activity_player_max                = max_activity
        self.activity_player_min                = min_activity
        self.activity_player_centered_on_zero   = activity_centered_on_zero
                             
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
                self.legend.mode = vis_type
                pygame.display.set_caption(vis_type + " " + cell_type)
                self.visualizeCellPlacement(self.visualization_surface, cell_type)
            elif vis_type == "Activity":
                self.legend.mode = None
                pygame.display.set_caption(vis_type + " " + cell_type + " " + str(self.timestep))
                if cell_type == "Cone":
                    self.legend.mode = vis_type
                    self.playLayerActivity(self.visualization_surface, self.cone_activities,
                                           self.cone_locations, self.cone_neighbor_radius,
                                           self.cone_activity_bounds[0],
                                           self.cone_activity_bounds[1])
                elif cell_type == "Horizontal":
                    self.legend.mode = vis_type
                    self.playLayerActivity(self.visualization_surface, self.horizontal_activities,
                                           self.horizontal_locations, self.horizontal_neighbor_radius,
                                           self.horizontal_activity_bounds[0],
                                           self.horizontal_activity_bounds[1])
                elif cell_type == "On Bipolar":
                    self.legend.mode = vis_type
                    self.playLayerActivity(self.visualization_surface, self.on_bipolar_activities,
                                           self.on_bipolar_locations, self.on_bipolar_neighbor_radius,
                                           self.on_bipolar_activity_bounds[0],
                                           self.on_bipolar_activity_bounds[1])
                elif cell_type == "Off Bipolar":
                    self.legend.mode = vis_type
                    self.playLayerActivity(self.visualization_surface, self.off_bipolar_activities,
                                           self.off_bipolar_locations, self.off_bipolar_neighbor_radius,
                                           self.off_bipolar_activity_bounds[0],
                                           self.off_bipolar_activity_bounds[1])
            elif vis_type == "Input Weights":
                self.legend.mode = None
                if cell_type == "On Bipolar":
                    self.legend.mode = vis_type
                    self.visualizeInputWeights(self.visualization_surface, self.on_bipolar_locations,
                                               self.on_bipolar_neighbor_radius,
                                               self.on_bipolar_input_radius,
                                               self.cone_locations,
                                               self.cone_neighbor_radius,
                                               self.on_bipolar_color, self.on_bipolar_color_deselected,
                                               self.cone_color, mouse_x, mouse_y)
                
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
            

class Legend:
    def __init__(self, visualizer, position, width=200, height=200, 
                 background_color=(245,245,245), fontSize=22, fontName=None,
                 antialias=True, mode=None):
        self.visualizer         = visualizer
        self.width              = width
        self.height             = height
        self.surface            = pygame.Surface((width,height))
        self.position           = position
        self.background_color   = background_color
        self.mode               = mode
        
        self.font = pygame.font.Font(fontName, fontSize)
        cell_types  = ["Cone", "Horizontal", "On Bipolar", "Off Bipolar"]
        self.cell_labels = []
        for type_name in cell_types:
            surf = self.font.render(type_name, antialias, (0,0,0))
            rect = surf.get_rect()
            self.cell_labels.append([surf, rect])
        
        self.padding = min(width, height)/10.0 
    
    def draw(self, display):
        self.drawBlank()
        
        if self.mode == "Soma Placement":
            self.drawCellLabels()
        elif self.mode == "Activity":
            self.drawColorBar()
        elif self.mode == "Input Weights":
            self.drawCellLabels()
        elif self.mode == "Stimulus":
            pass
        
        display.blit(self.surface, self.position)
            
        
    def drawCellLabels(self):
        visualizer = self.visualizer
        cell_types  = ["Cone", "Horizontal", "On Bipolar", "Off Bipolar"] 
        cell_colors = [visualizer.retina.cone_color, visualizer.retina.horizontal_color,
                       visualizer.on_bipolar_color, visualizer.off_bipolar_color]
        cell_radii  = [visualizer.cone_neighbor_radius, visualizer.horizontal_neighbor_radius, 
                       visualizer.on_bipolar_neighbor_radius, visualizer.off_bipolar_neighbor_radius]
                       
        # Divide the legend in 4 rows x 2 cols
        dx = (self.width - 2.0*self.padding)/3.0
        dy = (self.height - 2.0*self.padding)/4.0
        
        left_label_min = None
        for c in range(len(cell_types)):
            cell_surf, cell_rect  = self.cell_labels[c]
            cell_color  = cell_colors[c]
            cell_radius = cell_radii[c]
            
            position = [int(dx), int(dy*(c+1.0))]
            pygame.draw.circle(self.surface, cell_color, position, cell_radius)
            
            
            cell_rect.center = [int(dx*2.0), int(dy*(c+1.0))]
            if left_label_min == None: 
                left_label_min = cell_rect.left
            else:
                left_label_min = min(left_label_min, cell_rect.left)
        
        for cell_surf, cell_rect in self.cell_labels:
            cell_rect.left = left_label_min
            self.surface.blit(cell_surf, cell_rect)
            
    def drawColorBar(self):
        steps = 10
        
        max_activity    = self.visualizer.activity_player_max
        min_activity    = self.visualizer.activity_player_min
        range_activity  = max_activity - min_activity
        centered        = self.visualizer.activity_player_centered_on_zero
        
        # Divide the legend in steps rows x 2 cols
        dx = (self.width - 2.0*self.padding)/3.0
        dy = (self.height - 2.0*self.padding)/(steps+1.0)
        
        for step in range(steps):
            activity = max_activity - (float(step)/float(steps-1) * range_activity)
            color = self.visualizer.mapActivityToColor(activity, min_activity, 
                                                       max_activity, centered)
            pygame.draw.rect(self.surface, color, [self.padding+dx/2.0, 
                                                   self.padding+dy*(step+1.0)-dy/2.0, 
                                                   dx, dy])
        
            surf = self.font.render("{0:.1f}".format(activity), True, (0,0,0))
            rect = surf.get_rect()
            rect.center = [self.padding+dx*2.0, self.padding+dy*(step+1.0)]
            self.surface.blit(surf, rect)
        pass


    def drawBlank(self):
        self.surface.fill(self.background_color)
        
            
            
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



#    def visualizeConeWeights(self):
#        
#        pygame.init()
#        displaySurface = pygame.display.set_mode((self.gridWidth, self.gridHeight))
#        displaySurface.fill((0,0,0))
#        
#        cl = self.coneLayer
#        
#        locID   = random.choice(cl.locations)
#        
#
#        rectx = self.stimulus.position[0]
#        recty = self.stimulus.position[1]        
#        rectw = self.stimulus.size[0]      
#        recth = self.stimulus.size[1]
#        pygame.draw.rect(displaySurface, (255,255,255), (rectx, recty, rectw, recth))
#
#        
#        
#        connectedPixels = cl.inputs[locID]
#        for p in connectedPixels:
#            pID, w = p
#            x, y = pID.split(".")
#            x, y = float(x), float(y)
#            rectx = self.stimulus.position[0] + x * self.stimulus.pixelSize
#            recty = self.stimulus.position[1] + y * self.stimulus.pixelSize
#            rects = self.stimulus.pixelSize
#            pygame.draw.rect(displaySurface, (w*255,0,0), (rectx, recty, rects, rects))
#            
#
#
#        # Get cone rectangle
#        x, y    = locID.split(".")
#        x, y    = float(x), float(y)
#        rectx = x - cl.input_field_radius_gridded
#        recty = y - cl.input_field_radius_gridded
#        rects = 2 * cl.input_field_radius_gridded
#        pygame.draw.rect(displaySurface, (0,0,255), (rectx, recty, rects, rects), 1)
#
#        running = True
#        while running:
#            for event in pygame.event.get():
#                if event.type == QUIT:
#                    running = False
#            pygame.display.update()

        
