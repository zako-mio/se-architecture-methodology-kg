# 权威知识地图 — 软件工程 / 架构设计方法论（0910 阶段1）

> 配套机器可读版：`knowledge-map.json`（158 条信源 / 9 大主题域 / 12 项缺口，其中 GAP-05/06/07/08/09 已回源处理）。
> 证据来源：A（SE 定义）、B（架构定义）、C（本地盘点）、D（书单）、E（ISO 元数据）、P（技术债）、Q（厂商体系）、R（奠基文献回源）。
> 生成：software-architect-subagent ｜ 访问日期：2026-09-10 ｜ 契约：`00-plan/contract.md`。

## 0. 使用说明

- **ID 规范**：`S1-STD-nn` 国际标准 ｜ `S1-OFF-nn` 官方知识体系/机构 ｜ `S2-BK-nn` 经典著作 ｜ `S2-WEB-nn` 权威作者文章 ｜ `S3-VEN-nn` 厂商架构中心 ｜ `S4-PAP-nn` 学术论文 ｜ `S4-COM-nn` 会议期刊 ｜ `L-*` 本地信源 ｜ `P-S1/S2/S3/S4-nn` 技术债域（P 包）｜ `R-XC-nn` 奠基文献回源交叉验证（R 包）。阶段2/3 一律以本 ID 引用。
- **分级**：S1 国际标准/官方知识体系（最高权威）＞ S2 经典著作/权威作者官方文章 ＞ S3 厂商 ＞ S4 学术；`LOCAL` 为本机可复用资产（工具/方法论/语料，非外部权威）。
- **去重**：A/B/D/E 重复信源已合并，证据出处写入 `evidence_ref`；**ISO 版本以 E 为准**。
- **版权红线**：标准正文与书籍本体永不进公开仓库，仅作核对/本地语料。

## 1. S1 国际标准（10）

| ID | 标准全名 | 版本/年份 | 状态 | 获取路线 |
|---|---|---|---|---|
| S1-STD-01 | ISO/IEC/IEEE 42010 Software, systems and enterprise — Architecture description | 2022（Ed.2） | 现行 60.60 | Wayback 快照 + iso-architecture.org；iso.org 403 |
| S1-STD-02 | ISO/IEC/IEEE 42010 — Architecture description | 2011（Ed.1） | 已撤销 95.99 | Wayback + committee.iso.org（版本对照用） |
| S1-STD-03 | ISO/IEC/IEEE 12207 Software life cycle processes | 2026（Ed.2） | 现行（2026-04） | Wayback（DIS 页）+ 2017 版替换公告；scope 待核 |
| S1-STD-04 | ISO/IEC/IEEE 12207 Software life cycle processes | 2017（Ed.1） | 已撤销 95.99 | Wayback ×2 + committee.iso.org（scope 逐字核验） |
| S1-STD-05 | ISO/IEC 25010 SQuaRE — Product quality model | 2023（Ed.2） | 现行（九特性） | Wayback ×2 + iso25000.com 门户 |
| S1-STD-06 | ISO/IEC 25010 SQuaRE — quality models | 2011（Ed.1） | 已撤销（八特性） | Wayback ×2（版本对照用） |
| S1-STD-07 | ISO/IEC/IEEE 14764 Software life cycle processes — Maintenance | 2022（Ed.3） | 现行 | Wayback ×2 |
| S1-STD-08 | ISO/IEC 14764 — Maintenance | 2006（Ed.2） | 已撤销 95.99 | Wayback（版本对照用） |
| S1-STD-09 | ISO/IEC/IEEE 24765 Vocabulary（SEVOCAB） | 2017（Ed.2） | 现行（待修订 90.92） | Wayback ×2 + committee.iso.org + PAS zip |
| S1-STD-10 | IEEE Std 610.12 Software Engineering Terminology | 1990 | 历史（定义沿用） | IEEE 403；经 SEBoK/SWEBOK V3 转引（cited） |

> 全部 ISO 元数据经 Wayback 快照 + committee.iso.org / iso25000.com 交叉核验；iso.org 因 WAF 对直连/代理/代理+UA 均返回 403（详见 `02-research/iso-access-notes.md`）。
>
> **技术债域（P 包）**：P-S1-02 复用本表 **S1-STD-05**（ISO/IEC 25010:2023 的 maintainability 特性），作为 TDR/SQALE 指标的标准落点，不另计标准数。

