# 软件工程 / 架构设计方法论知识图谱

> 一个可人读、可机读、可演进的软件工程与架构设计方法论母库。
> 三层知识（本质 / 方法论 / 技术实践）× 11 个生命周期域 × 3 个横切主题 × 18 个真实工程案例。

本仓库是母库的公开交付集：既供人按图谱顺序学习架构判断力，也为 AI Agent 提供结构化的
架构知识底座（Markdown 镜像 + 单一 JSON 主图，可被检索层或 Agent 直接消费）。

> **在线站点**：https://zako-mio.github.io/se-architecture-methodology-kg/
> **仓库地址**：https://github.com/zako-mio/se-architecture-methodology-kg
> **CI**：GitHub Actions `rebuild` —— 重建（幂等）→ 漂移检测（`git diff --exit-code`）→ L2 / L3 / L6 / L7 / L8 + 方法论门控 → Pages 部署；
> 最近两次运行均 **success**（run `34510503610` / `34510696621`）。**L4 / L5 在 CI 中显式 SKIPPED**（需本地补跑，见下文「CI 中的门控」）。

## English Abstract

This repository is a public knowledge graph of software engineering and architecture
methodology. It organizes **167 nodes and 360 typed edges** into three layers—essence,
methodology, and technology practice—crossing **11 lifecycle domains** (requirements,
architecture, implementation, testing, deployment, operations, evolution, quality
attributes, team & Conway, methodology backbone, cross-domain cases) plus three
cross-cutting themes (quality attributes, technical debt, team & Conway). Eighteen
real-world engineering case studies are attached as a `layer=null` case layer.
Every node page follows a uniform `§1–§11` block sequence and is traceable to
**253 canonical sources** (100% traceable, 89.22% explicitly verified). The whole
site is statically generated from a single JSON graph by a standard-library-only
Python build chain, with an eight-layer gate suite guarding structure, coverage,
sourcing, and layout. Licensed under MIT.

## 一、项目定位与两用目标

- **人读图谱**：以「理解业务需求 → 可维护可扩展的架构设计 → 落地运维 → 持续对抗技术债」
  的完整生命周期为骨架，把跨书籍、标准与真实项目的知识重新消化、组织成一张可导航的图谱；
  读者可从总览出发，沿学习路径或域/层导航逐层下钻到节点页。
- **为 Agent 加持架构判断力**：同一份知识同时以机器友好的形态发布——单一权威图
  `10-dag-data/methodology-dag.json`、逐节点 `15-md/` Markdown 镜像、带类型与方向的边、
  逐条信源锚定，便于检索层、RAG 或 Agent 工作流直接引用。

核心理念：**知识库自身也要体现良好的架构设计**——数据与渲染解耦、单一数据源、可重复生成、
门控可追溯。

## 二、知识组织模型

```
            本质层 essence (51)  ──derives_from──▶  方法论层 methodology (67)  ──implements──▶  技术实践层 technology (31)
                 ▲                                                                                    │
                 └───────────────────────── case_instance (案例印证/违背) ◀──────────────────────────┘
                                    案例层 case (18, layer=null)
```

- **三层（layer）**
  - `essence` 本质：原理、概念与需求（"为什么"）—— 51 节点；
  - `methodology` 方法论：可复用的方法、模式与判据（"怎么做的方法"）—— 67 节点；
  - `technology` 技术实践：具体技术、工具与落地工程（"用什么"）—— 31 节点；
  - `case` 案例层：`layer=null`，18 个真实工程分析，经 `case_instance` 边印证或违背上层节点。
- **11 个生命周期域（domain）**：F 概念与需求(13)、G 架构设计(17)、H 实现与构造(16)、
  I 测试(14)、J 部署(17)、K 运维(17)、L 演化与弃用(14)、M 横切·质量属性(14)、
  N 横切·团队与康威(13)、O 方法论主干/跨域综合(14)、X 跨域/案例(18)。
