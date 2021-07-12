from unittest import TestCase
from context import LWWElementGraph


class IntegrationTests(TestCase):
    ''' Although we are using unittest as the testing framework in the project,
        I wanted to include integration tests which test out the behaviour of
        LWWWElementGraph as a whole, edge cases. In the future, we can 
        move these tests to an Integration Testing framework in Python '''

    def testMergeGraphAndPerformBFS(self):
        ''' Testcase for Creating 2 Graphs by Adding / Removing Vertices and Edges,
            Merging the 2 Graphs and then finding path between Vertices using BFS.
            Path changes when new node is added to merged graph '''
        firstGraph = LWWElementGraph()
        secondGraph = LWWElementGraph()
        removeEdgeInFirstGraph = {3, 4}
        removeEdgeInSecondGraph = {4, 6}

        for i in range(7):
            firstGraph.addVertex(i)
        firstGraph.removeVertex(0)
        for v1, v2 in [{1, 2}, {2, 4}, removeEdgeInFirstGraph, removeEdgeInSecondGraph, {5, 1}]:
            firstGraph.addEdge(v1, v2)
        firstGraph.removeEdge(*removeEdgeInFirstGraph)
        firstGraph.removeVertex(5)

        for i in range(3, 9):
            secondGraph.addVertex(i)
        for v1, v2 in [{3, 5}, {4, 5}, removeEdgeInSecondGraph, {5, 6}, {5, 7}, {6, 7}]:
            secondGraph.addEdge(v1, v2)
        secondGraph.removeEdge(*removeEdgeInSecondGraph)

        firstGraph.mergeGraphs(secondGraph)
        firstGraph.addEdge(2, 3)
        self.assertSetEqual(set(firstGraph.getNeighborsOf(4)), {2, 5})
        self.assertListEqual(firstGraph.findPath(1, 7), [1, 2, 4, 5, 7])
        firstGraph.addEdge(1, 8)
        firstGraph.addEdge(7, 8)
        self.assertListEqual(firstGraph.findPath(1, 7), [1, 8, 7])
    
    def testRemovedVertexMerge(self):
        ''' Removing a Vertex on the Second Graph should remove that Vertex AND ITS EDGES 
            on the Merged Graph. According to "A comprehensive study of Convergent and Commutative 
            Replicated Data Types", page 29. '''
        firstGraph = LWWElementGraph()
        secondGraph = LWWElementGraph()
        for i in range(4):
            firstGraph.addVertex(i)        
            secondGraph.addVertex(i)
        firstGraph.removeVertex(3)
        secondGraph.removeVertex(0)
        firstGraph.addEdge(0,1)
        secondGraph.addEdge(2,3)

        firstGraph.mergeGraphs(secondGraph)
        self.assertSetEqual(set(firstGraph.vertices.getMembers()), {1,2})
        self.assertListEqual(firstGraph.edges.getMembers(), [])
        self.assertEqual(len(firstGraph.graphState), 2)

    def testRemovedEdgeMerge(self):
        ''' Removing an Edge on the Second Graph should  
            remove that Edge on the Merged Graph '''
        firstGraph = LWWElementGraph()
        secondGraph = LWWElementGraph()
        for i in range(4):
            firstGraph.addVertex(i)    
            secondGraph.addVertex(i)
        for v1, v2 in [{0, 1}, {2, 3}]:
            firstGraph.addEdge(v1, v2)
            secondGraph.addEdge(v1, v2)
        firstGraph.removeEdge(0, 1)
        secondGraph.removeEdge(2, 3)

        firstGraph.mergeGraphs(secondGraph)
        self.assertSetEqual(set(firstGraph.vertices.getMembers()), {0,1,2,3})
        self.assertListEqual(firstGraph.edges.getMembers(), [])
        self.assertEqual(len(firstGraph.graphState), 4)
        
    def testMergeCommutativity(self):
        ''' Testcase for ensuring that firstGraph merged with secondGraph
            should be the same as secondGraph merge with firstGraph'''
        
        def setupGraphs():
            firstGraph = LWWElementGraph()
            secondGraph = LWWElementGraph()
            for i in range(4):
                firstGraph.addVertex(i)
                secondGraph.addVertex(i)
            firstGraph.removeVertex(3)
            secondGraph.removeVertex(0)
            firstGraph.addEdge(0, 1)
            secondGraph.addEdge(2, 3)
            firstGraph.addEdge(1, 2)
            return firstGraph, secondGraph
        
        g1, g2 = setupGraphs()
        g1.mergeGraphs(g2)
        g3, g4 = setupGraphs()
        g4.mergeGraphs(g3)
        self.assertCountEqual(g1.vertices.getMembers(), g4.vertices.getMembers())
        self.assertCountEqual(g1.edges.getMembers(), g4.edges.getMembers())

    def testMergeIdempotency(self):
        ''' Graph merged with itself should be the same graph ''' 
        def setupGraph():
            firstGraph = LWWElementGraph()
            for i in range(4):
                firstGraph.addVertex(i)
            firstGraph.removeVertex(3)
            firstGraph.addEdge(0, 1)
            firstGraph.addEdge(1, 2)
            firstGraph.addEdge(0, 2)
            return firstGraph
        
        g1 = setupGraph()
        g1.mergeGraphs(g1)
        g2 = setupGraph()
        self.assertCountEqual(g1.vertices.getMembers(), g2.vertices.getMembers())
        self.assertCountEqual(g1.edges.getMembers(), g2.edges.getMembers())

    def testMergeAssociativity(self):
        ''' (A merge B) merge C should equal A merge (B merge C) ''' 
        def setupGraphs():
            firstGraph = LWWElementGraph()
            secondGraph = LWWElementGraph()
            thirdGraph = LWWElementGraph()
            for i in range(4):
                firstGraph.addVertex(i)
                secondGraph.addVertex(i)
            firstGraph.removeVertex(3)
            secondGraph.removeVertex(0)
            for i in range(4, 7):
                thirdGraph.addVertex(i)
            thirdGraph.removeVertex(5)
            firstGraph.addEdge(0, 1)
            secondGraph.addEdge(2, 3)
            firstGraph.addEdge(1, 2)
            return firstGraph, secondGraph, thirdGraph
        
        g1, g2, g3 = setupGraphs()
        g1.mergeGraphs(g2)
        g1.mergeGraphs(g3)

        g4, g5, g6 = setupGraphs()
        g5.mergeGraphs(g6)
        g4.mergeGraphs(g5)

        self.assertCountEqual(g1.vertices.getMembers(), g4.vertices.getMembers())
        self.assertCountEqual(g1.edges.getMembers(), g4.edges.getMembers())
