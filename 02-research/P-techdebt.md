# P 域：技术债（Technical Debt）证据包摘要

> 补 GAP：矩阵标注「技术债域无独立证据包」。本包与 B/L/M 包复用同名来源（见 `cross_ref`），source id 采用 `P-` 前缀。

## 核心结论

1. **隐喻原义**：技术债由 Ward Cunningham 在 OOPSLA'92（WyCash 报告）提出——「Shipping first time code is like going into debt」，小额债务及时以重写（重构/consolidation）偿还可加速开发，危险在于债不被偿还。Fowler 将其操作化为「内部质量缺陷（cruft）导致的未来变更额外成本」。
2. **本金-利息模型**：利息＝每次修改该代码多花的时间，本金＝一次性清理 cruft 的投入。关键破绽：利息只按「修改」触发、不按时间累积，故稳定而少改的 cruft 可暂不处理，高频变更区需 zero-tolerance；因生产率不可客观度量，通常最优是**逐步偿还本金**。
3. **四象限**：以 prudent/reckless × deliberate/inadvertent 分诊。有用的问题是「审慎还是鲁莽」，而非「算不算债」；prudent-inadvertent 债即使优秀团队也不可避免。
4. **类型学**：Li 等（2015，94 项研究）归纳 10 类 TD、8 类 TDM 活动、29 种工具，code-related 最受关注；Alves 等（2014）以本体组织类型与 indicators。架构债另有理论：由「大」设计决策造成，难识别、修复成本范围大、常被回避。
5. **度量**：SQALE 以生命周期期望为基准（9 原则 + 4 组件）提供客观/可复现/自动化的债务评估；SonarQube 将其操作化——technical debt（sqale_index）＝所有 maintainability issue 的 remediation cost 之和，TDR＝修复成本 /（每行开发成本默认 30 分钟 × LOC），maintainability rating A ≤5%…E ≥50%；并区分 overall/new code。工具指标差异大、有效性证据有限，不可当作债务真值。SATD 可从注释/commit/PR/issue 四源自动识别。
6. **清偿与治理**：重构以「不改变可观察行为」为硬判据；boy-scout/机会式重构小步持续、测试绿灯；架构债用 strangler fig 渐进迁移，避免整机重写（多数失败）。
7. **与架构腐化的关系**：架构侵蚀（违规）与漂移（不敏感）造成「越来越抗拒变更」，是架构层债务累积机制；Lehman 定律的复杂度递增/质量下降为其时间维根据。

## 债务类型 → 信号 → 度量 → 清偿手段（专项门控）

| 债务类型 | 信号 | 度量 | 清偿手段 | 反例 |
|---|---|---|---|---|
| 代码债 | code smells、复杂度上升 | code_smells、sqale_index、TDR、rating、SATD | 小步重构、boy-scout、新代码零债务门控 | 无测试直接重构/假重构 |
| 设计债 | 错误抽象、SOLID 违背 | design smells、maintainability 子特性、利息估计 | preparatory refactoring、重构到模式、逐步还本 | 否定 prudent 债/过度抽象 |
| 架构债 | 侵蚀与漂移、脆化、抗拒变更 | fitness functions、ATAM、架构异味索引 | strangler fig、架构重构、ADR、组织配套 | 只做工具合规、约束过严僵化 |
| 测试债 | 覆盖低、flaky、无安全网 | 覆盖率、测试坏味、特征测试 | 先补特征测试再重构、去 flaky | 无安全网改遗留码 |
| 文档债 | 文档缺失/过时、无 ADR | 覆盖度、SATD 来源、ADR 存量 | 轻量模块化 ADR（被取代而非改写） | 依赖永不更新的大部头文档 |
| 需求债 | 规格与实现差距 | 需求债 indicators、SATD | backlog 优先级化、增量澄清 | 把需求债当「已实现即完成」 |
| 构建/基础设施/过程债 | 构建慢/脆、手工发布、流程摩擦 | 构建时长/失败率、DORA 指标 | CI/CD 自动化、fitness functions 入流水线、弱化抑制重构的摩擦 | 长生命周期分支抑制机会式重构 |

**原则↔反例**另附 11 对（见 JSON `principles_counterexamples`）。

## 关键信源
Cunningham c2.com（P-S2-03）、Fowler bliki TechnicalDebt/Quadrant/DesignStamina/OpportunisticRefactoring（P-S2-01/02/04/05）、CMU/SEI（P-S1-01）、SonarQube 官方文档（P-S3-01/02）、SQALE 官网快照（P-S3-03）、IEEE Software 技术债专题（Kruchten，P-S4-01；Letouzey SQALE，P-S4-02）、Li 等 JSS 系统映射（P-S4-03）、Alves 等本体（P-S4-04）。

## 未决问题（gaps）
- Alves 本体正文付费，13 类类型逐条清单未取；治理表骨架主要依 Li(2015) 的 10 类与任务指定分类。
- 度量工具量化对比与需求债 SLR 正文付费，仅摘要级；生产率损失（P-S4-10）仅题录级（confidence=medium）。
- SQALE 官方方法定义文档已下线，9 原则/4 组件经 Wayback 核验，各 index 精确定义与阈值未逐条获取。
- 书籍正文（Refactoring/Legacy Code）受版权未回源，复用 L 包作者官方页面；架构腐化检测工具清单留给 G/O/F 域。
