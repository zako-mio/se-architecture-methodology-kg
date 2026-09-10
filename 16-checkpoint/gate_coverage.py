#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_coverage.py — L6 覆盖度门控（四向覆盖 + manifest + GR-08/GR-09）

用法:
    python3 16-checkpoint/gate_coverage.py \
        --manifest 16-checkpoint/deliverables.json \
        --graph 10-dag-data/methodology-dag.json

检查项:
    [manifest] 契约声明的交付物清单逐项核对（glob 计数 vs expected）
    [四向覆盖] DAG 节点 ↔ 节点页 ↔ MD 镜像 ↔ 案例，逐项核对并输出覆盖率与缺失清单
    [GR-08]    每域三层完整（essence/methodology/technology）；O 域为跨域主干豁免
               technology，X 域为案例域豁免（显式豁免名单，见 EXEMPT）
    [GR-09]    ≥30% technology 节点有 case 字段或 case_instance 入边

结果: PASS / FAIL / PARTIAL；仅 PASS 时退出码 0。
    PASS    = manifest 覆盖 ≥ 阈值 且 四向覆盖 ≥ 阈值 且 GR-08 过 且 GR-09 过
    FAIL    = manifest 或四向覆盖低于阈值
    PARTIAL = 覆盖达标但 GR-08 / GR-09 未过
