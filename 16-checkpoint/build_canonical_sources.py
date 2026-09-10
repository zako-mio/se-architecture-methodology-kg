#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_canonical_sources.py — 生成唯一权威信源主表 03-knowledge-map/canonical-sources.json

输入：
  00-plan/id-mapping.json          （414 old_id -> 253 canonical_id；唯一权威实体枚举）
  03-knowledge-map/knowledge-map.json（阶段1 目录，sources[].id 已是 canonical，含最全元数据）
  02-research/{A,B,F,G,H,I,J,K,L,M,N,P,Q,R}-*.json（14 个证据包 sources[]，canonical id + verified）

输出：
  03-knowledge-map/canonical-sources.json
    { meta:{...}, sources:[{id,category,title,org,year,url,tier,verified,confidence,legacy_ids}] }

口径：
  - 实体集合 = id-mapping.json entries[].canonical_id（253，去重），id-mapping 为唯一真相。
  - 同一 canonical 来自多包/多旧 ID 时合并，legacy_ids 汇总全部旧 ID（entries + collisions + KM/research legacy_id）。
  - title/org/year/url/tier 优先取 knowledge-map.json，缺失回退 research sources[]，再回退 id-mapping entity_key。
  - verified 取 research sources[].verified（布尔）；仅阶段1 目录收录者标 "cited"。
  - confidence 派生：verified=true -> high；"cited" -> medium；false -> low。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDMAP = os.path.join(ROOT, "00-plan", "id-mapping.json")
KM = os.path.join(ROOT, "03-knowledge-map", "knowledge-map.json")
RES_DIR = os.path.join(ROOT, "02-research")
OUT = os.path.join(ROOT, "03-knowledge-map", "canonical-sources.json")

PKG_FILES = [
    "A-se-definition", "B-architecture-definition", "F-requirements",
    "G-architecture", "H-implementation", "I-testing", "J-deployment",
    "K-operations", "L-evolution", "M-quality-ility", "N-team-conway",
    "P-techdebt", "Q-vendor-architecture", "R-foundational-papers",
]
CATEGORIES = ["STD", "OFF", "BK", "WEB", "VEN", "PAP", "COM", "LOC", "XCV"]


def key_to_url(entity_key):
    if not entity_key:
        return None
    k = str(entity_key)
    if k.startswith("url:"):
        k = k[4:]
    if k.startswith("http://") or k.startswith("https://"):
        return k
    return "https://" + k


def first_nonnull(*vals):
    for v in vals:
        if v is not None and v != "":
            return v
    return None


