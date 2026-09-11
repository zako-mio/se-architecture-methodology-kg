#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成多视图页：{out_views}/{file}（浅色 Codex 文档外壳，对齐节点页）

由配置 cfg["views"] 声明清单，按 kind 分派渲染器：
  views-index      视图入口（卡片导航）
  stage            难度阶段视图（12factor 兼容）
  layer            三层视图（本质/方法论/技术实践 + 层间边）
  learning-path    学习路径（prerequisite 拓扑；有 src=app/agent 时输出三条路径）
  decision-matrix  生命周期域 × 层 × 横切主题落点矩阵
  cross-mapping    跨体系对照（cross_reference 边；12factor 模式回落 App↔Agent 映射）
  cases            案例视图（case 节点 + case_instance 边）

各视图原有语义与排序逻辑保持不变，仅替换呈现外壳；数据能力缺失时降级为空状态页。
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (build_graph, sections, esc, topo_sort, stage_badge,
                        layer_badge, src_badge, domain_badge, page_shell,
                        STAGE_STYLE, LAYER_STYLE, EDGE_STYLE,
                        LAYER_ORDER, add_common_args, config_from_args,
                        load_book_verification, BOOK_VERIFICATION_FILE,
                        _anchor_label, _STRENGTH_RANK)

EXTRA_CSS = """
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:12px 0;}
.card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px 18px;}
.card h3{font-size:15px;color:var(--accent);margin:0 0 8px;}
.card p{font-size:13px;color:var(--dim);margin-bottom:10px;}
.card .go{display:inline-block;background:#eef4ff;border:1px solid #c5d7f5;border-radius:8px;padding:6px 14px;color:#1d4ed8;font-size:13px;text-decoration:none;}
.stat{display:inline-block;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:4px;text-align:center;}
.stat b{display:block;font-size:22px;color:var(--accent);}
.stat span{font-size:12px;color:var(--dim);}
.row{display:flex;align-items:baseline;gap:10px;padding:9px 6px;border-bottom:1px solid var(--border);flex-wrap:wrap;}
.row .nm{min-width:200px;flex:0 0 auto;font-size:14px;font-weight:600;}
.row .brief{flex:1 1 320px;font-size:12.5px;color:var(--dim);min-width:240px;}
.layer-nav{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 4px;}
.layer-nav a{display:inline-block;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:4px 12px;font-size:13px;color:var(--text);text-decoration:none;}
.empty{background:var(--panel);border:1px dashed var(--border);border-radius:8px;padding:24px;color:var(--dim);text-align:center;}
.sec-card{background:var(--panel);border:1px solid var(--border);border-left-width:4px;border-radius:8px;padding:10px 18px;margin:12px 0;}
.bv-legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--dim);margin:8px 0;}
.bv-legend .k{display:inline-flex;align-items:center;gap:5px;}
.bv-legend i{width:11px;height:11px;border-radius:3px;display:inline-block;border:1px solid transparent;}
.bv-badge{display:inline-block;padding:1px 8px;border-radius:20px;font-size:11.5px;font-weight:600;border:1px solid var(--border);}
.bv-direct{color:#1f6f5c;border-color:#a9cbbf;background:#eef7f2;}
.bv-partial{color:#8a5a12;border-color:#e0c79a;background:#fbf3e6;}
.bv-inferred{color:#6f6656;border-color:var(--border);background:#f1ece0;}
.bv-contradicted{color:#a01f2c;border-color:#e0b0b0;background:#fbeeee;}
.bv-cell{min-width:92px;}
.bv-anchor{display:inline-block;font-family:Georgia,serif;font-size:11.5px;color:var(--dim);margin:1px 5px 1px 0;}
.bv-target{font-family:Consolas,monospace;font-size:12px;}
"""


