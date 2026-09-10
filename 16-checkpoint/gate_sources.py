#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_sources.py — L7 信源门控

用法:
    python3 16-checkpoint/gate_sources.py \
        --graph 10-dag-data/methodology-dag.json \
        --canonical 03-knowledge-map/canonical-sources.json \
        --glossary 03-knowledge-map/glossary.md

检查项:
    ① canonical 命中：节点 sources[] / errata[].source_id / 边 sources[] 必须全部可在
       canonical 主表解析（悬挂 = 0）。
    ② 可溯源率 ≥ 95%：节点 sources 非空、全部可解析且 verified ∈ {true, "cited"}。
    ③ verified==true 占比 ≥ 80%（GR-10）；sources 非空占比 100%。
    ④ disputed 术语标注：glossary.md 中 状态=disputed 的术语，若被节点 name/en/aliases
       引用，则其 confidence 必须为 low/medium（否则报冲突），并输出命中/冲突清单。

结果: PASS / FAIL；仅 PASS 时退出码 0。
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
CANON_RE = re.compile(r"^(STD|OFF|BK|WEB|VEN|PAP|COM|LOC|XCV)-\d{3}$")
TRACEABLE_RATE = 0.95
VERIFIED_RATE = 0.80
CONFIDENCE_OK = {"low", "medium"}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_glossary(path):
    """解析 glossary.md 表格，返回 disputed 术语列表 [{zh,en,status}]"""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.lstrip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 5:
                continue
            zh, en, _definition, _src, status = cells[0], cells[1], cells[2], cells[3], cells[-1]
            if status in ("settled", "disputed"):
                rows.append({"zh": zh, "en": en, "status": status})
    return rows


def collect_refs(graph):
    refs = []  # (origin_kind, origin_id, value)
    for n in graph.get("nodes", []):
        for s in n.get("sources", []) or []:
            refs.append(("node.sources", n["id"], s))
        for er in n.get("errata", []) or []:
            if isinstance(er, dict) and er.get("source_id"):
                refs.append(("errata.source_id", n["id"], er["source_id"]))
    for e in graph.get("edges", []):
        for s in e.get("sources", []) or []:
            refs.append(("edge.sources", e["id"], s))
    return refs


def check_dangling(graph, canon, show):
    refs = collect_refs(graph)
    dangling = []
    illegal = []
    for kind, oid, val in refs:
        if not isinstance(val, str):
            illegal.append((kind, oid, val))
            continue
        if val not in canon:
            dangling.append((kind, oid, val))
    by_kind = {}
    for kind, oid, val in refs:
        by_kind[kind] = by_kind.get(kind, 0) + 1
    print("[① canonical 命中] 引用总数 = %d %s" % (len(refs), by_kind))
    print("  悬挂（不在 canonical 主表）= %d %s" % (len(dangling), _short(dangling, show)))
    print("  非法引用（非字符串）= %d" % len(illegal))
    return len(dangling) == 0 and len(illegal) == 0, dangling


def check_traceable(graph, canon, show):
    nodes = graph.get("nodes", [])
    traceable = []
    untraceable = []
    empty_sources = []
    for n in nodes:
        src = n.get("sources", []) or []
        if not src:
            empty_sources.append(n["id"])
        ok = bool(src) and all(s in canon for s in src) and n.get("verified") in (True, "cited")
        (traceable if ok else untraceable).append(n["id"])
    rate = len(traceable) / len(nodes) if nodes else 1.0
    ok = rate >= TRACEABLE_RATE
    print("[② 可溯源率] %d/%d = %.2f%%（阈值 %.0f%%）→ %s"
          % (len(traceable), len(nodes), rate * 100, TRACEABLE_RATE * 100,
             "PASS" if ok else "FAIL"))
    print("  sources 为空的节点 = %d %s" % (len(empty_sources), _short(empty_sources, show)))
    print("  不可溯源节点 = %d %s" % (len(untraceable), _short(untraceable, show)))
    return ok, {"rate": rate, "traceable": len(traceable), "total": len(nodes),
                "empty_sources": empty_sources, "untraceable": untraceable}


def check_verified(graph, show):
    nodes = graph.get("nodes", [])
    true_n = [n["id"] for n in nodes if n.get("verified") is True]
    rate = len(true_n) / len(nodes) if nodes else 1.0
    ok = rate >= VERIFIED_RATE
    print("[③ verified=true 占比] %d/%d = %.2f%%（GR-10 阈值 %.0f%%）→ %s"
          % (len(true_n), len(nodes), rate * 100, VERIFIED_RATE * 100,
             "PASS" if ok else "FAIL"))
    others = [(n["id"], n.get("verified")) for n in nodes if n.get("verified") is not True]
    print("  非 true 节点 = %d %s" % (len(others), _short(others, show)))
    return ok, {"rate": rate, "true": len(true_n), "total": len(nodes)}


