# 软件工程 / 架构设计 经典著作候选书单 + 可得性核实

> 阶段1 · 01-books · 生成日期 2026-09-10 · 生成角色：技术文献选品研究员
> 配套结构文件：`D-book-candidates.json`（供主Agent 汇总、用户定稿；阶段2/3 再落地获取）
> 信源分级：本清单书目均为 **S2（经典著作）**；免费官方源可作公开层链接引用。

## ⛔ 版权红线（刚性，先读）

- **书籍本体不进公开仓库**，仅入**本地语料层**；公开库只承载「纳入、消化、重组后的知识与方法论」+ 我们自己的脚本。
- 本清单**不下载、不写入任何书籍全文**。`free-official` 项也只引用官方在线地址，不镜像正文。
- `paid` / `user-copy` 项：获取全文须由用户提供合法本地副本或购买；阶段2 抓取仅限可公开引用的目录/章节/官方摘要。

## 可得性标注说明

| 标注 | 含义 |
|---|---|
| `free-official` | 官方免费合法在线阅读/下载（附 URL） |
| `paid` | 需购买（附官方购买渠道） |
| `user-copy` | 需用户提供本地副本 |
| `unknown` | 待核 |

> 实测说明（2026-09-10）：`abseil.io`、`12factor.net`、`domainlanguage.com`、`enterpriseintegrationpatterns.com`、`aosabook.org` 直连 HTTP 200；`sre.google` 为 Google 域，直连超时，经代理 `172.29.0.1:7890` 实测 200。

---

## 一、软件工程通论

| 书名（中 / 英） | 作者 | 版本 / 年份 | 权威性（为何） | 可得性 | 优先级 |
|---|---|---|---|---|---|
| Google 软件工程 / *Software Engineering at Google* | Winters, Manshreck, Wright (Google) | 1st / 2020 | Google 大规模工程实践一手总结；时间/规模/权衡三主题 | `free-official` · https://abseil.io/resources/swe-book | 必入 |
| 人月神话 / *The Mythical Man-Month* | Frederick P. Brooks Jr. | Anniversary Ed. / 1995 | SE 史上最具影响力随笔集；人月不可互换、概念完整性 | `paid` · Pearson | 必入 |
| 没有银弹 / *No Silver Bullet* | Frederick P. Brooks Jr. | 1986（收于《人月神话》周年版第16章） | 本质复杂度 vs 偶然复杂度的奠基论文 | `paid` · 同上（随书） | 建议 |
| 代码大全（第2版）/ *Code Complete* | Steve McConnell | 2nd / 2004 | 软件构建领域最系统的实证手册 | `paid` · Microsoft Press | 建议 |
| 软件工程（原书第10版）/ *Software Engineering* | Ian Sommerville | 10th / 2015 | 全球最广本科教材，与 SWEBOK 互证 | `paid` · Pearson | 可选 |
| 程序员修炼之道（20周年版）/ *The Pragmatic Programmer* | Thomas, Hunt | 20th Anniv. / 2019 | DRY/正交性/契约式设计等经典工程原则 | `paid` · Pragmatic Bookshelf | 建议 |
| 人件（第3版）/ *Peopleware* | DeMarco, Lister | 3rd / 2013 | 软件工程中「人」维度奠基文本 | `paid` · Pearson | 可选 |

## 二、架构设计

| 书名（中 / 英） | 作者 | 版本 / 年份 | 权威性（为何） | 可得性 | 优先级 |
|---|---|---|---|---|---|
| 架构整洁之道 / *Clean Architecture* | Robert C. Martin | 1st / 2017 | 依赖规则/稳定依赖/稳定抽象，整洁架构体系代表 | `paid` · Pearson | 必入 |
| 软件设计哲学（第2版）/ *A Philosophy of Software Design* | John Ousterhout | 2nd / 2021 | 降低复杂度；深层模块/信息隐藏/设计两次 | `paid` · 作者官网 | 必入 |
| 软件架构实践（第4版）/ *Software Architecture in Practice* | Bass, Clements, Kazman | 4th / 2021 | SEI 出品；质量属性/战术/ATAM/文档化权威教科书 | `paid` · Pearson | 必入 |
| 软件架构基础（第2版）/ *Fundamentals of Software Architecture* | Richards, Ford | 2nd / 2025-03 | 架构特征/组件/风格/决策；含架构师定律 | `paid` · O'Reilly | 必入 |
| 构建演进式架构（第2版）/ *Building Evolutionary Architectures* | Ford, Parsons, Kua, Sadalage | 2nd / 2022 | fitness function 与自动化演进治理 | `paid` · O'Reilly | 建议 |
| 企业应用架构模式 / *Patterns of Enterprise Application Architecture* | Martin Fowler | 1st / 2002 | Repository/UoW/Data Mapper 等模式词源 | `paid` · martinfowler.com | 必入 |
| 软件架构文档化（第2版）/ *Documenting Software Architectures* | Clements, Bachmann, Bass, et al. | 2nd / 2010 | SEI「Views and Beyond」文档化标准 | `paid` · Pearson | 建议 |
| 软件架构：难点与权衡 / *Software Architecture: The Hard Parts* | Ford, Richards, Sadalage, Dehghani | 1st / 2021 | 分布式架构取舍决策结构化方法 | `paid` · O'Reilly | 可选 |
| 软件架构师电梯 / *The Software Architect Elevator* | Gregor Hohpe | 1st / 2020 | 架构师组织/战略角色与沟通视角 | `paid` · O'Reilly | 可选 |

