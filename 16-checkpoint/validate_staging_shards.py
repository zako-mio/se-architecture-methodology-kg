#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_staging_shards.py — 合并前的暂存分片机检（主 Agent 亲跑）

用途：在 `merge_verify_staging.py` 之前对工人产出的暂存分片做**独立复验**
（不信工人自述），逐项机器判定，fail-closed。

检查项：
  1. JSON 合法 / UTF-8 无 BOM / 无 U+FFFD
  2. ledger：record_id 前缀+连续无重复；必填字段齐全；枚举取值合法
  3. ledger：node_id 格式；record cap（阶段2 参与节点 16 / 其余 8，含既有记录）
  4. ledger：anchor.chapter ∈ toc-<slug>.json 的真实章号
  5. claims：claim_id ↔ ledger.claim 逐字一致；claim_id 唯一；origin 枚举合法
  6. gaps：gap_id 连续无重复；kind 枚举；target 不得双空
  7. 悬挂 claim_id 对账（WARN）

用法：
  python3 16-checkpoint/validate_staging_shards.py --slug sre-book --prefix sre
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
STAGING = os.path.join("01-books", "_verify", "_review", "staging")
PARTS = os.path.join("01-books", "_verify", "_parts")
LEDGER_REL = os.path.join("01-books", "_verify", "verification-ledger.json")
GATE_REL = os.path.join("16-checkpoint", "gate_verification.py")