"""
import argparse
import glob as globmod
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

# GR-08 显式豁免：域 → 理由（豁免后该域不参与"三层完整"判定）
EXEMPT = {
    "O": "方法论主干/跨域综合域：只承载方法论权衡轴（method）与本质原理（essence），"
         "按 stage4-architecture-design §二 D1 不作为独立技术落点，允许无 technology",
    "X": "跨域兜底/案例域：当前仅含 type=case 节点（layer=null），案例域按 GR-08 契约豁免",
}


def load_graph(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_manifest(manifest, root, show):
    rows = []
    total_expected = 0
    total_actual = 0
    for d in manifest.get("deliverables", []):
        pat = os.path.join(root, d["pattern"])
        files = [p for p in globmod.glob(pat) if os.path.isfile(p)]
        actual = len(files)
        expected = int(d.get("expected", 0))
        total_expected += expected
        total_actual += min(actual, expected) if expected else actual
        rows.append({
            "id": d["id"],
            "pattern": d["pattern"],
            "expected": expected,
            "actual": actual,
            "missing": max(0, expected - actual),
            "extra": max(0, actual - expected),
        })
    cov = (total_actual / total_expected) if total_expected else 1.0
    print("[manifest] 交付物清单核对（%d 项，expected 合计 %d）" % (len(rows), total_expected))
    for r in rows:
        flag = "OK " if r["missing"] == 0 else "缺%d" % r["missing"]
        extra = (" +%d" % r["extra"]) if r["extra"] else ""
        print("  %-14s %-28s expected=%-4d actual=%-4d %s%s"
              % (r["id"], r["pattern"], r["expected"], r["actual"], flag, extra))
    print("  manifest 覆盖率 = min(actual,expected) 合计 / expected 合计 = %.2f%%"
          % (cov * 100))
    return cov, rows


def node_keyed_coverage(graph, root, manifest, show):
    nodes = graph.get("nodes", [])
    node_ids = [n["id"] for n in nodes]
    nk = manifest.get("node_keyed", {})
    html_dir = nk.get("html", {}).get("dir", "11-node-pages")
    md_dir = nk.get("md", {}).get("dir", "15-md/nodes")
    html_ext = nk.get("html", {}).get("ext", ".html")
    md_ext = nk.get("md", {}).get("ext", ".md")

    page_missing = [i for i in node_ids
                    if not os.path.isfile(os.path.join(root, html_dir, i + html_ext))]
    md_missing = [i for i in node_ids
                  if not os.path.isfile(os.path.join(root, md_dir, i + md_ext))]
    page_cov = (len(node_ids) - len(page_missing)) / len(node_ids) if node_ids else 1.0
    md_cov = (len(node_ids) - len(md_missing)) / len(node_ids) if node_ids else 1.0

    # 孤儿文件（有产物无对应 DAG 节点）
    def orphans(d, ext):
        out = []
        for p in globmod.glob(os.path.join(root, d, "*" + ext)):
            stem = os.path.splitext(os.path.basename(p))[0]
            if stem not in set(node_ids):
                out.append(stem)
        return out

    orphan_pages = orphans(html_dir, html_ext)
    orphan_md = orphans(md_dir, md_ext)

    print("[四向覆盖] DAG 节点 ↔ 节点页 ↔ MD 镜像 ↔ 案例")
    print("  DAG 节点数 = %d" % len(node_ids))
    print("  DAG→节点页 覆盖率 = %.2f%%（缺失 %d）%s"
          % (page_cov * 100, len(page_missing), _short(page_missing, show)))
    print("  DAG→MD镜像 覆盖率 = %.2f%%（缺失 %d）%s"
          % (md_cov * 100, len(md_missing), _short(md_missing, show)))
    print("  孤儿节点页 = %d %s" % (len(orphan_pages), _short(orphan_pages, show)))
    print("  孤儿 MD    = %d %s" % (len(orphan_md), _short(orphan_md, show)))

    # 案例向：cases[] 索引 ↔ type=case 节点，双向必须一致
    case_nodes = sorted(n["id"] for n in nodes if n.get("type") == "case")
    case_idx = [c.get("id") or c.get("node_id") for c in graph.get("cases", [])]
    case_set = set(case_nodes)
    idx_set = set(x for x in case_idx if x)
    only_node = sorted(case_set - idx_set)
    only_idx = sorted(idx_set - case_set)
    case_cov = len(case_set & idx_set) / len(case_set) if case_set else 1.0
    print("  案例索引一致性 = %.2f%%（案例节点 %d，cases[] %d；仅节点有 %d，仅索引有 %d）%s%s"
          % (case_cov * 100, len(case_set), len(idx_set), len(only_node), len(only_idx),
             _short(only_node, show), _short(only_idx, show)))

    four_way = (page_cov + md_cov + case_cov) / 3.0
    print("  四向综合覆盖率 = (节点页+MD+案例)/3 = %.2f%%" % (four_way * 100))
    return four_way, {
        "dag_nodes": len(node_ids),
        "page_coverage": page_cov,
        "md_coverage": md_cov,
        "case_coverage": case_cov,
        "page_missing": page_missing,
        "md_missing": md_missing,
        "orphan_pages": orphan_pages,
        "orphan_md": orphan_md,
        "case_only_node": only_node,
        "case_only_index": only_idx,
    }


def check_gr08(graph, show):
    nodes = graph.get("nodes", [])
    dom_layer = {}
    for n in nodes:
        layer = n.get("layer")
        if not layer:
            continue
        dom_layer.setdefault(n.get("domain"), set()).add(layer)
    required = {"essence", "methodology", "technology"}
    failures = []
    print("[GR-08] 每域三层完整（essence/methodology/technology），豁免名单 %s" % sorted(EXEMPT))
    for d in sorted(k for k in dom_layer if k not in EXEMPT):
        missing = sorted(required - dom_layer[d])
        if missing:
            failures.append({"domain": d, "missing": missing,
                             "have": sorted(dom_layer[d])})
    for d, reason in EXEMPT.items():
        print("  豁免 域%s：%s" % (d, reason))
    if failures:
        for f in failures[:show]:
            print("  FAIL 域%s 缺 %s（现有 %s）" % (f["domain"], f["missing"], f["have"]))
    else:
        print("  OK 全部非豁免域三层齐全")
    return len(failures) == 0, failures


def check_gr09(graph, show):
    nodes = graph.get("nodes", [])
    byid = {n["id"]: n for n in nodes}
    tech = [n for n in nodes if n.get("layer") == "technology"]
    inbound = {}
    for e in graph.get("edges", []):
        if e.get("type") == "case_instance" and byid.get(e.get("to"), {}).get("layer") == "technology":
            inbound.setdefault(e["to"], []).append(e["from"])
    covered = [n["id"] for n in tech if n.get("case") or inbound.get(n["id"])]
    rate = len(covered) / len(tech) if tech else 1.0
    ok = rate >= 0.30
    print("[GR-09] technology 案例覆盖：%d/%d = %.2f%%（阈值 30%%）→ %s"
          % (len(covered), len(tech), rate * 100, "PASS" if ok else "FAIL"))
    uncovered = [n["id"] for n in tech if n["id"] not in set(covered)]
    print("  未覆盖 technology node%s" % _short(uncovered, show))
    return ok, {"total": len(tech), "covered": len(covered), "rate": rate,
                "uncovered": uncovered}


def _short(items, show):
    if not items:
        return ""
    head = items[:show]
    tail = " ...(共 %d)" % len(items) if len(items) > show else ""
    return "示例: " + ", ".join(head) + tail


def main():
    ap = argparse.ArgumentParser(description="L6 覆盖度门控")
    ap.add_argument("--manifest", default=os.path.join("16-checkpoint", "deliverables.json"))
    ap.add_argument("--graph", default=os.path.join("10-dag-data", "methodology-dag.json"))
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--threshold", type=float, default=0.90)
    ap.add_argument("--show", type=int, default=20)
    args = ap.parse_args()

    root = args.repo_root or ROOT_DEFAULT
    manifest_path = args.manifest if os.path.isabs(args.manifest) else os.path.join(root, args.manifest)
    graph_path = args.graph if os.path.isabs(args.graph) else os.path.join(root, args.graph)

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    graph = load_graph(graph_path)

    print("== L6 覆盖度门控 ==")
    print("repo_root = %s" % root)
    print("manifest  = %s" % manifest_path)
    print("graph     = %s" % graph_path)
    print("门槛      = %.0f%%" % (args.threshold * 100))
    print("")

    manifest_cov, rows = check_manifest(manifest, root, args.show)
    print("")
    four_way, cov_detail = node_keyed_coverage(graph, root, manifest, args.show)
    print("")
    gr08_ok, gr08 = check_gr08(graph, args.show)
    print("")
    gr09_ok, gr09 = check_gr09(graph, args.show)
    print("")

    coverage_ok = manifest_cov >= args.threshold and four_way >= args.threshold
    if coverage_ok and gr08_ok and gr09_ok:
        result = "PASS"
    elif not coverage_ok:
        result = "FAIL"
    else:
        result = "PARTIAL"

    print("== 结果 ==")
    print("  manifest 覆盖率 %.2f%% | 四向覆盖率 %.2f%% | GR-08 %s | GR-09 %s"
          % (manifest_cov * 100, four_way * 100,
             "PASS" if gr08_ok else "FAIL", "PASS" if gr09_ok else "FAIL"))
    print("  L6 综合判定 = %s" % result)

    summary = {
        "result": result,
        "threshold": args.threshold,
        "manifest_coverage": manifest_cov,
        "four_way_coverage": four_way,
        "gr08": {"pass": gr08_ok, "failures": gr08},
        "gr09": {"pass": gr09_ok, **gr09},
        "manifest": rows,
        "coverage_detail": cov_detail,
    }
    sys.exit(0 if result == "PASS" else 1)


if __name__ == "__main__":
    main()
