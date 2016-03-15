__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import global_variables as gv
import dm_tools as dt
import tools as t

try:
    gnm2weight = t.map_genome2weight()
except:
    gnm2weight = {}

try:
    file2org = t.map_file2organism()
except:
    file2org = {}


class ProfileCount(object):
    def __init__(self, count, weight, gid):
        self.count = count
        self.weight = weight
        self.gids = [gid]


class Neighborhood(object):
    def __init__(self, source_file):
        self.source_file = source_file
        self.genes = dt.get_pty_file(source_file)
        for gene in self.genes:
            gene.tag = 'neighborhood'
        self.flank_extension = None

    def extend_flanks(self, flank_size, pty_path, cdd_map=None):

        first = self.genes[0].gid
        last = self.genes[-1].gid
        upstream, downstream = [], []

        pty_genes = dt.get_pty_file(pty_path)
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

    def __init__(self, id, codes, count=None, files=None):
        self.codes = set(codes)
        self.k = len(codes)
        self.id = id
        self.count = count
        self.files = sorted(files)
        self.locations = {f: [] for f in self.files}
        self.gids = set()
        self.gid2file = dict()

    # def load_locations(self, neighborhoods_path):
    #
    #     for f in self.files:
    #         genes = dt.get_pty_file(neighborhoods_path+'/'+f)
    #
    #         gi_list = set([])
    #         for gene in genes:
    #             for cogid in gene.cogid.split():
    #                 if cogid in self.codes:
    #                     gi_list.update([gene.gid])
    #                     break
    #
    #         self.locations[f] = gi_list
    #         self.gids.update(gi_list)
    #
    #         for gid in gi_list:
    #             self.gid2file[gid] = f
    #
    #     self.weight = sum(gnm2weight[file2org[self.gid2file[gid]]] for gid in self.gids)


    def __cmp__(self, other):
        if self.weight > other.weight:
            return 1
        elif self.weight < other.weight:
            return -1
        else:
            return 0


class KpletList(object):

    def __init__(self, kplets):
        self.kplets = kplets
        # self.ranks_order = ranks_order

        # self.all_gids = set()
        # self.gid2file = dict()
        self.files = set()

        for kplet in kplets:
        #     _gids = kplet.gids
        #     self.all_gids.update(_gids)
        #     self.gid2file.update(kplet.gid2file)
            self.files.update(kplet.files)

        self.weight = 0

    def merge(self, other):

        self.kplets += other.kplets
        # self.ranks_order += other.ranks_order
        self.files.update(other.files)

        # for kplet in other.kplets:
        #     _gids = kplet.gids
        #     self.all_gids.update(_gids)
        #     self.gid2file.update(kplet.gid2file)

        # self.weight = sum(gnm2weight[file2org[self.gid2file[gid]]] for gid in self.all_gids)




# class File(object):
#
#     def __init__(self, file_name, data_type='bacteria'):
#
#         if data_type == "bacteria":
#             data_path = os.path.join(gv.project_data_path, 'Bacteria/genes_and_flanks/win_10/pty')
#         elif data_type == "archea":
#             data_path = os.path.join(gv.project_data_path,   'Archea/genes_and_flanks/win_10/pty')
#
#         self.name = file_name
#         terms = open(os.path.join(data_path, file_name)).readlines()[0].split("\t")
#
#         self.organism = terms[3]
#         self.source = terms[4]


class NeighborhoodFileSummary(object):

    def __init__(self, file_name, kplets, neighborhood, org, src, weight):
        """Class for keeping summery information for a file. Keeps account of kplets (and related information for
        that kplet) found in current file.
        Default sorting is carried by total weights"""

        self.file_name = file_name
        self.kplets = kplets
        self.genes = neighborhood
        self.count = sum([kplet.count for kplet in kplets])
        # self.kplets_weight = sum([kplet.weight for kplet in kplets])
        self.weight = weight
        self.org = org
        self.src = src
        self.cas_type = ''


class WGSNeighborhoodFileSummary(object):

    def __init__(self, file_name, kplets, genes, org, src, cluster=None):
        """ cluster: is the Cluster class objects from utils.merging.wgs
            shows which cluster current locus is representing.
        """

        self.file_name = file_name
        self.kplets = kplets
        self.genes = genes
        self.count = sum([kplet.count for kplet in kplets])
        self.org = org
        self.src = src
        self.cluster = cluster
        self.cluster_local_count = 0


class WgsKpletList(object):

    def __init__(self, kplets):

        self.kplets = kplets
        self.files = set()
        for kplet in kplets:
            self.files.update(kplet.files)
        self.count = len(self.files)

    def merge(self, other):

        self.kplets += other.kplets
        self.files.update(other.files)
