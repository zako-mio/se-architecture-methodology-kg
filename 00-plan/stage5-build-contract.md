# 阶段5 · 建库 P0 契约（可直接派单）

> 母任务：0910-软件工程架构方法论 · 阶段5 建库
> 本文件：阶段5 所有波次、所有子Agent 的**共享生产契约**。子Agent **只读本文件**，禁止复制全文进 prompt，只引用短路径。
> 上游依据（全部已落盘，字段/枚举/规则以它们为唯一真相）：
> - `00-plan/stage4-architecture-design.md`（§三 层边界 / §四 粒度 / §五 数据模型 / §六 视图 / §七 12factor 纳入 / §八 ID / §十 执行方式 / §十一 阶段5 计划与门控 / §十二 风险）
> - `00-plan/stage4-data-model.md`（字段级 schema v1.1，**本文件不另立命名**）
> - `00-plan/id-migration-plan.md`（信源 ID 命名空间与迁移，**节点 ID 不涉**）
> - `00-plan/dag-schema.example.json`（合法样例）
> - `00-plan/contract.md`（阶段1 契约：命名/信源分级/版权红线）
> - `03-knowledge-map/{sources-index,topic-source-matrix,glossary}.md`
> 生成日期：2026-09-10　复杂度继承：`[COMPLEXITY: 19/20] → Deep`
> **效力声明**：本契约与 `stage4-*` 设计**不冲突**；若有出入，以 `stage4-architecture-design.md` + `stage4-data-model.md` 为准，本文件负责把它们翻译为可派单任务。本文件之外的取值、字段、正则一律不新增。

---

## 〇、本契约解决什么（先读）

阶段4 已定"三层（本质/方法论/技术实践）× 生命周期域 × 横切主题 × 案例层"的非对称矩阵与数据模型；阶段5 要把 14 个证据包（阶段1 A–E + 阶段2 F–R）与 12factor 既有库，翻译成**可人读、可机读、可演进**的母库。本契约固定四件事，供全部波次共享：

1. **往哪写**——目录布局与分片命名（§一）；
2. **写什么**——节点/边生产契约（§二、§三）；
3. **谁在何时写**——批次计划（§四）与落盘纪律（§五）；
4. **怎么算合格**——门控清单（§六）与版权红线（§七）。

主Agent 只做**编排 / 聚合 / 裁决 / 门控**，内容生产全委派子Agent；子Agent 为纯执行者，先落盘再返回。

---

## 〇.1 实现现状（2026-09-10 实测，以此为准）

> 本节为对 §一 / §二 / §四 / §五 / §六 中 `shards/`、`04-migration/` 表述的**权威修正**；两者不一致时，以本节实测为准。

1. **分片目录 = `10-dag-data/_parts/`**：每批**单文件** `_parts/{batch_id}.json`，结构 `{"nodes": [...], "edges": [...]}`（可选头字段 `batch_id`/`wave`/`domain`/`layers`/`produced_by`/`generated`）。**非** `shards/` 目录，**非** `.nodes.json` + `.edges.json` 双文件形态。
2. **canonical 信源主表 = `03-knowledge-map/canonical-sources.json`**（253 个实体）。**非** `04-migration/` 内文件；`04-migration/` 目录**未创建**，其中的 canonical-sources.json 仅为阶段4 设计预留路径，实际产物落 `03-knowledge-map/`。
3. **脚本与骨架落点**：聚合 `16-checkpoint/aggregate.py`、校验 `16-checkpoint/validate_graph.py`、骨架抽取 `16-checkpoint/_base_extract.py`；骨架数据 `10-dag-data/_base.json`；批次跟踪 `10-dag-data/_batch-plan.json`。

---

## 一、仓库与目录布局

### 1.1 母库 repo root

```
MISSION_ROOT = ~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论
```

### 1.2 目录约定

```
0910-软件工程架构方法论/                 # 母库 repo root
├── 00-plan/                            # 【既有·不动】契约、阶段设计、ID 方案
├── 01-books/                           # 【既有·不动】书单与可得性、本地语料层索引
├── 02-research/                        # 【既有·不动】14 个证据包（A–E + F–R）
├── 03-knowledge-map/                   # 【既有·不动】知识地图、信源索引、术语表
│
├── 04-migration/                       # 【阶段4 设计预留 · 实际未创建】信源 ID 统一（canonical-sources.json + old2new.json + 门控/回执）
│                                       #   设计预留；实际未创建，产物落 03-knowledge-map/canonical-sources.json
├── 05–09/                              # 【预留】阶段5 中间工作区（如未来 D2 检索层），当前为空
│
├── 10-dag-data/                        # 【新建】DAG 数据（分片 + 聚合图）
├── 11-node-pages/                      # 【新建】节点详情页（HTML，人读主入口）
├── 12-groups/                          # 【新建】组页 + 组总索引
├── 13-interactive/                     # 【新建】交互 DAG 总览（cytoscape + vendor/）
├── 14-views/                           # 【新建】多视图（分层/学习路径/决策矩阵/跨体系/案例）
├── 15-md/                              # 【新建】AI 友好 Markdown 镜像
├── 16-checkpoint/                      # 【新建】生成脚本 + 门控脚本（可重复构建）
├── 17-source/                          # 【新建】公开入口链接清单 + 本地语料层索引（**不含书正文**）
│
├── index.html                          # 【新建】根入口
├── report.md / report.html             # 【新建】阶段5 报告双版本
└── quality-gate.md                     # 【新建】门控报告
```

