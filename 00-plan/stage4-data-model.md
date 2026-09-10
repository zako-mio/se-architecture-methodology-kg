# 阶段4 · 数据模型规范：DAG 知识图谱 schema（v1.1）

> 母任务：0910-软件工程架构方法论 · 阶段4 建库设计交付物（本文件只做设计，不建库、不迁移）
> 日期：2026-09-10　状态：设计稿（供阶段5 生产契约使用）
> **定位**：本文件是**主设计文档 `stage4-architecture-design.md §五` 数据模型的字段级细化与机器可校验表达**。字段名、枚举、层间边规则**一律以主设计为准**，本规范只做**加法扩展**（可校验字段、粒度规则、检索预留），不另立命名。
> 基线参照：`0823-12factor-methodology/01-dag-data/methodology-dag.json`（`{meta,groups,nodes,edges}` 四段结构）
> 配套文件：`id-migration-plan.md`（**信源 ID** 统一迁移）、`dag-schema.example.json`（合法样例）

---

## 0. 设计定位与边界（先读）

| 问题 | 归属 | 说明 |
|---|---|---|
| **节点 ID 形态** | **主设计 §八**：`{层前缀}-{域}-{序号}`（如 `ESS-H-01`） | 本规范只补 `CAS` 前缀用于案例层，并给出正则 |
| **信源 ID 形态** | **本规范配套** `id-migration-plan.md`：`{类别}-{序号}`（如 `STD-001`） | 两套命名空间**正交**：节点 ID 标识"知识节点"，信源 ID 标识"证据来源" |
| node/edge 字段与枚举 | **主设计 §五** | 本规范逐字段细化 + 追加任务要求的扩展字段（`deprecated_at` 等） |
| 节点粒度 | 主设计 §四（四条 + 量化启发式） | 本规范把它翻译为**可执行校验规则**（§5） |
| 检索层 D2 | 主设计 §十二（维持挂起，不建） | 本规范只约定未来字段与导出格式（§6），**不实现** |

> **一致性硬约束**：`layer` 枚举、`type` 枚举、`cross_cutting` 取值、`case` 字段名、层间边方向均与主设计 §五 完全一致；本规范新增字段一律可选，旧生产脚本可忽略。

---

## 1. 顶层结构

```jsonc
{
  "meta":    { /* §2.1 元信息 */ },
  "groups":  [ /* §2.2 分组容器（含 crosscut 组） */ ],
  "themes":  [ /* §2.4 横切主题登记表（扩展，可选） */ ],
  "cases":   [ /* §2.5 案例索引（扩展，可选） */ ],
  "nodes":   [ /* §2.3 知识节点 */ ],
  "edges":   [ /* §2.3 关系边 */ ]
}
```

> 与 12factor 一致保留 `meta/groups/nodes/edges`；`themes[]`、`cases[]` 为**可选的加法扩展**，缺失时不影响主干渲染（完全向后兼容）。案例重内容仍以 `nodes[]` 中 `type:"case"` 的节点为准，`cases[]` 只做索引。

### 1.1 与 12factor 的向后兼容

| 12factor 字段 | 新模型 | 处理 |
|---|---|---|
| `meta.{title,subtitle,version,generated,total_*}` | 同名 | 保留，新增 `schema_version`、`total_themes`、`total_cases` |
| `meta.stages`（`basic/intermediate/advanced`） | `node.stage` | 语义保留为**节点难度**（主设计 §五） |
| `meta.edge_types` | 同名（枚举扩展） | 保留并扩展（§2.6） |
| `groups[].{id,name,domain,kind,node_ids}` | 同名字段 | 兼容；`kind` 新增 `crosscut`/`case`/`layer` |
| `nodes[].{id,name,en,type,src,group,stage,definition}` | 同名 | 兼容；`type` 枚举改为主设计 §五 版（§2.3） |
| `edges[].{from,to,type,label}` | 同名 | 兼容；新增 `id`/`directed`/`weight`/`sources` |

---

## 2. 字段表

### 2.1 `meta`

