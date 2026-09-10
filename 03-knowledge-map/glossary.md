# 全局术语表（Glossary）

> 母库「软件工程 / 架构设计方法论」唯一术语裁决表。定义已按 O 域跨域比对裁决为统一口径；状态仅 `settled`（已裁决统一）与 `disputed`（无权威共识，给推荐口径）两种。
> `source_id` 采用「域:包内ID」格式（A–R 对应各证据包），可回溯至 `02-research/{字母}-*.json`；P/Q/R 三包 ID 见 `sources-index.md` §4.10–§4.12（写作 `P:...`/`Q:...`/`R:...`）。凡标注 disputed 者不得当作标准术语引用。

## 0. 总论与学科

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 软件工程 | software engineering | 把系统化、规范化、可量化的方法应用于软件的开发、运行与维护（即把工程应用于软件）；产业口径补充为「跨时间编程 + 团队协作」。 | A:S1-08, A:S1-01, A:S2-02 | settled |
| 软件生命周期过程 | software life cycle process | 把输入转化为输出的、相互关联或相互作用的活动集合；标准定义「过程」而非固定「阶段」，过程可在各阶段反复出现。 | A:S1-02, F:S1-03 | settled |
| 阶段 | stage | 生命周期中与实体描述/实现状态相关的时期，通常以「主决策门」结束；权威示例：concept/development/production/utilization/support/retirement。 | A:S1-03 | settled |
| 软件产品质量 | software product quality | 系统满足干系人显式与隐含需求、从而提供价值的程度；由 25010 九特性及子特性建模。 | A:S1-04, M:S1-M01 | settled |
| 软件危机 | software crisis / gap | 1968 NATO 会议讨论的成本/进度超支、质量低劣、难维护、项目失控现象；与会者对其严重程度意见不一。 | A:S1-07, F:S1-07 | settled |
| 本质复杂度 | essential complexity (essence) | 构成抽象软件实体的复杂概念结构本身固有的复杂度；无法被任何单一技术或管理突破（无银弹）。Brooks 原文四固有属性：complexity / conformity / changeability / invisibility。 | F:S4-04, R:S4-PAP-01, R:R-XC-06 | settled |
| 偶然复杂度 | accidental complexity (accident) | 将抽象实体用程序语言表示并映射到机器语言时受空间/速度约束产生的复杂度；属当下附带、可随技术进步消除的困难（过往高级语言/分时等突破多在此层）。 | F:S4-04, R:S4-PAP-01, R:R-XC-06 | settled |
| 无银弹 | no silver bullet | Brooks 论断：无论技术或管理手段，都不存在单一方法能在十年内使软件生产率、可靠性、简洁性提升一个数量级（十倍）。 | R:S4-PAP-01, R:R-XC-06 | settled |
| 复杂度（认知） | complexity (cognitive) | 使人难以理解与修改系统之物；主要来源为 information（依赖与 obscurity）；设计根本目标是降低 complexity。 | H:S2-02, B:S2-07 | settled |
| 软件演化 | software evolution | 软件在生命周期中随需求与环境变化而持续变化的过程；Lehman 定律指出不持续适配则满意度下降、复杂度递增、质量下降。 | A:S4-01, L:S4-02 | settled |

