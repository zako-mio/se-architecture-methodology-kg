# 缺口清单：paid / user-copy 书籍（来源与渠道的历史登记）

> 母任务：0910-软件工程架构方法论 · 阶段2
> 依据：`01-books/D-book-candidates.json`（35 本候选中的 **30 本**为 paid/user-copy，5 本 free-official 已于本轮直取，见 `fetch-log.md`）
> 生成日期：2026-09-10 ｜ 最近更新：2026-09-11（口径修订 + 采集完成回填指针）
> 用途：阶段2 以**目录 / 公开章节 / 官方摘要**支撑知识结构；书籍本体统一归**私有本地语料层**。
> 版权纪律：书本体**只入私有本地语料层 `01-books/_files/`**（含结构层快照），**永不进公开仓库**；公开仓只承载消化重组后的知识与自研脚本（`00-plan/contract.md §5`）。
> **当前状态（2026-09-11）**：30 本已全部采集落盘，逐文件状态见私有采集清单 `01-books/download-log.md` 与 `01-books/acquired-manifest.json`（两者均在私有语料层，不进公开仓）。**本文件自此转为「来源与渠道的历史登记」，不再作为待办清单。**

## 0. 历史使用说明（已履行）

1. 原流程：按 **P0 → P1 → P2** 优先级挑选书目，由用户提供合法本地副本或访问途径。
2. 已执行结果（2026-09-11）：30 本全部取得可用副本并落私有语料层；**每本的来源、版次与许可状态已在私有清单中逐文件登记**（`license` 字段），公开仓不承载该清单。
3. 解析管线：有文本层走 `pdf-worker`、扫描件走 `pdf-ocr` 解析 → 摘要落 `02-research/`；原文只入私有语料层。
4. 公开层覆盖：各书的**公开目录/作者博客/官方摘要**仍可作为「结构+链接」先行覆盖（下表「免费线索」列）。
5. 若日后购买官方电子版，可用合法副本替换私有层内同目录内容，并在私有清单中更新 `license`。

> **提示**：阶段2 知识结构所需的最小集是 **P0（14 本）**，已全部到位。

---

## 1. P0 · 必入（14 本）——已全部采集

| # | 书名 | 作者 | 版次/年 | 官方渠道 | 免费线索（可先覆盖结构） |
|:--:|---|---|---|---|---|
| 1 | 人月神话 The Mythical Man-Month | Frederick P. Brooks Jr. | 2nd/1995 | Pearson | 作者随笔/多方书评（仅线索） |
| 2 | 架构整洁之道 Clean Architecture | Robert C. Martin | 1st/2017 | Pearson | 作者博客 UncleBob（依赖规则等概念） |
| 3 | 软件设计哲学 A Philosophy of Software Design | John Ousterhout | 2nd/2021 | Stanford 作者页 | 作者官网 + 课程 slides（公开） |
| 4 | 软件架构实践 Software Architecture in Practice | Bass, Clements, Kazman | 4th/2021 | Pearson | SEI 官网（质量属性/ATAM 公开资料） |
| 5 | 软件架构基础 Fundamentals of Software Architecture | Richards, Ford | 2nd/2025 | O'Reilly | 作者博客/InfoQ 访谈 |
| 6 | 企业应用架构模式 PoEAA | Martin Fowler | 1st/2002 | martinfowler.com | 作者官网模式目录（公开） |
| 7 | 领域驱动设计 DDD | Eric Evans | 1st/2003 | Pearson | **DDD Reference（已直取 FO-04）** |
| 8 | 代码整洁之道 Clean Code | Robert C. Martin | 1st/2008 | Pearson | 作者博客 |
| 9 | 重构（第2版）Refactoring 2e | Martin Fowler | 2nd/2018 | Pearson | **martinfowler.com/refactoring 目录（公开）** |
| 10 | 修改遗留代码 Working Effectively with Legacy Code | Michael Feathers | 1st/2004 | Pearson | 作者博客/访谈 |
| 11 | 数据密集型应用系统设计 DDIA（第2版） | Kleppmann, Riccomini | 2nd/2026 | O'Reilly | 作者博客/官网章节（公开） |
| 12 | DevOps 实践指南（第2版） | Kim, Humble, Debois, Willis, Forsgren | 2nd/2021 | IT Revolution | 三大路径公开文章 |
| 13 | 加速 Accelerate | Forsgren, Humble, Kim | 1st/2018 | IT Revolution | **DORA 官方报告（公开）** |
| 14 | 设计模式 GoF | Gamma, Helm, Johnson, Vlissides | 1st/1994 | Pearson | 无官方全文；模式名称广为公开 |

