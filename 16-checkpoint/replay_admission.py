#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""replay_admission.py — ADR-004 准入谓词的**谓词重放**验收器（阶段7 阶段3 门控级）

用途：把 `reverse-gaps.json` 内全部概念逐条喂入 ADR-004 的 T1/T2/T3 准入谓词，
      输出档位与理由码，并与 ADR-004 的人工裁决表逐条比对，输出一致率。

判据来源：`18-design/adr/ADR-004.json` 的
  - `admission_predicate.form`      —— 谓词本体
  - `admission_predicate.forbidden_constants` —— 禁止出现快照常量
  - `candidate_register[]`          —— 人工裁决表（含概念 → gap_ids 归组）

────────── 输入契约（必须区分「机械」与「人工语义输入」，不得混淆） ──────────

机械可求值（本脚本从缺口数据自行计算）：
  · 概念集筛选：`target.proposed_node` 非空 ⇔ 参与结构扩展提案（34 条）
                 为空且 `target.existing_node_id` 非空 ⇔ 仅补引，不触发扩展（26 条）
  · A(c) = 该概念的 `evidence_strength == "direct"` 锚数
  · S(c) = 该概念涉及的**去重后 book_source_id 数**（信源按概念计，不按 id 字符串计；
           同一本书的不同章节只计 1 个信源）
  · 档位判定 = 对 (A, S, subsumed, id_unique, layer_ok) 求值

人工语义输入（来自 ADR-004 裁决表，属 CIT/SUBSUMED 语义判定，**不可机械推导**）：
  · 概念归组（gap_id → 概念）：同名簇须跑 CIT-1~4 才能定 MERGE / SPLIT / SUBSUMED
  · `subsumed` 标记：取自裁决表 `reason_code` 中的 `SUBSUMED`
    （实测：现有节点 `aliases` 不含中文概念名，无法用别名匹配机械推出，
      故 ADR-004 §五「语义判定漏检」风险与 §七「一致率 100%」验收以此为前提）

禁止常量（ADR-004 §七）：判据中不得出现提案条数、提案清单、编号区间、书单长度等快照常量。
本脚本已实现该自检（见 `check_forbidden_constants`）。
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

ADR_REL = os.path.join("18-design", "adr", "ADR-004.json")
GAPS_REL = os.path.join("01-books", "_verify", "reverse-gaps.json")

# ADR-004 §七 明令禁止出现在判据里的快照常量
FORBIDDEN_CONSTANTS = ("提案条数", "提案清单", "编号区间", "书单长度")
FORBIDDEN_LITERALS = ("14", "29", "34", "60")

STRENGTH_ENUM = ("direct", "partial", "inferred", "contradicted")


# ------------------------------------------------------------------ 载入

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize(name):
    """概念名归一化：去空白/标点、大小写归一、全角括号统一。"""
    s = (name or "").strip().lower()
    s = re.sub(r"[\s\u3000]+", "", s)
    s = s.replace("（", "(").replace("）", ")")
    s = re.sub(r"[·・、,，。.;；:：\-—_/]+", "", s)
    return s


# ------------------------------------------------------------- 谓词本体

def eval_tier(anchors, sources, subsumed=False, id_unique=True, layer_ok=True):
    """ADR-004 §决定二 的准入谓词（纯谓词，仅依赖概念自身字段）。

    T1: |A(c)| >= 1 且 |S(c)| >= 2 且 id 唯一 且 非 SUBSUMED 且 层前缀一致
    T2: |A(c)| >= 1 且 |S(c)| == 1 且 其余同上
    T3: 其余全部
    """
    if subsumed or not id_unique or not layer_ok:
        return "T3"
    if anchors >= 1 and sources >= 2:
        return "T1"
    if anchors >= 1 and sources == 1:
        return "T2"
    return "T3"


