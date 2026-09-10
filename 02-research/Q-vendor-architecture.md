# Q 域：主流厂商架构体系（S3）证据摘要

> 契约：`00-plan/contract.md` ｜ 访问日期：2026-09-10 ｜ 配套机器可读版：`Q-vendor-architecture.json`
> 范围：补齐 GAP-07（AWS）、GAP-08（Google Cloud）、GAP-09（ThoughtWorks）。**S3 = 官方厂商体系，非国际标准。**

## 一、核心结论

三大体系均为**厂商立场的方法论**，权威性来自"官方出处"而非中立性：

- **AWS Well-Architected Framework**（文档出版日 2024-11-06）：六大支柱 Operational Excellence、Security、Reliability、Performance Efficiency、Cost Optimization、Sustainability（2021-12 新增）。总纲含 6 条通用设计原则（容量不猜测、按生产规模测试、自动化、演进式架构、数据驱动、game day）。官方明示架构评审是"建设性对话，不是审计"。
- **Google Cloud Well-Architected Framework**（原 Architecture Framework，页面复核 2026-01-28）：六支柱为 Operational Excellence、Security/Privacy & Compliance、Reliability、Cost Optimization、Performance Optimization、Sustainability，另有 AI/ML 与 Financial Services 两个跨支柱 perspective。核心原则 5 条（为变更而设计、文档化架构、简化并用托管服务、解耦、无状态）。Sustainability 于 2026-01-28 升为完整支柱。
- **ThoughtWorks Technology Radar**（现行 Vol 34 / 2026-04）：用四象限（Techniques/Platforms/Tools/Languages & Frameworks）分类 blip，用四环表示采用推荐度。官方明确"有观点、不追求全面、不接受厂商付费影响"。

## 二、三体系对照表

| 维度 | AWS WAF | Google Cloud WAF | ThoughtWorks Radar |
|---|---|---|---|
| 性质 | 厂商架构框架 | 厂商架构框架 | 咨询机构观点快照 |
| 组织维度 | 6 支柱 + 6 通用原则 | 6 支柱 + 5 核心原则 + 2 视角 | 4 象限 × 4 环 |
| 第四环/末项 | — | — | **Caution（旧称 Hold）** |
| 更新节奏 | 版本化白皮书 | 持续更新 | 每半年一期 |
| 关键用途 | 架构评审/改进 | 云迁移与运营设计 | 技术采用取舍参考 |
| 立场风险 | 绑定 AWS 服务 | 绑定 Google 服务 | 主观、时效短 |

## 三、立场与适用边界提示

1. **厂商绑定倾向**：两大云框架均把"使用托管服务（use managed services）"写成原则，客观上引导采纳各自服务，存在锁定偏向，不可当中立标准。
2. **分类法不稳定**：Google 于 2024-08-27 移除 System Design 类别；AWS 2021 才增 Sustainability；说明厂商框架随产品与市场调整，稳定性弱于 ISO 系列。
3. **命名/版本陷阱**：ThoughtWorks 第四环在 Vol 33→Vol 34（2025-11→2026-04）由 "Hold: Proceed with caution" 更名为 "Caution: Proceed with care"；任务原表述 Adopt/Trial/Assess/**Hold** 已过时，引用须注明版本。Google 框架的 "Well-Architected" 命名亦是向 AWS 靠拢的品牌变更。
4. **时效性**：Radar 的 blip 默认只留一期，属当期观点而非长期定义源。

## 四、未决问题（gaps）

- 未取得**独立于厂商的第三方权威解读**（Gartner/InfoQ/同行评审），关键定义实为"官方页 + 官方深度文档"两源，非严格独立交叉验证，须明示立场。
- AWS 各支柱 design-principles 独立网页 slug 不稳（部分 302），本包以官方白皮书 PDF 为准。
- Google 框架改名精确日期、ThoughtWorks 第四环更名动因，均缺官方公告，仅由官方页面/PDF 对比推得。
- 三者均属 S3，**不得作 S1 国际标准引用**；本包不做标准级质量属性映射。
