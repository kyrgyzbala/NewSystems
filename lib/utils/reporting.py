__author__ = 'hudaiber'

import sys
import xlsxwriter as x

if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import global_variables as gv
sys.path.append(gv.project_code_path)

from lib.utils.classes import NeighborhoodFileSummary, Neighborhood
import os


def write_to_xls(params):

    xls_file = params['xls_file_name']
    src2org = params['src2org']
    file_summaries = params['file_summaries']
    community = params['community']
    target_profiles = params['target_profiles']
    profile2def = params['profile2def']
    gid2arcog_cdd = params['gid2arcog_cdd']

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

    target_format_neighborhood = workbook.add_format()
    target_format_neighborhood.set_font_color("red")
    target_format_neighborhood.set_bg_color("#c4bdbd")

    kplet_format = workbook.add_format()
    kplet_format.set_font_color("green")

    kplet_format_neighborhood = workbook.add_format()
    kplet_format_neighborhood.set_font_color("green")
    kplet_format_neighborhood.set_bg_color("#c4bdbd")

    top_border = 0
    left_border = 0

    worksheet.merge_range(0, 0, 0, 10, 'Community: ' + ' '.join(community), title_format)
    top_border += 1

    organisms = sorted(src2org.values())
    worksheet.merge_range(top_border, 0, top_border, 10, 'Organisms: %d'%len(organisms), title_format)
    top_border += 1

    worksheet.merge_range(top_border, 0, top_border, 10, ' '.join(organisms))
    top_border += 2


    for file_summary in file_summaries:

        cur_kplets = file_summary.kplets
        nbr = file_summary.neighborhood

        if not nbr.flank_extension:
            nbr.extend_flanks(10, os.path.join(gv.pty_data_path, file_summary.org, "%s.pty" % file_summary.src), gid2arcog_cdd)

        cur_top_border = top_border
        worksheet.merge_range(cur_top_border, left_border, cur_top_border, left_border + row_len-1, "%s %s" % (file_summary.org, file_summary.src), header_format)
        cur_top_border += 1
        worksheet.write_row(cur_top_border, left_border, column_names, header_format)
        cur_top_border += 2

        cur_top_border += 31 - len(nbr.genes)

        for gene in nbr.genes:
            cur_cogid = gene.cogid
            if cur_cogid in target_profiles:
                data_format = target_format_neighborhood if gene.tag == 'neighborhood' else target_format
            elif cur_cogid in community:
                data_format = kplet_format_neighborhood if gene.tag == 'neighborhood' else kplet_format
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
                            data_format = target_format_neighborhood if gene.tag == 'neighborhood' else target_format
                            break
                        if c in community:
                            data_format = kplet_format_neighborhood if gene.tag == 'neighborhood' else kplet_format
                            break
            data_raw = [gene.gid, gene.pFrom, gene.pTo, gene.strand, gene.cogid, cur_def]
            worksheet.write_row(cur_top_border, left_border, data_raw, data_format)
            worksheet.write_row(cur_top_border, left_border+row_len, [" "])
            worksheet.set_column(left_border+row_len-1,left_border+row_len-1,30)
            cur_top_border += 1
        cur_top_border += 2
        worksheet.merge_range(cur_top_border, left_border, cur_top_border, left_border + row_len-1, "Kplets:")
        cur_top_border += 1

        worksheet.write_row(cur_top_border, left_border, ["Id", "k", "Weight", "Count"])
        worksheet.merge_range(cur_top_border,left_border+4,cur_top_border,left_border+5, "Codes")
        cur_top_border += 1
        worksheet.write_row(cur_top_border, left_border, ["Total", "", file_summary.weight, file_summary.count])
        cur_top_border += 1

        for kplet in sorted(cur_kplets, reverse=True):
            worksheet.write_row(cur_top_border, left_border, [kplet.id, kplet.k, kplet.weight, kplet.count])
            worksheet.merge_range(cur_top_border,left_border+4,cur_top_border,left_border+5, " ".join(kplet.codes))
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
