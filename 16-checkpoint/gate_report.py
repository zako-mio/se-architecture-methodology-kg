#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_report.py - Mission 报告双版本质量门控（纯标准库 / 确定性 / 无时间戳）。

用法:
    python3 gate_report.py --input <html路径> [--md <md路径>]

判据:
    R1  UTF-8 解码成功、无 BOM、无 U+FFFD
    R2  <div> 与 </div> 数量相等；<section> 与 </section> 数量相等
    R3  5 段标题齐全：当时情况 / 制定计划 / 执行情况 / 完成情况 / 反思（在标题中匹配关键词）
    R4  本地相对链接与图片引用（src= / href= 指向本地文件者）目标存在；外链与页内锚点跳过
    R5  若给了 --md：MD 与 HTML 的段落（小节标题）计数一致（容差 ±1）

退出码: 全部 PASS 返回 0；否则返回 1。
"""

import argparse
import os
import re
import sys
import urllib.parse

BOM = b"\xef\xbb\xbf"
REPLACEMENT = "\ufffd"

SECTION_KEYWORDS = ["当时情况", "制定计划", "执行情况", "完成情况", "反思"]

TAG_RE = {
    "div": (re.compile(r"<div\b", re.IGNORECASE), re.compile(r"</div\s*>", re.IGNORECASE)),
    "section": (re.compile(r"<section\b", re.IGNORECASE), re.compile(r"</section\s*>", re.IGNORECASE)),
}

HEADING_RE = re.compile(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]\s*>", re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(r"""(?:src|href)\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
H2H3_RE = re.compile(r"<h[23]\b", re.IGNORECASE)
MD_H23_RE = re.compile(r"^#{2,3}[ \t]", re.MULTILINE)
TAG_STRIP_RE = re.compile(r"<[^>]+>")

EXTERNAL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:")


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def r1_encoding(raw):
    if raw.startswith(BOM):
        return False, "检测到 UTF-8 BOM"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return False, "UTF-8 解码失败: %s" % exc
    if REPLACEMENT in text:
        return False, "含 U+FFFD 替换字符"
    return True, "UTF-8 无 BOM / 无 U+FFFD"


def r2_tags(html):
    problems = []
    details = []
    for name, (open_re, close_re) in TAG_RE.items():
        n_open = len(open_re.findall(html))
        n_close = len(close_re.findall(html))
        if n_open == n_close:
            details.append("%s %d/%d" % (name, n_open, n_close))
        else:
            problems.append("%s 开 %d != 闭 %d" % (name, n_open, n_close))
    if problems:
        return False, "; ".join(problems)
    return True, "标签平衡: " + ", ".join(details)


def r3_sections(html):
    headings = [TAG_STRIP_RE.sub("", h).strip() for h in HEADING_RE.findall(html)]
    missing = [kw for kw in SECTION_KEYWORDS if not any(kw in h for h in headings)]
    if missing:
        return False, "缺段标题关键词: " + ", ".join(missing)
    return True, "5 段标题齐全: " + " / ".join(SECTION_KEYWORDS)


def r4_links(html, base_dir):
    checked = 0
    missing = []
    for m in ATTR_RE.finditer(html):
        target = (m.group(1) if m.group(1) is not None else m.group(2) or "").strip()
        if not target or target.startswith("#"):
            continue
        low = target.lower()
        if low.startswith(EXTERNAL_PREFIXES):
            continue
        # 去掉 query 与 fragment
        path_part = target.split("#", 1)[0].split("?", 1)[0]
        if not path_part:
            continue
        path_part = urllib.parse.unquote(path_part)
        if os.path.isabs(path_part):
            resolved = path_part
        else:
            resolved = os.path.join(base_dir, path_part)
        checked += 1
        if not os.path.exists(resolved):
            missing.append(target)
    if missing:
        return False, "本地引用目标缺失 %d 个: %s" % (len(missing), ", ".join(sorted(missing)))
    return True, "本地引用 %d 个目标均存在（外链/锚点跳过）" % checked


def r5_paragraphs(html, md_text):
    main_match = re.search(r"<main\b[^>]*>(.*?)</main\s*>", html, re.IGNORECASE | re.DOTALL)
    content = main_match.group(1) if main_match else html
    n_html = len(H2H3_RE.findall(content))
    n_md = len(MD_H23_RE.findall(md_text))
    if abs(n_html - n_md) <= 1:
        return True, "段落(小节标题)计数一致: md=%d html=%d" % (n_md, n_html)
    return False, "段落(小节标题)计数不一致: md=%d html=%d（容差 ±1）" % (n_md, n_html)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Mission 报告双版本质量门控")
    parser.add_argument("--input", required=True, help="HTML 报告路径")
    parser.add_argument("--md", default=None, help="可选的 Markdown 报告路径（用于 R5）")
    args = parser.parse_args(argv)

    html_path = os.path.abspath(args.input)
    if not os.path.isfile(html_path):
        print("[FAIL] R0 输入文件不存在: %s" % html_path)
        print("汇总: 1 项, PASS 0, FAIL 1")
        return 1

    raw = read_bytes(html_path)
    results = []

    ok, msg = r1_encoding(raw)
    results.append(("R1", ok, msg))
    html = raw.decode("utf-8", errors="replace")

    ok, msg = r2_tags(html)
    results.append(("R2", ok, msg))

    ok, msg = r3_sections(html)
    results.append(("R3", ok, msg))

    ok, msg = r4_links(html, os.path.dirname(html_path))
    results.append(("R4", ok, msg))

    if args.md:
        md_path = os.path.abspath(args.md)
        if not os.path.isfile(md_path):
            results.append(("R5", False, "Markdown 文件不存在: %s" % md_path))
        else:
            md_text = read_bytes(md_path).decode("utf-8", errors="replace")
            ok, msg = r5_paragraphs(html, md_text)
            results.append(("R5", ok, msg))
    else:
        results.append(("R5", True, "未提供 --md，跳过（SKIPPED 非 FAIL）"))

    n_fail = 0
    for rid, ok, msg in results:
        tag = "[PASS]" if ok else "[FAIL]"
        if not ok:
            n_fail += 1
        print("%s %s %s" % (tag, rid, msg))

    print("汇总: %d 项, PASS %d, FAIL %d" % (len(results), len(results) - n_fail, n_fail))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
