#!/usr/bin/env python
import os
import sys

if sys.platform == 'darwin':
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/lib/BioPy/'))
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/SystemFiles/'))
elif sys.platform == 'linux2':
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/lib/BioPy/'))
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/SystemFiles/'))

import global_variables as gv
sys.path.append(gv.project_code_path)
import numpy as np
import pylab

def add_loci_column_clustering():

    reports_path = os.path.join(gv.project_data_path, 'cas4/reports/dot_union_10_0.50_2.00/')
    scheme_file = os.path.join(work_dir, 'clustering_scheme.tab')
    new_scheme_file = os.path.join(work_dir, 'clustering_scheme_loci.tab')

    all_files = []

    with open(scheme_file) as inf:
        with open(new_scheme_file, 'w') as outf:
            for l in inf:
                cluster_report_no = l.split()[1].split('.')[0]
                locus_ids = [desc.split()[-1] for desc in
                             open(os.path.join(reports_path, "%s.tab" % cluster_report_no)).readlines()
                             if desc.startswith("===")]
                locus_files = ["%s.pty" % id for id in locus_ids]

                all_files += locus_files

                outf.write(l.strip() + "\t" + ",".join(locus_files) + "\n")

    return set(all_files)


def add_loci_column_communities():

    reports_path = os.path.join(gv.project_data_path, 'cas4/unknowns/baiticity_limited/reports/')
    scheme_file = os.path.join(work_dir, 'community_scheme.tab')
    new_scheme_file = os.path.join(work_dir, 'community_scheme_loci.tab')

    all_files = ""

    with open(scheme_file) as inf:
        with open(new_scheme_file, 'w') as outf:
            for l in inf:
                cluster_report_no = l.split()[1].split('.')[0]
                locus_files = open(os.path.join(reports_path, "%s.tab" % cluster_report_no)).readline()
                all_files += ","+locus_files.rstrip()
                outf.write(l.strip() + "\t" + locus_files)

    return set(all_files.split(','))


def H_mle(P):
  idx = pylab.find(P>0)
  return -(P.flat[idx]*np.log2(P.flat[idx])).sum()


def prepare_matrix():

    community_scheme_file = os.path.join(work_dir, 'community_scheme_loci.tab')
    clustering_scheme_file = os.path.join(work_dir, 'clustering_scheme_loci.tab')

    locus2cluster_no, locus2community_no = {}, {}
    cl_size, comm_size = 0,0


    with open(community_scheme_file) as inf:
        for l in inf:
            comm_size += 1
            (cluster_no, _, loci) = l.strip().split()
            for locus_file in loci.split(','):
                locus2community_no[locus_file] = int(cluster_no)

    with open(clustering_scheme_file) as inf:
        for l in inf:
            cl_size += 1
            (cluster_no, _, loci) = l.strip().split()
            for locus_file in loci.split(','):
                locus2cluster_no[locus_file] = int(cluster_no)

    cross_mat = np.zeros((cl_size, comm_size))


    for locus_file in set(locus2cluster_no.keys()).intersection(set(locus2community_no.keys())):

        cross_mat[locus2cluster_no[locus_file]-1, locus2community_no[locus_file]-1] += 1

    fname = os.path.join(work_dir, 'cross_matrix.txt')

    np.savetxt(fname, cross_mat, delimiter="\t", fmt="%d")

    p_cl = np.sum(cross_mat, 0)
    p_cl /= np.sum(p_cl)

    p_comm = np.sum(cross_mat, 1)
    p_comm /= np.sum(p_comm)

    p_joint = cross_mat/np.sum(np.sum(cross_mat))

    MI = H_mle(p_cl) + H_mle(p_comm) - H_mle(p_joint)
    # print H_mle(p_cl)
    # print H_mle(p_comm)
    # print H_mle(p_joint)

    return MI


if __name__ == "__main__":

    work_dir = os.path.join(gv.project_data_path, 'cas4/clustering_vs_community')

    print prepare_matrix()

    # tmp placeholder

    order_file = os.path.join(gv.project_data_path, 'cas4/reports/dot_union_10_0.50_2.00/cas4_gi_tree_order.txt')
    new_order_file = os.path.join(gv.project_data_path, 'cas4/reports/dot_union_10_0.50_2.00/cas4_gi_tree_order2.txt')


    gi2type = t.load_compressed_pickle('/Users/hudaiber/Projects/NewSystems/data/cas4/pickle/cas4_gi2crispr_type.p.bz2')

    with open(order_file) as inf:
        with open(new_order_file, 'w') as outf:
            for l in inf:
                gi = l.strip()
                outf.write("%s\t%s\n" % (gi, gi2type[gi]))



