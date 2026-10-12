#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
slice_corpus_by_chapter.py — 把私有层书语料按章切成独立小文件（供子 Agent 窄读）

动机（2026-10-12 实测）：BK-031 的复核/核验工人**因上下文耗尽而未产出**
（"ran out of room before it finished"）。根因之一是让工人一次性读整本语料
（BK-001 语料 1.3 MB）。按章切片后，工人只需读**目标章**那一个小文件。

切分口径：语料由 `extract_web_book.py` 生成，章头形如 `## <章号>. <标题>`；
本脚本按该标记切分，产出 `_text/_slices/<slug>/ch-<章号>.txt`。

性质：确定性（无时间戳）、只写私有层（`01-books/` 三重隔离）。

用法：
  python3 16-checkpoint/slice_corpus_by_chapter.py --slug sweg
  python3 16-checkpoint/slice_corpus_by_chapter.py --all
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
TEXT_DIR = os.path.join("01-books", "_verify", "_text")
SLICE_DIR = os.path.join(TEXT_DIR, "_slices")

HEAD_RE = re.compile(r"^===\s+(.+?)\s+\|\s+(.+?)\s+===$", re.M)


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def main():
    ap = argparse.ArgumentParser(description="按章切分书语料")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--slug", help="单个 slug")
    ap.add_argument("--all", action="store_true", help="处理 _text/ 下全部 <slug>.txt")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.all:
        slugs = sorted(f[:-4] for f in os.listdir(resolve(root, TEXT_DIR))
                       if f.endswith(".txt"))
    elif args.slug:
        slugs = [args.slug]
    else:
        print("请指定 --slug 或 --all")
        return 2

    for slug in slugs:
        p = resolve(root, os.path.join(TEXT_DIR, "%s.txt" % slug))
        if not os.path.isfile(p):
            print("  [SKIP] %s 不存在" % slug)
            continue
        with open(p, encoding="utf-8") as f:
            text = f.read()
        marks = list(HEAD_RE.finditer(text))
        if not marks:
            print("  [SKIP] %s 无章头标记（非 extract_web_book 产物？）" % slug)
            continue
        outdir = resolve(root, os.path.join(SLICE_DIR, slug))
        os.makedirs(outdir, exist_ok=True)
        total = 0
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            body = text[m.start():end].rstrip() + "\n"
            name = "ch-%s.txt" % m.group(1)
            with open(os.path.join(outdir, name), "w", encoding="utf-8",
                      newline="\n") as f:
                f.write(body)
            total += 1
            print("  %-16s %-12s %7d 字符  %s" % (slug, name, len(body),
                                                  m.group(2)[:34]))
        print("  -> %s：%d 章切片" % (os.path.relpath(outdir, root), total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
