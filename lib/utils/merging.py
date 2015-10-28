__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')
import global_variables as gv

from lib.utils import tools as t
from lib.db.archea import neighborhoods_path
from lib.utils.classes import NeighborhoodFileSummary, Neighborhood
import os

# Globals
_gid2arcog_cdd = t.map_gid2arcog_cdd()
_neighborhoods_path = neighborhoods_path()


def merge_similar_files(files):

    neighborhoods = t.load_neighborhoods(_neighborhoods_path, files)

    merged_out = [0 for i in range(len(neighborhoods))]

    for i in range(len(neighborhoods)):
        if merged_out[i] == 1:
            continue

        pivot_gids = set([g.gid for g in neighborhoods[i].genes])

        for j in range(i+1, len(neighborhoods)):
            if merged_out[j] == 1:
                continue
            cur_gids = set([g.gid for g in neighborhoods[j].genes])

            if len(pivot_gids.intersection(cur_gids)) >= len(pivot_gids)/2:
                merged_out[j] = 1

    included_files, excluded_files = [], []
    for i in range(len(merged_out)):
        cur_file = neighborhoods[i].source_file.split('/')[-1]
        if merged_out[i] == 0:
            included_files.append(cur_file)
        else:
            excluded_files.append(cur_file)

    return included_files, excluded_files


def _similar_same_order(kplet_1, kplet_2):
    """Chech if kplet_1 and kplet_2 are similar. Return boolean

    Input:
    kplet_1 and kplet_2 are lib.classes.Kplet objects.

    Procedure implements the similarity check for different values of k
    """
    k = kplet_1.k
    common = len(kplet_1.codes.intersection(kplet_2.codes))
    if k == 5:
        return True if common >3 else False
    elif k == 4:
        return True if common >2 else False
    elif k == 3:
        return True if common >=2 else False
    elif k == 2:
        return True if common >=1 else False


def basic_merge_within_orders(kplets):

    merged_kplets = []
    merged_out = [0 for _ in range(len(kplets))]

    for i in range(len(kplets)):
        # if i % 1000 == 0:
        #     print i
        if merged_out[i] == 1:
            continue
        outer_kplet = kplets[i]
        to_move = []
        for j in range(i+1, len(kplets)):
            if merged_out[j] == 1:
                continue
            inner_kplet = kplets[j]

            if _similar_same_order(outer_kplet, inner_kplet):
                to_move.append(inner_kplet)
                merged_out[j] = 1
        merged_kplets.append([outer_kplet] + to_move)

    return merged_kplets


def merge_kplets_within_orders_iterative(kplets):
    """ Merge the kplets of same size, if they carry similarity in composition. Return list.

    Keyword arguments:
    kplets -- list of objects of lib.classes.Kplet instances"""

    # First round of merging

    merged_kplets = basic_merge_within_orders(kplets)

    # Second round of merging
    # Iterate the merging procedure until it converges
    cnt = 1
    while True:
        merged_out = [0 for _ in range(len(merged_kplets))]
        # A list for representing the merged kplets' lists in terms of profile codes
        # communities = []
        # for merged_list in merged_kplets:
        #     communities.append(set(code for kplet in merged_list for code in kplet.codes))

        gid_pool = []
        for merged_list in merged_kplets:
            gid_pool.append(set(gid for kplet in merged_list for gid in kplet.gids))

        new_merged_kplets = []
        for i in range(len(merged_kplets)):
            if merged_out[i] == 1:
                continue
            to_move = []
            # outer_community = communities[i]
            outer_gids = gid_pool[i]
            outer_list = merged_kplets[i]
            for j in range(i+1, len(merged_kplets)):
                if merged_out[j] == 1:
                    continue
                # inner_community = communities[j]
                inner_gids = gid_pool[j]
                inner_list = merged_kplets[j]

                # common = inner_community.intersection(outer_community)
                # union = inner_community.union(outer_community)
                common = len(inner_gids.intersection(outer_gids))
                smaller = min(len(inner_gids), len(outer_gids))

                if not common:
                    continue

                if float(common)/smaller > 0.8:
                    to_move += inner_list
                    merged_out[j] = 1

            new_merged_kplets.append(outer_list + to_move)

        print cnt, len(merged_kplets), len(new_merged_kplets)#, "Communities:", " ".join([str(len(l)) for l in merged_kplets])
        cnt += 1

        if len(merged_kplets) == len(new_merged_kplets):
            merged_kplets = new_merged_kplets
            break
        merged_kplets = new_merged_kplets
    return merged_kplets


