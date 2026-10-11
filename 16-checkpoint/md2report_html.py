#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2report_html.py — 把 Markdown 报告转成与既有报告视觉一致的 HTML（自包含、无外链）

用法：
  python3 16-checkpoint/md2report_html.py --md report-phase7p2.md --out report-phase7p2.html \
      --title "Mission 报告：阶段7 阶段2「内容增密」执行"
"""
import argparse
import html
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSS_SRC = os.path.join(ROOT, "report-phase7p2-plan.html")


def load_css():
    try:
        s = io.open(CSS_SRC, encoding="utf-8").read()
        m = re.search(r"<style>(.*?)</style>", s, re.S)
        return m.group(1) if m else ""
    except OSError:
        return ""


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t


def convert(md):
    out, i = [], 0
    lines = md.split("\n")
    n = len(lines)
    while i < n:
        ln = lines[i]
        # 代码块
        if ln.startswith("```"):
            buf, i = [], i + 1
            while i < n and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i])); i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % "\n".join(buf))
            continue
        # 表格
        if ln.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join("<th>%s</th>" % inline(c) for c in head)
            trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in rows)
            out.append('<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, trs))
            continue
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue
        # 分隔线
        if re.match(r"^\s*---+\s*$", ln):
            out.append("<hr>"); i += 1; continue
        # 引用
        if ln.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").strip()); i += 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(inline(b) for b in buf))
            continue
        # 列表
        if re.match(r"^\s*([-*]|\d+\.)\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.\s+", ln))
            tag = "ol" if ordered else "ul"
            buf = []
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                item = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                buf.append("<li>%s</li>" % inline(item)); i += 1
            out.append("<%s>%s</%s>" % (tag, "".join(buf), tag))
            continue
        # 空行 / 段落
        if not ln.strip():
            i += 1; continue
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6}\s|>|```|\s*([-*]|\d+\.)\s|\s*\|)", lines[i]) \
                and not re.match(r"^\s*---+\s*$", lines[i]):
            buf.append(lines[i]); i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf)))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Mission 报告")
    args = ap.parse_args()
    md = io.open(args.md, encoding="utf-8").read()
    body = convert(md)
    doc = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<style>
%s
.tw{overflow-x:auto}
</style>
</head>
<body>
<main class="wrap">
%s
</main>
</body>
</html>
""" % (html.escape(args.title), load_css(), body)
    io.open(args.out, "w", encoding="utf-8").write(doc)
    print("[out] %s (%d bytes)" % (args.out, len(doc)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
