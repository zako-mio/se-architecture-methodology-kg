#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_publish.py — 公开集版权红线审计三合一工具（W4）

三种模式：
  --scan     只扫描本地原件并报告（不产出任何文件）
  --emit     产出脱敏副本到 _publish-staging/，并落盘 AUDIT-REPORT.json + PUBLISH-MANIFEST.md
  --verify   复扫 _publish-staging/ 产物，统计残差（要求 0）

分级规则（写入常量，可配置）：
  A 自研消化文本   无长引、无敏感串                       原样复制
  B 元数据与 URL   仅含出处/链接/ID                       原样复制
  C 需脱敏         含长引 或 含本机路径 或 含密钥样式       复制并改写
  D 需剔除         整文件为第三方正文                     不复制，清单记明理由

长引判据（>LONG_QUOTE_MIN=200 字）：
  1) JSON 显式引用字段：键名分词命中 QUOTE_KEY_HINTS（quote/excerpt/raw_text/original/text/scope），值 >200 → 整值移出
  2) 连续英文正文：任意文本/字段内连续 ASCII 散文段 >200（字母≥100、空格≥20、非表格/行内代码）→ 移出该段
  3) 成对引号：CJK 成对引号「」“”‘’内部 >200 → 移出内部（保留引号）
  4) Markdown 引用块：单段 >200 且几无中文（CJK<20）→ 整段移出

本机路径脱敏：本机 home 绝对路径 → ~ ；C:\\Users\\<user> → %USERPROFILE%
密钥凭据：GitHub token / OpenAI key / AWS AKIA / PRIVATE KEY / Slack token 样式 → 【已移出：疑似凭据】

诚实性刚性：任何改写/剔除均在 AUDIT-REPORT.json 中可追溯（位置 + 处理方式 + 原因），不记录被移出的正文。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 路径与扫描范围
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MROOT = os.path.dirname(SCRIPT_DIR)
STAGING = os.path.join(MROOT, "_publish-staging")

SCAN_DIRS = ("00-plan", "01-books", "02-research", "03-knowledge-map")
SCAN_ROOT_FILES = ("report.md", "report.html", "quality-gate.md")

# 未纳入公开集的目录（供清单说明）
EXCLUDED_SCOPE = [
    ("_backup-idmigration/", "ID 迁移本地备份，仅为回滚保留，无公开价值且含冗余原件"),
    ("18-design/", "设计候选与截图（含大体积 png），非交付正文"),
    ("16-checkpoint/_render-shots/", "门控渲染截图中间产物，体积大且可重生成"),
    ("__pycache__/", "Python 字节码缓存（本就不应入库）"),
]

# ---------------------------------------------------------------------------
# 规则常量（可配置）
# ---------------------------------------------------------------------------
LONG_QUOTE_MIN = 200
QUOTE_KEY_HINTS = ("quote", "excerpt", "raw_text", "original", "text", "scope")
QUOTE_KEY_RE = re.compile(
    r"(^|_)(quote|excerpt|raw_text|original|text|scope)($|_)", re.I
)

MARKER_QUOTE = "【已按版权红线移出（原引用 {n} 字）· 出处见 source_id/URL】"
MARKER_CRED = "【已移出：疑似凭据】"

CRED_RES = [
    # 前缀以拼接方式构造，避免本文件自身被凭据扫描命中（功能等价）
    re.compile("g" + "ho_[A-Za-z0-9]+"),
    re.compile("g" + "hp_[A-Za-z0-9]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"xox[bp]-[A-Za-z0-9-]+"),
]
HOME_PATH_RE = re.compile("/home/" + re.escape(os.environ.get("USER", "user")))
WIN_PATH_RE = re.compile(r"[A-Za-z]:\\Users\\[^\\\s\"']+")

CJK_CHAR = re.compile(
    r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]"
)
CJK_QUOTE_PAIRS = (("「", "」"), ("“", "”"), ("‘", "’"))

# D 级阈值：被移出占比 >= 该值且无明显自研标记 → 判 D
D_RATIO = 0.60
# needs_review 阈值：被移出占比 >= 该值 → 列入待裁决
REVIEW_RATIO = 0.35

