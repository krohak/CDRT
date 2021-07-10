from unittest import TestCase, mock
from datetime import datetime
from collections import defaultdict
from context import LWWElementGraph, LWWElementSet

class LWWElementSetTests(TestCase):

    # TODO: beforeeach, aftereach

    def testInit(self):
        g = LWWElementGraph()
        self.assertTrue(isinstance(g.vertices, LWWElementSet))
        self.assertTrue(isinstance(g.edges, LWWElementSet))
        
    @mock.patch('LWWElementSet.LWWElementSet.addElement')
    def testAddVertex(self, mockSetAddElement):
        LWWElementGraph().addVertex('a')
        mockSetAddElement.assert_called_once_with('a')

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveFails(self, mockIsMember):
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.removeVertex('a')
            
    @mock.patch('LWWElementSet.LWWElementSet.removeElement')
    @mock.patch('LWWElementSet.LWWElementSet.getMembers')
    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveVertex(self, mockIsMember, mockGetMembers, mockSetRemoveElement):
        mockIsMember.return_value = True
        mockGetMembers.return_value = [{'a', 'b'}, {'b', 'c'}, {'c', 'a'}]
        LWWElementGraph().removeVertex('a')
        calls = [mock.call('a'), mock.call({'a', 'b'}), mock.call({'c', 'a'})]
        mockSetRemoveElement.assert_has_calls(calls)

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testAddEdgeFails(self, mockIsMember):
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.addEdge('a', 'b')

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    @mock.patch('LWWElementSet.LWWElementSet.addElement')
    def testAddEdge(self, mockSetAddElement, mockIsMember):
        mockIsMember.return_value = True
        LWWElementGraph().addEdge('a', 'b')
        mockSetAddElement.assert_called_once_with({'a','b'})

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testRemoveEdgeFails(self, mockIsMember):
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.removeEdge('a', 'b')

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    @mock.patch('LWWElementSet.LWWElementSet.removeElement')
    def testRemoveEdge(self, mockSetRemoveElement, mockIsMember):
        mockIsMember.return_value = True
        LWWElementGraph().removeEdge('a', 'b')
        mockSetRemoveElement.assert_called_once_with({'a','b'})
    
    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    def testIsMember(self, mockIsMember):
        LWWElementGraph().isMember('a')
        mockIsMember.assert_called_once_with('a')

    @mock.patch('LWWElementGraph.LWWElementGraph.isMember')
    def testGetNeighborsOfFails(self, mockIsMember):
        mockIsMember.return_value = False
        g = LWWElementGraph()
        with self.assertRaises(KeyError):
            g.getNeighborsOf('a')

    @mock.patch('LWWElementSet.LWWElementSet.isMember')
    @mock.patch('LWWElementSet.LWWElementSet.getMembers')
    def testGetNeighbors(self, mockGetMembers, mockIsMember):
        mockIsMember.return_value = True
        mockGetMembers.return_value = [{1, 2}, {1, 3}, {1, 4}]
        neighbors = LWWElementGraph().getNeighborsOf(1)
        self.assertSetEqual(neighbors, {2,3,4})

    ## TODO: add test case in BFS for complex objects
    # should we use hash?