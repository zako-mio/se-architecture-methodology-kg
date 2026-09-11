# 可执行工作流 · 架构设计与选型

> 供 architect-worker 与主 Agent 执行。目标：把架构问题变成可交付、可机检的产物。
> 单一真相源为本目录（`<MISSION_ROOT>/20-agent-skill/`）。门控脚本 `gate_architecture.py`
> 位于私有层 `_private/`（不公开）；人读版检查项见 `checklist.md`。
> 知识分层纪律见 `SKILL.md` §2：本地图谱为主；MTH/ESS 重召回；TEC 仅作标尺、宁缺毋滥。

## 总览

```
判类型 → 读速查 → 深链接 → 产出 + 自检
  ①        ②         ③            ④
```

---

## 第 1 步 · 判类型

**输入**：用户问题（自然语言）。

**动作**：
1. 读 `routing.md` §0 场景索引，在 18 个场景中**先匹配「触发问法」**。
2. 命中后记下该场景号与「首要节点」，并记录同场景的组/视图/案例线索。
3. 若一个问题横跨多个场景，取与"决策落点"最相关的一个为主场景，其余作为补充阅读。

**回退**：无法归入任一场景时，**不得强行套用**。改为通用架构判断，并显式声明
"场景不确定"，说明所依据的层（本质层 ESS / 方法论层 MTH）与理由。

**产出**：场景号（1–18）或"未分类"标记 + 候选首要节点 id。

---

## 第 2 步 · 读速查

**输入**：上一步的场景与候选节点。

**动作**：
1. 读 `cheatsheet.md`，按"先定位层"原则取对应层条目（本质层 / 方法论层 / 技术实践层）。
2. 第一轮判断，得到支撑节点 id 候选。
3. 命中纪律：
   - **方法论层（MTH）与本质层（ESS）：重召回**——允许放宽命中，候选宁多勿漏，交由第 3 步深链核对。
   - **技术实践层（TEC）：严格精确**——必须与场景**字面精确命中**才引用，否则不引；
     且只作为标尺进入 `standards_refs`（细则见文末附录）。

**产出**：支撑节点 id 候选集（ESS/MTH 为主，TEC 仅作标尺候选）。

---

## 第 3 步 · 深链接

**输入**：候选节点 id。

**动作**：
1. 按 `<MISSION_ROOT>/11-node-pages/<ID>.html`（或 `<MISSION_ROOT>/15-md/nodes/<ID>.md`）读取节点全文确认。
2. 核对节点的定义/机制是否真的支撑当前判断；不支撑则从候选集中剔除。
3. 对敏感点/权衡点与质量属性场景，回到 `MTH-G-02`（质量属性场景与 ATAM）、
   `MTH-G-06`（效用树与敏感点权衡点分析）等节点确认度量口径。

**产出**：经确认的 `graph_refs`（ESS/MTH）与 `standards_refs`（TEC，可选）。

---

## 第 4 步 · 产出 + 自检

**输入**：确认的节点引用 + 问题约束。

**动作**：
1. 按 `schemas/adr.schema.json` 产出 ADR，模板见 `templates/adr.md`；
   必填字段齐全、`options` ≥2、`rationale` 含 ≥1 图谱节点 id。
2. 需要选型对比时，按 `templates/matrix.md` 产出多维权衡矩阵，
   并把结论回填到 ADR 的 `options` / `decision`。
3. 边界/模块设计场景（场景 11）：按 `schemas/boundary.schema.json` 产出边界说明（模板 `templates/boundary.md`），
   `adr_ref` 回链对应 ADR，落 `BD-xxx.json`。
4. 跑门控自检（`--kind` 按产物类型；schema 与 graph 自动解析，亦可显式 `--schema` / `--graph`）：

   ```bash
   python3 _private/gate_architecture.py --kind adr      --input <adr.json>
   python3 _private/gate_architecture.py --kind boundary --input <boundary.json>
   ```

   人读清单见 `checklist.md`。
5. **门控不过不得交付**：修正后重跑，最多 2 轮；仍不过则回退并报告卡点。

**产出**：ADR（必选）+ 权衡矩阵（选型场景）+ 边界/模块设计说明（边界场景，`kind=boundary`）+ 门控通过记录。

---

## 附录 · 技术层"仅作标尺"执行细则

| 规则 | 说明 |
|---|---|
| 引用位白名单 | `TEC-` 节点 id **只能**写入 ADR 的 `standards_refs`。 |
| 推荐位禁用 | `decision` / `rationale` 不得出现任何 `TEC-` 节点 id，也不得直接推荐具体技术/厂商。 |
| 命中要求 | 技术层必须**字面精确命中**场景才引用；不确定就不引（宁缺毋滥）。 |
| 版本时效 | 引用 TEC 节点时须提示其版本/时效性，说明"标尺可能过期，落地前需复核"。 |
| 措辞模板 | 用"以 `<TEC-节点名>` 作为选型标尺佐证"，而非"应选用 `<具体技术>`"。 |

> 机检对应判据 G-A5（见 `checklist.md`）：技术层节点不得出现在 `decision`/`rationale` 的推荐位，
> 仅允许在 `standards_refs`。该判据用"引用位白名单"实现，可机检。
