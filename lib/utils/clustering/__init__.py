
import sys
import dm_tools as dt
import scipy.spatial.distance as ssd
import numpy as np


class Locus(object):

    def __init__(self, file_name, annotation_map=None, file_format='pty', annotation_column=None):

        self.file_name = file_name
        if file_format=='pty':
            _genes = dt.get_pty_file(file_name, annotation_map=annotation_map)
        else:
            _genes = dt.get_pty_file_generic(file_name, annotation_map=annotation_map, annotation_column=annotation_column)

        type_line = open(file_name).readline()

        if type_line.startswith('#') and 'type:' in type_line:
            self.crispr_type = type_line.split(':')[1].strip()
        else:
            self.crispr_type = None

        self.genes = _genes
        self.profiles = set(profile for g in _genes for profile in g.cogid.split() if profile != '')
        self.organism = _genes[0].organism
        self.source = _genes[0].src

        _forward = set()
        _reverse = set()

        for i in range(len(_genes)):
            _gene = _genes[i]
            for _cogid in _gene.cogid.split(','):
                _forward.update((_cogid,))
                if i == len(_genes)-1:
                    continue
                _next_gene = _genes[i+1]
                for _next_cogid in _next_gene.cogid.split(','):
                    _forward.update(("%s-%s" % (_cogid, _next_cogid),))

        _genes.sort(reverse=True)

        for i in range(len(_genes)):
            _gene = _genes[i]
            for _cogid in _gene.cogid.split(','):
                _reverse.update((_cogid,))
                if i == len(_genes)-1:
                    continue
                _next_gene = _genes[i+1]
                for _next_cogid in _next_gene.cogid.split(','):
                    _reverse.update(("%s-%s" % (_cogid, _next_cogid),))

        self.forward_set = _forward
        self.reverse_set = _reverse

        self.feature_weights = None
        self.feature_labels  = None


    @staticmethod
    def calculate(first, second):

        score_intersection = sum([0.5 if '-' in term else 1 for term in first.intersection(second)])
        score_union        = sum([0.5 if '-' in term else 1 for term in first.union(second)])

        return score_intersection / score_union


    def score(self, other):

        ff = self.calculate(self.forward_set, other.forward_set)
        fr = self.calculate(self.forward_set, other.reverse_set)
        rf = self.calculate(self.reverse_set, other.forward_set)
        rr = self.calculate(self.reverse_set, other.reverse_set)

        return max(ff, fr, rf, rr)


    def set_features(self, feature_labels, feature_weights):

        self.feature_labels = feature_labels
        self.feature_weights = feature_weights[:]

        for i in range(len(feature_labels)):
            if feature_labels[i] not in self.profiles:
                self.feature_weights[i]=0

        self.feature_weights = np.asarray(self.feature_weights, dtype=float)


    def cosine_distance(self, other):

        if self.feature_labels==None or self.feature_weights==None:
            print("Set feature weights AND feature labels for loci before invoking cosine_distance")
            sys.exit()

        # if self.feature_weights or other.feature_weights is all zeros
        if not np.any(self.feature_weights) or not np.any(other.feature_weights):
            return 1.0
        distance = ssd.cosine(self.feature_weights, other.feature_weights)
        if distance < 1e-8:
            distance = 0
        # distance = np.dot(self.feature_weights, other.feature_weights)
        return distance