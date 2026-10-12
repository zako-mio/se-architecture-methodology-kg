#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_secondpass.py — 把第二路独立复核的裁决回写进核验分片（唯一写入方=主Agent）

输入：
  01-books/_verify/_review/secondpass-<slug>.json
    {"reviewed_by": "...", "review_date": "YYYY-MM-DD",
     "verdicts": [{"record_id","node_id","source_id","claim_id",
                   "first_pass_strength","second_pass_strength",
                   "agree": true|false, "anchor_locatable": true|false, "note": "..."}]}
  01-books/_verify/_parts/ledger-<slug>.json

输出（原地更新 `_parts/ledger-<slug>.json`）：
  对每条被判定的 record：
    - agree=true  → review.second_pass = "passed"
    - agree=false → review.second_pass = "disputed"，并**保守终裁**把
                    `evidence_strength` 降为 `second_pass_strength`（只降不升），
                    `evidence_note` 追加复核说明。

纪律：
- **只降不升**：复核结论高于首路时**不**升级（保守；防「复核变相加码」）。
- **fail-closed**：verdict 指向不存在的 record_id / 结构非法 → 跳过并报告，不猜。
- 确定性：records 保持按 record_id 升序；无时间戳；UTF-8 末尾换行。
- 幂等：重复运行结果一致（已 passed/disputed 的记录按同一规则重算）。

用法：
  python3 16-checkpoint/apply_secondpass.py --slug team-topologies
  python3 16-checkpoint/apply_secondpass.py --all
  python3 16-checkpoint/apply_secondpass.py --all --check     # 只读报告
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
VERIFY = os.path.join("01-books", "_verify")
REVIEW = os.path.join(VERIFY, "_review")
PARTS = os.path.join(VERIFY, "_parts")

STRENGTH_ORDER = {"contradicted": 0, "inferred": 1, "partial": 2, "direct": 3}

# 复核留痕标记（追加进 evidence_note）。2026-10-12 修：追加前先**剥掉历史标记**，
# 否则重跑会不断叠加（实测某记录已叠 3 份，违背「幂等」声明）。
MARK_RE = re.compile(r"\s*【第二路复核】[^【]*")


def strip_review_marks(note):
    return MARK_RE.sub("", note or "").rstrip()