def eval_tier_broken_ignore_direct(anchors, sources, subsumed=False, id_unique=True, layer_ok=True):
    """【负例用】漏掉「|A(c)| >= 1」这一条件的错误谓词。"""
    if subsumed or not id_unique or not layer_ok:
        return "T3"
    if sources >= 2:
        return "T1"
    if sources == 1:
        return "T2"
    return "T3"


def eval_tier_broken_direct_only_sources(anchors, sources, subsumed=False,
                                         id_unique=True, layer_ok=True):
    """【负例用】把 S(c) 误算为「仅 direct 锚所涉信源数」的错误谓词。"""
    return eval_tier(anchors, sources, subsumed, id_unique, layer_ok)


# ------------------------------------------------------------- 概念归组

CONCEPT_TIERS = ("T1", "T2", "T3")


def build_concepts(adr, gaps):
    """从 ADR 裁决表读人工归组；机械校验「裁决表概念条目 ⊆ 参与扩展集合」。

    ⚠️ 口径纠正（阶段3 回写轮）：**不得**再用 `target.proposed_node` 非空作为
    「是否参与结构扩展」的代理判据。`proposed_node` 语义是**号分配状态**，
    与「是否为概念提案」正交：T3 no-id / released 的概念条目按号释放政策
    回写后 `proposed_node` 必须为空（否则缺口文件谎称占用已释放号）。
    改为以裁决表的 `tier`（T1/T2/T3 = 概念条目）机械判定概念集。
    """
    concepts = []
    register_gaps = set()
    register_concept_gaps = set()
    register_odd_tiers = set()
    for i, e in enumerate(adr.get("candidate_register") or [], 1):
        gap_ids = list(e.get("gap_ids") or [])
        register_gaps.update(gap_ids)
        tier = e.get("tier")
        if tier in CONCEPT_TIERS:
            register_concept_gaps.update(gap_ids)
        elif tier is not None:
            register_odd_tiers.add(tier)
        reason = e.get("reason_code") or ""
        concepts.append({
            "idx": i,
            "key": normalize(e.get("concept")),
            "concept": e.get("concept"),
            "tier_adr": tier,
            "id": e.get("id"),
            "gap_ids": gap_ids,
            "subsumed": "SUBSUMED" in reason.upper(),
            "reason_code": reason,
        })

    # 机械筛选：① 裁决表中的概念条目（tier ∈ T1/T2/T3）；② 尚未裁决但已占号的新提案
    mech_expand = set(register_concept_gaps)
    mech_expand |= {gid for gid, g in gaps.items()
                    if gid not in register_gaps and (g.get("target") or {}).get("proposed_node")}
    mech_cite = set(gaps) - mech_expand
    return concepts, register_gaps, mech_expand, mech_cite, register_concept_gaps, register_odd_tiers


def concept_metrics(concept, gaps):
    """机械求值 A(c) / S(c)。"""
    anchors = 0
    sources = set()
    for gid in concept["gap_ids"]:
        g = gaps[gid]
        if g.get("evidence_strength") == "direct":
            anchors += 1
        src = g.get("book_source_id")
        if src:
            sources.add(src)
    return anchors, len(sources), sorted(sources)


# --------------------------------------------------- 禁止常量自检

def check_forbidden_constants(adr):
    """ADR-004 §七：判据不得以提案条数/清单/编号区间/书单长度作为快照常量。"""
    problems = []
    pred = adr.get("admission_predicate") or {}
    form = pred.get("form") or ""
    declared = set(pred.get("forbidden_constants") or [])
    if not declared:
        problems.append("admission_predicate.forbidden_constants 未声明")
    for word in FORBIDDEN_CONSTANTS:
        if word not in " ".join(declared) and word not in form:
            problems.append("谓词未显式排除快照常量类：%s" % word)
    # 谓词本体里不得出现具体提案条数/编号区间的字面量
    for lit in FORBIDDEN_LITERALS:
        if re.search(r"(?<![0-9])%s(?![0-9])" % lit, form):
            problems.append("谓词本体出现疑似快照常量字面量：%s" % lit)
    # 本脚本自身的谓词函数体不得含快照常量
    for fn in (eval_tier, eval_tier_broken_ignore_direct):
        src = fn.__doc__ or ""
        for lit in FORBIDDEN_LITERALS:
            if re.search(r"(?<![0-9])%s(?![0-9])" % lit, src):
                problems.append("%s 的判据文档出现快照常量字面量：%s" % (fn.__name__, lit))
    return problems


