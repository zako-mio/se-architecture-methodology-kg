#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_graph.py — 通用 DAG 知识图谱校验器（分片 / 全图）

依据 `00-plan/stage4-data-model.md §4.5` 及 `00-plan/stage5-build-contract.md §六`。

检查项：
  A 编码：UTF-8 无 BOM、无 U+FFFD
  B node：id 正则 / name / definition / sources / layer / type / domain / stage /
          status / verified / confidence / cross_cutting / GR-12 / GR-13 /
          deprecated_at / superseded_by / errata.source_id
  C edge：id 唯一 / 端点可解析 / type 枚举 / 层间方向 / 自环
  D 图性质：硬依赖边子集 Kahn 无环
  E 计数：全图模式 meta.total_* == 实际
  F edge id 正则：不符 → WARNING（不计 error），兼容既有 EB-P* 历史数据
  G case：全图模式校验案例层一致性（case 节点 layer=null / case_instance 边方向 /
          cases[] 与 case 节点集合双向一致 / 非案例节点 case[] 引用可解析）——无 case 数据时零告警

用法：
  python3 16-checkpoint/validate_graph.py --shard 10-dag-data/_parts/pilot-essence.json \
      --canonical 03-knowledge-map/canonical-sources.json
  python3 16-checkpoint/validate_graph.py --graph 10-dag-data/methodology-dag.json \
      --canonical 03-knowledge-map/canonical-sources.json