### 1.3 为什么用 10–17（而非 01–08）

1. **零断链**：`00-plan`、`01-books`、`02-research`、`03-knowledge-map` 是既有研究与设计产物，已被 `report.*`、`knowledge-map.*`、`sources-index.md`、`01-alignment.md` 大量内部引用。**移动或重编号它们会产生全量断链**，且与阶段1 契约 `contract.md §1` 的路径约定冲突。保持原位是零风险选择。
2. **天然分层**：`00–03` = 研究设计区（只读输入），`10–17` = 建库交付物区（可重生成输出）。编号段本身表达"输入/输出"边界。
3. **认知迁移成本最低**：`10–17` 与 12factor 既有库 `01–08` **逐位对应（整体 +9）**，可直接复用其 `07-checkpoint/gen_common.py` + 5 个生成器与门控脚本，改路径常量即可。
4. **预留中间区**：`04–09` 空出给阶段5 前置/中间工作区（`04-migration` 为阶段4 已**设计预留**；实际未创建，产物落 `03-knowledge-map/`），不与最终交付物混淆。

### 1.4 与 12factor 01–08 的对应关系（复用工程底座）

| 12factor `0823-12factor-methodology/` | 母库 `0910-软件工程架构方法论/` | 内容 | 复用方式 |
|---|---|---|---|
| `01-dag-data/` | `10-dag-data/` | 核心 DAG 数据（nodes/edges/groups） | 复用 schema，扩展 layer/domain/case |
| `02-node-pages/` | `11-node-pages/` | 节点详情页 HTML | 复用 `gen-nodes.py`（适配五段式+反例块） |
| `03-groups/` | `12-groups/` | 组页 + 组总索引 | 复用 `gen-groups.py` |
| `04-interactive/` | `13-interactive/` | 交互 DAG（cytoscape+dagre vendor） | 复用 `gen-interactive.py`（双 DATA 注入） |
| `05-views/` | `14-views/` | 人类入口视图 | 复用 `gen-views.py`（扩到 6 类视图） |
| `06-md/` | `15-md/` | AI 友好 MD 镜像 | 复用 `gen-md.py` |
| `07-checkpoint/` | `16-checkpoint/` | 生成脚本 + 门控脚本 | 复用 `gen_common.py`，**新增门控脚本**（§六） |
| `08-source/` | `17-source/` | 信源资产 | 母库**只放官方入口链接 + 本地语料索引**，不放书正文（§七） |

> 生成链重构为"数据模型 / 渲染引擎"解耦的通用框架（stage4 §十），是 Wave 0 前置项；38 节点回归试点必须通过后方可进入 Wave 1。

### 1.5 `10-dag-data/` 内部结构（分片纪律的物理基础）

```
10-dag-data/
├── _batch-plan.json          # 【主Agent 维护】批次跟踪（schema 见 §4.6）
├── _base.json                # 【Wave 0 骨架】初始 11 节点 / 12 边
├── _parts/                   # 【子Agent 只写这里】按批次唯一命名，每批单文件
│   ├── pilot-essence.json    #   每批次恰好一个文件，结构 {nodes:[...], edges:[...]}
│   ├── pilot-methodology.json
│   ├── W1-F.json
│   ├── W1-M.json
│   └── ...
├── methodology-dag.json      # 【主Agent 聚合】唯一权威图（聚合脚本产出，禁止手改）
├── node-content.json         # 【主Agent 聚合】五段式内容镜像（由 aggregate.py 派生）
└── stats.md                  # 【主Agent 聚合】统计与拓扑说明
```

> canonical 信源主表为 `03-knowledge-map/canonical-sources.json`（非本目录软引用文件）。

**分片文件 schema**（子Agent 落盘格式）：

```jsonc
{
  "batch_id": "W1-F",
  "wave": "W1",
  "domain": "F",
  "layers": ["essence", "methodology"],
  "produced_by": "<agent-role>",
  "generated": "2026-09-10",
  "nodes": [ /* 节点对象，字段见 §二 */ ],
  "edges": [ /* 边对象，字段见 §三；edge id 使用本批次预留块 */ ]
}
```

- **`detail` 内联于节点**（`stage4-data-model.md §2.3`），母库不建独立 `node-content.json`；12factor 的 `node-content.json` 为其库内历史形态，不迁移。
- 聚合后的 `methodology-dag.json` 顶层结构为 `{meta, groups, themes, cases, nodes, edges}`（`stage4-data-model.md §1`）。

---

## 二、节点生产契约

### 2.1 权威来源（字段与约束，不复制全文）

字段名、类型、必填、枚举、正则**一律以 `00-plan/stage4-data-model.md §2–§4` 为准**。子Agent 必须 `read` 该文件后再写节点。下面是**生产时最常用的字段速查**：

