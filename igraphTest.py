# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 16:48:08 2013

@author: mikewesthad
"""

import numpy as np
from igraph import *

compartments = 10000


a = np.random.random_integers(0, 1, size=(compartments,compartments))

print "Random Matrix Generated"
g = Graph.Adjacency(a.tolist(), mode=ADJ_UNDIRECTED)
print "Graph Created from Matrix"
shortest =  g.shortest_paths()

#for i in shortest:
#    print i