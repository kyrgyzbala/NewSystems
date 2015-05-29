#!/usr/bin/env python
__author__ = 'Sanjarbek hudaiberdiev'

import os
import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')



import global_variables as gv
import dm_tools
import time
import pickle
from operator import itemgetter
from lib import classes as cl
from itertools import combinations
import numpy as np

if sys.platform == 'darwin':
    project_data_path= '/Users/hudaiber/Projects/NewSystems/data/Bacteria'
    nbrhds_path = os.path.join(project_data_path, 'genes_and_flanks', 'win_10', 'merged')
    org_src_map_file = '/Users/hudaiber/data/info/map_gnm_src.txt'
    gnm_weights_file = '/Users/hudaiber/data/CDD/Prok1402_ad.weight.tab'
    profile_description_file = os.path.join(project_data_path, 'CDD', 'cdfind_pub_ad.dat')
elif sys.platform=='linux2':
    project_data_path= '/home/hudaiber/Projects/NewSystems/data/Bacteria'
    nbrhds_path = os.path.join(project_data_path, 'genes_and_flanks', 'win_10', 'merged')
    org_src_map_file = '/home/hudaiber/data/info/map_gnm_src.txt'
    gnm_weights_file = '/home/hudaiber/data/CDD/Prok1402_ad.weight.tab'
    profile_description_file = os.path.join(project_data_path, 'CDD', 'cdfind_pub_ad.dat')

inter_dist = 21


def map_src2org():
    return {l.split()[1]:l.split()[0] for l in open(org_src_map_file).readlines()}


def map_genome2weight():
    return {l.split()[0] : float(l.split()[1]) for l in open(gnm_weights_file).readlines()}


def map_profile2def():
    return {l.split('\t')[1]: l.split('\t')[3] for l in open(profile_description_file).readlines()}


def union(a,b):
    return list(set(a) | set(b))


def count_combinations(neighborhoods, profile_list, r, src2org, gnm2weight):

    key_fmt = "-".join(["%s" for i in range(r)])
    combination_count = {}
    for n in neighborhoods:
        cur_src = n.genes[0].src
        cur_org = src2org[cur_src]

        tmp_list = " ".join([g.cogid for g in n.genes])
        tmp_list = [p for p in tmp_list.split() if p in profile_list]
        combination_list = combinations(set(tmp_list), r)

        for comb in combination_list:

            k = key_fmt % comb
            if k in combination_count:
                combination_count[k].count += 1
                combination_count[k].weight += gnm2weight[cur_org]
            else:
                combination_count[k] = cl.ProfileCount(1, gnm2weight[cur_org])
    return combination_count


def test():

    nbrd_path = os.path.join(project_data_path,'genes_and_flanks', 'win_10', 'merged')
    neighborhoods = [cl.Neighborhood(os.path.join(nbrd_path, f)) for f in os.listdir(nbrd_path)]

    cnt = 0

    lookfor = set(['COG0550', 'COG0551'])
    print "Looking for:", lookfor
    for nbr in neighborhoods:
        tmp = " ".join(g.cogid for g in nbr.genes)
        tmp = tmp.split()
        if lookfor.issubset(tmp):
            print tmp
            print lookfor
            print
            cnt+=1

    print "Fount %d times" % cnt

    # print len(neighborhoods)


def count_profiles_in_neighborhoods(neighborhoods_path, limit_to, comb_size):

    target_profiles=[l.strip() for l in open(os.path.join(project_data_path, 'CDD', 'profile_ids_all.txt'))]
    src2org = map_src2org()
    gnm2weight = map_genome2weight()
    
    neighborhoods = [cl.Neighborhood(os.path.join(neighborhoods_path, f)) for f in os.listdir(neighborhoods_path)]
    
    # profile_neighborhoods = [[g.cogid for g in n.genes] for n in neighborhoods]
    # profile_neighborhoods = [" ".join(nbr) for nbr in profile_neighborhoods]
    # profile_neighborhoods = [nbr.split() for nbr in profile_neighborhoods]
    
    profile_stats = {}
    for nbr in neighborhoods:
        src_name = nbr.genes[0].src
        org_name = src2org[src_name]
        for g in nbr.genes:
            if g.cogid == "":
                continue
            for tmpCog in g.cogid.split():
                if tmpCog in target_profiles:
                    continue
                if tmpCog in profile_stats:
                    profile_stats[tmpCog].weight += gnm2weight[org_name]
                    profile_stats[tmpCog].count += 1
                else:
                    profile_stats[tmpCog] = cl.ProfileCount(1, gnm2weight[org_name])

    profile_weights = [(k, v.weight) for k, v in profile_stats.items()]
    profile_weights = sorted(profile_weights, key=itemgetter(1), reverse=True)

    pickle.dump(profile_weights, open('profile_weights.p','w'))
    profile_weights = pickle.load(open('profile_weights.p'))

    top_profiles = [k for (k, v) in profile_weights[:limit_to]]
    print 'started counting'
    counted_combinations = count_combinations(neighborhoods, top_profiles, comb_size, src2org, gnm2weight)
    print 'Done counting'
    weight_values = np.array([v.weight for v in counted_combinations.values()])
    weight_values.sort()
    weight_values = weight_values[::-1]
    pivot_ind = np.where(np.cumsum(weight_values)/np.sum(weight_values)>=0.9)[0][0]
    pivot_value = weight_values[pivot_ind]

    counted_combinations = {k:v for k,v in counted_combinations.items() if v.weight>pivot_value}

    print 'started writing'

    fout = open('%d_%d.tab'%(limit_to, comb_size), 'w')
    fout.write("Comb\tweight\tcount\n")
    for k, v in counted_combinations.items():
        fout.write("%s\t%f\t%d\n" % (k, v.weight, v.count))
    fout.close()


if __name__=='__main__':

    # limit_to = int(sys.argv[1])
    # comb_size = int(sys.argv[2])
    # src2org = map_src2org()
    # gnm2weights = map_genome2weight()
    # print gnm2weights

    # limit_to = 500
    # comb_size = 3
    # count_profiles_in_neighborhoods(os.path.join(project_data_path,'genes_and_flanks', 'win_10', 'merged'), limit_to, comb_size)

    test()
