from collections import defaultdict
from LWWElementSet import LWWElementSet, hashObj

class LWWElementGraph(object):
    
    # TODO: Insert vertices and edge set in constructor, for testing and mergeGraphs
    # TODO: type checking
    def __init__(self):
        ''' '''
        self.vertices = LWWElementSet()
        self.edges = LWWElementSet()
        # to optimize getNeighborsOf and findPath, maintaining a live updating internal state
        self.graph = defaultdict(set) 

    def addVertex(self, vertex):
        ''' '''
        self.vertices.addElement(vertex)
        self.graph[hashObj(vertex)]

    def removeVertex(self, vertex):
        ''' '''
        if not self.vertices.isMember(vertex):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex))
        self.vertices.removeElement(vertex)
        for edgeSet in self.edges.getMembers():
            self.edges.removeElement(edgeSet) if vertex in edgeSet else None
        self.graph = self._removeVertex(self.graph, vertex)
        
    def addEdge(self, vertex1, vertex2):
        ''' '''
        if not self.vertices.isMember(vertex1):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex1))
        elif not self.vertices.isMember(vertex2):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex2))
        self.edges.addElement(set([vertex1, vertex2]))
        self.graph = self._addEdge(self.graph, vertex1, vertex2)

    def removeEdge(self, vertex1, vertex2):
        ''' '''
        edgeSet = set([vertex1, vertex2])
        if not self.edges.isMember(edgeSet):
            raise KeyError("Edge {}-{} not in LWWElementGraph".format(vertex1, vertex2))
        self.edges.removeElement(edgeSet)
        self.graph = self._removeEdge(self.graph, vertex1, vertex2)

    def isMember(self, vertex):
        ''' '''
        return hashObj(vertex) in self.graph

    def getNeighborsOf(self, vertex):
        ''' '''
        if not self.isMember(vertex):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex))
        return self.graph[hashObj(vertex)]

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
        self.graph = self._computeGraph(self.vertices.getMembers(), self.edges.getMembers())

    def _removeVertex(self, vertex, graph):
        ''' '''
        del graph[hashObj(vertex)]
        for k in graph.keys(): graph[k].discard(vertex)
        return graph

    def _addEdge(self, graph, vertex1, vertex2):
        ''' '''
        graph[hashObj(vertex1)].add(vertex2)
        graph[hashObj(vertex2)].add(vertex1)
        return graph

    def _removeEdge(self, graph, vertex1, vertex2):
        ''' '''
        graph[hashObj(vertex1)].remove(vertex2)
        graph[hashObj(vertex2)].remove(vertex1)
        return graph

    def _computeGraph(self, vertices, edges):
        ''' '''
        graph = defaultdict(set)
        for v in vertices: graph[v]
        for a,b in edges: graph[hashObj(a)].add(b); graph[hashObj(b)].add(a)
        return graph