## 1. 架构

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 架构 | architecture | 系统在其环境中根本性的概念或属性，体现于元素、关系及设计与演化原则；架构是抽象，不是工件。 | A:S1-01, B:S1-01, G:S1-01 | settled |
| 软件架构 | software architecture | 系统的单个或多个结构，由软件元素、元素的外部可见属性及元素间关系构成（SEI/经典操作性表述）。 | A:S1-03, B:S1-03 | settled |
| 架构描述 | architecture description (AD) | 表达架构的工件（文档、模型集等）；架构本身是抽象，AD 是其表达，二者不可混同。 | A:S1-01, B:S1-07, G:S1-08 | settled |
| 干系人 | stakeholder | 对关注系统持有 Concern（关注点）的个人、群体或组织（含客户、用户、开发/维护者、监管者等）。 | B:S1-07, F:S1-F06 | settled |
| 关注点 | concern | 对系统的任何利益/关注；源自 separation of concerns。 | B:S1-07, G:S1-07 | settled |
| 架构视角 | architecture viewpoint | 构建、解释、分析某一类架构视图的约定集（含模型种类、记号、方法与分析技术）。 | B:S1-07, G:S1-07 | settled |
| 架构视图 | architecture view | 按某视角约定、面向特定干系人关注点对架构的具体表达；由一或多个架构模型（2022 改称 View Component）构成。 | B:S1-07, G:S1-07 | settled |
| 架构对应关系 | correspondence (rule) | AD 元素间关系及其强制规则（组合/细化/一致性/可追溯/依赖/约束/义务），支持跨视图一致性。 | G:S1-07 | settled |
| 架构决策 / 理由 | architecture decision / rationale | 影响 AD 元素并关联关注点的决策；理由记录决策依据及被否决的架构备选。 | A:S1-07, G:S1-07 | settled |
| 架构框架 | architecture framework | 为特定域/共同体建立创建、解释、分析、使用架构描述的通用实践（TOGAF、RM-ODP、4+1、MODAF）。 | G:S1-07 | settled |
| 架构风格 | architectural style | 定义一类系统结构组织模式：确定 components/connectors 词汇表及其组合约束；符合约束带来特定属性并制造代价。 | G:S2-14, B:S2-14 | settled |
| 微服务 | microservice | 可独立部署服务套件风格（围绕业务能力、去中心化数据治理、design for failure 等）；原作者声明无精确定义，工程口径采特征清单。 | B:S2-11, G:S3-02 | disputed |
| 架构决策记录 | architecture decision record (ADR) | 记录单个 architecturally significant decision 的短文本，含 Title/Context/Decision/Status/Consequences；单调编号、被取代而非改写，与 42010 Rationale 对齐。 | B:S2-09, G:S2-09, G:S1-07 | settled |
| 质量属性 | quality attribute | 功能之外、可独立选择期望水平的质量维度，须可操作化（SEI QA 场景）；NFR 是需求分类称呼、质量属性是设计/度量维度。 | F:S2-F01, B:S1-06, M:S1-M07 | settled |
| 质量属性场景 | quality attribute scenario | 特定质量属性的可验证需求，六要素：刺激源/刺激/环境/制品/响应/响应度量；分通用与具体场景。 | F:S2-F01, F:S1-F07 | settled |
| 敏感点 | sensitivity point | 对达成某一质量属性响应至关重要的组件/关系属性。 | G:S1-11 | settled |
| 权衡点 | tradeoff point | 同时是多个质量属性的敏感点、影响多个属性的属性；与敏感点非同义。 | G:S1-11, G:S1-05 | settled |
| 效用树 | utility tree | ATAM 的自顶向下机制：以 utility 为根，将质量属性细化到带刺激/响应的场景并排序。 | G:S1-11 | settled |
| 架构侵蚀 | architecture erosion | 由对架构的违规（violations）引起，导致系统问题增多与脆化（brittleness）；与 drift 共同造成「变更阻力递增」。 | B:S4-01, L:S2-11, P:P-S2-10, P:P-S4-08 | settled |
| 架构漂移 | architecture drift | 由对架构的不敏感（insensitivity）引起，导致不适应性、形式失一致与清晰度下降，进而更易违规。 | B:S4-01, L:S2-11, P:P-S2-10, P:P-S4-08 | settled |
| 微内核 | Microkernel (POSA) | 架构模式：将最小功能核（minimal functional core）与扩展功能及客户特定部分分离，microkernel 充当可插拔扩展的插座（socket）并协调其协作；适用于需适应变化系统需求的系统。 | R:S2-BK-16, R:R-XC-04 | settled |
| 有界上下文 | bounded context (DDD) | 显式定义模型适用范围的上下文，并在团队组织、应用部分与物理制品上设边界。 | B:S2-08 | settled |
| 通用语言 | ubiquitous language (DDD) | 单一有界上下文内、贯穿团队讨论与代码的共享语言。 | B:S2-08 | settled |

