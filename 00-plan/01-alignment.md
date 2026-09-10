# 阶段1 · 思路对齐文档：软件工程与架构设计

> 本文件是阶段1「思路对齐」交付物，面向学习者与开发者本人。
> 目标：把「软件工程」「架构设计」两个核心词讲清楚，并与本任务的既有观点逐条对齐。
> 证据来源：`02-research/` 下的 A/B/E/P/Q/R 证据包（S1 标准与官方知识体系、S2 经典著作、S3 厂商体系、S4 学术论文、P 技术债、R 奠基文献回源）。
> ISO 版本号一律采信 `E-iso-standards`：12207:**2026**（已取代 2017）、42010:**2022**、25010:**2023**、14764:**2022**、24765:2017。

---

## 一页速览

- **软件工程（Software Engineering）**：把系统化、规范化、可量化的方法应用于软件的**开发、运行与维护**，即"把工程应用于软件"；它覆盖软件完整的生命周期，而不只是写代码。[IEEE Std 610.12-1990；经 SWEBOK、SEVOCAB 采纳]
- **架构设计（Software Architecture & Design）**：对系统在环境中的**根本性**概念或属性所做的设计——体现于元素、元素间关系，以及指导其设计与演化的原则之中；它只关心系统对外可见、影响全局的部分。[ISO/IEC/IEEE 42010:2022；SEI]
- **二者关系**：软件工程是**覆盖全生命周期（从概念到弃用）的管理过程**，架构设计是其中**杠杆最大的一类"根本性决策"**——它决定系统的质量属性与后续演化能力，是对抗复杂度与熵增的第一道关口。

---

## 二、何为软件工程

### 2.1 权威定义：一条被反复采纳的"定义链"

软件工程最广为引用的定义由 IEEE 610.12-1990 给出：

> "The application of a systematic, disciplined, quantifiable approach to the development, operation, and maintenance of software; that is, the application of engineering to software."
> （将系统化、规范化、可量化的方法应用于软件的开发、运行与维护；即把工程应用于软件。）[IEEE Std 610.12-1990]

这条定义不是孤立的一家之言，而是一条清晰的**采纳链**：

1. **源头**：IEEE 610.12-1990 首次给出上述定义。[A-S1-08]
2. **采纳**：SWEBOK 开篇直接采用该定义，并标注来自 SEVOCAB。[SWEBOK V3；A-S1-01]
3. **术语标准化**：ISO/IEC/IEEE 24765（SEVOCAB）作为跨标准术语汇编，收录并沿用该定义，使"软件工程"在 ISO/IEC/IEEE 语境下口径一致。[ISO/IEC/IEEE 24765:2017；A-S1-09]
4. **教育共识**：SE2014（ACM/IEEE-CS 课程指南）同样引用该定义，并强调"软件工程不只是编程"。[SE2014；A-S1-05]

教材口径（Sommerville）把它讲得更直白："一门关注软件生产**所有方面**的工程学科，从早期系统规格说明，到系统投入使用后的维护"。[Sommerville；A-S2-01] 产业口径（Google）则补充了时间维度："软件工程不仅包括写代码，还包括组织用于**长期**构建与维护代码的全部工具与流程"，核心是 *Programming Over Time*（跨时间编程）。[Software Engineering at Google；A-S2-02]

**一句话抓住本质**：软件工程 = 工程方法 + 软件全生命周期 + 时间与团队的维度。

### 2.2 学科范畴：SWEBOK 知识域，V3 的 15 到 V4 的 18

软件工程的知识边界由 **SWEBOK**（Software Engineering Body of Knowledge，ISO/IEC TR 19759）划定，由 IEEE 计算机学会出版。[SWEBOK V3/V4；A-S1-01]

- **V3（2014）**：15 个知识域（KA），覆盖需求、设计、构造、测试、维护、配置管理、工程管理、工程过程、模型与方法、质量、职业实践、经济，以及计算/数学/工程基础。
- **V4（2024-10）**：扩展为 **18** 个，新增 **软件架构（Software Architecture）**、**软件工程运维（Software Engineering Operations）**、**软件安全（Software Security）** 三个知识域。[SWEBOK V4；A-S1-01；B-S1-02]

