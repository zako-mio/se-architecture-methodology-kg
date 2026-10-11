# 接力 Prompt：软件工程 / 架构设计方法论母库 · 阶段7（阶段2 已完成 → 轨B 已核验 8 本 → 阶段3 首批已准入）

> 用途：跨窗口接续任务。把本文档**整段**交给下一个会话的主Agent 作为任务输入即可。
> 生成：2026-09-11（阶段2 方案定稿 + 留档报告 + 门控 5/5 后）　生成者：上一窗口主Agent
> 本版**全面覆写**上一版（阶段7 阶段1 之后）；上一版仍在本地归档仓历史中可取回。
> 上一窗口已完成：**阶段2（内容增密）方案设计**（只出方案、不执行）。**本窗口的主任务 = 按方案执行。**

## ⚠️ 本轮增量（2026-10-11 · 阶段7 **阶段3 轨C 首批准入 + 轨B 续做三本 + 轨D 能力包同步**）—— 本节优先于下方 §A 的旧任务陈述

**本轮执行的是阶段3 全量四轨**：轨C（消费 ADR-004 做首批准入）、轨B 续做（BK-021/BK-024/BK-020）、
轨D（能力包同步 + 两段派生）、收尾 7 条裁决。全部已上线。

| 项 | 本轮实测结果 |
|---|---|
| **轨C 首批准入** | 新增 **`TEC-H-04` 依赖结构度量与渐进收紧治理**（technology/H，正文 1697 字，`sources` = BK-007 + BK-011）+ **4 条边**（E-996..E-999） |
| 图谱规模 | **168 节点 / 364 边 / 18 组**（**新建组 0**）；层分布 51 / 67 / 32 / 18 |
| 计数对账 | 五处（`meta.total_nodes` / 实际 / `deliverables.json` ×4 / `node-index.md` 表行 / `stats.md`）**偏差 0** |
| **谓词重放** | 新增 `replay_admission.py`：**一致率 100%（33/33）** + 负例 **4/4** + 禁止快照常量自检 PASS |
| **轨B 续做** | 新核验 **3 本**（`refactoring`/BK-021、`release-it`/BK-024、`clean-code`/BK-020）→ 已核验书 **8 本** |
| 核验层规模 | 记录 **341→403**；覆盖节点 **57→64**；缺口 **60→106** |
| 第二路复核 | 覆盖全部 `direct` **54/54 = 100%**；agree 51 / **降级 3**（`VR-CC-013`→inferred、`VR-RI-006`/`VR-RI-012`→partial） |
| 图谱指纹 | `b11eae6c…c197789` → **`f1f09a9b…87303a39`**（仅 10 行 `review_date` + 1 行 `verified`） |
| 门控 | `gate_verification` **9/9 PASS**；`validate_graph` errors=0；L6/L7/L8 + 方法论 4/4 + G-D 5/5 + `kb_gate` 2/2 全 PASS；版权 **0 命中**；负例 11/11 + 6/6 |
| 公开层 | 远端 commit **`2319cede…`**，tree **562 blobs == 本地 `ls-files`**；CI **success**；Pages **200** |
| 能力包 | 两段派生完成；DSH `reconcile.py` **PASS**（46 skills 逐字节可复现） |
| 基线 | `MISSION_ROOT/00-plan/stage7p4-baseline.md` |

**🔴 本轮发现的三处「文档不可信」前提纠正**（务必继承）：

1. **EPUB 体积表不准**：接力文档 §E.1 的 Tier A 体积有误（Release It! 称 6.2MB **实为 0.46MB** 等）。
   但**8 本 EPUB 抽取实测全部成功**（386KB–1.68MB 正文），Tier A 成立。
2. **「引用密度」不可复现**：文档称 BK-021=13 / BK-025=46 / BK-008=37；按节点 `sources[]` 实测为
   **BK-021=4 / BK-025=26 / BK-008=16**。文档数字口径未知，排序须重算。
3. **`refactoring.txt` 实为第 1 版（1999）**，不是任务书与 manifest 写的 2nd/2018 ——
   版权页 `Copyright © 1999`、ISBN `0-201-48567-2`、13/14/15 章作者为 Opdyke/Roberts+Brant/Beck、
   第 2 版专有坏味道（Mysterious Name / Global Data / Insider Trading）**全部缺席**。
   ⇒ `toc-refactoring.json` 的 `edition` 已改为 `1st/1999`；**manifest `P0-09` 的 `edition_actual` 仍是错的**，
   下一轮应订正（或补入真正的第 2 版语料）。锚点（章号）与语料一致，本次核验结论不受影响。

**🔴 本轮厘清的两段派生链与两处反向漂移**（见基线 §6）：

- 派生链 = `20-agent-skill/` --[`install-skill.py`]--> `~/.config/opencode/skills/architecture-judgment/`
  --[`~/.dsh/skills/opencode/install.py`]--> `~/.dsh/skills/opencode/architecture-judgment/`。
  **接力文档只写了第一段。**
- 反向漂移①（内容）：opencode 侧含仓内源侧没有的 0916 内容（规模三问、architect-worker 放行、ledger 回报通道）。
  **直接 `--apply` 会丢失** → 本轮用**三方合并**无损回植。
- 反向漂移②（私有层）：DSH `_private/{gate_architecture.py,local-bindings.json}` 比 0911 tooling **更新**
  （含 `GATE_LEDGER`/`ARTIFACT_ROOT`）→ 已从 1011 构建产物回植并重跑派生。
  **⚠️ 遗留风险：再跑一次 stage-1 `--apply` 会重新引入降级**（根治需更新 0911 tooling，属另一任务目录，本轮未动）。

**下一窗口的输入件**：
- 本轮基线（指纹 + 门控全表 + 公开层对账 + 回滚路径 + 待裁决） → `MISSION_ROOT/00-plan/stage7p4-baseline.md`
- 缺口号归一化报告 → `MISSION_ROOT/01-books/_verify/_meta/gap-id-reassignments.json`
- ADR-004（阶段3 准入与 ID 分配规则） → `MISSION_ROOT/18-design/adr/ADR-004.json`

**下一步建议（按优先级）**：
1. **旧缺口 `proposed_node` 回写**（ADR-004 §决定三要求）：`GAP-SAIP-003/004/007` 等仍是中文概念名，
   应按 ADR 裁决回写为 `MTH-F-07`（ASR）/ `MTH-G-12`（ADD）/ T3 宿主。
2. **T2 候选册晋升**：21 个 T2 保留号 + 本轮新增 36 个 T2 提案，取得第二个独立信源的 `direct` 锚即晋升 T1。
3. **SRE 采集**（`BK-025` 44 章 / `BK-026` 30 章，全文可得、CC BY-NC-ND 4.0）：
   许可为 **ND**，须先裁决「SRE 派生的节点正文是否进公开层」；建议先只做私有层采集 + 核验。
4. `BK-008`（APoSD）语料不足（本地仅 20 页无文本层），需 OCR 或补采集。

---

## ✅ 本轮增量（2026-10-12 · 阶段7 **阶段3 续做：P0 缺口号回写 + P1 T2 晋升评估 + P2 SRE 私有层采集**）—— 本节优先于上方 §「本轮增量（2026-10-11 …）」与 §A

**三轨全部完成**：P0（ADR-004 §决定三要求的旧缺口 `proposed_node` 回写）、
P1（T2 候选册晋升评估 → **0 晋升**）、P2（BK-025/BK-026 私有层采集 + 核验 + 第二路复核）。
**图谱零变更**（168/364/18 未动）；本轮是**纯核验层扩展 + 缺口号一致性回写**。