| 字段 | 类型 | 必填 | 说明 / 约束 |
|---|---|:--:|---|
| `title` / `subtitle` | string | ✅ / ○ | 标题 / 副标题 |
| `version` | string | ✅ | `^\d+\.\d+\.\d+$` |
| `schema_version` | string | ✅ | 本规范版本，固定 `1.1.0` |
| `source_namespace_version` | string | ✅ | 信源 ID 命名空间版本（`id-migration-plan.md`），如 `1.0.0` |
| `generated` / `updated` | date | ✅ | `YYYY-MM-DD` |
| `review_cycle_days` | integer | ○ | 复核周期（默认 180） |
| `total_groups` / `total_nodes` / `total_edges` | integer | ✅ | 须与实际数组长度相等 |
| `total_themes` / `total_cases` | integer | ○ | 有 `themes[]`/`cases[]` 时必填 |
| `layers` | string[] | ✅ | 固定 `["essence","methodology","technology"]`（主设计 §五） |
| `edge_types` | string[] | ✅ | 本图实际使用的边类型 |
| `hard_edge_types` | string[] | ○ | 参环检测的边类型（默认 `prerequisite/dependency/derives_from/refines`） |
| `dag_acyclic` | boolean | ✅ | 硬依赖边子集无环（须 `true`） |
| `license_note` | string | ○ | 版权说明 |
| `retrieval` | object | ○ | 检索层预留占位（§6.3） |

### 2.2 `groups[]`（含横切组）

| 字段 | 类型 | 必填 | 说明 / 约束 |
|---|---|:--:|---|
| `id` | string | ✅ | `^G[A-Z0-9-]{1,10}$`（沿用 12factor；新增用 `GD-*`/`GC-*`/`GX*`） |
| `name` / `en` | string | ✅ / ○ | 中文名 / 英文名 |
| `kind` | string | ✅ | `source` / `bridge` / `crosscut`(横切) / `case`(案例) / `tool` / `layer` / `domain` |
| `domain` | string | ○ | 关联域代码（F–N/O/X），保留 12factor 字段 |
| `description` | string | ○ | 说明 |
| `parent` | string\|null | ○ | 父分组 id |
| `order` | integer | ○ | 展示排序 |
| `node_ids` | string[] | ✅ | 组内节点 id（须与节点 `group` 双向一致） |

### 2.3 `nodes[]`

**基础字段（兼容 12factor）**

| 字段 | 类型 | 必填 | 说明 |
|---|---|:--:|---|
| `id` | string | ✅ | `^(ESS\|MTH\|TEC\|CAS)-[A-Z]{1,2}-\d{2}$`（主设计 §八 + `CAS` 案例扩展） |
| `name` | string | ✅ | 中文名，≤20 字符，同 `domain` 内唯一 |
| `en` | string | ○ | 英文名，≤60 字符 |
| `aliases` | string[] | ○ | 别名（检索与迁移用） |
| `type` | enum | ✅ | **主设计 §五**：`principle / method / technology / bridge / case / tool` |
| `subtype` | string | ○ | 可选细分（如 `process/pattern/tactic/practice/antipattern`），不参与强校验 |
| `src` | string | ○ | 旧 12factor 标记，可省略 |
| `group` | string | ✅ | 所属分组 id（须存在） |
| `stage` | enum | ✅ | **难度**：`basic / intermediate / advanced`（主设计 §五） |
| `priority` | enum | ○ | `P0 / P1 / P2 / P3` |
| `definition` | string | ✅ | 一句话定义，15–300 字符 |

**主设计扩展字段（★）+ 本规范追加（☆）**

| 字段 | 来源 | 类型 | 必填 | 说明 / 约束 |
|---|---|:--:|:--:|---|
| `layer` ★ | 主设计 | enum | ✅* | `essence / methodology / technology`；`type:"case"` 允许 `null` |
| `domain` ★ | 主设计 | enum | ✅ | 生命周期域：`F/G/H/I/J/K/L/M/N/O/X`（F–N 九域 + O 方法论 + X 跨域） |
| `cross_cutting` ★ | 主设计 | string[] | ○ | 横切主题代码，取自 `themes[].id`（默认主题 `M`=质量 / `P`=技术债 / `N`=团队 / `X`=其他）；默认 `[]` |
| `case` ★ | 主设计 | string[] | ○ | 关联案例节点 id（`CAS-*`）；任务清单里的 `case_ref` 是**单值别名**，本规范统一用 `case`（数组） |
| `sources` ★ | 主设计 | string[] | ✅ | **规范信源 ID**，每项 `^(STD\|OFF\|BK\|WEB\|VEN\|PAP\|COM\|LOC\|XCV)-\d{3}$`，≥1 且可解析 |
| `verified` ★ | 主设计 | enum | ✅ | `true / false / "cited"` |
| `confidence` ★ | 主设计 | enum | ✅ | `high / medium / low` |
| `review_date` ★ | 主设计 | date | ✅ | 易过时控制字段 |
| `status` ★ | 主设计 | enum | ✅ | `active / deprecated / superseded`（技术层生命周期） |
| `version` ★ | 主设计 §3.3 | string | ○ | 技术节点版本 |
| `errata` ★ | 主设计 | object[] | ○ | `[{misconception, verified_value, source_id}]` |
| `deprecated_at` ☆ | 任务要求 | date\|null | ✅ | 与 `status` 互补：`status=deprecated` 时填日期；否则 `null` |
| `superseded_by` ☆ | 本规范 | string\|null | ○ | `status=superseded` 时填取代节点 id |
| `detail` ☆ | stage2 五段式 | object | ○ | key ∈ `{principle, mechanism, engineering, tradeoff}`（定义为 `definition` 段） |
| `tags` | 12factor 兼容 | string[] | ○ | 自由标签 |
| `entry_links` | 本规范 | string[] | ○ | 权威 URL / 本地语料相对路径（只放链接） |