def shell(g, title, subtitle, sections, badges=""):
    cfg = g.cfg
    crumb = ('<div class="crumb"><a href="../%s">%s</a> <span class="sep">/</span> '
             '<a href="index.html">视图入口</a> <span class="sep">/</span> <span>%s</span></div>'
             % (esc(cfg["root_index"]), esc(cfg["title"]), esc(title)))
    doc = ('<header class="doc"><h1>%s</h1><div class="en">%s</div>'
           '<div class="badges">%s</div></header>' % (esc(title), esc(subtitle), badges))
    footer = ('<footer>%s · 视图页由 16-checkpoint/gen-views.py 生成</footer>' % esc(cfg["title"]))
    return page_shell(cfg, title, crumb, subtitle, doc, sections, footer, extra_css=EXTRA_CSS)


def node_link(g, nid):
    n = g.by_id.get(nid, {})
    return '<a href="../%s/%s.html">%s</a>' % (esc(g.cfg["out_dirs"]["nodes"]), esc(nid),
                                               esc(n.get("name", nid)))


def empty(msg):
    return '<div class="empty">%s</div>' % esc(msg)


def _stat_badges(g):
    return ('<span class="badge">%d 节点</span><span class="badge">%d 组</span>'
            '<span class="badge">%d 边</span>'
            % (len(g.nodes), len(g.groups), len(g.edges)))


# ---------------------------------------------------------------- views-index
def view_views_index(g):
    cards = []
    for v in g.cfg["views"]:
        if v["kind"] == "views-index":
            continue
        cards.append('<div class="card"><h3>%s</h3><p>%s</p>'
                     '<a class="go" href="%s">打开</a></div>'
                     % (esc(v["title"]), esc(v.get("desc", "")), esc(v["file"])))
    cards.append('<div class="card"><h3>交互 DAG 总览</h3><p>组级视图 + 点击下钻 + 数据驱动渲染。</p>'
                 '<a class="go" href="../%s/index.html">打开交互总览</a></div>'
                 % esc(g.cfg["out_dirs"]["interactive"]))
    stats = ('<div class="stat"><b>%d</b><span>节点</span></div>'
             '<div class="stat"><b>%d</b><span>组</span></div>'
             '<div class="stat"><b>%d</b><span>关系边</span></div>' % (len(g.nodes), len(g.groups), len(g.edges)))
    quick = ('<ul style="padding-left:22px;">'
             '<li><b>总览</b>：交互 DAG 总览查看 %d 组、%d 节点在拓扑中的分布，'
             '点击组节点可下钻组内 DAG。</li>'
             '<li><b>分面浏览</b>：%s。</li>'
             '<li><b>深读</b>：任一视图中点击节点名进入节点详情页，'
             '可读定义 / 原理 / 机制 / 工程 / 权衡与信源。</li>'
             '<li><b>机读</b>：Markdown 镜像供 AI 按路径索引调用。</li>'
             '</ul>' % (len(g.groups), len(g.nodes),
                        esc(" / ".join(v["title"] for v in g.cfg["views"] if v["kind"] != "views-index"))))
    sections = [("核心统计", stats), ("视图入口", "".join(cards)), ("快速开始", quick)]
    return shell(g, "视图入口", g.cfg.get("subtitle", ""), sections, _stat_badges(g))


# ---------------------------------------------------------------- stage
def view_stage(g):
    stages = [s for s in ["basic", "intermediate", "advanced"] if s in STAGE_STYLE]
    sections = []
    for s in stages:
        nodes = sorted([n for n in g.nodes if n["stage"] == s], key=lambda n: (n.get("group") or "", n["id"]))
        rows = "".join(
            '<div class="row"><span class="nm">%s</span>%s%s<span class="brief">%s</span></div>'
            % (node_link(g, n["id"]), src_badge(n.get("src")) or layer_badge(n.get("layer")),
               domain_badge(n.get("domain"), g.cfg), esc(n["definition"]))
            for n in nodes) or '<p class="dim">本档暂无节点。</p>'
        sections.append(("%s（%d）" % (STAGE_STYLE[s]["label"], len(nodes)),
                         '<div class="sec-card">%s</div>' % rows))
    return shell(g, "阶段视图", "按难度分档列出全部节点。", sections, _stat_badges(g))


