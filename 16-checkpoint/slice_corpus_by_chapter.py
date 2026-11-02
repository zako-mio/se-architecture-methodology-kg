#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
slice_corpus_by_chapter.py — 把私有层书语料按章切成独立小文件（供子 Agent 窄读）

动机（2026-10-12 实测）：BK-031 的复核/核验工人**因上下文耗尽而未产出**
（"ran out of room before it finished"）。根因之一是让工人一次性读整本语料
（BK-001 语料 1.3 MB）。按章切片后，工人只需读**目标章**那一个小文件。

切分口径（两路，2026-11-02 起）：
  ① **默认**：语料由 `extract_web_book.py` / `extract_pdf_book.py` / `extract_ocr_book.py`
     生成，章头形如 `=== <章号> | <标题> ===`；
  ② **`--pattern`**：EPUB 一路（`extract_book_text.py`）**不产章头**，正文章首形如
     `Chapter 7. The Commit Stage`（BK-028 实测 15 章），用自定正则切。正则必须**恰好
     两个捕获组**（章号、标题），按 MULTILINE 逐行匹配。⛔ 前置目录块用 `Chapter 7:`
     （冒号）形态，自定义正则要能把它排除（BK-028 用 `\\.` 点号即自然排除）。

三条 fail-closed（**拒写、退出码 3、一个文件都不落**）：
  - 匹配数 0（正则与语料不符，不静默产出空切片）；
  - 章号非严格递增（含重复 / 非数字）；
  - `--expect-chapters` 与实测章数不符、或与 `toc-<slug>.json` 章数不符。

性质：确定性（无时间戳）、只写私有层（`01-books/` 三重隔离）。

用法：
  python3 16-checkpoint/slice_corpus_by_chapter.py --slug sweg
  python3 16-checkpoint/slice_corpus_by_chapter.py --slug continuous-delivery \\
      --pattern '^Chapter (\\d+)\\. (.+)$' --expect-chapters 15
  python3 16-checkpoint/slice_corpus_by_chapter.py --negative-test    # 4 条探针

负例探针（`--negative-test`，4 条；含一条**旧判据反证**）：
  N1 无匹配            → 必须拒写
  N2 章号重复/非递增    → 必须拒写
  N3 章数与 expect 不符 → 必须拒写
  N4 旧判据反证        → 不带 `--pattern` 时对 `ddd` 语料重切，产物须与盘上既有
                         切片**逐字节一致**（证明新开关没有改动默认行为，探针非恒真）
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
TEXT_DIR = os.path.join("01-books", "_verify", "_text")
SLICE_DIR = os.path.join(TEXT_DIR, "_slices")
PARTS_DIR = os.path.join("01-books", "_verify", "_parts")

HEAD_RE = re.compile(r"^===\s+(.+?)\s+\|\s+(.+?)\s+===$", re.M)


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def compile_pattern(pattern):
    """编译切分正则；必须恰好含两个捕获组。"""
    try:
        rx = re.compile(pattern, re.M)
    except re.error as e:
        return None, "正则非法：%s" % e
    if rx.groups != 2:
        return None, "正则须恰好 2 个捕获组（章号, 标题），实测 %d 个" % rx.groups
    return rx, None


def slice_text(text, rx):
    """按正则切章；返回 (items, error)。items = [(章号str, 标题str, 正文str)]。"""
    marks = list(rx.finditer(text))
    if not marks:
        return None, "无章头匹配（正则与语料不符）"
    items = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        num = m.group(1).strip()
        title = m.group(2).strip()
        if not num.isdigit():
            return None, "章号非数字：%r（第 %d 个匹配）" % (num, i + 1)
        body = text[m.start():end].rstrip() + "\n"
        items.append((num, title, body))
    # 章号严格递增：防「章序错位」被当成合法切片（旧判据只查「有匹配」）
    prev = 0
    for num, _title, _body in items:
        cur = int(num)
        if cur <= prev:
            return None, "章号非严格递增：%d 出现在 %d 之后" % (cur, prev)
        prev = cur
    return items, None


def toc_chapter_count(root, slug):
    """`_parts/toc-<slug>.json` 声明的章数（无该分片则返回 None）。"""
    p = resolve(root, os.path.join(PARTS_DIR, "toc-%s.json" % slug))
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            toc = json.load(f)
    except (OSError, ValueError):
        return None
    ch = toc.get("toc")
    return len(ch) if isinstance(ch, list) else None


