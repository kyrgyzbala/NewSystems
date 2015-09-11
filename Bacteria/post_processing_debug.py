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


if __name__ == '__main__':
    import time
    import pickle

    print 'Pre-Loading dictionaries'
    target_profiles = t.bacteria_target_profiles()
    profile2def = t.map_cdd_profile2def()
    gid2arcog_cdd = t.map_gid2arcog_cdd()
    neighborhood_files_path = neighborhoods_path()
    # profile_id2code = map_id2cdd()
    # pickle.dump(profile_id2code, open('profile_id2code.p','w'))
    profile_id2code = pickle.load(open('/Users/hudaiber/Projects/NewSystems/code/Bacteria/profile_id2code.p'))

    limit_to = 100000
    # tic = time.time()
    print 'Loading'
    pentaplets = p.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=True)
    pickle.dump(pentaplets, open('bacteria_pentaplet_100K.p', 'w'))
    sys.exit()

    # loading time 106.627920866

    # pentaplets = pickle.load(open('bacteria_pentaplet_10K.p'))
    # load time 6.26154589653

    # limit_to = 100000
    # tic = time.time()
    # pentaplets = p.get_report_kplets(profile_id2code, limit_to=limit_to, load_locations=False)
    # # # loading time 95.19
    # print 'Pentaplet 100000 db load time', time.time() - tic
    # pickle.dump(pentaplets, open('bacteria_pentaplet_100K.p', 'w'))

    pentaplets = pickle.load(open('/Users/hudaiber/Projects/NewSystems/code/Bacteria/bacteria_pentaplet_100K.p'))
    kplets = pentaplets

    # from merging module
    # __________________


    merged_kplets = []
    merged_out = [0 for i in range(len(kplets))]

    for i in range(len(kplets)):
        if i % 1000 == 0:
            print i
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
        # break


    # cnt_codes = {}
    # for kplet in merged_kplets[2]:
    #     for code in kplet.codes:
    #         if code in cnt_codes:
    #             cnt_codes[code] += 1
    #         else:
    #             cnt_codes[code] = 1
    #
    # n_keys = np.asarray(cnt_codes.keys())
    # n_values = np.asarray(cnt_codes.values())
    # sorted_values_ind = np.argsort(n_values)
    # print sorted(n_keys[sorted_values_ind[::-1][:int(len(sorted_values_ind)*0.3)]])


    # Iterative part
    tic = time.time()
    initial_length = len(merged_kplets)
    cnt = 1
    last_round = None

    while True:
        merged_out = [0 for i in range(len(merged_kplets))]
        # A list for representing the merged kplets' lists in terms of profile codes
        communities = []
        for merged_list in merged_kplets:
            communities.append(set(code for kplet in merged_list for code in kplet.codes))

        gid_pool = []
        for merged_list in merged_kplets:
            gid_pool.append(set(gid for kplet in merged_list for gid in kplet.gids))


        new_merged_kplets = []
        for i in range(len(merged_kplets)):
            if merged_out[i] == 1:
                continue
            to_move = []
            outer_community = communities[i]
            outer_gids = gid_pool[i]
            outer_list = merged_kplets[i]

            for j in range(i+1, len(merged_kplets)):
                if merged_out[j] == 1:
                    continue
                inner_community = communities[j]
                inner_gids = gid_pool[j]
                inner_list = merged_kplets[j]

                common = inner_community.intersection(outer_community)
                union = inner_community.union(outer_community)

                gid_common = inner_gids.intersection(outer_gids)
                smaller = min(len(inner_community),len(outer_community))

                # if not common:
                #     continue
                # if float(len(common))/len(union) > 0.5:
                #     to_move += inner_list
                #     merged_out[j] = 1

                if not gid_common:
                    continue
                if float(len(gid_common))/smaller > 0.7:
                    to_move += inner_list
                    merged_out[j] = 1

            new_merged_kplets.append(outer_list + to_move)

        print cnt, len(merged_kplets), len(new_merged_kplets), len(communities), "Communities:", " ".join([str(len(l)) for l in communities])
        cnt += 1

        if len(merged_kplets) == len(new_merged_kplets):
            merged_kplets = new_merged_kplets
            break
        merged_kplets = new_merged_kplets

    print 'Primary merging time', time.time() - tic


    gid_pool = []
    for merged_list in merged_kplets:
        tmp_gids = set()
        [tmp_gids.update(kplet.gids) for kplet in merged_list]
        gid_pool.append(tmp_gids)





    # Iterative part
    tic = time.time()
    initial_length = len(merged_kplets)
    cnt = 1
    last_round = None

    while True:
        merged_out = [0 for i in range(len(merged_kplets))]
        # A list for representing the merged kplets' lists in terms of profile codes
        communities = []
        for merged_list in merged_kplets:
            communities.append(set(code for kplet in merged_list for code in kplet.codes))

        new_merged_kplets = []
        for i in range(len(merged_kplets)):
            if merged_out[i] == 1:
                continue
            to_move = []
            outer_community = communities[i]
            outer_list = merged_kplets[i]
            for j in range(i+1, len(merged_kplets)):
                if merged_out[j] == 1:
                    continue
                inner_community = communities[j]
                inner_list = merged_kplets[j]
                common = inner_community.intersection(outer_community)
                union = inner_community.union(outer_community)
                if not common:
                    continue
                if float(len(common))/len(union) > 0.5:
                    to_move += inner_list
                    merged_out[j] = 1

            new_merged_kplets.append(outer_list + to_move)

        print cnt, len(merged_kplets), len(new_merged_kplets), len(communities), "Communities:", " ".join([str(len(l)) for l in communities])
        cnt += 1

        if len(merged_kplets) == len(new_merged_kplets):
            merged_kplets = new_merged_kplets
            break
        merged_kplets = new_merged_kplets

    print 'Primary merging time', time.time() - tic

    # 7995 6461 4561 3100 2088


    # Plotting temp

    report_files_dir = os.path.join('/Users/hudaiber/Projects/NewSystems/data/Bacteria/reports/tmp/')

    for j, kplet_sublist in enumerate(merged_kplets):
        print j
        xls_file_name = os.path.join(report_files_dir,  "%d.xls" % j)
        r.write_to_xls(xls_file_name,kplet_sublist,target_profiles,profile2def,gid2arcog_cdd,neighborhood_files_path,file2src_src2org_map)



    sys.exit()
    print 'Merging done in:', time.time() - tic

    reports_folder =  os.path.join(gv.project_data_path, 'Bacteria/reports/tmp/')

    for i, kplets in enumerate(pentaplets):
        xls_file_name = os.path.join(reports_folder,  "%d.xls" % i)
        r.write_to_xls(xls_file_name,kplets,target_profiles,profile2def,gid2arcog_cdd,neighborhood_files_path,file2src_src2org_map)

    sys.exit()

    for limit_to, report_dir in zip([300, 500, 1000, 100000],['top_300', 'top_500', 'top_1000', 'top_100000']):

        print "Limit_to:", limit_to
        print
        generate_plots(limit_to, report_dir, target_profiles, profile2def, gid2arcog_cdd, neighborhood_files_path, profile_id2code)
        print 'Done'
        print "------------------------"
