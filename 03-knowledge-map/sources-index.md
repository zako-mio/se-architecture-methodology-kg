# 信源索引总表（Sources Index）

> 母任务：0910-软件工程架构方法论 · 阶段2/3 交付物（`03-knowledge-map/`）
> 生成日期：2026-09-10　契约：`00-plan/contract.md`　依据：`03-knowledge-map/knowledge-map.json`（阶段1）+ `02-research/F..R-*.json`（阶段2）
> 本表整合阶段1 全局 ID 信源与阶段2 各证据包（F–N 九包 + 新增 P/Q/R 三包）新增/复用信源，供阶段4 建库消费。**只收录可溯源信源，未杜撰。**

## 0. 计数总览

| 范围 | 信源数 | 说明 |
|---|---:|---|
| 阶段1（A–E 归并去重后） | 117 | 全局 ID：S1-STD/S1-OFF/S2-BK/S2-WEB/S3-VEN/S4-PAP/S4-COM/L-* |
| 阶段2 · F 包 | 17 | `F-requirements.json` |
| 阶段2 · G 包 | 17 | `G-architecture.json` |
| 阶段2 · H 包 | 18 | `H-implementation.json` |
| 阶段2 · I 包 | 33 | `I-testing.json` |
| 阶段2 · J 包 | 13 | `J-deployment.json` |
| 阶段2 · K 包 | 12 | `K-operations.json` |
| 阶段2 · L 包 | 24 | `L-evolution.json` |
| 阶段2 · M 包 | 13 | `M-quality-ility.json` |
| 阶段2 · N 包 | 13 | `N-team-conway.json` |
| 阶段2 · P 包（新增） | 27 | `P-techdebt.json`（技术债独立证据包） |
| 阶段2 · Q 包（新增） | 7 | `Q-vendor-architecture.json`（厂商架构框架 / 采用雷达） |
| 阶段2 · R 包（新增） | 14 | `R-foundational-papers.json`（奠基文献） |
| **阶段2 合计（含跨包复用/重复计数）** | 208 | 12 包 sources[] 计数之和（F–N 160 + P/Q/R 48） |

> 注：阶段2 各包的 `sources[]` 包含对阶段1 信源的复用（包内局部 ID 重新编号），因此 **208 为计数之和、非净新增**；各条新增/复用状态见 §4，复用映射见 §2。
> 计数范围：`02-research/` 下 F–N 九包 + 新增 P/Q/R 三包，共 **12 个含 `sources[]` 的证据包**。`O-methodology.json` 为方法论综合包（`sources` 长度为 0，无 `sources[]`），不计入信源与来源包总数。

## 1. ID 对照说明（阶段1 全局 ID vs 阶段2 局部 ID）

### 1.1 命名方案差异

| 维度 | 阶段1（A–E → knowledge-map.json） | 阶段2（F–R 证据包） |
|---|---|---|
| ID 唯一性 | **全局唯一**，跨包去重后统一编号 | **多为包内局部编号**，跨包会碰撞 |
| 命名形态 | 自描述前缀：`S1-STD-01`/`S1-OFF-01`/`S2-BK-01`/`S2-WEB-01`/`S3-VEN-01`/`S4-PAP-01`/`S4-COM-01`/`L-*` | 三种混用：①裸数字 `S1-01`/`S2-01`；②字母中缀 `S1-F01`/`S1-M01`；③直接沿用全局式 `S1-STD-11`/`S2-WEB-12` |
| 语义稳定性 | 高（前缀即类别+序号） | 低（同一 `S2-01` 在不同包指不同信源） |
| 复用表达 | `evidence_ref` 记录 A/B/D/E 出处 | 用包内 ID + 标题注明『复用 X 包』 |

### 1.2 各包命名惯例

| 包 | 局部 ID 形态 | 示例 | 是否与阶段1/他包碰撞 |
|---|---|---|---|
| F-requirements | 复用裸 ID + `S1-A01` + `S1-Fxx/S2-Fxx/S3-Fxx/S4-Fxx` | `S1-03`、`S1-A01`、`S1-F02` | 是（`S1-03`↔E 包 `S1-03`） |
| G-architecture | 裸数字 `S1-01..S1-12`、`S2-09/10/14/18/19`、`S3-02` | `S1-08`、`S2-14` | 是（跨包大量碰撞） |
| H-implementation | 裸数字 `S1-01/02`、`S2-01..S2-11`、`S3-01/02`、`S4-01..03` | `S2-01` | 是 |
| I-testing | **直接沿用全局式**：`S1-STD-11..20`、`S1-OFF-09..14`、`S2-WEB-12..19`、`S2-BK-*`、`S3-VEN-02..04` | `S1-STD-11`、`S2-WEB-12` | 否（续编号，可映射阶段1） |
| J-deployment | 裸数字 `S2-01..S2-07`、`S3-01..S3-05`、`BK-01` | `S2-01`、`BK-01` | 是 |
| K-operations | 裸数字 `S2-01..S2-06`、`S3-01..S3-06` | `S2-01` | 是 |
| L-evolution | 裸数字 `S1-01..03`、`S2-01..S2-13`、`S3-01..S3-05`、`S4-01..03` | `S4-01` | 是 |
| M-quality | 字母中缀 `S1-M01..M08`、`S2-M01/02`、`S4-M01..M03` | `S1-M01` | 否（M 段自限定） |
| N-team-conway | 裸数字 `S2-01..S2-06`、`S3-01..S3-05`、`S4-01/02` | `S2-01` | 是 |
| P-techdebt（新增） | 自限定前缀 `P-S1-xx`/`P-S2-xx`/`P-S3-xx`/`P-S4-xx` | `P-S1-01`、`P-S4-01` | 否（`P-` 段自限定） |
| Q-vendor-architecture（新增） | 直接沿用全局式 `S3-VEN-02..08` | `S3-VEN-02` | 是（与 I 包 `S3-VEN-02..04` 名义碰撞，见 §5） |
| R-foundational-papers（新增） | 混合：①直接沿用阶段1 全局 ID（`S4-PAP-01..05`/`S2-BK-16`/`S1-OFF-01`）；②自限定 `R-XC-01..07` | `S4-PAP-01`、`R-XC-01` | ①为同源复用（非碰撞）；②自限定 |

**结论**：阶段2 局部 ID **不可脱离包名直接引用**。本表每行同时给出『ID』与『来源包』，跨包引用须写作 `包/ID`（如 `H/S2-01`）或以标题消歧。

## 2. 跨包复用映射（阶段2 局部 ID → 阶段1 全局 ID / 他包局部 ID）

下表列出阶段2 证据包中**明确指向阶段1/他包既有信源**的条目。未列出的阶段2 ID 视为该包**净新增信源**（见 §3）。P 包与其来源在语义上重合的条目（技术债/重构/腐化）优先映射阶段1，无以阶段1 对应者映射他包（L/H）。

| 阶段2 局部 ID | → 阶段1 全局 ID / 他包 ID | 说明 |
|---|---|---|
| `F/S1-A01` | `S1-OFF-01` | SWEBOK Guide；A 包 `S1-01` |
| `F/S1-03` | `S1-STD-03` | ISO 12207:2026；复用 E 包 |
| `F/S1-07` | `S1-OFF-06` | NATO 1968 报告；A 包 `S1-07` |
| `F/S4-04` | `S4-PAP-01` | No Silver Bullet；A 包 `S4-04` |
| `G/S1-01` | `S1-STD-01` | 42010 官方解释页（关联） |
| `G/S1-07` | `S1-STD-01` | 42010 概念模型页（关联） |
| `G/S1-08` | `S1-STD-01` | ISO/IEC/IEEE 42010:2022 标准页 |
| `G/S1-03` | `S1-OFF-02` | SEI 架构定义 |
| `G/S1-04` | `S1-OFF-02` | SEI 架构总览页 |
| `G/S1-05` | `S1-OFF-02` | SEI ATAM fact sheet（关联） |
| `G/S1-11` | `S1-OFF-02` | SEI ATAM TR-2000（机构同、文档新增） |
| `G/S2-09` | `S2-WEB-04` | Nygard ADR 原文 |
| `G/S2-10` | `S2-WEB-05` | Fowler ADR bliki |
| `G/S2-14` | `S4-PAP-07` | Garlan&Shaw（阶段2 归 S2） |
| `G/S2-18` | `S2-BK-16` | POSA Vol.1 |
| `G/S2-19` | `S2-BK-13` | Documenting Software Architectures |
| `H/S1-01` | `S1-OFF-01` | SWEBOK V4.0 |
| `H/S1-02` | `S1-STD-05` | ISO/IEC 25010:2023 |
| `H/S2-01` | `S4-PAP-02` | Parnas 1972 |
| `H/S2-02` | `S2-BK-08` | A Philosophy of Software Design |
| `H/S2-05` | `S2-BK-20` | Clean Code |
| `H/S2-06` | `S2-BK-32` | GoF Design Patterns |
| `H/S2-10` | `S2-BK-01` | SE@Google Ch.3 |
| `I/S1-OFF-05` | `S1-OFF-05` | ISO 25000 Portal |
| `I/S2-BK-01` | `S2-BK-01` | SE@Google（同全局 ID） |
| `I/S2-BK-09` | `S2-BK-09` | SAiP 4e（同全局 ID） |
| `I/S2-BK-28` | `S2-BK-28` | Continuous Delivery（同全局 ID） |
| `I/S2-BK-29` | `S2-BK-29` | Accelerate（同全局 ID） |
| `J/S2-01` | `S2-BK-31` | The Twelve-Factor App |
| `J/S2-07` | `S2-BK-25` | SRE Book Ch.8 Release Engineering |
| `J/BK-01` | `L-BK-01` | 12factor.epub 本地语料 |
| `K/S2-01` | `S2-BK-25` | Google SRE Book |
| `K/S2-02` | `S2-BK-26` | SRE Workbook |
| `K/S2-03` | `S2-BK-24` | Release It! 2e |
| `L/S1-01` | `S1-STD-07` | ISO/IEC/IEEE 14764:2022 |
| `L/S2-01` | `S2-WEB-02` | Fowler Technical Debt bliki |
| `L/S2-02` | `S4-PAP-06` | Cunningham WyCash OOPSLA'92 |
| `L/S2-04` | `S2-BK-21` | Fowler Refactoring（关联） |
| `L/S2-05` | `S2-BK-21` | Refactoring 2e 官方目录 |
| `L/S2-09` | `S2-BK-22` | WELC 官方章节节选 |
| `L/S2-12` | `S2-BK-11` | Building Evolutionary Architectures |
| `L/S2-13` | `S2-BK-11` | BEA 官方样章 |
| `L/S4-01` | `S4-PAP-08` | 架构腐化系统映射 |
| `L/S4-02` | `S4-PAP-03` | Lehman 演化定律 |
| `M/S1-M01` | `S1-STD-05` | ISO/IEC 25010:2023 |
| `M/S1-M08` | `S1-STD-07` | ISO/IEC/IEEE 14764:2022 |
| `M/S2-M01` | `S1-OFF-05` | ISO 25000 Portal（另见 S2-WEB-11） |
| `M/S2-M02` | `S2-BK-09` | SAiP Ch.5 Introducing Tactics |
| `N/S2-06` | `S2-BK-30` | Team Topologies 书页 |
| `N/S2-04` | `S2-BK-30` | Fowler Team Topologies bliki（关联） |
| `P/P-S1-02` | `S1-STD-05` | ISO/IEC 25010:2023（另见 `M/S1-M01`、`M/S2-M01`） |
| `P/P-S2-01` | `S2-WEB-02` | Fowler Technical Debt bliki（另见 `L/S2-01`，同一 URL） |
| `P/P-S2-02` | `L/S2-03` | 复用 L 包 Technical Debt Quadrant（同一 URL）；阶段1 无对应源 |
| `P/P-S2-03` | `S4-PAP-06` | Cunningham WyCash OOPSLA'92（另见 `L/S2-02`，同一 URL） |
| `P/P-S2-06` | `L/S2-07` | 复用 L 包 Strangler Fig；阶段1 无对应源 |
| `P/P-S2-07` | `L/S2-04` | 复用 L 包 Definition Of Refactoring；阶段1 无对应源 |
| `P/P-S2-08` | `L/S2-06`；`H/S2-03` | 复用 L/H 包 Code Smell（同一 URL）；阶段1 无对应源 |
| `P/P-S2-10` | `L/S2-11` | 复用 L 包 Perry & Wolf 1992；阶段1 无对应源 |
| `P/P-S4-01` | `L/S4-03` | 复用 L 包 Kruchten 技术债理论；阶段1 无对应源 |
| `P/P-S4-08` | `S4-PAP-08` | Li 2022 架构腐化系统映射（另见 `B/S4-01`、`L/S4-01`，同一 DOI） |
| `P/P-S4-09` | `S4-PAP-03` | Lehman 1980（另见 `A/S4-01`、`L/S4-02`） |
| `R/S4-PAP-01` | `S4-PAP-01` | 直接沿用阶段1 全局 ID（No Silver Bullet） |
| `R/S4-PAP-02` | `S4-PAP-02` | 直接沿用阶段1 全局 ID（Parnas 1972；另复用 `H/S2-01`） |
| `R/S4-PAP-03` | `S4-PAP-03` | 直接沿用阶段1 全局 ID（Lehman 1980） |
| `R/S4-PAP-04` | `S4-PAP-04` | 直接沿用阶段1 全局 ID（Royce 1970） |
| `R/S4-PAP-05` | `S4-PAP-05` | 直接沿用阶段1 全局 ID（Parnas 1998） |
| `R/S2-BK-16` | `S2-BK-16` | 直接沿用阶段1 全局 ID（POSA Vol.1） |
| `R/S1-OFF-01` | `S1-OFF-01` | 直接沿用阶段1 全局 ID（SWEBOK V4.0） |
| `R/R-XC-03` | `F/S1-F04` | 复用 F 包 SEBoK SWEBOK 概览页；阶段1 无对应源 |

