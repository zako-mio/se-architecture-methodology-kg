#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成节点详情页：{out_nodes}/{node_id}.html（阶段6·A 案 · 浅色 Codex 文档流）

块序列（唯一顺序，见 00-plan/stage6-content-ia-spec.md §2）：
  §1 摘要与结论 · §2 局部关系图（内联静态 SVG）· §3 原理 · §4 机制 · §5 工程
  §6 权衡卡 · §7 学习路径条（条件）· §8 冲突 / 对比表（条件）· §9 案例带（条件）
  §10 信源与核验 · §11 原始关系清单 · 附 对照资源 · 12factor 子库

内容逐字取自数据（I3）；术语仅在页内首次出现时内联（§5）；零 JS（I4）。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (build_graph, sections, esc,
                        stage_badge, layer_badge, src_badge, type_badge,
                        group_badge, domain_badge, theme_badge,
                        priority_badge, verified_badge,
                        book_evidence_line,
                        BASE_CSS, EDGE_STYLE, TYPE_LABELS,
                        neighborhood_svg, nbhd_legend, nbhd_caption,
                        term_matcher_for, inline_terms, render_rich_paragraph,
                        split_tradeoff, derive_node_blocks, load_xref_index,
                        add_common_args, config_from_args)


# ---------------------------------------------------------------- 各块渲染

def _defcard(node, matcher, used, text):
    def_html = inline_terms(text, matcher, used)
    aliases = "、".join(node.get("aliases") or []) or "—"
    en = node.get("en") or "—"
    t = TYPE_LABELS.get(node.get("type"), node.get("type") or "")
    if node.get("subtype"):
        t = "%s / %s" % (t, node["subtype"])
    return ('<div class="defcard"><span class="lab">TL;DR · 一句话结论</span>'
            '<p><span class="lead">%s</span></p></div>'
            '<p class="note">别名：%s　|　英文：%s　|　类型：%s</p>'
            % (def_html, esc(aliases), esc(en), esc(t)))


def _relation_figure(g, nid):
    return ('<figure><div class="figbox">%s</div>%s<figcaption>%s</figcaption></figure>'
            % (neighborhood_svg(g, nid), nbhd_legend(), esc(nbhd_caption(g, nid))))


def _rich_section(text, matcher, used):
    return '<p class="lede">%s</p>' % render_rich_paragraph(text, matcher, used)


def _tradeoff_card(text, matcher, used):
    cols, neutral = split_tradeoff(text)
    rows = []
    for key, label in (("gain", "收益 · 正确姿势"), ("cost", "代价 · 风险"), ("counter", "反例 · 误区")):
        if not cols[key]:
            continue
        body = "".join("<p>%s</p>" % inline_terms(s, matcher, used) for s in cols[key])
        rows.append('<div class="row %s"><div class="h">%s</div><div class="b">%s</div></div>'
                    % (key, esc(label), body))
    if neutral:
        items = "".join("<li>%s</li>" % inline_terms(s, matcher, used) for s in neutral)
        rows.append('<div class="row neutral"><div class="h">原文要点</div>'
                    '<ul class="b">%s</ul></div>' % items)
    if not rows:
        return ""
    note = ('<p class="note">权衡原文仅按显式标记词归栏引用（收益 / 代价 / 反例），'
            '其余句子按原序列为「原文要点」；内容逐字引用未改写。</p>')
    return '<div class="tradeoff">%s</div>%s' % ("".join(rows), note)


def _pathbar(g, nid, preds, succs):
    def step(x, cur=False):
        nm = g.by_id.get(x, {}).get("name", x)
        return ('<span class="step%s"><span class="id">%s</span><span class="nm">%s</span></span>'
                % (" cur" if cur else "", esc(x), esc(nm)))

    seq = [step(x) for x in preds] + [step(nid, True)] + [step(x) for x in succs]
    return '<div class="pathbar">%s</div>' % '<span class="arw">→</span>'.join(seq)


def _compare_tables(g, nid, tables, matcher, used):
    cur = g.by_id.get(nid, {})
    out = []
    for t in tables:
        e = t["edge"]
        body = "".join('<tr><td class="k">%s</td><td>%s</td><td>%s</td></tr>'
                       % (esc(k), inline_terms(a or "—", matcher, used), inline_terms(b or "—", matcher, used))
                       for k, a, b in t["rows"])
        out.append('<div class="tblwrap"><table class="cmp"><caption>真实 %s 边：%s</caption>'
                   '<thead><tr><th>对照维度</th><th>%s</th><th>%s</th></tr></thead>'
                   '<tbody>%s</tbody></table></div>'
                   % (esc(t["label"]), esc(e.get("label", "")), esc(cur.get("name", nid)),
                      esc(t["other_name"]), body))
    return "".join(out)


