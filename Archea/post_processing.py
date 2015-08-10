#!/sw/bin/python2.7
__author__ = 'Sanjarbek Hudaiberdiev'

import os
import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import global_variables as gv
from lib import classes as cl
from lib import tools as t
import lib.db
from lib.db.archea import pentaplets as p
from lib.db.archea import quadruplets as q
from lib.db.archea import triplets as tr
from lib.db.archea import duplets as d
from lib.db.archea import db_tools
import report_generation as r


if __name__=='__main__':

    # id2cdd, cdd2id, cdd2def = lib.db.map_id2cdd_cdd2id_cdd2def()

    summary = p.get_report_kplets(limit_to=100000)
    print 'Total kplet summaries:', len(summary)


    merged_kplets = []
    merged_out = [0 for i in range(len(summary))]

    for i in range(len(summary)):
        if merged_out[i] == 1:
            continue

        cur_merged_list = [i]
        merged_out[i] = 1

        pivot = set(summary[i][1])

        for j in range(i, len(summary)):
            if merged_out[j] == 1:
                continue

            if len(pivot.intersection(summary[j][1])) >= len(pivot)/2:
                cur_merged_list.append(j)
                merged_out[j] = 1

        merged_kplets.append(cur_merged_list)

    cnt = 1
    reports_file_dir = os.path.join('reports', '5')

    for merged_list in merged_kplets:
        kplet_codes = []
        kplet_files = []
        for i in merged_list:
            kplet_codes += list(summary[i][1])
            kplet_files += summary[i][4].split(',')
        kplet_codes = set(kplet_codes)
        kplet_files = set(kplet_files)

        xls_file_name = os.path.join(reports_file_dir, "%d.xls" % cnt)
        r.write_to_xls(xls_file_name, [kplet_codes, kplet_files])
        cnt += 1

    # print
    # for merged_list in merged_kplets:
    #     print [summary[i][0] for i in merged_list]