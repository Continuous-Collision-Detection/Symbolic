import sys
import pickle
import subprocess

edge_edge = sys.argv[1] == 'True'
n_jobs = int(sys.argv[2])

jname = "" if edge_edge else "vf"

log = "log" if edge_edge else "log_vf"

file = "ee.pkl" if edge_edge else "vf.pkl"

with open(file, 'rb') as f:
    all_files = pickle.load(f)


if len(sys.argv) >= 5:
    start = int(sys.argv[3])
    n_files = int(sys.argv[4])
else:
    start = 0
    n_files = len(all_files)

delta = int(n_files/n_jobs)

for i in range(start, n_files, delta):
    args = [
        "sbatch", "-J", "{}{}".format(jname, i),
        "-o", "{}/{}.out".format(log, i),
        "-e", "{}/{}.err".format(log, i),
         "job.sh",
        file, str(i), str(i+delta), str(edge_edge)
    ]

    # print(" ".join(args))

    subprocess.run(args)