def _case_band(items):
    if not items:
        return ""
    cards = []
    for cid, label, cs in items:
        cards.append('<div class="case-card"><span class="id">%s · %s</span>'
                     '<h4>%s</h4><p>%s</p></div>'
                     % (esc(cid), esc(label), esc(cs.get("title", cid)), esc(cs.get("summary", ""))))
    return '<div class="case-band">%s</div>' % "".join(cards)


def _evidence(g, node):
    def kv(k, val):
        if val in (None, "", [], {}):
            return ""
        return '<div class="r"><span class="k">%s</span>%s</div>' % (esc(k), esc(val))

    rows = []
    v = node.get("verified")
    if v is not None:
        rows.append('<div class="r"><span class="k">核验状态</span>%s</div>'
                    % esc("True（verified）" if v else "False（unverified）"))
    rows.append(kv("置信度", node.get("confidence")))
    rows.append(kv("复核日期", node.get("review_date")))
    rows.append(kv("生命周期", node.get("status")))
    rows.append(kv("版本", node.get("version")))
    if node.get("sources"):
        rows.append('<div class="r"><span class="k">规范信源</span>%s</div>'
                    % esc("、".join(node["sources"])))
    book_ev = book_evidence_line(g.book_verification, node.get("id"))
    if book_ev:
        rows.append('<div class="r"><span class="k">书证核验</span>%s</div>' % esc(book_ev))
    links = []
    for u in node.get("entry_links") or []:
        if str(u).startswith("http"):
            links.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(u), esc(u)))
    if links:
        rows.append('<div class="r"><span class="k">入口链接</span>%s</div>' % "　".join(links))
    for er in node.get("errata") or []:
        rows.append('<div class="r" style="display:block"><span class="k">勘误</span>'
                    '<div class="erratum"><span class="m">常见误解：%s</span><br>'
                    '核验结论：%s　<span class="k">[%s]</span></div></div>'
                    % (esc(er.get("misconception", "")), esc(er.get("verified_value", "")),
                       esc(er.get("source_id", ""))))
    if not rows:
        return ""
    return '<div class="evidence">%s</div>' % "".join(rows)


def _relations(g, nid, my):
    if not my:
        return ""
    rows = []
    for e in my:
        direction = "→ %s" % e["to"] if e["from"] == nid else "← %s" % e["from"]
        other = e["to"] if e["from"] == nid else e["from"]
        onm = g.by_id.get(other, {}).get("name", other)
        tlabel = EDGE_STYLE.get(e["type"], {}).get("label", e["type"])
        rows.append('<tr><td class="k">%s</td><td>%s</td><td>%s<br>'
                    '<span style="color:var(--dim);font-size:12px">%s</span></td><td>%s</td></tr>'
                    % (esc(tlabel), esc(direction), esc(onm), esc(e.get("id", "")),
                       esc(e.get("label", ""))))
    return ('<details><summary>展开：本节点的全部原始关系边（%d 条，含边 ID 与方向）</summary>'
            '<div class="in"><div class="tblwrap"><table><thead><tr><th>关系</th><th>方向</th>'
            '<th>对端节点</th><th>说明</th></tr></thead><tbody>%s</tbody></table></div></div></details>'
            % (len(my), "".join(rows)))


def _xref_section(g, nid):
    xrows = load_xref_index(g.cfg).get(nid) or []
    if not xrows:
        return ""
    body = ['<div class="tblwrap"><table><thead><tr><th>12factor 节点</th><th>关系</th>'
            '<th>对照说明</th></tr></thead><tbody>']
    for r in xrows:
        link = r.get("deep_link") or ""
        name = r.get("tf_name") or r.get("tf_id") or ""
        tfid = r.get("tf_id") or ""
        if link:
            cell = ('<a href="%s" target="_blank" rel="noopener">%s</a> <span class="dim">%s</span>'
                    % (esc(link), esc(name), esc(tfid)))
        else:
            cell = esc(name)
        rel = r.get("relation") or ""
        rel_label = EDGE_STYLE.get(rel, {}).get("label", rel)
        body.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (cell, esc(rel_label), esc(r.get("rationale") or "")))
    body.append("</tbody></table></div>")
    return "".join(body)


# ---------------------------------------------------------------- 页面组装

_BLOCK_RENDER = {}