| 项 | 本轮实测结果 |
|---|---|
| **P0 回写** | **16 条**缺口 `target` 按 ADR-004 `id_status` 回写（新增 `16-checkpoint/writeback_gap_ids.py`）；映射报告 `01-books/_verify/_meta/gap-id-writeback.json` |
| **P0 判据修复** | `replay_admission.py` 的概念集判据由「`proposed_node` 非空」改为「裁决表 `tier ∈ T1/T2/T3`」——**回写暴露了口径缺陷**（见基线 §4） |
| **P1 晋升评估** | 新增 `replay_admission.py --scan-promotion`：候选 **30** 条，**可晋升 0 条**（全部单源）；负例 **3/3**；报告 `_meta/t2-promotion-scan.json` |
| **P2 采集** | BK-025 **42 章**（1 075 398 字符）/ BK-026 **29 章**（925 151 字符）；**直连 200、无需代理**（推翻 fetch-log 旧结论）；CC BY-NC-ND 4.0 **仅私有层** |
| **P2 核验** | 记录 **+122**（BK-025 78 / BK-026 44）；覆盖节点 **64→78**；已核验书 **8→10** 本 |
| **P2 第二路复核** | direct **360/360 全覆盖**；本轮降级 **5** 条（`VR-SRE-105/110/119/129/137`）；`anchor_locatable=false` 3 条 |
| 缺口全表 | **106 → 119**（+13：`GAP-SRE-*` 7 / `GAP-SREW-*` 6） |
| 图谱指纹 | **未变**（`f1f09a9b…87303a39`） |
| 核验层指纹 | ledger `a2e87bfe…` → **`ab276405…`**；overrides 64→**78** 节点；book-verification `dfbdd6b1…` |
| 门控 | `gate_verification` **9/9 PASS**；validate_graph errors=0；L2/L3/L6/L7/L8 + 方法论 4/4 + G-D 5/5 + `kb_gate` 2/2 全 PASS；版权 **0 命中**；负例 11/11 + 6/6 |
| **L4/L5（本轮纠正）** | 旧记录称「缺 `agent-browser`」**有误**：`agent-browser 0.34.0` 在 nvm bin，宿主 PATH 缺 nvm 导致解析失败。PATH 引导后 **L4 PASS（212/272，fail 0）/ L5 PASS（7/7，skip 0）** |
| 公开层 | 远端 commit **`d1d64ec5…`**，**566 blobs == 本地 `ls-files`**；CI run **`38156480019` success**；Pages 200 且已含新书证 |
| 基线 | `MISSION_ROOT/00-plan/stage7p5-baseline.md` |

**🔴 本轮四条必继承的教训**：

1. **动核验层就必须跑 `build.py`**：第一次推送因节点页未再生而 **CI Drift FAIL**；
   且「只改生成物不改数据/脚本」的提交**不触发 CI**（`paths` 过滤）⇒ 须 `gh workflow run rebuild.yml` 手动触发并确认 success。
2. **`proposed_node` 的语义是「号分配状态」，不是「是否概念提案」**：任何以它作概念集判据的逻辑都会在号回写后失效。
3. **暂存分片前缀不得互为前缀**（`sre` ⊂ `srew`）：`gaps-<prefix>*.json` 会串号；已改为精确双模式 glob。
4. **子 Agent 工具集不稳定**：首名工人**无 `write`**，其余有。派活前先做能力探针，或统一用 `subagent`。

**下一窗口的输入件**：
- 本轮基线（指纹 + 门控全表 + 公开层对账 + 回滚路径 + 待裁决） → `MISSION_ROOT/00-plan/stage7p5-baseline.md`
- P0 回写映射 → `MISSION_ROOT/01-books/_verify/_meta/gap-id-writeback.json`
- P1 晋升扫描 → `MISSION_ROOT/01-books/_verify/_meta/t2-promotion-scan.json`

**下一步建议（按优先级）**：
1. **K 域记录上限裁决**：ADR-003 的 8 条上限迫使本轮裁掉 **42 条合法 direct 证据**（14 个 K 域节点实有 10–12 条）。
   建议走一次 ADR 把 K 域纳入 `DENSIFY_NODES`（上限 16）——实测纳入后**不超限**。
2. **T2 晋升**：取得第二独立信源前不动；扫描器已就绪（`--scan-promotion`）。
3. **`build_claims()` 跨书覆盖缺陷**（新发现）：`derive_verification.py` 对同一节点跨书**只保留首个 slug 的 claims**，
   导致 `ESS-O-02` 的 clean-architecture 主张丢失（`ESS-O-02#principle#1` 重复的根因）。
4. **轨B 剩余书核验**：除 SRE 两本外，多需 PDF→OCR，边际成本高。



路径约定（全文只在此处声明一次，正文一律写 `MISSION_ROOT/...` / `SUB_LIB_ROOT/...`）：

```text
MISSION_ROOT = "~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"
SUB_LIB_ROOT = "~/opencode/archive/Mission-file/2026-08/0823-12factor-methodology"
```

本文档不含任何本机绝对路径，可直接复制进公开仓 `00-plan/`。

---

## A. 你的角色与任务

你是**主Agent（调度者）**：分析 → 拆解 → 委派子Agent → 聚合 → 门控；**不亲自执行多步操作**。子Agent 只执行、以结构化 JSON 回报；**主Agent 必须回盘复验，不信子Agent 自述**。

**阶段 1–6、阶段7 阶段1（核验升级）已全部完成并上线；阶段7 阶段2（内容增密）方案已定稿（`accepted`）。**
**本窗口主任务 = 按 `MISSION_ROOT/00-plan/stage7-phase2-content-densification-plan.md`（454 行 / 9 节）执行阶段2**：
以核验层主张锚定位，用一手书证深化 **26 个有 `direct` 锚节点**的五段正文，并完成派生、门控、重生、公开层推送。

- ⛔ **不要重做阶段 1–7**；⛔ **不要重新决策 §B**（尤其 §B.3 的 12 项阶段2 决策已由用户逐项裁决）。
- **执行前必读顺序**：① 方案文档全文 → ② 本文件 §E 契约 / §F 方案要点 / §G 执行清单 / §H 纪律 → ③ `MISSION_ROOT/00-plan/stage7-baseline.md`。
- **复杂度 = `[COMPLEXITY: 18/20]` → Deep**（Variant 继承规则：**必须沿用，不得重新评估**）。
- ⚠️ 本任务**只做 26 个节点**。9 个无 `direct` 锚节点（见 §F.3）**禁止改写**，G-D5 会硬拦。

---

## B. 已确认决策（⛔ 不要重新决策，除非用户明确要求）

### B.1 母库基础决策（阶段1–6，沿用）

| # | 决策 |
|---|---|
| 1 | 范围 = **全生命周期方法论**；内容分**三层**：本质层 `essence` / 方法论层 `methodology` / 技术实践层 `technology` + **案例层 `case`** |
| 2 | 组织模型 = **多维复合**：DAG 依赖 + 三层 + 横切主题 + 案例层；骨架主轴 = **生命周期 × 三层「非对称矩阵」** |
| 3 | **层间依赖倒置**：`technology --implements--> methodology --derives_from--> essence`；**内层不得引用外层**；横切主题用属性 + 染色，**不建跨层边** |
| 4 | 信源 ID = **全局重编号单一命名空间**（414 old_id → **253 canonical**）；`sources[]` 只能引 `03-knowledge-map/canonical-sources.json` |
| 5 | 交付形态 = **完整双轨 + 多视图**（节点页 / 组页 / 分层视图 / 学习路径 / 决策矩阵 / 跨体系对照 / 案例视图 / **书籍↔节点对照** / 术语表 / 交互 DAG + MD 镜像 + 根索引） |
| 6 | **版权红线（刚性）**：书籍/标准正文只入**私有语料层**；**公开库只承载消化重组后的知识与自研脚本**；长引一律移出（≤200 字短引须逐条标源） |
| 7 | 公开仓名 = `zako-mio/se-architecture-methodology-kg`（**PUBLIC**，默认分支 `main`）；Pages = `https://zako-mio.github.io/se-architecture-methodology-kg/` |
| 8 | 许可 = **MIT License**（Copyright (c) 2026 zako-mio） |
| 9 | 视觉基调 = **母库文档页用浅色 Codex；交互 DAG 总览保持暗色** |
| 10 | 12factor = **独立演进的子库，不内联**；母库仅以 `cross_reference` + **绝对 URL 深链**引用（映射见 `MISSION_ROOT/16-checkpoint/xref-12factor.json`） |
| 11 | 检索层 D2 = **预留接口不建**（用户已多次选择挂起） |
| 12 | 建库方式 = 复用 12factor 生成链并重构为「数据/渲染解耦」通用框架（`16-checkpoint/`，**仅 Python 标准库**） |
| 13 | 门控 = **kb-construction L1–L8 + 方法论专项四项 + 回放四硬指标**（L4 视觉 / L8 版式 / **G-V 核验**） |
| 14 | **内容逐字保真**：生成链**不得改写数据**；正文/边标签/案例/勘误一律取数据作者层原文，禁止在生成步骤改写/编造/推断性归类。（⚠️ 阶段2 的改写发生在**数据作者层 `_parts/`**，与生成链逐字搬运**不冲突**——见 §B.3#3） |
| 15 | 生成链**完全幂等且不含时间戳** → CI 用 `git diff --exit-code` 做漂移检测 |
| 16 | 语言：中文为主，保留英文标准名/术语 |

### B.2 阶段7 阶段1 决策（ADR，均已采纳且过 `gate_architecture.py` 6/6）

