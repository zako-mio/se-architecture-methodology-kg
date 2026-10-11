#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_book_text.py — EPUB → 纯文本抽取（核验层私有语料）

用途：把已获取的 EPUB 按 **spine 顺序**抽成纯文本，落到私有层
  `01-books/_verify/_text/<slug>.txt`
供核验（claim 改写红线机检）与证据展开使用。

性质：确定性（无时间戳）、UTF-8 无 BOM、末尾换行；只读 EPUB、只写私有层。
隔离：`01-books/` 已被本地仓 `.gitignore:13` 整体忽略；`_publish/.gitignore` 显式忽略
  `01-books/_verify/`；装配层 `publish-manifest.json` 把 `01-books/_verify/` 列为 private。

用法：
  python3 16-checkpoint/extract_book_text.py \
      --epub 01-books/_files/P1-23/P1-23_team-topologies_2019.epub \
      --slug team-topologies
  python3 16-checkpoint/extract_book_text.py --epub <p> --slug <s> --stdout | head
"""
import argparse
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
TEXT_DIR = os.path.join("01-books", "_verify", "_text")

SKIP_TAGS = ("script", "style", "head", "title", "meta", "link")
BLOCK_TAGS = ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr",
              "blockquote", "pre", "figcaption", "dt", "dd", "section", "article")


def default_root():
    return ROOT_DEFAULT


def read_container(zf):
    """返回 OPF 路径（相对 zip 根）。"""
    with zf.open("META-INF/container.xml") as f:
        data = f.read().decode("utf-8", "replace")
    m = re.search(r'full-path\s*=\s*"([^"]+)"', data)
    if not m:
        raise ValueError("container.xml 中未找到 rootfile full-path")
    return m.group(1)


def parse_opf(zf, opf_path):
    """返回 (spine_hrefs, manifest_id2href)。仅取 spine 顺序。"""
    from lxml import etree
    base = os.path.dirname(opf_path)
    with zf.open(opf_path) as f:
        root = etree.fromstring(f.read())
    ns = {"o": "http://www.idpf.org/2007/opf"}
    id2href = {}
    for item in root.findall(".//o:manifest/o:item", ns):
        iid = item.get("id")
        href = item.get("href")
        if iid and href:
            id2href[iid] = href
    spine = []
    for ref in root.findall(".//o:spine/o:itemref", ns):
        iid = ref.get("idref")
        if iid and iid in id2href:
            href = id2href[iid]
            spine.append(os.path.normpath(os.path.join(base, href)) if base else href)
    if not spine:
        # 回退：manifest 中所有 html/xhtml，按文件名排序
        spine = sorted(h for h in id2href.values()
                       if h.lower().endswith((".html", ".xhtml", ".htm")))
    return spine


def _local(tag):
    """取标签本地名（剥离 XHTML 默认命名空间前缀）。"""
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1].lower()


def html_to_text(raw):
    """HTML → 纯文本：按块级标签切段，段内空白折叠，段间空行分隔。

    兼容 XHTML 默认命名空间（`{http://www.w3.org/1999/xhtml}p`）——
    Team Topologies 的 EPUB 用命名空间，未剥离时块级标签全部漏采。
    """
    from lxml import html as LH
    if isinstance(raw, str):
        # lxml 拒绝「带编码声明的 str」→ 剥离 XML 声明后转 bytes
        raw = re.sub(r"^\s*<\?xml[^>]*\?>", "", raw, count=1).encode("utf-8")
    try:
        doc = LH.fromstring(raw)
    except Exception:
        return ""
    if doc is None:
        return ""
    for el in list(doc.iter()):
        if _local(el.tag) in SKIP_TAGS and el.getparent() is not None:
            el.getparent().remove(el)
    lines = []
    for el in doc.iter():
        if _local(el.tag) not in BLOCK_TAGS:
            continue
        # 只取叶子块：避免父子块重复采集
        if any(_local(c.tag) in BLOCK_TAGS for c in el):
            continue
        txt = " ".join(el.itertext())
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            lines.append(txt)
    if not lines:
        txt = re.sub(r"\s+", " ", " ".join(doc.itertext())).strip()
        return txt
    return "\n\n".join(lines)


def extract(epub_path, slug=None, drop_front_matter=True):
    with zipfile.ZipFile(epub_path) as zf:
        opf = read_container(zf)
        spine = parse_opf(zf, opf)
        chunks = []
        for href in spine:
            name = href.replace("\\", "/")
            if name not in zf.namelist():
                # 大小写/前缀容错
                cands = [n for n in zf.namelist() if n.lower() == name.lower()]
                if not cands:
                    continue
                name = cands[0]
            if not name.lower().endswith((".html", ".xhtml", ".htm")):
                continue
            with zf.open(name) as f:
                raw = f.read().decode("utf-8", "replace")
            txt = html_to_text(raw)
            if txt:
                chunks.append(txt)
    body = "\n\n".join(chunks)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="EPUB → 纯文本（私有核验语料）")
    ap.add_argument("--epub", required=True, help="EPUB 路径")
    ap.add_argument("--slug", required=True, help="输出 slug（_text/<slug>.txt）")
    ap.add_argument("--root", default=default_root(), help="母库 root")
    ap.add_argument("--stdout", action="store_true", help="只打印，不写文件")
    args = ap.parse_args()

    epub = args.epub if os.path.isabs(args.epub) else os.path.join(args.root, args.epub)
    text = extract(epub, args.slug)
    if args.stdout:
        sys.stdout.write(text)
        return 0
    out = os.path.join(args.root, TEXT_DIR, "%s.txt" % args.slug)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("chars=%d bytes=%d" % (len(text), len(text.encode("utf-8"))))
    print("wrote %s" % os.path.relpath(out, args.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
