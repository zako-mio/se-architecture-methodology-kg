# Mission 报告：软件工程 / 架构设计方法论母库 · 阶段1–6 完成

- **日期**：2026-09-11
- **任务目录**：`~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论/`
- **GATE**：范围=5 深度=5 操作=5 风险=4 → 19 → Deep（`[COMPLEXITY: 19/20]` 继承标记，Build 全程 Deep 推理）
- **本次完成阶段**：**阶段6 内容版式重构 + 版权审计与脱敏公开集 + Agent 能力包 + CI/Pages**；阶段1–5（建库）此前已完成并冻结
- **母任务**：建立「软件工程 / 架构设计方法论」知识库母库（人读图谱 + Agent 架构判断力），并以良好架构设计方式承载自身
- **关联文档**：`quality-gate.md`（阶段1–6 门控明细）、`_publish/README.md`（公开集口径权威）、`00-plan/stage6-content-ia-spec.md`（版式契约）、`00-plan/stage6-baseline.md`（阶段6 基线）、`_publish-staging/PUBLISH-MANIFEST.md`（审计清单）

---

## 一、当时情况

### 1.1 任务背景与两用目标

用户要建立一座**软件工程 / 架构设计方法论母库**，兼作两用：①自己学习（**人读图谱**）；②为 **Agent 加持架构判断力**（可机读、可检索、可深链）。核心理念：软件工程 = 理解业务需求 → 可维护可扩展的架构设计 → 落地运维 → 持续对抗技术债的全生命周期管理；**库自身也要体现良好架构设计**——数据与渲染解耦、单一数据源、可重复生成、门控可追溯。

### 1.2 阶段1–5 已完成事实（本轮的继承基线）

- **阶段1–2（调研与证据）**：产出 14 个证据包（A–R，JSON + Markdown）与本地架构分析留档（PA-01..18）。
- **阶段3–4（建模与设计）**：canonical 信源主表（253 实体）、全局 ID 迁移（414 old_id → 253 canonical，零悬挂）、三层 × 11 域 × 3 横切主题的数据模型与生成架构。
- **阶段5（建库，Wave 0–4）**：把证据包扩产为完整母库 —— **167 节点 / 360 边 / 18 组 / 18 案例**；6 视图 + 167 节点页 + 167 MD 镜像 + 18 组页 + 交互 DAG + 根入口；L1–L7 + 方法论四项 + 回放四硬指标全过。
- **冻结指纹（阶段6 回滚锚点）**：`methodology-dag.json` SHA-256 `58a7e3c3…`、`canonical-sources.json` SHA-256 `e7cd0eb7…`；阶段6 结束时上述数据指纹必须不变。

### 1.3 阶段6 的起点

阶段5 交付的母库在**内容正确性**上达标（门控全过），但**内容版式（内容信息的组织与呈现）**存在系统性缺陷。用户明确指出：**「问题最大的不是视觉设计，而是内容排版」**——即每个节点的详情区没有为阅读与扫读服务。

对改造对象 `MTH-F-02.html` 的实测（阶段6 基线 §4b）量化了该缺陷：

| 指标 | 改进前实测 |
|---|---:|
| 全页 `<p>` 数 | **1** |
| 全页 `<div>` 数 | **24** |
| 全页 `<h2>` 数 | **6** |
| 图 / 表 | **0 图 0 表** |
| TOC / 锚点 / 章节编号 | **无** |
| `detail` 字段呈现 | 每个字段被压成一段 **400–600 字不间断卡片** |

因此阶段6 的任务是：**内容版式架构重构**（把「读得下去、扫得出来、可定位、可溯源」编码进生成链与门控），并在此基础上完成**版权审计与脱敏公开集**、**Agent 能力包**与 **CI/Pages**，为公开上传做准备。

### 1.4 环境基础

- `12factor-methodology`（2026-08）成熟 DAG 图谱与生成链，已重构为「数据/渲染解耦」通用框架（`16-checkpoint/`）。
- `kb-construction` skill 的 L1–L7 分层门控体系 + `agency-agents` 角色库。
- 阶段5 冻结的**单一权威图** `10-dag-data/methodology-dag.json` 与 253 canonical 信源。
- 网络策略：默认直连，模型 API 直连，境外站点按需经网关代理。

---

## 二、制定计划

### 2.1 主线性重定位

