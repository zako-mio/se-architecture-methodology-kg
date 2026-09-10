# 主题—信源矩阵（Topic × Source Matrix）

> 母任务：0910-软件工程架构方法论 · 阶段2/3 交付物（`03-knowledge-map/`）
> 生成日期：2026-09-10　契约：`00-plan/contract.md`　依据：`03-knowledge-map/knowledge-map.json`（阶段1，117 条）+ `02-research/F..R-*.json`（阶段2，12 包 / 208 条计数）
> 用途：给出「生命周期域 → 主用信源 → 证据包文件 → 产出形态」的映射，供阶段4 建库的信息架构与检索消费。
> **ID 约定**：阶段1 用全局 ID（`S1-STD-*` 等），阶段2 用 `包/局部 ID`（如 `F/S1-F01`）；跨包裸 ID 会碰撞，详见 `sources-index.md` §1–§2。

---

## 1. 矩阵主表

| 生命周期域 | 主用信源 ID（阶段2 包限 / 阶段1 全局） | 对应证据包文件 | 产出形态（阶段2 实际产物） |
|---|---|---|---|
| **① 概念与需求** | `F/S1-F01` `F/S1-F02` `F/S1-F03` `F/S1-F04` `F/S1-F05` `F/S1-F06` `F/S1-F07` `F/S1-F08` `F/S2-F01` `F/S4-F01` `F/S4-F02` `F/S3-F01` `F/S3-F02` `F/S1-A01` `F/S1-07` `F/S1-03` `F/S4-04`；R：`R/S4-PAP-01` `R/S4-PAP-04` `R/S4-PAP-05` `R/S1-OFF-01` `R/R-XC-03` `R/R-XC-05` `R/R-XC-07`；阶段1：`S1-OFF-01` `S1-OFF-03` `S1-OFF-04` `S1-OFF-06` `S1-OFF-07` `S2-BK-02` `S2-BK-04` `S4-PAP-01` `S4-PAP-04` `S4-PAP-05` | `02-research/F-requirements.json`（+ `R-foundational-papers.json` + A/E 复用） | definitions×16 / findings×14 / gaps×8 + R（概念子集 7 源）：术语定义表（SWEBOK 需求定义、干系人、本质/偶然复杂度）、ISO 29148 需求过程链（BRS/StRS/SyRS/SRS）、QA scenario 六要素模板、软件危机现代审计；R 补 Brooks 本质/偶然复杂度原文四要素、Royce 迭代原意、Parnas「SE≠CS」、SWEBOK V4 KA 清单 |
| **② 架构设计** | `G/S1-01` `G/S1-02` `G/S1-03` `G/S1-04` `G/S1-05` `G/S1-07` `G/S1-08` `G/S1-09` `G/S1-10` `G/S1-11` `G/S1-12` `G/S2-09` `G/S2-10` `G/S2-14` `G/S2-18` `G/S2-19` `G/S3-02`；阶段1：`S1-STD-01` `S1-STD-02` `S1-OFF-02` `S3-VEN-01` `S2-BK-07`–`S2-BK-19` `S2-BK-32`–`S2-BK-35` `S2-WEB-01` `S2-WEB-03`–`S2-WEB-10` `S4-PAP-07`；Q：`Q/S3-VEN-02` `Q/S3-VEN-03` `Q/S3-VEN-04` `Q/S3-VEN-05` `Q/S3-VEN-06` `Q/S3-VEN-07` `Q/S3-VEN-08`；R：`R/S2-BK-16` `R/R-XC-04` | `02-research/G-architecture.json`（+ `Q-vendor-architecture.json` + `R-foundational-papers.json`） | definitions×21 / findings×34 / gaps×8 + Q×18 / findings×12 + R：架构定义多源对照表（42010 / SEI / Perry&Wolf / Kruchten）、架构风格清单（含权衡）、ADR 模板、ATAM 术语（sensitivity/tradeoff/risk）；Q 补 AWS/GCP Well-Architected 支柱与设计原则、Thoughtworks Technology Radar 四环四象限采用机制；R 补 POSA Vol.1 模式目录与 Microkernel 定义 |
| **③ 实现与构造** | `H/S1-01` `H/S1-02` `H/S2-01`–`H/S2-11` `H/S3-01` `H/S3-02` `H/S4-01`–`H/S4-03`；阶段1：`S2-BK-03` `S2-BK-05` `S2-BK-20` `S2-BK-21` `S2-BK-22` `S2-BK-32` `S2-BK-33` `S2-WEB-02` | `02-research/H-implementation.json` | definitions×20 / findings×27 / gaps×8：原则↔反例配对表（information hiding↔fragile base class、DRY↔过度抽象、YAGNI）、内聚/耦合度量（CK 套件）、GoF 模式速查与反模式、Code Smell 目录 |
| **④ 测试** | `I/S1-STD-11`–`I/S1-STD-20` `I/S1-OFF-05` `I/S1-OFF-09`–`I/S1-OFF-14` `I/S2-WEB-12`–`I/S2-WEB-19` `I/S2-BK-01` `I/S2-BK-09` `I/S2-BK-28` `I/S2-BK-29` `I/S2-BK-30` `I/S3-VEN-02`–`I/S3-VEN-04` | `02-research/I-testing.json` | definitions×15 / findings×19 / gaps×7：测试层次对照表、测试金字塔与反模式、可测试性战术、质量门控与 CI 检查清单、ISTQB/29119 标准族映射 |
| **⑤ 部署** | `J/S2-01`–`J/S2-07` `J/S3-01`–`J/S3-05` `J/BK-01`；阶段1：`S2-BK-24` `S2-BK-27` `S2-BK-28` `S2-BK-31` `S1-STD-03` | `02-research/J-deployment.json` | definitions×17 / findings×22 / gaps×8：部署策略对比表（蓝绿 / 金丝雀 / 滚动 / 凤凰）、不可变基础设施、构建-发布-运行分离、制品与配置管理（12-Factor）、部署流水线 |
| **⑥ 运维** | `K/S2-01`–`K/S2-06` `K/S3-01`–`K/S3-06`；阶段1：`S2-BK-24` `S2-BK-25` `S2-BK-26` `S2-BK-27` `S1-STD-07` `S4-PAP-03` | `02-research/K-operations.json` | definitions×19 / findings×23 / gaps×9：可靠性战术清单（断路器 / 舱壁 / 重试退避 / 混沌）、SLI/SLO/错误预算模板、可观测性三支柱信号表、无指责复盘、可靠性目标（Azure WA） |
| **⑦ 演化与弃用** | `L/S1-01`–`L/S1-03` `L/S2-01`–`L/S2-13` `L/S3-01`–`L/S3-05` `L/S4-01`–`L/S4-03`；R：`R/S4-PAP-03` `R/R-XC-01` `R/R-XC-02`；阶段1：`S1-STD-07` `S1-STD-08` `S4-PAP-01` `S4-PAP-03` `S4-PAP-08` `S2-BK-01` `S2-BK-11` `S2-BK-21` `S2-BK-22` `S2-WEB-02` | `02-research/L-evolution.json`（+ `R-foundational-papers.json`；技术债管理层见 ⑨ `P-techdebt.json`） | definitions×16 / findings×22 / gaps×8 + R：演化机制表（重构 / 技术债 / 腐化 / 演进 / 弃用的信号→手段→权衡）、fitness function 类型清单、Strangler Fig、弃用头（RFC 8594/9745）与语义化版本；R 补 Lehman 演化定律原文（1980 实为 5 条，1996 首次成文八条）、S/P/E 程序分类 |
| **⑧ 横切·质量属性** | `M/S1-M01`–`M/S1-M08` `M/S2-M01` `M/S2-M02` `M/S4-M01`–`M/S4-M03` `F/S2-F01`；阶段1：`S1-STD-05` `S1-STD-06` `S1-OFF-02` `S1-OFF-05` `S2-BK-09` `S2-BK-10` `S2-BK-14` `S2-WEB-11` `S4-PAP-08` | `02-research/M-quality-ility.json`（+ `F-requirements.json`） | definitions×25 / findings×13 / gaps×6：ISO 25010:2023 九特性表、ility 术语归位表（标准术语 vs 工程口语）、质量属性→战术映射（可修改性 / 可用性 / 可扩展性）、SQuaRE 25002/25019 |
| **⑨ 横切·技术债** | `P/P-S1-01` `P/P-S1-02` `P/P-S2-01`–`P/P-S2-10` `P/P-S3-01`–`P/P-S3-03` `P/P-S4-01`–`P/P-S4-12`；`L/S2-01` `L/S2-02` `L/S2-03` `L/S2-06` `L/S4-01` `L/S4-03` `H/S2-03`；阶段1：`S2-WEB-01` `S2-WEB-02` `S2-BK-01` `S2-BK-08` `S2-BK-21` `S2-BK-22` `S4-PAP-06` `S4-PAP-08` | `02-research/P-techdebt.json`（独立证据包；交叉引用 `L-evolution.json`、`H-implementation.json`） | definitions×15 / findings×24 / gaps×8：技术债隐喻（Cunningham）、技术债象限（Fowler 四象限 deliberate/inadvertent × prudent/reckless）、principal/interest、从隐喻到理论（Kruchten）、SQALE 方法与 TDR/SonarQube 度量、code smell、架构腐化（erosion/drift）与架构技术债、SATD、TDM 与优先级排序、需求技术债 |
| **⑩ 团队与康威定律** | `N/S2-01`–`N/S2-06` `N/S3-01`–`N/S3-05` `N/S4-01` `N/S4-02`；阶段1：`S2-BK-30` | `02-research/N-team-conway.json` | definitions×22 / findings×21 / gaps×6：Conway 定律原文与镜像假说、团队拓扑四类型×三交互、逆向康威、DORA 交付绩效指标、组织—架构对齐 |

