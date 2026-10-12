#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_verify_staging.py — 把核验子 Agent 的暂存分片合并为 SSOT 分片（唯一写入方=主Agent）

背景：阶段7 轨B 为并行核验，把每本书拆成多个**互不重叠**的暂存分片
（`_review/staging/{ledger,claims}-<book>-<part>.json`），由本脚本合并为
`_parts/{ledger,claims,gaps}-<slug>.json`。

设计原则：
- **fail-closed**：不可解析 / 结构不合法的分片一律**跳过并报告**，绝不带病合并。
- **确定性**：records 按 record_id 升序、claims 节点按 node_id 升序、gaps 按 gap_id 升序；
  `json.dump(ensure_ascii=False, indent=2)` + 末尾换行；无时间戳。
- **对账**：记录跨分片 record_id 重复、gap_id 重复、claim_id 悬挂（WARN）。

用法：
  python3 16-checkpoint/merge_verify_staging.py                 # 合并
  python3 16-checkpoint/merge_verify_staging.py --check         # 只读：报告将要写入的内容是否与盘上一致
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
STAGING = os.path.join("01-books", "_verify", "_review", "staging")
PARTS = os.path.join("01-books", "_verify", "_parts")

# 书 → (slug, source_id, 暂存前缀)
BOOKS = {
    "tt": ("team-topologies", "BK-030", "tt"),
    "ea": ("evolutionary-arch", "BK-011", "ea"),
    "ref": ("refactoring", "BK-021", "ref"),
    "ri": ("release-it", "BK-024", "ri"),
    "cc": ("clean-code", "BK-020", "cc"),
    "sre": ("sre-book", "BK-025", "sre"),
    "srew": ("workbook", "BK-026", "srew"),
    # 阶段7 阶段3 续做（2026-10-12）
    "sweg": ("sweg", "BK-001", "sweg"),
    "tfa": ("twelve-factor", "BK-031", "tfa"),
    "qasc": ("saip-ch4", "BK-036", "qasc"),
}


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def collect_ledger(root, prefix, book, problems, skipped):
    records = []
    seen = {}
    for p in sorted(glob.glob(os.path.join(resolve(root, STAGING), "ledger-%s-*.json" % prefix))):
        name = os.path.basename(p)
        try:
            doc = load(p)
        except Exception as e:                                   # noqa: BLE001
            skipped.append((name, "JSON 非法: %s" % e))
            continue
        recs = doc.get("records")
        if not isinstance(recs, list):
            skipped.append((name, "缺 records 数组"))
            continue
        for r in recs:
            rid = r.get("record_id")
            if not rid:
                problems.append("%s 有记录缺 record_id，已跳过" % name)
                continue
            if rid in seen:
                problems.append("record_id 跨分片重复: %s (%s, %s)" % (rid, seen[rid], name))
                continue
            seen[rid] = name
            records.append(r)
    records.sort(key=lambda r: r.get("record_id", ""))
    return records


def collect_claims(root, prefix, problems, skipped):
    nodes = {}
    for p in sorted(glob.glob(os.path.join(resolve(root, STAGING), "claims-%s-*.json" % prefix))):
        name = os.path.basename(p)
        try:
            doc = load(p)
        except Exception as e:                                   # noqa: BLE001
            skipped.append((name, "JSON 非法: %s" % e))
            continue
        if not isinstance(doc, dict):
            skipped.append((name, "非对象"))
            continue
        for node_id, node_doc in doc.items():
            if not isinstance(node_doc, dict) or "claims" not in node_doc:
                problems.append("%s 的 %s 结构非法，已跳过" % (name, node_id))
                continue
            if node_id in nodes:
                problems.append("claims 节点跨分片重复: %s（后者并入，claims 去重）" % node_id)
                have = {c.get("claim_id") for c in nodes[node_id]["claims"]}
                for c in node_doc["claims"]:
                    if c.get("claim_id") not in have:
                        nodes[node_id]["claims"].append(c)
                        have.add(c.get("claim_id"))
            else:
                nodes[node_id] = {"claims": list(node_doc["claims"])}
    ordered = {}
    for node_id in sorted(nodes):
        claims = sorted(nodes[node_id]["claims"], key=lambda c: c.get("claim_id", ""))
        ordered[node_id] = {"claims": claims}
    return ordered