| # | 决策 |
|---|---|
| 17 | **ADR-001（方案 A）**：**私有核验层为唯一真相源**（`MISSION_ROOT/01-books/_verify/`）；节点与信源表的 `verified`/`confidence`/`review_date`/`errata` **一律由确定性派生脚本生成，禁手改**；「**无锚点升级**」判 **FAIL** |
| 18 | **版权粒度**：**章节级结构锚**（BK 号 + 章/节编号与标题 + 强度 + 方向 + 日期）**可进公开层**；**页码区间与原文摘句仅留私有层** |
| 19 | **ADR-002（方案 A）**：证据模型 = **主张级四级强度** `direct/partial/inferred/contradicted` + **双向**（`forward` 正向回验 / `reverse` 反向发现）；拆原子主张 `definition` 1 条 + `detail` 四段各 ≥1 条 + 每条 `errata` 1 条，**单节点主张上限 8 条** |
| 20 | **升级判据**：`≥1 条 direct` **且** `0 条 contradicted`；出现 `contradicted` → 阻止升级并产 `errata` |
| 21 | **指标解耦**：核心主判据保留「可溯源率」；新指标「**直接锚定覆盖率**」**只报告不判** FAIL/WARN（连续谱无二值依据） |
| 22 | **阅读策略 = 分层混合**：正向目标按节点主张经 TOC/索引定位章节精读；无正向目标的书先做 TOC + 术语 + 关键词**全书扫描定位**再精读命中段 |
| 23 | **质检 = 单路核验 + 程序化回盘 + 高风险项（`direct` 升级 / `contradicted`）第二路独立复核 + 主Agent 抽检**（实测必要，FP 率 18.75%） |
| 24 | **派生作用域 = 增量式**：只动「被已核验书覆盖」的节点；未覆盖节点**保持原值** |
| 25 | **交付边界 = 全链路含公开层**（核验层 → 派生 → 门控 → 本地重生 → 公开投影 → 推公开仓/Pages） |
| 26 | **公开呈现 = C-lite**：`14-views/06-book-verification.html` 对照视图 + 节点页既有 `§信源与核验` 区块内加**一行**章节锚 |

### B.3 阶段7 阶段2 决策（**本窗口必须执行，2026-09-11 用户逐项裁决**）

| # | 决策 | 含义（执行口径） |
|---|---|---|
| 27 | **范围与顺序 = 先窄后宽** | 本轮只做 3 本 pilot 覆盖节点；剩余 27 本核验另立批次，之后再对新覆盖节点批量增密 |
| 28 | **落点形态 = 改写深化五段**（不扩 schema、不新增小节） | 只改 `definition` + `detail.{principle,mechanism,engineering,tradeoff}`；**禁**新增字段/区块/视图 |
| 29 | **SSOT 回写口径** | 段级 claim 锁定**强制**（每段 ≥1 claim；改写引入的实质新表述**必新增 ledger claim** + anchor + 第二路复核）；**无新事实时豁免**；句级映射降级为**抽检 WARN**；改写前先跑 **claim 完整性前置核查** |
| 30 | **生产拓扑 = 两段式** | ① 按书并行「证据展开」（只写各自证据分片，**不改正文**）② 按节点设**唯一写入方**综合改写五段 |
| 31 | **增密强度 = 双驱动** | 目标区间 **2400–3000 字**（上限不破契约 3000）+ **注水比机检**（每 +200 字 ≥1 条 claim 支撑） |
| 32 | **交付边界 = 全链路含公开层** | 与阶段1 同构；推送须走 GitHub Git Data API |
| 33 | **9 个无 `direct` 锚节点本轮排除** | 保持原值不动，写遗留清单；G-D5 硬拦越界 |
| 34 | **门控 = 双脚本按域拆分** | 新建 `gate_densify.py`（G-D1..G-D5）+ 扩 `gate_verification.py`（G-V9） |
| 35 | **公开呈现 = 零新增元素** | 正文变厚即成果；节点页锚行与 06 视图维持现状（内容可因新增 claim 微调） |
| 36 | **质检 = 双层复核** | ① 新增 claim 全部第二路独立复核（判强度）② 每节点成稿后「正文 vs 证据素材」保真复核（判越界）+ 主Agent 抽检 ≥20% |
| 37 | **本轮（上一窗口）只出方案文档** | 已在上一窗口完成；**本窗口转为执行** |
| 38 | **阶段3 不入上一轮**；Reflection 队列留给用户 `/reflection` | 阶段3 待阶段2 实测回收后再规划；阶段2 与阶段3 会改同一批节点，**顺序刚性** |

> **决策 14 与决策 28 的关系（务必理解，防误判违规）**：决策 14 约束的是**生成链不得改写数据**；本轮改写发生在**数据作者层 `_parts/*.json`**，生成链仍逐字搬运改写后的数据，故不违反决策 14。

---

## C. 当前进度（全部实测）

### C.1 阶段状态

| 阶段 | 状态 | 产物 |
|---|---|---|
| 阶段1–4 | ✅ | 契约、思路对齐、权威知识地图、证据包 A–R（14 包）、架构设计主文档、数据模型规范、ID 迁移（414→253） |
| 阶段5 | ✅ | 母库 **167 节点 / 360 边 / 18 组 / 18 案例**；门控 L1–L7 + 方法论四项全过 |
| 阶段6 | ✅ | 内容版式重构（浅色 Codex）、版权分级审计与脱敏公开集、L4/L8 实装、公开仓 + Pages + Actions 上线 |
| 遗留处理轮 | ✅ | Actions 大版本升级（Node 20 警告归零）+ L4 重叠探针改造（14 WARN → 0） |
| 阶段7 · 阶段1（核验升级） | ✅ | 核验层（144 记录 / 28 缺口）、ADR-001/002、派生链与两处根因修复、G-V1..G-V8、C-lite 公开投影、报告双版本 |
| **阶段7 · 阶段2（内容增密）方案** | ✅ | `stage7-phase2-content-densification-plan.md`（454 行 / 9 节 / `accepted`）+ `report-phase7p2-plan.{md,html}`（门控 5/5） |
| **阶段7 · 阶段2（内容增密）执行** | ✅ **已完成并上线**（2026-10-11） | 26 节点正文 1501–1813 → **2423–2998 字**；45 条新 claim；G-D 5/5 + G-V 9/9 + L2/L3/L6/L7/L8/方法论全 PASS；推送 `560236a7`；CI success；Pages 200。**基线见 `00-plan/stage7p2-baseline.md`** |
| **阶段7 · 阶段3（结构扩展）** | ⏳ **下一窗口** | 需先补 **ADR-004**（新节点 ID 分配与组归属）并过 `gate_architecture.py`；缺口清单 28 条（10 条 direct 具备准入资格） |

### C.1.1 阶段2 执行要点（供下一窗口承接）

- **新指纹**：`865e6a3d649281930b80107e8348f420ed51eb650be75f17e8a96fedbef4e915`（`methodology-dag.json`）。
- **新增脚本**（`16-checkpoint/`，均已提交）：`derive_densify.py` / `gate_densify.py` / `merge_densify.py` /
  `assemble_write_docs.py` / `register_densify_claims.py` / `check_corpus_overlap.py` /
  `negative_test_densify.py` / `gen_densify_briefs.py` / `push_publish.py`。
- **ADR-003**：主张上限 8→16（阶段2 参与节点），已过 `gate_architecture.py` **6/6**。
- **关键环境事实（本轮实测，纠正旧记录）**：
  1. 子 Agent **无任何 shell**（不可跑 `python3`），但**有 `write`/`edit`**。
  2. 🔴 **子 Agent 的字数自证系统性虚高 40–70%**——三轮 20+ 工人自报 2400–2900，
     机器实测恒为 1186–2048。**教训：计数权必须收回主Agent**（用 `assemble_write_docs.py --check`），
     工人只写文本、不自报数字。这是本轮唯一可靠的协作模式。
  3. `write` 工具**不截断**（`bytes/chars = 3.00` 整，CJK 完整）——旧「大负载截断」判断**已证伪**。
  4. 子 Agent **并发上限 5**（用户约束）。
- **G-V9 已收敛**：只对**阶段2 新增记录**（`VR-D2-` 前缀）的 claim_id 冲突判 FAIL；
  阶段1 遗留重复（`ESS-O-02#principle#1` = VR-CA-030 + VR-DDIA-009）报 **WARN**，待另案修复。
- **待办遗留**：① 轨B 剩余 27 本核验（价值排序已实测：T1 = `BK-025`46 / `BK-008`37 / `BK-030`31 /
  `BK-011`23 / `BK-026`22；其中 `BK-030` `BK-011` 已有抽文本，零解析成本）；② 阶段3 需 ADR-004；
  ③ 阶段1 遗留重复 claim_id 修复。

### C.2 上一窗口（阶段2 方案）交付

- **方案文档**：`MISSION_ROOT/00-plan/stage7-phase2-content-densification-plan.md`（454 行 / 32.5KB / 9 节；含 `[COMPLEXITY: 18/20]`；零本机路径；头部状态 = `accepted`）。
- **留档报告**：`MISSION_ROOT/report-phase7p2-plan.md` + `report-phase7p2-plan.html`（5 段完整；`16-checkpoint/gate_report.py` **R1–R5 全 PASS 5/5**，md/html 小节数 22/22）。
- **定稿变更**：方案文档头状态 `draft` → `accepted`。
- ⚠️ **尚未 `git commit`**：工作树有 3 个 untracked 文件（方案文档 + 报告 md/html），本窗口收尾时应一并提交本地归档仓。

