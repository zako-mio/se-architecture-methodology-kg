#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
writeback_gap_ids.py — 按 ADR-004 裁决表回写**旧缺口**的 `target.proposed_node`

依据：ADR-004 §决定三「号释放与重指派政策」——
  「已进入图谱或公开工件（已成为契约一部分）⇒ 永不复用（void）；
    仅存在于本 ADR 正在取代的缺口文件中 ⇒ 允许带映射重指派（候选册记 reassignment_map），
    并要求阶段3 回写缺口文件的 `target.proposed_node` 使之一致」

作用域（fail-closed）：
  · 只处理**出现在 ADR-004 `candidate_register` 中**的缺口（裁决表覆盖集）；
  · 未覆盖的缺口（含本轮新增提案）**一律不动**，仅在报告中列出计数；
  · 逐条唯一判定源 = 裁决表的 `id_status`，不做任何语义再裁决。

回写规则（唯一判定源：`candidate_register[].id_status`）：
  · `admit-now` / `reserved` / `reserved-after-collision` / `newly-allocated`
      ⇒ `proposed_node = register.id`
  · `released` / `no-id`
      ⇒ `proposed_node = null`；**仅当** `existing_node_id` 为空时，从 `action` 取宿主填入
        （G-V1 硬校验要求 `target` 不得双空，故必须补宿主）
  · 其他/未知 `id_status` ⇒ 拒绝落盘并报错（不静默放过）

性质：确定性（无时间戳）、UTF-8 无 BOM、末尾换行、稳定排序；
      只写私有层 `01-books/_verify/_parts/gaps-*.json` 与 `_meta/gap-id-writeback.json`。

用法：
  python3 16-checkpoint/writeback_gap_ids.py --check     # 只报告差集，不写
  python3 16-checkpoint/writeback_gap_ids.py             # 落盘
