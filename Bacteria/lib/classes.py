__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
from BioClasses import Gene
import tools as t

class ProfileCount(object):
    def __init__(self, count, weight):
        self.count = count
        self.weight = weight



class Neighborhood(object):
    def __init__(self, source_file):
        self.source_file = source_file
        self.genes = t.pty2genes_file2list(source_file)