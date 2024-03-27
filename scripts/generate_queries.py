import sys
import json
import meshio

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

    frames = natsort.natsorted(args.frames.glob("*"))

    for i in tqdm(range(len(frames) - 1)):
        mesh_t0 = meshio.read(frames[i])
        mesh_t1 = meshio.read(frames[i + 1])

        F = mesh_t0.cells_dict["triangle"]
        E = ipctk.edges(F)

        bf = ipctk.BruteForce()
        bf.build(mesh_t0.points, mesh_t1.points, E, F)

        boxes = vf_boxes(mesh_t0, mesh_t1, bf)
        with open(boxes_dir / f"{i}vf.json", "w") as f:
            if boxes:
                json.dump(boxes, f, separators=(",", ":"))
            else:
                f.write("[]")

        boxes = ee_boxes(mesh_t0, mesh_t1, bf)
        with open(boxes_dir / f"{i}ee.json", "w") as f:
            if boxes:
                json.dump(boxes, f, separators=(",", ":"))
            else:
                f.write("[]")


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