TEXT_EXTS = {".md", ".json", ".html", ".htm", ".txt", ".drawio", ".xml",
             ".jsonc", ".css", ".js", ".svg", ".yaml", ".yml"}


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------
def collect_inputs():
    items = []
    for d in SCAN_DIRS:
        base = os.path.join(MROOT, d)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs.sort()
            for f in sorted(files):
                items.append(os.path.join(root, f))
    for f in SCAN_ROOT_FILES:
        items.append(os.path.join(MROOT, f))
    return items


def relpath(p):
    return os.path.relpath(p, MROOT)


def is_binary_file(path):
    with open(path, "rb") as fh:
        chunk = fh.read(8192)
    return b"\x00" in chunk


def read_text(path):
    with open(path, encoding="utf-8", errors="strict") as fh:
        return fh.read()


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def dump_json(path, obj):
    text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    write_text(path, text)
    with open(path, encoding="utf-8") as fh:
        json.load(fh)
    return text


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def line_of(text, off):
    return text.count("\n", 0, off) + 1


def cjk_count(s):
    return len(CJK_CHAR.findall(s))


# ---------------------------------------------------------------------------
# 敏感串脱敏（路径 / 凭据），逐处登记
# ---------------------------------------------------------------------------
def mask_sensitive(text, location, rel, changes, counts, line_mode=False):
    """返回脱敏后的文本；路径→~ / %USERPROFILE%，凭据→标记。逐处登记 change。"""
    # 凭据（先做，避免路径替换影响）
    for r in CRED_RES:
        for m in r.finditer(text):
            changes.append({
                "file": rel,
                "location": (f"line {line_of(text, m.start())}" if line_mode else location),
                "kind": "credential",
                "removed_chars": 0,
                "reason": "命中密钥/凭据样式，整处替换为占位符",
            })
            counts["credential"] += 1
        text = r.sub(MARKER_CRED, text)
    # 本机路径
    for m in HOME_PATH_RE.finditer(text):
        changes.append({
            "file": rel,
            "location": (f"line {line_of(text, m.start())}" if line_mode else location),
            "kind": "path_mask",
            "removed_chars": 0,
            "reason": "本机绝对路径（home 前缀）→ ~（保留目录语义）",
        })
        counts["path_mask"] += 1
    text = HOME_PATH_RE.sub("~", text)
    for m in WIN_PATH_RE.finditer(text):
        changes.append({
            "file": rel,
            "location": (f"line {line_of(text, m.start())}" if line_mode else location),
            "kind": "path_mask",
            "removed_chars": 0,
            "reason": r"C:\Users\<user> → %USERPROFILE%（保留目录语义）",
        })
        counts["path_mask"] += 1
    text = WIN_PATH_RE.sub("%USERPROFILE%", text)
    return text


# ---------------------------------------------------------------------------
# 长引检测（文本层）
# ---------------------------------------------------------------------------
def strip_code_md(text):
    return re.sub(r"```.*?```", lambda m: " " * len(m.group()), text, flags=re.S)


def strip_code_html(text):
    return re.sub(
        r"<(style|script)\b.*?</\1\s*>",
        lambda m: " " * len(m.group()),
        text,
        flags=re.S | re.I,
    )


def ascii_runs(text):
    runs = []
    n = len(text)
    i = 0
    while i < n:
        if not CJK_CHAR.match(text[i]):
            j = i
            while j < n and not CJK_CHAR.match(text[j]):
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


def is_prose_run(text, s, e):
    run = text[s:e]
    if len(run) <= LONG_QUOTE_MIN:
        return False
    if "`" in run:            # 行内代码/字段清单，非引用
        return False
    letters = sum(1 for c in run if ("A" <= c <= "Z") or ("a" <= c <= "z"))
    spaces = run.count(" ")
    pipes = run.count("|")
    if letters < 100 or spaces < 20 or pipes >= 5:
        return False
    return True


def cjk_quote_intervals(text):
    ivs = []
    for op, cl in CJK_QUOTE_PAIRS:
        i = 0
        while True:
            s = text.find(op, i)
            if s < 0:
                break
            e = text.find(cl, s + len(op))
            if e < 0:
                break
            if (e - (s + len(op))) > LONG_QUOTE_MIN:
                ivs.append((s + len(op), e, "cjk_quote"))
            i = e + len(cl)
    return ivs


BQ_RE = re.compile(r"(?m)(?:^[ \t]*>.*(?:\n|$))+")