---

## 2. 覆盖度自检

| 域 | 独立证据包 | 阶段1 theme 源数 | 阶段2 包 `sources[]` | findings 数 | 是否 ≥1 包 | 是否 ≥5 源 | 薄弱标记 |
|---|---|:--:|:--:|:--:|:--:|:--:|---|
| ① 概念与需求 | `F-requirements.json`（+ R 概念子集） | 15 | 17（+R 7） | 14 | ✅ | ✅（39） | — |
| ② 架构设计 | `G-architecture.json`（+ Q） | 39 | 17（+Q 7） | 34（+Q 12） | ✅ | ✅（63） | — |
| ③ 实现与构造 | `H-implementation.json` | 17 | 18 | 27 | ✅ | ✅（35） | — |
| ④ 测试 | `I-testing.json` | 7 | 33 | 19 | ✅ | ✅（40） | —（阶段1 GAP-12 已由 I 包 33 源补足） |
| ⑤ 部署 | `J-deployment.json` | 7 | 13 | 22 | ✅ | ✅（20） | — |
| ⑥ 运维 | `K-operations.json` | 8 | 12 | 23 | ✅ | ✅（20） | — |
| ⑦ 演化与弃用 | `L-evolution.json`（+ R 演化子集） | 13 | 24（+R 3） | 22 | ✅ | ✅（40） | — |
| ⑧ 横切·质量属性 | `M-quality-ility.json`（+F） | 9 | 13 | 13 | ✅ | ✅（22） | — |
| ⑨ 横切·技术债 | `P-techdebt.json`（独立；+L/H 交叉） | 8 | 27 | 24 | ✅ | ✅（35） | ✅ **已补独立证据包（P），原缺口消除** |
| ⑩ 团队与康威定律 | `N-team-conway.json`（已有 N 包） | 0（阶段1 无独立 theme） | 13 | 21 | ✅ | ✅（13） | ⚠️ 轻微：阶段1 无 theme，主要靠阶段2 N 包 |

