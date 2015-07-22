__author__ = 'hudaiber'

import sys

import xlsxwriter as x

from lib import tools as t
from lib import db

if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')
import global_variables as gv
import os


def write_to_xls(xls_file, clustered_ids, community, target_profiles, profile2def, src2org, gid2cdd):

    neighborhood_files = db.archea_kplet_ids2files(clustered_ids)
    neighborhood_files = [n[0] for n in neighborhood_files]

    neighborhoods = t.load_neighborhoods(os.path.join(gv.project_data_path,'Archea/genes_and_flanks/win_10/pty/'), neighborhood_files)

    org2src, src2files = db.archea_files2src_org_map(neighborhood_files)

    workbook = x.Workbook(xls_file)
    worksheet = workbook.add_worksheet()

    row_len = 6
    column_names = ['GI', 'From', 'To', 'Strand', 'CDD', 'Definition']

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
            nbr.extend_flanks(10, os.path.join(gv.pty_data_path, src2org[source],"%s.pty"%source), gid2cdd)

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

            data_raw = [gene.gid, gene.pFrom, gene.pTo, gene.strand, gene.cogid, cur_def]
            worksheet.write_row(cur_top_border, left_border, data_raw, data_format)
            worksheet.write_row(cur_top_border, left_border+row_len, [" "])
            cur_top_border += 1
        left_border += row_len + 1
    workbook.close()


def generate_reports_for_experiment(n_clusters, clustered_kplets=None, target_profiles=None, profile2def=None):

    if not target_profiles:
        target_profiles = t.target_profiles()
    if not profile2def:
        profile2def = t.map_profile2def()
    src2org = t.map_src2org()
    gid2cdd = t.map_gid2cdd()
    gid2arcog = t.map_gid2arcog()

    for k ,v in gid2cdd.items():
        if k not in gid2arcog:
            gid2arcog[k] = v

    if not clustered_kplets:
        clustered_kplets_file = os.path.join(gv.project_data_path, 'Archea/clustering/%d/clustered_neighborhoods.txt' % n_clusters)
        clustered_kplet_ids = [l.strip().split('\t')[1].split() for l in open(clustered_kplets_file).readlines()[1:]]

        clustered_profiles_file = os.path.join(gv.project_data_path, 'Archea/clustering/%d/clustered_profiles.txt' % n_clusters)
        clustered_profiles = [l.strip().split('\t')[1].split() for l in open(clustered_profiles_file).readlines()[1:]]

    reports_file_dir = os.path.join('reports', str(n_clusters))
    if not os.path.exists(reports_file_dir):
        os.mkdir(reports_file_dir)

    print 'Data ready. Starting report generation.'

    for i in range(n_clusters):
        print 'Cluster no:', i
        xls_file_name = os.path.join(reports_file_dir, "cl_no_%d.xls" % i)
        write_to_xls(xls_file_name, clustered_kplet_ids[i], clustered_profiles[i], target_profiles, profile2def, src2org, gid2arcog)
        sys.exit()


if __name__=='__main__':

    n_clusters = 10

    generate_reports_for_experiment(n_clusters)