> Q 包的 `S3-VEN-02..08` 均为净新增厂商/机构信源，无阶段1 或他包映射（其 `S3-VEN-02` 与 I 包同名不同源，见 §5.1）。

## 3. 阶段1 信源总表（117 条，沿用全局 ID）

> 来源：`03-knowledge-map/knowledge-map.json`。列：ID / tier / 标题或标准号 / 机构 / 年份或版本 / verified·status / URL / 来源包。

### S1-STD · 国际标准（10）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified·status | URL | 来源包 |
|---|---|---|---|---|---|---|---|
| `S1-STD-01` | S1 | Software, systems and enterprise — Architecture description | ISO / IEC / IEEE（JTC 1/SC 7） | 2022；ISO/IEC/IEEE 42010:2022（Edition 2） | Published [60.60] | https://www.iso.org/standard/74393.html | E:42010-2022；B:S1-01；B:S1-07 |
| `S1-STD-02` | S1 | Systems and software engineering — Architecture description | ISO / IEC / IEEE（JTC 1/SC 7） | 2011；ISO/IEC/IEEE 42010:2011（Edition 1） | Withdrawn [95.99] | https://www.iso.org/standard/50508.html | E:42010-2011 |
| `S1-STD-03` | S1 | Systems and software engineering — Software life cycle processes | ISO / IEC / IEEE（JTC 1/SC 7） | 2026；ISO/IEC/IEEE 12207:2026（Edition 2） | Published — 当前有效版本（2026-04 发布，取代 12207:2017） | https://www.iso.org/standard/90219.html | E:12207-2026；A:S1-03 |
| `S1-STD-04` | S1 | Systems and software engineering — Software life cycle processes | ISO / IEC / IEEE（JTC 1/SC 7） | 2017；ISO/IEC/IEEE 12207:2017（Edition 1） | Withdrawn [95.99] | https://www.iso.org/standard/63712.html | E:12207-2017；A:S1-02 |
| `S1-STD-05` | S1 | Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model | ISO / IEC | 2023；ISO/IEC 25010:2023（Edition 2） | Published [60.60] | https://www.iso.org/standard/78176.html | E:25010-2023；A:S1-04；B:S1-06；A:S2-03；A:S2-04 |
| `S1-STD-06` | S1 | Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models | ISO / IEC | 2011；ISO/IEC 25010:2011（Edition 1） | Withdrawn [95.99] | https://www.iso.org/standard/35733.html | E:25010-2011；A:S2-05 |
| `S1-STD-07` | S1 | Software engineering — Software life cycle processes — Maintenance | ISO / IEC / IEEE | 2022；ISO/IEC/IEEE 14764:2022（Edition 3） | Published [60.60] | https://www.iso.org/standard/80710.html | E:14764-2022；A:S1-12 |
| `S1-STD-08` | S1 | Software Engineering — Software Life Cycle Processes — Maintenance | ISO / IEC | 2006；ISO/IEC 14764:2006（Edition 2） | Withdrawn [95.99] | https://www.iso.org/standard/39064.html | E:14764-2006 |
| `S1-STD-09` | S1 | Systems and software engineering — Vocabulary (SEVOCAB) | ISO / IEC / IEEE | 2017；ISO/IEC/IEEE 24765:2017（Edition 2） | Published，但为『to be revised [90.92]』 | https://www.iso.org/standard/71952.html | E:24765-2017；A:S1-09 |
| `S1-STD-10` | S1 | IEEE Standard Glossary of Software Engineering Terminology | IEEE | 1990；IEEE Std 610.12-1990 | 历史标准（定义沿用至 ISO/IEC/IEEE 24765 SEVOCAB） | https://standards.ieee.org/ieee/610.12/1016/ | A:S1-08 |

### S1-OFF · 官方知识体系/机构/门户（8）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified·status | URL | 来源包 |
|---|---|---|---|---|---|---|---|
| `S1-OFF-01` | S1 | Guide to the Software Engineering Body of Knowledge (SWEBOK) V3.0 / V4.0 | IEEE Computer Society（ISO/IEC TR 19759 认定的知识体系基线） | 2014（V3）/ 2024（V4）；V3.0（2014，15 KA）/ V4.0（2024-10，18 KA，新增 Software Architecture、SE Operations、Software Security） | verified | https://www.computer.org/education/bodies-of-knowledge/software-engineering | A:S1-01；B:S1-02 |
| `S1-OFF-02` | S1 | Carnegie Mellon Software Engineering Institute (SEI) — 架构定义/架构总览/ATAM 方法 | SEI, Carnegie Mellon University（美国国防部 FFRDC） | 2017-2018 及持续更新；SEI brochure 3854（定义 2017）；ATAM fact sheet 2018 | verified | https://www.sei.cmu.edu/architecture/ | A:S1-10；B:S1-03；B:S1-04；B:S1-05 |
| `S1-OFF-03` | S1 | Software Engineering 2014: Curriculum Guidelines for Undergraduate Degree Programs in Software Engineering (SE2014) | Joint Task Force, IEEE Computer Society & ACM | 2015（内容 2014）；SE2014 | verified | https://www.acm.org/binaries/content/assets/education/se2014.pdf | A:S1-05 |
| `S1-OFF-04` | S1 | Computer Science Curricula 2023 (CS2023) — Software Engineering Knowledge Area | ACM / IEEE-CS / AAAI Joint Task Force | 2023；CS2023（SE KA，Beta v2 文本） | verified | https://csed.acm.org/knowledge-areas | A:S1-06 |
| `S1-OFF-05` | S1 | ISO 25000 Portal — ISO/IEC 25010 质量标准门户 | AENOR（西班牙标准机构）/ iso25000.com | 2024；ISO 25000 系列官方门户 | verified | https://iso25000.com/index.php/en/iso-25000-standards/iso-25010 | A:S2-03；B:S1-06 |
| `S1-OFF-06` | S1 | Software Engineering: Report on a conference sponsored by the NATO Science Committee, Garmisch, 1968 | NATO Science Committee（Naur & Randell 编） | 1969；1968 Garmisch 会议报告 | verified | http://homepages.cs.ncl.ac.uk/brian.randell/NATO/nato1968.PDF | A:S1-07 |
| `S1-OFF-07` | S1 | Manifesto for Agile Software Development（敏捷软件开发宣言） | 17 位署名作者（Beck, Cockburn, Fowler 等） | 2001；原始宣言 | verified | https://agilemanifesto.org/ | A:S1-11 |
| `S1-OFF-08` | S1 | ISO/IEC/IEEE 24765 SEVOCAB 在线术语库（配合 S1-STD-09） | ISO / IEC / IEEE | 2017；SEVOCAB 在线版 | 入口引用（正文受版权，未入库） | https://www.iso.org/standard/71952.html | A:S1-09 |

### S2-BK · 经典著作（35）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified·status | URL | 来源包 |
|---|---|---|---|---|---|---|---|
| `S2-BK-01` | S2 | Software Engineering at Google: Lessons Learned from Programming Over Time | O'Reilly（Titus Winters, Tom Manshreck, Hyrum Wright 编） | 2020；1st | 官方免费在线全文 | https://abseil.io/resources/swe-book | D:通论-SE@Google；A:S2-02 |
| `S2-BK-02` | S2 | The Mythical Man-Month: Essays on Software Engineering | Pearson（Frederick P. Brooks Jr.） | 1995；Anniversary Edition (2nd) | 在版 | https://www.pearson.com/en-us/subject-catalog/p/mythical-man-month-the-essays-on-software-engineering-anniversary-edition/P200000009376 | D:通论-人月神话；A:S4-04 |
| `S2-BK-03` | S2 | Code Complete: A Practical Handbook of Software Construction | Microsoft Press（Steve McConnell） | 2004；2nd | 在版 | https://www.microsoftpressstore.com/store/code-complete-9780735619678 | D:通论-代码大全 |
| `S2-BK-04` | S2 | Software Engineering（Ian Sommerville 教材） | Pearson（Ian Sommerville） | 2015；10th | 在版 | https://www.pearson.com/en-us/subject-catalog/p/software-engineering/P200000003290 | D:通论-Sommerville；A:S2-01 |
| `S2-BK-05` | S2 | The Pragmatic Programmer: Your Journey to Mastery | The Pragmatic Bookshelf（David Thomas, Andrew Hunt） | 2019；20th Anniversary Edition (2nd) | 在版 | https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/ | D:通论-程序员修炼之道 |
| `S2-BK-06` | S2 | Peopleware: Productive Projects and Teams | Pearson（Tom DeMarco, Timothy Lister） | 2013；3rd | 在版 | https://www.pearson.com/en-us/subject-catalog/p/peopleware-productive-projects-and-teams/P200000009378 | D:通论-人件 |
| `S2-BK-07` | S2 | Clean Architecture: A Craftsman's Guide to Software Structure and Design | Pearson（Robert C. Martin） | 2017；1st | verified | https://www.pearson.com/en-us/subject-catalog/p/clean-architecture-a-craftsmans-guide-to-software-structure-and-design/P200000009282 | D:架构-CleanArchitecture；B:S2-06 |
| `S2-BK-08` | S2 | A Philosophy of Software Design | Yaknyam Press / Stanford（John Ousterhout） | 2021；2nd（修订版） | verified | https://web.stanford.edu/~ouster/cgi-bin/book.php | D:架构-APoSD；B:S2-07 |
| `S2-BK-09` | S2 | Software Architecture in Practice | Pearson（Len Bass, Paul Clements, Rick Kazman, SEI） | 2021；4th | 在版 | https://www.pearson.com/en-us/subject-catalog/p/software-architecture-in-practice/P200000009173 | D:架构-SAIP；B:S1-03 |
| `S2-BK-10` | S2 | Fundamentals of Software Architecture: A Modern Engineering Approach | O'Reilly（Mark Richards, Neal Ford） | 2025；2nd | 在版（2025-03 第2版） | https://www.oreilly.com/library/view/fundamentals-of-software/9781098175504/ | D:架构-FSA |
| `S2-BK-11` | S2 | Building Evolutionary Architectures: Automated Software Governance | O'Reilly（Neal Ford, Rebecca Parsons, Patrick Kua, Pramod Sadalage） | 2022；2nd | 在版 | https://www.oreilly.com/library/view/building-evolutionary-architectures/9781492097532/ | D:架构-BuildingEvolutionary |
| `S2-BK-12` | S2 | Patterns of Enterprise Application Architecture (PoEAA) | Addison-Wesley（Martin Fowler 等） | 2002；1st | verified | https://martinfowler.com/books/eaa.html | D:架构-PoEAA；B:S2-05 |
| `S2-BK-13` | S2 | Documenting Software Architectures: Views and Beyond | Pearson / SEI（Paul Clements, Felix Bachmann, Len Bass 等） | 2010；2nd | 在版 | https://www.pearson.com/en-us/subject-catalog/p/documenting-software-architectures-views-and-beyond/P200000009174 | D:架构-DocumentingArchitectures；B:S1-03 |
| `S2-BK-14` | S2 | Software Architecture: The Hard Parts | O'Reilly（Neal Ford, Mark Richards, Pramod Sadalage, Zhamak Dehghani） | 2021；1st | 在版 | https://www.oreilly.com/library/view/software-architecture-the/9781492086888/ | D:架构-HardParts |
| `S2-BK-15` | S2 | The Software Architect Elevator: Redefining the Architect's Role in the Digital Enterprise | O'Reilly（Gregor Hohpe） | 2020；1st | 在版 | https://www.oreilly.com/library/view/the-software-architect/9781492077541/ | D:架构-ArchitectElevator |
| `S2-BK-16` | S2 | Pattern-Oriented Software Architecture, Volume 1: A System of Patterns | Wiley（F. Buschmann, R. Meunier, H. Rohnert, P. Sommerlad, M. Stal） | 1996；1st | cited | https://www.wiley.com/ | B:S2-18 |
| `S2-BK-17` | S2 | Domain-Driven Design: Tackling Complexity in the Heart of Software | Addison-Wesley（Eric Evans） | 2003；1st | 在版 | https://www.pearson.com/en-us/subject-catalog/p/domain-driven-design-tackling-complexity-in-the-heart-of-software/P200000009134 | D:DDD-DDD原著 |
| `S2-BK-18` | S2 | Domain-Driven Design Reference: Definitions and Pattern Summaries | Domain Language, Inc.（Eric Evans，CC BY 4.0） | 2015（D 记 2014）；Reference PDF | verified | https://domainlanguage.com/ddd/reference/ | D:DDD-DDDReference；B:S2-08 |
| `S2-BK-19` | S2 | Implementing Domain-Driven Design | Addison-Wesley（Vaughn Vernon） | 2013；1st | 在版 | https://www.pearson.com/en-us/subject-catalog/p/implementing-domain-driven-design/P200000009135 | D:DDD-IDDD |
| `S2-BK-20` | S2 | Clean Code: A Handbook of Agile Software Craftsmanship | Pearson（Robert C. Martin） | 2008；1st | 在版（存在争议，但影响力与引用度极高） | https://www.pearson.com/en-us/subject-catalog/p/clean-code-a-handbook-of-agile-software-craftsmanship/P200000009283 | D:代码质量-CleanCode |
| `S2-BK-21` | S2 | Refactoring: Improving the Design of Existing Code | Addison-Wesley（Martin Fowler with Kent Beck） | 2018；2nd（JS 示例，新增函数式重构） | 在版 | https://www.pearson.com/en-us/subject-catalog/p/refactoring-improving-the-design-of-existing-code/P200000009306 | D:代码质量-Refactoring |
| `S2-BK-22` | S2 | Working Effectively with Legacy Code | Pearson（Michael Feathers） | 2004；1st | 在版 | https://www.pearson.com/en-us/subject-catalog/p/working-effectively-with-legacy-code/P200000009308 | D:代码质量-LegacyCode |
| `S2-BK-23` | S2 | Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems | O'Reilly（Martin Kleppmann, Chris Riccomini） | 2026；2nd（2026-02 出版） | 在版 | https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ | D:数据分布式-DDIA |
| `S2-BK-24` | S2 | Release It! Design and Deploy Production-Ready Software | The Pragmatic Bookshelf（Michael T. Nygard） | 2018；2nd | 在版 | https://pragprog.com/titles/mnee2/release-it-second-edition/ | D:数据分布式-ReleaseIt |
| `S2-BK-25` | S2 | Site Reliability Engineering: How Google Runs Production Systems | O'Reilly / Google（Betsy Beyer 等） | 2016；1st | 官方免费在线全文 | https://sre.google/sre-book/table-of-contents/ | D:运维-SRE Book |
| `S2-BK-26` | S2 | The Site Reliability Workbook: Practical Ways to Implement SRE | O'Reilly / Google（Betsy Beyer 等） | 2018；1st | 官方免费在线全文 | https://sre.google/workbook/table-of-contents/ | D:运维-SRE Workbook |
| `S2-BK-27` | S2 | The DevOps Handbook | IT Revolution（Gene Kim, Jez Humble, Patrick Debois, John Willis, Nicole Forsgren） | 2021；2nd | 在版 | https://itrevolution.com/product/the-devops-handbook-second-edition/ | D:运维-DevOpsHandbook |
| `S2-BK-28` | S2 | Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation | Pearson（Jez Humble, David Farley） | 2010；1st | 在版 | https://www.pearson.com/en-us/subject-catalog/p/continuous-delivery-reliable-software-releases-through-build-test-and-deployment-automation/P200000009253 | D:运维-ContinuousDelivery |
| `S2-BK-29` | S2 | Accelerate: The Science of Lean Software and DevOps | IT Revolution（Nicole Forsgren, Jez Humble, Gene Kim） | 2018；1st | 在版 | https://itrevolution.com/product/accelerate/ | D:运维-Accelerate |
| `S2-BK-30` | S2 | Team Topologies: Organizing Business and Technology Teams for Fast Flow | IT Revolution（Matthew Skelton, Manuel Pais） | 2019；1st | 在版 | https://itrevolution.com/product/team-topologies/ | D:运维-TeamTopologies |
| `S2-BK-31` | S2 | The Twelve-Factor App | Adam Wiggins (Heroku) | 2011；Methodology (web) | 官方免费 | https://12factor.net/ | D:运维-12Factor；C:BK-01 |
| `S2-BK-32` | S2 | Design Patterns: Elements of Reusable Object-Oriented Software | Addison-Wesley（Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides / GoF） | 1994；1st | 在版 | https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009144 | D:设计模式-GoF |
| `S2-BK-33` | S2 | Enterprise Integration Patterns: Designing, Building, and Deploying Messaging Solutions | Addison-Wesley（Gregor Hohpe, Bobby Woolf） | 2003；1st | 在版 | https://www.enterpriseintegrationpatterns.com/ | D:设计模式-EIP |
| `S2-BK-34` | S2 | Building Microservices: Designing Fine-Grained Systems | O'Reilly（Sam Newman） | 2021；2nd | 在版 | https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/ | D:微服务-BuildingMicroservices |
| `S2-BK-35` | S2 | Microservices Patterns: With Examples in Java | Manning（Chris Richardson） | 2018；1st | 在版 | https://www.manning.com/books/microservices-patterns | D:微服务-MicroservicesPatterns |

