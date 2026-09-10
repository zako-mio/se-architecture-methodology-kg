# free-official 书籍直取日志（阶段2 · 采集）

> 母任务：0910-软件工程架构方法论
> 执行角色：语料采集员（自写角色）
> 访问日期：**2026-09-10**（所有源同一批次核实）
> 版权纪律：**只提取公开在线的目录/章节结构与核心论点摘要；不下载、不落盘任何书籍/PDF 全文**。书籍本体仅可入本地语料层，公开仓库只承载消化重组后的知识（`00-plan/contract.md §5`）。

## 0. 汇总

| # | ID | 书 | 可达 | 渠道 | HTTP | 结构规模 |
|:--:|:--:|---|:--:|---|:--:|---|
| 1 | FO-01 | Software Engineering at Google | ✅ | 直连 | 200 | 5 部分 / 26 章 |
| 2 | FO-02 | Google SRE Book | ✅ | 代理 172.29.0.1:7890 | 200 | 5 部分 + 前后附件 / 43 条目（34 章） |
| 3 | FO-03 | SRE Workbook | ✅ | 代理 172.29.0.1:7890 | 200 | 3 部分 + 前后附件 / 31 条目（21 章） |
| 4 | FO-04 | DDD Reference (Evans) | ✅ | 直连 | 200 | 3 组 / 6 条目（详细模式索引在 CC 授权 PDF） |
| 5 | FO-05 | The Twelve-Factor App | ✅ | 直连 | 200 | 12 要素 |

结构化结果见 `free-official-extracts.json`（schema：`{sources:[{id,title,url,reachable,channel,http_status,toc:[],summary,gaps}]}`）。

---

## 1. Software Engineering at Google（FO-01）

- **URL**：https://abseil.io/resources/swe-book （落地页 200）→ 正文目录 https://abseil.io/resources/swe-book/html/toc.html
- **可达性**：可达。直连 HTTP 200；目录页字节数 11,039（落地页）。
- **渠道**：直连（国内可达）。
- **许可**：在线全文 CC BY-NC-ND 4.0（官方免费，禁商业、禁演绎）。
- **目录结构**：
  - **Part I. Thesis**：Ch1 What Is Software Engineering?
  - **Part II. Culture**：Ch2 How to Work Well on Teams / Ch3 Knowledge Sharing / Ch4 Engineering for Equity / Ch5 How to Lead a Team / Ch6 Leading at Scale / Ch7 Measuring Engineering Productivity
  - **Part III. Processes**：Ch8 Style Guides and Rules / Ch9 Code Review / Ch10 Documentation / Ch11 Testing Overview / Ch12 Unit Testing / Ch13 Test Doubles / Ch14 Larger Testing / Ch15 Deprecation
  - **Part IV. Tools**：【已按版权红线移出（原引用 337 字）· 出处见 source_id/URL】：Ch26 Afterword
- **核心论点摘要（约 470 字）**：核心命题——「编程是写代码，软件工程是编程在时间与规模上的整合」，核心变量为**时间与变化、规模、权衡**。时间维度提出 **Hyrum 定律**（接口有足够用户后，系统行为会被依赖，即使未承诺）；规模维度强调「可规模化的政策」与单版本/单体仓库（monorepo）、Live at Head；权衡维度主张显式记录决策并允许重访。文化上强调团队协作、心理安全、知识共享、无责复盘。流程上以**左移（shifting left）**与自动化（代码评审、静态分析、测试）降低缺陷成本。测试部分区分测试大小/范围，主张「测试公开 API、测状态不测交互、DAMP 优于 DRY、Beyoncé 规则」。工具链覆盖版本控制与分支管理、代码搜索、构建系统（任务式 vs 制品式）、依赖管理（SemVer 局限、Live at Head、最小版本选择）、大规模变更（LSC）与 CI/CD。弃用（Deprecation）区分建议型/强制型。
- **缺口**：仅结构+摘要；未镜像正文。引用受 NC-ND 约束，公开库仅可外链+自撰摘要。

---

## 2. Google SRE Book（FO-02）

