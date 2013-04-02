import math
import random
import time

def linearDistance(x1, y1, x2, y2):
    return ((x2-x1)**2.0 + (y2-y1)**2.0)**0.5


def linearDistanceMath(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2))


width   = 1000
height  = 1000


withoutMathModule = 0
withMathModule = 0
for i in xrange(1000000):
    x1 = random.uniform(0,width)
    y1 = random.uniform(0,height)
    x2 = random.uniform(0,width)
    y2 = random.uniform(0,height)
    
    s = time.clock()
    linearDistance(x1, y1, x2, y2)
    withoutMathModule += time.clock() - s

    s = time.clock()
    linearDistanceMath(x1, y1, x2, y2)
    withMathModule += time.clock() - s

print "With Math Module:", withMathModule
print "Without Math Module:", withoutMathModule
