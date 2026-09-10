#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用生成框架 · 配置层（数据路径 / 输出目录 / 站点标题 / 层与域枚举 / 视图清单）。

设计目标：数据模型与渲染引擎解耦。渲染器只消费本配置与规范化后的图数据，
不硬编码任何绝对路径、目录名、标题或枚举。

两种使用方式：
  1) 作为模块：  from config import load_config; cfg = load_config("mother")
  2) CLI 覆盖：  python3 gen-nodes.py --config mother --repo-root .. --data-dir 10-dag-data

预置 preset：
  - mother   ：母库 10–17 目录布局（默认）
  - 12factor ：12factor 旧库 02–06 布局 + 独立 node-content.json（向后兼容回归用）

字段说明：
  repo_root    输出基目录（也是相对 data_dir 的解析基准），默认 = 本脚本的父目录
  data_dir     DAG 数据目录（相对 repo_root 或绝对路径）
  dag_file     DAG 主文件名
  content_file 独立内容文件名（母库内联 detail 时为 None）
  out_dirs     逻辑角色 -> 输出目录名（相对 repo_root）
  root_index   根入口文件名
  views        视图清单 [{file, kind, title, desc}]
  layers       层枚举（essence/methodology/technology）
  domains      生命周期域枚举 code -> 中文名
  themes       横切主题登记 code -> 中文名
  stages       难度枚举
