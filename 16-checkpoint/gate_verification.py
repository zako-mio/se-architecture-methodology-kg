#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_verification.py — 阶段7 核验层门控（G-V1 … G-V8）

用法：
    python3 16-checkpoint/gate_verification.py --check all [--root <MROOT>]
    python3 16-checkpoint/gate_verification.py --check G-V1,G-V4

判据：
    G-V1 核验层 JSON 合法 + 必填字段齐全（含 id 格式、单节点主张 ≤8）
    G-V2 evidence_strength / direction / gap.kind 封闭枚举
    G-V3 记录 anchor 存在；chapter 非空（例外：inferred 且书无章节结构）
    G-V4 「无锚点升级」= 0（升级节点 direct 记录须有 anchor+direction）
    G-V5 claim 与书原文「≥20 字连续子串」近似检查；书文本不可用 → SKIP
    G-V6 编码 UTF-8 无 BOM、无 U+FFFD
    G-V7 幂等：derive_verification.py --check 连跑两次一致
    G-V8 对账：overrides 节点集 == ledger 应覆盖节点集

私有核验层不存在时整体 SKIP 并打印 SKIPPED（退出码 0），不得伪装 PASS。
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

VERIFY_DIR = os.path.join("01-books", "_verify")
LEDGER_REL = os.path.join(VERIFY_DIR, "verification-ledger.json")
TOC_REL = os.path.join(VERIFY_DIR, "book-toc-index.json")
GAPS_REL = os.path.join(VERIFY_DIR, "reverse-gaps.json")
CLAIMS_REL = os.path.join(VERIFY_DIR, "node-claim-map.json")
OVERRIDES_REL = os.path.join("10-dag-data", "_verification-overrides.json")

ALL_CRITERIA = ["G-V1", "G-V2", "G-V3", "G-V4", "G-V5", "G-V6", "G-V7", "G-V8"]

