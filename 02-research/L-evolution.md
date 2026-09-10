# 演化与弃用（Evolution & Deprecation）——权威源摘要

> 配套证据包：`L-evolution.json`；信源 24 条（S1=3、S2=13、S3=5、S4=3）；定义 16 条、findings 22 条、演化机制 6 条、原则↔反例 11 对、勘误 5 条。

## 一、核心结论

**1. 重构。** Fowler 给出硬判据：重构是“不改可观察行为（observable behavior）而改变内部结构”的操作，这是它与重写/改功能的分界（S2-04）。Refactoring 2nd ed 官方目录共 **68 个 refactorings**（第一版 10 个移除、新增 17 个），以 basic/moving-features/organizing-data 等标签组织（S2-05/S2-08）。**code smell** 是深层问题的表层迹象、可嗅探但非结论，是重构的启发式信号（S2-06）。

**2. 技术债。** 源自 Cunningham OOPSLA'92“首次交付如负债”（S2-02）；Fowler 强调利息按“修改该代码”触发而非时间累积——crufty 但稳定的代码可不动，高频变更区需零容忍（S2-01）。技术债应以“审慎/鲁莽 × 有意/无意”象限分诊，争论重点是债是否审慎（S2-03）；已发展为可识别/度量/跟踪/偿还的实践（IEEE Software, S4-03）。

**3. 架构腐化。** Perry & Wolf（1992）原始区分：**erosion=架构违规（violations）→脆化**；**drift=对架构不敏感→不适应性**（S2-11）。Li et al.(2022) 系统映射指出成因兼有技术与非技术因素，表现含违规与结构问题并影响质量与演化（S4-01）。Lehman 定律提供理论根据：不持续适配→满意度下降、不显式维护→复杂度递增、不严格维护→质量下降（S4-02）。

**4. 演进式架构。** Ford 等定义“支持有引导的增量变更作为多维度第一原则”，把可演化性作为一等 -ility；**架构适应度函数**对架构特性做客观完整性评估，可用 tests/metrics/monitoring 实现，并纳入部署流水线分阶段执行（S2-12/S2-13）。分类含 triggered/continual、atomic/holistic 等（S3-01/S3-02）。

**5. 遗留改造。** Feathers：遗留代码=“没有测试的代码”；**seam**=不改该处代码即可改变其行为的位置（预处理/链接/对象接缝）；**特征测试**对比新旧整体行为、只验证“是否变了”（S2-09/S2-10）。现代化首选 **strangler fig** 渐进迁移，反对整机重写（S2-07）。

**6. 弃用。** 弃用=劝阻使用并预示淘汰，但替换/移除非必需或紧急（S1-03）；标准信号有 Deprecation 头（RFC 9745）与 Sunset 头（RFC 8594）；semver 以 MINOR/MAJOR 区分“弃用/破坏”（S3-05）。厂商基线：Microsoft 需客户行动至少提前 30 天、停止支持前至少 12 个月通知（S3-04）；Google AIP-180 把 API 视为契约并给出兼容性清单（S3-03）。

## 二、演化机制表（信号 → 手段 → 权衡 → 反例）

| 机制 | 信号 | 手段 | 权衡 | 反例 |
|---|---|---|---|---|
| 重构 | 坏味道；变更成本上升 | 小步行为保持变换（68 手法）；测试安全网 | 前期投入、错误抽象、无测试即风险 | 以“重构”改行为；无测试直接重构 |
| 技术债 | 因 cruft 多花的时间（利息） | 象限分诊；逐步还本；高频区零容忍 | 无法客观度量；隐喻易被滥用 | 债当永不偿还许可；对稳定 crufty 码过度清理 |
| 架构腐化 | 违规（erosion）/不敏感（drift） | 风格约束、一致性检查、fitness functions、ADM/ATAM | 治理成本；工具漏掉非技术成因 | 只上工具忽视组织成因；约束过严僵化 |
| 演进式架构 | 目标独立变化、悄然漂移 | fitness functions + 增量变更 + 冲突识别 | 维护成本、属性互斥（agility↔stability） | 一次性检查不持续；约束过强 ossify |
| 遗留改造 | 无法打补丁、缺测试 | seam + 特征测试 + strangler fig | 特征测试冻结缺陷；周期长需组织配套 | 整机重写多数失败；无安全网改遗留码 |
| 弃用/日落 | 有更优替代、维护负担 | Deprecation/Sunset 头 + semver 分级 + 通知期 + 迁移指引 | 弃用≠移除；移除属破坏性 | 无通知直接移除；只弃用不移除；无替代即弃用 |

> 另附 11 条「原则↔反例」配对（见 JSON `principles_counterexamples`），满足“每条原则配 ≥1 反例”专项门控。

## 三、关键信源

- **S1（标准）**：ISO/IEC/IEEE 14764:2022（维护含退役/处置）、IETF RFC 9745（Deprecation 头）、RFC 8594（Sunset 头）。
- **S2（经典/作者）**：Fowler（TechnicalDebt / TechnicalDebtQuadrant / DefinitionOfRefactoring / CodeSmell / StranglerFig / Refactoring 2nd ed）、Cunningham（OOPSLA'92）、Perry & Wolf（1992）、Feathers（WELC 章节 + 博客）、Ford 等（Building Evolutionary Architectures 官方页 + 官方样章）。
- **S3**：Thoughtworks（fitness function 文章 + Tech Radar）、Google AIP-180、Microsoft Modern Lifecycle、semver.org。
- **S4**：Li et al.(2022) 侵蚀系统映射、Lehman(1980) 演化定律、Kruchten et al.(2012) 技术债。

## 四、勘误（常见误记 vs 核实值）

1. 技术债利息**不随时间累积**：只在修改该代码时触发（Fowler, S2-01）。
2. **重构 ≠ 重写/清理**：以“不改变可观察行为”为硬判据（S2-04）。
3. **erosion ≠ drift**：前者违规、后者不敏感（Perry & Wolf, S2-11）。
4. **弃用 ≠ 移除**：弃用是劝阻与预示，移除属破坏性变更（S1-03）。
5. 演进式架构/适应度函数思想根基更早（Lehman 1980、Perry&Wolf 1992、CD 实践），Ford 等 2017 才系统化命名。

## 五、未决问题（gaps）

1. O'Reilly《Building Evolutionary Architectures》正文 403 未回源；第二版新增的其余 fitness function 分类（temporal/intentional 等）未经一手核实，未列入。
2. Refactoring 2nd ed、WELC 书本体受版权未回源，仅用作者官方页 + 官方章节节选 + 公开目录；页码级引用待用户提供合法本地副本。
3. ISO 14764:2022 正文付费 + iso.org 403；退役/处置过程范围经 E 包快照核验，维护类型完整清单未逐条获取。
4. 架构腐化的量化检测工具清单（ArchUnit/Sonargraph/Structure101 等）与 Li et al. 全文未展开，需专项补齐。
5. 特征测试术语主要归功 Feathers，独立第二源偏弱；“软件腐烂/软件熵”权威一手定义未落实。
6. Deprecation/Sunset 的工程采纳率与具体迁移案例缺多源量化数据。
7. ADR supersede 机制与弃用策略的衔接留给 O 域（方法论主干）统一裁决。