这里有一个对后文很重要的信号：**架构从"设计知识域中的一部分"上升为独立知识域**，说明业界对"架构"独立地位的认识在成熟。[SWEBOK V4；B-S1-02]

### 2.3 起源与演化：1968、软件危机、瀑布到敏捷

- **起点**：软件工程作为学科，以 **1968 年 NATO 软件工程会议（德国 Garmisch）** 与 1969 年罗马会议为标志性起点。"software engineering"这个术语作为**故意带挑战性**的会议名称被提出，来源归于 F. L. Bauer。[NATO 1968 报告；A-S1-07]
- **软件危机**：1968 报告第 7 章明确记录了与会者关于 "software crisis / software gap" 的争论——成本与进度超支、质量低、难维护、项目失控。**注意：当时与会者对其严重程度存在分歧**，并非一致共识。[NATO 1968 报告；A-S1-07] 这提醒我们：软件工程从一开始就是为了**应对失控**而生的。
- **范式演化**：阶段化的瀑布模型常追溯到 Royce(1970)（其原意并非纯粹线性，而是强调回退迭代）；2001 年《敏捷宣言》提出四大价值与十二条原则，标志向**迭代、增量、快速反馈、响应变化**的转向。[Royce 1970；敏捷宣言 2001；A-S4-02、A-S1-11]

### 2.4 与计算机科学、编程的关系：时间 + 人员两个维度

软件工程以计算机科学（CS）为主要基础（SE2014 指出其最大知识组件是 computing essentials），但**不等同于 CS**：SE 额外引入了工程流程、团队协作，以及"时间/变更"维度。Parnas 更主张 SE 应作为与土木、机械并列的**独立工程学科**，而非 CS 的子领域。[SE2014；Parnas 1998；A-S1-05、A-S4-03]

区分"编程"与"软件工程"最精炼的说法来自 CS2023，用两个维度：

| 维度 | 编程（Programming） | 软件工程（Software Engineering） |
|---|---|---|
| **时间（time）** | 一次性写出能跑的代码 | 多版本、长期存活，需应对需求增删、平台/语言/依赖演进 |
| **人员（people）** | 通常个人 | 多人协作，需要沟通、评审、约定与工具流程 |

CS2023 引 Parnas 之语作注脚："Software engineering is the multi-person construction of multi-version programs."（软件工程是**多人**对**多版本**程序的构建。）[CS2023；A-S1-06]

### 2.5 生命周期与过程：12207 讲"过程"，不讲固定"阶段"

一个常见误解是"软件工程 = 需求→设计→编码→测试→维护的固定流程"。国际标准恰恰相反：

**ISO/IEC/IEEE 12207**（Software life cycle processes）为软件生命周期建立的是**过程（process）**框架，并**明确不规定具体的生命周期模型、开发方法或建模技术**。[ISO/IEC/IEEE 12207；A-S1-02]

- 过程 = 把输入转化为输出的、相互关联的活动集合，可在不同阶段反复出现。
- 12207:**2026** 版与 ISO/IEC/IEEE 15288 统一为**四组过程**：**协议（agreement）**、**组织项目使能（organizational project-enabling）**、**技术管理（technical management）**、**技术（technical）**；过程数由旧版的 43 统一为 30。[ISO/IEC/IEEE 12207:2026；E]
- **阶段（stage）** 则是另一回事：它是生命周期中与"描述/实现状态"相关的时期，通常以**主决策门（primary decision gate）** 结束。标准不规定任何特定阶段集，仅举例引用 ISO/IEC TS 24748-1 的六阶段：**concept、development、production、utilization、support、retirement**。[ISO/IEC/IEEE 12207:2026；A-S1-03]

**关键结论**：标准给出的是"要做哪些事"，而非"必须按什么顺序做"。这正是它比"瀑布 vs 敏捷"之争更底层的价值。

### 2.6 质量模型：ISO/IEC 25010:2023 的九特性

