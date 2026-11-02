#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_secondpass_worklists.py — 把「恢复记录」的第二路复核结论合并进 `<slug>` 的裁决文件

输入：`01-books/_verify/_review/secondpass-worklist-NN-verdicts.json`（复核工人产出）
输出：`01-books/_verify/_review/secondpass-<slug>.json`（`apply_secondpass.py` 的输入）

要点：
- 按 `record_id` 去重（幂等）：已存在的 verdict 以**新产出**为准（复核可重跑）。
- `claim_id` **以当前 ledger 为准**归一化：恢复时曾对 11 条撞号记录重编号，
  工单里的 `claim_id` 是重编号前的旧值。
- 只写 `_review/`，不改任何 SSOT。
- **无变化不写盘**（2026-11-02 修）：原实现会重写**全部**既有 `secondpass-<slug>.json`
  （实测内容逐字节相同，但 mtime 全变、SHA 快照复验看起来像「被改动」）。
  现在先序列化再与磁盘比对，逐字节相同则跳过写盘并计入 `unchanged`。

用法：
  python3 16-checkpoint/merge_secondpass_worklists.py --check
  python3 16-checkpoint/merge_secondpass_worklists.py
  python3 16-checkpoint/merge_secondpass_worklists.py --negative-test   # 2 条负例探针
