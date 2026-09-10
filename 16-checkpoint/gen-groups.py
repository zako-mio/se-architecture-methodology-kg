#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成组页 {out_groups}/{group_id}.html 与组总索引 {out_groups}/index.html。

组页（浅色 Codex 外壳，对齐 11-node-pages）：组简介 + 成员表 + 组内关系图（复用
gen_common 确定性子图 SVG 构造器）+ 组内 prerequisite 拓扑推荐顺序 + 入/出组依赖。
组索引：按 group_kind 分类卡片（层组/域组/来源组/主题组/横切组/案例组/工具组）。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (build_graph, esc, topo_sort, stage_badge, kind_badge,
                        layer_badge, src_badge, domain_badge,
                        group_subgraph_svg, group_subgraph_caption, nbhd_legend,
                        page_shell, STAGE_STYLE, KIND_STYLE, KIND_ORDER,
                        add_common_args, config_from_args)

EXTRA_CSS = """
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:12px 0;}
.card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px 18px;}
a.card{display:block;text-decoration:none;}
.card:hover{border-color:var(--accent);}
.card h3{font-size:15px;color:var(--accent);margin:0 0 6px;}
.card .meta{font-size:12px;color:var(--dim);margin-bottom:4px;}
.stat{display:inline-block;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:4px;text-align:center;}
.stat b{display:block;font-size:22px;color:var(--accent);}
.stat span{font-size:12px;color:var(--dim);}
.stage-row .badge{margin-right:6px;}
"""


def build_treenav(g):
    items = ['<a href="%s.html">%s</a>' % (esc(gp["id"]), esc(gp["name"])) for gp in g.groups]
    return '<div class="treenav"><span class="label">组目录:</span>%s</div>' % "".join(items)