def _prefix_glob(root, kind, prefix):
    """精确收集某前缀的暂存分片。

    ⚠️ 不能用 `gaps-<prefix>*.json`：前缀互为子串时（如 `sre` 与 `srew`）
    会串号——实测 `sre` 曾吞掉 `gaps-srew-*.json`，导致 sre-book 的缺口表
    混入 GAP-SREW-*。故只接受 `gaps-<prefix>.json` 与 `gaps-<prefix>-*.json`。
    """
    pats = [os.path.join(resolve(root, STAGING), "%s-%s.json" % (kind, prefix)),
            os.path.join(resolve(root, STAGING), "%s-%s-*.json" % (kind, prefix))]
    out = []
    for p in pats:
        out.extend(glob.glob(p))
    return sorted(set(out))


def collect_gaps(root, prefix, book_source_id, problems, skipped):
    gaps = []
    seen = set()
    for p in _prefix_glob(root, "gaps", prefix):
        name = os.path.basename(p)
        try:
            doc = load(p)
        except Exception as e:                                   # noqa: BLE001
            skipped.append((name, "JSON 非法: %s" % e))
            continue
        gs = doc.get("gaps")
        if not isinstance(gs, list):
            skipped.append((name, "缺 gaps 数组"))
            continue
        for g in gs:
            gid = g.get("gap_id")
            if not gid:
                problems.append("%s 有 gap 缺 gap_id，已跳过" % name)
                continue
            if gid in seen:
                problems.append("gap_id 跨分片重复: %s" % gid)
                continue
            seen.add(gid)
            gaps.append(g)
    gaps.sort(key=lambda g: g.get("gap_id", ""))
    return gaps


def build(root, problems, skipped, only=None):
    outputs = {}
    stats = {}
    for key, (slug, source_id, prefix) in sorted(BOOKS.items()):
        if only and slug not in only:
            continue
        records = collect_ledger(root, prefix, key, problems, skipped)
        claims = collect_claims(root, prefix, problems, skipped)
        gaps = collect_gaps(root, prefix, source_id, problems, skipped)
        if records:
            outputs[os.path.join(PARTS, "ledger-%s.json" % slug)] = dumps(
                {"book": slug, "source_id": source_id, "records": records})
        if claims:
            outputs[os.path.join(PARTS, "claims-%s.json" % slug)] = dumps(claims)
        if gaps:
            outputs[os.path.join(PARTS, "gaps-%s.json" % slug)] = dumps(
                {"book_source_id": source_id, "gaps": gaps})
        # 悬挂 claim_id 对账（WARN 级）
        known = {c.get("claim_id") for v in claims.values() for c in v["claims"]}
        dangling = sorted({r.get("claim_id") for r in records} - known)
        stats[slug] = {"records": len(records), "claims": len(known),
                       "gaps": len(gaps), "dangling_claim_ids": len(dangling),
                       "nodes": len(claims)}
        if dangling:
            problems.append("[WARN] %s 有 %d 个 claim_id 不在 claims 分片中（前 3：%s）"
                            % (slug, len(dangling), ", ".join(dangling[:3])))
    return outputs, stats


SECOND_PASS_SET = ("passed", "disputed")


def slug_of(rel):
    m = re.match(r"^(?:ledger|claims|gaps)-(.+)\.json$", os.path.basename(rel))
    return m.group(1) if m else None


def _count_secondpass(text):
    try:
        doc = json.loads(text)
    except ValueError:
        return 0
    return sum(1 for r in (doc.get("records") or [])
               if isinstance(r, dict)
               and ((r.get("review") or {}).get("second_pass") in SECOND_PASS_SET))


