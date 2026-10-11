#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_densify.py — 阶段7 阶段2 合并回写器（**主Agent 唯一写入方**，确定性、无时间戳）

把子Agent 产出的 `_densify/write-<node_id>.json` 合并回写为 SSOT 与数据层：
  1) `_verify/_parts/ledger-<slug>.json`   追加阶段2 记录（record_id 前缀 VR-D2-）
  2) `_verify/_parts/claims-<slug>.json`   追加主张到**该节点既有键**（reverse-only 节点新建键）
  3) `10-dag-data/_parts/<batch>.json`     写回正文五段（`_base.json` 的 4 个种子节点就地改写）

落点依据：`_densify/precheck-coverage.json` 的 `body_shard` 与 `claims_target_slug`
（由 derive_densify.py --precheck 实测产出，勿按书/域推测）。

用法：
  python3 16-checkpoint/merge_densify.py --check     # 只读：打印将写入的差异摘要
  python3 16-checkpoint/merge_densify.py --apply     # 实际写盘（幂等：重跑不重复追加）
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

DENSIFY = os.path.join("01-books", "_verify", "_densify")
PARTS = os.path.join("01-books", "_verify", "_parts")
DAG_DIR = "10-dag-data"
SEGMENTS = ("definition", "principle", "mechanism", "engineering", "tradeoff")
RECORD_PREFIX = "VR-D2-"
REVIEW_DATE = "2026-09-11"          # 冻结常量
SLUG_SOURCE = {"ddia": "BK-023", "clean-architecture": "BK-007", "saip": "BK-009"}


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_writes(root):
    """读 write-*.json；不可解析/未完成的文件一律跳过并记录（fail-closed，绝不带病合并）。"""
    out = {}
    bad = []
    for p in sorted(glob.glob(resolve(root, os.path.join(DENSIFY, "write-*.json")))):
        try:
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception as e:                               # noqa: BLE001
            bad.append({"file": os.path.basename(p), "error": str(e)[:120]})
            continue
        nid = doc.get("node_id")
        if not nid:
            bad.append({"file": os.path.basename(p), "error": "missing node_id"})
            continue
        segs = doc.get("segments") or {}
        ph = [s for s in SEGMENTS if "PLACEHOLDER" in (segs.get(s) or "")]
        if ph:
            bad.append({"file": os.path.basename(p), "error": "placeholder segments: %s" % ",".join(ph)})
            continue
        out[nid] = doc
    return out, bad


def load_evidence(root):
    out = {}
    for p in sorted(glob.glob(resolve(root, os.path.join(DENSIFY, "evidence-*.json")))):
        doc = load(p)
        for it in doc.get("items", []) or []:
            if it.get("evidence_id"):
                out[it["evidence_id"]] = it
    return out


def next_record_index(ledger_docs):
    """扫描既有 VR-D2- 记录，返回下一个可用序号。"""
    mx = 0
    for doc in ledger_docs.values():
        for r in doc.get("records", []) or []:
            rid = str(r.get("record_id", ""))
            if rid.startswith(RECORD_PREFIX):
                try:
                    mx = max(mx, int(rid[len(RECORD_PREFIX):]))
                except ValueError:
                    pass
    return mx + 1


def existing_d2_claim_ids(ledger_docs):
    ids = set()
    for doc in ledger_docs.values():
        for r in doc.get("records", []) or []:
            if str(r.get("record_id", "")).startswith(RECORD_PREFIX):
                ids.add(r.get("claim_id"))
    return ids


