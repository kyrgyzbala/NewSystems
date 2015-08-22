__author__ = 'hudaiber'

import sys

import xlsxwriter as x

from lib.db.archea import db_tools
from lib.utils import tools as t

if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')
import global_variables as gv
import os


target_profiles = t.target_profiles()
profile2def = t.map_profile2def()
# src2org = t.map_src2org()
gid2arcog_cdd = t.map_gid2arcog_cdd()
# gid2arcog = t.map_gid2arcog()

neighborhood_files_path = os.path.join(gv.project_data_path, 'Archea/genes_and_flanks/win_10/pty/')


def write_to_xls(xls_file, kplet):

    kplet_cdd_codes = kplet[0]
    kplet_files = kplet[1]
    # kplet_files = kplet_files.split(',')

    _org2src, _src2files = db_tools.archea_org2src_src2files_map(kplet_files)

    workbook = x.Workbook(xls_file)
    worksheet = workbook.add_worksheet()

    row_len = 6
    column_names = ['GI', 'From', 'To', 'Strand', 'CDD', 'Definition']

    title_format = workbook.add_format()
    title_format.set_font_size(14)
    title_format.set_bold()
    title_format.set_align('left')

    header_format = workbook.add_format()
    header_format.set_font_size(12)
    header_format.set_bold()
    header_format.set_align('center')

    target_format = workbook.add_format()
    target_format.set_font_color("red")

    kplet_format = workbook.add_format()
    kplet_format.set_font_color("green")

    top_border = 0
    left_border = 0

    worksheet.merge_range(0, 0, 0, 10, 'k-plet: ' + ' '.join(kplet_cdd_codes), title_format)
    top_border += 1
    worksheet.merge_range(top_border, 0, top_border, 10, 'Organisms: ', title_format)
    top_border += 1

    for org in _org2src.keys():
        worksheet.merge_range(top_border, 2, top_border, 10, org, title_format)
        top_border += 1

    top_border += 1
    for org, srcs in _org2src.items():

        for src in srcs:
            _files = _src2files[src]
            neighborhoods = t.load_neighborhoods(neighborhood_files_path, _files)

            for nbr in neighborhoods:

                cur_top_border = top_border

                if not nbr.flank_extension:
                    nbr.extend_flanks(10, os.path.join(gv.pty_data_path, org, "%s.pty" % src), gid2arcog_cdd)

                worksheet.merge_range(cur_top_border, left_border, cur_top_border, left_border + row_len-1, "%s %s" % (org, src), header_format)
                cur_top_border += 1
                worksheet.write_row(cur_top_border, left_border, column_names, header_format)

                cur_top_border += 2

                for gene in nbr.genes:
                    cur_cogid = gene.cogid
                    if cur_cogid in target_profiles:
                        data_format = target_format
                    elif cur_cogid in kplet_cdd_codes:
                        data_format = kplet_format
                    else:
                        data_format = workbook.add_format()

                    if gene.tag == 'neighborhood':
                        data_format.set_bg_color('#c4bdbd')

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
                                elif c in kplet_cdd_codes:
                                    data_format = kplet_format

                    data_raw = [gene.gid, gene.pFrom, gene.pTo, gene.strand, gene.cogid, cur_def]
                    worksheet.write_row(cur_top_border, left_border, data_raw, data_format)
                    worksheet.write_row(cur_top_border, left_border+row_len, [" "])
                    cur_top_border += 1
                left_border += row_len + 1
    workbook.close()


if __name__=='__main__':


    # print 'Pentaplets'
    # kplets = db_p.get_report_kplets()
    # reports_file_dir = os.path.join('reports', '5')
    #
    # cnt = 0
    # for kplet in kplets:
    #
    #     xls_file_name = os.path.join(reports_file_dir, "%d.xls" % (cnt+1))
    #     write_to_xls_2(xls_file_name, kplet)
    #     print xls_file_name
    #     cnt += 1
    #
    #
    # print 'quadruplets'
    # from lib.db.archea import quadruplets as db
    # kplets = db.get_report_kplets()
    # reports_file_dir = os.path.join('reports', '4')
    #
    # cnt = 0
    # for kplet in kplets:
    #
    #     xls_file_name = os.path.join(reports_file_dir, "%d.xls" % (cnt+1))
    #     write_to_xls_2(xls_file_name, kplet)
    #     # print xls_file_name
    #     cnt += 1
    #
    # print 'triplets'
    # from lib.db.archea import triplets as db
    # kplets = db.get_report_kplets()
    # reports_file_dir = os.path.join('reports', '3')
    #
    # cnt = 0
    # for kplet in kplets:
    #
    #     xls_file_name = os.path.join(reports_file_dir, "%d.xls" % (cnt+1))
    #     write_to_xls_2(xls_file_name, kplet)
    #     # print xls_file_name
    #     cnt += 1

    print 'duplets'
    from lib.db.archea import duplets as db
    kplets = db.get_report_kplets()
    reports_file_dir = os.path.join('reports', '2')

    cnt = 0
    for kplet in kplets:

        xls_file_name = os.path.join(reports_file_dir, "%d.xls" % (cnt+1))
        write_to_xls_2(xls_file_name, kplet)
        # print xls_file_name
        cnt += 1
