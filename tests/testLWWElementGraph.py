from unittest import TestCase, mock
from datetime import datetime
from collections import defaultdict
from random import random
from context import LWWElementGraph, LWWElementSet, hashObj

def createComplexObj():
    return [{
            'timestamp' : [ random() * 10**4],
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
        
    @mock.patch('LWWElementSet.LWWElementSet.addElement')
    def testAddVertex(self, mockSetAddElement):
        ''' Check if vertices.addElement is called '''
        g = LWWElementGraph()
        g.graphState = mock.MagicMock()
        g.addVertex('a')
        mockSetAddElement.assert_called_once_with('a')
        g.graphState.__getitem__.assert_called_with(hashObj('a'))

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveFails(self, mockIsMember):
        ''' Cannot remove before adding vertex '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.removeVertex('a')
            
    @mock.patch('LWWElementGraph.LWWElementGraph._removeVertex')
    @mock.patch('LWWElementSet.LWWElementSet.removeElement')
    @mock.patch('LWWElementSet.LWWElementSet.getMembers')
    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveVertex(self, mockIsMember, mockGetMembers, mockSetRemoveElement, _mockGraphRemoveVertex):
        ''' Check remove vertex and all its edges. Also check if _removeVertex is called '''
        mockIsMember.return_value = True
        mockGetMembers.return_value = [{'a', 'b'}, {'b', 'c'}, {'c', 'a'}]
        g = LWWElementGraph()
        g.removeVertex('a')
        calls = [mock.call('a'), mock.call({'a', 'b'}), mock.call({'c', 'a'})]
        mockSetRemoveElement.assert_has_calls(calls)
        self.assertTrue(_mockGraphRemoveVertex.called)

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testAddEdgeFails(self, mockIsMember):
        ''' Cannot add edge if vertex not present '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.addEdge('a', 'b')

    @mock.patch('LWWElementGraph.LWWElementGraph._addEdge')
    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    @mock.patch('LWWElementSet.LWWElementSet.addElement')
    def testAddEdge(self, mockSetAddElement, mockIsMember, _mockGraphAddEdge):
        ''' Check if addElement to edge LWWSet. Also check if _addEdge is called '''
        mockIsMember.return_value = True
        g = LWWElementGraph()
        g.addEdge('a', 'b')
        mockSetAddElement.assert_called_once_with({'a','b'})
        self.assertTrue(_mockGraphAddEdge.called)

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveEdgeFails(self, mockIsMember):
        ''' Cannot remove edge if it doesnt exist '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.removeEdge('a', 'b')

    @mock.patch('LWWElementGraph.LWWElementGraph._removeEdge')
    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    @mock.patch('LWWElementSet.LWWElementSet.removeElement')
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

    @mock.patch('LWWElementGraph.LWWElementGraph.isMember')
    def testGetNeighborsOfFails(self, mockGraphIsMember):
        ''' Cannot getNeighboursOf if vertex not present '''
        mockGraphIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.getNeighborsOf('a')

    @mock.patch('LWWElementGraph.LWWElementGraph.isMember')
    def testGetNeighbors(self, mockGraphIsMember):
        ''' Check if getNeighboursOf accesses graphState '''
        mockGraphIsMember.return_value = True
        g = LWWElementGraph()
        g.graphState = {hashObj(1): [2, 3, 4], hashObj(2): [1]}
        self.assertListEqual(g.getNeighborsOf(1), [2,3,4])
        self.assertListEqual(g.getNeighborsOf(2), [1])

    @mock.patch('LWWElementGraph.LWWElementGraph.getNeighborsOf')
    def testFindPath(self, mockGetNeighborsOf):
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
        g = LWWElementGraph()
        self.assertListEqual(g.findPath(1, 7), [1, 2, 3, 5, 7])
    
    @mock.patch('LWWElementGraph.LWWElementGraph._computeGraph')
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
    
    @mock.patch('LWWElementGraph.hashObj')
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

    @mock.patch('LWWElementGraph.hashObj')
    def test_addEdge(self, mockHash):
        ''' Check if _addEdge appends the vertex in the other vertex's neighbor list '''
        mockHash.side_effect = lambda x: x
        graphState = defaultdict(list)
        g = LWWElementGraph()
        self.assertDictEqual(g._addEdge(graphState, 1, 2), {1: [2], 2: [1]})
         
    @mock.patch('LWWElementGraph.hashObj')
    def test_removeEdge(self, mockHash):
        ''' Remove edge by deleting the vertice in the other's neighbor list '''
        mockHash.side_effect = lambda x: x
        graphState = {1: [2], 2: [1]}
        g = LWWElementGraph()
        self.assertDictEqual(g._removeEdge(graphState, 1, 2), {1: list(), 2: list()})

    @mock.patch('LWWElementGraph.hashObj')
    def test_computeGraph(self, mockHash):
        mockHash.side_effect = lambda x: x
        vertices = [1, 2, 3, 4, 5]
        edges = [{1,2}, {1, 4}, {2,3}, {2,4}]
        expectedGraphState = {
            1: {2, 4}, 
            2: {1, 3, 4},
            3: {2},
            4: {1, 2},
            5: set()
        }
        g = LWWElementGraph()
        l = g._computeGraph(vertices, edges)
        self.assertDictEqual(l, expectedGraphState)

class LWWElementGraphTestsComplexObject(TestCase):   
    @mock.patch('LWWElementGraph.LWWElementGraph.getNeighborsOf')
    def testFindPathComplexObject(self, mockGetNeighborsOf):
        ''' '''
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
        g = LWWElementGraph()
        self.assertListEqual(g.findPath(a, h), [a, b, c, e, h])

    # TODO: add test case for complex objects

