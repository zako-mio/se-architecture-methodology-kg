#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成根入口：{root_index}（浅色 Codex 皮肤，对齐节点页外壳）。

含：结构导航（交互总览 / 分组目录 / 多视图 / Markdown 镜像）+ 门控结果摘要
（生成时自检：硬依赖无环、canonical 可解析、可溯源率、verified 占比）+ 使用方式入口。
所有计数与检查结论均由配置、规范化图数据与 canonical 主表派生，不硬编码。
"""
import argparse
import os
import sys
from collections import defaultdict, deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (build_graph, esc, load_canonical_ids, page_shell,
                        HARD_EDGE_TYPES, add_common_args, config_from_args)

EXTRA_CSS = """
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin:12px 0;}
.card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px 18px;}
.card h3{font-size:15px;color:var(--accent);margin:0 0 6px;}
.card p{font-size:13px;color:var(--dim);}
.stat{display:inline-block;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:4px;text-align:center;}
.stat b{display:block;font-size:22px;color:var(--accent);}
.stat span{font-size:12px;color:var(--dim);}
ol.steps{padding-left:22px;margin:8px 0;}
ol.steps li{margin:6px 0;}
.badge.pass{color:#1f6f5c;border-color:#a9cbbf;background:#eef7f2;}
.badge.warn{color:#8a3b12;border-color:#e0b79a;background:#fbf1e8;}
"""


def _is_acyclic(g):
    idset = set(n["id"] for n in g.nodes)
    adj = defaultdict(list)
    indeg = {i: 0 for i in idset}
    for e in g.edges:
        if e["type"] in HARD_EDGE_TYPES and e["from"] in idset and e["to"] in idset:
            adj[e["from"]].append(e["to"])
            indeg[e["to"]] += 1
    q = deque(sorted(i for i in idset if indeg[i] == 0))
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == len(idset)


def _gate_rows(g):
    canon = load_canonical_ids(g.cfg)
    refs = []
    for n in g.nodes:
        refs += [s for s in (n.get("sources") or [])]
        refs += [er.get("source_id") for er in (n.get("errata") or []) if er.get("source_id")]
    for e in g.edges:
        refs += [s for s in (e.get("sources") or [])]
    dangling = 0
    if canon is not None:
        dangling = sum(1 for s in refs if isinstance(s, str) and s not in canon)
    traceable = 0
    for n in g.nodes:
        src = n.get("sources") or []
        if src and canon is not None and all(s in canon for s in src) \
                and n.get("verified") in (True, "cited"):
            traceable += 1
    n = len(g.nodes) or 1
    trace_rate = traceable / n
    verified = sum(1 for x in g.nodes if x.get("verified") is True)
    ver_rate = verified / n
    acyclic = _is_acyclic(g)

    def badge(ok):
        return ('<span class="badge pass">PASS</span>' if ok
                else '<span class="badge warn">注意</span>')

    rows = [
        ("节点 / 边 / 组", "%d / %d / %d" % (len(g.nodes), len(g.edges), len(g.groups)), "—", "—"),
        ("硬依赖无环（prerequisite 等）", "通过" if acyclic else "存在环",
         "无环", badge(acyclic)),
        ("canonical 信源引用", "共 %d 条，悬挂 %d" % (len(refs), dangling),
         "悬挂 = 0", badge(dangling == 0)),
        ("可溯源率", "%d/%d = %.2f%%" % (traceable, len(g.nodes), trace_rate * 100),
         "≥ 95%", badge(trace_rate >= 0.95)),
        ("verified=true 占比", "%d/%d = %.2f%%" % (verified, len(g.nodes), ver_rate * 100),
         "≥ 80%", badge(ver_rate >= 0.80)),
    ]
    return rows


def render(g):
    cfg = g.cfg
    od = cfg["out_dirs"]
    stats = ('<div class="stat"><b>%d</b><span>节点</span></div>'
             '<div class="stat"><b>%d</b><span>组</span></div>'
             '<div class="stat"><b>%d</b><span>关系边</span></div>'
             '<div class="stat"><b>%d</b><span>案例</span></div>'
             % (len(g.nodes), len(g.groups), len(g.edges), len(g.cases)))
    if g.has_layer:
        stats += '<div class="stat"><b>3</b><span>层</span></div>'
    if cfg.get("domains"):
        stats += '<div class="stat"><b>%d</b><span>生命周期域</span></div>' % len(cfg["domains"])

    nav_cards = [
        '<div class="card"><h3>交互 DAG 总览</h3><p>组级视图 + 点击下钻 + 数据驱动渲染。</p>'
        '<p><a href="%s/index.html">打开交互总览</a></p></div>' % esc(od["interactive"]),
        '<div class="card"><h3>分组目录</h3><p>%d 个组，按组类别分色，含组内关系图。</p>'
        '<p><a href="%s/index.html">打开分组目录</a></p></div>' % (len(g.groups), esc(od["groups"])),
        '<div class="card"><h3>多视图</h3><p>%s。</p>'
        '<p><a href="%s/index.html">打开视图入口</a></p></div>'
        % (esc(" / ".join(v["title"] for v in cfg["views"] if v["kind"] != "views-index")),
           esc(od["views"])),
        '<div class="card"><h3>Markdown 镜像</h3><p>AI 友好镜像：节点 MD + 索引。</p>'
        '<p><a href="%s/00-index.md">打开 MD 索引</a></p></div>' % esc(od["md"]),
    ]

    quick = ('<ol class="steps">'
             '<li><b>先总览</b>：打开交互 DAG 总览，看 %d 组 %d 节点在拓扑中的分布。</li>'
             '<li><b>点组下钻</b>：点击组节点展开组内 DAG，或从分组目录进入组页。</li>'
             '<li><b>选路径</b>：学习路径由 prerequisite 边自动拓扑生成。</li>'
             '<li><b>读节点</b>：读定义 / 原理 / 机制 / 工程 / 权衡，含相关边与信源。</li>'
             '<li><b>机读</b>：从 Markdown 镜像按节点 ID 直接调用。</li>'
             '</ol>' % (len(g.groups), len(g.nodes)))

    type_counts = {}
    for n in g.nodes:
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
    type_desc = "、".join("%d 个 %s" % (v, k) for k, v in sorted(type_counts.items()))
    method_cards = [
        '<div class="card"><h3>数据驱动</h3><p>节点、边、组与全部视图均由同一 DAG 数据源派生，'
        '禁止硬编码；改数据即改图谱。</p></div>',
        '<div class="card"><h3>三级下钻</h3><p>根入口 → 组页 → 节点页，交互图支持组级视图'
        '点击下钻到组内 DAG。</p></div>',
        '<div class="card"><h3>关系边</h3><p>本图谱共 %d 条边，核心为前置依赖'
        '（prerequisite）构成的硬依赖 DAG，保证无环。</p></div>' % len(g.edges),
        '<div class="card"><h3>内容深度</h3><p>每节点含定义与多段式正文，并附相关边与'
        '信源核验信息。</p></div>',
        '<div class="card"><h3>多形态交付</h3><p>HTML 人读主入口 + Markdown AI 镜像 + '
        '交互 DAG + 多视图，同源同构。</p></div>',
        '<div class="card"><h3>节点构成</h3><p>%s。</p></div>' % esc(type_desc),
    ]

    gate_rows = "".join(
        '<tr><td class="k">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(a), esc(b), esc(c), d)
        for a, b, c, d in _gate_rows(g))
    gate_tbl = ('<div class="tblwrap"><table><thead><tr><th>门控项</th><th>实测</th>'
                '<th>门槛</th><th>结论</th></tr></thead><tbody>%s</tbody></table></div>'
                '<p class="note">门控摘要于生成时自检（§11 契约）；完整 L1–L7 报告见 '
                'quality-gate.md。</p>' % gate_rows)

    badges = ('<span class="badge">%d 节点</span><span class="badge">%d 组</span>'
              '<span class="badge">%d 边</span>' % (len(g.nodes), len(g.groups), len(g.edges)))
    crumb = '<div class="crumb"><span>%s</span></div>' % esc(cfg["title"])
    doc = ('<header class="doc"><h1>%s</h1><div class="en">Knowledge Graph</div>'
           '<div class="badges">%s</div></header>' % (esc(cfg["title"]), badges))
    footer = ('<footer>%s · 根入口由 16-checkpoint/gen-index.py 生成 · 数据源 %s</footer>'
              % (esc(cfg["title"]), esc(cfg.get("dag_file") or "methodology-dag.json")))
    sections = [("核心统计", stats),
                ("结构导航", "".join(nav_cards)),
                ("质量门控摘要", gate_tbl),
                ("快速开始", quick),
                ("方法说明", "".join(method_cards))]
    return page_shell(cfg, cfg["title"], crumb, cfg.get("subtitle", ""), doc, sections,
                      footer, html_title="%s — 总览入口" % cfg["title"], extra_css=EXTRA_CSS)


def run(cfg):
    g = build_graph(cfg)
    path = cfg["root_index_path"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(render(g))
    return {"kind": "index", "written": 1, "path": path}


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成根入口")
    add_common_args(ap)
    args = ap.parse_args(argv)
    res = run(config_from_args(args))
    print("root index written: %s" % res["path"])


if __name__ == "__main__":
    main()
