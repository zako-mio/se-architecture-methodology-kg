#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成链编排器：按顺序运行全部渲染器，并可选做产出计数回归校验。

用法（母库默认）：
    python3 16-checkpoint/build.py

用法（12factor 回归 / 自定义输出）：
    python3 16-checkpoint/build.py --config 12factor \
        --repo-root /tmp/opencode/pilot-12factor \
        --data-dir /path/to/0823-12factor-methodology/01-dag-data \
        --vendor-src /path/to/0823-12factor-methodology/04-interactive/vendor \
        --verify

每个渲染器均可单独 `python3 gen-*.py --config ... ` 运行。
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import add_common_args, config_from_args  # noqa

STEPS = [
    ("gen-nodes.py", "节点页"),
    ("gen-groups.py", "组页"),
    ("gen-views.py", "视图页"),
    ("gen-glossary.py", "术语表"),
    ("gen-md.py", "Markdown 镜像"),
    ("gen-interactive.py", "交互图"),
    ("gen-index.py", "根入口"),
]


def run_step(script, cfg_args, quiet=False):
    cmd = [sys.executable, os.path.join(HERE, script)] + cfg_args
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        sys.stderr.write("[FAIL] %s\n%s\n%s\n" % (script, proc.stdout, proc.stderr))
        raise SystemExit(1)
    if not quiet and proc.stdout.strip():
        print(proc.stdout.strip())


def count_tree(path, exts=None):
    n = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            if exts is None or os.path.splitext(f)[1].lower() in exts:
                n += 1
    return n


def collect_counts(cfg):
    od = cfg["out_paths"]
    res = {}
    res["nodes"] = count_tree(od["nodes"], {".html"}) if os.path.isdir(od["nodes"]) else 0
    gp = count_tree(od["groups"], {".html"}) if os.path.isdir(od["groups"]) else 0
    gindex = 1 if os.path.isfile(os.path.join(od["groups"], "index.html")) else 0
    res["group_pages"] = gp - gindex
    res["group_index"] = gindex
    res["views"] = count_tree(od["views"], {".html"}) if os.path.isdir(od["views"]) else 0
    res["interactive"] = 1 if os.path.isfile(os.path.join(od["interactive"], "index.html")) else 0
    md_nodes_dir = os.path.join(od["md"], "nodes")
    res["md_nodes"] = count_tree(md_nodes_dir, {".md"}) if os.path.isdir(md_nodes_dir) else 0
    res["md_indexes"] = count_tree(od["md"], {".md"}) - res["md_nodes"] if os.path.isdir(od["md"]) else 0
    res["root_index"] = 1 if os.path.isfile(cfg["root_index_path"]) else 0
    return res


def verify(cfg, counts):
    expected = cfg.get("expected")
    if not expected:
        print("[verify] preset 未声明 expected，跳过回归比对")
        return True
    print("\n[verify] 产出计数 vs 12factor 仓库基准")
    ok = True
    for k in sorted(expected):
        got, want = counts.get(k, 0), expected[k]
        mark = "OK " if got == want else "MISMATCH"
        if got != want:
            ok = False
        print("  %-14s 实测=%-4d 基准=%-4d  %s" % (k, got, want, mark))
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成链编排器")
    add_common_args(ap)
    ap.add_argument("--verify", action="store_true", help="与 preset.expected 比对产出计数")
    ap.add_argument("--quiet", action="store_true", help="不打印各步骤 stdout")
    args = ap.parse_args(argv)
    cfg = config_from_args(args)

    # 将公共参数透传给子脚本（保持路径解析一致）
    cfg_args = ["--config", args.config]
    if args.repo_root:
        cfg_args += ["--repo-root", args.repo_root]
    if args.out_root:
        cfg_args += ["--out-root", args.out_root]
    if args.data_dir:
        cfg_args += ["--data-dir", args.data_dir]
    if args.vendor_src:
        cfg_args += ["--vendor-src", args.vendor_src]

    print("生成目标: repo_root=%s\ndata_dir=%s" % (cfg["repo_root"], cfg["data_dir"]))
    for script, label in STEPS:
        print("== %s (%s) ==" % (script, label))
        run_step(script, cfg_args, quiet=args.quiet)

    counts = collect_counts(cfg)
    print("\n[summary] 产出计数: %s" % counts)
    if args.verify:
        if verify(cfg, counts):
            print("[verify] PASS")
        else:
            print("[verify] FAIL")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