def build_plan(root):
    pre = load(resolve(root, os.path.join(DENSIFY, "precheck-coverage.json")))
    writes, bad_writes = load_writes(root)
    evidence = load_evidence(root)

    ledger_docs = {}
    for slug in SLUG_SOURCE:
        p = resolve(root, os.path.join(PARTS, "ledger-%s.json" % slug))
        if os.path.isfile(p):
            ledger_docs[slug] = load(p)
    claims_docs = {}
    for slug in SLUG_SOURCE:
        p = resolve(root, os.path.join(PARTS, "claims-%s.json" % slug))
        if os.path.isfile(p):
            claims_docs[slug] = load(p)

    idx = next_record_index(ledger_docs)
    already = existing_d2_claim_ids(ledger_docs)

    plan = {"ledger": [], "claims": [], "bodies": [], "skipped_claims": [], "problems": [],
            "bad_writes": bad_writes}
    for node_id in sorted(writes):
        doc = writes[node_id]
        info = pre["nodes"].get(node_id)
        if not info:
            plan["problems"].append("%s 不在 precheck 参与节点集" % node_id)
            continue
        slug = info["claims_target_slug"]
        if slug not in SLUG_SOURCE:
            plan["problems"].append("%s claims 落点 slug 非法: %r" % (node_id, slug))
            continue

        for nc in doc.get("new_claims", []) or []:
            cid = nc.get("claim_id")
            if cid in already:
                plan["skipped_claims"].append(cid)
                continue
            ev_ids = []
            prov = doc.get("provenance") or {}
            for s in SEGMENTS:
                ev_ids += list(prov.get(s) or [])
            note = ""
            for eid in ev_ids:
                it = evidence.get(eid)
                if it and it.get("claim_id") == cid:
                    note = it.get("text", "")[:200]
                    break
            rec = {
                "record_id": "%s%03d" % (RECORD_PREFIX, idx),
                "node_id": node_id,
                "source_id": SLUG_SOURCE[slug],
                "direction": nc.get("direction", "forward"),
                "claim_id": cid,
                "claim": nc.get("text", ""),
                "anchor": nc.get("anchor") or {},
                "page_anchor_private": nc.get("page_anchor_private"),
                "evidence_strength": nc.get("evidence_strength", "partial"),
                "evidence_note": note or "阶段2 增密新增主张（证据素材见 _densify/evidence-%s.json）" % slug,
                "review": {
                    "reviewed_by": doc.get("writer", "w-nodewriter"),
                    "review_date": REVIEW_DATE,
                    "second_pass": nc.get("second_pass", "passed"),
                    "second_pass_by": "w3-densify-secondpass",
                },
            }
            plan["ledger"].append({"slug": slug, "record": rec})
            plan["claims"].append({"slug": slug, "node_id": node_id,
                                   "claim": {"claim_id": cid, "text": nc.get("text", ""),
                                             "origin": cid.split("#")[1] if cid.count("#") >= 2 else "definition"}})
            idx += 1

        # 正文落点
        shard = info["body_shard"]
        if not shard:
            plan["problems"].append("%s 正文落点未解析" % node_id)
            continue
        plan["bodies"].append({"node_id": node_id, "shard": shard,
                               "segments": doc.get("segments") or {}})
    return plan


def apply_plan(root, plan):
    # 1) ledger
    touched = set()
    for item in plan["ledger"]:
        slug = item["slug"]
        p = resolve(root, os.path.join(PARTS, "ledger-%s.json" % slug))
        doc = load(p)
        doc.setdefault("records", []).append(item["record"])
        dump(p, doc)
        touched.add(p)
    # 2) claims
    for item in plan["claims"]:
        slug = item["slug"]
        p = resolve(root, os.path.join(PARTS, "claims-%s.json" % slug))
        doc = load(p)
        entry = doc.get(item["node_id"])
        if not isinstance(entry, dict):
            entry = {"claims": []}
            doc[item["node_id"]] = entry
        entry.setdefault("claims", []).append(item["claim"])
        dump(p, doc)
        touched.add(p)
    # 3) bodies（按分片聚合一次写）
    by_shard = {}
    for b in plan["bodies"]:
        by_shard.setdefault(b["shard"], []).append(b)
    for shard, items in sorted(by_shard.items()):
        p = resolve(root, shard)
        doc = load(p)
        by_id = {n["id"]: n for n in doc.get("nodes", []) or []}
        for b in items:
            node = by_id.get(b["node_id"])
            if node is None:
                plan["problems"].append("分片 %s 中无节点 %s" % (shard, b["node_id"]))
                continue
            segs = b["segments"]
            node["definition"] = segs.get("definition", node.get("definition", ""))
            det = node.get("detail") or {}
            for k in ("principle", "mechanism", "engineering", "tradeoff"):
                if k in segs:
                    det[k] = segs[k]
            node["detail"] = det
        dump(p, doc)
        touched.add(p)
    return touched


def main():
    ap = argparse.ArgumentParser(description="阶段2 合并回写（主Agent 唯一写入方）")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true", help="只读：打印差异摘要")
    ap.add_argument("--apply", action="store_true", help="实际写盘")
    args = ap.parse_args()
    if not (args.check or args.apply):
        ap.error("必须指定 --check 或 --apply")
    root = os.path.abspath(args.root)
    plan = build_plan(root)

    print("[plan] 新增 ledger 记录 %d 条（跳过已存在 %d）"
          % (len(plan["ledger"]), len(plan["skipped_claims"])))
    print("[plan] 新增 claims 条目 %d 条；正文写回 %d 节点" % (len(plan["claims"]), len(plan["bodies"])))
    by_slug = {}
    for it in plan["ledger"]:
        by_slug[it["slug"]] = by_slug.get(it["slug"], 0) + 1
    print("[plan] 按 claims 分片: %s" % json.dumps(by_slug, ensure_ascii=False))
    shards = {}
    for b in plan["bodies"]:
        shards[b["shard"]] = shards.get(b["shard"], 0) + 1
    print("[plan] 正文分片: %s" % json.dumps(shards, ensure_ascii=False))
    for p in plan["problems"]:
        print("[WARN] %s" % p)
    for b in plan.get("bad_writes", []):
        print("[SKIP-BAD] %s :: %s" % (b["file"], b["error"]))

    if args.check:
        print("== --check 完成（未写盘） ==")
        return 0 if not plan["problems"] else 1

    touched = apply_plan(root, plan)
    for p in sorted(touched):
        print("[write] %s" % os.path.relpath(p, root))
    print("== --apply 完成：%d 个文件 ==" % len(touched))
    return 0


if __name__ == "__main__":
    sys.exit(main())
