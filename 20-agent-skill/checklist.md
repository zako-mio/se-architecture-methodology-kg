# 架构检查单 · 人读版

> 把机检判据（G-A1~G-A6 / G-B1~G-B5）转成人工可勾选清单，每条附「为什么」。
> 机检脚本：`gate_architecture.py`（私有层，`--kind adr|boundary`）。
> **交付前逐项勾选；任一项不满足 → 不得交付。**
> 判据蕴含与降级规则见 `_private/CRITERIA.md`；回报见 `--ledger-report`。

## 一、正向判据

- [ ] **G-A1 · 结构合法**：ADR 是合法 JSON，且 schema 必填字段齐全
      （必填字段见 `adr.schema.json`，逐项释义见 `templates/adr.md`）。
      - 为什么：结构化为机检与下游消费的前提，缺字段直接失败。

- [ ] **G-A2 · 备选充分**（⊂ G-A1，非独立判据）：`options` 至少 2 个，且每项含非空 `pros` 与 `cons`。
      - 为什么：没有对比就没有决策；单方案或空利弊等于把"取舍"藏起来，无法复核。
      - 注：schema `minItems` 已完全蕴含（校验通过即必然通过）；**不得计入"独立判据数"**，详见 `_private/CRITERIA.md` §1。

- [ ] **G-A3 · 理由可溯**：`rationale` 非空，且至少引用 1 个图谱节点 id（计入 `graph_refs`）。
      - 为什么：判断必须挂在可追溯的方法论判据上，而不是个人偏好。

- [ ] **G-A4 · 引用零悬挂**：`graph_refs` / `standards_refs` 中每个 id 都能在
      `methodology-dag.json` 中解析；**且**工件内声明的兄弟文件引用（`matrix_ref` / `adr_ref` /
      `boundary_ref` / `review_ref`）指向的文件真实存在。
      - 为什么：悬挂引用等于伪溯源；零悬挂是"引用为真"的最低条件。
      - 注：此前只查图谱引用，兄弟文件引用悬空仍能 PASS——**契约自身允许悬空**，已收口。

- [ ] **G-A5 · 技术层不越位**：技术实践层节点（`TEC-`）只出现在 `standards_refs`；
      `decision` / `rationale` 推荐位无任何 `TEC-` id。
      - 为什么：技术层是"选型标尺"而非判据，越位会把方法论判断降格成技术推荐。

- [ ] **G-A6 · 场景可度量**：`quality_scenarios` 至少 1 条，且每条 `measure` 可度量。
      - 为什么：不可度量的目标无法验证，评审中无法判定达成。
      - 注：独立残余为「`measure` 是否占位符」；非空性已由 schema `minLength=1` 蕴含。

## 二、技术层"越位"自查

- [ ] `decision` 与 `rationale` 中检索不到任何 `TEC-` 节点 id。
- [ ] 未在推荐位出现具体技术/厂商名称；技术只作为 `standards_refs` 的标尺佐证。
- [ ] 每个被引用的 TEC 节点都标注了版本/时效提示，并注明"落地前需复核"。
- [ ] 技术层引用均满足"字面精确命中场景"，无为了凑数而引入的技术节点。

## 三、边界/模块设计说明检查单（`--kind boundary`）

- [ ] **G-B1 · 结构合法**：边界说明是合法 JSON，且 schema 必填字段齐全
      （必填字段见 `boundary.schema.json`，逐项释义见 `templates/boundary.md`）。
      - 为什么：同 G-A1，缺字段直接失败。
- [ ] **G-B2 · 模块化三要素**（⊂ G-B1，非独立判据）：`modules` ≥1，且每模块 `responsibility` /
      `interface` / `info_hidden` 均非空（三要素释义见 `templates/boundary.md`）。
      - 为什么：缺 `info_hidden` 的"模块"只是目录项；三要素齐备才对应 `MTH-H-02` 的信息隐藏。
      - 注：该断言已由 `boundary.schema.json` 完全蕴含（见 `_private/CRITERIA.md` §1）。
- [ ] **G-B3 · 边界引用一致**：`boundaries[]`（可选）的 `from`/`to` 必须是 `modules[].name` 中存在的模块。
      - 为什么：指向不存在模块的边界是幽灵依赖，无法复核。
- [ ] **G-B4 · 引用零悬挂**：`graph_refs` / `standards_refs` 每个 id 都能在 `methodology-dag.json` 解析；
      **且** `adr_ref` / `matrix_ref` 能解析到真实文件（裸 ID 如 `ADR-001` 按同目录文件名前缀匹配）。
      - 为什么：同 G-A4，悬挂引用等于伪溯源。
      - 注：`adr_ref` 存在性已由人工自查改为机检；schema 仍强制必填（范围倒逼，见 `_private/CRITERIA.md` §3.3）。
- [ ] **G-B5 · 技术层不越位**：`TEC-` id 只出现在 `standards_refs`；
      `context` / `title` / `responsibility` / `interface` / `info_hidden` / `contract` 等叙述位无 `TEC-` id。
      - 为什么：技术层是选型标尺，不得进入叙述/推荐位。

> 机检不覆盖的残余（人工自查）：`adr_ref` 内容一致性（存在性已机检）；`sources[]` 编号可否解析到 canonical 信源。

**门控不覆盖项的显式声明（`0926` 批）**

- **门控 PASS 只证契约合规**，⛔ **不证语义与价值**。
- ADR／边界类产件须补验四类**语义项**并在件内**显式声明门控不覆盖项**：① 引用图谱节点的**节点名语义归属**（id 存在 ≠ 归属正确）；② 备选方案的**取舍理由与量级**是否成立；③ 场景**可度量性**的度量口径是否真能测（而非仅「写了字段」）；④ 与上游需求／约束的**一致性**。
- **接口加严的影响面是「跨任务共享件」**：改必填/加严校验前须做**跨任务消费方普查**，变更须带**跨任务通告位**。

## 四、备注

- 负向测试由门控脚本自检：**11/11 判据各有负向样本**，覆盖由自检**自动断言**（缺一即 FAIL）；
  逐条样本矩阵见 `_private/CRITERIA.md` §2。
- 判据治理原则：优先换判据而非放宽阈值；连续谱度量只报告不判 FAIL；门控脚本自身也要门控。
- **降级裁决为预登记事项**（见 `_private/CRITERIA.md` §3.2）：默认**不降级任何判据**；降级须以
  `--ledger-report` 的真实分布 + 判据可证伪性分析为依据，不得凭"通过率高"直觉下调。
