#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_layout.py — L8 版式门控（阶段6·A 案 · 浅色 Codex 文档流）

用法:
    python3 16-checkpoint/gate_layout.py --check all
    python3 16-checkpoint/gate_layout.py --check tradeoff --show 30

契约: 00-plan/stage6-content-ia-spec.md §10（门控点位）

检查项（--check）:
    relation       每节点页内联关系图 svg.nbhd 计数 ≥1
    defcard        每节点页存在 class="defcard" 摘要卡
    tradeoff       每节点页存在 class="tradeoff" 权衡卡；每个已生成分栏（gain/cost/counter）
                   内**全部**句子必须含该栏显式标记词；三栏皆无时须有「原文要点」列表；
                   脚注须声明「显式标记词」归栏规则
    toc            class="toc" 存在；每个 §N 章节有对应 id="sN" 且编号连续；TOC href 全部可解析
    conditional    参与 contrasts/conflicts 的节点须含对比表；参与 prerequisite 的须含 pathbar
                   （反向亦然：未参与却出现对应块视为异常）
    term           全部 a.term 的 href 指向 ../14-views/glossary.html#g-NNN 且锚点存在
    selfcontained  0 <script>、0 外链资源（link/img/script 的 http(s) src/href、CSS url(http)）、
                   0 @import
    encoding       无 U+FFFD、UTF-8 无 BOM
    deeplink       生成物中「2026-08」出现次数为 0
    dualtrack      15-md/nodes/<id>.md 与对应 HTML 的块标题集合一致