| 字段 | 类型/取值 | 必填 | 生产要点 |
|---|---|:--:|---|
| `id` | `^(ESS\|MTH\|TEC\|CAS)-[A-Z]{1,2}-\d{2}$` | ✅ | 前缀由层定：essence→`ESS`、methodology→`MTH`、technology→`TEC`、case→`CAS`；域位为 F–N/O/X；序号 2 位 |
| `name` | string，2–20 字符 | ✅ | 中文名，同 `domain` 内归一后唯一 |
| `en` | string，≤60 | ○ | 英文名 |
| `aliases` | string[] | ○ | 别名（含旧 ID 溯源别名） |
| `type` | `principle\|method\|technology\|bridge\|case\|tool` | ✅ | 层→type 的常用映射：essence→principle/bridge，methodology→method/bridge，technology→technology/tool，案例层→case |
| `group` | string，须存在于 `groups[]` | ✅ | 与组 `node_ids` 双向一致 |
| `layer` | `essence\|methodology\|technology`（case 为 `null`） | ✅* | 规范轴，决定依赖方向 |
| `domain` | `F/G/H/I/J/K/L/M/N/O/X` 之一 | ✅ | 语境轴（生命周期域枚举全集，见 §2.2） |
| `stage` | `basic\|intermediate\|advanced` | ✅ | 难度（**非生命周期阶段**） |
| `priority` | `P0\|P1\|P2\|P3` | ○ | 继承算法库优先级 |
| `definition` | string，15–300 字符 | ✅ | 一句话定义（五段式之"定义"段） |
| `cross_cutting` | 主题代码数组，≤3 | ○ | 取自 `themes[].id`；默认 `[]` |
| `case` | `CAS-*` id 数组 | ○ | 关联案例节点 |
| `sources` | 规范信源 ID 数组，1–8 | ✅ | **必须 canonical ID**（§2.3） |
| `verified` | `true\|false\|"cited"` | ✅ | 核验状态 |
| `confidence` | `high\|medium\|low` | ✅ | disputed 术语须标 low/medium |
| `review_date` | `YYYY-MM-DD` | ✅ | 易过时控制字段 |
| `status` | `active\|deprecated\|superseded` | ✅ | 技术层生命周期 |
| `version` | string\|null | ○ | technology/tool 必填 |
| `deprecated_at` | date\|null | ✅ | `status=deprecated` 时必填，否则 `null` |
| `superseded_by` | node id\|null | ○ | `status=superseded` 时必填 |
| `errata` | `[{misconception, verified_value, source_id}]` | ○ | 勘误（如 Lehman 条数、Royce 瀑布误读） |
| `detail` | object（五段式，见 §2.4） | ✅ | `{principle, mechanism, engineering, tradeoff}` |
| `tags` | string[] | ○ | 自由标签 |
| `entry_links` | string[] | ○ | **只放权威 URL / 本地语料相对路径** |

> `*` 案例节点 `layer` 为 `null`；其余节点 `layer` 必填。节点 ID 集合、类型→必填字段矩阵见 `stage4-data-model.md §4.4`。

### 2.2 `domain` 枚举（语境轴，全集）

以 `stage4-data-model.md §2.3` 为准：

| 域 | 生命周期含义 | 主用证据包 |
|---|---|---|
| `F` | 概念与需求 | `02-research/F-requirements.json` + R 概念子集 |
| `G` | 架构设计 | `02-research/G-architecture.json` + Q + R（POSA） |
| `H` | 实现与构造 | `02-research/H-implementation.json` |
| `I` | 测试 | `02-research/I-testing.json` |
| `J` | 部署 | `02-research/J-deployment.json` |
| `K` | 运维 | `02-research/K-operations.json` |
| `L` | 演化与弃用 | `02-research/L-evolution.json` + R 演化子集 |
| `M` | 横切·质量属性 | `02-research/M-quality-ility.json` + F |
| `N` | 横切·团队与康威 | `02-research/N-team-conway.json` |
| `O` | 方法论主干/跨域综合 | `02-research/O-methodology.json`（11 维权衡 + 36 原则↔反例） |
| `X` | 跨域/其他 | 跨域兜底（技术债等无独立生命周期归属者） |

> **技术债包（P）不新增域**：其节点归 `L` 域或 `X` 域，带 `cross_cutting:["P"]`；`P` 是**横切主题代码**，不是 `domain` 值。`Q/R` 为证据包，不映射为独立域（Q→G，R 按主题拆分）。此条与 `topic-source-matrix.md §1 注` 一致。

### 2.3 `sources[]` 必须用 canonical 信源 ID（刚性）

- 形态：`^(STD|OFF|BK|WEB|VEN|PAP|COM|LOC|XCV)-\d{3}$`（`stage4-data-model.md §2.3 / §4.3`）。
- **唯一真相**：`03-knowledge-map/canonical-sources.json`（由 `id-migration-plan.md` 的 Wave 0 工具链生成）。`sources[]` 每项必须能在其中解析，**命中率 100%**。
- **禁止**：阶段1 旧形态（`S1-STD-01`）、阶段2 包限形态（`F/S1-F01`、`H/S2-01`、`P-S4-08`、`R-XC-01`）直接出现在节点 `sources[]` 或 `edges[].sources`。旧 ID 一律经 `alias_ids` 反查后写 canonical ID。
- **入口链接**：官方 URL 写 `entry_links`，不写进 `sources[]`。
- **前置硬门控**：`canonical-sources.json` 未生成（id-migration AC1–AC10 未全绿）前，**禁止启动 Wave 1 内容生产**。

### 2.4 五段式内容模板（1500–3000 字）

每个节点正文由"定义 + 四段"构成，合计**目标 1500–3000 字**（`stage4-architecture-design.md §四`；GR-11 软目标，告警不阻断）：

