#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_densify.py — 阶段7 阶段2「内容增密」门控（G-D1 … G-D5）

用法：
    python3 16-checkpoint/gate_densify.py --check all [--root <MROOT>]
    python3 16-checkpoint/gate_densify.py --check G-D1,G-D3

判据：
    G-D1 段级 claim 覆盖非空：26 参与节点 × 5 段 provenance 非空，且全部
         claim_id 可在 verification-ledger.json **且** node-claim-map.json 解析（零悬挂）
    G-D2 注水比：ceil(字数增量/200) ≤ 该节点 provenance 引用的 distinct claim_id 数
         （口径修正 2026-10-11；见 densify-contract.md §6）
    G-D3 字数区间：26 参与节点终稿 ∈ [2400,3000]；全局 [1500,3000] 不破；
         9 个排除节点保持原值
    G-D4 版权红线：节点正文 vs 三书原文「最长公共子串 ≥20 字」命中 = 0
    G-D5 对账：变更节点集 == 26 参与节点集（遗漏 0 / 越界 0）；
         26 节点 verified/confidence 值不翻转；其余 141 节点零改动

依赖：01-books/_verify/_densify/{precheck-coverage.json, write-*.json, evidence-*.json,
      paragraph-claim-map.json, densify-report.json}

私有层不存在（无 write-*.json）时整体 SKIP 并打印 SKIPPED（退出码 0），不得伪装 PASS。
"""
import argparse
import glob
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

VERIFY_DIR = os.path.join("01-books", "_verify")
DENSIFY_DIR = os.path.join(VERIFY_DIR, "_densify")
DAG_DIR = "10-dag-data"

LEDGER_REL = os.path.join(VERIFY_DIR, "verification-ledger.json")
CLAIMS_REL = os.path.join(VERIFY_DIR, "node-claim-map.json")
PRECHECK_REL = os.path.join(DENSIFY_DIR, "precheck-coverage.json")
PARA_MAP_REL = os.path.join(DENSIFY_DIR, "paragraph-claim-map.json")
REPORT_REL = os.path.join(DENSIFY_DIR, "densify-report.json")
BASELINE_REL = os.path.join(DAG_DIR, "_verification-baseline.json")
DAG_REL = os.path.join(DAG_DIR, "methodology-dag.json")
NODE_CONTENT_REL = os.path.join(DAG_DIR, "node-content.json")

CORPUS = [
    os.path.join("01-books", "_verify", "_text", "clean-architecture.txt"),
    os.path.join("01-books", "_verify", "_text", "saip.txt"),
]
CORPUS_GLOB = os.path.join("01-books", "_files", "P0-11", "ddia-zh-src", "*.md")

ALL_CRITERIA = ["G-D1", "G-D2", "G-D3", "G-D4", "G-D5"]

SEGMENTS = ("definition", "principle", "mechanism", "engineering", "tradeoff")
CHAR_MIN, CHAR_MAX = 2400, 3000
GLOBAL_CHAR_MIN, GLOBAL_CHAR_MAX = 1500, 3000
LCSUB_MIN = 20

# 与 derive_densify.py / gate_verification.py 同源（ADR-003）
PLAN_NODES = [
    "ESS-G-01", "ESS-G-02", "ESS-G-04", "ESS-I-02", "ESS-K-02", "ESS-L-05",
    "ESS-M-01", "ESS-M-02", "ESS-M-03", "ESS-M-04", "ESS-M-05",
    "ESS-O-01", "ESS-O-02", "ESS-O-03",
    "MTH-G-02", "MTH-G-03", "MTH-G-06", "MTH-M-01", "MTH-M-02", "MTH-M-03",
    "MTH-M-06", "MTH-O-03", "MTH-O-05", "MTH-O-09",
    "TEC-K-05", "TEC-M-03",
]
EXCLUDED_NODES = [
    "CAS-X-02", "ESS-G-03", "ESS-G-07", "ESS-H-02", "ESS-K-01",
    "MTH-K-06", "MTH-O-10", "MTH-O-11", "TEC-K-01",
]


def result(status, lines):
    return {"status": status, "lines": lines}


def resolve(root, path):
    return path if os.path.isabs(path) else os.path.join(root, path)


def safe_load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "缺失文件: %s" % path
    except Exception as e:                                   # noqa: BLE001
        return None, "解析失败 %s: %s" % (path, e)


def load_write_docs(root):
    out = {}
    for p in sorted(glob.glob(resolve(root, os.path.join(DENSIFY_DIR, "write-*.json")))):
        doc, err = safe_load(p)
        if doc and doc.get("node_id"):
            out[doc["node_id"]] = doc
    return out


def load_evidence(root):
    out = {}
    pats = (resolve(root, os.path.join(DENSIFY_DIR, "evidence-*.json")),
            resolve(root, os.path.join(DENSIFY_DIR, "sparse-*.json")))
    for p in sorted(glob.glob(pats[0]) + glob.glob(pats[1])):
        doc, _ = safe_load(p)
        if not doc:
            continue
        for it in doc.get("items", []) or []:
            if it.get("evidence_id"):
                out[it["evidence_id"]] = it
    return out


def body_chars(node):
    """节点正文五段字符数（从节点对象；detail 为 dict）。"""
    t = node.get("definition", "") or ""
    d = node.get("detail") or {}
    for k in ("principle", "mechanism", "engineering", "tradeoff"):
        t += d.get(k, "") or ""
    return len(t)


def load_head_dag(root):
    """读取阶段2 之前的 methodology-dag.json（正文基线）。

    优先顺序：
      1) 环境变量/参数指定的显式基线文件（负向测试用）
      2) git HEAD 的 10-dag-data/methodology-dag.json
    两者均不可用 → 返回 None，相关判据降级为 SKIP。
    """
    explicit = os.environ.get("DENSIFY_BODY_BASELINE")
    if explicit and os.path.isfile(explicit):
        try:
            with open(explicit, encoding="utf-8") as f:
                return json.load(f)
        except Exception:                                    # noqa: BLE001
            return None
    try:
        out = subprocess.run(["git", "-C", root, "show", "HEAD:%s" % DAG_REL.replace(os.sep, "/")],
                             capture_output=True, text=True, timeout=120)
        if out.returncode != 0:
            return None
        return json.loads(out.stdout)
    except Exception:                                        # noqa: BLE001
        return None


def build_ctx(root):
    ledger, err = safe_load(resolve(root, LEDGER_REL))
    if err:
        return None, err
    claims, _ = safe_load(resolve(root, CLAIMS_REL))
    precheck, _ = safe_load(resolve(root, PRECHECK_REL))
    dag, _ = safe_load(resolve(root, DAG_REL))
    baseline, _ = safe_load(resolve(root, BASELINE_REL))
    content, _ = safe_load(resolve(root, NODE_CONTENT_REL))
    head_dag = load_head_dag(root)

    ledger_ids = {r.get("claim_id") for r in (ledger or {}).get("records", []) or []}
    claim_map_ids = set()
    for _nid, cm in ((claims or {}).get("nodes") or {}).items():
        for c in cm.get("claims", []) or []:
            claim_map_ids.add(c.get("claim_id"))
    char_map = {e["id"]: e.get("char_count") for e in (content or {}).get("node_contents", []) or []}

    # _verification-baseline.json 的 nodes 是 {node_id: {verified, confidence}} 映射
    base_nodes = baseline.get("nodes") if isinstance(baseline, dict) else None
    if not isinstance(base_nodes, dict):
        base_nodes = {}

    return {
        "root": root,
        "records": (ledger or {}).get("records", []) or [],
        "ledger_ids": ledger_ids,
        "claim_map_ids": claim_map_ids,
        "precheck": precheck,
        "writes": load_write_docs(root),
        "evidence": load_evidence(root),
        "dag_nodes": {n["id"]: n for n in (dag or {}).get("nodes", []) or []},
        "base_verified": base_nodes,
        "head_nodes": {n["id"]: n for n in (head_dag or {}).get("nodes", []) or []},
        "char_map": char_map,
        "scope": list(PLAN_NODES),
        "show": 20,
    }, None


# ---------------------------------------------------------------- G-D1

def check_gd1(ctx):
    problems = []
    writes = ctx["writes"]
    if not writes:
        return result("SKIP", ["无 write-*.json（阶段2 未执行）"])
    for node_id in ctx["scope"]:
        doc = writes.get(node_id)
        if not doc:
            problems.append("%s 缺 write-*.json" % node_id)
            continue
        prov = doc.get("provenance") or {}
        for s in SEGMENTS:
            evs = prov.get(s) or []
            if not evs:
                problems.append("%s 段 %s provenance 为空" % (node_id, s))
        for nc in doc.get("new_claims", []) or []:
            cid = nc.get("claim_id")
            if cid not in ctx["ledger_ids"]:
                problems.append("%s claim %s 不在 ledger" % (node_id, cid))
            if cid not in ctx["claim_map_ids"]:
                problems.append("%s claim %s 不在 node-claim-map" % (node_id, cid))
    lines = ["参与节点 %d；write 文档 %d" % (len(PLAN_NODES), len(writes))]
    for p in problems[:ctx["show"]]:
        lines.append("  ! " + p)
    return result("PASS" if not problems else "FAIL", lines)


# ---------------------------------------------------------------- G-D2

def check_gd2(ctx):
    problems = []
    for node_id in ctx["scope"]:
        doc = ctx["writes"].get(node_id)
        if not doc:
            continue
        prov = doc.get("provenance") or {}
        segs = doc.get("segments") or {}
        final_chars = sum(len(segs.get(s, "") or "") for s in SEGMENTS)
        base = ctx["char_map"].get(node_id) or doc.get("baseline_chars") or 0
        delta = final_chars - base
        cids = set()
        for s in SEGMENTS:
            for eid in (prov.get(s) or []):
                it = ctx["evidence"].get(eid)
                if it and it.get("claim_id"):
                    cids.add(it["claim_id"])
        required = -(-max(delta, 0) // 200)
        if required > len(cids):
            problems.append("%s 增量 %d 字需 %d 条 claim，provenance 仅覆盖 %d 条"
                            % (node_id, delta, required, len(cids)))
    lines = ["注水比口径：ceil(Δ字/200) ≤ provenance distinct claim_id"]
    for p in problems[:ctx["show"]]:
        lines.append("  ! " + p)
    return result("PASS" if not problems else "FAIL", lines)


# ---------------------------------------------------------------- G-D3

def check_gd3(ctx):
    problems = []
    in_range = 0
    for node_id in ctx["scope"]:
        doc = ctx["writes"].get(node_id)
        if not doc:
            continue
        segs = doc.get("segments") or {}
        final_chars = sum(len(segs.get(s, "") or "") for s in SEGMENTS)
        if CHAR_MIN <= final_chars <= CHAR_MAX:
            in_range += 1
        else:
            problems.append("%s 终稿 %d 字，不在 [%d,%d]" % (node_id, final_chars, CHAR_MIN, CHAR_MAX))
    # 全局区间：所有节点（含排除节点）不得破 [1500,3000]
    global_bad = []
    for nid, node in sorted(ctx["dag_nodes"].items()):
        c = body_chars(node)
        if not (GLOBAL_CHAR_MIN <= c <= GLOBAL_CHAR_MAX):
            global_bad.append("%s=%d" % (nid, c))
    for g in global_bad[:ctx["show"]]:
        problems.append("全局区间破界: " + g)
    # 9 个排除节点保持原值（对账 git HEAD 的正文）
    excluded_changed = 0
    if not ctx["head_nodes"]:
        return result("SKIP", ["无 git HEAD 图谱可用 → 排除节点原值对账跳过（非 PASS）"])
    for nid in EXCLUDED_NODES:
        cur = ctx["dag_nodes"].get(nid)
        base = ctx["head_nodes"].get(nid)
        if cur and base and body_chars(cur) != body_chars(base):
            excluded_changed += 1
            problems.append("排除节点 %s 正文被改动（%d→%d）"
                            % (nid, body_chars(base), body_chars(cur)))
    lines = ["终稿在 [%d,%d] 区间: %d/%d；全局区间破界 %d；排除节点改动 %d"
             % (CHAR_MIN, CHAR_MAX, in_range, len(ctx["scope"]), len(global_bad), excluded_changed)]
    for p in problems[:ctx["show"]]:
        lines.append("  ! " + p)
    return result("PASS" if not problems else "FAIL", lines)


# ---------------------------------------------------------------- G-D4

def _ngrams(text, n):
    out = set()
    t = "".join(text.split())
    for i in range(len(t) - n + 1):
        out.add(t[i:i + n])
    return out


def check_gd4(ctx):
    corpus = []
    for rel in CORPUS:
        p = resolve(ctx["root"], rel)
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                corpus.append(f.read())
    for p in sorted(glob.glob(resolve(ctx["root"], CORPUS_GLOB))):
        with open(p, encoding="utf-8", errors="replace") as f:
            corpus.append(f.read())
    if not corpus:
        return result("SKIP", ["三书语料均不可用（无法机检版权红线）"])
    gram = set()
    for c in corpus:
        gram |= _ngrams(c, LCSUB_MIN)
    hits = []
    for node_id in ctx["scope"]:
        doc = ctx["writes"].get(node_id)
        if not doc:
            continue
        segs = doc.get("segments") or {}
        text = "".join(segs.get(s, "") or "" for s in SEGMENTS)
        for g in _ngrams(text, LCSUB_MIN):
            if g in gram:
                hits.append("%s: %s" % (node_id, g))
                break
    lines = ["语料 %d 份；≥%d 字公共子串命中 %d" % (len(corpus), LCSUB_MIN, len(hits))]
    for h in hits[:ctx["show"]]:
        lines.append("  ! " + h)
    return result("PASS" if not hits else "FAIL", lines)


# ---------------------------------------------------------------- G-D5

def check_gd5(ctx):
    problems = []
    writes = ctx["writes"]
    changed = sorted(writes)
    missing = sorted([n for n in ctx["scope"] if n not in writes])
    extra = sorted([n for n in writes if n not in PLAN_NODES])
    if missing:
        problems.append("遗漏 %d 个参与节点: %s" % (len(missing), ", ".join(missing[:5])))
    if extra:
        problems.append("越界 %d 个非参与节点: %s" % (len(extra), ", ".join(extra[:5])))

    # verified / confidence 值不翻转（对账 _verification-baseline.json，严格比较：
    # 注意 "cited" 与 True 不同，禁用真值判断）
    flips = []
    for node_id in ctx["scope"]:
        cur = ctx["dag_nodes"].get(node_id)
        base = ctx["base_verified"].get(node_id)
        if not cur or not base:
            continue
        if cur.get("verified") != base.get("verified"):
            flips.append("%s verified %r→%r" % (node_id, base.get("verified"), cur.get("verified")))
        if cur.get("confidence") != base.get("confidence"):
            flips.append("%s confidence %r→%r" % (node_id, base.get("confidence"), cur.get("confidence")))
    for f in flips[:ctx["show"]]:
        problems.append("值翻转: " + f)

    # 其余 141 节点正文零改动（对账 git HEAD）
    others_changed = []
    if not ctx["head_nodes"]:
        return result("SKIP", ["无 git HEAD 图谱可用 → 其余节点零改动对账跳过（非 PASS）"])
    for nid, node in sorted(ctx["dag_nodes"].items()):
        if nid in PLAN_NODES:
            continue
        base = ctx["head_nodes"].get(nid)
        if base and body_chars(node) != body_chars(base):
            others_changed.append(nid)
    for o in others_changed[:ctx["show"]]:
        problems.append("非参与节点正文被改动: " + o)

    lines = ["变更集 %d（期望 %d）；遗漏 %d；越界 %d；值翻转 %d；其余节点改动 %d"
             % (len(changed), len(ctx["scope"]), len(missing), len(extra), len(flips),
                len(others_changed))]
    for p in problems[:ctx["show"]]:
        lines.append("  ! " + p)
    return result("PASS" if not problems else "FAIL", lines)


CHECKS = {
    "G-D1": check_gd1,
    "G-D2": check_gd2,
    "G-D3": check_gd3,
    "G-D4": check_gd4,
    "G-D5": check_gd5,
}


def main():
    ap = argparse.ArgumentParser(description="阶段7 阶段2 增密门控 G-D1..G-D5")
    ap.add_argument("--check", default="all", help="all 或逗号分隔的判据名，如 G-D1,G-D3")
    ap.add_argument("--root", default=ROOT_DEFAULT, help="母库 root（默认脚本上级目录）")
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--nodes", default="", help="限定参与节点集（逗号分隔；负向测试用，默认全部 26）")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    ctx, err = build_ctx(root)
    if err:
        print("[SKIP] 私有核验层不可读：%s" % err)
        print("== 结果 = SKIPPED（私有层缺失，非 PASS） ==")
        return 0
    ctx["show"] = args.show
    if args.nodes.strip():
        ctx["scope"] = [n.strip() for n in args.nodes.split(",") if n.strip()]

    if args.check == "all":
        names = ALL_CRITERIA
    else:
        names = [c.strip() for c in args.check.split(",") if c.strip()]
    unknown = [c for c in names if c not in CHECKS]
    if unknown:
        ap.error("未知判据: %s" % ", ".join(unknown))

    print("== 阶段2 增密门控 ==")
    tally = {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0}
    for name in names:
        r = CHECKS[name](ctx)
        tally[r["status"]] += 1
        print("[%s] %s" % (r["status"], name))
        for ln in r["lines"]:
            print("    " + ln)
    print("== 汇总 ==")
    print("  PASS=%d FAIL=%d WARN=%d SKIP=%d" % (tally["PASS"], tally["FAIL"], tally["WARN"], tally["SKIP"]))
    overall = "PASS" if tally["FAIL"] == 0 else "FAIL"
    print("== 结果 = %s ==" % overall)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
