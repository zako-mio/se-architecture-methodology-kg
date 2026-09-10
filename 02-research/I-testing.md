# I 证据包：软件测试方法论

- 采集日期：2026-09-10 ｜ 采集角色：软件测试研究员（子Agent）｜ 信源 33 条（S1 标准 10 + S1 官方 6 + S2 13 + S3 3）
- 契约：`00-plan/contract.md`；执行依据：`stage2-search-plan.md` §2 I 域；信源缺口：GAP-12（本域已重点加密）

## 一、核心结论

**1）测试层次。** ISO/IEC/IEEE 29119 系列（现行共 8 部分：Part 1/2/3/4/5/6/11/13）规定测试过程与文档；ISTQB CTFL v4.0.1 把测试层次明确为五个，比常见的"单元/集成/系统/验收"四层更细。29119 已于 2014 年引发部分测试社群反对（过度文档化、排除 context-driven testing），选型时须权衡。

**2）测试金字塔与反模式。** Fowler(2012) 与 Google Testing Blog(2015) 口径一致：低层单元测试应最多，端到端应最少；Google 给出 70/20/10 经验配比，并命名两种反模式——**冰淇淋甜筒（ice cream cone / inverted pyramid）**与**沙漏（hourglass，缺中间集成层）**。

**3）测试驱动开发。** TDD 由 Kent Beck 于 1990 年代末作为 XP 的一部分提出，核心为 Red-Green-Refactor；ISTQB 将 TDD/ATDD/BDD 并列，均属 shift left。

**4）可测试性。** ISO/IEC 25010:2023 把 Testability 列为 Maintainability 子特性（建立测试准则并执行测试判定的有效性与效率）；SEI 把可测试性视为架构级质量属性，用 stimulus/environment/response 通用场景 + 战术表达。

**5）质量门控与 CI。** Fowler 的 CI 十项实践中"使构建自测试"是门控原点；SonarQube 质量门控以量化条件判定"是否可发布"并阻断 CI/PR；DORA 指标已从四指标演进为五指标，且证明速度与稳定性非取舍关系。

## 二、测试层次对照表

| 层次 | 焦点 | 执行者/环境 | 主要来源 |
|---|---|---|---|
| component / unit（组件/单元） | 隔离测试单个组件 | 开发者/开发环境，需 test harness | ISTQB S1-OFF-11；Fowler UnitTest |
| component integration（组件集成） | 组件间接口与交互 | 开发者/CI（bottom-up/top-down/big-bang） | ISTQB S1-OFF-11 |
| system（系统） | 整个系统整体行为、端到端功能+非功能 | 独立测试团队/代表性环境 | ISTQB；SEI Taxonomy |
| system integration（系统集成） | 本系统与外部系统/服务接口 | 类生产环境 | ISTQB S1-OFF-11 |
| acceptance（验收） | 验证部署就绪、满足业务需要 | 预期用户（UAT/运维/合同/法规/α/β） | ISTQB；Fowler Practical Pyramid |

> 对照：Google 用 Small/Medium/Large（数据驱动尺寸）近似映射 unit/integration/e2e；Fowler 用 unit / subcutaneous(service) / UI 三层。

## 三、可测试性战术（SAiP 4e Ch.12）

SAiP 4e 第 12 章结构为：12.1 Testability General Scenario、12.2 Tactics for Testability、12.3 Tactics-Based Questionnaire、12.4 Patterns for Testability。SEI 的通用场景三要素为 **stimulus / environment / response**。可测试性战术通常归为两类方向：**控制与观察系统状态**（便于注入刺激、观测响应）与**限制复杂度**（限制结构性复杂度、限制非确定性）。*具体战术条目须以书本体为准（本包未回源，标记 medium，见 gaps）。*

## 四、质量门控与 CI 检查清单（来源合成）

1. 单一版本控制主线 + 每次推送触发自动化构建（Fowler CI）。
2. **使构建自测试**：构建内含自动化测试套件，失败即红。
3. 立即修复坏构建；保持构建快；测试在类生产环境克隆中运行。
4. 质量门控：对 new code / overall code 设量化条件，未达标则阻断构建与 PR 合并（SonarQube）。
5. shift left：把测试左移（Traditional/Incremental/Agile-DevOps/Model-Based 四种），因 45%–65% 缺陷在需求/架构/设计阶段引入。
6. 交付效能度量：DORA 五指标（change lead time、deployment frequency、failed deployment recovery time、change fail rate、deployment rework rate），关注趋势而非设为目标（Goodhart 定律）。

## 五、未决问题（gaps）

- ISO 29119 正文、SWEBOK V4 Ch.5 正文因 WAF 403/登录墙不可得，定义以官方摘要 + ISTQB/SWEBOK 转述构建。
- Cohn 2009 原始三层金字塔未回源；SAiP 可测试性战术枚举未逐条回源；Continuous Delivery/Accelerate 正文为付费。
- 29119-13:2022 未提取到 ISO 摘要；SEI 历史质量属性战术公开页面已下线。

> 全部条目可溯源；每条 finding 带 `source_ids`，关键定义均 ≥2 独立源交叉验证。erratas 记录了 29119 部分数（8 非 5）、29119-1 标题、DORA 四→五指标、25010:2023 特性更名四处勘误。
