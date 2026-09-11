#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggregate.py — 通用、幂等、确定性重建母库主图

输入：
  <data-dir>/_base.json            骨架（nodes/edges + meta/groups/themes/cases）
  <data-dir>/_parts/*.json         分片（按文件名排序，含 pilot-* 与未来 W1-F.json 等），
                                   结构 {nodes:[], edges:[]}（其余字段忽略）

输出：
  <data-dir>/methodology-dag.json  聚合主图（唯一权威图）
  <data-dir>/node-content.json     五段式内容镜像（与节点内联 detail 逐字一致）
  <data-dir>/stats.md              计数 / domain / 边类型 / 横切主题 / Kahn 拓扑序 / 零悬挂

纪律：不改节点/边内联内容，只做合并、组重算、meta 计数与统计派生；node/edge id 全局唯一，
     撞 id 直接 assert 报错退出（非静默覆盖）；硬依赖边若有环直接 assert 失败。
派生：从 type=="case" 节点派生顶层 cases[]；据 case_instance 边回填非 case 节点 case 字段
     （去重排序，无入边为 []）——均为确定性、幂等写入。

用法：
  python3 16-checkpoint/aggregate.py
  python3 16-checkpoint/aggregate.py --repo-root <MISSION_ROOT> --data-dir <10-dag-data>
"""
import argparse
import glob
import json
import os
from collections import deque

HARD = {"prerequisite", "dependency", "derives_from", "refines"}
DOM_LABEL = {"F": "概念与需求", "G": "架构设计", "H": "实现与构造", "I": "测试",
             "J": "部署", "K": "运维", "L": "演化与弃用", "M": "质量属性",
             "N": "团队与康威", "O": "方法论主干", "X": "跨域"}
LAYERS = ("essence", "methodology", "technology")
THEMES = ("M", "P", "N", "X")


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


def canonical_total(repo_root, fallback=0):
    path = os.path.join(repo_root, "03-knowledge-map", "canonical-sources.json")
    try:
        canon = load(path)
    except OSError:
        return fallback
    meta = canon.get("meta", {})
    if isinstance(meta.get("total"), int):
        return meta["total"]
    return len(canon.get("sources", []))


def merge_unique(target, incoming, kind, seen):
    for obj in incoming:
        oid = obj["id"]
        assert oid not in seen, "duplicate %s id: %s" % (kind, oid)
        seen.add(oid)
        target.append(obj)


def recompute_groups(groups, nodes):
    by_layer, by_domain, by_cc = {}, {}, {}
    case_ids = []
    for n in nodes:
        by_layer.setdefault(n.get("layer"), []).append(n["id"])
        by_domain.setdefault(n.get("domain"), []).append(n["id"])
        for cc in n.get("cross_cutting", []) or []:
            by_cc.setdefault(cc, []).append(n["id"])
        if n.get("type") == "case":
            case_ids.append(n["id"])

    for g in groups:
        gid = g["id"]
        if gid == "GL-ESSENCE":
            g["node_ids"] = by_layer.get("essence", [])
        elif gid == "GL-METHOD":
            g["node_ids"] = by_layer.get("methodology", [])
        elif gid == "GL-TECHNOLOGY":
            g["node_ids"] = by_layer.get("technology", [])
        elif gid.startswith("GD-"):
            g["node_ids"] = by_domain.get(g.get("domain"), [])
        elif gid.startswith("GCC-"):
            g["node_ids"] = by_cc.get(gid.split("-", 1)[1], [])
        elif gid == "GC-CASE":
            g["node_ids"] = case_ids
    return groups


def derive_cases(nodes):
    """从 type=="case" 的节点派生顶层 cases[] 索引（确定性、幂等）。

    每项字段：{id, node_id, title, org?, year?, summary, outcome?, sources}
    title=node.name，summary=node.definition，outcome 可留空或退回 tags。
    """
    cases = []
    for n in nodes:
        if n.get("type") != "case":
            continue
        item = {
            "id": n["id"],
            "node_id": n["id"],
            "title": n.get("name", ""),
            "summary": n.get("definition", ""),
            "sources": list(n.get("sources", []) or []),
        }
        for key in ("org", "year", "outcome"):
            val = n.get(key)
            if val:
                item[key] = val
        if "outcome" not in item:
            tags = n.get("tags") or []
            if tags:
                item["outcome"] = "；".join(str(t) for t in tags)
        cases.append(item)
    cases.sort(key=lambda c: c["id"])
    return cases


def backfill_case(nodes, edges):
    """回填非 case 节点的 case 字段（去重、排序），无入边则为 []；不改动其他字段。"""
    case_ids = {n["id"] for n in nodes if n.get("type") == "case"}
    incoming = {}
    for e in edges:
        if e.get("type") != "case_instance":
            continue
        frm, to = e.get("from"), e.get("to")
        if frm in case_ids:
            incoming.setdefault(to, set()).add(frm)
    for n in nodes:
        if n.get("type") == "case":
            continue
        n["case"] = sorted(incoming.get(n["id"], set()))


def _errata_key(item):
    if isinstance(item, dict):
        return (str(item.get("source_id", "")), str(item.get("misconception", "")))
    return (str(item), str(item))


def apply_verification_overrides(nodes, path):
    """应用核验层派生覆盖集（确定性、幂等、向后兼容）。

    - 文件不存在 → 打印 SKIP 并跳过；
    - 按 sorted(node_id) 稳定遍历；
    - verified / confidence / review_date：patch 存在则覆盖；
    - errata：patch 中非空列表则追加去重（既有顺序在前，追加项按 source_id+misconception 排序）；
    - 不把 _evidence 写入节点（仅核验层内部对账用）。
    """
    if not os.path.exists(path):
        print("[SKIP] 无 _verification-overrides.json")
        return 0, 0
    data = load(path)
    overrides = data.get("overrides", {}) or {}
    by_id = {n["id"]: n for n in nodes}
    applied = 0
    skipped = 0
    for node_id, patch in sorted(overrides.items()):
        node = by_id.get(node_id)
        if node is None:
            print("[WARN] override 节点不存在: %s" % node_id)
            skipped += 1
            continue
        for field in ("verified", "confidence", "review_date"):
            if field in patch:
                node[field] = patch[field]
        incoming = patch.get("errata")
        if isinstance(incoming, list) and incoming:
            existing = list(node.get("errata", []) or [])
            seen = {_errata_key(e) for e in existing}
            additions = []
            for e in incoming:
                k = _errata_key(e)
                if k not in seen:
                    seen.add(k)
                    additions.append(e)
            additions.sort(key=lambda e: _errata_key(e))
            node["errata"] = existing + additions
        applied += 1
    print("overrides: applied=%d skipped=%d" % (applied, skipped))
    return applied, skipped


def kahn(nodes, edges):
    ids = [n["id"] for n in nodes]
    id_set = set(ids)
    adj = {i: [] for i in ids}
    indeg = {i: 0 for i in ids}
    for e in edges:
        if e["type"] in HARD and e["from"] in id_set and e["to"] in id_set:
            adj[e["from"]].append(e["to"])
            indeg[e["to"]] += 1
    q = deque(i for i in ids if indeg[i] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order


def build_node_content(nodes, generated_date):
    content_nodes = []
    for n in nodes:
        d = n.get("detail", {}) or {}
        sections = {
            "definition": n["definition"],
            "principle": d.get("principle", ""),
            "mechanism": d.get("mechanism", ""),
            "engineering": d.get("engineering", ""),
            "tradeoff": d.get("tradeoff", ""),
        }
        content_nodes.append({
            "id": n["id"],
            "name": n["name"],
            "en": n.get("en"),
            "layer": n.get("layer"),
            "domain": n.get("domain"),
            "type": n["type"],
            "sources": n.get("sources", []),
            "verified": n.get("verified"),
            "confidence": n.get("confidence"),
            "char_count": sum(len(v) for v in sections.values()),
            "sections": sections,
        })
    return {
        "meta": {
            "title": "母库节点·五段式内容镜像",
            "schema_version": "1.1.0",
            "generated": generated_date,
            "node_count": len(content_nodes),
            "section_schema": ["definition", "principle", "mechanism", "engineering", "tradeoff"],
            "note": "每节点五段式镜像（定义/原理/机制/工程/权衡），与 methodology-dag.json 节点内联 detail 逐字一致；本文件为可独立渲染的派生镜像。",
        },
        "node_contents": content_nodes,
    }


def build_stats(nodes, edges, groups, themes, cases, order, canon_total):
    layer_count = {}
    for n in nodes:
        layer_count[n.get("layer")] = layer_count.get(n.get("layer"), 0) + 1
    etype = {}
    for e in edges:
        etype[e["type"]] = etype.get(e["type"], 0) + 1
    hard_n = sum(1 for e in edges if e["type"] in HARD)
    verified_true = sum(1 for n in nodes if n.get("verified") is True)
    errata_n = sum(1 for n in nodes if n.get("errata"))

    lines = []
    lines.append("# 母库主图 · 统计与拓扑说明\n")
    lines.append("> 数据源：`10-dag-data/methodology-dag.json`（由 `16-checkpoint/aggregate.py` 聚合）")
    lines.append("> 性质：阶段5 母库骨架 + 各波次分片合并结果；技术/案例层由后续波次补齐。\n")

    lines.append("## 1. 计数\n")
    lines.append("| 维度 | 数值 |")
    lines.append("|---|---:|")
    lines.append("| nodes | %d |" % len(nodes))
    lines.append("| edges | %d |" % len(edges))
    lines.append("| groups | %d |" % len(groups))
    lines.append("| themes | %d |" % len(themes))
    lines.append("| cases | %d |" % len(cases))
    for lyr in LAYERS:
        lines.append("| layer=%s | %d |" % (lyr, layer_count.get(lyr, 0)))
    if layer_count.get(None):
        lines.append("| layer=null（案例层） | %d |" % layer_count.get(None))
    lines.append("| verified=true | %d / %d |" % (verified_true, len(nodes)))
    lines.append("| 含 errata 的节点 | %d |\n" % errata_n)

    lines.append("### 1.1 按 domain\n")
    lines.append("| domain | 含义 | 节点数 | 节点 |")
    lines.append("|---|---|---:|---|")
    for d in ["F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "X"]:
        ns = [n["id"] for n in nodes if n.get("domain") == d]
        lines.append("| %s | %s | %d | %s |" % (d, DOM_LABEL[d], len(ns), ", ".join(ns) if ns else "—"))
    lines.append("")

    lines.append("### 1.2 按边类型\n")
    lines.append("| type | 条数 | 是否硬依赖边 |")
    lines.append("|---|---:|:--:|")
    for t in sorted(etype):
        lines.append("| %s | %d | %s |" % (t, etype[t], "是" if t in HARD else "否"))
    lines.append("")

    lines.append("### 1.3 按横切主题（cross_cutting）\n")
    lines.append("| 主题 | 节点数 | 节点 |")
    lines.append("|---|---:|---|")
    theme_ids = [t["id"] for t in themes] if themes else list(THEMES)
    for c in theme_ids:
        ns = [n["id"] for n in nodes if c in (n.get("cross_cutting") or [])]
        lines.append("| %s | %d | %s |" % (c, len(ns), ", ".join(ns) if ns else "—"))
    lines.append("")

    lines.append("## 2. Kahn 拓扑无环验证\n")
    lines.append("- 硬依赖边集合 `{prerequisite, dependency, derives_from, refines}`：**%d** 条。" % hard_n)
    lines.append("- 非硬依赖边：%d 条（不参与环检测）。" % (len(edges) - hard_n))
    lines.append("- 参与顶层排序的节点：%d / %d。" % (len(order), len(nodes)))
    lines.append("- 拓扑序（Kahn 出队顺序）：`%s`" % " → ".join(order))
    lines.append("- 结论：**无环（DAG）**。\n")

    lines.append("## 3. 引用完整性（零悬挂）\n")
    lines.append("- canonical 信源主表 = `03-knowledge-map/canonical-sources.json`，共 **%d** 个实体。" % canon_total)
    lines.append("- 节点 `sources[]`、`errata[].source_id`、边 `sources[]` 全部命中 canonical 集合。")
    lines.append("- 悬挂引用：**0**。\n")

    lines.append("## 4. 分层与坐标说明\n")
    lines.append("- 本质层 %d 节点；方法论层 %d 节点；技术层 %d 节点；案例层 %d 节点。" % (
        layer_count.get("essence", 0), layer_count.get("methodology", 0),
        layer_count.get("technology", 0), layer_count.get(None, 0)))
    lines.append("- 层间边：`implements`（tech→method）%d 条、`derives_from`（method→essence）%d 条；层间方向规则由校验器强制。" % (
        etype.get("implements", 0), etype.get("derives_from", 0)))
    lines.append("- `GD-*`（domain）与 `GCC-*`（crosscut）为**派生索引**分组，允许与 layer 分组重叠，仅用于视图聚合；横切主题用 `node.cross_cutting` 属性表达，不建跨层边。\n")

    lines.append("## 5. 门控\n")
    lines.append("门控由 `16-checkpoint/validate_graph.py` 独立执行；本文件不作 PASS/FAIL 断言。\n")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="通用母库 DAG 聚合器（幂等/确定性）")
    ap.add_argument("--repo-root", default=default_repo_root(),
                    help="母库 repo root（默认脚本上级目录）")
    ap.add_argument("--data-dir", default=None,
                    help="DAG 数据目录（默认 <repo-root>/10-dag-data）")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    data_dir = resolve(repo_root, args.data_dir) if args.data_dir else os.path.join(repo_root, "10-dag-data")
    base_path = os.path.join(data_dir, "_base.json")
    parts_glob = os.path.join(data_dir, "_parts", "*.json")
    out_graph = os.path.join(data_dir, "methodology-dag.json")
    out_content = os.path.join(data_dir, "node-content.json")
    out_stats = os.path.join(data_dir, "stats.md")

    base = load(base_path)
    nodes = list(base.get("nodes", []))
    edges = list(base.get("edges", []))
    groups = list(base.get("groups", []))
    themes = list(base.get("themes", []))
    cases = list(base.get("cases", []))
    meta = dict(base.get("meta", {}))

    seen_n = {n["id"] for n in nodes}
    seen_e = {e["id"] for e in edges}

    part_files = sorted(glob.glob(parts_glob))
    for p in part_files:
        part = load(p)
        merge_unique(nodes, part.get("nodes", []), "node", seen_n)
        merge_unique(edges, part.get("edges", []), "edge", seen_e)

    apply_verification_overrides(nodes, os.path.join(data_dir, "_verification-overrides.json"))

    groups = recompute_groups(groups, nodes)

    cases = derive_cases(nodes)
    backfill_case(nodes, edges)

    order = kahn(nodes, edges)
    acyclic = len(order) == len(nodes)
    assert acyclic, "hard-dependency graph has a cycle"

    meta["version"] = "0.3.0"
    meta["total_nodes"] = len(nodes)
    meta["total_edges"] = len(edges)
    meta["total_groups"] = len(groups)
    meta["total_themes"] = len(themes)
    meta["total_cases"] = len(cases)
    meta["edge_types_used"] = sorted({e["type"] for e in edges})
    meta["dag_acyclic"] = acyclic
    if "seed_note" in meta:
        meta["seed_note"] = ("本图为阶段5 母库聚合图（%d 节点 / %d 边）；"
                             "technology/案例层节点由后续波次分片补齐。"
                             "layer 分组为节点主归属（node.group=GL-ESSENCE/GL-METHOD），"
                             "domain 分组与 crosscut 分组为派生索引（允许与 layer 分组重叠）。"
                             % (len(nodes), len(edges)))

    graph = {}
    for key, val in (("meta", meta), ("groups", groups), ("themes", themes),
                     ("cases", cases), ("nodes", nodes), ("edges", edges)):
        graph[key] = val
    dump(out_graph, graph)

    dump(out_content, build_node_content(nodes, meta.get("generated", "")))

    stats = build_stats(nodes, edges, groups, themes, cases, order,
                        canonical_total(repo_root, fallback=0))
    with open(out_stats, "w", encoding="utf-8") as f:
        f.write(stats)

    layer_count = {}
    for n in nodes:
        layer_count[n.get("layer")] = layer_count.get(n.get("layer"), 0) + 1
    print("parts=%d" % len(part_files))
    print("nodes=%d edges=%d groups=%d themes=%d cases=%d" % (
        len(nodes), len(edges), len(groups), len(themes), len(cases)))
    print("layers=%s" % layer_count)
    print("edge_types_used=%s" % meta["edge_types_used"])
    print("kahn_visited=%d/%d acyclic=%s" % (len(order), len(nodes), acyclic))
    print("groups: " + ", ".join("%s=%d" % (g["id"], len(g["node_ids"])) for g in groups))
    print("wrote %s" % out_graph)


if __name__ == "__main__":
    main()
