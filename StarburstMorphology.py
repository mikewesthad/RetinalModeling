from random import uniform, randint, shuffle, choice
from igraph import Graph, ADJ_UNDIRECTED
import matplotlib.pyplot as plt
import numpy as np
import pygame
from pygame.locals import *
from Vector2D import Vector2D
from StarburstDendrite import DendriteSegment
from Compartment import GrowingCompartment
from Constants import *


class StarburstMorphology(object):
    
    def __init__(self, retina, location=Vector2D(0.0, 0.0), average_wirelength=150*UM_TO_M, 
                 radius_deviation=.1, min_branches=6, max_branches=6, heading_deviation=10, 
                 step_size=15*UM_TO_M, max_segment_length=35*UM_TO_M, children_deviation=20, 
                 dendrite_vision_radius=30*UM_TO_M, diffusion_width=45*UM_TO_M,
                 diffusion_strength=1.0, decay_rate=0.1, input_strength=0.0,
                 color_palette=GOLDFISH, draw_location=Vector2D(0.0,0.0), visualize_growth=True, scale=1.0,
                 display=None):
        
        # General neuron variables
        self.retina             = retina
        self.display            = display
        self.location           = location
        
        # Visualization variables
        self.visualize_growth   = visualize_growth
        self.display            = display 
        self.background_color   = color_palette[0]
        self.draw_location      = draw_location
        self.scale              = scale
            
        grid_size               = retina.grid_size
    
        # Wirelength variables
        average_wirelength      = average_wirelength / grid_size
        max_wirelength          = average_wirelength * (1.0+radius_deviation)
        min_wirelength          = average_wirelength * (1.0-radius_deviation)
        self.bounding_radius    = max_wirelength
        
        # Dendrite variables
        self.heading_deviation      = heading_deviation
        self.step_size              = step_size / grid_size
        self.max_segment_length     = max_segment_length / grid_size
        self.dendrite_vision_radius = dendrite_vision_radius / grid_size
        
        # Initialize the first branches
        number_dendrites    = randint(min_branches, max_branches)
        heading_spacing     = 360.0 / number_dendrites
        heading             = 0.0
        
        self.dendrites = []
        for i in range(number_dendrites):
            wirelength = uniform(min_wirelength, max_wirelength)
            dendrite = DendriteSegment(self, self.location, heading, wirelength, wirelength,
                                       children_deviation, self.dendrite_vision_radius, i)
            dendrite.registerDendriteWithNeuron()                                                                       
            heading += heading_spacing
        
        # Slicing needed to force a copy of the elements (instead of creating a reference to a list)
        # Note: this only works if the lists are not nested (if they are, use deepcopy)
        self.master_dendrites           = self.dendrites[:]  
        self.number_master_dendrites    = len(self.master_dendrites)
        
        # Grow and color the dendrites
        self.grow()              
        self.number_dendrites = len(self.dendrites)        
        self.colorDendrites(color_palette[1:])  
        
        # Build compartments (this assumes compartments are line segments)
        self.compartmentalizeLineSegments()
        self.buildLineSegmentShortestPaths()
        self.colorCompartments(color_palette[1:])
        self.discretizeCompartments(1.0)
        self.createPointsOnCompartments()
        self.establishPointSynapses()
        self.establishCompartmentSynapses()
        
        # Establish variables needed for activity
        self.decay_rate         = decay_rate
        self.input_strength     = input_strength
        self.diffusion_width    = diffusion_width / retina.grid_size
        self.diffusion_strength = diffusion_strength
        self.establisthLineSegmentDiffusionWeights()
        
    
    def grow(self):
        
        active_dendrites = self.master_dendrites[:]
        
        running = True
        i       = 0
        while running and active_dendrites != []:
            
            # Grab a dendrite and update it
            dendrite = active_dendrites[i]
            is_growing, children = dendrite.grow()
            
            # If it isn't growing, delete it and adjust index
            if not(is_growing):
                del active_dendrites[i]
                i -= 1
            
            # If it had children, add them to the active list                 
            if children != []:
                for child in children: 
                    active_dendrites.insert(0, child)
            
            # Increment index
            i += 1
            if i >= len(active_dendrites): i=0
            
            if self.visualize_growth:
                self.display.fill(self.background_color)
                self.draw(self.display, new_location=self.draw_location,
                          draw_segments=True, scale=self.scale)
                pygame.display.update()
                    
                # Check for close button signal from pygame window
                for event in pygame.event.get():
                    if event.type == QUIT: running = False
    
            
    def colorCompartments(self, palette):
        colors  = palette
        index   = 0
        for compartment in self.master_compartments:
            compartment.colorCompartments(colors, index)
            index += 1
            if index >= len(colors): index = 0
            
    def colorDendrites(self, palette):
        colors  = palette
        index   = 0
        for dendrite in self.master_dendrites:
            dendrite.colorDendrites(colors, index)
            index += 1
            if index >= len(colors): index = 0
    
            
    def establishCompartmentSynapses(self):
        for compartment in self.compartments:
            compartment.buildNeurotransmitterWeights()
    
    def establishPointSynapses(self):
        inputs  = set([GLU])
        outputs = set([GABA, ACH])
        
        output_threshold_wirelength = 2.0/3.0 * self.bounding_radius
        
        for point in self.points:
            if point.wirelength >= output_threshold_wirelength:
                point.neurotransmitters_released = outputs.copy() # SHALLOW COPY!
            point.neurotransmitters_accepted = inputs.copy() # SHALLOW COPY!

    def compartmentalizeLineSegments(self):
        self.compartments = []
        
        # Build the master compartments recursively
        self.master_compartments = []
        for dendrite in self.master_dendrites:            
            compartment = GrowingCompartment(self)
            self.master_compartments.append(compartment)

        # Recursively compartmentalize starting from the master compartments
        for index in range(len(self.master_compartments)):
            compartment = self.master_compartments[index]
            
            proximal_compartments = []
            for other_compartment in self.master_compartments:
                if compartment != other_compartment: 
                    proximal_compartments.append(other_compartment)
            
            dendrite = self.master_dendrites[index]
            dendrite.compartmentalizeLineSegments(compartment, prior_compartments=proximal_compartments)
    
    def discretize(self, delta):
        for dendrite in self.master_dendrites:
            dendrite.discretize(delta=delta)
            
    def discretizeCompartments(self, delta):
        for compartment in self.master_compartments:
            compartment.discretize(delta=delta)
    
    def createPoints(self):
        self.points = []
        for dendrite in self.master_dendrites:
            dendrite.createPoints(self.location, 0.0)
            
    def createPointsOnCompartments(self):
        self.points = []
        for compartment in self.master_compartments:
            compartment.createPoints(self.location, 0.0)
    
    
    def buildLineSegmentShortestPaths(self):
        distance_adjacency = []
        number_segments = len(self.compartments)
        for row_num in range(number_segments): 
            distance_row    = []
            for element_num in range(number_segments):
                distance_row.append(0.0)
            distance_adjacency.append(distance_row)
            
        for compartment in self.compartments:
            for neighbor in compartment.distal_neighbors + compartment.proximal_neighbors:
                distance_adjacency[compartment.index][neighbor.index] = self.step_size
                distance_adjacency[neighbor.index][compartment.index] = self.step_size
                
        self.distance_adjacency = distance_adjacency
        self.distance_graph     = Graph.Weighted_Adjacency(distance_adjacency, mode=ADJ_UNDIRECTED)
        self.distances          = np.array(self.distance_graph.shortest_paths(weights="weight"))
        
        for row in range(number_segments):
            col = row
            self.distances[row][col] = 0.0
            
    def establisthLineSegmentDiffusionWeights(self, diffusion_method="Gaussian Distance"):
        number_segments         = len(self.compartments)
        self.diffusion_weights  = np.zeros((number_segments, number_segments))
        sigma                   = self.diffusion_width
        
        np_distances    = np.array(self.distances)
        np_lengths      = np.array(np.ones((1, number_segments))) * self.step_size
        
        for row in range(number_segments):
            for col in range(number_segments):
                distance = float(self.distances[row][col])
                volume = 0.0
                np_distance_row = np_distances[row,:]
                matching_cols, = np.where(np_distance_row<=distance)
                volume += np.sum(np_lengths[0, matching_cols])
                
                if diffusion_method == "Gaussian Volume":
                    self.diffusion_weights[row, col] = volume
                elif diffusion_method == "Gaussian Distance":
                    self.diffusion_weights[row, col] = distance
                elif diffusion_method == "Average Everyone":
                    self.diffusion_weights[row, col] = 1.0
                elif diffusion_method == "Nearest Neighbor Average":
                    if distance <= self.step_size: 
                        self.diffusion_weights[row, col] = 1.0
                    else: 
                        self.diffusion_weights[row, col] = 0.0
        
        if (diffusion_method == "Gaussian Volume") or (diffusion_method == "Gaussian Distance"): 
            self.diffusion_weights = np.exp(-self.diffusion_weights**2.0/(2.0*sigma**2.0))
            
        # Get the sum of each row
        row_sum = np.sum(self.diffusion_weights, 1)
        
        # Reshape the rowSum into a column vector since sum removes a dimension
        row_sum.shape = (len(self.compartments), 1)
        
        # Normalize the weight matrix
        self.diffusion_weights = self.diffusion_weights / row_sum
            
    def branchProbability(self, segment_length):
        return 1.05**(segment_length-self.max_segment_length)
        
    def drawDiffusionWeights(self, surface, index, new_location=None, scale=1.0):
        max_diffusion           = np.max(self.diffusion_weights)
        selected_compartment    = index   
        
        np.set_printoptions(precision=3, suppress=True, linewidth=300)
        print self.diffusion_weights[selected_compartment,:]
        
        for i in range(len(self.compartments)):
            compartment = self.compartments[i]
            diffusion   = self.diffusion_weights[selected_compartment,i]
            max_diffusion = np.max(self.diffusion_weights[selected_compartment,:])
            percent     = diffusion/float(max_diffusion)
            
            new_color = (int(percent*255),int(percent*255),int(percent*255))
            compartment.color = new_color
            
        self.draw(surface, scale=scale, new_location=new_location, 
                  draw_compartments=True, draw_text=True) 
    
        
    def draw(self, surface, scale=1.0, new_location=None, draw_segments=False,
             draw_compartments=False, draw_points=False, draw_text=False):
        
        # Shift the cell's location
        if new_location == None: 
            new_location = self.location
        old_location = self.location
        self.location = new_location   
        
        if draw_segments:
            for dendrite in self.dendrites:
                dendrite.draw(surface, scale=scale)
        elif draw_compartments:
            for compartment in self.compartments:
                compartment.draw(surface, scale=scale, draw_text=draw_text)
        elif draw_points:
            for point in self.points:
                point.draw(surface, scale=scale)
                
        # Shift the cell's location back to the original
        self.location = old_location
        
  



