from utils import get_samples_in_dir
import sys
import os

"""Usage: merge_fastqs.py fastq_dir num_name_elements fq_extension out_dir"""
"""Read file ids (first num_name_elements elements in file basename) and merge fastqs with same direction and id"""

fastq_dir = sys.argv[1]
num_name_elements = int(sys.argv[2])
fq_extension = sys.argv[3]
out_dir = sys.argv[4]

fqs = get_samples_in_dir(dir=fastq_dir, extensions=(fq_extension))
ids = list(set(['_'.join(os.path.basename(fq).split('_')[:num_name_elements]) for fq in fqs]))
groups = []
for id in ids:
    subset = [f for f in fqs if id in f]
    if len(subset)> 2:
        groups.append(id)
    else:
        os.system(f'mv {fastq_dir}{id}* {out_dir}{id}')
for id in groups:
    for direction,substitute_direction in {'_R1_001':'_1', '_R2_001':'_2'}.items():
        os.system(f'cat {fastq_dir}{id}*{direction}{fq_extension} > {out_dir}{id}{substitute_direction}{fq_extension}')