**ISO/IEC 25010:2023** 是 SQuaRE（ISO/IEC 25000 系列）的质量模型核心，取代 ISO/IEC 9126。它将软件产品质量建模为**九大特性**（相较 2011 版八特性）：功能适合性、性能效率、兼容性、交互能力、可靠性、安全性(security)、可维护性、灵活性、安全(safety)。[ISO/IEC 25010:2023；A-S1-04；E]

相较于 2011 版的三个关键变化：`Usability → Interaction capability`、`Portability → Flexibility`、**新增 Safety 顶层特性**（并在 Security 下补 Resistance、Flexibility 下补 Scalability 等子特性）。[ISO/IEC 25010:2023；A-S2-04；E]

质量模型的意义：**它把"软件好不好"从模糊感觉变成可逐项评价的结构**，也是后文架构质量属性、可维护性的共同落点。

---

## 三、何为架构设计

### 3.1 两种权威定义与它们的共同点

**定义 A（国际标准）**：ISO/IEC/IEEE 42010:2022 §3.2 将 architecture 定义为——

> "fundamental concepts or properties of a system in its environment embodied in its elements, relationships, and in the principles of its design and evolution."
> （系统在环境中的根本性概念或属性，体现于其元素、关系以及设计与演化的原则之中。）[ISO/IEC/IEEE 42010:2022]

它特别强调：**架构本身是抽象的**（概念或感知），记录架构的工件才叫 **architecture description（架构描述）**——不要把"架构"与"架构文档"混为一谈。[ISO/IEC/IEEE 42010:2022；B-S1-01]

**定义 B（SEI 经典）**：卡内基梅隆 SEI 的经典定义（Bass/Clements/Kazman）——

> 软件架构是系统的**单个或多个结构**，由**软件元素**、这些元素的**外部可见属性（externally visible properties）** 以及元素间的**关系**构成。[SEI；B-S1-03]

**二者的共同点**（也是理解架构的钥匙）：

1. **聚焦根本性**：只有 significant / fundamental 的东西才属于架构，不是所有设计决策都算。[42010；SEI；B-S1-01/03]
2. **只看外部可见**：架构只关心元素的 **public 侧**（对外提供的服务、性能、容错等），内部实现细节不属于架构。[SEI；B-S1-03]

实用判据（Fowler/Johnson）更接地气：架构就是"**the important stuff. Whatever that is**"——是否属于架构，取决于资深开发者是否认为它**重要**。[Fowler；B-S2-01、B-S2-04]

### 3.2 架构 vs 设计 vs 需求

42010 给出了清晰的方位：

- **架构"向外"**：关注"系统及其环境"，即系统边界、与外部的关系。
- **设计"向内"**：在系统边界确定之后，关注边界内部的实现细节。[42010；B-S1-01]

换句话说，**架构先确定边界与根本决策，详细设计再填充边界内部**。架构会**抑制与交互无关的实现细节**——因为它只对"影响全局的根本性内容"负责。[42010；B-S1-01]

### 3.3 架构决策与 ADR

架构既然是"一组重大决策"，就需要被记录。**ADR（Architecture Decision Record）** 由 Nygard 提出：只记录**架构上重要的决策**——那些影响 **structure、非功能特性、依赖、接口或构造技术** 的决策，格式包含 context（背景）/ decision（决策）/ consequences（后果）。[Nygard 2011；B-S2-09]

Fowler 补充了纪律：ADR 是短文档（约数页），用单调编号命名，随代码库一起版本化；决策变更时**不改写原 ADR，而是新写一份 superseding ADR 并链接**，状态分为 proposed / accepted / superseded。[Fowler；B-S2-10] 这既留档，也帮助厘清思路、暴露分歧。

### 3.4 质量属性与 ATAM

架构是**质量属性的主要承载者**（performance、modifiability、security 等）。[SEI；B-S1-04] 质量属性的标准落点即 ISO/IEC 25010 的九特性及其子特性。[ISO/IEC 25010:2023]

