#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
register_densify_claims.py — 把 write 文档所引证据中的**新 claim_id** 登记为 `new_claims`

背景：26 个参与节点中有 9 个 reverse-only 节点在核验层**无任何 claim 拆分**。为支撑其增密，
`sparse-*.json` 证据分片为它们新建了 5–6 条主张（`is_new=true`）。这些 claim_id 必须先进入
核验层（ledger + claims 分片），G-D1 才能解析 provenance（否则零悬挂 → FAIL）。

本脚本只**补写 write-<node>.json 的 `new_claims` 字段**（确定性、无时间戳）：
对每个 write 文档，取其 provenance 引用的全部 evidence 条目，凡 `claim_id` 尚未出现在
`verification-ledger.json` 者，生成一条 new_claim（携带 anchor / direction / evidence_strength）。

用法：
  python3 16-checkpoint/register_densify_claims.py --check
  python3 16-checkpoint/register_densify_claims.py --apply
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
LEDGER = os.path.join("01-books", "_verify", "verification-ledger.json")
SEGMENTS = ("definition", "principle", "mechanism", "engineering", "tradeoff")


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_evidence(root):
    out = {}
    for pat in ("evidence-*.json", "sparse-*.json"):
        for p in sorted(glob.glob(resolve(root, os.path.join(DENSIFY, pat)))):
            if os.path.getsize(p) == 0:
                continue
            try:
                doc = load(p)
            except Exception:                                # noqa: BLE001
                continue
            for it in doc.get("items", []) or []:
                if it.get("evidence_id"):
                    out[it["evidence_id"]] = it
    return out


def main():
    ap = argparse.ArgumentParser(description="登记 write 文档的新 claim")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not (args.check or args.apply):
        ap.error("必须指定 --check 或 --apply")
    root = os.path.abspath(args.root)

    ledger = load(resolve(root, LEDGER))
    known = {r.get("claim_id") for r in ledger.get("records", []) or []}
    evidence = load_evidence(root)

    total_new = 0
    changed = []
    for p in sorted(glob.glob(resolve(root, os.path.join(DENSIFY, "write-*.json")))):
        doc = load(p)
        node_id = doc.get("node_id")
        prov = doc.get("provenance") or {}
        cited = []
        for s in SEGMENTS:
            cited += list(prov.get(s) or [])
        new_claims = []
        seen = set()
        for eid in cited:
            it = evidence.get(eid)
            if not it:
                continue
            cid = it.get("claim_id")
            if not cid or cid in known or cid in seen:
                continue
            seen.add(cid)
            new_claims.append({
                "claim_id": cid,
                "text": it.get("text", ""),
                "anchor": it.get("anchor") or {},
                "evidence_strength": it.get("proposed_strength", "partial"),
                "direction": "forward",
            })
        if new_claims:
            total_new += len(new_claims)
            changed.append((node_id, len(new_claims)))
            if args.apply:
                doc["new_claims"] = new_claims
                dump(p, doc)

    print("[%s] 需登记新 claim 的节点 %d 个，合计 %d 条"
          % ("apply" if args.apply else "check", len(changed), total_new))
    for n, c in changed:
        print("   %-11s +%d 条" % (n, c))
    if args.apply:
        print("== 已写回 write-*.json 的 new_claims ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
