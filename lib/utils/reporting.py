__author__ = 'hudaiber'

import sys
import xlsxwriter as x
from operator import itemgetter

if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')

import global_variables as gv
sys.path.append(gv.project_code_path)

import os
from lib.utils import tools


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


def write_to_xls(params):

    xls_file           = params['xls_file_name']
    src2org            = params['src2org']
    file_summaries     = params['file_summaries']
    community          = params['community']
    target_profiles    = params['target_profiles']
    profile2def        = params['profile2def']
    gid2arcog_cdd      = params['gid2arcog_cdd']
    class2counts       = params['class2counts']
    class2profiles     = params['class2profiles']
    class2counts_flank = params['class2counts_flank']
    # profile2counts     = params['profile2counts']

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

    organisms = sorted(set(src2org.values()))
    _org2weight = tools.map_genome2weight()
    _total_weight = sum(_org2weight[file_summary.org] for file_summary in file_summaries)
    worksheet.merge_range(top_border, 0, top_border, 10, 'Organisms: %d,  Total weight: %f'%\
                          (len(organisms), _total_weight), title_format)
    top_border += 1

    worksheet.merge_range(top_border, 0, top_border, 10, ' '.join(organisms))
    top_border += 2

    # Writing the class distribution. The lestmost columns
    cur_top_border = top_border
    worksheet.write_row(cur_top_border, left_border, ['Weight','Class definition'], header_format)
    worksheet.set_column(left_border+1, left_border+1, 30)
    cur_top_border += 1
    worksheet.write_row(cur_top_border, left_border+1, ['Neighborhood'], header_format)
    cur_top_border += 2

    for (class_name, occurence) in sorted(class2counts.items(), key=itemgetter(1), reverse=True):
        worksheet.write_row(cur_top_border, left_border, [occurence, class_name])
        cur_top_border += 1

    cur_top_border += 2
    worksheet.write_row(cur_top_border, left_border+1, ['Neighborhood+flanks'], header_format)
    cur_top_border += 2

    for (class_name, occurence) in sorted(class2counts_flank.items(), key=itemgetter(1), reverse=True):
        worksheet.write_row(cur_top_border, left_border, [occurence, class_name])
        cur_top_border += 1

    # cur_top_border += 2
    # worksheet.write_row(cur_top_border, left_border, ['Code', 'Weight', 'Definition'], header_format)
    # cur_top_border += 2
    #
    # for (k, v) in sorted(profile2counts.items(), key= itemgetter(1), reverse=True):
    #     worksheet.write_row(cur_top_border, 0, [k, v, profile2def[k] if k in profile2def else '-'])
    #     cur_top_border += 1

    left_border = 5
    # Starting to write the data file-wise.
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
            worksheet.set_column(left_border+row_len-1, left_border+row_len-1, 30)
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

    worksheet_2 = workbook.add_worksheet()

    top_border = 4
    worksheet_2.write_row(top_border, 0, ['Class','','Member arCOGS,CDD'], header_format)
    top_border += 2
    for (class_name, occurence) in sorted(class2counts.items(), key=itemgetter(1), reverse=True):

        profiles = class2profiles[class_name]
        profile_definitions = [profile2def[profile] for profile in profiles if profile in profile2def]

        worksheet_2.write_row(top_border, 0, [class_name, ' ']+profiles)
        top_border += 1
        worksheet_2.write_row(top_border, 0, [' ', ' ']+profile_definitions+[' '])
        top_border += 2
    workbook.close()



def write_flanking_count_xls(params):

    xls_file = params['xls_file_name']
    flank_counts = params['flank_counts']
    profile2def = params['profile2def']
    title_string = params['title']
    target_profiles = params['target_profiles']

    workbook = x.Workbook(xls_file)
    worksheet = workbook.add_worksheet()

    title_format = workbook.add_format()
    title_format.set_font_size(14)
    title_format.set_bold()
    title_format.set_align('left')

    top_border = 0

    worksheet.merge_range(0, 0, 0, 10, 'Flanking genes distribution for: '+title_string, title_format)
    top_border += 1

    worksheet.write_row(top_border, 0, ["Type","Code", "Weight", "Description"], title_format)
    top_border += 1

    for (k, v) in sorted(flank_counts.items(), key= itemgetter(1), reverse=True):
        _type = "seed" if k in target_profiles else "not-seed"
        worksheet.write_row(top_border, 0, [_type, k, v, profile2def[k] if k in profile2def else '-'])
        top_border += 1

    workbook.close()


def write_to_xls_example(params):

    xls_file        = params['xls_file_name']
    src2org         = params['src2org']
    file_summaries  = params['file_summaries']
    target_profiles = params['target_profiles']
    profile2def     = params['profile2def']
    gid2arcog_cdd   = params['gid2arcog_cdd']

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

    # worksheet.merge_range(0, 0, 0, 10, 'Community: ' + ' '.join(community), title_format)
    top_border += 1

    organisms = sorted(set(src2org.values()))
    _org2weight = tools.map_genome2weight()
    _total_weight = sum(_org2weight[file_summary.org] for file_summary in file_summaries)
    worksheet.merge_range(top_border, 0, top_border, 10, 'Organisms: %d,  Total weight: %f'%\
                          (len(organisms), _total_weight), title_format)
    top_border += 1

    worksheet.merge_range(top_border, 0, top_border, 10, ' '.join(organisms))
    top_border += 2

    # Starting to write the data file-wise.
    for file_summary in file_summaries:

        cur_kplets = file_summary.kplets
        nbr = file_summary.neighborhood

        community = set()
        for kplet in cur_kplets:
            community.update(kplet.codes)

        if not nbr.flank_extension:
            nbr.extend_flanks(10, os.path.join(gv.pty_data_path, file_summary.org, "%s.pty" % file_summary.src), gid2arcog_cdd)

        cur_top_border = top_border
        worksheet.merge_range(cur_top_border, left_border, cur_top_border, left_border + row_len-1, "%s %s %f" % (file_summary.org, file_summary.src, file_summary.self_weight), header_format)
        cur_top_border += 1
        worksheet.write_row(cur_top_border, left_border, column_names, header_format)
        cur_top_border += 2

        if nbr.genes[0].tag == 'neighborhood':
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
            worksheet.set_column(left_border+row_len-1, left_border+row_len-1, 30)
            cur_top_border += 1
        cur_top_border = 41
        worksheet.merge_range(cur_top_border, left_border, cur_top_border, left_border + row_len-1, "Kplets:")
        cur_top_border += 1

        worksheet.write_row(cur_top_border, left_border, ["Id", "k", "Weight", "Count"])
        worksheet.merge_range(cur_top_border,left_border+4,cur_top_border,left_border+5, "Codes")
        cur_top_border += 1
        worksheet.write_row(cur_top_border, left_border, ["Total", "", file_summary.kplets_weight, file_summary.count])
        cur_top_border += 1

        for kplet in sorted(cur_kplets, reverse=True):
            worksheet.write_row(cur_top_border, left_border, [kplet.id, kplet.k, kplet.weight, kplet.count])
            worksheet.merge_range(cur_top_border,left_border+4,cur_top_border,left_border+5, " ".join(kplet.codes))
            cur_top_border += 1
        left_border += row_len + 1