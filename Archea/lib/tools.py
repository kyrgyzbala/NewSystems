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

def target_profiles():
    profiles_file = os.path.join(gv.project_data_path, 'Archea/arCOG/selected_arcogs.txt')
    return [l.strip() for l in open(profiles_file).readlines()]


def map_src2org():
    return {l.split()[1]:l.split()[0] for l in open(os.path.join(gv.data_path, 'info', 'map_gnm_src.txt')).readlines()}


def map_genome2weight():
    return {l.split()[0] : float(l.split()[1]) for l in open(os.path.join(gv.data_path, 'CDD', 'Prok1402_ad.weight.tab')).readlines()}


def map_profile2def():
    def_map = {l.split('\t')[0]: l.split('\t')[3] for l in open(os.path.join(gv.data_path, 'Archea/arCOG/ar14.arCOGdef.tab')).readlines()}
    def_map["-"] = " "
    return def_map


def map_genome2weight():
    return {l.split()[0]: float(l.split()[1]) for l in open(os.path.join(gv.data_path, 'CDD', 'Prok1402_ad.weight.tab')).readlines()}


def map_gid2src(map_file):
    out_map = {}
    with open(map_file) as f:
        for l in f:
            terms = l.split('\t')
            src = terms[1]
            gids = terms[2]
            for gid in gids.strip().split():
                out_map[gid] = src
    return out_map


def union(a, b):
    return list(set(a) | set(b))


def get_neighborhoods_of_kplet_ids(kplet_ids):