- **3 个横切主题（cross_cutting）**：M 质量属性(96)、P 技术债(31)、N 团队与康威(29)；
  以节点属性表达，不建跨层边。
- **18 个分组（groups）**：层分组 3（`GL-ESSENCE` / `GL-METHOD` / `GL-TECHNOLOGY`）、
  域分组 11（`GD-F` … `GD-X`）、跨切/案例分组 4（`GCC-M` / `GCC-P` / `GCC-N` / `GC-CASE`）。

## 三、数据规模（实测）

> 数据源：`10-dag-data/stats.md` 与 `10-dag-data/methodology-dag.json`（由
> `16-checkpoint/aggregate.py` 聚合），下列数字为仓库内实测值。

| 维度 | 数值 |
|---|---:|
| 节点 nodes | **167** |
| 边 edges | **360** |
| 分组 groups | **18**（+组总索引共 19 页） |
| 案例 cases | **18** |
| 横切主题 themes | 3 |
| layer=essence | **51** |
| layer=methodology | **67** |
| layer=technology | **31** |
| layer=null（案例层） | **18** |
| canonical 信源 | **253** |
| `verified=true` | **149 / 167 = 89.22%** |
| 可溯源率（sources 非空且可解析） | **167 / 167 = 100%** |
| 悬挂信源引用 | **0** |

**边类型分布**：`case_instance` 69 · `derives_from` 69 · `implements` 59 · `prerequisite` 58 ·
`combination` 36 · `dependency` 24 · `contrasts` 14 · `enables` 13 · `refines` 13 ·
`conflicts` 4 · `cross_reference` 1。硬依赖边集合
`{prerequisite, dependency, derives_from, refines}` 共 164 条，经 Kahn 拓扑排序验证为**无环 DAG**
（167/167 节点入队）。

## 四、目录结构

```
.
├── index.html                  # 根入口：全站导航（人读起点）
├── 00-plan/                    # 阶段 1–5 设计文档：契约、数据模型、IA 规范、ID 迁移、基线
├── 01-books/                   # 书单与获取日志（仅元数据，不含书籍正文）
├── 02-research/                # 已脱敏的研究证据包（A–R，JSON + Markdown）
├── 03-knowledge-map/           # canonical 信源主表、术语表、来源索引、主题-来源矩阵
├── 10-dag-data/                # 单一权威图数据（methodology-dag.json + 可重聚合分片 + stats）
├── 11-node-pages/              # 167 个节点详情页（HTML，统一 §1–§11 块序列）
├── 12-groups/                  # 18 个组页 + 组总索引（index.html）
├── 13-interactive/             # 交互式 DAG 总览（cytoscape + dagre，含本地 vendor）
├── 14-views/                   # 多视图：分层 / 学习路径 / 决策矩阵 / 跨体系对照 / 案例 / 术语表
├── 15-md/                      # Markdown 镜像（167 节点 + 索引），面向 AI 消费
├── 16-checkpoint/              # 生成链与门控脚本（Python 标准库，唯一构建入口）
├── 20-agent-skill/             # Agent 能力包（轻量速查 + 路径路由），本机可安装为 skill
├── report.md / report.html     # 阶段 1–6 全周期报告（双版本 / 五段式）
├── quality-gate.md             # 阶段 1–6 门控明细（L1–L8 + 方法论专项 + 回放四硬指标）
├── README.md / LICENSE         # 本文件 / MIT 许可
├── .nojekyll                   # 禁用 Jekyll 处理（保留以 `_` 开头等路径）
└── .github/workflows/rebuild.yml  # CI：重建 + 门控 + 漂移检测 + GitHub Pages 部署
```

> `16-checkpoint/` 中的 `merge_pilot.py` 与 `validate_pilot_merge.py` 为已失效的历史试点脚本，
> 公开集已剔除；`__pycache__/` 与 `_render-shots/`（门控渲染中间产物）同样不发布。