## 2. 需求

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 软件需求 | software requirement | 必须被某物展现、以解决现实世界问题的属性。 | F:S1-F08, F:S1-F01 | settled |
| 需求工程 | requirements engineering | 在生命周期各阶段对系统与软件产品的需求进行工程化处理的过程与产品；标准为 ISO/IEC/IEEE 29148:2018。 | F:S1-F02 | settled |
| 干系人需要 / 干系人需求 | stakeholder needs / requirements | 需要是对干系人 needs/wants/desires/expectations 的引出；需求是由需要转化而来、客观充分、结构化、更正式的陈述。 | F:S1-F05 | settled |
| 软件需求规格说明 | software requirements specification (SRS) | 29148 需求信息项之一，规定软件产品需求；与 BRS/StRS/SyRS 构成需求信息项体系。 | F:S1-F02 | settled |
| 功能/非功能需求 | functional / nonfunctional requirements | 功能需求=软件须执行的功能/行为；非功能需求=功能之外的质量约束与属性（另列技术约束与 QoS 约束）。 | F:S1-F01 | settled |
| 良构需求特性 | characteristics of well-formed requirements | 单条需求 9 特性（necessary/appropriate/unambiguous/complete/singular/feasible/verifiable/correct/conforming）；需求集 5 特性（complete/consistent/feasible/comprehensible/validatable）。 | F:S4-F01, F:S3-F01 | settled |
| 业务或任务分析 | business or mission analysis | 29148 第一个需求相关过程：定义问题/机会空间、刻画解决方案空间、评估备选方案类。 | F:S1-F02 | settled |

## 3. 实现与构造

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 信息隐藏 | information hiding | Parnas 分解判据：每个模块隐藏一个「困难或可能变化的设计决策」（secret），接口只揭示尽量少的内部工作。 | H:S2-01 | settled |
| 模块 / 模块化 | module / modularization | Parnas：模块是责任分配（非子程序）；模块化效果取决于划分判据。 | H:S2-01 | settled |
| 内聚 | cohesion | 模块内部元素彼此关联/隶属同一目标的程度；序数型，Coincidental→Functional。 | H:S2-09 | settled |
| 耦合 | coupling | 模块间相互依赖的程度；非二元而是多维，类型 Content→Data（高→低）。 | H:S2-09 | settled |
| 共生 | connascence | Page-Jones 的耦合分析框架，按 strength/locality/degree 三维评估，分静态与动态。 | H:S2-09 | settled |
| 模块化（标准） | modularity | ISO 25010 maintainability 子特性：改动一个组件对其它组件影响最小。 | H:S1-02, M:S2-M01 | settled |
| 设计模式 | design pattern | 对软件设计中反复出现问题的可复用解法（模板/蓝图），非可直接套用的成品设计。 | H:S2-06 | settled |
| 反模式 | anti-pattern | 常见但适得其反的问题解法；初看合适有效但弊大于利，且有已记录的有效替代。 | H:S2-08 | settled |
| 代码坏味道 | code smell | 对应系统更深层问题的、易于察觉（sniffable）的表层迹象（Kent Beck 提出）；是重构启发式信号而非结论。SonarQube 将其作为 maintainability 域的 issue 类型并计入技术债。 | H:S2-03, L:S2-06, P:P-S2-08, P:P-S3-02 | settled |
| 大泥球 | Big Ball of Mud | 缺乏可感知架构的软件系统；是最常见的「架构」之一，成因含业务压力、人员流动与软件熵。 | H:S2-08 | settled |
| 深/浅模块 | deep / shallow module | 深模块=接口简单但功能强大；浅模块=接口复杂却功能不足；设计目标是让模块「深」，避免 classitis。 | H:S2-02 | settled |
| 抽象 / 抽象泄漏 | abstraction / leaky abstraction | 抽象=对实体的简化视图；Spolsky 定律：所有非平凡抽象都会有不同程度泄漏，无法完全屏蔽底层复杂性。 | H:S2-02, H:S2-07 | settled |
| 脆弱基类 | fragile base class | 继承系统的固有架构问题：对基类看似安全的修改经继承传递可能使派生类故障。 | H:S4-03, H:S2-06 | settled |
| DRY | Don't Repeat Yourself | 每个知识点在系统内须有单一、无歧义、权威的表示；针对知识重复而非机械代码重复。 | H:S2-04 | settled |
| YAGNI | You Aren't Gonna Need It | XP 原则：未确认必需前不添加功能，须与持续重构/测试/集成配合。 | H:S2-11 | settled |
| SOLID | SRP/OCP/LSP/ISP/DIP | 面向对象设计五原则集合（Martin；Feathers 给出缩写）。 | H:S2-05 | settled |

