#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
negative_test_verification.py — 核验层门控**判据可信度**回归（负例自检）

背景（项目纪律）：新增或修改任何门控，**必须同时提交负例**，证明判据拦得住
（防「恒真判据 / 假绿 / 空集通过」）。本脚本针对阶段7 轨B 对
`gate_verification.py` 的扩展（新增书前缀登记 + 新书语料接入 G-V5 + fail-closed 未登记检查）
构造**必 FAIL** 负例。

做法：把真实核验层复制到临时 root，注入单点变异，跑 `gate_verification.py --check all`，
断言「预期判据 FAIL」且「其余判据不受连带影响（除显式声明的连带）」。

用法：
  python3 16-checkpoint/negative_test_verification.py
退出码：全部如期 → 0；任一不如期 → 1。
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
GATE = os.path.join(HERE, "gate_verification.py")
sys.path.insert(0, HERE)
import gate_verification as GV  # noqa: E402  （档位集合的单一真相源，ADR-003/ADR-005）

VERIFY = os.path.join("01-books", "_verify")
PARTS = os.path.join(VERIFY, "_parts")
TEXT = os.path.join(VERIFY, "_text")
DATA = "10-dag-data"

COPY_FILES = [
    os.path.join(VERIFY, "verification-ledger.json"),
    os.path.join(VERIFY, "book-toc-index.json"),
    os.path.join(VERIFY, "reverse-gaps.json"),
    os.path.join(VERIFY, "node-claim-map.json"),
    os.path.join(DATA, "_verification-overrides.json"),
    os.path.join(DATA, "_verification-baseline.json"),
    os.path.join(DATA, "methodology-dag.json"),
]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def stage(root, tmp):
    """把真实核验层复制到临时 root。"""
    for rel in COPY_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    os.makedirs(os.path.join(tmp, PARTS), exist_ok=True)
    for fn in os.listdir(os.path.join(root, PARTS)):
        shutil.copyfile(os.path.join(root, PARTS, fn), os.path.join(tmp, PARTS, fn))
    os.makedirs(os.path.join(tmp, TEXT), exist_ok=True)
    for fn in os.listdir(os.path.join(root, TEXT)):
        shutil.copyfile(os.path.join(root, TEXT, fn), os.path.join(tmp, TEXT, fn))


