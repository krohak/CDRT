from unittest import TestCase
from context import LWWElementGraph

class IntegrationTests(TestCase):
    ''' Although we are using unittest as the testing framework,
        I wanted to include integration tests which test out the behaviour of
        LWWWElementGraph as a whole with edge cases. In the future, we can 
        move these tests to an Integration Testing framework in Python '''

    def testMergeGraphAndPerformBFS(self):
        firstGraph = LWWElementGraph()
        secondGraph = LWWElementGraph()
        removeEdgeInFirstGraph = {3,4}
        removeEdgeInSecondGraph = {4,6}

        for i in range(7):
            firstGraph.addVertex(i)
        firstGraph.removeVertex(0)        
        for v1, v2 in [{1,2}, {2,4}, removeEdgeInFirstGraph, removeEdgeInSecondGraph, {5,1}]:
            firstGraph.addEdge(v1, v2)
        firstGraph.removeEdge(*removeEdgeInFirstGraph)
        firstGraph.removeVertex(5)
        
        for i in range(3,9):
            secondGraph.addVertex(i)
        for v1, v2 in [{3,5}, {4,5}, removeEdgeInSecondGraph, {5,6}, {5,7}, {6,7}]:
            secondGraph.addEdge(v1, v2)
        secondGraph.removeEdge(*removeEdgeInSecondGraph)

        firstGraph.mergeGraphs(secondGraph)
        firstGraph.addEdge(2, 3)
        self.assertSetEqual(firstGraph.getNeighborsOf(4), {2,5})
        self.assertListEqual(firstGraph.findPath(1, 7), [1, 2, 3, 5, 7])
        firstGraph.addEdge(1, 8); firstGraph.addEdge(7, 8)
        self.assertListEqual(firstGraph.findPath(1, 7), [1, 8, 7])

class IntegrationTestsComplexObject(TestCase):
    pass