- **URL**：https://sre.google/sre-book/table-of-contents/
- **可达性**：可达（经代理）。**境内直连失败**——连接层失败，`curl` 返回 `http_code=000`（域为 Google，境内超时）；经 `curl -x http://172.29.0.1:7890 -A "<browser UA>"` 得 **HTTP 200**，字节数 21,203。
- **渠道**：代理 `172.29.0.1:7890`（HTTP/SOCKS5 混合端口）。
- **许可**：CC BY-NC-ND 4.0。
- **目录结构**（5 部分 / 34 章 + 前后附件）：
  - **Front**：Foreword / Preface
  - **Part I - Introduction**：1 Introduction / 2 The Production Environment at Google, from the Viewpoint of an SRE
  - **Part II - Principles**：【已按版权红线移出（原引用 211 字）· 出处见 source_id/URL】：【已按版权红线移出（原引用 594 字）· 出处见 source_id/URL】：【已按版权红线移出（原引用 242 字）· 出处见 source_id/URL】：33 Lessons Learned from Other Industries / 34 Conclusion
  - **Back**：Appendix A–F / Bibliography
- **核心论点摘要（约 420 字）**：SRE 学科奠基作，把运维当作软件工程问题，用工程手段替代人工操作。四大支柱：①**服务等级目标 SLO**——以 SLI（指标）→ SLO（目标）→ SLA（对外承诺）分层量化可靠性；②**错误预算（error budget）**——1 减去 SLO 即可允许的不可靠额度，作为发布/冻结的量化闸门；③**消除琐事 toil**——将重复、可自动化、无长期价值的运维工作控制在 50% 以内；④**无责复盘（blameless postmortem）**——从失败学习而非追责。实践层面覆盖告警、on-call、有效排障、应急响应与事件管理、故障跟踪、可靠性测试、负载均衡（前端/数据中心）、过载与**级联故障防护**、分布式共识、周期调度、数据处理管道与数据完整性。管理层面讨论 on-call 上手、打断处理、运维过载、沟通协作与参与模型演进。核心理念：**拥抱风险**（可靠性有成本，不必追求 100%）与**简洁性**（复杂度是可靠性的敌人）。
- **缺口**：仅结构+摘要；未镜像正文；采集依赖代理（境内直连不可用）。

---

## 3. SRE Workbook（FO-03）

- **URL**：https://sre.google/workbook/table-of-contents/
- **可达性**：可达（经代理）。同 FO-02：境内直连失败（`http_code=000`），经代理 **HTTP 200**，字节数 15,448。
- **渠道**：代理 `172.29.0.1:7890`。
- **许可**：CC BY-NC-ND 4.0。
- **目录结构**（3 部分 / 21 章 + 前后附件）：
  - **Front**：Foreword I / Foreword II / Preface / 1 How SRE Relates to DevOps
  - **Part I - Foundations**：2 Implementing SLOs / 3 SLO Engineering Case Studies / 4 Monitoring / 5 Alerting on SLOs / 6 Eliminating Toil / 7 Simplicity
  - **Part II - Practices**：【已按版权红线移出（原引用 282 字）· 出处见 source_id/URL】：【已按版权红线移出（原引用 202 字）· 出处见 source_id/URL】：Appendix A Example SLO Document / Appendix B Example Error Budget Policy / Appendix C Results of Postmortem Analysis / Index / About the Editors / Colophon
- **核心论点摘要（约 365 字）**：SRE Book 的**落地操作手册**，把原则转化为可执行模板与流程。相较母书更偏工程细节：①**SLO 落地**——给出用 SLO 定义、误差预算政策（error budget policy）从制定到运作的完整方法与行业案例；②**基于 SLO 的告警**——提出多窗口多燃烧率（multi-window multi-burn-rate）告警，兼顾长短期误差率、降低误报；③**监控与负载管理**；④**消除 toil** 与**简洁性**的可操作实践；⑤**on-call / 事件响应 / 无责复盘**的组织与流程；⑥**NALSD（非抽象大系统设计）**——用容量估算与设计推演做系统设计；⑦**配置设计与配置细节**——配置即代码、避免配置漂移；⑧**金丝雀发布（canarying）**；⑨组织变革与 SRE 团队生命周期。附录给出 SLO 文档与错误预算政策模板，可直接复用。
- **缺口**：仅结构+摘要；未镜像正文；依赖代理。

---

## 4. DDD Reference (Evans)（FO-04）

