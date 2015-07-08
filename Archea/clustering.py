__author__ = 'hudaiber'


import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/SystemFiles/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/SystemFiles/')
import global_variables as gv
import os
import numpy as np
from sklearn.cluster import KMeans
import pickle
import lib.classes as cl


def cluster_neighborhoods(n_clusters, feature_profiles, conserved_profiles):
    print "Generating data matrix for clustering"

    # n_clusters=10
    # feature_profiles = top_500_profiles

    feature_size = len(feature_profiles)
    data_matrix = np.zeros((len(conserved_profiles), feature_size))

    for i in range(len(conserved_profiles)):
        for j in range(len(feature_profiles)):
            if feature_profiles[j] in conserved_profiles[i]:
                data_matrix[i, j] = 1
    data_matrix *= 100
    n_jobs = n_clusters/10
    estimator = KMeans(n_clusters=n_clusters, n_jobs=n_jobs)
    print "Starting clustering job(s):"
    print "Input data:", data_matrix.shape
    print "No of clusters: %d, no of jobs: %d" % (n_clusters, n_jobs)
    predictions = estimator.fit_predict(data_matrix)

    estimator_file = os.path.join(gv.project_data_path, 'Archea/clustering/models_predictions/', 'clustering_estimator_%d.p' % n_clusters)
    predictions_file = os.path.join(gv.project_data_path, 'Archea/clustering/models_predictions/', 'clustering_predictions_%d.p' % n_clusters)
    print "Clustering finished. Writing the results to files:"
    print "     ", estimator_file
    print "     ", predictions_file
    pickle.dump(estimator, open(estimator_file, 'w'))
    pickle.dump(predictions, open(predictions_file, 'w'))


def clustering_postprocess(n_clusters, conserved_profile_nbrhds):

    predictions_file = os.path.join(gv.project_data_path, 'Archea/clustering/models_predictions/clustering_predictions_%d.p' % n_clusters)
    predictions = pickle.load(open(predictions_file))

    all_cluster_profiles = []

    for i in range(n_clusters):
        indcs = np.where(predictions == i)
        cluster_mapped = conserved_profile_nbrhds[indcs]
        cluster_profiles = set()

        for nbr in cluster_mapped:
            cluster_profiles = cluster_profiles | set(nbr)
        cluster_profiles = sorted(list(cluster_profiles))
        all_cluster_profiles.append(cluster_profiles)

    cluster_path = os.path.join(gv.project_data_path, 'Archea/clustering', str(n_clusters))
    if not os.path.exists(cluster_path):
        os.mkdir(cluster_path)

    cluster_profiles_file = os.path.join(cluster_path, "clustered_profiles.txt")
    with open(cluster_profiles_file, "w") as f:
        for cl in all_cluster_profiles:
            f.write("\t".join(cl)+"\n")

    return all_cluster_profiles


if __name__=='__main__':

    profile_weights = open('files/profile_weights.tab').readlines()
    top_500_profiles = np.asarray([l.strip().split()[1] for l in profile_weights[:500]])

    conserved_profiles_file = os.path.join(gv.project_data_path, 'Archea/genes_and_flanks/win_10/kplets/pentaplets.csv')

    conserved_profiles = np.asanyarray([l.split(',')[1:6] for l in open(conserved_profiles_file).readlines()[1:]])
    # conserved_profiles_map = {l.split(',')[1:5]: float(l.split()[1]) for l in open(conserved_profiles_file).readlines()[1:]}

    # n_clusters = int(sys.argv[1])
    n_clusters = 10
    # cluster_neighborhoods(n_clusters, top_500_profiles, conserved_profiles)

    cluster_profiles = clustering_postprocess(n_clusters, conserved_profiles)