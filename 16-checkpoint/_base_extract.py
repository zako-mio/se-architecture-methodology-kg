#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_base_extract.py — 从已聚合主图中剔除分片节点/边，提取"骨架"到 10-dag-data/_base.json

用途：把当前 methodology-dag.json 中所有 _parts/*.json 已包含的 node id / edge id
剔除，得到骨架部分（groups/themes/cases/meta 原样保留），供 aggregate.py 作为
幂等重建的稳定输入。

用法：
  python3 16-checkpoint/_base_extract.py
  python3 16-checkpoint/_base_extract.py --repo-root <MISSION_ROOT> --data-dir <10-dag-data>
"""
import argparse
import glob
import json
import os


def default_repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve(repo_root, path):
    return path if os.path.isabs(path) else os.path.join(repo_root, path)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description="提取母库 DAG 骨架到 _base.json")
    ap.add_argument("--repo-root", default=default_repo_root(),
                    help="母库 repo root（默认脚本上级目录）")
    ap.add_argument("--data-dir", default=None,
                    help="DAG 数据目录（默认 <repo-root>/10-dag-data）")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    data_dir = resolve(repo_root, args.data_dir) if args.data_dir else os.path.join(repo_root, "10-dag-data")
    dag_path = os.path.join(data_dir, "methodology-dag.json")
    parts_dir = os.path.join(data_dir, "_parts")
    out_path = os.path.join(data_dir, "_base.json")

    dag = load(dag_path)

    part_node_ids = set()
    part_edge_ids = set()
    part_files = sorted(glob.glob(os.path.join(parts_dir, "*.json")))
    for p in part_files:
        d = load(p)
        part_node_ids.update(n["id"] for n in d.get("nodes", []))
        part_edge_ids.update(e["id"] for e in d.get("edges", []))

    base_nodes = [n for n in dag["nodes"] if n["id"] not in part_node_ids]
    base_edges = [e for e in dag["edges"] if e["id"] not in part_edge_ids]

    out = {"nodes": base_nodes, "edges": base_edges}
    for key in ("meta", "groups", "themes", "cases"):
        if key in dag:
            out[key] = dag[key]

    # 保持与原图顶层结构一致的键顺序（meta/groups/themes/cases/nodes/edges）
    ordered = {}
    for key in ("meta", "groups", "themes", "cases", "nodes", "edges"):
        if key in out:
            ordered[key] = out[key]
    dump(out_path, ordered)

    print("parts=%d" % len(part_files))
    for p in part_files:
        print("  - %s" % os.path.relpath(p, repo_root))
    print("base_nodes=%d" % len(base_nodes))
    print("  " + ", ".join(n["id"] for n in base_nodes))
    print("base_edges=%d" % len(base_edges))
    print("  " + ", ".join(e["id"] for e in base_edges))
    print("wrote %s" % out_path)


if __name__ == "__main__":
    main()