### C.3 公开交付（在线，实测）

- **公开仓**：`zako-mio/se-architecture-methodology-kg`（PUBLIC，默认分支 `main`）
  - 远端 HEAD = `7ad556f8`；本地 `_publish/` HEAD = `187baf1`
  - 本地受控文件 **533**；`PUBLISH-STATE.json` `file_count = 527`（期望集），另有 preserve 专有件
- **CI（rebuild workflow）最近 run（全部 success）**：
  | run id | 说明 |
  |---|---|
  | `34596436302` | 阶段7 核验层公开投影 + 06 视图批次 |
  | `34598149779` | 阶段7 报告公开 + `gate_report.py` 批次 |
- **Pages**：首页 / 节点页 / 组页 / 术语表 / MD 镜像 / 交互图 / `14-views/06-book-verification.html` / `report-phase7.html` / `00-plan/stage7-*.md` 均 HTTP **200**
- **12factor 姊妹仓**：`zako-mio/12-factor-methodology-kg`（默认分支 **master**，Pages built）

> ⚠️ **新增公开件声明（本窗口必做）**：`16-checkpoint/publish-manifest.json` 的 `classes.sanitize` **只显式列了 `report-phase7.md` / `report-phase7.html`**。
> `00-plan/` 在 sanitize 类内（故新方案文档自动放行），但**新增的 `report-phase7p2-plan.md` / `report-phase7p2-plan.html` 未被声明 → 默认拒绝**。
> 推送前必须把这两个路径**显式加入 `classes.sanitize`**，再 `--apply` + 门控 + 推送（**改 manifest 必然需要重新 `--apply`**）。

### C.4 数据规模（实测真值）

- `MISSION_ROOT/10-dag-data/methodology-dag.json` = **167 节点 / 360 边 / 18 组 / 18 案例 / 3 横切主题**；`dag_acyclic=true`（Kahn 167/167）；孤立节点 0
- 分层：`essence` **51** + `methodology` **67** + `technology` **31** + `case`（`layer=null`）**18**
- 域分布：F13 · G17 · H16 · I14 · J17 · K17 · L14 · M14 · N13 · O14 · X18(cases)
- canonical 信源 **253**（BK 38）
- 节点 `verified`：**布尔 `true` 149 / 字符串 `"cited"` 18**；`confidence`：`high` 151 / `medium` 16
- 节点 `review_date`：`2026-09-10` × 132 / **`2026-09-11` × 35**（阶段7 核验覆盖节点）
- 节点正文长度 **1501–1813 字**（中位数 1536，均值 1566）；契约区间 **1500–3000 字**
- `meta.generated` / `meta.updated` = **`2026-09-11`**（`_base.json` 冻结常量，**禁运行时钟**）

### C.5 数据指纹

| 值 | SHA-256 |
|---|---|
| **当前（阶段7 阶段1 基线，本窗口起点）** | `9ae4cc01f7b183f9a621997896a9033af6d9ca9ed38fee462077d8604496eba1` |
| 上一版（阶段5 冻结起） | `58a7e3c397dc772344d71d8f98dd107ad5ac54a607bcea956a6a8994a258a390` |
| **本窗口执行后** | **会再次一次性变更** → 须重设基线（见 §K.3） |

### C.6 核验层现状（阶段2 的输入，实测）

- `verification-ledger.json` = **144 记录**：`direct 78 / partial 59 / inferred 7 / contradicted 0`；`forward 120 / reverse 24`；第二路 `passed 78 / disputed 18 / none 48`
- 覆盖 **35 节点**：**26 个有 `direct` 锚**（本轮参与）、**9 个仅 partial/inferred**（本轮排除）
- `node-claim-map.json` = **18 节点 / 120 条主张**；⚠️ **26 个参与节点中有 9 个（reverse-only，各 1 条记录）尚无主张拆分** → 这是步骤 0 前置核查的**必需项**，不是优化项
- `reverse-gaps.json` = **28 条**：`coverage_hole 10 / concept_missing 10 / missed_citation 8`（阶段3 输入，本轮只读不用）
- 三本 pilot 语料：DDIA = `MISSION_ROOT/01-books/_files/P0-11/ddia-zh-src/`（26 个中文全文 MD）+ `P0-11_ddia-2nd-en.epub`；CleanArch = `MISSION_ROOT/01-books/_verify/_text/clean-architecture.txt`（536KB）；SAiP = `MISSION_ROOT/01-books/_verify/_text/saip.txt`（1069KB）

### C.7 门控基线（阶段1 实测；**执行前建议复跑确认**）

| 层 | 阶段1 实测值 | 结论 |
|---|---|---|
| **L1** 分片自验证 | 23 个分片（22 `_parts/*.json` + `_base.json`）`errors=0` | PASS |
| **L2** 全图审计 | `nodes=167 edges=360 kahn=167/167 errors=0 warnings=0` | PASS |
| **L3** 结构 + 断链 | structure **427** / 问题 **0**；links **5189** / 问题 **0** | PASS |
| **L4** 视觉 | **272 项 / 212 PASS / 0 FAIL / 0 WARN / 60 SKIP** | PASS |
| **L5** 渲染 | **7 用例全 PASS**；`skipped=0`；JS 错误 0；悬空端点 0 | PASS |
| **L6** 覆盖度 | manifest **365/365 = 100%**；GR-09 11/31 = 35.48% ≥30% | PASS |
| **L7** 信源 | canonical 引用 1446；悬挂 **0**；可溯源 **100%**；`verified=true` **89.22%** | PASS |
| **L8** 版式 | 综合覆盖率 **2128/2128 = 100.00%**，问题 **0** | PASS |
| **方法论专项** | 层边界 / 术语一致（disputed 4，漏标 0）/ 原则↔反例 36/36 / 11 维权衡 11/11 | **4/4 PASS** |
| **G-V1..G-V8** | 无锚点升级 0；枚举违规 0；`anchor` 违规 0；改写红线命中 **0**；编码 17 文件 0 问题；`derive --check` 幂等；对账 **35/35** | PASS |

> **CI 中 L4/L5/G-V（及新增 G-D）显式 SKIPPED**（标准 runner 缺 Pillow/numpy/agent-browser，且公开侧无私有核验层）**且绝不伪装 PASS**；推送前须本地补跑。
> **L4 唯一历史 WARN**（术语表超宽表格容器内滚动）属版式契约明确允许的行为，**不是缺陷**。
> **SVG 标签叠字**：用户已明确决定**保留不修**。
> **L4 瞬态白页**：观察到 L4 FAIL **先重跑一次确认**（`agent-browser` 偶发渲染纯白会污染结论）。

---

## D. 目录与关键文件

