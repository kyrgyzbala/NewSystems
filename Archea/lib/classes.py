__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
from BioClasses import Gene
import dm_tools as t

class ProfileCount(object):
    def __init__(self, count, weight):
        self.count = count
        self.weight = weight


class Neighborhood(object):
    def __init__(self, source_file):
        self.source_file = source_file
        self.genes = t.get_pty_file(source_file)
        self.flank_extension = None

    def extend_flanks(self, flank_size, pty_path, ptt_path):

        first = self.genes[0].gid
        last = self.genes[-1].gid
        upstream, downstream = [], []

        organism = self.genes[0].organism
        source = self.genes[0].src

        gid2ptt = t.get_ptt_map(ptt_path, pty_path, organism, source)

        ptt_genes = gid2ptt.values()
        ptt_genes.sort()
        for i in range(len(ptt_genes)):
            if ptt_genes[i].gid == first:
                upstream = ptt_genes[i-flank_size: i]
            if ptt_genes[i].gid == last:
                downstream = ptt_genes[i+1:i+flank_size]
                break
        self.genes = upstream + self.genes + downstream
        self.flank_extension = True


class kplet(object):
    def __init__(self, id, profiles, weight=None, files=None):
        self.profiles = profiles
        self.id = id
        self.weight = weight
        self.files = files