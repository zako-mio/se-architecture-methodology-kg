#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""normalize_gap_ids.py — 按 ADR-004 §决定三「ID 分配与冲突检测算法」归一化**新缺口**提案号

背景（实测）：
  阶段3 轨B 续做新增 3 本书后，`reverse-gaps.json` 由 60 增至 106 条。新缺口里带
  `target.proposed_node` 的条目有两类缺陷：
    (a) **撞号**：占用了 ADR-004 的 **T2 保留号**（如 `ESS-H-10` / `ESS-H-11` / `TEC-L-03`）；
        且新缺口之间也可能互相撞号。
    (b) **非法值**：`proposed_node` 填的是中文概念名而非 id。

作用域（**关键**）：
  只处理**未出现在 ADR-004 裁决表 `candidate_register` 中**的缺口。
  裁决表已覆盖的旧缺口，其 `proposed_node` 就是 ADR 的裁决结果（**保留号即占号登记，不是撞号**），
  一律跳过。（首版脚本曾误改旧 5 本、破坏 ADR 裁决，已回滚并加此守卫。）
  ⇒ 旧缺口的 `proposed_node` 回写（ADR §决定三「号释放与重指派政策」要求）
     属阶段3 的独立任务，本脚本不代劳。

判据（ADR-004 §决定三 规则 6）：
  可用号 = 未被图谱 `nodes[].id` 占用 **且** 未被 ADR 已登记提案（reserved / admitted）占用；
  从该（层，域）的**最小可用号**起分配。

产物：
  · 原地更新 `01-books/_verify/_parts/gaps-<slug>.json` 的 `target.proposed_node`（仅新缺口）
  · 重指派报告 `01-books/_verify/_meta/gap-id-reassignments.json`
  · 新缺口 T1/T2/T3 档位实测记录（ADR-004 §决定二 谓词）

确定性：无时间戳；排序稳定；`ensure_ascii=False, indent=2` + 末尾换行。
用法：python3 16-checkpoint/normalize_gap_ids.py [--check]
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
PARTS = os.path.join("01-books", "_verify", "_parts")
META = os.path.join("01-books", "_verify", "_meta")
DAG = os.path.join("10-dag-data", "methodology-dag.json")
ADR = os.path.join("18-design", "adr", "ADR-004.json")

NODE_RE = re.compile(r"^(ESS|MTH|TEC|CAS)-([A-Z]{1,2})-(\d{2})$")
# 非法值 → 层域归属（按概念性质显式登记；本轮仅 1 例）
LAYER_HINT = {"稳定性反模式体系": ("TEC", "K")}


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2) + "\n"


def parse_id(s):
    m = NODE_RE.match(s or "")
    return (m.group(1), m.group(2), int(m.group(3))) if m else None


def build_allocator(root):
    dag = load(os.path.join(root, DAG))
    used = {n["id"] for n in dag["nodes"]}
    adr = load(os.path.join(root, ADR))
    ia = adr["id_allocation_rule"]
    reserved = set(ia.get("reserved_ids_this_round") or [])
    admitted = set(ia.get("admitted_ids_this_round") or [])
    adr_gaps = set()
    for e in adr.get("candidate_register") or []:
        adr_gaps.update(e.get("gap_ids") or [])
    return used, reserved, admitted, adr_gaps


