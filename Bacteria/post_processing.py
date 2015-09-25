#!/sw/bin/python2.7
__author__ = 'Sanjarbek Hudaiberdiev'

import os
import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import global_variables as gv
sys.path.append(gv.project_code_path)

from lib.db.bacteria import pentaplets as p
from lib.db.bacteria import quadruplets as q
from lib.db.bacteria import triplets as tr
from lib.db.bacteria import duplets as d
from lib.db import map_id2cdd
from lib.db.bacteria import neighborhoods_path
from lib.db.bacteria.db_tools import file2src_src2org_map
import lib.utils.merging as merging
import lib.utils.tools as t
import lib.utils.reporting as r
import pickle
import bz2


def generate_plots(limit_to, report_dir, target_profiles, profile2def, gid2arcog_cdd, neighborhood_files_path, profile_id2code):

    print 'Reading kplets from database'
    pentaplets = p.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    quadruplets = q.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    triplets = tr.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    duplets = d.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)

    print 'Merging within order'
    pentaplets = merging.merge_kplets_within_orders(pentaplets, target_profiles)
    quadruplets= merging.merge_kplets_within_orders(quadruplets, target_profiles)
    triplets = merging.merge_kplets_within_orders(triplets, target_profiles)
    duplets = merging.merge_kplets_within_orders(duplets, target_profiles)

    print 'Generationg reports for within orders merged lists'

    report_files_dir = os.path.join(gv.project_data_path, 'Bacteria/reports/merged_within_orders/', report_dir)
    if not os.path.exists(report_files_dir):
        os.mkdir(report_files_dir)

    for i, kplet_pool in zip([5, 4, 3, 2], [pentaplets, quadruplets, triplets, duplets]):
        for j, kplet_sublist in enumerate(kplet_pool):
            cur_reports_folder = os.path.join(report_files_dir, str(i))
            if not os.path.exists(cur_reports_folder):
                os.mkdir(cur_reports_folder)
            xls_file_name = os.path.join(cur_reports_folder,  "%d_%d.xls" % (j+1, i))
            r.write_to_xls(xls_file_name,kplet_sublist,target_profiles,profile2def,gid2arcog_cdd,neighborhood_files_path,file2src_src2org_map)

    print 'Merging across order'
    triplets, duplets = merging.merge_kplets_across_order(triplets, duplets)
    quadruplets, triplets = merging.merge_kplets_across_order(quadruplets, triplets)
    pentaplets, quadruplets = merging.merge_kplets_across_order(pentaplets, quadruplets)

    print 'Generationg reports for across orders merged lists'

    report_files_dir = os.path.join(gv.project_data_path, 'Bacteria/reports/merged_across_orders/', report_dir)
    if not os.path.exists(report_files_dir):
        os.mkdir(report_files_dir)

    for i, kplet_pool in zip([5, 4, 3, 2], [pentaplets, quadruplets, triplets, duplets]):
        for j, kplet_sublist in enumerate(kplet_pool):
            cur_reports_folder = os.path.join(report_files_dir, str(i))
            if not os.path.exists(cur_reports_folder):
                os.mkdir(cur_reports_folder)
            xls_file_name = os.path.join(cur_reports_folder,  "%d_%d.xls" % (j+1, i))
            r.write_to_xls(xls_file_name,kplet_sublist,target_profiles,profile2def,gid2arcog_cdd,neighborhood_files_path,file2src_src2org_map)


def generate_pickles(save_path, limit_to):

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    pentaplets = p.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    quadruplets = q.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    triplets = tr.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    duplets = d.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)

    print 'Starting within mergings'
    pentaplets = merging.basic_merge_within_orders(pentaplets)
    quadruplets = merging.basic_merge_within_orders(quadruplets)
    triplets = merging.basic_merge_within_orders(triplets)
    duplets = merging.basic_merge_within_orders(duplets)

    print 'Starting accross mergings'
    triplets, duplets = merging.merge_kplets_across_orders(triplets, duplets)
    quadruplets, triplets = merging.merge_kplets_across_order(quadruplets, triplets)
    pentaplets, quadruplets = merging.merge_kplets_across_order(pentaplets, quadruplets)

    print 'Dumping to files'
    dump_file = bz2.BZ2File('pentaplets_merged_across.p.bz2', 'w')
    pickle.dump(pentaplets, dump_file)
    dump_file = bz2.BZ2File('quadruplets_merged_across.p.bz2', 'w')
    pickle.dump(quadruplets, dump_file)
    dump_file = bz2.BZ2File('triplets_merged_across.p.bz2', 'w')
    pickle.dump(triplets, dump_file)
    dump_file = bz2.BZ2File('duplets_merged_across.p.bz2', 'w')
    pickle.dump(duplets, dump_file)


if __name__ == '__main__':

    print 'Pre-Loading dictionaries'
    target_profiles = t.bacteria_target_profiles()
    profile2def = t.map_cdd_profile2def()
    gid2arcog_cdd = t.map_gid2arcog_cdd()
    neighborhood_files_path = neighborhoods_path()
    profile_id2code = map_id2cdd()

    # for limit_to, report_dir in zip([300, 500, 1000, 100000],['top_300', 'top_500', 'top_1000', 'top_100000']):
    #
    #     print "Limit_to:", limit_to
    #     print
    #     generate_plots(limit_to, report_dir, target_profiles, profile2def, gid2arcog_cdd, neighborhood_files_path, profile_id2code)
    #     print 'Done'
    #     print "------------------------"

    data_path = os.path.join(gv.project_data_path,'Bacteria/pickle/')

    for limit_to in [10000, 100000]:
        print "Limit_to:", limit_to
        print
        cur_path = os.path.join(data_path, str(limit_to))
        generate_pickles(cur_path, limit_to)
        print 'Done'
        print "------------------------"