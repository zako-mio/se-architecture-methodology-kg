# 阶段2 联网搜索 + 深度分析计划书

> 母任务：建立「软件工程 / 架构设计方法论」知识库（母库）
> 本文件：阶段2 执行计划（可直接驱动阶段3 派单）
> 生成日期：2026-09-10　依据：`00-plan/contract.md`、`02-research/A|B|C|E`、`01-books/D`
> 命名扩展：沿用契约 `{字母}-{主题}` 规范，阶段2/3 证据包续用字母 F–O（A–E 已占用）

---

## 1. 目标与范围

**阶段2/3 要产出什么**

- **未整理知识（原始证据包 + 结构化知识）**：按生命周期主题域，将 S1 标准 / S2 经典 / S3 官方架构中心 / S4 论文中的知识，从"权威源"转化为"可溯源、可复核、可重组"的结构化条目（定义 / 原理 / 机制 / 工程 / 权衡五段式）。
- **知识源结构（源结构清单）**：一张信源分级总表 + 主题域→信源→产物映射矩阵，供阶段4 架构设计直接消费。
- **落盘位置**：`MISSION_ROOT/02-research/`（证据包 JSON + 摘要 MD）、`MISSION_ROOT/03-knowledge-map/`（信源分级总表、主题映射矩阵）、`MISSION_ROOT/01-books/`（书籍获取日志）。

**明确不做什么**

- 不建库（不写生成脚本、不注入 DAG 数据、不产出 HTML/MD 交付物）——那是阶段4+。
- 不做最终架构设计（不收敛母库的信息架构/分层/导航）——阶段4 才做。
- 不下载、不镜像任何书籍/标准正文；书本体只入本地语料层，公开目录永不承载（契约 §5 版权红线）。

---

## 2. 搜索主轴 = 生命周期阶段（10 个主题域）

主线取自 ISO/IEC/IEEE 12207 的过程视角与 `A-se-definition` 的阶段示例（concept→development→production→utilization→support→retirement），按工程实践重构为 10 域（F–O）。

> **ISO 版本一律以 `E-iso-standards` 为准**：42010:2022（2011 已撤销）、12207:2026（2017 已撤销，2026 scope 暂无快照）、25010:2023（九特性，2011 已撤销）、14764:2022、24765:2017（修订中）。iso.org 已实测 403，**不再重试**，标准元数据走 Wayback 快照 + committee.iso.org + iso25000.com（`iso-access-notes.md`）。

### F · 概念与需求（concept & requirements）— 证据包 `F-requirements.*`

- **目标问题**：软件工程权威定义；软件危机/本质复杂度的现代解读；需求工程过程；干系人识别；质量属性需求（QA scenario）如何从业务驱动推导。
- **Query 策略**：`software engineering definition IEEE 610.12`、`SWEBOK V4 knowledge areas`、`software requirements engineering process ISO 29148`、`quality attribute scenarios SEI`、`stakeholder identification requirements`；中文 `软件工程 定义 需求工程 质量属性需求`。
- **权威源限定**：SWEBOK V3/V4、ISO/IEC/IEEE 29148（需求工程，另核版本）、ISO/IEC/IEEE 12207:2026、SEI、Brooks《No Silver Bullet》。
- **信源优先级**：S1 > S2 > S4 > S3。
- **预期产物**：术语定义表（≥12 条，每条 source_id）、需求工程过程图（文字化）、QA scenario 模板、gaps。

### G · 架构设计（architecture design）— `G-architecture.*`

- **目标问题**：架构定义的权威口径；架构↔设计↔需求边界；视图/视角；架构风格与模式；架构决策（ADR）；架构文档化；架构权衡（ATAM）。
- **Query 策略**：`ISO 42010 architecture description 2022 scope`、`SEI architecture definition ATAM`、`software architecture styles Garlan Shaw`、`architecture decision record Nygard`、`architecture tradeoff analysis method`；中文 `软件架构 定义 架构决策 权衡`。
- **权威源限定**：ISO/IEC/IEEE 42010:2022、SWEBOK V4 架构 KA、SEI（定义/ATAM/Views and Beyond）、martinfowler.com、Azure Architecture Center。
- **信源优先级**：S1 > S2 > S3 > S4。
- **预期产物**：架构定义多源对照表、风格清单（含每风格权衡）、ADR 模板、ATAM 术语（sensitivity/tradeoff points）、gaps。

