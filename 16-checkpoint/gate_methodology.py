#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_methodology.py — 方法论专项门控（四项）

用法:
    python3 16-checkpoint/gate_methodology.py --check all \
        --graph 10-dag-data/methodology-dag.json \
        --glossary 03-knowledge-map/glossary.md \
        --o-methodology 02-research/O-methodology.json

    --check layer-boundary           ① 层边界判定规则校验
    --check glossary                 ② 术语一致性（glossary 唯一裁决）
    --check principle-counterexample ③ O-PC-01..36 原则↔反例落点
    --check tradeoff-11              ④ O-TD-01..11 权衡落点
    --check all                      四项全跑

结果: 每项 PASS/PARTIAL/FAIL；仅当所有被检项 PASS 时退出码 0。

说明:
    - 层边界：case_instance 端点 layer=null（案例层）按契约豁免，不判跨层。
    - O-PC ③ 优先读取显式映射表 16-checkpoint/opc-mapping.json：逐条校验
      opc_id 齐备、node_ids 非空且节点真实存在、counterexample_kind != none，
      且声明反例可核（errata 型至少一节点 errata 非空；contrasts/conflicts 型
      至少一节点有该类型入/出边）。表不存在时回退旧关键词启发式（strong/weak/
      unresolved 三档），绝不谎报 100%。
    - O-TD ④ 逐个校验 MTH-O-01..11 存在且 aliases 含 O-methodology 的 legacy_dim。
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

# 层间允许的依赖边类型（按契约 §3.2 刚性）：仅 implements(tech→method) / derives_from(method→essence)
IMPL, DERI = "implements", "derives_from"
LAYER_ORDER = {"essence": 0, "methodology": 1, "technology": 2}  # 内 → 外
# 非层间依赖边（声明为"任意"，跨层出现报 warn 而非 err）
NON_LAYER_EDGES = {"cross_reference"}