## 2. P1 · 建议（10 本）——已全部采集

| # | 书名 | 作者 | 版次/年 | 官方渠道 | 免费线索 |
|:--:|---|---|---|---|---|
| 15 | 没有银弹 No Silver Bullet | Frederick P. Brooks Jr. | 1986 | 收录于《人月神话》周年版 | 论文常被二手引用（仅线索） |
| 16 | 代码大全（第2版）Code Complete 2e | Steve McConnell | 2nd/2004 | Microsoft Press | 作者博客/Construx |
| 17 | 程序员修炼之道（20周年）The Pragmatic Programmer | Thomas, Hunt | 2nd/2019 | Pragmatic Bookshelf | pragprog 公开摘录 |
| 18 | 构建演进式架构（第2版） | Ford, Parsons, Kua, Sadalage | 2nd/2022 | O'Reilly | **作者 fitness function 公开文章** |
| 19 | 软件架构文档化（第2版）Views and Beyond | Clements, Bachmann, Bass, et al. | 2nd/2010 | Pearson | SEI 文档化公开资料 |
| 20 | 实现领域驱动设计 Implementing DDD | Vaughn Vernon | 1st/2013 | Pearson | 作者博客/DDD 社区 |
| 21 | 发布！Release It!（第2版） | Michael T. Nygard | 2nd/2018 | Pragmatic | 作者博客（稳定性反模式） |
| 22 | 持续交付 Continuous Delivery | Humble, Farley | 1st/2010 | Pearson | **continuousdelivery.com（公开）** |
| 23 | 团队拓扑 Team Topologies | Skelton, Pais | 1st/2019 | IT Revolution | **teamtopologies.com（公开）** |
| 24 | 企业集成模式 Enterprise Integration Patterns | Hohpe, Woolf | 1st/2003 | enterpriseintegrationpatterns.com | **官网模式目录（公开）** |

## 3. P2 · 可选（6 本）——已全部采集

| # | 书名 | 作者 | 版次/年 | 官方渠道 |
|:--:|---|---|---|---|
| 25 | 软件工程（原书第10版）Software Engineering | Ian Sommerville | 10th/2015 | Pearson |
| 26 | 人件（第3版）Peopleware | DeMarco, Lister | 3rd/2013 | Pearson |
| 27 | 软件架构：难点与权衡 The Hard Parts | Ford, Richards, Sadalage, Dehghani | 1st/2021 | O'Reilly |
| 28 | 软件架构师电梯 The Software Architect Elevator | Gregor Hohpe | 1st/2020 | O'Reilly |
| 29 | 构建微服务（第2版）Building Microservices 2e | Sam Newman | 2nd/2021 | O'Reilly |
| 30 | 微服务模式 Microservices Patterns | Chris Richardson | 1st/2018 | Manning |

---

## 4. 统计

| 类别 | 数量 | 说明 |
|:--:|:--:|---|
| free-official（已直取） | 5 | abseil SWE Book / SRE Book / SRE Workbook / DDD Reference / 12-Factor |
| paid/user-copy（本清单，已全部采集） | 30 | P0=14 / P1=10 / P2=6；逐文件状态见私有语料层清单 |
| 候选总数 | 35 | 与 `D-book-candidates.json` 一致 |

## 5. 说明与边界

- **最小可行集**：P0 的 14 本覆盖 SE 通论、架构、DDD、整洁/重构、数据密集型、DevOps/交付、设计模式七个核心域的权威文本；缺失会显著削弱 S1/S2 层证据密度。**当前 30 本已全部到位**。
- **可先行的公开层**：多数书有作者官网/官方博客/官方模式目录可作为 S2 公开线索（上表"免费线索"列）；但**书本体概念原句**的一手核验以私有语料层为准，公开仓不承载原句。
- **解析管线**：`pdf-worker`（有文本层）/ `pdf-ocr`（扫描件）；原文仅入私有本地语料层，不进公开仓库。
- **三层隔离**（可机检）：本地仓 `.gitignore` + 公开仓 `_publish/.gitignore` + 装配层 `audit_publish.py` 的 `HARD_EXCLUDE_PREFIXES`；复核命令见 `00-plan/contract.md §5`。
- **不阻塞**：本缺口与阶段2 联网主线并行，不阻塞 Wave A/B 的证据包产出。

> 本清单的采集诉求已于 2026-09-11 履行完毕；后续如需核对某本的实际来源、版次与许可，请查私有采集清单（`01-books/download-log.md` / `01-books/acquired-manifest.json`）。