def main():
    idmap = json.load(open(IDMAP, encoding="utf-8"))
    entries = idmap["entries"]

    # canonical -> ordered unique legacy ids
    legacy = {}
    url_fallback = {}
    for e in entries:
        cid = e["canonical_id"]
        legacy.setdefault(cid, [])
        if e["old_id"] not in legacy[cid]:
            legacy[cid].append(e["old_id"])
        if cid not in url_fallback and e.get("entity_key"):
            url_fallback[cid] = key_to_url(e["entity_key"])
    for col in idmap.get("collisions", []):
        for occ in col["occurrences"]:
            cid = occ["canonical_id"]
            legacy.setdefault(cid, [])
            if col["old_id"] not in legacy[cid]:
                legacy[cid].append(col["old_id"])

    # knowledge-map: canonical id -> entry (merge duplicates, prefer first with evidence_ref/longest title)
    km_all = json.load(open(KM, encoding="utf-8"))["sources"]
    km = {}
    for s in km_all:
        cid = s["id"]
        if cid not in km:
            km[cid] = s
        else:
            cur = km[cid]
            # merge richer fields without dropping
            for k, v in s.items():
                if v not in (None, "", [], {}):
                    if cur.get(k) in (None, "", [], {}):
                        cur[k] = v
            if s.get("legacy_id") and s["legacy_id"] not in str(cur.get("legacy_id", "")):
                cur.setdefault("legacy_id_extra", []).append(s["legacy_id"])

    # research: canonical id -> source
    res = {}
    for fn in PKG_FILES:
        path = os.path.join(RES_DIR, fn + ".json")
        for s in json.load(open(path, encoding="utf-8"))["sources"]:
            cid = s.get("id")
            if cid and cid not in res:
                res[cid] = s

    canonical_ids = sorted(set(legacy.keys()))
    assert len(canonical_ids) == 253, "canonical 实体数 != 253: %d" % len(canonical_ids)

    out_sources = []
    for cid in canonical_ids:
        cat = cid.split("-")[0]
        assert cat in CATEGORIES, "非法类别 %s" % cid
        k = km.get(cid, {})
        r = res.get(cid, {})
        title = first_nonnull(k.get("title"), r.get("title"))
        org = first_nonnull(k.get("org"), r.get("org"))
        year = first_nonnull(k.get("year"), r.get("year"))
        url = first_nonnull(k.get("url"), r.get("url"), url_fallback.get(cid))
        tier = first_nonnull(k.get("tier"), r.get("tier"))
        if "verified" in r:
            verified = r["verified"]
        else:
            verified = "cited"
        if verified is True:
            confidence = "high"
        elif verified == "cited":
            confidence = "medium"
        else:
            confidence = "low"

        legs = list(legacy.get(cid, []))
        for src in (k, r):
            lid = src.get("legacy_id")
            if lid and lid not in legs:
                legs.append(lid)
            for lid in src.get("legacy_id_extra", []):
                if lid not in legs:
                    legs.append(lid)

        out_sources.append({
            "id": cid,
            "category": cat,
            "title": title,
            "org": org,
            "year": year,
            "url": url,
            "tier": tier,
            "verified": verified,
            "confidence": confidence,
            "legacy_ids": legs,
        })

    by_cat = {c: sum(1 for s in out_sources if s["category"] == c) for c in CATEGORIES}
    by_cat = {c: n for c, n in by_cat.items() if n}
    by_conf = {}
    for s in out_sources:
        by_conf[s["confidence"]] = by_conf.get(s["confidence"], 0) + 1
    by_ver = {}
    for s in out_sources:
        by_ver[str(s["verified"])] = by_ver.get(str(s["verified"]), 0) + 1

    doc = {
        "meta": {
            "title": "软件工程 / 架构设计方法论 · 唯一权威信源主表（canonical sources）",
            "namespace_version": idmap.get("namespace_version", "1.0.0"),
            "schema_version": "1.0.0",
            "generated": "2026-09-10",
            "generator": "16-checkpoint/build_canonical_sources.py",
            "total": len(out_sources),
            "by_category": by_cat,
            "by_confidence": by_conf,
            "by_verified": by_ver,
            "id_rule": "^(STD|OFF|BK|WEB|VEN|PAP|COM|LOC|XCV)-\\d{3}$",
            "entity_rule": "id-mapping.json entries[].canonical_id 为唯一实体枚举；同实体跨包复用合并，legacy_ids 汇总全部旧 ID",
            "field_source": "title/org/year/url/tier 优先 knowledge-map.json，回退 14 证据包 sources[]，再回退 id-mapping entity_key；verified 取证据包布尔值，仅阶段1 目录收录标 cited",
            "confidence_rule": "verified=true→high；cited→medium；false→low",
            "knowledge_map_relation": "本文件为 253 个 canonical 实体的唯一权威源主表。03-knowledge-map/knowledge-map.json（158 条，含 6 个重复 canonical id，实际 152 个唯一实体）为阶段1 子集视图，其 sources[].id 已按同一 canonical 命名空间标注；本主表覆盖其全部实体并并入 14 个阶段2 证据包 sources[]。两者 ID 命名空间一致，knowledge-map 不再作为 sources[] 解析依据。",
            "downstream": "节点/边的 sources[] 与 errata[].source_id 一律引用本表 ID；契约 04-migration/canonical-sources.json 为同一逻辑文件的迁移期路径，本文件为当前落点。"
        },
        "sources": out_sources,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("WROTE", OUT)
    print("total=%d by_category=%s by_confidence=%s" % (len(out_sources), by_cat, by_conf))
    # basic self-checks
    ids = [s["id"] for s in out_sources]
    assert len(ids) == len(set(ids)), "duplicate canonical id"
    assert all(s["id"].split("-")[0] in CATEGORIES for s in out_sources)
    empty_title = [s["id"] for s in out_sources if not s["title"]]
    print("empty_title=%s" % (empty_title or "none"))
    no_legacy = [s["id"] for s in out_sources if not s["legacy_ids"]]
    print("no_legacy=%s" % (no_legacy or "none"))


if __name__ == "__main__":
    main()
