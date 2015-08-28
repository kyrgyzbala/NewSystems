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

from lib.db.archea import pentaplets as p
from lib.db.archea import quadruplets as q
from lib.db.archea import triplets as tr
from lib.db.archea import duplets as d
from lib.db.archea.db_tools import org2src_src2files_map
from lib.db.archea import neighborhoods_path

# import report_generation as r
from lib.utils import reporting as r
import lib.utils.merging as merging
import lib.utils.tools as t


def generate_plots(limit_to, reports_folder, target_profiles, profile2def, gid2arcog_cdd, neighborhood_files_path):

    print 'Reading kplets from database'
    pentaplets = p.get_report_kplets(limit_to=limit_to, load_locations=True)
    quadruplets = q.get_report_kplets(limit_to=limit_to, load_locations=True)
    triplets = tr.get_report_kplets(limit_to=limit_to, load_locations=True)
    duplets = d.get_report_kplets(limit_to=limit_to, load_locations=True)

    print 'Merging within order'
    pentaplets = merging.merge_kplets_within_order(pentaplets)
    quadruplets= merging.merge_kplets_within_order(quadruplets)
    triplets = merging.merge_kplets_within_order(triplets)
    duplets = merging.merge_kplets_within_order(duplets)

    print 'Merging across order'
    triplets, duplets = merging.merge_kplets_across_order(triplets, duplets)
    quadruplets, triplets = merging.merge_kplets_across_order(quadruplets, triplets)
    pentaplets, quadruplets = merging.merge_kplets_across_order(pentaplets, quadruplets)

    print 'Reports'
    for i, kplet_pool in zip([5, 4, 3, 2], [pentaplets, quadruplets, triplets, duplets]):
        for j, kplet_sublist in enumerate(kplet_pool):
            xls_file_name = os.path.join(reports_folder, str(i),  "%d_%d.xls" % (j+1, i))
            r.write_to_xls(xls_file_name,kplet_sublist,target_profiles,profile2def,gid2arcog_cdd,neighborhood_files_path,org2src_src2files_map)


if __name__ == '__main__':

    print 'Pre-Loading dictionaries'
    target_profiles = t.target_profiles()
    profile2def = t.map_profile2def()
    gid2arcog_cdd = t.map_gid2arcog_cdd()
    neighborhood_files_path = neighborhoods_path()

    for limit_to, report_dir in zip([500, 1000, 1000000], ['top_500','top_1000','all']):
        reports_file_dir = os.path.join(gv.project_data_path, 'Archea/reports/merged_across_kplets/', report_dir)
        print "Generating reports for limit_to:", limit_to
        generate_plots(limit_to, reports_file_dir, target_profiles, profile2def, gid2arcog_cdd, neighborhood_files_path)
        print 'Done'
        print "------------------------"
        print