# Welcome to LWWElementGraph’s documentation!

## LWWElementGraph

Module for a lightweight LWWElementGraph, which uses LWWElementSet.
Handles merges in a Last Write Wins Manner.

## LWWElementSet

Module for a lightweight LWWElementSet in Python.
Handles merges in a Last Write Wins Manner.

## Install

To install packages, perform:
`pip install -r requirements.txt`

## Tests
- /tests/testLWWElementSet.py
- /tests/testLWWElementGraph.py
- /tests/testIntegration.py


# Contents:

* [LWWElementGraph package](#lwwelementgraph-package)

    * [Module contents](#module-contents)

        * [LWWElementGraph.LWWElementGraph module](#class-lwwelementgraphlwwelementgraph)

    * [Submodules](#submodules)

        * [LWWElementGraph.LWWElementSet module](#lwwelementgraphlwwelementset-module)


# LWWElementGraph package

## Module contents

### _class_ LWWElementGraph.LWWElementGraph()
Bases: `object`


#### \__init__()
Initializing Vertices and Edges as LWWElementSet. Maintaining live updating
graphState to optimize reads (getNeighborsOf, findPath)


#### addEdge(vertex1, vertex2)
If vertex1, vertex2 present, add edge to edges.addSet. Maintain graphState 
Runs in O(1)


#### addVertex(vertex)
Adds the Vertex to vertices LWWSet. Also maintains graphState for read optimization
Runs in O(1)


#### findPath(vertex1, vertex2)
Perform BFS for shortest path. Uses graphState which was optimized for read
to get all the neighbours of a vertex in O(1).
Runs in O(V + E)


#### getNeighborsOf(vertex)
O(1) query for all the vertices connected to the query vertex. Uses graphState 
which was optimized for read


#### isMember(vertex)
Check if vertex is valid, runs in O(1)


#### mergeGraphs(otherGraph)
Merging Graphs by merging their Vertice and Edge LLWSet. Remove Edge if Vertex not present
anymore after merge. Recompute the internal graphState as well. Runs in O(V + E)


#### removeEdge(vertex1, vertex2)
If edge present, add it to edges.removeSet. Maintain graphState.
Runs in O(E) because of _removeEdge


#### removeVertex(vertex)
If vertex is present, then add it to vertices.removeSet. Add each of its edge to 
edges.removeSet. Also maintains graphState for read optimization.
Runs in O(E) because of _removeVertex

## Submodules


## LWWElementGraph.LWWElementSet module


### _class_ LWWElementGraph.LWWElementSet.LWWElementSet()
Bases: `object`


#### \__init__()
Initialize addSet and removeSet to empty dictionary. iData and iTimestamp 
are the index of the data and timestamp respectively


#### addElement(element)
Adds in the addSet. If element already in addSet, replace timestamp with now()


#### getMembers()
Returns all the valid members. Go through addSet, check if it is a member


#### isMember(element)
Element is a member if it is in addSet, and either not removeSet, 
or in removeSet but with an earlier timestamp than it’s timestamp in addSet


#### mergeSet(selfSet, otherSet)
Prioritize Last Write. Since elements are in the form (data, datetime), reverse them to
compare by datetime and take max. Then, reverse back the max and store in merged


#### mergeWith(otherLWWElementSet)
Merge self with otherLWWElementSet in LWW manner


#### removeElement(element)
Adds in the removeSet. Cannot remove if not already in addSet

---
### Made by [krohak](https://github.com/krohak/)
