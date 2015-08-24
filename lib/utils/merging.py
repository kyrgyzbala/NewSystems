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


# def merge_kplets_within_order(kplets):
#
#     merged_kplets = []
#     merged_out = [0 for i in range(len(kplets))]
#
#     for i in range(len(kplets)):
#         if merged_out[i] == 1:
#             continue
#
#         cur_merged_list = [i]
#         merged_out[i] = 1
#
#         pivot = set(kplets[i][1])
#
#         for j in range(i, len(kplets)):
#             if merged_out[j] == 1:
#                 continue
#
#             if len(pivot.intersection(kplets[j][1])) >= len(pivot)/2:
#                 cur_merged_list.append(j)
#                 merged_out[j] = 1
#
#         merged_kplets.append(cur_merged_list)
#
#     ret_list = []
#     for merged_list in merged_kplets:
#         kplet_codes = []
#         kplet_files = []
#         kplet_ids = []
#         for i in merged_list:
#             kplet_codes += list(kplets[i][1])
#             kplet_files += kplets[i][4].split(',')
#             kplet_ids += [kplets[i][0]]
#         kplet_codes = set(kplet_codes)
#         kplet_files = set(kplet_files)
#         included_files, excluded_files = merge_similar_files(kplet_files)
#         # just in case
#         kplet_ids = set(kplet_ids)
#         ret_list.append([kplet_ids, kplet_codes, (included_files, excluded_files)])
#
#     return ret_list


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


def merge_kplets_within_order(kplets):
    """ Merge the kplets of same size, if they carry similarity in composition. Return list.

    Keyword arguments:
    kplets -- list of objects of lib.classes.Kplet instances"""

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
    return merged_kplets


def merge_kplet_orders(superplet_summaries, subplet_summaries):

    for i in range(len(subplet_summaries)):
        summary_subplet = subplet_summaries[i]

        [id_subplet, codes_subplet, (included_subplet, excluded_subplet)] = summary_subplet

        for j in range(len(superplet_summaries)):
            summary_superplet = superplet_summaries[j]
            [id_superplet, codes_superplet, (included_superplet, excluded_superplets)] = summary_superplet

            if codes_subplet.issubset(codes_superplet):
                for f in included_subplet:
                    if f not in included_superplet and f not in excluded_superplets:
                        superplet_summaries[j][2][0].append(f)

                included_subplet = []
                break

            if len(codes_subplet.intersection(codes_superplet)) >= ceil(len(codes_subplet)*0.7):
                for f in included_subplet:
                    if f in included_superplet or f in excluded_superplets:
                        included_subplet.remove(f)

        if included_subplet:
            subplet_summaries[i] = [id_subplet, codes_subplet, (included_subplet, excluded_subplet)]
        else:
            subplet_summaries[i] = []

    subplet_summaries = filter(None, subplet_summaries)
    return superplet_summaries, subplet_summaries


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
        tmp_codes = []
        for kplet in superplet_list:
            tmp_codes += kplet.codes
        superplet_codes.append(tmp_codes)




    for i in range(len(subplets)):
        subplet = subplets[i]

        [id_subplet, codes_subplet, (included_subplet, excluded_subplet)] = summary_subplet

        for j in range(len(superplet_summaries)):
            summary_superplet = superplet_summaries[j]
            [id_superplet, codes_superplet, (included_superplet, excluded_superplets)] = summary_superplet

            if codes_subplet.issubset(codes_superplet):
                for f in included_subplet:
                    if f not in included_superplet and f not in excluded_superplets:
                        superplet_summaries[j][2][0].append(f)

                included_subplet = []
                break

            if len(codes_subplet.intersection(codes_superplet)) >= ceil(len(codes_subplet)*0.7):
                for f in included_subplet:
                    if f in included_superplet or f in excluded_superplets:
                        included_subplet.remove(f)

        if included_subplet:
            subplet_summaries[i] = [id_subplet, codes_subplet, (included_subplet, excluded_subplet)]
        else:
            subplet_summaries[i] = []

    subplet_summaries = filter(None, subplet_summaries)
    return superplet_summaries, subplet_summaries