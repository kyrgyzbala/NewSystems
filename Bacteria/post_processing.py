#!/sw/bin/python2.7
__author__ = 'Sanjarbek Hudaiberdiev'

import os
import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')


import global_variables as gv
from lib.utils import tools as t
import lib.db
from lib.db.bacteria import pentaplets as p
from lib.db.bacteria import quadruplets as q
from lib.db.bacteria import triplets as tr
from lib.db.bacteria import duplets as d
import report_generation as r
from math import ceil

neighborhood_path = os.path.join(gv.project_data_path, 'Bacteria/genes_and_flanks/win_10/raw_nbr_files/')


def merge_similar_files(files):

    neighborhoods = t.load_neighborhoods(neighborhood_path, files)

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


def merge_similar_kplets(kplet_summaries):

    merged_kplets = []
    merged_out = [0 for i in range(len(kplet_summaries))]

    for i in range(len(kplet_summaries)):
        if merged_out[i] == 1:
            continue

        cur_merged_list = [i]
        merged_out[i] = 1
        pivot = set(kplet_summaries[i][1])

        for j in range(i, len(kplet_summaries)):
            if merged_out[j] == 1:
                continue

            if len(pivot.intersection(kplet_summaries[j][1])) > len(pivot)/2:
                cur_merged_list.append(j)
                merged_out[j] = 1

        merged_kplets.append(cur_merged_list)

    ret_list = []
    for merged_list in merged_kplets:
        kplet_codes = []
        kplet_files = []
        kplet_ids = []
        for i in merged_list:
            kplet_codes += list(kplet_summaries[i][1])
            kplet_files += kplet_summaries[i][4].split(',')
            kplet_ids += [kplet_summaries[i][0]]
        kplet_codes = set(kplet_codes)
        kplet_files = set(kplet_files)
        included_files, excluded_files = merge_similar_files(kplet_files)
        # just in case
        kplet_ids = set(kplet_ids)
        ret_list.append([kplet_ids, kplet_codes, (included_files, excluded_files)])

    return ret_list


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


def generate_reports_merged_within_kplets():

    summarized_5plets = p.get_report_kplets(limit_to=1000000)
    print len(summarized_5plets)
    merged_5plets = merge_similar_kplets(summarized_5plets)
    reports_file_dir = os.path.join('reports/merged_within_kplets', '5')
    cnt = 1
    for merged_5plet in merged_5plets:
        xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
        kplet_codes = merged_5plet[1]
        kplet_files = merged_5plet[2][0]
        r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
        cnt += 1

    summarized_4plets = q.get_report_kplets(limit_to=1000000)
    print len(summarized_4plets)
    merged_4plets = merge_similar_kplets(summarized_4plets)
    reports_file_dir = os.path.join('reports/merged_within_kplets', '4')
    cnt = 1
    for merged_4plet in merged_4plets:
        xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
        kplet_codes = merged_4plet[1]
        kplet_files = merged_4plet[2][0]
        r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
        cnt += 1

    summarized_3plets = tr.get_report_kplets(limit_to=1000000)
    print len(summarized_3plets)
    merged_3plets = merge_similar_kplets(summarized_3plets)
    reports_file_dir = os.path.join('reports/merged_within_kplets', '3')
    cnt = 1
    for merged_3plet in merged_3plets:
        xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
        kplet_codes = merged_3plet[1]
        kplet_files = merged_3plet[2][0]
        r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
        cnt += 1

    summarized_2plets = d.get_report_kplets(limit_to=1000000)
    print len(summarized_2plets)
    merged_2plets = merge_similar_kplets(summarized_2plets)
    reports_file_dir = os.path.join('reports/merged_within_kplets', '2')
    cnt = 1
    for merged_2plet in merged_2plets:
        xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
        kplet_codes = merged_2plet[1]
        kplet_files = merged_2plet[2][0]
        r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
        cnt += 1


if __name__ == '__main__':

    # id2cdd, cdd2id, cdd2def = lib.db.map_id2cdd_cdd2id_cdd2def()

    id2cdd = lib.db.map_id2cdd()

    print 'Generating summaries'
    summarized_5plets = merge_similar_kplets(p.get_report_kplets(id2cdd, limit_to=1000))
    print '5plets completed'
    summarized_4plets = merge_similar_kplets(q.get_report_kplets(id2cdd, limit_to=1000))
    print '4plets completed'
    summarized_3plets = merge_similar_kplets(tr.get_report_kplets(id2cdd, limit_to=1000))
    print '3plets completed'
    summarized_2plets = merge_similar_kplets(d.get_report_kplets(id2cdd, limit_to=1000))
    print '2plets completed'
    print

    print 'Merging summaries'
    summarized_3plets, summarized_2plets = merge_kplet_orders(summarized_3plets, summarized_2plets)
    print '3 and 2 completed'
    summarized_4plets, summarized_3plets = merge_kplet_orders(summarized_4plets, summarized_3plets)
    print '4 and 3 completed'
    summarized_5plets, summarized_4plets = merge_kplet_orders(summarized_5plets, summarized_4plets)
    print '5 and 4 completed'

    reports_file_dir = os.path.join('reports/merged_across_kplets/top_1000/')

    print 'Reports'
    for i, summarized_kplets in zip([5, 4, 3, 2], [summarized_5plets, summarized_4plets, summarized_3plets, summarized_2plets]):
        print 'Starting for', i
        for j, kplet in enumerate(summarized_kplets):
            xls_file_name = os.path.join(reports_file_dir, str(i),  "%d_%d.xls" % (j+1, i))
            kplet_codes = kplet[1]
            kplet_files = kplet[2][0]
            r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
