#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""backfill_candidate_register.py — 按「修订型 ADR」把补录条目并入 ADR-004 候选册

背景（实测）：`reverse-gaps.json` 中 16 条缺口的 `target.proposed_node` 不在
ADR-004 `candidate_register` 内 ⇒ ①11 条触发 `validate_staging_shards` 的 WARN；
②5 条仅由 `_meta/gap-id-reassignments.json`（重指派台账）静默、无正式档位；
③`replay_admission --scan-promotion` 把它们列为 `new_proposal_unaudited`。
补录即消：下游脚本（`writeback_gap_ids` / `validate_staging_shards` / `replay_admission`）
一律以 `ADR-004.json.candidate_register` 为唯一真相源，故补录后无需改任何读取口径。

数据流：修订型 ADR（如 `ADR-006.json`）的 `backfill_entries` + `id_allocation_delta`
        → 并入 `ADR-004.json`（candidate_register / id_allocation_rule / amended_by）
        → 报告 `01-books/_verify/_meta/adr-register-backfill.json`

fail-closed 校验（任一不过即拒写）：
  · 修订件的 `backfill_entries` 非空数组，每条含必需字段；`tier ∈ {T1,T2,T3}`
  · `id_status ∈ KEEP ∪ DROP`；KEEP ⇒ `id` 合法 id 形态、层前缀一致、未被图谱占用、
    且未被其它候选册条目占用；DROP ⇒ `id` 必须为 null
  · `gap_id` 必须真实存在于 `reverse-gaps.json`
  · 与既有候选册的 gap_id / id 不得重复（幂等：完全一致时判 no-op）

确定性：无时间戳；UTF-8 无 BOM；`ensure_ascii=False, indent=2` + 末尾换行。
用法：
  python3 16-checkpoint/backfill_candidate_register.py --amendment 18-design/adr/ADR-006.json --check
  python3 16-checkpoint/backfill_candidate_register.py --amendment 18-design/adr/ADR-006.json
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

ADR_TARGET = os.path.join("18-design", "adr", "ADR-004.json")
DAG = os.path.join("10-dag-data", "methodology-dag.json")
GAPS = os.path.join("01-books", "_verify", "reverse-gaps.json")
META = os.path.join("01-books", "_verify", "_meta")
OUT_REPORT = os.path.join(META, "adr-register-backfill.json")

KEEP_PROPOSED = {"admit-now", "reserved", "reserved-after-collision", "newly-allocated"}
DROP_PROPOSED = {"released", "no-id"}
TIERS = ("T1", "T2", "T3")

NODE_RE = re.compile(r"^(ESS|MTH|TEC|CAS)-([A-Z]{1,2})-(\d{2})$")
PREFIX_BY_LAYER = {"essence": "ESS", "methodology": "MTH", "technology": "TEC", "case": "CAS"}
GROUP_BY_LAYER = {"essence": "GL-ESSENCE", "methodology": "GL-METHOD",
                  "technology": "GL-TECHNOLOGY", "case": "GL-CASE"}

REQUIRED_ENTRY = ("gap_id", "concept", "tier", "id", "id_status", "layer", "domain",
                  "book_source_id", "evidence", "independent_sources", "reason_code", "action")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2) + "\n"


