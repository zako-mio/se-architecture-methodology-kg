#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 AI 友好 Markdown 镜像：{out_md}/nodes/*.md + 索引文件。

节点镜像块序列与 HTML 节点页严格同序（见 00-plan/stage6-content-ia-spec.md §2/§8）：
  §1 摘要与结论 · §2 局部关系图 · §3 原理 · §4 机制 · §5 工程 · §6 权衡卡
  §7 学习路径条（条件）· §8 冲突 / 对比表（条件）· §9 案例带（条件）
  §10 信源与核验 · §11 原始关系清单 · 附 对照资源（条件）
双轨一致性由 gen_common.derive_node_blocks 保证；术语保持纯文本不加外链。

基础索引（所有数据通用）：
  00-index.md         节点总表
  01-groups.md        分组索引
  02-stage.md         难度阶段视图
  03-learning-path.md prerequisite 拓扑学习路径
扩展索引（数据具备时自动追加）：
  04-layer.md         三层视图（有 layer 字段时）
  05-cases.md         案例视图（有 case 节点时）
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (build_graph, topo_sort, esc, STAGE_STYLE, LAYER_STYLE,
                        TYPE_LABELS, EDGE_STYLE, KIND_STYLE, LAYER_ORDER,
                        derive_node_blocks, split_tradeoff, neighborhood,
                        load_xref_index, add_common_args, config_from_args)

STAGE_LABEL = {"basic": "基础 basic", "intermediate": "进阶 intermediate", "advanced": "高级 advanced"}


def _cell(t):
    return ("" if t is None else str(t)).replace("|", "\\|").replace("\n", " ").strip()


def _stage_label(s):
    return STAGE_LABEL.get(s, s)


def _md_block(g, node, block):
    """把一个派生块渲染为 Markdown（与 HTML 块同序同数据）。"""
    kind = block["kind"]
    if kind == "summary":
        out = ["> %s" % _cell(block["text"]), ""]
        aliases = "、".join(node.get("aliases") or []) or "—"
        t = TYPE_LABELS.get(node.get("type"), node.get("type") or "")
        if node.get("subtype"):
            t = "%s / %s" % (t, node["subtype"])
        out += ["- 别名：%s" % _cell(aliases),
                "- 英文：%s" % _cell(node.get("en") or "—"),
                "- 类型：%s" % _cell(t), ""]
        return out
    if kind == "relation":
        nid = block["nid"]
        nb = neighborhood(g, nid)
        ids = sorted(nb["ids"], key=lambda x: (nb["dist"][x], x))
        out = ["以本节点为中心的 1–2 跳邻域（构建期静态派生；HTML 版为内联 SVG）。", "",
               "| 跳数 | 节点 ID | 名称 |", "|---|---|---|"]
        for x in ids:
            out.append("| %d | `%s` | %s |"
                       % (nb["dist"][x], x, _cell(g.by_id.get(x, {}).get("name", x))))
        out.append("")
        if nb["edges"]:
            out.append("邻域内关系边：")
            out.append("")
            out.append("| 类型 | 方向 | 说明 |")
            out.append("|---|---|---|")
            for e in sorted(nb["edges"], key=lambda e: (e["type"], e["from"], e["to"])):
                label = EDGE_STYLE.get(e["type"], {}).get("label", e["type"])
                out.append("| %s | %s → %s | %s |"
                           % (label, e["from"], e["to"], _cell(e.get("label", ""))))
            out.append("")
        return out
    if kind in ("principle", "mechanism", "engineering"):
        return [_cell(block["text"]), ""]
    if kind == "tradeoff":
        cols, neutral = split_tradeoff(block["text"])
        out = []
        for key, label in (("gain", "收益 · 正确姿势"), ("cost", "代价 · 风险"), ("counter", "反例 · 误区")):
            if not cols[key]:
                continue
            out += ["### %s" % label, ""]
            out += ["- %s" % _cell(s) for s in cols[key]]
            out.append("")
        if neutral:
            out += ["### 原文要点", ""]
            out += ["- %s" % _cell(s) for s in neutral]
            out.append("")
        out += ["> 权衡原文仅按显式标记词归栏引用（收益 / 代价 / 反例），"
                "其余句子按原序列为「原文要点」；内容逐字引用未改写。", ""]
        return out
    if kind == "path":
        def nm(x):
            return "%s（%s）" % (g.by_id.get(x, {}).get("name", x), x)
        seq = [nm(x) for x in block["preds"]] + ["**%s（%s）**" % (node["name"], node["id"])
               ] + [nm(x) for x in block["succs"]]
        return [" → ".join(seq), ""]
    if kind == "compare":
        out = []
        for t in block["tables"]:
            out += ["### 真实 %s 边：%s" % (t["label"], _cell(t["edge"].get("label", ""))), "",
                    "| 对照维度 | %s | %s |" % (_cell(node.get("name", node["id"])), _cell(t["other_name"])),
                    "|---|---|---|"]
            for k, a, b in t["rows"]:
                out.append("| %s | %s | %s |" % (_cell(k), _cell(a) or "—", _cell(b) or "—"))
            out.append("")
        return out
    if kind == "cases":
        out = []
        for cid, label, cs in block["items"]:
            out.append("- **%s**（%s）%s：%s"
                       % (cid, label, _cell(cs.get("title", cid)), _cell(cs.get("summary", ""))))
        out.append("")
        return out
    if kind == "evidence":
        n = block["node"]
        out = []
        if n.get("verified") is not None:
            out.append("- 核验状态：%s" % ("True（verified）" if n["verified"] else "False（unverified）"))
        for k, key in (("置信度", "confidence"), ("复核日期", "review_date"),
                       ("生命周期", "status"), ("版本", "version")):
            if n.get(key) not in (None, ""):
                out.append("- %s：%s" % (k, _cell(n.get(key))))
        if n.get("sources"):
            out.append("- 规范信源：%s" % "、".join(n["sources"]))
        for u in n.get("entry_links") or []:
            if str(u).startswith("http"):
                out.append("- 入口链接：%s" % u)
        for er in n.get("errata") or []:
            out.append("- 勘误：常见误解「%s」→ 核验结论「%s」（%s）"
                       % (_cell(er.get("misconception", "")), _cell(er.get("verified_value", "")),
                          er.get("source_id", "")))
        out.append("")
        return out
    if kind == "relations":
        edges = block["edges"]
        out = ["| 关系 | 方向 | 对端节点 | 边 ID | 说明 |", "|---|---|---|---|---|"]
        for e in edges:
            nid = block["nid"]
            direction = "%s → %s" % (e["from"], e["to"])
            other = e["to"] if e["from"] == nid else e["from"]
            onm = g.by_id.get(other, {}).get("name", other)
            label = EDGE_STYLE.get(e["type"], {}).get("label", e["type"])
            out.append("| %s | %s | %s（`%s`） | %s | %s |"
                       % (label, direction, _cell(onm), other, e.get("id", ""), _cell(e.get("label", ""))))
        out.append("")
        return out
    return []


