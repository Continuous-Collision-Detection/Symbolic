"""
Script to batch process many queries
input arguments:
- picked file containing the list pairs pointing to the folder and infile
- start index to process
- end index to process
- True/False if the query is an edge-edge or vertex face
- WolframKernel path
- output path
- root file

for every file in the range it generate "out_path/tmp_<vf|ee>/out_<folder>_<infile>.pkl", which contains a list of tuples (file, i, collision)
"""
import numpy as np
import subprocess
import pickle
from shutil import copyfile
import time
import argparse
import pathlib
import ast

from wolframclient.language import Global

from utils import *

################################################################################

parser = argparse.ArgumentParser(
    description="""
        Script to batch process many queries.
        For every file in the range it generates
        "out_path/tmp_<vf|ee>/out_<folder>_<infile>.pkl", which contains a list of tuples (file, i, collision).""",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("file_data")
parser.add_argument("loop_from", type=int)
parser.add_argument("loop_to", type=int)
parser.add_argument("edge_edge", type=ast.literal_eval)
parser.add_argument("--wolfram_kernel_path",
                    dest="WolframKernel_path",
                    default=default_wolfram_kernel_path(),
                    help=f"path to Wolfram kernel")
parser.add_argument("out_path", type=pathlib.Path)
parser.add_argument("root_path", type=pathlib.Path)

args = parser.parse_args()

################################################################################

out_folder = "tmp" if args.edge_edge else "tmp_vf"
out_path = args.out_path / out_folder
out_path.mkdir(parents=True, exist_ok=True)
print("- output directory: {}".format(out_path), flush=True)

mma_file = "roots_ee.wl" if args.edge_edge else "roots_vf.wl"

with open(args.file_data, 'rb') as f:
    all_files = pickle.load(f)

loop_from = args.loop_from
loop_to = min(args.loop_to, len(all_files))

session = None
for k, (folder, infile) in enumerate(all_files[loop_from:loop_to]):
    file = root_path / folder / (infile + ".csv")
    print(f"- processing file: {file}", flush=True)

    outs = []
    out_pickle = f"out_{folder}_{infile}.pkl"

    if (out_path / out_pickle).exists():
        with open(out_path / out_pickle, 'rb') as f:
            outs = pickle.load(f)

    data = np.genfromtxt(file, delimiter=",", dtype=type("x"))
    for i in range(0, data.shape[0], 8):
        ii = i // 8

        if ii % 10 == 0:
            print(f"processed {i}/{data.shape[0]}", flush=True)

        if ii < len(outs) and outs[ii][0] == file and outs[ii][1] == i:
            print(f"Skipping {i}, already done")
            continue

        if not session:
            session = open_wolfram_language_session(WolframKernel_path)
            if not session:
                print("failed to open wolfram language session, quitting!", flush=True)
                break
            load_wolfram_script(session, mma_file)

        query = data[i:i+8, :].tolist()
        outm = session.evaluate(Global.roots(query))
        outs.append((file, i, outm))

        with open(out_path / out_pickle, "wb") as fp:
            pickle.dump(outs, fp)

    print(f"done {k + 1 - loop_from}/{loop_to - loop_from}", flush=True)

if session:
    session.terminate()
print("done procedding 1", flush=True)
