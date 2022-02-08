from unittest import TestCase, mock
from datetime import datetime
from random import random
from context import LWWElementSet, hashObj, SRC_PATH


def createComplexObj():
    ''' Outputs a complex Python dictionary obj with embedded dict, list, string and float '''
    return [{
            'timestamp' : [ random() * 10**4],
            'event': {
                    'ABS_MT_POSITION_X': '{}'.format(int(random() * 10**8)),
                    'ABS_MT_POSITION_Y': '{}'.format(int(random() * 10**8)),
                    'ABS_MT_PRESSURE': '{}'.format(int(random() * 10**8)),
                }
    }]

class LWWElementSetTests(TestCase):

    def testInit(self):
        ''' Testing if addSet and removeSet are initialized correctly to an empty dict'''
        l = LWWElementSet()
        self.assertDictEqual(l.addSet, {})
        self.assertDictEqual(l.removeSet, {})

    @mock.patch('{}.LWWElementSet.hashObj'.format(SRC_PATH))
    def testAddElement(self, mockHash):
        ''' Adding element adds to addSet with value as (data, datetime). '''
        mockHash.side_effect = lambda x: x
        l = LWWElementSet()
        l.addElement(4)
        self.assertTrue(4 in l.addSet)
        self.assertEqual(l.addSet[4][l.iData], 4)
        self.assertTrue(isinstance(l.addSet[4][l.iTimestamp], datetime))
    
    def testRemoveBeforeAdd(self):
        ''' Removing element if not present, should throw KeyError Exception '''
        l = LWWElementSet()
        with self.assertRaises(KeyError):
            l.removeElement(4)

    @mock.patch('{}.LWWElementSet.hashObj'.format(SRC_PATH))
    def testRemoveElement(self, mockHash):
        ''' Removing element adds it in the removeSet with value as (data, datetime) '''
        mockHash.side_effect = lambda x: x
        l = LWWElementSet()
        l.addSet = {4}
        l.removeElement(4)
        self.assertTrue(4 in l.removeSet)
        self.assertEqual(l.removeSet[4][l.iData], 4)
        self.assertTrue(isinstance(l.removeSet[4][l.iTimestamp], datetime))        

    @mock.patch('{}.LWWElementSet.hashObj'.format(SRC_PATH))
    def testIsMember(self, mockHash):
        ''' Adding to the addSet makes item member. Adding to the removeSet with a 
            greater timestamp removes its membership. Adding back to the addSet with greater
            timestamp than removeSet adds it back to members. '''
        mockHash.side_effect = lambda x: x
        l = LWWElementSet()
        l.addSet[4] = (4, '20210709')
        self.assertTrue(l.isMember(4))
        l.removeSet[4] = (4, '20210710')
        self.assertFalse(l.isMember(4))
        l.addSet[4] = (4, '20210711')
        self.assertTrue(l.isMember(4))
    
    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    def testGetMembers(self, mockIsMember):
        ''' getMembers should return valid members using isMember for each member in addSet '''
        mockIsMember.side_effect = [True, False, True]
        l = LWWElementSet()
        l.addSet = {4: (4, '20210709'), 
                    5: (5, '20210710'), 
                    6: (6, '20210711')
                }
        self.assertListEqual(l.getMembers(), [4, 6]) 

    def testMergeSet(self):
        ''' Test merging by Last Write Wins. If an element is not in the other set,
            it is compared with (None, datetime.min) to get the same element back from the max function'''
        c = LWWElementSet()
        d = LWWElementSet()        
        c.addSet = {
            4: (4, datetime(2021, 7, 10, 0, 0)),
            3: (3, datetime(2021, 7, 11, 0, 0))
        }
        d.addSet = {
            4: (4, datetime(2021, 7, 12, 0, 0)),
            5: (5, datetime(2021, 7, 11, 0, 0))
        }
        mergedAddSet = c.mergeSet(c.addSet, d.addSet)
        self.assertEqual(mergedAddSet[4][d.iTimestamp], datetime(2021, 7, 12, 0, 0))
        self.assertEqual(mergedAddSet[5][d.iTimestamp], datetime(2021, 7, 11, 0, 0))
        self.assertEqual(mergedAddSet[3][c.iTimestamp], datetime(2021, 7, 11, 0, 0))

    @mock.patch('{}.LWWElementSet.LWWElementSet.mergeSet'.format(SRC_PATH))
    def testMergeWith(self, mockMergeSet):
        ''' '''
        mockMergeSet.return_value = {'foo':'bar'}
        c = LWWElementSet()
        d = LWWElementSet()
        c.mergeWith(d)
        self.assertDictEqual(c.addSet, {'foo':'bar'})
        self.assertDictEqual(c.removeSet, {'foo':'bar'})


class LWWElementSetTestsComplexObject(TestCase):
    ''' Testing the functionalities with a Complex object, rather than simple int '''
    def testComplexObjectAdd(self):
        ''' Adding the complex object in the LWWSet '''
        c = LWWElementSet()
        complexObj = createComplexObj()
        c.addElement(complexObj)
        self.assertTrue(hashObj(complexObj) in c.addSet)
        self.assertTrue(isinstance(c.addSet[hashObj(complexObj)][c.iTimestamp], datetime))

    def testComplexObjectRemove(self):
        ''' Removing the complex object from the LWWSet'''
        c = LWWElementSet()
        complexObj = createComplexObj()

        with self.assertRaises(KeyError):
            c.removeElement(complexObj)
        
        c.addSet = {hashObj(complexObj)}
        c.removeElement(complexObj)
        self.assertTrue(hashObj(complexObj) in c.removeSet)
    
    @mock.patch('{}.LWWElementSet.LWWElementSet.isMember'.format(SRC_PATH))
    def testComplexGetMembers(self, mockIsMember):
        ''' Testing getMembers with Complex Object. Need to store hash as the key in the addSet
            since Python objects like dict, set raise unhashable type error '''
        mockIsMember.side_effect = [True, False, True]
        l = LWWElementSet()
        c1, c2, c3 = createComplexObj(), createComplexObj(), createComplexObj()
        l.addSet = {
            hashObj(c1): (c1, '20210709'), 
            hashObj(c2): (c2, '20210710'), 
            hashObj(c3): (c3, '20210711')
        }
        self.assertListEqual(l.getMembers(), [c1, c3]) 

    def testComplexObjectMegeSet(self):
        ''' Merging with Complex object as the data. Again, we take the hash of the object
            to store as the key in our addSet '''
        c = LWWElementSet()
        d = LWWElementSet()
        cx1, cx2, cx3 = createComplexObj(), createComplexObj(), createComplexObj()     
        dt1, dt2, dt3 = datetime(2021, 7, 10, 0, 0), datetime(2021, 7, 11, 0, 0), datetime(2021, 7, 12, 0, 0)   
        c.addSet = {
            hashObj(cx2): (cx2, dt1),
            hashObj(cx1): (cx1, dt1)
        }
        d.addSet = {
            hashObj(cx2): (cx2, dt2),
            hashObj(cx3): (cx3, dt3)
        }
        mergedAddSet = c.mergeSet(c.addSet, d.addSet)
        self.assertEqual(mergedAddSet[hashObj(cx2)][d.iTimestamp], dt2)
        self.assertEqual(mergedAddSet[hashObj(cx3)][d.iTimestamp], dt3)
        self.assertEqual(mergedAddSet[hashObj(cx1)][c.iTimestamp], dt1)  