## 4. 测试

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 软件测试 | software testing | 一组以发现缺陷、评估质量为目的的测试活动；ISO/IEC/IEEE 29119 系列规定其概念与过程。 | I:S1-STD-11 | settled |
| 测试层次 | test level | 组织并一起管理的测试活动分组；每层是测试过程的一次实例，针对生命周期某阶段。 | I:S1-OFF-11 | settled |
| 测试类型 | test type | 与特定质量特性相关的一组测试活动；大多数类型可在每个层次执行。 | I:S1-OFF-11 | settled |
| 组件/单元测试 | component / unit testing | 在隔离状态下测试组件，通常需测试桩/框架，由开发者在开发环境执行。 | I:S1-OFF-11 | settled |
| 集成测试 | integration testing | 判定独立开发的软件单元连接后是否正确协同工作；可窄可宽。 | I:S2-WEB-16 | settled |
| 系统测试 | system testing | 聚焦整个系统的整体行为与能力，含端到端功能与非功能测试。 | I:S1-OFF-11 | settled |
| 验收测试 | acceptance testing | 验证系统满足用户业务需要、演示部署就绪；理想由预期用户执行。 | I:S1-OFF-11 | settled |
| 测试驱动开发 | test-driven development (TDD) | 先写测试再写实现的技术（Kent Beck），核心为 Red-Green-Refactor 循环。 | I:S2-WEB-14, I:S2-WEB-19 | settled |
| 测试金字塔 | test pyramid | 底层大量小、隔离、快速的单元测试，顶层少量复杂、高层的端到端测试（Fowler）。 | I:S2-WEB-12, I:S1-OFF-11 | settled |
| 冰淇淋反模式 | ice cream cone / inverted pyramid | 过度依赖端到端测试、缺少集成/单元测试的倒置金字塔；另有 hourglass（缺中间层）。 | I:S3-VEN-02 | settled |
| 可测试性 | testability | ISO 25010 maintainability 子特性：建立测试准则并执行测试判定其是否满足的有效性与效率程度；SEI 亦视为架构级质量属性。 | I:S1-OFF-05, H:S1-02, M:S2-M01 | settled |
| 测试替身 | test double | 为测试目的替换生产对象的泛称：Dummy/Fake/Stub/Spy/Mock。 | I:S2-WEB-17 | settled |
| 持续集成 | continuous integration (CI) | 团队成员至少每日把改动合并回主线，每次集成由自动化构建（含测试）验证。 | I:S2-WEB-18 | settled |
| 质量门控 | quality gate | 用一组分析时度量的条件判定项目是否可发布；未满足即阻断构建/PR 合并。 | I:S3-VEN-04 | settled |

## 5. 部署

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 构建/发布/运行 | build / release / run | build=代码→bundle；release=build+config 合并为不可变、带唯一 ID 的产物；run=执行选定 release，运行时无代码变更入口。 | J:S2-01, J:S2-07 | settled |
| 发布制品 | release | build 与 config 合并的产物，append-only 账本，一经创建不可变更，改动产生新 release。 | J:S2-01 | settled |
| 配置 | config | 随部署环境变化的一切（资源句柄、凭据、每部署值）；须与代码严格分离并存于环境变量。 | J:S2-01 | settled |
| 开发/生产一致性 | dev/prod parity | 让开发、预发、生产尽可能相似（时间差/人员差/工具差最小），backing service 同类型同版本。 | J:S2-01 | settled |
| 部署流水线 | deployment pipeline | 把构建拆为多阶段、逐阶段提升置信度的自动化链路；生产部署通常是最后阶段。 | J:S2-06 | settled |
| 发布工程 | release engineering | 以可复现、自动化方式构建并交付软件的工程学科；确保发布可重复而非「unique snowflake」。 | J:S2-07 | settled |
| 密闭构建 | hermetic build | 对构建机已装库不敏感、依赖已知版本编译器与库的自足构建，同 revision 在不同机器结果一致。 | J:S2-07 | settled |
| 不可变基础设施 | immutable infrastructure | 部署后不能再被更改的基础设施；变更只能通过创建新版本或重建实例实现。 | J:S3-05, J:S2-04 | settled |
| 蓝绿部署 | blue-green deployment | 维护两套相同生产环境，任一时刻仅一套承载流量；新版在另一套测试通过后切换流量，出错可快速切回。 | J:S2-02 | settled |
| 金丝雀发布 | canary release | 新版本先服务一小部分用户/流量，随信心提升扩大比例直至全量，以最小化爆炸半径。 | J:S2-03 | settled |
| 滚动更新 | rolling update | 逐步以新实例替换旧实例，新旧多版本并存；由 maxUnavailable/maxSurge 控制节奏。 | J:S3-04 | settled |
| 渐进暴露 | progressive exposure | 把变更分阶段逐步暴露给更大范围用户/基础设施；每阶段须通过健康检查才推进。 | J:S3-03 | settled |
| 烘焙时间 | bake time | 渐进暴露中各 rollout 组之间的观察等待时间，应以小时/天计且逐组增加。 | J:S3-03 | settled |

