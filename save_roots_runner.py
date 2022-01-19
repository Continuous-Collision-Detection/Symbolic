import sys
import pickle
import subprocess
import argparse
import ast
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("queries_root", type=pathlib.Path)
parser.add_argument("edge_edge", type=ast.literal_eval)
parser.add_argument("n_jobs", type=int)
# parser.add_argument("start", type=int, default=0, nargs='?')
# parser.add_argument("n_files", type=int, default=-1, nargs='?')
args = parser.parse_args()

job_name = "ee" if args.edge_edge else "vf"

log = "log_ee" if args.edge_edge else "log_vf"
pathlib.Path(log).mkdir(exist_ok=True)

all_files = list(args.queries_root.glob(f"*/queries/*{'ee' if args.edge_edge else 'vf'}.csv"))

# if args.n_files < 0:
#     args.n_files = len(all_files)

delta = max(len(all_files) // args.n_jobs, 1)

for i in range(0, len(all_files), delta):
    files = all_files[i:i+delta]
    sbatch_args = [
        "sbatch", "-J", f"{job_name}{i}",
        "-o", f"{log}/{i}.out", "-e", f"{log}/{i}.err",
        "save_roots_job.sh", str(args.edge_edge), 
        " ".join(str(f.resolve()) for f in files)
    ]

    print(" ".join(sbatch_args))

    subprocess.run(sbatch_args)