def discover_slugs(root):
    """从 `_parts/ledger-<slug>.json` 文件名发现 slug（数据驱动，稳定排序）。

    阶段7 阶段3 修正：原为硬编码 `{"team-topologies": ..., "evolutionary-arch": ...}`，
    新增书会被 `--all` **静默跳过**（同 `derive_verification.py` 曾修过的 B3 类问题）。
    改为与 `_parts/` 实际内容一致，新书自动纳入。
    """
    out = set()
    for p in glob.glob(os.path.join(resolve(root, PARTS), "ledger-*.json")):
        m = re.match(r"^ledger-(.+)\.json$", os.path.basename(p))
        if m:
            out.add(m.group(1))
    return tuple(sorted(out))


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_one(root, slug, check):
    vpath = os.path.join(resolve(root, REVIEW), "secondpass-%s.json" % slug)
    lpath = os.path.join(resolve(root, PARTS), "ledger-%s.json" % slug)
    report = {"slug": slug, "verdicts": 0, "matched": 0, "unmatched": [],
              "passed": 0, "disputed": 0, "downgraded": 0, "not_covered": 0,
              "missing_files": []}
    if not os.path.isfile(vpath):
        report["missing_files"].append(os.path.relpath(vpath, root))
        return report, None
    if not os.path.isfile(lpath):
        report["missing_files"].append(os.path.relpath(lpath, root))
        return report, None

    vdoc = load(vpath)
    verdicts = vdoc.get("verdicts") or []
    report["verdicts"] = len(verdicts)
    by_rid = {}
    for v in verdicts:
        rid = v.get("record_id")
        if not rid:
            continue
        by_rid[rid] = v

    ldoc = load(lpath)
    records = ldoc.get("records") or []
    for r in records:
        rid = r.get("record_id")
        v = by_rid.get(rid)
        rev = r.get("review") or {}
        if v is None:
            # 未被复核覆盖的记录：若其强度为 direct，属**未复核的升级依据**，须报出
            if r.get("evidence_strength") == "direct":
                report["not_covered"] += 1
            continue
        report["matched"] += 1
        agree = bool(v.get("agree"))
        sp_strength = v.get("second_pass_strength")
        rev["second_pass"] = "passed" if agree else "disputed"
        rev["second_pass_by"] = vdoc.get("reviewed_by") or ""
        base_note = strip_review_marks(r.get("evidence_note"))
        if not agree:
            report["disputed"] += 1
            cur = r.get("evidence_strength")
            # 保守终裁：只降不升
            if (sp_strength in STRENGTH_ORDER and cur in STRENGTH_ORDER
                    and STRENGTH_ORDER[sp_strength] < STRENGTH_ORDER[cur]):
                r["evidence_strength"] = sp_strength
                report["downgraded"] += 1
                marker = "【第二路复核】判为 %s（原判 %s），按保守终裁降级。" % (sp_strength, cur)
                r["evidence_note"] = (base_note + " " + marker).strip()
            else:
                marker = "【第二路复核】结论有分歧但未低于原判（复核=%s），保留原强度。" % sp_strength
                r["evidence_note"] = (base_note + " " + marker).strip()
        else:
            report["passed"] += 1
            r["evidence_note"] = base_note
        if v.get("anchor_locatable") is False:
            report["anchor_unlocatable"] = report.get("anchor_unlocatable", 0) + 1
            r["evidence_note"] = (strip_review_marks(r.get("evidence_note"))
                                  + " 【第二路复核】锚点未能定位，章号待回修。").strip()
        r["review"] = rev
    for rid in sorted(by_rid):
        if not any(r.get("record_id") == rid for r in records):
            report["unmatched"].append(rid)

    records.sort(key=lambda r: r.get("record_id", ""))
    ldoc["records"] = records
    return report, dumps(ldoc)


def main():
    ap = argparse.ArgumentParser(description="第二路复核裁决回写")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--slug", help="单本 slug")
    ap.add_argument("--all", action="store_true", help="处理全部已登记书")
    ap.add_argument("--check", action="store_true", help="只读报告，不写")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    slugs = [args.slug] if args.slug else (list(discover_slugs(root)) if args.all else [])
    if not slugs:
        print("请指定 --slug 或 --all")
        return 2

    print("== 第二路复核裁决回写 ==")
    print("")
    total = {"matched": 0, "passed": 0, "disputed": 0, "downgraded": 0,
             "not_covered": 0, "unmatched": 0}
    for slug in slugs:
        rep, text = apply_one(root, slug, args.check)
        print("[%s]" % slug)
        if rep["missing_files"]:
            for m in rep["missing_files"]:
                print("    [SKIP] 缺文件 %s" % m)
            continue
        print("    verdicts=%d matched=%d passed=%d disputed=%d downgraded=%d 未复核的 direct=%d"
              % (rep["verdicts"], rep["matched"], rep["passed"], rep["disputed"],
                 rep["downgraded"], rep["not_covered"]))
        if rep["unmatched"]:
            print("    ! verdict 指向不存在的 record_id：%s" % ", ".join(rep["unmatched"][:10]))
        for k in ("matched", "passed", "disputed", "downgraded", "not_covered"):
            total[k] += rep[k]
        total["unmatched"] += len(rep["unmatched"])
        if text is not None and not args.check:
            p = os.path.join(resolve(root, PARTS), "ledger-%s.json" % slug)
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print("    wrote %s" % os.path.relpath(p, root))
    print("")
    print("== 汇总 == matched=%d passed=%d disputed=%d downgraded=%d 未复核 direct=%d 悬挂 verdict=%d"
          % (total["matched"], total["passed"], total["disputed"], total["downgraded"],
             total["not_covered"], total["unmatched"]))
    if args.check:
        print("== --check：未写盘 ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