# ---------------------------------------------------------------- layer
def view_layer(g):
    if not g.has_layer:
        return shell(g, "分层视图", "本质 / 方法论 / 技术实践三层。",
                     [("说明", empty("当前数据未包含 layer 字段（12factor 旧库自动降级）。"))])
    layers = [l for l in LAYER_ORDER if l in LAYER_STYLE]
    for l in sorted({n.get("layer") for n in g.nodes if n.get("layer")}):
        if l not in layers:
            layers.append(l)
    sections = []
    for l in layers:
        nodes = sorted([n for n in g.nodes if n.get("layer") == l], key=lambda n: (n.get("domain") or "", n["id"]))
        rows = "".join(
            '<div class="row"><span class="nm">%s</span>%s%s<span class="brief">%s</span></div>'
            % (node_link(g, n["id"]), domain_badge(n.get("domain"), g.cfg),
               stage_badge(n.get("stage")), esc(n["definition"]))
            for n in nodes) or '<p class="dim">本层暂无节点。</p>'
        sections.append(("%s（%d）" % (LAYER_STYLE.get(l, {}).get("label", l), len(nodes)),
                         '<div class="sec-card">%s</div>' % rows))
    cross = [e for e in g.edges if e["type"] in ("implements", "derives_from")]
    if cross:
        rows = "".join(
            '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
            % (node_link(g, e["from"]), esc(EDGE_STYLE.get(e["type"], {}).get("label", e["type"])),
               node_link(g, e["to"]), esc(e.get("label", "")))
            for e in cross)
        cross_html = ('<div class="tblwrap"><table><thead><tr>'
                      '<th>来源（外→内）</th><th>类型</th><th>目标</th><th>说明</th></tr></thead>'
                      '<tbody>%s</tbody></table></div>' % rows)
        sections.append(("层间依赖边", cross_html))
    return shell(g, "分层视图", "按本质 / 方法论 / 技术实践三层浏览。", sections, _stat_badges(g))


# ---------------------------------------------------------------- learning-path
def _topo_ids(g, ids, types=("prerequisite",)):
    return topo_sort(ids, g.edges, set(types))


def view_learning_path(g):
    def seq(ids):
        return " &rarr; ".join(node_link(g, nid) for nid in ids)

    if g.has_src and any(n.get("src") in ("app", "agent") for n in g.nodes):
        app_ids = [n["id"] for n in g.nodes if n.get("src") == "app"]
        agent_ids = [n["id"] for n in g.nodes if n.get("src") == "agent"]
        all_ids = [n["id"] for n in g.nodes]
        paths = [
            ("A · 传统工程入门", "app 体系 prerequisite 拓扑序", _topo_ids(g, app_ids)),
            ("B · Agent 工程入门", "agent 体系 prerequisite 拓扑序", _topo_ids(g, agent_ids)),
            ("C · 打通", "全图谱 prerequisite 拓扑序", _topo_ids(g, all_ids)),
        ]
    else:
        all_ids = [n["id"] for n in g.nodes]
        paths = [("全局学习顺序", "全图谱 prerequisite 拓扑序", _topo_ids(g, all_ids))]
        if g.has_layer:
            for l in LAYER_ORDER:
                ids = [n["id"] for n in g.nodes if n.get("layer") == l]
                if ids:
                    paths.append(("%s 层路径" % LAYER_STYLE.get(l, {}).get("label", l),
                                  "层内 prerequisite 拓扑序", _topo_ids(g, ids)))
        elif g.has_domain_enum:
            for d in sorted({n.get("domain") for n in g.nodes if n.get("domain")}):
                ids = [n["id"] for n in g.nodes if n.get("domain") == d]
                paths.append(("%s 域路径" % d, "域内 prerequisite 拓扑序", _topo_ids(g, ids)))

    sections = []
    for title, desc, ids in paths:
        sections.append(("%s（%d 个节点）" % (title, len(ids)),
                         '<p class="dim">%s</p><div class="pathbox">'
                         '<div class="path-label">推荐顺序</div>'
                         '<div class="path-seq">%s</div></div>' % (esc(desc), seq(ids))))
    return shell(g, "学习路径", "基于前置依赖自动生成的学习顺序（prerequisite 拓扑排序，不硬编码）。",
                 sections, _stat_badges(g))