```text
MISSION_ROOT/
├── 00-plan/                          # 契约与设计（必读）
│   ├── contract.md / 01-alignment.md / stage2-search-plan.md
│   ├── stage4-architecture-design.md / stage4-data-model.md
│   ├── stage5-build-contract.md / stage6-baseline.md / stage6-content-ia-spec.md（含 C-lite 版式契约）
│   ├── stage7-book-absorption-plan.md         # 三阶段总计划（阶段1 可执行 + 2/3 接口）
│   ├── **stage7-phase2-content-densification-plan.md**  # ★★ 本窗口执行依据（454 行 / accepted）
│   ├── stage7-baseline.md                     # 阶段7 阶段1 基线（指纹/输入 SHA-256/纠偏/门控表）
│   ├── **stage7p2-baseline.md**               # ★ 本窗口收尾须新建（阶段2 执行后基线）
│   ├── NEXT-SESSION-HANDOFF.md                # ★ 本文件
│   ├── id-migration-plan.md / id-migration-report.md / id-mapping.json / dag-schema.example.json
│   └── diagrams/stage4-architecture.{drawio,png}
├── 01-books/                         # 书单与获取日志（元数据层）
│   ├── gap-request.md / D-book-candidates.json / fetch-log.md / free-official-extracts.json
│   ├── _files/                       # ★ 语料本体（30 本 / 75 文件 / 290MB；**私有，三重隔离**）
│   │   └── P0-11/ddia-zh-src/        # ★ DDIA 26 个中文全文 MD（阶段2 证据展开用）
│   ├── _meta/                        # 采集契约 / 门控 / 来源解析
│   └── _verify/                      # ★★ 核验层（**私有 SSOT**）
│       ├── _meta/verify-contract.md
│       ├── _parts/{ledger,claims,toc,gaps}-<slug>.json   # slug ∈ ddia/clean-architecture/saip
│       ├── verification-ledger.json / node-claim-map.json / book-toc-index.json / reverse-gaps.json
│       ├── _review/secondpass-*.json                 # 第二路独立复核
│       ├── _text/{clean-architecture,saip}.txt       # EPUB 抽文本（改写红线机检用）
│       └── **_densify/**                             # ★★ 本窗口新建（私有中间层，见 §E.3）
│           ├── densify-contract.md
│           ├── precheck-coverage.json
│           ├── evidence-{ddia,clean-architecture,saip}.json
│           ├── write-<node_id>.json
│           └── paragraph-claim-map.json / densify-report.json
├── 02-research/                      # 证据包 A–R（14 包）+ C-local-inventory.json
├── 03-knowledge-map/                 # canonical-sources.json（253 主表）/ knowledge-map / glossary / sources-index / topic-source-matrix
├── 10-dag-data/                      # ★ 建库数据（单一权威图）
│   ├── methodology-dag.json          # 唯一权威图（aggregate.py 产出，禁手改）
│   ├── node-content.json / stats.md  # 派生镜像与统计
│   ├── _base.json / _parts/          # 骨架 + 22 分片（**阶段2 正文写回点；子Agent 禁直写**）
│   ├── _verification-baseline.json   # 阶段7：阶段7 前冻结基线（**禁覆盖**）
│   ├── _verification-overrides.json  # 阶段7：派生覆盖集（aggregate.py 应用）
│   └── book-verification.json        # 阶段7：核验的公开安全投影
├── 11-node-pages/                    # 167 节点页（§1–§11 + 内联关系 SVG；35 个含「书证核验」锚行）
├── 12-groups/                        # 18 组页 + 组总索引（共 19 页）
├── 13-interactive/                   # 交互 DAG 总览（暗色）
├── 14-views/                         # 8 视图（01-layer / 02-learning-path / 03-decision-matrix /
│                                     #   04-cross-mapping / 05-cases / 06-book-verification / glossary / index）
├── 15-md/                            # MD 镜像（nodes/ 167 + 索引；35 个节点含书证锚行）
├── 16-checkpoint/                    # ★ 生成链 + 门控 + 审计（唯一构建入口）
│   ├── build.py / config.py / gen_common.py / aggregate.py
│   ├── gen-{nodes,groups,views,md,index,interactive,glossary}.py
│   ├── validate_graph.py / _base_extract.py
│   ├── kb_gate.py(L3) / gate_render.py(L5) / gate_coverage.py(L6) / gate_sources.py(L7)
│   ├── gate_layout.py(L8) / gate_visual.py(L4) / gate_methodology.py / gate_migration.py
│   ├── gate_verification.py（G-V1..G-V9）/ derive_verification.py
│   │   └─ **本窗口须新增 G-V9**；**须新增 derive_densify.py + gate_densify.py（G-D1..G-D5）**
│   ├── gate_report.py（报告 HTML 5 段门控 R1–R5）
│   ├── audit_publish.py / assemble_publish.py / publish-manifest.json / deliverables.json
│   ├── gate_disclosure.py / disclosure-allowlist.txt / xref-12factor.json / opc-mapping.json
│   └── _render-shots/（L4/L5 渲染产物）
├── 18-design/                        # 设计过程档案（cand-A/B/C、ADR；**不公开**）
│   └── adr/                          # ADR-001/002（json+md）+ matrix.md + matrix-ADR-002.md
├── 20-agent-skill/                   # architecture-judgment 能力包
├── _backup-idmigration/              # ID 迁移回滚备份（勿删；不公开）
├── _publish-staging/                 # 脱敏中间产物（不公开）
├── _publish/                         # ★★ 公开集组装目录（独立 git 仓，533 文件；只能经 assemble_publish.py 写入）
├── ARCHIVE-INDEX.md                  # 产物索引 + 验收状态（留档，不入公开仓）
├── report.md / report.html           # 阶段1–6 报告
├── report-phase7.md / report-phase7.html            # 阶段7 阶段1 报告
├── **report-phase7p2-plan.md / .html**              # ★ 阶段2 方案周期报告（门控 5/5）
├── quality-gate.md / index.html
└── .gitignore                        # 本地仓：`01-books/`、`02-research/`、`_publish/`、18-design 截图等
```

> **数据流向**：
> ① `10-dag-data/{_base.json + _parts/*.json}` --aggregate.py（**应用 `_verification-overrides.json`**）--> `methodology-dag.json` --build.py--> `11–15 + index.html`
> ② `01-books/_verify/_parts/*-<slug>.json` --derive_verification.py--> 4 件 SSOT + `_verification-overrides.json` + `book-verification.json`
> ③ **阶段2 新增**：`_verify/_densify/evidence-*.json` + `write-*.json` --主Agent 合并--> `_parts/ledger-*.json` + `10-dag-data/_parts/*.json`（正文）--derive_densify.py--> `paragraph-claim-map.json` + 对账报告
> 子Agent 只写自己的 `_densify/` 分片与 `write-<node_id>.json`；**主Agent 是唯一写入方**（负责 ledger 分片与正文分片）；**禁手改生成物**。

---

## E. 数据契约要点（刚性，违者门控不过）

### E.1 图谱侧（阶段5 沿用）

**节点字段**：`id / name / en / aliases / type / subtype / group / layer / domain / stage / priority / definition / detail{principle,mechanism,engineering,tradeoff} / cross_cutting[] / case[] / sources[] / verified / confidence / review_date / status / version / deprecated_at / superseded_by / errata[] / tags / entry_links`

| 契约项 | 规则 |
|---|---|
| **节点 ID** | `^(ESS\|MTH\|TEC\|CAS)-[A-Z]{1,2}-\d{2}$`；案例域固定 `CAS-X-XX` |
| **信源 ID** | `^(STD\|OFF\|BK\|WEB\|VEN\|PAP\|COM\|LOC\|XCV)-\d{3}$`（253 canonical） |
| **边 ID** | `^E-\d{2,3}$`，**上限 `E-999`**；新增边前先扫已用区间 |
| **边字段** | **`from` / `to`**（非 `source`/`target`）、`id`/`type`/`label`/`directed`/`weight`/`sources` |
| **五段式** | `definition`（15–300 字）+ `detail.{principle,mechanism,engineering,tradeoff}`；每节点正文 **1500–3000 字**（阶段2 参与节点须并入 **2400–3000** 区间） |
| **反例/权衡** | 每节点必带 ≥1 权衡或反例（GR-13）；`type=principle`/`case` 强制 `detail.tradeoff` |
| **`layer` 枚举** | `essence / methodology / technology`；`type:"case"`（`layer=null`，18 个） |
| **层间边方向** | **仅** `implements`（tech→method）/ `derives_from`（method→essence），单向、禁越级 |
| **`sources[]`** | ≥1，且必须能在 `canonical-sources.json` 解析（**零悬挂**） |
| **`technology`/`tool`** | 必填 `version` |
| **`essence` 层正文** | **禁出现工具名/版本号**（阶段2 改写后仍禁，方法论专项会重跑） |
| **`verified` 判定** | ⚠️ 取值有两种：布尔 `true`（149）与字符串 `"cited"`（18）；**必须用 `is True`（Python）/ `=== true` 严格判断**，真值判断会把 `"cited"` 误计为 true |

### E.2 核验层侧（阶段7 阶段1 新增，刚性）

| 契约项 | 规则 |
|---|---|
| **分片命名** | `_parts/{ledger,claims,toc,gaps}-<slug>.json`；slug 枚举固定 `ddia` / `clean-architecture` / `saip` |
| **`evidence_strength`** | **封闭枚举** `direct / partial / inferred / contradicted`（禁自由文本） |
| **`direction`** | `forward` / `reverse` |
| **`gap.kind`** | `missed_citation / coverage_hole / concept_missing` |
| **`claim`** | **必须为改写**（非引文）；与书原文**最长公共子串 ≤20 字** |
| **`anchor`** | 必填 `chapter`（可空**仅当** `inferred` 且书无章节结构） |
| **`page_anchor_private`** | `{"edition","pages"}`；**仅私有层，永不进公开投影** |
| **`contradiction`** | **当且仅当** `evidence_strength=="contradicted"` 时必填 `{verified_value, note}` |
| **`_single_node_claim_cap`** | **每节点主张上限 8 条**（含阶段2 新增） |
| **升级判据** | `≥1 direct` **且** `0 contradicted`；**无锚点升级即 FAIL** |
| **派生规则（增量式）** | 有 `contradicted` → 不升级 + errata；否则有 `≥1 direct` → `verified=true`/`confidence=high`；否则**保持基线原值**；`review_date` = 该节点记录 `review_date` 最大值 |
| **公开投影白名单** | 仅 `source_id/book/chapter/section/section_title/evidence_strength/direction/second_pass/review_date`；缺口仅 `gap_id/kind/book_source_id/chapter/section/target/summary/proposed_action/evidence_strength` |
| **确定性** | 脚本**无时间戳**（禁 `datetime.date.today()` / `time.time()`）；输出按稳定键排序；`json.dump(ensure_ascii=False, indent=2)` + 末尾换行 |