> `*` 案例节点 `layer` 为 `null`；其余节点 `layer` 必填。

### 2.4 `themes[]`（横切主题登记表，扩展）

主设计 §五 用 `cross_cutting` 属性 + 独立 `crosscut` 组承载横切。本表为**可选登记表**，把主题代码映射到元数据（便于生成专题视图），不改变 `cross_cutting` 取值口径。

| 字段 | 类型 | 必填 | 说明 |
|---|---|:--:|---|
| `id` | string | ✅ | 主题代码（`^[A-Z]{1,3}$`），与 `node.cross_cutting[]` 一致 |
| `name` / `en` | string | ✅ / ○ | 主题名 |
| `definition` | string | ✅ | 主题定义 |
| `domains` | string[] | ○ | 主要关联域 |
| `sources` | string[] | ✅ | 规范信源 ID |
| `order` | integer | ○ | 排序 |
| `related_nodes` | string[] | ○ | 派生字段（脚本回填） |

**初始主题登记**（对齐 `topic-source-matrix.md` 横切域）：

| id | 主题 | 主要来源 | 对应证据包 |
|---|---|---|---|
| `M` | 质量属性 / ilities | `STD-005`、`OFF-002`、`BK-009`、`PAP-008` | M 包 |
| `P` | 技术债 | `WEB-002`、`PAP-006`、`PAP-008` | P 包 |
| `N` | 团队与康威定律 | `BK-030` + N 包新增源 | N 包 |
| `X` | 其他跨域主题 | 视需要 | — |

> `crosscut` 组（`kind:"crosscut"`）与 `themes[]` 并存：组管布局，表管语义。

### 2.5 `cases[]`（案例索引，扩展）

案例以 `nodes[type=case]` 为主；本索引便于按项目聚合。

| 字段 | 类型 | 必填 | 说明 |
|---|---|:--:|---|
| `id` | string | ✅ | 案例节点 id（`CAS-*`），与 `nodes[].id` 一致 |
| `node_id` | string | ○ | 同 `id`（兼容双写；二者须一致） |
| `title` | string | ✅ | 标题 |
| `org` / `year` | string | ○ | 主体 / 年份 |
| `summary` | string | ✅ | 80–200 字概要 |
| `outcome` | string | ○ | 结论/成效 |
| `sources` | string[] | ✅ | 规范信源 ID（本地实战留档用 `LOC-*`） |

### 2.6 `edges[]`

| 字段 | 类型 | 必填 | 说明 |
|---|---|:--:|---|
| `id` | string | ✅ | `^E-\d{2,3}$` |
| `from` / `to` | string | ✅ | 节点 id（须可解析） |
| `type` | enum | ✅ | 见下 |
| `label` | string | ✅ | 中文说明（≤40 字符） |
| `directed` | boolean | ○ | 默认 `true` |
| `weight` | number\|null | ○ | `0–1`，仅 `cooccurrence` 使用 |
| `sources` | string[] | ○ | 支持该关系的规范信源 ID |

**边类型表**（保留 12factor 5 类 + 主设计扩展 + 本规范加法）