STOPWORDS = set("""the a an and or of to in for on with by is are be as at from that this it its not but no
software design system system's project code change make use used using can may should must will would
example etc via such over under more less than when then each other into out up down new old same
practice practices principle principles quality attribute attributes things thing element elements
based best good better work works way ways part parts""".split())


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_glossary(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.lstrip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 5:
                continue
            status = cells[-1]
            if status in ("settled", "disputed"):
                rows.append({"zh": cells[0], "en": cells[1], "status": status})
    return rows


def node_haystack(n):
    parts = [n.get("name", ""), n.get("en", ""),
             " ".join(n.get("aliases", []) or []), n.get("definition", "")]
    d = n.get("detail") or {}
    parts += [v for v in d.values() if isinstance(v, str)]
    for er in n.get("errata", []) or []:
        parts += [str(er.get("misconception", "")), str(er.get("verified_value", ""))]
    return " ".join(parts).lower()


# ---------------------------------------------------------------- ① 层边界
def check_layer_boundary(graph, show):
    nodes = graph.get("nodes", [])
    layer = {n["id"]: n.get("layer") for n in nodes}
    edges = graph.get("edges", [])
    errs = []
    warns = []
    exempt = 0
    n_impl = n_deri = 0
    for e in edges:
        lf, lt = layer.get(e["from"]), layer.get(e["to"])
        t = e.get("type")
        if lf is None or lt is None:
            exempt += 1  # 案例层端点（layer=null）豁免
            continue
        if t == IMPL:
            n_impl += 1
            if not (lf == "technology" and lt == "methodology"):
                errs.append((e["id"], t, "%s->%s" % (lf, lt), "implements 必须 technology→methodology"))
        elif t == DERI:
            n_deri += 1
            if not (lf == "methodology" and lt == "essence"):
                errs.append((e["id"], t, "%s->%s" % (lf, lt), "derives_from 必须 methodology→essence"))
        elif lf != lt:
            if t in NON_LAYER_EDGES:
                warns.append((e["id"], t, "%s->%s" % (lf, lt), "跨层非层间依赖边"))
            else:
                errs.append((e["id"], t, "%s->%s" % (lf, lt), "层间仅允许 implements/derives_from"))

    # 显式检查越级与内层引用外层
    tech2ess = [e["id"] for e in edges
                if layer.get(e["from"]) == "technology" and layer.get(e["to"]) == "essence"]
    inner2outer = [e["id"] for e in edges
                   if (layer.get(e["from"]) == "essence" and layer.get(e["to"]) in ("methodology", "technology"))
                   or (layer.get(e["from"]) == "methodology" and layer.get(e["to"]) == "technology")]
    if tech2ess:
        errs.append(("-", "tech->essence", "", "禁止技术→本质越级直连：%s" % tech2ess))
    if inner2outer:
        errs.append(("-", "inner->outer", "", "禁止内层引用外层：%s" % inner2outer))

    ok = len(errs) == 0
    print("[① layer-boundary]")
    print("  边总数 = %d | implements(tech→method) = %d | derives_from(method→essence) = %d | 案例层豁免 = %d"
          % (len(edges), n_impl, n_deri, exempt))
    print("  技术→本质越级 = %d | 内层引用外层 = %d" % (len(tech2ess), len(inner2outer)))
    print("  违规 = %d %s" % (len(errs), _short(errs, show)))
    print("  警告 = %d %s" % (len(warns), _short(warns, show)))
    print("  → %s" % ("PASS" if ok else "FAIL"))
    return ("PASS" if ok else "FAIL"), {"errors": errs, "warnings": warns,
                                        "implements": n_impl, "derives_from": n_deri,
                                        "case_exempt": exempt,
                                        "tech_to_essence": tech2ess, "inner_to_outer": inner2outer}


# ---------------------------------------------------------------- ② 术语一致性
def _errata_mentions(node, term_zh, term_en):
    for er in node.get("errata", []) or []:
        text = (str(er.get("misconception", "")) + str(er.get("verified_value", ""))).lower()
        if term_zh and term_zh in text:
            return True
        if term_en and term_en in text:
            return True
    return False


def check_glossary(graph, glossary, show):
    nodes = graph.get("nodes", [])
    disputed = [g for g in glossary if g["status"] == "disputed"]
    hits = []
    errs = []
    warns = []
    for d in disputed:
        zh, en = d["zh"], (d["en"] or "").lower()
        for n in nodes:
            name = n.get("name", "") or ""
            enf = (n.get("en", "") or "").lower()
            aliases = " ".join(n.get("aliases", []) or []).lower()
            in_name = bool(zh) and zh in name
            in_en = bool(en) and en == enf
            in_alias = (bool(en) and en in aliases) or (bool(zh) and zh in aliases)
            if not (in_name or in_en or in_alias):
                continue
            conf = n.get("confidence")
            errata = _errata_mentions(n, zh, en)
            annotated = conf in ("low", "medium") or errata
            rec = {"term": zh or d["en"], "node": n["id"], "name": name,
                   "confidence": conf, "errata_annotation": errata,
                   "slot": "name" if in_name else ("en" if in_en else "alias")}
            hits.append(rec)
            if annotated:
                continue
            if in_name:
                errs.append(rec)
            else:
                warns.append(rec)
    ok = len(errs) == 0
    print("[② glossary] disputed 术语 = %d 个：%s"
          % (len(disputed), ", ".join(g["zh"] or g["en"] for g in disputed)))
    print("  被节点引用命中 = %d %s" % (len(hits), _short(hits, show)))
    print("  冲突 err（disputed 术语出现在 name 且未标 low/medium、errata 未讨论）= %d %s"
          % (len(errs), _short(errs, show)))
    print("  警告 warn（出现在 en/aliases 且未标注）= %d %s"
          % (len(warns), _short(warns, show)))
    print("  → %s（已识别 errata 显式讨论 disputed 术语的节点为已标注，避免误报）"
          % ("PASS" if ok else "FAIL"))
    return ("PASS" if ok else "FAIL"), {"disputed": [g["zh"] or g["en"] for g in disputed],
                                        "hits": hits, "errors": errs, "warnings": warns}


# ---------------------------------------------------------------- ③ O-PC 落点
def probes(text):
    ps = set()
    for m in re.findall(r"[（(]([^）)]*)[)）]", text):
        for t in re.split(r"[/，,、;；]", m):
            t = t.strip().lower()
            if len(t) >= 4:
                ps.add(t)
    for t in re.findall(r"[A-Za-z][A-Za-z0-9'\-]+(?:\s+[A-Za-z][A-Za-z0-9'\-]+)*", text):
        toks = [x for x in t.strip().lower().split() if x not in STOPWORDS]
        if toks:
            tt = " ".join(toks)
            if len(tt) >= 4:
                ps.add(tt)
    for t in re.findall(r"[\u4e00-\u9fff]{2,8}", text):
        ps.add(t)
    return ps


def _check_pc_heuristic(graph, o_doc, show):
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    hay = {n["id"]: node_haystack(n) for n in nodes}
    has_errata = {n["id"]: bool(n.get("errata")) for n in nodes}
    contrast_nodes = set()
    for e in edges:
        if e.get("type") in ("contrasts", "conflicts"):
            contrast_nodes.add(e["from"])
            contrast_nodes.add(e["to"])
    pcs = o_doc.get("principles_counterexamples", [])
    strong, weak, unresolved = [], [], []
    for pc in pcs:
        text = str(pc.get("principle", "")) + " || " + str(pc.get("counterexample", ""))
        ps = probes(text)
        scores = []
        for nid, h in hay.items():
            hit = [p for p in ps if p in h]
            if hit:
                scores.append((len(hit), nid, sorted(hit)))
        scores.sort(key=lambda x: (-x[0], x[1]))
        best = scores[0] if scores else None
        rec = {"id": pc.get("id"), "principle": pc.get("principle"),
               "domains": pc.get("domains")}
        if best:
            score, nid, hit = best
            landed = has_errata.get(nid) or (nid in contrast_nodes)
            rec.update({"node": nid, "score": score, "evidence": hit[:6], "landed": landed})
        else:
            score, nid, hit, landed = 0, None, [], False
            rec.update({"node": None, "score": 0, "evidence": [], "landed": False})
        if score >= 3 and landed:
            strong.append(rec)
        elif score == 2 and landed:
            weak.append(rec)
        else:
            unresolved.append(rec)
    total = len(pcs)
    cov_any = (len(strong) + len(weak)) / total if total else 1.0
    cov_strict = len(strong) / total if total else 1.0
    print("[③ principle-counterexample] O-PC 总数 = %d" % total)
    print("  strong(score>=3 且落地) = %d | weak(score=2 且落地) = %d | unresolved = %d"
          % (len(strong), len(weak), len(unresolved)))
    print("  覆盖率（strong+weak）= %.2f%% | 严格覆盖率（strong）= %.2f%%"
          % (cov_any * 100, cov_strict * 100))
    for r in strong[:show]:
        print("    OK   %s -> %s (score=%d, evidence=%s)" % (r["id"], r["node"], r["score"], r["evidence"]))
    for r in weak[:show]:
        print("    WEAK %s -> %s (score=%d, 需复核)" % (r["id"], r["node"], r["score"]))
    print("  未覆盖（unresolved，供主Agent 复核）= %d" % len(unresolved))
    for r in unresolved[:show]:
        print("    ??   %s | %s | top=%s" % (r["id"], (r["principle"] or "")[:40], r.get("node")))
    result = "PASS" if len(unresolved) == 0 else "PARTIAL"
    print("  → %s（未覆盖项显式列出，不谎报 100%%）" % result)
    return result, {"total": total, "strong": len(strong), "weak": len(weak),
                    "unresolved_count": len(unresolved),
                    "coverage_any": cov_any, "coverage_strict": cov_strict,
                    "unresolved": unresolved, "weak_list": weak}


# ---------------------------------------------------------------- ③ O-PC 显式映射
def _node_counterexample(graph, nid):
    """返回 (has_errata:bool, contrast_types:set)"""
    by = {n["id"]: n for n in graph.get("nodes", [])}
    n = by.get(nid)
    if n is None:
        return False, set()
    has_errata = bool(n.get("errata"))
    cts = set()
    for e in graph.get("edges", []):
        if e.get("type") in ("contrasts", "conflicts") and nid in (e.get("from"), e.get("to")):
            cts.add(e.get("type"))
    return has_errata, cts


def _counterexample_ok(graph, node_ids, kind):
    """按声明类型核验反例确凿存在。"""
    for nid in node_ids:
        has_errata, cts = _node_counterexample(graph, nid)
        if kind == "errata" and has_errata:
            return True, nid
        if kind in ("contrasts", "conflicts") and kind in cts:
            return True, nid
    return False, None


def check_principle_counterexample(graph, o_doc, show, mapping_path=None):
    if not mapping_path or not os.path.exists(mapping_path):
        print("[③ principle-counterexample] 未找到显式映射表（%s），回退关键词启发式" % (mapping_path,))
        return _check_pc_heuristic(graph, o_doc, show)

    mapping = load_json(mapping_path)
    rows = mapping.get("rows", [])
    by_id = {r.get("opc_id"): r for r in rows}
    node_ids_all = {n["id"] for n in graph.get("nodes", [])}
    allowed_kinds = {"errata", "contrasts", "conflicts", "none"}

    missing, dangling, no_ce, bad_kind = [], [], [], []
    resolved = []
    for i in range(1, 37):
        pid = "O-PC-%02d" % i
        r = by_id.get(pid)
        if r is None:
            missing.append(pid)
            continue
        nids = r.get("node_ids") or []
        kind = r.get("counterexample_kind")
        ndang = [nid for nid in nids if nid not in node_ids_all]
        if ndang:
            dangling.append({"opc_id": pid, "node_ids": ndang})
            continue
        if not nids:
            no_ce.append({"opc_id": pid, "reason": "node_ids 为空"})
            continue
        if kind not in allowed_kinds:
            bad_kind.append({"opc_id": pid, "kind": kind})
            continue
        if kind == "none":
            no_ce.append({"opc_id": pid, "reason": "counterexample_kind=none"})
            continue
        ok, hit = _counterexample_ok(graph, nids, kind)
        if not ok:
            no_ce.append({"opc_id": pid, "reason": "声明 %s 但节点无对应反例/边" % kind,
                          "node_ids": nids})
            continue
        resolved.append({"opc_id": pid, "node": hit, "kind": kind})

    total = 36
    cov = len(resolved)
    problems = len(missing) + len(dangling) + len(no_ce) + len(bad_kind)
    ok = (problems == 0 and cov == total)

    print("[③ principle-counterexample] 显式映射表 = %s" % mapping_path)
    print("  O-PC 覆盖 %d/%d | 已解析 = %d" % (cov, total, cov))
    print("  缺失(未入库) = %d %s" % (len(missing), missing if missing else ""))
    print("  悬空节点引用 = %d %s" % (len(dangling), _short(dangling, show)))
    print("  无反例/类型不匹配 = %d %s" % (len(no_ce), _short(no_ce, show)))
    if bad_kind:
        print("  非法 counterexample_kind = %d %s" % (len(bad_kind), _short(bad_kind, show)))
    for r in resolved[:show]:
        print("    OK   %s -> %s (%s)" % (r["opc_id"], r["node"], r["kind"]))
    if len(resolved) > show:
        print("    ...（其余 %d 条已解析）" % (len(resolved) - show))
    result = "PASS" if ok else "PARTIAL"
    print("  → %s（36/36 且节点存在且确有反例 ⇒ PASS；否则如实列出）" % result)
    return result, {"mode": "explicit-mapping", "total": total, "resolved": cov,
                    "missing": missing, "dangling": dangling, "no_counterexample": no_ce,
                    "bad_kind": bad_kind, "resolved_rows": resolved}


# ---------------------------------------------------------------- ④ O-TD 落点
def check_tradeoff11(graph, o_doc, show):
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    tds = o_doc.get("tradeoff_dimensions", [])
    rows = []
    missing = []
    alias_fail = []
    for td in tds:
        tid = td.get("id")  # O-TD-01
        num = tid.split("-")[-1]
        nid = "MTH-O-" + num
        legacy = td.get("legacy_dim", "")
        n = nodes.get(nid)
        if not n:
            missing.append({"td": tid, "expect_node": nid})
            rows.append({"td": tid, "node": nid, "exists": False, "alias_ok": False,
                         "legacy_dim": legacy})
            continue
        aliases = n.get("aliases", []) or []
        alias_ok = legacy in aliases
        if not alias_ok:
            alias_fail.append({"td": tid, "node": nid, "legacy_dim": legacy, "aliases": aliases})
        rows.append({"td": tid, "node": nid, "exists": True, "alias_ok": alias_ok,
                     "name": n.get("name"), "legacy_dim": legacy})
    ok = len(missing) == 0 and len(alias_fail) == 0
    print("[④ tradeoff-11] O-TD 总数 = %d" % len(tds))
    for r in rows:
        flag = "OK " if r["exists"] and r["alias_ok"] else "FAIL"
        print("    %s %s -> %s（%s）" % (flag, r["td"], r["node"], r.get("legacy_dim", "")))
    if missing:
        print("  缺失落点节点 = %d %s" % (len(missing), _short(missing, show)))
    if alias_fail:
        print("  aliases 未含 legacy_dim = %d %s" % (len(alias_fail), _short(alias_fail, show)))
    print("  → %s" % ("PASS" if ok else "FAIL"))
    return ("PASS" if ok else "FAIL"), {"total": len(tds), "rows": rows,
                                        "missing": missing, "alias_fail": alias_fail}


def _short(items, show):
    if not items:
        return ""
    head = items[:show]
    tail = " ...(共 %d)" % len(items) if len(items) > show else ""
    return "示例: " + ", ".join(str(x) for x in head) + tail


def main():
    ap = argparse.ArgumentParser(description="方法论专项门控（四项）")
    ap.add_argument("--check", default="all",
                    choices=["layer-boundary", "glossary", "principle-counterexample",
                             "tradeoff-11", "all"])
    ap.add_argument("--graph", default=os.path.join("10-dag-data", "methodology-dag.json"))
    ap.add_argument("--glossary", default=os.path.join("03-knowledge-map", "glossary.md"))
    ap.add_argument("--o-methodology", default=os.path.join("02-research", "O-methodology.json"))
    ap.add_argument("--opc-mapping", default=os.path.join("16-checkpoint", "opc-mapping.json"))
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--show", type=int, default=20)
    args = ap.parse_args()

    root = args.repo_root or ROOT_DEFAULT

    def rp(p):
        return p if os.path.isabs(p) else os.path.join(root, p)

    graph = load_json(rp(args.graph))
    print("== 方法论专项门控 ==")
    print("graph = %s" % rp(args.graph))
    print("check = %s" % args.check)
    print("")

    results = {}
    todo = ["layer-boundary", "glossary", "principle-counterexample", "tradeoff-11"] \
        if args.check == "all" else [args.check]
    for c in todo:
        if c == "layer-boundary":
            results[c] = check_layer_boundary(graph, args.show)[0]
        elif c == "glossary":
            results[c] = check_glossary(graph, parse_glossary(rp(args.glossary)), args.show)[0]
        elif c == "principle-counterexample":
            results[c] = check_principle_counterexample(
                graph, load_json(rp(args.o_methodology)), args.show, rp(args.opc_mapping))[0]
        elif c == "tradeoff-11":
            results[c] = check_tradeoff11(graph, load_json(rp(args.o_methodology)), args.show)[0]
        print("")

    print("== 结果 ==")
    for k, v in results.items():
        print("  %-26s %s" % (k, v))
    overall = "PASS" if all(v == "PASS" for v in results.values()) else "PARTIAL"
    print("  方法论专项综合 = %s" % overall)
    sys.exit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
