#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recover_trimmed_records.py — 从 DSH 会话转录回捞「按上限被裁」的核验记录

背景（2026-10-12）：BK-025《SRE》/ BK-026《Workbook》入层后，14 个 K 域节点记录数达
10–12 ⇒ `G-V1` FAIL。上一轮按 ADR-003 的「其余节点 8」上限**裁掉 42 条**合法证据
（39 direct + 3 partial），裁剪日志与裁剪前的暂存分片**只存在于 DSH 会话转录**，
仓库内已无副本（`01-books/` 被 gitignore，无 git 历史）。

裁剪前分片规模（裁剪日志实测）与重建口径：

    staging/ledger-sre-a.json   39 → 38   pre = VR-SRE-001..039
    staging/ledger-sre-b.json   39 → 37   pre = VR-SRE-101..139
    staging/ledger-srew-a.json  37 → 18   pre = VR-SREW-001..037
    staging/ledger-srew-b.json  46 → 26   pre = VR-SREW-101..146
    ⇒ pre 合计 161；post 119；差集 42

**待恢复集合 = pre 区间 − 现盘 post 集合**（无需复现裁剪优先级规则）。

数据源：`~/.dsh/sessions/<workspace>/<session>/session.v4.jsonl.zstd`
  · 多帧 zstd（Node 的 `zstdDecompressSync` 只能解首帧；本脚本用 ctypes 调
    `libzstd` 的 `ZSTD_findFrameCompressedSize` + `ZSTD_decompress` 逐帧解）。
  · 会话行是 JSONL；工具结果里的记录对象在 `content[].text` 字符串中，
    `json.loads` 解行后递归收集字符串即可拿到**未转义**原文。

`claim_id` 口径：D2 修复已把 BK-026 侧 claim_id 序号整体重编到 200+（按节点、按
record_id 升序）。会话里同一 record_id 可能同时存在**重编前（<200）与重编后（≥200）**
两个版本 ⇒ 本脚本按「序号大者优先」择版本，并在报告里列出取值来源。

性质：确定性（无时间戳）、只读（除非显式 `--apply`）、UTF-8 无 BOM。

用法：
  python3 16-checkpoint/recover_trimmed_records.py --check     # 只读：重建 + 校验 + 报告
  python3 16-checkpoint/recover_trimmed_records.py --apply     # 写入 _meta/trimmed-recovery.json
  python3 16-checkpoint/recover_trimmed_records.py --apply --restore
        # 额外把记录并入 _parts/ledger-<slug>.json（**须先放宽 DENSIFY_NODES**）
