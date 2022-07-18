import json
from tqdm import tqdm
import pathlib
import sys

scene_path = pathlib.Path(sys.argv[1])

for p in tqdm(list(scene_path.glob("tpq/*.json"))):
    bools_path = scene_path / "mma_bool" / (p.stem + f"ee_mma_bool.json")
    if bools_path.exists():
        with open(bools_path) as f:
            ee_mma_bools = json.load(f)
    else:
        ee_mma_bools = []
    
    bools_path = scene_path / "mma_bool" / (p.stem + f"vf_mma_bool.json")
    if bools_path.exists():
        with open(bools_path) as f:
            vf_mma_bools = json.load(f)
    else:
        vf_mma_bools = []

    with open(p) as f:
        data = json.load(f)
    if "toi_per_query" in data:
        toi_per_query = data["toi_per_query"]
    else:
        no_collisions = not (any(vf_mma_bools) and any(ee_mma_bools))
        if no_collisions:
            continue
        print(p, no_collisions)
    
    toi_per_query = {(int(q[0]), int(q[1])): q[2:] for q in toi_per_query}
    
    with open(scene_path / "boxes" / (p.stem + "ee.json")) as f:
        ee_pairs = json.load(f)
        ee_pairs = [tuple(pair) for pair in ee_pairs]
    if(len(ee_pairs) != len(ee_mma_bools)):
        assert(len(ee_mma_bools) == 0)
        ee_mma_bools = [False] * len(ee_pairs)

    with open(scene_path / "boxes" / (p.stem + "vf.json")) as f:
        vf_pairs = json.load(f)
        vf_pairs = [tuple(pair) for pair in vf_pairs]
    if(len(vf_pairs) != len(vf_mma_bools)):
        assert(len(vf_mma_bools) == 0)
        vf_mma_bools = [False] * len(vf_pairs)

    missing = 0

    ee_tois = []
    for ee_pair in ee_pairs:
        if ee_pair in toi_per_query:
            ee_tois.append(toi_per_query[ee_pair])
        elif ee_pair[::-1] in toi_per_query:
            ee_tois.append(toi_per_query[ee_pair[::-1]])
        else:
            missing += ee_mma_bools[len(ee_tois)]
            ee_tois.append(["1", "1"])
    
    vf_tois = []
    for vf_pair in vf_pairs:
        if vf_pair in toi_per_query:
            vf_tois.append(toi_per_query[vf_pair])
        elif vf_pair[::-1] in toi_per_query:
            vf_tois.append(toi_per_query[vf_pair[::-1]])
        else:
            missing += vf_mma_bools[len(vf_tois)]
            ee_tois.append(["1", "1"])

    if missing != 0:
        print(p, missing)

    toi_path = scene_path / "toi"
    toi_path.mkdir(exist_ok=True)
    if len(ee_tois) > 0:
        with open(toi_path / (p.stem + "ee.csv"), "w") as f:
            for toi in ee_tois:
                f.write("{:s}, {:s}\n".format(*toi))
    if len(vf_tois) > 0:
        with open(toi_path / (p.stem + "vf.csv"), "w") as f:
            for toi in vf_tois:
                f.write("{:s}, {:s}\n".format(*toi))
