---
name: architecture-judgment
description: >
  软件工程与架构设计方法论**可执行工作流**能力包（由「速查 + 路径路由」升级），内置 167 节点知识图谱（无需联网）。
  当用户涉及：架构决策、技术选型、架构评审、需求工程、演进与技术债治理、
  康威定律/团队边界、质量属性权衡、上线与运维设计、测试策略、软件工程方法论、
  选型矩阵、架构判断力、遗留系统重构、可观测性、DORA 交付效能 等场景时加载。
  触发关键词：架构决策、技术选型、架构评审、需求工程、技术债、演进式架构、
  康威定律、团队拓扑、质量属性、ATTO/ATAM、敏感点、权衡点、可观测性、SLO、
  错误预算、测试金字塔、绞杀者、适应度函数、康威、选型矩阵、架构判断力、
  ADR、架构检查单、多维权衡矩阵。
  是否需要联网：否（内置图谱）。
  本地节点页深链模板：<MISSION_ROOT>/11-node-pages/<ID>.html（另有 <MISSION_ROOT>/15-md/nodes/<ID>.md）。
  公开 Pages 深链模板：https://zako-mio.github.io/se-architecture-methodology-kg/11-node-pages/<ID>.html
---

# architecture-judgment · 架构判断力能力包

> 把「软件工程 / 架构设计方法论知识图谱」（167 节点 / 360 边 / 18 组 / 11 域 / 三层）
> 从"速查 + 路径路由"升级为 Agent 可执行的**架构设计工作流**。
> 权威源（单一真相源）在本仓 `<MISSION_ROOT>/20-agent-skill/`；本机派生安装副本由
> `install-skill.py` 生成，路径由 `local-bindings.json` 声明。
> **不内联大段内容、不做检索层**：命中场景后按路由表定位节点，需要细节再打开节点页深链。

## 1. 能力定位

- 三层能力栈中的**能力层**：为 architect-worker 与主 Agent 提供可执行工作流，而非仅是索引。
- 把一个架构问题变成**可解释、可复核、可交付**的产物：先判决策类型，再路由节点，
  最后产出 ADR（必选）与多维权衡矩阵（选型场景），并过机检门控方可交付。
- 配套文件：
  - `workflow.md`：4 步可执行工作流（判类型 → 读速查 → 深链 → 产出 + 自检）。
  - `checklist.md`：架构检查单（人读版），对应机检判据 G-A1~G-A6。
  - `templates/adr.md` / `templates/matrix.md`：ADR 与多维权衡矩阵产出模板（门控级，场景 1–5、10–12）。
  - `templates/review.md`：评审结论模板（产出级，场景 4、8）。
  - `templates/tech-debt.md`：技术债象限与重构优先级模板（按需级，场景 2、3、11）。
  - `templates/boundary.md` + `schemas/boundary.schema.json`：边界/模块设计说明契约（`kind=boundary`，门控级）。
  - `schemas/adr.schema.json`：ADR 结构化契约（机检依据，唯一真相源，不得改动）。
  - `integrations/openspec-design.md`：openspec `design` 工件集成契约（触发/动作/门控/留档）。
- 覆盖三层：本质（为什么，51）→ 方法论（怎么做，67）→ 技术实践（用什么做，31）+ 案例（18）。
- 适用：绿地选型、遗留治理、需求收敛、质量权衡、团队边界、上线运维、测试与度量。
- 边界：不提供具体厂商操作手册；技术实践层节点仅作选型标尺，落地细节需结合项目约束。

## 2. 知识分层策略（引用纪律）

- **本地图谱为主**：节点全文以 `<MISSION_ROOT>/` 下图谱为准，离线可用；公开 Pages 深链仅作外部引用。
- **方法论层（MTH）重召回**：判断阶段允许放宽命中，候选宁多勿漏，再由深链核对确认。
- **本质层（ESS）重召回**：作为判据来源，同样放宽命中。
- **技术实践层（TEC）仅作"选型标尺"，宁缺毋滥**：
  - TEC 节点只能写入 ADR 的 `standards_refs`，作为选型佐证或时效性标尺；
  - `decision` / `rationale` 等推荐位**不得出现 TEC- 节点 id**，也不直接推荐具体技术/厂商；
  - 必须与场景字面精确命中才引用，否则不引。

## 3. 何时加载（触发条件）

1. **自动路由**：任务涉及技术选型 / 架构风格 / 模块与服务边界与粒度 / 架构评审 /
   质量属性权衡 / 技术债治理 / 演进治理时，主流程（plan/build）自动加载本 skill 并委派 architect-worker。
2. **显式命令**：`/arch <架构任务描述>` 或 `/arch 选型|评审|边界|技术债 ...`。
3. **openspec design 阶段**：`design` 工件生成时，由行为层 `architecture-behavior.md` **强制触发**本 skill；详细契约见 `integrations/openspec-design.md`；`gate_architecture.py` PASS 前不得定稿 `design.md`。