评估架构的权威方法是 SEI 的 **ATAM（Architecture Tradeoff Analysis Method）**：从业务驱动与架构出发，细化为 **scenarios（场景）** 与支撑它们的 **架构决策**；分析产出 **risks（风险）、non-risks（非风险）、sensitivity points（敏感点）、tradeoff points（权衡点）**，并归纳为 **risk themes**。[SEI ATAM；B-S1-05] 它说明一个重要态度：架构不是"对错题"，而是**在场景下做权衡**。

### 3.5 架构风格与模式

**Garlan & Shaw 的风格框架**：把架构抽象为"**组件（components）+ 连接件（connectors）+ 配置（configuration）**"，并给出经典风格分类：管道-过滤器、数据抽象/面向对象、事件驱动/隐式调用、分层、仓库、解释器——**每种风格都有其权衡**。[Garlan & Shaw；B-S2-14]

**工程模式层面**（把风格落到实践）：

- **分层（Layering）**：最常见，presentation / domain logic / data access 三层；最大价值是**缩小注意力范围**。[Fowler；PoEAA；B-S2-12、B-S2-05]
- **MVC**：Reenskaug 1978/79 于 Xerox PARC 提出；Fowler 释为"一组原则"（表现与领域逻辑分离 + 事件同步）。[B-S2-16、B-S2-17]
- **微服务**：把应用设计为**可独立部署的服务套件**，特征是围绕业务能力组织、去中心化数据治理、design for failure、evolutionary design。[Fowler & Lewis 2014；B-S2-11]
- **CQRS**：用不同模型分离读写（Greg Young 提出），但 Fowler 明确警示它对多数系统会引入 **risky complexity**。[B-S2-13、B-S3-01]
- **Microkernel**：最小功能核心 + 可插拔扩展。[PoSA；B-S2-18，本条 cited/medium]

### 3.6 经典著作观点

| 著作 | 核心观点 | 来源 |
|---|---|---|
| Clean Architecture（R. C. Martin） | 同心圆分层 + **依赖规则**：源码依赖只能**向内**；内层为 policies，外层为 mechanisms，从而独立于框架/UI/数据库 | [B-S2-06] |
| A Philosophy of Software Design（Ousterhout） | 设计根本目标是**易理解、易修改**；**complexity** 主要来源于 information（开发者需掌握多少信息、信息是否显见）；一切设计理念都用"能否降低 complexity"来评估 | [B-S2-07] |
| DDD（Eric Evans） | 战略设计核心是 **bounded context（限界上下文）** 与 **ubiquitous language（通用语言）**；模型表达只在上下文中才有意义 | [B-S2-08] |
| Fowler 架构观 | 好架构**支持自身演化**且与编程深度交织；差架构是 cruft 增长的主因 | [B-S2-01] |
| PoEAA | 系统整理企业应用分层与约 40 个模式，判断架构的本质问题与解法长期稳定 | [B-S2-05] |

### 3.7 演化 vs 技术债 vs 架构腐化

- **技术债（Technical Debt）**：Ward Cunningham 1992 的隐喻——首次交付的代码如同负债，**及时重写可加速开发，未偿则每分钟都成为利息**。[Cunningham；B-S2-03] Fowler 释义为"内部质量缺陷带来的额外变更成本"，主张适时"偿还本金"。[Fowler；B-S2-02]
- **架构腐化（erosion / drift）**：架构层面的退化与偏离，表现为架构违规（architectural violations）与结构问题，并损害软件质量与演化能力；成因**兼有技术与非技术因素**。[Li et al. 2022；B-S4-01]

**三者串起来**：演化是常态（见第四节 Lehman 定律），技术债与架构腐化是演化未受管理时的两种"病变"。架构设计正是预防与治理它们的核心手段。

---

## 四、可维护性 / 可扩展性 / 可演化性

这一组词常被混用，需要区分"标准术语"与"日常说法"。

**可维护性（Maintainability）** 有明确标准定义。IEEE 14764:2022 定义为"**软件产品被修改的能力**"（capability of the software product to be modified），修改包括纠错、改进，以及适配环境与需求变化。[ISO/IEC/IEEE 14764:2022；SWEBOK V3；A-S1-01、A-S1-12]