def merge_kplets_across_orders(superplets_pool, subplets_pool):
    """ Merge kplets of different size.

    Input arguments:
    superplets -- higher level kplets
    subplets -- lower level kplets

    In case of pentaplets and quadruplets, merge out the quadruplets into the pentaplets, if it happens to be a
    supbset of any pentaplet.
    """

    superplet_gi_pool = []
    for superplet_list in superplets_pool:
        tmp_gi_list = set([])
        for kplet in superplet_list:
            tmp_gi_list.update(kplet.gids)
        superplet_gi_pool.append(tmp_gi_list)

    assert len(superplet_gi_pool) == len(superplets_pool)

    merged_out = [[0]*len(subplets_list) for subplets_list in subplets_pool]

    for subplet_outer_ind in range(len(subplets_pool)):
        subplet_list = subplets_pool[subplet_outer_ind]

        for subplet_inner_ind in range(len(subplet_list)):
            cur_subplet = subplet_list[subplet_inner_ind]

            for superplet_ind in range(len(superplets_pool)):

                if cur_subplet.gids.issubset(superplet_gi_pool[superplet_ind]):
                    superplets_pool[superplet_ind].append(cur_subplet)
                    merged_out[subplet_outer_ind][subplet_inner_ind] = 1
                    break

    subplets_pool = [[subplet_list[i] for i in range(len(subplet_list)) if not merged_out[cnt][i]] for cnt, subplet_list in enumerate(subplets_pool)]
    subplets_pool = [l for l in subplets_pool if l]

    return superplets_pool, subplets_pool


def update_dictionary(map, key, value):
    if key in map:
        map[key] += value
    else:
        map[key] = value


def merge_into_file_summaries(kplets, neighborhood_files_path, file2src_src2org_map, data_type='bacteria'):

    _file2kplets = {}
    for kplet in kplets:
        for f in kplet.files:
            if f in _file2kplets:
                _file2kplets[f].append(kplet)
            else:
                _file2kplets[f] = [kplet]

    kplet_files = _file2kplets.keys()
    _file2src, _src2org = file2src_src2org_map(kplet_files)

    file_summaries = []
    for f in kplet_files:
        _neighborhood = Neighborhood(os.path.join(neighborhood_files_path, f))
        _src = _file2src[f]
        _org = _src2org[_src]
        kplets = _file2kplets[f]
        _neighborhood.extend_flanks(10, os.path.join(gv.pty_data_path, _org, "%s.pty" % _src), _gid2arcog_cdd)
        file_summaries.append(NeighborhoodFileSummary(f, kplets, _neighborhood, _org, _src))

    file_summaries = trim_file_summary_list(file_summaries, data_type)
    file_summaries = [fs for fs in file_summaries if fs]
    if len(file_summaries) < 2:
        return None, None, None, None, None

    file_summaries.sort(reverse=True)

    # Updating the map _file2src after trimming.
    new_file_list = [ fs.file_name for fs in file_summaries]
    for _file_name in _file2src.keys():
        if _file_name not in new_file_list:
            del _file2src[_file_name]

    community = set()
    for fs in file_summaries:
        [community.update(kplet.codes) for kplet in fs.kplets]

    community_count_with_flanks = {}
    community_count = {}

    for i in range(len(file_summaries)):
        cur_file_summary = file_summaries[i]
        for gene in cur_file_summary.neighborhood.genes:
            if gene.tag == 'flank':
                for k in gene.cogid.split():
                    update_dictionary(community_count_with_flanks, k, 1)
            else:
                for k in gene.cogid.split():
                    update_dictionary(community_count_with_flanks, k, 1)
                    update_dictionary(community_count, k, 1)

    return _src2org, file_summaries, community, community_count, community_count_with_flanks


def arcog_profiles_pool_into_classes_pool(profile_community):

    _arcog2class = t.map_arcog2class()
    class_community = list()

    for profiles in profile_community:
        classes = dict()
        for k in profiles:
            if k in _arcog2class:
                update_dictionary(classes, _arcog2class[k], profiles[k])
        class_community.append(classes)
    return class_community


def arcog_profile_count_into_class_count(community_count):

    _arcog2class = t.map_arcog2class()
    class_count = dict()
    for k in community_count:
        if k in _arcog2class:
            update_dictionary(class_count, _arcog2class[k], community_count[k])
        else:
            update_dictionary(class_count, 'Unclassified', community_count[k])

    return class_count


def cdd_profile_count_into_class_count(community_count):

    _cdd2class = t.map_cdd2class()
    class_count = dict()
    for k in community_count:
        if k in _cdd2class:
            update_dictionary(class_count, _cdd2class[k], community_count[k])
        else:
            update_dictionary(class_count, 'Unclassified', community_count[k])

    return class_count


def trim_file_summary_list(file_summaries, data_type='bacteria'):

    if data_type == 'bacteria':
        return [ c for c in file_summaries if len(c.kplets) > 20 ]
    elif data_type == 'archaea':
        return [ c for c in file_summaries if len(c.kplets) > 10 ]
    else:
        raise NotImplementedError
