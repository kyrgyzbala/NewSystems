__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import os
import global_variables as gv
from lib import tools
from lib import archea_db as adb
import pickle as p
import time


def kplet_gids(neighborhood, kplet_codes):

    out_gids = set()

    for term in kplet_codes:
        for g in neighborhood.genes:
            if term in g.cogid:
                out_gids.add(g.gid)
                break
    return out_gids


if __name__=='__main__':

    files_path = os.path.join(gv.project_data_path, 'Archea/genes_and_flanks/win_10/pty//')

    neighborhoods = tools.load_neighborhoods(files_path)

    # kplets = adb.get_multiple_kplets()
    # p.dump(kplets, open('multiple_kplets.p', 'w'))

    file_id2name = adb.map_file_id2name()
    kplets = p.load(open('multiple_kplets.p'))

    cnt = 0
    for kplet in kplets:

        kplet_id = kplet[0]
        kplet_file_ids = kplet[2].split(',')
        kplet_file_names = [file_id2name[id] for id in kplet_file_ids]
        kplet_file_names.sort()

        kplet_codes = adb.get_code_kplet(kplet_id)
        neighborhoods = tools.load_neighborhoods(files_path, kplet_file_names)
        n_files = [n.source_file.split('/')[-1] for n in neighborhoods]
        files_to_remove = []

        cur_gids = set([])
        for nbr in neighborhoods:
            if not cur_gids:
                cur_gids = kplet_gids(nbr, kplet_codes)
                continue

            tmp_gids = kplet_gids(nbr, kplet_codes)
            if tmp_gids == cur_gids:
                files_to_remove.append(nbr.source_file)







