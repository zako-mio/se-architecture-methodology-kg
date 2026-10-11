#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
negative_test_densify.py — 阶段2 门控负向测试（判据可信度自检）

目的：证明 G-D1..G-D5 与 G-V9 **真的拦得住**违规，防止恒真判据 / 假绿。
做法：在临时 scratch root 中复刻最小夹具（含 git HEAD 正文基线），逐条注入负例，
      断言对应判据 FAIL；随后注入正例，断言 PASS。

用法：
  python3 16-checkpoint/negative_test_densify.py            # 跑全部负例
  python3 16-checkpoint/negative_test_densify.py --keep     # 保留 scratch（排障用）
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
CHECKPOINT = HERE

SEGMENTS = ("definition", "principle", "mechanism", "engineering", "tradeoff")
# 用一个真实参与节点构造夹具
FIXTURE_NODE = "ESS-G-04"
FIXTURE_CLAIM = "ESS-G-04#principle#1"
FIXTURE_EV = "EV-FIX-001"
FIXTURE_EV2 = "EV-FIX-002"
FIXTURE_CLAIM2 = "ESS-G-04#mechanism#2"
FIXTURE_BASE = 2600
LONG_BODY = "本段为负向测试夹具正文，用于验证增密门控的判据可信度。" * 85   # ≈ 2200 字
BODY_MED = "夹具中段正文。" * 105                    # ≈ 630 字
CORPUS_SENTENCE = "软件架构是系统的基本组织结构，包含组件、组件之间的关系以及二者之间的约束。"  # 用于 G-D4 命中