| type | 来源 | 语义 | 方向 | 硬依赖边 |
|---|---|:--:|:--:|:--:|
| `prerequisite` | 12factor | A 是 B 的前置知识 | 单向 | ✅ |
| `dependency` | 12factor | A 依赖 B 存在 | 单向 | ✅ |
| `derives_from` | **主设计** | 方法论→本质（依据）；A 由 B 推导 | 单向 | ✅ |
| `refines` | 本规范 | A 细化 B | 单向 | ✅ |
| `implements` | **主设计** | 技术→方法论（实现） | 单向 | ✗ |
| `case_instance` | **主设计** | 案例→知识节点（印证/违背） | 单向 | ✗ |
| `cross_reference` | **主设计** | 跨体系对照（如母库↔12factor） | 双向 | ✗ |
| `supersedes` / `deprecated_by` | **主设计** | 版本演化 | 单向 | ✗ |
| `variant` | 12factor | 同一本质的两种形态 | 双向 | ✗ |
| `combination` | 12factor | 组合使用 | 双向 | ✗ |
| `cooccurrence` | 12factor | 弱共现（需 `weight`） | 双向 | ✗ |
| `mitigates` | 本规范 | A 缓解/治理 B（如重构→技术债） | 单向 | ✗ |
| `contrasts` / `conflicts` | 本规范 | 对照 / 张力（如 DRY↔过度抽象） | 双向 | ✗ |
| `enables` | 本规范 | A 使 B 成为可能 | 单向 | ✗ |

> **层间边硬规则（主设计 §3.2，必须遵守）**：层间只允许 `implements`（技术→方法论）与 `derives_from`（方法论→本质）**单向**；**禁止**内层引用外层（如本质→技术）。反向关联一律用 `case_instance` 或视图染色，不建边。硬依赖边（含层内 `prerequisite`）共同保证主干 DAG 无环。

---

## 3. 横切主题与案例层承载方式

| 轴 | 载体 | 引用方式 | 依据 |
|---|---|---|---|
| 三层（规范轴） | `node.layer` | 枚举 | 主设计 §二/§三 |
| 生命周期域（语境轴） | `node.domain` | 枚举（F–N/O/X） | 主设计 §二 |
| 横切主题 | `node.cross_cutting[]` + `crosscut` 组 + `themes[]` | 主题代码引用 | 主设计 §五 |
| 案例层 | `nodes[type=case]`（`CAS-*`）+ `cases[]` + `case` 字段 + `case_instance` 边 | id 引用 | 主设计 §五/§七 |

- **横切**：横切节点不建跨层边（主设计 §五），仅用 `cross_cutting` 属性 + 染色；`themes[]` 只是代码→元数据登记。
- **案例**：案例是独立节点，**不阻塞主干 DAG**，可离线加载；主干节点用 `case:["CAS-..."]` 挂载，案例节点用 `case_instance` 边回指所印证/违背的节点，二者由门控核对一致。

---

## 4. 节点粒度规则的机器可校验表达

### 4.1 校验分层（对应 kb-construction L1–L7）

| 层 | 检查 | 工具 |
|---|---|---|
| L-A 语法 | JSON 可解析 / UTF-8 无 U+FFFD / 无 BOM | `json.loads` + 编码扫描 |
| L-B 结构 | 必填字段、类型、枚举、ID 唯一 | 校验脚本 §4.5 |
| L-C 引用 | `group/themes/case/sources/edge 端点` 全解析，零悬挂 | 校验脚本 |
| L-D 粒度 | 定义长度、名称唯一、sources 数量、坐标唯一 | 校验脚本 |
| L-E 图性质 | 硬依赖无环、无自环、计数一致、**层间边方向合法** | 校验脚本 |
| L-F 版本 | `status=deprecated/superseded` 有对应日期/取代者 | 校验脚本 |
| L-G 统一 | 同域 `name/en/aliases` 归一后不重复（主设计 §四"合并"启发式） | 校验脚本 |

### 4.2 粒度上下限（主设计 §四的量化）

