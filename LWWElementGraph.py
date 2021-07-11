from collections import defaultdict
from LWWElementSet import LWWElementSet, hashObj

class LWWElementGraph(object):
    
    # TODO: type checking
    def __init__(self):
        # TODO: DOCUMENTATION ''' '''
        self.vertices = LWWElementSet()
        self.edges = LWWElementSet()
        # to optimize getNeighborsOf and findPath, 
        # maintaining a live updating internal state
        self.graphState = defaultdict(set)

    def __repr__(self):
        return "Graph: \n{} \nHistory: \nVertices: \n{}\n Edges: \n{}".format(self.graphState, self.vertices, self.edges) 

    def addVertex(self, vertex):
        ''' '''
        self.vertices.addElement(vertex)
        self.graphState[hashObj(vertex)]

    def removeVertex(self, vertex):
        ''' '''
        if not self.vertices.isMember(vertex):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex))
        self.vertices.removeElement(vertex)
        for edgeSet in self.edges.getMembers():
            self.edges.removeElement(edgeSet) if vertex in edgeSet else None
        self.graphState = self._removeVertex(self.graphState, vertex)
        
    def addEdge(self, vertex1, vertex2):
        ''' '''
        if not self.vertices.isMember(vertex1):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex1))
        elif not self.vertices.isMember(vertex2):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex2))
        self.edges.addElement({vertex1, vertex2})
        self.graphState = self._addEdge(self.graphState, vertex1, vertex2)

    def removeEdge(self, vertex1, vertex2):
        ''' '''
        edgeSet = {vertex1, vertex2}
        if not self.edges.isMember(edgeSet):
            raise KeyError("Edge {}-{} not in LWWElementGraph".format(vertex1, vertex2))
        self.edges.removeElement(edgeSet)
        self.graphState = self._removeEdge(self.graphState, vertex1, vertex2)

    def isMember(self, vertex):
        ''' '''
        return hashObj(vertex) in self.graphState

    def getNeighborsOf(self, vertex):
        ''' '''
        if not self.isMember(vertex):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex))
        return self.graphState[hashObj(vertex)]

    def findPath(self, vertex1, vertex2):
        ''' Perform BFS '''
        frontier = [vertex1]
        explored = set()
        ancestory = {}
        while frontier:
            node = frontier.pop(0)
            explored.add(node)
            if node == vertex2:
                path = [node]
                while hashObj(node) in ancestory:                     
                    node=ancestory.get(hashObj(node), None)
                    path.append(node) 
                return path[::-1]
            for ngbr in self.getNeighborsOf(node):
                if ngbr not in frontier and ngbr not in explored:
                    frontier.append(ngbr)
                    ancestory[hashObj(ngbr)] = node
        return []

    def mergeGraphs(self, otherGraph):
        ''' '''
        self.vertices.mergeWith(otherGraph.vertices)
        self.edges.mergeWith(otherGraph.edges)
        # go through all edges.members, remove edge if vertex not present anymore
        for v1, v2 in self.edges.getMembers():
            if not self.vertices.isMember(v1) or not self.vertices.isMember(v2):
                self.edges.removeElement({v1, v2})
        self.graphState = self._computeGraph(self.vertices.getMembers(), self.edges.getMembers())

    def _removeVertex(self, graphState, vertex):
        ''' '''
        del graphState[hashObj(vertex)]
        for k in graphState.keys(): graphState[k].discard(vertex)
        return graphState

    def _addEdge(self, graphState, vertex1, vertex2):
        ''' '''
        graphState[hashObj(vertex1)].add(vertex2)
        graphState[hashObj(vertex2)].add(vertex1)
        return graphState

    def _removeEdge(self, graphState, vertex1, vertex2):
        ''' '''
        graphState[hashObj(vertex1)].remove(vertex2)
        graphState[hashObj(vertex2)].remove(vertex1)
        return graphState

    def _computeGraph(self, vertices, edges):
        ''' '''
        graphState = defaultdict(set)
        for v in vertices: graphState[hashObj(v)] # initialize the vertices first, since there can some with no edges
        for a,b in edges: graphState[hashObj(a)].add(b); graphState[hashObj(b)].add(a)
        return graphState