## 6. 运维与可靠性

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 服务等级指标 | service level indicator (SLI) | 对服务水平某方面被谨慎定义的定量度量；推荐口径为「好事件数 / 总事件数」。 | K:S2-01 | settled |
| 服务等级目标 | service level objective (SLO) | 由 SLI 度量、针对某服务水平的目标值或取值范围；100% 不是正确目标。 | K:S2-01 | settled |
| 服务等级协议 | service level agreement (SLA) | 与用户之间含「达成/未达成后果」的契约；无明确后果者只是 SLO。 | K:S2-01 | settled |
| 错误预算 | error budget | 允许的不可靠度 = 100% − SLO，将「创新 vs 稳定」转为客观发布决策机制。 | K:S2-01, K:S2-02 | settled |
| 燃尽率 | burn rate | 错误预算被消耗的速率；用多窗口、多燃尽率组合告警兼顾 precision/recall/detection/reset。 | K:S2-02 | settled |
| 四大黄金信号 | four golden signals | 面向用户的监控若只留四个指标则选：延迟、流量、错误、饱和度。 | K:S2-01 | settled |
| 可观测性 | observability | 从系统外部输出推断内部状态、回答 unknown unknowns 与「为什么」的能力；正式信号清单用 OTel 的 Traces/Metrics/Logs/Baggage。 | K:S3-02 | disputed |
| 分布式追踪 / Span | distributed trace / span | trace 记录请求跨服务传播路径，由若干 span 组成，用于定位分布式性能根因。 | K:S3-02 | settled |
| 断路器 | circuit breaker | 监控远程调用失败数，超阈值即跳闸进入 Open 快速失败，给依赖恢复时间并阻断级联；状态机 Closed/Open/Half-Open。 | K:S2-04, K:S3-01 | settled |
| 舱壁 | bulkhead / cell-based | 按消费者或负载划分隔离资源池，使单分区失败不跨舱扩散。 | K:S3-01, K:S2-03 | settled |
| 超时与重试 | timeout / retry | 超时限制远程调用等待；重试处理瞬时故障，须配指数退避+抖动且仅对幂等操作安全。 | K:S2-03, K:S3-04 | settled |
| 级联故障 | cascading failure | 随时间增长的、由正反馈驱动的故障（局部过载抬高其余失败概率）；最常见根因是过载。 | K:S2-01, K:S2-03 | settled |
| 混沌工程 | chaos engineering | 在生产中对系统做受控实验（稳态→假设→注入→证伪）以建立对动荡条件抵御能力的信心。 | K:S2-05 | settled |
| 无指责复盘 | blameless postmortem | 聚焦导致事件的系统性原因而非追责个人；假设参与者基于当时信息善意行事。 | K:S2-06, K:S2-01 | settled |
| 事件指挥官 | incident commander (IC) | 事件响应核心角色，掌握高层状态、组建响应组织并分派职责（ICS 框架）。 | K:S2-01 | settled |
| 意图驱动容量规划 | intent-based capacity planning | 以程序化方式编码服务依赖与参数（意图），据此自动生成资源分配计划并随需求变化重算。 | K:S2-01 | settled |