阶段6 的主线被明确重定位为 **内容版式架构（Content IA）**，而非视觉皮肤：**皮肤只是版式的载体**。目标是让 167 个节点页从「一段段长卡片」变成「**有编号、有锚点、有结构化块、有可溯源证据区**的技术文档」，并把该规范同时写入**生成链**与**门控**，使后续节点维护可机器校验。

### 2.2 四个暂停点（人工把关）

| # | 暂停点 | 裁决内容 |
|---|---|---|
| 1 | **设计选型** | 3 套版式+皮肤候选（A 文档流 / B 卡片·仪表盘 / C 图谱）横评后，用户选定「**仅 A 单套落地**」+「**文档页浅色 / 交互图保持暗色**」 |
| 2 | **样板验收** | 以 `MTH-F-02`（文档页）与 `MTH-O-04`（含真实 `conflicts` 边的冲突页）为样板，验收 §1–§11 块序列后再全量生成 |
| 3 | **审计清单** | 审阅 `_publish-staging/PUBLISH-MANIFEST.md`：长引移出、本机路径脱敏、`needs_review` 裁决 |
| 4 | **推送前** | 口径一致性复核（README vs 报告 vs 门控）、脱敏残差复扫、本报告更新后方可推送 |

### 2.3 W0–W7 波次设计

| 波次 | 目标 | 产物 / 证据 |
|---|---|---|
| **W0** | 基线冻结与回滚锚点 | `00-plan/stage6-baseline.md`（SHA-256 指纹、输入完整性清单、纠偏记录、自决项 17–23） |
| **W1** | 版式与皮肤设计选型 | `18-design/`（cand-A/B/C + compare/gallery + rationale）；暂停点 1 |
| **W2** | 版式契约与样板 | `00-plan/stage6-content-ia-spec.md`（§1–§11 块序列 + 设计 token + 门控点位）；样板 `MTH-F-02` / `MTH-O-04`；暂停点 2 |
| **W3** | 全量重构与门控实装 | `gen-nodes/gen-groups/gen-views/gen-md/gen-index/gen-glossary` 重生 + `gate_layout.py`（L8）+ `gate_visual.py`（L4 首实装） |
| **W4** | 版权审计与脱敏 | `16-checkpoint/audit_publish.py` + `_publish-staging/{PUBLISH-MANIFEST.md,AUDIT-REPORT.json}`；暂停点 3 |
| **W5** | 公开集装配 | `_publish/`（含 README / LICENSE / `.gitignore` / `.nojekyll`） |
| **W6** | Agent 能力包 + CI | `20-agent-skill/`（5 文件）+ `_publish/.github/workflows/rebuild.yml` |
| **W7** | 推送前复核 | 口径一致性、脱敏复扫、本报告与 `quality-gate.md` 更新；暂停点 4 |

### 2.4 版式与皮肤一体出 3 套候选（设计选型过程）

3 套候选**共用同一数据契约**，但 IA 立场与皮肤一体设计，供横评（痛点权重：结构化表达 4 > 可扫读性 3 > 层级导航 2 > 连贯行文 1）：

| 候选 | IA 立场 | 皮肤 | 适用 | 取舍 |
|---|---|---|---|---|
| **A 文档流** | 节点=技术文档，结构化块作文中嵌图/嵌表 | **浅色 Codex**（纸感暖底 `#f5f1e8`、Georgia/宋体衬线标题、琥珀强调） | 精读、教学、打印/导出、无障碍 | 扫读性弱于 B；宽屏留白多 |
| **B 卡片/仪表盘** | 每语义块独立可扫读卡片/指标条 | 暗色 Console（板岩底、蓝强调，与交互图同源） | 速查、Agent 结构化抽取 | 行文呼吸最弱 |
| **C 图谱优先** | 以关系为中心，图 Hero + 注解 | 暗色 Atlas（近黑 + 青紫辉光） | 依赖逆查、影响面分析 | 呈现成本最高 |

**实际选定结果（用户裁决）**：**仅 A 单套落地**——文档页采用 **A 文档流 · 浅色 Codex**，以换取最强的**连贯行文 + 层级导航（TOC/§/锚点）+ 打印导出**能力；**交互图（`13-interactive`）保持暗色**不动，形成「暗色总览 ↔ 浅色精读」的互补心智。设计参考实现留档于 `18-design/cand-A/`（非生成物）。

