#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_secondpass_worklist.py — 为「恢复的被裁记录」生成第二路复核工单（分片）

背景（2026-10-12）：P1 从会话转录恢复了 42 条被裁记录，按 ADR-005 边界裁回 8 条域外记录，
在域 34 条（direct 24 / partial 10）。项目硬判据要求**全部 direct 有第二路 verdict**，
故须为这 24 条 direct 补一轮独立复核。

本脚本只产**工单**（只读 + 写 `_review/`），不改任何 SSOT；复核结论由复核工人产出后，
由主 Agent 合并进 `_review/secondpass-workbook.json` 并跑 `apply_secondpass.py --all`。

用法：
  python3 16-checkpoint/make_secondpass_worklist.py --parts 2
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
VERIFY = os.path.join("01-books", "_verify")
REVIEW = os.path.join(VERIFY, "_review")
PARTS = os.path.join(VERIFY, "_parts")
RECOVERY_REL = os.path.join(VERIFY, "_meta", "trimmed-recovery.json")


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main():
    ap = argparse.ArgumentParser(description="生成恢复记录的第二路复核工单")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--parts", type=int, default=2)
    ap.add_argument("--strength", default="direct", help="只纳入该强度的记录")
    ap.add_argument("--slug", help="从 `_parts/ledger-<slug>.json` 取记录（新书用；缺省走 P1 恢复报告）")
    ap.add_argument("--tag", default=None, help="工单文件名标签（缺省用 slug）")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.slug:
        led = json.load(open(resolve(root, os.path.join(PARTS, "ledger-%s.json" % args.slug)),
                            encoding="utf-8"))
        covered = set()
        import glob as _glob
        for f in _glob.glob(os.path.join(resolve(root, REVIEW), "secondpass-*.json")):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except ValueError:
                continue
            for v in d.get("verdicts") or []:
                covered.add(v.get("record_id"))
        rows = [r for r in led.get("records") or []
                if r.get("evidence_strength") == args.strength
                and r.get("record_id") not in covered]
        tag = args.tag or args.slug
        note = "新书 %s 的 %s 复核工单（只读输入；结论由主 Agent 合并）" % (args.slug, args.strength)
    else:
        rec = json.load(open(resolve(root, RECOVERY_REL), encoding="utf-8"))
        removed = {x["record_id"] for x in rec.get("out_of_domain_removed", [])}
        rows = [r for r in rec["records"]
                if r["record_id"] not in removed and r.get("evidence_strength") == args.strength]
        tag = "p1-recovery"
        note = "恢复记录的第二路复核工单（只读输入；结论由主 Agent 合并）"
    rows.sort(key=lambda r: r["record_id"])

    parts = [[] for _ in range(args.parts)]
    for i, r in enumerate(rows):
        parts[i % args.parts].append(r)

    written = []
    for i, chunk in enumerate(parts, 1):
        rel = os.path.join(REVIEW, "secondpass-worklist-%s-%02d.json" % (tag, i))
        doc = {
            "meta": {"schema_version": "1.0.0", "generated": "2026-09-11", "note": note},
            "part": i,
            "of": args.parts,
            "slug": args.slug,
            "strength_filter": args.strength,
            "records": [{
                "record_id": r["record_id"],
                "node_id": r["node_id"],
                "source_id": r["source_id"],
                "claim_id": r["claim_id"],
                "claim": r.get("claim", ""),
                "anchor": r.get("anchor"),
                "first_pass_strength": r.get("evidence_strength"),
                "first_pass_note": r.get("evidence_note", ""),
            } for r in chunk],
        }
        p = resolve(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(doc))
        written.append((rel, len(chunk)))
        print("  wrote %s（%d 条）" % (rel, len(chunk)))

    print("== 工单合计 %d 条（%s）==" % (len(rows), args.strength))
    return 0


if __name__ == "__main__":
    sys.exit(main())
