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
from lib import classes as cl
from operator import itemgetter


def target_profiles():
    profiles_file = os.path.join(gv.project_data_path, 'Archea/arCOG/selected_arcogs.txt')
    return [l.strip() for l in open(profiles_file).readlines()]

def bacteria_target_profiles():
    profiles_file = os.path.join(gv.project_data_path, 'Bacteria/CDD/profile_ids.txt')
    return [l.strip() for l in open(profiles_file).readlines()]


def map_src2org():
    return {l.split()[1]:l.split()[0] for l in open(os.path.join(gv.data_path, 'info', 'map_gnm_src.txt')).readlines()}


def map_genome2weight():
    return {l.split()[0] : float(l.split()[1]) for l in open(os.path.join(gv.data_path, 'CDD', 'Prok1402_ad.weight.tab')).readlines()}


def map_profile2def():
    def_map = {l.split('\t')[0]: l.split('\t')[3] for l in open(os.path.join(gv.data_path, 'Archea/arCOG/ar14.arCOGdef.tab')).readlines()}
    def_map["-"] = " "
    return def_map

def map_cdd_profile2def():
    def_map = {l.split('\t')[1]: l.split('\t')[3] for l in open(os.path.join(gv.data_path, 'CDD/cdfind_pub_ad.dat')).readlines()}
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


def map_gid2arcog():
    return {l.split(',')[0]: l.split(',')[6] for l in open(os.path.join(gv.data_path, 'Archea/arCOG/ar14.arCOG.csv')).readlines() if 'arCOG' in l}


def map_gid2arcog_cdd():
    _gid2arcog = map_gid2arcog()
    _gid2cdd = map_gid2cdd()

    return dict(_gid2cdd.items() + _gid2arcog.items())


def union(a, b):
    return list(set(a) | set(b))


def get_weighted_profiles_from_neighborhoods(neighborhoods_path, exclude_target=True):

    if exclude_target:
        _target_profiles = target_profiles()
    _src2org = map_src2org()
    _gnm2weight = map_genome2weight()
    neighborhoods = [cl.Neighborhood(os.path.join(neighborhoods_path, f)) for f in os.listdir(neighborhoods_path)]

    profile_stats = {}
    for nbr in neighborhoods:
        src_name = nbr.genes[0].src
        org_name = _src2org[src_name]
        org_weight = _gnm2weight[org_name] if org_name in _gnm2weight else 1
        for g in nbr.genes:
            if g.cogid == "":
                continue
            for tmpCog in g.cogid.split():
                if exclude_target and tmpCog in _target_profiles:
                    continue
                if tmpCog in profile_stats:
                    if g.gid not in profile_stats[tmpCog].gids:
                        profile_stats[tmpCog].weight += org_weight
                        profile_stats[tmpCog].count += 1
                        profile_stats[tmpCog].gids += [g.gid]
                else:
                    profile_stats[tmpCog] = cl.ProfileCount(1, org_weight, g.gid)

    profile_weights = [(k, v.weight) for k, v in profile_stats.items()]
    profile_weights = sorted(profile_weights, key=itemgetter(1), reverse=True)

    return profile_weights


def load_neighborhoods(path, target_files=None):

    if not target_files:
        files = [os.path.join(path, f) for f in os.listdir(path)]
    else:
        files= [os.path.join(path, f) for f in target_files]

    return [cl.Neighborhood(f) for f in files]


if __name__=='__main__':

    source_path = '/Users/hudaiber/Projects/NewSystems/data/Archea/genes_and_flanks/win_10/pty/'
    target_file = 'src_to_gids.txt'

    build_src2gids_map(source_path, target_file)