def sh(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("cmd failed: %s\n%s\n%s" % (cmd, r.stdout, r.stderr))
    return r


def build_scratch(real_root, scratch):
    """复刻最小夹具：dag + baseline + ledger + claims + precheck + evidence + write。"""
    def cp(rel, dest_rel=None):
        src = os.path.join(real_root, rel)
        dst = os.path.join(scratch, dest_rel or rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    # 真实产物（提供参与节点集、ledger、claims 结构）
    cp(os.path.join("10-dag-data", "methodology-dag.json"))
    cp(os.path.join("10-dag-data", "_verification-baseline.json"))
    cp(os.path.join("10-dag-data", "node-content.json"))
    cp(os.path.join("01-books", "_verify", "verification-ledger.json"))
    cp(os.path.join("01-books", "_verify", "node-claim-map.json"))

    dens = os.path.join(scratch, "01-books", "_verify", "_densify")
    os.makedirs(dens, exist_ok=True)

    # 语料（G-D4 需要；放一句会被命中的原文）
    text_dir = os.path.join(scratch, "01-books", "_verify", "_text")
    os.makedirs(text_dir, exist_ok=True)
    with open(os.path.join(text_dir, "saip.txt"), "w", encoding="utf-8") as f:
        f.write(CORPUS_SENTENCE + "\n")

    # precheck（仅需 nodes 映射的 body_shard / claims_target_slug）
    pre = {"meta": {}, "summary": {}, "nodes": {
        FIXTURE_NODE: {"node_id": FIXTURE_NODE,
                       "body_shard": os.path.join("10-dag-data", "_parts", "W1-M.json"),
                       "claims_target_slug": "saip",
                       "claims_action": "create_new_node_key",
                       "baseline_chars": 2600,
                       "missing_segments": list(SEGMENTS)}}}
    with open(os.path.join(dens, "precheck-coverage.json"), "w", encoding="utf-8") as f:
        json.dump(pre, f, ensure_ascii=False, indent=2)

    # evidence
    ev = {"meta": {"schema_version": "1.0.0", "slug": "saip"}, "items": [
        {"evidence_id": FIXTURE_EV, "node_id": FIXTURE_NODE, "origin": "principle",
         "claim_id": FIXTURE_CLAIM, "is_new": False, "text": "夹具素材",
         "anchor": {"chapter": "1", "section": "1.1", "section_title": "T"},
         "proposed_strength": "direct", "read_scope": "fixture"},
        {"evidence_id": FIXTURE_EV2, "node_id": FIXTURE_NODE, "origin": "mechanism",
         "claim_id": FIXTURE_CLAIM2, "is_new": False, "text": "夹具素材二",
         "anchor": {"chapter": "1", "section": "1.2", "section_title": "T2"},
         "proposed_strength": "direct", "read_scope": "fixture"}]}
    with open(os.path.join(dens, "evidence-saip.json"), "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=2)

    # 正文分片（W1-M 含 ESS-M-05 等真实节点；此处追加夹具节点）
    parts_dir = os.path.join(scratch, "10-dag-data", "_parts")
    os.makedirs(parts_dir, exist_ok=True)
    shutil.copy2(os.path.join(real_root, "10-dag-data", "_parts", "W1-M.json"),
                 os.path.join(parts_dir, "W1-M.json"))

    # 夹具自洽：把 node-content.json 的 char_count 与 dag HEAD 正文都设为夹具基线 2600，
    # 否则 G-D2 会用真实基线（1563）算出过大的增量而误判。
    nc_p = os.path.join(scratch, "10-dag-data", "node-content.json")
    nc = json.load(open(nc_p, encoding="utf-8"))
    for e in nc.get("node_contents", []):
        if e["id"] == FIXTURE_NODE:
            e["char_count"] = FIXTURE_BASE
    json.dump(nc, open(nc_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    dag_p = os.path.join(scratch, "10-dag-data", "methodology-dag.json")
    dag = json.load(open(dag_p, encoding="utf-8"))
    for n in dag.get("nodes", []):
        if n["id"] == FIXTURE_NODE:
            # 基线总字数 = 2600（与 FIXTURE_BASE 一致）
            n["definition"] = "基线定义。" * 130                      # 650
            n["detail"] = {k: "基线正文。" * 100 for k in SEGMENTS[1:]}  # 4×500=2000
    json.dump(dag, open(dag_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    write_fixture_write(dens, clean=True)
    return dens


def write_fixture_write(dens, clean=True, **overrides):
    """写入夹具 write-<node>.json；clean=True 时为合规正例。"""
    seg = {}
    for i, s in enumerate(SEGMENTS):
        seg[s] = ("定义段。" if i == 0 else BODY_MED) if clean else "短。"
    doc = {
        "node_id": FIXTURE_NODE,
        "segments": overrides.get("segments", seg),
        "provenance": overrides.get("provenance", {s: [FIXTURE_EV, FIXTURE_EV2] for s in SEGMENTS}),
        "new_claims": overrides.get("new_claims", []),
        "baseline_chars": 2600,
        "final_chars": sum(len(v) for v in (overrides.get("segments", seg)).values()),
        "writer": "w-nodetypes-negtest",
        "review_date": "2026-09-11",
    }
    p = os.path.join(dens, "write-%s.json" % FIXTURE_NODE)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return p


def run_gate(root, criteria, nodes=""):
    cmd = [sys.executable, os.path.join(CHECKPOINT, "gate_densify.py"),
           "--check", criteria, "--root", root]
    if nodes:
        cmd += ["--nodes", nodes]
    r = sh(cmd, check=False)
    return r.returncode, r.stdout


def run_gate_v(root, criteria):
    r = sh([sys.executable, os.path.join(CHECKPOINT, "gate_verification.py"),
            "--check", criteria, "--root", root], check=False)
    return r.returncode, r.stdout


def main():
    ap = argparse.ArgumentParser(description="阶段2 门控负向测试")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()
    real_root = os.path.abspath(args.root)
    scratch = tempfile.mkdtemp(prefix="densify-negtest-")
    results = []
    try:
        dens = build_scratch(real_root, scratch)

        # 基线：把 scratch 的 dag 提交为 git HEAD（供 G-D3/G-D5 正文对账）
        sh(["git", "init", "-q"], cwd=scratch)
        sh(["git", "config", "user.email", "t@example.com"], cwd=scratch)
        sh(["git", "config", "user.name", "t"], cwd=scratch)
        sh(["git", "add", "-A"], cwd=scratch)
        sh(["git", "commit", "-qm", "baseline"], cwd=scratch)

        def case(name, criteria, expect_fail, mutate, gate="densify", nodes=""):
            mutate()
            if gate == "densify":
                rc, out = run_gate(scratch, criteria, nodes=nodes)
            else:
                rc, out = run_gate_v(scratch, criteria)
            got_fail = rc != 0
            ok = (got_fail == expect_fail)
            results.append((name, criteria, expect_fail, got_fail, ok))
            print("[%s] %-34s %-8s expect=%s got=%s"
                  % ("OK" if ok else "XX", name, criteria,
                     "FAIL" if expect_fail else "PASS", "FAIL" if got_fail else "PASS"))
            return out

        # ---- G-D1 负例：provenance 某段为空
        def m1():
            write_fixture_write(dens, provenance={"definition": [FIXTURE_EV], "principle": [],
                                                  "mechanism": [FIXTURE_EV],
                                                  "engineering": [FIXTURE_EV],
                                                  "tradeoff": [FIXTURE_EV]})
        case("G-D1 provenance 段为空", "G-D1", True, m1)

        # ---- G-D1 负例：new_claim 不在 ledger / claim-map
        def m1b():
            write_fixture_write(dens, new_claims=[{"claim_id": FIXTURE_NODE + "#principle#99",
                                                   "text": "幽灵", "anchor": {"chapter": "1"},
                                                   "evidence_strength": "direct", "direction": "forward"}])
        case("G-D1 claim 不在 ledger/claim-map", "G-D1", True, m1b)

        # ---- G-D2 负例：增量大但 provenance 只覆盖 1 条 claim
        def m2():
            seg = {s: LONG_BODY for s in SEGMENTS}
            write_fixture_write(dens, segments=seg)
        case("G-D2 注水（claim 覆盖不足）", "G-D2", True, m2)

        # ---- G-D3 负例：终稿字数不足 2400
        def m3():
            seg = {s: "短正文。" * 20 for s in SEGMENTS}
            write_fixture_write(dens, segments=seg)
        case("G-D3 字数低于 2400", "G-D3", True, m3)

        # ---- G-D3 负例：排除节点正文被改动
        def m3b():
            write_fixture_write(dens, clean=True)
            dag_p = os.path.join(scratch, "10-dag-data", "methodology-dag.json")
            dag = json.load(open(dag_p, encoding="utf-8"))
            for n in dag["nodes"]:
                if n["id"] == "ESS-G-03":
                    n["definition"] = (n.get("definition") or "") + "被改动。"
            json.dump(dag, open(dag_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        case("G-D3 排除节点被改动", "G-D3", True, m3b)

        # ---- G-D4 负例：正文复制语料 20+ 字
        def m4():
            seg = {s: LONG_BODY for s in SEGMENTS}
            seg["mechanism"] = CORPUS_SENTENCE + LONG_BODY
            write_fixture_write(dens, segments=seg)
        case("G-D4 正文命中 ≥20 字原文", "G-D4", True, m4)

        # ---- G-D5 负例：变更集缺参与节点（只 1 个 write，期望 26）
        def m5():
            write_fixture_write(dens, clean=True)
        case("G-D5 变更集 != 26", "G-D5", True, m5)

        # ---- G-V9 负例：阶段2 记录 second_pass=none
        def m6():
            write_fixture_write(dens, clean=True)
            led_p = os.path.join(scratch, "01-books", "_verify", "_parts", "ledger-saip.json")
            os.makedirs(os.path.dirname(led_p), exist_ok=True)
            led = {"book": "saip", "source_id": "BK-009", "records": [{
                "record_id": "VR-D2-001", "node_id": FIXTURE_NODE, "source_id": "BK-009",
                "direction": "forward", "claim_id": FIXTURE_CLAIM, "claim": "夹具",
                "anchor": {"chapter": "1", "section": "1.1", "section_title": "T"},
                "page_anchor_private": None, "evidence_strength": "direct",
                "evidence_note": "n",
                "review": {"reviewed_by": "x", "review_date": "2026-09-11",
                           "second_pass": "none", "second_pass_by": "x"}}]}
            json.dump(led, open(led_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            # 同步进合并 ledger（G-V9 读 verification-ledger.json）
            vl_p = os.path.join(scratch, "01-books", "_verify", "verification-ledger.json")
            vl = json.load(open(vl_p, encoding="utf-8"))
            vl["records"].append(led["records"][0])
            json.dump(vl, open(vl_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        case("G-V9 second_pass=none", "G-V9", True, m6, gate="verify")

        # ---- 正例：合规夹具应使 G-D1/D2/D4 PASS
        def m_ok():
            write_fixture_write(dens, clean=True)
        out = case("正例 G-D1", "G-D1", False, m_ok, nodes=FIXTURE_NODE)
        case("正例 G-D2", "G-D2", False, m_ok, nodes=FIXTURE_NODE)
        case("正例 G-D4", "G-D4", False, m_ok, nodes=FIXTURE_NODE)

        print()
        bad = [r for r in results if not r[4]]
        print("== 负向测试汇总：%d 例，%d 通过，%d 未达预期 ==" % (len(results), len(results) - len(bad), len(bad)))
        for r in bad:
            print("  XX %s (%s)" % (r[0], r[1]))
        return 0 if not bad else 1
    finally:
        if args.keep:
            print("[keep] scratch = %s" % scratch)
        else:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
