#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_web_book.py — 在线书籍/章节页 → 私有层纯文本 + 自建 TOC 分片

用途（阶段7 阶段3 轨B 续做，BK-001 / BK-031 / BK-036）：
把**官方免费在线正文**抽成私有层语料（`01-books/_verify/_text/<slug>.txt`）与
自建 TOC（`01-books/_verify/_parts/toc-<slug>.json`），供核验层（ledger/claims/gaps）
与改写红线机检（G-V5 / check_corpus_overlap）使用。

设计（复用 `extract_sre_web.py` 的 DOM 抽取经验）：
- **必须用 DOM**（lxml），不得用非贪婪 `</section>` 正则：章节正文含**嵌套 <section>**，
  非贪婪正则会在一级嵌套闭合处截断（SRE 实测某章 25 389 字符被截为 3 863）。
- 正文容器按站点 `kind` 选择：
    · `oreilly`  → `section[data-type="chapter"|"appendix"]`（O'Reilly Atlas 体例，BK-001）
    · `article`  → 首个 `<article>`（BK-031）
    · `body`     → `<body>`（无结构化容器的普通页面，BK-036）
- **fail-closed**：0 章 / 单章字符数低于阈值 / 抓取失败 ⇒ 报错退出，不写残缺语料。
- 确定性：无时间戳、UTF-8 无 BOM、末尾换行；章节顺序 = 配置顺序（与站点目录一致）。

用法：
  python3 16-checkpoint/extract_web_book.py --book sweg
  python3 16-checkpoint/extract_web_book.py --book twelve-factor --stdout | head