## 2. S1 官方知识体系 / 机构 / 门户（10）

| ID | 名称 | 机构 | 版本/年份 | 定位 |
|---|---|---|---|---|
| S1-OFF-01 | SWEBOK | IEEE CS（ISO/IEC TR 19759） | V3(2014,15KA)/V4(2024,18KA) | 知识体系基线；V4 新增 Software Architecture KA |
| S1-OFF-02 | SEI 架构定义 / 总览 / ATAM | CMU SEI | 2017-2018 | 架构经典定义与架构评估方法一手源 |
| S1-OFF-03 | SE2014 课程体系 | ACM & IEEE-CS | 2014/2015 | SE 学科范畴、软件特性与工程方法 |
| S1-OFF-04 | CS2023 SE KA | ACM/IEEE-CS/AAAI | 2023 | 编程 vs SE（时间/人员两维）、维护与演化 |
| S1-OFF-05 | ISO 25000 Portal | AENOR / iso25000.com | 2024 | 25010 九特性逐项定义核验门户 |
| S1-OFF-06 | NATO 1968 Garmisch 报告 | NATO Science Committee | 1969 | 学科起点、software crisis 原始记录 |
| S1-OFF-07 | 敏捷宣言 | 17 位作者 | 2001 | 范式转向第一手声明 |
| S1-OFF-08 | SEVOCAB 在线术语库入口 | ISO/IEC/IEEE | 2017 | 术语查询与标准来源标注 |
| P-S1-01 | Technical Debt: From Metaphor to Theory and Practice（SEI 资产页） | CMU / SEI | 2012 | 技术债域 S1 官方源；债需显式管理与 common backlog |
| R-XC-03 | An Overview of the SWEBOK Guide | SEBoK | accessed 2026-09-10 | 逐条交叉核验 V4 的 18 KA（含三个新增 KA）与 14764:2022 对齐 |

## 3. S2 经典著作 / 权威信源（35 著作 + P 包 10 + R 包 5）

**通论（6）**：S2-BK-01《Software Engineering at Google》[免费] ｜ S2-BK-02《人月神话》｜ S2-BK-03《代码大全》｜ S2-BK-04《软件工程 Sommerville》｜ S2-BK-05《程序员修炼之道》｜ S2-BK-06《人件》。

**架构设计（10）**：S2-BK-07《Clean Architecture》｜ S2-BK-08《A Philosophy of Software Design》｜ S2-BK-09《Software Architecture in Practice》｜ S2-BK-10《Fundamentals of Software Architecture》｜ S2-BK-11《Building Evolutionary Architectures》｜ S2-BK-12《企业应用架构模式 PoEAA》｜ S2-BK-13《Documenting Software Architectures》｜ S2-BK-14《Software Architecture: The Hard Parts》｜ S2-BK-15《The Software Architect Elevator》｜ S2-BK-16《POSA Vol.1》[verified-sample]。

**领域驱动设计（3）**：S2-BK-17《DDD》｜ S2-BK-18《DDD Reference》[免费, CC BY] ｜ S2-BK-19《Implementing DDD》。

**代码质量/重构/遗留（3）**：S2-BK-20《Clean Code》｜ S2-BK-21《Refactoring 2e》｜ S2-BK-22《Working Effectively with Legacy Code》。

**数据/分布式（2）**：S2-BK-23《DDIA 2e（2026-02）》｜ S2-BK-24《Release It! 2e》。

**运维/可靠性/交付（7）**：S2-BK-25《SRE》[免费] ｜ S2-BK-26《SRE Workbook》[免费] ｜ S2-BK-27《DevOps Handbook 2e》｜ S2-BK-28《Continuous Delivery》｜ S2-BK-29《Accelerate》｜ S2-BK-30《Team Topologies》｜ S2-BK-31《12-Factor App》[免费]。

**设计模式/企业架构（2）**：S2-BK-32《GoF 设计模式》｜ S2-BK-33《企业集成模式》。

**微服务（2）**：S2-BK-34《Building Microservices 2e》｜ S2-BK-35《Microservices Patterns》。

