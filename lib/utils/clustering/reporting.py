import os
import sys
if sys.platform == 'darwin':
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/lib/BioPy/'))
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/SystemFiles/'))
elif sys.platform == 'linux2':
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/lib/BioPy/'))
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/SystemFiles/'))
import global_variables as gv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import shutil as sh
import xlsxwriter as x
from operator import itemgetter

import scores
import dendrogram

from lib.utils import tools as t
gnm2weight = t.map_genome2weight()
# file2org = {l.split()[0]:l.strip().split()[1] for l in open(os.path.join(gv.project_data_path,'cas1402/file2org.txt')).readlines()}
# file2crispr_type = {l.split('\t')[0]:l.strip().split('\t')[1].split(';') for l in open(os.path.join(gv.project_data_path,'cas1402/file2type.tab'))}

import lib.utils.reporting as r

from lib.db.generic import map_profiles_id2code_code2def
(_, profile_code2def) = map_profiles_id2code_code2def('cas')


def plot_block(block):

    _fname = block[0].strip()

    thresholds = []
    singles = []
    clusters = []
    mean_errors = []
    entropies = []

    for l in block[1:]:

        terms = l.strip().split('\t')

        thresholds.append(terms[0])
        singles.append(terms[1])
        clusters.append(terms[2])
        entropies.append(terms[3])

    thresholds = np.asarray(thresholds,dtype=np.float)
    singles = np.asarray(singles, dtype=np.int)
    clusters = np.asarray(clusters, dtype=np.int)
    entropies = 1000*np.asarray(entropies, dtype=np.float)

    plt.plot(thresholds, singles)
    plt.plot(thresholds, clusters)
    plt.plot(thresholds, entropies)

    _cnt = _fname.split('_')[1]
    _crispricity = _fname.split()[0].split('_')[2][:-4]
    _profiles = _fname.split()[1]

    plt.title("Occurrence:%s, CRISPRicity:%s, profiles: %s"%(_cnt, _crispricity, _profiles))
    plt.grid(True)
    plt.legend(['Singletons', 'Clusters', r'$ \left<\textit{I}\right> x(10^3) $'],loc='upper left')
    plt.xticks(thresholds, [str(t) for t in thresholds], rotation='vertical')
    plt.xlabel('Clustering thresholds')


def plot_results(data_file_name = 'results.txt', image_file_name='results.png'):

    plt.figure(figsize=(60,20))
    plt.rc('text', usetex=True)

    font = {'family': 'serif',
            'weight': 'bold',
            'size': 22}

    plt.rc('font', **font)

    block = []
    i = 1

    for l in open(data_file_name).readlines():
        if not block:
            block.append(l)
            continue

        if l.startswith('#'):
            plt.subplot(1,3,i)
            plt.tight_layout()
            plot_block(block)
            i += 1
            block = [l]
            continue

        block.append(l)

    plt.subplot(1,3,i)
    plot_block(block)

    plt.savefig(image_file_name)


def report_clustering_dot_product(loci, thresholds_pack, method, cluster_id2profiles, cluster_id2gene_names):

    thr_occ, thr_crisp, cluster_thresholds = thresholds_pack
    feature_definition_file = os.path.join(gv.project_data_path, 'cas4/profiles/profiles_%d_%.2f.tab' % (thr_occ, thr_crisp))

    M, feature_labels, feature_weights = scores.generate_dot_product_score_matrix(feature_definition_file, method, loci=loci)
    M += np.transpose(M)
    M = -1 * np.log(M)
    M[np.diag_indices_from(M)] = 0
    M[np.where(M==np.inf)] = 100

    reports_dir_base = os.path.join(gv.project_data_path, 'cas4/reports/')

    for threshold in cluster_thresholds:

        repors_dir = reports_dir_base + 'dot_%s_%d_%.2f_%.2f'%(method, thr_occ, thr_crisp, threshold)
        print "Thresholds:", thr_occ, thr_crisp, threshold
        print repors_dir
        if os.path.exists(repors_dir):
            sh.rmtree(repors_dir)
        os.mkdir(repors_dir)

        singles, cluster_packs, entropies = dendrogram.classify_by_scores_cas4(M, threshold, loci)

        _local_thresholds_pack = (thr_occ, thr_crisp, threshold)

        generate_cluster_reports_cas4(cluster_packs,
                                      loci,
                                      repors_dir,
                                      feature_labels,
                                      method,
                                      _local_thresholds_pack,
                                      cluster_id2profiles,
                                      cluster_id2gene_names)


def report_clustering_jw(loci, thresholds):

    M = scores.generate_jackard_score_matrix(loci)

    M += np.transpose(M)
    M = -1 * np.log(M)
    M[np.diag_indices_from(M)] = 0
    M[np.where(M==np.inf)] = 50

    reports_dir_base = os.path.join(gv.project_data_path, 'cas1402/reports/')

    for threshold in thresholds:

        repors_dir = reports_dir_base + 'jw_%.2f' % threshold
        print repors_dir
        if os.path.exists(repors_dir):
            sh.rmtree(repors_dir)
        os.mkdir(repors_dir)

        singles, cluster_packs, sum_errors, entropies = dendrogram.classify_by_scores(M, threshold, loci)

        # generate_cluster_reports(cluster_packs, loci, repors_dir, feature_labels, method, _local_thresholds_pack)
        generate_jw_cluster_reports(cluster_packs, loci, repors_dir, threshold)