## 五、使用方式

### 人读入口

1. `index.html` —— 根入口，全站导航起点；
2. `13-interactive/index.html` —— 交互式 DAG 总览，可按组展开/下钻；
3. `12-groups/index.html` → `12-groups/<group>.html` —— 组页，按层 / 域 / 横切浏览；
4. `11-node-pages/<ID>.html` —— 节点详情页，统一 `§1–§11` 块序列：
   `§1 摘要与结论`、`§2 局部关系图`、`§3 原理·为什么`、`§4 机制·如何运作`、
   `§5 工程·怎么落地`、`§6 权衡卡`、`§7 学习路径条`、`§8 冲突/对比表`、
   `§9 案例带`、`§10 信源与核验`、`§11 原始关系清单`；
5. `14-views/` —— 分层视图、学习路径、决策矩阵、跨体系对照、案例视图、全局术语表。

### AI 入口

- `15-md/` —— 全量 Markdown 镜像（`15-md/nodes/*.md` 逐节点 + `00-index.md` 等索引），
  适合直接注入上下文或建检索索引；
- `10-dag-data/methodology-dag.json` —— 单一权威图（节点 + 带类型/方向的边 + 内联内容 + 信源），
  所有 HTML/MD 均由此生成。

### Agent 能力包入口（`20-agent-skill/`）

面向「让 Agent 具备架构判断力」的轻量能力包，形态为**轻量速查 + 路径路由**（不内联大段内容、不依赖联网）：

| 文件 | 用途 |
|---|---|
| `SKILL.md` | 能力包入口：定位、触发场景与关键词、使用流程、跨库深链模板 |
| `cheatsheet.md` | 三层各 8–12 条最关键判断准则（每条附支撑节点 id） |
| `routing.md` | 路径路由表：18 个高频任务场景 → 应读节点 / 组 / 视图 / 学习路径 |
| `decision-matrix.md` | 决策矩阵摘要：域×层矩阵、横切主题覆盖、默认取舍启发式、案例索引 |
| `node-index.md` | 167 节点 id ↔ 名称 ↔ 层 ↔ 域 一句话索引（供按 id 深链） |

本机安装（opencode skills 目录约定）：

```bash
mkdir -p ~/.config/opencode/skills/architecture-judgment
cp 20-agent-skill/*.md ~/.config/opencode/skills/architecture-judgment/
```

安装后 `name: architecture-judgment` 的 skill 会在涉及架构决策、技术选型、架构评审、
需求工程、演进与技术债治理、质量属性权衡等任务时被加载。

## 六、门控结果（实测）

门控全部由 `16-checkpoint/*.py` 执行；**`skipped ≠ PASS`**。下表为发布时实测值。

| 层 | 检查项 | 命令 | 实测值 | 结论 |
|---|---|---|---|---|
| **L1** 分片自验证 | JSON/schema/枚举/信源/边/无环 | `validate_graph.py --shard <分片>` | 23 个分片 `errors=0` | **PASS** |
| **L2** 全图审计 | 字段/ID/计数一致/无环 | `validate_graph.py --graph ...` | `nodes=167 edges=360 kahn=167/167 errors=0 warnings=0` | **PASS** |
| **L3** 结构 + 断链 | UTF-8/空文件/空正文/内部断链 | `kb_gate.py --root . --layers structure,links` | structure **401 项 0 问题**；links **5134 项 0 问题** | **PASS** |
| **L4** 视觉 | 位图渲染无截断、中文完整（像素计数 + VLM） | `gate_visual.py --check all` | **262 项检查 0 FAIL / 15 WARN** | **PASS**（详见下） |
| **L5** 渲染 | headless Chromium 实渲染 canvas 计数/JS 错误/边端点 | `gate_render.py` | 7 用例全 PASS；`skipped=0`；JS 错误 0；悬空端点 0 | **PASS** |
| **L6** 覆盖度 | manifest + 四向覆盖 + GR-08 + GR-09 | `gate_coverage.py` | manifest **362/362=100%**；四向 **100%**；GR-08 PASS；GR-09 **11/31=35.48%** | **PASS** |
| **L7** 信源 | canonical 解析/可溯源率/`verified`/disputed | `gate_sources.py` | 悬挂 **0**；可溯源 **100%**；`verified=true` **89.22%**；disputed 漏标 **0** | **PASS** |
| **L8** 版式 | 关系图/摘要卡/权衡卡/TOC/术语/自包含/编码/深链/双轨 | `gate_layout.py --check all` | 综合覆盖率 **2124/2124 = 100.00%**，问题 **0** | **PASS** |
| **方法论专项** | 层边界 / 术语一致 / 原则↔反例 / 11 维权衡 | `gate_methodology.py --check all` | 4 项全 PASS（含 O-PC **36/36**、O-TD **11/11**） | **PASS（4/4）** |

