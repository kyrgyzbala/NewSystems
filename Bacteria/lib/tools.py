__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform == 'darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform == 'linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')
import global_variables as gv
import os
import classes as cl

def target_profiles():
    profiles_file = os.path.join(gv.project_data_path, 'CDD/profile_ids_all.txt')
    return [l.strip() for l in open(profiles_file).readlines()]


def map_src2org():
    return {l.split()[1]:l.split()[0] for l in open(os.path.join(gv.data_path, 'info', 'map_gnm_src_pty.txt')).readlines()}


def map_genome2weight():
    return {l.split()[0] : float(l.split()[1]) for l in open(os.path.join(gv.data_path, 'CDD', 'Prok1402_ad.weight.tab')).readlines()}


def map_profile2def():
    def_map = {l.split('\t')[1]: l.split('\t')[3] for l in open(os.path.join(gv.data_path, 'CDD', 'cdfind_pub_ad.dat')).readlines()}
    def_map["-"] = " "
    return def_map


def map_gid2cdd():
    cdd_map = {}
    for l in open(os.path.join(gv.data_path, 'CDD', 'all_Prok1402.ccp.csv')):
        terms = l.split(',')
        gid = terms[0]
        profile = terms[6]
        if gid in cdd_map:
            cdd_map[gid] += " %s"%profile
        else:
            cdd_map[gid] = profile

    return cdd_map




def union(a, b):
    return list(set(a) | set(b))


def load_neighborhoods(path):
    
    return [cl.Neighborhood(os.path.join(path, f)) for f in os.listdir(path)]

