import subprocess
import argparse
import pathlib

from natsort import natsorted

root_dir = pathlib.Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(
        description="Run the save_roots_job.sh script on the HPC.")
    parser.add_argument("-i,--input", dest="all_files",
                        type=pathlib.Path, nargs="+")
    parser.add_argument("--ee,--edge_edge", dest="edge_edge",
                        action='store_true')
    parser.add_argument("--vf,--vertex_face", dest="edge_edge",
                        action='store_false', default=False)
    parser.add_argument("n_jobs", type=int)
    args = parser.parse_args()

    job_name = "ee" if args.edge_edge else "vf"

    log = root_dir / ("log_ee" if args.edge_edge else "log_vf")
    log.mkdir(exist_ok=True)

    all_files = natsorted(args.all_files)

    delta = max(int(round(len(all_files) / args.n_jobs)), 1)

    prev_end = 0
    for i in range(args.n_jobs):
        end = prev_end + delta if i < args.n_jobs - 1 else len(all_files)
        files = all_files[prev_end:end]
        prev_end = end

        sbatch_args = [
            "sbatch",
            "-J", f"{job_name}{i}",
            "-o", str(log / f"{i}.out"),
            "-e", str(log / f"{i}.err"),
            str(root_dir / "hpc" / "save_roots_job.sh"),
            str(args.edge_edge),
            " ".join(str(f.resolve()) for f in files)
        ]

        # print(" ".join(sbatch_args))

        if len(files) > 0:
            subprocess.run(sbatch_args)


if __name__ == "__main__":
    main()