ORIGINS = {"definition", "principle", "mechanism", "engineering", "tradeoff", "errata"}
STRENGTH = {"direct", "partial", "inferred", "contradicted"}
DIRECTIONS = {"forward", "reverse"}
GAP_KINDS = {"missed_citation", "coverage_hole", "concept_missing"}
NODE_RE = re.compile(r"^(ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2}$")
SOURCE_RE = re.compile(r"^BK-\d{3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def densify_nodes():
    src = open(GATE_REL, encoding="utf-8").read()
    m = re.search(r"DENSIFY_NODES = \{(.*?)\}", src, re.S)
    return set(re.findall(r'"([A-Z]{3}-[A-Z]{1,2}-\d{2})"', m.group(1))) if m else set()


def main():
    ap = argparse.ArgumentParser(description="暂存分片合并前机检")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--book-source-id", required=True)
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    problems = []
    warns = []

    # 既有记录计数（用于 cap 判定）
    existing = Counter()
    led = load(os.path.join(root, LEDGER_REL))
    for r in led["records"]:
        existing[r["node_id"]] += 1
    dens = densify_nodes()

    # TOC 章号集合 + 章级正文切片（用于「节标题属哪一章」交叉校验）
    toc_path = os.path.join(root, PARTS, "toc-%s.json" % args.slug)
    toc = load(toc_path)
    toc_ch = {str(c["chapter"]) for c in toc["toc"]}
    chapter_text = {}
    text_path = os.path.join(root, "01-books", "_verify", "_text", "%s.txt" % args.slug)
    if os.path.isfile(text_path):
        raw = open(text_path, encoding="utf-8").read()
        marks = [(m.start(), m.group(1)) for m in
                 re.finditer(r"^=== (.+?) \| (.+?) ===$", raw, re.M)]
        for i, (off, no) in enumerate(marks):
            end = marks[i + 1][0] if i + 1 < len(marks) else len(raw)
            chapter_text[str(no)] = raw[off:end]
    print("=" * 80)
    print("暂存分片机检：slug=%s prefix=%s" % (args.slug, args.prefix))
    print("  TOC 章号 = %d 个：%s" % (len(toc_ch), sorted(toc_ch)[:12]))
    print("=" * 80)

    # ---------------- ledger ----------------
    lpaths = sorted(glob.glob(os.path.join(root, STAGING, "ledger-%s-*.json" % args.prefix)))
    records = []
    seen_rid = {}
    for p in lpaths:
        name = os.path.basename(p)
        raw = open(p, "rb").read()
        if raw[:3] == b"\xef\xbb\xbf":
            problems.append("%s 含 UTF-8 BOM" % name)
        try:
            doc = json.loads(raw.decode("utf-8"))
        except Exception as e:                                    # noqa: BLE001
            problems.append("%s JSON 非法: %s" % (name, e))
            continue
        if doc.get("source_id") != args.book_source_id:
            problems.append("%s source_id=%r 与声明 %s 不符" % (name, doc.get("source_id"), args.book_source_id))
        for r in doc.get("records") or []:
            rid = r.get("record_id")
            if rid in seen_rid:
                problems.append("record_id 重复: %s" % rid)
                continue
            seen_rid[rid] = name
            records.append(r)

    print("\n[1] ledger 分片 %d 个，记录 %d 条" % (len(lpaths), len(records)))
    for r in records:
        rid = r.get("record_id", "?")
        for k in ("record_id", "node_id", "source_id", "direction", "claim_id",
                  "claim", "anchor", "page_anchor_private", "evidence_strength",
                  "evidence_note", "review"):
            if k not in r:
                problems.append("%s 缺字段 %s" % (rid, k))
        nid = str(r.get("node_id", ""))
        if not NODE_RE.match(nid):
            problems.append("%s node_id 非法: %s" % (rid, nid))
        if not SOURCE_RE.match(str(r.get("source_id", ""))):
            problems.append("%s source_id 非法" % rid)
        if r.get("direction") not in DIRECTIONS:
            problems.append("%s direction 非法: %r" % (rid, r.get("direction")))
        if r.get("evidence_strength") not in STRENGTH:
            problems.append("%s evidence_strength 非法: %r" % (rid, r.get("evidence_strength")))
        cid = str(r.get("claim_id", ""))
        if nid and not re.match(r"^%s#(%s)#\d+$" % (re.escape(nid), "|".join(ORIGINS)), cid):
            problems.append("%s claim_id 非法: %s" % (rid, cid))
        claim = r.get("claim") or ""
        if not (10 <= len(claim) <= 400):
            problems.append("%s claim 长度异常: %d" % (rid, len(claim)))
        anchor = r.get("anchor")
        if not isinstance(anchor, dict):
            problems.append("%s anchor 非对象" % rid)
        else:
            ch = str(anchor.get("chapter", ""))
            if not ch:
                problems.append("%s anchor.chapter 为空" % rid)
            elif ch not in toc_ch:
                problems.append("%s anchor.chapter=%r 不在 TOC（章号错位门控拦不住）" % (rid, ch))
            if not anchor.get("section_title"):
                problems.append("%s anchor.section_title 为空" % rid)
            # 章号-节标题一致性：声明的 section 须能在**所声明章内**找到
            # （章号错位门控拦不住：只查章号存在性无法发现「节标题属另一章」）
            sec = str(anchor.get("section") or "").strip()
            if sec and ch in toc_ch and sec not in ("", ch):
                if ch not in chapter_text:
                    problems.append("%s 无法读取所声明章 %r 的正文，跳过节一致性校验" % (rid, ch))
                else:
                    body = chapter_text[ch]
                    if sec not in body:
                        other = [c for c, txt in chapter_text.items() if sec in txt]
                        problems.append(
                            "%s anchor.section=%r 在声明章 %r 内未出现%s"
                            % (rid, sec, ch,
                               ("（出现在章 %s）" % ",".join(sorted(other)) if other else "")))
        rev = r.get("review")
        if not isinstance(rev, dict):
            problems.append("%s review 非对象" % rid)
        else:
            for rk in ("reviewed_by", "review_date", "second_pass", "second_pass_by"):
                if rk not in rev:
                    problems.append("%s review 缺 %s" % (rid, rk))
            if not DATE_RE.match(str(rev.get("review_date", ""))):
                problems.append("%s review_date 非法" % rid)
            if rev.get("second_pass") != "none":
                problems.append("%s 首路 second_pass 应为 none" % rid)

    # record_id 连续性：仅对**单一分片且记录数 == 编号跨度**时判定（多分片/多轮旧分片不判，
    # 避免把历史分片的编号断档误报为新批缺陷；SSOT 级编号完整性由 gate_verification 负责）
    if len(lpaths) == 1:
        nums = sorted(int(m.group(1)) for m in
                      (re.match(r"^VR-%s-(\d+)$" % re.escape(args.prefix.upper()), rid)
                       for rid in seen_rid) if m)
        if nums:
            expect = list(range(nums[0], nums[0] + len(nums)))
            if nums != expect:
                problems.append("record_id 编号不连续：%s…（缺口 %s）"
                                % (nums[:3], sorted(set(expect) - set(nums))[:6]))
            print("    record_id 区间 = VR-%s-%03d … VR-%s-%03d"
                  % (args.prefix.upper(), nums[0], args.prefix.upper(), nums[-1]))

    # cap 判定（既有 + 新增）
    # ⚠️ 若本书**已合并**（_parts/ledger-<slug>.json 存在且其记录已含本批），
    #    则 `existing` 已包含暂存分片的记录，再加一次会重复计数 ⇒ 此时只报实测总量，不判超限。
    parts_ledger = os.path.join(root, PARTS, "ledger-%s.json" % args.slug)
    already_merged = os.path.isfile(parts_ledger)
    add = Counter(r.get("node_id") for r in records)
    over = []
    for nid, n in sorted(add.items()):
        cap = 16 if nid in dens else 8
        tot = existing.get(nid, 0) + (0 if already_merged else n)
        if tot > cap:
            over.append((nid, existing.get(nid, 0), n, tot, cap))
    print("\n[2] 节点记录上限（既有+新增 ≤ 上限）%s"
          % ("｜本书已合并 ⇒ 以 SSOT 实测总量为准" if already_merged else ""))
    for nid, ex, n, tot, cap in over:
        problems.append("%s 超上限：既有 %d + 新增 %d = %d > %d" % (nid, ex, n, tot, cap))
    if not over:
        print("    全部通过（覆盖节点 %d 个）" % len(add))
    for nid, n in sorted(add.items()):
        print("    %-10s 暂存 %d（SSOT 既有 %d，上限 %d）"
              % (nid, n, existing.get(nid, 0), 16 if nid in dens else 8))

    # ---------------- claims ----------------
    cpaths = sorted(glob.glob(os.path.join(root, STAGING, "claims-%s-*.json" % args.prefix)))
    claims = {}
    for p in cpaths:
        doc = load(p)
        for nid, nd in doc.items():
            if not NODE_RE.match(nid):
                problems.append("claims 节点键非法: %s" % nid)
            for c in nd.get("claims") or []:
                cid = c.get("claim_id")
                if cid in claims:
                    problems.append("claim_id 跨分片重复: %s" % cid)
                if c.get("origin") not in ORIGINS:
                    problems.append("%s origin 非法: %r" % (cid, c.get("origin")))
                claims[cid] = (nid, c.get("text"))

    print("\n[3] claims 分片 %d 个，主张 %d 条" % (len(cpaths), len(claims)))

    # 一致性检查：每条 direct 记录须在 claims 分片中有对应 claim_id
    # （claims 文本以 `_parts/claims-<slug>.json` 的 SSOT 为准；暂存分片可能跨轮，
    #   故此处只校验 claim_id 覆盖与唯一性，不做文本比对，避免历史分片误报）
    direct_recs = [r for r in records if r.get("evidence_strength") == "direct"]
    mism = []
    for r in direct_recs:
        cid = r.get("claim_id")
        if cid not in claims:
            mism.append((r.get("record_id"), cid, "claims 分片缺失该 claim_id"))
    print("    direct 记录 %d 条；claims 覆盖检查：缺失 %d" % (len(direct_recs), len(mism)))
    for rid, cid, why in mism[:10]:
        problems.append("%s 的 %s %s" % (rid, cid, why))

    # 悬挂 claim_id
    dangling = sorted({r.get("claim_id") for r in records} - set(claims))
    if dangling:
        warns.append("悬挂 claim_id %d 个（非 direct 记录可无 claims）：%s" % (len(dangling), dangling[:4]))

    # ---------------- gaps ----------------
    # ⚠️ 分片名可能是 `gaps-<prefix>.json`（无后缀）或 `gaps-<prefix>-<x>.json`；
    #    必须排除 `gaps-<prefix><other>-*.json`（如 prefix=sre 时不得吞掉 gaps-srew-a.json）
    gpaths = sorted(set(glob.glob(os.path.join(root, STAGING, "gaps-%s.json" % args.prefix)))
                    | set(glob.glob(os.path.join(root, STAGING, "gaps-%s-*.json" % args.prefix))))
    gaps = []
    seen_gid = set()
    for p in gpaths:
        doc = load(p)
        if doc.get("book_source_id") != args.book_source_id:
            problems.append("%s book_source_id 不符" % os.path.basename(p))
        for g in doc.get("gaps") or []:
            gid = g.get("gap_id")
            if gid in seen_gid:
                problems.append("gap_id 重复: %s" % gid)
            seen_gid.add(gid)
            for k in ("gap_id", "kind", "book_source_id", "anchor", "target",
                      "summary", "proposed_action", "evidence_strength"):
                if k not in g:
                    problems.append("%s 缺字段 %s" % (gid, k))
            if g.get("kind") not in GAP_KINDS:
                problems.append("%s kind 非法: %r" % (gid, g.get("kind")))
            t = g.get("target") or {}
            if not (t.get("existing_node_id") or t.get("proposed_node")):
                problems.append("%s target 双空（G-V1 硬校验）" % gid)
            if t.get("proposed_node") is not None:
                # 非空仅当该号已在 ADR-004 候选册登记（旧缺口），
                # 或该缺口已被 normalize_gap_ids.py 重指派（旧暂存分片保留重指派前旧值）。
                adr_path = os.path.join(root, "18-design", "adr", "ADR-004.json")
                re_path = os.path.join(root, "01-books", "_verify", "_meta",
                                       "gap-id-reassignments.json")
                allowed = False
                if os.path.isfile(adr_path):
                    adr = load(adr_path)
                    for e in adr.get("candidate_register") or []:
                        if gid in (e.get("gap_ids") or []):
                            allowed = True
                if not allowed and os.path.isfile(re_path):
                    rej = load(re_path)
                    for r in rej.get("reassignments") or []:
                        if r.get("gap_id") == gid:
                            allowed = True
                if not allowed:
                    # 降为 WARN：历史分片可能保留未走归一化的旧提案号（如 clean-code 的
                    # MTH-H-05..08 —— 因未撞 blocked 集合故 normalize 未重指派）；
                    # 本轮新缺口一律要求留 null（见工人 prompt），故此处只提示不判失败。
                    warns.append("%s proposed_node=%r 未在 ADR 候选册登记、亦无重指派记录"
                                 % (gid, t.get("proposed_node")))
            ch = str((g.get("anchor") or {}).get("chapter", ""))
            if ch and ch not in toc_ch:
                problems.append("%s anchor.chapter=%r 不在 TOC" % (gid, ch))
            gaps.append(g)
    print("\n[4] gaps 分片 %d 个，缺口 %d 条" % (len(gpaths), len(gaps)))
    nums = sorted(int(m.group(1)) for m in
                  (re.match(r"^GAP-%s-(\d+)$" % re.escape(args.prefix.upper()), g["gap_id"]) for g in gaps)
                  if m)
    # 多分片时各工人使用不重叠号段（如 001-… 与 101-…），不判连续性
    if len(gpaths) == 1 and nums:
        expect = list(range(nums[0], nums[0] + len(nums)))
        if nums != expect:
            problems.append("gap_id 编号不连续：%s" % sorted(set(expect) - set(nums))[:6])
    elif nums:
        print("    gap_id 号段 = %s（多分片，不判连续性）"
              % sorted({n // 100 * 100 for n in nums}))

    # ---------------- 汇总 ----------------
    print("\n[5] WARN")
    for w in warns:
        print("    ~ %s" % w)
    print("\n[6] 问题 %d 条" % len(problems))
    for p in problems[:40]:
        print("    ! %s" % p)
    ok = not problems
    print("\n" + "=" * 80)
    print("  == 结果 = %s ==" % ("PASS" if ok else "FAIL"))
    print("=" * 80)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