# ---------------------------------------------------------------- decision-matrix
def view_decision_matrix(g):
    domains = [d for d in g.cfg.get("domains", {}) if any(n.get("domain") == d for n in g.nodes)]
    if not domains and g.has_domain_enum:
        domains = sorted({n.get("domain") for n in g.nodes if n.get("domain")})
    layers = [l for l in LAYER_ORDER if any(n.get("layer") == l for n in g.nodes)]
    if not (domains and (layers or g.themes)):
        return shell(g, "决策矩阵", "生命周期域 × 层 × 横切主题。",
                     [("说明", empty("当前数据不足以构建决策矩阵（需 domain + layer/themes）。"))])

    sections = []
    head = "<th>生命周期域</th>" + "".join("<th>%s</th>" % esc(LAYER_STYLE.get(l, {}).get("label", l)) for l in layers)
    rows = []
    for d in domains:
        label = g.cfg.get("domains", {}).get(d, d)
        cells = []
        for l in layers:
            ns = [n for n in g.nodes if n.get("domain") == d and n.get("layer") == l]
            links = "".join(node_link(g, n["id"]) + "<br>" for n in ns) or '<span class="dim">—</span>'
            cells.append("<td>%s</td>" % links)
        rows.append("<tr><td>%s · %s</td>%s</tr>" % (esc(d), esc(label), "".join(cells)))
    matrix = ('<div class="tblwrap"><table><thead><tr>%s</tr></thead>'
              '<tbody>%s</tbody></table></div>' % (head, "".join(rows)))
    sections.append(("生命周期域 × 层 落点矩阵", matrix))

    theme_ids = [t.get("id") for t in g.themes if t.get("id")]
    if theme_ids:
        trs = []
        for tid in theme_ids:
            ns = [n for n in g.nodes if tid in (n.get("cross_cutting") or [])]
            tname = g.theme_by_id.get(tid, {}).get("name", tid)
            trs.append("<tr><td>%s · %s</td><td>%d</td><td>%s</td></tr>"
                       % (esc(tid), esc(tname), len(ns),
                          "、".join(node_link(g, n["id"]) for n in ns) or '<span class="dim">—</span>'))
        theme_html = ('<div class="tblwrap"><table><thead><tr>'
                      '<th>主题</th><th>节点数</th><th>落点节点</th></tr></thead><tbody>%s</tbody></table></div>'
                      % "".join(trs))
        sections.append(("横切主题覆盖", theme_html))
    return shell(g, "决策矩阵", "按生命周期域与层定位知识点，并核对横切主题覆盖。",
                 sections, _stat_badges(g))


# ---------------------------------------------------------------- cross-mapping
XREF_FILE = "xref-12factor.json"
_XREF_CONTAINER_KEYS = ("rows", "mappings", "xref", "entries", "items", "data")


def _load_xref(cfg):
    checkpoint_dir = cfg.get("checkpoint_dir") or os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(checkpoint_dir, XREF_FILE)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as ex:
        sys.stderr.write("[warn] 读取 %s 失败，回落：%s\n" % (path, ex))
        return None
    if isinstance(data, dict):
        for key in _XREF_CONTAINER_KEYS:
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            return None
    if not isinstance(data, list) or not data:
        return None
    return [r for r in data if isinstance(r, dict)]


def _xref_field(row, *names):
    for nm in names:
        val = row.get(nm)
        if val not in (None, ""):
            return val
    return None