## 7. 演化与弃用

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 重构 | refactoring | 对软件内部结构的修改，目的是更易理解/修改，而不改变可观察行为（observable behavior）。 | L:S2-04, L:S2-05 | settled |
| 技术债 | technical debt | Cunningham 隐喻：首次交付的代码如同负债；内部质量缺陷（cruft）造成的额外变更成本。Fowler 将其操作化为「因 cruft 多花的未来变更时间」；Kruchten 等推进为需显式管理的理论与实践。 | B:S2-03, L:S2-01, L:S2-03, P:P-S2-01, P:P-S2-03, P:P-S4-01 | settled |
| 本金与利息 | principal & interest | 本金=清除 cruft、恢复内部质量的一次性投入（偿还 principal）；利息=因 cruft 存在而每次修改该代码多花的时间。关键区别于金融债：利息只在「修改该代码」时触发，不按时间流逝累积（crufty 但稳定的代码可不偿还）。 | P:P-S2-01, P:P-S2-03 | settled |
| 技术债象限 | technical debt quadrant | 以 deliberate/inadvertent（有意/无意）× prudent/reckless（审慎/鲁莽）两组正交判据区分设计缺陷；核心问题是「审慎的债还是鲁莽的债」而非「是不是债」。prudent-inadvertent 债即使优秀团队也不可避免。 | P:P-S2-02, L:S2-03 | settled |
| SQALE | Software Quality Assessment based on Life-cycle Expectations | 以客观、准确、可复现、自动化方式评估源代码质量并提供技术债管理的方法；含 9 项基本原则与 4 主组件（Quality Model / Analysis Model / indices / indicators），以生命周期期望为基准。SonarQube 的 `sqale_*` 指标沿用其命名。 | P:P-S3-03, P:P-S4-02 | settled |
| 技术债比率 | technical debt ratio (TDR) | `sqale_debt_ratio` = 修复成本（technical debt）/（每行开发成本 × 代码行数）；每行开发成本默认 30 分钟、可配置。据 TDR 映射 maintainability rating（A ≤5% / B 5–10% / C 10–20% / D 20–50% / E ≥50%）。 | P:P-S3-01 | settled |
| 架构技术债 | architectural technical debt (ATD) | 由「大」设计决策（结构、框架、技术、语言选择等）造成的技术债：作出时可能合适甚至最优，却显著阻碍未来进展；难识别、修复成本范围大、常被回避且与沟通问题相关。 | P:P-S4-11, P:P-S4-03 | settled |
| 童军规则 / 机会式重构 | boy-scout rule & opportunistic refactoring | 「始终让离开时的代码比你发现时更干净」；Fowler 倡导把重构作为机会式活动，在改动代码时顺带清理，而非安排专门重构阶段（须测试全绿、以判断力避免钻入兔子洞）。 | P:P-S2-04 | settled |
| 设计回报线 | design payoff line / design stamina hypothesis | 良好设计提升项目「耐力」使长期交付更快；无设计项目初期更快但代码劣化，二者在某点（design payoff line）交叉。低于该线时牺牲设计换速度或可成立，越过该线后取舍是虚幻的。 | P:P-S2-05 | settled |
| 软件演化定律 | Lehman's laws | E-type 软件在演化中应遵循的规律（完整八条：持续变更 / 复杂度递增 / 自我调节 / 组织稳定性守恒 / 熟悉度守恒 / 持续增长 / 质量下降 / 反馈系统）；条数经多次扩展：1974 起 3 条 → 1980 增 2 条（共 5）→ 1991 第 6 条 → 1996 首次成文第 7、8 条。 | L:S4-02, A:S4-01, R:R-XC-01, R:R-XC-02, P:P-S4-09 | settled |
| E 型软件 | E-type software | Lehman 定律适用对象：「在真实世界中求解问题/实现应用的软件系统」，嵌入真实世界、需随运行环境持续演化（另有 S/P/A 型程序）。 | R:R-XC-01, R:R-XC-02 | settled |
| 演进式架构 | evolutionary architecture | 支持「有引导的增量变更」作为多维度首要原则的架构；可演化性作为一等 -ility。 | L:S2-12 | settled |
| 架构适应度函数 | architectural fitness function | 对某些架构特性提供客观完整性评估的机制；可用 tests/metrics/monitoring 实现，在流水线持续校验。 | L:S2-12, L:S3-01 | settled |
| 遗留代码 | legacy code | Feathers：没有测试的代码（code without tests）；判据在可变更性/可验证性，非年代或技术栈。 | L:S2-09 | settled |
| 接缝 | seam | 在不改动该处代码的前提下即可改变程序行为的位置（预处理/链接/对象接缝）。 | L:S2-09 | settled |
| 特征测试 | characterization test | 描述既有软件实际行为、比对新旧版本整体结果（不断言值正确性）的安全网测试。 | L:S2-10 | settled |
| 绞杀者模式 | strangler fig pattern | 遗留系统渐进现代化：在旧系统之上/之旁增量建新功能并逐步迁移行为，直至旧系统被替换，而非一次性整机重写。 | L:S2-07, P:P-S2-06 | settled |
| 弃用 | deprecation | 对某技术/功能/设计/实践的「劝阻使用」状态，预示未来淘汰，但替换或移除并非必需或紧急（RFC 9745）。 | L:S1-03 | settled |
| 日落 | sunset | 以 HTTP Sunset 响应头指示某 URI 很可能在某未来时点不可响应（RFC 8594）。 | L:S1-02 | settled |