> **版本时效勘误**：FSA 第2版=2025-03；DDIA 第2版=2026-02（Kleppmann+Riccomini）；DevOps Handbook 第2版=2021-11；SAIP 最新为第4版=2021；DDD Reference 官方 PDF 标注 2015-03（D 记 2014）。**可得性**：free-official（S2-BK-01/18/25/26/31）可直接作公开层引用；其余 paid 书本体仅入本地语料层。

**技术债域（P 包，S2，10）**：P-S2-01 Fowler《Technical Debt》[复用 S2-WEB-02] ｜ P-S2-02《Technical Debt Quadrant》｜ P-S2-03 Cunningham《The WyCash Portfolio Management System》(OOPSLA'92，[复用 S4-PAP-06]) ｜ P-S2-04《Opportunistic Refactoring》｜ P-S2-05《Design Stamina Hypothesis》｜ P-S2-06《Strangler Fig》｜ P-S2-07《Definition Of Refactoring》｜ P-S2-08《Code Smell》｜ P-S2-09《Is High Quality Software Worth the Cost?》｜ P-S2-10 Perry & Wolf《Foundations for the Study of Software Architecture》(1992，architectural erosion/drift 原始提出)。

**奠基文献交叉验证（R 包，S2，5）**：R-XC-02 Wikipedia《Lehman's laws of software evolution》｜ R-XC-04 POSA 官方配套站点 software-pattern.org（模式目录 + Microkernel 定义）｜ R-XC-05 Wikipedia《Waterfall model》｜ R-XC-06 Wikipedia《No Silver Bullet》｜ R-XC-07 Wikipedia《Software Engineering Body of Knowledge》。

## 4. S3 官方厂商体系（8）

| ID | 名称 | 机构 | 状态 |
|---|---|---|---|
| S3-VEN-01 | Azure Architecture Center（CQRS / Event-driven） | Microsoft Learn | 已采集 |
| S3-VEN-02 | AWS Well-Architected Framework — The pillars of the framework | AWS | 已采集（官方文档，2024-11-06） |
| S3-VEN-03 | AWS Well-Architected Framework（白皮书 PDF，各支柱定义与原则） | AWS | 已采集（官方白皮书 PDF） |
| S3-VEN-04 | Google Cloud Well-Architected Framework（原 Architecture Framework） | Google Cloud | 已采集（官方枢纽页，2026-01-28） |
| S3-VEN-05 | Google Cloud WAF 支柱页与 What's new | Google Cloud | 已采集（core principles 与变更记录） |
| S3-VEN-06 | Thoughtworks Technology Radar（Vol 34 / 2026-04） | Thoughtworks | 已采集（官方主页） |
| S3-VEN-07 | Thoughtworks Technology Radar FAQ（四环×四象限机制） | Thoughtworks | 已采集（官方 FAQ） |
| S3-VEN-08 | Thoughtworks Technology Radar 归档 PDF（Vol 26–34） | Thoughtworks | 已采集（第四环 Hold→Caution 证据） |

> **已解决缺口**：GAP-07（AWS）、GAP-08（Google Cloud）、GAP-09（ThoughtWorks）均由 Q 包补齐。
> **S3 定位提示**：厂商立场体系，权威性来自官方出处而非中立性，**不得作 S1 国际标准引用**。**勘误**：Thoughtworks Radar 第四环在 Vol 33→Vol 34（2025-11→2026-04）由 **Hold** 更名为 **Caution**（"Caution: Proceed with care."），任务原 "Adopt/Trial/Assess/Hold" 表述已过时。

## 5. S4 学术（论文 21 + 会议期刊 4）

**奠基论文**：S4-PAP-01 Brooks《No Silver Bullet》[verified] ｜ S4-PAP-02 Parnas《On the Criteria…》(1972) ｜ S4-PAP-03 Lehman《Laws of Software Evolution》(1980；**原文 5 条定律**，"八条"最早成文于 Lehman 1996) [abstract-only] ｜ S4-PAP-04 Royce《Managing the Development…》(1970；原文无 "waterfall"，含迭代与五步补救) [verified] ｜ S4-PAP-05 Parnas《SE Programmes are not CS Programmes》(1998) [verified] ｜ S4-PAP-06 Cunningham《WyCash》(OOPSLA'92，技术债) ｜ S4-PAP-07 Garlan & Shaw《An Introduction to Software Architecture》｜ S4-PAP-08 Li et al.《Understanding software architecture erosion》(2022)。

**技术债域（P 包，S4，12）**：P-S4-01 Kruchten et al.《Technical Debt: From Metaphor to Theory and Practice》｜ P-S4-02 Letouzey & Ilkiewicz《Managing Technical Debt with the SQALE Method》｜ P-S4-03 Li et al.《A systematic mapping study on technical debt and its management》(2015，94 项研究) ｜ P-S4-04 Alves et al.《Towards an Ontology of Terms on Technical Debt》｜ P-S4-05《An Overview and Comparison of Technical Debt Measurement Tools》｜ P-S4-06《Automatic identification of self-admitted technical debt from four different sources》｜ P-S4-07《A systematic literature review on Technical Debt prioritization》｜ P-S4-08 Li et al.《Understanding software architecture erosion》([复用 S4-PAP-08]) ｜ P-S4-09 Lehman《Programs, Life Cycles, and Laws of Software Evolution》([复用 S4-PAP-03]) ｜ P-S4-10《Software developer productivity loss due to technical debt》｜ P-S4-11《Building and evaluating a theory of architectural technical debt》｜ P-S4-12《Identification and measurement of Requirements Technical Debt》。

**奠基文献回源交叉源（R 包，S4，1）**：R-XC-01 Lehman《Laws of Software Evolution Revisited》(1996，八条定律完整复述与演进史)。

**主要会议/期刊**：S4-COM-01 ICSE ｜ S4-COM-02 FSE ｜ S4-COM-03 TSE ｜ S4-COM-04 EMSE。

> **回源状态更新（R 包）**：S4-PAP-01（Brooks）、S4-PAP-04（Royce）、S4-PAP-05（Parnas 1998）、S4-PAP-02（Parnas 1972）已由 cited 升级为 **verified（全文）**；S4-PAP-03（Lehman 1980）升级为 **abstract-only**（IEEE 付费全文未取得，条数经 Lehman 1996 复述回源）；S2-BK-16 升级为 **verified（official-sample）**。S4-COM 仍为任务要求补齐的 canonical venue 入口（证据包未直接收录）。

## 6. 本地信源（39，按可复用点）

| ID 段 | 类型 | 数量 | 可复用点 |
|---|---|---|---|
| L-KG-01..04 | 知识图谱库 | 4 | 12factor DAG 工程底座、算法 DAG 基础设施、章节模板/证据区块、11 维权衡矩阵 |
| L-SK-01..04 | skill | 4 | kb-construction 五类谱系+门控+信源分级；教程可读性；cytoscape 交互图；多窗口接力+三硬依据 E1/E2/E3 |
| L-RL-01..10 | 角色 | 10 | 架构/后端/多Agent/上手/评审/最小变更/Git/实现/原型/产品角色描述行 |
| L-MM-01 | 记忆 | 1 | 编码安全、权衡矩阵、覆盖率审计、双轨一致性、根因反推等方法论条目 |
| L-PA-01..18 | 实战留档 | 18 | 18 个真实架构分析案例（逆向/重构/契约先行/级联升级/跨学科迁移等） |
| L-BK-01..02 | 本地语料 | 2 | 12-Factor 原文、Agent 工程语料（版权：仅本地语料层） |

## 7. 主题域 × 信源映射（生命周期主轴）

| 阶段 | 可用信源 ID |
|---|---|
| 1 概念与需求 | S1-STD-03/04, S1-OFF-01/03/04/06/07, S2-BK-02/04/06/30, S4-PAP-04/05, L-KG-04, L-RL-10 |
| 2 架构设计 | S1-STD-01/02, S1-OFF-01/02, S2-BK-07..19, S2-BK-32..35, S2-WEB-01/03..10, S3-VEN-01..08, S4-PAP-02/07, L-KG-04, L-SK-04, L-PA-01/02/03/11 |
| 3 实现与构造 | S1-OFF-01, S2-BK-01/03/05/06/08/20/21/22/32/33, S2-WEB-02, L-RL-05..09 |
| 4 测试 | S1-OFF-01/04, S2-BK-01/22/28, L-SK-01, L-RL-05（偏薄，见 GAP-12） |
| 5 部署 | S1-STD-03, S2-BK-24/27/28/31, L-KG-01, L-BK-01 |
| 6 运维 | S1-STD-07, S1-OFF-01, S2-BK-24/25/26/27, S4-PAP-03, L-PA-15 |
| 7 演化与弃用 | S1-STD-03/07/08, S2-BK-01/11/21/22, S2-WEB-02, S4-PAP-01/03/08, R-XC-01, L-PA-06/07 |
| 横切｜质量属性 | S1-STD-05/06, S1-OFF-02/05, S2-BK-09/10/14, S2-WEB-11, S4-PAP-08, P-S1-02 |
| 横切｜技术债 | P-S1-01/02, P-S2-01..10, P-S3-01..03, P-S4-01..12, S2-BK-01/08/21/22, S2-WEB-01/02, S4-PAP-06/08 |

## 8. 缺口清单（12；其中 5 项已回源处理）

1. **GAP-01**〔未解决〕ISO 标准正文未取得（iso.org 403）→ 走 Wayback + committee.iso.org + iso25000 门户，正文订阅。
2. **GAP-02**〔未解决〕SWEBOK V4 正文 18 KA → 官方购买/会员。
3. **GAP-03**〔未解决〕ISO/IEC/IEEE 15288:2015 未单独采集 → Wayback + committee。
4. **GAP-04**〔未解决〕12207:2026 定稿 scope 未核验 → 待新快照/OBP。
5. **GAP-05**〔已解决（部分）〕Royce/Lehman/Parnas1998/Brooks 原文未回源 → **R 包已回源**：Royce 1970 / Parnas 1998 / Parnas 1972 / Brooks 1987 / Lehman 1996 / POSA 官方样章 / SWEBOK V4 官方页元数据均 verified；仅 Lehman 1980 为 abstract-only（IEEE 付费），Royce/Brooks 双版未逐字对照。
6. **GAP-06**〔已解决（部分）〕POSA Vol.1 本体未回源 → **R 包已取得 Wiley 官方免费样章（Chapter 1 + 目录 PDF）与官方配套站点**，Microkernel 定义可核验；书本体仍受版权未回源。
7. **GAP-07**〔已解决〕AWS Well-Architected 未采集 → **Q 包补齐 S3-VEN-02/03**（官方文档 + 白皮书 PDF，2024-11-06）。
8. **GAP-08**〔已解决〕Google Cloud Architecture Center 未采集 → **Q 包补齐 S3-VEN-04/05**（官方枢纽页 + What's new，2026-01-28）。
9. **GAP-09**〔已解决〕ThoughtWorks Tech Radar 未采集 → **Q 包补齐 S3-VEN-06/07/08**（主页 + FAQ + 归档 PDF，Vol 34）。
10. **GAP-10**〔未解决〕本机无 SE/架构经典书籍本体 → 免费官方源先引用，付费书入本地语料层。
11. **GAP-11**〔未解决〕S4 会议期刊非证据包直接收录 → 阶段2 定向检索。
12. **GAP-12**〔未解决〕测试专用信源薄、extensibility/evolvability 无标准级独立定义、1969 Rome 报告未提取 → 定向补充 29119/ISTQB/Fowler 测试专文与架构演化术语。

## 9. 结论与阶段2 建议

本区分级信源共 **158 条**：S1-STD 10 + S1-OFF 8 + S2-BK 35 + S2-WEB 12 + S3-VEN 8 + S4-PAP 8 + S4-COM 4 + LOCAL 39 + **P-S1 2 + P-S2 10 + P-S3 3 + P-S4 12（P 包技术债 27）+ R-XC 7（R 包回源交叉源）**。**架构与质量属性**两条主线信源最厚（ISO 42010/25010 + SEI + 经典架构书 + 模式文献，可支撑高质量建库）；**技术债**与**厂商实践视角**经 P/Q 包显著增厚；**测试**与**架构演化术语**仍偏薄，需阶段2 定向补齐。所有条目均可溯源，未杜撰；原 cited 条目（S4-PAP-01/03/04/05、S2-BK-16）已由 R 包升级为 verified / abstract-only，S1-STD-10（IEEE 610.12-1990）仍为 cited/历史。
