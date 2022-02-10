from collections import defaultdict
from .LWWElementSet import LWWElementSet, hashObj

class LWWElementGraph(object):
    
    def __init__(self):
        ''' Initializing Vertices and Edges as LWWElementSet. Maintaining live updating
            graphState to optimize reads (getNeighborsOf, findPath) ''' 
        self.vertices = LWWElementSet()
        self.edges = LWWElementSet()
        self.graphState = defaultdict(list)

    def __repr__(self):
        return "Graph: \n{} \nHistory: \nVertices: \n{}\n Edges: \n{}".format(self.graphState, self.vertices, self.edges) 

    def addVertex(self, vertex):
        ''' Adds the Vertex to vertices LWWSet. Also maintains graphState for read optimization
            Runs in O(1)'''
        self.vertices.addElement(vertex)
        self.graphState[hashObj(vertex)]

    def removeVertex(self, vertex):
        ''' If vertex is present, then add it to vertices.removeSet. Add each of its edge to 
            edges.removeSet. Also maintains graphState for read optimization.
            Runs in O(E) because of _removeVertex '''
        if not self.vertices.isMember(vertex):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex))
        self.vertices.removeElement(vertex)
        for edgeSet in self.edges.getMembers():
            self.edges.removeElement(edgeSet) if vertex in edgeSet else None
        self.graphState = self._removeVertex(self.graphState, vertex)
        
    def addEdge(self, vertex1, vertex2):
        ''' If vertex1, vertex2 present, add edge to edges.addSet. Maintain graphState 
            Runs in O(1) '''
        if not self.vertices.isMember(vertex1):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex1))
        elif not self.vertices.isMember(vertex2):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex2))
        self.edges.addElement({vertex1, vertex2})
        self.graphState = self._addEdge(self.graphState, vertex1, vertex2)

    def removeEdge(self, vertex1, vertex2):
        ''' If edge present, add it to edges.removeSet. Maintain graphState.
            Runs in O(E) because of _removeEdge'''
        edgeSet = {vertex1, vertex2}
        if not self.edges.isMember(edgeSet):
            raise KeyError("Edge {}-{} not in LWWElementGraph".format(vertex1, vertex2))
        self.edges.removeElement(edgeSet)
        self.graphState = self._removeEdge(self.graphState, vertex1, vertex2)

    def isMember(self, vertex):
        ''' Check if vertex is valid, runs in O(1) '''
        return hashObj(vertex) in self.graphState

    def getNeighborsOf(self, vertex):
        ''' O(1) query for all the vertices connected to the query vertex. Uses graphState 
            which was optimized for read '''
        if not self.isMember(vertex):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex))
        return self.graphState[hashObj(vertex)]

    def findPath(self, vertex1, vertex2):
        ''' Perform BFS for shortest path. Uses graphState which was optimized for read
            to get all the neighbours of a vertex in O(1).
            Runs in O(V + E) '''
        if not self.vertices.isMember(vertex1):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex1))
        elif not self.vertices.isMember(vertex2):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex2))
        frontier, explored, ancestory = [vertex1], set(), {}
        while frontier:
            node = frontier.pop(0)
            explored.add(hashObj(node))
            if node == vertex2:
                path = [node]
                while hashObj(node) in ancestory:                     
                    node=ancestory.get(hashObj(node), None)
                    path.append(node) 
                return path[::-1]
            for ngbr in self.getNeighborsOf(node):
                if ngbr not in frontier and hashObj(ngbr) not in explored:
                    frontier.append(ngbr)
                    ancestory[hashObj(ngbr)] = node
        return []

    def mergeGraphs(self, otherGraph):
        ''' Merging Graphs by merging their Vertice and Edge LLWSet. Remove Edge if Vertex not present
            anymore after merge. Recompute the internal graphState as well. Runs in O(V + E)'''
        self.vertices.mergeWith(otherGraph.vertices)
        self.edges.mergeWith(otherGraph.edges)
        for v1, v2 in self.edges.getMembers():
            if not self.vertices.isMember(v1) or not self.vertices.isMember(v2):
                self.edges.removeElement({v1, v2})
        self.graphState = self._computeGraph(self.vertices.getMembers(), self.edges.getMembers())

    def _removeVertex(self, graphState, vertex):
        ''' Runs in O(E) '''
        del graphState[hashObj(vertex)]
        for k in graphState.keys(): graphState[k].remove(vertex) if vertex in graphState[k] else None
        return graphState

    def _addEdge(self, graphState, vertex1, vertex2):
        '''  Runs in O(1) '''
        graphState[hashObj(vertex1)].append(vertex2)
        graphState[hashObj(vertex2)].append(vertex1)
        return graphState

    def _removeEdge(self, graphState, vertex1, vertex2):
        '''  Runs in O(E) '''
        graphState[hashObj(vertex1)].remove(vertex2)
        graphState[hashObj(vertex2)].remove(vertex1)
        return graphState

    def _computeGraph(self, vertices, edges):
        ''' Calculate the graphState using latest vertices and edges. Initialize the Vertices first, 
            since there be some vertices with no edges. Runs in O(V + E)'''
        graphState = defaultdict(list)
        for v in vertices: graphState[hashObj(v)]
        for a,b in edges: graphState[hashObj(a)].append(b); graphState[hashObj(b)].append(a)
        return graphState