#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_pdf_book.py — PDF → 纯文本（核验层私有语料，含章头标记）

用途：把已获取的 **PDF** 按页抽成纯文本，落到私有层
  `01-books/_verify/_text/<slug>.txt`，并在每章起始页前插入机读章头
  `=== <章号> | <章标题> ===`（`validate_staging_shards.py` 与
  `slice_corpus_by_chapter.py` 依赖该标记切章级正文）。

与既有抽取器的分工：`extract_book_text.py`（EPUB）/ `extract_web_book.py`（在线）
本脚本补 **PDF** 一路。

性质：确定性（无时间戳）、UTF-8 无 BOM、末尾换行；只读 PDF、只写私有层。
隔离：`01-books/` 已被本地仓 `.gitignore:13` 整体忽略；`_publish/.gitignore` 显式忽略
  `01-books/_verify/`；装配层 `publish-manifest.json` 把 `01-books/_verify/` 列为 private。

**fail-closed 判据（任一不过即拒写，exit≠0）**：
  1. `pdftotext` 抽出的页数 == `pdfinfo -Pages` == 章图的 `pages_expected`
  2. 每条章的 `norm(title)` 必须出现在其声明页的正文中（`norm` = 大小写折叠 +
     连字/引号归一 + 去非字母数字，兼容小型大写渲染与换行折行）
  3. `pdf_page` 严格递增、且在 `[1, 页数]` 内；`first_page` 合法

用法：
  python3 16-checkpoint/extract_pdf_book.py \\
      --pdf 01-books/_files/P0-10/xxx.pdf --slug welc \\
      --chapters 01-books/_verify/_meta/pdf-chapters-welc.json --check
  python3 16-checkpoint/extract_pdf_book.py --pdf <p> --slug <s> --chapters <m>
  python3 16-checkpoint/extract_pdf_book.py --chapters <m> --negative-test
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
TEXT_DIR = os.path.join("01-books", "_verify", "_text")

# 归一化：连字与排版引号/破折号先展开，再折叠大小写并去掉一切非字母数字
# （这样换行折行、`R ISKY C HANGE` 这类小型大写、’ 与 ' 的差异都不影响匹配）
_SUBS = (
    ("\ufb01", "fi"), ("\ufb02", "fl"), ("\ufb00", "ff"), ("\ufb03", "ffi"),
    ("\ufb04", "ffl"), ("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'),
    ("\u201d", '"'), ("\u2013", "-"), ("\u2014", "-"), ("\u2212", "-"),
)


def norm(s):
    s = (s or "").lower()
    for a, b in _SUBS:
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "", s)


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def pdfinfo_pages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, check=True).stdout
    m = re.search(rb"^Pages:\s+(\d+)\s*$", out, re.M)
    if not m:
        raise ValueError("pdfinfo 未给出 Pages")
    return int(m.group(1))


def extract_pages(pdf):
    out = subprocess.run(["pdftotext", "-layout", pdf, "-"],
                         capture_output=True, check=True).stdout
    pages = out.decode("utf-8", "replace").split("\f")
    while pages and not pages[-1].strip():
        pages.pop()
    return pages


def validate(spec, pages, pdf_pages=None):
    """返回 problems 列表（空 = 通过）。纯函数，便于负例探针复用。"""
    problems = []
    expect = spec.get("pages_expected")
    if pdf_pages is not None and pdf_pages != len(pages):
        problems.append("pdfinfo Pages=%s 与 pdftotext 页数=%d 不一致"
                        % (pdf_pages, len(pages)))
    if expect != len(pages):
        problems.append("pages_expected=%s 与实际页数=%d 不一致" % (expect, len(pages)))

    chapters = spec.get("chapters") or []
    if not chapters:
        problems.append("章图 chapters 为空")
    first = spec.get("first_page")
    if not isinstance(first, int) or not (1 <= first <= max(len(pages), 1)):
        problems.append("first_page 非法: %r" % first)

    prev = 0
    for c in chapters:
        ch, title, pg = c.get("chapter"), c.get("title"), c.get("pdf_page")
        if not isinstance(pg, int) or not (1 <= pg <= len(pages)):
            problems.append("章 %s 的 pdf_page 非法: %r" % (ch, pg))
            continue
        if pg <= prev:
            problems.append("章 %s 的 pdf_page=%d 非严格递增（上一章 %d）" % (ch, pg, prev))
        prev = pg
        # `match` 为可选覆盖：当章标题在页面上被分栏/折行打断、整串不连续时，
        # 用页面上**确实连续**的一段子串作为定位判据（仍须 ≥6 字符）。
        needle_src = c.get("match") or title
        needle = norm(needle_src)
        if len(needle) < 6:
            problems.append("章 %s 标题过短，无法作为定位判据: %r（可用 match 指定更长串）"
                            % (ch, needle_src))
            continue
        if needle not in norm(pages[pg - 1]):
            problems.append("章 %s 的标题在声明页 %d 未出现: %r" % (ch, pg, needle_src))
    return problems


