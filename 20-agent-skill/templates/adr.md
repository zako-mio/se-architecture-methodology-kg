# ADR 模板 · 架构决策记录

> 契约为唯一真相源：`schemas/adr.schema.json`。本模板只是其人类可读映射。
> 产出后必须过 `gate_architecture.py`；人读清单见 `checklist.md`。
> 所有节点 id 须先在 `<MISSION_ROOT>/10-dag-data/methodology-dag.json` 中核实存在，禁止编造。

## 一、字段说明

| 字段 | 必填 | 类型 / 约束 | 说明 |
|---|---|---|---|
| `id` | 是 | string，`^ADR-\d{3}$` | ADR 编号，如 `ADR-001` |
| `title` | 是 | string，非空 | 决策标题 |
| `status` | 是 | enum：`proposed`/`accepted`/`superseded`/`deprecated` | 状态 |
| `context` | 是 | string，非空 | 问题背景与约束 |
| `quality_scenarios` | 是 | array，≥1 | 每项 `stimulus`/`response`/`measure`，`measure` 必须可度量 |
| `options` | 是 | array，≥2 | 每项 `name`/`description`/`pros[]`/`cons[]`，`pros`/`cons` 非空 |
| `decision` | 是 | string，非空 | 选定方案；不得直接推荐技术实践层具体技术（禁 `TEC-` id） |
| `rationale` | 是 | string，非空 | 决策理由；须含 ≥1 个图谱节点 id；不得出现 `TEC-` id |
| `consequences` | 是 | object | `positive[]` / `negative[]` / `risks[]` |
| `sensitive_points` | 否 | array | 敏感点：一动即影响多个质量属性的设计点 |
| `tradeoff_points` | 否 | array | 权衡点：多个质量属性在此互相牵制 |
| `reversal_cost` | 否 | string | 回退条件与成本 |
| `graph_refs` | 是 | array，≥1，`^(ESS|MTH)-[A-Z]{1,2}-\d{2}$` | 支撑节点，**仅本质层（ESS）与方法论层（MTH）**；须能在 `methodology-dag.json` 解析 |
| `standards_refs` | 否 | array，`^TEC-[A-Z]{1,2}-\d{2}$` | 技术实践层节点，**仅作选型标尺佐证**；须能在 `methodology-dag.json` 解析 |
| `sources` | 是 | array，≥1 | 溯源：须能解析到 canonical 信源（`03-knowledge-map/canonical-sources.json`）或图谱节点的 `sources[]` |

> `graph_refs` 与 `standards_refs` 的分工：
> 前者是"判据"（ESS/MTH），决定 `decision` / `rationale`；
> 后者是"标尺"（TEC），只用于外部对照，**绝不进入推荐位**。

## 二、骨架（占位符，填完须产出合法 JSON）

```json
{
  "id": "ADR-000",
  "title": "<决策标题>",
  "status": "proposed",
  "context": "<问题背景与约束>",
  "quality_scenarios": [
    { "stimulus": "<刺激>", "response": "<响应>", "measure": "<可度量指标>" }
  ],
  "options": [
    { "name": "<方案A>", "description": "<描述>", "pros": ["<优点>"], "cons": ["<缺点>"] },
    { "name": "<方案B>", "description": "<描述>", "pros": ["<优点>"], "cons": ["<缺点>"] }
  ],
  "decision": "<选定方案，不推荐具体技术>",
  "rationale": "<理由，引图谱节点 id 如 MTH-O-03>",
  "consequences": { "positive": ["<正>"], "negative": ["<负>"], "risks": ["<风险>"] },
  "sensitive_points": ["<敏感点>"],
  "tradeoff_points": ["<权衡点>"],
  "reversal_cost": "<回退条件与成本>",
  "graph_refs": ["MTH-O-03", "ESS-O-02"],
  "standards_refs": ["TEC-G-01"],
  "sources": ["OFF-002", "BK-009"]
}
```

## 三、填好的最小示例（场景 1 · 绿地项目技术选型）

以下所有节点 id 均已核实在 `methodology-dag.json` 中存在：
`MTH-O-03`、`MTH-O-06`、`ESS-O-02`、`ESS-H-01`、`MTH-M-06`、`MTH-G-06`、
`TEC-G-01`、`TEC-G-04`。

```json
{
  "id": "ADR-001",
  "title": "内部工具平台的运行时形态：模块化单体优先",
  "status": "proposed",
  "context": "5 人团队、6 个月内交付一个内部工具平台；流量可预期、变更频繁、运维人力有限。问题：采用模块化单体还是按服务拆分。",
  "quality_scenarios": [
    {
      "stimulus": "新增一类报表需求",
      "response": "在单个已定边界内完成开发与上线",
      "measure": "变更触及模块数 <= 1，交付周期 <= 5 个工作日"
    },
    {
      "stimulus": "发布新版本后发现回归缺陷",
      "response": "可整体回滚到上一版本",
      "measure": "回滚时间 <= 10 分钟"
    }
  ],
  "options": [
    {
      "name": "模块化单体",
      "description": "单一部署单元内按信息隐藏划分模块，接口只暴露稳定契约。",
      "pros": ["运维面小，匹配 5 人团队的认知负荷", "变更局部化，回滚简单"],
      "cons": ["模块边界需靠纪律维持，易侵蚀", "单点扩展受部署单元限制"]
    },
    {
      "name": "按服务拆分",
      "description": "按子域拆为多个独立部署的服务。",
      "pros": ["团队与服务边界对齐，可独立扩展", "单服务故障可隔离"],
      "cons": ["引入分布式复杂性（一致性与可观测性）", "运维与发布成本超出团队承载"]
    }
  ],
  "decision": "采用模块化单体优先：先以信息隐藏判据划清模块边界并跑通最简可工作方案；待边界稳定、团队规模增长后，再沿已识别接缝按需拆分。",
  "rationale": "依 MTH-O-03 够用原则，任何额外能力都伴随新的持续复杂度；依 ESS-O-02 架构即权衡，当前约束下模块化单体在认知负荷与交付速度上收益更高；边界划分依 MTH-O-06 与 ESS-H-01，沿「可能变化的设计决策」设定，使未来拆分有接缝可依；质量属性冲突按 MTH-M-06、MTH-G-06 显式化为权衡点后再定序。",
  "consequences": {
    "positive": ["交付与运维成本低，匹配团队规模", "变更局部化，利于快速迭代"],
    "negative": ["需以适应度函数守护模块边界，否则易侵蚀"],
    "risks": ["边界纪律失守会导致耦合上升，未来拆分成本升高"]
  },
  "sensitive_points": ["模块边界划分（影响可修改性与可演化性）"],
  "tradeoff_points": ["交付速度 vs 独立可扩展性"],
  "reversal_cost": "若边界稳定后需拆分，按已识别接缝逐个绞杀式迁移；回退条件为服务拆分收益（独立扩缩容 / 故障隔离）超过分布式复杂度成本。",
  "graph_refs": ["MTH-O-03", "MTH-O-06", "ESS-O-02", "ESS-H-01", "MTH-M-06", "MTH-G-06"],
  "standards_refs": ["TEC-G-01", "TEC-G-04"],
  "sources": ["OFF-002", "BK-009", "BK-036", "VEN-006"]
}
```

> 说明：示例中 `TEC-G-01`（AWS 良好架构框架）、`TEC-G-04`（ThoughtWorks 技术雷达）
> 仅作为 `standards_refs` 的选型标尺，未出现在 `decision` / `rationale` 推荐位。
> `sources` 条目为 canonical 信源 id，可在 `03-knowledge-map/canonical-sources.json` 解析。