### H · 实现（implementation）— `H-implementation.*`

- **目标问题**：模块化与信息隐藏；内聚/耦合度量；整洁代码与可读性；设计模式（GoF）与反模式；深/浅模块与抽象。
- **Query 策略**：`Parnas 1972 information hiding`、`coupling cohesion software metrics`、`design patterns GoF classification`、`deep modules philosophy of software design`、`code smells catalog`；中文 `模块化 信息隐藏 内聚 耦合 设计模式`。
- **权威源限定**：Parnas(1972)、SWEBOK 设计/构造 KA、martinfowler.com（bliki）、Ousterhout 官方书页、refactoring.guru（仅作线索，不作为 S 级源）。
- **信源优先级**：S1 > S2 > S3 > S4。
- **预期产物**：原则↔反例配对表（如 information hiding ↔ fragile base class）、模式速查（来源标注）、gaps。

### I · 测试（testing）— `I-testing.*`

- **目标问题**：测试层次（单元/集成/系统/验收）；测试驱动开发；质量门控与 CI 检查；可测试性设计；测试金字塔/大量原则。
- **Query 策略**：`software testing levels IEEE 829`、`test pyramid Fowler`、`test-driven development Kent Beck`、`testability quality attribute`、`continuous integration quality gates`；中文 `测试层次 测试金字塔 可测试性 质量门控`。
- **权威源限定**：SWEBOK 测试 KA、ISO/IEC/IEEE 29119（另核版本）、martinfowler.com、Google Testing Blog、SRE/Accelerate（DORA 指标）。
- **信源优先级**：S1 > S2 > S3 > S4。
- **预期产物**：测试层次对照表、可测试性战术清单、质量门控清单、gaps。

### J · 部署（deployment）— `J-deployment.*`

- **目标问题**：构建-发布-运行分离；制品与配置管理；不可变基础设施；部署策略（蓝绿/金丝雀/滚动）；环境一致性。
- **Query 策略**：`build release run separation`、`immutable infrastructure definition`、`blue green vs canary deployment`、`twelve-factor app config`、`continuous delivery deployment pipeline`；中文 `不可变基础设施 部署策略 蓝绿 金丝雀 十二要素`。
- **权威源限定**：12factor.net（本地已有 12factor.epub 可交叉核验，C-local-inventory BK-01）、Humble & Farley《Continuous Delivery》、HashiCorp/CNCF 官方文档、Google Cloud/AWS 部署白皮书。
- **信源优先级**：S1 > S2 > S3 > S4。
- **预期产物**：部署策略对比表（含权衡）、配置/制品管理原则、gaps。

### K · 运维（operations）— `K-operations.*`

- **目标问题**：可靠性与容错（反模式/断路器/舱壁）；可观测性（日志/指标/追踪）；SLI/SLO/错误预算；事件响应与复盘；容量与变更管理。
- **Query 策略**：`site reliability engineering SLI SLO error budget`、`release it stability anti-patterns`、`observability three pillars`、`incident response postmortem blameless`、`chaos engineering principles`；中文 `可靠性 可观测性 SRE 事件响应`。
- **权威源限定**：sre.google（SRE Book/Workbook，**直连超时，走代理 172.29.0.1:7890**）、Nygard《Release It!》、Google SRE 官方、CNCF/OpenTelemetry 官方。
- **信源优先级**：S1 > S2 > S3 > S4。
- **预期产物**：可靠性战术清单、SLI/SLO 定义模板、可观测性信号表、gaps。

### L · 演化 / 弃用（evolution & deprecation）— `L-evolution.*`