def _render_block(g, block, matcher, used):
    k = block["kind"]
    if k == "summary":
        return _defcard(block["node"], matcher, used, block["text"])
    if k == "relation":
        return _relation_figure(g, block["nid"])
    if k in ("principle", "mechanism", "engineering"):
        return _rich_section(block["text"], matcher, used)
    if k == "tradeoff":
        return _tradeoff_card(block["text"], matcher, used)
    if k == "path":
        return _pathbar(g, block["nid"], block["preds"], block["succs"])
    if k == "compare":
        return _compare_tables(g, block["nid"], block["tables"], matcher, used)
    if k == "cases":
        return _case_band(block["items"])
    if k == "evidence":
        return _evidence(g, block["node"])
    if k == "relations":
        return _relations(g, block["nid"], block["edges"])
    return ""


def node_html(g, node):
    nid = node["id"]
    gid = node["group"] or ""
    group = g.group_by_id.get(gid, {})
    gname = group.get("name", gid)
    matcher = term_matcher_for(g.cfg)
    used = set()

    blocks = []
    for b in derive_node_blocks(g, node):
        blocks.append((b["title"], _render_block(g, b, matcher, used)))
    blocks = [(t, h) for t, h in blocks if h]

    toc = ['<div class="t">目录 · CONTENTS</div>']
    body_parts = []
    for i, (title, inner) in enumerate(blocks, 1):
        toc.append('<a href="#s%d"><span class="n">§%d</span>%s</a>' % (i, i, esc(title)))
        body_parts.append('<section id="s%d"><h2><span class="num">§%d</span>%s</h2>%s</section>'
                          % (i, i, esc(title), inner))
    xref = _xref_section(g, nid)
    if xref:
        toc.append('<a href="#xref"><span class="n">附</span>对照资源</a>')
        body_parts.append('<section id="xref"><h2><span class="num">附</span>'
                          '对照资源 · 12factor 子库</h2>%s</section>' % xref)

    badges = (priority_badge(node.get("priority")) + stage_badge(node.get("stage"))
              + verified_badge(node.get("verified")) + src_badge(node.get("src"))
              + layer_badge(node.get("layer")) + type_badge(node)
              + domain_badge(node.get("domain"), g.cfg)
              + "".join(theme_badge(x, g.cfg) for x in node.get("cross_cutting", []))
              + (group_badge(gid, gname) if gid else ""))

    crumb = ('<div class="crumb"><a href="../%s">%s</a> <span class="sep">/</span> '
             '<a href="../%s/index.html">分组目录</a> <span class="sep">/</span> '
             '<a href="../%s/%s.html">%s</a> <span class="sep">/</span> <span>%s</span></div>'
             % (esc(g.cfg["root_index"]), esc(g.cfg["title"]),
                esc(g.cfg["out_dirs"]["groups"]), esc(g.cfg["out_dirs"]["groups"]),
                esc(gid), esc(gname), esc(node["name"])))
    topmeta = " · ".join(str(x) for x in [node.get("layer"), node.get("domain"),
                                          node.get("priority"), node.get("status")] if x)
    topbar = ('<div class="topbar"><div class="in">%s'
              '<div class="meta">%s</div></div></div>' % (crumb, esc(topmeta)))
    doc = ('<header class="doc"><h1>%s</h1><div class="en">%s</div>'
           '<div class="badges">%s</div></header>'
           % (esc(node["name"]), esc(node.get("en") or ""), badges))
    try:
        data_rel = os.path.relpath(g.cfg.get("dag_path") or "", g.cfg["repo_root"])
    except ValueError:
        data_rel = g.cfg.get("dag_file") or "methodology-dag.json"
    footer = ('<footer>%s · 节点页由 16-checkpoint/gen-nodes.py 生成 · 数据源 %s</footer>'
              % (esc(g.cfg["title"]), esc(data_rel.replace(os.sep, "/"))))

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} · {title}</title>
<style>
{extra_css}
</style>
</head>
<body>
{topbar}
<div class="wrap">
{toc}
<article>
{doc}
{body}
{footer}
</article>
</div>
</body>
</html>
""".format(name=esc(node["name"]), title=esc(g.cfg["title"]), extra_css=BASE_CSS,
           topbar=topbar, toc='<nav class="toc">%s</nav>' % "".join(toc), doc=doc,
           body="\n".join(body_parts), footer=footer)


def run(cfg):
    out = cfg["out_paths"]["nodes"]
    os.makedirs(out, exist_ok=True)
    g = build_graph(cfg)
    for node in g.nodes:
        with open(os.path.join(out, node["id"] + ".html"), "w", encoding="utf-8") as f:
            f.write(node_html(g, node))
    return {"kind": "nodes", "written": len(g.nodes), "dir": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成节点详情页")
    add_common_args(ap)
    args = ap.parse_args(argv)
    res = run(config_from_args(args))
    print("node pages written: %d -> %s" % (res["written"], res["dir"]))


if __name__ == "__main__":
    main()