def group_html(g, group):
    gid = group["id"]
    gname = group["name"]
    node_ids = [n for n in group["node_ids"] if n in g.by_id]
    members = set(node_ids)
    edges = g.edges

    stages = [g.by_id[nid]["stage"] for nid in node_ids]
    stage_set = sorted(set(stages), key=lambda s: (["basic", "intermediate", "advanced"].index(s)
                                                   if s in ["basic", "intermediate", "advanced"] else 99))
    in_prereq = [e for e in edges if e["type"] == "prerequisite" and e["from"] in members and e["to"] in members]
    topo = topo_sort(node_ids, edges) if node_ids else []
    external_in = sorted([e for e in edges if e["type"] == "prerequisite"
                          and e["from"] not in members and e["to"] in members], key=lambda e: e["to"])
    external_out = sorted([e for e in edges if e["type"] == "prerequisite"
                           and e["from"] in members and e["to"] not in members], key=lambda e: e["from"])

    def link(nid):
        return '<a href="../%s/%s.html">%s</a>' % (esc(g.cfg["out_dirs"]["nodes"]), esc(nid),
                                                   esc(g.by_id[nid]["name"]))

    # §1 组简介
    intro = [build_treenav(g)]
    intro.append('<p>本组 <strong>%d</strong> 个节点，类型为 <strong>%s</strong>，域 <strong>%s</strong>，'
                 '覆盖阶段 <strong>%s</strong>。</p>'
                 % (len(node_ids), esc(KIND_STYLE.get(group["kind"], {}).get("label", group["kind"])),
                    esc(group.get("domain", "") or "—"),
                    esc(" / ".join(STAGE_STYLE[s]["label"] for s in stage_set if s in STAGE_STYLE))))
    intro.append('<div class="navseq">'
                 '<a class="nav-index" href="index.html"><span class="dir">&#8592; 上一页</span>'
                 '<span class="v">组总索引</span></a>'
                 '<a class="nav-index" href="../%s/index.html"><span class="dir">全局</span>'
                 '<span class="v">交互总览</span></a>'
                 '<a class="nav-index" href="../%s/index.html"><span class="dir">视图</span>'
                 '<span class="v">视图入口</span></a>'
                 '</div>' % (esc(g.cfg["out_dirs"]["interactive"]), esc(g.cfg["out_dirs"]["views"])))

    # §2 成员节点目录
    rows = []
    for nid in node_ids:
        n = g.by_id[nid]
        rows.append(
            '<tr><td class="nid"><a href="../%s/%s.html">%s</a></td>'
            '<td><a href="../%s/%s.html" class="nname">%s</a></td>'
            '<td>%s</td><td>%s</td><td class="brief">%s</td></tr>'
            % (esc(g.cfg["out_dirs"]["nodes"]), esc(nid), esc(nid),
               esc(g.cfg["out_dirs"]["nodes"]), esc(nid), esc(n["name"]),
               (src_badge(n.get("src")) or layer_badge(n.get("layer"))),
               stage_badge(n.get("stage")), esc(n["definition"])))
    catalog = ('<div class="tblwrap"><table><thead><tr><th>节点 ID</th><th>名称</th><th>层/来源</th>'
               '<th>阶段</th><th>简介</th></tr></thead><tbody>%s</tbody></table></div>'
               % "".join(rows)) if rows else '<p class="dim">本组暂无成员节点。</p>'

    # §3 组内关系图
    svg = group_subgraph_svg(g, node_ids, name=gname)
    if svg:
        rel = ('<figure><div class="figbox">%s</div>%s<figcaption>%s</figcaption></figure>'
               % (svg, nbhd_legend(), esc(group_subgraph_caption(g, node_ids, name=gname))))
    else:
        rel = '<p class="dim">本组暂无节点，无法生成组内关系图。</p>'

    # §4 学习路径提示
    learn = ['<p class="dim">本组内存在 <strong>%d</strong> 条前置依赖边（prerequisite），'
             '推荐先掌握前置知识点，再进入依赖它的节点。</p>' % len(in_prereq)]
    if topo:
        learn.append('<div class="pathbox"><div class="path-label">推荐阅读顺序（拓扑序）</div>'
                     '<div class="path-seq">%s</div></div>'
                     % " &rarr; ".join(link(nid) for nid in topo))

    def dep_list(es):
        out = []
        for e in es:
            out.append("<li>%s &rarr; %s<span class=\"evi\">%s</span></li>"
                       % (link(e["from"]), link(e["to"]), esc(e.get("label", ""))))
        return '<ul class="dep-list">%s</ul>' % "".join(out)

    if in_prereq:
        learn.append(dep_list(in_prereq))
    if external_in:
        learn.append("<h3>入组前置依赖（组外节点 → 本组成员）</h3>%s" % dep_list(external_in))
    if external_out:
        learn.append("<h3>出组依赖（本组成员 → 组外节点）</h3>%s" % dep_list(external_out))

    kind_st = KIND_STYLE.get(group["kind"], KIND_STYLE["source"])
    badges = (kind_badge(group["kind"]) + layer_badge(group.get("layer"))
              + "".join(stage_badge(s) for s in stage_set)
              + '<span class="badge cnt">%d 节点</span>' % len(node_ids))
    crumb = ('<div class="crumb"><a href="../%s">%s</a> <span class="sep">/</span> '
             '<a href="index.html">分组目录</a> <span class="sep">/</span> <span>%s</span></div>'
             % (esc(g.cfg["root_index"]), esc(g.cfg["title"]), esc(gname)))
    meta = " · ".join(str(x) for x in [KIND_STYLE.get(group["kind"], {}).get("label"),
                                       group.get("domain"), "%d 节点" % len(node_ids)] if x)
    doc = ('<header class="doc"><h1>%s</h1><div class="en">%s</div>'
           '<div class="badges">%s</div></header>'
           % (esc(gname), esc(gid), badges))
    footer = ('<footer>%s · 组页由 16-checkpoint/gen-groups.py 生成 · '
              '组内关系图复用 gen_common 确定性子图构造器</footer>' % esc(g.cfg["title"]))
    sections = [("组简介", "".join(intro)),
                ("成员节点目录", catalog),
                ("组内关系图", rel),
                ("学习路径提示", "".join(learn))]
    return page_shell(g.cfg, gname, crumb, meta, doc, sections, footer, extra_css=EXTRA_CSS)