> 计数口径：**阶段1 theme 源数** 取自 `knowledge-map.json` 的 `themes[].sources` 长度（精确值：15/39/17/7/7/8/13/9/8，无团队 theme）；**阶段2 包 sources** 与 **findings** 取自各 `02-research/{F..R}-*.json` 的 `sources[]`/`findings[]` 长度（精确值，见 `sources-index.md` §0）；括号内合计 = 阶段1 + 阶段2，**含两阶段重复引用未去重**（跨包复用映射见 `sources-index.md` §2）。
> **包—域归属**：P 全量（27 源 / 24 findings）归 ⑨ 技术债；Q 全量（7 源 / 12 findings）归 ② 架构设计；R（14 源 / 12 findings）为跨域奠基文献，按主题拆分至 ①（概念，7 源）、②（架构，2 源：POSA/Microkernel）、⑦（演化，3 源：Lehman）、③（实现，1 源：Parnas 1972 复用）等，故包总数 208 = 阶段2 12 包 `sources[]` 计数之和，而域内 sources 合计小于等于该值。R/R-XC-* 为交叉验证条目，findings 不重复计入多个域。

### 薄弱域与缺口说明

1. **⑨ 横切·技术债（已补独立证据包，原缺口消除）**：新增 `P-techdebt.json`（27 源 / 24 findings），覆盖技术债隐喻与四象限、principal/interest、SQALE 方法与 TDR/SonarQube 度量、code smell、架构侵蚀/漂移与架构技术债、SATD、TDM 与优先级排序、需求技术债。与 `L-evolution.json`（`L/S2-01/02/03`、`L/S4-01`、`L/S4-03`）及 `H-implementation.json`（`H/S2-03`）交叉引用（去重映射见 `sources-index.md` §2）。
2. **⑩ 团队与康威定律（轻微薄弱，当前唯一剩余薄弱域）**：阶段1 无独立 theme，仅 `S2-BK-30`（Team Topologies）1 条相关源（且被归入阶段1「概念与需求」theme）；阶段2 N 包补 13 条后达标。镜像假说实证（`N/S4-01` `N/S4-02`）为 2012/2016 论文，时效性需在阶段4 回查更新研究。
3. **剩余薄弱域结论**：除 ⑩ 团队域因「阶段1 无独立 theme」仍标轻微外，①–⑨ 均已具备 ≥1 独立证据包且 ≥5 源。Q 包补强架构设计域的厂商权威口径（AWS/GCP Well-Architected、Thoughtworks Radar）；R 包补强概念与演化域的奠基文献原始出处（Brooks 本质/偶然、Royce 迭代原意、Lehman 演化定律、Parnas、POSA）。
4. **O 域（方法论主干/跨域综合）已落盘**：`02-research/O-methodology.json` **已存在**（11 维权衡骨架、跨域原则↔反例总表、术语一致性裁决记录，`gaps`×10；`sources` 长度为 0），故不计入信源数与「12 个含 `sources[]` 的证据包」。本矩阵原「O 域未落盘」缺口消除。
5. **术语一致性裁决**：`03-knowledge-map/glossary.md` 已产出为跨域唯一裁决表，并按 P/Q/R 新增术语（technical debt quadrant、principal & interest、SQALE、technical debt ratio、architecture erosion/drift、essence vs accident、E-type system、well-architected pillar、adopt/trial/assess/caution、strangler fig、boy-scout rule 等）级联更新。

