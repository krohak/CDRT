from unittest import TestCase, mock
from datetime import datetime
from collections import defaultdict
from random import random
from context import LWWElementGraph, LWWElementSet, hashObj, SRC_PATH

def createComplexObj():
    ''' Outputs a complex Python dictionary obj with embedded dict, list, string and float '''
    return [{
            'timestamp' : [ random() * 10**4 ],
            'event': {
                    'ABS_MT_POSITION_X': '{}'.format(int(random() * 10**8)),
                    'ABS_MT_POSITION_Y': '{}'.format(int(random() * 10**8)),
                    'ABS_MT_PRESSURE': '{}'.format(int(random() * 10**8)),
                }
    }]

class LWWElementGraphTests(TestCase):

    def testInit(self):
        ''' Check if Vertices and Edges are initialized to LWWElementSet instance '''
        g = LWWElementGraph()
        self.assertTrue(isinstance(g.vertices, LWWElementSet))
        self.assertTrue(isinstance(g.edges, LWWElementSet))
        
    @mock.patch('{}.LWWElementSet.LWWElementSet.addElement'.format(SRC_PATH))
    def testAddVertex(self, mockSetAddElement):
        ''' Check if vertices.addElement is called '''
        g = LWWElementGraph()
        g.graphState = mock.MagicMock()
        g.addVertex('a')
        mockSetAddElement.assert_called_once_with('a')
        g.graphState.__getitem__.assert_called_with(hashObj('a'))

    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    def testRemoveFails(self, mockIsMember):
        ''' Cannot remove before adding vertex '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.removeVertex('a')

    @mock.patch('{}.LWWElementGraph.LWWElementGraph._removeVertex'.format(SRC_PATH))
    @mock.patch('{}.LWWElementSet.LWWElementSet.removeElement'.format(SRC_PATH))
    @mock.patch('{}.LWWElementSet.LWWElementSet.getMembers'.format(SRC_PATH))
    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    def testRemoveVertex(self, mockIsMember, mockGetMembers, mockSetRemoveElement, _mockGraphRemoveVertex):
        ''' Check remove vertex and all its edges. Also check if _removeVertex is called '''
        mockIsMember.return_value = True
        mockGetMembers.return_value = [{'a', 'b'}, {'b', 'c'}, {'c', 'a'}]
        g = LWWElementGraph()
        g.removeVertex('a')
        calls = [mock.call('a'), mock.call({'a', 'b'}), mock.call({'c', 'a'})]
        mockSetRemoveElement.assert_has_calls(calls)
        self.assertTrue(_mockGraphRemoveVertex.called)

    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    def testAddEdgeFails(self, mockIsMember):
        ''' Cannot add edge if vertex not present '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.addEdge('a', 'b')
    
    @mock.patch('{}.LWWElementGraph.LWWElementGraph._addEdge'.format(SRC_PATH))
    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    @mock.patch('{}.LWWElementSet.LWWElementSet.addElement'.format(SRC_PATH))
    def testAddEdge(self, mockSetAddElement, mockIsMember, _mockGraphAddEdge):
        ''' Check if addElement to edge LWWSet. Also check if _addEdge is called '''
        mockIsMember.return_value = True
        g = LWWElementGraph()
        g.addEdge('a', 'b')
        mockSetAddElement.assert_called_once_with({'a','b'})
        self.assertTrue(_mockGraphAddEdge.called)

    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    def testRemoveEdgeFails(self, mockIsMember):
        ''' Cannot remove edge if it doesnt exist '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.removeEdge('a', 'b')

    @mock.patch('{}.LWWElementGraph.LWWElementGraph._removeEdge'.format(SRC_PATH))
    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    @mock.patch('{}.LWWElementSet.LWWElementSet.removeElement'.format(SRC_PATH))
    def testRemoveEdge(self, mockSetRemoveElement, mockIsMember, _mockGraphRemoveEdge):
        ''' Check if removeElement in edge LWWSet. Also check if _removeEdge is called '''
        mockIsMember.return_value = True
        LWWElementGraph().removeEdge('a', 'b')
        mockSetRemoveElement.assert_called_once_with({'a','b'})
        self.assertTrue(_mockGraphRemoveEdge.called)
    
    def testIsMember(self):
        ''' Check if isMember accesses graphState '''
        g = LWWElementGraph()
        g.graphState = {hashObj('a'): set()}
        self.assertTrue(g.isMember('a'))
        self.assertFalse(g.isMember('b'))

    @mock.patch('{}.LWWElementGraph.LWWElementGraph.isMember'.format(SRC_PATH))
    def testGetNeighborsOfFails(self, mockGraphIsMember):
        ''' Cannot getNeighboursOf if vertex not present '''
        mockGraphIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.getNeighborsOf('a')

    @mock.patch('{}.LWWElementGraph.LWWElementGraph.isMember'.format(SRC_PATH))
    def testGetNeighbors(self, mockGraphIsMember):
        ''' Check if getNeighboursOf accesses graphState '''
        mockGraphIsMember.return_value = True
        g = LWWElementGraph()
        g.graphState = {hashObj(1): [2, 3, 4], hashObj(2): [1]}
        self.assertListEqual(g.getNeighborsOf(1), [2,3,4])
        self.assertListEqual(g.getNeighborsOf(2), [1])

    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    @mock.patch('{}.LWWElementGraph.LWWElementGraph.getNeighborsOf'.format(SRC_PATH))
    def testFindPath(self, mockGetNeighborsOf, mockIsMember):
        ''' Check if BFS runs correctly, given custom graph '''
        graph = {
            1: [2], 
            2: [1, 3, 4],
            3: [2, 5],
            4: [2, 5],
            5: [3, 4, 6, 7],
            6: [5, 7],
            7: [5, 6],
        }
        mockGetNeighborsOf.side_effect = lambda x: graph[x]
        mockIsMember.return_value = True
        g = LWWElementGraph()
        self.assertListEqual(g.findPath(1, 7), [1, 2, 3, 5, 7])
    
    @mock.patch('{}.LWWElementGraph.LWWElementGraph._computeGraph'.format(SRC_PATH))
    def testMergeGraphs(self, _mockComputeGraph):
        ''' Check if vertices and edges are merged using LLWElementSet mergeWith
            Also check if _computeGraph is called with the right parameters '''
        g1 = LWWElementGraph()        
        g1.vertices, g1.edges = mock.MagicMock(), mock.MagicMock()
        g1.vertices.getMembers.return_value = ['v1'] 
        g1.edges.getMembers.return_value = [{'v1', 'v2'}]
        g1.vertices.isMember.return_value = False
        g2 = LWWElementGraph()
        g1.mergeGraphs(g2)
        g1.vertices.mergeWith.assert_has_calls([mock.call(g2.vertices)])
        g1.edges.mergeWith.assert_has_calls([mock.call(g2.edges)])
        g1.edges.removeElement.assert_called_once_with({'v1', 'v2'})
        _mockComputeGraph.assert_called_once_with(['v1'], [{'v1', 'v2'}])
    
    @mock.patch('{}.LWWElementGraph.hashObj'.format(SRC_PATH))
    def test_removeVertex(self, mockHash):
        ''' Check if _removeVertex updates the graphState by removing the vertex and 
            its edges with other vertices. '''
        mockHash.side_effect = lambda x: x
        graphState = {
            1: [2, 4], 
            2: [1, 3],
            3: [2],
            4: [1],
        }
        g = LWWElementGraph()
        self.assertDictEqual(g._removeVertex(graphState, 2), {1: [4], 3: list(), 4: [1]})

    @mock.patch('{}.LWWElementGraph.hashObj'.format(SRC_PATH))
    def test_addEdge(self, mockHash):
        ''' Check if _addEdge appends the vertex in the other vertex's adjacency list '''
        mockHash.side_effect = lambda x: x
        graphState = defaultdict(list)
        g = LWWElementGraph()
        self.assertDictEqual(g._addEdge(graphState, 1, 2), {1: [2], 2: [1]})
         
    @mock.patch('{}.LWWElementGraph.hashObj'.format(SRC_PATH))
    def test_removeEdge(self, mockHash):
        ''' Remove edge by deleting the vertice in the other's adjacency list '''
        mockHash.side_effect = lambda x: x
        graphState = {1: [2], 2: [1]}
        g = LWWElementGraph()
        self.assertDictEqual(g._removeEdge(graphState, 1, 2), {1: list(), 2: list()})

    @mock.patch('{}.LWWElementGraph.hashObj'.format(SRC_PATH))
    def test_computeGraph(self, mockHash):
        ''' Check new computed graphState using vertices and edges
            Initialize the vertices first, and then for each edge, add the vertices to 
            each other's adjacency list in graphState '''
        mockHash.side_effect = lambda x: x
        vertices = [1, 2, 3, 4, 5]
        edges = [{1,2}, {1, 4}, {2,3}, {2,4}]
        expectedGraphState = {
            1: [2, 4], 
            2: [1, 3, 4],
            3: [2],
            4: [1, 2],
            5: list()
        }
        g = LWWElementGraph()
        l = g._computeGraph(vertices, edges)
        self.assertDictEqual(l, expectedGraphState)

