#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_ocr_book.py — 无文本层 PDF 的 OCR 结果 → 核验层纯文本语料（含章头标记）

与既有抽取器的分工：
  · `extract_book_text.py`  —— EPUB
  · `extract_web_book.py`   —— 在线 HTML
  · `extract_pdf_book.py`   —— **有文本层**的 PDF（pdftotext）
  · 本脚本                   —— **无文本层**的 PDF：消费 OCR 结果（`pdf_ocr.py --json`），
                               同样是「PDF 一路」，但不重跑 OCR、不做识别，只做**装配与校验**。

为什么单列：`extract_pdf_book.py` 的三条 fail-closed 判据全部建立在 pdftotext 的页文本上；
无文本层时 pdftotext 只返回分页符（实测 20 页 = 20 个 `\\f`，0 字符），标题落位判据必然失败。
OCR 一路因此需要**独立脚本 + 独立负例**，不能把判据放宽了塞进原脚本。

隔离：只读 PDF（仅取页数）与 OCR JSON；只写私有层 `01-books/_verify/_text/<slug>.txt`。
`01-books/` 三重隔离（本地 .gitignore / `_publish/.gitignore` / `publish-manifest.json` private）。

**fail-closed 判据（任一不过即拒写，exit=1）**：
  1. `pdfinfo -Pages` == OCR 页数 == 章图 `pages_expected`
  2. OCR 页序必须是完整 1..N（缺页/重页/乱序一律拒）
  3. 每页 OCR 文本长度 ≥ `MIN_PAGE_CHARS`（空页=识别静默失败，不得当作"该页无内容"放过）
  4. 每条章的 `pdf_page` 在 `[1, 页数]` 内且**严格递增**；`norm(match|title)` 必须出现在该页 OCR 文本中
  5. 声明了 `printed_page` 的章，其印刷页码必须**严格递增**（防章图与抽取件错位）

用法：
  python3 16-checkpoint/extract_ocr_book.py \\
      --pdf 01-books/_files/P0-03/xxx.pdf --slug aposd \\
      --chapters 01-books/_verify/_meta/pdf-chapters-aposd.json \\
      --ocr-json 01-books/_verify/_text/_ocr/aposd.ocr.json --check
  python3 16-checkpoint/extract_ocr_book.py --chapters <m> --negative-test
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

# 单页 OCR 文本下限：低于此值视为识别失败（不是"空白页"——本书无整页空白）
MIN_PAGE_CHARS = 30

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


def ocr_pages(doc):
    """OCR JSON（`pdf_ocr.py --json`）→ {页码: 文本}；结构不合法直接抛错。"""
    if not isinstance(doc, list) or not doc:
        raise ValueError("OCR JSON 必须是页数组且非空")
    pages = {}
    for i, p in enumerate(doc, 1):
        if not isinstance(p, dict):
            raise ValueError("OCR JSON 第 %d 项不是对象" % i)
        n = p.get("page")
        if not isinstance(n, int):
            raise ValueError("OCR JSON 第 %d 项缺整数 page" % i)
        if n in pages:
            raise ValueError("OCR JSON 页号重复: %d" % n)
        pages[n] = p.get("text") or ""
    return pages


