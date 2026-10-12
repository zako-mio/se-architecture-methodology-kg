#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_secondpass_worklists.py — 把「恢复记录」的第二路复核结论合并进 `<slug>` 的裁决文件

输入：`01-books/_verify/_review/secondpass-worklist-NN-verdicts.json`（复核工人产出）
输出：`01-books/_verify/_review/secondpass-<slug>.json`（`apply_secondpass.py` 的输入）

要点：
- 按 `record_id` 去重（幂等）：已存在的 verdict 以**新产出**为准（复核可重跑）。
- `claim_id` **以当前 ledger 为准**归一化：恢复时曾对 11 条撞号记录重编号，
  工单里的 `claim_id` 是重编号前的旧值。
- 只写 `_review/`，不改任何 SSOT。

用法：
  python3 16-checkpoint/merge_secondpass_worklists.py --check
  python3 16-checkpoint/merge_secondpass_worklists.py
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
VERIFY = os.path.join("01-books", "_verify")
REVIEW = os.path.join(VERIFY, "_review")
PARTS = os.path.join(VERIFY, "_parts")


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main():
    ap = argparse.ArgumentParser(description="合并第二路复核工单结论")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true", help="只读：报告将写入的内容")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    # record_id → (slug, claim_id) 以当前 ledger 为准
    rid2slug, rid2cid = {}, {}
    for p in sorted(glob.glob(os.path.join(resolve(root, PARTS), "ledger-*.json"))):
        slug = os.path.basename(p)[len("ledger-"):-len(".json")]
        for r in load(p).get("records") or []:
            rid2slug[r.get("record_id")] = slug
            rid2cid[r.get("record_id")] = r.get("claim_id")

    incoming = {}
    files = sorted(glob.glob(os.path.join(resolve(root, REVIEW),
                                          "secondpass-worklist-*-verdicts.json")))
    for p in files:
        doc = load(p)
        for v in doc.get("verdicts") or []:
            rid = v.get("record_id")
            if not rid:
                continue
            v = dict(v)
            v["claim_id"] = rid2cid.get(rid, v.get("claim_id"))
            v["second_pass_by"] = doc.get("reviewed_by", "")
            incoming[rid] = v
    print("== 第二路复核工单合并 ==")
    print("工单文件 %d 个；verdict %d 条" % (len(files), len(incoming)))

    by_slug = {}
    for rid, v in incoming.items():
        slug = rid2slug.get(rid)
        if not slug:
            print("  ! %s 不在任何 ledger 分片（跳过）" % rid)
            continue
        by_slug.setdefault(slug, {})[rid] = v

    for slug in sorted(by_slug):
        vp = resolve(root, os.path.join(REVIEW, "secondpass-%s.json" % slug))
        doc = load(vp) if os.path.isfile(vp) else {
            "reviewed_by": "w-p1-secondpass（合并）", "review_date": "2026-10-12",
            "verdicts": []}
        existing = {v.get("record_id"): v for v in doc.get("verdicts") or []}
        added = updated = 0
        for rid, v in by_slug[slug].items():
            if rid in existing:
                existing[rid] = v
                updated += 1
            else:
                existing[rid] = v
                added += 1
        doc["verdicts"] = [existing[k] for k in sorted(existing)]
        print("  [%s] 新增 %d / 更新 %d → 共 %d 条 verdict"
              % (slug, added, updated, len(doc["verdicts"])))
        if args.check:
            continue
        os.makedirs(os.path.dirname(vp), exist_ok=True)
        with open(vp, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(doc))
        print("    wrote %s" % os.path.relpath(vp, root))

    if args.check:
        print("== --check：未写盘 ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