### 2.5 执行层自决项（主Agent 承担，可被否决）

| # | 决策 |
|---|---|
| 17 | 新增 `16-checkpoint/gate_layout.py` 版式门控（结构块存在性 / SVG 内联有效 / 术语链接数 / 对比表布尔） |
| 18 | 新增契约 `00-plan/stage6-content-ia-spec.md`（版式规范，生成链与后续节点维护共同遵循） |
| 19 | `15-md` 镜像同步结构化块（双轨一致性原则） |
| 20 | 术语内联 = 每术语在页内**首次出现**时链 glossary |
| 21 | 不改 `10-dag-data` 数据契约；派生素材由构建期计算 |
| 22 | `12-groups` / `14-views` / `index.html` 同步套用新版式 |
| 23 | 结构化块数据依据：`prerequisite` 74 节点→学习路径条；`conflicts`/`contrasts` 34 节点→对比表卡；`case_instance` 41 节点→案例带；局部关系 SVG 全量 167 |

### 2.6 门控设计（L1–L8 + 方法论专项 + 回放四硬指标）

- **L1 生成时自验证** → `validate_graph.py --shard`（每批 0 错误）；
- **L2 全量审计** → `validate_graph.py --graph`（字段/ID/计数/无环）；
- **L3 结构 + 断链** → `kb_gate.py --layers structure,links`；
- **L4 视觉（本轮首次实装）** → `gate_visual.py`（像素计数 + 运行时结构 + 外部 VLM 支路）；
- **L5 渲染** → `gate_render.py`（headless Chromium 实渲染 canvas 计数/JS 错误/边端点）；
- **L6 覆盖度** → `gate_coverage.py`（manifest + 四向覆盖 + GR-08/GR-09）；
- **L7 信源** → `gate_sources.py`（canonical 可解析/可溯源率/verified/disputed）；
- **L8 版式（新增）** → `gate_layout.py`（§1–§11 结构块/权衡卡严格归栏/TOC 锚点/术语/自包含/编码/深链/双轨）；
- **方法论专项四项** → `gate_methodology.py`（层边界 / 术语一致性 / 原则↔反例 36 条 / 11 维权衡）；
- **回放四硬指标**：覆盖度 ≥90% / 门控全过 / 可溯源率 ≥95% / 人工抽查无重大语义错误。

**刚性约定**：`skipped ≠ PASS`（环境或产物缺失须显式记录）；无新鲜验证证据不得声称完成。**L4 / L5 在 CI 中显式 SKIPPED（不伪装 PASS）**——CI 标准 runner 不预装 Pillow/numpy/agent-browser。

---

## 三、执行情况

### 3.1 各波委派与产物

**W0 · 基线冻结**：落盘 `stage6-baseline.md`，记录 4 个数据文件 SHA-256、`02-research/`（35 文件）+ `01-books/`（5 文件）输入完整性清单、数据规模实测、纠偏记录与自决项 17–23；`git` 首个 commit 即回滚锚点（本地仓永不推送）。

**W1 · 设计选型**：以 `MTH-F-02`（文档页）与 `MTH-O-04`（冲突页）为样本，产出 A/B/C 三套候选（各含 `index.html` + `conflict.html`）与 `compare.html` / `gallery.html` / `rationale.md`；暂停点 1 由用户选定 A 单套 + 文档页浅色/交互图暗色。

**W2 · 契约与样板**：落盘 `stage6-content-ia-spec.md`（权威契约：§0 不变式 I1–I7、§1 浅色 Codex token、§2 §1–§11 块序列、§3 局部 SVG 规则、§4 权衡卡归栏保真红线、§5 术语内联、§6 跨库深链、§7 无溢出、§8 MD 镜像、§10 门控点位、§11 变更管理）；以样板页验收后进入量产。

**W3 · 全量重构与门控实装**：
- 生成链改造 `gen_common.py`（共享派生函数）→ `gen-nodes` / `gen-groups` / `gen-views` / `gen-md` / `gen-index` / `gen-glossary`，重生 167 节点页 + 19 组页 + 7 视图（含新增 `14-views/glossary.html`）+ 167 MD 镜像 + 根入口；
- 结构块全量落地：局部关系 SVG（167/167）、摘要 `defcard`（167/167）、权衡卡（167/167）、TOC/锚点、`pathbar` 学习路径条（prerequisite 74 节点）、冲突/对比表（34 节点）、案例带、信源证据区；
- 新增 `gate_layout.py`（L8）与 `gate_visual.py`（L4 首实装）；`10-dag-data` 数据指纹保持不变（I1）。

