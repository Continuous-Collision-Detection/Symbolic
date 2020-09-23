"""Script to batch process many queries
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
import os
import glob
import numpy as np
import subprocess
import pickle
from shutil import copyfile
import sys
import time

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr, Global


WolframKernel_path = sys.argv[5]
out_path = sys.argv[6]
root_path = sys.argv[7]

file_data = sys.argv[1]
loop_from = int(sys.argv[2])
loop_to = int(sys.argv[3])
edge_edge = sys.argv[4] == 'True'

suffix = "" if edge_edge else "_vf"
out_folder = "tmp" + suffix

mma_file = "roots_ee.mma" if edge_edge else "roots_vf.mma"

out_path = os.path.join(out_path, out_folder)
if not os.path.exists(out_path):
    os.mkdir(out_path)

print("- output directory: {}".format(out_path), flush=True)

with open(file_data, 'rb') as f:
    all_files = pickle.load(f)

loop_to = min(loop_to, len(all_files))

session = None
for k in range(loop_from, loop_to):
    folder = all_files[k][0]
    infile = all_files[k][1]

    if edge_edge:
        data_folder = os.path.join(
            root_path, folder)
    else:
        data_folder = os.path.join(
            root_path, folder)

    file = os.path.join(data_folder, infile + ".csv")
    print("- processing file: {}".format(file), flush=True)

    outs = []
    out_pickle = "out_"+folder+"_"+infile+".pkl"

    if os.path.exists(os.path.join(out_path, out_pickle)):
        with open(os.path.join(out_path, out_pickle), 'rb') as f:
            outs = pickle.load(f)

    data = np.genfromtxt(file, delimiter=",", dtype=type("x"))
    for i in range(0, data.shape[0], 8):
        ii = int(i/8)

        if ii % 10 == 0:
            print("processed {}/{}".format(i, data.shape[0]), flush=True)

        if ii < len(outs) and outs[ii][0] == file and outs[ii][1] == i:
            print("Skipping {}, already done".format(i))
            continue

        if not session:
            n_retry = 0
            while n_retry < 5:
                try:
                    session = WolframLanguageSession(
                        WolframKernel_path, stdout=sys.stdout)
                    with open(mma_file, 'r') as f:
                        script = f.read()
                    session.evaluate(wlexpr(script))
                    print("- mma file loaded", flush=True)
                    n_retry = 10
                except:
                    print("failed to check license, retrying", flush=True)
                    time.sleep(1)
                    n_retry += 1
            if n_retry != 10:
                print("failed to check license, {} times, quitting!".format(
                    n_retry), flush=True)
                break

        query = data[i:i+8, :].tolist()
        outm = session.evaluate(Global.roots(query))
        outs.append((file, i, outm))

        with open(os.path.join(out_path, out_pickle), "wb") as fp:
            pickle.dump(outs, fp)

    print("done {}/{}".format(k+1-loop_from, loop_to-loop_from), flush=True)

print("done procedding 1", flush=True)