具体场景（判类型见 `routing.md` §0）：技术选型 / 架构评审 / 需求获取与规格化 / 质量属性与 ATAM 分析 /
技术债识别与偿还 / 遗留系统重构与绞杀者替换 / 演进式架构与防漂移 / 康威定律与团队拓扑 /
部署与发布策略 / 可观测性与 SLO / 测试策略与门控 / 交付效能度量 / 软件工程方法论与架构判断力。

## 4. 使用流程（4 步，详见 workflow.md）

1. **判类型**：把问题归到 `routing.md` 的 18 个任务场景之一（先匹配「触发问法」）。
2. **读速查**：用 `cheatsheet.md` 对应层条目做第一轮判断，得到支撑节点 id。
3. **深链接**：按 `<MISSION_ROOT>/11-node-pages/<ID>.html`（或 `<MISSION_ROOT>/15-md/nodes/<ID>.md`）读节点全文确认。
4. **产出 + 自检**：按 `schemas/adr.schema.json` 产 ADR（模板 `templates/adr.md`），
   需要选型时产多维权衡矩阵（`templates/matrix.md`）；边界/模块设计说明走 `templates/boundary.md` +
   `schemas/boundary.schema.json`，以 `gate_architecture.py --kind boundary` 门控。
   两者均以 `gate_architecture.py --kind adr|boundary --input <path>` 自检；不过不得交付。

## 5. 文件导航

| 文件 | 用途 | 何时读 |
|---|---|---|
| `workflow.md` | 可执行工作流：判类型→读速查→深链→产出+自检 | 拿到问题第一步读 |
| `checklist.md` | 架构检查单（人读版），对应门控判据 G-A1~G-A6 | 交付前逐项勾选 |
| `templates/adr.md` | ADR 模板（全部字段占位 + 填好示例） | 产出 ADR 时 |
| `templates/matrix.md` | 多维权衡矩阵模板（维度/权重/评分/结论衔接） | 需要选型对比时 |
| `templates/review.md` | 评审结论模板（敏感点/权衡点/风险主题/结论） | 做架构评审、设计裁决时（场景 4、8） |
| `templates/tech-debt.md` | 技术债象限与重构优先级模板 | 识别/治理技术债时（场景 2、3、11） |
| `templates/boundary.md` | 边界/模块设计说明模板（kind=boundary） | 设计模块/服务边界时（场景 11） |
| `schemas/adr.schema.json` | ADR 结构化契约（机检依据，不得改动） | 产出前与门控时 |
| `schemas/boundary.schema.json` | 边界/模块设计说明结构化契约（`gate_architecture.py --kind boundary` 依据） | 产出前与门控时 |
| `integrations/openspec-design.md` | openspec `design` 工件集成契约（触发/动作/门控/留档） | design 阶段被行为层触发时 |
| `cheatsheet.md` | 三层各 8–12 条关键判断准则（每条 ≤60 字，附节点 id） | 需要快速判断时先读 |
| `routing.md` | 18 个高频任务场景 → 应读节点/组/视图/学习路径 | 拿到问题先查这里定位 |
| `decision-matrix.md` | 域 × 层落点矩阵 + 横切主题 + 权衡启发式（派生自决策矩阵视图） | 需要按域/层系统排查覆盖时 |
| `node-index.md` | 167 节点 id ↔ 名称 ↔ 层 ↔ 域 一句话索引 | 需要按 id 深链或查名时 |

## 6. 深链与外部入口

- 本地节点页：`<MISSION_ROOT>/11-node-pages/<ID>.html`（例：`<MISSION_ROOT>/11-node-pages/MTH-G-02.html`）
- 本地节点 MD：`<MISSION_ROOT>/15-md/nodes/<ID>.md`
- 公开节点页：`https://zako-mio.github.io/se-architecture-methodology-kg/11-node-pages/<ID>.html`
- 分组目录：`https://zako-mio.github.io/se-architecture-methodology-kg/12-groups/`
- 视图入口：`.../14-views/index.html`（分层 / 学习路径 / 决策矩阵 / 案例 / 术语表）
- 交互总览：`.../13-interactive/index.html`

## 7. 术语权威口径

术语以本仓 `03-knowledge-map/glossary.md`（152 词条，状态 `settled` / `disputed`）为唯一裁决表。
标注 `disputed` 者（如 `微服务`、`可观测性`、`可扩展性`、`可演化性`）不得当作标准术语引用。
本速查表内的术语（如 `康威定律`、`信息隐藏`、`质量属性场景`、`技术债象限`、`架构适应度函数`、
`逆向康威操作`、`错误预算`、`测试金字塔`、`质量门控`、`古德哈特定律`）均取自该表。