| 规则 | 对象 | 约束 | 对应主设计 |
|---|---|---|---|
| `GR-01` | `name` | 2–20 字符 | §四 可引用/单一主张 |
| `GR-02` | `name`/`en`/`aliases` | 同 `domain` 内归一化后唯一 | §四 ">70% 重叠→合并" |
| `GR-03` | `definition` | 15–300 字符 | §四 单一主张；超限转 `detail` |
| `GR-04` | `detail.*` 单段 | ≤600 字符 | §四 ">5 段或跨≥3 域→拆分" |
| `GR-05` | `sources` | 1–8 | 保可溯源；>8 说明聚合过度 |
| `GR-06` | 坐标 | 一个节点在 `layer` 与 `domain` 各只有一个落点 | 主设计 §四"单坐标" |
| `GR-07` | `cross_cutting` | 每节点 ≤3 个主题 | 防止横切滥用 |
| `GR-08` | 三层完整性 | 每 `domain` 至少各有 1 个 `essence`/`methodology`/`technology` 节点（案例域豁免） | §二 D1 解耦 |
| `GR-09` | 案例覆盖 | ≥30% 的 `technology` 节点有 `case` 或 `case_instance` 入边 | §六 案例视图 |
| `GR-10` | 溯源覆盖 | 节点 `sources` 非空 100%；`verified=true` 占比 ≥80% | 契约 §6 / L7 |
| `GR-11` | 详细度 | `name+definition+detail` 合计目标 1500–3000 字（软目标，告警不阻断） | 主设计 §四"可承载" |
| `GR-12` | 权衡配平 | `type=principle` 节点必须含 `detail.tradeoff` | 阶段2 原则↔反例门控 |

### 4.3 命名规则（正则）

| 对象 | 正则 | 示例 |
|---|---|---|
| 节点 id | `^(ESS\|MTH\|TEC\|CAS)-[A-Z]{1,2}-\d{2}$` | `ESS-H-01`、`MTH-G-03`、`TEC-J-05`、`CAS-H-01` |
| 分组 id | `^G[A-Z0-9-]{1,10}$` | `GA`、`GD-ARCH`、`GX1`、`GC-CASE` |
| 边 id | `^E-\d{2,3}$` | `E-01`、`E-014` |
| 主题代码 | `^[A-Z]{1,3}$` | `M`、`P`、`N`、`X` |
| 信源 id | `^(STD\|OFF\|BK\|WEB\|VEN\|PAP\|COM\|LOC\|XCV)-\d{3}$` | `PAP-001`、`LOC-016` |
| 日期 | `^\d{4}-\d{2}-\d{2}$` | `2026-09-10` |
| 版本 | `^\d+\.\d+\.\d+$` | `1.0.0` |

### 4.4 节点类型 → 必填字段矩阵

| 字段 \ type | principle | method | technology | bridge | case | tool |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| `id/name/group/definition` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `layer` | ✅ | ✅ | ✅ | ✅ | ○(null) | ✅ |
| `domain` / `stage` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `sources` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `verified/confidence/review_date/status` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `cross_cutting`（可空） | ○ | ○ | ○ | ○ | ○ | ○ |
| `case`（可空） | ○ | ○ | ○ | ○ | — | ○ |
| `detail.tradeoff` | ✅ | ○ | ○ | ○ | ✅ | ○ |
| `version` | ○ | ○ | ✅ | ○ | ○ | ✅ |

> ✅=必填；○=可选；—=不适用。`technology/tool` 必须带 `version`（配合 `status`/`review_date` 实现"技术过时隔离"，主设计 §3.3）。

### 4.5 校验器设计（伪代码，阶段5 实现）

