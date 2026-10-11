#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_densify_briefs.py — 为阶段2 证据展开（W1）与节点改写（W2）生成子Agent 生产简报。

产出（全部落在私有 _densify/_briefs/，不公开）：
  _briefs/evidence-<slug>.md      每本书一份：该书全部 ledger 记录（含锚点）+ 任务说明
  _briefs/write-<node_id>.md      每个参与节点一份：现五段正文 + 落点 + 证据素材索引

用法：
  python3 16-checkpoint/gen_densify_briefs.py            # 生成全部
  python3 16-checkpoint/gen_densify_briefs.py --kind evidence
  python3 16-checkpoint/gen_densify_briefs.py --kind write
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

DENSIFY = os.path.join("01-books", "_verify", "_densify")
BRIEFS = os.path.join(DENSIFY, "_briefs")

SLUG_SOURCE = {"ddia": "BK-023", "clean-architecture": "BK-007", "saip": "BK-009"}
SLUG_BOOK = {"ddia": "Designing Data-Intensive Applications（数据密集型应用系统设计，中文版）",
             "clean-architecture": "Clean Architecture（架构整洁之道）",
             "saip": "Software Architecture in Practice, 4th ed."}
SLUG_CORPUS = {
    "ddia": "01-books/_files/P0-11/ddia-zh-src/*.md（25 个中文全文 MD）",
    "clean-architecture": "01-books/_verify/_text/clean-architecture.txt（536KB 抽文本）",
    "saip": "01-books/_verify/_text/saip.txt（1069KB 抽文本）",
}
SEGMENTS = ("definition", "principle", "mechanism", "engineering", "tradeoff")


