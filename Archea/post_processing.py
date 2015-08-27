#!/sw/bin/python2.7
__author__ = 'Sanjarbek Hudaiberdiev'

import os
import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

sys.path.append('/Users/hudaiber/Projects/NewSystems/code/')

from lib.db.archea import pentaplets as p
from lib.db.archea import quadruplets as q
from lib.db.archea import triplets as tr
from lib.db.archea import duplets as d
import report_generation as r
import lib.utils.merging as merging


def generate_plots(limit_to, reports_folder):

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
            r.write_to_xls(xls_file_name, kplet_sublist)


if __name__ == '__main__':

    reports_file_dir = os.path.join('reports/merged_across_kplets/top_500/')
    limit_to = 500
    print "Generating reports for limit_to:", limit_to
    generate_plots(limit_to, reports_file_dir)
    print 'Done'
    print "------------------------"
    print

    limit_to = 1000
    reports_file_dir = os.path.join('reports/merged_across_kplets/top_1000/')
    print "Generating reports for limit_to:", limit_to
    generate_plots(limit_to, reports_file_dir)
    print 'Done'
    print "------------------------"
    print

    limit_to = 1000000
    reports_file_dir = os.path.join('reports/merged_across_kplets/all/')
    print "Generating reports for limit_to:", limit_to
    generate_plots(limit_to, reports_file_dir)
    print 'Done'
    print "------------------------"
    print
