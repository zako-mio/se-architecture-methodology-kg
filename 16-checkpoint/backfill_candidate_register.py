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
        → 报告 `01-books/_verify/_meta/adr-register-backfill-<adrNNN>.json`（**按修订件留存**）
        → 索引 `01-books/_verify/_meta/adr-register-backfill.json`（`kind=index`，含全部报告清单）

报告留存的修正（2026-11-01 P2d）：原实现只写**单槽** `adr-register-backfill.json`，
每轮补录覆盖上一轮（ADR-006 版曾被 ADR-007 版覆盖，只能靠手工另存找回）。
现改为「一修订件一报告 + 一份索引」：
  · `adr-register-backfill-<adrNNN>.json` —— 该修订件的补录报告（不再被后续轮次覆盖）
  · `adr-register-backfill.json` —— **索引**（`reports[]` 按修订件号升序，`latest` 指向最新）
  · 兼容迁移：若索引位仍是**旧单槽报告**（含 `amendment` 且无 `kind=index`），
    写索引前先把它另存为对应 per-amendment 文件，历史不丢（幂等：已存在则不覆盖）

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
  python3 16-checkpoint/backfill_candidate_register.py --negative-test    # 3 条负例探针（临时目录）
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

ADR_TARGET = os.path.join("18-design", "adr", "ADR-004.json")
DAG = os.path.join("10-dag-data", "methodology-dag.json")
GAPS = os.path.join("01-books", "_verify", "reverse-gaps.json")
META = os.path.join("01-books", "_verify", "_meta")

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


INDEX_NAME = "adr-register-backfill.json"
PER_TMPL = "adr-register-backfill-%s.json"


def amendment_tag(amendment):
    return (amendment or "").lower().replace("-", "")


def per_report_path(root, amendment):
    return os.path.join(root, META, PER_TMPL % amendment_tag(amendment))


def index_path(root):
    return os.path.join(root, META, INDEX_NAME)


def write_reports(root, report):
    """一修订件一报告 + 一份索引（幂等；兼容旧单槽迁移）。

    返回 (per_path, index_path, migrated_relpath_or_None)。
    """
    migrated = None
    ip = index_path(root)
    if os.path.isfile(ip):
        try:
            doc = load(ip)
        except ValueError:
            doc = None
        if isinstance(doc, dict) and doc.get("amendment") and doc.get("kind") != "index":
            legacy = os.path.join(root, META, PER_TMPL % amendment_tag(doc["amendment"]))
            if not os.path.isfile(legacy):
                with open(legacy, "w", encoding="utf-8", newline="\n") as f:
                    f.write(dumps(doc))
                migrated = os.path.relpath(legacy, root)

    pp = per_report_path(root, report["amendment"])
    os.makedirs(os.path.dirname(pp), exist_ok=True)
    # 先写者胜：同一修订件被复跑时（条目早已并入 ⇒ entries_added == 0）**不得**用
    # 退化报告覆盖既有明细；只有真正发生并入（entries_added > 0）才改写该修订件报告。
    # 实测触发：旧单槽 ADR-007 报告迁移到 per-amendment 位后，紧接的 no-op 复跑
    # 把它覆盖成 entries_added=0、entries=[] 的空壳。
    if not (os.path.isfile(pp) and not report.get("entries_added")):
        with open(pp, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(report))

    entries = []
    for p in sorted(glob.glob(os.path.join(root, META, "adr-register-backfill-*.json"))):
        try:
            d = load(p)
        except ValueError:
            continue
        if not isinstance(d, dict) or d.get("kind") == "index" or not d.get("amendment"):
            continue
        entries.append({
            "amendment": d["amendment"],
            "path": os.path.relpath(p, root),
            "entries_added": d.get("entries_added"),
            "register_entries_before": d.get("register_entries_before"),
            "register_entries_after": d.get("register_entries_after"),
        })
    entries.sort(key=lambda e: e["amendment"])
    index = {
        "schema_version": "1.0.0",
        "kind": "index",
        "note": "候选册补录报告索引（每修订件一份，互不覆盖；本文件只维护清单，不承载单轮明细）",
        "reports": entries,
        "latest": entries[-1]["amendment"] if entries else None,
    }
    with open(ip, "w", encoding="utf-8", newline="\n") as f:
        f.write(dumps(index))
    return pp, ip, migrated