def guard_secondpass(root, outputs):
    """返回 [(slug, why)]：重合并会回退已落地的第二路裁决的书。

    `apply_secondpass.py` / `writeback_gap_ids.py` / `normalize_gap_ids.py`
    只写 `_parts/`，不回写 staging ⇒ staging 对已复核书落后。直接重跑本脚本
    会把 second_pass 与缺口号回写整批回退。本护栏 fail-closed：该书的
    ledger / claims / gaps 一并拒写，须显式 `--force`。
    """
    blocked = []
    for rel, text in sorted(outputs.items()):
        if not os.path.basename(rel).startswith("ledger-"):
            continue
        path = resolve(root, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            disk = f.read()
        have, new = _count_secondpass(disk), _count_secondpass(text)
        if have > new:
            blocked.append((slug_of(rel),
                            "磁盘 %d 条已复核，重合并后只剩 %d 条（staging 落后于 _parts）"
                            % (have, new)))
    return blocked


def main():
    ap = argparse.ArgumentParser(description="合并核验暂存分片 → _parts SSOT 分片")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true", help="只读：报告盘上状态，不写")
    ap.add_argument("--only", help="只合并指定 slug（逗号分隔），如 team-topologies")
    ap.add_argument("--force", action="store_true",
                    help="忽略第二路复核护栏（会回退 second_pass 与缺口回写，慎用）")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    problems, skipped = [], []
    only = set(x.strip() for x in args.only.split(",") if x.strip()) if args.only else None
    outputs, stats = build(root, problems, skipped, only)

    print("== 合并核验暂存分片 ==")
    print("staging = %s" % resolve(root, STAGING))
    print("")
    if not outputs:
        print("[SKIP] 未发现可用暂存分片")
        return 0
    for slug in sorted(stats):
        s = stats[slug]
        print("  %-18s records=%d claims=%d nodes=%d gaps=%d dangling=%d"
              % (slug, s["records"], s["claims"], s["nodes"], s["gaps"], s["dangling_claim_ids"]))
    print("")
    for name, why in skipped:
        print("  [SKIP] %s —— %s" % (name, why))
    for p in problems:
        print("  ! %s" % p)
    print("")

    stale = []
    for rel, text in sorted(outputs.items()):
        path = resolve(root, rel)
        disk = None
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                disk = f.read()
        if disk != text:
            stale.append(rel)
        print("  [%s] %s" % ("up-to-date" if disk == text else ("missing" if disk is None else "stale"), rel))

    # 🔴 数据安全护栏（2026-10-12 新增）：`_parts/` 是本链的**权威终态**——
    # `apply_secondpass.py`（第二路裁决）与 `writeback_gap_ids.py` /
    # `normalize_gap_ids.py`（缺口号回写）都**只写 `_parts/`，不回写 staging**。
    # 因此 staging 对已复核书是**落后**的：直接重跑本脚本会把 second_pass 与
    # 缺口回写**整批回退**。故 fail-closed：某书的 ledger 若会丢失 second_pass，
    # 则该书的 ledger 与 gaps 一并拒写，须显式 `--force` 才覆盖。
    blocked = [] if args.force else guard_secondpass(root, outputs)
    if blocked:
        print("")
        for slug, why in blocked:
            print("  !! 拒写 [%s]：%s" % (slug, why))
        print("  !! 如确要覆盖，请显式传 --force（会回退第二路复核与缺口回写）")

    if args.check:
        print("== --check：%s ==" % ("全部 up-to-date" if not stale else "有 %d 件待写" % len(stale)))
        return 0
    blocked_slugs = {s for s, _ in blocked}
    wrote = 0
    for rel, text in sorted(outputs.items()):
        if slug_of(rel) in blocked_slugs:
            continue
        path = resolve(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        wrote += 1
    print("== 已写入 %d 件（拒写 %d 件）==" % (wrote, len(outputs) - wrote))
    return 0


if __name__ == "__main__":
    sys.exit(main())