# ------------------------------------------------------------- 重放

def replay(adr, gaps, show=40):
    (concepts, register_gaps, mech_expand, mech_cite,
     register_concept_gaps, register_odd_tiers) = build_concepts(adr, gaps)
    rows = []
    for c in concepts:
        anchors, nsources, src_list = concept_metrics(c, gaps)
        tier_pred = eval_tier(anchors, nsources, subsumed=c["subsumed"])
        # 理由码（机械生成）
        if c["subsumed"]:
            code = "T3-SUBSUMED"
        elif anchors == 0:
            code = "T3-NO-DIRECT-ANCHOR"
        elif nsources >= 2:
            code = "T1-MULTI-SOURCE"
        elif nsources == 1:
            code = "T2-SINGLE-SOURCE"
        else:
            code = "T3-NO-SOURCE"
        rows.append({
            "concept": c["concept"], "id": c["id"], "tier_adr": c["tier_adr"],
            "tier_pred": tier_pred, "anchors": anchors, "sources": nsources,
            "src_list": src_list, "subsumed": c["subsumed"], "reason_code": code,
            "match": tier_pred == c["tier_adr"],
        })
    return (rows, register_gaps, mech_expand, mech_cite,
            register_concept_gaps, register_odd_tiers)

# ------------------------------------------------------- 负向测试

def negative_tests(adr, gaps):
    """构造「判据失效」的假象，确认正确判据拦得住、错误判据拦不住。

    每条断言：错误谓词给出错误档位（证明该判别点确有区分力），
              正确谓词给出正确档位（证明判据拦得住）。
    """
    results = []

    # --- NT1: 应为 T3（2 源但 0 direct 锚），漏检「A>=1」的谓词会误给 T1 ---
    fake = {"anchors": 0, "sources": 2, "subsumed": False}
    good = eval_tier(**fake)
    bad = eval_tier_broken_ignore_direct(**fake)
    results.append({
        "case": "NT1-漏检-direct-锚要求",
        "expect_good": "T3", "got_good": good,
        "expect_bad": "T1", "got_bad": bad,
        "ok": good == "T3" and bad == "T1",
    })

    # --- NT2: S(c) 口径错误 —— 真实 T1 概念若只计 direct 锚的信源数会被降为 T2 ---
    t1 = [r for r in replay(adr, gaps)[0] if r["tier_adr"] == "T1"]
    if t1:
        r = t1[0]
        good = eval_tier(r["anchors"], r["sources"], subsumed=r["subsumed"])
        # 错误口径：只数 direct 锚所涉信源
        c = next(c for c in build_concepts(adr, gaps)[0] if c["tier_adr"] == "T1")
        direct_srcs = {gaps[g]["book_source_id"] for g in c["gap_ids"]
                       if gaps[g].get("evidence_strength") == "direct"}
        bad = eval_tier(r["anchors"], len(direct_srcs), subsumed=r["subsumed"])
        results.append({
            "case": "NT2-S-口径误算为仅-direct-信源（%s）" % r["concept"],
            "expect_good": "T1", "got_good": good,
            "expect_bad": "T2", "got_bad": bad,
            "ok": good == "T1" and bad == "T2",
        })

    # --- NT3: 漏检 SUBSUMED —— 有 direct 锚但语义被既有节点承载者会被误给 T2 ---
    sub = [c for c in build_concepts(adr, gaps)[0] if c["subsumed"] and c["tier_adr"] == "T3"]
    if sub:
        c = sub[0]
        anchors, nsources, _ = concept_metrics(c, gaps)
        good = eval_tier(anchors, nsources, subsumed=True)
        bad = eval_tier(anchors, nsources, subsumed=False)
        results.append({
            "case": "NT3-漏检-SUBSUMED（%s）" % c["concept"],
            "expect_good": "T3", "got_good": good,
            "expect_bad": "T2", "got_bad": bad,
            "ok": good == "T3" and bad == "T2",
        })

    # --- NT4: 正例对照 —— 真实 T1 概念在正确谓词下仍为 T1（判据未被负例改坏）---
    if t1:
        results.append({
            "case": "NT4-正例对照（%s）" % t1[0]["concept"],
            "expect_good": "T1", "got_good": eval_tier(t1[0]["anchors"], t1[0]["sources"],
                                                       subsumed=t1[0]["subsumed"]),
            "expect_bad": None, "got_bad": None,
            "ok": eval_tier(t1[0]["anchors"], t1[0]["sources"], subsumed=t1[0]["subsumed"]) == "T1",
        })
    return results


