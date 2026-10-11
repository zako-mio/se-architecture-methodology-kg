#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
derive_densify.py — 阶段7 阶段2「内容增密」确定性派生器 / 前置核查器

唯一真相源：01-books/_verify/_densify/{evidence-<slug>.json, write-<node_id>.json}
            01-books/_verify/_parts/{ledger,claims}-<slug>.json
            10-dag-data/{_base.json, _parts/*.json, node-content.json, _verification-baseline.json}

输出（全部确定性、无时间戳、稳定排序、UTF-8 无 BOM、末尾换行）：
  01-books/_verify/_densify/precheck-coverage.json   步骤0 前置核查（--precheck）
  01-books/_verify/_densify/paragraph-claim-map.json 段级 claim 映射 + 字数/注水比
  01-books/_verify/_densify/densify-report.json      对账报告

用法：
  python3 16-checkpoint/derive_densify.py --precheck   # 步骤0：26 节点 × 5 段主张覆盖 + 落点映射
  python3 16-checkpoint/derive_densify.py              # 派生 paragraph-claim-map + 对账报告
  python3 16-checkpoint/derive_densify.py --check      # 幂等自检（只读，连算两次比对）
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
GENERATED = "2026-09-11"          # 冻结常量：禁止 datetime.date.today() / time.time()
SCHEMA_VERSION = "1.0.0"

# 封闭集合（与 00-plan/stage7-phase2-content-densification-plan.md §2.2 一致）
PLAN_NODES = [
    # essence (14)
    "ESS-G-01", "ESS-G-02", "ESS-G-04", "ESS-I-02", "ESS-K-02", "ESS-L-05",
    "ESS-M-01", "ESS-M-02", "ESS-M-03", "ESS-M-04", "ESS-M-05",
    "ESS-O-01", "ESS-O-02", "ESS-O-03",
    # methodology (10)
    "MTH-G-02", "MTH-G-03", "MTH-G-06", "MTH-M-01", "MTH-M-02", "MTH-M-03",
    "MTH-M-06", "MTH-O-03", "MTH-O-05", "MTH-O-09",
    # technology (2)
    "TEC-K-05", "TEC-M-03",
]
EXCLUDED_NODES = [
    "CAS-X-02", "ESS-G-03", "ESS-G-07", "ESS-H-02", "ESS-K-01",
    "MTH-K-06", "MTH-O-10", "MTH-O-11", "TEC-K-01",
]
SEGMENTS = ("definition", "principle", "mechanism", "engineering", "tradeoff")
ORIGINS = ("definition", "principle", "mechanism", "engineering", "tradeoff", "errata")

SLUG_ORDER = ("clean-architecture", "ddia", "saip")
SLUG_SOURCE = {"ddia": "BK-023", "clean-architecture": "BK-007", "saip": "BK-009"}
SLUG_BY_PREFIX = {"CA": "clean-architecture", "DDIA": "ddia", "SAIP": "saip"}

LEDGER_DIR = os.path.join("01-books", "_verify")
PARTS_DIR = os.path.join(LEDGER_DIR, "_parts")
DENSIFY_DIR = os.path.join(LEDGER_DIR, "_densify")
DAG_DIR = "10-dag-data"

OUT_PRECHECK = os.path.join(DENSIFY_DIR, "precheck-coverage.json")
OUT_PARA_MAP = os.path.join(DENSIFY_DIR, "paragraph-claim-map.json")
OUT_REPORT = os.path.join(DENSIFY_DIR, "densify-report.json")

CHAR_MIN, CHAR_MAX = 2400, 3000          # 参与节点终稿区间
GLOBAL_CHAR_MIN, GLOBAL_CHAR_MAX = 1500, 3000


def default_root():
    return os.path.dirname(HERE)


def resolve(root, path):
    return path if os.path.isabs(path) else os.path.join(root, path)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_opt(path):
    return load(path) if os.path.isfile(path) else None


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def write_out(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(dumps(obj))


# ---------------------------------------------------------------- 落点映射

def build_shard_map(root):
    """node_id -> 源分片相对路径（_base.json 或 _parts/<file>.json）。"""
    out = {}
    base = load_opt(resolve(root, os.path.join(DAG_DIR, "_base.json")))
    if base:
        for n in base.get("nodes", []) or []:
            out[n["id"]] = os.path.join(DAG_DIR, "_base.json")
    parts_glob = resolve(root, os.path.join(DAG_DIR, "_parts", "*.json"))
    for p in sorted(glob.glob(parts_glob)):
        doc = load(p)
        for n in doc.get("nodes", []) or []:
            out[n["id"]] = os.path.join(DAG_DIR, "_parts", os.path.basename(p))
    return out


def build_claims_slug_map(root):
    """node_id -> [slug...]（claims-<slug>.json 中出现该节点键的分片，按 SLUG_ORDER）。"""
    out = {}
    for slug in SLUG_ORDER:
        p = resolve(root, os.path.join(PARTS_DIR, "claims-%s.json" % slug))
        doc = load_opt(p)
        if not doc:
            continue
        for node_id in doc:
            out.setdefault(node_id, []).append(slug)
    return out


def build_ledger_prefix_map(root):
    """node_id -> [slug...]（由 record_id 前缀 VR-CA-/VR-DDIA-/VR-SAIP- 解析，稳定排序）。"""
    doc = load_opt(resolve(root, os.path.join(LEDGER_DIR, "verification-ledger.json")))
    if not doc:
        return {}
    out = {}
    for r in doc.get("records", []) or []:
        rid = r.get("record_id", "")
        node_id = r.get("node_id")
        if not rid.startswith("VR-") or not node_id:
            continue
        prefix = rid.split("-", 2)[1]
        slug = SLUG_BY_PREFIX.get(prefix)
        if slug:
            out.setdefault(node_id, set()).add(slug)
    return {k: sorted(v, key=SLUG_ORDER.index) for k, v in out.items()}


def build_body_char_map(root):
    """node_id -> char_count（读 node-content.json 的预计算字段；不重算）。"""
    doc = load_opt(resolve(root, os.path.join(DAG_DIR, "node-content.json")))
    if not doc:
        return {}
    out = {}
    for e in doc.get("node_contents", []) or []:
        out[e["id"]] = e.get("char_count")
    return out


# ---------------------------------------------------------------- 步骤0 前置核查

def do_precheck(root):
    ledger = load_opt(resolve(root, os.path.join(LEDGER_DIR, "verification-ledger.json"))) or {}
    records = ledger.get("records", []) or []
    claim_map = (load_opt(resolve(root, os.path.join(LEDGER_DIR, "node-claim-map.json"))) or {}).get("nodes", {}) or {}

    shard_map = build_shard_map(root)
    claims_slug_map = build_claims_slug_map(root)
    ledger_prefix_map = build_ledger_prefix_map(root)
    char_map = build_body_char_map(root)

    # 每节点的 ledger 记录（按 claim_id 索引）
    recs_by_node = {}
    for r in records:
        recs_by_node.setdefault(r["node_id"], []).append(r)

    nodes_out = {}
    for node_id in PLAN_NODES:
        cm = claim_map.get(node_id) or {}
        claims = cm.get("claims", []) or []
        # 段 → 既有 claim_id
        seg_claims = {s: [] for s in SEGMENTS}
        other_claims = []
        for c in claims:
            cid = c.get("claim_id", "")
            origin = c.get("origin") or (cid.split("#")[1] if cid.count("#") >= 2 else None)
            if origin in seg_claims:
                seg_claims[origin].append(cid)
            else:
                other_claims.append(cid)
        ledger_recs = recs_by_node.get(node_id, [])
        ledger_direct = [r["claim_id"] for r in ledger_recs if r.get("evidence_strength") == "direct"]

        missing_segments = [s for s in SEGMENTS if not seg_claims[s]]
        # reverse-only 口径：**无主张拆分**且 ledger 记录**全为 reverse**（实测 ESS-O-01 有 2 条 reverse 记录）
        is_reverse_only = (len(claims) == 0 and bool(ledger_recs)
                           and all(r.get("direction") == "reverse" for r in ledger_recs))

        # claims 落点：既有分片优先；reverse-only 节点按 ledger 前缀推断（新建键）
        existing_slug = claims_slug_map.get(node_id, [])
        if existing_slug:
            claims_target = existing_slug[0]
            claims_action = "append_to_existing_node_key"
        else:
            inferred = ledger_prefix_map.get(node_id, [])
            claims_target = inferred[0] if inferred else None
            claims_action = "create_new_node_key"

        nodes_out[node_id] = {
            "node_id": node_id,
            "layer": None,
            "baseline_chars": char_map.get(node_id),
            "body_shard": shard_map.get(node_id),
            "claims_target_slug": claims_target,
            "claims_action": claims_action,
            "claims_existing_slugs": existing_slug,
            "ledger_slugs": ledger_prefix_map.get(node_id, []),
            "ledger_records": len(ledger_recs),
            "ledger_direct": len(ledger_direct),
            "claims_total": len(claims),
            "segment_claims": {s: sorted(seg_claims[s]) for s in SEGMENTS},
            "other_claims": sorted(other_claims),
            "missing_segments": missing_segments,
            "reverse_only": is_reverse_only,
        }

    # 层信息（从 dag 读，仅用于分组）
    dag = load_opt(resolve(root, os.path.join(DAG_DIR, "methodology-dag.json")))
    if dag:
        by_id = {n["id"]: n for n in dag.get("nodes", []) or []}
        for node_id, info in nodes_out.items():
            n = by_id.get(node_id) or {}
            info["layer"] = n.get("layer")
            info["group"] = n.get("group")
            info["domain"] = n.get("domain")

    reverse_only = sorted([k for k, v in nodes_out.items() if v["reverse_only"]])
    unresolved = sorted([k for k, v in nodes_out.items() if not v["body_shard"]])
    no_claims_target = sorted([k for k, v in nodes_out.items() if not v["claims_target_slug"]])
    missing_any = sorted([k for k, v in nodes_out.items() if v["missing_segments"]])

    doc = {
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "generated": GENERATED,
            "note": "步骤0 前置核查：26 参与节点 × 5 段主张覆盖 + 正文/claims 落点映射",
            "plan_nodes": len(PLAN_NODES),
            "segments": list(SEGMENTS),
            "char_range": [CHAR_MIN, CHAR_MAX],
        },
        "summary": {
            "plan_nodes": len(PLAN_NODES),
            "reverse_only": len(reverse_only),
            "reverse_only_nodes": reverse_only,
            "nodes_with_missing_segments": len(missing_any),
            "nodes_with_missing_segments_list": missing_any,
            "body_shard_unresolved": unresolved,
            "claims_target_unresolved": no_claims_target,
            "baseline_chars_min": min([v["baseline_chars"] for v in nodes_out.values() if v["baseline_chars"]] or [0]),
            "baseline_chars_max": max([v["baseline_chars"] for v in nodes_out.values() if v["baseline_chars"]] or [0]),
            "already_in_target_range": sorted([k for k, v in nodes_out.items()
                                               if v["baseline_chars"] and CHAR_MIN <= v["baseline_chars"] <= CHAR_MAX]),
        },
        "nodes": {k: nodes_out[k] for k in sorted(nodes_out)},
    }
    write_out(resolve(root, OUT_PRECHECK), doc)
    return doc


# ---------------------------------------------------------------- 派生（② 之后）

def collect_write_docs(root):
    """读 _densify/write-<node_id>.json，返回 ({node_id: doc}, bad)。

    fail-closed：不可解析 / 含 PLACEHOLDER 的稿子一律跳过并记录，绝不带病派生。
    """
    out = {}
    bad = []
    pattern = resolve(root, os.path.join(DENSIFY_DIR, "write-*.json"))
    for p in sorted(glob.glob(pattern)):
        try:
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception as e:                               # noqa: BLE001
            bad.append({"file": os.path.basename(p), "error": str(e)[:120]})
            continue
        nid = doc.get("node_id")
        if not nid:
            bad.append({"file": os.path.basename(p), "error": "missing node_id"})
            continue
        segs = doc.get("segments") or {}
        ph = [s for s in SEGMENTS if "PLACEHOLDER" in (segs.get(s) or "")]
        if ph:
            bad.append({"file": os.path.basename(p), "error": "placeholder: %s" % ",".join(ph)})
            continue
        out[nid] = doc
    return out, bad


def collect_evidence_docs(root):
    """读 _densify/evidence-*.json，返回 ({evidence_id: item}, problems)。"""
    out = {}
    problems = []
    pattern = resolve(root, os.path.join(DENSIFY_DIR, "evidence-*.json"))
    sparse = resolve(root, os.path.join(DENSIFY_DIR, "sparse-*.json"))
    for p in sorted(glob.glob(pattern) + glob.glob(sparse)):
        if os.path.getsize(p) == 0:
            problems.append({"file": os.path.basename(p), "issue": "empty_file"})
            continue
        try:
            with open(p, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception as e:                               # noqa: BLE001
            problems.append({"file": os.path.basename(p), "issue": "invalid_json: %s" % e})
            continue
        for it in doc.get("items", []) or []:
            eid = it.get("evidence_id")
            if not eid:
                problems.append({"file": os.path.basename(p), "issue": "item_without_evidence_id"})
                continue
            if eid in out:
                problems.append({"file": os.path.basename(p), "issue": "duplicate_evidence_id: %s" % eid})
                continue
            nid = it.get("node_id")
            if nid not in PLAN_NODES:
                problems.append({"file": os.path.basename(p), "evidence_id": eid,
                                 "issue": "node_id_not_in_plan: %s" % nid})
            cid = it.get("claim_id") or ""
            origin = cid.split("#")[1] if cid.count("#") >= 2 else None
            if origin not in ORIGINS:
                problems.append({"file": os.path.basename(p), "evidence_id": eid,
                                 "issue": "claim_id_origin_invalid: %s" % cid})
            out[eid] = it
    return out, problems


def do_derive(root):
    writes, bad_writes = collect_write_docs(root)
    evidence, evidence_problems = collect_evidence_docs(root)
    ledger = load_opt(resolve(root, os.path.join(LEDGER_DIR, "verification-ledger.json"))) or {}
    ledger_claim_ids = {r.get("claim_id") for r in ledger.get("records", []) or []}
    claim_map = (load_opt(resolve(root, os.path.join(LEDGER_DIR, "node-claim-map.json"))) or {}).get("nodes", {}) or {}
    claim_map_ids = set()
    for _nid, cm in claim_map.items():
        for c in cm.get("claims", []) or []:
            claim_map_ids.add(c.get("claim_id"))
    baseline = load_opt(resolve(root, os.path.join(DAG_DIR, "_verification-baseline.json"))) or {}
    char_map = build_body_char_map(root)

    para_map = {}
    nodes_report = {}
    issues = {"dangling_evidence": [], "dangling_claim": [], "segment_missing": [],
              "char_out_of_range": [], "inflation": [], "unknown_node": [],
              "evidence_shard": list(evidence_problems)}

    for node_id in sorted(writes):
        doc = writes[node_id]
        if node_id not in PLAN_NODES:
            issues["unknown_node"].append(node_id)
        segments = doc.get("segments", {}) or {}
        provenance = doc.get("provenance", {}) or {}
        new_claims = doc.get("new_claims", []) or []

        seg_map = {}
        for s in SEGMENTS:
            text = segments.get(s, "") or ""
            evs = provenance.get(s, []) or []
            if not evs:
                issues["segment_missing"].append({"node_id": node_id, "segment": s, "reason": "provenance_empty"})
            for eid in evs:
                if eid not in evidence:
                    issues["dangling_evidence"].append({"node_id": node_id, "segment": s, "evidence_id": eid})
            seg_map[s] = sorted(set(evs))
        para_map[node_id] = seg_map

        # 新 claim 可解析性（G-D1：须同时见于 ledger 与 claim-map）
        for nc in new_claims:
            cid = nc.get("claim_id")
            if cid not in ledger_claim_ids:
                issues["dangling_claim"].append({"node_id": node_id, "claim_id": cid, "missing_in": "ledger"})
            if cid not in claim_map_ids:
                issues["dangling_claim"].append({"node_id": node_id, "claim_id": cid, "missing_in": "node-claim-map"})

        final_chars = sum(len(segments.get(s, "") or "") for s in SEGMENTS)
        baseline_chars = char_map.get(node_id) or doc.get("baseline_chars") or 0
        delta = final_chars - baseline_chars
        # G-D2 口径（2026-10-11 修正）：按 provenance 引用的 distinct claim_id 计数。
        # provenance 值为 evidence_id → 经 evidence 表映射到其 claim_id；无法映射的记为空。
        prov_claim_ids = set()
        for s in SEGMENTS:
            for eid in (provenance.get(s) or []):
                it = evidence.get(eid)
                if it and it.get("claim_id"):
                    prov_claim_ids.add(it["claim_id"])
        distinct_new_claims = len({c.get("claim_id") for c in new_claims})
        required = -(-max(delta, 0) // 200)  # ceil
        if not (CHAR_MIN <= final_chars <= CHAR_MAX):
            issues["char_out_of_range"].append({"node_id": node_id, "final_chars": final_chars})
        if required > len(prov_claim_ids):
            issues["inflation"].append({"node_id": node_id, "delta": delta,
                                        "required_claims": required,
                                        "provenance_claim_ids": len(prov_claim_ids),
                                        "new_claims": distinct_new_claims})

        nodes_report[node_id] = {
            "baseline_chars": baseline_chars,
            "final_chars": final_chars,
            "delta_chars": delta,
            "provenance_claim_ids": len(prov_claim_ids),
            "distinct_new_claims": distinct_new_claims,
            "required_claims_for_delta": required,
            "segments_present": sorted([s for s in SEGMENTS if (segments.get(s) or "").strip()]),
        }

    report = {
        "meta": {"schema_version": SCHEMA_VERSION, "generated": GENERATED,
                 "note": "阶段2 增密对账报告（变更集 / 字数 / 注水比 / 零悬挂）"},
        "summary": {
            "write_docs": len(writes),
            "plan_nodes": len(PLAN_NODES),
            "changed_nodes": sorted(writes),
            "missing_write_docs": sorted([n for n in PLAN_NODES if n not in writes]),
            "extra_write_docs": sorted([n for n in writes if n not in PLAN_NODES]),
            "evidence_items": len(evidence),
            "evidence_shard_problems": len(evidence_problems),
            "bad_write_docs": bad_writes,
            "final_chars_min": min([v["final_chars"] for v in nodes_report.values()] or [0]),
            "final_chars_max": max([v["final_chars"] for v in nodes_report.values()] or [0]),
            "issue_counts": {k: len(v) for k, v in sorted(issues.items())},
        },
        "issues": issues,
        "nodes": {k: nodes_report[k] for k in sorted(nodes_report)},
    }

    write_out(resolve(root, OUT_PARA_MAP), {
        "meta": {"schema_version": SCHEMA_VERSION, "generated": GENERATED,
                 "note": "段级 claim/evidence 映射（provenance）"},
        "nodes": {k: para_map[k] for k in sorted(para_map)},
    })
    write_out(resolve(root, OUT_REPORT), report)
    return report


def do_check(root):
    """幂等自检：连算两次比对（输出可写，但两次结果必须逐字节一致）。"""
    outs = [OUT_PRECHECK, OUT_PARA_MAP, OUT_REPORT]

    def snapshot():
        snap = {}
        for rel in outs:
            p = resolve(root, rel)
            snap[rel] = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
        return snap

    def run_once():
        do_precheck(root)
        if collect_write_docs(root)[0]:
            do_derive(root)

    run_once()
    mid = snapshot()
    run_once()
    after = snapshot()
    diffs = [rel for rel in outs if mid[rel] != after[rel]]
    if diffs:
        print("[FAIL] 派生非幂等：%s" % ", ".join(diffs))
        return 1
    print("[IDEMPOTENT] %s" % ", ".join(outs))
    print("== 增密派生幂等自检 = PASS ==")
    return 0


def main():
    ap = argparse.ArgumentParser(description="阶段7 阶段2 增密派生 / 前置核查")
    ap.add_argument("--root", default=default_root(), help="母库 root（默认脚本上级目录）")
    ap.add_argument("--precheck", action="store_true", help="步骤0：26 节点 × 5 段主张覆盖 + 落点映射")
    ap.add_argument("--check", action="store_true", help="幂等自检（只读，连算两次比对）")
    args = ap.parse_args()

    root = os.path.abspath(args.root)

    if args.check:
        return do_check(root)
    if args.precheck:
        doc = do_precheck(root)
        s = doc["summary"]
        print("[precheck] 参与节点 %d | reverse-only %d | 缺段节点 %d"
              % (s["plan_nodes"], s["reverse_only"], s["nodes_with_missing_segments"]))
        print("[precheck] reverse-only: %s" % ", ".join(s["reverse_only_nodes"]))
        print("[precheck] 正文分片未解析: %s" % (", ".join(s["body_shard_unresolved"]) or "无"))
        print("[precheck] claims 落点未解析: %s" % (", ".join(s["claims_target_unresolved"]) or "无"))
        print("[precheck] 基线字数 %d–%d | 已在 [%d,%d] 区间: %d"
              % (s["baseline_chars_min"], s["baseline_chars_max"], CHAR_MIN, CHAR_MAX,
                 len(s["already_in_target_range"])))
        print("[out] %s" % OUT_PRECHECK)
        return 0

    report = do_derive(root)
    s = report["summary"]
    print("[derive] write 文档 %d / 参与节点 %d" % (s["write_docs"], s["plan_nodes"]))
    print("[derive] 变更节点 %d | 缺稿 %d | 越界稿 %d"
          % (len(s["changed_nodes"]), len(s["missing_write_docs"]), len(s["extra_write_docs"])))
    print("[derive] 终稿字数 %d–%d" % (s["final_chars_min"], s["final_chars_max"]))
    print("[derive] 问题计数: %s" % json.dumps(s["issue_counts"], ensure_ascii=False))
    print("[out] %s" % OUT_PARA_MAP)
    print("[out] %s" % OUT_REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