- **目标问题**：重构（Fowler 手法目录）；技术债；架构腐化/漂移；演进式架构与 fitness function；遗留系统改造；弃用策略（deprecation/sunset）。
- **Query 策略**：`refactoring catalog Fowler 2nd`、`technical debt metaphor Cunningham`、`architecture erosion drift systematic mapping`、`evolutionary architecture fitness functions`、`legacy code seams Feathers`、`software deprecation sunset policy`；中文 `重构 技术债 架构腐化 演进式架构 遗留系统 弃用`。
- **权威源限定**：martinfowler.com/refactoring、Cunningham OOPSLA'92、Li et al.(2022) 系统映射（B 包已引）、Ford et al.《Building Evolutionary Architectures》、Feathers、Lehman 演化定律。
- **信源优先级**：S2 ≈ S1 > S4 > S3。
- **预期产物**：演化机制表（重构/技术债/腐化/演进/弃用各自"信号→手段→权衡"）、fitness function 类型清单、gaps。

### M · 横切：质量模型与 ilities — `M-quality-ility.*`

- **目标问题**：ISO 25010:2023 九特性；可维护性/可修改性/可复用性/可测试性子特性；可扩展性/可演化性的术语落点（A/B 包已证无标准顶层术语）；质量属性到战术的映射。
- **Query 策略**：`ISO 25010 2023 product quality model nine characteristics`、`ISO 25002 SQuaRE overview`、`maintainability subcharacteristics`、`extensibility vs evolvability definition`、`quality attribute tactics SEI`；中文 `质量模型 可维护性 可扩展性 可演化性`。
- **权威源限定**：ISO/IEC 25010:2023、ISO/IEC 25002:2024、ISO/IEC 25019:2023、iso25000.com、SEI quality attribute tactics。
- **信源优先级**：S1 > S4 > S2 > S3。
- **预期产物**：九特性表（中英+定义+source）、ility 术语归位表（标准术语 vs 工程口语）、质量→战术映射、gaps。

### N · 团队与康威定律（teams & Conway）— `N-team-conway.*`

- **目标问题**：康威定律及其逆向操作（Inverse Conway Maneuver）；团队拓扑（stream-aligned/enabling/complicated-subsystem/platform）；松散耦合的团队边界；DORA 效能指标。
- **Query 策略**：`Conway's law inverse Conway maneuver`、`team topologies four fundamental types`、`DORA four key metrics`、`microservices team autonomy`；中文 `康威定律 团队拓扑 逆向康威 交付效能`。
- **权威源限定**：Melvin Conway 原文、Team Topologies 官网、Accelerate/DORA 官方报告、 martinfowler.com。
- **信源优先级**：S2 > S1 > S3 > S4。
- **预期产物**：康威定律表述+推论、团队类型表、团队边界与架构耦合的对应关系、gaps。

### O · 方法论主干（取舍与工程原则综合）— `O-methodology.*`

- **目标问题**：将 F–N 的"权衡点"统一到母库主干框架——复用 `KG-04 0813-知识库建库工程` 的「**架构权衡思维 11 维**」（每维：有什么可权衡 / 如何权衡 / 为何如此权衡 / 你的场景，C-local-inventory §3.2）；提炼跨域工程原则与反例。
- **Query 策略**：不新增领域检索；对 F–N 证据包做二次归纳，必要时回源补 `trade-off` / `quality attribute` 关键节点。
- **权威源限定**：以 F–N 的 source_id 为准，不引入新源。
- **信源优先级**：继承上游。
- **预期产物**：11 维权衡骨架填充版、跨域原则↔反例总表、术语一致性裁决记录。

---

## 3. 并行委派方案

**波次编排（每波 5–8 个并行子Agent，波间读盘核验）**

- **Wave A（6 个）**：F 需求 / G 架构 / H 实现 / I 测试 / J 部署 / K 运维。同时 1 个 **书籍获取 Agent**（free-official 直取，见 §5）。
- **Wave B（5 个）**：L 演化 / M 质量 / N 团队 / O 方法论 / + **书籍解析 Agent**（pdf-worker / pdf-ocr 处理用户提供的本地副本，见 §5）。

**契约先行**：本计划书即 P0 契约。开波前主Agent 将各域任务写为独立子Agent prompt，引用 `contract.md` + `06-gates-cascade.md` 短路径，**禁止内联全文**（kb-construction C01/C21）。

**子Agent 落盘纪律**（kb-construction C18–C20）