"""
import argparse
import html as html_mod
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
TEXT_DIR = os.path.join("01-books", "_verify", "_text")
PARTS = os.path.join("01-books", "_verify", "_parts")
FO_REL = os.path.join("01-books", "free-official-extracts.json")

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124 Safari/537.36")
SKIP_TAGS = ("script", "style", "head", "title", "meta", "link", "nav", "footer",
             "noscript", "iframe")
BLOCK_TAGS = ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr",
              "blockquote", "pre", "figcaption", "dt", "dd", "section", "article",
              "table", "ul", "ol", "br", "hr")

# BK-001 章节表由 `01-books/free-official-extracts.json` 的 FO-01 提供（已登记、可复核）
FO_CHAPTERS = {"sweg": "FO-01"}

SITES = {
    "sweg": {
        "slug": "sweg",
        "source_id": "BK-001",
        "book": "Software Engineering at Google: Lessons Learned from Programming Over Time",
        "edition": "1st/2020",
        "kind": "oreilly",
        "data_types": ("chapter", "appendix", "afterword", "preface", "foreword"),
        "min_chars": 5000,
        # 短结构页（Afterword 等）单独放宽下限，避免 fail-closed 误伤
        "min_chars_overrides": {"26": 400},
        "license": "CC BY-NC-ND 4.0（官方在线全文）",
    },
    "twelve-factor": {
        "slug": "twelve-factor",
        "source_id": "BK-031",
        "book": "The Twelve-Factor App",
        "edition": "1st/2017",
        "kind": "article",
        "min_chars": 800,
        "license": "MIT（官方在线全文）",
        "chapters": [
            ("I", "Codebase", "https://12factor.net/codebase"),
            ("II", "Dependencies", "https://12factor.net/dependencies"),
            ("III", "Config", "https://12factor.net/config"),
            ("IV", "Backing services", "https://12factor.net/backing-services"),
            ("V", "Build, release, run", "https://12factor.net/build-release-run"),
            ("VI", "Processes", "https://12factor.net/processes"),
            ("VII", "Port binding", "https://12factor.net/port-binding"),
            ("VIII", "Concurrency", "https://12factor.net/concurrency"),
            ("IX", "Disposability", "https://12factor.net/disposability"),
            ("X", "Dev/prod parity", "https://12factor.net/dev-prod-parity"),
            ("XI", "Logs", "https://12factor.net/logs"),
            ("XII", "Admin processes", "https://12factor.net/admin-processes"),
        ],
    },
    "saip-ch4": {
        "slug": "saip-ch4",
        "source_id": "BK-036",
        "book": "Software Architecture in Practice — Chapter 4: Quality Attribute Scenarios",
        "edition": "2nd/2003",
        "kind": "body",
        "min_chars": 1500,
        "license": "章节级公开转载页（仅私有层核验；公开层处置另案）",
        "chapters": [
            ("4", "Quality Attribute Scenarios",
             "https://people.ece.ubc.ca/matei/EECE417/BASS/ch04lev1sec3.html"),
        ],
    },
}


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def fetch(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def strip_tags(s):
    return html_mod.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def main_section(page_html, kind, data_types=("chapter", "appendix")):
    from lxml import etree
    parser = etree.HTMLParser(recover=True, huge_tree=True)
    tree = etree.fromstring(page_html.encode("utf-8"), parser)
    if tree is None:
        return None
    if kind == "oreilly":
        for el in tree.iter():
            tag = getattr(el, "tag", None)
            if isinstance(tag, str) and tag.lower() == "section" \
                    and (el.get("data-type") or "") in data_types:
                return el
        for el in tree.iter():
            if isinstance(getattr(el, "tag", None), str) and el.get("id") == "content":
                return el
        return None
    if kind == "article":
        for el in tree.iter():
            if isinstance(getattr(el, "tag", None), str) and el.tag.lower() == "article":
                return el
        return None
    if kind == "body":
        for el in tree.iter():
            if isinstance(getattr(el, "tag", None), str) and el.tag.lower() == "body":
                return el
        return None
    return None


def to_text(el):
    """DOM 元素 → 纯文本（块级标签转换行，压空白，保留段落空行）。"""
    parts = []

    def walk(node):
        tag = getattr(node, "tag", None)
        tag = tag.lower() if isinstance(tag, str) else ""
        if tag in SKIP_TAGS:
            return
        block = tag in BLOCK_TAGS
        if block and parts and parts[-1] != "\n":
            parts.append("\n")
        if node.text:
            parts.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                parts.append(child.tail)
        if block and parts and parts[-1] != "\n":
            parts.append("\n")

    walk(el)
    s = html_mod.unescape("".join(parts))
    s = s.replace("\xa0", " ").replace("\u200b", "")
    s = re.sub(r"[ \t]+", " ", s)
    out, blank = [], False
    for ln in (x.strip() for x in s.split("\n")):
        if ln:
            out.append(ln)
            blank = False
        elif not blank and out:
            out.append("")
            blank = True
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def chapters_of(root, site):
    """返回 [(chapter_no, title, url)]。"""
    fo_id = FO_CHAPTERS.get(site["slug"])
    if not fo_id:
        return list(site.get("chapters") or [])
    doc = json.load(open(resolve(root, FO_REL), encoding="utf-8"))
    src = next((s for s in doc["sources"] if s.get("id") == fo_id), None)
    if src is None:
        raise SystemExit("! %s 未在 free-official-extracts.json 登记" % fo_id)
    out = []
    for part in src.get("toc") or []:
        for ch in part.get("chapters") or []:
            out.append((str(ch["n"]), ch["title"], ch["url"]))
    return out


def main():
    ap = argparse.ArgumentParser(description="在线书 → 私有层语料 + 自建 TOC")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--book", required=True, choices=sorted(SITES))
    ap.add_argument("--stdout", action="store_true", help="只打印，不落盘")
    ap.add_argument("--timeout", type=int, default=45)
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    site = SITES[args.book]
    slug = site["slug"]

    chapters = chapters_of(root, site)
    if not chapters:
        print("! 0 章（fail-closed）")
        return 1

    blocks, toc, problems = [], [], []
    for no, title, url in chapters:
        try:
            page = fetch(url, timeout=args.timeout)
        except Exception as e:                                   # noqa: BLE001
            problems.append("%s 抓取失败：%s" % (url, e))
            continue
        el = main_section(page, site["kind"],
                          site.get("data_types", ("chapter", "appendix")))
        if el is None:
            problems.append("%s 未找到正文容器（kind=%s）" % (url, site["kind"]))
            continue
        text = to_text(el)
        min_chars = (site.get("min_chars_overrides") or {}).get(no, site["min_chars"])
        if len(text) < min_chars:
            problems.append("%s 正文字符数 %d < 阈值 %d（疑似截断）"
                            % (url, len(text), min_chars))
            continue
        # ⚠️ 章头格式必须与 `extract_sre_web.py` 一致（`=== <章号> | <标题> ===`）：
        # `validate_staging_shards.py` 以该正则切「章级正文」做节标题交叉校验；
        # 用其它格式（如 `## N. Title`）会使该机检**静默退化**为「无法读取所声明章」。
        blocks.append("=== %s | %s ===\n\n%s" % (no, title, text))
        toc.append({"chapter": no, "title": title, "url": url, "chars": len(text)})

    print("== %s（%s）==" % (slug, site["source_id"]))
    for c in toc:
        print("  [ok] 章 %-8s %-46s %d 字符" % (c["chapter"], c["title"][:46], c["chars"]))
    for p in problems:
        print("  ! %s" % p)
    if problems:
        print("== FAIL：%d 个问题，未落盘（fail-closed）==" % len(problems))
        return 1
    if len(toc) != len(chapters):
        print("== FAIL：目录 %d 章、成功 %d 章（不完整）==" % (len(chapters), len(toc)))
        return 1

    corpus = "\n\n".join(blocks) + "\n"
    toc_doc = {
        "source_id": site["source_id"],
        "book": site["book"],
        "edition": site["edition"],
        "license": site["license"],
        "toc": [{"chapter": c["chapter"], "title": c["title"]} for c in toc],
    }

    if args.stdout:
        print(corpus[:4000])
        return 0

    tp = resolve(root, os.path.join(TEXT_DIR, "%s.txt" % slug))
    os.makedirs(os.path.dirname(tp), exist_ok=True)
    with open(tp, "w", encoding="utf-8", newline="\n") as f:
        f.write(corpus)
    pp = resolve(root, os.path.join(PARTS, "toc-%s.json" % slug))
    with open(pp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(toc_doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("  wrote %s（%d 字符）" % (os.path.relpath(tp, root), len(corpus)))
    print("  wrote %s（%d 章）" % (os.path.relpath(pp, root), len(toc)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
