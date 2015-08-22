#!/sw/bin/python2.7
__author__ = 'Sanjarbek Hudaiberdiev'

import os
import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

sys.path.append('/Users/hudaiber/Projects/NewSystems/code/')

import global_variables as gv
from lib.db.archea import pentaplets as p
from lib.db.archea import quadruplets as q
from lib.db.archea import triplets as tr
from lib.db.archea import duplets as d
import report_generation as r
import lib.utils.merging as merging


# def generate_reports_merged_within_kplets():
#
#     summarized_5plets = p.get_report_kplets(limit_to=1000000)
#     print len(summarized_5plets)
#     merged_5plets = merge_similar_kplets(summarized_5plets)
#     reports_file_dir = os.path.join('reports/merged_within_kplets', '5')
#     cnt = 1
#     for merged_5plet in merged_5plets:
#         xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
#         kplet_codes = merged_5plet[1]
#         kplet_files = merged_5plet[2][0]
#         r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
#         cnt += 1
#
#     summarized_4plets = q.get_report_kplets(limit_to=1000000)
#     print len(summarized_4plets)
#     merged_4plets = merge_similar_kplets(summarized_4plets)
#     reports_file_dir = os.path.join('reports/merged_within_kplets', '4')
#     cnt = 1
#     for merged_4plet in merged_4plets:
#         xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
#         kplet_codes = merged_4plet[1]
#         kplet_files = merged_4plet[2][0]
#         r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
#         cnt += 1
#
#     summarized_3plets = tr.get_report_kplets(limit_to=1000000)
#     print len(summarized_3plets)
#     merged_3plets = merge_similar_kplets(summarized_3plets)
#     reports_file_dir = os.path.join('reports/merged_within_kplets', '3')
#     cnt = 1
#     for merged_3plet in merged_3plets:
#         xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
#         kplet_codes = merged_3plet[1]
#         kplet_files = merged_3plet[2][0]
#         r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
#         cnt += 1
#
#     summarized_2plets = d.get_report_kplets(limit_to=1000000)
#     print len(summarized_2plets)
#     merged_2plets = merge_similar_kplets(summarized_2plets)
#     reports_file_dir = os.path.join('reports/merged_within_kplets', '2')
#     cnt = 1
#     for merged_2plet in merged_2plets:
#         xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
#         kplet_codes = merged_2plet[1]
#         kplet_files = merged_2plet[2][0]
#         r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
#         cnt += 1


if __name__ == '__main__':

    # id2cdd, cdd2id, cdd2def = lib.db.map_id2cdd_cdd2id_cdd2def()
    # duplets = d.get_report_kplets(limit_to=500,load_locations=True)
    # triplets = tr.get_report_kplets(limit_to=500,load_locations=True)
    pentaplets = p.get_report_kplets(limit_to=500,load_locations=True)

    import lib.utils.merging as merging
    pentaplets = merging.merge_kplets_within_order2(pentaplets)
    sys.exit()
    print 'Generating summaries'
    summarized_5plets = merge_similar_kplets(p.get_report_kplets(limit_to=500))
    summarized_4plets = merge_similar_kplets(q.get_report_kplets(limit_to=500))
    summarized_3plets = merge_similar_kplets(tr.get_report_kplets(limit_to=500))
    summarized_2plets = merge_similar_kplets(d.get_report_kplets(limit_to=500))

    print 'Merging summaries'
    summarized_3plets, summarized_2plets = merge_kplet_orders(summarized_3plets, summarized_2plets)
    summarized_4plets, summarized_3plets = merge_kplet_orders(summarized_4plets, summarized_3plets)
    summarized_5plets, summarized_4plets = merge_kplet_orders(summarized_5plets, summarized_4plets)
    reports_file_dir = os.path.join('reports/merged_across_kplets')

    print 'Reports'
    for i, summarized_kplets in zip([5, 4, 3, 2], [summarized_5plets, summarized_4plets, summarized_3plets, summarized_2plets]):
        for j, kplet in enumerate(summarized_kplets):
            xls_file_name = os.path.join(reports_file_dir, str(i),  "%d_%d.xls" % (j+1, i))
            kplet_codes = kplet[1]
            kplet_files = kplet[2][0]
            r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