def negative_test():
    """3 条负例探针（临时目录；断言「不覆盖历史 + 幂等 + 旧单槽可迁移」）。"""
    import shutil
    import tempfile

    def probe(name, ok, detail):
        print("  [%s] %s —— %s" % ("OK" if ok else "!! FAILED", name, detail))
        return 0 if ok else 1

    bad = 0
    tmp = tempfile.mkdtemp(prefix="backfill-neg-")
    try:
        meta = os.path.join(tmp, META)
        os.makedirs(meta, exist_ok=True)
        legacy = {"schema_version": "1.0.0", "basis": "x", "amendment": "ADR-007",
                  "entries_added": 3, "register_entries_before": 49,
                  "register_entries_after": 52,
                  "entries": [{"origin_gap": "GAP-X-001"}, {"origin_gap": "GAP-X-002"},
                              {"origin_gap": "GAP-X-003"}]}
        with open(os.path.join(meta, INDEX_NAME), "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(legacy))

        # N1：旧单槽报告（与本次修订件**同名**）必须迁移到 per-amendment 位，
        #     且随后的 no-op 复跑（entries_added=0）不得把它覆盖成空壳。
        pp, ip, migrated = write_reports(tmp, {"schema_version": "1.0.0", "amendment": "ADR-007",
                                               "entries_added": 0, "register_entries_before": 52,
                                               "register_entries_after": 52, "entries": []})
        kept = load(pp) == legacy
        idx = load(ip)
        bad += probe("N1 旧单槽迁移后不被 no-op 复跑覆盖",
                     kept and migrated is not None and idx.get("kind") == "index",
                     "per=entries_added %r / entries %d；migrated=%s"
                     % (load(pp).get("entries_added"), len(load(pp).get("entries") or []), migrated))

        # N2：再补一轮 ADR-006 ⇒ 两轮报告**共存**（正是原单槽实现的缺陷场景）
        write_reports(tmp, {"schema_version": "1.0.0", "amendment": "ADR-006",
                            "entries_added": 16, "register_entries_before": 33,
                            "register_entries_after": 49, "entries": []})
        idx = load(ip)
        reports = {e["amendment"]: e for e in idx.get("reports") or []}
        bad += probe("N2 两轮报告共存互不覆盖",
                     set(reports) == {"ADR-006", "ADR-007"} and idx.get("latest") == "ADR-007",
                     "reports=%s latest=%s" % (sorted(reports), idx.get("latest")))

        # N3：同一修订件连写两次 ⇒ 索引逐字节一致（幂等）
        p1 = open(os.path.join(meta, INDEX_NAME), encoding="utf-8").read()
        write_reports(tmp, {"schema_version": "1.0.0", "amendment": "ADR-006",
                            "entries_added": 0, "register_entries_before": 49,
                            "register_entries_after": 49, "entries": []})
        p2 = open(os.path.join(meta, INDEX_NAME), encoding="utf-8").read()
        bad += probe("N3 索引重写幂等", p1 == p2, "len=%d vs %d" % (len(p1), len(p2)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("== 负例探针 %d/%d 如期通过 ==" % (3 - bad, 3))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="补录修订型 ADR 的候选册条目进 ADR-004")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--amendment", help="修订型 ADR（含 backfill_entries）")
    ap.add_argument("--target", default=ADR_TARGET)
    ap.add_argument("--check", action="store_true", help="只报告，不写")
    ap.add_argument("--negative-test", action="store_true", help="跑 3 条负例探针后退出")
    args = ap.parse_args()

    if args.negative_test:
        print("== 负例探针（报告留存机制可信度） ==")
        return negative_test()
    if not args.amendment:
        print("缺少 --amendment（或使用 --negative-test）")
        return 2

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
    rp, ip, migrated = write_reports(root, report)

    print("\n[3] wrote %s（%d → %d 条）"
          % (os.path.relpath(tgt_path, root), reg_before, len(tgt["candidate_register"])))
    if migrated:
        print("    migrated 旧单槽报告 → %s" % migrated)
    print("    wrote %s" % os.path.relpath(rp, root))
    print("    wrote %s（index）" % os.path.relpath(ip, root))
    print("\n== 结果 = PASS ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