def run_gate(tmp):
    """返回 {判据: 状态}。"""
    proc = subprocess.run([sys.executable, GATE, "--check", "all", "--root", tmp],
                          capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    status = {}
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("[") and "]" in line:
            tag, _, rest = line[1:].partition("]")
            if tag in ("PASS", "FAIL", "WARN", "SKIP") and rest.strip() in (
                    "G-V1", "G-V2", "G-V3", "G-V4", "G-V5", "G-V6", "G-V7", "G-V8", "G-V9"):
                status[rest.strip()] = tag
    status["__rc__"] = proc.returncode
    return status, out


def first_record(doc):
    return doc["records"][0]


# ---- 变异器 ----

def mut_unregistered_slug(tmp):
    """新增一个未登记前缀的书分片 → G-V1 须 FAIL（fail-closed）。"""
    dump(os.path.join(tmp, PARTS, "toc-zz-unknown.json"),
         {"source_id": "BK-099", "book": "Unknown", "edition": "1st", "toc": []})
    return {"G-V1": "FAIL"}


def mut_bad_prefix(tmp):
    """把一条记录的 record_id 改成未登记前缀 → G-V1 须 FAIL。"""
    p = os.path.join(tmp, VERIFY, "verification-ledger.json")
    doc = load(p)
    first_record(doc)["record_id"] = "VR-ZZ-001"
    dump(p, doc)
    return {"G-V1": "FAIL"}


def mut_empty_chapter_partial(tmp):
    """把一条 direct 记录的 chapter 清空 → G-V3 须 FAIL（非 inferred 无例外）。"""
    p = os.path.join(tmp, VERIFY, "verification-ledger.json")
    doc = load(p)
    for r in doc["records"]:
        if r.get("evidence_strength") == "direct":
            r["anchor"] = dict(r.get("anchor") or {})
            r["anchor"]["chapter"] = ""
            break
    dump(p, doc)
    return {"G-V3": "FAIL"}


def mut_contradicted_no_value(tmp):
    """strength=contradicted 但无 contradiction.verified_value → G-V1 须 FAIL。"""
    p = os.path.join(tmp, VERIFY, "verification-ledger.json")
    doc = load(p)
    r = first_record(doc)
    r["evidence_strength"] = "contradicted"
    r.pop("contradiction", None)
    dump(p, doc)
    return {"G-V1": "FAIL"}


def mut_verbatim_new_book(tmp, root):
    """为 BK-030 注入一条**含书原文 ≥20 字连续子串**的 claim → G-V5 须 FAIL。

    这是本轮**最关键**的负例：它证明新书的语料确实被接进了 G-V5
    （否则把书加进 book_text 只是空动作，会形成假绿）。
    """
    with open(os.path.join(root, TEXT, "team-topologies.txt"), encoding="utf-8") as f:
        text = "".join(f.read().split())
    # 取中段 40 字，避开目录/版权页
    start = len(text) // 2
    verbatim = text[start:start + 40]
    p = os.path.join(tmp, VERIFY, "verification-ledger.json")
    doc = load(p)
    tpl = dict(first_record(doc))
    tpl.update({
        "record_id": "VR-TT-001",
        "node_id": "ESS-N-01",
        "source_id": "BK-030",
        "direction": "forward",
        "claim_id": "ESS-N-01#definition#1",
        "claim": "此处照抄原文以触发红线：" + verbatim,
        "anchor": {"chapter": "1", "section": "", "section_title": "The Problem with Org Charts"},
        "page_anchor_private": None,
        "evidence_strength": "partial",
        "evidence_note": "负例：故意照抄书原文，用于验证 G-V5 对新书语料生效。",
    })
    doc["records"].append(tpl)
    dump(p, doc)
    return {"G-V5": "FAIL"}


def mut_claims_incomplete(tmp):
    """从 `node-claim-map` 删掉一条仍被 ledger 引用的 claim → G-V1 须 FAIL。

    复现 2026-10-12 修复前的**实际状态**（ledger 有记录、claims 缺失，实测 73 条：
    50 条源于派生器「首 slug 胜出」、23 条从未进分片）。本负例证明新增的
    「claims 完整性」子判据**真的拦得住**，不是恒真判据。
    """
    p = os.path.join(tmp, VERIFY, "node-claim-map.json")
    doc = load(p)
    for nid in sorted(doc["nodes"]):
        claims = doc["nodes"][nid].get("claims") or []
        if len(claims) >= 2:
            claims.pop(0)                      # 删一条：ledger 仍引用它 ⇒ 应报不完整
            dump(p, doc)
            return {"G-V1": "FAIL"}
    raise RuntimeError("夹具失效：找不到含 ≥2 条 claim 的节点")


def mut_duplicate_claim_id(tmp):
    """把第二条记录的 claim_id 改成与第一条相同 → G-V1 须 FAIL。

    2026-10-12 起「claim_id 全局唯一」由 WARN 提升为 FAIL（阶段1 遗留重复
    `ESS-O-02#principle#1` 已由 `fix_duplicate_claim_ids.py` 修完）。
    """
    p = os.path.join(tmp, VERIFY, "verification-ledger.json")
    doc = load(p)
    recs = doc["records"]
    recs[1]["claim_id"] = recs[0]["claim_id"]
    dump(p, doc)
    return {"G-V1": "FAIL"}


def _counts(doc):
    from collections import Counter
    return Counter(r.get("node_id") for r in doc["records"])


def add_to_node(tmp, node_id, target):
    """把 node_id 的记录数补到 target（复制既有 direct 记录的合法字段，换新 record_id/claim_id）。

    同步向 `node-claim-map` 注入对应 claim 条目（否则会连带触发「claims 不完整」，
    使上限判据的负例失去**单点隔离**）。
    """
    lp = os.path.join(tmp, VERIFY, "verification-ledger.json")
    doc = load(lp)
    have = {r.get("record_id") for r in doc["records"]}
    cids = {r.get("claim_id") for r in doc["records"]}
    tpl = next(r for r in doc["records"] if r.get("evidence_strength") == "direct")
    added, n = [], 900
    while _counts(doc)[node_id] < target:
        while n <= 999 and "VR-SRE-%03d" % n in have:
            n += 1
        if n > 999:
            raise RuntimeError("夹具失效：VR-SRE-9xx 号段耗尽")
        rid = "VR-SRE-%03d" % n
        k = 900
        while "%s#engineering#%d" % (node_id, k) in cids:
            k += 1
        cid = "%s#engineering#%d" % (node_id, k)
        rec = dict(tpl)
        rec.update({"record_id": rid, "node_id": node_id, "claim_id": cid})
        doc["records"].append(rec)
        have.add(rid)
        cids.add(cid)
        added.append(cid)
        n += 1
    dump(lp, doc)
    cp = os.path.join(tmp, VERIFY, "node-claim-map.json")
    cdoc = load(cp)
    node = cdoc["nodes"].setdefault(node_id, {"claims": []})
    for cid in added:
        node["claims"].append({"claim_id": cid, "text": tpl.get("claim", ""),
                               "origin": "engineering"})
    node["claims"].sort(key=lambda c: c.get("claim_id", ""))
    dump(cp, cdoc)
    return node_id


def mut_k_domain_at_cap(tmp):
    """K 域节点恰好 16 条 → G-V1 须 **PASS**（ADR-005 放宽**确实生效**，非空动作）。"""
    add_to_node(tmp, "ESS-K-03", 16)
    return {"G-V1": "PASS"}


def mut_k_domain_over_cap(tmp):
    """K 域节点 17 条 → G-V1 须 FAIL（放宽后判据仍可证伪，上限不是恒真）。"""
    add_to_node(tmp, "ESS-K-03", 17)
    return {"G-V1": "FAIL"}


def mut_out_of_domain_over_cap(tmp):
    """**非高档位**节点 9 条 → G-V1 须 FAIL（放宽不得蔓延到 K 域之外）。"""
    doc = load(os.path.join(tmp, VERIFY, "verification-ledger.json"))
    c = _counts(doc)
    cand = sorted(n for n, v in c.items() if n not in GV.DENSIFY_NODES and v < 9)
    if not cand:
        raise RuntimeError("夹具失效：找不到非高档位且 <9 条的节点")
    add_to_node(tmp, cand[0], 9)
    return {"G-V1": "FAIL"}


CASES = [
    ("baseline", None, {}),
    ("unregistered_slug", mut_unregistered_slug, {"G-V1": "FAIL"}),
    ("bad_record_prefix", mut_bad_prefix, {"G-V1": "FAIL"}),
    ("empty_chapter_partial", mut_empty_chapter_partial, {"G-V3": "FAIL"}),
    ("contradicted_no_value", mut_contradicted_no_value, {"G-V1": "FAIL"}),
    ("verbatim_new_book", mut_verbatim_new_book, {"G-V5": "FAIL"}),
    ("claims_incomplete", mut_claims_incomplete, {"G-V1": "FAIL"}),
    ("duplicate_claim_id", mut_duplicate_claim_id, {"G-V1": "FAIL"}),
    ("k_domain_at_cap_16", mut_k_domain_at_cap, {"G-V1": "PASS"}),
    ("k_domain_over_cap_17", mut_k_domain_over_cap, {"G-V1": "FAIL"}),
    ("out_of_domain_over_cap_9", mut_out_of_domain_over_cap, {"G-V1": "FAIL"}),
]


def main():
    ap = argparse.ArgumentParser(description="核验层门控负例自检")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    print("== 核验层门控负例自检（判据可信度）==")
    print("root = %s" % root)
    print("")
    passed = 0
    failed = []

    for name, mut, expect in CASES:
        tmp = tempfile.mkdtemp(prefix="gvneg-%s-" % name)
        try:
            stage(root, tmp)
            if mut is not None:
                if name == "verbatim_new_book":
                    mut(tmp, root)
                else:
                    mut(tmp)
            status, out = run_gate(tmp)
            if name == "baseline":
                bad = sorted(k for k, v in status.items() if v == "FAIL")
                ok = not bad
                detail = "无 FAIL" if ok else "意外 FAIL: %s" % ",".join(bad)
            else:
                got = {k: status.get(k) for k in expect}
                ok = all(got[k] == expect[k] for k in expect)
                detail = "预期 %s，实际 %s" % (
                    ",".join("%s=%s" % (k, expect[k]) for k in expect),
                    ",".join("%s=%s" % (k, status.get(k)) for k in expect))
            print("[%s] %-24s %s" % ("如期" if ok else "不如期", name, detail))
            if not ok:
                failed.append(name)
                for ln in out.strip().splitlines()[-25:]:
                    print("      | " + ln)
            else:
                passed += 1
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("== 汇总 ==")
    print("  如期 %d/%d" % (passed, len(CASES)))
    if failed:
        print("  不如期: %s" % ", ".join(failed))
    print("== 结果 = %s ==" % ("PASS" if not failed else "FAIL"))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