**W4 · 版权审计与脱敏**：`audit_publish.py` 扫描 64 份原件，分级 A=30 / B=14 / C=20 / D=0；**长引移出 42 处 / 20493 字**（最长 2507 字），**本机路径脱敏 209 处**，疑似凭据 0 处；产出 `PUBLISH-MANIFEST.md` + `AUDIT-REPORT.json`；暂停点 3 审阅，`needs_review` 1 项（`E-iso-standards.json` 移出占比 56%）待裁决。

**W5 · 公开集装配**：装配 `_publish/`（自包含公开交付集），含 `README.md`（阶段6 口径权威）、`LICENSE`（MIT）、`.gitignore`、`.nojekyll`；装配阶段另发现并改写 4 处残留（见 §4.4）。

**W6 · Agent 能力包 + CI**：`20-agent-skill/`（`SKILL.md` / `cheatsheet.md` / `routing.md` / `decision-matrix.md` / `node-index.md`，轻量速查 + 路径路由）；`rebuild.yml`（重建 → 漂移检测 → L2/L3/L6/L7/L8 + 方法论门控 → L4/L5 显式 SKIP → Pages 部署）。

**W7 · 推送前复核**：对 `_publish/` 全量残差复扫（本机路径 0、U+FFFD 0、疑似凭据 0、陈旧月份 0、内联脚本 0）；统一 README / 报告 / 门控三方口径；本报告与 `quality-gate.md` 升级为阶段1–6 口径。

### 3.2 关键实测证据

- **版式缺陷 → 结构化改造**：改进前 `MTH-F-02.html` 仅 1 `<p>` / 24 `<div>` / 6 `<h2>` / 0 图 0 表 / 无 TOC；改造后每节点页含内联关系 SVG、`defcard`、权衡卡、TOC+§锚点、信源证据区，L8 版式门控综合 **2124/2124 = 100.00%（问题 0）**。
- **权衡卡严格归栏**：`gate_layout.py` 对 `detail.tradeoff` 三栏（收益/代价/反例）做**逐句显式标记词**校验（反例：反例/误区/失败/反面；代价：代价/成本/风险/过度/不足；收益：收益/好处/价值），无标记句进中性「原文要点」，文本逐字引用——167/167 通过、问题 0。
- **视觉门控首实装**：L4 `gate_visual.py` 像素 + 运行时 + VLM 三支路共 **262 项检查 / 0 FAIL / 15 WARN / 44 SKIP**，综合判定 **WARN**（无 FAIL）；WARN 均为可接受的版式提示（VLM 支路 5 PASS + 1 WARN：glossary 超宽表格在 `overflow-x:auto` 容器内横向滚动）。
- **数据契约不动**：全量重生后 `methodology-dag.json` 仍为 167 节点 / 360 边、Kahn 167/167 无环、`validate_graph` errors=0 warnings=0，SHA-256 指纹未变。

### 3.3 遇到的问题及处置

**（1）权衡卡归栏的两次口径澄清**

- **第一次**：主Agent 怀疑实现存在「**越栏**」（把非本栏的句子塞进收益/代价/反例栏）。实测证明原实现即**严格标记词**驱动，不存在越栏；遂以「**仅按显式标记词归栏**」固化语义，并写入 `gate_layout.py` 的**强校验**（无标记证据不得归栏；无证据句进中性列表）。契约 §4「保真红线」与门控点位 §10 同步对齐。
- **第二次**：主Agent 再次误判权衡卡「**把无标记句归入代价栏**」。回盘逐句核对后发现，被疑的两句分别含标记词「**风险**」，归栏成立。该误判同样被实测推翻。

**（2）主Agent 的两次自我纠偏**

- **① `verified` 口径纠偏（纠偏本身是错的）**：主Agent 曾用**真值判断**（truthiness）统计，把 `"cited"`（字符串，真值也为 True）误计为 `verified=true`，据此得出「167/167=100%」并**反驳接力文档的 89.22%**。实测真相：`true` 149 个 + `"cited"` 18 个 = 167，故 `verified=true` 占比 **89.22% 成立，接力文档正确**。主Agent 结论错误，已撤回并写入基线纠偏记录（敏感点：**必须用 `is True` 判断**）。
- **② 权衡卡误判纠偏**：见上（2），实测那两句含标记词「风险」，原实现正确。