def validate(spec, pages, pdf_pages=None):
    """返回 problems 列表（空 = 通过）。纯函数，负例探针复用。"""
    problems = []
    expect = spec.get("pages_expected")
    n = len(pages)
    if pdf_pages is not None and pdf_pages != n:
        problems.append("pdfinfo Pages=%s 与 OCR 页数=%d 不一致" % (pdf_pages, n))
    if expect != n:
        problems.append("pages_expected=%s 与 OCR 页数=%d 不一致" % (expect, n))

    # 判据 2：页序完整 1..N
    missing = sorted(set(range(1, n + 1)) - set(pages))
    extra = sorted(set(pages) - set(range(1, n + 1)))
    if missing:
        problems.append("OCR 缺页: %s" % missing[:10])
    if extra:
        problems.append("OCR 页号越界: %s" % extra[:10])

    # 判据 3：空页 = 识别静默失败
    short = [p for p in sorted(pages) if len((pages[p] or "").strip()) < MIN_PAGE_CHARS]
    if short:
        problems.append("OCR 文本过短（疑似识别失败）: 页 %s" % short[:10])

    chapters = spec.get("chapters") or []
    if not chapters:
        problems.append("章图 chapters 为空")
    first = spec.get("first_page")
    if not isinstance(first, int) or not (1 <= first <= max(n, 1)):
        problems.append("first_page 非法: %r" % first)

    prev_pdf = 0
    prev_printed = None
    for c in chapters:
        ch, title, pg = c.get("chapter"), c.get("title"), c.get("pdf_page")
        if not isinstance(pg, int) or not (1 <= pg <= n):
            problems.append("章 %s 的 pdf_page 非法: %r" % (ch, pg))
            continue
        # 判据 4：pdf_page 严格递增
        if pg <= prev_pdf:
            problems.append("章 %s 的 pdf_page=%d 非严格递增（上一章 %d）" % (ch, pg, prev_pdf))
        prev_pdf = pg
        # 判据 5：印刷页码严格递增（仅对声明者）
        pp = c.get("printed_page")
        if isinstance(pp, int):
            if prev_printed is not None and pp <= prev_printed:
                problems.append("章 %s 的 printed_page=%d 非严格递增（上一章 %d）"
                                % (ch, pp, prev_printed))
            prev_printed = pp
        # 判据 4b：标题（或 match）须落在声明页
        needle_src = c.get("match") or title
        needle = norm(needle_src)
        if len(needle) < 6:
            problems.append("章 %s 标题过短，无法作为定位判据: %r（可用 match 指定更长串）"
                            % (ch, needle_src))
            continue
        if pg in pages and needle not in norm(pages[pg]):
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
        out.append((pages.get(p) or "").rstrip() + "\n\n")
    text = "".join(out)
    text = re.sub(r"\n{0,3}\Z", "", text) + "\n"
    return text


def negative_test(spec, pages, pdf_pages):
    """5 条负例探针：判据必须逐条**以其应有理由**拒写，否则判据已退化（exit=1）。"""
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
        s["chapters"][0]["pdf_page"], s["chapters"][1]["pdf_page"] = \
            s["chapters"][1]["pdf_page"], s["chapters"][0]["pdf_page"]
    probes.append(("N3 pdf_page 非递增必拒", "非严格递增", validate(s, pages, pdf_pages)))

    # N4：空页（识别静默失败）必须拒 —— 若放过，G-V5 会用残缺语料做改写检查
    bad_pages = dict(pages)
    bad_pages[spec["first_page"]] = ""
    probes.append(("N4 空页/识别失败必拒", "疑似识别失败", validate(spec, bad_pages, None)))

    # N5：印刷页码回退（章图与抽取件错位）必须拒
    s = copy.deepcopy(spec)
    printed = [c for c in s["chapters"] if isinstance(c.get("printed_page"), int)]
    if len(printed) >= 2:
        printed[0]["printed_page"], printed[1]["printed_page"] = \
            printed[1]["printed_page"], printed[0]["printed_page"]
    probes.append(("N5 printed_page 非递增必拒", "非严格递增", validate(s, pages, pdf_pages)))

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
    ap = argparse.ArgumentParser(description="OCR 结果 → 核验层纯文本语料")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--pdf", help="PDF 路径（只用于取页数；--negative-test 时可省）")
    ap.add_argument("--slug", help="输出 slug（_text/<slug>.txt）")
    ap.add_argument("--chapters", required=True, help="章图 JSON")
    ap.add_argument("--ocr-json", help="OCR 结果 JSON（pdf_ocr.py --json 的产物）")
    ap.add_argument("--check", action="store_true", help="只校验并报告，不写盘")
    ap.add_argument("--negative-test", action="store_true", help="跑 5 条负例探针后退出")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    spec = load(resolve(root, args.chapters))
    pdf = args.pdf or spec.get("pdf")
    ocr = args.ocr_json or spec.get("ocr_json")
    if not pdf:
        print("缺少 --pdf（章图内也无 pdf 字段）")
        return 2
    pdf = resolve(root, pdf)
    if not os.path.isfile(pdf):
        print("PDF 不存在: %s" % pdf)
        return 2
    if not ocr:
        print("缺少 --ocr-json（须先跑 ~/.dsh/skills/opencode/pdf-ocr/scripts/pdf_ocr.py --json）")
        return 2
    ocr = resolve(root, ocr)
    if not os.path.isfile(ocr):
        print("OCR JSON 不存在: %s" % ocr)
        return 2

    pdf_pages = pdfinfo_pages(pdf)
    pages = ocr_pages(load(ocr))
    print("pdf=%s" % os.path.relpath(pdf, root))
    print("ocr=%s" % os.path.relpath(ocr, root))
    print("pdfinfo Pages=%d ｜ OCR 页数=%d ｜ 章图 pages_expected=%s"
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
            and needle in norm(pages.get(pg, "")) else "MISS"
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
