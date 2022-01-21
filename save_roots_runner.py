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
parser.add_argument("edge_edge", type=ast.literal_eval)
parser.add_argument("n_jobs", type=int)
args = parser.parse_args()

job_name = "ee" if args.edge_edge else "vf"

log = "log_ee" if args.edge_edge else "log_vf"
pathlib.Path(log).mkdir(exist_ok=True)

all_files = natsorted(args.all_files)

delta = max(int(round(len(all_files) / args.n_jobs)), 1)

prev_end = 0
for i in range(args.n_jobs):
    end = prev_end + delta if i < args.n_jobs - 1 else len(all_files)
    files = all_files[prev_end:end]
    prev_end = end

    sbatch_args = [
        "sbatch", "-J", f"{job_name}{i}",
        "-o", f"{log}/{i}.out", "-e", f"{log}/{i}.err",
        "save_roots_job.sh", str(args.edge_edge), 
        " ".join(str(f.resolve()) for f in files)
    ]

    # print(" ".join(sbatch_args))

    subprocess.run(sbatch_args)
