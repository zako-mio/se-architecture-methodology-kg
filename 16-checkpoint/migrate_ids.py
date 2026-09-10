#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_ids.py — 按 00-plan/id-mapping.json 脚本化重写信源 ID 引用（安全迁移）

原则（id-migration-plan.md §2.2）：
  * 读映射表，按 (source_pack, old_id) 与 跨包限定 "PKG:old_id" 精确匹配；
  * **禁止裸正则全局替换**（防同形碰撞 ID 被误伤）；
  * 重写 sources[].id（并保留 legacy_id）、definitions[].source_id、
    findings[].source_ids[] 及一切 source_id/source_ids/sources(字符串列表) 字段；
  * 保持 UTF-8、无 BOM；输出变更台账 16-checkpoint/migration-ledger.json。

用法：
  python3 16-checkpoint/migrate_ids.py            # 默认 --dry-run（只报告不写盘）
  python3 16-checkpoint/migrate_ids.py --apply    # 实际写盘
"""
import json, re, os, sys, argparse, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPING = os.path.join(ROOT, "00-plan", "id-mapping.json")
LEDGER = os.path.join(ROOT, "16-checkpoint", "migration-ledger.json")
PKGS = ["A", "B", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R"]
KM_PATH = os.path.join(ROOT, "03-knowledge-map", "knowledge-map.json")

QUALIFIED = re.compile(r'^([A-Za-z]{1,3}):(.+)$')
OLD_FORM = re.compile(r'(?:^|:)(S[1-4]-(?:STD|OFF|BK|WEB|VEN|PAP|COM)?-?\d+|S[1-4]-[A-Z]\d+|'
                      r'P-S[1-4]-\d+|R-XC-\d+|L-[A-Z]{2}-\d+|R-XC)$')


def load_mapping():
    m = json.load(open(MAPPING, encoding="utf-8"))
    lookup = {}
    canonical = set()
    for e in m["entries"]:
        lookup[(e["source_pack"], e["old_id"])] = e["canonical_id"]
        canonical.add(e["canonical_id"])
    return m, lookup, canonical


def target_files(root):
    files = []
    for p in PKGS:
        if p == "O":
            fp = os.path.join(root, "02-research", "O-methodology.json")
        else:
            hits = [f for f in os.listdir(os.path.join(root, "02-research"))
                    if f.startswith(p + "-") and f.endswith(".json")]
            fp = os.path.join(root, "02-research", hits[0]) if hits else None
        if fp and os.path.exists(fp):
            files.append((p, fp))
    files.append(("PHASE1", KM_PATH))
    return files


def migrate(apply, only=None):
    m, lookup, canonical = load_mapping()
    ledger = {"generated": m.get("generated"), "applied": bool(apply),
              "files": [], "unresolved": [], "totals": {"ids_rewritten": 0,
                                                        "refs_rewritten": 0, "legacy_added": 0}}
    for pkg, path in target_files(ROOT):
        if only and pkg not in only:
            continue
        raw = open(path, "rb").read()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig" if bom else "utf-8")
        doc = json.loads(text)
        fl = {"package": pkg, "file": os.path.relpath(path, ROOT),
              "sources": 0, "ids": 0, "refs": 0, "legacy": 0, "bom": bom}

        def resolve(value, self_pkg):
            if not isinstance(value, str):
                return value, False, False
            if value in canonical:
                return value, False, True
            mq = QUALIFIED.match(value)
            if mq and (mq.group(1), mq.group(2)) in lookup:
                return lookup[(mq.group(1), mq.group(2))], True, True
            if (self_pkg, value) in lookup:
                return lookup[(self_pkg, value)], True, True
            return value, False, False

        # 1) top-level sources[].id
        if isinstance(doc.get("sources"), list):
            for s in doc["sources"]:
                if isinstance(s, dict) and "id" in s:
                    fl["sources"] += 1
                    old = s["id"]
                    if (pkg, old) in lookup:
                        if "legacy_id" not in s:
                            s["legacy_id"] = old
                            fl["legacy"] += 1
                            ledger["totals"]["legacy_added"] += 1
                        s["id"] = lookup[(pkg, old)]
                        fl["ids"] += 1
                        ledger["totals"]["ids_rewritten"] += 1
                    elif old in canonical:
                        pass  # already migrated (idempotent)
                    else:
                        ledger["unresolved"].append({"file": fl["file"], "where": "sources[].id", "value": old})

        # 2) recursive reference fields
        def walk(o):
            if isinstance(o, dict):
                for key, val in list(o.items()):
                    if key == "source_id" and isinstance(val, str):
                        nv, ch, ok = resolve(val, pkg)
                        if ch:
                            o[key] = nv
                            fl["refs"] += 1
                            ledger["totals"]["refs_rewritten"] += 1
                        elif not ok and OLD_FORM.search(val):
                            ledger["unresolved"].append({"file": fl["file"], "where": "source_id", "value": val})
                    elif key == "source_ids" and isinstance(val, list):
                        new = []
                        for x in val:
                            nv, ch, ok = resolve(x, pkg)
                            if ch:
                                new.append(nv)
                                fl["refs"] += 1
                                ledger["totals"]["refs_rewritten"] += 1
                            else:
                                new.append(x)
                                if not ok and isinstance(x, str) and OLD_FORM.search(x):
                                    ledger["unresolved"].append({"file": fl["file"], "where": "source_ids[]", "value": x})
                        o[key] = new
                    elif key == "sources" and isinstance(val, list) and val and \
                            all(isinstance(x, str) for x in val):
                        new = []
                        for x in val:
                            nv, ch, ok = resolve(x, pkg)
                            if ch:
                                new.append(nv)
                                fl["refs"] += 1
                                ledger["totals"]["refs_rewritten"] += 1
                            else:
                                new.append(x)
                                if not ok and OLD_FORM.search(x):
                                    ledger["unresolved"].append({"file": fl["file"], "where": "sources[str]", "value": x})
                        o[key] = new
                    else:
                        walk(val)
            elif isinstance(o, list):
                for x in o:
                    walk(x)

        walk(doc)
        ledger["files"].append(fl)
        if apply:
            out = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
            if "\ufffd" in out:
                raise SystemExit("FATAL: U+FFFD introduced in " + path)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(out)
    with open(LEDGER, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return ledger


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写盘（默认 dry-run）")
    ap.add_argument("--pkg", nargs="*", help="仅处理指定包")
    args = ap.parse_args()
    led = migrate(args.apply, args.pkg)
    print("applied:", led["applied"])
    print("totals:", json.dumps(led["totals"], ensure_ascii=False))
    for f in led["files"]:
        print(f"  {f['package']:<6} sources={f['sources']:<4} ids={f['ids']:<4} refs={f['refs']:<4} legacy={f['legacy']}")
    print("unresolved:", len(led["unresolved"]))
    for u in led["unresolved"][:40]:
        print("   ", u)