```python
import re
NODE = re.compile(r'^(ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2}$')
CANON = re.compile(r'^(STD|OFF|BK|WEB|VEN|PAP|COM|LOC|XCV)-\d{3}$')
HARD = {'prerequisite', 'dependency', 'derives_from', 'refines'}

def validate(g):
    errs = []
    node_ids = {n['id'] for n in g['nodes']}
    theme_ids = {t['id'] for t in g.get('themes', [])} or {'M','P','N','X'}
    group_ids = {x['id'] for x in g['groups']}
    case_node_ids = {n['id'] for n in g['nodes'] if n['type'] == 'case'}

    seen = set()
    for n in g['nodes']:
        if n['id'] in seen: errs.append(('DUP_ID', n['id']))
        seen.add(n['id'])
        if not NODE.match(n['id']): errs.append(('NODE_ID', n['id']))
        if not 2 <= len(n['name']) <= 20: errs.append(('GR-01', n['id']))
        if not 15 <= len(n['definition']) <= 300: errs.append(('GR-03', n['id']))
        if not 1 <= len(n['sources']) <= 8: errs.append(('GR-05', n['id']))
        if n['layer'] not in ('essence','methodology','technology', None):
            errs.append(('LAYER', n['id']))
        if n['type'] != 'case' and n['layer'] is None: errs.append(('LAYER_MISSING', n['id']))
        if n['type'] == 'case' and n['layer'] is not None: errs.append(('CASE_LAYER', n['id']))
        if n['group'] not in group_ids: errs.append(('BAD_GROUP', n['id']))
        for s in n['sources']:
            if not CANON.match(s): errs.append(('BAD_SRC', n['id'], s))
        if len(n.get('cross_cutting', [])) > 3: errs.append(('GR-07', n['id']))
        for cc in n.get('cross_cutting', []):
            if cc not in theme_ids: errs.append(('BAD_THEME', n['id'], cc))
        for c in n.get('case', []):
            if c not in case_node_ids: errs.append(('BAD_CASE', n['id'], c))
        if n['type'] == 'principle' and not n.get('detail', {}).get('tradeoff'):
            errs.append(('GR-12', n['id']))
        if n['status'] == 'deprecated' and not n.get('deprecated_at'):
            errs.append(('DEP_NO_DATE', n['id']))
        if n['status'] == 'superseded' and not n.get('superseded_by'):
            errs.append(('SUP_NO_SUCC', n['id']))

    for e in g['edges']:
        if e['from'] not in node_ids or e['to'] not in node_ids:
            errs.append(('EDGE_ENDPOINT', e['id']))
        if e['from'] == e['to'] and e['type'] in HARD:
            errs.append(('SELF_LOOP', e['id']))
        # 层间方向规则
        if e['type'] in ('implements', 'derives_from'):
            lf = layer_of(g, e['from']); lt = layer_of(g, e['to'])
            if e['type'] == 'derives_from' and not (lf == 'methodology' and lt == 'essence'):
                errs.append(('EDGE_DIR', e['id'], 'derives_from 须 methodology->essence'))
            if e['type'] == 'implements' and not (lf == 'technology' and lt == 'methodology'):
                errs.append(('EDGE_DIR', e['id'], 'implements 须 technology->methodology'))

    # 硬依赖环检测（Kahn）
    adj, indeg = {}, {n: 0 for n in node_ids}
    for e in g['edges']:
        if e['type'] in HARD:
            adj.setdefault(e['from'], []).append(e['to']); indeg[e['to']] += 1
    q = [n for n in node_ids if indeg[n] == 0]; cnt = 0
    while q:
        u = q.pop(); cnt += 1
        for v in adj.get(u, []):
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    if cnt != len(node_ids): errs.append(('CYCLE',))

    if g['meta']['total_nodes'] != len(g['nodes']): errs.append(('COUNT_NODES',))
    return errs
```

---

## 5. 检索层预留接口设计（D2 = 预留不建）

> 主设计 §十二 明确：**不建检索层，除非出现明确跨域检索需求**（YAGNI）。本节只约定字段与格式，供阶段5+ 决策时直接落地，避免届时返工改图。**本阶段不实现任何导出脚本、不建 SQLite。**

### 5.1 检索单元（chunk）划分

| `chunk_kind` | 来源字段 | 说明 |
|---|---|---|
| `name` | `name` + `en` + `aliases` | 标题级召回（权重最高） |
| `definition` | `definition` | 定义级召回 |
| `principle` / `mechanism` / `engineering` / `tradeoff` | `detail.*` | 五段式分段召回 |
| `case` | 案例节点 `detail` + `cases[].summary` | 案例召回 |
| `theme` | `themes[].definition` | 横切主题召回 |
| `edge` | `edges[].label` | 关系召回（可选） |

### 5.2 导出格式约定（不实现）

```
retrieval/
├── manifest.json      # 索引元信息 + 图哈希 + 计数
├── nodes.jsonl        # 归一化节点（一行一节点）
└── chunks.jsonl       # 检索单元（一行一 chunk，FTS5 导入源）
```

**`chunks.jsonl` 单行字段**：`chunk_id`、`node_id`、`node_name`、`chunk_kind`、`lang`、`text_zh`、`text_en`、`layer`、`domain`、`cross_cutting`、`case`、`sources`、`verified`、`confidence`、`review_date`、`status`、`aliases`、`updated`。

**`manifest.json` 字段**：`schema_version`、`generated`、`graph_hash`（规范化 `nodes+edges+themes+cases` 的 SHA-256）、`chunk_count`、`node_count`、`langs`、`tokenizer`（建议 `trigram`）、`retrieval_enabled`（D2 阶段固定 `false`）。