- **URL**：https://domainlanguage.com/ddd/reference/ （301 → https://www.domainlanguage.com/ddd/reference/，最终 200）
- **可达性**：可达。直连；HTTP 301→200；页面字节数 48,064。
- **渠道**：直连。
- **许可**：Reference 文档 **CC BY 4.0**；原书摘要 **CC BY 3.0**（作者 2006 年置入 Creative Commons，鼓励衍生）。
- **目录结构**：
  - **文档定位**：DDD 模式与定义速查，是 Evans 2004 原著所有定义/模式的摘要，另含 3 个未入书的补充模式。
  - **摘要来源**：抽取自 2004 年《Domain-Driven Design》原著文本，编辑精简但未改写。
  - **覆盖范围（按 DDD 标准模式组织，待与 PDF 逐条核验）**：
    1. 通用语言与模型驱动设计（Ubiquitous Language / Model-Driven Design / Hands-on Modelers / Refactoring Toward Deeper Insight）
    2. 构建块（Entities / Value Objects / Services / Modules / Aggregates / Factories / Repositories / Domain Events 等）
    3. 柔性设计（Supple Design：Intention-Revealing Interfaces / Side-Effect-Free Functions / Assertions / Conceptual Contours / Standalone Classes / Closure of Operations）
    4. 战略设计（Bounded Context / Context Map / Core Domain / 上下文映射模式 / Distillation）
- **核心论点摘要（约 400 字）**：Evans 官方免费精炼参考，定位为「DDD 模式速查与术语索引」，不含完整教学，而是对 2004 年原著全部定义与模式做摘要，并补入 3 个当年未入书的模式。核心价值在于**权威词源**：为通用语言（Ubiquitous Language）、模型驱动设计、构建块（实体/值对象/服务/模块/聚合/工厂/仓储）、柔性设计与战略设计（限界上下文/上下文映射/核心域）提供可交叉验证的官方定义。原文说明这些摘要抽取自原著并自 2006 年起置于 Creative Commons，可作为衍生作品基础。**注意**：逐条模式定义位于官方 PDF（`DDD_Reference_2015-03.pdf`），本次遵守「不下载/不落盘 PDF 全文」的红线**未下载**；因该 PDF 为 CC 授权，如后续需要可安全提取其结构。
- **缺口**：
  1. 详细模式条目（每条定义原文）在官方 PDF 内，本轮未提取——**待补**（可安全补，因 CC 授权）；
  2. 目录中的「覆盖范围」为按标准模式组织，尚未与 PDF 逐条核对，条目标题置信 **medium**。

---

## 5. The Twelve-Factor App（FO-05）

- **URL**：https://12factor.net/
- **可达性**：可达。直连 HTTP 200；页面字节数 10,596。官方另提供 ePub：`/12factor.epub`。
- **渠道**：直连。
- **许可**：官方免费在线（含 ePub 下载）。本地已有 `12factor.epub`（BK-01）可交叉核验。
- **目录结构**（Introduction + 12 要素）：【已按版权红线移出（原引用 287 字）· 出处见 source_id/URL】核心论点摘要（约 565 字）**：云原生/SaaS 时代应用架构的奠基方法论。作者基于 Heroku 平台成百上千应用的开发与运维经验，总结出面向「以服务形式交付（web app / SaaS）」的 12 条规范。目标：以声明式格式自动化环境搭建；与操作系统保持干净契约以获得可移植性；适配现代云平台部署；最小化开发与生产差异以支持持续部署；支持水平扩展而无需改动工具链/架构/实践。**十二要素**：I **Codebase** 一份代码库纳入版本控制、多次部署；II **Dependencies** 显式声明并隔离依赖；III **Config** 配置存于环境变量（不硬编码）；IV **Backing services** 后端服务（数据库/队列/缓存）视为可挂载资源；V **Build, release, run** 严格分离构建、发布、运行三阶段；VI **Processes** 以无状态进程运行，不依赖本地留存状态；VII **Port binding** 通过端口绑定自导出服务；VIII **Concurrency** 通过进程模型横向扩展；IX **Disposability** 快速启动与优雅终止以增强健壮性；X **Dev/prod parity** 保持开发/预发/生产对等；XI **Logs** 日志作为事件流，不管理日志文件；XII **Admin processes** 后台管理任务作为一次性进程运行。方法目标：提升可移植性、降低软件侵蚀（software erosion）成本、提供共同词汇。
- **缺口**：仅结构+摘要；未下载 ePub/正文（本地 BK-01 可交叉核验）。

---

## 6. 采集方法与证据口径

- 可达性判定：`curl -sS -o <file> -w "%{http_code}"`，并核对落盘字节数（非空即视为内容层成功）；连接层失败记为 `000`。
- SRE 两源必须加浏览器 UA（`-A`），且经代理 `172.29.0.1:7890`；其余三源直连。
- 结构提取：解析落地页/目录页 HTML 的 `<a href>` 锚点，按 Part/Chapter 层级归一；每个条目保留官方 URL 便于深链。
- 摘要为**自撰中文归纳**（基于目录结构 + 公开定位），非原文翻译；字数控制在 200–500 之间。
- 可溯源：每条 `source.url` 可解析且为本轮实测；`channel` / `http_status` 显式记录。
