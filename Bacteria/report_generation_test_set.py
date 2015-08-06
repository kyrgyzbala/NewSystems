__author__ = 'hudaiber'

import xlsxwriter as x
from lib_old import tools as t
import pickle
import sys
if sys.platform == 'darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform == 'linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')
import global_variables as gv
import os


def write_to_xls(xls_file, neighborhoods, community, target_profiles, profile2def, src2org, gid2cdd):

    workbook = x.Workbook(xls_file)
    worksheet = workbook.add_worksheet()

    row_len = 5
    column_names = ['From', 'To', 'Strand', 'CDD', 'Definition']

    title_format = workbook.add_format()
    title_format.set_font_size(14)
    title_format.set_bold()
    title_format.set_align('center')

    header_format = workbook.add_format()
    header_format.set_font_size(12)
    header_format.set_bold()
    header_format.set_align('center')

    target_format = workbook.add_format()
    target_format.set_font_color("red")

    comm_format = workbook.add_format()
    comm_format.set_font_color("green")

    top_border = 0
    left_border = 0

    worksheet.merge_range(0, 0, 0, 10, 'Community: ' + ' '.join(community), title_format)
    top_border += 1
    tmp_cnt = 1
    for nbr in neighborhoods:
        tmp_cnt += 1
        cur_top_border = top_border

        source = nbr.genes[0].src
        if not nbr.flank_extension:
            nbr.extend_flanks(10, os.path.join(gv.pty_data_path,src2org[source],"%s.pty"%source), gid2cdd)

        orgs = set(g.organism for g in nbr.genes)
        if 'genomes' in orgs:
            orgs.remove('genomes')
        organism = orgs.pop()

        worksheet.merge_range(cur_top_border, left_border, cur_top_border, left_border + row_len-1, "%s %s"%(organism, source), header_format)
        cur_top_border += 1
        worksheet.write_row(cur_top_border, left_border, column_names, header_format)

        cur_top_border += 2

        for gene in nbr.genes:
            cur_cogid = gene.cogid
            data_format = None
            if cur_cogid in target_profiles:
                data_format = target_format
            elif cur_cogid in community:
                data_format = comm_format

            if cur_cogid in ["", "-", None]:
                cur_def = ""
            else:
                cur_cogid = cur_cogid.split()
                if len(cur_cogid) > 0:
                    cur_def = []
                    for k in cur_cogid:
                        if k in profile2def:
                            cur_def.append(profile2def[k])
                        else:
                            cur_def.append("")
                    cur_def = " | ".join(cur_def)

                    for c in cur_cogid:
                        if c in target_profiles:
                            data_format = target_format

            data_raw = [gene.pFrom, gene.pTo, gene.strand, gene.cogid, cur_def]
            worksheet.write_row(cur_top_border, left_border, data_raw, data_format)
            worksheet.write_row(cur_top_border, left_border+row_len, [" "])
            cur_top_border += 1

        left_border += row_len + 1

    workbook.close()


def generate_reports_for_experiment(n_clusters, root_path, reports_path, summary_file):

    target_profiles = [l.strip() for l in open('/Users/hudaiber/Projects/NewSystems/data/Bacteria/test/test_profiles.txt').readlines()]
    profile2def = t.map_profile2def()
    summary = open(summary_file).readlines()
    src2org = t.map_src2org()
    gid2cdd = t.map_gid2cdd()

    print 'Data ready. Starting report generation.'

    for i in range(n_clusters):
        print 'Cluster no:', i
        cl_path = os.path.join(root_path, str(i+1))
        cl_neighborhoods = t.load_neighborhoods(cl_path)
        cl_community = summary[i*3+1].split()[1:]
        # print i, len(cl_community), len(summary[i*3+2].split()[1:]), summary[i*3]
        xls_file = os.path.join(reports_path, "cl_no_%d.xls" % (i+1))
        write_to_xls(xls_file, cl_neighborhoods, cl_community, target_profiles, profile2def, src2org, gid2cdd)


if __name__ == '__main__':

    neighborhoods_path_root = '/Users/hudaiber/Projects/NewSystems/data/Bacteria/test/clustering/10/'
    reports_path = '/Users/hudaiber/Projects/NewSystems/data/Bacteria/test/reports'
    clustering_summary_file = '/Users/hudaiber/Projects/NewSystems/data/Bacteria/test/clustering/cluster_profiles_cutoff_0.000000.txt'
    n_clusters = 10

    generate_reports_for_experiment(n_clusters, neighborhoods_path_root, reports_path, clustering_summary_file)