| 段 | 字段 | 回答 | 写作要求 |
|---|---|---|---|
| **定义** | `definition` | 是什么 | 一句话，15–300 字符，单一主张 |
| **原理** | `detail.principle` | 为什么成立/为什么重要 | 稳定原理，不绑工具版本；≤600 字符 |
| **机制** | `detail.mechanism` | 如何运作 | 因果链/结构/步骤；≤600 字符 |
| **工程** | `detail.engineering` | 如何落地 | 可操作做法（可含工具但工具须另立技术节点） |
| **权衡** | `detail.tradeoff` | 代价与反例 | **见 §2.5 刚性要求**；≤600 字符 |

- 单段 ≤600 字符（GR-04）；需要 >5 段结构或跨 ≥3 域 → **拆节点**（`stage4-architecture-design.md §四`）。
- 写作语言：中文为主，保留英文术语原名（SWEBOK、ATAM、information hiding 等）；术语口径以 `03-knowledge-map/glossary.md` 为**唯一裁决表**（settled 用统一口径，disputed 显式标注且不得当标准术语引用）。

### 2.5 每节点必带反例或权衡（契约追加 GR-13）

**刚性**：每个非案例节点的 `detail.tradeoff` **必填**，且整节点至少满足其一：

1. 含**权衡**（`detail.tradeoff` 明确写出代价/适用边界/失效条件）；或
2. 含**反例**（`errata` 记录常见误解，或建有 `contrasts`/`conflicts` 边指向其反面）。

- `type=principle` 节点：`detail.tradeoff` 为强制（即 `stage4-data-model.md GR-12`），并建议同时配反例。
- 案例节点：`detail.tradeoff` 反映该案例的取舍与代价。
- 依据：`stage4-architecture-design.md §十二`（架构是权衡而非对错）与阶段2 原则↔反例门控（O 域 36 条）。
- 校验落点：`16-checkpoint/validate_graph.py` 的 `GR-13` 检查（追加于 GR-12 之上，报告为独立告警/错误项）。

### 2.6 层边界判定（写节点前先自问）

| 层 | 判据（全部满足才归入） | 反例警示 |
|---|---|---|
| `essence` | 换语言/框架/年代仍成立；与技术无关；对抗复杂度的根本概念或定律 | **本质层正文不得出现任何工具名与版本号** |
| `methodology` | 跨项目可迁移的过程/方法/决策框架；不绑定具体工具与版本 | 出现版本号即应下沉为技术节点 |
| `technology` | 有版本号/厂商/可被替代的具体工具、框架、命令行、平台条款 | 必须带 `version` + `status` + `review_date` |

若一个知识点同时含"稳定原理"与"工具实例"，**拆成两节点**（如"不可变基础设施"（methodology）↔"K8s 声明式部署"（technology）），用 `implements` 边连接，而非合并（`stage4-architecture-design.md §3.1`）。

---

## 三、分层与边规则

### 3.1 层间方向（依赖倒置，单向）

```
技术实践层 technology  --implements-->  方法论层 methodology  --derives_from-->  本质层 essence
（外层，易变）                          （中层，稳定）                            （内层，最稳定）
```

- `implements`：`from.layer == technology` 且 `to.layer == methodology`，单向；
- `derives_from`：`from.layer == methodology` 且 `to.layer == essence`，单向；
- **内层不得引用外层**：本质层节点不得出现指向技术层/方法论层的依赖边；方法论层不得指向技术层。
- **禁止技术层→本质层直连**（技术必须先经方法论中转，否则越级耦合）。

### 3.2 允许的边类型

以 `stage4-data-model.md §2.6` 为准。生产常用：

| type | 语义 | 方向 | 硬依赖边 | 层间合法性 |
|---|---|:--:|:--:|---|
| `implements` | 技术→方法论（实现） | 单向 | ✗ | **层间唯一允许之一**（tech→method） |
| `derives_from` | 方法论→本质（依据） | 单向 | ✅ | **层间唯一允许之一**（method→essence） |
| `prerequisite` | A 是 B 前置知识 | 单向 | ✅ | 层内/同层 |
| `refines` | A 细化 B | 单向 | ✅ | 同层 |
| `dependency` | A 依赖 B 存在 | 单向 | ✅ | 同层 |
| `case_instance` | 案例→知识节点（印证/违背） | 单向 | ✗ | 案例层→各层 |
| `cross_reference` | 跨体系对照（母库↔12factor） | 双向 | ✗ | 任意（**非层间依赖**） |
| `supersedes` / `deprecated_by` | 版本演化 | 单向 | ✗ | 技术层内 |
| `mitigates` | A 缓解/治理 B | 单向 | ✗ | 任意 |
| `contrasts` / `conflicts` | 对照/张力 | 双向 | ✗ | 任意 |
| `variant` / `combination` / `cooccurrence` | 12factor 继承 | 双向 | ✗ | 同层 |

**刚性**：层间（`layer` 不同）**只允许** `implements` 与 `derives_from`，且方向受 §3.1 约束。反向关联（如本质↔具体工具）**禁止建边**，一律用 `case_instance` 案例边或视图染色表达。

### 3.3 横切主题（用属性 + 染色，不建跨层边）

