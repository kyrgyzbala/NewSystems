__author__ = 'hudaiber'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import global_variables as gv
import os


def extract_loci_into_files():

    source_files_path = os.path.join(gv.data_path, 'from_Sergey/dataset_crispr/')
    source_file = os.path.join(source_files_path, 'AnnWithClusters_ID.ann')

    out_path = os.path.join(gv.project_data_path, 'CRISPR/datasets/crispr/wgs/')
    all_blocks = list()

    with open(source_file) as inf:
        block = []
        l = inf.readline()
        while l:
            if l.startswith("==="):
                if not block:
                    block.append(l)
                else:
                    all_blocks.append(block)
                    block = [l]
            else:
                block.append(l)
            l = inf.readline()
        all_blocks.append(block)

    for block in all_blocks:
        fname = "wgs_2_%s.pty" % block[0].split('\t')[-1].split()[1]
        with open(os.path.join(out_path, fname), 'w') as outf:
            for l in block[1:]:
                outf.write(l)

    return all_blocks


def add_id_to_crispr_loci():

    id_counter = 1

    files_path = os.path.join(gv.data_path, 'from_Sergey/dataset_crispr/')

    with open(os.path.join(files_path, 'AnnWithClusters.ann')) as inf:

        with open(os.path.join(files_path,'AnnWithClusters_ID.ann'),'w') as outf:
            l = inf.readline()
            while l:
                if l.startswith("==="):
                    l = l.rstrip() + '\tID: %d\n' % id_counter
                    id_counter += 1
                outf.write(l)
                l = inf.readline()


if __name__=='__main__':

    add_id_to_crispr_loci()
    blocks = extract_loci_into_files()