"""
import argparse
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

ADR_REL = os.path.join("18-design", "adr", "ADR-004.json")
PARTS = os.path.join("01-books", "_verify", "_parts")
META = os.path.join("01-books", "_verify", "_meta")
OUT_REPORT = os.path.join(META, "gap-id-writeback.json")

# 裁决表 id_status → 是否保留提案号
KEEP_PROPOSED = {"admit-now", "reserved", "reserved-after-collision", "newly-allocated"}
DROP_PROPOSED = {"released", "no-id"}

NODE_RE = re.compile(r"^(ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2}$")


def resolve(root, *parts):
    p = os.path.join(*parts)
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def host_from_action(action):
    """从 ADR `action` 正文取宿主节点 id（形如「宿主 MTH-N-06 …」「宿主 ESS-H-02 …」）。

    仅取第一个出现的节点 id；取不到返回 None（此时若原 existing_node_id 也为空，
    调用方会 fail-closed 报错，不静默写入双空 target）。
    """
    if not action:
        return None
    # 优先「宿主 X」之后的首个 id
    m = re.search(r"宿主\s*((?:ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2})", action)
    if m:
        return m.group(1)
    m = re.search(r"((?:ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2})", action)
    return m.group(1) if m else None


def build_register(adr):
    """gap_id → 裁决条目。"""
    reg = {}
    for e in adr.get("candidate_register") or []:
        for gid in e.get("gap_ids") or []:
            reg[gid] = e
    return reg


def main():
    ap = argparse.ArgumentParser(description="按 ADR-004 裁决表回写旧缺口 proposed_node")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--adr", default=None)
    ap.add_argument("--check", action="store_true", help="只报告，不写")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    adr_path = args.adr or resolve(root, ADR_REL)
    adr = load(adr_path)
    reg = build_register(adr)

    print("=" * 88)
    print("ADR-004 旧缺口 proposed_node 回写")
    print("  ADR   = %s" % os.path.relpath(adr_path, root))
    print("  作用域 = 裁决表覆盖的缺口（%d 条）" % len(reg))
    print("=" * 88)

    rows = []
    problems = []
    per_file = {}
    covered_seen = set()
    uncovered = 0

    for gf in sorted(glob.glob(resolve(root, PARTS, "gaps-*.json"))):
        doc = load(gf)
        slug = os.path.basename(gf)[len("gaps-"):-len(".json")]
        changed = 0
        for g in doc.get("gaps") or []:
            gid = g.get("gap_id")
            if gid not in reg:
                uncovered += 1
                continue
            covered_seen.add(gid)
            e = reg[gid]
            status = e.get("id_status")
            tgt = g.get("target")
            if not isinstance(tgt, dict):
                problems.append("%s target 非对象" % gid)
                continue
            before = tgt.get("proposed_node")
            before_ex = tgt.get("existing_node_id")
            rid = e.get("id")

            if status in KEEP_PROPOSED:
                if rid is None:
                    problems.append("%s id_status=%s 但裁决表 id 为空（裁决表自相矛盾）" % (gid, status))
                    continue
                after = rid
                after_ex = before_ex
            elif status in DROP_PROPOSED:
                after = None
                after_ex = before_ex
                if not after_ex:
                    host = host_from_action(e.get("action"))
                    if host is None or not NODE_RE.match(host):
                        problems.append("%s id_status=%s 且无 existing_node_id，"
                                        "action 中亦取不到合法宿主 ⇒ 将造成 target 双空（G-V1）"
                                        % (gid, status))
                        continue
                    after_ex = host
            else:
                problems.append("%s 未知 id_status=%r（拒绝落盘）" % (gid, status))
                continue

            if not (after or after_ex):
                problems.append("%s 回写后 target 双空（G-V1 硬校验）" % gid)
                continue

            changed_here = (before != after) or (before_ex != after_ex)
            rows.append({
                "gap_id": gid,
                "slug": slug,
                "book_source_id": g.get("book_source_id"),
                "register_id": rid,
                "id_status": status,
                "tier": e.get("tier"),
                "before": {"proposed_node": before, "existing_node_id": before_ex},
                "after": {"proposed_node": after, "existing_node_id": after_ex},
                "basis": "ADR-004 §决定三（号释放与重指派政策）",
                "changed": changed_here,
            })
            if changed_here:
                tgt["proposed_node"] = after
                tgt["existing_node_id"] = after_ex
                changed += 1
        if changed:
            per_file[gf] = (doc, changed)

    missing = sorted(set(reg) - covered_seen)

    print("\n[1] 裁决表覆盖缺口：命中 %d / 裁决表 %d；缺失 %d %s"
          % (len(covered_seen), len(reg), len(missing), missing[:8]))
    print("    未覆盖缺口（不动）= %d 条" % uncovered)

    print("\n[2] 需变更条目（%d 条）" % sum(1 for r in rows if r["changed"]))
    for r in rows:
        if not r["changed"]:
            continue
        print("    %-14s %-18s %-24s %s → %s | ex %s → %s"
              % (r["gap_id"], r["slug"], r["id_status"],
                 repr(r["before"]["proposed_node"]), repr(r["after"]["proposed_node"]),
                 repr(r["before"]["existing_node_id"]), repr(r["after"]["existing_node_id"])))

    unchanged = sum(1 for r in rows if not r["changed"])
    print("\n[3] 已一致（无需变更）= %d 条" % unchanged)

    print("\n[4] 写前硬校验（target 双空 / 未知状态 / 裁决表自相矛盾）：问题 %d" % len(problems))
    for p in problems[:20]:
        print("    ! %s" % p)

    if problems:
        print("\n  == 结果 = FAIL（拒绝落盘；请先修裁决表或脚本规则） ==")
        return 1

    if args.check:
        print("\n    [--check] 未落盘")
    else:
        for gf, (doc, n) in sorted(per_file.items()):
            with open(gf, "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(doc))
            print("    wrote %s（%d 处）" % (os.path.relpath(gf, root), n))
        report = {
            "schema_version": "1.0.0",
            "scope": "仅 ADR-004 裁决表覆盖的缺口；未覆盖缺口（含新增提案）一律不动",
            "basis": "ADR-004 §决定三 号释放与重指派政策",
            "register_covered": len(reg),
            "register_missing": missing,
            "uncovered_untouched": uncovered,
            "changed": sum(1 for r in rows if r["changed"]),
            "unchanged": unchanged,
            "entries": sorted(rows, key=lambda x: x["gap_id"]),
        }
        os.makedirs(resolve(root, META), exist_ok=True)
        rp = resolve(root, OUT_REPORT)
        with open(rp, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(report))
        print("    wrote %s" % os.path.relpath(rp, root))

    print("\n  == 结果 = PASS ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
