#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
derive_verification.py — 阶段7 核验层确定性派生器

唯一真相源：01-books/_verify/_parts/{ledger,claims,toc,gaps}-<slug>.json
输出（全部确定性、无时间戳、稳定排序、UTF-8 无 BOM、末尾换行）：
  01-books/_verify/verification-ledger.json   核验记录主表
  01-books/_verify/node-claim-map.json        节点 → 原子主张拆分
  01-books/_verify/book-toc-index.json        书 TOC / 章节索引
  01-books/_verify/reverse-gaps.json          反向发现缺口清单
  10-dag-data/_verification-overrides.json    派生覆盖集（仅被覆盖节点）
  10-dag-data/book-verification.json           书证核验的公开安全投影（章节级元数据，无正文）

用法：
  python3 16-checkpoint/derive_verification.py [--root <MROOT>]
  python3 16-checkpoint/derive_verification.py --check   # 幂等自检（只读，连算两次比对）
"""
import argparse
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
GENERATED = "2026-09-11"          # 冻结常量：禁止 datetime.date.today() / time.time()
SCHEMA_VERSION = "1.0.0"
SLUG_ORDER = ("clean-architecture", "ddia", "saip")  # 仅用于遍历；输出按 source_id/node_id 排序
SLUG_SOURCE = {"ddia": "BK-023", "clean-architecture": "BK-007", "saip": "BK-009"}

LEDGER_DIR = os.path.join("01-books", "_verify")
PARTS_DIR = os.path.join(LEDGER_DIR, "_parts")
OVERRIDES_PATH = os.path.join("10-dag-data", "_verification-overrides.json")
BASELINE_PATH = os.path.join("10-dag-data", "_verification-baseline.json")
DAG_PATH = os.path.join("10-dag-data", "methodology-dag.json")

OUT_LEDGER = os.path.join(LEDGER_DIR, "verification-ledger.json")
OUT_CLAIMS = os.path.join(LEDGER_DIR, "node-claim-map.json")
OUT_TOC = os.path.join(LEDGER_DIR, "book-toc-index.json")
OUT_GAPS = os.path.join(LEDGER_DIR, "reverse-gaps.json")
OUT_BOOK_VERIFICATION = os.path.join("10-dag-data", "book-verification.json")

OUTPUT_PATHS = [OUT_LEDGER, OUT_CLAIMS, OUT_TOC, OUT_GAPS, OVERRIDES_PATH,
                OUT_BOOK_VERIFICATION]

# 公开安全投影：仅允许的章节级字段（白名单）；claim/evidence_note/
# page_anchor_private/record_id 一律禁止进入公开层（版权红线）。
BOOK_VERIFICATION_NOTE = (
    "书证核验的公开安全投影：仅章节级引用元数据（信源 id + 章/节编号与标题 + 强度 + "
    "方向 + 复核状态 + 日期）。不含 claim 文本、页码、摘句；gaps.summary 为改写摘要。"
)


def default_root():
    return os.path.dirname(HERE)


def resolve(root, path):
    return path if os.path.isabs(path) else os.path.join(root, path)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def load_opt(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_parts(root, prefix):
    """返回 {slug: doc}，仅含存在的分片。"""
    out = {}
    for slug in SLUG_ORDER:
        p = os.path.join(resolve(root, PARTS_DIR), "%s-%s.json" % (prefix, slug))
        doc = load_opt(p)
        if doc is not None:
            out[slug] = doc
    return out


def meta(with_sot):
    m = {"schema_version": SCHEMA_VERSION, "generated": GENERATED}
    if with_sot:
        m["source_of_truth"] = True
    return m


def build_ledger(ledger_parts):
    records = []
    seen = set()
    for slug in SLUG_ORDER:
        doc = ledger_parts.get(slug)
        if doc is None:
            continue
        for r in doc.get("records", []) or []:
            rid = r.get("record_id")
            if rid in seen:
                raise ValueError("duplicate record_id: %s" % rid)
            seen.add(rid)
            records.append(r)
    records.sort(key=lambda r: r.get("record_id", ""))
    return {"meta": meta(True), "records": records}


def build_claims(claims_parts):
    nodes = {}
    for slug in SLUG_ORDER:
        doc = claims_parts.get(slug)
        if doc is None:
            continue
        for node_id, node_doc in doc.items():
            if node_id not in nodes:
                nodes[node_id] = node_doc
    ordered = {}
    for node_id in sorted(nodes):
        claims = list(nodes[node_id].get("claims", []) or [])
        claims.sort(key=lambda c: c.get("claim_id", ""))
        ordered[node_id] = {"claims": claims}
    return {"meta": meta(False), "nodes": ordered}


def build_toc(toc_parts):
    books = {}
    for slug in SLUG_ORDER:
        doc = toc_parts.get(slug)
        if doc is None:
            continue
        sid = doc.get("source_id") or SLUG_SOURCE.get(slug, "")
        books[sid] = {
            "book": doc.get("book", ""),
            "edition": doc.get("edition", ""),
            "toc": list(doc.get("toc", []) or []),
        }
    ordered = {}
    for sid in sorted(books):
        ordered[sid] = books[sid]
    return {"meta": meta(False), "books": ordered}


def build_gaps(gaps_parts):
    gaps = []
    seen = set()
    for slug in SLUG_ORDER:
        doc = gaps_parts.get(slug)
        if doc is None:
            continue
        for g in doc.get("gaps", []) or []:
            gid = g.get("gap_id")
            if gid in seen:
                raise ValueError("duplicate gap_id: %s" % gid)
            seen.add(gid)
            gaps.append(g)
    gaps.sort(key=lambda g: g.get("gap_id", ""))
    return {"meta": meta(False), "gaps": gaps}


def _natkey(value):
    """章节号自然序键（"10" 排在 "2" 之后；兼容非数字与空值）。"""
    out = []
    for part in re.split(r"(\d+)", str(value or "")):
        if part.isdigit():
            out.append((0, int(part), ""))
        else:
            out.append((1, 0, part))
    return out


def build_book_verification(records, toc_books, gaps):
    """构造公开安全投影：仅章节级元数据 + 改写摘要缺口；无 claim/页码/摘句/record_id。"""
    by_node = {}
    for r in records:
        nid = r.get("node_id")
        if not nid:
            continue
        sid = r.get("source_id", "")
        anchor = r.get("anchor") or {}
        review = r.get("review") or {}
        by_node.setdefault(nid, []).append({
            "source_id": sid,
            "book": (toc_books.get(sid) or {}).get("book", ""),
            "chapter": anchor.get("chapter", ""),
            "section": anchor.get("section", ""),
            "section_title": anchor.get("section_title", ""),
            "evidence_strength": r.get("evidence_strength", ""),
            "direction": r.get("direction", ""),
            "second_pass": review.get("second_pass", ""),
            "review_date": review.get("review_date", ""),
        })
    ordered = {}
    for nid in sorted(by_node):
        ordered[nid] = sorted(
            by_node[nid],
            key=lambda x: (x["source_id"], _natkey(x["chapter"]), _natkey(x["section"])),
        )
    proj_gaps = []
    for g in gaps:
        anchor = g.get("anchor") or {}
        target = g.get("target") or {}
        proj_gaps.append({
            "gap_id": g.get("gap_id", ""),
            "kind": g.get("kind", ""),
            "book_source_id": g.get("book_source_id", ""),
            "chapter": anchor.get("chapter", ""),
            "section": anchor.get("section", ""),
            "target": {
                "existing_node_id": target.get("existing_node_id"),
                "proposed_node": target.get("proposed_node"),
            },
            "summary": g.get("summary", ""),
            "proposed_action": g.get("proposed_action", ""),
            "evidence_strength": g.get("evidence_strength", ""),
        })
    proj_gaps.sort(key=lambda x: x["gap_id"])
    return {
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "generated": GENERATED,
            "note": BOOK_VERIFICATION_NOTE,
        },
        "by_node": ordered,
        "gaps": proj_gaps,
    }


def graph_baseline(root):
    """读冻结基线 _verification-baseline.json 的 nodes 映射（节点原 verified/confidence）。

    基线缺失时回退读当前 methodology-dag.json 并打 WARN（此时非纯函数）。
    该文件为冻结快照，本脚本只读、绝不写。
    """
    doc = load_opt(os.path.join(root, BASELINE_PATH))
    if isinstance(doc, dict) and isinstance(doc.get("nodes"), dict):
        return doc["nodes"]
    print("[WARN] baseline 缺失，回退读当前 dag（可能非纯函数）")
    graph = load_opt(os.path.join(root, DAG_PATH))
    if not graph:
        return {}
    return {n.get("id"): {"verified": n.get("verified"), "confidence": n.get("confidence")}
            for n in graph.get("nodes", []) or []}


def build_overrides(records, baseline):
    by_node = {}
    for r in records:
        by_node.setdefault(r.get("node_id"), []).append(r)
    overrides = {}
    for node_id in sorted(k for k in by_node if k):
        if node_id not in baseline:
            print("[WARN] 覆盖节点不在基线中，跳过: %s" % node_id)
            continue
        recs = by_node[node_id]
        contradicted = [r for r in recs if r.get("evidence_strength") == "contradicted"]
        directs = [r for r in recs if r.get("evidence_strength") == "direct"]
        orig = baseline.get(node_id, {})
        errata = []
        if contradicted:
            verified = orig.get("verified")
            confidence = orig.get("confidence")
            for r in contradicted:
                c = r.get("contradiction") or {}
                errata.append({
                    "misconception": r.get("claim", ""),
                    "verified_value": c.get("verified_value", ""),
                    "source_id": r.get("source_id", ""),
                })
        elif directs:
            verified = True
            confidence = "high"
        else:
            verified = orig.get("verified")
            confidence = orig.get("confidence")
        dates = [((r.get("review") or {}).get("review_date") or "") for r in recs]
        overrides[node_id] = {
            "verified": verified,
            "confidence": confidence,
            "review_date": max(dates) if dates else "",
            "errata": errata,
            "_evidence": sorted(r.get("record_id", "") for r in recs),
        }
    return {"meta": meta(True), "overrides": overrides}


def build_outputs(root):
    """返回 (outputs: {relpath: text}, has_data: bool)。无任何分片 → has_data=False。"""
    ledger_parts = load_parts(root, "ledger")
    claims_parts = load_parts(root, "claims")
    toc_parts = load_parts(root, "toc")
    gaps_parts = load_parts(root, "gaps")
    if not (ledger_parts or claims_parts or toc_parts or gaps_parts):
        return {}, False

    outputs = {}
    records = []
    toc_doc = None
    gaps_doc = None
    if ledger_parts:
        ledger = build_ledger(ledger_parts)
        records = ledger["records"]
        outputs[OUT_LEDGER] = dumps(ledger)
    if claims_parts:
        outputs[OUT_CLAIMS] = dumps(build_claims(claims_parts))
    if toc_parts:
        toc_doc = build_toc(toc_parts)
        outputs[OUT_TOC] = dumps(toc_doc)
    if gaps_parts:
        gaps_doc = build_gaps(gaps_parts)
        outputs[OUT_GAPS] = dumps(gaps_doc)
    if records:
        outputs[OVERRIDES_PATH] = dumps(build_overrides(records, graph_baseline(root)))
    gaps_list = (gaps_doc or {}).get("gaps", [])
    if records or gaps_list:
        toc_books = (toc_doc or {}).get("books", {})
        outputs[OUT_BOOK_VERIFICATION] = dumps(
            build_book_verification(records, toc_books, gaps_list))
    return outputs, True


def write_outputs(root, outputs):
    for rel, text in outputs.items():
        path = resolve(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote %s" % rel)


def run_check(root):
    a, has_a = build_outputs(root)
    b, has_b = build_outputs(root)
    if not has_a:
        print("[SKIP] 无核验分片，无需派生")
        return 0
    ok = has_a == has_b and a == b
    for rel in sorted(a):
        same = a.get(rel) == b.get(rel)
        print("  [%s] %s" % ("IDEMPOTENT" if same else "DRIFT", rel))
    for rel in sorted(a):
        path = resolve(root, rel)
        disk = None
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                disk = f.read()
        state = "up-to-date" if disk == a[rel] else ("missing" if disk is None else "stale")
        print("  [%s] %s" % (state, rel))
    print("== 派生幂等自检 = %s ==" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="阶段7 核验层确定性派生器")
    ap.add_argument("--root", default=default_root(), help="母库 root（默认脚本上级目录）")
    ap.add_argument("--check", action="store_true", help="只读幂等自检：连算两次并比对")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.check:
        sys.exit(run_check(root))

    outputs, has_data = build_outputs(root)
    if not has_data:
        print("[SKIP] 无核验分片（01-books/_verify/_parts/ 为空），跳过派生")
        print("== 派生结果 = SKIP ==")
        sys.exit(0)
    write_outputs(root, outputs)
    print("== 派生结果 = PASS（%d 个产物）==" % len(outputs))
    sys.exit(0)


if __name__ == "__main__":
    main()