class LWWElementGraphTestsComplexObject(TestCase):

    def test_removeVertexComplexObject(self):
        ''' Check if _removeVertex updates the graphState by removing the vertex and 
            its edges with other vertices for a graph with Complex data type (other than int, str) '''
        a = createComplexObj()
        b = createComplexObj()
        c = createComplexObj()
        d = createComplexObj()
        graphState = {
            hashObj(a): [b, d], 
            hashObj(b): [a, c],
            hashObj(c): [b],
            hashObj(d): [a],
        }
        g = LWWElementGraph()
        self.assertDictEqual(g._removeVertex(graphState, b), {hashObj(a): [d], hashObj(c): list(), hashObj(d): [a]})
    
    def test_removeEdgeComplexObject(self):
        ''' Remove edge by deleting the vertice in the other's adjacency list  
            for a graph with Complex data type (other than int, str)'''
        a, b = createComplexObj(), createComplexObj()
        graphState = {hashObj(a): [b], hashObj(b): [a]}
        g = LWWElementGraph()
        self.assertDictEqual(g._removeEdge(graphState, a, b), {hashObj(a): list(), hashObj(b): list()})

    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    @mock.patch('{}.LWWElementGraph.LWWElementGraph.getNeighborsOf'.format(SRC_PATH))
    def testFindPathComplexObject(self, mockGetNeighborsOf, mockIsMember):
        ''' Check if BFS runs correctly for a graph with Complex data type (other than int, str) '''
        a = createComplexObj()
        b = createComplexObj()
        c = createComplexObj()
        d = createComplexObj()
        e = createComplexObj()
        f = createComplexObj()
        h = createComplexObj()

        graph = {
            hashObj(a): [b], 
            hashObj(b): [a, c, d],
            hashObj(c): [b, e],
            hashObj(d): [b, e],
            hashObj(e): [c, d, f, h],
            hashObj(f): [e, h],
            hashObj(h): [e, f],
        }
        mockGetNeighborsOf.side_effect = lambda x: graph[hashObj(x)]
        mockIsMember.return_value = True
        g = LWWElementGraph()
        self.assertListEqual(g.findPath(a, h), [a, b, c, e, h])