**（3）审计的正则误判复验**

粗正则初筛曾判定 `02-research/P-techdebt.json` 与 `02-research/N-team-conway.md` 含长引；**回盘复核后均为 ≤200 字**，未达长引移出判据，**未移出**（二者在 `PUBLISH-MANIFEST.md` 中分别记为 B 级原样复制与 A 级原样复制）。

**（4）响应式溢出的根因与修法**：A 参考实现中 `.nbhd{min-width:680px}` 等在 390px 下导致页面级横向溢出（实测 A +124px / B +89px / C +67px）；契约 §7 规定改为 `.figbox{overflow-x:auto}` + `.nbhd{width:100%}`，把滚动收敛到容器内，页面级 `scrollWidth <= 391`——L4 运行时 `runtime.h-overflow` 全 PASS 验证。

### 3.4 阶段1–5 执行回顾（建库 Wave 1–4 摘要）

- **Wave 1 · 本质层 + 方法论层**：按域分批委派 `W1-F/G/H/I/J`、`W1-K/L/M/N/O` + 补强 `W1b-G/H`，产出本质层 51 + 方法论层 67 节点；`W1-J`/`W1-N` 字数不足节点补至 ≥1500 字。
- **Wave 2 · 技术层 + 案例层 + 12factor 映射**：`W2-TEC-*` 产出技术层，`W2-TEC-FN` 补 F/N 技术层 4 节点满足 GR-08；`W2-CASE-A/B` 提炼 18 个 `CAS-X-*` 案例；`W2-XREF` 产出 38 行 12factor 对照表（不内联主 DAG）。
- **Wave 3 · 多视图 + 深链**：由单一数据源派生 6 视图 + 167 节点页 + 167 MD + 18 组页；12factor 跨年份深链修复 38 处断链。
- **Wave 4 · 门控与留档**：全量 L1–L7 + 方法论四项 + 回放四硬指标通过；产出阶段5 `quality-gate.md` 与报告双版本。

阶段1–5 关键问题处置：历史边 id `EB-P##` 11 条归一为 `E-101..111`；契约路径漂移以「新增 §〇.1 权威修正」对齐；O-PC 覆盖由启发式升级为 `opc-mapping.json` 显式映射（36 行）；Wave 0 骨架 11 种子节点由 281–424 字补齐至 1604–1772 字（全库 <1500 字 = 0）。

---

## 四、完成情况

### 4.1 最终交付物清单

| 类别 | 交付物 | 规模 |
|---|---|---:|
| 主图谱 | `10-dag-data/methodology-dag.json` | **167 节点 / 360 边 / 18 组 / 18 案例** |
| DAG 数据 | `10-dag-data/{_parts/*.json(22), _base.json, _batch-plan.json, stats.md}` | 分片可重聚合 |
| 节点页 | `11-node-pages/*.html` | **167**（§1–§11 块序列） |
| MD 镜像 | `15-md/nodes/*.md` | **167** |
| 组页 | `12-groups/*.html` | **19**（18 组 + index） |
| 多视图 | `14-views/*.html` | **7**（6 视图 + 新增 glossary） |
| 交互 DAG | `13-interactive/index.html`（+vendor） | 1（暗色，保持原状） |
| 根入口 | `index.html` | 1 |
| 版式契约 | `00-plan/stage6-content-ia-spec.md` | 1 |
| 阶段6 基线 | `00-plan/stage6-baseline.md` | 1 |
| 设计留档 | `18-design/{cand-A/B/C, compare, gallery, rationale}` | 3 套候选 |
| 12factor 对照 | `16-checkpoint/xref-12factor.json` | 38 行 |
| 原则↔反例映射 | `16-checkpoint/opc-mapping.json` | 36 行 |
| canonical 信源 | `03-knowledge-map/canonical-sources.json` | 253 |
| 新增脚本 | `gate_visual.py`（L4 首实装）+ `gate_layout.py`（L8）+ `audit_publish.py`（发布审计）**3 个门控/审计脚本**，另 `gen-glossary.py`（术语表生成） | 4 |
| Agent 能力包 | `20-agent-skill/{SKILL,cheatsheet,routing,decision-matrix,node-index}` | 5 文件 |
| 审计留档 | `_publish-staging/{PUBLISH-MANIFEST.md, AUDIT-REPORT.json}` | 2 + 脱敏副本 |
| 公开集 | `_publish/`（README / LICENSE / `.gitignore` / `.nojekyll` / CI） | 1 集 |
| CI | `_publish/.github/workflows/rebuild.yml` | 1 |
| 门控 / 报告 | `quality-gate.md` / `report.md` / `report.html` | 本阶段（阶段1–6 口径） |

