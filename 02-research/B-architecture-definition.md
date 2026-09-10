# 何为架构设计（Software Architecture & Design）——权威源摘要

> 配套证据包：`B-architecture-definition.json`；信源 27 条（S1=7、S2=18、S3=1、S4=1）。

## 一、核心结论

**1. 架构的定义（双源交叉）。** 国际标准 ISO/IEC/IEEE 42010:2022 将 architecture 定义为「系统在环境中的根本性概念或属性，体现于其元素、关系以及设计与演化的原则之中」，并强调架构是抽象的（概念或感知），记录它的工件才叫 **architecture description**。SEI 的经典定义（Bass/Clements/Kazman）则描述为「系统的单个或多个结构，由软件元素、元素的**外部可见属性**及元素间关系构成」。二者共同点：架构聚焦根本性（significant/fundamental）内容，架构只关心元素的 public 接口，内部实现细节不属于架构。Fowler/Johnson 的实用判据更直白——架构是「the important stuff. Whatever that is」。

**2. 架构与设计、需求的关系。** 42010 指出：架构**向外**关注「系统及其环境」，设计在系统边界确定后**向内**关注；架构抑制与交互无关的实现细节。架构是「一组重大决策」（Kruchten/RUP），只有根本性决策才属于架构。这些决策应被记录为 **ADR**：Nygard 定义 ADR 记录影响结构、非功能特性、依赖、接口或构造技术的决策，格式含 context/decision/consequences；Fowler 补充其编号、状态（proposed/accepted/superseded）与「被取代而非改写」的纪律。

**3. 质量属性与评估。** ISO/IEC 25010 质量模型是产品评价体系的基石：质量=系统满足干系人已声明与隐含需求的程度，并细分为特性与子特性（如 maintainability 含 modularity/reusability/analysability/modifiability/testability）。SEI 的 **ATAM** 是权威评估方法：由 business drivers 与架构引出 scenarios 与 decisions，分析产出 risks、non-risks、sensitivity points、tradeoff points 并归纳为 risk themes。

**4. 架构风格与模式。** Garlan & Shaw 给出组件-连接件-配置框架与风格分类（管道-过滤器、数据抽象/OO、事件驱动/隐式调用、分层、仓库、解释器），每种风格均有权衡。工程模式层面：分层（presentation/domain/data，PoEAA）、MVC（Reenskaug 1978/79，Fowler 释为一组原则）、微服务（Fowler & Lewis 2014）、CQRS（Greg Young，Fowler 警示其对多数系统引入 risky complexity）、Microkernel（PoSA）。

**5. 经典著作观点。** Clean Architecture（Martin）：同心圆 + **依赖规则**（源码依赖只能向内）。APoSD（Ousterhout）：设计根本目标是易理解易修改，**complexity** 主要来源于 information，评估标准是能否降低复杂度；强调 deep/shallow 与 abstraction。DDD（Evans）：**bounded context** + **ubiquitous language** 是战略设计核心。Fowler：好架构支持自身演化且与编程深度交织。

**6. 演化与对抗设计腐化。** Ward Cunningham 1992 提出**技术债隐喻**：首次交付代码如负债，及时重写可加速开发，未偿则成为利息；Fowler 释义为内部质量缺陷带来的额外变更成本。**架构腐化（erosion/drift）** 表现为架构违规与结构问题并损害质量与演化（Li et al. 2022 系统映射）。

**7. 可维护性/可扩展性落点。** 落点即 ISO 25010 的 modularity（改一个组件对其它组件影响最小）等子特性；Parnas (1972) 的**信息隐藏**（按隐藏可变设计决策划分模块）是其奠基思想；权衡则体现于风格选择与 ATAM 的 sensitivity/tradeoff points。

## 二、关键信源

- **S1**：ISO/IEC/IEEE 42010:2022（定义、概念模型）、SWEBOK V4.0（新增 Software Architecture KA）、SEI（定义手册、架构总览、ATAM）、ISO/IEC 25010。
- **S2**：Fowler（Software Architecture Guide、TechnicalDebt、Who Needs an Architect、PoEAA、Microservices、Layering、CQRS）、Ward Cunningham（OOPSLA'92）、R. C. Martin（Clean Architecture）、Ousterhout（APoSD）、Eric Evans（DDD Reference）、Nygard（ADR）、Garlan & Shaw、Parnas (1972)、Reenskaug (MVC)。
- **S3/S4**：Azure Architecture Center（CQRS/Event-driven）；Li et al. (2022) 架构腐化系统映射。

## 三、未决问题

1. 42010:2022、25010:2023 标准正文付费且 iso.org 拒绝抓取，定义经官方站点/门户核验，未见全文。
2. SWEBOK V4 的架构章正文未下载，仅核验 KA 结构与主编（Rich Hilliard）。
3. PoSA Vol.1（Microkernel）本体未回源，该条标 cited/medium；Fowler 演进式架构专文 URL 已 404，待补一手文本。
4. 架构腐化定义主要依赖单一 S4 综述，Whiting & Andrews (2020) 仅取元数据。
