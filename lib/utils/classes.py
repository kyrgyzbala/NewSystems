__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
import dm_tools as t

class ProfileCount(object):
    def __init__(self, count, weight, gid):
        self.count = count
        self.weight = weight
        self.gids = [gid]


class Neighborhood(object):
    def __init__(self, source_file):
        self.source_file = source_file
        self.genes = t.get_pty_file(source_file)
        for gene in self.genes:
            gene.tag = 'neighborhood'
        self.flank_extension = None

    def extend_flanks(self, flank_size, pty_path, cdd_map=None):

        first = self.genes[0].gid
        last = self.genes[-1].gid
        upstream, downstream = [], []

        pty_genes = t.get_pty_file(pty_path)
        pty_genes.sort()

        for i in range(len(pty_genes)):
            if pty_genes[i].gid == first:
                upstream = pty_genes[i-flank_size: i]
            if pty_genes[i].gid == last:
                downstream = pty_genes[i+1:i+flank_size+1]
                break

        for gene in upstream:
            gene.tag = 'flank'
        for gene in downstream:
            gene.tag = 'flank'

        self.genes = upstream + self.genes + downstream

        if cdd_map:
            for gene in self.genes:
                if gene.cogid in ['-',''] and gene.gid in cdd_map:
                    gene.cogid = cdd_map[gene.gid]

        self.flank_extension = True


class Kplet(object):

    def __init__(self, id, codes, weight=None, count=None, files=None):
        self.codes = set(codes)
        self.k = len(codes)
        self.id = id
        self.weight = weight
        self.count = count
        self.files = sorted(files)
        self.locations = {f:[] for f in self.files}

    def load_locations(self, neighborhoods_path):

        for f in self.files:
            genes = t.get_pty_file(neighborhoods_path+'/'+f)
            gi_list = []
            for gene in genes:
                for cogid in gene.cogid.split():
                    if cogid in self.codes:
                        gi_list.append(gene.gid)
                        break
            self.locations[f] = gi_list

    def __cmp__(self, other):
        if self.weight > other.weight:
            return 1
        elif self.weight < other.weight:
            return -1
        else:
            return 0


class NeighborhoodFileSummary(object):
    def __init__(self, file_name, kplets, neighborhood, org, src):
        self.file_name = file_name
        self.kplets = kplets
        self.neighborhood = neighborhood
        self.count = sum([kplet.count for kplet in kplets])
        self.weight = sum([kplet.weight for kplet in kplets])
        self.org = org
        self.src = src

    def __cmp__(self, other):
        if self.weight > other.weight:
            return 1
        elif self.weight < other.weight:
            return -1
        else:
            return 0