# M · 质量模型与 ilities（摘要）

> 证据包：`M-quality-ility.json`；访问日期 2026-09-10。iso.org 直连/代理均 403（E 包已证），标准元数据经 ISO OBP 片段 + iTeh 官方样页 + iso25000 门户 + SEI 官方报告四路核验。境外走代理。

## 核心结论

1. **九特性口径以 2023 版为准**。现行 ISO/IEC 25010:2023 产品模型为 **9 特性**，2011 版的 8 特性模型已废止，且由 **25002:2024（总览与使用）+ 25019:2023（使用质量模型）+ 25010:2023（产品模型）三者联合取代**（25019 前言原文，闭合 E 包缺口）。高分信源交叉：ISO OBP 片段 / iTeh 官方样页 / iso25000 / SEI。
2. **使用质量模型已重构**：ISO/IEC 25019:2023 由 2011 版 5 特性（effectiveness/efficiency/satisfaction/freedom from risk/context coverage）改为 **3 特性：beneficialness、freedom from risk、acceptability**；context coverage 被移除。
3. **extensibility / evolvability 均无标准顶层术语**。标准侧最近似落点为 Flexibility（adaptability/scalability）与 Maintainability 子特性（modifiability/analysability）；SEI 将 extensibility 作为独立质量属性系统研究，学术界（Rowe/Leaney/Lowe 1994；Breivold 综述）给出 evolvability 独立定义。二者常被工程口语与 flexibility/maintainability/adaptability/modifiability 混用。

## 九特性表（ISO/IEC 25010:2023 产品质量模型）

| # | 特性（EN / 中文） | 定义要点 | source |
|---|---|---|---|
| 1 | Functional Suitability / 功能适合性 | 在指定条件下提供满足明示与隐含需求的功能 | S2-M01 |
| 2 | Performance Efficiency / 性能效率 | 在规定时间与吞吐内完成功能且高效用资源 | S2-M01 |
| 3 | Compatibility / 兼容性 | 与其产品共享环境并交换信息 / 互操作 | S2-M01 |
| 4 | Interaction Capability / 交互能力 | 指定用户在多种使用情境下经 UI 交互完成特定任务（取代 2011 Usability） | S2-M01 |
| 5 | Reliability / 可靠性 | 指定条件下规定时间内执行规定功能 | S2-M01 |
| 6 | Security / 信息安全 | 抵御恶意攻击并保护信息与数据访问 | S2-M01 |
| 7 | Maintainability / 可维护性 | 有效高效地改进、纠正或适配环境与需求变更 | S2-M01 |
| 8 | Flexibility / 灵活性 | 适配需求、使用情境或系统环境的变化（2011 Portability 改名） | S1-M01 |
| 9 | Safety / 安全（人身/环境） | 避免危及生命、健康、财产或环境的状态（2023 新增） | S2-M01 |

**可维护性五子特性**：modularity、reusability、analysability、modifiability、testability（S2-M01/S1-M01）。**Flexibility 四子特性**：adaptability、scalability、installability、replaceability。

## ilities 归位表（标准术语 vs 工程口语）

| 工程口径 | 标准落点 | 状态 |
|---|---|---|
| maintainability | ISO 25010:2023 顶层特性 | 标准术语 |
| modularity / reusability / analysability / modifiability / testability | Maintainability 子特性 | 标准术语 |
| flexibility / adaptability / scalability / installability / replaceability | ISO 25010:2023 顶层 / Flexibility 子特性 | 标准术语 |
| portability | ISO 25010:2011 顶层 | 已废止（改名 Flexibility） |
| usability（产品侧） | ISO 25010:2011 顶层 | 已废止（改名 Interaction Capability） |
| usability（使用侧） | 25019 beneficialness 的子特性 | 标准术语（与产品侧不同概念） |
| quality in use | ISO/IEC 25019:2023（3 特性） | 标准术语（重构） |
| **extensibility** | 无顶层术语；近似 Flexibility + modifiability；SEI 独立属性 | 工程界（SEI CMU/SEI-2022-TR-002） |
| **evolvability** | 无顶层术语；近似 Maintainability + Flexibility | 学术/工程界（Rowe 1994；Breivold 综述） |
| changeability | 无独立术语，常与 Flexibility 混用 | 口语，需消歧 |

## 质量属性→战术映射（SEI）

| 质量属性 | 战术分类 | source |
|---|---|---|
| Availability | Fault Detection / Fault Recovery / Fault Prevention | S1-M05 |
| Modifiability | Defer binding time / Localize changes / Prevent ripple effects | S1-M06 |
| Extensibility | 12 项（Encapsulate, Defer binding, Discover service, Specialized interfaces, Segment deployments…） | S1-M04 |
| Performance / Security / Testability / Usability | 资源需求与仲裁 / 抵御-检测-恢复 / 控制与观测状态 / 运行时与设计时战术 | S2-M02 |

## 未决问题（gaps）

- 25010 九特性条款原句受 iso.org 403 限制，主要取自 iso25000（S2），非一手逐字核实。
- 25019 第三特性 acceptability 仅由学术源（DIS 阶段论文）确认，标 medium。
- 25002 仅核验样页 Scope，框架/本体章节未读。
- 战术目录随报告版本演化，未逐版比对 SAiP 4e。
