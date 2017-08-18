#!/home/hudaiber/env2.7/bin/python

import os
import sys
import configparser
from collections import defaultdict

###############################################################
config_file = os.path.join(os.path.expanduser('~'),'paths.cfg')
cfg=configparser.ConfigParser()
cfg.read(config_file)

code_path = cfg.get('NewSystems','code_path')
data_path = cfg.get('NewSystems','data_path')
sys.path.append(code_path)

###############################################################


import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import powerlaw
import lib.utils.graph.tools as gt
import lib.utils.tools as t


PROK1603_WEIGHT = 4930.0
RAND_ADJ_PROB = 0.0451314274706

work_dir = os.path.join(data_path, "prok1603/graph/")


def graph_preprocessing_with_prob_expectation(save_file=None):

    graph_file = os.path.join(work_dir, "adj_graph.p")

    G = nx.read_gpickle(graph_file)
    print "Raw graph size:", G.size()

    profile2prob = {l.split()[0]: float(l.split()[1]) for l in open(os.path.join(work_dir, 'profile_weight.txt'))}

    for k in profile2prob:
        profile2prob[k] /= PROK1603_WEIGHT

    G_orig = G.copy()

    total_edges = 0
    removed_edges = 0

    for edge in G.edges(data=True):
        nodes = edge[:2]
        _weight = edge[2]['weight']/PROK1603_WEIGHT
        _expected_weight = profile2prob[nodes[0]] * profile2prob[nodes[1]] * RAND_ADJ_PROB

        total_edges += 1
        if _weight < _expected_weight:
            G.remove_edge(*nodes)
            removed_edges +=1
        else:
            G[nodes[0]][nodes[1]]['weight'] = _weight

    print total_edges
    print removed_edges

    for node in G.nodes():
        if G.degree(node) == 0:
            print G[node]

    print "Pre-processed graph size", G.size()

    if save_file:
        print "Saving to", save_file
        nx.write_gpickle(G,save_file)

    return G



def graph_preprocessing_with_counts(G_input=None, save_file=None):

    if not G_input:
        graph_file = os.path.join(work_dir, "adj_graph.p")
        G = nx.read_gpickle(graph_file)
    else:
        G = G_input.copy()

    print "Raw graph size:", G.size()
    print "Raw graph nodes", G.number_of_nodes()

    profile2prob = {l.split()[0]: float(l.split()[1]) for l in open(os.path.join(work_dir, 'profile_weight.txt'))}

    for edge in G.edges(data=True):
        nodes = edge[:2]
        _weight = edge[2]['weight']
        _count = edge[2]['count']
        
        if _count < 3:
            G.remove_edge(*nodes)

    print "Pre-processed graph size", G.size()
    print "Pre-processed graph nodes", G.number_of_nodes()

    G.remove_nodes_from(nx.isolates(G))

    print "Pre-processed graph size", G.size()
    print "Pre-processed graph nodes", G.number_of_nodes()
    
    if save_file:
        print "Saving to", save_file
        nx.write_gpickle(G,save_file)

    return G



def uvrd_cas4_links(G, graph_save_dir):

    uvrd_profiles = ["COG0210", "PRK11773", "TIGR01075", "cl22977", "cl26202", "cl28312", "pfam00580", "pfam13361", "pfam13538"]
    cas4_profiles = ["cd09637", "cd09659", "cls000170", "COG1468", "COG4343", "pfam01930", "pfam06023"]
    all_profiles = uvrd_profiles + cas4_profiles
    profile2gene = t.map_cdd_defense2gene_name()

    print "Extracting subgraphs"
    cas4_g = gt.subgraph(G, cas4_profiles, radius=1)
    uvrd_g = gt.subgraph(G, uvrd_profiles, radius=1)
    print "Joining subgraphs"
    joint_g = nx.compose(cas4_g, uvrd_g)
    print "Writing graph to files"

    nodes_to_write= set()

    with open(os.path.join(graph_save_dir, "edgelist.txt"),"w") as edge_outf:

        for edge in joint_g.edges(data=True):
            (p1, p2, data) = edge

            # if p1 in all_profiles and p2 in all_profiles:
            edge_outf.write("%s\t%s\t%f\n" % (p1, p2, data['weight'])) 
            nodes_to_write.update([p1, p2])

    with open(os.path.join(graph_save_dir, "nodes.txt"),"w") as node_outf:

        for p in nodes_to_write:
            if p in cas4_profiles:
                _type = 1
            elif p in uvrd_profiles:
                _type = 2
            else:
                _type = 0

            node_outf.write("%s\t%s\t%d\n" % (p, profile2gene[p], _type))

    return joint_g



if __name__=="__main__":

    preprocessed_file=os.path.join(work_dir, "adj_graph.p")
    # G = graph_preprocessing(preprocessed_file)
    G = nx.read_gpickle(preprocessed_file)

    # gt.degree_distributions(G)
    # gt.clustering_coefficients(G)