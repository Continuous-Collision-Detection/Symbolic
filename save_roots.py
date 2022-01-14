import argparse
import pathlib
import ast

import numpy

from wolframclient.language import Global

from utils import *

################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("queries_root", type=pathlib.Path)
parser.add_argument("edge_edge", type=ast.literal_eval)
parser.add_argument("-o,--out_path", dest="out_path", default=pathlib.Path("out"), type=pathlib.Path)
parser.add_argument("--wolfram_kernel_path", 
                    default=default_wolfram_kernel_path(), 
                    help=f"path to Wolfram kernel")

args = parser.parse_args()

################################################################################

session = open_wolfram_language_session(args.wolfram_kernel_path)
if not session:
    print("failed to open mathematica!")
    exit(1)

load_wolfram_script(session, "roots_ee.wl" if args.edge_edge else "roots_vf.wl")

for csv in args.queries_root.glob("*/vertex-face/*.csv"):
    print(csv)

    root_out_dir = args.out_path / csv.parent.relative_to(args.queries_root)
    root_out_dir.mkdir(parents=True, exist_ok=True)
    
    data = numpy.genfromtxt(csv, delimiter=",", dtype=str)
    for i in range(0, data.shape[0], 8):
        collides = bool(int(data[i, -1]))
        assert(all(collides == bool(int(c)) for c in data[i:i+8, -1]))
        
        if(collides):
            print(i)
            query = data[i:i+8, :-1].tolist()
            roots_filename = (
                root_out_dir / (csv.stem + f"_q{i//8}_root.bin")).resolve()
            result = session.evaluate(Global.roots(query, str(roots_filename)))
            # print(result)
            assert("True" in result)


session.terminate()