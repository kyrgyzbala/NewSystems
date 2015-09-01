__author__ = 'Sanjarbek Hudaiberdiev'

from lib.utils import tools as t
from lib.db.archea import neighborhoods_path
_neighborhoods_path = neighborhoods_path()
import sys


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

    assert len(kplet_1.codes) == len(kplet_2.codes)

    k = len(kplet_1.codes)
    common = len(kplet_1.codes.intersection(kplet_2.codes))
    if k == 5:
        return True if common >=3 else False
    elif k == 4:
        return True if common >2 else False
    elif k == 3:
        return True if common >=2 else False
    elif k==2:
        return True if common >=1 else False


def merge_kplets_within_orders(kplets, target_profiles):
    """ Merge the kplets of same size, if they carry similarity in composition. Return list.

    Keyword arguments:
    kplets -- list of objects of lib.classes.Kplet instances"""

    # First round of merging

    merged_kplets = []
    merged_out = [0 for i in range(len(kplets))]

    for i in range(len(kplets)):
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

    # Second round of merging
    del kplets
    del merged_out

    merged_communities = []
    merged_out = [0 for i in range(len(merged_kplets))]

    # A list for representing the merged kplets' lists in terms of target and community profiles
    merged_list_profiles = []

    for merged_list in merged_kplets:

        tmp_target_profiles, tmp_community_profiles = set([]), set([])
        for kplet in merged_list:
            tmp_target_profiles.update(set([profile for profile in kplet.codes if profile in target_profiles]))
            tmp_community_profiles.update(set([profile for profile in kplet.codes if profile not in target_profiles]))

        merged_list_profiles.append([tmp_target_profiles, tmp_community_profiles])

    del merged_list
    assert len(merged_list_profiles) == len(merged_kplets)

    for i in range(len(merged_kplets)):
        if merged_out[i] == 1:
            continue

        outer_list = merged_kplets[i]
        outer_target_profiles = merged_list_profiles[i][0]
        outer_community_profiles = merged_list_profiles[i][1]
        to_move = []

        for j in range(i+1, len(merged_kplets)):
            if merged_out[j] == 1:
                continue

            inner_list = merged_kplets[j]
            inner_target_profiles = merged_list_profiles[j][0]
            inner_community_profiles = merged_list_profiles[j][1]

            union = inner_community_profiles.union(outer_community_profiles)
            common = inner_community_profiles.intersection(outer_community_profiles)

            if not outer_target_profiles or not inner_target_profiles:
                if float(len(common))/len(union) > 0.7:
                    to_move += inner_list
                    merged_out[j] = 1

            # For majority of cases, when kplet includes a target profile
            elif outer_target_profiles == inner_target_profiles:
                # When target profiles match, the rest can be selected with lose threshold
                if float(len(common)) / len(union) >= 0.5:
                    to_move += inner_list
                    merged_out[j] = 1

        merged_communities.append(outer_list + to_move)

    # Third round of merging

    merged_communities_2 = []
    merged_out = [0 for i in range(len(merged_communities))]

    merged_list_profiles = []

    for merged_list in merged_communities:
        merged_list_profiles.append(set([code for code in kplet.codes for kplet in merged_list]))

    for i in range(len(merged_communities)):
        if merged_out[i] == 1:
            continue
        to_move = []
        outer_community = merged_list_profiles[i]
        outer_list = merged_communities[i]

        for j in range(i+1, len(merged_communities)):
            if merged_out[j] == 1:
                continue
            inner_community = merged_list_profiles[j]
            inner_list = merged_communities[j]

            union = inner_community.union(outer_community)
            common = inner_community.intersection(outer_community)

            if float(len(common))/len(union) >= 0.8:
                to_move += inner_list
                merged_out[j] = 1

        merged_communities_2.append(outer_list + to_move)

    return merged_communities_2


def merge_kplets_across_order(superplets_pool, subplets_pool):
    """ Merge kplets of different size.

    Input arguments:
    superplets -- higher level kplets
    subplets -- lower level kplets.

    In case of pentaplets and quadruplets, merge out the quadruplets into the pentaplets, if it happens to be a
    supbset of any pentaplet.
    """

    superplet_codes = []
    for superplet_list in superplets_pool:
        tmp_codes = set([])
        for kplet in superplet_list:
            tmp_codes.update(kplet.codes)
        superplet_codes.append(tmp_codes)

    assert len(superplet_codes) == len(superplets_pool)

    merged_out = [[0]*len(subplets_list) for subplets_list in subplets_pool]

    for subplet_outer_ind in range(len(subplets_pool)):
        subplet_list = subplets_pool[subplet_outer_ind]

        for subplet_inner_ind in range(len(subplet_list)):
            cur_subplet = subplet_list[subplet_inner_ind]

            for superplet_ind in range(len(superplets_pool)):

                if cur_subplet.codes.issubset(superplet_codes[superplet_ind]):
                    superplets_pool[superplet_ind].append(cur_subplet)
                    merged_out[subplet_outer_ind][subplet_inner_ind] = 1
                    break

    subplets_pool = [[subplet_list[i] for i in range(len(subplet_list)) if not merged_out[cnt][i]] for cnt, subplet_list in enumerate(subplets_pool)]

    return  superplets_pool, subplets_pool