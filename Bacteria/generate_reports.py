__author__ = 'hudaiber'


import sys
import numpy as np
from sklearn.cluster import KMeans
import pickle
from multiprocessing import Process

n_clusters = int(sys.argv[1])

def cluster_neighborhoods(n_clusters):
    print "Starting Kmeans with cluster number: %d" % n_clusters
    data_matrix = np.zeros((len(conserved_profiles), 500))

    for i in range(len(conserved_profiles)):
        for j in range(500):
            if top_500_profiles[j] in conserved_profiles[i]:
                data_matrix[i, j] = 1

    estimator = KMeans(n_clusters=n_clusters)
    predictions = estimator.fit_predict(data_matrix)
    pickle.dump(open('clustering_estimator_%d.p' % n_clusters, 'w'), estimator)
    pickle.dump(open('clustering_predictions_%d.p' % n_clusters, 'w'), predictions)


if __name__=='__main__':

    profile_weights = pickle.load(open('profile_weights.p'))
    top_500_profiles = [k for k,v in profile_weights[:500]]
    conserved_profiles = [l.split()[0].split('-') for l in open('500_7.tab').readlines()[1:]]

    for cl in [10,20,30,40,50,60,70,80,90,10]:
        p = Process(target=cluster_neighborhoods, args=(cl,))
        p.start()
        p.join()
    