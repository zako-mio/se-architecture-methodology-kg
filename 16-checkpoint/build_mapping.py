#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_mapping.py — 生成信源统一 ID 迁移映射表（00-plan/id-mapping.json）

实体身份判定（id-migration-plan.md §2.0）：
  1) sources-index.md §2 的跨包复用映射为**权威人工输入**（不得被脚本覆盖）；
  2) knowledge-map.json 的 evidence_ref 反查出 A/B 阶段1 原始包 -> 阶段1 全局条目的归属；
  3) 同 URL / 同 DOI 归并仅用于**阶段2 包内部净新增实体**（不跨 PHASE1，防止把两个不同
     载体的阶段1 实体经阶段2 节点传递合并，如 S4-PAP-04 与 R-XC-05）；
  4) 同形旧 ID 字符串但 URL/DOI 不同者 = 不同实体（collision_split），各分配独立规范 ID。

规范 ID 命名空间：STD/OFF/BK/WEB/VEN/PAP/COM/LOC/XCV-{3 位序号}
分配顺序：阶段1（PHASE1）实体按 knowledge-map 出现序优先；其后阶段2 净新增实体按
包名 A,B,F..R 字母序 + 包内出现序。以"实体"为单位递增（同实体复用不占新号）。

输出：00-plan/id-mapping.json
"""
import json, re, glob, os, collections, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "02-research")
KM = os.path.join(ROOT, "03-knowledge-map", "knowledge-map.json")
SIDX = os.path.join(ROOT, "03-knowledge-map", "sources-index.md")
OUT = os.path.join(ROOT, "00-plan", "id-mapping.json")

PKG_ORDER = ["A", "B", "F", "G", "H", "I", "J", "K", "L", "M", "N", "P", "Q", "R"]
FR = set("FGHIJKLMNPQR")


def norm_url(u):
    if not u:
        return ""
    u = str(u).strip().lower()
    u = re.sub(r'^https?://web\.archive\.org/web/\d+(id_)?/', '', u)
    u = re.sub(r'^https?://', '', u)
    u = u.split('#')[0].split('?')[0].rstrip('/')
    return u


def norm_doi(d):
    if not d:
        return ""
    d = str(d).strip().lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    return d


# ---------------- load nodes ----------------
nodes = {}
order = []


def add(pkg, src, idx):
    key = (pkg, src['id'])
    if key in nodes:
        return key
    nodes[key] = {
        'pkg': pkg, 'id': src['id'], 'tier': src.get('tier'),
        'title': src.get('title', ''), 'org': src.get('org', ''),
        'year': src.get('year', ''), 'url': src.get('url', ''),
        'doi': src.get('doi', '') or src.get('DOIs', ''),
        'urls': src.get('urls') or [], 'srcindex': idx,
    }
    order.append(key)
    return key


km = json.load(open(KM, encoding="utf-8"))
for i, s in enumerate(km['sources']):
    add("PHASE1", s, i)

pkgfiles = {}
for f in sorted(glob.glob(os.path.join(RES, "*.json"))):
    base = os.path.basename(f)
    pkg = base.split("-")[0]
    d = json.load(open(f, encoding="utf-8"))
    if isinstance(d.get('sources'), list) and d['sources'] and \
       isinstance(d['sources'][0], dict) and 'id' in d['sources'][0]:
        pkgfiles[pkg] = f
        for i, s in enumerate(d['sources']):
            add(pkg, s, i)

# ---------------- union-find ----------------
parent = {k: k for k in nodes}


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra == rb:
        return
    if ra[0] == "PHASE1":
        parent[rb] = ra
    elif rb[0] == "PHASE1":
        parent[ra] = rb
    else:
        parent[rb] = ra


def uk(a, b):
    if a in nodes and b in nodes:
        union(a, b)


urlidx = collections.defaultdict(list)
doiidx = collections.defaultdict(list)
for k, n in nodes.items():
    if n['url']:
        urlidx[norm_url(n['url'])].append(k)
    for u in (n['urls'] or []):
        if u:
            urlidx[norm_url(u)].append(k)
    if n['doi']:
        doiidx[norm_doi(n['doi'])].append(k)

# ---- 防线一：sources-index §2 权威复用映射 ----
txt = open(SIDX, encoding="utf-8").read()
sec = txt.split("## 2. 跨包复用映射")[1].split("## 3.")[0]
edges = []
for line in sec.splitlines():
    line = line.strip()
    if not line.startswith("|") or set(line) <= set("|-: "):
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) < 2:
        continue
    left = re.findall(r'`([^`]+)`', cells[0])
    if not left or "/" not in left[0]:
        continue
    fp, fi = left[0].split("/", 1)
    if (fp, fi) not in nodes:
        print("  !! §2 src not found:", left[0], file=sys.stderr)
        continue
    for t in re.findall(r'`([^`]+)`', cells[1]):
        tp, ti = t.split("/", 1) if "/" in t else ("PHASE1", t)
        if (tp, ti) in nodes:
            edges.append(((fp, fi), (tp, ti)))
        else:
            print("  !! §2 target not found:", t, "from", left[0], file=sys.stderr)
for a, b in edges:
    uk(a, b)

# ---- knowledge-map 已合并的 P/R/S3-VEN 条目与包内同 ID 条目同一实体 ----
for (pkg, i) in list(nodes):
    if pkg != "PHASE1":
        continue
    if i.startswith("P-S"):
        uk(("PHASE1", i), ("P", i))
    elif i.startswith("R-XC"):
        uk(("PHASE1", i), ("R", i))
    elif re.match(r'^S3-VEN-0[2-8]$', i):
        uk(("PHASE1", i), ("Q", i))

# ---- A/B 阶段1 原始包 -> 阶段1 全局条目（evidence_ref 反查 + URL 消歧）----
AB_OVERRIDE = {('A', 'S4-04'): 'S4-PAP-01', ('B', 'S1-03'): 'S1-OFF-02'}
rev = collections.defaultdict(set)
for s in km['sources']:
    for e in s.get('evidence_ref', []) or []:
        m = re.match(r'^([A-Z]):(.+)$', str(e).strip())
        if m and m.group(1) in ("A", "B"):
            rev[(m.group(1), m.group(2).strip())].add(s['id'])
for (pkg, i), n in list(nodes.items()):
    if pkg not in ("A", "B"):
        continue
    cands = rev.get((pkg, i), set())
    if not cands:
        continue
    if len(cands) == 1:
        uk((pkg, i), ("PHASE1", next(iter(cands))))
        continue
    nu = norm_url(n['url'])
    hit = [c for c in cands if ("PHASE1", c) in nodes
           and nu and norm_url(nodes[("PHASE1", c)]['url']) == nu]
    if len(hit) == 1:
        uk((pkg, i), ("PHASE1", hit[0]))
        continue
    ov = AB_OVERRIDE.get((pkg, i))
    if ov and ("PHASE1", ov) in nodes:
        uk((pkg, i), ("PHASE1", ov))
        continue
    pick = sorted(cands)[0]
    uk((pkg, i), ("PHASE1", pick))

# ---- 防线二：仅阶段2 包内净新增实体按同 URL/DOI 归并；禁止桥接两个 PHASE1 分量 ----
def comp_has_p1(root):
    return any(find(k) == root and k[0] == "PHASE1" for k in nodes)


def safe_union_pairs(ks):
    ks = [k for k in ks if nodes[k]['pkg'] in FR]
    for a, b in zip(ks, ks[1:]):
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        if comp_has_p1(ra) and comp_has_p1(rb):
            continue
        union(a, b)


for u, ks in urlidx.items():
    if u:
        safe_union_pairs(ks)
for u, ks in doiidx.items():
    if u:
        safe_union_pairs(ks)

# ---------------- components & categories ----------------
comp = collections.defaultdict(list)
for k in nodes:
    comp[find(k)].append(k)


def cat_phase1(i, title):
    if i.startswith("S1-STD"): return "STD"
    if i.startswith("S1-OFF"): return "OFF"
    if i.startswith("S2-BK"): return "BK"
    if i.startswith("S2-WEB"): return "WEB"
    if i.startswith("S3-VEN"): return "VEN"
    if i.startswith("S4-PAP"): return "PAP"
    if i.startswith("S4-COM"): return "COM"
    if i.startswith("L-"): return "LOC"
    if i.startswith("R-XC"): return "XCV"
    if i.startswith("P-S1"): return "STD" if "ISO" in (title or "").upper() else "OFF"
    if i.startswith("P-S2"): return "WEB"
    if i.startswith("P-S3"): return "VEN"
    if i.startswith("P-S4"): return "PAP"
    return "WEB"


def cat_netnew(n):
    i = n['id']; title = n['title'] or ''; org = n['org'] or ''; tier = n['tier']
    up = (title + ' ' + org).upper()
    if n['doi']:
        return "PAP"
    if i.startswith("P-") or i.startswith("R-XC"):
        return cat_phase1(i, title)
    if ('ISO 25000' in up) or ('ISO/IEC 25010' in up) or ('ISO 25010' in up):
        return "STD"
    if tier == "S4":
        return "PAP"
    if tier == "S3":
        return "VEN"
    if tier == "S2":
        if any(k in up for k in ('ADDISON', "O'REILLY", 'PEARSON', 'MANNING', 'PRAGMATIC',
                                 'WILEY', 'MICROSOFT PRESS', 'PRESS', 'BOOK')):
            return "BK"
        return "WEB"
    if tier == "S1":
        official_body = any(k in up for k in ('SWEBOK', 'COMPUTER SOCIETY', 'SEBOK',
                                              'SEI', 'ISTQB', 'CONSORTIUM'))
        is_std = any(k in up for k in ('ISO', 'IEC', 'IEEE', 'IETF', 'RFC', 'W3C', 'STANDARD'))
        return "OFF" if (official_body or not is_std) else "STD"
    return "WEB"


def comp_sortkey(root):
    ks = comp[root]
    p1 = [k for k in ks if k[0] == "PHASE1"]
    if p1:
        return (0, min(nodes[k]['srcindex'] for k in p1))
    others = [k for k in ks if k[0] in ("A", "B")]
    if others:
        return (1, min((PKG_ORDER.index(k[0]), nodes[k]['srcindex']) for k in others))
    return (2, min((PKG_ORDER.index(k[0]) if k[0] in PKG_ORDER else 99,
                    nodes[k]['srcindex']) for k in ks))


cat_of = {}
for root, ks in comp.items():
    p1 = [k for k in ks if k[0] == "PHASE1"]
    if p1:
        p1.sort(key=lambda k: nodes[k]['srcindex'])
        cat_of[root] = cat_phase1(p1[0][1], nodes[p1[0]]['title'])
    else:
        k0 = sorted(ks, key=lambda k: (PKG_ORDER.index(k[0]) if k[0] in PKG_ORDER else 99,
                                       nodes[k]['srcindex']))[0]
        cat_of[root] = cat_netnew(nodes[k0])

bycat = collections.defaultdict(list)
for root in comp:
    bycat[cat_of[root]].append(root)
canon = {}
for cat, roots in bycat.items():
    roots.sort(key=comp_sortkey)
    for idx, root in enumerate(roots, 1):
        canon[root] = f"{cat}-{idx:03d}"

# ---------------- entity_key ----------------
def entity_key(root):
    ks = sorted(comp[root], key=lambda k: (0 if k[0] == "PHASE1" else 1, nodes[k]['srcindex']))
    for k in ks:
        u = norm_url(nodes[k]['url'])
        if u:
            return "url:" + u
    for k in ks:
        d = norm_doi(nodes[k]['doi'])
        if d:
            return "doi:" + d
    n = nodes[ks[0]]
    return "title+org+year:" + re.sub(r'\s+', ' ', (n['title'] + '|' + n['org'] + '|' + str(n['year']))).strip()

# ---------------- actions / collisions ----------------
canonical_ids = set(canon.values())
oldid_map = collections.defaultdict(dict)   # old_id -> {pkg: canonical}
for k in nodes:
    oldid_map[k[1]][k[0]] = canon[find(k)]

entries = []
collisions = []
for old_id, pkgmap in sorted(oldid_map.items()):
    if len(set(pkgmap.values())) > 1:
        collisions.append({
            "old_id": old_id,
            "rule": "same_id_diff_entity_split",
            "occurrences": [{"source_pack": p, "canonical_id": c}
                            for p, c in sorted(pkgmap.items())],
        })

for pkg in ["PHASE1"] + PKG_ORDER:
    ks = [k for k in order if k[0] == pkg]
    for k in ks:
        root = find(k)
        old_id = k[1]
        canon_id = canon[root]
        pkgmap = oldid_map[old_id]
        if len(set(pkgmap.values())) > 1:
            action = "collision_split"
            note = "同形 ID 跨包指向不同实体，按 URL/DOI 拆分"
        elif len(comp[root]) > 1:
            action = "merge"
            note = "同实体复用：" + ", ".join(f"{p}/{i}" for (p, i) in
                                               sorted(comp[root],
                                                      key=lambda x: (x[0] != "PHASE1", x[0], x[1]))
                                               if (p, i) != k)
        else:
            action = "rename"
            note = "净新增/直接重命名"
        entries.append({
            "old_id": old_id,
            "source_pack": pkg,
            "entity_key": entity_key(root),
            "canonical_id": canon_id,
            "action": action,
            "note": note,
        })

# ---------------- stats ----------------
by_pkg = collections.Counter(e['source_pack'] for e in entries)
by_action = collections.Counter(e['action'] for e in entries)
out = {
    "namespace_version": "1.0.0",
    "generated": "2026-09-10",
    "generator": "16-checkpoint/build_mapping.py",
    "entity_rule": "normalized URL > DOI > (title+org+year); authoritative reuse edges = sources-index.md §2 + knowledge-map evidence_ref",
    "canonical_prefixes": ["STD", "OFF", "BK", "WEB", "VEN", "PAP", "COM", "LOC", "XCV"],
    "totals": {
        "entries": len(entries),
        "entities": len(comp),
        "by_package": dict(sorted(by_pkg.items(), key=lambda x: (x[0] != "PHASE1", x[0]))),
        "by_action": dict(sorted(by_action.items())),
        "by_category": {c: len(r) for c, r in sorted(bycat.items())},
    },
    "collisions": collisions,
    "entries": entries,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

print(json.dumps(out["totals"], ensure_ascii=False, indent=2))
print("collisions:", len(collisions))
for c in collisions:
    print("  ", c["old_id"], c["occurrences"])
print("wrote", OUT)
