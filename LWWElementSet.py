from datetime import datetime
from hashlib import sha1

def hashObj(data):
    return sha1(repr(data).encode('utf-8')).hexdigest()

class LWWElementSet(object):

    def __init__(self):
        ''' Initialize addSet and removeSet to empty dictionary. iData and iTimestamp 
            are the index of the data and timestamp respectively'''
        self.addSet = {}
        self.removeSet = {}
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
        ''' Returns all the valid members. Go through addSet, check if it is a member '''
        return [ data for data, _ in self.addSet.values() if self.isMember(data)]
        
    def mergeSet(self, selfSet, otherSet):
        ''' Prioritize Last Write. Since elements are in the form (data, datetime), reverse them to
            compare by datetime and take max. Then, reverse back the max and store in merged '''
        merged = {}
        for hashElement in set(selfSet.keys()).union(set(otherSet.keys())):
            minElement = (None, datetime.min)
            element1, element2 = selfSet.get(hashElement, minElement), otherSet.get(hashElement, minElement)
            merged[hashElement] = max(element1[::-1], element2[::-1])[::-1]
        return merged
                
    def mergeWith(self, otherLWWElementSet):
        ''' Merge self with otherLWWElementSet in LWW manner '''
        self.addSet = self.mergeSet(self.addSet, otherLWWElementSet.addSet)
        self.removeSet = self.mergeSet(self.removeSet, otherLWWElementSet.removeSet)
        