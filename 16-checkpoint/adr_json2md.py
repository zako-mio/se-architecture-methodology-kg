#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
adr_json2md.py — 把 ADR JSON 渲染为 Markdown（与 ADR-001/002 体例一致）

用法：
  python3 16-checkpoint/adr_json2md.py --input 18-design/adr/ADR-003.json
"""
import argparse
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    d = json.load(io.open(args.input, encoding="utf-8"))
    out = args.out or os.path.splitext(args.input)[0] + ".md"

    L = []
    L.append("# %s · %s\n" % (d["id"], d["title"]))
    L.append("> 状态：**%s** ｜ 机检：`gate_architecture.py --kind adr --input %s`"
             % (d["status"], os.path.basename(args.input)))
    if d.get("graph_refs"):
        L.append("> 图谱依据：%s" % " / ".join("`%s`" % x for x in d["graph_refs"]))
    if d.get("standards_refs"):
        L.append("> 选型标尺（仅 `standards_refs`）：%s" % " / ".join("`%s`" % x for x in d["standards_refs"]))
    if d.get("sources"):
        L.append("> 信源：%s" % " / ".join("`%s`" % x for x in d["sources"]))
    L.append("")

    L.append("## 1. 背景与约束（Context）\n")
    L.append(d["context"]); L.append("")

    L.append("## 2. 质量属性场景（Quality Scenarios）\n")
    for i, q in enumerate(d.get("quality_scenarios", []), 1):
        L.append("**S%d**" % i)
        L.append("- 刺激：%s" % q.get("stimulus", ""))
        L.append("- 响应：%s" % q.get("response", ""))
        L.append("- 度量：%s" % q.get("measure", ""))
        L.append("")

    L.append("## 3. 备选方案（Options）\n")
    for i, o in enumerate(d.get("options", []), 1):
        L.append("### %d. %s\n" % (i, o.get("name", "")))
        L.append(o.get("description", "")); L.append("")
        L.append("**优点**")
        for x in o.get("pros", []):
            L.append("- %s" % x)
        L.append("")
        L.append("**代价**")
        for x in o.get("cons", []):
            L.append("- %s" % x)
        L.append("")

    L.append("## 4. 决策（Decision）\n")
    L.append(d["decision"]); L.append("")

    L.append("## 5. 理由（Rationale）\n")
    L.append(d["rationale"]); L.append("")

    c = d.get("consequences", {}) or {}
    L.append("## 6. 后果（Consequences）\n")
    for key, label in (("positive", "正面"), ("negative", "负面"), ("risks", "风险")):
        items = c.get(key) or []
        if items:
            L.append("**%s**" % label)
            for x in items:
                L.append("- %s" % x)
            L.append("")

    if d.get("sensitive_points"):
        L.append("## 7. 敏感点（Sensitive Points）\n")
        for x in d["sensitive_points"]:
            L.append("- %s" % x)
        L.append("")
    if d.get("tradeoff_points"):
        L.append("## 8. 权衡点（Tradeoff Points）\n")
        for x in d["tradeoff_points"]:
            L.append("- %s" % x)
        L.append("")
    if d.get("reversal_cost"):
        L.append("## 9. 回退条件与成本（Reversal Cost）\n")
        L.append(d["reversal_cost"]); L.append("")

    io.open(out, "w", encoding="utf-8").write("\n".join(L).rstrip() + "\n")
    print("[out] %s (%d bytes)" % (out, os.path.getsize(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