def _render_xref(g, rows):
    trs = []
    for row in rows:
        fid = _xref_field(row, "tf_id", "factor_id", "id", "factor", "node_id", "from")
        fname = (_xref_field(row, "tf_name", "factor_name", "name", "title", "factor_title")
                 or fid or "—")
        deep = _xref_field(row, "deep_link", "deepLink", "link", "url")
        rel = _xref_field(row, "relation", "relation_type", "type", "edge_type") or "cross_reference"
        mids_raw = _xref_field(row, "mother_ids", "mother_node", "mother", "mother_id", "to", "target")
        if isinstance(mids_raw, (list, tuple)):
            mids = [m for m in mids_raw if m]
        else:
            mids = [mids_raw] if mids_raw else []
        rationale = _xref_field(row, "rationale", "reason", "label", "note", "desc") or ""

        if deep:
            fcell = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(deep), esc(fname))
        else:
            fcell = esc(fname)
        rel_label = EDGE_STYLE.get(rel, {}).get("label", rel)
        if mids:
            mcell = "、".join(
                node_link(g, mid) if mid in g.by_id else '<span class="dim">%s</span>' % esc(mid)
                for mid in mids)
        else:
            mcell = '<span class="dim">—</span>'
        trs.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                   % (fcell, esc(rel_label), mcell, esc(rationale)))

    note = ('<p class="dim">12factor 为母库首个子库/实例库，<b>不内联</b>进母库主 DAG；'
            '下表逐行给出 12factor 节点 ↔ 母库节点的映射与关系类型，深链直达子库节点页。</p>')
    body = (note + '<div class="tblwrap"><table><thead><tr><th>12factor 节点</th>'
            '<th>关系类型</th><th>母库节点</th><th>rationale</th></tr></thead><tbody>%s</tbody></table></div>'
            % "".join(trs))
    return shell(g, "跨体系对照", "母库 ↔ 12factor 子库逐条映射（%d 行）。" % len(trs),
                 [("逐条映射表", body)])


