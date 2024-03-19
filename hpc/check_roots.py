import pathlib
import pickle
import subprocess
import argparse

root_dir = pathlib.Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(
        description="Run the check_roots_job.sh script on the HPC.")
    parser.add_argument("--ee,--edge_edge", dest="edge_edge",
                        action='store_true')
    parser.add_argument("--vf,--vertex_face", dest="edge_edge",
                        action='store_false', default=False)
    parser.add_argument("n_jobs", type=int)
    parser.add_argument("start", type=int, default=0, nargs='?')
    parser.add_argument("n_files", type=int, default=-1, nargs='?')
    args = parser.parse_args()

    job_name = "ee" if args.edge_edge else "vf"

    log = root_dir / ("log" if args.edge_edge else "log_vf")
    log.mkdir(exist_ok=True)

    file = "ee.pkl" if args.edge_edge else "vf.pkl"

    with open(file, 'rb') as f:
        all_files = pickle.load(f)

    if args.n_files < 0:
        args.n_files = len(all_files)

    delta = max(int(round(args.n_files / args.n_jobs)), 1)

    for i in range(args.start, args.n_files, delta):
        args = [
            "sbatch",
            "-J", f"{job_name}{i}",
            "-o", str(log / f"{i}.out"),
            "-e", str(log / f"{i}.err"),
            str(root_dir / "hpc" / "check_roots_job.sh"),
            file, str(i), str(i+delta), str(args.edge_edge)
        ]

        # print(" ".join(args))

        subprocess.run(args)


if __name__ == "__main__":
    main()