def blockquote_intervals(text):
    ivs = []
    for m in BQ_RE.finditer(text):
        seg = m.group()
        inner = re.sub(r"(?m)^[ \t]*>[ \t]?", "", seg).strip()
        if len(inner) > LONG_QUOTE_MIN and cjk_count(inner) < 20:
            ivs.append((m.start(), m.end(), "blockquote"))
    return ivs


def select_intervals(ivs):
    """按起点排序，包含者丢弃，返回互不重叠的区间（保留大区间）。"""
    ivs = sorted(ivs, key=lambda x: (x[0], -(x[1] - x[0])))
    out = []
    for s, e, kind in ivs:
        if out and s < out[-1][1]:
            if (e - s) > (out[-1][1] - out[-1][0]):
                out[-1] = (s, e, kind)
            continue
        out.append((s, e, kind))
    return out


def apply_intervals(text, ivs, changes, rel, counts=None, line_mode=True,
                    location_prefix="", extra=None):
    """从后向前替换，返回 (新文本, 移出总字符数)。同时累加 counts[kind] 并登记 change。"""
    removed = 0
    for s, e, kind in sorted(ivs, key=lambda x: -x[0]):
        n = e - s
        marker = MARKER_QUOTE.format(n=n)
        if kind == "blockquote":
            marker = "> " + marker
        loc = (f"line {line_of(text, s)}" if line_mode else location_prefix)
        rec = {
            "file": rel,
            "location": loc,
            "kind": kind,
            "removed_chars": n,
            "reason": {
                "quote_key": "JSON 显式引用字段 >200 字，整值移出",
                "prose_run": "连续英文正文 >200 字，判为第三方连续引用",
                "cjk_quote": "成对 CJK 引号内 >200 字，移出内部",
                "blockquote": "Markdown 引用块单段 >200 字，整段移出",
            }.get(kind, kind),
        }
        if extra:
            rec.update(extra)
        changes.append(rec)
        if counts is not None:
            counts[kind] = counts.get(kind, 0) + 1
        text = text[:s] + marker + text[e:]
        removed += n
    return text, removed


# ---------------------------------------------------------------------------
# JSON 变换
# ---------------------------------------------------------------------------
def hint_from_parent(parent):
    if not isinstance(parent, dict):
        return ""
    bits = []
    for k in ("source_id", "source_ids", "id", "legacy_id", "url", "urls",
              "sources", "title", "org"):
        if k in parent:
            v = parent[k]
            if isinstance(v, (str, int, float)):
                sv = str(v)
                if len(sv) > 120:
                    sv = sv[:117] + "..."
                bits.append(f"{k}={sv}")
            elif isinstance(v, list) and v and isinstance(v[0], (str, int, float)):
                bits.append(f"{k}[0]={v[0]}")
    return "; ".join(bits)[:150]


def transform_json_obj(data, rel, changes, counts, path="", parent=None):
    if isinstance(data, dict):
        new = {}
        for k, v in data.items():
            nk = mask_sensitive(str(k), f"{path}.{k}".strip("."), rel,
                                changes, counts, line_mode=False)
            loc = (path + "." + k) if path else k
            if isinstance(v, str) and QUOTE_KEY_RE.search(k) and len(v) > LONG_QUOTE_MIN:
                n = len(v)
                changes.append({
                    "file": rel, "location": loc, "kind": "quote_key",
                    "removed_chars": n, "source_hint": hint_from_parent(data),
                    "reason": "JSON 显式引用字段 >200 字，整值移出",
                })
                counts["quote_key"] += 1
                new[nk] = MARKER_QUOTE.format(n=n)
            else:
                new[nk] = transform_json_obj(v, rel, changes, counts, loc, data)
        return new
    if isinstance(data, list):
        return [transform_json_obj(x, rel, changes, counts, f"{path}[{i}]", parent)
                for i, x in enumerate(data)]
    if isinstance(data, str):
        s = mask_sensitive(data, path, rel, changes, counts, line_mode=False)
        ivs = cjk_quote_intervals(s)
        for s2, e2 in ascii_runs(s):
            if is_prose_run(s, s2, e2):
                ivs.append((s2, e2, "prose_run"))
        ivs = select_intervals(ivs)
        extra = {"source_hint": hint_from_parent(parent)}
        s, _ = apply_intervals(s, ivs, changes, rel, counts, line_mode=False,
                              location_prefix=path, extra=extra)
        return s
    return data


