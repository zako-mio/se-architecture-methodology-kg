# G · 架构设计证据包摘要

> 配套 `G-architecture.json`；生成日期 2026-09-10；来源分级见契约 §3。

## 核心结论

**概念模型（ISO/IEC/IEEE 42010:2022）**：架构是抽象的「根本性概念或属性」，记录它的工件才叫架构描述（AD）；42010 只规定 AD 的**表示**，不规定过程/方法/记号。其元模型以 Entity of Interest、Stakeholder、Concern 为起点，用 **Viewpoint（约定集）→ View（按约定表达）→ View Component/Model Kind** 分层，并以 Correspondence Rule 强制跨视图关系；Architecture Decision 与 Architecture Rationale 也被纳入 AD（S1-07/S1-08）。2022 版新增 Stakeholder Perspectives、Architecture Aspects，主体泛化为 Entity of Interest（S1-07）。

**架构↔设计↔需求边界**：架构向外关注「系统及其环境」，设计在边界确定后向内关注（S1-01）；架构只含 significant/fundamental 决策，且只关心元素的外部可见属性（S1-01/S1-03）。SWEBOK V4 将 Architecture 与 Design 分设为两个 KA（S1-02）；需求（business drivers + 质量属性）经场景驱动架构分析（ATAM，S1-05/S1-11）。

**架构风格与权衡**（S2-14/S3-02）：

| 风格 | 收益 | 代价/约束 |
|---|---|---|
| Pipes & Filters | 可组合理解、复用、易维护、可并发、可做吞吐/死锁分析 | 倾向批处理、不利交互式、双流对应难、统一数据格式损性能 |
| Event-based / 隐式调用 | 强复用、易演化（替换组件不改接口） | 放弃计算控制、顺序不可知、可能依赖共享仓库、正确性推理难 |
| Layered | 抽象递增设计、改动仅影响相邻层、可换实现复用 | 非所有系统易分层、性能或需跨层紧耦合、难找抽象层 |
| Microservices | 独立部署、故障隔离、高频更新、易引新技术 | 服务发现/数据一致性/分布式管理复杂度高，需成熟 DevOps |
| Event-driven | broker 解耦、近实时、横向扩展、故障隔离 | 投递保证、事件排序、最终一致性 |
| N-tier / Web-Queue-Worker | 易理解/迁移、前后端独立扩缩 | 横向分层改动扩散、易变单体 |

结论：无普适最优风格，约束带来的收益与挑战并存，需按子域权衡（S3-02）。

**ADR**：Nygard 原始模板 = Title/Context/Decision/Status/Consequences，1–2 页、单调编号、被取代而非改写（S2-09）；Fowler 补充 inverted pyramid、备选方案利弊、置信度与重评触发条件（S2-10）。

**架构文档化（V&B）**：文档化相关视图 + 跨视图信息（how-what-why）；视图分 Module / Component-and-Connector / Allocation 三类，另文档化接口与行为（S1-09/S2-19）。**ATAM**：九步 + utility tree，产出 risk/non-risk、sensitivity point、tradeoff point 并归纳为 risk theme（S1-11/S1-05）。

## 未决问题（gaps）

- 42010:2022 正文付费 + iso.org 403，概念模型依赖编辑站与 Wayback（未读全文）。
- V&B 书籍本体未获取，三类视图下的完整 viewtype 清单未逐一回源。
- SWEBOK V4 架构/设计章正文未下载；ATAM 无单一最新规范（risk themes 仅见 2018 fact sheet）。
- ISO 42020/42030 版本 scope 仅由官方新闻页核验；POSA 标 cited；未纳入现代风格权衡矩阵与 S4 实证。