### S2-WEB · 权威作者文章/官方章节（12）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified·status | URL | 来源包 |
|---|---|---|---|---|---|---|---|
| `S2-WEB-01` | S2 | Software Architecture Guide | Martin Fowler (martinfowler.com) | 2019-08-01 | verified | https://martinfowler.com/architecture/ | B:S2-01 |
| `S2-WEB-02` | S2 | Technical Debt (bliki) | Martin Fowler (martinfowler.com) | 2019-05-21 | verified | https://martinfowler.com/bliki/TechnicalDebt.html | B:S2-02 |
| `S2-WEB-03` | S2 | Who Needs an Architect? | Martin Fowler, IEEE Software | 2003 | verified | https://martinfowler.com/ieeeSoftware/whoNeedsArchitect.pdf | B:S2-04 |
| `S2-WEB-04` | S2 | Documenting Architecture Decisions | Michael Nygard (Cognitect Blog) | 2011-11-15 | verified | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | B:S2-09 |
| `S2-WEB-05` | S2 | Architecture Decision Record (bliki) | Martin Fowler (martinfowler.com) | 2026-03-24 (updated) | verified | https://martinfowler.com/bliki/ArchitectureDecisionRecord.html | B:S2-10 |
| `S2-WEB-06` | S2 | Microservices — a definition of this new architectural term | James Lewis & Martin Fowler (martinfowler.com) | 2014-03-25 | verified | https://martinfowler.com/articles/microservices.html | B:S2-11 |
| `S2-WEB-07` | S2 | Presentation Domain Data Layering | Martin Fowler (martinfowler.com) | 2015-08-26 | verified | https://martinfowler.com/bliki/PresentationDomainDataLayering.html | B:S2-12 |
| `S2-WEB-08` | S2 | CQRS (bliki) | Martin Fowler (martinfowler.com) | 2011-07-14 | verified | https://martinfowler.com/bliki/CQRS.html | B:S2-13 |
| `S2-WEB-09` | S2 | MVC — Xerox PARC 1978-79（作者原始说明） | Trygve Reenskaug | 1979；原始 MVC note | verified | https://folk.universitetetioslo.no/trygver/themes/mvc/mvc-index.html | B:S2-16 |
| `S2-WEB-10` | S2 | GUI Architectures | Martin Fowler (martinfowler.com) | 2006-07-18 | verified | https://martinfowler.com/eaaDev/uiArchs.html | B:S2-17 |
| `S2-WEB-11` | S2 | ISO/IEC 25010 Explained: 9 Software Quality Characteristics | SonarSource | 2024 | verified | https://www.sonarsource.com/resources/library/iso-iec-25010-explained/ | A:S2-04 |
| `S2-WEB-12` | S2 | Wikipedia 条目组（Software engineering / SWEBOK / NATO Conferences / Software crisis / ISO 12207 / Lehman's laws / ISO 9126） | Wikimedia Foundation | 2026（持续更新） | verified | https://en.wikipedia.org/wiki/Software_engineering | A:S2-05；E:cross-sources |

### S3-VEN · 官方厂商架构中心（1）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified·status | URL | 来源包 |
|---|---|---|---|---|---|---|---|
| `S3-VEN-01` | S3 | Azure Architecture Center — Cloud design patterns (CQRS / Event-driven architecture) | Microsoft (Microsoft Learn) | n.d. (accessed 2026-09-10) | verified | https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs | B:S3-01 |

