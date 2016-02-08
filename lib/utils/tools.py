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
from operator import itemgetter
import cPickle
import bz2
import csv

def target_profiles():

    profiles_file = os.path.join(gv.project_data_path, 'Archea/arCOG/selected_arcogs.txt')
    return [l.strip() for l in open(profiles_file).readlines()]


def bacteria_target_profiles():

    profiles_file = os.path.join(gv.project_data_path, 'Bacteria/CDD/profile_ids.txt')
    return [l.strip() for l in open(profiles_file).readlines()]


def map_src2org():

    return {l.split()[1]:l.split()[0] for l in
            open(os.path.join(gv.data_path, 'info', 'map_gnm_src.txt')).readlines()}


def map_genome2weight():

    return {l.split()[0] : float(l.split()[1]) for l in
            open(os.path.join(gv.data_path, 'CDD', 'Prok1402_ad.weight.tab')).readlines()}


def map_profile2def():

    def_map = {l.split('\t')[0]: l.split('\t')[3] for l in
               open(os.path.join(gv.data_path, 'Archea/arCOG/ar14.arCOGdef.tab')).readlines()}
    def_map["-"] = " "
    return def_map


def map_cdd_profile2def():

    def_map = {l.split('\t')[1]: l.split('\t')[3] for l in
               open(os.path.join(gv.data_path, 'CDD/cdfind_pub_ad.dat')).readlines()}
    def_map["-"] = " "
    return def_map


def update_dictionary(map, key, value):
    if key in map:
        map[key] += value
    else:
        map[key] = value


def update_dictionary_set(map, key, value):
    if key in map:
        if isinstance(value, set):
            map[key].update(value)
        else:
            map[key].update(set([value]))
    else:
        if isinstance(value, set):
            map[key] = value
        else:
            map[key] = set([value])


# def update_dictionary_list_value(map, key, value):
#     if key in map:
#         map[key] += [value]
#     else:
#         map[key] = [value]


def merge(d1, d2, merge_fn):
    """
    Merges two dictionaries, non-destructively, combining
    values on duplicate keys as defined by the optional merge
    function.  The default behavior replaces the values in d1
    with corresponding values in d2.

    Examples:

    >>> d1
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1, lambda x,y: y)
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1)
    {'a': 2, 'c': 6, 'b': 4}
    """
    result = dict(d1)
    for k,v in d2.items():
        if k in result:
            result[k] = merge_fn(result[k], v)
        else:
            result[k] = v
    return result


def merge_set_val(d1, d2):

    result = dict(d1)
    for k,v in d2.items():
        if k in result:
            result[k].update(v)
        else:
            result[k] = v
    return result



def merge_dict_list(dict_list, merge_fn=lambda x,y: x+y):
    """
    Merge list of dictionaries into one dictionary.
    It uses the merge(d1, d2, merge_fn=lambda x,y: x+y)
    function from above. For the purpose of this library,
    it uses the default function for merging, which is addition.
    """
    result = dict()
    for _dict in dict_list:
        result = merge(result, _dict, merge_fn)
    return result


def merge_dict_set_list(dict_list, gid2weights):

    result = dict()
    for _dict in dict_list:
        result = merge_set_val(result, _dict)

    for k,v in result.items():
        result[k] = sum(gid2weights[gid] for gid in v)

    return result


# def merge_cog2gids_list(cog2gids_list):
#
#     result = dict()
#
#     for _dict in cog2gids_list:
#
#


def map_arcog2class():

    _profile2class_code = {l.split('\t')[0]: l.split('\t')[1] for l in
                      open(os.path.join(gv.data_path, 'Archea/arCOG/ar14.arCOGdef.tab')).readlines()}
    _class2def = {l.split('\t')[0]: l.split('\t')[2].strip() for l in
                  open(os.path.join(gv.data_path, 'Archea/arCOG/ar14/funclass.tab'))}

    _profile2class_def = dict()
    for _profile,_class_code in _profile2class_code.items():
        for _sub_class_code in _class_code:
            _class_def = _class2def[_sub_class_code]
            # update_dictionary_list_value(_profile2class_def, _profile, _class_def)
            update_dictionary(_profile2class_def, _profile, [_class_def])

    return _profile2class_def