### 5.3 图内预留块（`meta.retrieval`，占位）

```jsonc
"retrieval": {
  "enabled": false,
  "export_dir": "retrieval/",
  "chunk_schema_version": "1.0.0",
  "planned_engine": "sqlite-fts5",
  "tokenizer": "trigram",
  "filters": ["layer", "domain", "cross_cutting", "case", "verified", "status"],
  "note": "D2=预留不建；阶段5 决策后置 enabled=true 并实现导出脚本"
}
```

### 5.4 未来 FTS5 DDL（仅文档，不执行）

```sql
CREATE VIRTUAL TABLE node_fts USING fts5(
  chunk_id UNINDEXED, node_id UNINDEXED, text,
  tokenize='trigram'
);
CREATE TABLE chunk_meta(
  chunk_id TEXT PRIMARY KEY, node_id TEXT, layer TEXT, domain TEXT,
  cross_cutting TEXT, case_ref TEXT, sources TEXT, verified INTEGER,
  confidence TEXT, review_date TEXT, status TEXT
);
```

---

## 6. 门控映射（本 schema 对应主设计 §十一 L1–L7）

| 层 | 本 schema 落点 |
|---|---|
| L1 生成时自验证 | §4.5 校验器写盘前运行，返回 `[]` |
| L2 全量审计 | 全图校验 + 计数一致 + 信源 ID 统一（迁移方案） |
| L3 结构 | JSON 合法、UTF-8 无 U+FFFD、无空字段 |
| L5 渲染 | 交互 DAG 用 `nodes/edges` 实渲染，计数与 `meta` 一致 |
| L6 覆盖度 | 三层完整性（GR-08）、案例覆盖（GR-09） |
| L7 信源 | `sources` 可解析率 100%、`verified` ≥80%（GR-10）、`errata` 已标注 |
| 方法论专项 | 层边界（§4.5 EDGE_DIR）、术语（glossary 唯一裁决）、原则↔反例（GR-12） |

---

## 7. 与主设计文档一致性核对表

| 主设计条目 | 本规范处理 | 一致？ |
|---|---|---|
| §五 `layer` = essence/methodology/technology | 同枚举，案例层 `layer` 可空 | ✅ |
| §五 `domain` = F…N 十域 + cross | 用 `F…N/O/X`，与主设计示例 `ESS-H-01` 同构 | ✅ |
| §五 `type` = principle/method/technology/bridge/case/tool | 同枚举；新增可选 `subtype` 细化 | ✅ |
| §五 `cross_cutting` = [M,P,N…] | 同口径；`themes[]` 仅为登记表 | ✅ |
| §五 `case` = [case-id] | 同字段名（任务清单的 `case_ref` 为别名） | ✅ |
| §五 `status` = active/deprecated/superseded | 同枚举；追加 `deprecated_at`（任务要求） | ✅ |
| §五 `verified` = true/false/"cited" | 同枚举 | ✅ |
| §五 边 implements/derives_from/cross_reference/case_instance/supersedes | 全保留；新增 mitigates/contrasts/conflicts/enables/refines | ✅ |
| §3.2 层间只允许 implements/derives_from 单向 | §4.5 `EDGE_DIR` 强制校验 | ✅ |
| §八 节点 ID `{层前缀}-{域}-{序号}` | 采用，补 `CAS` 案例前缀 | ✅ |
| §八 为阶段1/2 信源 ID 建映射表 | 由 `id-migration-plan.md` 承担（**信源 ID** 命名空间） | ✅ |
| §十二 不建检索层（D2 挂起） | §5 仅约定字段，不实现 | ✅ |

---

## 8. 未决与交接

1. **`src` 字段去留**：12factor 的 `app/agent/bridge` 标记对本母库无意义，建议阶段5 弃用；本稿设为可选。
2. **`domain` 是否含 `O`/`X`**：主设计称"F…N 十域 + cross"，实际字母为 F–N（9）+ O（方法论）+ X（跨域）；阶段5 需敲定枚举全集。
3. **案例节点前缀 `CAS`**：主设计未指定案例节点 id 形态，本规范补 `CAS`；若主设计另有约定，以主设计为准。
4. **信源 ID 依赖**：本文所有 `sources` 示例均用**规范 ID**；在 `id-migration-plan.md` 完成前，阶段5 **不得**直接引用旧的 `S1-STD-01` 形态。