### 4.2 数据规模与层/域分布（现场实测）

- **167 节点 / 360 边 / 18 组 / 3 横切主题 / 18 案例**；`dag_acyclic=true`，孤立节点 **0**，`nodes < 1500 字` = **0**。
- layer = essence **51** + methodology **67** + technology **31** + case(layer=null) **18**。
- 域分布：F13 · G17 · H16 · I14 · J17 · K17 · L14 · M14 · N13 · O14 · X18(cases)。
- 边类型：`case_instance` 69 · `derives_from` 69 · `implements` 59 · `prerequisite` 58 · `combination` 36 · `dependency` 24 · `contrasts` 14 · `enables` 13 · `refines` 13 · `conflicts` 4 · `cross_reference` 1。
- 正文长度（definition + 四 detail 字段）：min **1501** / 中位 **1536** / max **1813** 字。
- canonical 信源 **253**；`verified` 取值分布 **`true` 149 / `"cited"` 18**；`verified=true` 占比 **149/167 = 89.22%**；可溯源率 **167/167 = 100%**。

### 4.3 阶段6 门控结果（全部现场实测）

| 门控 | 实测 | 结论 |
|---|---|---|
| L1 分片自验证 | 分片 `errors=0`（阶段5 全量通过，阶段6 未改数据） | **PASS** |
| L2 全图审计 | `nodes=167 edges=360 kahn_visited=167/167`，`errors=0 warnings=0` | **PASS** |
| L3 结构 + 断链（母库口径） | structure 检查项 **412** / 问题 **0**；links 检查项 **5134** / 问题 **0** | **PASS** |
| L4 视觉（首实装） | **262 项检查 / 0 FAIL / 15 WARN / 44 SKIP**（像素+运行时 256，VLM 支路 5 PASS + 1 WARN） | **WARN**（无 FAIL） |
| L5 渲染（headless Chromium） | **7 用例全 PASS**；`skipped=0`；JS 错误 0；悬空端点 0 | **PASS** |
| L6 覆盖度 | manifest **363/363 = 100%**；四向 **100%**；GR-08 PASS；GR-09 **11/31 = 35.48%** | **PASS** |
| L7 信源 | canonical 引用 1446（node 605 / errata 222 / edge 619），悬挂 **0**；可溯源 **100%**；`verified=true` **89.22%**；disputed 漏标 **0** | **PASS** |
| L8 版式 | 综合覆盖率 **2124/2124 = 100.00%**，问题 **0** | **PASS** |
| 方法论专项 | layer-boundary / glossary / principle-counterexample **36/36** / tradeoff-11 **11/11** | **4/4 PASS** |
| 回放四硬指标 | 覆盖度 100% / 门控全过 / 可溯源 100% / 抽查无重大语义错误 | **达标** |

> **L4 口径说明**：`gate_visual.py --check all` 的像素+运行时支路为 **256 项 / 0 FAIL / 14 WARN / 44 SKIP**；并入外部 VLM 支路（`_render-shots/visual/vlm-result.json`，5 PASS + 1 WARN）后为 **262 项 / 0 FAIL / 15 WARN / 44 SKIP**。综合判定 **WARN**，无 FAIL。唯一 VLM WARN 为 glossary 超宽表格的容器内滚动（契约 §7 允许）。
>
> **CI 说明**：L4 / L5 因 CI runner 缺 Pillow/numpy/agent-browser，在 CI 中**显式 SKIPPED**，日志打印跳过原因，**绝不伪装 PASS**。

### 4.4 过程改动明细（阶段6）

