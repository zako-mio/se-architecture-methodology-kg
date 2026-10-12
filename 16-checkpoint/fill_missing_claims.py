#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fill_missing_claims.py — 补齐「ledger 有记录、claims 分片缺失」的原子主张

背景（2026-10-12 实测）：`ledger.claim_id − node-claim-map.claim_id = 73`，
其中两条独立根因：

  ① 跨书同节点被 `derive_verification.build_claims()` 旧实现整段丢弃（50 条）
     → 已在派生器侧修复（按 claim_id 并集去重），**不属本脚本职责**。
  ② 部分 claim **从未进入任何 claims 分片**（23 条）：
     BK-023（`ddia`）18 条 + BK-007（`clean-architecture`）5 条
     → 本脚本按 ledger 的 `claim` 文本补入**归属书**的 claims 分片。

写入规则（fail-closed、确定性、幂等）：
  · 归属判定：`source_id` → slug（读 `_parts/toc-<slug>.json` 的 `source_id`）；
    无法归属 ⇒ 报错退出（不猜）。
  · **有暂存分片的书**（`merge_verify_staging.BOOKS` 登记）：
    写入专用分片 `_review/staging/claims-<prefix>-fill.json`，
    再由调用方跑 `merge_verify_staging.py --only <slug>` 生成 SSOT
    （避免被下一次 merge 覆盖，也避免污染工人分片）。
  · **无暂存分片的书**（阶段1 手写 SSOT：`ddia` / `clean-architecture` / `saip`）：
    直接写 `_parts/claims-<slug>.json`（例外须在 verify-contract.md 留痕）。
  · 条目形态与既有分片一致：`{"claim_id": …, "text": …, "origin": …}`；
    同一 claim_id 已存在 ⇒ 跳过（幂等）。
  · 键序：保留既有节点键序，新节点按字典序追加；节点内按 `claim_id` 排序。
  · 若同一 claim_id 对应多条 ledger 记录（历史重复）⇒ **报错退出**
    （须先跑 `fix_duplicate_claim_ids.py`）。

用法：
  python3 16-checkpoint/fill_missing_claims.py --check    # 只读
  python3 16-checkpoint/fill_missing_claims.py            # 写入 + 落报告
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
sys.path.insert(0, HERE)
import merge_verify_staging as MVS  # noqa: E402  （复用 BOOKS 前缀表，单一真相源）

VERIFY = os.path.join("01-books", "_verify")
PARTS = os.path.join(VERIFY, "_parts")
STAGING = os.path.join(VERIFY, "_review", "staging")
REPORT_REL = os.path.join(VERIFY, "_meta", "claims-fill-report.json")

ORIGINS = {"definition", "principle", "mechanism", "engineering", "tradeoff", "errata"}
CID_RE = re.compile(r"^(?P<node>(?:ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2})#(?P<origin>[a-z]+)#(?P<n>\d+)$")


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def load_opt(path):
    try:
        return load(path)
    except (OSError, ValueError):
        return None


def source_to_slug(root):
    """source_id → slug（读 toc 分片；重复 source_id 报错）。"""
    out, dup = {}, []
    for p in sorted(glob.glob(os.path.join(resolve(root, PARTS), "toc-*.json"))):
        doc = load_opt(p) or {}
        sid = doc.get("source_id")
        slug = os.path.basename(p)[len("toc-"):-len(".json")]
        if not sid:
            continue
        if sid in out and out[sid] != slug:
            dup.append((sid, out[sid], slug))
        out[sid] = slug
    return out, dup


def ledger_records(root):
    """{claim_id: [record, …]}（跨所有 ledger 分片）。"""
    out = {}
    for p in sorted(glob.glob(os.path.join(resolve(root, PARTS), "ledger-*.json"))):
        doc = load(p)
        for r in doc.get("records") or []:
            cid = r.get("claim_id")
            if cid:
                out.setdefault(cid, []).append(r)
    return out


def existing_claim_ids(root):
    """已在任何 claims 分片（_parts ∪ staging）中的 claim_id。"""
    ids = set()
    pats = [os.path.join(resolve(root, PARTS), "claims-*.json"),
            os.path.join(resolve(root, STAGING), "claims-*.json")]
    for pat in pats:
        for p in sorted(glob.glob(pat)):
            doc = load(p)
            for node_id, node_doc in (doc or {}).items():
                if not isinstance(node_doc, dict):
                    continue
                for c in node_doc.get("claims") or []:
                    if c.get("claim_id"):
                        ids.add(c["claim_id"])
    return ids


def staging_prefix(slug):
    for _key, (s, _sid, prefix) in MVS.BOOKS.items():
        if s == slug:
            return prefix
    return None