def main():
    ap = argparse.ArgumentParser(description="补录修订型 ADR 的候选册条目进 ADR-004")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--amendment", required=True, help="修订型 ADR（含 backfill_entries）")
    ap.add_argument("--target", default=ADR_TARGET)
    ap.add_argument("--check", action="store_true", help="只报告，不写")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    amd_path = args.amendment if os.path.isabs(args.amendment) else os.path.join(root, args.amendment)
    tgt_path = args.target if os.path.isabs(args.target) else os.path.join(root, args.target)

    amd = load(amd_path)
    tgt = load(tgt_path)
    dag = load(os.path.join(root, DAG)) if os.path.isfile(os.path.join(root, DAG)) else {"nodes": []}
    gapdoc = load(os.path.join(root, GAPS)) if os.path.isfile(os.path.join(root, GAPS)) else {"gaps": []}

    problems = []
    entries = amd.get("backfill_entries")
    if not isinstance(entries, list) or not entries:
        problems.append("修订件 backfill_entries 缺失或为空")
        entries = []

    gap_ids_known = {g.get("gap_id") for g in (gapdoc.get("gaps") or [])}
    node_ids = {n.get("id") for n in (dag.get("nodes") or [])}
    reg = tgt.get("candidate_register") or []
    reg_gap_ids = {}
    reg_ids = {}
    for i, e in enumerate(reg, 1):
        for gid in e.get("gap_ids") or []:
            reg_gap_ids[gid] = i
        if e.get("id"):
            reg_ids.setdefault(e["id"], i)

    delta = amd.get("id_allocation_delta") or {}
    reserved_added = list(delta.get("reserved_added") or [])
    released_removed = list(delta.get("released_removed") or [])
    reassignment_added = list(delta.get("reassignment_map_added") or [])
    released_removed_set = set(released_removed)

    new_entries = []
    seen_gap, seen_id = {}, {}
    reused_released = []
    for e in entries:
        gid = e.get("gap_id")
        for k in REQUIRED_ENTRY:
            if k not in e:
                problems.append("%s 缺字段 %s" % (gid, k))
        if e.get("tier") not in TIERS:
            problems.append("%s tier 非法: %r" % (gid, e.get("tier")))
        status = e.get("id_status")
        if status not in (KEEP_PROPOSED | DROP_PROPOSED):
            problems.append("%s id_status 非法: %r" % (gid, status))
            continue
        if gid not in gap_ids_known:
            problems.append("%s 不存在于 reverse-gaps.json" % gid)
        if gid in reg_gap_ids:
            if status in KEEP_PROPOSED and e.get("id") not in reg_ids:
                problems.append("%s 已在候选册第 %d 条且号不同（须人工裁决）" % (gid, reg_gap_ids[gid]))
            continue
        if gid in seen_gap:
            problems.append("%s 在修订件内重复" % gid)
        seen_gap[gid] = True

        if status in KEEP_PROPOSED:
            nid = e.get("id")
            m = NODE_RE.match(nid or "")
            if not m:
                problems.append("%s 保留号非法形态: %r" % (gid, nid))
            else:
                want = PREFIX_BY_LAYER.get(e.get("layer"))
                if want and m.group(1) != want:
                    problems.append("%s 号 %s 与层 %s 前缀不一致" % (gid, nid, e.get("layer")))
                if nid in node_ids:
                    problems.append("%s 号 %s 已被图谱节点占用" % (gid, nid))
                if nid in reg_ids:
                    prev = reg[reg_ids[nid] - 1]
                    if prev.get("id_status") in DROP_PROPOSED and nid in released_removed_set:
                        # 号释放政策明文：仅存在于旧缺口文件的号允许「被后续提案补洞」。
                        # 该号必须同时出现在修订件的 released_removed 中（显式回收留痕）。
                        reused_released.append({
                            "id": nid,
                            "gap_id": gid,
                            "prev_concept": prev.get("concept"),
                            "prev_gap_ids": prev.get("gap_ids"),
                            "basis": "ADR-004 号释放政策「可被后续提案补洞」+ 修订件 "
                                     "id_allocation_delta.released_removed 显式回收",
                        })
                    else:
                        problems.append("%s 号 %s 已被候选册第 %d 条占用（id_status=%r）"
                                        % (gid, nid, reg_ids[nid], prev.get("id_status")))
                if nid in seen_id:
                    problems.append("%s 号 %s 在修订件内重复" % (gid, nid))
                seen_id[nid] = True
        else:
            if e.get("id") is not None:
                problems.append("%s id_status=%s 但 id 非 null" % (gid, status))

        new_entries.append({
            "concept": e.get("concept"),
            "tier": e.get("tier"),
            "id": e.get("id"),
            "id_status": status,
            "layer": e.get("layer"),
            "domain": e.get("domain"),
            "group": e.get("group") or GROUP_BY_LAYER.get(e.get("layer")),
            "gap_ids": [gid],
            "books": [e.get("book_source_id")],
            "evidence": e.get("evidence"),
            "independent_sources": e.get("independent_sources"),
            "reason_code": e.get("reason_code"),
            "action": e.get("action"),
            "amended_by": amd.get("id"),
            "origin_gap": gid,
            "cit_trace": e.get("cit_trace"),
        })

    for rid in reserved_added:
        if not NODE_RE.match(rid or ""):
            problems.append("reserved_added 号非法形态: %r" % rid)
        if rid in node_ids:
            problems.append("reserved_added 号 %s 已被图谱占用" % rid)

    # released_removed 必须是候选册中「已释放」的号（否则回收集合语义被误用）
    for rid in released_removed:
        idx = reg_ids.get(rid)
        if idx is None or reg[idx - 1].get("id_status") not in DROP_PROPOSED:
            problems.append("released_removed 中的 %s 不是候选册中的已释放号" % rid)

    if problems:
        print("=" * 78)
        print("候选册补录 —— fail-closed 拒写")
        print("=" * 78)
        for p in problems:
            print("    ! %s" % p)
        print("\n== 结果 = FAIL（问题 %d 条，未落盘）==" % len(problems))
        return 1

    noop = not new_entries and not reserved_added and not released_removed and not reassignment_added
    print("=" * 78)
    print("候选册补录：%s → %s" % (os.path.relpath(amd_path, root), os.path.relpath(tgt_path, root)))
    print("=" * 78)
    print("\n[1] 新增条目 %d 条" % len(new_entries))
    for e in new_entries:
        print("    %-14s %-3s %-11s %-22s %s"
              % (e["origin_gap"], e["tier"], e["id"] or "—", e["concept"][:22], e["reason_code"]))
    print("\n[2] 号表增量：reserved +%d ｜ released 回收 %d ｜ 重指派 +%d"
          % (len(reserved_added), len(released_removed), len(reassignment_added)))
    for r in released_removed:
        print("    ~ 号 %s：由 released 收回为 reserved" % r)
    for r in reused_released:
        print("    ~ 号 %s：释放号复用 —— 原属『%s』（%s）⇒ 本轮由 %s 重新占用"
              % (r["id"], str(r["prev_concept"])[:18], ",".join(r["prev_gap_ids"] or []), r["gap_id"]))
    for r in reassignment_added:
        print("    ~ 号 %s ← %s" % (r.get("id"), str(r.get("from_concept"))[:44]))

    if noop:
        print("\n[3] 判 no-op（修订件内容已在候选册中），不落盘")
        print("\n== 结果 = PASS（no-op）==")
        return 0

    if args.check:
        print("\n[3] [--check] 未落盘")
        print("\n== 结果 = PASS（仅报告）==")
        return 0

    # ---- 落盘 ----
    reg_before = len(reg)
    tgt["candidate_register"] = reg + new_entries

    ia = tgt.setdefault("id_allocation_rule", {})
    reserved = list(ia.get("reserved_ids_this_round") or [])
    for rid in reserved_added:
        if rid not in reserved:
            reserved.append(rid)
    ia["reserved_ids_this_round"] = sorted(set(reserved))

    released = [r for r in (ia.get("released_ids_this_round") or []) if r not in released_removed]
    ia["released_ids_this_round"] = released

    rmap = list(ia.get("reassignment_map") or [])
    have = {r.get("id") for r in rmap}
    for r in reassignment_added:
        if r.get("id") not in have:
            rmap.append(r)
    ia["reassignment_map"] = rmap

    ab = list(tgt.get("amended_by") or [])
    if amd.get("id") not in ab:
        ab.append(amd.get("id"))
    tgt["amended_by"] = ab

    with open(tgt_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(dumps(tgt))

    report = {
        "schema_version": "1.0.0",
        "basis": "%s 的 backfill_entries + id_allocation_delta 并入 %s"
                 % (amd.get("id"), os.path.basename(tgt_path)),
        "amendment": amd.get("id"),
        "entries_added": len(new_entries),
        "register_entries_before": reg_before,
        "register_entries_after": len(tgt["candidate_register"]),
        "reserved_added": reserved_added,
        "released_removed": released_removed,
        "released_reuse": reused_released,
        "reassignment_map_added": reassignment_added,
        "entries": new_entries,
    }
    os.makedirs(os.path.join(root, META), exist_ok=True)
    rp = os.path.join(root, OUT_REPORT)
    with open(rp, "w", encoding="utf-8", newline="\n") as f:
        f.write(dumps(report))

    print("\n[3] wrote %s（%d → %d 条）"
          % (os.path.relpath(tgt_path, root), reg_before, len(tgt["candidate_register"])))
    print("    wrote %s" % os.path.relpath(rp, root))
    print("\n== 结果 = PASS ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
