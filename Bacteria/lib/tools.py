__author__ = 'Sanjarbek Hudaiberdiev'

import sys
if sys.platform=='darwin':
    sys.path.append('/Users/hudaiber/Projects/lib/BioPy/')
elif sys.platform=='linux2':
    sys.path.append('/home/hudaiber/Projects/lib/BioPy/')
from BioClasses import Gene

def pty2genes_file2list(pty_file):
    gene_list = []

    for l in open(pty_file):
        terms = l.strip().split('\t')

        gid = terms[0]
        coordinates = terms[1]
        strand = terms[2]
        genome = terms[3]
        chromosome = terms[4]
        annotations = terms[5] if len(terms) > 5 else ""

        pfrom, pto = coordinates.split('..')
        curGene = Gene(source=chromosome, gid=gid, pFrom=pfrom, pTo=pto, organism=genome, strand=strand, cogid=annotations)
        gene_list.append(curGene)

    return gene_list

