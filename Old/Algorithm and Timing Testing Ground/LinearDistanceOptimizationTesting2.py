import numpy as np
import time
import random

def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5

def npLinearDistance(x1, y1, x2, y2):
    return np.linalg.norm(np.array([x1, y1])-np.array([x2, y2]))

def npAlreadyArrayLinearDistance(p1, p2):
    return np.linalg.norm(p1-p2)




width   = 1000
height  = 1000


withoutnp = 0
withnp = 0
withnpalreadyarray = 0

for i in xrange(10000):
    x1 = random.uniform(0,width)
    y1 = random.uniform(0,height)
    x2 = random.uniform(0,width)
    y2 = random.uniform(0,height)
    
    s = time.clock()
    linearDistance(x1, y1, x2, y2)
    withoutnp += time.clock() - s

    s = time.clock()
    npLinearDistance(x1, y1, x2, y2)
    withnp += time.clock() - s

    a1 = np.array([x1, y1])
    a2 = np.array([x2, y2])
    s = time.clock()
    npAlreadyArrayLinearDistance(a1, a2)
    withnpalreadyarray += time.clock() - s

print withoutnp
print withnp
print withnpalreadyarray