def index_html(g):
    total_nodes, total_groups, total_edges = len(g.nodes), len(g.groups), len(g.edges)
    stats = ('<div class="stat"><b>%d</b><span>节点</span></div>'
             '<div class="stat"><b>%d</b><span>组</span></div>'
             '<div class="stat"><b>%d</b><span>关系边</span></div>'
             '<div class="stat"><b>%d</b><span>域/层枚举</span></div>'
             % (total_nodes, total_groups, total_edges,
                len(g.cfg.get("domains", {})) or len(g.cfg.get("layers", []))))

    order = [k for k in g.cfg.get("group_kind_order", KIND_ORDER) if k in KIND_STYLE]
    for k in KIND_STYLE:
        if k not in order:
            order.append(k)

    cards = []
    for kind in order:
        ks = KIND_STYLE[kind]
        items = []
        for gp in g.groups:
            if gp.get("kind") != kind:
                continue
            nids = [n for n in gp["node_ids"] if n in g.by_id]
            stages = sorted(set(g.by_id[n]["stage"] for n in nids),
                            key=lambda s: (["basic", "intermediate", "advanced"].index(s)
                                           if s in ["basic", "intermediate", "advanced"] else 99))
            stage_str = "".join(stage_badge(s) for s in stages if s in STAGE_STYLE)
            items.append(
                '<a class="card" style="border-left:4px solid %s" href="%s.html">'
                '<h3>%s · %s</h3><div class="meta">%s ｜ %d 个节点</div>'
                '<div class="stage-row">%s</div></a>'
                % (ks["brd"], esc(gp["id"]), esc(gp["id"]), esc(gp["name"]),
                   esc(gp.get("domain", "") or "—"), len(nids), stage_str))
        if items:
            cards.append('<h3>%s</h3><div class="cards">%s</div>' % (ks["label"], "".join(items)))

    crumb = ('<div class="crumb"><a href="../%s">%s</a> <span class="sep">/</span> '
             '<span>分组目录</span></div>' % (esc(g.cfg["root_index"]), esc(g.cfg["title"])))
    doc = ('<header class="doc"><h1>分组目录</h1><div class="en">Groups</div>'
           '<div class="badges"><span class="badge">%d 组</span>'
           '<span class="badge">%d 节点</span></div></header>'
           % (total_groups, total_nodes))
    footer = ('<footer>%s · 组索引由 16-checkpoint/gen-groups.py 生成</footer>' % esc(g.cfg["title"]))
    sections = [("核心统计", stats), ("全部组", "".join(cards))]
    return page_shell(g.cfg, "分组目录", crumb, "%d 组 · %d 节点" % (total_groups, total_nodes),
                      doc, sections, footer, html_title="分组目录 · %s" % g.cfg["title"],
                      extra_css=EXTRA_CSS)


def run(cfg):
    out = cfg["out_paths"]["groups"]
    os.makedirs(out, exist_ok=True)
    g = build_graph(cfg)
    for gp in g.groups:
        with open(os.path.join(out, gp["id"] + ".html"), "w", encoding="utf-8") as f:
            f.write(group_html(g, gp))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html(g))
    return {"kind": "groups", "group_pages": len(g.groups), "index": 1,
            "total": len(g.groups) + 1, "dir": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成组页与组索引")
    add_common_args(ap)
    args = ap.parse_args(argv)
    res = run(config_from_args(args))
    print("group pages written: %d (+index) -> %s" % (res["group_pages"], res["dir"]))


if __name__ == "__main__":
    main()
