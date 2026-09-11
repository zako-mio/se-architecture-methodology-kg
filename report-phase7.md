# Mission 报告：软件工程 / 架构设计方法论母库 · 阶段7 参考书吸收与知识库融合（阶段1 核验升级）

- **日期**：2026-09-11
- **任务目录**：`~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论/`
- **GATE**：范围=5 深度=5 操作=5 风险=4 → 19 → Deep（`[COMPLEXITY: 19/20]` 继承标记，Build 全程 Deep 推理）
- **本次完成阶段**：**阶段7（阶段1 核验升级）**——用书籍正文对图谱存量 BK 引用做主张级书证核验，产出章节锚 + 缺口 + 可审计证据链，并确定性派生回图谱状态字段
- **母任务**：建立「软件工程 / 架构设计方法论」知识库母库（人读图谱 + Agent 架构判断力），并以良好架构设计方式承载自身
- **关联文档**：`00-plan/stage7-book-absorption-plan.md`（§3.1 ADR-001 / §3.2 ADR-002 决策摘要）、`00-plan/stage7-baseline.md`（ADR 原件属私有设计档案 `18-design/`，不公开，此处以纯文本引用）

---

## 1. 当时情况

### 1.1 母任务与用户诉求

母任务 `0910-软件工程架构方法论` 阶段1–6 已全部完成并上线：母库 **167 节点 / 360 边 / 18 组 / 18 案例**，公开仓 `zako-mio/se-architecture-methodology-kg` + GitHub Pages + Actions 全绿。用户随后提出本轮原始诉求，原话为：「**之前下载了部分书目，在知识库完成后，还未吸收参考书中内容，故需要计划吸收参考书并融入知识库**」。

该诉求的时间序倒置是阶段7 的起点：知识库先建成，参考书语料后到位。

### 1.2 核心缺口：书语料晚于知识库定稿

- 30 本 paid/user-copy 经典著作（DDIA、Clean Architecture、Software Architecture in Practice 等）的语料直到 **2026-09-11** 才全部落入私有语料层 `01-books/_files/`（**75 文件 / 290MB**；含 35 PDF + 13 EPUB + DDIA 26 个中文全文 MD），并配套 `acquired-manifest.json` / `download-log.md`。
- 而图谱（`methodology-dag.json`）与信源主表（`canonical-sources.json`）在 **2026-09-10 前**即已定稿：现有 **106/167 节点引用 BK 信源**（BK 引用合计 159 处），但节点的 `verified`（布尔 `true` **149** / 字符串 `"cited"` **18**）与 `confidence`（`high` 151 / `medium` 16）**全部来自公开线索、官方目录与作者博客的间接核验，从未读过书籍正文**。
- 结论：**当前的「已验证」是名义状态，不是书证状态**。阶段7 要做的，就是把「名义 verified」升级为「带章节锚、可审计的书证核验」。

### 1.3 环境约束

- 图谱冻结指纹 `58a7e3c3…`（阶段5 起未变），`canonical-sources.json` 指纹 `e7cd0eb7…`。
- 生成链仅 Python 标准库、幂等、**无时间戳**；CI 用 `git diff --exit-code` 做漂移检测。
- 沙箱禁 `git push`（公开仓推送须走 GitHub Git Data API）、禁 `python -c`、禁 `rm -rf`。
- 版权红线：书籍正文只入私有语料层，公开层只承载消化重组后的知识与自研脚本。

---

## 2. 制定计划

### 2.1 11 轮拷问收敛

计划轮以 **11 轮拷问** 逐步收敛（其中一次由用户主动要求「**先做工程权衡分析**」再决策）。收敛过程中不预设结论，而是把「落盘层」与「证据模型」两个核心问题分别交给架构裁决流程。

### 2.2 ADR-001：私有核验层为唯一真相源

委派 `architect-worker` 产 ADR-001，经 `gate_architecture.py --kind adr` **机检 6/6 PASS**，用户裁决采纳方案 A：