### E.3 阶段2 增密层（**本窗口新建，私有**）

**`_verify/_densify/densify-contract.md`** —— Build 第一件事：把下列字段与枚举固化为机读契约。

**`evidence-<slug>.json`（① 按书证据素材分片）**

```json
{
  "meta": { "schema_version": "1.0.0", "book_source_id": "BK-009", "slug": "saip",
            "review_date": "<冻结常量，禁运行时钟>", "note": "素材分片；只增不改既有账本" },
  "items": [
    { "evidence_id": "EV-SAIP-001", "node_id": "MTH-G-02", "origin": "mechanism",
      "claim_id": "MTH-G-02#mechanism#3", "is_new": false,
      "text": "<改写素材：机制/权衡/反例说明，非引文，与书原文最长公共子串 ≤20 字>",
      "anchor": { "chapter": "5", "section": "5.2", "section_title": "<取自 book-toc-index.json>" },
      "proposed_strength": "direct", "read_scope": "<本次读了哪些章节/页段>" }
  ]
}
```

**`write-<node_id>.json`（② 按节点改写稿，唯一写入方产出）**

```json
{
  "node_id": "MTH-G-02",
  "segments": { "definition": "<改写后正文>", "principle": "...", "mechanism": "...",
                "engineering": "...", "tradeoff": "..." },
  "provenance": { "definition": ["EV-SAIP-001"], "principle": ["..."], "mechanism": ["..."],
                  "engineering": ["..."], "tradeoff": ["..."] },
  "new_claims": [ { "claim_id": "MTH-G-02#mechanism#3", "text": "<改写，≤20 字子串>",
                    "anchor": { "chapter": "5", "section": "5.2", "section_title": "<...>" },
                    "evidence_strength": "direct", "direction": "forward" } ],
  "baseline_chars": 1519, "final_chars": 2530,
  "writer": "w-nodewriter-<batch>", "review_date": "<冻结常量>"
}
```

**字段硬约束**

| 项 | 规则 |
|---|---|
| `origin` | 封闭枚举 `definition / principle / mechanism / engineering / tradeoff / errata`（与 `claim_id` 命名同源） |
| `proposed_strength` / `evidence_strength` | 封闭枚举 `direct / partial / inferred / contradicted` |
| `claim_id` | `<node_id>#<origin>#<n>`，全局唯一稳定；复用既有者 `is_new=false` |
| `text` / `segments` | **必须为改写**；与书原文**最长公共子串 ≤20 字** |
| `anchor` | 必填 `chapter`；`section_title` 须能回溯 `book-toc-index.json` |
| 新增 claim | 必有 `anchor` + `direction` + 第二路复核结论，否则 **G-V9 FAIL** |
| 单节点主张上限 | ≤ **8 条**（ADR-002，含新增） |
| 确定性 | 无时间戳；排序稳定；`review_date` 用契约冻结常量 |

### E.4 三重隔离（缺一即违规）

1. **本地归档仓** `.gitignore`：`01-books/` 整体忽略 → `_densify/` 自动覆盖（**已实测**：`git check-ignore -v 01-books/_verify/_densify/evidence-saip.json` 命中 `.gitignore:13:01-books/`）
2. **公开仓** `_publish/.gitignore`：显式 `01-books/_verify/`
3. **装配层** `16-checkpoint/publish-manifest.json`：`classes.private` 含 `"01-books/_verify/"`，`private_probe` 含 `"01-books/_verify"`（**已实测**，`_densify/` 自动覆盖）
   > ⚠️ `01-books/` 属 **`sanitize` 类**（会被发布），故 `_verify/` 必须**显式**列入 private，**不得依赖父目录语义**。

---

## F. 阶段2 方案要点（执行前必读）

> 完整设计见 `MISSION_ROOT/00-plan/stage7-phase2-content-densification-plan.md`；此处只列执行口径。

### F.1 目标

用一手书证把 **26 个有 `direct` 锚节点**的五段正文，从当前 1501–1813 字深化到 **2400–3000 字**，且**每条新实质表述都可回溯到章节锚 + 强度 + 复核人**。

### F.2 26 个参与节点（**只写这些**）

- `essence`（14）：`ESS-G-01` `ESS-G-02` `ESS-G-04` `ESS-I-02` `ESS-K-02` `ESS-L-05` `ESS-M-01` `ESS-M-02` `ESS-M-03` `ESS-M-04` `ESS-M-05` `ESS-O-01` `ESS-O-02` `ESS-O-03`
- `methodology`（10）：`MTH-G-02` `MTH-G-03` `MTH-G-06` `MTH-M-01` `MTH-M-02` `MTH-M-03` `MTH-M-06` `MTH-O-03` `MTH-O-05` `MTH-O-09`
- `technology`（2）：`TEC-K-05` `TEC-M-03`

⚠️ 其中 **5 个被多本书共同覆盖**（`ESS-O-02` 三本；`ESS-M-03` `ESS-O-03` `ESS-I-02` `ESS-O-01` 各两本）→ 必须走两段式，防并发写冲突。
⚠️ 其中 **9 个为 reverse-only**（`ESS-G-04` `ESS-K-02` `ESS-L-05` `ESS-M-01` `ESS-M-02` `ESS-M-04` `ESS-O-01` `MTH-O-09` `TEC-K-05`）→ 步骤 0 前置核查须为其补齐五段主张集。

### F.3 9 个排除节点（**禁止改写**，写入遗留清单）

`CAS-X-02` `ESS-G-03` `ESS-G-07` `ESS-H-02` `ESS-K-01` `MTH-K-06` `MTH-O-10` `MTH-O-11` `TEC-K-01`

### F.4 两段式生产（DAG）

```text
[W0] 契约与骨架 + 步骤0 前置核查（主Agent 自办，串行）
      │
      ├─▶ [W1a] DDIA 证据展开（BK-023，18 记录）
      ├─▶ [W1b] CleanArch 证据展开（BK-007，30 记录）      ── 三路并行
      └─▶ [W1c] SAiP 证据展开（BK-009，96 记录）
                  │
                  ▼
      [W2] 节点综合改写（node-writer，按节点唯一写入方；26 节点分 7–9 批）   ── 分批并行
                  │
                  ▼
      [W3a] 新增 claim 强度第二路复核
      [W3b] 正文 vs 素材保真复核（不重读全书）                                ── 并行
                  │
                  ▼
      [W4] 主Agent 合并回写 + derive_verification + derive_densify + aggregate  ── 串行
                  │
                  ▼
      [W5] 门控实跑（gate_densify + gate_verification + L1–L8 + 方法论四项）   ── 串行（主Agent 亲跑）
                  │
                  ▼
      [W6] 重生 + 装配 + 推送 + Pages 复验 + CI 对账                            ── 串行
```

### F.5 新增门控（**必须实装并实跑**）

**`16-checkpoint/gate_densify.py`（G-D1..G-D5）**

| 判据 | 内容 | 层级 |
|---|---|---|
| **G-D1** | **段级 claim 覆盖非空**：26 节点 × 5 段 `provenance` 非空，且全部 `claim_id` 可在 ledger 解析（**零悬挂**） | FAIL |
| **G-D2** | **注水比**：`ceil(字数增量/200) ≤ 该节点 provenance 的 distinct claim 数` | FAIL |
| **G-D3** | **字数区间**：26 节点终稿 ∈ **[2400, 3000]**；全局契约 `[1500, 3000]` 不破 | FAIL |
| **G-D4** | **版权红线（新增！）**：**节点正文** vs 三书原文（`_text/clean-architecture.txt` / `_text/saip.txt` / `_files/P0-11/ddia-zh-src/*.md`）**最长公共子串 ≥20 字命中 = 0** | FAIL |
| **G-D5** | **对账**：变更节点集 **== 26 参与节点集**（遗漏 0 / 越界 0）；26 节点 `verified`/`confidence` **值不翻转**（`_evidence` 允许增加）；其余 141 节点零改动 | FAIL |

**`16-checkpoint/gate_verification.py` 新增 G-V9**

| 判据 | 内容 | 层级 |
|---|---|---|
| **G-V9** | **回写完整性**：阶段2 新增每条 claim 必有 `anchor` + `direction` + `second_pass ∈ {passed, disputed}`（不得 `none`）；`claim_id` 全局唯一；`origin` ∈ 封闭枚举 | FAIL |

**新增 `16-checkpoint/derive_densify.py`**（仅标准库、确定性、无时间戳）
- 输入：`_densify/write-*.json` + `verification-ledger.json` + `_verification-baseline.json`
- 产出：`_densify/paragraph-claim-map.json`（`{node_id: {segment: [claim_id...]}}` + 字数增量/注水比）+ `_densify/densify-report.json`（对账）

