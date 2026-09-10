# 16-checkpoint · 通用知识图谱生成框架

本目录是母库 `0910-软件工程架构方法论` 的**可重复生成底座**：把 12factor 生成链重构为
「数据模型 / 渲染引擎」解耦的通用框架，并附门控脚本与回归基准。

- 渲染器只消费 `config` + 规范化图数据，**不硬编码**任何绝对路径、目录名、标题或枚举。
- 同一套脚本可生成母库（10–17 布局）与 12factor 旧库（02–06 布局），且对旧数据**优雅降级**。
- 数据源唯一：`{data_dir}/methodology-dag.json`（母库 `detail` 内联；12factor 另有 `node-content.json`）。

## 一、目录与角色

| 文件 | 角色 |
|---|---|
| `config.py` | 配置层：preset（`mother` / `12factor`）、路径解析、层/域/主题枚举、视图清单 |
| `gen_common.py` | 公共层：数据加载 → schema 规范化、拓扑、样式徽章、共享 CSS |
| `gen-nodes.py` | 节点详情页 `{out_nodes}/{id}.html` |
| `gen-groups.py` | 组页 `{out_groups}/{id}.html` + 组总索引 `index.html` |
| `gen-views.py` | 多视图 `{out_views}/{file}`（按 `views` 清单分派） |
| `gen-md.py` | Markdown 镜像 `{out_md}/nodes/*.md` + 索引文件 |
| `gen-interactive.py` | 交互 DAG `{out_interactive}/index.html`（cytoscape + dagre） |
| `gen-index.py` | 根入口 `{root_index}` |
| `build.py` | 编排器：顺序运行全部渲染器，`--verify` 做产出计数回归 |
| `kb_gate.py` | 分层门控（structure / links / nav / cascade / coverage / sources / render） |
| `config.py` 的 `expected` | 12factor 产出计数基准（回归校验） |

> 既有 `migrate_ids.py` / `build_mapping.py` / `gate_migration.py` 属信源 ID 迁移工具，与本框架独立，未改动。

## 二、快速开始

### 母库（默认，10–17 布局）

```bash
# 前置：10-dag-data/methodology-dag.json 已聚合
python3 16-checkpoint/build.py
# 产物：11-node-pages / 12-groups / 13-interactive / 14-views / 15-md / index.html
```

单步运行（任选）：

```bash
python3 16-checkpoint/gen-nodes.py
python3 16-checkpoint/gen-views.py --data-dir 10-dag-data
```

### 12factor 回归（输出到临时目录，不动原仓库）

```bash
python3 16-checkpoint/build.py --config 12factor \
  --repo-root /tmp/opencode/pilot-12factor \
  --data-dir <12factor 仓库>/01-dag-data \
  --vendor-src <12factor 仓库>/04-interactive/vendor \
  --verify
```

## 三、配置（`config.py`）

每个 preset 是一个 dict，字段：

| 字段 | 说明 |
|---|---|
| `repo_root` | 输出基目录（也是相对路径解析基准），默认 = 本目录父级 |
| `data_dir` / `dag_file` / `content_file` | 数据目录、主图文件名、独立内容文件名（母库为 `None`） |
| `out_dirs` | 逻辑角色 → 目录名（`nodes/groups/interactive/views/md/source`） |
| `root_index` | 根入口文件名 |
| `views` | 视图清单 `[{file, kind, title, desc}]`，`build` 只生成清单内文件 |
| `layers` / `layer_labels` | 层枚举与标签（母库三层；12factor 为空 → 分层视图降级） |
| `domains` / `themes` | 生命周期域 / 横切主题登记表 |
| `group_kind_order` | 组类别展示顺序 |

新增一个知识库：复制一个 preset，改 `out_dirs`/`title`/`views` 即可，无需改渲染器。

### CLI 覆盖