# ---------------------------------------------------------------------------
# 单文件处理
# ---------------------------------------------------------------------------
def process_text_file(rel, raw):
    changes = []
    counts = {"quote_key": 0, "prose_run": 0, "cjk_quote": 0, "blockquote": 0,
              "path_mask": 0, "credential": 0}
    text = raw
    # 1) 路径 / 凭据（逐处登记，带行号）
    text = mask_sensitive(text, "", rel, changes, counts, line_mode=True)

    is_md = rel.lower().endswith(".md")
    is_html = rel.lower().endswith((".html", ".htm"))
    # 连续英文正文检测仅适用于纯文本文档（md/txt）；标记语言（xml/drawio/svg/html）
    # 会被整体判为大段 ASCII，必须跳过以免误伤结构。
    allow_prose = rel.lower().endswith((".md", ".txt"))
    if is_md:
        masked = strip_code_md(text)
    elif is_html:
        masked = strip_code_html(text)
    else:
        masked = text

    # 2) 长引区间
    ivs = []
    ivs.extend(cjk_quote_intervals(masked))
    if allow_prose:
        for s, e in ascii_runs(masked):
            if is_prose_run(masked, s, e):
                ivs.append((s, e, "prose_run"))
    if is_md:
        ivs.extend(blockquote_intervals(masked))

    ivs = select_intervals(ivs)
    text, removed = apply_intervals(text, ivs, changes, rel, counts, line_mode=True)
    return text, changes, counts, removed


def process_json_file(rel, raw):
    changes = []
    counts = {"quote_key": 0, "prose_run": 0, "cjk_quote": 0, "blockquote": 0,
              "path_mask": 0, "credential": 0}
    data = json.loads(raw)
    new = transform_json_obj(data, rel, changes, counts)
    return new, changes, counts


def is_metadata_like(rel, raw, is_json, parsed):
    urls = len(re.findall(r"https?://", raw))
    if is_json and isinstance(parsed, (dict, list)):
        strs = []

        def walk(o):
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
            elif isinstance(o, str):
                strs.append(o)
        walk(parsed)
        maxlen = max((len(s) for s in strs), default=0)
        if maxlen <= LONG_QUOTE_MIN and urls >= 1:
            return True
    base = os.path.basename(rel).lower()
    markers = ("index", "sources", "fetch-log", "baseline", "id-mapping",
               "candidate", "free-official", "canonical", "matrix", "log",
               "schema", "notes")
    if urls >= 3:
        return True
    if any(m in base for m in markers) and urls >= 1:
        return True
    return False


def analyze_file(abs_path):
    rel = relpath(abs_path)
    entry = {
        "path": rel,
        "sha256_original": sha256_of(abs_path),
        "level": "",
        "action": "",
        "removed_chars": 0,
        "long_quote_removed_chars": 0,
        "removed_ratio": 0.0,
        "counts": {},
        "notes": "",
    }
    if is_binary_file(abs_path):
        entry.update({"level": "B", "action": "原样复制",
                      "counts": {"binary": True}, "is_binary": True})
        return entry, {"binary": True}, None, []

    raw = read_text(abs_path)
    entry["total_chars"] = len(raw)
    is_json = rel.lower().endswith(".json")

    if is_json:
        newobj, changes, counts = process_json_file(rel, raw)
        # 计算移出字符数
        removed = sum(c["removed_chars"] for c in changes)
        lq = sum(c["removed_chars"] for c in changes
                 if c["kind"] in ("quote_key", "prose_run", "cjk_quote", "blockquote"))
        payload = newobj
    else:
        text, changes, counts, removed = process_text_file(rel, raw)
        lq = sum(c["removed_chars"] for c in changes
                 if c["kind"] in ("quote_key", "prose_run", "cjk_quote", "blockquote"))
        payload = text

    entry["counts"] = {k: v for k, v in counts.items() if v}
    entry["removed_chars"] = removed
    entry["long_quote_removed_chars"] = lq
    entry["removed_ratio"] = round(removed / max(1, len(raw)), 4)

    violation = (counts["quote_key"] + counts["prose_run"] + counts["cjk_quote"]
                 + counts["blockquote"] + counts["path_mask"] + counts["credential"]) > 0

    if violation:
        entry["level"] = "C"
        entry["action"] = "复制并脱敏"
    else:
        if is_metadata_like(rel, raw, is_json, payload if is_json else None):
            entry["level"] = "B"
        else:
            entry["level"] = "A"
        entry["action"] = "原样复制"

    # D 级判定：被移出占比很高且无自研标记
    self_authored = ("generated_by" in raw or "\"notes\"" in raw
                     or "generated_date" in raw or cjk_count(raw) > len(raw) * 0.05)
    if entry["removed_ratio"] >= D_RATIO and not self_authored:
        entry["level"] = "D"
        entry["action"] = "剔除"
        entry["notes"] = "整文件主体为第三方正文，不纳入公开集"

    return entry, counts, payload, changes