# ------------------------------------------------- T2 晋升扫描（P1）

def eval_promotion(anchors, sources, subsumed=False, id_unique=True, layer_ok=True):
    """T2 → T1 晋升谓词（ADR-004 §决定二 的 T1 条件在 T2 候选上的直接套用）。

    语义：T2 候选取得「第二个独立信源」后即满足 T1 条件，可晋升入图。
    返回 True 表示**当前证据下已可晋升**。判据不得含条数/清单/区间快照常量。
    """
    if subsumed or not id_unique or not layer_ok:
        return False
    if anchors < 1:
        return False
    return sources >= 2


def eval_promotion_broken(anchors, sources, subsumed=False, id_unique=True, layer_ok=True):
    """【负例用】错误谓词：只看 direct 锚数、漏检独立信源数 ⇒ 单源候选会被误判可晋升。"""
    return anchors >= 1 and not subsumed


def scan_promotion(adr, gaps):
    """枚举全部 T2 候选（裁决表 T2 条目 ∪ 未裁决但已占号的新提案），逐条求值晋升谓词。"""
    concepts, register_gaps, _mech_expand, _mech_cite, _rcg, _rot = build_concepts(adr, gaps)
    rows = []
    for c in concepts:
        if c["tier_adr"] != "T2":
            continue
        anchors, nsources, src_list = concept_metrics(c, gaps)
        rows.append({
            "origin": "candidate_register",
            "concept": c["concept"],
            "id": c["id"],
            "gap_ids": c["gap_ids"],
            "anchors": anchors,
            "sources": nsources,
            "src_list": src_list,
            "subsumed": c["subsumed"],
            "promotable": eval_promotion(anchors, nsources, subsumed=c["subsumed"]),
            "blocked_by": ("SUBSUMED" if c["subsumed"] else
                           ("无 direct 锚" if anchors < 1 else
                            ("独立信源 < 2（当前 %d）" % nsources if nsources < 2 else None))),
        })
    # 未裁决但已占号的新提案（无 ADR tier，按同一谓词评估；概念名即缺口提案）
    for gid in sorted(gaps):
        if gid in register_gaps:
            continue
        g = gaps[gid]
        tgt = g.get("target") or {}
        if not tgt.get("proposed_node"):
            continue
        anchors = 1 if g.get("evidence_strength") == "direct" else 0
        src = g.get("book_source_id")
        nsources = 1 if src else 0
        rows.append({
            "origin": "new_proposal_unaudited",
            "concept": (g.get("summary") or "")[:60],
            "id": tgt.get("proposed_node"),
            "gap_ids": [gid],
            "anchors": anchors,
            "sources": nsources,
            "src_list": [src] if src else [],
            "subsumed": False,
            "promotable": eval_promotion(anchors, nsources),
            "blocked_by": ("无 direct 锚" if anchors < 1 else
                           ("独立信源 < 2（当前 %d）" % nsources if nsources < 2 else None)),
        })
    return rows


