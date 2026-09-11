#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用生成框架 · 公共模块（配置加载 / 数据规范化 / 拓扑 / 样式 / HTML 片段）。

数据模型与渲染引擎解耦：本模块把「12factor 基础 schema」或「母库 v1.1 schema」
统一规范化为内部结构；渲染器只消费规范化结果，不再关心字段是否缺失。

向后兼容：12factor 数据缺 layer / domain / cross_cutting / case / sources / detail
时优雅降级（填默认值或跳过对应区块），保证 12factor 生成链可原样回归。
"""
import html as html_mod
import json
import math
import os
import re
import sys
from collections import defaultdict, deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import load_config, add_common_args, config_from_args  # noqa: F401

# ================================================================ 样式常量

STAGE_STYLE = {
    "basic":        {"fg": "#2fb98a", "bg": "#122b22", "brd": "#2fb98a", "label": "基础"},
    "intermediate": {"fg": "#e0a75e", "bg": "#332412", "brd": "#e8933b", "label": "进阶"},
    "advanced":     {"fg": "#c9a8ef", "bg": "#2b2040", "brd": "#b48ae0", "label": "高级"},
}

LAYER_STYLE = {
    "essence":     {"fg": "#c9a8ef", "bg": "#2b2040", "brd": "#b48ae0", "label": "本质 essence"},
    "methodology": {"fg": "#6fd3ae", "bg": "#0f2b1f", "brd": "#2fb98a", "label": "方法论 methodology"},
    "technology":  {"fg": "#9cc2ff", "bg": "#16273f", "brd": "#4f8cff", "label": "技术实践 technology"},
}

SRC_STYLE = {
    "app":    {"fg": "#9cc2ff", "bg": "#16273f", "brd": "#4f8cff", "label": "App 体系"},
    "agent":  {"fg": "#ff8a97", "bg": "#3a1520", "brd": "#e05563", "label": "Agent 体系"},
    "bridge": {"fg": "#6fd3ae", "bg": "#0f2b1f", "brd": "#2fb98a", "label": "桥接主题"},
    "tool":   {"fg": "#e8c66a", "bg": "#3a2f12", "brd": "#e0c35e", "label": "工具"},
}

KIND_STYLE = {
    "layer":    {"fg": "#9cc2ff", "bg": "#16273f", "brd": "#4f8cff", "label": "层组"},
    "domain":   {"fg": "#7fe0d8", "bg": "#12302c", "brd": "#5ad0d0", "label": "域组"},
    "source":   {"fg": "#9cc2ff", "bg": "#16273f", "brd": "#4f8cff", "label": "来源组"},
    "bridge":   {"fg": "#6fd3ae", "bg": "#0f2b1f", "brd": "#2fb98a", "label": "主题组"},
    "crosscut": {"fg": "#c9a8ef", "bg": "#2b2040", "brd": "#b48ae0", "label": "横切组"},
    "case":     {"fg": "#ff8a97", "bg": "#3a1520", "brd": "#e05563", "label": "案例组"},
    "tool":     {"fg": "#e8c66a", "bg": "#3a2f12", "brd": "#e0c35e", "label": "工具组"},
}

TYPE_LABELS = {
    "principle":  "方法原则",
    "method":     "方法",
    "technology": "技术",
    "bridge":     "桥接主题",
    "case":       "案例",
    "tool":       "工具",
}

EDGE_STYLE = {
    "prerequisite":   {"fg": "#8fb5ff", "bg": "#16273f", "brd": "#4f8cff", "label": "前置依赖"},
    "dependency":     {"fg": "#e8a25e", "bg": "#332412", "brd": "#e8933b", "label": "依赖关联"},
    "derives_from":   {"fg": "#c9a8ef", "bg": "#2b2040", "brd": "#b48ae0", "label": "依据推导"},
    "refines":        {"fg": "#9cc2ff", "bg": "#16273f", "brd": "#4f8cff", "label": "细化"},
    "implements":     {"fg": "#6fd3ae", "bg": "#0f2b1f", "brd": "#2fb98a", "label": "实现"},
    "case_instance":  {"fg": "#ff8a97", "bg": "#3a1520", "brd": "#e05563", "label": "案例印证"},
    "cross_reference": {"fg": "#7fe0d8", "bg": "#12302c", "brd": "#5ad0d0", "label": "跨体系对照"},
    "supersedes":     {"fg": "#e8c66a", "bg": "#3a2f12", "brd": "#e0c35e", "label": "取代"},
    "deprecated_by":  {"fg": "#9aa3b2", "bg": "#23272f", "brd": "#3a3f4a", "label": "被弃用"},
    "mitigates":      {"fg": "#2fb98a", "bg": "#0f2b1f", "brd": "#2fb98a", "label": "缓解治理"},
    "contrasts":      {"fg": "#e05563", "bg": "#3a1520", "brd": "#e05563", "label": "对照"},
    "conflicts":      {"fg": "#e05563", "bg": "#3a1520", "brd": "#e05563", "label": "张力冲突"},
    "enables":        {"fg": "#7fe0d8", "bg": "#12302c", "brd": "#5ad0d0", "label": "促成"},
    "variant":        {"fg": "#e8c66a", "bg": "#3a2f12", "brd": "#e0c35e", "label": "变体"},
    "combination":    {"fg": "#c9a8ef", "bg": "#2b2040", "brd": "#b48ae0", "label": "组合"},
    "cooccurrence":   {"fg": "#7fe0d8", "bg": "#12302c", "brd": "#5ad0d0", "label": "共现"},
}
HARD_EDGE_TYPES = {"prerequisite", "dependency", "derives_from", "refines"}

KIND_ORDER = ["layer", "domain", "source", "bridge", "crosscut", "case", "tool"]

LAYER_ORDER = ["essence", "methodology", "technology"]


def esc(s):
    return html_mod.escape(str(s) if s is not None else "", quote=True)


def _label(v):
    return "" if v is None else str(v)


# ================================================================ 数据加载 / 规范化

def load_dag(cfg):
    if not cfg.get("dag_path") or not os.path.isfile(cfg["dag_path"]):
        raise FileNotFoundError("DAG 数据文件不存在: %s" % cfg.get("dag_path"))
    with open(cfg["dag_path"], encoding="utf-8") as f:
        return json.load(f)


def load_content(cfg):
    path = cfg.get("content_path")
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"nodes": []}


# ---------------------------------------------------------------- 书证核验投影

BOOK_VERIFICATION_FILE = "book-verification.json"


def load_book_verification(cfg):
    """读 10-dag-data/book-verification.json（公开安全投影）；缺失/损坏 → {}。"""
    dd = cfg.get("data_dir")
    if not dd:
        return {}
    path = os.path.join(dd, BOOK_VERIFICATION_FILE)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _anchor_label(rec):
    """章节锚标签：有 section 用 Ch<section>，否则 Ch<chapter>。"""
    section = rec.get("section") or ""
    chapter = rec.get("chapter") or ""
    if section:
        return "Ch%s" % section
    if chapter:
        return "Ch%s" % chapter
    return ""


_STRENGTH_RANK = {"contradicted": 3, "direct": 2, "partial": 1, "inferred": 0}


def _strongest(recs):
    """取证据强度优先级最高者（contradicted > direct > partial > inferred）。"""
    return max(recs, key=lambda r: _STRENGTH_RANK.get(r.get("evidence_strength"), -1))


def book_evidence_line(by_node, nid):
    """节点页/镜像 §10 的书证核验行文本（仅章节级，按 source_id 升序）。

    返回纯文本锚串，例如 ``BK-007 Ch5.2（direct）、Ch11（partial）``；无记录返回 ""。
    """
    recs = by_node.get(nid) or []
    if not recs:
        return ""
    grouped = {}
    for r in recs:
        label = _anchor_label(r)
        if label:
            grouped.setdefault((r.get("source_id") or "", label), []).append(r)
    by_src = {}
    for (sid, label), group in grouped.items():
        by_src.setdefault(sid, []).append(
            (label, _strongest(group).get("evidence_strength", "")))
    parts = []
    for sid in sorted(by_src):
        cells = ["%s（%s）" % (label, strength)
                 for label, strength in sorted(by_src[sid], key=lambda t: _nat_key(t[0]))]
        parts.append("%s %s" % (sid, "，".join(cells)))
    return "；".join(parts)


def _nat_key(label):
    parts = re.split(r"(\d+)", str(label or ""))
    return [(0, int(p), "") if p.isdigit() else (1, 0, p) for p in parts]


class Graph(object):
    """规范化后的图数据，渲染器统一消费对象。"""

    def __init__(self, cfg, raw_dag):
        self.cfg = cfg
        self.raw = raw_dag
        c_by_id = {n.get("id"): n for n in (load_content(cfg).get("nodes") or [])}

        groups = list(raw_dag.get("groups") or [])
        for g in groups:
            g.setdefault("kind", "source")
            g.setdefault("domain", "")
            g.setdefault("node_ids", [])
            g.setdefault("name", g.get("id", ""))

        nodes = []
        for raw in raw_dag.get("nodes") or []:
            nodes.append(self._norm_node(raw, c_by_id.get(raw.get("id"))))

        edges = []
        for i, raw in enumerate(raw_dag.get("edges") or []):
            e = dict(raw)
            e.setdefault("id", "E-%03d" % (i + 1))
            e.setdefault("type", "dependency")
            e.setdefault("label", "")
            e.setdefault("directed", True)
            e.setdefault("sources", [])
            edges.append(e)

        self.groups = groups
        self.group_by_id = {g["id"]: g for g in groups}
        self.nodes = nodes
        self.by_id = {n["id"]: n for n in nodes}
        self.edges = edges
        self.node_to_group = {}
        self.group_node_index = {}
        for g in groups:
            for i, nid in enumerate(g["node_ids"]):
                self.node_to_group[nid] = g["id"]
                self.group_node_index[nid] = i

        themes = raw_dag.get("themes") or []
        if not themes and cfg.get("themes"):
            themes = [{"id": k, "name": v} for k, v in cfg["themes"].items()]
        self.themes = themes
        self.theme_by_id = {t.get("id"): t for t in themes}
        self.cases = raw_dag.get("cases") or [n for n in nodes if n["type"] == "case"]

        # 能力探测（决定视图生成与降级）
        self.has_layer = any(n.get("layer") for n in nodes)
        self.has_domain_enum = any(n.get("domain") for n in nodes)
        self.has_src = any(n.get("src") for n in nodes)
        self.has_cross_ref = any(e["type"] == "cross_reference" for e in edges)
        self.has_cases = bool([n for n in nodes if n["type"] == "case"]) or bool(self.cases)
        self.book_verification = load_book_verification(cfg).get("by_node") or {}

    @staticmethod
    def _norm_node(raw, content):
        n = dict(raw)
        n.setdefault("name", n.get("id", ""))
        n.setdefault("en", "")
        n.setdefault("aliases", [])
        n.setdefault("type", "principle")
        n.setdefault("stage", "basic")
        n.setdefault("definition", "")
        n.setdefault("group", None)
        n.setdefault("layer", None)
        n.setdefault("domain", None)
        n.setdefault("cross_cutting", [])
        n.setdefault("case", [])
        n.setdefault("sources", [])
        n.setdefault("src", None)
        n.setdefault("verified", None)
        n.setdefault("confidence", None)
        n.setdefault("review_date", None)
        n.setdefault("status", None)
        n.setdefault("version", None)
        n.setdefault("deprecated_at", None)
        n.setdefault("superseded_by", None)
        n.setdefault("errata", [])
        n.setdefault("entry_links", [])
        n.setdefault("tags", [])
        n["_content"] = content or {}
        det = n.get("detail") or {}
        if not det:
            c = n["_content"]
            det = {
                "principle": " ".join(c.get("why", []) or []),
                "mechanism": " ".join(c.get("how", []) or []),
                "engineering": "",
                "tradeoff": " ".join(c.get("tradeoff", []) or []),
            }
        n["_detail"] = det
        return n


def build_graph(cfg):
    return Graph(cfg, load_dag(cfg))


def sections(node):
    """统一内容分段（兼容 12factor what/why/how 与母库 detail.*）。"""
    c = node["_content"]
    det = node["_detail"]
    why = list(c.get("why") or [])
    if not why and det.get("principle"):
        why = [det["principle"]]
    how = list(c.get("how") or [])
    if not how:
        for k in ("mechanism", "engineering"):
            if det.get(k):
                how.append(det[k])
    tradeoff = list(c.get("tradeoff") or [])
    if not tradeoff and det.get("tradeoff"):
        tradeoff = [det["tradeoff"]]
    return {
        "what": list(c.get("what") or []),
        "why": why,
        "how": how,
        "tradeoff": tradeoff,
        "cases": list(c.get("cases") or []),
        "anti": list(c.get("anti_patterns") or []),
        "app_side": list(c.get("app_side") or []),
        "agent_side": list(c.get("agent_side") or []),
        "difference": list(c.get("difference") or []),
        "source_refs": list(c.get("source_refs") or []),
    }


# ================================================================ 拓扑

def topo_sort(node_ids, edges, types=HARD_EDGE_TYPES):
    idset = set(node_ids)
    adj = defaultdict(list)
    indeg = {n: 0 for n in node_ids}
    for e in edges:
        f, t = e["from"], e["to"]
        if e["type"] in types and f in idset and t in idset:
            adj[f].append(t)
            indeg[t] += 1
    for u in adj:
        adj[u] = sorted(adj[u])
    q = deque(sorted(n for n in node_ids if indeg[n] == 0))
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    for n in node_ids:
        if n not in order:
            order.append(n)
    return order


def edges_for_node(g, nid):
    out = [e for e in g.edges if e["from"] == nid or e["to"] == nid]
    out.sort(key=lambda e: (e["type"], e["from"], e["to"]))
    return out


# ================================================================ 徽章 / 片段

def _badge(cls, style, text):
    if not text:
        return ""
    return '<span class="badge %s">%s</span>' % (cls, esc(text))


def stage_badge(stage):
    st = STAGE_STYLE.get(stage)
    return _badge("st %s" % stage, st, st["label"]) if st else ""


def layer_badge(layer):
    ls = LAYER_STYLE.get(layer)
    return _badge("ly", ls, ls["label"]) if ls else ""


def src_badge(src):
    s = SRC_STYLE.get(src)
    return _badge("src", s, s["label"]) if s else ""


def kind_badge(kind):
    k = KIND_STYLE.get(kind)
    return _badge("kind", k, k["label"]) if k else ""


def domain_badge(domain, cfg=None):
    if not domain:
        return ""
    label = (cfg or {}).get("domains", {}).get(domain, domain)
    c = {"fg": "#7fe0d8", "bg": "#12302c", "brd": "#5ad0d0"}
    return _badge("dm", c, "%s · %s" % (domain, label) if label != domain else domain)


def theme_badge(code, cfg=None):
    if not code:
        return ""
    label = (cfg or {}).get("themes", {}).get(code, code)
    c = {"fg": "#c9a8ef", "bg": "#2b2040", "brd": "#b48ae0"}
    return _badge("th", c, label)


def type_badge(node):
    t = node.get("type", "principle")
    label = TYPE_LABELS.get(t, t)
    colors = {
        "principle": {"fg": "#9cc2ff", "bg": "#16273f", "brd": "#4f8cff"},
        "method": {"fg": "#6fd3ae", "bg": "#0f2b1f", "brd": "#2fb98a"},
        "technology": {"fg": "#9cc2ff", "bg": "#16273f", "brd": "#4f8cff"},
        "bridge": {"fg": "#6fd3ae", "bg": "#0f2b1f", "brd": "#2fb98a"},
        "case": {"fg": "#ff8a97", "bg": "#3a1520", "brd": "#e05563"},
        "tool": {"fg": "#e8c66a", "bg": "#3a2f12", "brd": "#e0c35e"},
    }
    return _badge("tp", colors.get(t, colors["principle"]), label)


def group_badge(gid, gname):
    return '<span class="badge grp">%s · %s</span>' % (esc(gid), esc(gname))


def priority_badge(priority):
    if not priority:
        return ""
    return '<span class="badge pr">%s</span>' % esc(priority)


def verified_badge(verified):
    if verified is None:
        return ""
    return '<span class="badge ve">%s</span>' % esc("verified" if verified else "unverified")


def edge_chip(e, node_id, by_id):
    st = EDGE_STYLE.get(e["type"], EDGE_STYLE["dependency"])
    other = e["to"] if e["from"] == node_id else e["from"]
    arrow = "&#8594;" if e["from"] == node_id else "&#8592;"
    oname = by_id.get(other, {}).get("name", other)
    return ('<a class="chip e-%s" href="%s.html">%s%s%s<span class="etype">%s</span></a>'
            % (e["type"], esc(other), esc(oname), arrow, esc(e.get("label", "")), st["label"]))


def nav_seq(items):
    """items: [(dir_label, value, href, cls)]"""
    out = []
    for it in items:
        out.append('<a class="%s" href="%s"><span class="dir">%s</span><span class="v">%s</span></a>'
                   % (it[3], esc(it[2]), esc(it[0]), esc(it[1])))
    return '<div class="navseq">%s</div>' % "".join(out)


# ================================================================ 共享 CSS

BASE_CSS = """
:root{--bg:#f5f1e8;--panel:#fffdf8;--border:#e2d9c8;--text:#2b2620;--dim:#6f6656;--accent:#9a5b1b;--accent2:#1f6f5c;--line:#d8cdb8;--ok:#1f6f5c;--warn:#a8641a;--err:#a33a2e;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.7;}
header{background:var(--panel);border-bottom:1px solid var(--border);padding:14px 24px;}
header .crumb{color:var(--dim);font-size:13px;margin-bottom:6px;}
header .crumb a{color:var(--accent);text-decoration:none;}
header .crumb a:hover{text-decoration:underline;}
header h1{font-size:20px;font-weight:650;color:#f0f3f9;display:inline-block;margin-right:12px;}
.badges{display:inline-flex;gap:6px;flex-wrap:wrap;vertical-align:middle;}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600;border:1px solid transparent;letter-spacing:.3px;}
.badge.grp{background:#1d2a3f;color:#7fb0ff;border-color:#2b3d5f;}
.badge.cnt{background:#23272f;color:#9aa0ab;border-color:#3a3f4a;}
main{padding:24px;max-width:1150px;margin:0 auto;}
h2{font-size:18px;margin:34px 0 12px;color:#cfd6e4;border-bottom:1px solid var(--border);padding-bottom:8px;}
h2 .dim{font-size:13px;font-weight:400;}
h3{font-size:15px;margin:20px 0 8px;color:#b8c2d4;}
p,li{font-size:14px;}
ul{padding-left:22px;}
a{color:var(--accent);text-decoration:none;}
a:hover{text-decoration:underline;}
.dim{color:var(--dim);}
.section{scroll-margin-top:8px;}
.brieflead{background:#0d1a14;border:1px solid #2f5a4a;border-left:4px solid var(--ok);border-radius:8px;padding:12px 16px;font-size:15px;color:#cfe8dd;margin:12px 0;}
.whybox{background:var(--panel);border:1px solid var(--border);border-left-width:4px;border-radius:8px;padding:14px 18px;margin:10px 0;}
.whybox .tag{font-size:12px;font-weight:600;margin-bottom:6px;}
.bullet{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:6px 0;font-size:14px;color:#d3d9e4;}
.pit li{margin:5px 0;font-size:14px;}
.pit li::marker{color:var(--warn);}
.tblwrap{overflow-x:auto;margin:8px 0;}
table{border-collapse:collapse;width:100%;}
th,td{border:1px solid var(--border);padding:7px 11px;font-size:13px;text-align:left;vertical-align:top;}
th{background:var(--panel);color:#b8c2d4;white-space:nowrap;}
td.nid{white-space:nowrap;font-family:Consolas,monospace;font-size:12px;}
td.nid a{color:#8fb5ff;}
td .nname{font-weight:600;color:var(--text);}
td.brief{font-size:12.5px;color:#b6c0d0;}
.navseq{display:flex;gap:10px;margin:16px 0;flex-wrap:wrap;}
.navseq a{display:inline-block;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 18px;font-size:14px;color:#b8c2d4;text-align:center;min-width:150px;}
.navseq a .dir{display:block;font-size:11px;color:var(--dim);margin-bottom:2px;}
.navseq a .v{font-weight:600;color:var(--accent);}
.navseq a.nav-index .v{color:var(--ok);}
.navseq .spacer{flex:1;min-width:60px;}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0;}
.chip{font-size:12px;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:6px;padding:2px 8px;color:#7fb0ff;text-decoration:none;}
.chip:hover{background:#2b3d5f;}
.chip .etype{font-size:10px;opacity:.85;margin-left:4px;}
.pathbox{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:12px 16px;margin:10px 0;}
.path-label{font-size:12px;color:var(--dim);margin-bottom:8px;}
.path-seq{display:flex;flex-wrap:wrap;gap:4px 0;font-size:13px;}
.path-seq a{display:inline-block;background:#16273f;border:1px solid #2b3d5f;border-radius:6px;padding:2px 8px;color:#7fb0ff;text-decoration:none;margin:2px;}
.path-seq a:hover{background:#2b3d5f;}
.dep-list{list-style:none;padding-left:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:8px;margin-top:8px;}
.dep-list li{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:13px;border-left:3px solid var(--warn);}
.dep-list .evi{display:block;font-size:11px;color:var(--dim);margin-top:2px;}
.treenav{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:6px 0 18px;display:flex;flex-wrap:wrap;gap:2px 10px;}
.treenav .label{font-size:12px;color:var(--dim);align-self:center;flex-shrink:0;}
.treenav a{color:var(--dim);font-size:12px;text-decoration:none;border-radius:5px;padding:1px 6px;}
.treenav a:hover{color:var(--accent);background:#1d2a3f;}
.evidence{background:var(--panel);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:8px;padding:12px 16px;margin:10px 0;font-size:13px;}
.evidence .row{margin:4px 0;color:#c7d0de;}
.evidence .k{color:var(--dim);display:inline-block;min-width:96px;}
.compare-cols{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;}
footer{margin-top:44px;padding:16px 24px;border-top:1px solid var(--border);color:var(--dim);font-size:12px;text-align:center;}
@media (max-width:720px){
  main{padding:14px;}
  header{padding:12px 14px;}
  header h1{font-size:17px;}
  .navseq a{min-width:100%;}
  .badges{display:flex;margin-top:6px;}
}
@media print{
  body{background:#fff;color:#000;}
  header,footer,.navseq,.treenav{display:none;}
  th,td{border-color:#999;color:#000;}
}

/* ================================================================
   浅色 Codex 皮肤（阶段6·A 案）——新组件 + 旧组件浅色适配
   ================================================================ */
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;line-height:1.85;font-size:16px;}
.serif,h1,h2,h3{font-family:Georgia,'Songti SC','Noto Serif CJK SC','SimSun',serif;}
a{color:#1d4ed8;}
a:hover{text-decoration:underline;}

/* 顶栏 / 面包屑（新节点页） */
.topbar{position:sticky;top:0;z-index:20;background:rgba(245,241,232,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--border);}
.topbar .in{max-width:1180px;margin:0 auto;padding:9px 22px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;}
.crumb{font-size:12.5px;color:var(--dim);}
.crumb a{color:var(--accent);}
.crumb .sep{margin:0 5px;opacity:.5;}
.topbar .meta{font-size:12px;color:var(--dim);margin-left:auto;}

/* 版心 / TOC */
.wrap{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:236px minmax(0,760px);gap:44px;padding:34px 22px 80px;}
nav.toc{position:sticky;top:70px;align-self:start;font-size:13.5px;}
nav.toc .t{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim);margin-bottom:10px;}
nav.toc a{display:block;color:var(--dim);padding:5px 0 5px 14px;border-left:2px solid var(--border);line-height:1.45;text-decoration:none;}
nav.toc a:hover{color:var(--accent);border-left-color:var(--accent);}
nav.toc a .n{font-family:Georgia,serif;color:var(--accent);font-weight:700;margin-right:6px;}
article{min-width:0;}

/* 文档头 */
header.doc h1{font-size:34px;line-height:1.25;letter-spacing:-.01em;margin:2px 0 6px;font-weight:700;color:var(--text);display:block;}
header.doc .en{font-family:Georgia,serif;font-style:italic;color:var(--dim);font-size:16px;}
header.doc .badges{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px;vertical-align:baseline;}

/* 章节 */
section{scroll-margin-top:76px;margin:46px 0;}
section>h2{font-size:23px;font-weight:700;letter-spacing:-.01em;display:flex;align-items:baseline;gap:12px;color:var(--text);border-bottom:0;padding-bottom:0;margin:0 0 8px;}
section>h2 .num{font-size:15px;color:var(--accent);font-family:Georgia,serif;font-weight:700;}
section>h2::after{content:"";flex:1;height:1px;background:var(--border);}
section>h3{font-size:17px;margin:22px 0 8px;color:var(--text);}
.lede{font-size:17px;}
.lead{font-weight:600;}
.hl{background:linear-gradient(transparent 58%,#f0dcae 58%);}

/* 摘要卡 */
.defcard{background:var(--panel);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:4px;padding:18px 22px;margin:16px 0 4px;position:relative;}
.defcard .lab{position:absolute;top:-9px;left:16px;background:var(--accent);color:#fff;font-size:10.5px;letter-spacing:.14em;padding:1px 8px;border-radius:3px;}
.defcard p{font-size:17px;margin:2px 0;}
.note{font-family:Georgia,serif;font-style:italic;color:var(--dim);border-left:3px solid var(--border);padding:2px 0 2px 16px;margin:14px 0;font-size:14.5px;}

/* 关系图 */
figure{margin:22px 0;}
.figbox{background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:10px;overflow-x:auto;-webkit-overflow-scrolling:touch;}
.nbhd{width:100%;height:auto;display:block;}
figcaption{font-size:13px;color:var(--dim);margin-top:8px;line-height:1.6;}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--dim);margin:8px 2px;}
.lgd{display:inline-flex;align-items:center;gap:6px;}
.lgd i{width:18px;height:3px;border-radius:2px;display:inline-block;}

/* 表格（浅色，兼容组页） */
th,td{border:1px solid var(--border);padding:8px 11px;text-align:left;vertical-align:top;}
th{background:#efe9dc;color:#5a5142;font-weight:600;}
td.k{white-space:nowrap;color:var(--dim);font-size:12.5px;}
table.cmp th{text-align:left;}

/* 权衡卡 */
.tradeoff{border:1px solid var(--border);border-radius:5px;overflow:hidden;background:var(--panel);}
.tradeoff .row{display:grid;grid-template-columns:118px 1fr;border-top:1px solid var(--border);}
.tradeoff .row:first-child{border-top:0;}
.tradeoff .row .h{padding:14px;font-weight:700;font-size:13.5px;}
.tradeoff .row .b{padding:14px 16px;font-size:14.5px;border-left:1px solid var(--border);margin:0;}
.tradeoff ul.b{list-style:disc;padding-left:34px;}
.tradeoff .row.gain .h{background:#eef7f2;color:#1f6f5c;}
.tradeoff .row.cost .h{background:#fbf3e6;color:#8a5a12;}
.tradeoff .row.counter .h{background:#fbeeee;color:#a01f2c;}
.tradeoff .row.neutral .h{background:#f1ece0;color:#6f6656;}

/* 学习路径条 */
.pathbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:14px 16px;overflow-x:auto;}
.pathbar .step{display:flex;flex-direction:column;gap:2px;background:#eef4ff;border:1px solid #c5d7f5;border-radius:5px;padding:7px 12px;}
.pathbar .step .id{font-size:10.5px;color:#4b6ea8;font-family:Georgia,serif;}
.pathbar .step .nm{font-size:13.5px;color:#1d4ed8;}
.pathbar .step.cur{background:#fbf1e8;border-color:#e0b79a;}
.pathbar .step.cur .nm{font-weight:700;color:#8a3b12;font-family:Georgia,serif;}
.pathbar .arw{color:var(--dim);font-size:16px;}

/* 案例带 */
.case-band{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;}
.case-card{background:var(--panel);border:1px solid var(--border);border-top:3px solid #c2680e;border-radius:5px;padding:13px 15px;}
.case-card .id{font-size:11px;color:#c2680e;font-family:Georgia,serif;font-weight:700;}
.case-card h4{font-size:14.5px;margin:4px 0 6px;color:var(--text);}
.case-card p{font-size:13px;color:#4d463a;margin:0;}

/* 渐进披露 */
details{border:1px solid var(--border);border-radius:5px;background:var(--panel);padding:0 14px;margin:12px 0;}
details summary{cursor:pointer;padding:12px 0;font-weight:600;font-size:14px;color:#5a5142;}
details[open] summary{border-bottom:1px solid var(--border);}
details .in{padding:6px 0 14px;font-size:14px;}

/* 信源核验（新 .r / 旧 .row 双兼容） */
.evidence{background:var(--panel);border:1px solid var(--border);border-radius:5px;padding:6px 18px;font-size:13px;}
.evidence .r{display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--border);font-size:14px;color:var(--text);flex-wrap:wrap;min-width:0;}
.evidence .r:first-child{border-top:0;}
.evidence .r .k{width:112px;flex:0 0 auto;color:var(--dim);font-size:12.5px;}
.evidence .r a{word-break:break-all;overflow-wrap:anywhere;}
.evidence .row{margin:6px 0;color:var(--text);}
.evidence .k{color:var(--dim);display:inline-block;min-width:96px;}
.erratum{background:#fbf1e8;border-left:3px solid #c2680e;padding:10px 14px;margin:10px 0;font-size:13.5px;}
.erratum .m{color:#a01f2c;text-decoration:line-through;}

/* 术语内联 */
.term{border-bottom:1px dotted #b08a55;color:#7a4a12;font-weight:500;text-decoration:none;}
.term:hover{border-bottom-style:solid;}
.glterm{border-bottom:1px dotted #b08a55;color:#7a4a12;font-weight:500;}

/* 徽章（浅色） */
body>header{background:var(--panel);border-bottom:1px solid var(--border);padding:14px 24px;}
body>header h1{font-size:20px;font-weight:650;color:var(--text);display:inline-block;margin-right:12px;}
body>header .crumb{color:var(--dim);font-size:13px;margin-bottom:6px;}
body>header .crumb a{color:var(--accent);}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600;border:1px solid var(--border);background:var(--panel);color:var(--dim);letter-spacing:.3px;}
.badge.basic{color:#1f6f5c;border-color:#a9cbbf;background:#eef7f2;}
.badge.intermediate{color:#8a3b12;border-color:#e0b79a;background:#fbf1e8;}
.badge.advanced{color:#5b3a8a;border-color:#c9b6e8;background:#f3eefb;}
.badge.pr{color:#8a3b12;border-color:#e0b79a;background:#fbf1e8;}
.badge.ve{color:#1f6f5c;border-color:#a9cbbf;background:#eef7f2;}
.badge.ly{color:#7a4a12;border-color:#e0c9a0;background:#f7f0e2;}
.badge.tp{color:#1d4ed8;border-color:#c5d7f5;background:#eef4ff;}
.badge.src{color:#1d4ed8;border-color:#c5d7f5;background:#eef4ff;}
.badge.dm{color:#0d7f7f;border-color:#a9cfcf;background:#eaf6f6;}
.badge.th{color:#5b3a8a;border-color:#c9b6e8;background:#f3eefb;}
.badge.kind{color:#7a4a12;border-color:#e0c9a0;background:#f7f0e2;}
.badge.grp{color:#7a4a12;border-color:#e0c9a0;background:#f7f0e2;}
.badge.cnt{color:#6f6656;border-color:var(--border);background:#f1ece0;}

/* 旧组件浅色适配（组页 / 视图页立即可用） */
h2{color:var(--text);}
h3{color:var(--text);}
.brieflead{background:#eef7f2;border:1px solid #a9cbbf;border-left:4px solid var(--ok);border-radius:8px;padding:12px 16px;font-size:15px;color:#234a3d;margin:12px 0;}
.bullet{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:6px 0;font-size:14px;color:var(--text);}
th{background:#efe9dc;color:#5a5142;}
td.brief{font-size:12.5px;color:var(--dim);}
.navseq a{display:inline-block;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 18px;font-size:14px;color:var(--text);text-align:center;min-width:150px;}
.chip{font-size:12px;background:#eef4ff;border:1px solid #c5d7f5;border-radius:6px;padding:2px 8px;color:#1d4ed8;text-decoration:none;}
.chip:hover{background:#dbe7fb;}
.path-seq a{display:inline-block;background:#eef4ff;border:1px solid #c5d7f5;border-radius:6px;padding:2px 8px;color:#1d4ed8;text-decoration:none;margin:2px;}
.path-seq a:hover{background:#dbe7fb;}
.treenav a:hover{color:var(--accent);background:#f1ece0;}
.evidence .row{color:var(--text);}

@media(max-width:900px){
  .wrap{grid-template-columns:1fr;gap:20px;padding:20px 15px 60px;}
  nav.toc{position:static;order:-1;border:1px solid var(--border);border-radius:5px;background:var(--panel);padding:8px 12px;}
  nav.toc a{padding:4px 0 4px 12px;}
  .nbhd{min-width:640px;}
  header.doc h1{font-size:26px;}
}
@media(max-width:720px){
  main{padding:14px;}
  body>header{padding:12px 14px;}
  body>header h1{font-size:17px;}
  .badges{display:flex;margin-top:6px;}
}
@media(max-width:560px){
  .tradeoff .row{grid-template-columns:1fr;}
  .tradeoff .row .b{border-left:0;border-top:1px dashed var(--border);}
  .nbhd{min-width:560px;}
  table{font-size:12.5px;}
}
"""


# ================================================================ 浅色邻域图 / 术语（阶段6）

NBHD_EDGE = {
    "prerequisite":    {"color": "#2563eb", "dashed": False},
    "implements":      {"color": "#0f8a63", "dashed": False},
    "derives_from":    {"color": "#7c3aed", "dashed": False},
    "case_instance":   {"color": "#c2680e", "dashed": True},
    "contrasts":       {"color": "#a17c00", "dashed": True},
    "conflicts":       {"color": "#c22836", "dashed": True},
    "dependency":      {"color": "#6b7280", "dashed": False},
    "refines":         {"color": "#7c3aed", "dashed": False},
    "combination":     {"color": "#0d7f7f", "dashed": False},
    "enables":         {"color": "#0d7f7f", "dashed": False},
    "cross_reference": {"color": "#0d7f7f", "dashed": False},
    "mitigates":       {"color": "#0f8a63", "dashed": False},
    "supersedes":      {"color": "#a17c00", "dashed": False},
    "deprecated_by":   {"color": "#6b7280", "dashed": False},
    "variant":         {"color": "#a17c00", "dashed": False},
    "cooccurrence":    {"color": "#0d7f7f", "dashed": False},
}
NBHD_LEGEND = [
    ("prerequisite", "前置依赖"),
    ("implements", "实现"),
    ("derives_from", "依据推导"),
    ("case_instance", "案例印证"),
    ("contrasts", "对比"),
    ("conflicts", "冲突"),
]

_GLOSSARY_CACHE = {}
_TERM_CACHE = {}


def _adjacency(g):
    adj = defaultdict(list)
    for e in g.edges:
        adj[e["from"]].append(e["to"])
        adj[e["to"]].append(e["from"])
    return {k: sorted(set(v)) for k, v in adj.items()}


def bfs_dist(g, nid, maxd=2):
    adj = _adjacency(g)
    dist = {nid: 0}
    parent = {nid: None}
    frontier = [nid]
    for d in range(1, maxd + 1):
        nxt = []
        for u in frontier:
            for v in adj.get(u, []):
                if v not in dist:
                    dist[v] = d
                    parent[v] = u
                    nxt.append(v)
        frontier = nxt
    return dist, parent


def neighborhood(g, nid, max_nodes=24):
    adj = _adjacency(g)
    dist, parent = bfs_dist(g, nid, 2)
    order = [nid] + [x for x in sorted(dist, key=lambda k: (dist[k], k)) if x != nid]
    d1 = [x for x in order if dist[x] == 1]
    d2 = [x for x in order if dist[x] == 2]
    allowed = [nid] + d1
    slots = max(0, max_nodes - len(allowed))
    d2 = sorted(d2, key=lambda x: (-len(adj.get(x, [])), x))
    allowed += d2[:slots]
    aset = set(allowed)
    nedges = []
    seen = set()
    for e in g.edges:
        if e["from"] in aset and e["to"] in aset:
            key = (e["type"], e["from"], e["to"], e.get("label", ""))
            if key in seen:
                continue
            seen.add(key)
            nedges.append(e)
    return {"ids": allowed, "dist": dist, "parent": parent, "edges": nedges, "adj": adj}


def _layout_positions(ids, dist, parent, edges):
    pos = {}
    center = ids[0]
    pos[center] = [0.0, 0.0]
    n1 = [x for x in ids if x != center and dist[x] == 1]
    n2 = [x for x in ids if dist[x] == 2]
    for i, x in enumerate(n1):
        a = -math.pi / 2 + 2 * math.pi * i / max(1, len(n1))
        pos[x] = [150.0 * math.cos(a), 150.0 * math.sin(a)]
    sib = defaultdict(list)
    for x in n2:
        sib[parent[x]].append(x)
    for p in sorted(sib, key=lambda k: str(k)):
        kids = sorted(sib[p])
        if p in pos:
            px, py = pos[p]
            base = math.atan2(py, px) if (abs(px) > 1e-6 or abs(py) > 1e-6) else -math.pi / 2
        else:
            base = -math.pi / 2
        k = len(kids)
        for j, x in enumerate(kids):
            a = base + (j - (k - 1) / 2.0) * (2 * math.pi / 24.0)
            pos[x] = [275.0 * math.cos(a), 275.0 * math.sin(a)]
    for _ in range(2):
        disp = {x: [0.0, 0.0] for x in ids}
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                dx = pos[a][0] - pos[b][0]
                dy = pos[a][1] - pos[b][1]
                d = math.sqrt(dx * dx + dy * dy)
                if d < 1e-6:
                    dx, dy, d = 1.0, 0.0, 1.0
                if d < 140.0:
                    f = (140.0 - d) * 0.35
                    ux, uy = dx / d, dy / d
                    disp[a][0] += ux * f
                    disp[a][1] += uy * f
                    disp[b][0] -= ux * f
                    disp[b][1] -= uy * f
        for e in edges:
            a, b = e["from"], e["to"]
            if a not in pos or b not in pos:
                continue
            dx = pos[b][0] - pos[a][0]
            dy = pos[b][1] - pos[a][1]
            d = math.sqrt(dx * dx + dy * dy) or 1.0
            if d > 240.0:
                f = (d - 240.0) * 0.15
                ux, uy = dx / d, dy / d
                disp[a][0] += ux * f
                disp[a][1] += uy * f
                disp[b][0] -= ux * f
                disp[b][1] -= uy * f
        for x in ids:
            if x == center:
                pos[x] = [0.0, 0.0]
                continue
            pos[x][0] += max(-30.0, min(30.0, disp[x][0]))
            pos[x][1] += max(-30.0, min(30.0, disp[x][1]))
    return {x: (round(pos[x][0], 1), round(pos[x][1], 1)) for x in ids}


def _trunc(s, n):
    s = "" if s is None else str(s)
    return s if len(s) <= n else s[:n] + "\u2026"


def nbhd_legend():
    parts = []
    for t, label in NBHD_LEGEND:
        st = NBHD_EDGE.get(t, {})
        parts.append('<span class="lgd"><i style="background:%s"></i>%s</span>'
                     % (st.get("color", "#6b7280"), esc(label)))
    return '<div class="legend">%s</div>' % "".join(parts)


def _render_graph_svg(g, ids, dist, parent, edges, center, aria_label, title_text):
    """确定性关系图渲染器（邻域图 / 组内子图共用同一构造器）。

    ids[0] 必须为中心节点（_layout_positions 以 ids[0] 为原点）。
    节点：中心实心强调；dist==1 实心小点；dist>=2 空心小点。
    """
    pos = _layout_positions(ids, dist, parent, edges)
    xs = [pos[x][0] for x in ids]
    ys = [pos[x][1] for x in ids]
    pad = 64.0
    minx = min(min(xs) - pad, -275 - pad)
    maxx = max(max(xs) + pad, 275 + pad)
    miny = min(min(ys) - pad, -275 - pad)
    maxy = max(max(ys) + pad, 275 + pad)
    w = maxx - minx
    h = maxy - miny
    out = ['<svg class="nbhd" viewBox="%s %s %s %s" role="img" aria-label="%s">'
           % (fmt_num(minx), fmt_num(miny), fmt_num(w), fmt_num(h), esc(aria_label))]
    out.append('<title>%s</title>' % esc(title_text))
    out.append('<circle cx="0" cy="0" r="150" fill="none" stroke="#d8cdb8" stroke-dasharray="3 6" opacity=".35"/>')
    out.append('<circle cx="0" cy="0" r="275" fill="none" stroke="#d8cdb8" stroke-dasharray="3 6" opacity=".2"/>')
    for e in edges:
        st = NBHD_EDGE.get(e["type"], {"color": "#6b7280", "dashed": False})
        x1, y1 = pos[e["from"]]
        x2, y2 = pos[e["to"]]
        dash = ' stroke-dasharray="5 4"' if st["dashed"] else ""
        center_edge = e["from"] == center or e["to"] == center
        width = "2.0" if center_edge else "1.2"
        op = ".85" if center_edge else ".45"
        out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" opacity="%s"%s>'
                   '<title>%s</title></line>'
                   % (fmt_num(x1), fmt_num(y1), fmt_num(x2), fmt_num(y2),
                      st["color"], width, op, dash,
                      esc("%s（%s）%s" % (EDGE_STYLE.get(e["type"], {}).get("label", e["type"]),
                                          e["type"], ("：" + e.get("label", "")) if e.get("label") else ""))))
    for x in ids:
        px, py = pos[x]
        nd = g.by_id.get(x, {})
        nm = nd.get("name", x)
        if x == center:
            r, fs, fw = 13.0, 13.0, 700
            out.append('<circle cx="%s" cy="%s" r="%s" fill="#9a5b1b" stroke="#9a5b1b" stroke-width="2.5"/>'
                       % (fmt_num(px), fmt_num(py), r))
        elif dist[x] == 1:
            r, fs, fw = 9.0, 12.0, 700
            out.append('<circle cx="%s" cy="%s" r="%s" fill="#c98a3a" stroke="none"/>'
                       % (fmt_num(px), fmt_num(py), r))
        else:
            r, fs, fw = 6.0, 11.5, 500
            out.append('<circle cx="%s" cy="%s" r="%s" fill="#fffdf8" stroke="#c98a3a" stroke-width="1.5"/>'
                       % (fmt_num(px), fmt_num(py), r))
        out.append('<text x="%s" y="%s" text-anchor="middle" font-size="%s" font-weight="%s" fill="#2b2620">%s'
                   '<title>%s（%s）</title></text>'
                   % (fmt_num(px), fmt_num(py + r + 10), fs, fw, esc(_trunc(nm, 12)), esc(nm), esc(x)))
    out.append("</svg>")
    return "".join(out)


def neighborhood_svg(g, nid, max_nodes=24):
    node = g.by_id.get(nid, {})
    name = node.get("name", nid)
    nb = neighborhood(g, nid, max_nodes)
    aria = "%s 的 1-2 跳邻域关系图" % name
    return _render_graph_svg(g, nb["ids"], nb["dist"], nb["parent"], nb["edges"], nid, aria, aria)


def group_subgraph(g, node_ids, max_nodes=24):
    """组内诱导子图（确定性）：以度数最高的成员为中心，按 BFS 距离裁剪到 max_nodes。"""
    aset = set(n for n in node_ids if n in g.by_id)
    if not aset:
        return {"ids": [], "dist": {}, "parent": {}, "edges": [], "center": None, "total": 0}

    def induced(idset):
        seen, out = set(), []
        for e in g.edges:
            if e["from"] in idset and e["to"] in idset:
                key = (e["type"], e["from"], e["to"], e.get("label", ""))
                if key in seen:
                    continue
                seen.add(key)
                out.append(e)
        return out

    total = len(aset)
    edges = induced(aset)
    deg = defaultdict(int)
    for e in edges:
        deg[e["from"]] += 1
        deg[e["to"]] += 1
    center = sorted(aset, key=lambda x: (-deg.get(x, 0), x))[0]
    if len(aset) > max_nodes:
        adj = defaultdict(list)
        for e in edges:
            adj[e["from"]].append(e["to"])
            adj[e["to"]].append(e["from"])
        order, seen, frontier = [center], {center}, [center]
        while frontier and len(order) < max_nodes:
            nxt = []
            for u in frontier:
                for v in sorted(set(adj.get(u, []))):
                    if v not in seen:
                        seen.add(v)
                        order.append(v)
                        nxt.append(v)
                        if len(order) >= max_nodes:
                            break
                if len(order) >= max_nodes:
                    break
            frontier = nxt
        if len(order) < max_nodes:
            kept = set(order)
            rest = sorted((x for x in aset if x not in kept), key=lambda x: (-deg.get(x, 0), x))
            order += rest[:max_nodes - len(order)]
        aset = set(order)
        edges = induced(aset)
    adj = defaultdict(list)
    for e in edges:
        adj[e["from"]].append(e["to"])
        adj[e["to"]].append(e["from"])
    dist, parent, frontier = {center: 0}, {center: None}, [center]
    while frontier:
        nxt = []
        for u in frontier:
            for v in sorted(set(adj.get(u, []))):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    nxt.append(v)
        frontier = nxt
    ids = [center] + sorted(x for x in aset if x != center)
    for x in ids:
        if x not in dist:
            dist[x] = 2
            parent[x] = center
        if dist[x] > 2:
            dist[x] = 2
    return {"ids": ids, "dist": dist, "parent": parent, "edges": edges,
            "center": center, "total": total}


def group_subgraph_svg(g, node_ids, name="", max_nodes=24):
    sg = group_subgraph(g, node_ids, max_nodes)
    if not sg["ids"]:
        return ""
    aria = "%s 组内关系图" % name if name else "组内关系图"
    return _render_graph_svg(g, sg["ids"], sg["dist"], sg["parent"], sg["edges"],
                             sg["center"], aria, aria)


def group_subgraph_caption(g, node_ids, name="", max_nodes=24):
    sg = group_subgraph(g, node_ids, max_nodes)
    n, total, ne = len(sg["ids"]), sg["total"], len(sg["edges"])
    if total > n:
        scope = "组内共 %d 个成员，按度数裁剪展示 %d 个" % (total, n)
    else:
        scope = "全部 %d 个成员" % total
    prefix = ("%s：" % name) if name else ""
    return ("%s组内关系图（%s）：内联 %d 个节点、%d 条组内边，连线按边类型着色（六类配色见下）；"
            "构建期确定性计算，无运行期脚本。" % (prefix, scope, n, ne))


def fmt_num(v):
    v = round(float(v), 1)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return ("%.1f" % v).rstrip("0").rstrip(".")


def nbhd_caption(g, nid, max_nodes=24):
    nb = neighborhood(g, nid, max_nodes)
    n1 = sum(1 for x in nb["ids"] if nb["dist"][x] == 1)
    n2 = sum(1 for x in nb["ids"] if nb["dist"][x] == 2)
    return ("以本节点为中心，静态内联 1–2 跳邻域：内环 %d 个直接邻接、外环 %d 个二跳节点，"
            "共 %d 个节点；连线按边类型着色（六类配色见下）。构建期计算，无运行期脚本。"
            % (n1, n2, len(nb["ids"])))


# ================================================================ 节点块派生（HTML / MD 双轨共用）

def derive_pathbar(g, nid):
    """§7 学习路径数据（入向优先，保持原顺序）；无 prerequisite 时返回 None。"""
    my = edges_for_node(g, nid)
    pre = sorted([e for e in my if e["type"] == "prerequisite"], key=lambda e: str(e.get("id", "")))
    if not pre:
        return None
    preds, succs = [], []
    for e in pre:
        if e["to"] == nid and e["from"] not in preds:
            preds.append(e["from"])
        elif e["from"] == nid and e["to"] not in succs:
            succs.append(e["to"])
    return {"preds": preds, "succs": succs}


def derive_cases(g, nid):
    """§9 案例带数据（直接 case + 2 跳派生，派生须标注来源路径）。"""
    case_map = {cs.get("id"): cs for cs in g.cases}
    dist, parent = bfs_dist(g, nid, 2)
    direct = [c for c in (g.by_id.get(nid, {}).get("case") or []) if c]
    seen = set(direct)
    items = [(cid, "经 direct", case_map.get(cid, {})) for cid in direct]
    for e in g.edges:
        if e["type"] != "case_instance":
            continue
        cid, concept = e["from"], e["to"]
        if cid == nid or cid in seen:
            continue
        if concept == nid:
            label = "经 direct(边)"
        elif concept in dist and dist[concept] == 1:
            label = "经 %s" % concept
        elif concept in dist and dist[concept] == 2:
            label = "2 跳派生：当前节点 → %s → %s" % (parent.get(concept), concept)
        else:
            continue
        seen.add(cid)
        items.append((cid, label, case_map.get(cid, {})))
    items.sort(key=lambda t: (0 if t[1].startswith("经 direct") else 1, t[0]))
    return items


def derive_compare_tables(g, nid, edges):
    """§8 冲突 / 对比表数据：每格取两端节点原文（首句 / 反例句）。"""
    cur = g.by_id.get(nid, {})
    c_det = cur.get("_detail") or {}
    out = []
    for e in edges:
        other = e["to"] if e["from"] == nid else e["from"]
        o = g.by_id.get(other, {})
        o_det = o.get("_detail") or {}
        ctr = "".join(split_tradeoff(c_det.get("tradeoff") or "")[0]["counter"]) \
            or first_sentence(c_det.get("tradeoff") or "")
        otr = "".join(split_tradeoff(o_det.get("tradeoff") or "")[0]["counter"]) \
            or first_sentence(o_det.get("tradeoff") or "")
        label = EDGE_STYLE.get(e["type"], {}).get("label", e["type"])
        rows = [
            ("定位 / 依据层",
             "%s · %s" % (cur.get("name", nid), cur.get("en", "")),
             "%s · %s" % (o.get("name", other), o.get("en", ""))),
            ("核心定义（原文）", first_sentence(cur.get("definition") or ""),
             first_sentence(o.get("definition") or "")),
            ("首条机制断言（原文）", first_sentence(c_det.get("principle") or ""),
             first_sentence(o_det.get("principle") or "")),
            ("%s关系" % label,
             "%s（%s）" % (e.get("label", ""), label),
             "同一条 %s 边的另一端" % label),
            ("典型反例（原文）", ctr, otr),
            ("处置要点（原文）", first_sentence(c_det.get("engineering") or ""),
             first_sentence(o_det.get("engineering") or "")),
        ]
        out.append({"edge": e, "other": other, "label": label,
                    "other_name": o.get("name", other), "rows": rows})
    return out


def derive_node_blocks(g, node):
    """§1–§11 块的纯数据派生（gen-nodes.py 渲染 HTML、gen-md.py 渲染 Markdown 共用）。

    块序与 00-plan/stage6-content-ia-spec.md §2 完全一致；仅返回存在的块。
    """
    nid = node["id"]
    c = sections(node)
    det = node.get("_detail") or {}
    my = edges_for_node(g, nid)
    principle = det.get("principle") or " ".join(c["why"])
    mechanism = det.get("mechanism") or (" ".join(c["how"]) if c["how"] else "")
    engineering = det.get("engineering") or ""
    to_text = "".join(c["tradeoff"]) if c["tradeoff"] else ""

    blocks = [
        {"kind": "summary", "title": "摘要与结论", "node": node,
         "text": node.get("definition") or "".join(c["what"])},
        {"kind": "relation", "title": "局部关系图", "nid": nid},
    ]
    if principle:
        blocks.append({"kind": "principle", "title": "原理 · 为什么", "text": principle})
    if mechanism:
        blocks.append({"kind": "mechanism", "title": "机制 · 如何运作", "text": mechanism})
    if engineering:
        blocks.append({"kind": "engineering", "title": "工程 · 怎么落地", "text": engineering})
    if to_text:
        blocks.append({"kind": "tradeoff", "title": "权衡卡", "text": to_text, "nid": nid})
    path = derive_pathbar(g, nid)
    if path:
        blocks.append({"kind": "path", "title": "学习路径条", "nid": nid,
                       "preds": path["preds"], "succs": path["succs"]})
    cmp_edges = sorted([e for e in my if e["type"] in ("contrasts", "conflicts")],
                       key=lambda e: str(e.get("id", "")))
    if cmp_edges:
        blocks.append({"kind": "compare", "title": "冲突 / 对比表", "nid": nid,
                       "tables": derive_compare_tables(g, nid, cmp_edges)})
    cases = derive_cases(g, nid)
    if cases:
        blocks.append({"kind": "cases", "title": "案例带", "items": cases})
    blocks.append({"kind": "evidence", "title": "信源与核验", "node": node})
    blocks.append({"kind": "relations", "title": "原始关系清单", "nid": nid, "edges": my})
    return blocks


XREF_FILE = "xref-12factor.json"


def load_xref_index(cfg):
    """加载 12factor 对照表，返回 mother_id -> [row, ...]；缺失/损坏时降级为 {}。"""
    path = os.path.join(cfg.get("checkpoint_dir") or os.path.dirname(os.path.abspath(__file__)),
                        XREF_FILE)
    idx = {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return idx
    for row in data.get("rows") or []:
        if not isinstance(row, dict):
            continue
        for mid in row.get("mother_ids") or []:
            if mid:
                idx.setdefault(mid, []).append(row)
    return idx


def load_canonical_ids(cfg):
    path = os.path.join(cfg.get("repo_root") or "", "03-knowledge-map",
                        "canonical-sources.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    return {s.get("id") for s in data.get("sources", []) if s.get("id")}


# ================================================================ 页面外壳（组页 / 视图页 / 根索引共用）

def page_shell(cfg, title, crumb_html, meta_text, doc_header_html, sections,
               footer_html, toc_label="目录 · CONTENTS", html_title=None, extra_css=""):
    """浅色 Codex 文档外壳：sticky 顶栏 + 面包屑 + 左侧 TOC + 760px 版心。

    sections: [(section_title, inner_html), ...]，自动编号 §1.. 并生成锚点 s1..
    """
    toc = ['<div class="t">%s</div>' % esc(toc_label)]
    body = []
    for i, (t, h) in enumerate(sections, 1):
        toc.append('<a href="#s%d"><span class="n">§%d</span>%s</a>' % (i, i, esc(t)))
        body.append('<section id="s%d"><h2><span class="num">§%d</span>%s</h2>%s</section>'
                    % (i, i, esc(t), h))
    topbar = ('<div class="topbar"><div class="in">%s<div class="meta">%s</div></div></div>'
              % (crumb_html, esc(meta_text)))
    if html_title is None:
        html_title = "%s · %s" % (title, cfg["title"])
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_title}</title>
<style>
{css}{extra_css}
</style>
</head>
<body>
{topbar}
<div class="wrap">
<nav class="toc">{toc}</nav>
<article>
{doc}
{body}
{footer}
</article>
</div>
</body>
</html>
""".format(html_title=esc(html_title), css=BASE_CSS, extra_css=extra_css, topbar=topbar,
           toc="".join(toc), doc=doc_header_html, body="\n".join(body), footer=footer_html)


# ---------------------------------------------------------------- 术语表

def glossary_path(cfg):
    return os.path.join(cfg.get("repo_root") or "", "03-knowledge-map", "glossary.md")


def load_glossary(cfg):
    key = glossary_path(cfg)
    if key in _GLOSSARY_CACHE:
        return _GLOSSARY_CACHE[key]
    result = {"sections": [], "entries": []}
    if not os.path.isfile(key):
        _GLOSSARY_CACHE[key] = result
        return result
    cur = None
    idx = 0
    with open(key, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("## "):
                cur = {"title": line[3:].strip(), "id": "gsec-%d" % (len(result["sections"]) + 1),
                       "entries": []}
                result["sections"].append(cur)
            elif line.startswith("|") and cur is not None:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) < 5:
                    continue
                if cells[0] in ("术语", "---") or set(cells[0]) <= set("-: "):
                    continue
                idx += 1
                e = {"anchor": "g-%03d" % idx, "term": cells[0], "english": cells[1],
                     "definition": cells[2], "source_id": cells[3], "status": cells[4],
                     "section": cur["title"]}
                result["entries"].append(e)
                cur["entries"].append(e)
    _GLOSSARY_CACHE[key] = result
    return result


def build_term_matcher(entries):
    cands = {}
    for e in entries:
        for raw in (e["term"], e["english"]):
            for part in re.split(r"\s*/\s*|\uff0f", raw or ""):
                part = part.strip()
                if len(part) < 2:
                    continue
                if part.isascii() and len(part) < 3:
                    continue
                if part not in cands:
                    cands[part] = e
    if not cands:
        return None
    items = sorted(cands.items(), key=lambda kv: (-len(kv[0]), kv[0]))
    pattern = "(?<![A-Za-z0-9_-])(?:" + "|".join(re.escape(c) for c, _ in items) + ")(?![A-Za-z0-9_-])"
    try:
        rx = re.compile(pattern)
    except re.error:
        return None
    return {"rx": rx, "cand2entry": {c: e for c, e in items}}


def term_matcher_for(cfg):
    key = glossary_path(cfg)
    if key in _TERM_CACHE:
        return _TERM_CACHE[key]
    m = build_term_matcher(load_glossary(cfg)["entries"])
    _TERM_CACHE[key] = m
    return m


def inline_terms(text, matcher, used):
    if text is None:
        return ""
    text = str(text)
    if not matcher or not matcher.get("rx"):
        return esc(text)
    rx = matcher["rx"]
    c2e = matcher["cand2entry"]
    out = []
    last = 0
    for m in rx.finditer(text):
        out.append(esc(text[last:m.start()]))
        cand = m.group(0)
        e = c2e.get(cand)
        anchor = e["anchor"] if e else None
        if anchor and anchor not in used:
            used.add(anchor)
            title = "%s — %s" % (e["english"], e["definition"])
            if e["status"] == "disputed":
                title = "（无权威共识，给推荐口径）" + title
            out.append('<a class="term" href="../14-views/glossary.html#%s" title="%s">%s</a>'
                       % (anchor, esc(title), esc(cand)))
        else:
            out.append(esc(cand))
        last = m.end()
    out.append(esc(text[last:]))
    return "".join(out)


_SENT_RE = re.compile(r"[^\u3002\uff01\uff1f]*[\u3002\uff01\uff1f]|[^\u3002\uff01\uff1f]+$")


def split_sentences(text):
    if not text:
        return []
    return [s for s in _SENT_RE.findall(str(text)) if s.strip()]


def first_sentence(text):
    ss = split_sentences(text)
    return ss[0] if ss else (text or "")


def render_rich_paragraph(text, matcher, used):
    parts = []
    for i, s in enumerate(split_sentences(text)):
        html = inline_terms(s, matcher, used)
        if i == 0:
            parts.append('<span class="lead">%s</span>' % html)
        elif 'class="term"' in html:
            parts.append('<span class="hl">%s</span>' % html)
        else:
            parts.append(html)
    return "".join(parts)


TRADEOFF_MARKERS = {
    "counter": ("\u53cd\u4f8b", "\u8bef\u533a", "\u5931\u8d25", "\u53cd\u9762"),
    "cost": ("\u4ee3\u4ef7", "\u6210\u672c", "\u98ce\u9669", "\u8fc7\u5ea6", "\u4e0d\u8db3"),
    "gain": ("\u6536\u76ca", "\u597d\u5904", "\u4ef7\u503c"),
}


def split_tradeoff(text):
    """严格归栏：句首逐句判定，仅当句子自身含该栏显式标记词才归栏。

    规则（契约 §4 保真红线）：
      - counter 仅收含「反例/误区/失败/反面」的句子；cost 仅收含「代价/成本/风险/过度/不足」；
        gain 仅收含「收益/好处/价值」。
      - 不得因标记词前后相邻而把无标记句一并拉入该栏。
      - 其余所有句子按原顺序进入 neutral（原文要点）。
    每句至多归入一栏（多标记时按 counter→cost→gain 优先级择一），文本逐字引用。
    """
    cols = {"gain": [], "cost": [], "counter": []}
    neutral = []
    for s in split_sentences(text):
        cat = None
        for c in ("counter", "cost", "gain"):
            if any(mk in s for mk in TRADEOFF_MARKERS[c]):
                cat = c
                break
        if cat:
            cols[cat].append(s)
        else:
            neutral.append(s)
    return cols, neutral