- **私有核验层为唯一真相源（SSOT）**：记录 节点 ↔ 信源 ↔ 章节锚 ↔ 证据强度 ↔ 复核元数据。
- 节点与信源表的 `verified` / `confidence` / `review_date` / `errata` **一律由确定性派生脚本生成**，禁手改生成物；派生脚本对「**无锚点升级**」判 FAIL。
- **版权粒度裁定**：**章节级结构锚**（BK 号 + 章/节编号与标题 + 证据强度 + 处理日期）**可经脱敏门控进公开层**；**页码区间与原文摘句仅留私有层**。
- 多维权衡矩阵（9 维）加权：**A 4.28 > B 3.72 > C 3.02 > D 2.20**。B/C 因「保留未与书证联动的公开 verified → 双真相」否决，D 因「页码/摘句进公开图谱 → 触版权红线」否决；仅 A 通过全部否决项。

### 2.3 ADR-002：主张级四级强度 + 双向

委派 `architect-worker` 产 ADR-002，同样 **机检 6/6 PASS**，用户裁决采纳方案 A + 指标解耦：

- **主张级四级强度 + 双向（正向回验 + 反向发现）**：拆原子主张——`definition` 1 条 + `detail` 四段各 ≥1 条 + 每条 `errata` 1 条，**单节点主张上限 8 条**（封顶成本）。
- 强度为**封闭枚举**：`direct`（书中明确支持）/ `partial`（支持部分要素或需一步推断）/ `inferred`（概念相关但书未直陈）/ `contradicted`（与书相悖）。
- 方向 `direction`：`forward`（回验存量引用）/ `reverse`（发现应引未引、覆盖缺口）。
- **节点升级判据**：`≥1 条 direct` **且** `0 条 contradicted`；出现 `contradicted` 即产出 `errata` 并阻止升级。
- **指标解耦**：核心主判据保留「可溯源率」；新指标「**直接锚定覆盖率**」**只报告不判** FAIL/WARN。
- 多维权衡矩阵（9 维）加权：**A 3.92 > D 3.51 > B 3.10 > C 3.07**；D 因「不驱动升级」、C 因「无法定位到哪句话被支持」否决。

### 2.4 收敛决策与复杂度

本计划轮共收敛 **11 条决策**，要点包括：pilot 选 **3 本**（DDIA 反向 / CleanArch 3 个正向目标 / SAiP 15 个正向目标）、阅读策略**分层混合**、质检**单路核验 + 程序化回盘 + 高风险项第二路独立复核**、交付边界**全链路含公开层**、派生作用域**增量式**、指标解耦、公开呈现 **C-lite**（新增视图 06 + 节点页一行章节锚，不新增整块）。

复杂度评估 **`[COMPLEXITY: 19/20]` → Deep**（Build 阶段须沿用，不得重新评估）。最终产出计划文档 `00-plan/stage7-book-absorption-plan.md`（**432 行 / 9 节**）。

---

## 3. 执行情况

### 3.1 七路委派

本阶段按 DAG 委派 **7 路**工作：**W1 契约骨架**（核验层 schema + 目录 + 三重隔离）→ **W2a DDIA 反向** / **W2b CleanArch** / **W2c SAiP**（三路并行核验）→ **W3 第二路复核**（verifier-worker 独立视角）→ **W4 + W4b 派生接入与纠偏**（`derive_verification.py` + `aggregate.py` 接入）→ **W5 生成链改造**（视图 06 + 节点页锚行 + deliverables）→ **W6 门控**（新增 `gate_verification.py` + L1–L8）→ **W7 公开层**（装配 + 推送 + Pages 复验）。

### 3.2 执行中挖出并修复的两处根因缺陷

