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
- **降级触发（2026-11-02 P2f 收紧）**：① 复核强度 < 验前强度 ⇒ 一律降（不论 agree）；
  ② `agree=false` ⇒ 终裁强度至多 `partial`。原实现只在 agree=false 时读强度、且允许
  「否决但同强度」保留 direct ⇒ 两条静默放宽路径（见负例 N6/N7）。
- **fail-closed**：verdict 指向不存在的 record_id / 结构非法 → 跳过并报告，不猜。
- 确定性：records 保持按 record_id 升序；无时间戳；UTF-8 末尾换行。
- 幂等：重复运行结果一致。❗**留痕判据锚定「复核前强度」而不是「当前强度」**
  （`review.first_pass_strength` → 否则用 verdict 自带的 `first_pass_strength`
  → 再否则才退回当前值）。2026-11-01（P2d）修：原实现以**当前** `evidence_strength`
  为判据，对已降级记录重跑时 `sp == cur` 不再成立，于是把
  「按保守终裁降级」改写成「未低于原判，保留原强度」——**数据值不变、语义反转**。
  反之进行中的记录若被判为「保留原强度」也不会被误升。

用法：
  python3 16-checkpoint/apply_secondpass.py --slug team-topologies
  python3 16-checkpoint/apply_secondpass.py --all
  python3 16-checkpoint/apply_secondpass.py --all --check     # 只读报告
  python3 16-checkpoint/apply_secondpass.py --negative-test   # 8 条负例探针（临时目录，不动真数据）
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
              "passed": 0, "disputed": 0, "downgraded": 0, "already_downgraded": 0,
              "not_covered": 0, "basis_fallback": 0, "missing_files": []}
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
        cur = r.get("evidence_strength")
        # 幂等判据（P2d 修）：降级/保留必须锚定「该记录第二路复核**之前**的强度」。
        # 优先读已留痕的 review.first_pass_strength（未来周边自洽），
        # 其次读 verdict 自带的 first_pass_strength（789/789 条实测均有），
        # 最后才退回当前值（老数据兜底）。P2e 修：兜底分支**必须显式 WARN**，
        # 否则未来数据一旦缺字段，会静默退化回「以当前强度为判据」的旧缺陷。
        basis = rev.get("first_pass_strength") or v.get("first_pass_strength")
        if not basis:
            basis = cur
            report["basis_fallback"] += 1
            print("    [WARN] %s：验前强度两处均缺（review.first_pass_strength / "
                  "verdict.first_pass_strength），已退回当前强度 %r 为判据——"
                  "此路径会静默退化降级留痕，请补齐 verdict 的 first_pass_strength。"
                  % (rid, basis), file=sys.stderr)
        rev["second_pass"] = "passed" if agree else "disputed"
        rev["second_pass_by"] = vdoc.get("reviewed_by") or ""
        base_note = strip_review_marks(r.get("evidence_note"))
        report["disputed" if not agree else "passed"] += 1

        # —— 终裁强度（2026-11-02 P2f 收紧；原实现有两条静默放宽路径）——
        # ① 复核强度低于验前强度 ⇒ 一律取复核值。原实现只在 `agree=False` 时读它，
        #    于是「同意结论方向、但判定证据只够 partial」的复核被**静默忽略**，
        #    direct 被原样保留 = 强度虚高（本轮实测 8 条命中）。
        # ② `agree=False` ⇒ 终裁强度**至多 partial**。原实现在「复核强度 = 验前强度」
        #    时保留 direct，等于「结论被否决但强度不变」（本轮实测 1 条命中）。
        final = basis
        if (sp_strength in STRENGTH_ORDER and basis in STRENGTH_ORDER
                and STRENGTH_ORDER[sp_strength] < STRENGTH_ORDER[final]):
            final = sp_strength
        if (not agree and final in STRENGTH_ORDER
                and STRENGTH_ORDER[final] > STRENGTH_ORDER["partial"]):
            final = "partial"

        if (final in STRENGTH_ORDER and basis in STRENGTH_ORDER
                and STRENGTH_ORDER[final] < STRENGTH_ORDER[basis]):
            if (sp_strength in STRENGTH_ORDER
                    and STRENGTH_ORDER[sp_strength] < STRENGTH_ORDER[basis]):
                marker = "【第二路复核】判为 %s（原判 %s），按保守终裁降级。" % (final, basis)
            else:
                marker = ("【第二路复核】复核否决归属或结论，降至 %s（原判 %s）。"
                          % (final, basis))
            if cur != final and STRENGTH_ORDER.get(cur, 99) > STRENGTH_ORDER[final]:
                r["evidence_strength"] = final
                report["downgraded"] += 1
            else:
                # 已降级过：值不再变，但**留痕仍是降级口径**（原实现此处会反转语义）
                report["already_downgraded"] += 1
            r["evidence_note"] = (base_note + " " + marker).strip()
        else:
            if not agree:
                marker = ("【第二路复核】结论有分歧但未低于原判（复核=%s），保留原强度。"
                          % sp_strength)
                r["evidence_note"] = (base_note + " " + marker).strip()
            else:
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



