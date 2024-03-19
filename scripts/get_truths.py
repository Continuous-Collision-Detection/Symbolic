"""Generate a CSV file with the truth values for the roots."""

import os
import glob
import pickle
import pandas as pd

path = "<root-out-path>"
print(path, flush=True)

suffixes = ["ee", "vf"]

for suffix in suffixes:
    folder = "tmp_" + suffix
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

    with open(f"truths_{suffix}.pkl", "wb") as fp:
        pickle.dump(results, fp)

    df = pd.DataFrame(results, columns=[
                      'i', 'file', 'experiment', "intersects"])
    df.to_csv(f"truths_{suffix}.csv")