1. **运行时钟污染幂等**：`aggregate.py:308/337` 用 `datetime.date.today()` 写 `meta.updated` → **跨日重聚合即改 SHA**，与「幂等 + 无时间戳」口径冲突 → 改为从 `_base.json` 冻结常量读取日期。
2. **派生循环依赖**：派生器从**派生后 dag** 回读「原值」→ **循环依赖**（失去资格的节点无法回退，`CAS-X-02` 会错误停在 `true`）→ 引入 `10-dag-data/_verification-baseline.json`（从 git HEAD 冻结快照，167 节点）使派生成为 `(baseline, ledger)` 的**纯函数**。

### 3.3 主Agent 回盘复验抓出的关键事实

三路子Agent 均自报 `success`，但主Agent 独立复算发现：

- **DDIA 正向引用 = 0**：原选书未意识到 DDIA 在现图谱中没有任何正向引用，随即把 pilot 调整为 **3 本覆盖双方向**。
- **18 个 `cited` 节点全部是 CAS-X-\* 自研案例**，仅 `CAS-X-02` 引 CleanArch。
- **第二路复核实测 FP 率 18.75%**：96 条 `direct` 中有 **18 条假阳性**被独立复核抓出并保守降级为 `partial`。

### 3.4 子Agent 权限事实

- `architect-worker` 沙箱 **bash 全禁**，故架构门控须由主Agent 亲跑（不得由其自报 PASS）。
- `general` 子Agent 可执行 `python3 script.py`，但读私有语料 + 写分片的唯一写入方约束仍须保持。

---

## 4. 完成情况

### 4.1 门控实测（L1–L8 + 方法论四项 + G-V1..G-V8）

全部现场实测，**全 PASS**：

| 门控 | 实测摘要 | 结论 |
|---|---|---|
| L1 分片自验证 | 23 分片 errors=0 | PASS |
| L2 全图审计 | nodes=167 edges=360 kahn=167/167，errors=0 warnings=0 | PASS |
| L3 结构 + 断链 | structure 427/0；links 5189/0 | PASS |
| L4 视觉 | 272 项 / 212 PASS / 0 FAIL / 0 WARN / 60 SKIP | PASS |
| L5 渲染 | 7 用例 0 悬空 | PASS |
| L6 覆盖度 | manifest 365/365 = 100% | PASS |
| L7 信源 | 悬挂 0 + 可溯源 100% | PASS |
| L8 版式 | 2128/2128 = 100% | PASS |
| 方法论四项 | layer-boundary / glossary / principle-counterexample 36/36 / tradeoff-11 11/11 | 4/4 PASS |
| G-V1..G-V8 | 核验层 schema / 枚举 / 锚点 / 无锚点升级 0 / 改写红线 / 编码 / 幂等 / 对账 | 8/8 PASS |

### 4.2 幂等自证

- `build.py` 连跑生成物哈希一致 `303991d7…`。
- `aggregate.py` 连跑 SHA 稳定（`git diff --exit-code` 为空）。

### 4.3 核验数据

- **144 条核验记录**：`direct` **78** / `partial` **59** / `inferred` **7** / `contradicted` **0**。
- **35 覆盖节点**、**26 升级节点**（G-V4 口径：≥1 `direct` 且 0 `contradicted`）。
- **28 条反向缺口**：`coverage_hole` 10 / `concept_missing` 10 / `missed_citation` 8。
- 第二路复核 96 条 `direct` → **18 条假阳性降级**，FP 率 **18.75%**。
- **本轮 `verified` 零翻转**（维持 149/18），**`contradicted` = 0 无新勘误**——真实产出是章节锚 + 缺口 + 可审计证据链。

### 4.4 指纹与公开层

- 图谱指纹：`58a7e3c3…` → **`9ae4cc01…`**（一次性变更：日期坑修复 + 覆盖应用）。
- 公开层：`_publish` **528 文件** → 远端提交 `08e0ef9`；CI run **`34596436302`** success；Pages **6 URL 全 200**；公开面本机路径 `~` 命中 **0**；导出 **527 件 / 18.46MB**，无 PDF/EPUB。
- `canonical-sources.json` 指纹 `e7cd0eb7…` **未变**。