NODE_RE = re.compile(r"^(ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2}$")
RECORD_RE = re.compile(r"^VR-(DDIA|CA|SAIP)-\d{3}$")
SOURCE_RE = re.compile(r"^BK-\d{3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ORIGINS = {"definition", "principle", "mechanism", "engineering", "tradeoff", "errata"}
STRENGTH = {"direct", "partial", "inferred", "contradicted"}
DIRECTIONS = {"forward", "reverse"}
GAP_KINDS = {"missed_citation", "coverage_hole", "concept_missing"}
CLAIM_CAP = 8
LCSUB_MIN = 20


def resolve(root, path):
    return path if os.path.isabs(path) else os.path.join(root, path)


def safe_load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except (OSError, ValueError) as e:
        return None, str(e)


def result(status, lines):
    return status, lines


def check_gv1(ctx):
    problems = []
    records = ctx["records"]
    for r in records:
        rid = r.get("record_id", "?")
        for key in ("record_id", "node_id", "source_id", "direction", "claim_id",
                    "claim", "anchor", "page_anchor_private", "evidence_strength",
                    "evidence_note", "review"):
            if key not in r:
                problems.append("%s 缺字段 %s" % (rid, key))
        if not RECORD_RE.match(str(r.get("record_id", ""))):
            problems.append("%s record_id 格式非法" % rid)
        nid = str(r.get("node_id", ""))
        if not NODE_RE.match(nid):
            problems.append("%s node_id 非法: %s" % (rid, nid))
        if not SOURCE_RE.match(str(r.get("source_id", ""))):
            problems.append("%s source_id 非法: %s" % (rid, r.get("source_id")))
        if r.get("direction") not in DIRECTIONS:
            problems.append("%s direction 非法" % rid)
        cid = str(r.get("claim_id", ""))
        if nid and not re.match(r"^%s#(%s)#\d+$" % (re.escape(nid), "|".join(ORIGINS)), cid):
            problems.append("%s claim_id 非法: %s" % (rid, cid))
        if r.get("evidence_strength") == "contradicted":
            c = r.get("contradiction")
            if not isinstance(c, dict) or not c.get("verified_value"):
                problems.append("%s contradicted 缺 contradiction.verified_value" % rid)
        rev = r.get("review")
        if not isinstance(rev, dict):
            problems.append("%s review 非对象" % rid)
        else:
            for rk in ("reviewed_by", "review_date", "second_pass", "second_pass_by"):
                if rk not in rev:
                    problems.append("%s review 缺 %s" % (rid, rk))
            if not DATE_RE.match(str(rev.get("review_date", ""))):
                problems.append("%s review_date 非法" % rid)
    counts = {}
    for r in records:
        counts[r.get("node_id")] = counts.get(r.get("node_id"), 0) + 1
    over = [n for n, c in counts.items() if c > CLAIM_CAP]
    for n in over:
        problems.append("%s 记录数 %d 超上限 %d" % (n, counts[n], CLAIM_CAP))
    for g in ctx["gaps"]:
        gid = g.get("gap_id", "?")
        for key in ("gap_id", "kind", "book_source_id", "anchor", "target",
                    "summary", "proposed_action", "evidence_strength"):
            if key not in g:
                problems.append("%s 缺字段 %s" % (gid, key))
        tgt = g.get("target")
        if isinstance(tgt, dict) and not (tgt.get("existing_node_id") or tgt.get("proposed_node")):
            problems.append("%s target 两字段均为空" % gid)
    ok = not problems
    lines = ["记录 %d 条 / gap %d 条；问题 %d" % (len(records), len(ctx["gaps"]), len(problems))]
    for p in problems[:ctx["show"]]:
        lines.append("  ! " + p)
    if len(problems) > ctx["show"]:
        lines.append("  ...(共 %d)" % len(problems))
    return result("PASS" if ok else "FAIL", lines)


def check_gv2(ctx):
    problems = []
    for r in ctx["records"]:
        if r.get("evidence_strength") not in STRENGTH:
            problems.append("%s evidence_strength=%r" % (r.get("record_id"), r.get("evidence_strength")))
        if r.get("direction") not in DIRECTIONS:
            problems.append("%s direction=%r" % (r.get("record_id"), r.get("direction")))
    for g in ctx["gaps"]:
        if g.get("kind") not in GAP_KINDS:
            problems.append("%s kind=%r" % (g.get("gap_id"), g.get("kind")))
    lines = ["非枚举命中 = %d" % len(problems)]
    for p in problems[:ctx["show"]]:
        lines.append("  ! " + p)
    return result("PASS" if not problems else "FAIL", lines)


def check_gv3(ctx):
    problems = []
    for r in ctx["records"]:
        anchor = r.get("anchor")
        rid = r.get("record_id")
        if not isinstance(anchor, dict):
            problems.append("%s anchor 缺失" % rid)
            continue
        chapter = anchor.get("chapter", "")
        if chapter in (None, ""):
            src = r.get("source_id")
            no_struct = not ctx["toc_by_source"].get(src)
            if r.get("evidence_strength") == "inferred" and no_struct:
                continue
            problems.append("%s chapter 为空（非 inferred/无结构例外）" % rid)
    lines = ["anchor.chapter 违规 = %d" % len(problems)]
    for p in problems[:ctx["show"]]:
        lines.append("  ! " + p)
    return result("PASS" if not problems else "FAIL", lines)


def check_gv4(ctx):
    by_node = {}
    for r in ctx["records"]:
        by_node.setdefault(r.get("node_id"), []).append(r)
    violations = []
    upgrades = 0
    for nid, recs in by_node.items():
        directs = [r for r in recs if r.get("evidence_strength") == "direct"]
        contradicted = [r for r in recs if r.get("evidence_strength") == "contradicted"]
        if directs and not contradicted:
            upgrades += 1
            for r in directs:
                a = r.get("anchor")
                if not (isinstance(a, dict) and a.get("chapter") and r.get("direction")):
                    violations.append("%s/%s 无锚点升级" % (nid, r.get("record_id")))
    lines = ["升级节点 = %d；无锚点升级 = %d" % (upgrades, len(violations))]
    for v in violations[:ctx["show"]]:
        lines.append("  ! " + v)
    return result("PASS" if not violations else "FAIL", lines)


def strip_ws(s):
    return re.sub(r"\s+", "", s or "")


def book_text(root, source_id):
    """返回 (kind, text)；kind ∈ {'text','missing'}。"""
    if source_id == "BK-023":
        paths = sorted(glob.glob(os.path.join(root, "01-books", "_files", "P0-11", "ddia-zh-src", "*.md")))
    elif source_id == "BK-007":
        paths = [os.path.join(root, VERIFY_DIR, "_text", "clean-architecture.txt")]
    elif source_id == "BK-009":
        paths = [os.path.join(root, VERIFY_DIR, "_text", "saip.txt")]
    else:
        return "missing", ""
    chunks = []
    for p in paths:
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="ignore") as f:
                chunks.append(f.read())
    if not chunks:
        return "missing", ""
    return "text", strip_ws("\n".join(chunks))


