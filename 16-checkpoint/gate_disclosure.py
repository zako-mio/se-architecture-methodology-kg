#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate_disclosure.py — 披露口径门控（公开仓发布前硬门禁）

作用:
    扫描 --root 下所有「文本类」文件（见 TEXT_EXTS），若正文出现任何一条
    「披露口径」禁用词（揭露采集渠道 / 来源合法性 / 版权风险），即判 FAIL，
    退出码 1。CI 在生成 Pages 工件之前运行本门控，任何命中都会阻断部署。

用法:
    python3 16-checkpoint/gate_disclosure.py --root .            # 默认 root=.
    python3 16-checkpoint/gate_disclosure.py --root _publish --quiet
    python3 16-checkpoint/gate_disclosure.py --root . --json

豁免:
    16-checkpoint/disclosure-allowlist.txt（相对 --root）逐行声明
    「相对路径 :: 豁免词」或「相对路径 :: *」。命中豁免即跳过该条。
    该豁免登记簿自身被本脚本跳过（它天然要书写禁用词）。用法见该文件头部。

输出:
    逐条「文件 :: 行号 :: 命中词（脱敏展示）」，不回显整行原文。
    --json 时输出结构化 JSON（命中词仍脱敏）。
    有命中 exit 1；干净 exit 0；用法/读取错误 exit 2。

为何词表用「分片拼接」而非明文常量:
    本门控会被自己扫描（--root . 覆盖 16-checkpoint/）。若源码里以明文写死
    禁用词，门控将命中自身、永远无法通过，也无法用「脚本自身零命中」作为
    自检证据。故把所有词条拆成片段、运行时 join 还原；源文件字节中不出现
    任何完整禁用词。修改词表时同样必须保持分片写法。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# 禁用词表：分片构造（切勿改为明文，原因见模块 docstring）
# ---------------------------------------------------------------------------
_TERM_PARTS = (
    ("来", "源", "受限"),
    ("第", "三方", "副本"),
    ("非", "官方", "渠道"),
    ("网", "盘"),
    ("影", "子", "库"),
    ("盗", "版"),
    ("lib", "gen"),
    ("annas", "-archive"),
    ("z", "-library"),
    ("z", "lib"),
    ("52", "pojie"),
    ("vdoc", ".pub"),
    ("a", "cloud"),
    ("aliyun", "drive"),
)
TERMS = tuple("".join(parts) for parts in _TERM_PARTS)

# 文本类扩展名（与契约 §6 一致；二进制/脚本类不在扫描范围）
TEXT_EXTS = (".md", ".html", ".json", ".txt", ".yml", ".yaml", ".css", ".js", ".svg")

# 扫描时跳过的目录名
SKIP_DIRS = {".git", "__pycache__"}

ALLOWLIST_REL = os.path.join("16-checkpoint", "disclosure-allowlist.txt")

_TERM_RE = re.compile("|".join(re.escape(t) for t in TERMS), re.IGNORECASE)
_LOWER_TO_TERM = {t.lower(): t for t in TERMS}


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------
def mask_term(term):
    """脱敏展示：保留首字符，第二字符替换为 *（如 来*受限）。"""
    if not term:
        return ""
    if len(term) == 1:
        return "*"
    return term[0] + "*" + term[2:]


def rel_posix(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")


def has_text_ext(name):
    low = name.lower()
    return any(low.endswith(ext) for ext in TEXT_EXTS)


def load_allowlist(root):
    """返回 {相对路径: set(豁免词或 '*')}。文件不存在则返回空表。"""
    path = os.path.join(root, ALLOWLIST_REL)
    table = {}
    if not os.path.isfile(path):
        return table, None
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "::" not in line:
                print(f"[gate_disclosure] WARN allowlist:{lineno} 缺少 '::'，已忽略: {line}",
                      file=sys.stderr)
                continue
            rel, _, term = line.partition("::")
            rel = rel.strip().replace("\\", "/").lstrip("./")
            term = term.strip()
            if not rel or not term:
                print(f"[gate_disclosure] WARN allowlist:{lineno} 路径或词为空，已忽略",
                      file=sys.stderr)
                continue
            table.setdefault(rel, set()).add(term)
    return table, os.path.abspath(path)


def is_exempt(rel, term, table):
    """rel 为相对 root 的 posix 路径；支持精确文件与 'dir/' 前缀两种写法。"""
    if rel in table:
        allowed = table[rel]
        return "*" in allowed or term in allowed
    for key, allowed in table.items():
        if key.endswith("/") and rel.startswith(key):
            if "*" in allowed or term in allowed:
                return True
    return False


def iter_text_files(root, skip_abs):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if not has_text_ext(name):
                continue
            path = os.path.join(dirpath, name)
            if skip_abs and os.path.abspath(path) == skip_abs:
                continue
            yield path


def scan_file(path, root, table):
    """返回 (hits, exemptions)；每条为 (rel, lineno, 规范词)。"""
    rel = rel_posix(path, root)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"[gate_disclosure] WARN 无法读取 {rel}: {exc}", file=sys.stderr)
        return [], []

    hits, exemptions = [], []
    for lineno, line in enumerate(text.splitlines(), 1):
        seen = set()
        for m in _TERM_RE.finditer(line):
            term = _LOWER_TO_TERM.get(m.group().lower())
            if term is None or term in seen:
                continue
            seen.add(term)
            if is_exempt(rel, term, table):
                exemptions.append((rel, lineno, term))
            else:
                hits.append((rel, lineno, term))
    return hits, exemptions


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="披露口径门控：命中禁用词即 FAIL")
    ap.add_argument("--root", default=".", help="扫描根目录（默认 .）")
    ap.add_argument("--quiet", action="store_true", help="干净时不输出；有命中仍打印明细")
    ap.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"[gate_disclosure] ERROR root 不存在或非目录: {args.root}", file=sys.stderr)
        return 2

    table, allowlist_abs = load_allowlist(root)
    hits, exemptions = [], []
    scanned = 0
    for path in iter_text_files(root, allowlist_abs):
        scanned += 1
        fh, fe = scan_file(path, root, table)
        hits.extend(fh)
        exemptions.extend(fe)

    hits.sort(key=lambda h: (h[0], h[1], h[2]))
    exemptions.sort(key=lambda h: (h[0], h[1], h[2]))
    hit_files = len({h[0] for h in hits})

    if args.json:
        print(json.dumps({
            "root": args.root,
            "scanned_files": scanned,
            "hit_count": len(hits),
            "hit_files": hit_files,
            "hits": [{"file": f, "line": ln, "term": mask_term(t)} for f, ln, t in hits],
            "exemption_count": len(exemptions),
            "exemptions": [{"file": f, "line": ln, "term": mask_term(t)}
                           for f, ln, t in exemptions],
        }, ensure_ascii=False, indent=2))
    elif hits:
        for f, ln, t in hits:
            print(f"{f} :: {ln} :: {mask_term(t)}")
        print(f"[gate_disclosure] FAIL: {len(hits)} hit(s) / {hit_files} file(s) "
              f"(root={args.root}, scanned={scanned}, exempt={len(exemptions)})")
    elif not args.quiet:
        print(f"[gate_disclosure] PASS: 0 hit / {scanned} file(s) "
              f"(root={args.root}, exempt={len(exemptions)})")

    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