### F.6 生成链改动 = **最小化**

| 产物 | 改动 |
|---|---|
| `gen-nodes.py` / `gen-md.py` / `gen-views.py` / `deliverables.json` | **无改动**（正文来自数据层；无新页面 → L6 仍 365/365） |
| `10-dag-data/_verification-baseline.json` | **绝不覆盖**（阶段1 §F.4 根因防线） |

> 本轮是**数据层增密**，生成链只需重跑——这是决策 28（不扩 schema）与 35（零新增元素）的直接红利。

---

## G. 执行清单（本窗口主任务，可直接照做）

### G.1 前置（主Agent 自办，串行）

```bash
cd "$MROOT"
mkdir -p 01-books/_verify/_densify
git check-ignore -v 01-books/_verify/_densify/evidence-saip.json   # 须命中 .gitignore:13:01-books/
grep -n '01-books/_verify' 16-checkpoint/publish-manifest.json      # 须含 classes.private + private_probe
python3 16-checkpoint/derive_densify.py --precheck                  # 步骤0：26 节点 × 5 段主张覆盖
```

- [ ] 写 `_verify/_densify/densify-contract.md`（固化 §E.3 字段/枚举）
- [ ] 实作 `derive_densify.py` 的 `--precheck`（输出 `precheck-coverage.json`），标注 9 个 reverse-only 节点的补齐项

### G.2 生产（委派）

- [ ] W1a/W1b/W1c 三路并行证据展开（每路只写 `evidence-<slug>.json`）
- [ ] 主Agent 回盘抽检 W1 产物（素材是否越出锚点章节、`is_new` 标注是否可信）
- [ ] W2 按节点唯一写入方改写（7–9 批；每批次内节点互不重叠）
- [ ] W3a 新增 claim 第二路复核；W3b「正文 vs 素材」保真复核；分歧由主Agent 保守终裁
- [ ] 主Agent 对 `direct` 断言抽检 **≥20%**

### G.3 合并回写（主Agent，唯一写入方）

- [ ] 汇总 `new_claims` → 追加 `_verify/_parts/ledger-<slug>.json`
- [ ] `write-<node_id>.json` 的 `segments` → 写回 `10-dag-data/_parts/*.json`（对应节点）
- [ ] 运行 `derive_verification.py` → `derive_verification.py --check` → `derive_densify.py` → `derive_densify.py --check`
- [ ] `aggregate.py`（应用覆盖集）→ `aggregate.py && git diff --exit-code`（幂等自证）

### G.4 门控（主Agent 亲跑，**不得采信子Agent 自述**）

- [ ] `gate_densify.py --check all`（G-D1..G-D5 全 PASS）
- [ ] `gate_verification.py --check all`（G-V1..G-V9 全 PASS）
- [ ] `validate_graph.py`（errors=0、`dag_acyclic=true`、`sources[]` 零悬挂）
- [ ] L3（structure/links 问题 0）/ L6 / L7 / L8（**正文变长后必须回到 100%、问题 0**）
- [ ] 方法论四项（**重点：`essence` 层禁工具名/版本号不回归**）
- [ ] L4 / L5 本地补跑（FAIL 先重跑一次确认）

### G.5 公开层（见 §I.4–§I.6）

- [ ] **先在 `publish-manifest.json` 的 `classes.sanitize` 显式新增 `report-phase7p2-plan.md` / `report-phase7p2-plan.html`**
- [ ] `build.py` 重生 11–15 + index（幂等）
- [ ] `assemble_publish.py --check`（0/0/0 + P1–P5 OK）→ `--apply`
- [ ] `gate_disclosure.py` → `--export` → `--assert-clean`
- [ ] GitHub Git Data API 推送 → Pages 七类页面 200 复验 → CI `git diff --exit-code` 为空

### G.6 收尾（见 §K.3）

---

## H. 执行纪律与沙箱约束（实测，务必继承）

1. **`git push` 被沙箱禁止**（`git push *` = deny）→ 推送**必须**走 `gh` / **GitHub Git Data API**（`POST /git/blobs` → `/git/trees` → `/git/commits` → `PATCH /git/refs/heads/main`），做法见 §I.6。
2. **`python -c` 被禁止**（deny）→ 需要脚本时**写独立 `.py` 文件再执行**。**严禁 shell 内联管道写中文**（会截断 UTF-8 多字节）。
3. **`rm -rf` 被禁止** → 用 `rm -f`（逐个删）。
4. **子Agent 权限分层（实测）**：
   - `architect-worker` 的 `bash` 为**全禁**（仅放行 `git status`/`git diff`）→ **门控脚本必须由主Agent 亲跑**，不得采信其「手工模拟 PASS」
   - `general` 子Agent 继承全局 bash 规则（仅 `python -c` / `rm -rf` / `git push` 被禁）→ **可执行 `python3 script.py`**，适合脚本/解析/门控类任务
5. **CI 无法覆盖 L4 / L5 / G-V / G-D**（缺 Pillow / numpy / agent-browser + 公开侧无私有核验层）→ **必须在本地补跑**；`rebuild.yml` 中显式打印 SKIPPED 原因，**绝不伪装 PASS**。
6. **子Agent 自述必须回盘复验**：历史已多轮出现「全报 success 但独立复算修正结论」；本轮尤其要复算 **`write-*.json` 的字数与 provenance**、**`new_claims` 是否真的新增**（防「假回写」）。任何结论都要用**新鲜的一手数据**复算。
7. **生成链仅 Python 标准库且完全幂等**：全量生成物重跑后 `git diff` 为空。**新增脚本务必延续「无时间戳」约束**（`aggregate.py` 的时钟坑已修，勿回退）。
8. **单一真相源 + 派生 + 对账**：核验层是唯一真相源；派生「原值」**必须**来自 `_verification-baseline.json`（**冻结，不覆盖**），**禁止**从派生后的 dag 回读。
9. **本地归档仓**：阶段5 冻结基线 `e16244a`；阶段6 完成快照 `f4fc157`；阶段7 阶段1 = `3078693`；接力文档覆写 = `8ec6a41`；**上一窗口新增 3 文件尚未提交**。
10. **编码安全**：中文用 `edit`/`write`（勿用 shell echo/管道）；产出 **UTF-8 无 BOM、无 U+FFFD**；改 JSON 后必验合法性与零悬挂。
11. **命令与工具**：只读优先 `glob`/`grep`；不重复检索已采集内容；子Agent 提示词引用**短路径 + 生产简报**，禁内联长契约（防 JSON 截断）。
12. **Variant 继承**：复杂度沿用 **`[COMPLEXITY: 18/20]` → Deep**（**全程 Deep 推理**，不得重新评估）。
13. **装配不变量**：`assemble_publish.py --check` 必须 **0/0/0** 且 P1–P5 全 OK；**新增母库顶层文件必须在 `publish-manifest.json` 显式声明**（默认拒绝）；改 `publish-manifest.json` 必然需要重新 `--apply` + 重新推送。
14. **路径卫生（新增强调）**：`00-plan/` 与 `report-*.md/html` 都会进**公开 Pages** → 文档内**禁本机绝对路径**；跨窗口文档中的路径一律写**纯文本**（避免 L3 断链），不要写成 Markdown 链接指向不存在的文件。

---

## I. 命令清单（可直接复制）

> 设 `MROOT="$HOME/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"`；除注明外均在 `$MROOT/16-checkpoint/` 下执行。

### I.1 核验链 + 增密链

```bash
cd "$MROOT/16-checkpoint"
python3 derive_verification.py --check         # 幂等自证
python3 derive_densify.py --precheck           # 步骤0：26 节点 × 5 段主张覆盖
python3 derive_densify.py                      # paragraph-claim-map + 对账报告
python3 derive_densify.py --check              # 幂等自证
python3 aggregate.py                           # 应用覆盖集 → 权威主图（勿手改输出）
python3 aggregate.py && git -C "$MROOT" diff --exit-code   # 幂等自证
```

### I.2 重建 / 数据校验

```bash
cd "$MROOT/16-checkpoint"
python3 build.py --config mother --quiet        # 全量重建 11–15 + index.html（幂等，无时间戳）
python3 validate_graph.py --graph ../10-dag-data/methodology-dag.json \
  --canonical ../03-knowledge-map/canonical-sources.json
python3 validate_graph.py --shard ../10-dag-data/_parts/W1-M.json \
  --canonical ../03-knowledge-map/canonical-sources.json
```

### I.3 门控（L1–L8 + 方法论四项 + G-V + G-D）