## 三、领域驱动设计（DDD）

| 书名（中 / 英） | 作者 | 版本 / 年份 | 权威性（为何） | 可得性 | 优先级 |
|---|---|---|---|---|---|
| 领域驱动设计 / *Domain-Driven Design* | Eric Evans | 1st / 2003 | DDD 奠基；ubiquitous language/bounded context/aggregate | `paid` · Pearson | 必入 |
| 领域驱动设计参考 / *DDD Reference* | Eric Evans | PDF / 2014 | 作者官方免费术语/模式速查 | `free-official` · https://domainlanguage.com/ddd/reference/ | 必入 |
| 实现领域驱动设计 / *Implementing Domain-Driven Design* | Vaughn Vernon | 1st / 2013 | DDD 工程落地权威续作 | `paid` · Pearson | 建议 |

## 四、代码整洁 / 重构 / 遗留系统

| 书名（中 / 英） | 作者 | 版本 / 年份 | 权威性（为何） | 可得性 | 优先级 |
|---|---|---|---|---|---|
| 代码整洁之道 / *Clean Code* | Robert C. Martin | 1st / 2008 | 可读性实践行业标杆（有争议但影响力极高） | `paid` · Pearson | 必入 |
| 重构（第2版）/ *Refactoring* | Martin Fowler | 2nd / 2018 | 重构手法权威目录；重构术语事实标准 | `paid` · Pearson | 必入 |
| 修改遗留代码的有效方法 / *Working Effectively with Legacy Code* | Michael Feathers | 1st / 2004 | 接缝/依赖打破/特征测试权威手册 | `paid` · Pearson | 必入 |

## 五、数据密集型 / 分布式

| 书名（中 / 英） | 作者 | 版本 / 年份 | 权威性（为何） | 可得性 | 优先级 |
|---|---|---|---|---|---|
| 数据密集型应用系统设计（第2版）/ *Designing Data-Intensive Applications* | Kleppmann, Riccomini | 2nd / 2026-02 | 分布式数据系统事实标准；新增 AI/云原生 | `paid` · O'Reilly | 必入 |
| 发布！（第2版）/ *Release It!* | Michael T. Nygard | 2nd / 2018 | 稳定性反模式/断路器/舱壁的生产就绪经典 | `paid` · Pragmatic Bookshelf | 建议 |

## 六、运维 / 可靠性 / 交付

| 书名（中 / 英） | 作者 | 版本 / 年份 | 权威性（为何） | 可得性 | 优先级 |
|---|---|---|---|---|---|
| Google SRE 运维解密 / *Site Reliability Engineering* | Beyer, Jones, Petoff, Murphy (Google) | 1st / 2016 | SRE 学科奠基；SLI/SLO/错误预算 | `free-official` · https://sre.google/sre-book/table-of-contents/ | 必入 |
| SRE 工作手册 / *The Site Reliability Workbook* | Beyer, Murphy, Rensin, et al. (Google) | 1st / 2018 | SRE 落地模板；官方免费 | `free-official` · https://sre.google/workbook/table-of-contents/ | 建议 |
| DevOps 实践指南（第2版）/ *The DevOps Handbook* | Kim, Humble, Debois, Willis, Forsgren | 2nd / 2021 | DevOps 三路径实践总纲 | `paid` · IT Revolution | 必入 |
| 持续交付 / *Continuous Delivery* | Humble, Farley | 1st / 2010 | CD/部署流水线奠基著作 | `paid` · Pearson | 建议 |
| 加速 / *Accelerate* | Forsgren, Humble, Kim | 1st / 2018 | DORA 实证研究；工程效能权威来源 | `paid` · IT Revolution | 必入 |
| 团队拓扑 / *Team Topologies* | Skelton, Pais | 1st / 2019 | 团队类型/交互模式；康威定律操作化 | `paid` · IT Revolution | 建议 |
| 十二要素应用 / *The Twelve-Factor App* | Adam Wiggins (Heroku) | Web / 2011 | 云原生应用架构奠基方法论；官方免费 | `free-official` · https://12factor.net/ | 必入 |