在 **ISO/IEC 25010** 下，可维护性的子特性为：**模块性（Modularity）、可复用性（Reusability）、可分析性（Analysability）、可修改性（Modifiability）、可测试性（Testability）**。[ISO/IEC 25010:2023；A-S2-04；B-S1-06]

**设计奠基思想**：Parnas (1972) 的**信息隐藏**——模块应封装"一个可能变化的设计决策（secret）"，而不是按处理步骤切分。这是模块性与可维护性的思想源头。[Parnas 1972；B-S2-15]

**软件维护的分类与成本结构**：维护按意图分为 **纠正性、适应性、完善性、预防性** 四类。维护消耗软件生命周期的主要成本份额——**超过 80% 的维护是非纠正性的**；理解待修改软件约占维护工作量的一半。[SWEBOK V3；A-S1-01、A-S1-12]

**可演化性与 Lehman 定律**：软件演化具有规律性。Lehman 的演化定律（持续变化、复杂度递增、自我调节、组织稳定性守恒、熟悉度守恒、持续增长、质量下降、反馈系统）表明：软件必须持续适应环境，否则满意度与质量下降；**维护应被理解为"演化式（继续）开发"**。注意条数口径：**1980 原文为 5 条定律；完整"八条"最早成文于 Lehman 1996《Laws of Software Evolution Revisited》**。[Lehman 1980（5 定律）／Lehman 1996（八定律复述）；A-S4-01、R]

一个重要的**边界事实**：**"可扩展性（extensibility）/ 可演化性（evolvability）"在国际标准中并不是独立顶层术语**。它们的权威地位，主要由 ISO/IEC 25010 的 **可修改性 / 灵活性（Flexibility）/ 可复用性** 等子特性，以及"维护即演化式开发"的定位来承载。[A-S1-01、A-S1-04、E]

---

## 五、二者关系与本任务共识

本任务的核心判断是两条，下面把**既有观点**与**权威表述**逐条对应：

**观点 1：架构设计是软件工程全生命周期中最关键的杠杆。**

| 既有观点 | 权威对应 |
|---|---|
| 架构杠杆最大 | 架构是**质量属性的主要承载者**（performance / modifiability / security）[SEI；B-S1-04] |
| 架构决定后续成败 | 好架构**支持自身演化**；差架构是 cruft 增长主因，使交付更慢、缺陷更多[Fowler；B-S2-01] |
| 架构是根本性决策 | 架构 = 一组 significant / fundamental 决策，只有根本性决策才算[42010；SEI；B-S1-01/03] |
| 架构独立重要 | SWEBOK V4 把 Software Architecture 升为**独立知识域**[SWEBOK V4；B-S1-02] |

**观点 2：软件工程 = 对软件全生命周期（上线 / 弃用 / 重构）的管理，是"对抗熵增 / 对抗史山（技术债）"的持续过程。**

| 既有观点 | 权威对应 |
|---|---|
| 覆盖全生命周期（含弃用） | 12207 六阶段示例明确包含 **support 与 retirement**（支持与退役）[12207:2026；A-S1-03] |
| "重构"是生命周期一部分 | 维护分类含**预防性维护**；维护即"演化式继续开发"[SWEBOK V3；Lehman 1980；A-S1-01] |
| 对抗熵增 | Lehman **复杂度递增定律**：系统必须持续投入降低复杂度，否则质量下降[A-S4-01] |
| 对抗"史山"/技术债 | Cunningham 技术债隐喻 + Fowler 偿债主张；架构腐化（erosion/drift）[B-S2-03/02、B-S4-01] |
| "持续过程"而非一次性交付 | 12207 定义的是**过程**而非固定阶段；敏捷宣言主张持续交付与响应变化[12207；敏捷宣言 2001] |

**对齐后的统一表述**：

> 软件工程是一门以工程方法管理软件**完整生命周期**的学科；它天生与"熵增"作对——需求会变、依赖会旧、复杂度会涨。**架构设计是这场持久战中杠杆最大的一步棋**：它用一组根本性决策，锁定了系统的质量属性与未来的演化空间，从源头抑制技术债与架构腐化。

---

## 六、共识结论（可直接指导后续阶段）

