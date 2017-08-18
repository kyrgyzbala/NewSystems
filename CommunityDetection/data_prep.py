#!/usr/bin/env python
__author__ = 'hudaiber'

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

from lib.utils.clustering import Locus
import lib.utils.tools as t
import lib.utils.clustering.scores as scores
import lib.utils.clustering.dendrogram as dendrogram
import numpy as np


def get_feature_clusters():

    feature_definition_file = os.path.join(gv.project_data_path, 'cas4/profiles/profiles_10_0.50.tab')

    feature_clusters = []

    cluster_description_file = os.path.join(gv.project_data_path, 'cas4/baiticity/cluster_id_size.tsv')
    cluster_id2effective_size = {l.split()[0]: l.strip().split()[1] for l in open(cluster_description_file)}

    for id in open(feature_definition_file).readlines():
        id = id.strip()
        feature_clusters.append("CLUSTER_%s_%s" % (id, cluster_id2effective_size[id]))

    return set(feature_clusters)


def prepare_network_files(loci, data_dir, feature_profiles_file=None):

    locus2id = {}
    cluster2id = {}

    if not feature_profiles_file:
        feature_clusters = set([cluster for locus in loci for cluster in locus.clusters])
    else:
        feature_clusters = set([l.strip() for l in open(feature_profiles_file)])

    print "No of feature clusters", len(feature_clusters)

    vertices, edges = [], []

    id = 1
    for locus in loci:
        locus2id[locus.base_file_name] = id

        _crispr_type = locus.crispr_type

        if _crispr_type.startswith("part unk") or _crispr_type.startswith("unk"):

            _type_code = 0

        elif _crispr_type.startswith("CAS-I-") or _crispr_type.strip() == "CAS-I" \
                or _crispr_type.strip() == "part CAS-I" \
                or _crispr_type.startswith("part CAS-I-"):

            _type_code = 1

        elif _crispr_type.startswith("CAS-II-"):

            _type_code = 2

        elif _crispr_type.startswith("CAS-III") \
                or _crispr_type.strip() == "part CAS-III" \
                or _crispr_type.startswith("part CAS-III-"):

            _type_code = 3

        elif _crispr_type.startswith("CAS-IV-") \
                or _crispr_type.startswith("part CAS-IV-"):

            _type_code = 4

        elif _crispr_type.startswith("CAS-V-"):

            _type_code = 5

        else:

            _type_code = 6
            print "Not parsed:", _crispr_type

        vertices.append("%d\t\"%s %s\"\t1\t%d\n" % (id, locus.crispr_type, locus.base_file_name, _type_code))
        id += 1

    for cluster in feature_clusters:
        vertices.append("%d\t\"%s\"\t2\t7\n" % (id, cluster))
        cluster2id[cluster] = id
        id += 1

    ########################################################################
    ################## This part is for preparing pajek file ###############
    ########################################################################

    net_file = open(os.path.join(data_dir, 'network.net'), 'w')
    for locus in loci:
        locus_id = locus2id[locus.base_file_name]
        for cluster in locus.clusters:
            if cluster in cluster2id:
                cluster_id = cluster2id[cluster]
                edges.append("%d %d 1\n" % (locus_id, cluster_id))

    net_file.write("*Vertices %d\n" % len(vertices))
    [net_file.write(l) for l in vertices]

    net_file.write("*Edges %d\n"%len(edges))
    [net_file.write(l) for l in edges]
    net_file.close()

    ########################################################################
    ############ This part is for preparing link file for cytoscape ########
    ########################################################################

    net_file = open(os.path.join(data_dir, 'network.ln'), 'w')

    [net_file.write(l) for l in edges]
    net_file.close()

    vertex_description_file = open(os.path.join(data_dir, 'vertices.txt'), 'w')
    vertex_description_file.write("#Id\tDescription\tType\tCRISPR type\n")
    [vertex_description_file.write(l) for l in vertices]
    vertex_description_file.close()


def add_column_to_file(source_file, target_file, add_file, column_name):

    add_lines = [l.strip() for l in open(add_file) if not l.startswith("#")]

    with open(target_file, 'w') as outf:
        with open(source_file) as inf:
            l = inf.readline().strip()
            outf.write(l + "\t" + column_name + "\n")
            ind = 1

            while l:

                l = inf.readline().strip()

                if not l:
                    continue

                try:
                    outf.write(l + "\t" + add_lines[ind] + "\n")
                except:
                    print "list index error:", ind

                ind += 1


def jw_based_weights(loci, save_dir):

    print "Preparing score matrix"
    M = scores.generate_jackard_score_matrix(loci)
    M += np.transpose(M)
    M = -1 * np.log(M)
    M[np.diag_indices_from(M)] = 0
    M[np.where(M==np.inf)] = 100

    dendrogram_file = save_dir + 'jw_based.png'
    print "Drawing dendrogram", dendrogram_file
    dendrogram.plot_dendrogram_from_score_matrix(M, dendrogram_file)

    newick_file = save_dir + 'jw_based.nw'
    print "Writing newick", newick_file
    leaf_names = [os.path.basename(locus.file_name) for locus in loci]
    dendrogram.convert_score_to_newick(M, leaf_names, newick_file)


if __name__=='__main__':

    data_dir = os.path.join(gv.project_data_path, 'cas4/unknowns/')
    files_path = os.path.join(data_dir, 'files')

    print "Loading loci"

    loci = [Locus(os.path.join(files_path, f), file_format='generic') for f in os.listdir(files_path)]

    # jw_based_weights(loci, data_dir + "full/")

    feature_profiles_file = os.path.join(gv.project_data_path, 'cas4/profiles/profiles_10_0.50_full.tab')

    prepare_network_files(loci, os.path.join(data_dir,'baiticity_limited'), feature_profiles_file=feature_profiles_file)

    # add_column_to_file(data_dir + "vertices.txt",
    #                    data_dir + "vertices2.txt",
    #                    data_dir + "infomap/network.clu",
    #                    "infomap_clu")