__author__ = 'hudaiber'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import global_variables as gv
sys.path.append(gv.project_code_path)
import lib.utils.tools as t
import csv
import os
import gzip
import bz2


if __name__=='__main__':

    pickle_file = sys.argv[1]
    csv_file = sys.argv[2]
    compression = sys.argv[3]

    # pickle_file = os.path.join(gv.project_code_path, 'scripts/', 'duplets_seed.p.bz2')
    # csv_file = os.path.join(gv.project_code_path, 'scripts/', 'duplets_seed.csv')
    # compression = True

    print "Loading objects from file:", pickle_file
    objects = t.load_compressed_pickle(pickle_file)
    
    print "Writing into CSV file:", csv_file
    if compression=='True':
        # fout = bz2.BZ2File(csv_file, "w")
        fout = gzip.open(csv_file,"w")
    else:
        fout = open(csv_file, "w")

    csv_writer = csv.writer(fout)
    csv_writer.writerow(('Id', 'K', 'Count', 'Codes', 'Files'))
    for o in objects:
        row = []
        row += [o.id, o.k, o.count,]
        row += [' '.join(list(o.codes)), ' '.join(o.files)]
        csv_writer.writerow(row)

    print "Done!"