- 横切节点用 `cross_cutting[]` 属性 + `crosscut` 组（`kind:"crosscut"`）承载，配独立专题视图；
- **横切节点不建跨层边**，用染色表达（复用 cytoscape 经验：跨层关系用属性而非建边）；
- 主题代码登记于 `themes[]`（`M`=质量 / `P`=技术债 / `N`=团队 / `X`=其他）；
- 每节点 `cross_cutting` ≤3（GR-07）。

### 3.4 无环保证

硬依赖边集合 `{prerequisite, dependency, derives_from, refines}` 构成的子图必须**无环**，由 `16-checkpoint/validate_graph.py` 的 Kahn 拓扑校验强制；`meta.dag_acyclic` 必须为 `true`（12factor 门控项 4）。`implements`/`case_instance`/`cross_reference` 等非硬依赖边不参与环检测，但同样受层间方向规则约束。

---

## 四、批次计划（Wave 0–4）

### 4.0 编排总则

- **主Agent**：只做编排 / 聚合 / 裁决 / 门控，不写节点内容。
- **子Agent 粒度**：**每批 8–14 个节点**（按域邻近成批，`kb-construction §委派要点`）。
- **并行度**：**每波 5–8 个并行**子Agent；超出则拆子波（如 W1a/W1b）。
- **每波前读盘核对**：主Agent 读 `_batch-plan.json` + `_parts/` 实际文件，确认上一波 `status=pass` 后再启动。
- **失败处理**：任一批失败 → 该批重派，不阻塞同波其它批；同波结束再统一聚合。
- 复杂度继承 `[COMPLEXITY: 19/20] → Deep`，全程使用 Deep variant。

### 4.1 Wave 0 · 契约与骨架（前置，Wave 1 的硬门）

| 项 | 内容 |
|---|---|
| **输入** | 本文件、`stage4-data-model.md`、`id-migration-plan.md`、`dag-schema.example.json`、`0823-12factor-methodology/07-checkpoint/` |
| **产出** | ① `04-migration/{canonical-sources.json,old2new.json,collision-report.json,receipts/}`（id-migration AC1–AC10 全绿）；② `16-checkpoint/gen_common.py` + 5 生成器重构为通用框架（支持 layer/domain/case/多视图）；③ `10-dag-data/_batch-plan.json` 初版；④ 12factor 38 节点回归试点通过 |
| **验收** | id-migration AC1–AC10 全绿；12factor 38 节点在母库 schema 下 0 校验错误；`_batch-plan.json` schema 合法 |

> **Wave 0 未过，禁止进入 Wave 1。** 尤其 `canonical-sources.json` 是所有 `sources[]` 的解析前提（§2.3）。

### 4.2 Wave 1 · 本质层 + 方法论层节点生产

**输入**（证据包路径，按域）：

| 批次 | 域 | 输入证据包 | 补充依据 |
|---|---|---|---|
| `W1-F` | 概念与需求 | `02-research/F-requirements.json`、`02-research/R-foundational-papers.json`（概念子集）、`02-research/A-se-definition.json` | `glossary.md §0/§2`、`sources-index.md §2` |
| `W1-G` | 架构设计 | `02-research/G-architecture.json`、`02-research/Q-vendor-architecture.json`、`R`（POSA） | `glossary.md §1` |
| `W1-H` | 实现与构造 | `02-research/H-implementation.json` | `glossary.md §3` |
| `W1-I` | 测试 | `02-research/I-testing.json` | `glossary.md §4` |
| `W1-J` | 部署 | `02-research/J-deployment.json` | `glossary.md §5` |
| `W1-K` | 运维 | `02-research/K-operations.json` | `glossary.md §6` |
| `W1-L` | 演化与弃用 | `02-research/L-evolution.json`、`R`（Lehman）、`02-research/P-techdebt.json` | `glossary.md §7` |
| `W1-M` | 质量属性 | `02-research/M-quality-ility.json`、`F`（QA scenario） | `glossary.md §8` |
| `W1-N` | 团队与康威 | `02-research/N-team-conway.json` | `glossary.md §9` |
| `W1-O` | 方法论主干 | `02-research/O-methodology.json`（11 维权衡 `O-TD-01..11` + 36 原则↔反例 `O-PC-01..36`） | `glossary.md` 全部 23 条裁决 |

**并行编排**：W1a = `W1-F/G/H/I/J`（5 批）；W1b = `W1-K/L/M/N/O`（5 批）。若某域节点数 >14，拆子批（`W1-G-1`/`W1-G-2`），文件名随之唯一。

**产出**：每批 `10-dag-data/_parts/{batch_id}.json`（单文件，含 `nodes[]` + `edges[]`；`batch_id` 如 `W1-F`）。

**验收**：
- 每批 node 数 8–14；`validate_graph.py` 单分片 0 错误；
- `sources[]` 100% canonical 且可解析；无旧 ID 残留；
- `layer`/`domain` 枚举合法；`principle` 节点含 `tradeoff`（GR-12）；全节点含权衡或反例（GR-13）；
- 10 域中 `essence`/`methodology` 均有产出（为 GR-08 三层完整性打底）；
- 主Agent 聚合后 `methodology-dag.json` 通过 L2/L3，`glossary` 术语一致性专项通过。

### 4.3 Wave 2 · 技术实践层 + 案例层

**输入**：

