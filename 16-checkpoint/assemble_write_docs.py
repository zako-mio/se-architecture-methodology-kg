#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_write_docs.py — 把「分段小文件」装配为 `write-<node_id>.json`

**背景（实测根因）**：子 Agent 的 `write` 工具在单次大负载（≈2.5–3 KB）时会**静默截断**，
且子 Agent 无 shell 无法自查，导致 `write-*.json` 系统性残缺（自报字数虚高 2–46%）。
修复：写入方**每段写一个小文件**（约 400–700 字，远低于截断阈值），本脚本确定性装配。

输入（每节点 6 个文件，落在 `_densify/_seg/`）：
  _seg/<node_id>__meta.json       {"provenance": {...5 键...}, "new_claims": [...], "baseline_chars": N}
  _seg/<node_id>__definition.txt
  _seg/<node_id>__principle.txt
  _seg/<node_id>__mechanism.txt
  _seg/<node_id>__engineering.txt
  _seg/<node_id>__tradeoff.txt

输出：`_densify/write-<node_id>.json`（契约 §3 结构）

用法：
  python3 16-checkpoint/assemble_write_docs.py --check    # 只读：校验分段完整性 + 字数
  python3 16-checkpoint/assemble_write_docs.py --apply    # 装配落盘
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

DENSIFY = os.path.join("01-books", "_verify", "_densify")
SEG_DIR = os.path.join(DENSIFY, "_seg")
SEGMENTS = ("definition", "principle", "mechanism", "engineering", "tradeoff")
REVIEW_DATE = "2026-09-11"
CHAR_MIN, CHAR_MAX = 2400, 3000
# 单段写入上限告警阈值（超过则提示可能截断）
SEG_WARN_CHARS = 1200   # 实测已证 write 无截断（bytes/chars=3.00），仅作极端异常提示


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def read_text(p):
    with open(p, encoding="utf-8") as f:
        return f.read().strip()


def node_ids(root):
    ids = set()
    for p in sorted(glob.glob(resolve(root, os.path.join(SEG_DIR, "*__meta.json")))):
        ids.add(os.path.basename(p)[:-len("__meta.json")])
    return sorted(ids)


def build_doc(root, node_id):
    seg_dir = resolve(root, SEG_DIR)
    meta_p = os.path.join(seg_dir, "%s__meta.json" % node_id)
    problems = []
    with open(meta_p, encoding="utf-8") as f:
        meta = json.load(f)

    segments = {}
    for s in SEGMENTS:
        p = os.path.join(seg_dir, "%s__%s.txt" % (node_id, s))
        if not os.path.isfile(p):
            problems.append("缺段文件: %s__%s.txt" % (node_id, s))
            continue
        t = read_text(p)
        if not t:
            problems.append("空段: %s" % s)
        if "PLACEHOLDER" in t:
            problems.append("占位符: %s" % s)
        if len(t) > SEG_WARN_CHARS:
            problems.append("段过长（可能截断）: %s = %d 字" % (s, len(t)))
        segments[s] = t

    provenance = meta.get("provenance") or {}
    for s in SEGMENTS:
        if not (provenance.get(s) or []):
            problems.append("provenance 空: %s" % s)

    final_chars = sum(len(segments.get(s, "")) for s in SEGMENTS)
    if not (CHAR_MIN <= final_chars <= CHAR_MAX):
        problems.append("字数 %d 不在 [%d,%d]" % (final_chars, CHAR_MIN, CHAR_MAX))

    doc = {
        "node_id": node_id,
        "segments": segments,
        "provenance": provenance,
        "new_claims": meta.get("new_claims") or [],
        "baseline_chars": meta.get("baseline_chars"),
        "final_chars": final_chars,
        "writer": meta.get("writer", "w-nodewriter-seg"),
        "review_date": REVIEW_DATE,
    }
    return doc, problems


def main():
    ap = argparse.ArgumentParser(description="分段小文件 → write-<node>.json 装配器")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not (args.check or args.apply):
        ap.error("必须指定 --check 或 --apply")
    root = os.path.abspath(args.root)

    ids = node_ids(root)
    if not ids:
        print("[SKIP] %s 下无 *__meta.json（写入方尚未产出分段）" % SEG_DIR)
        return 0

    total_bad = 0
    print("%-11s %-7s %s" % ("node", "chars", "problems"))
    for node_id in ids:
        doc, problems = build_doc(root, node_id)
        total_bad += len(problems)
        print("%-11s %-7d %s" % (node_id, doc["final_chars"], "; ".join(problems) or "OK"))
        if args.apply and not problems:
            out = resolve(root, os.path.join(DENSIFY, "write-%s.json" % node_id))
            with open(out, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print("   [write] %s" % os.path.relpath(out, root))

    print()
    print("== %s：%d 节点，问题 %d ==" % ("apply" if args.apply else "check", len(ids), total_bad))
    if args.apply:
        print("   注：仅**无问题**的节点被落盘；有问题者保持不落盘（fail-closed）")
    return 0 if total_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