def render(spec, pages):
    by_page = {c["pdf_page"]: c for c in spec["chapters"]}
    out = []
    for p in range(spec["first_page"], len(pages) + 1):
        if p in by_page:
            c = by_page[p]
            if out and not out[-1].endswith("\n"):
                out.append("\n")
            out.append("=== %s | %s ===\n" % (c["chapter"], c["title"]))
        out.append(pages[p - 1])
    text = "".join(out)
    text = re.sub(r"\n{0,3}\Z", "", text) + "\n"
    return text


def negative_test(spec, pages, pdf_pages):
    """3 条负例探针：判据必须逐条**以其应有理由**拒写，否则判据已退化（exit=1）。"""
    import copy
    probes = []

    s = copy.deepcopy(spec)
    s["pages_expected"] = (s.get("pages_expected") or 0) + 1
    probes.append(("N1 页数不符必拒", "pages_expected", validate(s, pages, pdf_pages)))

    s = copy.deepcopy(spec)
    s["chapters"][0]["title"] = "QZXJV Nonexistent Chapter Title WVU"
    s["chapters"][0].pop("match", None)
    probes.append(("N2 标题不在声明页必拒", "未出现", validate(s, pages, pdf_pages)))

    s = copy.deepcopy(spec)
    if len(s["chapters"]) >= 2:
        # 交换前两章的 pdf_page（**不重排列表**）⇒ 列表序上出现下降沿
        s["chapters"][0]["pdf_page"], s["chapters"][1]["pdf_page"] = \
            s["chapters"][1]["pdf_page"], s["chapters"][0]["pdf_page"]
    probes.append(("N3 pdf_page 非递增必拒", "非严格递增", validate(s, pages, pdf_pages)))

    bad = 0
    for name, must, probs in probes:
        hit = [p for p in probs if must in p]
        ok = bool(hit)
        print("  [%s] %s —— %s" % ("REJECT" if ok else "!! NOT-REJECTED", name,
                                   hit[0] if hit else (probs[0] if probs else "无问题（判据退化）")))
        bad += 0 if ok else 1
    print("== 负例探针 %d/%d 如期按应有理由拒写 ==" % (len(probes) - bad, len(probes)))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="PDF → 纯文本（核验层私有语料）")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--pdf", help="PDF 路径（--negative-test 时可省，从章图取）")
    ap.add_argument("--slug", help="输出 slug（_text/<slug>.txt）")
    ap.add_argument("--chapters", required=True, help="章图 JSON")
    ap.add_argument("--check", action="store_true", help="只校验并报告，不写盘")
    ap.add_argument("--negative-test", action="store_true", help="跑 3 条负例探针后退出")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    spec = load(resolve(root, args.chapters))
    pdf = args.pdf or spec.get("pdf")
    if not pdf:
        print("缺少 --pdf（章图内也无 pdf 字段）")
        return 2
    pdf = resolve(root, pdf)
    if not os.path.isfile(pdf):
        print("PDF 不存在: %s" % pdf)
        return 2

    pdf_pages = pdfinfo_pages(pdf)
    pages = extract_pages(pdf)
    print("pdf=%s" % os.path.relpath(pdf, root))
    print("pdfinfo Pages=%d ｜ pdftotext 页数=%d ｜ 章图 pages_expected=%s"
          % (pdf_pages, len(pages), spec.get("pages_expected")))

    if args.negative_test:
        print("== 负例探针（判据可信度） ==")
        return negative_test(spec, pages, pdf_pages)

    problems = validate(spec, pages, pdf_pages)
    print("== 章头落位矩阵（%d 章） ==" % len(spec.get("chapters") or []))
    for c in spec.get("chapters") or []:
        pg = c.get("pdf_page")
        needle = norm(c.get("match") or c.get("title"))
        hit = "OK " if isinstance(pg, int) and 1 <= pg <= len(pages) and len(needle) >= 6 \
            and needle in norm(pages[pg - 1]) else "MISS"
        print("  [%s] ch=%-3s pdf_p=%-4s printed=%-4s %s"
              % (hit, c.get("chapter"), pg, c.get("printed_page"),
                 (c.get("title") or "")[:52]))
    if problems:
        print("")
        for p in problems:
            print("  ! %s" % p)
        print("\n== 结果 = FAIL（问题 %d 条，未落盘）==" % len(problems))
        return 1
    print("\n== 判据 = PASS ==")

    text = render(spec, pages)
    if args.check:
        print("[--check] 未落盘（将写入 %d 字符）" % len(text))
        return 0
    if not args.slug:
        print("缺少 --slug")
        return 2
    out = os.path.join(root, TEXT_DIR, "%s.txt" % args.slug)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    marks = len(re.findall(r"^=== .+? \| .+? ===$", text, re.M))
    print("chars=%d bytes=%d 章头标记=%d" % (len(text), len(text.encode("utf-8")), marks))
    print("wrote %s" % os.path.relpath(out, root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