def main():
    ap = argparse.ArgumentParser(description="ADR-004 新缺口提案号归一化")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true", help="只报告，不写")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    used, reserved, admitted, adr_gaps = build_allocator(root)
    blocked = used | reserved | admitted

    gap_files = sorted(glob.glob(os.path.join(root, PARTS, "gaps-*.json")))
    allocations = {}
    reassignments = []
    per_file_changes = {}
    new_gaps = []          # (gap, slug, final_proposed)

    for gf in gap_files:
        doc = load(gf)
        slug = os.path.basename(gf)[len("gaps-"):-len(".json")]
        changed = 0
        for g in doc.get("gaps") or []:
            if g["gap_id"] in adr_gaps:
                continue                                   # 旧缺口：ADR 已裁决，跳过
            t = g.get("target") or {}
            pn = t.get("proposed_node")
            final = pn
            if pn:
                pid = parse_id(pn)
                need, reason = False, ""
                if pid is None:
                    need, reason = True, "非法值（非 id 形态）: %r" % pn
                elif pn in blocked:
                    need, reason = True, "撞号：%s 已被图谱/ADR 保留/已准入占用" % pn
                elif pn in allocations.get((pid[0], pid[1]), set()):
                    need, reason = True, "本轮内重复分配: %s" % pn
                if need:
                    if pid is not None:
                        pre, dom = pid[0], pid[1]
                    else:
                        pre, dom = LAYER_HINT.get(pn.split("（")[0].strip(), ("MTH", "O"))
                    taken = blocked | allocations.get((pre, dom), set())
                    n = 1
                    while "%s-%s-%02d" % (pre, dom, n) in taken:
                        n += 1
                    final = "%s-%s-%02d" % (pre, dom, n)
                    t["proposed_node"] = final
                    changed += 1
                    reassignments.append({
                        "gap_id": g["gap_id"], "book": slug, "from": pn, "to": final,
                        "reason": reason, "basis": "ADR-004 §决定三 规则 6（最小可用号）",
                    })
                    allocations.setdefault((pre, dom), set()).add(final)
                elif pid is not None:
                    allocations.setdefault((pid[0], pid[1]), set()).add(pn)
            new_gaps.append((g, slug, final))
        if changed:
            per_file_changes[gf] = (doc, changed)

    # ---- 档位实测（ADR-004 §决定二 谓词；每个新缺口 = 1 个概念）----
    print("=" * 88)
    print("ADR-004 新缺口提案号归一化 + 档位实测")
    print("=" * 88)
    print("\n[0] 作用域：新缺口 %d 条（ADR 裁决表已覆盖旧缺口 %d 条，跳过）"
          % (len(new_gaps), len(adr_gaps)))
    print("\n[1] 重指派（%d 条）" % len(reassignments))
    for r in reassignments:
        print("    %-14s %-12s %-42s → %-10s  %s"
              % (r["gap_id"], r["book"], r["from"][:42], r["to"], r["reason"]))

    print("\n[2] 档位实测")
    tiers = Counter()
    rows = []
    for g, slug, final in sorted(new_gaps, key=lambda x: x[0]["gap_id"]):
        t = g.get("target") or {}
        ev = g["evidence_strength"]
        if t.get("existing_node_id") and not t.get("proposed_node"):
            tier, why = "T3", "指向既有节点（补引），不触发结构扩展"
        elif ev != "direct":
            tier, why = "T3", "最强锚为 %s（<1 direct）" % ev
        elif t.get("proposed_node"):
            tier, why = "T2", "1 个独立信源 direct 锚 → 占号入候选册（不入图、不改计数）"
        else:
            tier, why = "T3", "无 proposed_node 且无 existing_node_id"
        tiers[tier] += 1
        rows.append((g["gap_id"], slug, g["kind"], ev, tier, final))
        print("    %-14s %-12s %-16s %-8s %-3s %s" % (g["gap_id"], slug, g["kind"], ev, tier, final or "—"))
        print("        → %s" % why)
    print("\n    档位分布：%s" % dict(sorted(tiers.items())))
    props = [r for r in rows if r[5]]
    print("    其中带 proposed_node（提案新节点，占号入候选册）= %d 条" % len(props))
    print("    仅补引（existing_node_id 非空）= %d 条"
          % sum(1 for g, s, f in new_gaps if (g.get('target') or {}).get('existing_node_id')
                and not (g.get('target') or {}).get('proposed_node')))

    if not args.check:
        for gf, (doc, n) in per_file_changes.items():
            with open(gf, "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(doc))
            print("\n    wrote %s（%d 处重指派）" % (os.path.relpath(gf, root), n))
        rep = {
            "schema_version": "1.0.0",
            "scope": "仅 ADR-004 裁决表未覆盖的新缺口；旧缺口 proposed_node 为 ADR 裁决值，跳过",
            "basis": "ADR-004 §决定三（ID 分配与冲突检测算法）规则 6 + 号释放政策",
            "blocked_ids": sorted(blocked),
            "reassignments": reassignments,
            "tier_distribution": dict(sorted(tiers.items())),
            "new_gap_count": len(new_gaps),
            "proposed_node_count": len(props),
        }
        os.makedirs(os.path.join(root, META), exist_ok=True)
        rp = os.path.join(root, META, "gap-id-reassignments.json")
        with open(rp, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(rep))
        print("    wrote %s" % os.path.relpath(rp, root))
    else:
        print("\n    [--check] 未落盘")

    # 复验：新缺口无非法/撞号残留
    bad = []
    for g, slug, final in new_gaps:
        pn = (g.get("target") or {}).get("proposed_node")
        if pn:
            if parse_id(pn) is None:
                bad.append((g["gap_id"], "非法", pn))
            elif pn in blocked:
                bad.append((g["gap_id"], "撞号", pn))
    dup = [k for k, v in Counter((g["target"] or {}).get("proposed_node") for g, s, f in new_gaps
                                 if (g["target"] or {}).get("proposed_node")).items() if v > 1]
    print("\n[3] 复验：新缺口非法/撞号残留 = %d %s；新缺口间重复号 = %s" % (len(bad), bad[:5], dup))
    ok = not bad and not dup
    print("\n== 结果 = %s ==" % ("PASS" if ok else "FAIL"))
    print("=" * 88)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