# .............................................................................
# Old functions that may not be used?
# .............................................................................

#    def establisthDiffusionWeights(self):
#        self.buildGraph()
#        self.distances = self.findShortestPathes()
##        
##        # Perform e^(-distance**2/width) on each element in the distance matrix
##        sigma = self.diffusion_width
##        self.diffusion_weights = np.exp(-(self.distances)**2/(2.0*sigma**2.0))
##        
##        # Get the sum of each row
##        row_sum = np.sum(self.diffusion_weights, 1)
##        
##        # Reshape the rowSum into a column vector since sum removes a dimension
##        row_sum.shape = (len(self.compartments), 1)
##        
##        # Normalize the weight matrix
##        self.diffusion_weights = self.diffusion_weights / row_sum
#        
#    def findShortestPathes(self):
#        branching_shortest_paths    = np.array(self.branching_graph.shortest_paths(weights="weight"))
#        distance_shortest_paths     = np.array(self.distance_graph.shortest_paths(weights="weight"))
#        
#        
#        for a in range(self.number_dendrites):
#            for b in range(a, self.number_dendrites):
#                if a == b:
#                    # There is no effect of branching on youself
#                    branching_shortest_paths[a][a] = 1.0
#                else:
#                    dendrite_a = self.dendrites[a]
#                    dendrite_b = self.dendrites[b]
#                    
#                    if dendrite_a.master_branch_ID == dendrite_b.master_branch_ID:
#                        power           = branching_shortest_paths[a][b]
#                        branch_factor   = 1.0/(2.0**power)
#                    else:
#                        power           = branching_shortest_paths[a][b] - 1.0
#                        branch_factor   = 1.0/(2.0**power * (self.number_master_dendrites - 1.0)) 
#                        
#                    branching_shortest_paths[a][b] = branch_factor
#                    branching_shortest_paths[b][a] = branch_factor
#    
#    def buildGraph(self):
#        branching_adjacency = []
#        distance_adjacency  = []
#        for row_num in range(self.number_dendrites): 
#            branching_row   = []
#            distance_row    = []
#            for element_num in range(self.number_dendrites):
#                branching_row.append(0.0)
#                distance_row.append(0.0)
#            branching_adjacency.append(branching_row)
#            distance_adjacency.append(distance_row)
#        
#        for master_number in range(self.number_master_dendrites):
#            for other_master_number in range(master_number+1, self.number_master_dendrites):
#                master          = self.master_dendrites[master_number]
#                other_master    = self.master_dendrites[other_master_number]
#                
#                master_index        = master.index
#                other_index         = other_master.index
#                dist_master_other   = master.length/2.0 + other_master.length/2.0
#                
#                branching_adjacency[master_index][other_index]  = 1.0
#                branching_adjacency[other_index][master_index]  = 1.0
#                
#                distance_adjacency[master_index][other_index]   = dist_master_other
#                distance_adjacency[other_index][master_index]   = dist_master_other
#            
#            
#        
#        for dendrite in self.dendrites:
#            if dendrite.children != []:
#                child1, child2 = dendrite.children
#                
#                dendrite_index  = dendrite.index
#                child1_index    = child1.index
#                child2_index    = child2.index 
#                
#                dist_dendrite_child1    = dendrite.length/2.0 + child1.length/2.0
#                dist_dendrite_child2    = dendrite.length/2.0 + child2.length/2.0
#                dist_child1_child2      = child1.length/2.0 + child2.length/2.0
#               
#                branching_adjacency[dendrite_index][child1_index]   = 1.0
#                branching_adjacency[child1_index][dendrite_index]   = 1.0
#                branching_adjacency[dendrite_index][child2_index]   = 1.0
#                branching_adjacency[child2_index][dendrite_index]   = 1.0
#                branching_adjacency[child1_index][child2_index]     = 1.0
#                branching_adjacency[child2_index][child1_index]     = 1.0
#                
#                distance_adjacency[dendrite_index][child1_index]    = dist_dendrite_child1
#                distance_adjacency[child1_index][dendrite_index]    = dist_dendrite_child1
#                distance_adjacency[dendrite_index][child2_index]    = dist_dendrite_child2
#                distance_adjacency[child2_index][dendrite_index]    = dist_dendrite_child2
#                distance_adjacency[child1_index][child2_index]      = dist_child1_child2
#                distance_adjacency[child2_index][child1_index]      = dist_child1_child2
#         
#        self.branching_adjacency    = branching_adjacency
#        self.branching_graph        = Graph.Weighted_Adjacency(branching_adjacency, mode=ADJ_UNDIRECTED)
#        self.distance_adjacency     = distance_adjacency
#        self.distance_graph         = Graph.Weighted_Adjacency(distance_adjacency, mode=ADJ_UNDIRECTED)

    def buildCompartmentBoundingPolygons(self):
        for compartment in self.compartments:
            compartment.buildBoundingPolgyon()
            
    def compartmentalizePoints(self, compartment_size):
        self.compartments = []
        
        # Build the master compartments recursively
        self.master_compartments = []
        for dendrite in self.master_dendrites:            
            compartment = GrowingCompartment(self)
            self.master_compartments.append(compartment)

        # Recursively compartmentalize starting from the master compartments
        for index in range(len(self.master_compartments)):
            compartment = self.master_compartments[index]
            
            proximal_compartments = []
            for other_compartment in self.master_compartments:
                if compartment != other_compartment: 
                    proximal_compartments.append(other_compartment)
            
            dendrite = self.master_dendrites[index]
            dendrite.compartmentalizePoints(compartment, compartment_size, compartment_size,
                                            prior_compartments=proximal_compartments)
    
    def plotBranchProbability(self):
        xs = np.arange(0, self.max_segment_length, 0.1)
        ys = [self.branchProbability(x) for x in xs]
        plt.plot(xs,ys)
        plt.title("Branching as a Function of Wirelength")
        plt.xlabel("Fraction of Max Wirelength")
        plt.ylabel("Branch Probability")
        plt.grid(True)
        plt.show()
            
    def findCentroid(self):
        average_location = Vector2D(0.0, 0.0)
        number_locations = 0.0
        for dendrite in self.dendrites:
            for location in dendrite.locations:
                average_location += location
                number_locations += 1.0
        average_location /= number_locations
        soma_to_average = average_location.distanceTo(Vector2D(0.0,0.0))
        soma_to_average_fraction = soma_to_average / self.bounding_radius
        print "Cell Centroid:\t\t\t\t\t", average_location
        print "Number of Dendrite Points (before discretization):\t\t{0:,.0f}".format(number_locations)
        print "Linear Distance from Soma to Centroid:\t\t\t{0:.3f}".format(soma_to_average)
        print "Linear Distance from Soma to Centroid Normalized by Radius:\t{0:.3%}".format(soma_to_average_fraction)
        print














###############################################################################
# Old functions that may get retired soon
###############################################################################

    def animateCompartments(self, surface):
        compartments_to_draw = self.master_compartments[:]
#        compartments_to_draw = [choice(self.compartments)]
            
        
        running = True
        next_iteration = False
        while running:
            surface.fill((255,255,255))
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    next_iteration = True
        
            for c in self.compartments:
                old_color = c.color
                c.color = (0,0,0)
                c.draw(surface)
                c.color = old_color
            for c in compartments_to_draw:
                c.draw(surface)
            
            pygame.display.update()
                
                
            if next_iteration:
                
                print "<<<<<<<<<<<<<<<<<<<"
                for c in compartments_to_draw:
                    print c.index,
                print
                
                distal_neighbors = []
                for c in compartments_to_draw:
                    distal_neighbors.extend(c.distal_neighbors)
#                    distal_neighbors.extend(c.proximal_neighbors)
                compartments_to_draw = distal_neighbors
                
                print "==================="
                for c in compartments_to_draw:
                    print c.index,
                print                
                print ">>>>>>>>>>>>>>>>>>>"
                
                next_iteration = False
       
        