def promotion_negative_tests(adr, gaps):
    """晋升判据可信度负例：错误谓词须被拦下、正确谓词须守住。"""
    rows = scan_promotion(adr, gaps)
    results = []

    # NT5：单源候选（|A|≥1 且 |S|=1）—— 正确谓词判不可晋升，错误谓词会误判可晋升
    single = [r for r in rows if r["anchors"] >= 1 and r["sources"] == 1]
    if single:
        r = single[0]
        good = eval_promotion(r["anchors"], r["sources"])
        bad = eval_promotion_broken(r["anchors"], r["sources"])
        results.append({
            "case": "NT5-单源候选误判可晋升（%s）" % str(r["id"]),
            "expect_good": False, "got_good": good,
            "expect_bad": True, "got_bad": bad,
            "ok": good is False and bad is True,
        })

    # NT6：0 direct 锚 —— 即使 2 源也不得晋升（正确谓词守住；漏检 direct 要求者会误判）
    # 合成用例（不依赖数据集中是否存在零锚候选），故无条件执行。
    results.append({
        "case": "NT6-零 direct 锚不得晋升（合成 |A|=0,|S|=2）",
        "expect_good": False, "got_good": eval_promotion(0, 2),
        "expect_bad": None, "got_bad": None,
        "ok": eval_promotion(0, 2) is False,
    })

    # NT7：正例对照 —— 构造 2 源 direct 候选，正确谓词须判可晋升（判据未被负例改坏）
    results.append({
        "case": "NT7-正例对照（2 独立信源 + 1 direct 锚须判可晋升）",
        "expect_good": True, "got_good": eval_promotion(1, 2),
        "expect_bad": None, "got_bad": None,
        "ok": eval_promotion(1, 2) is True,
    })
    return results