| 批次 | 内容 | 输入 |
|---|---|---|
| `W2-TEC-H` | 实现技术（静态分析/SonarQube/SQALE-TDR 等） | `P-techdebt.json`、`H-implementation.json`、`Q` |
| `W2-TEC-I` | 测试技术（CI、质量门控工具、27119 族落地） | `I-testing.json` |
| `W2-TEC-J` | 部署技术（K8s、不可变基础设施实现、蓝绿/金丝雀工具） | `J-deployment.json`、`Q` |
| `W2-TEC-K` | 运维技术（OpenTelemetry、断路器/混沌工程实现、SLO 平台） | `K-operations.json`、`Q` |
| `W2-TEC-G/Q` | 架构工具与厂商框架（AWS/GCP Well-Architected、ThoughtWorks Radar、ADR 工具） | `G-architecture.json`、`Q-vendor-architecture.json` |
| `W2-TEC-L/M` | 演化/质量工具（fitness function 工具、Strangler Fig 实现） | `L-evolution.json`、`M-quality-ility.json` |
| `W2-CASE-A` | 案例 `CAS-*`（PA-01..09） | `02-research/C-local-inventory.json` 的 `assets[]`（PA-01..09 路径与可复用点） |
| `W2-CASE-B` | 案例 `CAS-*`（PA-10..18） | `02-research/C-local-inventory.json` 的 `assets[]`（PA-10..18） |
| `W2-XREF` | 12factor 38 节点 ↔ 母库映射表（`cross_reference`） | `0823-12factor-methodology/01-dag-data/methodology-dag.json`、本波技术节点 |

**12factor 纳入规则（严守 stage4 §七）**：
- 12factor 38 节点（12 App + 12 Agent + 10 桥接 + 4 工具）**不内联进母库主 DAG**，作为母库的**首个子库/实例库**，以 `cross_cutting` 专题（部署域 + AI 原生工程）呈现，**禁止复制其内容进母库**（防 ID 冲突与双份漂移）；
- 母库侧产出的是 `W2-XREF` 的**映射表**：每行给出 `母库节点 ID ↔ 12factor 节点 id ↔ 关系类型（cross_reference/case_instance）`，共 38 行；
- 深链格式：`../../../2026-08/0823-12factor-methodology/02-node-pages/<node-id>.html`；
  > ⚠️ 路径修正（2026-09-10 实测）：12factor 子库位于 `2026-08/`（跨年份目录），母库在 `2026-09/`，故从母库 `11-node-pages/` 或 `14-views/` 出发需**三级上跳 + 显式 `2026-08`**，原 `../../0823-...` 假设同级目录会导致 38 处断链。权威对照表落在 `16-checkpoint/xref-12factor.json`（38 行，`deep_link` 字段即以此格式）。
- 案例层 PA-01..18：提炼为 `CAS-*` 节点（独立、不阻塞主干 DAG、可离线加载），经 `case_instance` 边指向所印证/违背的方法论/本质节点；`cases[]` 索引与节点双写须一致。

**产出**：`10-dag-data/_parts/W2-*.json`；`16-checkpoint/xref-12factor.json`（38 行映射）；`10-dag-data/cases.json`（案例索引，聚合时并入）。

**验收**：
- technology/tool 节点 100% 带 `version` + `status` + `review_date`；
- 每条 `implements` 边方向合法（tech→method）且端点可解析；
- 38 行 12factor 映射齐全、无空行、深链可达；
- 18 个 PA 案例全部成为 `CAS-*` 节点，`case_instance` 边端点可解析，`case` 字段与 `cases[]` 一致；
- GR-09 案例覆盖：≥30% technology 节点有 `case` 或 `case_instance` 入边。

### 4.4 Wave 3 · 多视图 + 深链

**输入**：聚合后的 `10-dag-data/methodology-dag.json`（唯一数据源）。

**产出**（全部由同一模型派生，禁止硬编码，`stage4-architecture-design.md §六`）：

| 视图 | 数据来源 | 落点 |
|---|---|---|
| 总览（组级 + 点击下钻） | groups + nodes | `13-interactive/index.html` |
| 分层视图 | `layer` 过滤 + `implements`/`derives_from` | `14-views/01-layer.html` |
| 学习路径 | `stage`+`priority`+`prerequisite` | `14-views/02-learning-path.html` |
| 决策矩阵 | `O-TD-01..11` + `O-PC-01..36` + ATAM 术语 | `14-views/03-decision-matrix.html` |
| 跨体系对照 | `cross_reference` + 12factor | `14-views/04-cross-mapping.html` |
| 案例视图 | `case` 节点 + `case_instance` | `14-views/05-cases.html` |

外加：`12-groups/`（组页）、`11-node-pages/`（节点页，含"实践资源"区块列 12factor 深链）、`15-md/`（MD 镜像）、`index.html`（根入口）、双向深链（母库节点页↔12factor 节点页，**由生成脚本产出，禁止手改**）。

**验收**：六视图齐备；L5 渲染层 headless Chromium 实渲染通过（canvas 节点/边计数 == `meta` 计数、无 JS 错误）；内部相对链接 0 断链；双向深链由脚本生成且可达。

### 4.5 Wave 4 · 门控与留档

**输入**：全部 `10–17` 交付物 + `methodology-dag.json`。

**产出**：`quality-gate.md`（L1–L7 + 方法论专项实测明细）、`report.md` + `report.html`（双版本）、最终 `stats.md`。