1. **定义基线唯一**：软件工程采用 IEEE 610.12-1990 定义（经 SWEBOK / SEVOCAB 采纳）；架构采用 ISO/IEC/IEEE 42010:2022 与 SEI 双源定义。后续所有内容不得另立口径。
2. **全生命周期视角**：一切讨论以"概念→开发→运行→支持→退役"的完整周期为背景，拒绝"写完代码就结束"的狭义工程观。
3. **架构只看根本性与外部可见**：判断一个决策是否属于架构，用"是否影响结构、非功能特性、依赖、接口或构造技术"（ADR 判据）筛选。
4. **架构是权衡而非对错**：以 ATAM 式的 scenarios + risks/sensitivity/tradeoff 思维讨论架构，避免绝对化。
5. **质量属性有统一落点**：一律回到 ISO/IEC 25010:2023 九特性及其子特性，尤其是可维护性的五个子特性。
6. **演化是默认前提**：以 Lehman 定律与"维护即演化式开发"为基本假设，把技术债与架构腐化视为必须持续治理的对象。
7. **标准讲"过程"不讲"阶段"**：后续方法论应以"要做哪些事（过程）"组织，而非拘泥于固定的阶段顺序。
8. **版本以最新为准**：ISO 标准一律采用 `E-iso-standards` 核实的现行版（12207:2026、42010:2022、25010:2023、14764:2022、24765:2017），历史版本仅作沿革说明。

---

## 七、边界与未决

1. **"本质方法论 vs 具体方法细节"的边界留待阶段4**：本文只对齐"是什么 / 为什么"，具体方法（如何做架构决策、如何画图、如何评估）的取舍与组织，属于阶段4 的任务。本阶段不越界下结论。
2. **ISO 标准正文版权约束**：iso.org 对抓取返回 403，且标准正文受版权保护。本文所有标准定义均通过官方站点、SQuaRE 门户（iso25000.com）与 Wayback 快照**核对元数据与 scope 摘要**，**未下载、未引用标准正文全文**。[E-iso-standards；iso-access-notes]
3. **extensibility / evolvability 无标准级独立定义**：它们不是 ISO 顶层术语，权威地位由可修改性 / 灵活性 / 可复用性等子特性与演化定律承载。这是标准体系的既有限制，非本文缺漏。[A-S1-01、E]
4. **经典论文回源状态已更新（R 包）**：Royce 1970、Parnas 1998、Parnas 1972、Brooks 1987、Lehman 1996、POSA 官方样章、SWEBOK V4 官方页元数据均已回源核验（verified）；仅 Lehman 1980 为 abstract-only（IEEE 付费全文）。本文原先"经 Wikipedia 交叉转引、置信度按 medium 计"的表述作废，相关结论改为 high/verified，详见 `02-research/R-foundational-papers.md`。[R-gaps]
5. **12207:2026 定稿 scope 尚无快照**：版本与四组过程结构已核实，但完整 scope 文本暂标 medium。[E]
6. **勘误说明（2026-09-10，据 R 奠基文献包）**：
   - **① Lehman 定律条数**：本文曾有"Lehman 1980 的八条演化定律"表述，经回源校正——**1980 原文为 5 条**，"八条"完整表述最早成文于 Lehman 1996《Laws of Software Evolution Revisited》（第 6 条为 1991 年脚注、第 7/8 条 1996 首次发表）；"演化是常态"结论不变，引用统一改标 `Lehman 1980（5 定律）/ Lehman 1996（八定律复述）`。[R-XC-01；S4-PAP-03]
   - **② Brooks 本质复杂度四属性**：正确表述为 **essence（本质复杂度）的四个固有属性 complexity / conformity / changeability / invisibility**，而非"本质与偶然各四要素"；essence 与 accident 是另一维二分。[S4-PAP-01]
   - **③ Royce 1970 非瀑布宣言**：原文未出现 "waterfall" 一词，Figure 3/4 明确阶段间与非相邻步骤的迭代，并提出五步补救（含 STEP 3 "DO IT TWICE"）。[S4-PAP-04；R-XC-05]
   - 来源：`02-research/R-foundational-papers.{json,md}`。
