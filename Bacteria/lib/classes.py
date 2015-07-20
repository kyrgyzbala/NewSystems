__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
import dm_tools as t

class ProfileCount(object):
    def __init__(self, count, weight, src_file=None):
        self.count = count
        self.weight = weight
        self.files = set([src_file]) if src_file else None


class Neighborhood(object):
    def __init__(self, source_file):
        self.source_file = source_file
        self.genes = t.get_pty_file(source_file)
        self.flank_extension = None

    def extend_flanks(self, flank_size, pty_path, cdd_map=None):

        first = self.genes[0].gid
        last = self.genes[-1].gid
        upstream, downstream = [], []

        pty_genes = t.get_pty_file(pty_file=pty_path, annotation_map=cdd_map)
        pty_genes.sort()

        for i in range(len(pty_genes)):
            if pty_genes[i].gid == first:
                upstream = pty_genes[i-flank_size: i]
            if pty_genes[i].gid == last:
                downstream = pty_genes[i+1:i+flank_size]
                break

        self.genes = upstream + self.genes + downstream

        if cdd_map:
            for gene in self.genes:
                if gene.cogid in ['-',''] and gene.gid in cdd_map:
                    gene.cogid = cdd_map[gene.gid]

        self.flank_extension = True