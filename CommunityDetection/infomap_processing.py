#!/usr/bin/env python

import os
import sys

if sys.platform == 'darwin':
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/lib/BioPy/'))
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/SystemFiles/'))
elif sys.platform == 'linux2':
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/lib/BioPy/'))
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/SystemFiles/'))

import global_variables as gv
sys.path.append(gv.project_code_path)

import lib.utils.clustering.reporting as reporting
import lib.utils.tools as t
from lib.utils.clustering import Locus


class Node(object):

    def __init__(self, type, name, weight=None, file_name=None):
        # type 1 = cluster, 2 = locus
        self.type = type
        self.name = name
        # only if type is 2
        self.weight = weight
        self.file_name = file_name




def parse_tree_file(in_file, locus2weight=None):

    cluster2nodes = {}

    for l in open(in_file):
        if l.startswith("#"):
            continue

        if "CLUSTER_" in l:

            node_name = l.split()[2][1:-1]
            _node = Node(type=1, name=node_name)

        else:

            node_name = l.split("\"")[1]
            file_name = node_name.split()[-1]

            weight = locus2weight[file_name] if locus2weight else 1

            _node = Node(type=2, name=node_name, weight=weight, file_name=file_name)

        cluster_no = l.split()[0].split(":")[0]

        if cluster_no in cluster2nodes:
            cluster2nodes[cluster_no].append(_node)
        else:
            cluster2nodes[cluster_no] = [_node]

    return cluster2nodes


def write_community_stats_file(community_stats_file, sorted_clusters):

    with open(community_stats_file, 'w') as outf:
        outf.write("#Community no\tGenes\tLoci\tE. loci\n")
        for cl_no, cl_loci in sorted_clusters:

            loci_size = len([locus for locus in cl_loci if locus.type==2])
            loci_esize = sum(locus.weight for locus in cl_loci if locus.type == 2)
            genes_size = len([locus for locus in cl_loci if locus.type==1])

            outf.write("%s\t%s\t%s\t%s\n" % (cl_no, genes_size, loci_size, loci_esize))



if __name__ == '__main__':

    data_dir = gv.project_data_path + 'cas4/unknowns/'
    infomap_file = data_dir + 'baiticity_limited/infomap/network.tree'
    weights_file = data_dir + 'full/jw_based_weights.tab'
    community_stats_file = data_dir + 'baiticity_limited/community_stats.tab'
    
    reports_dir = os.path.join(data_dir, 'baiticity_limited/reports')
    if not os.path.exists(reports_dir):
        os.mkdir(reports_dir)

    print "Loading loci"

    def_file = os.path.join(gv.project_data_path, 'cas4/profiles/defenseProfiles.tab')
    profile2gene = {}

    for l in open(def_file):
        terms = l.split('\t')
        profile = terms[0]
        gene_names = terms[3].split(',')
        if len(gene_names) > 1:
            profile2gene[profile] = gene_names[1]
        else:
            profile2gene[profile] = gene_names[0]

    cdd_profile2gene = t.map_cdd_profile2gene_name()
    cdd_profile2gene.update(profile2gene)

    file2locus = {}

    for f in os.listdir(data_dir + 'files'):
        locus = Locus(os.path.join(data_dir, 'files', f),
                      file_format='generic',
                      profile2gene=cdd_profile2gene)
        file2locus[f] = locus

    locus2weight = { l.split()[0]: float(l.split()[1]) for l in open(weights_file)}
    community2nodes = parse_tree_file(infomap_file, locus2weight)

    sorted_clusters = sorted(community2nodes.values(),
                             key=lambda x: sum(locus.weight for locus in x if locus.type==2),
                             reverse=True)

    # write_community_stats_file(community_stats_file, sorted_clusters)

    cdd_profile2def = t.map_cdd_profile2def()

    feature_profiles_file = os.path.join(gv.project_data_path, 'cas4/profiles/profiles_10_0.50_full.tab')

    reporting.generate_community_reports(sorted_clusters,
                                         reports_dir,
                                         locus2weight,
                                         file2locus,
                                         cdd_profile2def,
                                         feature_profiles_file=feature_profiles_file)