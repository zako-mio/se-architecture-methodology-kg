#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_corpus_overlap.py — 阶段2 版权红线机检（证据素材 + 节点正文 vs 三书原文）

用途：`gate_densify.py` 的 G-D4 只查**节点正文**；本脚本额外覆盖**证据素材**
（`evidence-*.json`），并可在 W2 之前独立跑，避免把违规素材带进改写。

判据：与书原文的最长公共子串 ≥ N 字（默认 20）命中 = 0。

用法：
  python3 16-checkpoint/check_corpus_overlap.py                 # 查全部 evidence + write
  python3 16-checkpoint/check_corpus_overlap.py --target evidence
  python3 16-checkpoint/check_corpus_overlap.py --target write
  python3 16-checkpoint/check_corpus_overlap.py -n 20 --show 30
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
SEGMENTS = ("definition", "principle", "mechanism", "engineering", "tradeoff")

CORPUS = [
    os.path.join("01-books", "_verify", "_text", "clean-architecture.txt"),
    os.path.join("01-books", "_verify", "_text", "saip.txt"),
    # 阶段7 轨B：新增核验书语料（BK-030 / BK-011）——证据素材亦须过版权红线
    os.path.join("01-books", "_verify", "_text", "team-topologies.txt"),
    os.path.join("01-books", "_verify", "_text", "evolutionary-arch.txt"),
    # 阶段7 阶段3 轨B 续做：新增核验书语料（BK-021 / BK-024 / BK-020）
    os.path.join("01-books", "_verify", "_text", "refactoring.txt"),
    os.path.join("01-books", "_verify", "_text", "release-it.txt"),
    os.path.join("01-books", "_verify", "_text", "clean-code.txt"),
]
CORPUS_GLOB = os.path.join("01-books", "_files", "P0-11", "ddia-zh-src", "*.md")


def grams(text, n):
    t = "".join(text.split())
    return {t[i:i + n] for i in range(len(t) - n + 1)}


def build_corpus(root, n):
    g = set()
    for rel in CORPUS:
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                g |= grams(f.read(), n)
    for p in sorted(glob.glob(os.path.join(root, CORPUS_GLOB))):
        with open(p, encoding="utf-8", errors="replace") as f:
            g |= grams(f.read(), n)
    return g


def main():
    ap = argparse.ArgumentParser(description="阶段2 版权红线机检")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--target", default="all", choices=["all", "evidence", "write"])
    ap.add_argument("-n", type=int, default=20)
    ap.add_argument("--show", type=int, default=30)
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    corpus = build_corpus(root, args.n)
    if not corpus:
        print("[SKIP] 三书语料均不可用")
        return 0
    print("[corpus] 语料 %d 个 distinct %d-gram" % (len(corpus), args.n))

    hits = []
    checked = 0
    skipped = []

    def try_load(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f), None
        except Exception as e:                               # noqa: BLE001
            return None, str(e)
    if args.target in ("all", "evidence"):
        for p in sorted(glob.glob(os.path.join(root, DENSIFY, "evidence-*.json"))):
            doc, err = try_load(p)
            if doc is None:
                skipped.append((os.path.basename(p), err))
                continue
            for it in doc.get("items", []) or []:
                checked += 1
                inter = grams(it.get("text", ""), args.n) & corpus
                if inter:
                    hits.append(("evidence", os.path.basename(p), it.get("evidence_id"),
                                 sorted(inter)[0]))
    if args.target in ("all", "write"):
        for p in sorted(glob.glob(os.path.join(root, DENSIFY, "write-*.json"))):
            doc, err = try_load(p)
            if doc is None:
                skipped.append((os.path.basename(p), err))
                continue
            segs = doc.get("segments") or {}
            text = "".join(segs.get(s, "") or "" for s in SEGMENTS)
            checked += 1
            inter = grams(text, args.n) & corpus
            if inter:
                hits.append(("write", os.path.basename(p), doc.get("node_id"),
                             sorted(inter)[0]))

    if skipped:
        print("[skipped] %d 个文件不可解析（未完成写入或损坏）:" % len(skipped))
        for f, e in skipped[:10]:
            print("  - %s: %s" % (f, e))
    print("[checked] %d 个对象" % checked)
    print("[hits] ≥%d 字公共子串命中 = %d" % (args.n, len(hits)))
    for kind, f, ident, sample in hits[:args.show]:
        print("  ! %-8s %-28s %-16s %s" % (kind, f, ident, sample))
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
