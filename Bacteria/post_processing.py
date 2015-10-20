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
            r.write_to_xls(xls_file_name, kplet_sublist, target_profiles, profile2def, gid2arcog_cdd, neighborhood_files_path, file2src_src2org_map)


def generate_plots_from_pickle(limit_to, report_dir, target_profiles, profile2def, gid2arcog_cdd, neighborhood_files_path):

    data_path = os.path.join(gv.project_data_path, 'Bacteria/pickle/')

    fname = os.path.join(data_path, str(limit_to), 'pentaplets_merged_across.p.bz2')
    pentaplets = t.load_compressed_pickle(fname)
    fname = os.path.join(data_path, str(limit_to), 'quadruplets_merged_across.p.bz2')
    quadruplets = t.load_compressed_pickle(fname)
    fname = os.path.join(data_path, str(limit_to), 'triplets_merged_across.p.bz2')
    triplets = t.load_compressed_pickle(fname)
    fname = os.path.join(data_path, str(limit_to), 'duplets_merged_across.p.bz2')
    duplets = t.load_compressed_pickle(fname)

    print 'Generationg reports for across orders merged lists'

    report_files_dir = os.path.join(gv.project_data_path, 'Bacteria/reports/merged_across_orders/', report_dir)
    if not os.path.exists(report_files_dir):
        os.mkdir(report_files_dir)

    for i, kplet_pool in zip([5, 4, 3, 2], [pentaplets, quadruplets, triplets, duplets]):
        j = 0
        for kplet_sublist in kplet_pool:
            cur_reports_folder = os.path.join(report_files_dir, str(i))
            if not os.path.exists(cur_reports_folder):
                os.mkdir(cur_reports_folder)

            src2org, file_summaries, community, community_count = merging.merge_into_file_summaries(kplet_sublist,
                                                                                   neighborhood_files_path,
                                                                                   file2src_src2org_map)
            if not src2org:
                continue

            xls_file_name = os.path.join(cur_reports_folder,  "%d_%d.xls" % (j+1, i))
            j += 1
            params = dict()
            params['xls_file_name'] = xls_file_name
            params['src2org'] = src2org
            params['file_summaries'] = file_summaries
            params['community'] = community
            params['target_profiles'] = target_profiles
            params['profile2def'] = profile2def
            params['gid2arcog_cdd'] = gid2arcog_cdd
            r.write_to_xls(params)


def generate_pickles(save_path, limit_to):

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    pentaplets = p.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    quadruplets = q.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    triplets = tr.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    duplets = d.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)

    print 'Starting within mergings'
    pentaplets = merging.merge_kplets_within_orders_iterative(pentaplets)
    quadruplets = merging.merge_kplets_within_orders_iterative(quadruplets)
    triplets = merging.merge_kplets_within_orders_iterative(triplets)
    duplets = merging.merge_kplets_within_orders_iterative(duplets)

    print 'Starting accross mergings'
    triplets, duplets = merging.merge_kplets_across_orders(triplets, duplets)
    quadruplets, triplets = merging.merge_kplets_across_orders(quadruplets, triplets)
    pentaplets, quadruplets = merging.merge_kplets_across_orders(pentaplets, quadruplets)

    print 'Dumping to files'
    dump_file = bz2.BZ2File(os.path.join(save_path, 'pentaplets_merged_across.p.bz2'), 'w')
    pickle.dump(pentaplets, dump_file)
    dump_file = bz2.BZ2File(os.path.join(save_path, 'quadruplets_merged_across.p.bz2'), 'w')
    pickle.dump(quadruplets, dump_file)
    dump_file = bz2.BZ2File(os.path.join(save_path, 'triplets_merged_across.p.bz2'), 'w')
    pickle.dump(triplets, dump_file)
    dump_file = bz2.BZ2File(os.path.join(save_path, 'duplets_merged_across.p.bz2'), 'w')
    pickle.dump(duplets, dump_file)


def get_profiles_counts(data_path):
    file_names = ['pentaplets', 'quadruplets', 'triplets', 'duplets']
    print 'Reading merged kplet files'

    for file_name in file_names:
        print 'Loading the file:', file_name
        dump_file = bz2.BZ2File(os.path.join(data_path, '%s_merged_across.p.bz2'%file_name))
        kplets_pool = pickle.load(dump_file)

        print 'Counting community'
        community_count_pool = []
        community_count_pool_with_flanks = []
        for kplets in kplets_pool:
            a, b, c, community_count, community_count_with_flanks = merging.merge_into_file_summaries(kplets,
                                                                         neighborhood_files_path,
                                                                         file2src_src2org_map)
            if not a:
                continue
            community_count_pool.append(community_count)
            community_count_pool_with_flanks.append(community_count_with_flanks)

        dump_file_name = os.path.join(data_path, '%s_community_count.p.bz2'%file_name)
        print 'Dumping into', dump_file_name
        t.dump_compressed_pickle(dump_file_name, community_count_pool)

        dump_file_name = os.path.join(data_path, '%s_community_count_with_flanks.p.bz2'%file_name)
        print 'Dumping into', dump_file_name
        t.dump_compressed_pickle(dump_file_name, community_count_pool_with_flanks)

        print
        print


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
    print 'Generating community counts'
    for limit_to in [100000]:
        print "Limit_to:", limit_to
        print
        cur_path = os.path.join(data_path, str(limit_to))
        # generate_pickles(cur_path, limit_to)
        get_profiles_counts(cur_path)
        print 'Done'
        print "------------------------"


    print 'Generating plots'
    limit_to = 100000
    report_dir = 'top_100000'
    print "Limit_to:", limit_to
    print
    generate_plots_from_pickle(limit_to, report_dir, target_profiles, profile2def, gid2arcog_cdd, neighborhood_files_path, profile_id2code)
    print 'Done'
    print "------------------------"