## 8. 质量模型与 ilities

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 产品质量模型 | product quality model | ISO/IEC 25010:2023 九特性：Functional Suitability/Performance Efficiency/Compatibility/Interaction Capability/Reliability/Security/Maintainability/Flexibility/Safety。 | M:S1-M01, M:S2-M01 | settled |
| 可使用质量模型 | quality-in-use model | ISO/IEC 25019:2023 三特性：beneficialness/freedom from risk/acceptability。 | M:S1-M03 | settled |
| 可维护性 | maintainability | 产品/系统被修改以改进、纠错或适应环境与需求变化的有效性与效率程度；子特性 modularity/reusability/analysability/modifiability/testability。 | M:S1-M01, H:S1-02, A:S1-01 | settled |
| 可复用性 | reusability | 25010 maintainability 子特性：产品可作为资产用于多个系统或构建其它资产的程度。 | M:S2-M01 | settled |
| 可分析性 | analysability | 25010 maintainability 子特性：评估预期变更影响、诊断缺陷或识别待修改部件的有效性与效率程度。 | M:S2-M01 | settled |
| 可修改性 | modifiability | 25010 maintainability 子特性：在不引入缺陷、不降低既有质量的前提下有效修改的程度（非顶层特性）。 | M:S2-M01 | settled |
| 灵活性 | flexibility | 25010:2023 顶层特性：产品适应需求、使用情境或系统环境变化的能力；子特性 adaptability/scalability/installability/replaceability；由 2011 版 Portability 改名。 | M:S1-M01, M:S2-M01 | settled |
| 安全性（人身/环境） | safety | 25010:2023 新增顶层特性：在既定条件下避免危及人身、健康、财产或环境的状态的程度。 | M:S2-M01 | settled |
| 信息安全 | security | 25010 顶层特性：防御恶意攻击并保护信息与数据、使访问权限与其授权类型/级别相称的程度。 | M:S2-M01 | settled |
| 可扩展性 | extensibility | 无 ISO 顶层术语；推荐 SEI 口径：可能独立的团队通过架构预置扩展点，以已知、有计划的方式扩展系统功能或质量特性的能力。 | M:S1-M04, A:S1-04 | disputed |
| 可演化性 | evolvability | 无 ISO 术语、无共识定义；推荐学术口径：在全生命周期以最低成本容纳需求变更、同时保持架构完整性；与 extensibility 边界模糊。 | M:S4-M01, M:S4-M02 | disputed |
| 架构战术 | tactic | 影响质量属性响应控制的设计决策；一组战术构成 architectural strategy，pattern 打包战术。 | M:S2-M02, M:S1-M06 | settled |

