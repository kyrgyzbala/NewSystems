__author__ = 'Sanjarbek Hudaiberdiev'

import os
import sys
import configparser
from collections import defaultdict

###############################################################
config_file = os.path.join(os.path.expanduser('~'), 'paths.cfg')
cfg = configparser.ConfigParser()
cfg.read(config_file)

code_path = cfg.get('NewSystems', 'code_path')
data_path = cfg.get('NewSystems', 'data_path')
sys.path.append(code_path)

###############################################################

import os
from lib.utils import BasicLocus, Locus

HHPRED_PROB_THR = 80
HHPRED_EVALUE_THR = 1e-3


class Hit(object):
    """docstring for Hit"""

    def __init__(self, line):
        parts = line.strip().split()

        self.profile = parts[1]
        self.prob = float(parts[2])
        self.evalue = float(parts[3])
        self.score = float(parts[5])

        q_coords = parts[8]
        self.q_from = int(q_coords.split('-')[0])
        self.q_to = int(q_coords.split('-')[1])
        t_coords = parts[9]
        if "(" in t_coords:
            t_coords = t_coords[:t_coords.index("(")]

        self.t_from = int(t_coords.split('-')[0])
        self.t_to = int(t_coords.split('-')[1])

    def __str__(self):
        return "%s\t%f\t%s\t%d\t%d" % (self.profile, self.prob, self.evalue, self.q_from, self.q_to)

    def overlaps(self, other):
        dist1 = other.q_from - self.q_to
        dist2 = self.q_from - other.q_to
        return True if dist1 * dist2 >= 0 else False


def hhsearch_parse(hhr_file, prob_thr=HHPRED_PROB_THR, eval_thr=HHPRED_EVALUE_THR):

    lines = open(hhr_file).readlines()[9:]

    ind = lines.index("\n")
    lines = lines[:ind]

    hits = [Hit(line) for line in lines]

    hits = [hit for hit in hits if hit.prob >= prob_thr and float(hit.evalue) <= eval_thr]

    if len(hits) > 1:

        picked_hits = [hits[0]]

        for i in range(1, len(hits)):

            if all([not hits[i].overlaps(_hit) for _hit in picked_hits]):
                picked_hits += [hits[i]]

        hits = picked_hits

    return hits
