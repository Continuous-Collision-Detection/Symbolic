import os
import glob
import numpy as np
import pickle
import pandas as pd

path = <root-out-path>
print(path, flush=True)

suffixes = ["", "_vf"]

for suffix in suffixes:
    folder = "tmp" + suffix
    results = []
    for file in glob.glob(os.path.join(path, folder, "*.pkl")):
        with open(file, "rb") as fp:
            data = pickle.load(fp)

        for i, t in enumerate(data):
            if i % 1000 == 0:
                print("{}/{}".format(i, len(data)), flush=True)


            exact = t[2]
            intersects = "True" in exact or "true" in exact or "<=" in exact

            results.append((i, t[0], t[1], intersects))

    with open("truths{}.pkl".format(suffix), "wb") as fp:
        pickle.dump(results, fp)
        
    df = pd.DataFrame(results, columns=['i', 'file', 'experiemnt', "intersects"])
    df.to_csv("truths{}.csv".format(suffix))