def map_cdd2class():

    base_path = os.path.join(gv.project_code_path, 'scripts/cdd_clusters')
    cdd_class_file     = os.path.join(base_path, 'cdd_to_class.tab')
    cdd_class_def_file = os.path.join(base_path, 'fun2003-2014.tab')

    _profile2class_code = {l.split('\t')[0]: l.split('\t')[1].strip() for l in open(cdd_class_file).readlines()}
    _class2def = {l.split('\t')[0]: l.split('\t')[1].strip() for l in open(cdd_class_def_file).readlines()}

    _profile2class_def = dict()
    for _profile,_class_code in _profile2class_code.items():
        for _sub_class_code in _class_code:
            _class_def = _class2def[_sub_class_code]
            update_dictionary(_profile2class_def, _profile, [_class_def])

    return _profile2class_def


def map_genome2weight():

    return {l.split()[0]: float(l.split()[1]) for l in
            open(os.path.join(gv.data_path, 'CDD', 'Prok1402_ad.weight.tab')).readlines()}


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

    import classes as cl

    if not target_files:
        files = [os.path.join(path, f) for f in os.listdir(path)]
    else:
        files = [os.path.join(path, f) for f in target_files]

    return [cl.Neighborhood(f) for f in files]


def load_compressed_pickle(fname, compression='bz2'):

    if isinstance(fname, str) and compression == 'bz2':
        f = bz2.BZ2File(fname, 'rb')
        retval = cPickle.load(f)
    else:
        raise NotImplementedError

    return retval


def dump_compressed_pickle(fname, data, compression='bz2'):

    if isinstance(fname, str) and compression == 'bz2':
        f = bz2.BZ2File(fname, 'wb')
        cPickle.dump(data, f)
    else:
        raise NotImplementedError


def map_file2organism():

    retval = dict()
    fname = os.path.join(gv.project_data_path, 'Archea/genes_and_flanks/win_10/filename_source_organism.tab')
    for l in open(fname):
        terms = l.strip().split()
        retval[terms[0]] = terms[2]

    fname = os.path.join(gv.project_data_path, 'Bacteria/genes_and_flanks/win_10/filename_source_organism.tab')
    for l in open(fname):
        terms = l.strip().split()
        retval[terms[0]] = terms[2]

    return retval


def map_wgs_profile_count(dataset):
    # Before filtration, After filtration
    bf, af = {}, {}
    if dataset==1:
        fname = os.path.join(gv.project_data_path, 'CRISPR/datasets/cas1_1/wgs_profile_count.tab')
        bf = {l.strip().split()[1]: l.strip().split()[0] for l in open(fname).readlines()}
        fname = os.path.join(gv.project_data_path, 'CRISPR/datasets/cas1_1/wgs_profile_count_af.tab')
        bf = {l.strip().split()[1]: l.strip().split()[0] for l in open(fname).readlines()}
    elif dataset==2:
        fname = os.path.join(gv.project_data_path, 'CRISPR/datasets/cas1_2/wgs_profile_count.tab')
        bf = {l.strip().split()[1]: l.strip().split()[0] for l in open(fname).readlines()}
        fname = os.path.join(gv.project_data_path, 'CRISPR/datasets/cas1_2/wgs_profile_count_af.tab')
        af = {l.strip().split()[1]: l.strip().split()[0] for l in open(fname).readlines()}
    elif dataset==3:
        fname = os.path.join(gv.project_data_path, 'CRISPR/datasets/crispr/wgs_profile_count.tab')
        bf = {l.strip().split()[1]: l.strip().split()[0] for l in open(fname).readlines()}
        fname = os.path.join(gv.project_data_path, 'CRISPR/datasets/crispr/wgs_profile_count_af.tab')
        af = {l.strip().split()[1]: l.strip().split()[0] for l in open(fname).readlines()}

    return bf, af


def write_kplets_to_csv(kplets, out_name, compression=False):

    if compression=='True':
        fout = bz2.BZ2File(out_name, "w")
        # fout = gzip.open(csv_file,"w")
    else:
        fout = open(out_name, "w")

    csv_writer = csv.writer(fout)
    csv_writer.writerow(('Id', 'K', 'Count', 'Codes', 'Files'))
    for kplet in kplets:
        row = []
        row += [kplet.id, kplet.k, kplet.count,]
        row += [' '.join(list(kplet.codes)), ' '.join(kplet.files)]
        csv_writer.writerow(row)



if __name__=='__main__':

    file2organism = map_file2organism()

    pass
    # source_path = '/Users/hudaiber/Projects/NewSystems/data/Archea/genes_and_flanks/win_10/pty/'
    # target_file = 'src_to_gids.txt'
    #
    # build_src2gids_map(source_path, target_file)