- 先落盘再返回：每个子Agent 必须在 `02-research/` 写出 `{字母}-{主题}.json` 与 `.json` 对应的 `.md` 摘要（300–800 字），返回文本仅作索引。
- 文件命名唯一：按字母+主题，禁止多 Agent 写同名文件（C19）。
- 落盘 schema 严格遵循 `contract.md §4.1/4.2`；每条 finding 必须带 `source_ids`，无源不写。
- 子Agent 只写 `02-research/`，**不得写 `03-knowledge-map/` 与公开交付目录**（该层由主Agent 聚合）。

**主Agent 聚合校验**（不信返回文本，只信磁盘）

1. 逐文件 `read` 核对：`sources[].url` 非空、`tier` ∈ {S1..S4}、`definitions[].source_id` 可解析、`verified` 已标注。
2. 跨包一致性：同术语（如 maintainability / architecture / technical debt）定义在 F/G/L/M 间是否冲突，冲突交 O 裁决。
3. 缺口回填：`gaps` 汇总，能本轮补的立即回源，不能的进入源结构清单"待补"区。
4. 交付 `03-knowledge-map/sources-index.md`（分级总表）+ `topic-source-matrix.md`（域→源→产物矩阵）。

---

## 4. 深度分析流程（原文 → 结构化知识）

**五段式结构化模板**（每个知识点）

| 段 | 内容 | 判定标准 |
|---|---|---|
| 定义 | 权威原句/标准定义 + source_id | 与至少 1 个 S1 或 2 个独立 S2 一致 |
| 原理 | 为何成立（动机/理论根基） | 可追溯到一手源 |
| 机制 | 如何运作（过程/结构/规则） | 可操作、可复述 |
| 工程 | 落地手段/模式/工具 | 附权威实践来源 |
| 权衡 | 代价/边界/适用场景 | 至少 1 条反例或限制 |

**信源分级与交叉验证**（`contract.md §3/§6`）

- S1/S2 为主，S3/S4 补充；禁止无出处二手博客、AI 内容、营销软文。
- **≥2 独立源交叉验证**：高危数据（标准版本号、定义原句、量化指标）强制回源核对；无法核验写入 `gaps`，不伪装成事实。
- 一手源（标准 scope 原文、官方页、作者原文）优先于二手转述。

**勘误规范**

- 主动勘误而非照抄：如发现"常见误记 vs 核实值"（参考 01-books 的版本时效勘误表），在 JSON 增加 `errata[]` 字段（误记/核实值/依据）。
- 版本类结论一律标注 access date + 快照时间（参考 E 包做法）。

---

## 5. 书籍获取落地计划（版权红线优先）

**5.1 free-official（阶段2 直取清单，可公开引用链接，不镜像正文）**

| 书 | URL | 获取方式 |
|---|---|---|
| Software Engineering at Google | https://abseil.io/resources/swe-book | 在线 HTML 章节按需读取、提取论点 |
| Google SRE Book | https://sre.google/sre-book/table-of-contents/ | 直连超时，**走代理** `curl -x http://172.29.0.1:7890` 或 browser |
| SRE Workbook | https://sre.google/workbook/table-of-contents/ | 同上 |
| DDD Reference (Evans) | https://domainlanguage.com/ddd/reference/ | 官方 PDF 术语速查，直取 |
| The Twelve-Factor App | https://12factor.net/ | 直取；与本地 `12factor.epub` 交叉核验（BK-01） |

**5.2 paid / user-copy（缺口清单，交用户提供本地副本）**

- `paid`（35 本候选中的 30 本，见 `D-book-candidates.json`）：Clean Architecture、APoSD、SAiP 4e、Fundamentals 2e、PoEAA、DDD(Evans)、Clean Code、Refactoring 2e、WELC、DDIA 2e、DevOps Handbook 2e、Accelerate、GoF、Mythical Man-Month 等。
- 阶段2 仅提取**目录 / 公开章节 / 官方摘要**用于知识结构；**实体全文待用户提供合法本地副本**。
- 主Agent 汇总一份 `01-books/gap-request.md`（缺口清单+优先级），一次性请求用户提供。

**5.3 解析管线**

