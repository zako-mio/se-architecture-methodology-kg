#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_sre_web.py — sre.google 在线书 → 私有层纯文本 + 自建 TOC 分片

用途：把 `https://sre.google/{sre-book,workbook}/` 的**全文**（静态 HTML）抽成私有层语料，
供核验层（ledger/claims/gaps）与改写红线机检使用。

产出（均落私有层，`01-books/` 被本地仓 .gitignore 整体忽略）：
  · 01-books/_verify/_text/<slug>.txt
  · 01-books/_verify/_parts/toc-<slug>.json

性质：确定性（无时间戳）、UTF-8 无 BOM、末尾换行；只读站点、只写私有层。
      章节顺序按目录页出现顺序；章号取自页面 `<h2 class="chapter-title">`（形如 `Chapter N - Title`
      或 `Appendix X - Title`），**不依赖 NCX**（该站点无 NCX，故 TOC 自建）。

护栏（fail-closed）：
  · 0 章 → 报错退出（不写 0 章 TOC）
  · 章节页抓取失败 / 正文字符数低于阈值 → 报错退出
  · 目录页链接数与成功抽取章数不符 → 报错退出（防站点结构变动静默截断）

许可：CC BY-NC-ND 4.0（只做私有层采集与核验；公开层处置另案裁决）。

用法：
  python3 16-checkpoint/extract_sre_web.py --site sre-book
  python3 16-checkpoint/extract_sre_web.py --site workbook --stdout | head