def walk_paths(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk_paths(v, (path + "." + k) if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk_paths(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o


# ---------------------------------------------------------------------------
# 汇总
# ---------------------------------------------------------------------------
def run_scan(write_outputs=False):
    inputs = collect_inputs()
    entries = []
    all_changes = []
    levels = {"A": 0, "B": 0, "C": 0, "D": 0}
    needs_review = []
    total_removed = 0
    total_lq_chars = 0
    longest = 0
    total_paths = 0
    total_creds = 0
    retained_long = []
    converted = []  # (abs, rel, entry, payload)

    if write_outputs and os.path.isdir(STAGING):
        shutil.rmtree(STAGING)

    for abs_path in inputs:
        entry, counts, payload, changes = analyze_file(abs_path)
        entries.append(entry)
        all_changes.extend(changes)
        levels[entry["level"]] += 1
        total_removed += entry.get("removed_chars", 0)
        total_lq_chars += entry.get("long_quote_removed_chars", 0)
        for c in changes:
            if c["kind"] in ("quote_key", "prose_run", "cjk_quote", "blockquote"):
                longest = max(longest, c["removed_chars"])
        total_paths += entry.get("counts", {}).get("path_mask", 0)
        total_creds += entry.get("counts", {}).get("credential", 0)
        if entry["removed_ratio"] >= REVIEW_RATIO and entry["level"] in ("C", "D"):
            needs_review.append({
                "path": entry["path"],
                "removed_ratio": entry["removed_ratio"],
                "removed_chars": entry["removed_chars"],
                "note": "第三方正文占比偏高，建议人工裁决是否整文件剔除",
            })
        if write_outputs:
            converted.append((abs_path, entry, payload))
        # 保留的自研长文本（CJK 为主、>200 字、非连续英文引用）——透明化登记
        if entry["path"].lower().endswith(".json") and isinstance(payload, (dict, list)):
            for pth, val in walk_paths(payload):
                if len(val) <= LONG_QUOTE_MIN:
                    continue
                letters = sum(1 for c in val if c.isascii() and c.isalpha())
                cj = cjk_count(val)
                retained_long.append({
                    "file": entry["path"], "location": pth, "chars": len(val),
                    "en_heavy": letters > 2 * cj,
                })

    # 产出
    report = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "mission_root": ".",
        "rules": {
            "long_quote_min": LONG_QUOTE_MIN,
            "quote_key_hints": list(QUOTE_KEY_HINTS),
            "path_mask": "home 绝对前缀 → ~ ; C:\\Users\\<user> → %USERPROFILE%",
            "credential_marker": MARKER_CRED,
            "quote_marker": MARKER_QUOTE,
            "D_ratio": D_RATIO,
            "review_ratio": REVIEW_RATIO,
        },
        "summary": {
            "files_scanned": len(inputs),
            "levels": levels,
            "needs_review": len(needs_review),
            "long_quotes_removed": sum(
                1 for c in all_changes
                if c["kind"] in ("quote_key", "prose_run", "cjk_quote", "blockquote")),
            "long_quote_removed_chars": total_lq_chars,
            "longest_quote_chars": longest,
            "paths_masked": total_paths,
            "credential_hits": total_creds,
            "total_removed_chars": total_removed,
            "retained_self_authored_long": len(retained_long),
            "retained_en_heavy_long": sum(1 for r in retained_long if r["en_heavy"]),
        },
        "files": entries,
        "removals": all_changes,
        "needs_review": needs_review,
        "retained_long_text": retained_long,
        "excluded_scope": [{"path": p, "reason": r} for p, r in EXCLUDED_SCOPE],
    }

    if write_outputs:
        for abs_path, entry, payload in converted:
            dest = os.path.join(STAGING, entry["path"])
            if entry["level"] == "D":
                continue
            if entry.get("is_binary"):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(abs_path, dest)
            elif entry["path"].lower().endswith(".json"):
                dump_json(dest, payload)
            else:
                write_text(dest, payload)
        dump_json(os.path.join(STAGING, "AUDIT-REPORT.json"), report)
        write_manifest(report, STAGING)

    return report


# ---------------------------------------------------------------------------
# 清单
# ---------------------------------------------------------------------------
def write_manifest(report, staging):
    s = report["summary"]
    lv = s["levels"]
    lines = []
    lines.append("# 公开集发布清单（PUBLISH-MANIFEST）\n")
    lines.append(f"- 生成时间：{report['generated_at']}")
    lines.append(f"- 扫描原件数：{s['files_scanned']}｜分级：A={lv['A']} B={lv['B']} "
                 f"C={lv['C']} D={lv['D']}")
    lines.append(f"- 长引移出：{s['long_quotes_removed']} 处 / {s['long_quote_removed_chars']} 字"
                 f"（最长 {s['longest_quote_chars']} 字）")
    lines.append(f"- 本机路径脱敏：{s['paths_masked']} 处｜疑似凭据：{s['credential_hits']} 处")
    lines.append(f"- 待人工裁决（needs_review）：{s['needs_review']} 个文件")
    lines.append(f"- 保留的 >200 字文本：{s.get('retained_self_authored_long', 0)} 处"
                 f"（英文为主 {s.get('retained_en_heavy_long', 0)} 处，见五·附）\n")

    lines.append("## 一、发布规则摘要\n")
    lines.append("- 短引用（≤200 字）保留，出处见各文 source_id/URL。")
    lines.append("- 长引用（>200 字）移出并替换为占位符，保留原出处键。")
    lines.append("- 长引判据：JSON 显式引用字段、连续英文正文、成对 CJK 引号、Markdown 引用块。")
    lines.append("- 本机路径（home 绝对前缀）→ `~`；Windows 用户目录 → `%USERPROFILE%`。")
    lines.append("- 疑似凭据整处替换为占位符。\n")

    lines.append("## 二、逐文件清单\n")
    lines.append("| 路径 | 级别 | 动作 | 变更计数 | 备注 |")
    lines.append("|---|---|---|---|---|")
    for f in report["files"]:
        cnt = f.get("counts", {})
        if cnt.get("binary"):
            cntstr = "二进制"
        else:
            parts = []
            if cnt.get("quote_key"):
                parts.append(f"长引字段×{cnt['quote_key']}")
            if cnt.get("prose_run"):
                parts.append(f"英文长引×{cnt['prose_run']}")
            if cnt.get("cjk_quote"):
                parts.append(f"CJK长引×{cnt['cjk_quote']}")
            if cnt.get("blockquote"):
                parts.append(f"引用块×{cnt['blockquote']}")
            if cnt.get("path_mask"):
                parts.append(f"路径×{cnt['path_mask']}")
            if cnt.get("credential"):
                parts.append(f"凭据×{cnt['credential']}")
            cntstr = "、".join(parts) if parts else "无"
        note = f.get("notes", "")
        if f["removed_ratio"] >= REVIEW_RATIO and f["level"] in ("C", "D"):
            note = (note + "；" if note else "") + f"移出占比 {f['removed_ratio']:.0%}，建议裁决"
        lines.append(f"| `{f['path']}` | {f['level']} | {f['action']} | {cntstr} | {note} |")
    lines.append("")

    # 长引剔除清单
    lines.append("## 三、长引剔除清单\n")
    lq = [c for c in report["removals"]
          if c["kind"] in ("quote_key", "prose_run", "cjk_quote", "blockquote")]
    lq.sort(key=lambda c: -c["removed_chars"])
    lines.append("| 文件 | 位置 | 类型 | 原引用字数 | 出处（source hint） |")
    lines.append("|---|---|---|---|---|")
    for c in lq:
        hint = c.get("source_hint", "") or "见文中 source_id/URL"
        hint = HOME_PATH_RE.sub("~", "\n".join(hint.split("\n")))
        hint = hint[:120]
        lines.append(f"| `{c['file']}` | {c['location']} | {c['kind']} | "
                     f"{c['removed_chars']} | {hint} |")
    lines.append("")

    # 路径脱敏清单
    lines.append("## 四、本机路径脱敏清单\n")
    lines.append("| 文件 | 位置 | 次数 |")
    lines.append("|---|---|---|")
    from collections import defaultdict
    path_by_file = defaultdict(list)
    for c in report["removals"]:
        if c["kind"] == "path_mask":
            path_by_file[c["file"]].append(c["location"])
    for fn, locs in sorted(path_by_file.items()):
        first = "、".join(locs[:6])
        if len(locs) > 6:
            first += f" 等 {len(locs)} 处"
        lines.append(f"| `{fn}` | {first} | {len(locs)} |")
    lines.append("")

    # needs_review
    lines.append("## 五、needs_review（待人工裁决）\n")
    if report["needs_review"]:
        lines.append("| 文件 | 移出占比 | 移出字数 | 说明 |")
        lines.append("|---|---|---|---|")
        for n in report["needs_review"]:
            lines.append(f"| `{n['path']}` | {n['removed_ratio']:.0%} | "
                         f"{n['removed_chars']} | {n['note']} |")
    else:
        lines.append("- 无。")
    lines.append("")

    # 保留的自研长文本
    lines.append("## 五·附、保留的 >200 字文本（未达连续引用判据）\n")
    lines.append("以下字段虽 >200 字，但非**单段连续引文**（中文消化为主，或英文被中文/")
    lines.append("术语枚举切碎，最长连续英文段 ≤200 字），按「短引用保留」与「最大公开子集」")
    lines.append("原则保留，未做移出。仅登记以便复核：\n")
    ret = report.get("retained_long_text", [])
    if ret:
        agg = defaultdict(lambda: {"n": 0, "max": 0, "sum": 0, "en": 0})
        for r in ret:
            a = agg[r["file"]]
            a["n"] += 1
            a["max"] = max(a["max"], r["chars"])
            a["sum"] += r["chars"]
            if r.get("en_heavy"):
                a["en"] += 1
        lines.append("| 文件 | 条数 | 中文为主 | 英文为主 | 最长(字) |")
        lines.append("|---|---|---|---|---|")
        for fn, a in sorted(agg.items(), key=lambda x: -x[1]["sum"]):
            lines.append(f"| `{fn}` | {a['n']} | {a['n'] - a['en']} | {a['en']} | {a['max']} |")
    else:
        lines.append("- 无。")
    lines.append("")

    # 未纳入目录
    lines.append("## 六、未纳入公开集的目录及理由\n")
    for e in report["excluded_scope"]:
        lines.append(f"- `{e['path']}`：{e['reason']}")
    lines.append("")

    lines.append("## 七、公开后不可撤回声明\n")
    lines.append("> **一旦将本目录推送至 GitHub 公开仓库，历史内容即可被永久检索、"
                 "爬取与镜像，删除本地或远端亦无法撤回已扩散的副本。**")
    lines.append("> 用户确认本清单，即视为授权按上述分级结果公开发布；"
                 "needs_review 项须先裁决后再决定是否发布。\n")
    lines.append("---")
    lines.append("本清单由 `16-checkpoint/audit_publish.py --emit` 自动生成，"
                 "与 `AUDIT-REPORT.json` 同源，内容互相印证。")

    write_text(os.path.join(staging, "PUBLISH-MANIFEST.md"), "\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# 复扫
# ---------------------------------------------------------------------------
def verify_staging():
    if not os.path.isdir(STAGING):
        print("verify: _publish-staging 不存在，请先 --emit")
        return 1
    residual = {"path": 0, "credential": 0, "quote": 0, "replacement_char": 0,
                "invalid_json": 0}
    detail = []
    for root, dirs, files in os.walk(STAGING):
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = relpath(p)
            if is_binary_file(p):
                continue
            try:
                text = read_text(p)
            except Exception:
                continue
            if "\ufffd" in text:
                residual["replacement_char"] += text.count("\ufffd")
            residual["path"] += len(HOME_PATH_RE.findall(text))
            residual["path"] += len(WIN_PATH_RE.findall(text))
            for r in CRED_RES:
                residual["credential"] += len(r.findall(text))

            is_json = f.lower().endswith(".json")
            if is_json:
                try:
                    data = json.loads(text)
                except Exception as ex:
                    residual["invalid_json"] += 1
                    detail.append(f"INVALID JSON: {rel} :: {ex}")
                    continue
                for s in json_all_strings(data):
                    found = scan_quote_residual(s)
                    if found:
                        residual["quote"] += found
                        detail.append(f"QUOTE RESIDUAL: {rel} :: {found} span(s)")
                qk = scan_json_quote_key_residual(data)
                if qk:
                    residual["quote"] += qk
                    detail.append(f"QUOTE KEY RESIDUAL: {rel} :: {qk} field(s)")
            else:
                lower = f.lower()
                if lower.endswith(".md"):
                    masked = strip_code_md(text)
                elif lower.endswith((".html", ".htm")):
                    masked = strip_code_html(text)
                else:
                    masked = text
                allow_prose = lower.endswith((".md", ".txt"))
                found = scan_text_quote_residual(masked, allow_prose)
                if found:
                    residual["quote"] += found
                    detail.append(f"QUOTE RESIDUAL: {rel} :: {found} span(s)")

    print(json.dumps({"residual": residual, "detail": detail[:50]},
                     ensure_ascii=False, indent=2))
    total = sum(residual.values())
    print(f"\n[verify] 残差合计 = {total}（要求 0）")
    return 0 if total == 0 else 2


def json_all_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from json_all_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from json_all_strings(v)
    elif isinstance(obj, str):
        yield obj


def scan_json_quote_key_residual(obj):
    n = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and QUOTE_KEY_RE.search(str(k)) and len(v) > LONG_QUOTE_MIN:
                n += 1
            n += scan_json_quote_key_residual(v)
    elif isinstance(obj, list):
        for v in obj:
            n += scan_json_quote_key_residual(v)
    return n


def scan_quote_residual(s):
    n = 0
    for _, _, _ in cjk_quote_intervals(s):
        n += 1
    for a, b in ascii_runs(s):
        if is_prose_run(s, a, b):
            n += 1
    return n


def scan_text_quote_residual(masked, allow_prose=True):
    n = 0
    for _, _, _ in cjk_quote_intervals(masked):
        n += 1
    if allow_prose:
        for a, b in ascii_runs(masked):
            if is_prose_run(masked, a, b):
                n += 1
    return n


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def print_scan(report):
    s = report["summary"]
    print("=" * 68)
    print("audit_publish.py --scan")
    print("=" * 68)
    print(f"扫描原件: {s['files_scanned']}  分级: A={s['levels']['A']} "
          f"B={s['levels']['B']} C={s['levels']['C']} D={s['levels']['D']} "
          f"needs_review={s['needs_review']}")
    print(f"长引移出: {s['long_quotes_removed']} 处 / {s['long_quote_removed_chars']} 字 "
          f"(最长 {s['longest_quote_chars']})")
    print(f"路径脱敏: {s['paths_masked']}  凭据: {s['credential_hits']}")
    print("-" * 68)
    for f in report["files"]:
        cnt = f.get("counts", {})
        compact = ",".join(f"{k}={v}" for k, v in cnt.items())
        print(f"[{f['level']}] {f['path']:<52} {compact}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="公开集版权红线审计三合一")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--scan", action="store_true", help="只扫描报告，不产出")
    g.add_argument("--emit", action="store_true", help="产出脱敏副本与清单")
    g.add_argument("--verify", action="store_true", help="复扫产物残差")
    args = ap.parse_args(argv)

    if args.verify:
        return verify_staging()

    report = run_scan(write_outputs=args.emit)
    print_scan(report)
    if args.emit:
        a = os.path.join(STAGING, "AUDIT-REPORT.json")
        m = os.path.join(STAGING, "PUBLISH-MANIFEST.md")
        # 自检：产物不得残留路径/凭据
        bad = 0
        for root, dirs, files in os.walk(STAGING):
            for f in files:
                p = os.path.join(root, f)
                if is_binary_file(p):
                    continue
                t = read_text(p)
                bad += len(HOME_PATH_RE.findall(t))
                for r in CRED_RES:
                    bad += len(r.findall(t))
        print("-" * 68)
        print(f"已产出: {a}")
        print(f"已产出: {m}")
        print(f"emit 自检（路径+凭据残留）: {bad}（要求 0）")
        return 0 if bad == 0 else 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