def _md_xref(g, nid):
    xrows = load_xref_index(g.cfg).get(nid) or []
    if not xrows:
        return []
    out = ["| 12factor 节点 | 关系 | 对照说明 |", "|---|---|---|"]
    for r in xrows:
        name = r.get("tf_name") or r.get("tf_id") or ""
        link = r.get("deep_link") or ""
        cell = "%s（%s）%s" % (name, r.get("tf_id") or "", (" %s" % link) if link else "")
        rel = r.get("relation") or ""
        rel_label = EDGE_STYLE.get(rel, {}).get("label", rel)
        out.append("| %s | %s | %s |" % (_cell(cell), _cell(rel_label), _cell(r.get("rationale") or "")))
    out.append("")
    return out


def write_nodes(g, out):
    nodes_dir = os.path.join(out, "nodes")
    os.makedirs(nodes_dir, exist_ok=True)
    for n in g.nodes:
        gid = n.get("group") or ""
        gname = g.group_by_id.get(gid, {}).get("name", gid)
        lines = ["# %s (%s)" % (n["name"], n.get("en") or "—"), "",
                 "- ID: `%s`" % n["id"],
                 "- 类型: %s" % TYPE_LABELS.get(n["type"], n["type"]),
                 "- 所属组: %s" % (("%s %s" % (gid, gname)).strip() or "—"),
                 "- 阶段: %s" % _stage_label(n.get("stage"))]
        if n.get("layer"):
            lines.append("- 层: %s" % LAYER_STYLE.get(n["layer"], {}).get("label", n["layer"]))
        if n.get("domain"):
            lines.append("- 域: %s" % n["domain"])
        if n.get("src"):
            lines.append("- 来源体系: %s" % n["src"])
        if n.get("cross_cutting"):
            lines.append("- 横切主题: %s" % "、".join(n["cross_cutting"]))
        if n.get("case"):
            lines.append("- 关联案例: %s" % "、".join(n["case"]))
        if n.get("version"):
            lines.append("- 版本: %s" % n["version"])
        if n.get("status"):
            lines.append("- 生命周期: %s" % n["status"])
        lines.append("")

        num = 0
        for block in derive_node_blocks(g, n):
            num += 1
            lines.append("## §%d %s" % (num, block["title"]))
            lines.append("")
            lines += _md_block(g, n, block)
        xref = _md_xref(g, n["id"])
        if xref:
            lines += ["## 附 对照资源 · 12factor 子库", ""]
            lines += xref
        lines += ["---", "",
                  "本页由 16-checkpoint/gen-md.py 生成；与 11-node-pages/%s.html 同源同序。" % n["id"], ""]
        with open(os.path.join(nodes_dir, n["id"] + ".md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def write_indexes(g, out):
    total = len(g.nodes)
    edges = len(g.edges)
    # 00-index
    lines = ["# %s · AI 友好索引" % g.cfg["title"], "",
             "节点 %d | 边 %d | 组 %d" % (total, edges, len(g.groups)), "",
             "## 节点总表", "",
             "| ID | 名称 | 类型 | 层 | 域 | 阶段 | 分组 | 定义 |",
             "|---|---|---|---|---|---|---|---|"]
    for n in g.nodes:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |"
                     % (n["id"], _cell(n["name"]), TYPE_LABELS.get(n["type"], n["type"]),
                        n.get("layer") or "—", n.get("domain") or "—", _stage_label(n.get("stage")),
                        n.get("group") or "—", _cell(n["definition"])))
    lines.append("")
    with open(os.path.join(out, "00-index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # 01-groups
    lines = ["# 分组索引", "", "| 分组 ID | 名称 | 类别 | 域 | 节点数 |", "|---|---|---|---|---|"]
    for gp in g.groups:
        lines.append("| %s | %s | %s | %s | %d |"
                     % (gp["id"], _cell(gp["name"]),
                        KIND_STYLE.get(gp.get("kind"), {}).get("label", gp.get("kind")),
                        _cell(gp.get("domain", "")), len(gp["node_ids"])))
    lines.append("")
    for gp in g.groups:
        lines += ["## %s %s" % (gp["id"], gp["name"]), ""]
        for nid in gp["node_ids"]:
            n = g.by_id.get(nid)
            if n:
                lines.append("- [%s] %s — %s" % (nid, n["name"], _cell(n["definition"])))
        lines.append("")
    with open(os.path.join(out, "01-groups.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # 02-stage
    lines = ["# 阶段视图", ""]
    for s in ["basic", "intermediate", "advanced"]:
        lines += ["## %s" % _stage_label(s), ""]
        for n in g.nodes:
            if n.get("stage") == s:
                lines.append("- [%s] %s (%s)" % (n["id"], n["name"], TYPE_LABELS.get(n["type"], n["type"])))
        lines.append("")
    with open(os.path.join(out, "02-stage.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # 03-learning-path
    all_ids = [n["id"] for n in g.nodes]
    lines = ["# 学习路径（prerequisite 拓扑序自动生成）", ""]
    if g.has_src and any(n.get("src") in ("app", "agent") for n in g.nodes):
        groups = [("路径 A：传统工程入门（app 体系）", [n["id"] for n in g.nodes if n.get("src") == "app"]),
                  ("路径 B：Agent 工程入门（agent 体系）", [n["id"] for n in g.nodes if n.get("src") == "agent"]),
                  ("路径 C：打通（全图谱）", all_ids)]
    else:
        groups = [("全局学习顺序", all_ids)]
        if g.has_layer:
            for l in LAYER_ORDER:
                ids = [n["id"] for n in g.nodes if n.get("layer") == l]
                if ids:
                    groups.append(("%s 层" % LAYER_STYLE.get(l, {}).get("label", l), ids))
    for title, ids in groups:
        lines += ["## %s" % title, ""]
        for i, nid in enumerate(topo_sort(ids, g.edges), 1):
            n = g.by_id.get(nid, {})
            lines.append("%d. [%s] %s" % (i, nid, n.get("name", nid)))
        lines.append("")
    with open(os.path.join(out, "03-learning-path.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    written = 4
    # 04-layer（有条件）
    if g.has_layer:
        lines = ["# 分层视图", ""]
        for l in LAYER_ORDER:
            ns = [n for n in g.nodes if n.get("layer") == l]
            if not ns:
                continue
            lines += ["## %s（%d）" % (LAYER_STYLE.get(l, {}).get("label", l), len(ns)), ""]
            for n in ns:
                lines.append("- [%s] %s — %s" % (n["id"], n["name"], _cell(n["definition"])))
            lines.append("")
        with open(os.path.join(out, "04-layer.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        written += 1

    # 05-cases（有条件）
    cases = [n for n in g.nodes if n.get("type") == "case"]
    if cases:
        lines = ["# 案例视图", "", "| 案例 | 概要 | 信源 |", "|---|---|---|"]
        for n in cases:
            lines.append("| %s | %s | %s |" % (n["id"], _cell(n["definition"]),
                                               "/".join(n.get("sources") or []) or "—"))
        lines.append("")
        with open(os.path.join(out, "05-cases.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        written += 1
    return written


def run(cfg):
    out = cfg["out_paths"]["md"]
    os.makedirs(out, exist_ok=True)
    g = build_graph(cfg)
    write_nodes(g, out)
    index_count = write_indexes(g, out)
    return {"kind": "md", "nodes": len(g.nodes), "indexes": index_count,
            "total": len(g.nodes) + index_count, "dir": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成 Markdown 镜像")
    add_common_args(ap)
    args = ap.parse_args(argv)
    res = run(config_from_args(args))
    print("md written: nodes=%d indexes=%d -> %s" % (res["nodes"], res["indexes"], res["dir"]))


if __name__ == "__main__":
    main()