- 用户提供副本后 → `pdf-worker`（有文本层）或 `pdf-ocr`（扫描件）解析 → 摘要落 `02-research/`，**原文只入本地语料层，不进公开仓库**。

---

## 6. 产物清单 + 门控映射

**阶段3 产物**

| 产物 | 路径 | 说明 |
|---|---|---|
| 证据包 JSON×10 | `02-research/{F..O}-*.json` | 遵循契约 schema |
| 摘要 MD×10 | `02-research/{F..O}-*.md` | 300–800 字中文 |
| 信源分级总表 | `03-knowledge-map/sources-index.md` | 域→源→tier→verified |
| 主题源结构矩阵 | `03-knowledge-map/topic-source-matrix.md` | 生命周期域×信源×产物 |
| 术语总表 | `03-knowledge-map/glossary.md` | 定义+source_id，跨域去重 |
| 书籍获取日志 | `01-books/fetch-log.md` + `gap-request.md` | 直取结果 + 缺口请求 |

**kb-construction L1–L7 门控映射**

| 层 | 查什么 | 本阶段落点 |
|---|---|---|
| L1 生成时自验证 | schema 合法/关键样例 | 子Agent 自测 JSON 可解析 |
| L2 全量审计 | 字段完整性/命名归一/跨产物一致 | 全部 JSON 字段非空、命名统一 |
| L3 结构层 | 编码纯净/断链/空文件 | UTF-8 无乱码字符、URL 可解析、无空文件 |
| L6 覆盖度层 | 产物清单逐项核对 | 10 域全部产出，缺一即扣（回放覆盖度 ≥90%） |
| L7 信源层 | verified/证据区块/交叉验证 | 每条 finding 有 source_ids、可溯源率 ≥95% |
| L4/L5 | 视觉/渲染 | **本阶段不启用**（无图无渲染），显式记录 skipped≠PASS |

**方法论专项门控**

1. **定义准确性交叉验证**：核心术语（software engineering / architecture / maintainability / technical debt）必须 ≥2 独立源一致；不一致处标 `disputed` 并说明分歧。
2. **术语一致性**：`glossary.md` 为唯一裁决表，同一术语跨域不得出现相互冲突定义。
3. **原则↔反例配对完整性**：每条工程原则必须配 ≥1 反例或失败模式（如 DRY↔over-abstraction、微服务↔分布式复杂度）。

---

## 7. 风险与依赖

| 风险 | 影响 | 对策 |
|---|---|---|
| iso.org 403（WAF） | 标准正文不可达 | 已实测：**不再重试**，走 Wayback 快照 + committee.iso.org + iso25000.com（`iso-access-notes.md`） |
| 境外源直连超时（sre.google 等） | 采集失败 | 走代理 `curl -x http://172.29.0.1:7890` 或 browser-harness；国内源直连 |
| 12207:2026 scope 无快照 | 时效结论降级 | 标 medium，标注"定稿 scope 待补"，不伪装 high |
| 书籍版权 | 违规风险 | 严守红线：只入本地语料层，公开库只放消化重组知识 |
| 搜索广度 vs 预算 | 成本失控 | 每域 query 上限（≤8 主查询 + ≤6 补查）；每波前读盘、不重复检索；子Agent 优先国内源直连 |
| 长 prompt 子Agent JSON 截断 | 返回不完整 | 契约外置文件 + prompt 引用短路径（C01/C21）；先落盘再返回 |

**依赖**：用户提供 `paid` 书籍本地副本（可与阶段2 并行，不阻塞联网部分）；`ISO/IEC/IEEE 29148/29119` 版本需在 F/I 域另行核实（E 包未覆盖）。

---

## 8. 复杂度自评

`[COMPLEXITY: 16/20]` → **Deep**

- 影响范围 4（多文件/多域，10 证据包 + 3 总表）；逻辑深度 4（方法论文本结构化与权衡综合）；操作数量 4（10 域检索 + 聚合校验）；风险精度 4（信源可溯源、需交叉验证）。
- 阶段2/3 判定：**Deep variant**（≥13），max_tokens 16384、reasoning_effort max；阶段4（建库与架构设计）预计仍为 Deep。