def negative_test():
    """5 条负例探针：幂等判据与兜底分支必须逐条**以其应有理由**通过/拒绝，否则判据已退化（exit=1）。

    探针在**临时目录**里造合成夹具，绝不触碰真实 `_parts/`。
    """
    import shutil
    import tempfile

    def fixture(tmp, records, verdicts, reviewed_by="probe"):
        parts = os.path.join(tmp, PARTS)
        review = os.path.join(tmp, REVIEW)
        os.makedirs(parts, exist_ok=True)
        os.makedirs(review, exist_ok=True)
        with open(os.path.join(parts, "ledger-probe.json"), "w", encoding="utf-8") as f:
            f.write(dumps({"book": "probe", "source_id": "BK-999", "records": records}))
        with open(os.path.join(review, "secondpass-probe.json"), "w", encoding="utf-8") as f:
            f.write(dumps({"reviewed_by": reviewed_by, "review_date": "2026-11-01",
                           "verdicts": verdicts}))

    def rec(rid, strength, note=""):
        return {"record_id": rid, "node_id": "ESS-G-01", "source_id": "BK-999",
                "claim_id": "ESS-G-01#definition#300", "claim": "probe claim text",
                "anchor": {"chapter": "1", "section": "1.1"},
                "direction": "forward", "evidence_strength": strength,
                "evidence_note": note, "review": {}}

    def verdict(rid, first, second, agree):
        return {"record_id": rid, "node_id": "ESS-G-01", "source_id": "BK-999",
                "claim_id": "ESS-G-01#definition#300",
                "first_pass_strength": first, "second_pass_strength": second,
                "agree": agree, "anchor_locatable": True, "note": "probe"}

    def probe(name, ok, detail):
        print("  [%s] %s —— %s" % ("OK" if ok else "!! FAILED", name, detail))
        return 0 if ok else 1

    bad = 0
    tmp = tempfile.mkdtemp(prefix="apply2p-neg-")
    try:
        # N1：已降级记录重跑 ⇒ 留痕仍是「按保守终裁降级」，且不重复叠加标记。
        #     这是原实现的真实缺陷场景（数据值不变、语义反转）。
        fixture(tmp, [rec("VR-PRB-001", "partial",
                          "原始注记 【第二路复核】判为 partial（原判 direct），按保守终裁降级。")],
                [verdict("VR-PRB-001", "direct", "partial", False)])
        rep1, text1 = apply_one(tmp, "probe", False)
        note1 = json.loads(text1)["records"][0]["evidence_note"]
        ok = ("判为 partial（原判 direct），按保守终裁降级" in note1
              and "未低于原判" not in note1
              and note1.count("【第二路复核】") == 1)
        bad += probe("N1 已降级记录重跑不反转留痕", ok,
                     "留痕仍为降级口径且标记唯一（already_downgraded=%d）"
                     % rep1.get("already_downgraded", -1))

        # N2：未降级的分歧（复核强度 ≥ 首路）⇒ 保留原强度，不得升级、不得记降级。
        fixture(tmp, [rec("VR-PRB-002", "partial")],
                [verdict("VR-PRB-002", "partial", "direct", False)])
        rep2, text2 = apply_one(tmp, "probe", False)
        r2 = json.loads(text2)["records"][0]
        ok = (r2["evidence_strength"] == "partial" and rep2["downgraded"] == 0
              and "保留原强度" in r2["evidence_note"])
        bad += probe("N2 未低于原判不升级不降级", ok,
                     "strength=%s downgraded=%d" % (r2["evidence_strength"], rep2["downgraded"]))

        # N3：同一输入连跑两次 ⇒ 产出逐字节一致（幂等）。
        fixture(tmp, [rec("VR-PRB-003", "direct")],
                [verdict("VR-PRB-003", "direct", "partial", False)])
        _, a = apply_one(tmp, "probe", False)
        with open(os.path.join(tmp, PARTS, "ledger-probe.json"), "w", encoding="utf-8") as f:
            f.write(a)
        _, b = apply_one(tmp, "probe", False)
        bad += probe("N3 连跑两次逐字节一致", a == b,
                     "len=%d vs %d" % (len(a), len(b)))

        # N4：判据有效性反证 —— 用**旧判据**（以当前强度为基准）跑 N1 场景，
        #     必须复现「语义反转」，否则说明本探针无法区分新旧实现（等于恒真）。
        def legacy_marker(cur, sp, first):
            return ("判为 %s（原判 %s），按保守终裁降级" % (sp, cur)
                    if STRENGTH_ORDER.get(sp, 99) < STRENGTH_ORDER.get(cur, 99)
                    else "结论有分歧但未低于原判（复核=%s），保留原强度" % sp)

        legacy = legacy_marker("partial", "partial", "direct")
        new = "判为 partial（原判 direct），按保守终裁降级"
        bad += probe("N4 旧判据复现反转（判据非恒真）",
                     ("未低于原判" in legacy) and ("未低于原判" not in new),
                     "legacy=%r vs fixed=%r" % (legacy[:24], new[:24]))

        # N5：兜底分支必须**可见**——验前强度两处均缺时须置位 basis_fallback（并 WARN），
        #     而有字段时不得置位。旧实现静默退回当前强度（无任何信号）。
        v5 = verdict("VR-PRB-005", "direct", "partial", False)
        v5.pop("first_pass_strength")
        fixture(tmp, [rec("VR-PRB-005", "direct")], [v5])
        rep5, _ = apply_one(tmp, "probe", False)
        fixture(tmp, [rec("VR-PRB-006", "direct")],
                [verdict("VR-PRB-006", "direct", "partial", False)])
        rep6, _ = apply_one(tmp, "probe", False)
        ok = (rep5.get("basis_fallback") == 1 and rep6.get("basis_fallback") == 0)
        bad += probe("N5 兜底分支置位 WARN（有字段时不置位）", ok,
                     "缺字段 basis_fallback=%d / 有字段 basis_fallback=%d"
                     % (rep5.get("basis_fallback", -1), rep6.get("basis_fallback", -1)))

        # N6：agree=true 但复核强度更低 ⇒ 必须降级（旧实现只在 agree=false 时看强度，
        #     此路径会把「同意但证据不足」静默放过、direct 虚高）。同时 second_pass 仍须 passed。
        fixture(tmp, [rec("VR-PRB-007", "direct")],
                [verdict("VR-PRB-007", "direct", "partial", True)])
        rep7, text7 = apply_one(tmp, "probe", False)
        r7 = json.loads(text7)["records"][0]
        ok = (r7["evidence_strength"] == "partial" and rep7["downgraded"] == 1
              and r7["review"]["second_pass"] == "passed"
              and "按保守终裁降级" in r7["evidence_note"])
        bad += probe("N6 agree=true 但强度更低须降级", ok,
                     "strength=%s downgraded=%d second_pass=%s"
                     % (r7["evidence_strength"], rep7["downgraded"],
                        r7["review"]["second_pass"]))

        # N7：agree=false 且复核强度 = 验前强度 ⇒ 仍须降至 partial（否决不得保留 direct）。
        fixture(tmp, [rec("VR-PRB-008", "direct")],
                [verdict("VR-PRB-008", "direct", "direct", False)])
        rep8, text8 = apply_one(tmp, "probe", False)
        r8 = json.loads(text8)["records"][0]
        ok = (r8["evidence_strength"] == "partial" and rep8["downgraded"] == 1
              and "否决归属或结论" in r8["evidence_note"])
        bad += probe("N7 否决须降至 partial（不得保留 direct）", ok,
                     "strength=%s downgraded=%d" % (r8["evidence_strength"], rep8["downgraded"]))

        # N8：agree=true 且复核强度 = 验前强度 ⇒ 不得降级、不得加标记（防「恒降」）。
        fixture(tmp, [rec("VR-PRB-009", "direct")],
                [verdict("VR-PRB-009", "direct", "direct", True)])
        rep9, text9 = apply_one(tmp, "probe", False)
        r9 = json.loads(text9)["records"][0]
        ok = (r9["evidence_strength"] == "direct" and rep9["downgraded"] == 0
              and "【第二路复核】" not in r9["evidence_note"])
        bad += probe("N8 一致且同强度不降级（防恒降）", ok,
                     "strength=%s downgraded=%d" % (r9["evidence_strength"], rep9["downgraded"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("== 负例探针 %d/%d 如期通过 ==" % (8 - bad, 8))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="第二路复核裁决回写")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--slug", help="单本 slug")
    ap.add_argument("--all", action="store_true", help="处理全部已登记书")
    ap.add_argument("--check", action="store_true", help="只读报告，不写")
    ap.add_argument("--negative-test", action="store_true", help="跑 8 条负例探针后退出")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.negative_test:
        print("== 负例探针（幂等判据可信度） ==")
        return negative_test()

    slugs = [args.slug] if args.slug else (list(discover_slugs(root)) if args.all else [])
    if not slugs:
        print("请指定 --slug 或 --all")
        return 2

    print("== 第二路复核裁决回写 ==")
    print("")
    total = {"matched": 0, "passed": 0, "disputed": 0, "downgraded": 0,
             "not_covered": 0, "unmatched": 0, "basis_fallback": 0}
    for slug in slugs:
        rep, text = apply_one(root, slug, args.check)
        print("[%s]" % slug)
        if rep["missing_files"]:
            for m in rep["missing_files"]:
                print("    [SKIP] 缺文件 %s" % m)
            continue
        print("    verdicts=%d matched=%d passed=%d disputed=%d downgraded=%d 已降级复算=%d 未复核的 direct=%d"
              % (rep["verdicts"], rep["matched"], rep["passed"], rep["disputed"],
                 rep["downgraded"], rep["already_downgraded"], rep["not_covered"]))
        if rep["unmatched"]:
            print("    ! verdict 指向不存在的 record_id：%s" % ", ".join(rep["unmatched"][:10]))
        for k in ("matched", "passed", "disputed", "downgraded", "not_covered",
                  "basis_fallback"):
            total[k] += rep[k]
        total["unmatched"] += len(rep["unmatched"])
        if rep.get("basis_fallback"):
            print("    [WARN] %d 条记录走兜底分支（验前强度两处均缺，已退回当前强度判据）"
                  % rep["basis_fallback"])
        if text is not None and not args.check:
            p = os.path.join(resolve(root, PARTS), "ledger-%s.json" % slug)
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print("    wrote %s" % os.path.relpath(p, root))
    print("")
    print("== 汇总 == matched=%d passed=%d disputed=%d downgraded=%d 未复核 direct=%d 悬挂 verdict=%d 兜底判据=%d"
          % (total["matched"], total["passed"], total["disputed"], total["downgraded"],
             total["not_covered"], total["unmatched"], total["basis_fallback"]))
    if args.check:
        print("== --check：未写盘 ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