```bash
cd "$MROOT/16-checkpoint"
# L3 结构 + 断链（母库口径；问题数须为 0）
python3 kb_gate.py --root "$MROOT" --layers structure,links \
  --exclude _backup-idmigration --exclude 02-research --exclude 01-books \
  --exclude 03-knowledge-map --exclude 00-plan --exclude 16-checkpoint \
  --exclude _publish --exclude 18-design --exclude .github
python3 gate_densify.py --check all              # G-D1..G-D5（本地）
python3 gate_verification.py --check all         # G-V1..G-V9（本地）
python3 gate_visual.py --check all               # L4（本地；CI SKIPPED）
python3 gate_render.py --timeout 25              # L5（本地；CI SKIPPED）
python3 gate_coverage.py
python3 gate_sources.py
python3 gate_layout.py --check all
python3 gate_methodology.py --check all
python3 gate_report.py --input ../report-phase7p2-plan.html --md ../report-phase7p2-plan.md
```

### I.4 公开集侧门控（在 `$MROOT/_publish/` 下）

```bash
cd "$MROOT/_publish"
python3 16-checkpoint/build.py --config mother --quiet
git diff --exit-code                            # 漂移检测：必须为空
python3 16-checkpoint/validate_graph.py --graph 10-dag-data/methodology-dag.json \
  --canonical 03-knowledge-map/canonical-sources.json
python3 16-checkpoint/kb_gate.py --root . --layers structure,links \
  --exclude 02-research --exclude 01-books --exclude 03-knowledge-map \
  --exclude 00-plan --exclude 16-checkpoint --exclude .github --quiet
python3 16-checkpoint/gate_layout.py --check all
python3 16-checkpoint/gate_coverage.py
python3 16-checkpoint/gate_sources.py
python3 16-checkpoint/gate_methodology.py --check all
python3 16-checkpoint/gate_report.py --input report-phase7p2-plan.html --md report-phase7p2-plan.md
python3 16-checkpoint/gate_verification.py --check all    # 应 SKIPPED
python3 16-checkpoint/gate_densify.py --check all         # 应 SKIPPED
```

### I.5 装配与推送

```bash
cd "$MROOT"
python3 16-checkpoint/assemble_publish.py --check          # 须 0/0/0 + P1–P5 OK
python3 16-checkpoint/assemble_publish.py --apply          # 预检后落盘
python3 16-checkpoint/gate_disclosure.py --root "$MROOT/_publish"
python3 16-checkpoint/assemble_publish.py --export "$MROOT/_pages-export"
python3 16-checkpoint/assemble_publish.py --assert-clean "$MROOT/_pages-export"
# 临时导出目录用后删除
```

### I.6 公开集推送（沙箱禁 `git push` → GitHub Git Data API）

```bash
cd "$MROOT/_publish"
OWNER=zako-mio; REPO=se-architecture-methodology-kg; BRANCH=main
gh auth status

PARENT=$(gh api repos/$OWNER/$REPO/git/ref/heads/$BRANCH --jq '.object.sha')
BASE_TREE=$(gh api repos/$OWNER/$REPO/git/commits/$PARENT --jq '.tree.sha')
# 用**独立 .py 脚本**（标准库 + subprocess 调 gh api）遍历 `git ls-files`：
#   逐文件 POST /git/blobs (encoding=base64) → 组装 tree.json（path/mode/type/sha）
#   gh api repos/$OWNER/$REPO/git/trees -f base_tree=$BASE_TREE --input tree.json --jq '.sha'
#   gh api repos/$OWNER/$REPO/git/commits -f message='...' -f tree=$NEW_TREE -f parents[]=$PARENT --jq '.sha'
#   gh api -X PATCH repos/$OWNER/$REPO/git/refs/heads/$BRANCH -f sha=$NEW_COMMIT -F force=false
# 回验：远端 tree 文件数 == 本地 `git ls-files | wc -l`；`gh run list --limit 3` 确认 success
```

**API 推送踩坑**：
- `force=false` 时非快进会被拒；必须把工作区**全部**受控文件纳入 tree（含 `.nojekyll`、`.github/`、`PUBLISH-STATE.json`），否则远端会领先
- 二进制走 base64 blob；推送后用 `gh api repos/$OWNER/$REPO/git/trees/main?recursive=1 --jq '.tree|length'` 对账（注意该计数含目录对象）

### I.7 本地归档提交（仅本地仓，**不推送**）

```bash
cd "$MROOT"
git add -A && git commit -m "<scope>: <description>"
git log --oneline -3
```

---

## J. 待用户决策 / 需要用户提供

| # | 事项 | 选项 | 默认 |
|---|---|---|---|
| 1 | 节点写入方的批大小 | 3 / 4 / 6 节点每批 | **4** |
| 2 | 是否需要用户本人参与 `direct` 抽检 | 需要 / 仅主Agent 抽检 | **仅主Agent** |
| 3 | 剩余 27 本核验是否本轮并行启动 | 并行 / 阶段2 后 | **阶段2 后**（决策 27） |
| 4 | 阶段3（结构扩展）是否启动 | 启动 / 等阶段2 后 | **等阶段2 后**（决策 38） |
| 5 | 检索层 **D2（FTS5）** 是否启用 | 启用 / 继续挂起 | **挂起** |
| 6 | **12factor 反向深链**（子库 → 母库） | 做 / 不做 | **不做** |
| 7 | **SVG 标签避让** | 做 / 保持现状 | **保持现状（用户已决定不修）** |
| 8 | 是否放行 `git push` 权限以简化推送 | 放行 / 继续走 API | **继续走 API** |
| 9 | Reflection 提案审阅（`/reflection`） | 现在审 / 稍后 | **稍后**（队列 waiting 2） |
| 10 | 上一窗口 3 个未提交文件是否随本轮一并提交 | 一并 / 分开 | **一并提交** |

> **无需用户提供材料**：三本 pilot 语料已全部落私有层，阶段2 无外部依赖。

---

## K. 验收标准与收尾

### K.1 验收判据（**无新鲜验证证据不得声称完成**）

- **结构**：UTF-8 无 BOM、无 U+FFFD；内部断链 0；JSON 全合法
- **数据**：`validate_graph.py` errors=0；`dag_acyclic=true`；`sources[]` 零悬挂；**变更集 == 26 节点**
- **增密**：26 节点终稿字数 ∈ [2400, 3000]；每段 prompt 依据非空；注水比达标；`paragraph-claim-map.json` 零悬挂
- **核验层**：`gate_verification.py` **PASS 9/9**；「无锚点升级」= 0；新增 claim 均可回溯「章节锚 + 强度 + 复核人」
- **门控**：`gate_densify.py` **PASS 5/5**；L1–L8 + 方法论四项全 PASS；`skipped` 必须显式记录且 **`skipped ≠ PASS`**
- **版权红线**：**正文** ≥20 字子串命中 0；公开层无 `claim`/页码/摘句；公开面无本机路径
- **幂等**：`build.py` / `aggregate.py` / `derive_verification.py` / `derive_densify.py --check` 连跑稳定
- **页面可达性**：Pages 首页 / 节点页 / 组页 / 术语表 / MD 镜像 / 交互图 / 06 视图 均 HTTP 200
- **装配**：`assemble_publish.py --check` 0/0/0 且 P1–P5 OK；新增报告已声明进 `sanitize`
- **CI**：`git diff --exit-code` 漂移检测为空；最近 run success；L4/L5/G-V/G-D 注明 SKIPPED
- **报告**：双版本（`.md` + `.html`，过 `gate_report.py` 5/5，5 段完整）

### K.2 验收后须重设的基线

- 记录新 `methodology-dag.json` SHA-256
- 新建 `MISSION_ROOT/00-plan/stage7p2-baseline.md`（新指纹 + 输入 SHA-256 + 门控表 + 纠偏记录）
- 同步 CI 预期（若 `rebuild.yml` 内嵌指纹则更新）

### K.3 任务结束时的收尾动作（必做）

1. **清理** `/tmp` 及临时目录残留（脚本、日志、中间 JSON、导出目录）。
2. **本地归档提交**（含上一窗口遗留的 3 个文件）→ `git log --oneline -3` 记录。
3. **Mission 留档询问**（`question` 工具）；如留档，双版本（AI 友好 `.md` + 可读 `.html`，HTML 过 `gate_report.py` 5/5），5 段完整（当时情况 / 制定计划 / 执行情况 / 完成情况 / 反思·分析·建议）。
4. 按协议封装 **Reflection 4 层**（A: GATE+COMPLEXITY+决策 / B: 子Agent 回报+聚合 / C: MEMORY.md 快照 / D: 报告），追加 `~/opencode/archive/Reflection/pending.json`（`status=waiting`，**仅主Agent**，fire-and-forget）。
5. 若产出新公开件：**先在 `publish-manifest.json` 显式声明**，再 `--apply` / 门控 / 推送 / 对账。
6. 任务完成后**更新本接力文档**（覆写为“阶段2 已完成”版，供下一窗口接续阶段3）。
