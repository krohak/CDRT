from unittest import TestCase
from datetime import datetime
from collections import defaultdict
from context import LWWElementGraph, LWWElementSet

class LWWElementSetTests(TestCase):

    def testInit(self):
        g = LWWElementGraph()
        self.assertTrue(isinstance(g.vertices, LWWElementSet))
        self.assertTrue(isinstance(g.edges, LWWElementSet))