### S4-PAP · 学术奠基论文（8）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified·status | URL | 来源包 |
|---|---|---|---|---|---|---|---|
| `S4-PAP-01` | S4 | No Silver Bullet — Essence and Accidents of Software Engineering | IEEE Computer（Frederick P. Brooks, Jr.）；原为 IFIP 1986，收录于《人月神话》周年版第16章 | 1987（essay 1986） | cited | https://doi.org/10.1109/MC.1987.1663532 | A:S4-04；D:通论-没有银弹 |
| `S4-PAP-02` | S4 | On the Criteria To Be Used in Decomposing Systems into Modules | D. L. Parnas, Communications of the ACM | 1972 | verified | https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf | B:S2-15 |
| `S4-PAP-03` | S4 | Programs, Life Cycles, and Laws of Software Evolution | Meir M. Lehman, Proc. IEEE 68(9) | 1980 | cited | https://doi.org/10.1109/PROC.1980.11805 | A:S4-01 |
| `S4-PAP-04` | S4 | Managing the Development of Large Software Systems | Winston W. Royce, Proc. IEEE WESCON | 1970 | cited | https://en.wikipedia.org/wiki/Waterfall_model | A:S4-02 |
| `S4-PAP-05` | S4 | Software Engineering Programmes are not Computer Science Programmes | David L. Parnas, Annals of Software Engineering | 1998 | cited | https://doi.org/10.1023/A:1018949113292 | A:S4-03 |
| `S4-PAP-06` | S4 | The WyCash Portfolio Management System (OOPSLA'92 Experience Report) | Ward Cunningham | 1992-03-26 | verified | https://c2.com/doc/oopsla92.html | B:S2-03 |
| `S4-PAP-07` | S4 | An Introduction to Software Architecture (CMU-CS-94-166 / SEI-94-TR-21) | David Garlan & Mary Shaw, Carnegie Mellon University / SEI | 1993（book chapter）/ 1994（tech report） | verified | https://www.cs.cmu.edu/afs/cs/project/able/ftp/intro_softarch/intro_softarch.pdf | B:S2-14 |
| `S4-PAP-08` | S4 | Understanding software architecture erosion: A systematic mapping study | R. Li, P. Liang, M. Soliman, P. Avgeriou, Journal of Software: Evolution and Process | 2022 | verified | https://doi.org/10.1002/smr.2423 | B:S4-01 |

### S4-COM · 主要学术会议/期刊（4）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified·status | URL | 来源包 |
|---|---|---|---|---|---|---|---|
| `S4-COM-01` | S4 | ICSE — International Conference on Software Engineering | ACM / IEEE-CS（软件工程顶会） | annual | canonical venue（证据包未直接收录 | https://conf.researchr.org/series/icse | task-required |
| `S4-COM-02` | S4 | FSE (ESEC/FSE) — ACM International Conference on the Foundations of Software Engineering | ACM SIGSOFT（软件工程顶会） | annual | canonical venue（证据包未直接收录 | https://conf.researchr.org/series/fse | task-required |
| `S4-COM-03` | S4 | IEEE Transactions on Software Engineering (TSE) | IEEE Computer Society（软件工程顶级期刊） | 1975– | canonical venue（证据包未直接收录 | https://www.computer.org/csdl/journal/ts | task-required |
| `S4-COM-04` | S4 | Empirical Software Engineering (EMSE) | Springer（软件工程权威期刊） | 1996– | canonical venue（证据包未直接收录 | https://link.springer.com/journal/10664 | task-required |

### L- · 本地信源（39）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified·status | URL | 来源包 |
|---|---|---|---|---|---|---|---|
| `L-KG-01` | LOCAL | 12 Factor App × 12 Factor Agent 合并方法论知识图谱 | 本地留档 | 2026-08 | 存在（38 节点/61 边/16 组） | ~/opencode/archive/Mission-file/2026-08/0823-12factor-methodology/ | C:KG-01 |
| `L-KG-02` | LOCAL | 算法知识图谱 | 本地留档 | 2026-08 | 存在（60 组/372 节点/318 边） | ~/opencode/archive/Mission-file/2026-08/0820-algorithm-knowledge-graph/ | C:KG-02 |
| `L-KG-03` | LOCAL | RL/LLM 推理/显存优化面试知识库 | 本地留档 | 2026-08 | 存在（13 章 + 总述页） | ~/opencode/archive/Mission-file/2026-08/0826-RL推理显存面试知识库/ | C:KG-03 |
| `L-KG-04` | LOCAL | RAG 建库工程教材 + 第5层『架构权衡思维』11 维权衡矩阵 | 本地留档 | 2026-08 | 存在（17/18 篇） | ~/opencode/archive/Mission-file/2026-08/0813-知识库建库工程/ | C:KG-04 |
| `L-SK-01` | LOCAL | kb-construction 知识库构建全流程主入口 | 本地 skill | 2026 | 存在 | ~/.config/opencode/skills/kb-construction/SKILL.md | C:SK-01 |
| `L-SK-02` | LOCAL | dag-tutorial-authoring DAG 教程编写方法论 | 本地 skill | 2026 | 存在 | ~/.config/opencode/skills/dag-tutorial-authoring/SKILL.md | C:SK-02 |
| `L-SK-03` | LOCAL | cytoscape-dag-visualization 交互 DAG 可视化方法论 | 本地 skill | 2026 | 存在 | ~/.config/opencode/skills/cytoscape-dag-visualization/SKILL.md | C:SK-03 |
| `L-SK-04` | LOCAL | multi-window-dag-delivery 多窗口接力 DAG 分析交付方法论 | 本地 skill | 2026 | 存在 | ~/.config/opencode/skills/multi-window-dag-delivery/SKILL.md | C:SK-04 |
| `L-RL-01` | LOCAL | Software Architect 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-software-architect.md | C:RL-01 |
| `L-RL-02` | LOCAL | Backend Architect 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-backend-architect.md | C:RL-02 |
| `L-RL-03` | LOCAL | Multi-Agent Systems Architect 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-multi-agent-systems-architect.md | C:RL-03 |
| `L-RL-04` | LOCAL | Codebase Onboarding Engineer 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-codebase-onboarding-engineer.md | C:RL-04 |
| `L-RL-05` | LOCAL | Code Reviewer 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-code-reviewer.md | C:RL-05 |
| `L-RL-06` | LOCAL | Minimal Change Engineer 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-minimal-change-engineer.md | C:RL-06 |
| `L-RL-07` | LOCAL | Git Workflow Master 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-git-workflow-master.md | C:RL-07 |
| `L-RL-08` | LOCAL | Senior Developer 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-senior-developer.md | C:RL-08 |
| `L-RL-09` | LOCAL | Rapid Prototyper 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/engineering/engineering-rapid-prototyper.md | C:RL-09 |
| `L-RL-10` | LOCAL | Product Manager 角色 prompt | 本地 agency-agents | 2026 | 存在 | ~/.dsh/agency-agents/product/product-manager.md | C:RL-10 |
| `L-MM-01` | LOCAL | 项目记忆索引 MEMORY.md（建库/架构/编码纪律条目） | 本地记忆 | 2026 | 存在 | ~/.config/opencode/MEMORY.md | C:MM-01 |
| `L-PA-01` | LOCAL | 去中心化聊天架构全景分析 + 模块化 DAG（58 份设计文档） | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0820-去中心化聊天架构分析/ | C:PA-01 |
| `L-PA-02` | LOCAL | OpenJobAutofill Chrome MV3 扩展逆向架构分析 | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0805-OpenJobAutofill逆向分析/ | C:PA-02 |
| `L-PA-03` | LOCAL | 多模块解耦系统架构设计 + 跨模块接口契约（网申 v3） | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0812-网申v3调取复制版/ | C:PA-03 |
| `L-PA-04` | LOCAL | 网申扩展 v2 深度重构 — 架构设计思路与根因分析 | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0806-网申扩展v2实现/ | C:PA-04 |
| `L-PA-05` | LOCAL | harness preset 通道架构耦合分析（dsh 启动失败修复 N7） | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0816-dsh启动失败修复/N7-架构/ | C:PA-05 |
| `L-PA-06` | LOCAL | DeepSeek Harness 插件级 DAG 知识库 RC5→RC7 级联升级 | 本地实战留档 | 2026-08 | 存在（173 插件/49 seam/545 边） | ~/opencode/archive/Mission-file/2026-08/0819-plugin-dag-rc7/ | C:PA-06 |
| `L-PA-07` | LOCAL | dsh 插件 DAG 知识库 RC7→RC8→rc2 级联升级 | 本地实战留档 | 2026-08 | 存在（含两份差异报告） | ~/opencode/archive/Mission-file/2026-08/0822-plugin-dag-v0.1.1-rc2/ | C:PA-07 |
| `L-PA-08` | LOCAL | dsh-manager 插件深度分析（依赖/功能/需求溯源/设计问题）— 三硬依据 E1/E2/E3 | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0822-dsh-manager-analysis/ | C:PA-08 |
| `L-PA-09` | LOCAL | deepseek-harness 源码解析（官方 architecture.md 镜像 + 模块分层） | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0814-deepseek-harness源码解析/ | C:PA-09 |
| `L-PA-10` | LOCAL | dsh-anchored-standard 社区插件依赖位置分析 | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0818-dsh-anchored-standard-analysis/ | C:PA-10 |
| `L-PA-11` | LOCAL | Hermes Agent 整体架构报告（8251 文件工业级项目，七层架构） | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0802-Hermes-Arch/ | C:PA-11 |
| `L-PA-12` | LOCAL | MCP 四件套源码深挖 | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0808-MCP四件套源码深挖/ | C:PA-12 |
| `L-PA-13` | LOCAL | Claude Code Agent 架构深度解析 | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0808-claude-code-analysis/ | C:PA-13 |
| `L-PA-14` | LOCAL | OpenSpec × Superpower 工具解析（含架构对比图） | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0803-OpenSpec_Superpower解析/ | C:PA-14 |
| `L-PA-15` | LOCAL | Open Code Review（阿里 open-code-review）项目解析知识图谱 | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0823-open-code-review/ | C:PA-15 |
| `L-PA-16` | LOCAL | 控制理论 ⊗ Agent 设计知识库 | 本地实战留档 | 2026-09 | 存在 | ~/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/ | C:PA-16 |
| `L-PA-17` | LOCAL | 技术知识中枢方法论（全量版 + 可读 HTML） | 本地实战留档 | 2026-09 | 存在 | ~/opencode/archive/Mission-file/2026-09/0910-技术知识中枢主页/methodology/METHODOLOGY-full.md | C:PA-17 |
| `L-PA-18` | LOCAL | AI Agent 架构 DAG 分析项目复盘 | 本地实战留档 | 2026-08 | 存在 | ~/opencode/archive/Mission-file/2026-08/0818-项目经历撰写/AI Agent 架构 DAG 分析项目复盘.md | C:PA-18 |
| `L-BK-01` | LOCAL | 12 Factor App 官方电子书（epub/mobi） | 本地语料 | 2011；epub/mobi | 存在（版权：仅本地语料层） | ~/opencode/archive/Mission-file/2026-08/0823-12factor项目/12-factor-app/public/12factor.epub | C:BK-01 |
| `L-BK-02` | LOCAL | AI Agents in Depth（中文版，Agent 工程） | 本地语料 | —；PDF | 存在（版权：仅本地语料层） | ~/opencode/archive/AI-Agents-in-Depth-zh-CN.pdf | C:BK-02 |

## 4. 阶段2 F–R 新增/复用信源总表（208 条，包内局部 ID）

> 来源：`02-research/{F..R}-*.json` 的 `sources[]`。**ID 为包内局部编号**，引用须带包名。列为新增（未在 §2 映射）或复用（已在 §2 映射）。P 包 ID 自带 `P-` 前缀，Q 包沿用 `S3-VEN-*`（引用须写 `Q/S3-VEN-*` 以区别 I 包），R 包混合沿用全局 ID 与 `R-XC-*`。

### 4.1 F 包 — `F-requirements.json`（17 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `F/S1-03` | S1 | ISO/IEC/IEEE 12207:2026 — Systems and software engineering — Software life cycle processes（复用 E 包） | ISO / IEC / IEEE | 2026 | False | https://www.iso.org/standard/90219.html | F | 复用（见 §2） |
| `F/S1-07` | S1 | Software Engineering: Report on a conference sponsored by the NATO Science Committee, Garmisch, Germany, 7–11 October 1968（Naur & Randell 编）（复用 A 包） | NATO Science Committee | 1969 | True | http://homepages.cs.ncl.ac.uk/brian.randell/NATO/nato1968.PDF | F | 复用（见 §2） |
| `F/S4-04` | S4 | No Silver Bullet — Essence and Accidents of Software Engineering（Frederick P. Brooks, Jr.，TR86-020）（复用 A 包；本轮获取原始 PDF） | University of North Carolina at Chapel Hill / IEEE Computer | 1986/1987 | True | https://www.cs.unc.edu/techreports/86-020.pdf | F | 复用（见 §2） |
| `F/S1-A01` | S1 | Guide to the Software Engineering Body of Knowledge (SWEBOK Guide V3.0；V4.0 于 2024-10 发布) | IEEE Computer Society（SWEBOK / ISO/IEC TR 19759） | 2014 (V3) / 2024 (V4) | True | https://www.computer.org/education/bodies-of-knowledge/software-engineering | F | 复用（见 §2） |
| `F/S1-F01` | S1 | SWEBOK Guide V4.0 Topics — Chapter 1: Software Requirements Fundamentals（官方目录页快照） | IEEE Computer Society | 2024 | True | https://web.archive.org/web/20241212105347/https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics | F | 新增 |
| `F/S1-F02` | S1 | ISO/IEC/IEEE 29148:2018 — Systems and software engineering — Life cycle processes — Requirements engineering（官方页快照） | ISO / IEC / IEEE（ISO/IEC JTC 1/SC 7） | 2018 | True | https://web.archive.org/web/20240116061908/https://www.iso.org/standard/72089.html | F | 新增 |
| `F/S1-F03` | S1 | IEEE SA — IEEE/ISO/IEC P29148（Active PAR，修订项目） | IEEE Standards Association | 2026（访问时） | True | https://standards.ieee.org/ieee/29148/12262 | F | 新增 |
| `F/S1-F04` | S1 | SEBoK — An Overview of the SWEBOK Guide（软件工程知识体系概览） | BKCASE / Stevens Institute of Technology（Guide to the Systems Engineering Body of Knowledge） | 2026（持续更新） | True | https://sebokwiki.org/wiki/An_Overview_of_the_SWEBOK_Guide | F | 新增 |
| `F/S1-F05` | S1 | SEBoK — Stakeholder Needs and Requirements (glossary)（干系人需要与需求术语条目） | BKCASE / SEBoK | 2026（持续更新） | True | https://sebokwiki.org/wiki/Stakeholder_Needs_and_Requirements_(glossary) | F | 新增 |
| `F/S1-F06` | S1 | SEBoK — Stakeholder (glossary)（干系人术语条目） | BKCASE / SEBoK | 2026（持续更新） | True | https://sebokwiki.org/wiki/Stakeholder_(glossary) | F | 新增 |
| `F/S1-F07` | S1 | SEI — Software Architecture（质量属性与 ATAM 架构评估） | Carnegie Mellon Software Engineering Institute (SEI) | 2026（访问时） | True | https://www.sei.cmu.edu/our-work/software-architecture/ | F | 新增 |
| `F/S1-F08` | S1 | SWEBOK Guide V3.0（PDF 镜像，Chapter 1 Software Requirements Fundamentals） | IEEE Computer Society（镜像：Florida Institute of Technology） | 2014 | False | https://cs.fit.edu/~kgallagher/Schtick/Serious/SWEBOKv3.pdf | F | 新增 |
| `F/S2-F01` | S2 | Software Architecture in Practice — Chapter 4: Quality Attribute Scenarios（Bass, Clements, Kazman，在线章节节选） | Addison-Wesley / SEI（作者含 SEI 首席架构师） | 2003 (2nd ed.) | True | https://people.ece.ubc.ca/matei/EECE417/BASS/ch04lev1sec3.html | F | 新增 |
| `F/S4-F01` | S4 | The application of ISO 29148 to requirements in NZ infrastructure projects（John Welford，INCOSE NZ Conference 2025） | INCOSE New Zealand（会议论文/实务审计） | 2025 | True | http://www.extuitive.co.uk/papers/iso29148NzRequirements.pdf | F | 新增 |
| `F/S4-F02` | S4 | Towards an Anatomy of Software Requirements（Bertrand Meyer，ETH Zurich） | ETH Zurich（学术论文） | 2019 | False | https://se.inf.ethz.ch/~meyer/publications/requirements/requirements_anatomy.pdf | F | 新增 |
| `F/S3-F01` | S3 | ISO/IEC/IEEE 29148:2018 Requirements Characteristics（Possession Planning 汇总页） | Possession Planning（需求管理从业者站点） | 2024 | True | https://possessionplanning.com/traceability-matrix/iso-iec-ieee-291482018 | F | 新增 |
| `F/S3-F02` | S3 | ISO 29148 Explained: Requirements Engineering Standard（Modern Requirements 解释页） | Modern Requirements（需求管理工具厂商） | 2024 | True | https://www.modernrequirements.com/blogs/iso-29148-explained | F | 新增 |

### 4.2 G 包 — `G-architecture.json`（17 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `G/S1-01` | S1 | ISO/IEC/IEEE 42010 — Defining "architecture"（标准编辑 Rich Hilliard 维护的官方解释页） | ISO/IEC/IEEE (iso-architecture.org) | 2022 (2nd ed.) | True | http://www.iso-architecture.org/ieee-1471/defining-architecture.html | G | 复用（见 §2） |
| `G/S1-02` | S1 | SWEBOK Guide V4.0 — Software Architecture KA 与 Software Design KA 分立 | IEEE Computer Society | 2024 | True | https://www.computer.org/education/bodies-of-knowledge/software-engineering | G | 新增 |
| `G/S1-03` | S1 | SEI: What Is Your Definition of Software Architecture?（含 Perry&Wolf / Kruchten / Garlan&Shaw 对照） | Carnegie Mellon University, Software Engineering Institute (SEI) | 2017 (brochure 3854) | True | https://www.sei.cmu.edu/architecture/start/glossary/ | G | 复用（见 §2） |
| `G/S1-04` | S1 | SEI: Software Architecture（架构领域总览页） | Carnegie Mellon University, Software Engineering Institute | n.d. (accessed 2026-09-10) | True | https://www.sei.cmu.edu/architecture/ | G | 复用（见 §2） |
| `G/S1-05` | S1 | SEI ATAM fact sheet: Reduce Risk with Architecture Evaluation（含 risk themes） | Carnegie Mellon University, Software Engineering Institute | 2018 | True | https://www.sei.cmu.edu/documents/2543/2018_010_001_515610.pdf | G | 复用（见 §2） |
| `G/S1-07` | S1 | ISO/IEC/IEEE 42010 — A Conceptual Model of Architecture Description（概念模型细分：视角/视图/模型种类/对应关系/决策与理由） | ISO/IEC/IEEE (iso-architecture.org) | 2022 (2nd ed.) | True | http://www.iso-architecture.org/ieee-1471/cm/ | G | 复用（见 §2） |
| `G/S1-08` | S1 | ISO/IEC/IEEE 42010:2022 标准页（scope 原文与版本状态，经 Wayback 快照核验） | ISO (via web.archive.org) | 2022 | True | https://web.archive.org/web/20260716114220/https://www.iso.org/standard/74393.html | G | 复用（见 §2） |
| `G/S1-09` | S1 | SEI: Views and Beyond — The SEI Approach to Architecture Documentation（官方方法页，Archive 快照） | Carnegie Mellon University, Software Engineering Institute | c. 2011 (archived 2011-08-07) | True | https://web.archive.org/web/20110807114506/http://www.sei.cmu.edu/architecture/tools/document/viewsandbeyond.cfm | G | 新增 |
| `G/S1-10` | S1 | SEI: Methods for Software Architecture Documentation（官方方法页，Archive 快照） | Carnegie Mellon University, Software Engineering Institute | c. 2008 (archived 2008-05-13) | True | https://web.archive.org/web/20080513033149/http://www.sei.cmu.edu/architecture/documentation_methods.html | G | 新增 |
| `G/S1-11` | S1 | ATAM: Method for Architecture Evaluation（CMU/SEI-2000-TR-004, Kazman/Klein/Clements） | Carnegie Mellon University, Software Engineering Institute | 2000-08 | True | https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf | G | 复用（见 §2） |
| `G/S1-12` | S1 | ISO/IEC/IEEE 42020（Architecture processes）与 42030（Architecture evaluation framework）发布信息 | ISO/IEC/IEEE (iso-architecture.org 新闻) | 2019-07 | True | http://www.iso-architecture.org/42010/ | G | 新增 |
| `G/S2-09` | S2 | Documenting Architecture Decisions（ADR 术语原始出处，文中即为一篇 ADR） | Michael Nygard (Cognitect Blog) | 2011-11-15 | True | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | G | 复用（见 §2） |
| `G/S2-10` | S2 | Architecture Decision Record (bliki) | Martin Fowler (martinfowler.com) | 2026-03-24 (updated) | True | https://martinfowler.com/bliki/ArchitectureDecisionRecord.html | G | 复用（见 §2） |
| `G/S2-14` | S2 | An Introduction to Software Architecture（组件-连接件-配置框架与风格分类，含各风格权衡） | David Garlan & Mary Shaw, CMU / SEI (CMU-CS-94-166 / SEI-94-TR-21) | 1993 (book chapter); 1994 (tech report) | True | https://www.cs.cmu.edu/afs/cs/project/able/ftp/intro_softarch/intro_softarch.pdf | G | 复用（见 §2） |
| `G/S2-18` | S2 | Pattern-Oriented Software Architecture, Vol.1: A System of Patterns（架构模式目录） | F. Buschmann et al. (Wiley) | 1996 | False | https://www.wiley.com/ | G | 复用（见 §2） |
| `G/S2-19` | S2 | Documenting Software Architectures: Views and Beyond, 2nd Edition（目录经出版社/零售商 InformIT 页核验） | Paul C. Clements, Felix Bachmann, Len Bass, David Garlan, James Ivers, Reed Little, Paulo Merson, Robert Nord, Judith Stafford (Addison-Wesley) | 2010 | True | https://www.sei.cmu.edu/library/documenting-software-architectures-views-and-beyond-second-edition/ ; https://www.informit.com/store/documenting-software-architectures-views-and-beyond-9780321552686 | G | 复用（见 §2） |
| `G/S3-02` | S3 | Azure Architecture Center — Architecture Styles（云架构风格清单，每风格含适用性/收益/挑战） | Microsoft (Microsoft Learn) | 2025-10-14 (last updated) | True | https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/ | G | 新增 |

### 4.3 H 包 — `H-implementation.json`（18 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `H/S1-01` | S1 | SWEBOK Guide V4.0 (Software Engineering Body of Knowledge) — Software Design (Ch.3) / Software Construction (Ch.4) | IEEE Computer Society | 2024 | True | https://www.computer.org/education/bodies-of-knowledge/software-engineering | H | 复用（见 §2） |
| `H/S1-02` | S1 | ISO/IEC 25010:2023 Product quality model — maintainability sub-characteristics（经 ISO/IEC 25000 官方门户 iso25000.com 核验） | ISO/IEC (via ISO/IEC 25000 SQuaRE portal) | 2023 | True | https://iso25000.com/index.php/en/iso-25000-standards/iso-25010 | H | 复用（见 §2） |
| `H/S2-01` | S2 | On the Criteria To Be Used in Decomposing Systems into Modules（全文回源） | D. L. Parnas, Carnegie-Mellon University; Communications of the ACM, 15(12):1053-1058 | 1972 | True | https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf | H | 复用（见 §2） |
| `H/S2-02` | S2 | A Philosophy of Software Design (2nd ed., 2021) + 作者官方 2nd ed. book extract | John Ousterhout, Stanford University / Yaknyam Press | 2021 (2nd ed.) | True | https://web.stanford.edu/~ouster/cgi-bin/aposd.php ; https://web.stanford.edu/~ouster/cgi-bin/aposd2ndEdExtract.pdf | H | 复用（见 §2） |
| `H/S2-03` | S2 | Code Smell (bliki) | Martin Fowler (martinfowler.com) | 2006-02-09 | True | https://martinfowler.com/bliki/CodeSmell.html | H | 新增 |
| `H/S2-04` | S2 | The Pragmatic Programmer — DRY (Don't Repeat Yourself) 原则 | Andy Hunt & Dave Thomas (Addison-Wesley, 1999) | 1999 | True | https://en.wikipedia.org/wiki/Don%27t_repeat_yourself | H | 新增 |
| `H/S2-05` | S2 | Clean Code (Robert C. Martin) + SOLID + 与 APoSD 的分歧 | Robert C. Martin；Wikipedia 综合（引 Martin 及 Ousterhout 原文） | 2008 (book) / 2000 (SOLID 论文) | True | https://en.wikipedia.org/wiki/Clean_Code ; https://en.wikipedia.org/wiki/SOLID | H | 复用（见 §2） |
| `H/S2-06` | S2 | Design Patterns: Elements of Reusable Object-Oriented Software (GoF) | Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides (Addison-Wesley) | 1994 | True | https://en.wikipedia.org/wiki/Design_Patterns | H | 复用（见 §2） |
| `H/S2-07` | S2 | The Law of Leaky Abstractions | Joel Spolsky (Joel on Software) | 2002-11-11 | True | https://www.joelonsoftware.com/2002/11/11/the-law-of-leaky-abstractions/ | H | 新增 |
| `H/S2-08` | S2 | Big Ball of Mud | Brian Foote & Joseph Yoder（PLoP '97, Fourth Conference on Pattern Languages of Programs） | 1997（页面更新 1999-06-26） | True | http://www.laputan.org/mud/ | H | 新增 |
| `H/S2-09` | S2 | Structured Design（cohesion / coupling 概念的正式发表） | W. P. Stevens, G. J. Myers, L. L. Constantine, IBM Systems Journal 13(2):115-139 | 1974 | True | https://doi.org/10.1147/sj.132.0115 | H | 新增 |
| `H/S2-10` | S2 | Software Engineering at Google — Ch.3 Knowledge Sharing（readability 流程） | Google (abseil.io) | 2020 | True | https://abseil.io/resources/swe-book/html/ch03.html | H | 复用（见 §2） |
| `H/S2-11` | S2 | You Aren't Gonna Need It (YAGNI) — Extreme Programming | Ron Jeffries / Kent Beck, Extreme Programming（XP） | 1998/1999 | True | https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it ; http://ronjeffries.com/xprog/articles/practices/pracnotneed/ | H | 新增 |
| `H/S3-01` | S3 | Refactoring.Guru — Design Patterns 目录 / Code Smells 目录 | Refactoring.Guru（patterns 与 smells 的工程速查门户） | 2014-2026 | True | https://refactoring.guru/design-patterns ; https://refactoring.guru/refactoring/smells | H | 新增 |
| `H/S3-02` | S3 | SourceMaking — Design Patterns / AntiPatterns | SourceMaking | 2007-2026 | True | https://sourcemaking.com/antipatterns ; https://sourcemaking.com/design_patterns | H | 新增 |
| `H/S4-01` | S4 | A Metrics Suite for Object Oriented Design | S. R. Chidamber, C. F. Kemerer, IEEE Transactions on Software Engineering 20(6):476-493 | 1994 | True | https://doi.org/10.1109/32.295895 ; https://mural.maynoothuniversity.ie/id/eprint/2391/1/JM_NUIM-CS-TR-2006-03.pdf | H | 新增 |
| `H/S4-02` | S4 | Bad Smells of Gang of Four Design Patterns: A Decade Systematic Literature Review | S. Almadi, D. Hooshyar, R. B. Ahmad, Sustainability 13(18):10256 | 2021 | True | https://doi.org/10.3390/su131810256 | H | 新增 |
| `H/S4-03` | S4 | A Study of the Fragile Base Class Problem | L. Mikhajlov, E. Sekerinski, ECOOP'98 — Object-Oriented Programming, LNCS 1445:355-382 | 1998 | True | https://doi.org/10.1007/BFb0054099 | H | 新增 |

### 4.4 I 包 — `I-testing.json`（33 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `I/S1-STD-11` | S1 | ISO/IEC/IEEE 29119-1:2022 Software and systems engineering — Software testing — Part 1: General concepts (Edition 2) | ISO/IEC/IEEE | 2022 | True | https://web.archive.org/web/20260217124355id_/https://www.iso.org/standard/81291.html | I | 新增 |
| `I/S1-STD-12` | S1 | ISO/IEC/IEEE 29119-2:2021 Software testing — Part 2: Test processes (Edition 2) | ISO/IEC/IEEE | 2021 | True | https://web.archive.org/web/20260308093756id_/https://www.iso.org/standard/79428.html | I | 新增 |
| `I/S1-STD-13` | S1 | ISO/IEC/IEEE 29119-3:2021 Software testing — Part 3: Test documentation (Edition 2) | ISO/IEC/IEEE | 2021 | True | https://web.archive.org/web/20260217065439id_/https://www.iso.org/standard/79429.html | I | 新增 |
| `I/S1-STD-14` | S1 | ISO/IEC/IEEE 29119-4:2021 Software testing — Part 4: Test techniques (Edition 2) | ISO/IEC/IEEE | 2021 | True | https://web.archive.org/web/20260224134336id_/https://www.iso.org/standard/79430.html | I | 新增 |
| `I/S1-STD-15` | S1 | ISO/IEC/IEEE 29119-5:2024 Software testing — Part 5: Keyword-driven testing (Edition 2) | ISO/IEC/IEEE | 2024 | True | https://web.archive.org/web/20250906170532id_/https://www.iso.org/standard/87233.html | I | 新增 |
| `I/S1-STD-16` | S1 | ISO/IEC TR 29119-6:2021 Software testing — Part 6: Guidelines for the use of ISO/IEC/IEEE 29119 (all parts) in agile projects | ISO/IEC | 2021 | True | https://web.archive.org/web/20230607070622id_/https://www.iso.org/standard/81293.html | I | 新增 |
| `I/S1-STD-17` | S1 | ISO/IEC TR 29119-11:2020 Software testing — Part 11: Guidelines on the testing of AI-based systems | ISO/IEC | 2020 | True | https://web.archive.org/web/20260113122913id_/https://www.iso.org/standard/79016.html | I | 新增 |
| `I/S1-STD-18` | S1 | ISO/IEC TR 29119-13:2022 Software testing — Part 13: Using the ISO/IEC/IEEE 29119 series in the testing of biometric systems | ISO/IEC | 2022 | True | https://web.archive.org/web/20231209142936id_/https://www.iso.org/standard/84220.html | I | 新增 |
| `I/S1-STD-19` | S1 | ISO/IEC 20246:2017 Software and systems engineering — Work product reviews | ISO/IEC | 2017 | True | https://www.iso.org/standard/67407.html | I | 新增 |
| `I/S1-STD-20` | S1 | ISO/IEC 33063:2015 Process assessment model | ISO/IEC | 2015 | True | https://www.iso.org/standard/55154.html | I | 新增 |
| `I/S1-OFF-09` | S1 | ISO/IEC/IEEE 29119 Software Testing — official WG26 site | ISO/IEC JTC 1/SC 7/WG 26 (softwaretestingstandard.org) | 2026 | True | https://softwaretestingstandard.org/ | I | 新增 |
| `I/S1-OFF-10` | S1 | SWEBOK Guide V4.0 — Chapter 5: Software Testing | IEEE Computer Society | 2024 | True | https://www.computer.org/education/bodies-of-knowledge/software-engineering/v4 | I | 新增 |
| `I/S1-OFF-11` | S1 | ISTQB Certified Tester Foundation Level (CTFL) Syllabus v4.0.1 | International Software Testing Qualifications Board (ISTQB) | 2024 | True | https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf | I | 新增 |
| `I/S1-OFF-05` | S1 | ISO 25000 Portal — ISO/IEC 25010 quality model | AENOR / iso25000.com | 2024 | True | https://iso25000.com/index.php/en/iso-25000-standards/iso-25010?start=5 | I | 复用（见 §2） |
| `I/S1-OFF-12` | S1 | A Taxonomy of Testing (SEI Blog) | CMU Software Engineering Institute（Donald Firesmith） | 2015 | True | https://www.sei.cmu.edu/blog/a-taxonomy-of-testing/ | I | 新增 |
| `I/S1-OFF-13` | S1 | Four Types of Shift Left Testing (SEI Blog) | CMU Software Engineering Institute（Donald Firesmith） | 2015 | True | https://www.sei.cmu.edu/blog/four-types-of-shift-left-testing/ | I | 新增 |
| `I/S1-OFF-14` | S1 | Using Quality Attributes as a Means to Improve Acquisition Strategies (SEI Blog) | CMU Software Engineering Institute（Lisa Brownsword） | 2014 | True | https://www.sei.cmu.edu/blog/using-quality-attributes-as-a-means-to-improve-acquisition-strategies/ | I | 新增 |
| `I/S2-WEB-12` | S2 | Test Pyramid (martinfowler.com bliki) | Martin Fowler | 2012 | True | https://martinfowler.com/bliki/TestPyramid.html | I | 新增 |
| `I/S2-WEB-13` | S2 | The Practical Test Pyramid (martinfowler.com) | Ham Vocke（Thoughtworks） | 2018 | True | https://martinfowler.com/articles/practical-test-pyramid.html | I | 新增 |
| `I/S2-WEB-14` | S2 | Test Driven Development (martinfowler.com bliki) | Martin Fowler | 2023 | True | https://martinfowler.com/bliki/TestDrivenDevelopment.html | I | 新增 |
| `I/S2-WEB-15` | S2 | Unit Test (martinfowler.com bliki) | Martin Fowler | 2014 | True | https://martinfowler.com/bliki/UnitTest.html | I | 新增 |
| `I/S2-WEB-16` | S2 | Integration Test (martinfowler.com bliki) | Martin Fowler | 2018 | True | https://martinfowler.com/bliki/IntegrationTest.html | I | 新增 |
| `I/S2-WEB-17` | S2 | Test Double (martinfowler.com bliki) | Martin Fowler（Gerard Meszaros 词汇） | 2006 | True | https://martinfowler.com/bliki/TestDouble.html | I | 新增 |
| `I/S2-WEB-18` | S2 | Continuous Integration (martinfowler.com) | Martin Fowler | 2024 | True | https://martinfowler.com/articles/continuousIntegration.html | I | 新增 |
| `I/S2-WEB-19` | S2 | Kent Beck — Software Design Pioneer（个人官网） | Kent Beck | 2026 | True | https://kentbeck.com/ | I | 新增 |
| `I/S2-BK-01` | S2 | Software Engineering at Google, Ch.11 Testing Overview; Ch.14 Larger Testing | Titus Winters, Tom Manshreck, Hyrum Wright（Google，abseil.io 免费 HTML） | 2020 | True | https://abseil.io/resources/swe-book/html/ch14.html | I | 复用（见 §2） |
| `I/S2-BK-09` | S2 | Software Architecture in Practice, 4th Edition（SAiP 4e）Ch.12 Testability | Len Bass, Paul Clements, Rick Kazman（Addison-Wesley） | 2021 | True | https://www.informit.com/store/software-architecture-in-practice-9780136886099 | I | 复用（见 §2） |
| `I/S2-BK-28` | S2 | Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation | Jez Humble, David Farley（Addison-Wesley） | 2010 | True | https://www.informit.com/store/continuous-delivery-9780321601919 | I | 复用（见 §2） |
| `I/S2-BK-29` | S2 | Accelerate: The Science of Lean Software and DevOps（DORA 四指标原始研究） | Nicole Forsgren, Jez Humble, Gene Kim（IT Revolution） | 2018 | True | https://dora.dev/ | I | 复用（见 §2） |
| `I/S2-BK-30` | S2 | Succeeding with Agile: Software Development Using Scrum（测试金字塔原始模型） | Mike Cohn（Addison-Wesley） | 2009 | False | https://www.mountaingoatsoftware.com/books/succeeding-with-agile | I | 碰撞（见 §5） |
| `I/S3-VEN-02` | S3 | Google Testing Blog: Test Sizes (2010) / Just Say No to More End-to-End Tests (2015) | Google | 2010/2015 | True | https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html | I | 新增 |
| `I/S3-VEN-03` | S3 | DORA — Software delivery performance metrics (five keys) | DORA / Google Cloud | 2024 | True | https://dora.dev/guides/dora-metrics-four-keys/ | I | 新增 |
| `I/S3-VEN-04` | S3 | SonarQube Server Documentation — Understanding quality gates | SonarSource | 2026 | True | https://docs.sonarsource.com/sonarqube-server/latest/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates/ | I | 新增 |

### 4.5 J 包 — `J-deployment.json`（13 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `J/S2-01` | S2 | The Twelve-Factor App | Adam Wiggins / 12factor.net (Salesforce) | 2017 | True | https://12factor.net/ | J | 复用（见 §2） |
| `J/S2-02` | S2 | Blue Green Deployment (bliki) | Martin Fowler | 2010 | True | https://martinfowler.com/bliki/BlueGreenDeployment.html | J | 新增 |
| `J/S2-03` | S2 | Canary Release (bliki) | Danilo Sato / Martin Fowler | 2014 | True | https://martinfowler.com/bliki/CanaryRelease.html | J | 新增 |
| `J/S2-04` | S2 | Immutable Server (bliki) | Kief Morris / Martin Fowler | 2013 | True | https://martinfowler.com/bliki/ImmutableServer.html | J | 新增 |
| `J/S2-05` | S2 | Phoenix Server (bliki) | Martin Fowler | 2012 | True | https://martinfowler.com/bliki/PhoenixServer.html | J | 新增 |
| `J/S2-06` | S2 | Deployment Pipeline (bliki) | Martin Fowler (致谢 Jez Humble) | 2013 | True | https://martinfowler.com/bliki/DeploymentPipeline.html | J | 新增 |
| `J/S2-07` | S2 | Site Reliability Engineering — Chapter 8: Release Engineering | Google (Dinah McNutt), O'Reilly, CC BY-NC-ND | 2017 | True | https://sre.google/sre-book/release-engineering/ | J | 复用（见 §2） |
| `J/S3-01` | S3 | DORA — Deployment automation (DevOps capability) | DORA / Google Cloud | 2024 | True | https://dora.dev/devops-capabilities/technical/deployment-automation | J | 新增 |
| `J/S3-02` | S3 | Blue/Green Deployments on AWS (Whitepaper) | Amazon Web Services | 2021 | True | https://docs.aws.amazon.com/whitepapers/latest/blue-green-deployments/introduction.html | J | 新增 |
| `J/S3-03` | S3 | Architecture strategies for safe deployment practices (Azure Well-Architected Framework) | Microsoft Azure | 2026 | True | https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments | J | 新增 |
| `J/S3-04` | S3 | Kubernetes Documentation — Deployments | The Kubernetes Authors (CNCF) | 2026 | True | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | J | 新增 |
| `J/S3-05` | S3 | Cloud Native Glossary — Immutable Infrastructure | CNCF | 2022 | True | https://glossary.cncf.io/immutable-infrastructure/ | J | 新增 |
| `J/BK-01` | S2 | 12 Factor App（本地电子书，仅本地语料层） | Adam Wiggins (local epub) | 2017 | True | local: ~/opencode/archive/Mission-file/2026-08/0823-12factor项目/12-factor-app/public/12factor.epub | J | 复用（见 §2） |

### 4.6 K 包 — `K-operations.json`（12 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `K/S2-01` | S2 | Site Reliability Engineering: How Google Runs Production Systems (Google SRE Book) | Google / O'Reilly Media | 2017 | True | https://sre.google/sre-book/table-of-contents/ | K | 复用（见 §2） |
| `K/S2-02` | S2 | The Site Reliability Workbook: Practical Ways to Implement SRE | Google / O'Reilly Media | 2018 | True | https://sre.google/workbook/table-of-contents/ | K | 复用（见 §2） |
| `K/S2-03` | S2 | Release It! Second Edition: Design and Deploy Production-Ready Software | Michael T. Nygard / The Pragmatic Bookshelf | 2018 | True | https://pragprog.com/titles/mnee2/release-it-second-edition/ | K | 复用（见 §2） |
| `K/S2-04` | S2 | CircuitBreaker (bliki) | Martin Fowler | 2014 | True | https://martinfowler.com/bliki/CircuitBreaker.html | K | 新增 |
| `K/S2-05` | S2 | Principles of Chaos Engineering | Chaos Engineering Community / CNCF | 2019 | True | https://principlesofchaos.org/ | K | 新增 |
| `K/S2-06` | S2 | Blameless PostMortems and a Just Culture | John Allspaw / Etsy Code as Craft（经 web.archive.org 快照） | 2012 | True | https://web.archive.org/web/2019id_/https://codeascraft.com/2012/05/22/blameless-postmortems/ | K | 新增 |
| `K/S3-01` | S3 | Cloud Design Patterns: Circuit Breaker / Bulkhead / Retry | Microsoft Azure Architecture Center (Microsoft Learn) | 2026 | True | https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker | K | 新增 |
| `K/S3-02` | S3 | Observability Primer & Signals | OpenTelemetry (CNCF) | 2026 | True | https://opentelemetry.io/docs/concepts/observability-primer/ | K | 新增 |
| `K/S3-03` | S3 | Service Level Objectives (SLO) 文档 / What is observability? | Datadog | 2026 | True | https://docs.datadoghq.com/service_management/service_level_objectives/ | K | 新增 |
| `K/S3-04` | S3 | Exponential Backoff And Jitter | AWS Architecture Blog（Amazon） | 2015 (updated 2023) | True | https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ | K | 新增 |
| `K/S3-05` | S3 | DORA's software delivery metrics: the four keys | DORA / Google Cloud | 2026 | True | https://dora.dev/guides/dora-metrics-four-keys/ | K | 新增 |
| `K/S3-06` | S3 | Architecture strategies for defining reliability targets | Microsoft Azure Well-Architected Framework | 2026 | True | https://learn.microsoft.com/en-us/azure/well-architected/reliability/metrics | K | 新增 |

### 4.7 L 包 — `L-evolution.json`（24 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `L/S1-01` | S1 | ISO/IEC/IEEE 14764:2022 — Software engineering — Software life cycle processes — Maintenance | ISO/IEC/IEEE | 2022 | True | https://web.archive.org/web/20260819024657/https://www.iso.org/standard/80710.html | L | 复用（见 §2） |
| `L/S1-02` | S1 | RFC 8594 — The Sunset HTTP Header Field | IETF (Internet Engineering Task Force) | 2019 | True | https://www.rfc-editor.org/rfc/rfc8594.txt | L | 新增 |
| `L/S1-03` | S1 | RFC 9745 — The Deprecation HTTP Response Header Field | IETF (Internet Engineering Task Force) | 2025 | True | https://www.rfc-editor.org/rfc/rfc9745.txt | L | 新增 |
| `L/S2-01` | S2 | Technical Debt (bliki) | Martin Fowler (martinfowler.com) | 2019-05-21 | True | https://martinfowler.com/bliki/TechnicalDebt.html | L | 复用（见 §2） |
| `L/S2-02` | S2 | The WyCash Portfolio Management System (OOPSLA'92 Experience Report) | Ward Cunningham (c2.com) | 1992-03-26 | True | https://c2.com/doc/oopsla92.html | L | 复用（见 §2） |
| `L/S2-03` | S2 | Technical Debt Quadrant (bliki) | Martin Fowler (martinfowler.com) | 2009-10-14 | True | https://martinfowler.com/bliki/TechnicalDebtQuadrant.html | L | 新增 |
| `L/S2-04` | S2 | Definition Of Refactoring (bliki) | Martin Fowler (martinfowler.com) | 2004-09-01 | True | https://martinfowler.com/bliki/DefinitionOfRefactoring.html | L | 复用（见 §2） |
| `L/S2-05` | S2 | Catalog of Refactorings（Refactoring 2nd Edition 官方在线目录） | Martin Fowler / martinfowler.com (refactoring.com) | 2018 (2nd ed.) | True | https://refactoring.com/catalog/ | L | 复用（见 §2） |
| `L/S2-06` | S2 | Code Smell (bliki) | Martin Fowler (martinfowler.com) | 2006-02-09 | True | https://martinfowler.com/bliki/CodeSmell.html | L | 新增 |
| `L/S2-07` | S2 | Strangler Fig (bliki) | Martin Fowler (martinfowler.com) | 2024-08-22 | True | https://martinfowler.com/bliki/StranglerFigApplication.html | L | 新增 |
| `L/S2-08` | S2 | The Second Edition of "Refactoring" | Martin Fowler (martinfowler.com) | 2018 | True | https://martinfowler.com/articles/refactoring-2nd-ed.html | L | 新增 |
| `L/S2-09` | S2 | Testing Effectively With Legacy Code（Working Effectively with Legacy Code 官方章节节选：Seams / Seam Types） | Michael Feathers / InformIT (Pearson) | 2005-01-21 | True | https://www.informit.com/articles/article.aspx?p=359417&seqNum=2 | L | 复用（见 §2） |
| `L/S2-10` | S2 | characterization tests interactively | Michael Feathers (silvrback blog) | 2020-09-22 | True | https://michaelfeathers.silvrback.com/ | L | 新增 |
| `L/S2-11` | S2 | Foundations for the Study of Software Architecture | D. E. Perry & A. L. Wolf, ACM SIGSOFT Software Engineering Notes 17(4), pp.40-52 | 1992-10 | True | https://users.ece.utexas.edu/~perry/work/papers/swa-sen.pdf | L | 新增 |
| `L/S2-12` | S2 | Building Evolutionary Architectures（作者官方书页） | Neal Ford, Rebecca Parsons, Patrick Kua, Pramod Sadalage (nealford.com / O'Reilly) | 2017 (1st ed.) / 2022 (2nd ed.) | True | https://nealford.com/books/buildingevolutionaryarchitectures.html | L | 复用（见 §2） |
| `L/S2-13` | S2 | Building Evolutionary Architectures, Sample Chapter (Chapter 1) | Neal Ford et al. / Thoughtworks (官方样章 PDF) | 2017 | True | https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_building_evolutionary_architectures_en.pdf | L | 复用（见 §2） |
| `L/S3-01` | S3 | Fitness function-driven development | Paula Paul & Rosemary Wang, Thoughtworks | 2019-01-11 | True | https://www.thoughtworks.com/insights/blog/fitness-function-driven-development | L | 新增 |
| `L/S3-02` | S3 | Technology Radar — Architectural fitness function (Techniques, Trial, May 2018) | Thoughtworks Technology Radar | 2018-05 | True | https://www.thoughtworks.com/radar/techniques/architectural-fitness-function | L | 新增 |
| `L/S3-03` | S3 | Google AIP-180 — Backwards compatibility（API Improvement Proposals，State: Approved） | Google (google.aip.dev) | 2019 (updated) | True | https://google.aip.dev/180 | L | 新增 |
| `L/S3-04` | S3 | Modern Lifecycle Policy（Microsoft Lifecycle 官方政策） | Microsoft Learn | n.d. (accessed 2026-09-10) | True | https://learn.microsoft.com/en-us/lifecycle/policies/modern | L | 新增 |
| `L/S3-05` | S3 | Semantic Versioning 2.0.0 (spec) | Tom Preston-Werner (semver.org) | 2013 / spec 2.0.0 | True | https://semver.org/ | L | 新增 |
| `L/S4-01` | S4 | Understanding software architecture erosion: A systematic mapping study | R. Li, P. Liang, M. Soliman, P. Avgeriou, Journal of Software: Evolution and Process, DOI 10.1002/smr.2423 | 2022 | True | https://doi.org/10.1002/smr.2423 | L | 复用（见 §2） |
| `L/S4-02` | S4 | Programs, Life Cycles, and Laws of Software Evolution | M. M. Lehman, Proceedings of the IEEE 68(9), pp.1060-1076, DOI 10.1109/PROC.1980.11805 | 1980 | True | https://doi.org/10.1109/PROC.1980.11805 | L | 复用（见 §2） |
| `L/S4-03` | S4 | Technical Debt: From Metaphor to Theory and Practice | P. Kruchten, R. Nord, I. Ozkaya, IEEE Software 29(6), DOI 10.1109/MS.2012.167 | 2012-11 | True | https://doi.org/10.1109/MS.2012.167 | L | 新增 |

### 4.8 M 包 — `M-quality-ility.json`（13 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `M/S1-M01` | S1 | ISO/IEC 25010:2023 Systems and software engineering — SQuaRE — Product quality model（产品质量模型，第二版） | ISO/IEC（JTC 1/SC 7） | 2023 | False | https://www.iso.org/obp/ui#iso:std:iso-iec:25010:en | M | 复用（见 §2） |
| `M/S1-M02` | S1 | ISO/IEC 25002:2024 Systems and software engineering — SQuaRE — Quality model overview and usage（质量模型总览与使用，第一版） | ISO/IEC（JTC 1/SC 7） | 2024 | True | https://www.iso.org/standard/78175.html | M | 新增 |
| `M/S1-M03` | S1 | ISO/IEC 25019:2023 Systems and software engineering — SQuaRE — Quality-in-use model（使用质量模型，第一版） | ISO/IEC（JTC 1/SC 7） | 2023 | True | https://www.iso.org/standard/78177.html | M | 新增 |
| `M/S1-M04` | S1 | Kazman, R., Echeverría, S., & Ivers, J. (2022). Extensibility (CMU/SEI-2022-TR-002) | Software Engineering Institute, Carnegie Mellon University | 2022 | True | https://www.sei.cmu.edu/library/extensibility | M | 新增 |
| `M/S1-M05` | S1 | Scott, J., & Kazman, R. (2009). Realizing and Refining Architectural Tactics: Availability (CMU/SEI-2009-TR-006) | Software Engineering Institute, Carnegie Mellon University | 2009 | True | https://www.sei.cmu.edu/library/realizing-and-refining-architectural-tactics-availability | M | 新增 |
| `M/S1-M06` | S1 | Bachmann, F., Bass, L., & Nord, R. (2007). Modifiability Tactics (CMU/SEI-2007-TR-009) | Software Engineering Institute, Carnegie Mellon University | 2007 | True | https://www.sei.cmu.edu/library/modifiability-tactics | M | 新增 |
| `M/S1-M07` | S1 | SEI — Reasoning About Software Quality Attributes (Quality Attribute General Scenarios & Attribute Primitives) | Software Engineering Institute, Carnegie Mellon University | n.d. (accessed 2026-09-10) | True | https://www.sei.cmu.edu/library/reasoning-about-software-quality-attributes | M | 新增 |
| `M/S1-M08` | S1 | ISO/IEC/IEEE 14764:2022 Software engineering — Software life cycle processes — Maintenance（复用 E 包） | ISO/IEC/IEEE | 2022 | True | https://www.iso.org/standard/80710.html | M | 复用（见 §2） |
| `M/S2-M01` | S2 | ISO 25000 Portal — ISO/IEC 25010（质量模型九特性与子特性逐条释义） | ISO 25000 Portal (iso25000.com) | 2024 (site) | True | https://iso25000.com/index.php/en/iso-25000-standards/iso-25010 | M | 复用（见 §2） |
| `M/S2-M02` | S2 | Bass, L., Clements, P., & Kazman, R. — Software Architecture in Practice, Ch.5 'Introducing Tactics'（UBC EECE417 镜像） | Addison-Wesley / SEI Series（镜像站为课程公开页） | 2012/2021 | True | https://people.ece.ubc.ca/matei/EECE417/BASS/ch05lev1sec1.html | M | 复用（见 §2） |
| `M/S4-M01` | S4 | Breivold, H. P. — A Systematic Review of Software Evolvability（IEEE/ICSE 系系统综述） | ABB Corporate Research / Mälardalen University | 2009 (published)/2012 | True | https://www.es.mdh.se/pdf_publications/1739.pdf | M | 新增 |
| `M/S4-M02` | S4 | Rowe, D., Leaney, J., & Lowe, D. (1994). Defining systems evolvability — a taxonomy of change | IEEE Conference on Computer Based Systems (cited in S4-M01) | 1994 | False | https://www.researchgate.net/profile/John-Leaney/publication/240718016 | M | 新增 |
| `M/S4-M03` | S4 | Glinz, M., et al. (2023). Towards a Modern Quality Framework（IEEE RE Workshops, REW 2023） | University of Zurich / IEEE | 2023 | True | https://upcommons.upc.edu/bitstreams/aa5bbbe8-740f-41ac-953a-1b0322541abe/download | M | 新增 |

### 4.9 N 包 — `N-team-conway.json`（13 条）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `N/S2-01` | S2 | How Do Committees Invent? (a.k.a. Conway's Law 原文) | Melvin E. Conway / Datamation, F. D. Thompson Publications | 1968 | True | https://www.melconway.com/Home/Committees_Paper.html | N | 新增 |
| `N/S2-02` | S2 | Conway's Law（作者本人说明页 + Brooks 命名溯源） | Melvin E. Conway (melconway.com) | 2010 | True | https://www.melconway.com/Home/Conways_Law.html | N | 新增 |
| `N/S2-03` | S2 | Conway's Law (bliki) | Martin Fowler / martinfowler.com | 2022 | True | https://martinfowler.com/bliki/ConwaysLaw.html | N | 新增 |
| `N/S2-04` | S2 | Team Topologies (bliki) | Martin Fowler / martinfowler.com | 2023 | True | https://martinfowler.com/bliki/TeamTopologies.html | N | 复用（见 §2） |
| `N/S2-05` | S2 | Team Topologies: Key Concepts（作者官方站点） | Matthew Skelton & Manuel Pais / teamtopologies.com | 2026 | True | https://teamtopologies.com/key-concepts | N | 新增 |
| `N/S2-06` | S2 | Team Topologies: Organizing Business and Technology Teams for Fast Flow（官方书页） | Matthew Skelton & Manuel Pais / IT Revolution Press | 2019 | True | https://teamtopologies.com/book | N | 复用（见 §2） |
| `N/S3-01` | S3 | Inverse Conway Maneuver (Technology Radar) | Thoughtworks Technology Radar | 2015 | True | https://www.thoughtworks.com/radar/techniques/inverse-conway-maneuver | N | 新增 |
| `N/S3-02` | S3 | DORA's software delivery performance metrics（当前官方口径） | DORA / Google Cloud | 2026 | True | https://dora.dev/guides/dora-metrics/ | N | 新增 |
| `N/S3-03` | S3 | A history of DORA's software delivery metrics | Nathen Harvey / DORA (Google Cloud) | 2026 | True | https://dora.dev/insights/dora-metrics-history | N | 新增 |
| `N/S3-04` | S3 | Accelerate State of DevOps Report 2024（DORA 官方报告页） | DORA / Google Cloud | 2024 | True | https://dora.dev/research/2024/dora-report/ | N | 新增 |
| `N/S3-05` | S3 | Organizing Agile Teams and ARTs: Team Topologies at Scale | Scaled Agile Framework (SAFe) | 2026 | True | https://framework.scaledagile.com/organizing-agile-teams-and-arts-team-topologies-at-scale | N | 新增 |
| `N/S4-01` | S4 | Exploring the duality between product and organizational architectures: A test of the 'mirroring' hypothesis | Alan MacCormack, Carliss Baldwin, John Rusnak / Research Policy 41(8):1309-1324 (Elsevier) | 2012 | True | https://ideas.repec.org/a/eee/respol/v41y2012i8p1309-1324.html | N | 新增 |
| `N/S4-02` | S4 | The mirroring hypothesis: theory, evidence, and exceptions | Lyra J. Colfer & Carliss Y. Baldwin / Industrial and Corporate Change 25(5):709-737 (Oxford) | 2016 | True | https://www.hbs.edu/ris/Publication%20Files/Colfer%20Baldwin%20Mirroring%20Hypothesis%20Ind%20Corp%20Change-2016_8aa320ff-6aa6-42ef-b259-d139012faaf6.pdf | N | 新增 |

### 4.10 P 包 — `P-techdebt.json`（27 条，新增技术债独立证据包）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `P-S1-01` | S1 | Technical Debt: From Metaphor to Theory and Practice（SEI 资产页，含摘要） | Carnegie Mellon University, Software Engineering Institute (SEI) | 2012 | True | https://www.sei.cmu.edu/library/technical-debt-from-metaphor-to-theory-and-practice/ | P | 新增（与 `P/P-S4-01` 同论文，见 §2） |
| `P-S1-02` | S1 | ISO/IEC 25010:2023 — Product quality model（maintainability 质量特性） | ISO/IEC（ISO OBP，经 25000 门户核验） | 2023 | True | https://www.iso.org/obp/ui#iso:std:iso-iec:25010:en | P | 复用（见 §2） |
| `P-S2-01` | S2 | Technical Debt (bliki) | Martin Fowler (martinfowler.com) | 2019-05-21（原 2003-10-01，2019 重写） | True | https://martinfowler.com/bliki/TechnicalDebt.html | P | 复用（见 §2） |
| `P-S2-02` | S2 | Technical Debt Quadrant (bliki) | Martin Fowler (martinfowler.com) | 2009-10-14（2014-11-19 repost） | True | https://martinfowler.com/bliki/TechnicalDebtQuadrant.html | P | 新增（另见 `L/S2-03`，见 §2） |
| `P-S2-03` | S2 | The WyCash Portfolio Management System (OOPSLA'92 Experience Report) | Ward Cunningham (c2.com) | 1992-03-26 | True | https://c2.com/doc/oopsla92.html | P | 复用（见 §2） |
| `P-S2-04` | S2 | Opportunistic Refactoring (bliki) | Martin Fowler (martinfowler.com) | 2011-11-01 | True | https://martinfowler.com/bliki/OpportunisticRefactoring.html | P | 新增 |
| `P-S2-05` | S2 | Design Stamina Hypothesis (bliki) | Martin Fowler (martinfowler.com) | 2007-06-20 | True | https://martinfowler.com/bliki/DesignStaminaHypothesis.html | P | 新增 |
| `P-S2-06` | S2 | Strangler Fig (bliki) | Martin Fowler (martinfowler.com) | 2024-08-22 | True | https://martinfowler.com/bliki/StranglerFigApplication.html | P | 复用（见 §2） |
| `P-S2-07` | S2 | Definition Of Refactoring (bliki) | Martin Fowler (martinfowler.com) | 2004-09-01 | True | https://martinfowler.com/bliki/DefinitionOfRefactoring.html | P | 复用（见 §2） |
| `P-S2-08` | S2 | Code Smell (bliki) | Martin Fowler (martinfowler.com) | 2006-02-09 | True | https://martinfowler.com/bliki/CodeSmell.html | P | 复用（见 §2） |
| `P-S2-09` | S2 | Is High Quality Software Worth the Cost? (article) | Martin Fowler (martinfowler.com) | 2019-05-29 | True | https://martinfowler.com/articles/is-quality-worth-cost.html | P | 新增 |
| `P-S2-10` | S2 | Foundations for the Study of Software Architecture | D. E. Perry & A. L. Wolf, ACM SIGSOFT Software Engineering Notes 17(4), pp.40-52 | 1992-10 | True | https://users.ece.utexas.edu/~perry/work/papers/swa-sen.pdf | P | 复用（见 §2） |
| `P-S3-01` | S3 | Metric definitions（SonarQube Server 官方文档） | SonarSource (docs.sonarsource.com) | n.d.（accessed 2026-09-10，Server 2026.4） | True | https://docs.sonarsource.com/sonarqube/latest/user-guide/metric-definitions/ | P | 新增 |
| `P-S3-02` | S3 | Viewing and managing rules（SonarQube Server 官方文档，含 issue 类型与 clean code 属性） | SonarSource (docs.sonarsource.com) | n.d.（accessed 2026-09-10，Server 2026.4） | True | https://docs.sonarsource.com/sonarqube-server/quality-standards-administration/managing-rules/rules | P | 新增 |
| `P-S3-03` | S3 | SQALE — Software Quality Assessment based on Lifecycle Expectations（官方站点，Wayback 快照） | SQALE / inspearit (formerly DNV ITGS France) | 2014（站点）/ 方法 2010s | True | https://web.archive.org/web/2016/http://www.sqale.org/ | P | 新增 |
| `P-S4-01` | S4 | Technical Debt: From Metaphor to Theory and Practice | P. Kruchten, R. L. Nord, I. Ozkaya, IEEE Software 29(6), pp.18-21 | 2012-11 | True | https://doi.org/10.1109/MS.2012.167 | P | 复用（见 §2） |
| `P-S4-02` | S4 | Managing Technical Debt with the SQALE Method | J.-L. Letouzey, M. Ilkiewicz, IEEE Software 29(6), pp.44-51 | 2012-11 | True | https://doi.org/10.1109/MS.2012.129 | P | 新增 |
| `P-S4-03` | S4 | A systematic mapping study on technical debt and its management | Z. Li, P. Avgeriou, P. Liang, Journal of Systems and Software 101 | 2015-03 | True | https://doi.org/10.1016/j.jss.2014.12.027 | P | 新增 |
| `P-S4-04` | S4 | Towards an Ontology of Terms on Technical Debt | Alves, Ribeiro, Caires, Mendes, Spinola, MTD 2014 | 2014-09 | True | https://doi.org/10.1109/MTD.2014.9 | P | 新增 |
| `P-S4-05` | S4 | An Overview and Comparison of Technical Debt Measurement Tools | IEEE Software | 2020 | True | https://doi.org/10.1109/MS.2020.3024958 | P | 新增 |
| `P-S4-06` | S4 | Automatic identification of self-admitted technical debt from four different sources | Empirical Software Engineering | 2023 | True | https://doi.org/10.1007/s10664-023-10297-9 | P | 新增 |
| `P-S4-07` | S4 | A systematic literature review on Technical Debt prioritization: Strategies, processes, factors, and tools | Journal of Systems and Software 171 | 2020 | True | https://doi.org/10.1016/j.jss.2020.110827 | P | 新增 |
| `P-S4-08` | S4 | Understanding software architecture erosion: A systematic mapping study | R. Li, P. Liang, M. Soliman, P. Avgeriou, JSEP | 2022 | True | https://doi.org/10.1002/smr.2423 | P | 复用（见 §2） |
| `P-S4-09` | S4 | Programs, Life Cycles, and Laws of Software Evolution | M. M. Lehman, Proceedings of the IEEE 68(9), pp.1060-1076 | 1980 | True | https://doi.org/10.1109/PROC.1980.11805 | P | 复用（见 §2） |
| `P-S4-10` | S4 | Software developer productivity loss due to technical debt—A replication and extension study | Journal of Systems and Software 156 | 2019 | True | https://doi.org/10.1016/j.jss.2019.06.004 | P | 新增 |
| `P-S4-11` | S4 | Building and evaluating a theory of architectural technical debt in software-intensive systems | Journal of Systems and Software 176 | 2021 | True | https://doi.org/10.1016/j.jss.2021.110925 | P | 新增 |
| `P-S4-12` | S4 | Identification and measurement of Requirements Technical Debt in software development: A systematic literature review | Journal of Systems and Software 190 | 2022 | True | https://doi.org/10.1016/j.jss.2022.111483 | P | 新增 |

### 4.11 Q 包 — `Q-vendor-architecture.json`（7 条，新增厂商架构框架 / 采用雷达）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `Q/S3-VEN-02` | S3 | AWS Well-Architected Framework — The pillars of the framework（官方文档） | Amazon Web Services (AWS Documentation) | 2024-11-06 | True | https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html | Q | 新增（与 `I/S3-VEN-02` 名义碰撞，见 §5） |
| `Q/S3-VEN-03` | S3 | AWS Well-Architected Framework（官方白皮书 PDF，含各支柱定义与设计原则） | Amazon Web Services | 2024-11-06 | True | https://docs.aws.amazon.com/pdfs/wellarchitected/latest/framework/wellarchitected-framework.pdf | Q | 新增 |
| `Q/S3-VEN-04` | S3 | Google Cloud Well-Architected Framework（原 Google Cloud Architecture Framework） | Google Cloud (Cloud Architecture Center) | 2026-01-28 (Last reviewed) | True | https://cloud.google.com/architecture/framework | Q | 新增 |
| `Q/S3-VEN-05` | S3 | Google Cloud WAF 支柱页与 What's new（各支柱 core principles 与变更记录） | Google Cloud (Cloud Architecture Center) | 2024-10 ~ 2026-02 | True | https://cloud.google.com/architecture/framework/whats-new | Q | 新增 |
| `Q/S3-VEN-06` | S3 | Thoughtworks Technology Radar（官方主页，Vol 34 / April 2026） | Thoughtworks | 2026-04 (Vol 34) | True | https://www.thoughtworks.com/radar | Q | 新增 |
| `Q/S3-VEN-07` | S3 | Thoughtworks Technology Radar FAQ — 四环与四象限机制（方法论官方说明） | Thoughtworks | 2026 (accessed 2026-09-10) | True | https://www.thoughtworks.com/radar/faq | Q | 新增 |
| `Q/S3-VEN-08` | S3 | Thoughtworks Technology Radar 归档 PDF（Vol 26–34，用于核对第四环 Hold→Caution 演变） | Thoughtworks | 2022-03 ~ 2026-04 | True | https://www.thoughtworks.com/radar/archive | Q | 新增 |

### 4.12 R 包 — `R-foundational-papers.json`（14 条，新增奠基文献）

| ID | tier | 标题/标准号 | 机构 | 年份/版本 | verified | URL | 来源包 | 状态 |
|---|---|---|---|---|---|---|---|---|
| `R/S4-PAP-04` | S4 | Managing the Development of Large Software Systems（Royce 1970 原文） | Winston W. Royce, TRW; Proceedings, IEEE WESCON, pp.1-9 | 1970 | True | https://web.archive.org/web/2019id_/http://www-scf.usc.edu/~csci201/lectures/Lecture11/royce1970.pdf | R | 复用（沿用全局 ID，见 §2） |
| `R/S4-PAP-03` | S4 | Programs, Life Cycles, and Laws of Software Evolution（Lehman 1980 原文） | M. M. Lehman; Proceedings of the IEEE 68(9):1060-1076 | 1980 | False | https://doi.org/10.1109/proc.1980.11805 | R | 复用（见 §2；abstract-only） |
| `R/S4-PAP-05` | S4 | Software Engineering Programmes Are Not Computer Science Programmes（Parnas 1998 原文） | David Lorge Parnas, McMaster Univ.; Annals of Software Engineering 6:19-37 | 1998 | True | https://bioinfo.uib.es/~joemiro/semdoc/PlansEstudis/Bachelor_Masters_Curricula/DParnas.pdf | R | 复用（见 §2） |
| `R/S4-PAP-02` | S4 | On the Criteria To Be Used in Decomposing Systems into Modules（Parnas 1972 原文） | D. L. Parnas, Carnegie-Mellon Univ.; CACM 15(12):1053-1058 | 1972 | True | https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf | R | 复用（见 §2） |
| `R/S4-PAP-01` | S4 | No Silver Bullet—Essence and Accident in Software Engineering（Brooks 1987 原文） | Frederick P. Brooks, Jr.; IEEE Computer 20(4):10-19 | 1987 | True | https://worrydream.com/refs/Brooks_1986_-_No_Silver_Bullet.pdf | R | 复用（见 §2） |
| `R/S2-BK-16` | S2 | Pattern-Oriented Software Architecture, Volume 1: A System of Patterns（POSA Vol.1） | Buschmann, Meunier, Rohnert, Sommerlad, Stal (John Wiley & Sons) | 1996 | True | https://www.wiley.com/en-us/Pattern-Oriented+Software+Architecture%2C+Volume+1%3A+A+System+of+Patterns-p-9780471958697 | R | 复用（沿用全局 ID，见 §2） |
| `R/S1-OFF-01` | S1 | SWEBOK Guide V4.0（Guide to the Software Engineering Body of Knowledge） | IEEE Computer Society（ISO/IEC TR 19759） | 2024 | True | https://web.archive.org/web/2024/https://www.computer.org/education/bodies-of-knowledge/software-engineering | R | 复用（沿用全局 ID，见 §2） |
| `R/R-XC-01` | S4 | Laws of Software Evolution Revisited（Lehman 本人对八条定律的完整复述） | M. M. Lehman; Software Process Technology (EWSPT'96), LNCS 1149:108-124, Springer | 1996 | True | https://www.cs.kent.edu/~jmaletic/cs63902/Papers/Lehman96.pdf | R | 新增 |
| `R/R-XC-02` | S2 | Lehman's laws of software evolution（百科条目，交叉验证定律条数与 S/P/E 分类） | Wikipedia | accessed 2026-09-10 | True | https://en.wikipedia.org/wiki/Lehman%27s_laws_of_software_evolution | R | 新增 |
| `R/R-XC-03` | S1 | An Overview of the SWEBOK Guide（SEBoK 百科，逐条列出 V4 的 18 KA） | SEBoK (Guide to the Systems Engineering Body of Knowledge) | accessed 2026-09-10 | True | https://sebokwiki.org/wiki/An_Overview_of_the_SWEBOK_Guide | R | 新增 |
| `R/R-XC-04` | S2 | Pattern-Oriented Software Architecture Volume 1 — 官方配套站点（模式目录 + Microkernel 定义） | software-pattern.org（POSA 官方配套站点） | accessed 2026-09-10 | True | http://software-pattern.org/Book/30 | R | 新增 |
| `R/R-XC-05` | S2 | Waterfall model（百科条目，交叉验证 Royce 五步与迭代原意） | Wikipedia | accessed 2026-09-10 | True | https://en.wikipedia.org/wiki/Waterfall_model | R | 新增 |
| `R/R-XC-06` | S2 | No Silver Bullet（百科条目，交叉验证核心论断与本质/偶然复杂度） | Wikipedia | accessed 2026-09-10 | True | https://en.wikipedia.org/wiki/No_Silver_Bullet | R | 新增 |
| `R/R-XC-07` | S2 | Software Engineering Body of Knowledge（百科条目，交叉验证 SWEBOK V4 发布与 18 KA） | Wikipedia | accessed 2026-09-10 | True | https://en.wikipedia.org/wiki/Software_Engineering_Body_of_Knowledge | R | 新增 |

## 5. 碰撞与无法映射（如实标注）

1. **同形 ID 跨包碰撞**（最常见问题）：`S1-01`、`S2-01`、`S3-01`、`S4-01` 等裸数字 ID 在 G/H/J/K/L/N 中各自代表完全不同的信源。例：`K/S2-01`=Google SRE Book，而 `J/S2-01`=Twelve-Factor App，`N/S2-01`=Conway 原文。**不得跨包引用裸 ID。**
2. **`Q/S3-VEN-02..08` 与 `I/S3-VEN-02..04` 名义碰撞**：两包均沿用全局式 `S3-VEN-*` 命名但指向不同信源。例：`I/S3-VEN-02`=Google Testing Blog（测试金字塔/端到端测试），而 `Q/S3-VEN-02`=AWS Well-Architected Framework 支柱页。**同名不同源，引用须带包名。**
3. **`I/S2-BK-30` 名义碰撞**：I 包用全局式编号，但 `S2-BK-30` 在该包指 Mike Cohn《Succeeding with Agile》（测试金字塔原始模型），而阶段1 全局 `S2-BK-30` 为《Team Topologies》。此条为 **同名不同源**，无法映射为同一 ID，须以标题消歧。
4. **机构同、文档不同**（非同一实体，不合并）：如 `G/S1-11`（SEI ATAM TR-2000）与阶段1 `S1-OFF-02` 同属 SEI，但为不同文档；`I/S2-BK-30` 与阶段1 无对应源；`P/P-S1-01`（SEI 资产页摘要）与 `P/P-S4-01`（论文本体）同论文不同载体。
5. **阶段2 尚未回源/低置信条目**：`F/S1-03`（12207:2026 scope 未核验，verified=false）、`F/S1-F08`（SWEBOK V3 镜像损坏，verified=false）、`F/S4-F02`（Meyer 论文 verified=false）、`H/S2-10` 引用 Wikipedia 综合、`M/S1-M01`（25010 正文经 OBP，verified=false）、`M/S4-M02`（凭 S4-M01 转引，verified=false）、`I/S2-BK-30`（verified=false）、`R/S4-PAP-03`（Lehman 1980 全文 IEEE 付费，abstract-only，verified=false）——均按证据包原样标注，未升级为 verified。
6. **未能映射进阶段1 的类别**：阶段2 新技术债/演进类来源（`H/S4-03` Fragile Base Class、`L/S4-03` Kruchten 技术债理论、`N/S4-01/02` Mirroring Hypothesis）、P 包净新增技术债来源（`P-S2-02` 象限、`P-S2-04/05` 机会式重构/设计耐力、`P-S3-01/02/03` SonarQube/SQALE、`P-S4-02..12` 技术债实证与度量）、Q 包全部 7 条（AWS/GCP WAF、Thoughtworks Radar）、R 包交叉验证条目（`R-XC-01..07`）在阶段1 无对应全局 ID，属**净新增**。

---

*本表由阶段2 主Agent 聚合生成，仅整合证据包既有信源，未新增未经核验来源；数字与 `knowledge-map.json`、`F..R-*.json` 实际计数一致（阶段2 12 包 / 208 条计数；P=27、Q=7、R=14）。*