---

## 3. 与阶段1 主题域的对照（阶段1 themes → 阶段2 域）

| 阶段1 theme（`knowledge-map.json`） | 阶段1 源数 | 阶段2 对应域 / 证据包 | 变化 |
|---|:--:|---|---|
| 1. 概念与需求 | 15 | ① 概念与需求 / `F-requirements.json` | 阶段2 新增 SWEBOK V4 KA1、ISO 29148、干系人、QA scenario |
| 2. 架构设计 | 39 | ② 架构设计 / `G-architecture.json` | 补 42010:2022 概念模型、SEI ATAM TR、Azure 风格 |
| 3. 实现与构造 | 17 | ③ 实现与构造 / `H-implementation.json` | 补 Parnas/APoSD/CK 度量/GoF 反模式 |
| 4. 测试 | 7 | ④ 测试 / `I-testing.json` | **大幅补强**：+ISO/IEC/IEEE 29119 全族、ISTQB、DORA、质量门控 |
| 5. 部署 | 7 | ⑤ 部署 / `J-deployment.json` | 补部署策略、不可变基础设施、K8s、CNCF |
| 6. 运维 | 8 | ⑥ 运维 / `K-operations.json` | 补混沌工程、无指责复盘、OpenTelemetry |
| 7. 演化与弃用 | 13 | ⑦ 演化与弃用 / `L-evolution.json` | 补 RFC 8594/9745、semver、Kruchten、Strangler Fig |
| 横切·质量属性 | 9 | ⑧ 横切·质量属性 / `M-quality-ility.json` | 补 SQuaRE 25002/25019、SEI 战术 TR、extensibility/evolvability 综述 |
| 横切·技术债 | 8 | ⑨ 横切·技术债 / `P-techdebt.json` | **已独立成包**：补 SQALE/TDR、技术债象限、架构技术债、SATD、TDM |
| （阶段1 无独立"团队"theme） | — | ⑩ 团队与康威 / `N-team-conway.json` | 阶段2 新增域：Conway 原文、团队拓扑、镜像假说、DORA |

> P/Q/R 三包不新增阶段1 theme：P 归属既有「横切·技术债」域，Q 归属「架构设计」域（+质量属性横切），R 为跨域奠基文献（概念与需求 / 架构 / 演化）。

---

## 4. 使用须知

- 本矩阵的「产出形态」列描述的是各证据包**已落盘**的 `definitions/findings/gaps` 结构与阶段2 计划书 §2 的预期产物映射，**非阶段4 最终交付物**（阶段4 才做信息架构收敛与建库）。
- 阶段2 局部 ID 引用须带包名（`包/ID`）；跨包复用映射见 `sources-index.md` §2，碰撞与无法映射项见 §5。注意 `Q/S3-VEN-02..08` 与 `I/S3-VEN-02..04` 同名不同源，`R/S4-PAP-*`、`R/S2-BK-16`、`R/S1-OFF-01` 为直接沿用阶段1 全局 ID 的同源复用。
- 技术债域缺口已由 `P-techdebt.json` 补齐，O 域方法论综合已落盘（`O-methodology.json`，无 sources）且术语裁决表 `glossary.md` 已产出；当前唯一剩余薄弱项为 ⑩ 团队域的「阶段1 无独立 theme」（见 §2）。

---

*本矩阵由阶段2 主Agent 聚合生成，数字与 `knowledge-map.json`、`F..R-*.json` 实际计数一致（阶段2 12 包 / 208 条计数：F–N 160 + P 27 + Q 7 + R 14）；未杜撰信源。*
