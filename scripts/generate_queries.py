import sys
import json
import meshio
import gmpy2

sys.path.append(
    "/Users/zachary/Development/research/contact/ipc-toolkit/build/release/python")
import ipctk  # noqa


def vf_boxes(mesh_t0, mesh_t1, bf):
    C_vf = bf.detect_face_vertex_candidates()

    F = mesh_t0.cells_dict["triangle"]
    face_offset = len(mesh_t0.points) + len(ipctk.edges(F))

    boxes = []
    for vf in C_vf:
        vid = vf.vertex_id
        fid = vf.face_id
        f0id, f1id, f2id = F[fid]
        is_colliding, *_ = ipctk.tight_inclusion.point_triangle_ccd(
            mesh_t0.points[vid], mesh_t0.points[f0id], mesh_t0.points[f1id], mesh_t0.points[f2id],
            mesh_t1.points[vid], mesh_t1.points[f0id], mesh_t1.points[f1id], mesh_t1.points[f2id],
            max_iterations=-1, no_zero_toi=False)
        if is_colliding:
            boxes.append([vid, face_offset + fid])

    return sorted(boxes)


def ee_boxes(mesh_t0, mesh_t1, bf):
    C_ee = bf.detect_edge_edge_candidates()

    E = ipctk.edges(mesh_t0.cells_dict["triangle"])
    edge_offset = len(mesh_t0.points)

    boxes = []
    for ee in C_ee:
        is_colliding, *_ = ipctk.tight_inclusion.edge_edge_ccd(
            mesh_t0.points[E[ee.edge0_id][0]],
            mesh_t0.points[E[ee.edge0_id][1]],
            mesh_t0.points[E[ee.edge1_id][0]],
            mesh_t0.points[E[ee.edge1_id][1]],
            mesh_t1.points[E[ee.edge0_id][0]],
            mesh_t1.points[E[ee.edge0_id][1]],
            mesh_t1.points[E[ee.edge1_id][0]],
            mesh_t1.points[E[ee.edge1_id][1]],
            max_iterations=-1, no_zero_toi=False)
        if is_colliding:
            boxes.append([
                edge_offset + ee.edge0_id, edge_offset + ee.edge1_id
            ])

    return sorted(boxes)


def generate_rational_queries(mesh_t0, mesh_t1, boxes, path):
    nV = len(mesh_t0.points)
    F = mesh_t0.cells_dict["triangle"]
    E = ipctk.edges(F)

    lines = []
    for box in boxes:
        if box[1] > nV + len(E):  # is a vertex-face box
            assert box[0] < nV
            fid = box[1] - nV - len(E)
            vertex_ids = [box[0], F[fid][0], F[fid][1], F[fid][2]]
        else:  # is an edge-edge box
            assert nV <= box[0] < nV + len(E)  # noqa
            assert nV <= box[1] < nV + len(E)  # noqa
            eaid = box[0] - nV
            ebid = box[1] - nV
            vertex_ids = [E[eaid][0], E[eaid][1], E[ebid][0], E[ebid][1]]

        for mesh in (mesh_t0, mesh_t1):
            for vid in vertex_ids:
                point = [gmpy2.mpq(x) for x in mesh.points[vid]]
                lines.append("{},{},{},{},{},{}".format(
                    str(point[0].numerator), str(point[0].denominator),
                    str(point[1].numerator), str(point[1].denominator),
                    str(point[2].numerator), str(point[2].denominator)))

    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    import argparse
    import natsort
    import pathlib
    from tqdm import tqdm

    parser = argparse.ArgumentParser()
    parser.add_argument("frames", type=pathlib.Path,
                        help="Path to the frames directory")
    args = parser.parse_args()

    boxes_dir = args.frames.parent / "boxes"
    boxes_dir.mkdir(exist_ok=True)

    query_dir = args.frames.parent / "queries"
    query_dir.mkdir(exist_ok=True)

    frames = natsort.natsorted(list(
        filter(lambda p: p.name != ".DS_Store", args.frames.glob("*"))))

    for i in tqdm(range(len(frames) - 1)):
        mesh_t0 = meshio.read(frames[i])
        mesh_t1 = meshio.read(frames[i + 1])

        F = mesh_t0.cells_dict["triangle"]
        E = ipctk.edges(F)

        bf = ipctk.BruteForce()
        bf.build(mesh_t0.points, mesh_t1.points, E, F)

        # Vertex-Face

        # boxes:
        if not (boxes_dir / f"{i}vf.json").exists():
            boxes = vf_boxes(mesh_t0, mesh_t1, bf)
            with open(boxes_dir / f"{i}vf.json", "w") as f:
                if boxes:
                    json.dump(boxes, f, separators=(",", ":"))
                else:
                    f.write("[]")
        else:
            with open(boxes_dir / f"{i}vf.json", "r") as f:
                boxes = json.load(f)

        # queries:
        if len(boxes) > 0:
            generate_rational_queries(
                mesh_t0, mesh_t1, boxes, query_dir / f"{i}vf.csv")

        # Edge-Edge

        # boxes:
        if not (boxes_dir / f"{i}ee.json").exists():
            boxes = ee_boxes(mesh_t0, mesh_t1, bf)
            with open(boxes_dir / f"{i}ee.json", "w") as f:
                if boxes:
                    json.dump(boxes, f, separators=(",", ":"))
                else:
                    f.write("[]")
        else:
            with open(boxes_dir / f"{i}ee.json", "r") as f:
                boxes = json.load(f)

        # queries:
        if len(boxes) > 0:
            generate_rational_queries(
                mesh_t0, mesh_t1, boxes, query_dir / f"{i}ee.csv")


def test():
    # Load the meshes
    mesh_t0 = meshio.read(
        "/Users/zachary/Development/research/collision-detection/sample-scalable-ccd-data/cloth-funnel/frames/227.ply")
    mesh_t1 = meshio.read(
        "/Users/zachary/Development/research/collision-detection/sample-scalable-ccd-data/cloth-funnel/frames/228.ply")

    F = mesh_t0.cells_dict["triangle"]
    E = ipctk.edges(F)

    bf = ipctk.BruteForce()
    bf.build(mesh_t0.points, mesh_t1.points, E, F)

    boxes = vf_boxes(mesh_t0, mesh_t1, bf)
    with open("vf.json", "w") as f:
        json.dump(boxes, f, separators=(",", ":"))
    with open("/Users/zachary/Development/research/collision-detection/sample-scalable-ccd-data/cloth-funnel/boxes/227vf.json", "r") as f:
        expected_boxes = json.load(f)
    expected_boxes.sort()
    print(boxes == expected_boxes)

    boxes = ee_boxes(mesh_t0, mesh_t1, bf)
    with open("ee.json", "w") as f:
        json.dump(boxes, f, separators=(",", ":"))
    with open("/Users/zachary/Development/research/collision-detection/sample-scalable-ccd-data/cloth-funnel/boxes/227ee.json", "r") as f:
        expected_boxes = json.load(f)
    expected_boxes.sort()
    print(boxes == expected_boxes)


if __name__ == "__main__":
    main()