def check_gv5(ctx):
    by_source = {}
    for r in ctx["records"]:
        claim = strip_ws(r.get("claim", ""))
        if len(claim) >= LCSUB_MIN:
            by_source.setdefault(r.get("source_id"), {})
            for i in range(len(claim) - LCSUB_MIN + 1):
                by_source[r.get("source_id")].setdefault(claim[i:i + LCSUB_MIN], []).append(r.get("record_id"))
    hits = []
    available = []
    missing = []
    for sid in sorted(by_source):
        kind, text = book_text(ctx["root"], sid)
        if kind != "text":
            missing.append(sid)
            continue
        available.append(sid)
        if len(text) < LCSUB_MIN:
            continue
        for i in range(len(text) - LCSUB_MIN + 1):
            gram = text[i:i + LCSUB_MIN]
            if gram in by_source[sid]:
                hits.append((sid, gram, sorted(set(by_source[sid][gram]))[:3]))
    if not available:
        lines = ["书文本不可用（缺失源 %s）→ SKIP，未做改写检查" % ", ".join(missing or ["all"])]
        return result("SKIP", lines)
    lines = ["可用书文本源 %s；缺失 %s；命中 ≥%d 字子串 = %d"
             % (", ".join(available), ", ".join(missing) or "无", LCSUB_MIN, len(hits))]
    for sid, gram, rids in hits[:ctx["show"]]:
        lines.append("  ! %s 命中 %r（%s）" % (sid, gram, ",".join(rids)))
    if missing:
        lines.append("  （缺失源记 SKIP：%s）" % ", ".join(missing))
    return result("PASS" if not hits else "FAIL", lines)


def iter_json_files(ctx):
    files = [resolve(ctx["root"], p) for p in
             (LEDGER_REL, TOC_REL, GAPS_REL, CLAIMS_REL, OVERRIDES_REL)]
    files += sorted(glob.glob(os.path.join(ctx["root"], VERIFY_DIR, "_parts", "*.json")))
    return [p for p in files if os.path.isfile(p)]


def check_gv6(ctx):
    problems = []
    for p in iter_json_files(ctx):
        with open(p, "rb") as f:
            raw = f.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            problems.append("%s 含 BOM" % os.path.relpath(p, ctx["root"]))
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            problems.append("%s 非 UTF-8: %s" % (os.path.relpath(p, ctx["root"]), e))
            continue
        if "\ufffd" in text:
            problems.append("%s 含 U+FFFD" % os.path.relpath(p, ctx["root"]))
    lines = ["检查文件 %d 个；问题 %d" % (len(iter_json_files(ctx)), len(problems))]
    for p in problems[:ctx["show"]]:
        lines.append("  ! " + p)
    return result("PASS" if not problems else "FAIL", lines)