## 七、设计模式 / 企业架构

| 书名（中 / 英） | 作者 | 版本 / 年份 | 权威性（为何） | 可得性 | 优先级 |
|---|---|---|---|---|---|
| 设计模式 / *Design Patterns*（GoF） | Gamma, Helm, Johnson, Vlissides | 1st / 1994 | 23 个模式开山之作，OOP 共享词汇奠基 | `paid` · Pearson | 必入 |
| 企业集成模式 / *Enterprise Integration Patterns* | Hohpe, Woolf | 1st / 2003 | 消息/集成 65 模式词源；官网免费概览 | `paid` · 官网（站点含免费模式说明） | 建议 |

## 八、微服务（补充域）

| 书名（中 / 英） | 作者 | 版本 / 年份 | 权威性（为何） | 可得性 | 优先级 |
|---|---|---|---|---|---|
| 构建微服务（第2版）/ *Building Microservices* | Sam Newman | 2nd / 2021 | 微服务权威导论 | `paid` · O'Reilly | 可选 |
| 微服务模式 / *Microservices Patterns* | Chris Richardson | 1st / 2018 | 微服务模式语言，工程落地强 | `paid` · Manning | 可选 |

---

## 统计与优先建议

- 候选合计 **35 本**（含 DDD Reference 免费版与 SRE Workbook），覆盖任务要求的全部谱系。
- **必入（18）**：SE at Google、人月神话、Clean Architecture、A Philosophy of Software Design、Software Architecture in Practice、Fundamentals of Software Architecture、PoEAA、DDD（Evans）、DDD Reference、Clean Code、Refactoring 2e、WELC、DDIA 2e、SRE Book、DevOps Handbook 2e、Accelerate、12factor、Design Patterns（GoF）——按主题均衡。
- **建议（11）**：No Silver Bullet、Code Complete、Pragmatic Programmer、Building Evolutionary Architectures、Documenting Software Architectures、Implementing DDD、Release It!、SRE Workbook、Continuous Delivery、Team Topologies、EIP。
- **可选（6）**：Sommerville、Peopleware、Software Architecture: The Hard Parts、The Software Architect Elevator、Building Microservices、Microservices Patterns。
- **免费官方直取（free-official）优先入库**：12factor、SRE Book、SRE Workbook、SE at Google、DDD Reference——可作公开层可引用链接。
- `paid`/`user-copy` 书目：阶段2 仅提取目录/公开章节/官方摘要用于知识结构，不落全书；实体全文待用户提供本地副本。

## 版本时效勘误记录（主动核实，2026-09-10）

| 书 | 常见误记 | 核实值 | 依据 |
|---|---|---|---|
| Designing Data-Intensive Applications | 第1版 2017（视为最新） | **第2版 2026-02**（+Chris Riccomini 合著） | O'Reilly 版权页 / Kleppmann 访谈（一手） |
| Fundamentals of Software Architecture | 第1版 2020 | **第2版 2025-03** | 作者 Mark Richards 官方视频 + O'Reilly ISBN 978-1-098-17551-1 |
| The DevOps Handbook | 第1版 2016 | **第2版 2021-11** | IT Revolution 官方产品页 |
| Software Architecture in Practice | 「第5版」传闻 | **最新为第4版 2021** | Pearson/Google Books 版本列表 |

## 未决问题（gaps）

- 部分 Pearson/O'Reilly 官方页可能存在区域访问限制，购买链接以各出版社官网为准；阶段2 落地时需复核链接可用性。
- 「No Silver Bullet」独立免费官方版本：未确认存在出版社授权的独立免费 PDF，暂按随《人月神话》周年版获取。
- Sommerville《Software Engineering》是否已有第11版未获权威确认，暂记第10版。