退出码：errors>0 → 1；否则 0。
"""
import argparse
import json
import os
import re
import sys
from collections import deque

NODE_RE = re.compile(r"^(ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2}$")
CANON_RE = re.compile(r"^(STD|OFF|BK|WEB|VEN|PAP|COM|LOC|XCV)-\d{3}$")
EDGE_ID_RE = re.compile(r"^E-\d{2,3}$")

TYPE_ENUM = {"principle", "method", "technology", "bridge", "case", "tool"}
DOMAIN_ENUM = set("FGHIJKLMNOX")
STAGE_ENUM = {"basic", "intermediate", "advanced"}
STATUS_ENUM = {"active", "deprecated", "superseded"}
VERIFIED_ENUM = {True, False, "cited"}
CONFIDENCE_ENUM = {"high", "medium", "low"}
EDGE_TYPES = {"prerequisite", "dependency", "derives_from", "refines", "implements",
              "case_instance", "cross_reference", "supersedes", "deprecated_by",
              "variant", "combination", "cooccurrence", "mitigates", "contrasts",
              "conflicts", "enables"}
HARD = {"prerequisite", "dependency", "derives_from", "refines"}
THEME_DEFAULT = {"M", "P", "N", "X"}
LAYER_ENUM = {"essence", "methodology", "technology"}

ERR = []
WARN = []


def err(code, detail):
    ERR.append((code, detail))


def warn(code, detail):
    WARN.append((code, detail))


def check_encoding(path):
    try:
        raw = open(path, "rb").read()
    except OSError as ex:
        err("ENCODING", "无法读取 %s: %s" % (path, ex))
        return None
    if raw.startswith(b"\xef\xbb\xbf"):
        err("BOM", path)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as ex:
        err("UTF8", "解码失败 %s: %s" % (path, ex))
        return None
    if "\ufffd" in text:
        err("UFFFD", path)
    return text


def load_canonical(path):
    if check_encoding(path) is None:
        return set()
    try:
        canon = json.load(open(path, encoding="utf-8"))
    except Exception as ex:
        err("CANON_JSON", "%s: %s" % (path, ex))
        return set()
    ids = set()
    for s in canon.get("sources", []):
        sid = s.get("id")
        if not sid:
            err("CANON_ID", "canonical source 缺少 id: %r" % s)
            continue
        if not CANON_RE.match(sid):
            err("CANON_ID", "canonical id 形态非法: %s" % sid)
        if sid in ids:
            err("CANON_DUP", sid)
        ids.add(sid)
    meta = canon.get("meta", {})
    if isinstance(meta.get("total"), int) and meta["total"] != len(canon.get("sources", [])):
        err("CANON_TOTAL", "meta.total=%s 与 len(sources)=%d 不一致" % (meta["total"], len(canon.get("sources", []))))
    return ids


def validate_nodes(nodes, node_ids, canon_set, group_ids=None, themes=None):
    theme_ids = set(THEME_DEFAULT)
    if themes:
        theme_ids |= {t["id"] for t in themes}
    seen = set()
    for n in nodes:
        nid = n.get("id", "<missing>")
        if nid in seen:
            err("DUP_NODE", nid)
        seen.add(nid)
        if not isinstance(nid, str) or not NODE_RE.match(nid):
            err("NODE_ID", str(nid))
        name = n.get("name", "")
        if not isinstance(name, str) or not (2 <= len(name) <= 20):
            err("GR-01", "%s name 长度=%d" % (nid, len(name) if isinstance(name, str) else -1))
        definition = n.get("definition", "")
        if not isinstance(definition, str) or not (15 <= len(definition) <= 300):
            err("GR-03", "%s definition 长度=%s" % (nid, len(definition) if isinstance(definition, str) else -1))
        sources = n.get("sources")
        if not isinstance(sources, list) or not (1 <= len(sources) <= 8):
            err("GR-05", "%s sources 数量非法: %r" % (nid, len(sources) if isinstance(sources, list) else sources))
        else:
            for s in sources:
                if s not in canon_set:
                    err("DANGLING_SRC", "%s 节点 source 悬挂: %s" % (nid, s))
        ntype = n.get("type")
        if ntype not in TYPE_ENUM:
            err("TYPE", "%s type 非法: %r" % (nid, ntype))
        layer = n.get("layer")
        if ntype == "case":
            if layer is not None:
                err("CASE_LAYER", "%s 案例节点 layer 须为 null，实际 %r" % (nid, layer))
        else:
            if layer not in LAYER_ENUM:
                err("LAYER", "%s layer 非法/缺失: %r" % (nid, layer))
        domain = n.get("domain")
        if domain not in DOMAIN_ENUM:
            err("DOMAIN", "%s domain 非法: %r" % (nid, domain))
        stage = n.get("stage")
        if stage not in STAGE_ENUM:
            err("STAGE", "%s stage 非法: %r" % (nid, stage))
        status = n.get("status")
        if status not in STATUS_ENUM:
            err("STATUS", "%s status 非法: %r" % (nid, status))
        verified = n.get("verified")
        if verified not in VERIFIED_ENUM:
            err("VERIFIED", "%s verified 非法: %r" % (nid, verified))
        confidence = n.get("confidence")
        if confidence not in CONFIDENCE_ENUM:
            err("CONFIDENCE", "%s confidence 非法: %r" % (nid, confidence))
        if group_ids is not None:
            if n.get("group") not in group_ids:
                err("BAD_GROUP", "%s group 不存在: %r" % (nid, n.get("group")))
        cc = n.get("cross_cutting", []) or []
        if not isinstance(cc, list) or len(cc) > 3:
            err("GR-07", "%s cross_cutting>3 或非数组: %r" % (nid, cc))
        else:
            for c in cc:
                if c not in theme_ids:
                    err("BAD_THEME", "%s cross_cutting 主题未登记: %s" % (nid, c))
        detail = n.get("detail") or {}
        tradeoff = detail.get("tradeoff")
        if ntype == "principle" and not tradeoff:
            err("GR-12", "%s principle 缺 detail.tradeoff" % nid)
        if ntype != "case" and not tradeoff and not n.get("errata"):
            err("GR-13", "%s 非案例节点缺权衡(tradeoff)且无反例(errata)" % nid)
        if status == "deprecated" and not n.get("deprecated_at"):
            err("DEP_NO_DATE", nid)
        if status == "superseded" and not n.get("superseded_by"):
            err("SUP_NO_SUCC", nid)
        for er in (n.get("errata") or []):
            sid = er.get("source_id")
            if sid not in canon_set:
                err("DANGLING_ERRATA", "%s errata.source_id 悬挂: %r" % (nid, sid))


def validate_edges(edges, node_ids, layer_of, is_full, canon_set):
    seen = set()
    for e in edges:
        eid = e.get("id", "<missing>")
        if eid in seen:
            err("DUP_EDGE", eid)
        seen.add(eid)
        if not isinstance(eid, str) or not EDGE_ID_RE.match(eid):
            warn("EDGE_ID_RE", "edge id 不合规: %s（既有数据豁免，新批次应使用 E-\\d{2,3}）" % eid)
        etype = e.get("type")
        if etype not in EDGE_TYPES:
            err("EDGE_TYPE", "%s type 非法: %r" % (eid, etype))
        frm, to = e.get("from"), e.get("to")
        frm_ok = frm in node_ids
        to_ok = to in node_ids
        if not frm_ok or not to_ok:
            detail = "%s 端点不可解析: from=%r to=%r" % (eid, frm, to)
            if is_full:
                err("EDGE_ENDPOINT", detail)
            else:
                warn("EDGE_ENDPOINT_EXTERNAL", detail + "（分片模式：跨分片端点视为 warning）")
        for s in (e.get("sources") or []):
            if s not in canon_set:
                err("DANGLING_EDGE_SRC", "%s 边 source 悬挂: %s" % (eid, s))
        if frm == to and etype in HARD:
            err("SELF_LOOP", eid)
        if frm_ok and to_ok:
            lf, lt = layer_of.get(frm), layer_of.get(to)
            if etype == "implements":
                if not (lf == "technology" and lt == "methodology"):
                    err("EDGE_DIR", "%s implements 须 technology->methodology，实际 %s->%s" % (eid, lf, lt))
            elif etype == "derives_from":
                if not (lf == "methodology" and lt == "essence"):
                    err("EDGE_DIR", "%s derives_from 须 methodology->essence，实际 %s->%s" % (eid, lf, lt))
            elif lf is not None and lt is not None and lf != lt:
                err("CROSS_LAYER", "%s 层间边类型非法: type=%s (%s->%s)" % (eid, etype, lf, lt))


def validate_cases(nodes, edges, cases, is_full):
    """案例层一致性校验（仅全图模式生效；无 case 数据时零告警）。"""
    if not is_full:
        return
    case_node_ids = {n.get("id") for n in nodes if n.get("type") == "case"}
    index = {}
    for c in (cases or []):
        if not isinstance(c, dict):
            err("CASE_ITEM", "cases[] 项非对象: %r" % c)
            continue
        cid = c.get("id")
        if cid in index:
            err("CASE_DUP", "cases[] 重复 id: %s" % cid)
        index[cid] = c
        if c.get("node_id") != cid:
            err("CASE_NODE_ID", "cases[].node_id=%r 与 id=%r 不一致" % (c.get("node_id"), cid))
        if cid not in case_node_ids:
            err("CASE_INDEX_UNKNOWN", "cases[] 含非案例节点 id: %r" % cid)
        if not c.get("summary"):
            err("CASE_SUMMARY", "cases[] 缺 summary: %r" % cid)
        srcs = c.get("sources")
        if not isinstance(srcs, list) or not srcs:
            err("CASE_SOURCES", "cases[] 缺 sources: %r" % cid)
    for cid in sorted(x for x in case_node_ids if x):
        if cid not in index:
            err("CASE_NOT_INDEXED", "case 节点未出现在 cases[]: %s" % cid)

    for n in nodes:
        if n.get("type") == "case":
            continue
        for cid in (n.get("case") or []):
            if cid not in case_node_ids:
                err("BAD_CASE", "%s node.case 引用不存在的案例节点: %s" % (n.get("id"), cid))

    for e in edges:
        if e.get("type") != "case_instance":
            continue
        frm, to = e.get("from"), e.get("to")
        if frm not in case_node_ids:
            err("CASE_EDGE_FROM", "%s case_instance.from 非案例节点: %r" % (e.get("id"), frm))
        if to in case_node_ids:
            err("CASE_EDGE_TO", "%s case_instance.to 指向案例节点: %r" % (e.get("id"), to))


def kahn_acyclic(nodes, edges):
    ids = [n["id"] for n in nodes]
    id_set = set(ids)
    adj = {i: [] for i in ids}
    indeg = {i: 0 for i in ids}
    for e in edges:
        if e.get("type") in HARD and e.get("from") in id_set and e.get("to") in id_set:
            adj[e["from"]].append(e["to"])
            indeg[e["to"]] += 1
    q = deque(i for i in ids if indeg[i] == 0)
    visited = 0
    while q:
        u = q.popleft()
        visited += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return visited


def main():
    ap = argparse.ArgumentParser(description="通用 DAG 知识图谱校验器")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--shard", help="校验单个分片文件（结构 {nodes,edges}）")
    src.add_argument("--graph", help="校验完整主图")
    ap.add_argument("--canonical", default=None,
                    help="canonical-sources.json 路径（默认 <repo-root>/03-knowledge-map/canonical-sources.json）")
    ap.add_argument("--repo-root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    help="母库 repo root（默认脚本上级目录）")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    target = args.shard or args.graph
    is_full = bool(args.graph)
    canonical = args.canonical or os.path.join(repo_root, "03-knowledge-map", "canonical-sources.json")

    if check_encoding(target) is None:
        pass
    canon_set = load_canonical(canonical)
    try:
        g = json.load(open(target, encoding="utf-8"))
    except Exception as ex:
        err("JSON", "%s: %s" % (target, ex))
        report(is_full)
        return 1

    nodes = g.get("nodes", [])
    edges = g.get("edges", [])
    node_ids = {n.get("id") for n in nodes}
    layer_of = {n.get("id"): n.get("layer") for n in nodes}

    groups = g.get("groups", [])
    group_ids = {x.get("id") for x in groups} if groups else None
    themes = g.get("themes", [])

    validate_nodes(nodes, node_ids, canon_set, group_ids=group_ids, themes=themes)
    validate_edges(edges, node_ids, layer_of, is_full, canon_set)
    validate_cases(nodes, edges, g.get("cases", []), is_full)

    visited = kahn_acyclic(nodes, edges)
    if visited != len(nodes):
        err("CYCLE", "硬依赖子图有环: kahn visited %d/%d" % (visited, len(nodes)))

    if is_full:
        meta = g.get("meta", {})
        for key, actual in (("total_nodes", len(nodes)), ("total_edges", len(edges)),
                            ("total_groups", len(groups))):
            if meta.get(key) != actual:
                err("COUNT", "meta.%s=%r 与实际=%d 不一致" % (key, meta.get(key), actual))
        if meta.get("dag_acyclic") is not True:
            err("DAG_FLAG", "meta.dag_acyclic 非 true: %r" % meta.get("dag_acyclic"))

    report(is_full, target, len(nodes), len(edges), visited)
    return 1 if ERR else 0


def report(is_full, target=None, n_nodes=0, n_edges=0, visited=0):
    mode = "graph" if is_full else "shard"
    if target:
        print("mode=%s  file=%s" % (mode, target))
        print("nodes=%d  edges=%d  kahn_visited=%d/%d" % (n_nodes, n_edges, visited, n_nodes))
    for code, detail in ERR:
        print("ERR %s %s" % (code, detail))
    for code, detail in WARN:
        print("WARN %s %s" % (code, detail))
    print("errors=%d warnings=%d" % (len(ERR), len(WARN)))
    print("PASS" if not ERR else "FAIL")


if __name__ == "__main__":
    sys.exit(main())
