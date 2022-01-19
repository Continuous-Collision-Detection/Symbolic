import argparse
import pathlib
import ast
import json
import traceback
from tqdm import tqdm
import tarfile

import numpy

from wolframclient.language import Global

from utils import *

def make_tarfile(tar_filename, sources):
    with tarfile.open(tar_filename, "w") as tar:
        for source in sources:
            tar.add(source, arcname=source.name)

def main():
    global session

    parser = argparse.ArgumentParser()
    # parser.add_argument("queries_root", type=pathlib.Path)
    parser.add_argument("-i,--input", dest="input", nargs="+", type=pathlib.Path)
    parser.add_argument("edge_edge", type=ast.literal_eval)
    parser.add_argument("-o,--out_path", dest="out_path", 
                        default=pathlib.Path("out"), type=pathlib.Path)
    parser.add_argument("--wolfram_kernel_path", 
                        default=default_wolfram_kernel_path(), 
                        help=f"path to Wolfram kernel")

    args = parser.parse_args()

    session = open_wolfram_language_session(args.wolfram_kernel_path)

    if not session:
        print("failed to open mathematica!")
        exit(1)

    load_wolfram_script(
        session, "roots_ee.wl" if args.edge_edge else "roots_vf.wl")

    # for csv in args.queries_root.glob("*/vertex-face/*.csv"):
    # for csv in args.queries_root.glob(
    #         f"*/queries/*{'ee' if args.edge_edge else 'vf'}.csv"):
    for csv in args.input:
        print(csv)

        # root_out_dir = args.out_path / csv.parent.relative_to(args.queries_root)
        root_out_dir = csv.parents[1] / "roots"
        root_out_dir.mkdir(parents=True, exist_ok=True)
        
        data = numpy.genfromtxt(csv, delimiter=",", dtype=str)
        assert(data.shape[0] % 8 == 0)
        if data.shape[1] > 6:
            collides = data[::8, -1].astype(bool)
        else: 
            bools_path = (
                csv.parents[1] / "mma_bool" / (csv.stem + "_mma_bool.json"))
            assert(bools_path.exists())
            with open(bools_path) as f:
                collides = numpy.array(json.load(f))
        if data.shape[0] // 8 != collides.shape[0]:
            print("skipping", flush=True)
            continue

        root_files = []

        for i in tqdm(range(0, data.shape[0], 8)):
            if collides[i // 8]:
                query = data[i:i+8, :6].tolist()
                roots_filename = (
                    root_out_dir / (csv.stem + f"_q{i//8}_roots.bin")
                ).resolve()
                root_files.append(roots_filename)
                if roots_filename.exists():
                    continue # assumes this query has been processed successfully
                result = session.evaluate(
                    Global.roots(query, str(roots_filename)))
                # print(result)
                assert("True" in result)

        # TAR up the root binary files to avoid using my # files quota on HPC
        root_files = list(filter(lambda p: p.exists(), root_files))
        print(f"creating {root_out_dir / (csv.stem + '_roots.tar')}")
        make_tarfile(root_out_dir / (csv.stem + "_roots.tar"), root_files)
        for f in root_files:
            f.unlink() # delete file
        

if __name__ == "__main__":
    session = None
    try:
        main()
    except:
        traceback.print_exc()
    finally:
        if session:
            session.terminate()