> **L4 说明**：本审计轮次首次实装视觉门控（像素计数 + VLM 交叉），结果为 **262 项检查
> 0 FAIL / 15 WARN**；15 条 WARN 为可接受的非阻断项（14 条为启发式「同行墨迹近邻」探针，误报率高，
> 仅告警不阻断；1 条为术语表超宽表格在 `overflow-x:auto` 容器内滚动，属设计允许行为）。
> `report.md` / `report.html` / `quality-gate.md` 已按同一口径更新为**阶段 1–6 全周期**版本，数字一致。
> **L5 说明**：交互图正确性由真实浏览器实渲染覆盖（7 用例含默认组级 + 6 个下钻组）。

### CI 中的门控（重要：L4 / L5 显式 SKIPPED）

GitHub Actions 的标准 runner **不预装** `Pillow` / `numpy` / `agent-browser`（headless Chromium），
因此 **L4 视觉门控与 L5 渲染门控在 CI 中显式 SKIPPED**，CI 日志会打印明确的跳过原因，
**绝不伪装成 PASS**。请在本地补跑：

```bash
python3 16-checkpoint/gate_visual.py --check all   # L4，需 Pillow + numpy + agent-browser
python3 16-checkpoint/gate_render.py               # L5，需 agent-browser（headless Chromium）
```

## 七、重建方式

生成链**仅依赖 Python 标准库**（无第三方包），且**完全幂等**（同数据重跑产出零差异，
故 CI 可用 `git diff --exit-code` 做漂移检测）。

```bash
# 1) 重建全部产物（节点页 / 组页 / 视图 / MD / 交互图 / 根入口）
cd 16-checkpoint && python3 build.py --config mother --quiet && cd ..

# 2) 重新聚合主图（由 10-dag-data/_parts/*.json + _base.json 合并）
python3 16-checkpoint/aggregate.py

# 3) 门控命令清单（CI 可跑）
python3 16-checkpoint/validate_graph.py --graph 10-dag-data/methodology-dag.json \
  --canonical 03-knowledge-map/canonical-sources.json
python3 16-checkpoint/kb_gate.py --root . --layers structure,links \
  --exclude 02-research --exclude 01-books --exclude 03-knowledge-map \
  --exclude 00-plan --exclude 16-checkpoint --exclude .github --quiet
python3 16-checkpoint/gate_layout.py --check all
python3 16-checkpoint/gate_coverage.py
python3 16-checkpoint/gate_sources.py
python3 16-checkpoint/gate_methodology.py --check all
```

## 八、CI：自动重建与 GitHub Pages

`.github/workflows/rebuild.yml` 在 `push`（`main` 分支，且改动命中 `10-dag-data/**`、
`16-checkpoint/**` 或工作流自身）与手动 `workflow_dispatch` 时触发：

