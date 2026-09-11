# 架构检查单 · 人读版

> 把机检判据（ADR：G-A1~G-A6；边界说明：G-B1~G-B5）转成人工可勾选清单，每条附「为什么」。
> 机检对应脚本：`gate_architecture.py`（私有层，`--kind adr|boundary`，产物为结构化 ADR / 边界说明 / 权衡矩阵）。
> **交付前逐项勾选；任一项不满足 → 不得交付。**

## 一、正向判据

- [ ] **G-A1 · 结构合法**：ADR 是合法 JSON，且 schema 必填字段齐全
      （`id` / `title` / `status` / `context` / `quality_scenarios` / `options` / `decision` /
      `rationale` / `consequences` / `graph_refs` / `sources`）。
      - 为什么：机检与下游加工都以结构化为前提，缺字段会让门控和后续消费直接失败。

- [ ] **G-A2 · 备选充分**：`options` 至少 2 个，且每项含非空 `pros` 与 `cons`。
      - 为什么：没有对比就没有决策；单方案或空利弊等于把"取舍"藏起来，无法复核。

- [ ] **G-A3 · 理由可溯**：`rationale` 非空，且至少引用 1 个图谱节点 id（计入 `graph_refs`）。
      - 为什么：判断必须挂在可追溯的方法论判据上，而不是个人偏好。

- [ ] **G-A4 · 引用零悬挂**：`graph_refs` / `standards_refs` 中每个 id 都能在
      `methodology-dag.json` 中解析。
      - 为什么：悬挂引用会指向不存在的判据，等于伪溯源；零悬挂是"引用为真"的最低条件。

- [ ] **G-A5 · 技术层不越位**：技术实践层节点（`TEC-`）只出现在 `standards_refs`；
      `decision` / `rationale` 推荐位无任何 `TEC-` id。
      - 为什么：技术层节点是"选型标尺"而非本能力包的判据，越位会把方法论判断降格成具体技术推荐。

- [ ] **G-A6 · 场景可度量**：`quality_scenarios` 至少 1 条，且每条 `measure` 可度量。
      - 为什么：不可度量的质量目标无法验证，也就无法在评审中判定是否达成。

## 二、技术层"越位"自查

- [ ] `decision` 与 `rationale` 中检索不到任何 `TEC-` 节点 id。
- [ ] 未在推荐位出现具体技术/厂商名称；技术只作为 `standards_refs` 的标尺佐证。
- [ ] 每个被引用的 TEC 节点都标注了版本/时效提示，并注明"落地前需复核"。
- [ ] 技术层引用均满足"字面精确命中场景"，无为了凑数而引入的技术节点。

## 三、边界/模块设计说明检查单（`--kind boundary`）

- [ ] **G-B1 · 结构合法**：边界说明是合法 JSON，且 schema 必填字段齐全
      （`id` / `title` / `context` / `adr_ref` / `modules` / `graph_refs` / `sources`）。
      - 为什么：与 ADR 同属机检与下游加工的输入，缺字段直接失败。
- [ ] **G-B2 · 模块化三要素**：`modules` ≥1，且每模块 `responsibility`（职责）/
      `interface`（对外契约）/ `info_hidden`（隐藏的内部细节）均非空。
      - 为什么：缺 `info_hidden` 的"模块"只是目录项；三要素齐备才对应 `MTH-H-02` 的信息隐藏。
- [ ] **G-B3 · 边界引用一致**：`boundaries[]`（可选）的 `from`/`to` 必须是 `modules[].name` 中存在的模块。
      - 为什么：指向不存在模块的边界是幽灵依赖，无法复核。
- [ ] **G-B4 · 引用零悬挂**：`graph_refs` / `standards_refs` 每个 id 都能在 `methodology-dag.json` 解析。
      - 为什么：同 G-A4，悬挂引用等于伪溯源。
- [ ] **G-B5 · 技术层不越位**：`TEC-` id 只出现在 `standards_refs`；
      `context` / `title` / `responsibility` / `interface` / `info_hidden` / `contract` 等叙述位无 `TEC-` id。
      - 为什么：技术层是选型标尺，不得进入叙述/推荐位。

> 人工补充自查（机检不覆盖）：`adr_ref` 指向的 ADR 编号确实存在，且本说明与之一致。

## 四、备注

- 负向测试由门控脚本自检：ADR 侧"缺字段 / 单备选 / 悬挂引用 / 技术层越位"、
  边界侧"缺模块三要素 / boundaries 引用不存在模块 / 悬挂引用 / 技术层越位"样本必须 FAIL，
  不列入人工清单。
- 判据治理原则：优先换判据而非放宽阈值；连续谱度量只报告不判 FAIL；门控脚本自身也要门控。
