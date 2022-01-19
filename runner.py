import sys
import pickle
import subprocess
import argparse
import ast

parser = argparse.ArgumentParser()
parser.add_argument("edge_edge", type=ast.literal_eval)
parser.add_argument("n_jobs", type=int)
parser.add_argument("start", type=int, default=0, nargs='?')
parser.add_argument("n_files", type=int, default=-1, nargs='?')
args = parser.parse_args()

job_name = "" if args.edge_edge else "vf"

log = "log" if args.edge_edge else "log_vf"

file = "ee.pkl" if args.edge_edge else "vf.pkl"

with open(file, 'rb') as f:
    all_files = pickle.load(f)

if args.n_files < 0:
    args.n_files = len(all_files)

delta = args.n_files // args.n_jobs

for i in range(args.start, args.n_files, delta):
    args = [
        "sbatch", "-J", f"{job_name}{i}",
        "-o", f"{log}/{i}.out",
        "-e", f"{log}/{i}.err",
        "job.sh",
        file, str(i), str(i+delta), str(args.edge_edge)
    ]

    # print(" ".join(args))

    subprocess.run(args)
