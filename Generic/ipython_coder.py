import numpy as np
import matplotlib.pyplot as plt


fname = 'Clusters.descr'

id2gene = {}

for l in open(fname):
    parts = l.split('\t')
    id = parts[0]
    genes = parts[2]
    id2gene[id] = genes


baits, cas_hits, others = [], [], []

all_hits = open('SortedRatio.tsv').readlines()

for l in all_hits:

    parts = l.split()
    id = parts[0]

    genes = id2gene[id]

    if 'cas4' in genes:
        baits.append(l)
    elif 'cas' in genes:
        cas_hits.append(l)
    else:
        others.append(l)


with open('cas_hits.tsv', 'w') as fout:
    for l in cas_hits:
        id, in_loci, everywhere = l.strip().split('\t')
        try:
            icity = float(in_loci)/float(everywhere)
        except:
            continue
        fout.write("%s\t%s\t%s\t%f\n" % (id, in_loci, everywhere, icity))


with open('bait_hits.tsv', 'w') as fout:
    for l in baits:
        id, in_loci, everywhere = l.strip().split('\t')
        try:
            icity = float(in_loci)/float(everywhere)
        except:
            continue
        fout.write("%s\t%s\t%s\t%f\n" % (id, in_loci, everywhere, icity))


with open('other_hits.tsv', 'w') as fout:
    for l in others:
        id, in_loci, everywhere = l.strip().split('\t')
        try:
            icity = float(in_loci)/float(everywhere)
        except:
            continue
        fout.write("%s\t%s\t%s\t%f\n" % (id, in_loci, everywhere, icity))



# plt.figure(figsize=(20,10))

ax = plt.gca()

icity, in_loci = [], []

for l in open('other_hits.tsv'):
    parts = l.split()
    in_loci.append(int(parts[1]))
    icity.append(float(parts[3]))

icity = np.asarray(icity)
in_loci = np.asarray(in_loci)

plt.scatter(np.log10(in_loci), icity, label='others')
# ax.scatter(in_loci, icity, color='blue', label='others')
# ax.set_xscale('log')


icity, in_loci = [], []

for l in open('cas_related_hits.tsv'):
    parts = l.split()
    in_loci.append(int(parts[1]))
    icity.append(float(parts[3]))

icity = np.asarray(icity)
in_loci = np.asarray(in_loci)

# ax.scatter(in_loci, icity, color='green', label='cas (~cas4)')
plt.scatter(np.log10(in_loci), icity, color='green', label='cas (~cas4)')

icity, in_loci = [], []

for l in open('bait_hits.tsv'):
    parts = l.split()
    in_loci.append(int(parts[1]))
    icity.append(float(parts[3]))

icity = np.asarray(icity)
in_loci = np.asarray(in_loci)

# plt.scatter(in_loci, icity, color='red', label='cas4')
plt.scatter(np.log10(in_loci), icity, color='red', label='cas4')



plt.plot([0,3], [1.0, 1.0], color='black')
plt.plot([0,3], [0, 0], color='black')
plt.plot([0,3], [0.5, 0.5], color='black', linestyle='--')
plt.legend()
plt.xlim([0,3])

plt.ylabel("Occurrence in loci")
plt.xlabel("Cas4icity")
plt.title("Cas4icity plot")


# ax.set_xtickls([np.trunc(np.power(10, [0, 0.5, 1, 1.5, 2, 2.5, 3]))])
# ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter(lambda x: str(int(np.power(10,x)))))

locs, labels = plt.xticks()
plt.xticks(locs, map(lambda x: "%d" % np.power(10,x), locs))


plt.show()