"""
import argparse
import json
import os

CHECKPOINT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO_ROOT = os.path.dirname(CHECKPOINT_DIR)

# ---------------------------------------------------------------- 母库（默认）
MOTHER = {
    "name": "mother",
    "repo_root": None,                 # None -> DEFAULT_REPO_ROOT
    "data_dir": "10-dag-data",
    "dag_file": "methodology-dag.json",
    "content_file": None,              # 母库 detail 内联于节点
    "title": "软件工程 / 架构设计方法论知识图谱",
    "subtitle": "三层（本质 / 方法论 / 技术实践）× 生命周期域 × 横切主题 × 案例层",
    "out_dirs": {
        "nodes": "11-node-pages",
        "groups": "12-groups",
        "interactive": "13-interactive",
        "views": "14-views",
        "md": "15-md",
        "source": "17-source",
    },
    "root_index": "index.html",
    "layers": ["essence", "methodology", "technology"],
    "layer_labels": {
        "essence": "本质 essence",
        "methodology": "方法论 methodology",
        "technology": "技术实践 technology",
    },
    "domains": {
        "F": "概念与需求", "G": "架构设计", "H": "实现与构造", "I": "测试",
        "J": "部署", "K": "运维", "L": "演化与弃用", "M": "横切·质量属性",
        "N": "横切·团队与康威", "O": "方法论主干/跨域综合", "X": "跨域/其他",
    },
    "themes": {"M": "质量属性", "P": "技术债", "N": "团队与康威", "X": "其他跨域"},
    "stages": ["basic", "intermediate", "advanced"],
    "group_kind_order": ["layer", "domain", "source", "bridge", "crosscut", "case", "tool"],
    "views": [
        {"file": "index.html", "kind": "views-index", "title": "视图入口",
         "desc": "全部视图的导航入口"},
        {"file": "01-layer.html", "kind": "layer", "title": "分层视图",
         "desc": "按本质 / 方法论 / 技术实践三层浏览，含 implements / derives_from 层间边"},
        {"file": "02-learning-path.html", "kind": "learning-path", "title": "学习路径",
         "desc": "按 prerequisite 拓扑与 stage / priority 生成的学习顺序"},
        {"file": "03-decision-matrix.html", "kind": "decision-matrix", "title": "决策矩阵",
         "desc": "生命周期域 × 层 × 横切主题的落点矩阵与权衡要点"},
        {"file": "04-cross-mapping.html", "kind": "cross-mapping", "title": "跨体系对照",
         "desc": "母库 ↔ 12factor 子库的 cross_reference 对照"},
        {"file": "05-cases.html", "kind": "cases", "title": "案例视图",
         "desc": "案例节点及其 case_instance 印证关系"},
        {"file": "glossary.html", "kind": "glossary", "title": "全局术语表",
         "desc": "11 分区术语裁决表；为节点页术语内联提供锚点目标（g-001…）"},
    ],
    "vendor_src": None,
}

# ---------------------------------------------------------------- 12factor 旧库
FACTOR12 = {
    "name": "12factor",
    "repo_root": None,
    "data_dir": None,                  # 由 --data-dir 指定
    "dag_file": "methodology-dag.json",
    "content_file": "node-content.json",
    "title": "12 Factor 方法论合并知识图谱",
    "subtitle": "12 Factor App × 12 Factor Agent — 软件工程方法论统一图谱",
    "out_dirs": {
        "nodes": "02-node-pages",
        "groups": "03-groups",
        "interactive": "04-interactive",
        "views": "05-views",
        "md": "06-md",
        "source": "08-source",
    },
    "root_index": "index.html",
    "layers": [],
    "layer_labels": {},
    "domains": {},
    "themes": {},
    "stages": ["basic", "intermediate", "advanced"],
    "group_kind_order": ["source", "bridge", "crosscut", "tool"],
    "views": [
        {"file": "index.html", "kind": "views-index", "title": "视图入口",
         "desc": "全部视图的导航入口"},
        {"file": "02-stage.html", "kind": "stage", "title": "阶段视图",
         "desc": "按 basic → intermediate → advanced 三档浏览"},
        {"file": "03-learning-path.html", "kind": "learning-path", "title": "学习路径",
         "desc": "传统工程 / Agent 工程 / 打通三条自动生成路径"},
        {"file": "04-cross-mapping.html", "kind": "cross-mapping", "title": "跨体系对照",
         "desc": "App 12 条 ↔ Agent 12 条逐条对照"},
    ],
    "vendor_src": None,
    # 12factor 仓库实测基准（用于回归校验）
    "expected": {
        "nodes": 38, "group_pages": 16, "group_index": 1, "views": 4,
        "interactive": 1, "md_nodes": 38, "md_indexes": 4, "root_index": 1,
    },
}

PRESETS = {"mother": MOTHER, "12factor": FACTOR12}


def _resolve(base, path):
    if not path:
        return None
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base, path))


def load_config(config="mother", repo_root=None, data_dir=None, out_root=None,
                vendor_src=None):
    """合并 preset 与 CLI 覆盖，返回解析后的绝对路径配置 dict。

    config     : preset 名（mother / 12factor）或 JSON 配置文件路径
    repo_root  : 输出基目录（覆盖 preset；None -> DEFAULT_REPO_ROOT）
    data_dir   : DAG 数据目录（相对 repo_root 或绝对）；None -> preset 值
    out_root   : 输出基目录（默认同 repo_root；用于数据与输出分离的场景）
    """
    if isinstance(config, dict):
        preset = dict(config)
    elif os.path.isfile(str(config)):
        with open(config, encoding="utf-8") as f:
            preset = json.load(f)
    else:
        preset = dict(PRESETS.get(str(config), MOTHER))
    preset.setdefault("name", "custom")

    rr = repo_root or preset.get("repo_root") or DEFAULT_REPO_ROOT
    rr = os.path.abspath(rr)
    out_base = os.path.abspath(out_root) if out_root else rr

    dd = data_dir if data_dir is not None else preset.get("data_dir")
    dd = _resolve(rr, dd)
    cfg = dict(preset)
    cfg["repo_root"] = rr
    cfg["out_root"] = out_base
    cfg["data_dir"] = dd
    cfg["dag_path"] = _resolve(dd, preset.get("dag_file", "methodology-dag.json")) if dd else None
    cf = preset.get("content_file")
    cand = _resolve(dd, cf) if (dd and cf) else None
    cfg["content_path"] = cand if (cand and os.path.isfile(cand)) else None
    cfg["checkpoint_dir"] = CHECKPOINT_DIR
    if vendor_src:
        cfg["vendor_src"] = os.path.abspath(vendor_src)
    # 输出目录绝对路径
    cfg["out_paths"] = {k: os.path.join(out_base, v) for k, v in preset.get("out_dirs", {}).items()}
    cfg["root_index_path"] = os.path.join(out_base, preset.get("root_index", "index.html"))
    return cfg


def add_common_args(ap):
    ap.add_argument("--config", default="mother",
                    help="preset 名（mother / 12factor）或 JSON 配置路径")
    ap.add_argument("--repo-root", default=None, help="输出基目录（默认 = 16-checkpoint 的父目录）")
    ap.add_argument("--out-root", default=None, help="输出基目录（与 --repo-root 分离时使用）")
    ap.add_argument("--data-dir", default=None, help="DAG 数据目录（相对 repo-root 或绝对）")
    ap.add_argument("--vendor-src", default=None, help="交互图 vendor JS 来源目录")
    return ap


def config_from_args(args):
    return load_config(config=args.config, repo_root=args.repo_root,
                       data_dir=args.data_dir, out_root=args.out_root,
                       vendor_src=getattr(args, "vendor_src", None))
