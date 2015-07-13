#!/usr/bin/env python

import os
import sys
sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
import global_variables as gv
import dm_tools
import time
import pickle

nbrhds_path = '/Users/hudaiber/Projects/NewSystems/data/Bacteria/genes_and_flanks/win_10/raw_nbr_files/'
inter_dist = 20


def build_src2gids_map(source_files):

    src_to_gids = {}

    for f in source_files:
        tmp_l = open(os.path.join(source_files, f)).readline()
        cur_gid = os.path.basename(f).split('_')[0]
        cur_src = tmp_l.split()[4]
        if src_to_gids.has_key(cur_src):
            src_to_gids[cur_src].append(cur_gid)
        else:
            src_to_gids[cur_src] = [cur_gid]

    return src_to_gids


def write_src2gids_file(src_to_gids, result_file):
    outf = open(result_file+'.txt', 'w')
    for k, v in src_to_gids.items():
        outf.write('%d\t%s\t%s\n' % (len(v), k, ' '.join(v)))


def write_merged_block(block, background_genes, fname, source_path):

    subject_files = ['%s_annot.pty'%background_genes[i].gid for i in block]
    subject_files = [os.path.join(source_path, f) for f in subject_files]
    lines = []
    for f in subject_files:
        lines += open(f).readlines()
    lines = set(lines)
    lines = sorted(lines)

    outf = open(fname, 'w')
    [outf.write(l) for l in lines]


def merge_neighborhoods(src_to_gid_map, src_to_org, dest_path, source_path):

    for src, gids in src_to_gid_map.items():

        org = src_to_org[src]
        subject_genes = dm_tools.gid_to_gene(os.path.join(gv.pty_genomes_path, org), gids)
        subject_genes.sort()

        background_genes = dm_tools.get_pty(os.path.join(gv.pty_genomes_path, org, '%s.pty' % src))
        background_genes.sort()
        background_genes_gids = [g.gid for g in background_genes]

        blocks = []
        indices = [background_genes_gids.index(g.gid) for g in subject_genes]
        indices.sort()

        cur_block = []
        for ind in indices:
            if not cur_block:
                cur_block.append(ind)
                continue
            diff = ind - cur_block[-1]
            assert(diff > 0)
            if diff < inter_dist:
                cur_block.append(ind)
            else:
                blocks.append(cur_block)
                cur_block = [ind]
        blocks.append(cur_block)

        cnt = 1
        for block in blocks:
            write_merged_block(block, background_genes, os.path.join(dest_path, '%s_%d.pty'%(src, cnt)), source_path)
            cnt += 1

        assert (sum([len(b) for b in blocks]) == len(indices))




if __name__=='__main__':

    # gid_list_file = sys.argv[1]
    # out_dest = sys.argv[2]
    # nbrhds_path = '/Users/hudaiber/Projects/NewSystems/data/Bacteria/test/genes_and_flanks/pty/'
    # result_file_prefix = 'src_to_gids_test_set'
    # build_src2gids_map(nbrhds_path, result_file_prefix)

    merge_neighborhoods('src_to_gids.txt', '../../../data/Bacteria/genes_and_flanks/win_10/merged/', '../../../data/Bacteria/genes_and_flanks/win_10/raw_nbr_files/')


