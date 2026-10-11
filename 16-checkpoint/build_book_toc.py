#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_book_toc.py — 从 EPUB NCX 生成核验层 TOC 分片

产物：`01-books/_verify/_parts/toc-<slug>.json`
结构（与既有 toc-*.json 一致，刚性）：
  {"source_id": "BK-0xx", "book": "<英文书名>", "edition": "<版次/年>",
   "toc": [{"chapter": "1", "title": "<章标题>",
            "sections": [{"no": "1.1", "title": "<节标题>"}]}]}

章识别规则（数据驱动，兼容两种常见 NCX 写法）：
  - `Chapter 1: The Problem with Org Charts`  → chapter=1
  - `1. Evolving Software Architecture`       → chapter=1
节识别：章的**后代** navPoint（层级更深），按出现顺序编号 `<chapter>.<i>`。

性质：确定性（无时间戳）、UTF-8、末尾换行；只读 EPUB、只写私有 `_parts/`。

用法：
  python3 16-checkpoint/build_book_toc.py \
    --epub 01-books/_files/P1-23/P1-23_team-topologies_2019.epub \
    --slug team-topologies --source-id BK-030 \
    --book "Team Topologies" --edition "1st/2019"
"""
import argparse
import json
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
PARTS_DIR = os.path.join("01-books", "_verify", "_parts")

CHAPTER_RE = re.compile(r"^(?:Chapter\s+)?(\d+)\s*[.:]\s*(.+)$")
CHAPTER_ONLY_RE = re.compile(r"^(?:Chapter\s+)(\d+)\s*$")


def default_root():
    return ROOT_DEFAULT


def ncx_points(epub_path):
    """返回 [(label, depth, src)]，按文档顺序。"""
    from lxml import etree
    with zipfile.ZipFile(epub_path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".ncx")]
        if not names:
            raise ValueError("EPUB 中未找到 .ncx")
        root = etree.fromstring(z.read(names[0]))
    ns = {"n": "http://www.daisy.org/z3986/2005/ncx/"}
    out = []
    for np in root.xpath("//n:navPoint", namespaces=ns):
        label = np.find("n:navLabel/n:text", ns)
        content = np.find("n:content", ns)
        txt = (label.text or "").strip() if label is not None else ""
        txt = re.sub(r"\s+", " ", txt)   # NCX 标题内可能含换行（如 "9. Putting ... \ninto Practice"）
        src = content.get("src") if content is not None else ""
        depth = len(np.xpath("ancestor::n:navPoint", namespaces=ns))
        out.append((txt, depth, src))
    return out


def build_toc(points):
    chapters = []
    cur = None
    for label, depth, _src in points:
        m = CHAPTER_RE.match(label)
        if m:
            cur = {"chapter": m.group(1), "title": m.group(2).strip(),
                   "sections": [], "_depth": depth}
            chapters.append(cur)
            continue
        m2 = CHAPTER_ONLY_RE.match(label)
        if m2:
            cur = {"chapter": m2.group(1), "title": "", "sections": [], "_depth": depth}
            chapters.append(cur)
            continue
        if cur is not None and depth > cur["_depth"] and label:
            n = len(cur["sections"]) + 1
            cur["sections"].append({"no": "%s.%d" % (cur["chapter"], n), "title": label})
    for c in chapters:
        c.pop("_depth", None)
    return chapters


def main():
    ap = argparse.ArgumentParser(description="EPUB NCX → _parts/toc-<slug>.json")
    ap.add_argument("--epub", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--book", required=True)
    ap.add_argument("--edition", default="")
    ap.add_argument("--root", default=default_root())
    args = ap.parse_args()

    epub = args.epub if os.path.isabs(args.epub) else os.path.join(args.root, args.epub)
    toc = build_toc(ncx_points(epub))
    doc = {"source_id": args.source_id, "book": args.book,
           "edition": args.edition, "toc": toc}
    out = os.path.join(args.root, PARTS_DIR, "toc-%s.json" % args.slug)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    ns = sum(len(c["sections"]) for c in toc)
    print("chapters=%d sections=%d" % (len(toc), ns))
    for c in toc:
        print("  %s %s (%d sections)" % (c["chapter"], c["title"], len(c["sections"])))
    print("wrote %s" % os.path.relpath(out, args.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