def _errata_mentions(node, term_zh, term_en):
    """节点是否在 errata 中显式讨论了该 disputed 术语（视为已标注）"""
    for er in node.get("errata", []) or []:
        text = (str(er.get("misconception", "")) + str(er.get("verified_value", ""))).lower()
        if term_zh and term_zh in text:
            return True
        if term_en and term_en in text:
            return True
    return False


def check_disputed(graph, glossary, show):
    disputed = [g for g in glossary if g["status"] == "disputed"]
    nodes = graph.get("nodes", [])
    hits = []
    conflicts = []
    for term in disputed:
        zh = term["zh"]
        en = (term["en"] or "").lower()
        for n in nodes:
            name = (n.get("name") or "")
            en_field = (n.get("en") or "").lower()
            aliases = " ".join(n.get("aliases", []) or []).lower()
            matched = False
            if zh and zh in name:
                matched = True
            if en and (en == en_field or en in aliases or en in en_field):
                matched = True
            if not matched:
                continue
            conf = n.get("confidence")
            errata = _errata_mentions(n, zh, en)
            annotated = conf in CONFIDENCE_OK or errata
            rec = {"term": zh or term["en"], "node": n["id"], "name": n.get("name"),
                   "confidence": conf, "errata_annotation": errata, "annotated": annotated}
            hits.append(rec)
            if not annotated:
                conflicts.append(rec)
    print("[④ disputed 术语标注] glossary disputed 术语 %d 个：%s"
          % (len(disputed), ", ".join(g["zh"] or g["en"] for g in disputed)))
    print("  被节点引用命中 = %d" % len(hits))
    for h in hits[:show]:
        how = "confidence=%s" % h["confidence"]
        if h["errata_annotation"]:
            how += " + errata 已讨论"
        print("    - %s -> %s（%s），%s"
              % (h["term"], h["node"], h["name"], how))
    print("  未标注（confidence 非 low/medium 且 errata 未讨论）= %d" % len(conflicts))
    for c in conflicts[:show]:
        print("    ! %s -> %s（%s），confidence=%s" % (c["term"], c["node"], c["name"], c["confidence"]))
    ok = len(conflicts) == 0
    return ok, {"disputed_terms": [g["zh"] or g["en"] for g in disputed],
                "hits": hits, "conflicts": conflicts}


def _short(items, show):
    if not items:
        return ""
    head = items[:show]
    tail = " ...(共 %d)" % len(items) if len(items) > show else ""
    return "示例: " + ", ".join(str(x) for x in head) + tail


def main():
    ap = argparse.ArgumentParser(description="L7 信源门控")
    ap.add_argument("--graph", default=os.path.join("10-dag-data", "methodology-dag.json"))
    ap.add_argument("--canonical", default=os.path.join("03-knowledge-map", "canonical-sources.json"))
    ap.add_argument("--glossary", default=os.path.join("03-knowledge-map", "glossary.md"))
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--show", type=int, default=20)
    args = ap.parse_args()

    root = args.repo_root or ROOT_DEFAULT
    graph_path = args.graph if os.path.isabs(args.graph) else os.path.join(root, args.graph)
    canon_path = args.canonical if os.path.isabs(args.canonical) else os.path.join(root, args.canonical)
    gloss_path = args.glossary if os.path.isabs(args.glossary) else os.path.join(root, args.glossary)

    graph = load_json(graph_path)
    canon_doc = load_json(canon_path)
    canon = {s["id"] for s in canon_doc.get("sources", [])}
    glossary = parse_glossary(gloss_path)

    print("== L7 信源门控 ==")
    print("graph     = %s" % graph_path)
    print("canonical = %s（%d 实体）" % (canon_path, len(canon)))
    print("glossary  = %s（%d 术语，disputed %d）"
          % (gloss_path, len(glossary), sum(1 for g in glossary if g["status"] == "disputed")))
    print("")

    d_ok, dangling = check_dangling(graph, canon, args.show)
    print("")
    t_ok, trace = check_traceable(graph, canon, args.show)
    print("")
    v_ok, ver = check_verified(graph, args.show)
    print("")
    g_ok, disc = check_disputed(graph, glossary, args.show)
    print("")

    result = "PASS" if (d_ok and t_ok and v_ok and g_ok) else "FAIL"
    print("== 结果 ==")
    print("  ① 悬挂=0 %s | ② 可溯源率 %.2f%% %s | ③ verified=true %.2f%% %s | ④ disputed 标注 %s"
          % ("PASS" if d_ok else "FAIL", trace["rate"] * 100,
             "PASS" if t_ok else "FAIL", ver["rate"] * 100,
             "PASS" if v_ok else "FAIL", "PASS" if g_ok else "FAIL"))
    print("  L7 综合判定 = %s" % result)
    sys.exit(0 if result == "PASS" else 1)


if __name__ == "__main__":
    main()
