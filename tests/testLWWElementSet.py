from unittest import TestCase, mock
from datetime import datetime
from context import LWWElementSet, hashObj

class LWWElementSetTests(TestCase):

    def __init__(self, *args, **kwargs):
        super(LWWElementSetTests, self).__init__(*args, **kwargs)
        self.complexObj1 = [{
            'timestamp' : [ 46112.124651],
            'event': {
                    'ABS_MT_POSITION_X': '0000010f',
                    'ABS_MT_POSITION_Y': '00000439',
                    'ABS_MT_PRESSURE': '0000009e',
                }
        }]
        self.complexObj2 = [{
            'timestamp' : [ 94519.765437],
            'event': {
                    'ABS_MT_POSITION_X': '08742101',
                    'ABS_MT_POSITION_Y': '00032101',
                    'ABS_MT_PRESSURE': '063329506',
                }
        }]
        self.complexObj3 = [{
            'timestamp' : [ 117517.08237],
            'event': {
                    'ABS_MT_POSITION_X': '023475306',
                    'ABS_MT_POSITION_Y': '874248959',
                    'ABS_MT_PRESSURE': '7869040953',
                }
        }]

    def testInit(self):
        l = LWWElementSet()
        self.assertEqual(len(l.addSet), 0)
        self.assertEqual(len(l.removeSet), 0)

    def testInitWithArgs(self):
        l = LWWElementSet({3:3}, {4:4})
        self.assertDictEqual(l.addSet, {3:3})
        self.assertDictEqual(l.removeSet, {4:4})

    def testAddElement(self):
        l = LWWElementSet()
        l.addElement(4)
        self.assertTrue(hashObj(4) in l.addSet)
        self.assertTrue(isinstance(l.addSet[hashObj(4)][l.iTimestamp], datetime))
        self.assertEqual(l.addSet[hashObj(4)][l.iData], 4)
    
    def testRemoveBeforeAdd(self):
        l = LWWElementSet()
        with self.assertRaises(KeyError):
            l.removeElement(4)

    def testRemoveElement(self):
        l = LWWElementSet()
        l.addElement(4)
        l.removeElement(4)
        self.assertTrue(hashObj(4) in l.removeSet)
        self.assertTrue(isinstance(l.removeSet[hashObj(4)][l.iTimestamp], datetime))
        self.assertEqual(l.removeSet[hashObj(4)][l.iData], 4)

    def testIsMember(self):
        l = LWWElementSet()
        l.addElement(4)
        self.assertTrue(l.isMember(4))
        l.removeElement(4)
        self.assertFalse(l.isMember(4))
        l.addElement(4)
        self.assertTrue(l.isMember(4))
    
    def testGetMembers(self):
        l = LWWElementSet()
        l.addElement(4)
        l.removeElement(4)
        l.addElement(4)
        l.addElement(5)
        l.addElement(6)
        l.removeElement(5)
        self.assertListEqual(l.getMembers(), [4, 6]) 

    def testMergeSet(self):
        c = LWWElementSet()
        c.addElement(4)
        c.removeElement(4)
        c.addElement(4)

        d = LWWElementSet()
        d.addElement(4)
        d.removeElement(4)
        d.addElement(5)
        addTime = d.addSet[hashObj(4)][d.iTimestamp]
        removetime = d.removeSet[hashObj(4)][d.iTimestamp]
        addTimeFive = d.addSet[hashObj(5)][d.iTimestamp]

        mergedAddSet = c.mergeSet(c.addSet, d.addSet)
        mergedRemoveSet = c.mergeSet(c.removeSet, d.removeSet)

        self.assertEqual(mergedAddSet[hashObj(4)][d.iTimestamp], addTime)
        self.assertEqual(mergedRemoveSet[hashObj(4)][d.iTimestamp], removetime)
        self.assertEqual(mergedAddSet[hashObj(5)][d.iTimestamp], addTimeFive)

    @mock.patch('LWWElementSet.LWWElementSet.mergeSet')
    def testMergeWith(self, mockMergeSet):
        mockMergeSet.return_value = {'foo':'bar'}
        c = LWWElementSet()
        d = LWWElementSet()
        c.mergeWith(d)
        self.assertDictEqual(c.addSet, {'foo':'bar'})
        self.assertDictEqual(c.removeSet, {'foo':'bar'})

    def testComplexObjectAdd(self):
        c = LWWElementSet()
        c.addElement(self.complexObj1)
        self.assertTrue(hashObj(self.complexObj1) in c.addSet)
        self.assertTrue(c.isMember(self.complexObj1))

    def testComplexObjectRemove(self):
        c = LWWElementSet()

        with self.assertRaises(KeyError):
            c.removeElement(self.complexObj1)
        
        c.addElement(self.complexObj1)
        c.removeElement(self.complexObj1)
        self.assertTrue(hashObj(self.complexObj1) in c.removeSet)
        self.assertFalse(c.isMember(self.complexObj1))
    
    def testComplexGetMembers(self):
        l = LWWElementSet()
        l.addElement(set([4,5]))
        l.removeElement(set([4,5]))
        l.addElement(set([4,5]))
        l.addElement(set([5,6]))
        l.addElement(set([6,7]))
        l.removeElement(set([5,6]))
        self.assertListEqual(l.getMembers(), [set([4,5]), set([6,7])]) 

    def testComplexObjectMegeSet(self):
        c = LWWElementSet()
        d = LWWElementSet()

        c.addElement(self.complexObj1)
        d.addElement(self.complexObj1)
        addTime1 = d.addSet[hashObj(self.complexObj1)][d.iTimestamp]

        d.addElement(self.complexObj2)
        c.addElement(self.complexObj2)
        d.removeElement(self.complexObj2)
        addTime2 = c.addSet[hashObj(self.complexObj2)][d.iTimestamp]
        removetime2 = d.removeSet[hashObj(self.complexObj2)][d.iTimestamp]

        c.addElement(self.complexObj3)
        d.addElement(self.complexObj3)
        c.removeElement(self.complexObj3)
        d.removeElement(self.complexObj3)
        addTime3 = d.addSet[hashObj(self.complexObj3)][d.iTimestamp]
        removetime3 = d.removeSet[hashObj(self.complexObj3)][d.iTimestamp]

        c.removeElement(self.complexObj1)
        removetime1 = c.removeSet[hashObj(self.complexObj1)][d.iTimestamp]

        mergedAddSet = c.mergeSet(c.addSet, d.addSet)
        mergedRemoveSet = c.mergeSet(c.removeSet, d.removeSet)
        self.assertEqual(mergedAddSet[hashObj(self.complexObj1)][d.iTimestamp], addTime1)
        self.assertEqual(mergedRemoveSet[hashObj(self.complexObj1)][d.iTimestamp], removetime1)
        self.assertEqual(mergedAddSet[hashObj(self.complexObj2)][d.iTimestamp], addTime2)
        self.assertEqual(mergedRemoveSet[hashObj(self.complexObj2)][d.iTimestamp], removetime2)
        self.assertEqual(mergedAddSet[hashObj(self.complexObj3)][d.iTimestamp], addTime3)
        self.assertEqual(mergedRemoveSet[hashObj(self.complexObj3)][d.iTimestamp], removetime3)       