### 4.5 交付物清单

| 类别 | 交付物 | 规模 |
|---|---|---|
| 架构决策 | ADR-001 / ADR-002 + matrix ×2 | 4 文件（均机检 6/6 PASS） |
| 计划文档 | `00-plan/stage7-book-absorption-plan.md` | 432 行 / 9 节 |
| 核验层（私有 SSOT） | `01-books/_verify/`：契约 / 分片 / ledger / claims / toc / gaps / 第二路复核 / 抽文本 | 全套 |
| 派生链路 | `derive_verification.py` / `gate_verification.py` + 3 个 json（baseline/overrides/book-verification） | 2 脚本 + 3 json |
| 生成链改造 | `gen-views` / `gen-nodes` / `gen-md` / `aggregate` / `config` / `gen_common` / `deliverables` + 新视图 06 + 35 节点页锚行 | 7 文件 + 生成物 |
| 基线 | `00-plan/stage7-baseline.md` | 1 |
| 公开层 | `_publish/`（528 文件）→ 远端 `08e0ef9` | 1 集 |

### 4.6 改动明细

- **新增**：`01-books/_verify/` 全套、`10-dag-data/_verification-baseline.json`、`_verification-overrides.json`、`book-verification.json`、`16-checkpoint/derive_verification.py`、`16-checkpoint/gate_verification.py`、`14-views/06-book-verification.html`、`00-plan/stage7-baseline.md`。
- **修改**：`aggregate.py`（日期坑修复 + 应用覆盖）、`gen-views.py` / `gen-nodes.py` / `gen-md.py` / `gen_common.py` / `config.py` / `deliverables.json`、`publish-manifest.json`（`private` 类 + `private_probe`）、`_publish/.gitignore`、`_base.json`（冻结日期常量）、`methodology-dag.json` / `node-content.json`（再生）。
- **未改**：`canonical-sources.json` 指纹不变。

---

## 5. 反思/分析/建议

### 5.1 关键认知

1. **ADR-002 对 FP 的估计（≤5%）严重偏乐观，实测 18.75%**。这证明「高风险项第二路独立复核」**不是可选项而是必需项**。且 FP 形态高度一致——**claim 是「书中原句 + 我们的推断扩展」的复合主张**，扩展部分被误判为 `direct`。
2. **pilot 的「核验升级」产出为 0 次 `verified` 翻转**，真实产出是**章节锚 + 缺口 + 可审计证据链** → 说明「吸收」的价值主要在**证据可审计**与**覆盖发现**，而非状态翻转。
3. **循环依赖是「派生型 SSOT」的典型陷阱**：真相源之外若有第二个可变来源（派生后的产物被回读），派生即不纯；解法是引入**冻结基线**使派生成为纯函数。
4. **运行时钟是幂等口径的隐形杀手**，且只在「跨日重跑」时暴露，日常测试不触发。
5. **子Agent 自述仍不可信**：本轮 3 路子Agent 全报 success，但独立复算修正了选书前提、发现 FP、并揪出两处根因缺陷。

### 5.2 改进建议

1. 阶段2 应把「**第二路复核**」内建进流水线，而非事后抽查。
2. 主张拆分时应显式标注「**书中直陈部分 vs 我们推断部分**」，从源头降低 FP。
3. 阶段2/3 的准入判据可直接复用 `reverse-gaps.json`。
4. 建议把 `gate_verification.py` 的 **G-V5（改写红线）扩展为 claim 级复合性检测**，对「直陈 + 推断」复合主张主动告警。

---

- **报告双版本**：`report-phase7.md`（本文件）与 `report-phase7.html`（人读入口）。
- **报告门控**：`16-checkpoint/gate_report.py --input report-phase7.html --md report-phase7.md`，R1–R5 全 PASS。