def check_gv7(ctx):
    script = os.path.join(HERE, "derive_verification.py")
    proc = subprocess.run([sys.executable, script, "--check", "--root", ctx["root"]],
                          capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0 and "[SKIP]" in out:
        return result("SKIP", ["derive --check 报告 SKIP（无分片）"])
    ok = proc.returncode == 0
    lines = ["derive --check 退出码 = %d" % proc.returncode]
    for ln in out.strip().splitlines()[-ctx["show"]:]:
        lines.append("  | " + ln)
    return result("PASS" if ok else "FAIL", lines)


def check_gv8(ctx):
    covered = {r.get("node_id") for r in ctx["records"] if r.get("node_id")}
    ov = ctx["overrides"]
    if ov is None:
        if not covered:
            return result("PASS", ["overrides 缺失且无覆盖节点（0==0）"])
        return result("FAIL", ["overrides 缺失，但 ledger 覆盖 %d 节点" % len(covered)])
    got = set((ov.get("overrides") or {}).keys())
    missing = sorted(covered - got)
    extra = sorted(got - covered)
    lines = ["应覆盖 %d / 实际覆盖 %d；遗漏 %d；越界 %d"
             % (len(covered), len(got), len(missing), len(extra))]
    for n in missing[:ctx["show"]]:
        lines.append("  ! 遗漏 " + n)
    for n in extra[:ctx["show"]]:
        lines.append("  ! 越界 " + n)
    return result("PASS" if not missing and not extra else "FAIL", lines)


CHECKS = {
    "G-V1": check_gv1,
    "G-V2": check_gv2,
    "G-V3": check_gv3,
    "G-V4": check_gv4,
    "G-V5": check_gv5,
    "G-V6": check_gv6,
    "G-V7": check_gv7,
    "G-V8": check_gv8,
}


def build_ctx(root):
    ledger, err = safe_load(resolve(root, LEDGER_REL))
    if err:
        return None, err
    toc, _ = safe_load(resolve(root, TOC_REL))
    gaps_doc, _ = safe_load(resolve(root, GAPS_REL))
    overrides, _ = safe_load(resolve(root, OVERRIDES_REL))
    toc_by_source = {}
    if isinstance(toc, dict):
        toc_by_source = {k: (v.get("toc") if isinstance(v, dict) else None)
                         for k, v in (toc.get("books") or {}).items()}
    return {
        "root": root,
        "ledger": ledger,
        "records": (ledger or {}).get("records", []) or [],
        "gaps": (gaps_doc or {}).get("gaps", []) or [],
        "toc_by_source": toc_by_source,
        "overrides": overrides,
    }, None


def main():
    ap = argparse.ArgumentParser(description="阶段7 核验层门控 G-V1..G-V8")
    ap.add_argument("--check", default="all", help="all 或逗号分隔的判据名，如 G-V1,G-V4")
    ap.add_argument("--root", default=ROOT_DEFAULT, help="母库 root（默认脚本上级目录）")
    ap.add_argument("--show", type=int, default=20)
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.check.strip().lower() == "all":
        selected = list(ALL_CRITERIA)
    else:
        selected = [c.strip() for c in args.check.split(",") if c.strip()]
    unknown = [c for c in selected if c not in CHECKS]
    if unknown:
        print("未知判据: %s" % ", ".join(unknown))
        sys.exit(2)

    verify_dir = resolve(root, VERIFY_DIR)
    ledger_path = resolve(root, LEDGER_REL)
    print("== 阶段7 核验层门控 ==")
    print("root   = %s" % root)
    print("verify = %s" % verify_dir)
    print("")
    if not os.path.isdir(verify_dir) or not os.path.isfile(ledger_path):
        print("[SKIPPED] 私有核验层不存在（%s）" % ledger_path)
        print("== 结果 = SKIPPED ==")
        sys.exit(0)

    ctx, err = build_ctx(root)
    if err:
        print("[FAIL] G-V1 核验层 JSON 非法: %s" % err)
        print("== 结果 = FAIL ==")
        sys.exit(1)
    ctx["show"] = args.show

    counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0}
    fails = []
    for c in selected:
        status, lines = CHECKS[c](ctx)
        counts[status] = counts.get(status, 0) + 1
        if status == "FAIL":
            fails.append(c)
        print("[%s] %s" % (status, c))
        for ln in lines:
            print("    " + ln)
        print("")

    print("== 汇总 ==")
    print("  PASS=%d FAIL=%d WARN=%d SKIP=%d" % (counts["PASS"], counts["FAIL"], counts["WARN"], counts["SKIP"]))
    overall = "FAIL" if fails else "PASS"
    if fails:
        print("  失败判据: %s" % ", ".join(fails))
    print("== 结果 = %s ==" % overall)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
