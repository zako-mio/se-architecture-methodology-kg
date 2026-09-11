# 边界/模块设计说明模板 · Boundary

> 契约为唯一真相源：`schemas/boundary.schema.json`。本模板只是其人类可读映射。
> 产出后必须过 `gate_architecture.py --kind boundary`；人读清单见 `checklist.md`。
> 所有节点 id 须先在 `<MISSION_ROOT>/10-dag-data/methodology-dag.json` 中核实存在，禁止编造。
> 定位：ADR 决定「做什么取舍」，本说明描述「按此决策如何划分模块与边界」。

## 一、字段说明

| 字段 | 必填 | 类型 / 约束 | 说明 |
|---|---|---|---|
| `id` | 是 | string，`^BD-\d{3}$` | 边界说明编号，如 `BD-001` |
| `title` | 是 | string，非空 | 标题 |
| `context` | 是 | string，非空 | 问题背景与约束；叙述位不得出现 `TEC-` id |
| `adr_ref` | 是 | string，`^ADR-\d{3}$` | 关联 ADR 编号（回链），本说明落地的是该决策 |
| `modules` | 是 | array，≥1 | 每项 `name`/`responsibility`/`interface`/`info_hidden`，**四者均非空** |
| `boundaries` | 否 | array | 模块间边界；每项 `from`/`to`/`contract`，`from`/`to` 必须是 `modules[].name` 中存在的模块 |
| `graph_refs` | 是 | array，≥1，`^(ESS|MTH)-[A-Z]{1,2}-\d{2}$` | 支撑节点（**仅 ESS/MTH**）；须能在 `methodology-dag.json` 解析 |
| `standards_refs` | 否 | array，`^TEC-[A-Z]{1,2}-\d{2}$` | 技术实践层节点，**仅作选型标尺佐证**；不得出现在 `context`/`title`/`responsibility`/`interface`/`info_hidden`/`contract` |
| `sources` | 是 | array，≥1 | 溯源：须能解析到 canonical 信源或图谱节点 `sources[]` |

> **模块化三要素**（机检 `G-B2`）：`responsibility`（职责）、`interface`（对外契约）、`info_hidden`（隐藏的内部细节，对应 `MTH-H-02` 信息隐藏）。三者缺一即视为伪边界设计。

## 二、骨架（占位符，填完须产出合法 JSON）

```json
{
  "id": "BD-000",
  "title": "<边界说明标题>",
  "context": "<背景与约束>",
  "adr_ref": "ADR-000",
  "modules": [
    { "name": "<模块A>", "responsibility": "<职责>", "interface": "<对外契约>", "info_hidden": "<隐藏的内部细节>" },
    { "name": "<模块B>", "responsibility": "<职责>", "interface": "<对外契约>", "info_hidden": "<隐藏的内部细节>" }
  ],
  "boundaries": [
    { "from": "<模块A>", "to": "<模块B>", "contract": "<跨边界契约 / 依赖方向约束>" }
  ],
  "graph_refs": ["MTH-H-02", "MTH-O-06"],
  "standards_refs": [],
  "sources": ["BK-009"]
}
```

## 三、填好的最小示例（场景 11 · 模块 / 服务边界与粒度）

以下所有节点 id 均已核实在 `methodology-dag.json` 中存在：
`ESS-G-04`、`ESS-H-01`、`MTH-H-02`、`MTH-O-06`、`MTH-G-04`、`TEC-G-04`。

```json
{
  "id": "BD-001",
  "title": "内部工具平台：模块边界与信息隐藏划分",
  "context": "承接 ADR-001 的模块化单体决策。约束：5 人团队、变更频繁、运维人力有限；需按「可能变化的设计决策」设定边界，使未来按接缝拆分有据可依。",
  "adr_ref": "ADR-001",
  "modules": [
    {
      "name": "报表模块",
      "responsibility": "聚合与呈现业务数据报表，负责报表定义与渲染",
      "interface": "对外暴露稳定的报表查询契约（输入：报表标识与筛选条件；输出：结果集），不暴露内部存储结构",
      "info_hidden": "报表计算引擎、缓存策略与数据源适配细节全部封装在模块内，对外不可见"
    },
    {
      "name": "数据访问模块",
      "responsibility": "统一封装持久化与数据源访问",
      "interface": "对外暴露与具体存储无关的读写契约，隔离上层与存储实现",
      "info_hidden": "连接管理、事务边界与具体存储方言均隐藏于模块内"
    },
    {
      "name": "身份与权限模块",
      "responsibility": "认证、授权与会话管理",
      "interface": "对外暴露鉴权判定契约（主体 + 资源 → 允许/拒绝），不暴露凭证存储",
      "info_hidden": "口令散列算法、令牌生成与密钥轮换细节封装于模块内"
    }
  ],
  "boundaries": [
    { "from": "报表模块", "to": "数据访问模块", "contract": "仅经数据访问模块的读写契约取数，禁止报表模块直接持有存储连接" },
    { "from": "报表模块", "to": "身份与权限模块", "contract": "报表访问前调用鉴权判定契约；权限模块不感知报表语义" }
  ],
  "graph_refs": ["ESS-G-04", "ESS-H-01", "MTH-H-02", "MTH-O-06", "MTH-G-04"],
  "standards_refs": ["TEC-G-04"],
  "sources": ["BK-009", "OFF-002"]
}
```

> 说明：示例中 `TEC-G-04`（ThoughtWorks 技术雷达）仅作为 `standards_refs` 的选型标尺佐证，
> 未出现在 `context`/`title`/`responsibility`/`interface`/`info_hidden`/`contract` 等叙述位。
> `sources` 条目为 canonical 信源 id，可在 `03-knowledge-map/canonical-sources.json` 解析。
