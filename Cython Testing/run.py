import NearestNeighborPlacement
import timeit
#
#iterations = 1000
#
#start = time.clock()
#for x in range(iterations):
#    NearestNeighborPlacement.linearDistance(0, 0, 10, 10)
#print time.clock() - start
#
#
#start = time.clock()
#for x in range(iterations):
#    NearestNeighborPlacement.linearDistancePython(0, 0, 10, 10)
#print time.clock() - start



#t1 = timeit.timeit("NearestNeighborPlacement.placeNeurons(400, 400, 1000, 10.0, 10000)", setup="import NearestNeighborPlacement", number=10)
#print t1
#
#t2 = timeit.timeit("NearestNeighborPlacement.placeNeuronsPython(400, 400, 1000, 10.0, 10000)", setup="import NearestNeighborPlacement", number=10)
#print t2
#
#print t1/t2


import Retina

r = Retina.Retina(400, 400, 1, 1)
r.buildConeLayer(10, 1000)