def write_items(outdir, items):
    os.makedirs(outdir, exist_ok=True)
    for num, _title, body in items:
        with open(os.path.join(outdir, "ch-%s.txt" % num), "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(body)


def slice_one(root, slug, pattern, expect, quiet=False):
    """切一本；返回 (ret, items)。ret=0 成功 / 3 拒写（fail-closed）。"""
    p = resolve(root, os.path.join(TEXT_DIR, "%s.txt" % slug))
    if not os.path.isfile(p):
        print("  [SKIP] %s 不存在" % slug)
        return 0, None
    with open(p, encoding="utf-8") as f:
        text = f.read()
    rx, err = compile_pattern(pattern)
    if err:
        print("  [REFUSE] %s：%s" % (slug, err))
        return 3, None
    items, err = slice_text(text, rx)
    if err:
        print("  [REFUSE] %s：%s" % (slug, err))
        return 3, None
    if expect is not None and len(items) != expect:
        print("  [REFUSE] %s：章数 %d ≠ --expect-chapters %d"
              % (slug, len(items), expect))
        return 3, None
    toc_n = toc_chapter_count(root, slug)
    if toc_n is not None and toc_n != len(items):
        print("  [REFUSE] %s：章数 %d ≠ toc-%s.json 声明 %d"
              % (slug, len(items), slug, toc_n))
        return 3, None
    outdir = resolve(root, os.path.join(SLICE_DIR, slug))
    write_items(outdir, items)
    if not quiet:
        for num, title, body in items:
            print("  %-22s %-9s %7d 字符  %s"
                  % (slug, "ch-%s" % num, len(body), title[:34]))
        print("  -> %s：%d 章切片" % (os.path.relpath(outdir, root), len(items)))
    return 0, items


# ---------------------------------------------------------------- 负例探针

def negative_test(root):
    """4 条探针；全部如期通过才算 PASS。"""
    results = []

    def stage(tmp, text):
        p = os.path.join(tmp, TEXT_DIR, "probe.txt")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return p

    def run_probe(text, pattern, expect, want_refuse):
        tmp = tempfile.mkdtemp(prefix="slice-probe-")
        try:
            stage(tmp, text)
            ret, items = slice_one(tmp, "probe", pattern, expect, quiet=True)
            wrote = os.path.isdir(os.path.join(tmp, SLICE_DIR, "probe"))
            ok = (ret == 3) if want_refuse else (ret == 0)
            if want_refuse and wrote:
                ok = False   # 拒写必须一个文件都不落
            return ok, ret, wrote
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    good = "\n".join("Chapter %d. Title %d\n\nbody %d\n" % (i, i, i)
                     for i in range(1, 4))

    # N1 无匹配 → 拒写
    ok, ret, wrote = run_probe("no chapter markers here at all\n",
                               r"^Chapter (\d+)\. (.+)$", None, want_refuse=True)
    results.append(("N1 无匹配须拒写", ok, "ret=%d wrote=%s" % (ret, wrote)))

    # N2 章号重复 / 非递增 → 拒写
    bad_order = "Chapter 1. A\n\nx\n\nChapter 1. B\n\ny\n\nChapter 3. C\n\nz\n"
    ok, ret, wrote = run_probe(bad_order, r"^Chapter (\d+)\. (.+)$", None,
                               want_refuse=True)
    results.append(("N2 章号非严格递增须拒写", ok,
                    "ret=%d wrote=%s" % (ret, wrote)))

    # N3 章数与 --expect-chapters 不符 → 拒写
    ok, ret, wrote = run_probe(good, r"^Chapter (\d+)\. (.+)$", 5,
                               want_refuse=True)
    results.append(("N3 章数与 expect 不符须拒写", ok,
                    "ret=%d wrote=%s" % (ret, wrote)))

    # N4 旧判据反证：不带 --pattern 时对 ddd 语料重切，须与盘上切片逐字节一致
    ref_slug = "ddd"
    ref_text = resolve(root, os.path.join(TEXT_DIR, "%s.txt" % ref_slug))
    ref_dir = resolve(root, os.path.join(SLICE_DIR, ref_slug))
    if not os.path.isfile(ref_text) or not os.path.isdir(ref_dir):
        results.append(("N4 旧判据反证（ddd 逐字节）", False,
                        "缺少参照语料或切片：%s" % ref_slug))
    else:
        tmp = tempfile.mkdtemp(prefix="slice-ref-")
        try:
            with open(ref_text, encoding="utf-8") as f:
                text = f.read()
            items, err = slice_text(text, HEAD_RE)
            if err:
                results.append(("N4 旧判据反证（ddd 逐字节）", False, err))
            else:
                write_items(os.path.join(tmp, "slices"), items)
                names = sorted(os.listdir(ref_dir))
                gen = sorted(os.listdir(os.path.join(tmp, "slices")))
                diff = []
                if names != gen:
                    diff.append("文件名集合不同")
                for n in names:
                    if n not in gen:
                        continue
                    a = open(os.path.join(ref_dir, n), "rb").read()
                    b = open(os.path.join(tmp, "slices", n), "rb").read()
                    if a != b:
                        diff.append(n)
                ok = not diff
                results.append(("N4 旧判据反证（ddd 逐字节）", ok,
                                "文件 %d / 差异 %s" % (len(names), diff or "无")))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("负例探针（slice_corpus_by_chapter）：")
    passed = 0
    for name, ok, detail in results:
        print("  %-28s %s   %s" % (name, "PASS" if ok else "FAIL", detail))
        passed += 1 if ok else 0
    print("  -> %d/%d" % (passed, len(results)))
    return 0 if passed == len(results) else 1


def main():
    ap = argparse.ArgumentParser(description="按章切分书语料")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--slug", help="单个 slug")
    ap.add_argument("--all", action="store_true", help="处理 _text/ 下全部 <slug>.txt")
    ap.add_argument("--pattern", default=None,
                    help="自定义章头正则（须 2 个捕获组：章号, 标题）；用于 EPUB 一路")
    ap.add_argument("--expect-chapters", type=int, default=None,
                    help="期望章数（不符则拒写）")
    ap.add_argument("--negative-test", action="store_true", help="跑 4 条负例探针后退出")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.negative_test:
        return negative_test(root)

    pattern = args.pattern if args.pattern is not None else HEAD_RE.pattern

    if args.all:
        if args.pattern is not None or args.expect_chapters is not None:
            print("⛔ --all 不能与 --pattern / --expect-chapters 同用（每本书正则不同）")
            return 2
        slugs = sorted(f[:-4] for f in os.listdir(resolve(root, TEXT_DIR))
                       if f.endswith(".txt"))
    elif args.slug:
        slugs = [args.slug]
    else:
        print("请指定 --slug 或 --all")
        return 2

    ret = 0
    for slug in slugs:
        r, _ = slice_one(root, slug, pattern, args.expect_chapters)
        ret = ret or r
    return ret


if __name__ == "__main__":
    sys.exit(main())