def merge_into_shard(path, entries_by_node):
    """把 {node_id: [entry, …]} 并入分片（保留既有键序，新键字典序追加，节点内按 claim_id 排序）。"""
    doc = load_opt(path) or {}
    added = 0
    for node_id in sorted(entries_by_node):
        bucket = doc.setdefault(node_id, {"claims": []})
        have = {c.get("claim_id") for c in bucket.get("claims") or []}
        for e in entries_by_node[node_id]:
            if e["claim_id"] in have:
                continue
            bucket.setdefault("claims", []).append(e)
            have.add(e["claim_id"])
            added += 1
    for node_id in doc:
        claims = doc[node_id].get("claims") or []
        claims.sort(key=lambda c: c.get("claim_id", ""))
        doc[node_id]["claims"] = claims
    return doc, added


def main():
    ap = argparse.ArgumentParser(description="补齐缺失的 claims 分片条目")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true", help="只读：报告将补写的条目")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    sid2slug, dup = source_to_slug(root)
    if dup:
        print("! toc 分片 source_id 重复：%s" % dup)
        return 1

    records = ledger_records(root)
    have = existing_claim_ids(root)
    missing = sorted(cid for cid in records if cid not in have)

    print("== claims 缺失补齐 ==")
    print("ledger claim_id %d 条；已在 claims 分片 %d 条；缺失 %d 条"
          % (len(records), len(have), len(missing)))

    problems = []
    plan = {}          # slug -> {node_id: [entry]}
    for cid in missing:
        recs = records[cid]
        if len(recs) > 1:
            problems.append("%s 对应 %d 条 ledger 记录（历史重复）——须先跑 "
                            "fix_duplicate_claim_ids.py" % (cid, len(recs)))
            continue
        r = recs[0]
        m = CID_RE.match(cid)
        if not m:
            problems.append("%s claim_id 格式非法" % cid)
            continue
        origin = m.group("origin")
        if origin not in ORIGINS:
            problems.append("%s origin 非封闭枚举" % cid)
            continue
        slug = sid2slug.get(r.get("source_id"))
        if not slug:
            problems.append("%s 的 source_id=%s 无法归属到任何 slug"
                            % (cid, r.get("source_id")))
            continue
        text = r.get("claim")
        if not text:
            problems.append("%s 的 ledger 记录缺 claim 文本" % cid)
            continue
        plan.setdefault(slug, {}).setdefault(m.group("node"), []).append(
            {"claim_id": cid, "text": text, "origin": origin})

    for slug in sorted(plan):
        n = sum(len(v) for v in plan[slug].values())
        prefix = staging_prefix(slug)
        print("  %-18s 补 %d 条；节点 %s；目标 = %s"
              % (slug, n, sorted(plan[slug]),
                 ("staging/claims-%s-fill.json" % prefix) if prefix
                 else ("_parts/claims-%s.json（无暂存，手写 SSOT 例外）" % slug)))
    for p in problems:
        print("  ! %s" % p)
    print("")

    if problems:
        print("== FAIL：%d 个问题，未写任何文件 ==" % len(problems))
        return 1
    if not missing:
        print("== 无缺失，无需补写 ==")
        return 0
    if args.check:
        print("== --check：未写入任何文件 ==")
        return 0

    written, total_added = [], 0
    for slug in sorted(plan):
        prefix = staging_prefix(slug)
        if prefix:
            path = os.path.join(resolve(root, STAGING), "claims-%s-fill.json" % prefix)
            note = "staging（须随后跑 merge_verify_staging.py --only %s）" % slug
        else:
            path = os.path.join(resolve(root, PARTS), "claims-%s.json" % slug)
            note = "_parts（无暂存：手写 SSOT 例外）"
        doc, added = merge_into_shard(path, plan[slug])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(doc))
        written.append({"slug": slug, "path": os.path.relpath(path, root),
                        "added": added, "note": note})
        total_added += added
        print("  wrote %s（+%d 条，%s）" % (os.path.relpath(path, root), added, note))

    report = {
        "meta": {"schema_version": "1.0.0", "generated": "2026-09-11"},
        "missing_before": len(missing),
        "added": total_added,
        "targets": written,
        "problems": problems,
    }
    rp = resolve(root, REPORT_REL)
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    with open(rp, "w", encoding="utf-8", newline="\n") as f:
        f.write(dumps(report))
    print("  wrote %s" % REPORT_REL)

    left = sorted(cid for cid in records if cid not in existing_claim_ids(root))
    print("== 回读：仍缺 %d 条 ==" % len(left))
    return 0 if not left else 1


if __name__ == "__main__":
    sys.exit(main())