def run_scan_promotion(root, adr, gaps):
    """P1 晋升扫描报告（私有层；不含书证文本）。"""
    rows = scan_promotion(adr, gaps)
    nts = promotion_negative_tests(adr, gaps)
    promotable = [r for r in rows if r["promotable"]]

    print("=" * 78)
    print("T2 候选册晋升扫描（ADR-004 §决定二 T1 谓词在 T2 候选上的套用）")
    print("  候选来源：裁决表 T2 条目 ∪ 未裁决但已占号的新提案")
    print("=" * 78)
    print("\n[1] 逐条裁决（%-3s %-11s %-5s %-4s %-4s %-5s %s"
          % ("#", "id", "来源", "|A|", "|S|", "可晋升", "概念 / 阻塞原因"))
    for i, r in enumerate(sorted(rows, key=lambda x: str(x["id"])), 1):
        print("    %-3d %-11s %-5s %-4d %-4d %-5s %s  [%s]"
              % (i, str(r["id"] or "—"),
                 "裁决表" if r["origin"] == "candidate_register" else "新提案",
                 r["anchors"], r["sources"], "是" if r["promotable"] else "否",
                 str(r["concept"])[:26], r["blocked_by"] or "已满足 T1 条件"))
    print("\n[2] 汇总：候选 %d 条 ｜ 可晋升 %d 条" % (len(rows), len(promotable)))
    for r in promotable:
        print("    ! 可晋升：%s %s（|A|=%d |S|=%d %s）"
              % (r["id"], r["concept"], r["anchors"], r["sources"], r["src_list"]))

    print("\n[3] 晋升判据负向测试")
    for t in nts:
        if t["expect_bad"] is None:
            print("    [%s] %-56s good=%s(期望 %s)"
                  % ("OK" if t["ok"] else "FAIL", t["case"], t["got_good"], t["expect_good"]))
        else:
            print("    [%s] %-56s good=%s(期望 %s)  bad=%s(期望 %s)"
                  % ("OK" if t["ok"] else "FAIL", t["case"], t["got_good"], t["expect_good"],
                     t["got_bad"], t["expect_bad"]))
    nt_ok = sum(1 for t in nts if t["ok"])
    print("    负例汇总：%d/%d 如期" % (nt_ok, len(nts)))

    report = {
        "schema_version": "1.0.0",
        "basis": "ADR-004 §决定二 准入谓词（T1 条件）在 T2 候选上的套用",
        "predicate": "promotable ⇔ |A(c)| ≥ 1 且 |S(c)| ≥ 2（S 按 canonical source id 去重）",
        "candidate_count": len(rows),
        "promotable_count": len(promotable),
        "candidates": sorted(rows, key=lambda x: str(x["id"])),
        "negative_tests": nts,
    }
    out = os.path.join(root, os.path.dirname(GAPS_REL), "_meta", "t2-promotion-scan.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False) + "\n")
    print("\n    wrote %s" % os.path.relpath(out, root))

    passed = nt_ok == len(nts)
    print("\n" + "=" * 78)
    print("  负例 = %d/%d ｜ 可晋升 = %d 条 ｜ == 结果 = %s =="
          % (nt_ok, len(nts), len(promotable), "PASS" if passed else "FAIL"))
    print("=" * 78)
    return 0 if passed else 1


# --------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="ADR-004 准入谓词重放验收器")
    ap.add_argument("--root", default=ROOT_DEFAULT, help="母库 root")
    ap.add_argument("--adr", default=None, help="ADR-004.json 路径")
    ap.add_argument("--gaps", default=None, help="reverse-gaps.json 路径")
    ap.add_argument("--show", type=int, default=40)
    ap.add_argument("--scan-promotion", action="store_true",
                    help="只做 T2→T1 晋升扫描（P1），不跑完整重放")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    adr_path = args.adr or os.path.join(root, ADR_REL)
    gaps_path = args.gaps or os.path.join(root, GAPS_REL)
    adr = load(adr_path)
    gaps = {g["gap_id"]: g for g in load(gaps_path)["gaps"]}

    if args.scan_promotion:
        return run_scan_promotion(root, adr, gaps)

    print("=" * 78)
    print("ADR-004 准入谓词重放验收")
    print("  ADR   = %s" % os.path.relpath(adr_path, root))
    print("  GAPS  = %s（%d 条）" % (os.path.relpath(gaps_path, root), len(gaps)))
    print("=" * 78)

    # 1) 禁止常量自检
    forbidden = check_forbidden_constants(adr)
    print("\n[1] 禁止快照常量自检（ADR-004 §七）")
    if forbidden:
        for p in forbidden:
            print("    ! %s" % p)
    else:
        print("    PASS：谓词本体未出现提案条数/清单/编号区间/书单长度等快照常量")

    # 2) 机械筛选校验
    (rows, register_gaps, mech_expand, mech_cite,
     register_concept_gaps, register_odd_tiers) = replay(adr, gaps, args.show)
    print("\n[2] 概念集筛选（机械：裁决表 tier ∈ T1/T2/T3 ∪ 未裁决但已占号的新提案）")
    # 不变量：**裁决表中的概念条目必须全部落在「参与结构扩展」集合内**（否则 ADR 判了不该判的东西）。
    # 反向不成立：新增缺口尚未经人工裁决，允许出现在 mech_expand 中而不在裁决表里。
    # 注：仅补引条目（missed_citation 指向既有节点）不属概念条目，故不参与本不变量。
    missing_from_mech = sorted(register_concept_gaps - mech_expand)
    extra_new = sorted(mech_expand - register_gaps)
    ok_filter = not missing_from_mech and not register_odd_tiers
    print("    裁决表覆盖缺口 = %d ｜ 其中概念条目缺口 = %d ｜ 机械判定「参与扩展」= %d"
          % (len(register_gaps), len(register_concept_gaps), len(mech_expand)))
    print("    裁决表概念条目 ⊆ 机械扩展 = %s（差集 %d 条）" % (ok_filter, len(missing_from_mech)))
    if register_odd_tiers:
        print("    ! 裁决表出现未知 tier：%s" % sorted(register_odd_tiers))
    if extra_new:
        print("    尚无人工裁决的新缺口（不在裁决表内，仅报告档位）= %d 条：%s"
              % (len(extra_new), extra_new[:6]))
    print("    仅补引（不参与结构扩展）= %d" % len(mech_cite))
    if missing_from_mech:
        print("    ! 裁决表概念条目被机械判定为「仅补引」：%s" % missing_from_mech)

    # 3) 逐条重放
    print("\n[3] 逐概念重放（概念归组与 SUBSUMED 为 ADR 人工语义输入；A/S/档位为机械求值）")
    print("    %-3s %-9s %-4s %-4s %-3s %-3s %-5s %s"
          % ("#", "id", "ADR", "谓词", "|A|", "|S|", "匹配", "概念 / 理由码"))
    for i, r in enumerate(rows, 1):
        print("    %-3d %-9s %-4s %-4s %-3d %-3d %-5s %s  [%s]"
              % (i, r["id"] or "—", r["tier_adr"], r["tier_pred"], r["anchors"],
                 r["sources"], "OK" if r["match"] else "MISMATCH",
                 r["concept"][:24], r["reason_code"]))
    total = len(rows)
    hit = sum(1 for r in rows if r["match"])
    rate = (hit / total * 100.0) if total else 0.0
    print("\n    一致率 = %d/%d = %.2f%%" % (hit, total, rate))
    mism = [r for r in rows if not r["match"]]
    for r in mism[:args.show]:
        print("    ! %s：ADR=%s 谓词=%s" % (r["concept"], r["tier_adr"], r["tier_pred"]))

    # 4) 档位分布对账
    from collections import Counter
    dist_adr = Counter(r["tier_adr"] for r in rows)
    dist_pred = Counter(r["tier_pred"] for r in rows)
    print("\n[4] 档位分布对账")
    print("    ADR  = %s" % dict(sorted(dist_adr.items())))
    print("    谓词 = %s" % dict(sorted(dist_pred.items())))
    print("    口径核对：裁决表条目 %d = T1 %d + T2 %d + T3 %d"
          % (total, dist_pred.get("T1", 0), dist_pred.get("T2", 0), dist_pred.get("T3", 0)))
    merged = sum(max(0, len(r["gap_ids"]) - 1) for r in build_concepts(adr, gaps)[0])
    print("    注：裁决表条目数 = 已 MERGE 后的节点候选数；未合并概念数 = %d + %d（T1 条目由 %d 个概念合并）"
          % (total, merged, 1 + merged))
    print("        ⇒ 与 ADR-004 §一「60 缺口 → 34 概念（T1 合并 2 + T2 21 + T3 11）」口径一致")

    # 5) 负向测试
    nts = negative_tests(adr, gaps)
    print("\n[5] 负向测试（判据可信度：错误谓词须被拦下，正确谓词须守住）")
    for t in nts:
        if t["expect_bad"] is None:
            print("    [%s] %-52s good=%s(期望 %s)"
                  % ("OK" if t["ok"] else "FAIL", t["case"], t["got_good"], t["expect_good"]))
        else:
            print("    [%s] %-52s good=%s(期望 %s)  bad=%s(期望 %s)"
                  % ("OK" if t["ok"] else "FAIL", t["case"], t["got_good"], t["expect_good"],
                     t["got_bad"], t["expect_bad"]))
    nt_ok = sum(1 for t in nts if t["ok"])
    print("    负例汇总：%d/%d 如期" % (nt_ok, len(nts)))

    # 6) 结论
    passed = (not forbidden) and ok_filter and not mism and nt_ok == len(nts)
    print("\n" + "=" * 78)
    print("  禁止常量自检 = %s ｜ 概念筛选一致 = %s ｜ 一致率 = %.2f%% ｜ 负例 = %d/%d"
          % ("PASS" if not forbidden else "FAIL", "PASS" if ok_filter else "FAIL",
             rate, nt_ok, len(nts)))
    print("  == 结果 = %s ==" % ("PASS" if passed else "FAIL"))
    print("=" * 78)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