def load(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return json.load(f)


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def body_of(node):
    d = node.get("detail") or {}
    return {"definition": node.get("definition", "") or "",
            **{k: d.get(k, "") or "" for k in SEGMENTS[1:]}}


def gen_evidence(root):
    ledger = load(root, os.path.join("01-books", "_verify", "verification-ledger.json"))
    pre = load(root, os.path.join(DENSIFY, "precheck-coverage.json"))
    plan = set(pre["nodes"].keys())
    out = []
    for slug, src in SLUG_SOURCE.items():
        recs = [r for r in ledger["records"] if r["source_id"] == src and r["node_id"] in plan]
        recs.sort(key=lambda r: (r["node_id"], r["claim_id"]))
        by_node = {}
        for r in recs:
            by_node.setdefault(r["node_id"], []).append(r)
        lines = []
        lines.append("# W1 证据展开简报 · %s（`%s`）\n" % (SLUG_BOOK[slug], slug))
        lines.append("- **source_id**：`%s`" % src)
        lines.append("- **语料路径**：`%s`" % SLUG_CORPUS[slug])
        lines.append("- **本书记录**：%d 条，覆盖参与节点 %d 个" % (len(recs), len(by_node)))
        lines.append("- **产出文件**：`01-books/_verify/_densify/evidence-%s.json`（**只写这一个文件**）\n" % slug)
        lines.append("## 任务\n")
        lines.append("对下表每条既有 claim，读**其锚点章节 + 一跳上下文**，产出 1 条 `items[]` 素材条目：")
        lines.append("把该 claim 展开为**可支撑节点正文的素材**（机制细节 / 权衡 / 反例 / 适用边界），")
        lines.append("并标注 `is_new`（是否超出该 claim 已覆盖的范围）。\n")
        lines.append("**硬约束**：`text` 必须为**改写**（非引文），与书原文最长公共子串 **≤20 字**；")
        lines.append("`read_scope` 必须如实记录你实际读了哪些章节/页段。\n")
        lines.append("## 记录清单\n")
        for node_id in sorted(by_node):
            info = pre["nodes"][node_id]
            lines.append("### `%s`（基线 %s 字，缺段：%s）\n"
                         % (node_id, info["baseline_chars"],
                            ", ".join(info["missing_segments"]) or "无"))
            for r in by_node[node_id]:
                a = r.get("anchor") or {}
                lines.append("- `%s` ｜origin=%s ｜强度=%s ｜方向=%s"
                             % (r["claim_id"], r["claim_id"].split("#")[1], r["evidence_strength"], r["direction"]))
                lines.append("  - 锚点：第 %s 章 / %s 节 · %s" % (a.get("chapter"), a.get("section") or "-", a.get("section_title") or "-"))
                lines.append("  - 既有 claim：%s" % r["claim"])
                lines.append("  - 既有证据说明：%s" % (r.get("evidence_note") or "-"))
            lines.append("")
        lines.append("## 产出 JSON 结构（严格照抄字段名）\n")
        lines.append("```json")
        lines.append(json.dumps({
            "meta": {"schema_version": "1.0.0", "book_source_id": src, "slug": slug,
                     "review_date": "2026-09-11", "note": "素材分片；只增不改既有账本"},
            "items": [{
                "evidence_id": "EV-%s-001" % slug.upper().replace("-", "")[:4],
                "node_id": "<上表节点 id>",
                "origin": "<definition|principle|mechanism|engineering|tradeoff|errata>",
                "claim_id": "<上表 claim_id>",
                "is_new": False,
                "text": "<改写素材，≤20 字公共子串>",
                "anchor": {"chapter": "<章>", "section": "<节，可空>", "section_title": "<标题>"},
                "proposed_strength": "<direct|partial|inferred|contradicted>",
                "read_scope": "<实际阅读范围>"
            }]
        }, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("\n> `evidence_id` 用 `EV-%s-<3位序号>`，分片内唯一。" % slug.upper().replace("-", "")[:4])
        out.append(write(root, os.path.join(BRIEFS, "evidence-%s.md" % slug), "\n".join(lines) + "\n"))
    return out


def gen_write(root):
    pre = load(root, os.path.join(DENSIFY, "precheck-coverage.json"))
    content = load(root, os.path.join("10-dag-data", "node-content.json"))
    sections = {e["id"]: e.get("sections", {}) for e in content["node_contents"]}
    out = []
    for node_id in sorted(pre["nodes"]):
        info = pre["nodes"][node_id]
        sec = sections.get(node_id, {})
        lines = []
        lines.append("# W2 节点改写简报 · `%s`\n" % node_id)
        lines.append("- **基线字数**：%s ｜ **目标**：2400–3000 字" % info["baseline_chars"])
        lines.append("- **层**：%s ｜ **域**：%s" % (info.get("layer"), info.get("domain")))
        lines.append("- **正文落点**：`%s`" % info["body_shard"])
        lines.append("- **claims 落点**：`_verify/_parts/claims-%s.json`（%s）"
                     % (info["claims_target_slug"], info["claims_action"]))
        lines.append("- **缺段**：%s" % (", ".join(info["missing_segments"]) or "无"))
        lines.append("- **既有主张**：%d 条（上限 16，ADR-003）｜ **direct 锚**：%d 条"
                     % (info["claims_total"], info["ledger_direct"]))
        lines.append("- **产出文件**：`01-books/_verify/_densify/write-%s.json`（**只写这一个文件**）\n" % node_id)
        lines.append("## 当前五段正文\n")
        for s in SEGMENTS:
            lines.append("### %s（%d 字）\n" % (s, len(sec.get(s, "") or "")))
            lines.append(sec.get(s, "") or "（空）")
            lines.append("")
        lines.append("## 可用证据素材\n")
        lines.append("读 `01-books/_verify/_densify/evidence-*.json`，筛出 `node_id == \"%s\"` 的条目。" % node_id)
        lines.append("（若某书尚未产出素材，则该节点证据不完整——**不要编造**，在 `warnings` 中说明。）\n")
        lines.append("## 改写要求\n")
        lines.append("1. **五段全部重写**为 2400–3000 字总量，深化而非灌水；每段必须有 `provenance`（引用 `evidence_id`）。")
        lines.append("2. **不得越出素材范围**：引入素材未支持的新实质表述 → 必须同时落 `new_claims`。")
        lines.append("3. `essence` 层正文**禁出现工具名/版本号**；`technology` 层须保留 `version`。")
        lines.append("4. 每段 ≥1 条 provenance；`ceil(字数增量/200) ≤ provenance 引用的 distinct claim_id 数`。")
        lines.append("5. 单节点主张总数（既有 + 新增）**≤16 条**（ADR-003）。\n")
        lines.append("## 产出 JSON 结构（严格照抄字段名）\n")
        lines.append("```json")
        lines.append(json.dumps({
            "node_id": node_id,
            "segments": {s: "<改写后正文>" for s in SEGMENTS},
            "provenance": {s: ["EV-XXXX-001"] for s in SEGMENTS},
            "new_claims": [{"claim_id": "%s#mechanism#1" % node_id, "text": "<改写，≤20 字公共子串>",
                            "anchor": {"chapter": "<章>", "section": "<节>", "section_title": "<标题>"},
                            "evidence_strength": "direct", "direction": "forward"}],
            "baseline_chars": info["baseline_chars"], "final_chars": 2600,
            "writer": "w-nodewriter-b?", "review_date": "2026-09-11"
        }, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("\n> 新增 claim 的 `claim_id` 用 `<node_id>#<origin>#<n>`，`n` 从**既有最大序号 +1** 起。")
        out.append(write(root, os.path.join(BRIEFS, "write-%s.md" % node_id), "\n".join(lines) + "\n"))
    return out


def main():
    ap = argparse.ArgumentParser(description="生成阶段2 生产简报")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--kind", default="all", choices=["all", "evidence", "write"])
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    made = []
    if args.kind in ("all", "evidence"):
        made += gen_evidence(root)
    if args.kind in ("all", "write"):
        made += gen_write(root)
    for p in made:
        print("[out] %s" % os.path.relpath(p, root))
    print("[done] %d 份简报" % len(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
