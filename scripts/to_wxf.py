#!/usr/bin/env python3
"""Convert .mx files to .wxf files using Mathematica."""

import argparse
import shutil
import subprocess
import tarfile
import pathlib
import tempfile

from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="+", type=pathlib.Path)
    args = parser.parse_args()

    for mx_roots in (pbar := tqdm(args.input)):
        pbar.set_description(mx_roots.name)

        wxf_dir = (mx_roots.parent.parent / "roots_wxf").resolve()
        wxf_dir.mkdir(parents=True, exist_ok=True)
        wxf_roots = wxf_dir / mx_roots.name
        if wxf_roots.exists():
            num_mx_roots = len(tarfile.open(mx_roots, "r:gz").getnames())
            num_wxf_roots = len(tarfile.open(wxf_roots, "r:gz").getnames())
            if num_mx_roots == num_wxf_roots:
                continue
            wxf_roots.unlink()  # remove the partial wxf_roots

        # Create a temporary directory to extract the tarball
        with tempfile.TemporaryDirectory() as working_dir:
            # print("[debug]", working_dir)

            # Extract the tarball containing the .mx files
            with tarfile.open(mx_roots, "r:gz") as tar:
                if len(tar.getnames()) == 0:
                    shutil.copyfile(mx_roots, wxf_dir / mx_roots.name)
                    continue
                tar.extractall(working_dir)

            # Convert the .mx files to .wxf
            subprocess.run([
                pathlib.Path(__file__).parent / "to_wxf.wls",
                str(working_dir)
            ], check=True)

            # Create a new tarball containing the .wxf files
            with tarfile.open(wxf_roots, "w:gz") as tar:
                for source in pathlib.Path(working_dir).glob("*.wxf"):
                    tar.add(source, arcname=source.name)


if __name__ == "__main__":
    main()