1. `actions/checkout@v4` → `actions/setup-python@v5`（Python 3.12）；
2. 执行重建，并运行 L2 / L3 / L6 / L7 / L8 与方法论专项门控；
3. 运行 `git diff --exit-code` 做**漂移检测**（重建幂等，任何差异即失败）；
4. L4 / L5 打印显式 SKIP 原因（环境依赖缺失）；
5. `actions/configure-pages@v5` → `actions/upload-pages-artifact@v3`（`path: .`）；
6. `jobs.deploy` 经 `actions/deploy-pages@v4` 发布到 `github-pages` 环境。

## 九、姊妹仓库

- **`zako-mio/12-factor-methodology-kg`** —— 12 Factor App × 12 Factor Agent 方法论图谱
  （38 节点 / 61 边 / 16 组）。这是一个**独立演进**的**旧代设计**子库，采用与母库不同的目录布局
  （02–06）与数据模型；母库中有 29 个节点页通过 `cross_reference` 关系以**绝对 URL 深链**过去：

  `https://zako-mio.github.io/12-factor-methodology-kg/02-node-pages/<node-id>.html`

  两个仓库各自维护，母库仅在「跨体系对照」视图中引用子库，不反向耦合其构建链。

## 十、内容与版权声明

- 本仓库是**消化重组后的自研知识**：节点正文为对公开资料的归纳、重写与交叉核验，
  **不含任何书籍或标准的正文**。
- **短引用**（≤200 字）保留并逐条标注出处（`source_id` / URL）；**长引用已全部移出**，
  以占位符替换并保留原出处键。
- 第三方事实信息（标准编号、书名、权威链接等）仅保留**元数据与 URL**，不复制其受版权保护的表述。
- `01-books/` **仅含书单与获取日志**（候选书目、获取状态、缺口请求），不含书籍正文或摘录正文。
- `02-research/` 为已脱敏的研究证据包；本机绝对路径、疑似凭据、超阈值长引用均已清除（见下节）。

## 十一、发布期脱敏补充

审计在装配后对 `_publish/` 全体（含 `16-checkpoint/*.py` 与文档）做了全量残差复扫。除
`_publish-staging/` 既有脱敏外，装配阶段另发现并改写了以下残留（**仅改公开集副本，
未触碰原始母库**）：

| 文件 | 残留类型 | 处理 |
|---|---|---|
| `10-dag-data/methodology-dag.json` | 本机绝对路径 ×9（`entry_links`） | `/home/<user>` → `~` |
| `10-dag-data/_parts/W2-CASE-B.json` | 本机绝对路径 ×9（`entry_links`） | `/home/<user>` → `~` |
| `10-dag-data/_batch-plan.json` | 本机绝对路径 ×1（`inputs`） | `/home/<user>` → `~` |
| `16-checkpoint/audit_publish.py` | 工具自身文档串含本机路径与凭据样式前缀 | 文档改为通用表述；凭据正则前缀改为拼接构造、home 正则改用 `$USER`（功能等价） |

复扫结果（全部必须为 0，实测**均为 0**）：

| 复扫项 | 命令 | 结果 |
|---|---|---|
| 本机路径 | `grep -rIl '/home/<user>' _publish \| wc -l` | **0** |
| U+FFFD 替换字符 | `grep -rIl $'\uFFFD' _publish \| wc -l` | **0** |
| 疑似凭据 | `grep -rIoh -E 'gh[op]_|sk-[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY' _publish \| wc -l` | **0** |
| 生成物陈旧月份 | `grep -rl '2026-08' 11-node-pages 12-groups 14-views 15-md index.html \| wc -l` | **0** |
| 生成物内联脚本 | `grep -rl '<script' 11-node-pages 12-groups 14-views index.html \| wc -l` | **0** |

## 十二、许可

本项目以 **MIT License** 发布，详见 [`LICENSE`](./LICENSE)。Copyright (c) 2026 zako-mio。