**验收**：§六全部门控层 PASS（`skipped` 须显式记录，**skipped ≠ PASS**）；回放四硬指标全过（覆盖度 ≥90%、门控全过、信源可溯源率 ≥95%、人工抽查无重大语义错误）；HTML 双交付质量门控（UTF-8 无替换字符/div 开闭平衡/5 段完整）通过。

### 4.6 批次跟踪 `_batch-plan.json` schema

```jsonc
{
  "schema_version": "1.0.0",
  "generated": "2026-09-10",
  "waves": [
    {
      "id": "W1", "status": "running",
      "batches": [
        {
          "id": "W1-F", "domain": "F", "layers": ["essence", "methodology"],
          "responsible": "<agent-role>", "depends_on": ["W0"],
          "inputs": ["02-research/F-requirements.json", "03-knowledge-map/canonical-sources.json"],
          "edge_id_block": "E-001..E-060",
          "outputs": ["10-dag-data/_parts/W1-F.json"],
          "status": "pending", "node_count": 0, "edge_count": 0,
          "gate_cmd": "python3 16-checkpoint/validate_graph.py --shard 10-dag-data/_parts/W1-F.json --canonical 03-knowledge-map/canonical-sources.json",
          "receipt": null
        }
      ]
    }
  ]
}
```

- 每批**预留 edge ID 块**（`E-xxx` 全局唯一），避免跨分片碰撞；node ID 由"层前缀+域+批内序号"天然隔离。
- 主Agent 每波结束更新 `_batch-plan.json` 并落盘 `receipt`（批次回执）。

---

## 五、子Agent 落盘纪律（刚性）

1. **先落盘再返回**：子Agent 必须先把 `_parts/{batch_id}.json`（单文件，含 `nodes[]`/`edges[]`）写到磁盘，再返回 JSON 回执。禁止只返回内容文本（`kb-construction` C18）。
2. **文件名唯一，域+批次命名**：`W1-F.json`、`W2-TEC-J.json`、`W2-CASE-A.json`。多路并行共用目录时**禁止同名**（防同名互覆盖，`MEMORY` 经验）。
3. **只写指定分片**：子Agent **只能写** `10-dag-data/_parts/{本批次}.json`，**禁止**写 `methodology-dag.json`、禁止改 `00-plan/`、`02-research/`、`03-knowledge-map/`、禁止创建 `04-migration/` 内容。
4. **主Agent 聚合**：由 `16-checkpoint/aggregate.py` 合并全部分片为唯一 `methodology-dag.json`；聚合时做全局重号校验、计数一致、edge 端点解析；**禁止子Agent 各自写最终图**。
5. **`_batch-plan.json` 跟踪**：每批开工前主Agent 置 `running`，收批后核盘并置 `pass/failed` + 写 `receipt`。
6. **每波读盘核对**：主Agent 不信返回文本，逐文件 `read`/校验收批；缺失或不合规即重派该批（不继续下一波）。
7. **自验证**：子Agent 返回前必须自跑 `python3 -m json.tool <其分片>`（JSON 合法）+ `validate_graph.py --shard <其分片>`（0 错误），并在回执里给出命令与结果。
8. **返回格式**：所有子Agent 返回
   ```json
   {"status":"success|partial|failed","summary":"200字以内","data":{},"files_created":[],"files_modified":[],"decisions":[],"warnings":[],"errors":[]}
   ```
   `files_created/modified` 用绝对路径。
9. **内容纪律**：无源不写（每条事实挂 `sources[]`）；一手源优先；无法核验写入 `errata` 或标记 `confidence`，不伪装为事实；**禁止杜撰**信源、节点或边。
10. **不改契约**：本契约与所有 `stage4-*` 在阶段5 运行期间**字节稳定**（prefix-cache 与一致性要求）；子Agent 不得改动。

---

## 六、门控清单（L1–L7 + 方法论专项）

### 6.1 分层门控与脚本落点（`16-checkpoint/`）

| 层 | 查什么 | 脚本落点 | 命令（示例） | 通过阈值 |
|---|---|---|---|---|
| **L1 生成时自验证** | JSON 合法、schema/枚举、关键样例实跑 | `16-checkpoint/validate_graph.py`（含 `--shard`） | `python3 16-checkpoint/validate_graph.py --shard 10-dag-data/_parts/W1-F.json` | 错误 = 0 |
| **L2 全量审计** | 字段完整性、ID 唯一、计数一致、跨产物一致 | `16-checkpoint/validate_graph.py`（全图） | `python3 16-checkpoint/validate_graph.py --graph 10-dag-data/methodology-dag.json --canonical 03-knowledge-map/canonical-sources.json` | 错误 = 0；`meta.total_*` == 实际长度 |
| **L3 结构** | UTF-8/U+FFFD、断链、空文件、空正文、NAV 条目 | `kb_gate.py`（复用 kb-construction） | `python3 16-checkpoint/kb_gate.py --root . --layers structure,links,nav --exclude 04-migration --exclude 17-source/raw` | 结构坏项 = 0；断链 = 0 |
| **L4 视觉** | 架构图/决策矩阵图无截断、中文完整 | `16-checkpoint/gate_visual.py`（VLM + 像素计数） | `python3 16-checkpoint/gate_visual.py --images 14-views/*architecture*.png` | 无截断；中文字符像素计数达标 |
| **L5 渲染** | cytoscape 实渲染 canvas、节点/边计数、无 JS 错 | `16-checkpoint/gate_render.py`（headless Chromium） | `python3 16-checkpoint/gate_render.py --html 13-interactive/index.html --expect-nodes <N> --expect-edges <M>` | canvas 计数 == `meta`；JS 错误 = 0 |
| **L6 覆盖度** | 节点/视图/案例/深链矩阵逐项核对 | `16-checkpoint/gate_coverage.py` | `python3 16-checkpoint/gate_coverage.py --manifest 16-checkpoint/deliverables.json --graph 10-dag-data/methodology-dag.json` | 四向覆盖 ≥90%（DAG↔节点页↔MD↔案例） |
| **L7 信源** | canonical 可解析、证据区块、≥2 源交叉、disputed 标注 | `16-checkpoint/gate_sources.py` | `python3 16-checkpoint/gate_sources.py --graph 10-dag-data/methodology-dag.json --canonical 03-knowledge-map/canonical-sources.json` | 可溯源率 ≥95%；`verified=true` ≥80%（GR-10）；未解析 = 0 |

