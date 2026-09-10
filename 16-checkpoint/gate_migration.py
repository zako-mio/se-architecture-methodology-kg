#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_migration.py — 信源 ID 迁移门控校验（返回码非 0 = 失败）

检查项：
  G1 JSON 合法          所有迁移范围内文件可 json.loads
  G2 引用零未解析       source_id / source_ids[] / sources[]（字符串列表）的值必须为规范 ID
  G3 编码纯净           无 U+FFFD、无 BOM、无空文件
  G4 计数一致           sources[] 条数迁移前后一致
  G5 映射完备           备份中每个 (pack, old_id) 都在 id-mapping.json 中有条目
  G6 无旧 ID 残留       sources[].id 与引用字段中不再出现旧形态 ID
"""
import json, re, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPING = os.path.join(ROOT, "00-plan", "id-mapping.json")
BACKUP = os.path.join(ROOT, "_backup-idmigration")
RES = os.path.join(ROOT, "02-research")
KM = os.path.join(ROOT, "03-knowledge-map", "knowledge-map.json")
PKGS = ["A", "B", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R"]
CANON = re.compile(r'^(STD|OFF|BK|WEB|VEN|PAP|COM|LOC|XCV)-\d{3}$')
OLD = re.compile(r'(?:^|:)(S[1-4]-(?:STD|OFF|BK|WEB|VEN|PAP|COM)?-?\d+|S[1-4]-[A-Z]\d+|'
                 r'P-S[1-4]-\d+|R-XC-\d+|L-[A-Z]{2}-\d+|R-XC)')


def files():
    out = []
    for p in PKGS:
        hits = [f for f in os.listdir(RES) if f.startswith(p + "-") and f.endswith(".json")]
        if hits:
            out.append((p, os.path.join(RES, hits[0]), os.path.join(BACKUP, "02-research", hits[0])))
    out.append(("PHASE1", KM, os.path.join(BACKUP, "03-knowledge-map", "knowledge-map.json")))
    return out


def refs_walk(o, path=""):
    """yield (field, value) for reference-bearing fields"""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "source_id" and isinstance(v, str):
                yield ("source_id", v)
            elif k == "source_ids" and isinstance(v, list):
                for x in v:
                    yield ("source_ids[]", x)
            elif k == "sources" and isinstance(v, list) and v and all(isinstance(x, str) for x in v):
                for x in v:
                    yield ("sources[str]", x)
            else:
                yield from refs_walk(v, path)
    elif isinstance(o, list):
        for x in o:
            yield from refs_walk(x, path)


def main():
    fails, warns = [], []
    mapping = json.load(open(MAPPING, encoding="utf-8"))
    lookup = {(e["source_pack"], e["old_id"]): e["canonical_id"] for e in mapping["entries"]}
    canon_set = set(e["canonical_id"] for e in mapping["entries"])
    assert all(CANON.match(c) for c in canon_set), "映射表存在非法规范 ID"

    for pkg, path, bpath in files():
        # G1 / G3
        raw = open(path, "rb").read()
        if not raw:
            fails.append(f"G3 {pkg}: 空文件")
            continue
        if raw.startswith(b"\xef\xbb\xbf"):
            fails.append(f"G3 {pkg}: 含 BOM")
        text = raw.decode("utf-8")
        if "\ufffd" in text:
            fails.append(f"G3 {pkg}: 含 U+FFFD")
        try:
            doc = json.loads(text)
        except Exception as e:
            fails.append(f"G1 {pkg}: JSON 解析失败 {e}")
            continue
        # G2 / G6
        unresolved = []
        for field, val in refs_walk(doc):
            if not isinstance(val, str):
                continue
            if CANON.match(val):
                if val not in canon_set:
                    fails.append(f"G2 {pkg}: 规范 ID {val} 不在映射表 canonical 集")
                continue
            if OLD.search(val):
                unresolved.append((field, val))
        if unresolved:
            fails.append(f"G2/G6 {pkg}: 未解析/旧 ID 残留 {unresolved[:8]} (共 {len(unresolved)})")
        # G4
        cur = doc.get("sources")
        cur_n = len(cur) if isinstance(cur, list) else 0
        if os.path.exists(bpath):
            bak = json.load(open(bpath, encoding="utf-8"))
            bak_n = len(bak.get("sources", [])) if isinstance(bak.get("sources"), list) else 0
            if cur_n != bak_n:
                fails.append(f"G4 {pkg}: sources 数 {bak_n} -> {cur_n}")
            # G5 + G6 on sources[].id
            if isinstance(bak.get("sources"), list):
                for s in bak["sources"]:
                    if isinstance(s, dict) and "id" in s:
                        if (pkg, s["id"]) not in lookup:
                            fails.append(f"G5 {pkg}: 旧 ID {s['id']} 无映射条目")
            if isinstance(cur, list):
                for s in cur:
                    if isinstance(s, dict) and "id" in s:
                        if not CANON.match(str(s["id"])):
                            fails.append(f"G6 {pkg}: sources[].id 非规范 {s['id']}")
                        if "legacy_id" not in s:
                            warns.append(f"{pkg}: source {s['id']} 缺 legacy_id")

    print("== 门控结果 ==")
    print("映射条目:", len(mapping["entries"]), "| 规范实体:", len(canon_set))
    print("FAIL:", len(fails))
    for f in fails:
        print("  ", f)
    print("WARN:", len(warns))
    for w in warns[:10]:
        print("  ", w)
    if fails:
        sys.exit(1)
    print("ALL GATES PASS")


if __name__ == "__main__":
    main()
