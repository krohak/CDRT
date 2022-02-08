import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SRC_PATH = 'src.LWWElementGraph'

from src.LWWElementGraph.LWWElementSet import LWWElementSet, hashObj
from src.LWWElementGraph.LWWElementGraph import LWWElementGraph