## 9. 团队与交付效能

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| 康威定律 | Conway's Law | 设计系统的组织会产出结构复制其沟通结构的设计；用同态描述系统图与组织图的保结构对应。 | N:S2-01, N:S2-02 | settled |
| 镜像假说 | mirroring hypothesis | 组织连接对应技术依赖，是 Conway's Law 在组织设计领域的名称，不规定因果方向。 | N:S4-02 | settled |
| 逆向康威操作 | Inverse Conway Maneuver (ICM) | 主动改变团队与组织结构，以催生期望的软件架构，使技术架构与业务架构同构。 | N:S3-01 | settled |
| 流对齐团队 | stream-aligned team | 对齐单一业务域价值流、端到端负责、无交接的团队。 | N:S2-04, N:S2-05 | settled |
| 赋能团队 | enabling team | 通过指导/教练帮助流对齐团队克服障碍、提升能力的团队（Facilitation 交互）。 | N:S2-05 | settled |
| 复杂子系统团队 | complicated-subsystem team | 负责需大量专业知识的子系统，以降低其他团队认知负荷（X-as-a-Service 交互）。 | N:S2-04 | settled |
| 平台团队 | platform team | 为流对齐团队提供自服务内部产品/平台以加速交付、降低认知负荷的团队。 | N:S2-05, N:S2-04 | settled |
| 三种交互模式 | three interaction modes | Collaboration（限时高带宽协作）/ X-as-a-Service（低交互边界清晰）/ Facilitation（促进）。 | N:S2-05 | settled |
| 认知负荷 | cognitive load | 团队能承载的复杂度有限，每个新增工具/职责/域都消耗心智带宽；平台首要价值即降低它。 | N:S2-04 | settled |
| 最薄可行平台 | thinnest viable platform (TVP) | 平台只提供刚够能力、避免不必要复杂度，让流对齐团队更快而不制造更多依赖。 | N:S2-05 | settled |
| DORA 交付指标 | DORA software delivery metrics | 现行五指标：change lead time、deployment frequency、failed deployment recovery time（吞吐）+ change fail rate、deployment rework rate（不稳定）；旧「四键」/MTTR 为历史口径。 | I:S3-VEN-03, K:S3-05, N:S3-02, N:S3-03 | settled |
| 变更前置时间 | change lead time | 一次变更从提交进版本控制到成功部署至生产所耗时间。 | N:S3-02 | settled |
| 部署频率 | deployment frequency | 给定周期内应用变更部署的次数或两次部署间隔。 | N:S3-02 | settled |
| 失败部署恢复时间 | failed deployment recovery time | 从一次失败且需立即干预的部署中恢复所需时间（2023 取代 MTTR）。 | N:S3-03 | settled |
| 变更失败率 | change fail rate | 部署中需立即干预（通常导致回滚或 hotfix）的比例。 | N:S3-02 | settled |
| 部署返工率 | deployment rework rate | 因生产事故发生的非计划部署比例（2024 新增第五指标）。 | N:S3-03 | settled |
| 古德哈特定律 | Goodhart's law | 当度量成为目标时它就不再是好度量；DORA 据此警示指标 gaming。 | N:S3-02 | settled |

## 10. 厂商架构框架与采用雷达

| 术语 | English | 定义（统一口径） | source_id | 状态 |
|---|---|---|---|---|
| Well-Architected 支柱 | well-architected pillar | 厂商架构框架中对某一非功能关注点的原则与建议集合。AWS 六支柱：Operational excellence / Security / Reliability / Performance efficiency / Cost optimization / Sustainability；GCP 六支柱：Operational excellence / Security privacy and compliance / Reliability / Cost optimization / Performance optimization / Sustainability。 | Q:S3-VEN-02, Q:S3-VEN-03, Q:S3-VEN-04, Q:S3-VEN-05 | settled |
| Well-Architected 框架 | AWS/Google Cloud Well-Architected Framework | 帮助架构师等一致地对照最佳实践度量与改进架构的方法框架；明确定位为「建设性对话」而非审计机制，并随云能力与行业实践持续更新。GCP 原名 Google Cloud Architecture Framework。 | Q:S3-VEN-02, Q:S3-VEN-04 | settled |
| 采用雷达 | Thoughtworks Technology Radar | 由 Thoughtworks Technology Advisory Board 撰写、每年两次的技术快照；以 blip 经四象限与四环组织，表达对技术采用程度的推荐意见（明确不追求全面、不接受厂商付费影响）。 | Q:S3-VEN-06, Q:S3-VEN-07 | settled |
| blip / 象限 | blip / quadrant | blip=在软件开发中扮演角色的技术或方法，位置随信心变化在环间移动；quadrant（Techniques / Platforms / Tools / Languages and Frameworks）表示 blip 类型，官方称其重要性低于环。 | Q:S3-VEN-07 | settled |
| 采用四环 | adopt / trial / assess / caution | 采用推荐程度，由内向外：Adopt（成熟证实的 blip，适当情境下应认真考虑）→ Trial（可用于生产但不如 Adopt 充分验证，进入该环须已有生产经验）→ Assess（值得密切关注但尚不宜试用）→ Caution（行业可能已接受但存在重大顾虑，须结合情境审慎评估）。第四环历史上称 Hold，Vol 33→Vol 34（2026-04）更名为 Caution。 | Q:S3-VEN-07, Q:S3-VEN-08 | settled |

---
> 生成：2026-09-10 · O 域方法论综合，并按 P（技术债）/Q（厂商架构）/R（奠基文献）三包级联更新。本表为跨域唯一裁决表，任何后续工件中的术语定义如与本表冲突，以本表为准。