1. 新增版式契约 `00-plan/stage6-content-ia-spec.md`（§1–§11 块序列 + 保真红线）。
2. 生成链改造并全量重生 167 节点页 / 19 组页 / 7 视图 / 167 MD / `index.html`；**`10-dag-data` 数据契约与 SHA-256 指纹不变**。
3. 新增 `14-views/glossary.html`（152 术语 + ASCII 安全锚点 `g-001…`），纳入 `14-views/index.html` 导航。
4. 新增 `gate_layout.py`（L8 版式门控）、首实装 `gate_visual.py`（L4）、`gen-glossary.py`（术语表生成）。
5. 术语内联：每术语页内首次出现链 glossary（`a.term` → `#g-0NN`），禁止跨标签/代码/ID/URL 匹配。
6. 响应式修法：`.figbox{overflow-x:auto}` 收敛滚动，390px 页面级溢出 = 0。
7. 12factor 跨库深链统一为绝对 URL（`https://zako-mio.github.io/12-factor-methodology-kg/...`），生成物中 `2026-08/` 出现次数 = 0。
8. 审计脱敏：`audit_publish.py` 对 64 原件长引移出 42 处 / 20493 字、本机路径脱敏 209 处。
9. 公开集残差改写 4 处（仅改 `_publish/` 副本，未触碰母库）：`methodology-dag.json` ×9、`_parts/W2-CASE-B.json` ×9、`_batch-plan.json` ×1 的 `entry_links` 本机路径 → `~`；`audit_publish.py` 工具文档串与凭据正则前缀去本机路径化。
10. 新增 `20-agent-skill/`（5 文件）与 `_publish/.github/workflows/rebuild.yml`（重建 + 漂移检测 + 门控 + Pages）。
11. 报告/门控三件套同步覆盖 `_publish/`；因 `quality-gate.md` 含 MISSION_ROOT 绝对路径，**仅 `_publish/` 副本**将其改写为 `~/…`（公开集脱敏），母库原件保留绝对路径不变；复扫 `_publish/` 本机路径 0、U+FFFD 0、疑似凭据 0。

### 4.5 上线结果（公开仓 · 现场实测）

| 项 | 实测值 |
|---|---|
| 公开仓 | `zako-mio/se-architecture-methodology-kg`（**PUBLIC**，默认分支 `main`） |
| 仓库地址 | https://github.com/zako-mio/se-architecture-methodology-kg |
| Pages 站点 | https://zako-mio.github.io/se-architecture-methodology-kg/ |
| Pages 可达性 | 首页 / 节点页 / 组页 / 术语表 / MD 镜像 / 交互图 / Agent skill **7 项全部 HTTP 200** |
| CI 运行 | `507aff1` → run `34510503610` **success**；`8c69f27`（CI 修正）→ run `34510696621` **success**（build + deploy） |
| CI 覆盖门控 | 重建（幂等）+ 漂移检测（`git diff --exit-code`）+ L2 / L3 / L6 / L7 / L8 + 方法论 4 项全过；**L4 / L5 显式 SKIPPED（绝不伪装 PASS）** |
| 版权红线复验（远端原文） | `02-research/E-iso-standards.json` 占位符 14 处、残留 ISO 正文行 **0**；`01-books/` 仅 5 个元数据文件 |
| 公开集体量 | 505 文件 / 19 MB |
| CI 首次失败点与处置 | `configure-pages` 的 `enablement: true` 因 `GITHUB_TOKEN` 无权创建 Pages 站点而失败（**其前置 13 个步骤全绿**）；改为用 CLI 一次性启用 Pages（`gh api -X POST .../pages -f build_type=workflow`）+ 工作流内注释化说明前置条件 |
| 遗留（透明披露） | Node 20 废弃警告（action 大版本可日后升级）；L4 15 条 WARN 均为非阻断项；检索层 D2 与 12factor 反向深链未做（用户已决定不做） |

### 4.6 暂停点 4 的裁决结果（已执行）

- `02-research/E-iso-standards.json`：**保留脱敏版**（ISO 正文性字段 `scope_en/zh` 等 14 个已全部移出，仅余标准号/版本/状态/URL 等事实元数据）。
- 公开集范围：**按现方案定稿**（交付物 10–15 + 生成链 16 + `00-plan` + `01-books` + 脱敏 `02-research` + `03-knowledge-map` + 报告三件套；不公开 `18-design/`、`_backup-idmigration/`）。
- 推送方式：先本地提交供用户过目 → 确认后建公开仓推送；Pages 在 Actions 首次绿后启用。

---

## 五、反思 / 分析 / 建议