"""
import argparse
import glob
import json
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
VERIFY = os.path.join("01-books", "_verify")
REVIEW = os.path.join(VERIFY, "_review")
PARTS = os.path.join(VERIFY, "_parts")


def resolve(root, p):
    return p if os.path.isabs(p) else os.path.join(root, p)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def run(root, check=False, quiet=False):
    """执行合并；返回统计。`check=True` 时零写入。"""
    def say(msg):
        if not quiet:
            print(msg)

    # record_id → (slug, claim_id) 以当前 ledger 为准
    rid2slug, rid2cid = {}, {}
    for p in sorted(glob.glob(os.path.join(resolve(root, PARTS), "ledger-*.json"))):
        slug = os.path.basename(p)[len("ledger-"):-len(".json")]
        for r in load(p).get("records") or []:
            rid2slug[r.get("record_id")] = slug
            rid2cid[r.get("record_id")] = r.get("claim_id")

    incoming = {}
    files = sorted(glob.glob(os.path.join(resolve(root, REVIEW),
                                          "secondpass-worklist-*-verdicts.json")))
    for p in files:
        doc = load(p)
        for v in doc.get("verdicts") or []:
            rid = v.get("record_id")
            if not rid:
                continue
            v = dict(v)
            v["claim_id"] = rid2cid.get(rid, v.get("claim_id"))
            v["second_pass_by"] = doc.get("reviewed_by", "")
            incoming[rid] = v
    say("== 第二路复核工单合并 ==")
    say("工单文件 %d 个；verdict %d 条" % (len(files), len(incoming)))

    by_slug = {}
    for rid, v in incoming.items():
        slug = rid2slug.get(rid)
        if not slug:
            say("  ! %s 不在任何 ledger 分片（跳过）" % rid)
            continue
        by_slug.setdefault(slug, {})[rid] = v

    stats = {"files": len(files), "incoming": len(incoming),
             "written": 0, "unchanged": 0, "by_slug": {}}
    for slug in sorted(by_slug):
        vp = resolve(root, os.path.join(REVIEW, "secondpass-%s.json" % slug))
        doc = load(vp) if os.path.isfile(vp) else {
            "reviewed_by": "w-p1-secondpass（合并）", "review_date": "2026-10-12",
            "verdicts": []}
        existing = {v.get("record_id"): v for v in doc.get("verdicts") or []}
        added = updated = 0
        for rid, v in by_slug[slug].items():
            if rid in existing:
                existing[rid] = v
                updated += 1
            else:
                existing[rid] = v
                added += 1
        doc["verdicts"] = [existing[k] for k in sorted(existing)]
        text = dumps(doc)
        same = False
        if os.path.isfile(vp):
            with open(vp, encoding="utf-8") as f:
                same = (f.read() == text)
        say("  [%s] 新增 %d / 更新 %d → 共 %d 条 verdict"
            % (slug, added, updated, len(doc["verdicts"])))
        stats["by_slug"][slug] = {"added": added, "updated": updated,
                                  "total": len(doc["verdicts"]), "same": same}
        if check:
            continue
        if same:
            stats["unchanged"] += 1
            say("    无变化，跳过写盘 %s" % os.path.relpath(vp, root))
            continue
        os.makedirs(os.path.dirname(vp), exist_ok=True)
        with open(vp, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        stats["written"] += 1
        say("    wrote %s" % os.path.relpath(vp, root))

    say("== 写盘 %d / 无变化跳过 %d ==" % (stats["written"], stats["unchanged"]))
    return stats


def negative_test():
    """2 条负例探针：守卫必须**只在真有变化时**写盘（否则等于没装守卫或恒真）。"""
    def probe(name, ok, detail):
        print("  [%s] %s —— %s" % ("OK" if ok else "!! FAILED", name, detail))
        return 0 if ok else 1

    def fixture(tmp, verdict_second="partial"):
        parts = os.path.join(tmp, PARTS)
        review = os.path.join(tmp, REVIEW)
        os.makedirs(parts, exist_ok=True)
        os.makedirs(review, exist_ok=True)
        with open(os.path.join(parts, "ledger-probe.json"), "w", encoding="utf-8") as f:
            f.write(dumps({"book": "probe", "source_id": "BK-999", "records": [
                {"record_id": "VR-PRB-001", "claim_id": "ESS-G-01#definition#301",
                 "node_id": "ESS-G-01", "source_id": "BK-999",
                 "evidence_strength": "direct"}]}))
        with open(os.path.join(review, "secondpass-worklist-01-verdicts.json"),
                  "w", encoding="utf-8") as f:
            f.write(dumps({"reviewed_by": "probe", "verdicts": [
                {"record_id": "VR-PRB-001", "first_pass_strength": "direct",
                 "second_pass_strength": verdict_second, "agree": False}]}))
        return os.path.join(review, "secondpass-probe.json")

    bad = 0
    tmp = tempfile.mkdtemp(prefix="merge2p-neg-")
    try:
        # N1：同一输入连跑两次 ⇒ 第二次必须 0 写盘、1 无变化跳过，文件字节与 mtime 不变。
        out = fixture(tmp)
        s1 = run(tmp, quiet=True)
        st1 = os.stat(out)
        bytes1 = open(out, "rb").read()
        s2 = run(tmp, quiet=True)
        st2 = os.stat(out)
        ok = (s1["written"] == 1 and s2["written"] == 0 and s2["unchanged"] == 1
              and open(out, "rb").read() == bytes1
              and (st1.st_mtime_ns, st1.st_size) == (st2.st_mtime_ns, st2.st_size))
        bad += probe("N1 无变化不写盘（字节与 mtime 均不变）", ok,
                     "written=%d→%d unchanged=%d" % (s1["written"], s2["written"],
                                                     s2["unchanged"]))

        # N2：真变化必须写盘（守卫不是「永远不写」）；且工单变更后内容随之更新。
        #     反证：若守卫写成恒跳过，本探针会失败。
        tmp2 = tempfile.mkdtemp(prefix="merge2p-neg2-")
        try:
            out2 = fixture(tmp2, verdict_second="partial")
            run(tmp2, quiet=True)
            fixture(tmp2, verdict_second="inferred")
            s3 = run(tmp2, quiet=True)
            doc = json.load(open(out2, encoding="utf-8"))
            ok = (s3["written"] == 1
                  and doc["verdicts"][0]["second_pass_strength"] == "inferred")
            bad += probe("N2 内容变化必须写盘（守卫非恒跳过）", ok,
                         "written=%d strength=%s"
                         % (s3["written"],
                            doc["verdicts"][0].get("second_pass_strength")))
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("== 负例探针 %d/%d 如期通过 ==" % (2 - bad, 2))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="合并第二路复核工单结论")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--check", action="store_true", help="只读：报告将写入的内容")
    ap.add_argument("--negative-test", action="store_true", help="跑 2 条负例探针后退出")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.negative_test:
        print("== 负例探针（无变化不写盘守卫） ==")
        return negative_test()

    run(root, check=args.check)
    if args.check:
        print("== --check：未写盘 ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
