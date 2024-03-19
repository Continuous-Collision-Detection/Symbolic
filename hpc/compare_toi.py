import subprocess
import argparse
import pathlib

from natsort import natsorted

root_dir = pathlib.Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(
        description="Run the compare_toi_job.sh script on the HPC.")
    parser.add_argument("-i,--input", dest="all_files",
                        type=pathlib.Path, nargs="+")
    parser.add_argument("n_jobs", type=int)
    args = parser.parse_args()

    job_name = "compare_toi_"

    log = root_dir / "log"
    log.mkdir(exist_ok=True)

    all_files = natsorted(args.all_files)

    files_split = [[] for _ in range(args.n_jobs)]
    for i, f in enumerate(all_files):
        files_split[i % args.n_jobs].append(f)

    for i, files in enumerate(files_split):
        sbatch_args = [
            "sbatch",
            "-J", f"{job_name}{i}",
            "-o", str(log / f"{i}.out"),
            "-e", str(log / f"{i}.err"),
            "compare_toi_job.sh", " ".join(str(f.resolve()) for f in files)
        ]

        if len(files) > 0:
            subprocess.run(sbatch_args)


if __name__ == "__main__":
    main()