1. **内容版式缺陷的根因是「结构化缺失」，而非视觉不美**。改进前 `MTH-F-02.html` 一页仅 **1 个 `<p>`、24 个 `div`、6 个 `h2`、0 图 0 表、无 TOC/锚点**，每个 `detail` 字段被压成 **400–600 字不间断卡片**——信息没有被「分块、编号、定位、图示」。修复的抓手是把 §1–§11 块序列**数据驱动**地写进生成链，而不是调 CSS。这印证了用户的判断：**内容排版才是主矛盾**。

2. **先落契约再并行委派 = 长 prompt 不截断、零返工**。阶段6 先落盘 `stage6-content-ia-spec.md`（版式契约）与 `stage6-baseline.md`（事实基线），使多路并行子Agent 只需引用短路径契约而非接收超长 prompt，避免了长 prompt 被截断导致的约定漂移；生成链与门控共享同一份块序列定义，保证双轨一致。

3. **门控自身要可机检——把「保真红线」写成逐句标记词校验**。权衡卡归栏最容易在「看起来合理」处失真，因此不写成文字约定，而写成 `gate_layout.py` 的**逐句显式标记词校验**（无证据不得归栏）。这让「保真」从主观承诺变为可证明、可回归的机器判据。

4. **视觉门控中像素重叠探针误报率高，只作 WARN**。L4 的 `pixel.overlap-suspect` 在 14 条 WARN 中占绝大多数（密集文本行被 ≤3px 背景隔断即触发），属启发式粗检；因此其定位是**提示而非阻断**，真正阻断的是 FAIL。对 grep 类启发式应以「粗筛 + 人工/VLM 复核」而非「一票否决」对待。

5. **子Agent 自述必须回盘复验——本轮 3 次复验抓出误判**。三次误判（权衡卡疑越栏、疑无标记句归栏、`verified` 真值口径）均由「回盘实测」纠正，其中一次是**主Agent 自己的错误结论**。这说明：**任何结论都必须以新鲜的一手数据复算**，接力文档与子Agent 自述都不能直接采信；`skipped`/`WARN` 也要如实标注，不得伪装 PASS。

6. **版本敏感判断要用 `is True`**：`verified` 取值存在 `true`（布尔）与 `"cited"`（字符串）两种，真值判断会把 `"cited"` 误计为 true。该陷阱已写入基线纠偏记录与门控口径（GR-10 按 149/167=89.22% 判定）。

7. **遗留与建议（交由后续阶段决策）**：
   - **`needs_review` 已裁决（撤回原建议）**：`02-research/E-iso-standards.json` **保留脱敏版**——ISO 正文性字段（`scope_en/zh` 等 14 个，最长 2507 字）已全部移出，余下标准号/版本/状态/URL 属不受版权保护的事实元数据，对读者有价值。
   - **L4 / L5 已在本地补跑并留档**：`gate_visual.py --check all` → 262 项 / 0 FAIL / 15 WARN；`gate_render.py` → 7 用例全 PASS；CI 无法覆盖故在 `rebuild.yml` 中显式 SKIPPED。
   - **12factor 反向深链未做**：当前仅母库→子库单向；建议补子库→母库回链形成双向导航。
   - **30 本付费书语料待用户提供**（`01-books/gap-request.md`，P0 14 / P1 10 / P2 6），提供后走 pdf-worker 解析。
   - **检索层 D2 挂起**：预留接口不建，建库后再定（轻量 FTS5 为候选）。
8. **上线完成**：公开仓 `zako-mio/se-architecture-methodology-kg`（**PUBLIC**）+ GitHub Pages 已上线 —— 站点 https://zako-mio.github.io/se-architecture-methodology-kg/ ，仓库 https://github.com/zako-mio/se-architecture-methodology-kg ；Actions 两次运行（`34510503610` / `34510696621`）均 **success**。**版权红线**：书籍/标准正文只入本地语料层，公开库只承载消化重组后的知识与自研脚本（远端复验：ISO 正文残留 0、`01-books/` 仅元数据）。
9. **下一步建议**：①按需升级 GitHub Actions 的 action 大版本（消除 Node 20 废弃警告）；②按需启用检索层 D2 与 12factor 反向深链；③30 本付费书语料由用户提供后走 pdf-worker 解析（`01-books/gap-request.md`，P0 14 本优先）。
