#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成术语表页：{out_views}/glossary.html（由 03-knowledge-map/glossary.md 派生）。

- 每个 H2 分区渲染为带锚点的章节；每个词条渲染为表格行，行锚点 g-001、g-002…
- 供节点页正文术语内联（a.term）深链，锚点在生成期与节点页同源（gen_common.load_glossary）。
- 内容逐字取自 glossary.md（不修改源文件）；零 JS、自包含、浅色 Codex 皮肤。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (esc, load_glossary, BASE_CSS, config_from_args, add_common_args)

EXTRA = """
.glossary tr[id]{scroll-margin-top:84px;}
.glossary th{white-space:nowrap;}
.glossary td.gterm{font-weight:600;white-space:nowrap;color:var(--text);}
.glossary td.gdef{font-size:14px;}
.glossary td.gsrc{font-size:12px;color:var(--dim);white-space:normal;}
.glossary .badge.disputed{color:#8a3b12;border-color:#e0b79a;background:#fbf1e8;}
.glossary .badge.settled{color:#1f6f5c;border-color:#a9cbbf;background:#eef7f2;}
.glossary .gcount{font-size:12.5px;color:var(--dim);margin:-4px 0 12px;}
"""


def render(cfg):
    data = load_glossary(cfg)
    sections = data["sections"]
    entries = data["entries"]
    title = "全局术语表"

    toc = ['<div class="t">目录 · SECTIONS</div>']
    body = []
    for si, sec in enumerate(sections):
        sid = sec["id"]
        toc.append('<a href="#%s"><span class="n">%d</span>%s</a>' % (sid, si + 1, esc(sec["title"])))
        rows = []
        for e in sec["entries"]:
            status = e["status"]
            scls = "settled" if status == "settled" else ("disputed" if status == "disputed" else "")
            stitle = "（无权威共识，给推荐口径）" if status == "disputed" else ""
            rows.append(
                '<tr id="%s"><td class="gterm">%s</td><td>%s</td><td class="gdef">%s</td>'
                '<td class="gsrc">%s</td><td><span class="badge %s" title="%s">%s</span></td></tr>'
                % (esc(e["anchor"]), esc(e["term"]), esc(e["english"]), esc(e["definition"]),
                   esc(e["source_id"]), esc(scls), esc(stitle), esc(status)))
        body.append(
            '<section id="%s"><h2><span class="num">§%d</span>%s</h2>'
            '<div class="gcount">共 %d 个词条</div>'
            '<div class="tblwrap"><table><thead><tr><th>术语</th><th>English</th>'
            '<th>定义（统一口径）</th><th>source_id</th><th>状态</th></tr></thead>'
            '<tbody>%s</tbody></table></div></section>'
            % (sid, si + 1, esc(sec["title"]), len(sec["entries"]), "".join(rows)))

    topmeta = "%d 个分区 · %d 个词条" % (len(sections), len(entries))
    topbar = ('<div class="topbar"><div class="in">'
              '<div class="crumb"><a href="../%s">%s</a> <span class="sep">/</span> '
              '<a href="index.html">视图入口</a> <span class="sep">/</span> <span>%s</span></div>'
              '<div class="meta">%s</div></div></div>'
              % (esc(cfg["root_index"]), esc(cfg["title"]), esc(title), esc(topmeta)))
    doc = ('<header class="doc"><h1>%s</h1><div class="en">Glossary</div>'
           '<div class="badges"><span class="badge">%d 分区</span>'
           '<span class="badge">%d 词条</span><span class="badge">anchors g-001…</span></div></header>'
           % (esc(title), len(sections), len(entries)))
    footer = ('<footer>%s · 术语表由 16-checkpoint/gen-glossary.py 生成 · '
              '源 03-knowledge-map/glossary.md（逐字引用）</footer>' % esc(cfg["title"]))

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · {site}</title>
<style>
{css}{extra}
</style>
</head>
<body>
{topbar}
<div class="wrap">
<nav class="toc">{toc}</nav>
<article class="glossary">
{doc}
{body}
{footer}
</article>
</div>
</body>
</html>
""".format(title=esc(title), site=esc(cfg["title"]), css=BASE_CSS, extra=EXTRA,
           topbar=topbar, toc="".join(toc), doc=doc, body="\n".join(body), footer=footer)


def run(cfg):
    data = load_glossary(cfg)
    if not data["entries"]:
        # 无术语源（如 12factor 旧库）时不产出，保持该 preset 产出计数不变
        return {"kind": "glossary", "written": 0, "entries": 0, "sections": 0, "skipped": True,
                "path": os.path.join(cfg["out_paths"]["views"], "glossary.html")}
    out = cfg["out_paths"]["views"]
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "glossary.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(render(cfg))
    return {"kind": "glossary", "written": 1, "entries": len(data["entries"]),
            "sections": len(data["sections"]), "path": path}


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成术语表页")
    add_common_args(ap)
    args = ap.parse_args(argv)
    res = run(config_from_args(args))
    if res.get("skipped"):
        print("glossary skipped: 无术语源（%s）" % res["path"])
    else:
        print("glossary written: %d entries / %d sections -> %s"
              % (res["entries"], res["sections"], res["path"]))


if __name__ == "__main__":
    main()