def generate_cluster_reports(cluster_packs, loci, reports_dir, feature_labels, method, thresholds_pack):

    if not feature_labels:
        local_features = True
    else:
        local_features = False

    thr_occ, thr_crisp, cluster_threshold = thresholds_pack

    summary_file = os.path.join(reports_dir,
                                'summary_%s_%d_%.2f_%.2f.xls' % (method, thr_occ, thr_crisp, cluster_threshold))

    workbook = x.Workbook(summary_file)
    worksheet = workbook.add_worksheet()

    header_format = workbook.add_format()
    header_format.set_font_size(12)
    header_format.set_bold()
    header_format.set_align('center')
    worksheet.set_column(4,5,50)
    worksheet.write_row(0, 0, ["File name", "Weight", "Loci", "Entropy", "systems weight", "systems count"], header_format)

    print "Generating report files"
    ind = 0

    weights = np.zeros(len(cluster_packs))
    entropies = np.zeros(len(cluster_packs))

    for outer_i in range(len(cluster_packs)):

        (cluster, type2count, type2weight, entropy) = cluster_packs[outer_i]

        ind += 1
        cl_files = [os.path.basename(loci[i].file_name) for i in cluster]

        weight = sum([gnm2weight[file2org[file]] for file in cl_files])

        weights[outer_i] = weight
        entropies[outer_i] = entropy

        crispr_cas_types_count = " ; ".join([k+":"+str(v) for (k,v) in sorted(type2count.items(), key=itemgetter(1), reverse=True)])
        crispr_cas_types_weight = " ; ".join([k+":"+str(v) for (k,v) in sorted(type2weight.items(), key=itemgetter(1), reverse=True)])

        xls_file_name = os.path.join(reports_dir, '%d.xls' % ind)

        worksheet.write_row(ind+1, 0, ['%d.xls'%ind,
                                       weight,
                                       len(cl_files),
                                       entropy,
                                       crispr_cas_types_weight,
                                       crispr_cas_types_count,
                                       " "])

        cl_loci = sorted([loci[_i] for _i in cluster], key = lambda x: gnm2weight[x.organism], reverse=True)

        local_profile2weight = {}
        for locus in cl_loci:
            for gene in locus.genes:
                for profile in gene.cogid.split(','):
                    t.update_dictionary(local_profile2weight, profile, gnm2weight[locus.organism])

        global_profile2weight = t.map_global_cdd_profile_count()

        if local_features:
            feature_labels = [ k for k,v in local_profile2weight.items() if v/weight >= 0.5 ]

        params = {}

        params['xls_file_name']         = xls_file_name
        params['loci']                  = cl_loci
        params['weight']                = weight
        params['profile_code2def']      = profile_code2def
        params['gnm2weight']            = gnm2weight
        params['feature_labels']        = feature_labels
        params['file2crispr_type']      = file2crispr_type
        params['local_profile2weight']  = local_profile2weight
        params['global_profile2weight'] = global_profile2weight

        r.write_to_xls_generic_loci(params)

    worksheet.write_row(ind+3, 0, ['Average entropy'], header_format)
    worksheet.write_row(ind+3, 1, [np.sum(weights*entropies)/np.sum(weights)])

    worksheet.write_row(ind + 4, 0, ['Exp(Average entropy)'], header_format)
    worksheet.write_row(ind + 4, 1, [np.exp(np.sum(weights * entropies) / np.sum(weights))])


