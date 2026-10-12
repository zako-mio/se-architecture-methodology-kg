#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_duplicate_claim_ids.py — 修历史重复 `claim_id`（阶段1 遗留），确定性重编号

背景：核验层要求 `claim_id` **全局唯一**（`gate_verification.py` 的 G-V1 唯一性判据；
2026-10-12 起重复由 WARN 提升为 FAIL）。阶段1 遗留 1 组重复：

    ESS-O-02#principle#1  ←  VR-CA-030（BK-007，讲「细节可推迟」）
                          ←  VR-DDIA-009（BK-023，讲「数据系统取舍」）

两条记录**语义不同 ⇒ 不得合并**。本脚本按 `record_id` 字典序保留首条，
把后到者重编号为该 `<node_id>#<origin>#<n>` 的**下一个空号**。

同步点（缺一即数据不一致）：
  1. `01-books/_verify/_parts/ledger-<slug>.json`（SSOT 分片）
  2. `01-books/_verify/_review/staging/ledger-<prefix>-*.json`（按 record_id 对齐；该书无暂存则跳过）
  3. `01-books/_verify/_review/secondpass-*.json` 的 verdict（按 record_id 对齐）
派生物（`verification-ledger.json` / `node-claim-map.json`）**不在此改**，
由 `derive_verification.py` 再生。

性质：确定性（无时间戳）、UTF-8 无 BOM、`ensure_ascii=False, indent=2` + 末尾换行。

用法：
  python3 16-checkpoint/fix_duplicate_claim_ids.py --check    # 只读：报告将做的改动
  python3 16-checkpoint/fix_duplicate_claim_ids.py            # 写入（并落报告）
"""
import argparse
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

VERIFY = os.path.join("01-books", "_verify")
PARTS = os.path.join(VERIFY, "_parts")
STAGING = os.path.join(VERIFY, "_review", "staging")
REVIEW = os.path.join(VERIFY, "_review")
REPORT_REL = os.path.join(VERIFY, "_meta", "duplicate-claimid-fix-report.json")

CID_RE = re.compile(r"^(?P<node>(?:ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2})#(?P<origin>[a-z]+)#(?P<n>\d+)$")
PART_FILE_RE = re.compile(r"^(ledger|claims|toc|gaps)-(.+)\.json$")


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def ledger_files(root, kind="parts"):
    base = resolve(root, PARTS if kind == "parts" else STAGING)
    return sorted(glob.glob(os.path.join(base, "ledger-*.json")))


def secondpass_files(root):
    return sorted(glob.glob(os.path.join(resolve(root, REVIEW), "secondpass-*.json")))


def find_duplicates(root):
    """返回 {claim_id: [(record_id, slug, path)]}（仅含 len>1 的组）。"""
    groups = {}
    for path in ledger_files(root):
        doc = load(path)
        slug = os.path.basename(path)[len("ledger-"):-len(".json")]
        for r in doc.get("records") or []:
            cid = r.get("claim_id")
            if not cid:
                continue
            groups.setdefault(cid, []).append((r.get("record_id", ""), slug, path))
    return {c: v for c, v in groups.items() if len(v) > 1}


def all_claim_ids(root):
    ids = set()
    for path in ledger_files(root):
        doc = load(path)
        for r in doc.get("records") or []:
            if r.get("claim_id"):
                ids.add(r["claim_id"])
    return ids


def next_free(node, origin, taken):
    n = 1
    while "%s#%s#%d" % (node, origin, n) in taken:
        n += 1
    return "%s#%s#%d" % (node, origin, n)


def plan_renames(root):
    """返回 (renames, unresolved)。renames: [(record_id, old_cid, new_cid, slug)]。"""
    dups = find_duplicates(root)
    taken = all_claim_ids(root)
    renames, unresolved = [], []
    for cid in sorted(dups):
        entries = sorted(dups[cid], key=lambda x: x[0])
        m = CID_RE.match(cid)
        if not m:
            unresolved.append((cid, "claim_id 格式非法，无法重编号"))
            continue
        node, origin = m.group("node"), m.group("origin")
        for rid, slug, _ in entries[1:]:
            new_cid = next_free(node, origin, taken)
            taken.add(new_cid)
            renames.append((rid, cid, new_cid, slug))
    return renames, unresolved


def apply_to_parts(root, renames):
    touched = []
    by_rid = {rid: new for rid, _, new, _ in renames}
    for path in ledger_files(root):
        doc = load(path)
        changed = False
        for r in doc.get("records") or []:
            if r.get("record_id") in by_rid:
                r["claim_id"] = by_rid[r["record_id"]]
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(doc))
            touched.append(path)
    return touched


def apply_to_staging(root, renames):
    touched = []
    by_rid = {rid: new for rid, _, new, _ in renames}
    for path in ledger_files(root, kind="staging"):
        doc = load(path)
        changed = False
        for r in doc.get("records") or []:
            if r.get("record_id") in by_rid:
                r["claim_id"] = by_rid[r["record_id"]]
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(doc))
            touched.append(path)
    return touched


def apply_to_secondpass(root, renames):
    touched = []
    by_rid = {rid: new for rid, _, new, _ in renames}
    for path in secondpass_files(root):
        doc = load(path)
        changed = False
        for v in doc.get("verdicts") or []:
            if v.get("record_id") in by_rid:
                v["claim_id"] = by_rid[v["record_id"]]
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(doc))
            touched.append(path)
    return touched


def main():
    ap = argparse.ArgumentParser(description="修历史重复 claim_id（确定性重编号）")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true", help="只读：报告将做的改动，不写")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    renames, unresolved = plan_renames(root)
    dups = find_duplicates(root)

    print("== 历史重复 claim_id 修复 ==")
    print("重复组 %d 组；待重编号 %d 条" % (len(dups), len(renames)))
    for cid in sorted(dups):
        entries = sorted(dups[cid], key=lambda x: x[0])
        print("  ! %s" % cid)
        for i, (rid, slug, _) in enumerate(entries):
            keep = "保留" if i == 0 else "重编号"
            print("      [%s] %s (%s)" % (keep, rid, slug))
    for rid, old, new, slug in renames:
        print("  -> %s (%s): %s => %s" % (rid, slug, old, new))
    for cid, why in unresolved:
        print("  ! 未决 %s —— %s" % (cid, why))
    print("")

    if args.check:
        print("== --check：未写入任何文件 ==")
        return 0 if not unresolved else 1

    touched = apply_to_parts(root, renames)
    touched += apply_to_staging(root, renames)
    touched += apply_to_secondpass(root, renames)
    for p in touched:
        print("  wrote %s" % os.path.relpath(p, root))

    report = {
        "meta": {"schema_version": "1.0.0", "generated": "2026-09-11"},
        "duplicate_groups": len(dups),
        "renames": [{"record_id": rid, "old_claim_id": old, "new_claim_id": new,
                     "slug": slug} for rid, old, new, slug in renames],
        "unresolved": [{"claim_id": c, "reason": w} for c, w in unresolved],
        "files_written": sorted(os.path.relpath(p, root) for p in touched),
    }
    rp = resolve(root, REPORT_REL)
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    with open(rp, "w", encoding="utf-8", newline="\n") as f:
        f.write(dumps(report))
    print("  wrote %s" % REPORT_REL)

    # 回读复验：重复组必须归零
    left = find_duplicates(root)
    print("== 回读：剩余重复组 %d ==" % len(left))
    return 0 if not left and not unresolved else 1


if __name__ == "__main__":
    sys.exit(main())
