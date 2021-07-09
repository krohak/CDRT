from collections import defaultdict
from LWWElementSet import LWWElementSet

class LWWElementGraph(object):
    def __init__(self):
        self.vertices = LWWElementSet()
        self.edges = LWWElementSet()

    def addVertex(self, vertex):
        self.vertices.addElement(vertex)

    def removeVertex(self, vertex):
        if not self.vertices.isMember(vertex):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex))
        for edgeSet in self.edges.getMembers():
            self.edges.removeElement(edgeSet) if vertex in edgeSet else None
        self.vertices.removeElement(vertex)

    def addEdge(self, vertex1, vertex2):
        self.edges.addElement(set([vertex1, vertex2]))

    def removeEdge(self, vertex1, vertex2):
        edgeSet = set([vertex1, vertex2])
        if not self.edges.isMember(edgeSet):
            raise KeyError("Edge {}-{} not in LWWElementGraph".format(vertex1, vertex2))
        self.edges.removeElement(edgeSet)

    def isMember(self, vertex):
        return self.vertices.isMember(vertex)

    def getNeighborsOf(self, vertex):
        if not self.isMember(vertex):
            raise KeyError("Vertex {} not in LWWElementGraph".format(vertex))
        return set.union(*[ edgeSet for edgeSet in self.edges.getMembers() if vertex in edgeSet ]).remove(vertex)            

    def findPath(self, vertex1, vertex2):
        ''' Perform BFS here '''
        pass

    def mergeGraphs(self, otherGraph):
        pass