def generate_cluster_reports_cas4(cluster_packs,
                                  loci,
                                  reports_dir,
                                  feature_labels,
                                  method,
                                  thresholds_pack,
                                  cluster_id2profiles,
                                  cluster_id2gene_names):

    thr_occ, thr_crisp, cluster_threshold = thresholds_pack

    summary_file = os.path.join(reports_dir,
                                'summary_%s_%d_%.2f_%.2f.xlsx' % (method, thr_occ, thr_crisp, cluster_threshold))

    workbook = x.Workbook(summary_file)
    worksheet = workbook.add_worksheet()

    header_format = workbook.add_format()
    header_format.set_font_size(12)
    header_format.set_bold()
    header_format.set_align('center')

    worksheet.set_column(2,3,20)
    worksheet.set_column(4,4,50)

    worksheet.write_row(0, 0, ["File name", "Loci", "Effective size", "Entropy", "systems count"], header_format)

    print "Generating report files"
    ind = 0

    entropies = np.zeros(len(cluster_packs))

    for outer_i in range(len(cluster_packs)):

        (cluster, type2count, entropy) = cluster_packs[outer_i]

        ind += 1
        cl_files = [os.path.basename(loci[i].file_name) for i in cluster]

        entropies[outer_i] = entropy

        crispr_cas_types_count = " ; ".join([k+":"+str(v) for (k,v) in sorted(type2count.items(), key=itemgetter(1), reverse=True)])

        xls_file_name = os.path.join(reports_dir, '%d.xlsx' % ind)
        dendrogram_file_name = os.path.join(reports_dir, '%d.png' % ind)

        cl_loci = [loci[_i] for _i in cluster]

        M = scores.jackard_weighted_scores(cl_loci)

        threshold = dendrogram.plot_dendrogram_from_score_matrix(M, dendrogram_file_name)

        M = scores.jackard_weighted_scores(cl_loci)

        sub_singles, sub_cluster_packs, _ = dendrogram.classify_by_scores_cas4(M, threshold, cl_loci)

        params = {}

        params['xls_file_name']         = xls_file_name
        params['loci']                  = cl_loci
        params['clusters']              = sub_cluster_packs
        params['singles']               = sub_singles
        params['profile_code2def']      = profile_code2def
        params['feature_labels']        = feature_labels
        params['cluster_id2profiles']   = cluster_id2profiles
        params['cluster_id2gene_names'] = cluster_id2gene_names

        r.write_to_xls_generic_loci_cas4(params)

        worksheet.write_row(ind, 0, ['%d.xlsx' % ind,
                                     len(cl_files),
                                     len(sub_cluster_packs) + len(sub_singles),
                                     entropy,
                                     crispr_cas_types_count,
                                     " "])

    worksheet.write_row(ind+3, 0, ['Average entropy'], header_format)
    worksheet.write_row(ind+3, 1, [np.average(entropies)])

    worksheet.write_row(ind + 4, 0, ['Exp(Average entropy)'], header_format)
    worksheet.write_row(ind + 4, 1, [np.exp(np.average(entropies))])


def generate_jw_cluster_reports(cluster_packs, loci, reports_dir, threshold):

    # if not feature_labels:
    #     local_features = True
    # else:
    #     local_features = False

    # thr_occ, thr_crisp, cluster_threshold = thresholds_pack

    summary_file = os.path.join(reports_dir,
                                'summary_jw_%.2f.xls' % threshold)

    workbook = x.Workbook(summary_file)
    worksheet = workbook.add_worksheet()

    header_format = workbook.add_format()
    header_format.set_font_size(12)
    header_format.set_bold()
    header_format.set_align('center')
    worksheet.set_column(4,5,50)
    worksheet.write_row(0, 0, ["File name", "Weight", "Loci", "Entropy", "systems weight", "systems count"], header_format)

    print "Generating report files"
    ind = 0

    weights = np.zeros(len(cluster_packs))
    entropies = np.zeros(len(cluster_packs))

    for outer_i in range(len(cluster_packs)):

        (cluster, type2count, type2weight, entropy) = cluster_packs[outer_i]

        ind += 1
        cl_files = [os.path.basename(loci[i].file_name) for i in cluster]

        weight = sum([gnm2weight[file2org[file]] for file in cl_files])

        weights[outer_i] = weight
        entropies[outer_i] = entropy

        crispr_cas_types_count = " ; ".join([k+":"+str(v) for (k,v) in sorted(type2count.items(), key=itemgetter(1), reverse=True)])
        crispr_cas_types_weight = " ; ".join([k+":"+str(v) for (k,v) in sorted(type2weight.items(), key=itemgetter(1), reverse=True)])

        xls_file_name = os.path.join(reports_dir, '%d.xls' % ind)

        worksheet.write_row(ind+1, 0, ['%d.xls'%ind,
                                       weight,
                                       len(cl_files),
                                       entropy,
                                       crispr_cas_types_weight,
                                       crispr_cas_types_count,
                                       " "])

        cl_loci = sorted([loci[_i] for _i in cluster], key = lambda x: gnm2weight[x.organism], reverse=True)

        local_profile2weight = {}
        for locus in cl_loci:
            for gene in locus.genes:
                for profile in gene.cogid.split(','):
                    t.update_dictionary(local_profile2weight, profile, gnm2weight[locus.organism])

        global_profile2weight = t.map_global_cdd_profile_count()

        # if local_features:
        #     feature_labels = [ k for k,v in local_profile2weight.items() if v/weight >= 0.5 ]

        params = {}

        params['xls_file_name']         = xls_file_name
        params['loci']                  = cl_loci
        params['weight']                = weight
        params['profile_code2def']      = profile_code2def
        params['gnm2weight']            = gnm2weight
        # params['feature_labels']        = feature_labels
        params['feature_labels']        = []
        params['file2crispr_type']      = file2crispr_type
        params['local_profile2weight']  = local_profile2weight
        params['global_profile2weight'] = global_profile2weight

        r.write_to_xls_generic_loci(params)

    worksheet.write_row(ind+3, 0, ['Average entropy'], header_format)
    worksheet.write_row(ind+3, 1, [np.sum(weights*entropies)/np.sum(weights)])

    worksheet.write_row(ind + 4, 0, ['Exp(Average entropy)'], header_format)
    worksheet.write_row(ind + 4, 1, [np.exp(np.sum(weights * entropies) / np.sum(weights))])