结果: PASS / FAIL；仅全项 PASS 时退出码 0。汇总输出覆盖率与问题清单，可复跑幂等。
"""
import argparse
import glob as globmod
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from gen_common import TRADEOFF_MARKERS  # noqa: E402  归栏标记词契约（单一来源）

# ---------------------------------------------------------------- 正则

RE_SVG_NBHD = re.compile(r'<svg[^>]*\bclass="nbhd"')
RE_DEFCARD = re.compile(r'class="defcard"')
RE_TRADEOFF = re.compile(r'<div class="tradeoff">(.*?)</div><p class="note">(.*?)</p>', re.S)
RE_ROW = re.compile(r'<div class="row (gain|cost|counter)"><div class="h">(.*?)</div>'
                    r'<div class="b">(.*?)</div></div>', re.S)
RE_NEUTRAL = re.compile(r'<div class="row neutral"><div class="h">原文要点</div>'
                        r'<ul class="b">(.*?)</ul></div>', re.S)
RE_P = re.compile(r'<p>(.*?)</p>', re.S)
RE_LI = re.compile(r'<li>(.*?)</li>', re.S)
RE_TAG = re.compile(r'<[^>]+>')
RE_TOC = re.compile(r'<nav class="toc">(.*?)</nav>', re.S)
RE_TOC_HREF = re.compile(r'href="#([^"]+)"')
RE_ID = re.compile(r'id="([^"]+)"')
RE_SECTION = re.compile(r'<section id="(s\d+|xref)"><h2><span class="num">([^<]*)</span>'
                        r'([^<]*)</h2>', re.S)
RE_TERM = re.compile(r'<a class="term" href="([^"]+)"')
RE_GLOSS_ID = re.compile(r'id="(g-\d{3})"')
RE_MD_TITLE = re.compile(r'^## (?:§\d+\s+|附\s+)(.+?)\s*$', re.M)
RE_EXT_RES = re.compile(r'<(?:link|img|script|source|iframe)\b[^>]*?\b(?:src|href)="https?://', re.I)
RE_CSS_EXT = re.compile(r'url\(\s*[\'"]?https?://', re.I)
RE_SCRIPT = re.compile(r'<script', re.I)

HTML_DIRS = ["11-node-pages", "12-groups", "14-views"]
MD_DIR = "15-md"


# ---------------------------------------------------------------- 工具

def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def strip_tags(segment):
    return RE_TAG.sub("", segment)


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def incident_nodes(graph, edge_types):
    out = set()
    for e in graph.get("edges", []):
        if e.get("type") in edge_types:
            if e.get("from"):
                out.add(e["from"])
            if e.get("to"):
                out.add(e["to"])
    return out


class Check(object):
    def __init__(self, key, title):
        self.key = key
        self.title = title
        self.checked = 0
        self.passed = 0
        self.issues = []

    def tally(self, ok):
        self.checked += 1
        if ok:
            self.passed += 1

    def fail(self, ident, detail):
        self.issues.append("%s: %s" % (ident, detail))

    @property
    def ok(self):
        return not self.issues

    @property
    def coverage(self):
        return (float(self.passed) / self.checked) if self.checked else 1.0


class Ctx(object):
    def __init__(self, root, graph):
        self.root = root
        self.graph = graph
        self.node_ids = [n["id"] for n in graph.get("nodes", [])]
        self.node_pages = []
        nodes_dir = os.path.join(root, "11-node-pages")
        for nid in self.node_ids:
            p = os.path.join(nodes_dir, nid + ".html")
            if os.path.isfile(p):
                self.node_pages.append((nid, p, read_text(p)))
        self.html_files = []
        for d in HTML_DIRS:
            self.html_files += sorted(globmod.glob(os.path.join(root, d, "*.html")))
        ri = os.path.join(root, "index.html")
        if os.path.isfile(ri):
            self.html_files.append(ri)
        self.doc_files = list(self.html_files)
        for p in sorted(globmod.glob(os.path.join(root, MD_DIR, "**", "*.md"), recursive=True)):
            self.doc_files.append(p)
        gp = os.path.join(root, "14-views", "glossary.html")
        self.glossary_anchors = set()
        if os.path.isfile(gp):
            self.glossary_anchors = set(RE_GLOSS_ID.findall(read_text(gp)))
        self.md_nodes = os.path.join(root, MD_DIR, "nodes")


# ---------------------------------------------------------------- 各检查

def check_relation(ctx, chk):
    for nid, _p, text in ctx.node_pages:
        ok = bool(RE_SVG_NBHD.search(text))
        if not ok:
            chk.fail(nid, "缺少内联关系图 svg.nbhd")
        chk.tally(ok)


def check_defcard(ctx, chk):
    for nid, _p, text in ctx.node_pages:
        ok = bool(RE_DEFCARD.search(text))
        if not ok:
            chk.fail(nid, "缺少摘要卡 class=defcard")
        chk.tally(ok)


def check_tradeoff(ctx, chk):
    for nid, _p, text in ctx.node_pages:
        m = RE_TRADEOFF.search(text)
        if not m:
            chk.fail(nid, "缺少权衡卡 class=tradeoff")
            chk.tally(False)
            continue
        block, note = m.group(1), m.group(2)
        problems = []
        cols = {}
        for rm in RE_ROW.finditer(block):
            cols.setdefault(rm.group(1), []).append(rm.group(3))
        for cat in sorted(cols):
            markers = TRADEOFF_MARKERS[cat]
            for body in cols[cat]:
                ps = RE_P.findall(body)
                if not ps:
                    problems.append("%s 栏为空" % cat)
                for p in ps:
                    plain = strip_tags(p)
                    if not any(mk in plain for mk in markers):
                        problems.append("%s 栏含无标记句「%s」" % (cat, plain[:36]))
        neutral = RE_NEUTRAL.search(block)
        has_neutral = bool(neutral and RE_LI.search(neutral.group(1)))
        if not cols and not has_neutral:
            problems.append("三栏皆空且无「原文要点」列表")
        if "显式标记词" not in note:
            problems.append("脚注未声明「显式标记词」归栏规则")
        for p in problems:
            chk.fail(nid, p)
        chk.tally(not problems)


def check_toc(ctx, chk):
    for nid, _p, text in ctx.node_pages:
        problems = []
        toc_m = RE_TOC.search(text)
        if not toc_m:
            chk.fail(nid, "缺少 nav.toc")
            chk.tally(False)
            continue
        hrefs = RE_TOC_HREF.findall(toc_m.group(1))
        ids = set(RE_ID.findall(text))
        for h in hrefs:
            if h not in ids:
                problems.append("TOC 悬挂锚点 #%s" % h)
        secs = RE_SECTION.findall(text)
        seen_s = []
        for sid, num, _title in secs:
            if sid.startswith("s"):
                seen_s.append(int(sid[1:]))
                if num != "§%d" % int(sid[1:]):
                    problems.append("章节 %s 编号标注为 %s" % (sid, num))
                if sid not in hrefs:
                    problems.append("章节 #%s 未在 TOC 列出" % sid)
        if seen_s != list(range(1, len(seen_s) + 1)):
            problems.append("章节锚点不连续：%s" % seen_s)
        for p in problems:
            chk.fail(nid, p)
        chk.tally(not problems)


def check_conditional(ctx, chk):
    cmp_nodes = incident_nodes(ctx.graph, {"contrasts", "conflicts"})
    pre_nodes = incident_nodes(ctx.graph, {"prerequisite"})
    for nid, _p, text in ctx.node_pages:
        problems = []
        has_cmp = 'class="cmp"' in text
        has_path = 'class="pathbar"' in text
        if nid in cmp_nodes and not has_cmp:
            problems.append("参与 contrasts/conflicts 但缺对比表 table.cmp")
        if nid in pre_nodes and not has_path:
            problems.append("参与 prerequisite 但缺 pathbar")
        if nid not in cmp_nodes and has_cmp:
            problems.append("未参与 contrasts/conflicts 却含对比表")
        if nid not in pre_nodes and has_path:
            problems.append("未参与 prerequisite 却含 pathbar")
        for p in problems:
            chk.fail(nid, p)
        chk.tally(not problems)


def check_term(ctx, chk):
    if not ctx.glossary_anchors:
        chk.fail("14-views/glossary.html", "无可解析术语锚点（g-NNN）")
        chk.tally(False)
        return
    total_links = 0
    for path in ctx.html_files:
        text = read_text(path)
        problems = []
        for href in RE_TERM.findall(text):
            total_links += 1
            if not href.startswith("../14-views/glossary.html#"):
                problems.append("a.term 目标非 glossary.html：%s" % href)
                continue
            frag = href.split("#", 1)[1]
            if frag not in ctx.glossary_anchors:
                problems.append("a.term 锚点不存在：#%s" % frag)
        for p in problems:
            chk.fail(rel(ctx.root, path), p)
        chk.tally(not problems)
    if total_links == 0:
        chk.fail("site", "全站未出现任何 a.term 术语内联")


def check_selfcontained(ctx, chk):
    for path in ctx.html_files:
        text = read_text(path)
        problems = []
        if RE_SCRIPT.search(text):
            problems.append("含 <script>")
        if "@import" in text:
            problems.append("含 @import")
        for m in RE_EXT_RES.finditer(text):
            problems.append("外链资源：%s" % m.group(0)[:70])
        if RE_CSS_EXT.search(text):
            problems.append("CSS url(http) 外链")
        for p in problems:
            chk.fail(rel(ctx.root, path), p)
        chk.tally(not problems)


def check_encoding(ctx, chk):
    for path in ctx.doc_files:
        raw = read_bytes(path)
        problems = []
        if raw.startswith(b"\xef\xbb\xbf"):
            problems.append("含 UTF-8 BOM")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            problems.append("非合法 UTF-8：%s" % exc)
            text = ""
        if "\ufffd" in text:
            problems.append("含 U+FFFD 替换字符")
        for p in problems:
            chk.fail(rel(ctx.root, path), p)
        chk.tally(not problems)


def check_deeplink(ctx, chk):
    for path in ctx.doc_files:
        text = read_text(path)
        n = text.count("2026-08")
        if n:
            chk.fail(rel(ctx.root, path), "出现 %d 次「2026-08」" % n)
        chk.tally(n == 0)


def check_dualtrack(ctx, chk):
    for nid, _p, html in ctx.node_pages:
        md_path = os.path.join(ctx.md_nodes, nid + ".md")
        if not os.path.isfile(md_path):
            chk.fail(nid, "缺少 MD 镜像 %s" % rel(ctx.root, md_path))
            chk.tally(False)
            continue
        md = read_text(md_path)
        html_titles = [t.strip() for _sid, _num, t in RE_SECTION.findall(html)]
        md_titles = [t.strip() for t in RE_MD_TITLE.findall(md)]
        problems = []
        if set(html_titles) != set(md_titles):
            only_html = [t for t in html_titles if t not in set(md_titles)]
            only_md = [t for t in md_titles if t not in set(html_titles)]
            if only_html:
                problems.append("仅 HTML 有块：%s" % only_html)
            if only_md:
                problems.append("仅 MD 有块：%s" % only_md)
        for p in problems:
            chk.fail(nid, p)
        chk.tally(not problems)


CHECKS = [
    ("relation", "关系图（每节点页 svg.nbhd ≥1）", check_relation),
    ("defcard", "摘要卡（class=defcard）", check_defcard),
    ("tradeoff", "权衡卡（显式标记词严格归栏）", check_tradeoff),
    ("toc", "TOC / 锚点（无悬挂、编号连续）", check_toc),
    ("conditional", "条件块（对比表 / 学习路径条）", check_conditional),
    ("term", "术语链接（a.term → glossary 锚点）", check_term),
    ("selfcontained", "自包含（0 JS / 0 外链资源）", check_selfcontained),
    ("encoding", "编码（无 BOM / U+FFFD）", check_encoding),
    ("deeplink", "深链（无 2026-08）", check_deeplink),
    ("dualtrack", "双轨一致（HTML↔MD 块标题）", check_dualtrack),
]


def main():
    ap = argparse.ArgumentParser(description="L8 版式门控（阶段6·A 案）")
    ap.add_argument("--check", default="all",
                    choices=[k for k, _t, _f in CHECKS] + ["all"])
    ap.add_argument("--graph", default=os.path.join("10-dag-data", "methodology-dag.json"))
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--show", type=int, default=15)
    args = ap.parse_args()

    root = args.repo_root or ROOT_DEFAULT
    graph_path = args.graph if os.path.isabs(args.graph) else os.path.join(root, args.graph)

    print("== L8 版式门控 ==")
    print("repo_root = %s" % root)
    print("graph     = %s" % graph_path)
    print("check     = %s" % args.check)
    print("")

    with open(graph_path, encoding="utf-8") as f:
        graph = json.load(f)
    ctx = Ctx(root, graph)
    print("节点页 = %d | HTML 生成物 = %d | 文档（HTML+MD）= %d | glossary 锚点 = %d"
          % (len(ctx.node_pages), len(ctx.html_files), len(ctx.doc_files),
             len(ctx.glossary_anchors)))
    print("")

    todo = CHECKS if args.check == "all" else [c for c in CHECKS if c[0] == args.check]
    results = []
    for key, title, fn in todo:
        chk = Check(key, title)
        fn(ctx, chk)
        results.append(chk)
        mark = "PASS" if chk.ok else "FAIL"
        print("[%s] %-13s %s（覆盖 %d/%d = %.2f%%，问题 %d）"
              % (mark, key, title, chk.passed, chk.checked, chk.coverage * 100,
                 len(chk.issues)))
        for issue in chk.issues[:args.show]:
            print("    ! %s" % issue)
        if len(chk.issues) > args.show:
            print("    ...（另 %d 条，用 --show 调整）" % (len(chk.issues) - args.show))
        print("")

    total_checked = sum(c.checked for c in results)
    total_passed = sum(c.passed for c in results)
    total_issues = sum(len(c.issues) for c in results)
    overall_cov = (float(total_passed) / total_checked) if total_checked else 1.0
    overall = "PASS" if all(c.ok for c in results) else "FAIL"

    print("== 结果 ==")
    print("  综合覆盖率 = %d/%d = %.2f%%" % (total_passed, total_checked, overall_cov * 100))
    print("  问题总数   = %d" % total_issues)
    print("  L8 综合判定 = %s" % overall)
    sys.exit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