"""
import argparse
import html as html_mod
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
TEXT_DIR = os.path.join("01-books", "_verify", "_text")
PARTS = os.path.join("01-books", "_verify", "_parts")

SITES = {
    "sre-book": {
        "prefix": "/sre-book/",
        "toc_url": "https://sre.google/sre-book/table-of-contents/",
        "slug": "sre-book",
        "source_id": "BK-025",
        "book": "Site Reliability Engineering: How Google Runs Production Systems",
        "edition": "1st/2016",
        "min_chars": 800,
        # 无章号但属全书结构的页 → 固定标签（须收录）
        "label_map": {"Foreword": "Foreword", "Preface": "Preface"},
        # 无章号且非正文的页 → 结构页（跳过，且不计入「抓取不完整」）
        "structural": (),
    },
    "workbook": {
        "prefix": "/workbook/",
        "toc_url": "https://sre.google/workbook/table-of-contents/",
        "slug": "workbook",
        "source_id": "BK-026",
        "book": "The Site Reliability Workbook: Practical Ways to Implement SRE",
        "edition": "1st/2018",
        "min_chars": 800,
        "label_map": {"Foreword I": "Foreword I", "Foreword II": "Foreword II",
                      "Preface": "Preface", "Conclusion": "Conclusion",
                      "About the Editors": "About the Editors"},
        "structural": ("Index", "Colophon"),
    },
}

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
SKIP_TAGS = ("script", "style", "head", "title", "meta", "link", "nav", "footer")
BLOCK_TAGS = ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr",
              "blockquote", "pre", "figcaption", "dt", "dd", "section", "article")
# 非正文页（part 分隔页 / 目录页 / 书目页不构成章节）
NON_CHAPTER = ("table-of-contents", "bibliography")


def fetch(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def strip_tags(s):
    return html_mod.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def toc_links(toc_html, prefix):
    """按目录页出现顺序返回 (rel_path, absolute_url) 去重列表。"""
    out = []
    seen = set()
    for m in re.finditer(r'href="(%s[^"#?]+)"' % re.escape(prefix), toc_html):
        rel = m.group(1)
        if rel in seen:
            continue
        seen.add(rel)
        out.append(rel)
    return out


def is_chapter(rel):
    tail = rel[len(rel.rstrip("/").rsplit("/", 1)[0]) + 1:].strip("/")
    if not tail:
        return False
    if tail.startswith("part-"):
        return False
    if tail in NON_CHAPTER:
        return False
    return True


def main_section(page_html):
    """用 DOM 取正文容器：优先 <section data-type="chapter|appendix">，回退 <div id="content">。

    ⚠️ 必须用 DOM（而非非贪婪正则）：章节正文内含**嵌套 <section>**，
    非贪婪 `.*?</section>` 会在第一个嵌套节闭合处截断（实测某章 25 389 字符被截为 3 863）。
    """
    from lxml import etree
    parser = etree.HTMLParser(recover=True, huge_tree=True)
    tree = etree.fromstring(page_html.encode("utf-8"), parser)
    if tree is None:
        return None
    for el in tree.iter():
        tag = getattr(el, "tag", None)
        if not isinstance(tag, str):
            continue
        if tag.lower() == "section" and (el.get("data-type") or "") in ("chapter", "appendix"):
            return el
    for el in tree.iter():
        if isinstance(getattr(el, "tag", None), str) and el.get("id") == "content":
            return el
    return None


def to_text(el):
    """DOM 元素 → 纯文本（块级标签转换行，压空白，保留段落空行）。"""
    parts = []

    def walk(node, depth=0):
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
            walk(child, depth + 1)
            if child.tail:
                parts.append(child.tail)
        if block and parts and parts[-1] != "\n":
            parts.append("\n")

    walk(el)
    s = "".join(parts)
    s = html_mod.unescape(s)
    s = s.replace("\xa0", " ").replace("\u200b", "")
    s = re.sub(r"[ \t]+", " ", s)
    lines = [ln.strip() for ln in s.split("\n")]
    out = []
    blank = False
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank and out:
            out.append("")
            blank = True
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def chapter_no_title(page_html, label_map):
    """从 <h2 class="chapter-title"> 取 (chapter_no, chapter_title, structural)。

    章号形态：`Chapter N - Title` / `Appendix X - Title`；无章号页按 `label_map`
    映射为固定标签（须收录）；既无章号又不在 label_map 者记为结构页（调用方跳过）。
    """
    m = re.search(r'(?is)<h2[^>]*class="chapter-title"[^>]*>(.*?)</h2>', page_html)
    if not m:
        return None, None, True
    raw = strip_tags(m.group(1))
    mm = re.match(r"^(Chapter|Appendix)\s+([0-9A-Z]+)\s*[-–—]\s*(.+)$", raw)
    if mm:
        kind, no, title = mm.group(1), mm.group(2), mm.group(3).strip()
        return (no if kind == "Chapter" else "Appendix %s" % no), title, False
    if raw in label_map:
        return label_map[raw], raw, False
    return None, raw, True


def main():
    ap = argparse.ArgumentParser(description="sre.google 在线书 → 私有层语料 + 自建 TOC")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--site", required=True, choices=sorted(SITES))
    ap.add_argument("--stdout", action="store_true", help="只打印，不落盘")
    ap.add_argument("--timeout", type=int, default=45)
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    cfg = SITES[args.site]

    print("=" * 84)
    print("sre.google 采集：%s（%s / %s）" % (cfg["slug"], cfg["source_id"], cfg["edition"]))
    print("  TOC = %s" % cfg["toc_url"])
    print("  许可 = CC BY-NC-ND 4.0（仅私有层）")
    print("=" * 84)

    toc_html = fetch(cfg["toc_url"], args.timeout)
    links = [r for r in toc_links(toc_html, cfg["prefix"]) if is_chapter(r)]
    print("\n[1] 目录页：%d 个去重章节链接（已排除 part 分隔页 / 目录页 / 书目页）" % len(links))

    chapters = []
    texts = []
    problems = []
    skipped_structural = []
    for i, rel in enumerate(links, 1):
        url = "https://sre.google" + rel
        try:
            page = fetch(url, args.timeout)
        except Exception as exc:                       # noqa: BLE001
            problems.append("%s 抓取失败: %s" % (rel, exc))
            continue
        frag = main_section(page)
        if frag is None:
            problems.append("%s 未找到正文容器" % rel)
            continue
        body = to_text(frag)
        no, title, structural = chapter_no_title(page, cfg["label_map"])
        if structural:
            # 无章号且非全书结构页（Index / Colophon 之类）：跳过，不计入抓取不完整
            skipped_structural.append("%s（%s）" % (rel, title))
            continue
        if len(body) < cfg["min_chars"]:
            problems.append("%s 正文过短（%d < %d）" % (rel, len(body), cfg["min_chars"]))
            continue
        chapters.append({
            "chapter": no,
            "title": title,
            "sections": [],
            "_rel": rel,
            "_url": url,
            "_chars": len(body),
        })
        texts.append("=== %s | %s ===\n\n%s" % (no, title, body))
        print("    [%2d/%2d] %-12s %-42s %6d 字符" % (i, len(links), no, title[:42], len(body)))

    expected = len(links) - len(skipped_structural)
    print("\n[2] 抽取结果：成功 %d / 应抽 %d（链接 %d，结构页跳过 %d）"
          % (len(chapters), expected, len(links), len(skipped_structural)))
    for s in skipped_structural:
        print("    - 结构页跳过：%s" % s)
    for p in problems:
        print("    ! %s" % p)

    # ---- 护栏（fail-closed）----
    if not chapters:
        print("\n  == 结果 = FAIL（0 章；拒绝落盘）==")
        return 1
    if problems or len(chapters) != expected:
        print("\n  == 结果 = FAIL（抓取不完整 %d/%d；拒绝落盘）==" % (len(chapters), expected))
        return 1

    text_doc = "\n\n".join(texts) + "\n"
    toc_doc = {
        "source_id": cfg["source_id"],
        "book": cfg["book"],
        "edition": cfg["edition"],
        "toc": [{"chapter": c["chapter"], "title": c["title"], "sections": c["sections"]}
                for c in chapters],
    }

    if args.stdout:
        print(text_doc[:1200])
        return 0

    tpath = os.path.join(root, TEXT_DIR, "%s.txt" % cfg["slug"])
    jpath = os.path.join(root, PARTS, "toc-%s.json" % cfg["slug"])
    os.makedirs(os.path.dirname(tpath), exist_ok=True)
    os.makedirs(os.path.dirname(jpath), exist_ok=True)
    with open(tpath, "w", encoding="utf-8", newline="\n") as f:
        f.write(text_doc)
    import json
    with open(jpath, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(toc_doc, ensure_ascii=False, indent=2, sort_keys=False) + "\n")
    print("\n[3] wrote %s（%d 字符）" % (os.path.relpath(tpath, root), len(text_doc)))
    print("    wrote %s（%d 章）" % (os.path.relpath(jpath, root), len(chapters)))
    print("\n  == 结果 = PASS ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
