from datetime import datetime
from hashlib import sha1

def hashObj(data):
    return sha1(repr(data).encode('utf-8')).hexdigest()

class LWWElementSet(object):
    def __init__(self, addSet=None, removeSet=None):
        self.addSet = addSet if addSet else {}
        self.removeSet = removeSet if removeSet else {}
        self.iData = 0
        self.iTimestamp = 1
    
    def __repr__(self):
        return "addSet: {} \nremoveSet: {}".format(self.addSet, self.removeSet)
    
    def addElement(self, element):
        ''' Adds in the addSet. If element already in addSet, replace timestamp with now() '''
        self.addSet[hashObj(element)] = (element, datetime.now())

    def removeElement(self, element):
        ''' Adds in the removeSet. Cannot remove if not already in addSet '''
        if hashObj(element) not in self.addSet:
            raise KeyError("{} not in LWWElementSet".format(element))
        self.removeSet[hashObj(element)] = (element, datetime.now())

    def isMember(self, element):
        ''' Element is a member if it is in addSet, and either not removeSet, 
        or in removeSet but with an earlier timestamp than it's timestamp in addSet '''
        hashElement = hashObj(element)
        isRemoveSetValid = hashElement not in self.removeSet or self.removeSet[hashElement][self.iTimestamp] < self.addSet[hashElement][self.iTimestamp]
        return hashElement in self.addSet and isRemoveSetValid
    
    def getMembers(self):
        return [ data for data, _ in self.addSet.values() if self.isMember(data)]
        
    def mergeSet(self, set1, set2):
        ''' Prioritize Last Write '''
        merged = {}
        for hashElement in set(set1.keys()).union(set(set2.keys())):
            if hashElement in set1 and hashElement in set2:
                element1, element2 = set1[hashElement], set2[hashElement]
                # reverse, take max by timestamp, then reverse back.
                merged[hashElement] = max(element1[::-1], element2[::-1])[::-1] 
            elif hashElement in set1:
                merged[hashElement] = set1[hashElement]
            else:
                merged[hashElement] = set2[hashElement]
        return merged
                
    def mergeWith(self, otherLWWElementSet):
        ''' merge self with otherLWWElementSet in LWW manner '''
        self.addSet = self.mergeSet(self.addSet, otherLWWElementSet.addSet)
        self.removeSet = self.mergeSet(self.removeSet, otherLWWElementSet.removeSet)
        