```bash
--config mother|12factor|<json 路径>
--repo-root <输出基目录>
--out-root  <输出基目录（与 repo-root 分离时）>
--data-dir  <DAG 数据目录，相对 repo-root 或绝对>
--vendor-src <交互图 vendor JS 来源目录>
```

## 四、视图（`gen-views.py`）

| kind | 依赖 | 说明 |
|---|---|---|
| `views-index` | — | 视图入口卡片 |
| `stage` | `stage` | 难度阶段视图（12factor） |
| `layer` | `layer` | 三层视图 + `implements`/`derives_from` 层间边 |
| `learning-path` | `prerequisite` | 拓扑学习路径（有 `src=app/agent` 时输出 A/B/C 三条） |
| `decision-matrix` | `domain` + `layer`/`themes` | 域 × 层落点矩阵 + 横切主题覆盖 |
| `cross-mapping` | `cross_reference` 边（或 `src=app/agent`） | 跨体系对照 |
| `cases` | `type=case` 节点 | 案例视图 + `case_instance` 印证关系 |

**降级规则**：数据缺字段时对应视图输出空状态页（不报错）；数据缺 `layer` 时 `layer` 视图
不产出真实内容，12factor preset 的 `views` 清单也**不含**这些视图，故回归计数不受影响。

## 五、向后兼容（12factor ↔ 母库）

`gen_common.Graph` 对每个节点补默认值并合并内容模型：

- 内容模型统一：12factor `what/why/how/cases/anti_patterns/app_side/agent_side/difference/source_refs`
  与母库 `definition + detail.{principle,mechanism,engineering,tradeoff}` 均归一为 `sections(node)`。
- 母库扩展字段 `layer/domain/cross_cutting/case/sources/verified/confidence/review_date/status/errata/entry_links`
  在 12factor 数据缺失时填默认值（`None` / `[]`），相关徽章与区块自动省略。
- 节点 ID、组 ID 原样使用，不重写（12factor 的 `app-codebase` 与母库 `ESS-H-01` 并存）。

## 六、门控（`kb_gate.py`）

```bash
# 结构与断链（12factor 回归实测：structure 0 问题、links 0 问题）
python3 16-checkpoint/kb_gate.py --root <输出目录> --layers structure,links

# 全层（按需；环境缺失的层会显式标 skipped）
python3 16-checkpoint/kb_gate.py --root <输出目录> \
  --layers structure,links,nav,cascade,coverage,sources,render
```

> `nav` 层要求全站统一导航目录；本框架各页使用**上下文导航**（navseq），故 nav 层为
> 已知非适用项（12factor 原仓库亦 55 处同类问题）。请用 `--layers structure,links` 作为
> 生成链回归门控；母库若需 nav 层，须先定义统一 nav 数据源并经 `--nav-source` 提供。

## 七、回归基准（2026-09-10 实测）

以 12factor `methodology-dag.json`（38 节点 / 61 边 / 16 组）+ `node-content.json`
生成到 `/tmp/opencode/pilot-12factor/`，文件名集合与原仓库逐目录一致：

| 产物 | 实测 | 12factor 基准 |
|---|:--:|:--:|
| 节点页 HTML | 38 | 38 |
| 组页（不含索引） | 16 | 16 |
| 组索引 | 1 | 1 |
| 视图页 | 4 | 4 |
| 交互图 index.html | 1 | 1 |
| MD 节点镜像 | 38 | 38 |
| MD 索引 | 4 | 4 |
| 根入口 index.html | 1 | 1 |

`build.py --verify` 输出全部 `OK` → PASS。回归后临时目录已清理，未写入 12factor 原仓库。

## 八、约束与纪律

- 脚本均可 `python3 <script>` 直接运行；仅依赖标准库。
- UTF-8 安全：门控 structure 层扫描全部文本，确认无 U+FFFD 替换字符。
- 不硬编码绝对路径：路径一律来自 config preset 或 CLI 参数。
- 数据驱动：改数据即改图谱，禁止在渲染器中硬编码节点/组/边或计数。