"""
import argparse
import ctypes
import ctypes.util
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
VERIFY = os.path.join("01-books", "_verify")
PARTS = os.path.join(VERIFY, "_parts")
STAGING = os.path.join(VERIFY, "_review", "staging")
META = os.path.join(VERIFY, "_meta")
REPORT_REL = os.path.join(META, "trimmed-recovery.json")

SESSION_ROOT = os.path.expanduser("~/.dsh/sessions")

# 分片 → (record_id 前缀, pre 区间起, pre 区间止, slug)
SHARDS = [
    ("ledger-sre-a.json", "VR-SRE-", 1, 39, "sre-book"),
    ("ledger-sre-b.json", "VR-SRE-", 101, 139, "sre-book"),
    ("ledger-srew-a.json", "VR-SREW-", 1, 37, "workbook"),
    ("ledger-srew-b.json", "VR-SREW-", 101, 146, "workbook"),
]
EXPECT_DROPPED = 42
EXPECT_PRE_TOTAL = 161

RID_RE = re.compile(r"VR-[A-Z0-9]+-\d{3}")


# ---------------- zstd（ctypes libzstd，多帧） ----------------

def _libzstd():
    name = ctypes.util.find_library("zstd") or "libzstd.so.1"
    lib = ctypes.CDLL(name)
    lib.ZSTD_findFrameCompressedSize.restype = ctypes.c_size_t
    lib.ZSTD_findFrameCompressedSize.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    lib.ZSTD_isError.restype = ctypes.c_uint
    lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
    lib.ZSTD_getErrorName.restype = ctypes.c_char_p
    lib.ZSTD_getErrorName.argtypes = [ctypes.c_size_t]
    lib.ZSTD_createDCtx.restype = ctypes.c_void_p
    lib.ZSTD_freeDCtx.argtypes = [ctypes.c_void_p]
    lib.ZSTD_decompressStream.restype = ctypes.c_size_t
    lib.ZSTD_decompressStream.argtypes = [ctypes.c_void_p,
                                          ctypes.POINTER(OutBuf),
                                          ctypes.POINTER(InBuf)]
    return lib


class InBuf(ctypes.Structure):
    _fields_ = [("src", ctypes.c_void_p), ("size", ctypes.c_size_t),
                ("pos", ctypes.c_size_t)]


class OutBuf(ctypes.Structure):
    _fields_ = [("dst", ctypes.c_void_p), ("size", ctypes.c_size_t),
                ("pos", ctypes.c_size_t)]


OUT_CHUNK = 1 << 17


def zstd_decode_all(lib, buf):
    """逐帧解出全部内容（**流式**：帧头可能不带 content size）。

    返回 (text, frames, problems)。
    """
    out, pos, frames, problems = [], 0, 0, []
    n = len(buf)
    while pos < n:
        src = buf[pos:]
        csize = lib.ZSTD_findFrameCompressedSize(src, len(src))
        if lib.ZSTD_isError(csize):
            problems.append("帧 %d @%d：%s"
                            % (frames, pos, lib.ZSTD_getErrorName(csize).decode()))
            break
        frame = src[:csize]
        fbuf = ctypes.create_string_buffer(frame, len(frame))
        inb = InBuf(ctypes.cast(fbuf, ctypes.c_void_p), len(frame), 0)
        dc = lib.ZSTD_createDCtx()
        try:
            while True:
                obuf = ctypes.create_string_buffer(OUT_CHUNK)
                ob = OutBuf(ctypes.cast(obuf, ctypes.c_void_p), OUT_CHUNK, 0)
                ret = lib.ZSTD_decompressStream(dc, ctypes.byref(ob), ctypes.byref(inb))
                if lib.ZSTD_isError(ret):
                    problems.append("帧 %d 解压失败：%s"
                                    % (frames, lib.ZSTD_getErrorName(ret).decode()))
                    break
                if ob.pos:
                    out.append(obuf.raw[:ob.pos])
                if ret == 0:                      # 该帧结束
                    break
                if inb.pos >= inb.size and ob.pos == 0:   # 无进展，防死循环
                    problems.append("帧 %d 解压停滞" % frames)
                    break
        finally:
            lib.ZSTD_freeDCtx(dc)
        frames += 1
        pos += csize
    return b"".join(out).decode("utf-8", errors="replace"), frames, problems


# ---------------- 会话发现与字符串采集 ----------------

def find_workspace_session_dir(root):
    """按会话首帧里的 cwd 匹配 MROOT。"""
    lib = _libzstd()
    want = os.path.abspath(root)
    for d in sorted(glob.glob(os.path.join(SESSION_ROOT, "*"))):
        if not os.path.isdir(d):
            continue
        for sub in sorted(glob.glob(os.path.join(d, "*"))):
            f = os.path.join(sub, "session.v4.jsonl.zstd")
            if not os.path.isfile(f):
                continue
            with open(f, "rb") as fh:
                head = fh.read(1 << 16)
            try:
                text, _, _ = zstd_decode_all(lib, head)
            except Exception:                                   # noqa: BLE001
                continue
            for line in text.splitlines():
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("cwd"):
                    if os.path.abspath(ev["cwd"]) == want:
                        return d
                    break
    return None


def harvest_strings(obj, sink):
    """递归收集 JSON 结构里的全部字符串。"""
    if isinstance(obj, str):
        sink.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            harvest_strings(v, sink)
    elif isinstance(obj, list):
        for v in obj:
            harvest_strings(v, sink)


def iter_sessions(session_dir):
    """逐会话产出 (session_name, text, meta)；**流式**，避免一次性拼出百 MB 字符串。"""
    lib = _libzstd()
    for sub in sorted(glob.glob(os.path.join(session_dir, "*"))):
        f = os.path.join(sub, "session.v4.jsonl.zstd")
        if not os.path.isfile(f):
            continue
        with open(f, "rb") as fh:
            buf = fh.read()
        text, frames, problems = zstd_decode_all(lib, buf)
        sink = []
        for line in text.splitlines():
            try:
                ev = json.loads(line)
            except ValueError:
                sink.append(line)
                continue
            harvest_strings(ev, sink)
        yield (os.path.basename(sub), "\n".join(sink),
               {"session": os.path.basename(sub), "bytes": len(buf),
                "frames": frames, "problems": problems})


# ---------------- 记录对象抽取 ----------------

def match_brace(s, start):
    depth, i, in_str, esc = 0, start, False, False
    while i < len(s):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return -1


def match_brace_esc(s, start):
    """**转义形态**专用配对：字符串由 `\\"` 开闭（正文里的字面引号即 `\\"`）。"""
    depth, i, in_str = 0, start, False
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == '"':
            in_str = not in_str
            i += 2
            continue
        c = s[i]
        if not in_str:
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return -1


LOOKBACK = 4000          # 记录对象的最大回看窗口（记录为紧凑 JSON，实测 < 1.5 KB）
MAX_TRIES = 8            # 每个命中最多尝试的候选 `{` 个数


def parse_record_blob(blob, rid, escaped):
    """解析记录对象。

    ⚠️ 会话里工具结果常被**双重编码**：`json.loads` 解行之后，正文里仍是
    `\\"record_id\\": \\"VR-…\\"` 这种**转义形态**。此时 blob 恰是内层 JSON 的
    **字符串字面量正文**，故 `json.loads('"' + blob + '"')` 可还原内层 JSON 文本，
    再解一次即得记录对象（**不做 `\\"`→`"` 的朴素替换，避免破坏正文里的引号**）。
    """
    try:
        if escaped:
            rec = json.loads(json.loads('"' + blob + '"'))
        else:
            rec = json.loads(blob)
    except ValueError:
        return None
    if isinstance(rec, dict) and rec.get("record_id") == rid:
        return rec
    return None


def extract_records(text, wanted):
    """返回 {record_id: [record, …]}（同一 id 的多个版本）。

    对每个命中同时尝试**普通形态**与**转义形态**两种配对/解析；
    性能护栏：回看窗口与候选个数**有界**，避免在百 MB 文本上做无界 rfind 回溯。
    """
    out = {}
    for m in RID_RE.finditer(text):
        rid = m.group(0)
        if rid not in wanted:
            continue
        i = m.start()
        for matcher, escaped in ((match_brace, False), (match_brace_esc, True)):
            j = text.rfind("{", max(0, i - LOOKBACK), i)
            tries = 0
            while j != -1 and tries < MAX_TRIES:
                tries += 1
                end = matcher(text, j)
                if end != -1:
                    blob = text[j:end + 1]
                    if "record_id" in blob and rid in blob:
                        rec = parse_record_blob(blob, rid, escaped)
                        if rec is not None:
                            out.setdefault(rid, []).append(rec)
                            break
                j = text.rfind("{", max(0, j - LOOKBACK), j)
    return out


def cid_num(rec):
    m = re.search(r"#(\d+)$", str(rec.get("claim_id", "")))
    return int(m.group(1)) if m else -1


def pick_version(versions):
    """择版本：claim_id 序号大者优先（post-D2 重编版本），其次字段多者。"""
    return sorted(versions, key=lambda r: (cid_num(r), len(r)), reverse=True)[0]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def k_domain_nodes():
    """从 gate_verification 取 K 域集合（单一真相源，ADR-005）。"""
    sys.path.insert(0, HERE)
    import gate_verification as G
    return set(G.K_DOMAIN_NODES)


def enforce_domain(root, record_ids):
    """按 ADR-005 边界裁回**域外**被恢复记录。

    ADR-005 只把 **K 域**纳入高档位；`MTH-J-07` / `MTH-N-05` / `TEC-J-04` 等域外贴限
    节点仍适用 8 条上限 ⇒ 其证据**不得**随本轮恢复（须另立 ADR）。
    本步骤把已恢复的域外记录及其 claims 条目一并撤出（幂等）。
    """
    kdom = k_domain_nodes()
    removed = []
    for slug in ("sre-book", "workbook"):
        lp = os.path.join(root, PARTS, "ledger-%s.json" % slug)
        doc = load_json(lp)
        keep, drop = [], []
        for r in doc.get("records") or []:
            if r.get("record_id") in record_ids and r.get("node_id") not in kdom:
                drop.append(r)
            else:
                keep.append(r)
        if not drop:
            continue
        doc["records"] = keep
        with open(lp, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(doc))
        drop_ids = {r["claim_id"] for r in drop}
        cp = os.path.join(root, PARTS, "claims-%s.json" % slug)
        cdoc = load_json(cp)
        for node in list(cdoc):
            claims = [c for c in (cdoc[node].get("claims") or [])
                      if c.get("claim_id") not in drop_ids]
            cdoc[node]["claims"] = claims
        with open(cp, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(cdoc))
        removed.extend({"slug": slug, "record_id": r["record_id"],
                        "node_id": r["node_id"], "claim_id": r["claim_id"],
                        "evidence_strength": r.get("evidence_strength")}
                       for r in drop)
    print("  ADR-005 域外裁回 %d 条：" % len(removed))
    for x in removed:
        print("    %s %s (%s, %s)" % (x["record_id"], x["node_id"], x["claim_id"],
                                      x["evidence_strength"]))
    return removed


def main():
    ap = argparse.ArgumentParser(description="从会话转录回捞被裁的核验记录")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--sessions", default=None, help="会话工作区目录（缺省自动按 cwd 匹配）")
    ap.add_argument("--apply", action="store_true", help="写 _meta/trimmed-recovery.json")
    ap.add_argument("--check", action="store_true",
                    help="只读（默认行为；显式给出以便与其它脚本一致）")
    ap.add_argument("--restore", action="store_true",
                    help="额外把记录并入 _parts/ledger-<slug>.json（须先放宽 DENSIFY_NODES）")
    ap.add_argument("--enforce-domain", action="store_true",
                    help="按 ADR-005 边界裁回**域外**被恢复记录（K 域之外不放宽）")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    problems = []

    # 1) pre 区间与 post 现盘
    pre, post = {}, {}
    for fname, prefix, lo, hi, slug in SHARDS:
        ids = {"%s%03d" % (prefix, n) for n in range(lo, hi + 1)}
        pre[fname] = ids
        p = os.path.join(root, STAGING, fname)
        if not os.path.isfile(p):
            problems.append("缺分片 %s" % fname)
            continue
        post[fname] = {r.get("record_id") for r in load_json(p).get("records") or []}

    if problems:
        for p in problems:
            print("! %s" % p)
        return 1

    dropped = {}
    for fname in pre:
        dropped[fname] = sorted(pre[fname] - post.get(fname, set()))
    total_dropped = sum(len(v) for v in dropped.values())
    total_pre = sum(len(v) for v in pre.values())

    print("== 被裁记录重建 ==")
    print("pre 合计 %d（期望 %d）；post 合计 %d；差集 %d（期望 %d）"
          % (total_pre, EXPECT_PRE_TOTAL, sum(len(v) for v in post.values()),
             total_dropped, EXPECT_DROPPED))
    for fname in sorted(dropped):
        print("  %-22s pre=%2d post=%2d 被裁=%2d" %
              (fname, len(pre[fname]), len(post.get(fname, set())), len(dropped[fname])))

    wanted = {rid for v in dropped.values() for rid in v}

    # 2) 会话转录（流式：逐会话抽记录并合并；全部取到 post-D2 版本即提前收敛）
    sdir = args.sessions or find_workspace_session_dir(root)
    if not sdir:
        print("! 未能定位会话工作区目录（--sessions 显式指定）")
        return 1
    print("\n会话目录 = %s" % sdir)
    versions, sess_meta = {}, []
    for name, text, meta in iter_sessions(sdir):
        sess_meta.append(meta)
        got = extract_records(text, wanted)
        for rid, vs in got.items():
            versions.setdefault(rid, []).extend(vs)
        have_post = {rid for rid, vs in versions.items()
                     if max(cid_num(r) for r in vs) >= 200}
        print("  [%s] 会话 %d/%d 帧=%d 累计取到 %d/%d（其中 post-D2 %d）"
              % (name[:8], len(sess_meta), len(sess_meta), meta["frames"],
                 len(versions), len(wanted), len(have_post)))
        if len(have_post) == len(wanted):
            print("  -> 全部记录已取到 post-D2 版本，提前收敛")
            break
    print("解出会话 %d 个" % len(sess_meta))

    # 3) 择版本
    recovered, missing = {}, []
    for rid in sorted(wanted):
        vs = versions.get(rid) or []
        if not vs:
            missing.append(rid)
            continue
        recovered[rid] = pick_version(vs)

    print("待恢复 %d 条；已取到完整记录对象 %d 条；缺 %d 条"
          % (len(wanted), len(recovered), len(missing)))
    for rid in missing:
        print("  ! 未取到 %s" % rid)

    # 4) 校验：claim_id 唯一性
    # 说明：会话里**只有重编前（<200）版本**（D2 的 BK-026 侧重编号未把完整记录对象
    # 打进会话）⇒ 恢复记录与原 SRE 记录存在**历史撞号**（正是 D2 要解决的 17 对之一）。
    # 处置：`--restore` 时对**撞号者**按确定性规则重编号（保留唯一者可原号），并全程留痕。
    all_cids = {}
    for slug in ("sre-book", "workbook"):
        p = os.path.join(root, PARTS, "ledger-%s.json" % slug)
        for r in load_json(p).get("records") or []:
            all_cids.setdefault(r.get("claim_id"), r.get("record_id"))
    collisions = {}
    for rid, r in sorted(recovered.items()):
        cid = r.get("claim_id")
        if cid in all_cids:
            collisions[rid] = (cid, all_cids[cid])
    print("取到版本全部为重编前（<200）；与现盘 claim_id 撞号 %d 条（restore 时重编号）"
          % len(collisions))
    for rid in sorted(collisions):
        print("    %s: %s ↔ %s" % (rid, collisions[rid][0], collisions[rid][1]))

    # 5) 报告
    report = {
        "meta": {"schema_version": "1.0.0", "generated": "2026-09-11",
                 "source": "DSH session transcripts (multi-frame zstd)"},
        "sessions_dir": sdir,
        "sessions": sess_meta,
        "pre_counts": {k: len(v) for k, v in sorted(pre.items())},
        "post_counts": {k: len(post.get(k, set())) for k in sorted(pre)},
        "dropped_counts": {k: len(v) for k, v in sorted(dropped.items())},
        "dropped_total": total_dropped,
        "recovered_total": len(recovered),
        "missing": missing,
        "problems": problems,
        "claim_id_collisions": {k: {"recovered": v[0], "existing_record": v[1]}
                                for k, v in sorted(collisions.items())},
        "records": [recovered[rid] for rid in sorted(recovered)],
    }

    ok = (not missing and not problems and total_dropped == EXPECT_DROPPED
          and total_pre == EXPECT_PRE_TOTAL)
    print("\n== 校验 = %s ==" % ("PASS" if ok else "FAIL"))
    for p in problems:
        print("  ! %s" % p)

    if args.apply:
        rp = os.path.join(root, REPORT_REL)
        os.makedirs(os.path.dirname(rp), exist_ok=True)
        with open(rp, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(report))
        print("  wrote %s" % REPORT_REL)

    if args.restore:
        if not ok:
            print("  !! --restore 被拒绝：校验未通过")
            return 1
        # 全局已占用的 claim_id（跨全部书）
        taken = set()
        for p in glob.glob(os.path.join(root, PARTS, "ledger-*.json")):
            for r in load_json(p).get("records") or []:
                if r.get("claim_id"):
                    taken.add(r["claim_id"])
        by_slug, renumbers = {}, []
        for fname, _prefix, _lo, _hi, slug in SHARDS:
            for rid in sorted(dropped[fname]):
                r = recovered.get(rid)
                if r is None:
                    continue
                old = r.get("claim_id", "")
                m = re.match(r"^(?P<node>.+)#(?P<origin>[a-z]+)#(?P<n>\d+)$", old)
                if not m:
                    print("  !! %s claim_id 非法，拒绝恢复：%s" % (rid, old))
                    return 1
                if old in taken:                     # 撞号 ⇒ 重编号到下一个空号
                    node, origin = m.group("node"), m.group("origin")
                    k = 1
                    while "%s#%s#%d" % (node, origin, k) in taken:
                        k += 1
                    new = "%s#%s#%d" % (node, origin, k)
                    r = dict(r)
                    r["claim_id"] = new
                    renumbers.append({"record_id": rid, "old_claim_id": old,
                                      "new_claim_id": new, "reason": "与既有 claim_id 撞号"})
                else:
                    new = old
                taken.add(new)
                by_slug.setdefault(slug, []).append(r)
        for slug in sorted(by_slug):
            lp = os.path.join(root, PARTS, "ledger-%s.json" % slug)
            doc = load_json(lp)
            have = {x.get("record_id") for x in doc.get("records") or []}
            added = 0
            for r in by_slug[slug]:
                if r.get("record_id") in have:
                    continue
                doc.setdefault("records", []).append(r)
                have.add(r.get("record_id"))
                added += 1
            doc["records"].sort(key=lambda x: x.get("record_id", ""))
            with open(lp, "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(doc))
            print("  restored %d 条 → %s" % (added, os.path.relpath(lp, root)))
            # claims 分片同步（**不得**对这些书重跑 merge：staging 落后于 _parts）
            cp = os.path.join(root, PARTS, "claims-%s.json" % slug)
            cdoc = load_json(cp) if os.path.isfile(cp) else {}
            cadded = 0
            for r in by_slug[slug]:
                cid = r["claim_id"]
                node = r["node_id"]
                origin = cid.split("#")[1]
                bucket = cdoc.setdefault(node, {"claims": []})
                if any(c.get("claim_id") == cid for c in bucket.get("claims") or []):
                    continue
                bucket.setdefault("claims", []).append(
                    {"claim_id": cid, "text": r.get("claim", ""), "origin": origin})
                cadded += 1
            for node in cdoc:
                cdoc[node]["claims"] = sorted(cdoc[node].get("claims") or [],
                                              key=lambda c: c.get("claim_id", ""))
            with open(cp, "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(cdoc))
            print("  claims +%d 条 → %s" % (cadded, os.path.relpath(cp, root)))
        print("  claim_id 重编号 %d 条：" % len(renumbers))
        for x in renumbers:
            print("    %s: %s => %s" % (x["record_id"], x["old_claim_id"], x["new_claim_id"]))
        report["renumbers"] = renumbers
        if args.apply:
            with open(os.path.join(root, REPORT_REL), "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(report))

    if args.enforce_domain:
        all_dropped = {rid for v in dropped.values() for rid in v}
        removed = enforce_domain(root, all_dropped)
        report["out_of_domain_removed"] = removed
        report["restored_in_domain"] = len(all_dropped) - len(removed)
        if args.apply:
            with open(os.path.join(root, REPORT_REL), "w", encoding="utf-8", newline="\n") as f:
                f.write(dumps(report))

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
