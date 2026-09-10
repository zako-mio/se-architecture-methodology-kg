# O 域 · 方法论主干综合（11 维权衡骨架 + 原则↔反例 + 术语裁决）

> 对 F–N 证据包做二次归纳，不新增外部检索。骨架复用 0813「架构权衡思维」四问（有什么可权衡 / 如何权衡 / 为何如此权衡 / 你的场景），并将原 RAG 场景 11 维泛化为软件工程/架构主干权衡轴；每条 source_id 均取自 F–N。

## 一、11 维权衡骨架（泛化版）

| # | 泛化主题（legacy_dim 溯源） | 核心权衡 | 母库/架构落点 | 主要域 |
|---|---|---|---:|---|
| 1 | 正确性/收益 vs 完备性/覆盖（D1 精度vs召回） | 漏失不可补救 > 噪声可过滤，代价不对称 | 覆盖宁多、门控精筛 | F/I/K/H/M |
| 2 | 准入/触发时机（D2 摄取时机） | 质量门槛 vs 便利性 | 半自动 + 决策门 | F/I/J/K/L |
| 3 | 技术/风格/组件选型（D3 存储选型） | 够用就好，勿过度 | 轻量自建 + ATAM 排序 | G/H/J/M/N |
| 4 | 能力-成本-速度三角（D4 Embedding选型） | 一次性 vs 持续成本 | 先量化，优化持续成本 | I/J/K/N |
| 5 | 成本/资源 vs 质量成效（D5 成本vs质量） | 质量属性间冲突、100% 非正解 | tradeoff point + 错误预算 | G/H/J/K/L/M |
| 6 | 粒度与边界（D6 检索粒度） | 变更波及面 vs 理解成本 | 按信息隐藏切分、与组织同步 | G/H/M/N |
| 7 | 自动化方式（D7 抽取方式） | 规则/模板 vs 模型生成 vs 人工 | 模板为主、模型辅助、可执行治理 | F/I/J/L/N |
| 8 | 复杂度阶梯（D8 图谱时机） | 能用≠该用，简单优先 | 简单可工作架构起步，按需演进 | G/H/J/K/L |
| 9 | 简单/透明 vs 可维护（D9 简单vs可维护） | 理解成本是真实成本 | 组件最小化、按关注点选视图 | G/H/L/M/N |
| 10 | 演化与一致性（D10 增量更新） | 增量 vs 全量、变更/删除传播 | 增量+契约、fitness function、strangler fig | F/G/I/J/L |
| 11 | 度量与反馈闭环（D11 评估体系） | 不度量 vs 人工 vs 自动；Goodhart | 基线+客观门控+DORA/SLO 闭环 | G/I/K/L/N |

**跨域原则↔反例**：合并 H/L/N 结构化字段与 F/I/J/K/M/G 派生条目，去重后共 **36 条**（每条 ≥1 反例）。代表性配对：信息隐藏↔脆弱基类；封装↔抽象泄漏；DRY↔错误抽象；YAGNI↔推测性泛化；设计模式↔模式自身坏味道；小步重构↔big rewrite；技术债↔过度清理/永不偿还；fitness function↔一次性检查；弃用信号↔无通知移除；康威定律↔partial mirroring；DORA↔Goodhart 指标；测试金字塔↔冰淇淋反模式；断路器/重试↔重试风暴；不可变基础设施↔配置漂移；蓝绿/金丝雀↔schema 未 expand/contract。

## 二、术语裁决摘要

共裁决 **23 条**（settled 19 / disputed 4）。统一口径示例：*software engineering* 采 IEEE 610.12/SWEBOK；*software architecture* 采 ISO 42010:2022 且强调架构≠架构描述（AD）；*maintainability* 采 25010:2023（子特性 modularity/reusability/analysability/modifiability/testability）；*modularity* 采 25010（改动影响最小）+ Parnas 责任分配；*technical debt* 采 Fowler（额外变更成本）并附两条限定（利息按变更触发；非道德评判）；*coupling/cohesion* 为多维、无普适阈值；*erosion* 与 *drift* 严格区分；*deprecation/sunset/removal* 三级区分；*DORA* 现行五指标（旧四键标版本）；*sensitivity point* ≠ *tradeoff point*。

**disputed 4 条**：*extensibility*（无 ISO 顶层术语，暂用 SEI 操作定义）、*evolvability*（无共识定义，暂用学术定义，与 extensibility 边界模糊）、*microservice*（原作者声明无精确定义）、*observability 三支柱*（工程口语，非 OTel 官方术语，改用 OTel 信号清单）。

## 三、Gaps

- 11 维泛化为 0813→主干的主观映射（medium），legacy_dim 仅溯源、非等价。
- 需求优先级方法/追溯、现代风格权衡矩阵（Richards & Ford）、erosion 检测工具清单、29119 正文、团队-架构耦合 S1 标准均缺，待阶段4 或专项回源。
- extensibility/evolvability 无权威定义、耦合无普适阈值，术语裁决只能给推荐口径。
