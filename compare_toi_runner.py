import sys
import pickle
import subprocess
import argparse
import ast
import pathlib
import math

from natsort import natsorted, ns

parser = argparse.ArgumentParser()
parser.add_argument("-i,--input", dest="all_files", type=pathlib.Path, nargs="+")
parser.add_argument("n_jobs", type=int)
args = parser.parse_args()

job_name = "compare_toi_"

log = "log"
pathlib.Path(log).mkdir(exist_ok=True)

all_files = natsorted(args.all_files)

files_split = [[] for i in range(args.n_jobs)]
for i, f in enumerate(all_files):
    files_split[i % args.n_jobs].append(f)

for i, files in enumerate(files_split):
    sbatch_args = [
        "sbatch", "-J", f"{job_name}{i}",
        "-o", f"{log}/{i}.out", "-e", f"{log}/{i}.err",
        "compare_toi_job.sh",  " ".join(str(f.resolve()) for f in files)
    ]

    if len(files) > 0:
        subprocess.run(sbatch_args)
