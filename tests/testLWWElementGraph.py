from unittest import TestCase, mock
from datetime import datetime
from collections import defaultdict
from context import LWWElementGraph, LWWElementSet, hashObj

class LWWElementSetTests(TestCase):

    def testInit(self):
        ''' '''
        g = LWWElementGraph()
        self.assertTrue(isinstance(g.vertices, LWWElementSet))
        self.assertTrue(isinstance(g.edges, LWWElementSet))
        
    @mock.patch('LWWElementSet.LWWElementSet.addElement')
    def testAddVertex(self, mockSetAddElement):
        ''' '''
        g = LWWElementGraph()
        g.graph = mock.MagicMock()
        g.addVertex('a')
        mockSetAddElement.assert_called_once_with('a')
        g.graph.__getitem__.assert_called_with(hashObj('a'))

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveFails(self, mockIsMember):
        ''' '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.removeVertex('a')
            
    @mock.patch('LWWElementGraph.LWWElementGraph._removeVertex')
    @mock.patch('LWWElementSet.LWWElementSet.removeElement')
    @mock.patch('LWWElementSet.LWWElementSet.getMembers')
    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveVertex(self, mockIsMember, mockGetMembers, mockSetRemoveElement, _mockGraphRemoveVertex):
        ''' '''
        mockIsMember.return_value = True
        mockGetMembers.return_value = [{'a', 'b'}, {'b', 'c'}, {'c', 'a'}]
        g = LWWElementGraph()
        g.removeVertex('a')
        calls = [mock.call('a'), mock.call({'a', 'b'}), mock.call({'c', 'a'})]
        mockSetRemoveElement.assert_has_calls(calls)
        self.assertTrue(_mockGraphRemoveVertex.called)

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testAddEdgeFails(self, mockIsMember):
        ''' '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.addEdge('a', 'b')

    @mock.patch('LWWElementGraph.LWWElementGraph._addEdge')
    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    @mock.patch('LWWElementSet.LWWElementSet.addElement')
    def testAddEdge(self, mockSetAddElement, mockIsMember, _mockGraphAddEdge):
        ''' '''
        mockIsMember.return_value = True
        g = LWWElementGraph()
        g.addEdge('a', 'b')
        mockSetAddElement.assert_called_once_with({'a','b'})
        self.assertTrue(_mockGraphAddEdge.called)

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveEdgeFails(self, mockIsMember):
        ''' '''
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.removeEdge('a', 'b')

    @mock.patch('LWWElementGraph.LWWElementGraph._removeEdge')
    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    @mock.patch('LWWElementSet.LWWElementSet.removeElement')
    def testRemoveEdge(self, mockSetRemoveElement, mockIsMember, _mockGraphRemoveEdge):
        ''' '''
        mockIsMember.return_value = True
        LWWElementGraph().removeEdge('a', 'b')
        mockSetRemoveElement.assert_called_once_with({'a','b'})
        self.assertTrue(_mockGraphRemoveEdge.called)
    
    def testIsMember(self):
        ''' '''
        g = LWWElementGraph()
        g.graph = {hashObj('a'): set()}
        self.assertTrue(g.isMember('a'))
        self.assertFalse(g.isMember('b'))

    @mock.patch('LWWElementGraph.LWWElementGraph.isMember')
    def testGetNeighborsOfFails(self, mockGraphIsMember):
        ''' '''
        mockGraphIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.getNeighborsOf('a')

    @mock.patch('LWWElementGraph.LWWElementGraph.isMember')
    def testGetNeighbors(self, mockGraphIsMember):
        ''' '''
        mockGraphIsMember.return_value = True
        g = LWWElementGraph()
        g.graph = {hashObj(1): {2, 3, 4}, hashObj(2): {1}}
        self.assertSetEqual(g.getNeighborsOf(1), {2,3,4})
        self.assertSetEqual(g.getNeighborsOf(2), {1})

    @mock.patch('LWWElementGraph.LWWElementGraph.getNeighborsOf')
    def testFindPath(self, mockGetNeighborsOf):
        ''' '''
        graph = {
            1: {2}, 
            2: {1, 3, 4},
            3: {2, 5},
            4: {2, 5},
            5: {3, 4, 6, 7},
            6: {5, 7},
            7: {5, 6},
        }
        mockGetNeighborsOf.side_effect = lambda x: graph[x]
        g = LWWElementGraph()
        self.assertListEqual(g.findPath(1, 7), [1, 2, 3, 5, 7])
    
    @mock.patch('LWWElementGraph.LWWElementGraph.getNeighborsOf')
    def testFindPathComplexObject(self, mockGetNeighborsOf):
        ''' '''
        class ComplexObject(object):
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def foo(self):
                pass

        a = ComplexObject(1,2)
        b = ComplexObject(1,3)
        c = ComplexObject(4,6)
        d = ComplexObject(5,7)
        e = ComplexObject(3,9)
        f = ComplexObject(8,3)
        h = ComplexObject(5,21)

        graph = {
            hashObj(a): {b}, 
            hashObj(b): {a, c, d},
            hashObj(c): {b, e},
            hashObj(d): {b, e},
            hashObj(e): {c, d, f, h},
            hashObj(f): {e, h},
            hashObj(h): {e, f},
        }
        mockGetNeighborsOf.side_effect = lambda x: graph[hashObj(x)]
        g = LWWElementGraph()
        self.assertListEqual(g.findPath(a, h), [a, b, d, e, h])

    # TODO: add test case in BFS for complex objects

    @mock.patch('LWWElementGraph.LWWElementGraph._computeGraph')
    @mock.patch('LWWElementSet.LWWElementSet.mergeWith')
    def testMergeGraphs(self, mockSetMergeWith, _mockComputeGraph):
        ''' '''
        pass
    