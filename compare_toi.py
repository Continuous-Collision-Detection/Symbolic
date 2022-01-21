import argparse
import pathlib
import ast
import json
import traceback
from tqdm import tqdm
import tarfile
import json

import numpy

from wolframclient.language import Global

from utils import *

def main():
    global session

    parser = argparse.ArgumentParser()
    parser.add_argument("-i,--input", dest="input", nargs="+", type=pathlib.Path)
    parser.add_argument("edge_edge", type=ast.literal_eval)
    parser.add_argument("--wolfram_kernel_path", 
                        default=default_wolfram_kernel_path(), 
                        help=f"path to Wolfram kernel")

    args = parser.parse_args()

    session = open_wolfram_language_session(args.wolfram_kernel_path)
    if not session:
        print("failed to open mathematica!")
        exit(1)
    load_wolfram_script(session, "compare_toi.wl")

    for tar_file in args.input:
        print(tar_file)
        output = {}

        working_dir = pathlib.Path(os.getenv("SLURM_TMPDIR"))
        if not working_dir.exists():
            working_dir = tar_file.parent

        toi_file = (tar_file.parents[1] / "toi" 
                    / (tar_file.stem.split("_")[0][:-2] + ".json"))
        with open(toi_file) as f:
            min_toi = json.load(f)["toi"]

        with tarfile.open(tar_file, "r") as tar:
            tar.extractall(working_dir)
            names = tar.getnames()
            
        for name in tqdm(names):
            roots_path = working_dir / name

            toi = min_toi
            try:
                results = rules_to_dict(session.evaluate(
                    Global.compareToI(str(roots_path), toi)))
                results["diff"] = float(results["diff"])
            except: 
                print(f"{name} failed")
                continue
            output[str(int(name.split("_")[1][1:]))] = results

            roots_path.unlink() # delete roots file
        
        print("valid={} min_diff={}".format(
            all([r["valid"] for k, r in output.items()]), 
            min([r["diff"] for k, r in output.items()])))

        toi_comparison_dir = tar_file.parents[1] / "toi_comparison"
        toi_comparison_dir.mkdir(parents=True, exist_ok=True)
        json_path = toi_comparison_dir / (tar_file.name.split("_")[0] + ".json")
        with open(json_path, 'w') as f:
            json.dump(output, f, separators=(',', ':'))

if __name__ == "__main__":
    session = None
    try:
        main()
    except:
        traceback.print_exc()
    finally:
        if session:
            session.terminate()