> `kb_gate.py` 复用 `~/.config/opencode/skills/kb-construction/scripts/kb_gate.py`（复制/软链到 `16-checkpoint/`，避免跨机路径假设）。
> 按规模按需启用：小批仅 L1+L3；全量建库 **L1–L7 全开**。环境缺失导致跳过的层必须**显式记录 `skipped`**，不算 PASS。

### 6.2 方法论专项门控（四项，`stage4-architecture-design.md §十一`）

由 `16-checkpoint/gate_methodology.py` 统一执行：

| # | 专项 | 判据 | 命令 |
|---|---|---|---|
| ① | **层边界判定规则校验** | 无内层引用外层（essence→methodology/technology、methodology→technology 均禁止）；无技术→本质直连边；`implements`/`derives_from` 方向正确 | `python3 16-checkpoint/gate_methodology.py --check layer-boundary --graph 10-dag-data/methodology-dag.json` |
| ② | **术语一致性** | 定义口径以 `03-knowledge-map/glossary.md` 为唯一裁决；disputed 术语显式标注且未当标准术语引用 | `... --check glossary --glossary 03-knowledge-map/glossary.md` |
| ③ | **原则↔反例配对完整性** | 每条 `O-PC-01..36` 必须入库且配反例（`errata` 或 `contrasts`/`conflicts` 边） | `... --check principle-counterexample` |
| ④ | **11 维权衡覆盖** | `O-TD-01..11` 均有落点节点 | `... --check tradeoff-11` |

### 6.3 回放四硬指标（Wave 4 终门，四项全过）

1. **覆盖度 ≥90%**：契约声明的交付物清单（`16-checkpoint/deliverables.json`）vs 实际产出，缺一即扣；
2. **门控全过**：L1–L7 中所有启用层 PASS（`skipped` 显式记录，不算 PASS）；
3. **信源可溯源率 ≥95%**：每条事实有 canonical 来源且标 verified/cited；
4. **人工抽查无重大语义错误**：抽样复核。

---

## 七、版权红线复述（刚性，逐波遵守）

依据 `00-plan/contract.md §5` 与 `stage4-architecture-design.md §十二`：

1. **书本体只入本地语料层**，**永不进公开仓库**；`17-source/` 只放官方入口链接与本地语料索引，**不得放入受版权保护的书籍/标准正文**。
2. **技术节点只引官方公开文档链接**（厂商 docs、标准官方页、官方开源仓库），`entry_links` 存链接，不复制正文。
3. **公开库只承载"消化、重组后的知识与方法论" + 自研脚本**。
4. 子Agent **不得下载或写入受版权保护的书籍全文**到 `MISSION_ROOT` 下任何交付目录。
5. 引文一律改写为自研表述；必要短引用须注明出处并控制篇幅（合理引用）。
6. 12factor 子库内容**不复制进母库**，仅以深链 `cross_reference` 对照（§4.3）。

---

## 八、快速自检清单（子Agent 返回前逐项打勾）

- [ ] 我已 `read` 本契约对应的 `stage4-data-model.md` 相关章节，未另立字段/枚举/正则。
- [ ] 我的分片文件名唯一（`{batch_id}.json`），只写 `10-dag-data/_parts/`。
- [ ] 每节点 8–14 个/批；`id` 正则合法；`layer`/`domain` 枚举合法；`type` 合法。
- [ ] 每节点 `sources[]` 全为 canonical ID，且能在 `03-knowledge-map/canonical-sources.json` 解析。
- [ ] 每节点含 `detail.tradeoff`（GR-13）或反例；`principle` 节点含 `tradeoff`（GR-12）。
- [ ] 层间边只有 `implements`（tech→method）/`derives_from`（method→essence），方向正确，无越级。
- [ ] 五段式合计 1500–3000 字（软目标）。
- [ ] 已自跑 `json.tool` + `validate_graph.py --shard`，0 错误，并写入回执。
- [ ] **先落盘再返回**，返回 JSON 含 `files_created`（绝对路径）与自验证命令结果。
- [ ] 未触碰 `00-plan/`、`02-research/`、`03-knowledge-map/`、`04-migration/`、`methodology-dag.json`。

---

*本契约与 `stage4-architecture-design.md`、`stage4-data-model.md`、`id-migration-plan.md`、`contract.md` 一致，无新增命名与杜撰；可作为阶段5 Wave 1–4 各波子Agent 的共享 P0 契约。*