def view_cross_mapping(g):
    xref_rows = _load_xref(g.cfg)
    if xref_rows is not None:
        return _render_xref(g, xref_rows)

    if g.has_cross_ref:
        rows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (node_link(g, e["from"]), esc(EDGE_STYLE.get(e["type"], {}).get("label", e["type"])),
               node_link(g, e["to"]), esc(e.get("label", "")))
            for e in g.edges if e["type"] == "cross_reference")
        body = ('<p class="dim">跨体系对照边（cross_reference）由数据驱动，不复制子库内容。</p>'
                '<div class="tblwrap"><table><thead><tr><th>母库节点</th><th>关系</th>'
                '<th>对照节点</th><th>说明</th></tr></thead><tbody>%s</tbody></table></div>' % rows)
        return shell(g, "跨体系对照", "cross_reference 对照表。", [("对照表", body)])

    app_nodes = sorted([n for n in g.nodes if n.get("src") == "app"], key=lambda n: n["id"])
    agent_ids = {n["id"] for n in g.nodes if n.get("src") == "agent"}
    if not app_nodes or not agent_ids:
        return shell(g, "跨体系对照", "跨体系映射。",
                     [("说明", empty("当前数据无 cross_reference 边，也无 app/agent 体系标记。"))])
    rows = []
    for a in app_nodes:
        rel_agent = rel_label = None
        for e in g.edges:
            if e["from"] == a["id"] and e["to"] in agent_ids and e["type"] in ("variant", "dependency"):
                rel_agent, rel_label = e["to"], e.get("label", "")
                break
        topic = None
        for e in g.edges:
            if e["from"] == a["id"] and g.by_id.get(e["to"], {}).get("src") == "bridge" and e["type"] == "prerequisite":
                topic = e["to"]
                break
        if rel_agent is None and topic:
            for e in g.edges:
                if e["from"] == topic and e["to"] in agent_ids and e["type"] == "prerequisite":
                    rel_agent, rel_label = e["to"], "经桥接主题 %s 映射" % g.by_id[topic]["name"]
                    break
        diff = ""
        if topic:
            diff = " ".join(sections(g.by_id[topic]).get("difference", []) or [])
        diff = diff or rel_label or "—"
        topic_txt = node_link(g, topic) if topic else '<span class="dim">—</span>'
        agent_txt = node_link(g, rel_agent) if rel_agent else '<span class="dim">—</span>'
        rows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (node_link(g, a["id"]), topic_txt, agent_txt, esc(diff)))
    body = ('<p class="dim">逐条比对 app 体系与 agent 体系，映射经由桥接主题。</p>'
            '<div class="tblwrap"><table><thead><tr><th>App 体系</th><th>桥接主题</th>'
            '<th>Agent 体系</th><th>差异根源</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(rows))
    return shell(g, "跨体系对照", "app ↔ agent 逐条对照。", [("对照表", body)])


# ---------------------------------------------------------------- cases
def view_cases(g):
    cases = [n for n in g.nodes if n.get("type") == "case"]
    if not cases:
        return shell(g, "案例视图", "案例节点与印证关系。",
                     [("说明", empty("当前数据无案例节点（CAS-*）。"))])
    rows = []
    for n in cases:
        rel = [e for e in g.edges if e["from"] == n["id"] or e["to"] == n["id"]]
        rel_txt = "、".join(
            "%s %s" % (EDGE_STYLE.get(e["type"], {}).get("label", e["type"]),
                       esc(g.by_id.get(e["to"] if e["from"] == n["id"] else e["from"], {}).get("name", "")))
            for e in rel) or '<span class="dim">—</span>'
        rows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (node_link(g, n["id"]), esc(n["definition"]),
                       esc("/".join(n.get("sources") or []) or "—"), rel_txt))
    body = ('<div class="tblwrap"><table><thead><tr><th>案例</th><th>概要</th>'
            '<th>信源</th><th>印证关系</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(rows))
    return shell(g, "案例视图", "案例节点及其 case_instance 印证关系。", [("案例清单", body)], _stat_badges(g))


# ---------------------------------------------------------------- book-verification
_BV_KIND_LABEL = {
    "missed_citation": "应引未引",
    "coverage_hole": "覆盖盲区",
    "concept_missing": "概念缺口",
}
_BV_STRENGTH_LABEL = {
    "direct": "direct",
    "partial": "partial",
    "inferred": "inferred",
    "contradicted": "contradicted",
}
_BV_LAYER_GROUPS = [
    ("essence", "本质 essence"),
    ("methodology", "方法论 methodology"),
    ("technology", "技术实践 technology"),
    (None, "其他 / 案例"),
]


def _bv_natkey(value):
    parts = re.split(r"(\d+)", str(value or ""))
    return [(0, int(p), "") if p.isdigit() else (1, 0, p) for p in parts]


def _bv_legend():
    items = [("direct", "#1f6f5c"), ("partial", "#8a5a12"),
             ("inferred", "#6f6656"), ("contradicted", "#a01f2c")]
    cells = "".join('<span class="k"><i style="background:%s"></i>%s</span>' % (c, esc(name))
                    for name, c in items)
    return '<div class="bv-legend">%s</div>' % cells


def _bv_books(by_node):
    names = {}
    for recs in by_node.values():
        for r in recs:
            sid = r.get("source_id") or ""
            if sid and r.get("book"):
                names.setdefault(sid, r["book"])
            elif sid:
                names.setdefault(sid, "")
    return [(sid, names.get(sid, "")) for sid in sorted(names)]


def _bv_cell(recs):
    if not recs:
        return '<span class="dim">—</span>'
    best = max(recs, key=lambda r: _STRENGTH_RANK.get(r.get("evidence_strength"), -1))
    strength = best.get("evidence_strength") or ""
    labels = sorted({_anchor_label(r) for r in recs if _anchor_label(r)}, key=_bv_natkey)
    badge = '<span class="bv-badge bv-%s">%s</span>' % (esc(strength), esc(strength))
    anchors = "".join('<span class="bv-anchor">%s</span>' % esc(x) for x in labels)
    return badge + ("<br>" + anchors if anchors else "")


def _bv_matrix(g, by_node, books):
    nodes_dir = g.cfg["out_dirs"]["nodes"]
    grouped = {}
    for nid in sorted(by_node):
        layer = (g.by_id.get(nid) or {}).get("layer")
        grouped.setdefault(layer, []).append(nid)
    tables = []
    for layer, label in _BV_LAYER_GROUPS:
        ids = grouped.get(layer) or []
        if not ids:
            continue
        head = "".join(
            '<th><a href="../%s/%s.html">%s</a><br><span class="dim">%s</span></th>'
            % (esc(nodes_dir), esc(nid), esc(nid),
               esc((g.by_id.get(nid) or {}).get("name", "")))
            for nid in ids)
        rows = []
        for sid, bname in books:
            cells = []
            for nid in ids:
                recs = [r for r in by_node.get(nid, []) if r.get("source_id") == sid]
                cells.append('<td class="bv-cell">%s</td>' % _bv_cell(recs))
            rows.append('<tr><td>%s<br><span class="dim">%s</span></td>%s</tr>'
                        % (esc(sid), esc(bname), "".join(cells)))
        table = ('<div class="tblwrap"><table><caption style="text-align:left;color:var(--dim);'
                 'font-size:12.5px;padding:6px 0">%s（%d 个被核验节点）</caption>'
                 '<thead><tr><th>书 \\ 节点</th>%s</tr></thead><tbody>%s</tbody></table></div>'
                 % (esc(label), len(ids), head, "".join(rows)))
        tables.append(table)
    if not tables:
        return empty("投影中暂无可展示的节点书证记录。")
    return _bv_legend() + "".join(tables)


def _bv_stats(by_node, books):
    if not by_node:
        return empty("无可统计的核验记录。")
    strengths = ["direct", "partial", "inferred", "contradicted"]
    rows = []
    totals = {"nodes": set(), "direct": 0, "partial": 0, "inferred": 0,
              "contradicted": 0, "forward": 0, "reverse": 0}
    for sid, bname in books:
        nodes = set()
        sc = {s: 0 for s in strengths}
        forward = reverse = 0
        for nid, recs in by_node.items():
            for r in recs:
                if r.get("source_id") != sid:
                    continue
                nodes.add(nid)
                if r.get("evidence_strength") in sc:
                    sc[r["evidence_strength"]] += 1
                if r.get("direction") == "forward":
                    forward += 1
                elif r.get("direction") == "reverse":
                    reverse += 1
        totals["nodes"] |= nodes
        for s in strengths:
            totals[s] += sc[s]
        totals["forward"] += forward
        totals["reverse"] += reverse
        rows.append("<tr><td>%s<br><span class='dim'>%s</span></td><td>%d</td>%s"
                    "<td>%d</td><td>%d</td></tr>"
                    % (esc(sid), esc(bname), len(nodes),
                       "".join("<td>%d</td>" % sc[s] for s in strengths),
                       forward, reverse))
    rows.append("<tr><td><b>合计</b></td><td><b>%d</b></td>%s<td><b>%d</b></td>"
                "<td><b>%d</b></td></tr>"
                % (len(totals["nodes"]),
                   "".join("<td><b>%d</b></td>" % totals[s] for s in strengths),
                   totals["forward"], totals["reverse"]))
    head = ("<th>书</th><th>覆盖节点</th><th>direct</th><th>partial</th>"
            "<th>inferred</th><th>contradicted</th><th>正向</th><th>反向</th>")
    return ('<div class="tblwrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (head, "".join(rows)))


def _bv_gaps(g, gaps):
    if not gaps:
        return empty("反向发现缺口清单为空。")
    rows = []
    for gp in gaps:
        existing = (gp.get("target") or {}).get("existing_node_id")
        proposed = (gp.get("target") or {}).get("proposed_node")
        if existing and existing in g.by_id:
            target = node_link(g, existing)
        elif existing:
            target = '<span class="bv-target">%s</span>' % esc(existing)
        else:
            target = '<span class="dim">—</span>'
        if proposed:
            target += '<br><span class="dim">提案：%s</span>' % esc(proposed)
        sid = gp.get("book_source_id") or ""
        anchor = "Ch%s" % (gp.get("section") or gp.get("chapter") or "")
        rows.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
            "<td>%s</td><td>%s</td></tr>"
            % (esc(gp.get("gap_id", "")),
               esc(_BV_KIND_LABEL.get(gp.get("kind"), gp.get("kind", ""))),
               esc(sid), esc(anchor), target,
               esc(gp.get("summary", "")),
               esc(gp.get("proposed_action", ""))))
    head = ("<th>gap</th><th>类型</th><th>书</th><th>锚</th><th>目标</th>"
            "<th>改写摘要</th><th>建议动作</th>")
    note = ('<p class="dim">缺口为阶段3 结构扩展的输入导航；<code>summary</code> 与 '
            '<code>proposed_action</code> 为改写摘要，非书籍原文。仅展示章节级锚。</p>')
    return note + ('<div class="tblwrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody>'
                   '</table></div>' % (head, "".join(rows)))


def view_book_verification(g):
    doc = load_book_verification(g.cfg)
    by_node = doc.get("by_node") or {}
    gaps = doc.get("gaps") or []
    if not by_node and not gaps:
        msg = "[SKIP] 06-book-verification: 10-dag-data/%s 缺失或为空" % BOOK_VERIFICATION_FILE
        print(msg)
        return shell(g, "书籍↔节点对照", "书证核验的公开安全投影。",
                     [("说明", empty("数据源 10-dag-data/%s 缺失或为空"
                                     "（由 derive_verification.py 生成）。"
                                     % BOOK_VERIFICATION_FILE))])
    books = _bv_books(by_node)
    secs = [
        ("书籍 ↔ 节点对照矩阵",
         '<p class="dim">行 = 参考书，列 = 被核验节点（按层分组）；格 = 证据强度徽标'
         '（取该节点 × 该书记录的最高优先级）与章级锚，点击节点 ID 进入节点页。</p>'
         + _bv_matrix(g, by_node, books)),
        ("覆盖统计", _bv_stats(by_node, books)),
        ("反向发现缺口（阶段3 输入）", _bv_gaps(g, gaps)),
    ]
    return shell(g, "书籍↔节点对照",
                 "书证的公开安全投影：书籍 ↔ 节点强度矩阵、覆盖统计与反向缺口。",
                 secs, _stat_badges(g))


_DISPATCH = {
    "views-index": view_views_index,
    "stage": view_stage,
    "layer": view_layer,
    "learning-path": view_learning_path,
    "decision-matrix": view_decision_matrix,
    "cross-mapping": view_cross_mapping,
    "cases": view_cases,
    "book-verification": view_book_verification,
}


def run(cfg):
    out = cfg["out_paths"]["views"]
    os.makedirs(out, exist_ok=True)
    g = build_graph(cfg)
    written = 0
    for v in cfg["views"]:
        fn = _DISPATCH.get(v["kind"])
        if fn is None:
            sys.stderr.write("[warn] 未知视图 kind=%s，跳过\n" % v["kind"])
            continue
        with open(os.path.join(out, v["file"]), "w", encoding="utf-8") as f:
            f.write(fn(g))
        written += 1
    return {"kind": "views", "written": written, "dir": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成多视图页")
    add_common_args(ap)
    args = ap.parse_args(argv)
    res = run(config_from_args(args))
    print("views written: %d -> %s" % (res["written"], res["dir"]))


if __name__ == "__main__":
    main()
