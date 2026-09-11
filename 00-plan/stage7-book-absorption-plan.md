# 阶段7 · 参考书吸收与知识库融合（计划）

> 母任务：0910-软件工程架构方法论 ｜ 生成日期：2026-09-11 ｜ 生成人：主Agent（Plan 周期）
> 状态：**已定稿（accepted）** —— 2026-09-11 经用户裁决「定稿并执行」；ADR-001 / ADR-002 同步转 `accepted`
> 前置产物：`18-design/adr/ADR-001.{json,md}`、`18-design/adr/ADR-002.{json,md}`、`18-design/adr/matrix.md`、`18-design/adr/matrix-ADR-002.md`（两份 ADR 均经 `gate_architecture.py --kind adr` 实测 **6/6 PASS**）
> 复杂度：`[COMPLEXITY: 19/20]` → Deep 推理深度（Build 阶段须沿用，不得重新评估）
> 路径约定：`MISSION_ROOT = ~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论`

---

## 1. 当时情况

- **母任务状态**：阶段1–6 已全部完成并上线（母库 167 节点 / 360 边 / 18 组 / 18 案例；公开仓 `zako-mio/se-architecture-methodology-kg` + Pages + Actions 全绿）。
- **参考书语料状态**：30 本 paid/user-copy 经典著作已于 2026-09-11 全部采集落盘至**私有语料层** `01-books/_files/`（75 文件 / 290MB；含 35 PDF + 13 EPUB + DDIA 26 个中文全文 MD），并配套 `acquired-manifest.json` / `download-log.md`（私有清单）。
- **核心缺口（用户原始诉求）**：**知识库先建成、参考书后到位**——图谱（2026-09-10 前）与信源表在书籍语料落盘前即已定稿。现有 167 节点中 **106 个引用 BK 信源**（BK 引用合计 159 处），但节点自身的 `verified`（布尔 `true` 149 / 字符串 `"cited"` 18）与 `confidence`（`high` 151 / `medium` 16）**全部来自公开线索、官方目录与作者博客的间接核验，从未读过书籍正文**。即：**当前"已验证"是名义状态，不是书证状态。**
- **用户诉求原话语义**：「之前下载了部分书目，在知识库完成后，还未吸收参考书中内容，故需要计划吸收参考书并融入知识库。」
- **环境约束**：`methodology-dag.json` 指纹 `58a7e3c397dc772344d71d8f98dd107ad5ac54a607bcea956a6a8994a258a390`（阶段5 冻结以来未变）；生成链仅 Python 标准库、幂等、无时间戳；CI 用 `git diff --exit-code` 做漂移检测；沙箱禁 `git push`（公开仓推送须走 GitHub Git Data API）。

---

## 2. 目标与范围

### 2.1 总目标（三阶段）

| 阶段 | 名称 | 一句话 |
|---|---|---|
| **阶段1** | **核验升级** | 用书籍正文对图谱的存量 BK 引用做**主张级书证核验**，产出可审计的章节锚、勘误与缺口清单，并把核验结论**确定性派生**回图谱状态字段 |
| **阶段2** | **内容增密** | 以核验层的主张锚为定位，用一手书证深化节点 `definition` / `detail` 四段 / `errata` |
| **阶段3** | **结构扩展** | 以反向发现的缺口清单为输入，新增节点 / 边 / 组，修补覆盖盲区 |

### 2.2 本次范围（用户裁决）

- **阶段1 详细到可执行粒度**（数据契约、脚本、门控、委派、验收、回滚全定）。
- **阶段2 / 阶段3 只留接口与准入契约**，不展开实现；待 pilot 实测数据（FP 率、工时、指标实测值）回收后再行规划。

### 2.3 pilot 范围（用户裁决）

3 本，覆盖两个方向与两种格式：

| 书 | 语料 | 正向核验目标 | 方向 | 格式/可行性 |
|---|---|---|---|---|
| **DDIA**（`P0-11`，BK-023） | 26 个中文全文 MD（1.9MB） | **0** | **反向发现**（书→图谱） | 最高（纯 MD） |
| **Clean Architecture**（`P0-02`，BK-007） | EPUB（89 万字符） | **3**（ESS-G-01、ESS-G-02、CAS-X-02） | 正向 + 反向 | 高（EPUB 可解压抽文） |
| **Software Architecture in Practice**（`P0-04`，BK-009） | EPUB（150 万字符） | **15** | 正向 + 反向 | 高（EPUB） |

> 说明：DDIA 在现图谱中正向引用为 **0**（既无节点 `sources[]`，也无 errata），因此它是**纯反向发现样本**；CleanArch 与 SAiP 承担正向核验吞吐验证（3 + 15 = 18 个目标节点）。

---

## 3. 已定决策（ADR 摘要，门控已过，勿重新决策）

### 3.1 ADR-001 · 核验结果的落盘层（方案 A，已采纳）

- **私有核验层为唯一真相源**（SSOT）：记录 节点 ↔ 信源 ↔ 章节锚 ↔ 证据强度 ↔ 复核元数据。
- 节点与信源表的 `verified` / `confidence` / `review_date` / `errata` **一律由确定性派生脚本生成**，**禁手改生成物**；派生脚本对「**无锚点升级**」判 **FAIL**。
- **版权粒度裁定**：**章节级结构锚**（BK 号 + 章/节编号与标题 + 证据强度 + 处理日期）**可经脱敏门控进公开层**；**页码区间与原文摘句仅留私有层**。
- 依据：`MTH-O-10` 增量演化与一致性治理、`ESS-L-03` 架构侵蚀与漂移、`MTH-L-05` 架构适应度函数、`ESS-F-03` 需求可追溯性与可验证性、`ESS-O-02` 架构即权衡、`ESS-H-01` 信息隐藏、`MTH-G-01` 架构决策记录。
- 权重矩阵：A 4.28 > B 3.72 > C 3.02 > D 2.20；B/C 因「保留未与书证联动的公开 verified → 双真相」否决，D 因「页码/摘句进公开图谱 → 触版权红线」否决。

### 3.2 ADR-002 · 核验证据模型（方案 A，已采纳）

- **主张级四级强度 + 双向**：
  - 拆原子主张：`definition` 1 条 + `detail` 四段各 ≥1 条 + 每条 `errata` 1 条，**单节点上限 8 条**（封顶成本）。
  - 强度为**封闭枚举**：`direct`（书中明确支持）/ `partial`（支持部分要素或需一步推断）/ `inferred`（概念相关但书未直陈）/ `contradicted`（与书相悖）。
  - 方向 `direction`：`forward`（回验存量引用）/ `reverse`（发现应引未引、覆盖缺口）。
- **节点升级判据**：`≥1 条 direct` **且** `0 条 contradicted`；出现 `contradicted` 即产出 `errata` 并阻止升级。
- **指标解耦**：核心主判据保留「可溯源率」（现状 100%）；新指标「**直接锚定覆盖率**」**只报告不判** FAIL/WARN。
- 依据：`ESS-O-02`、`ESS-F-03`、`MTH-L-05`、`MTH-I-06` 质量门控、`ESS-O-01`、`MTH-O-03` 够用原则、`ESS-L-03`、`MTH-O-10`、`MTH-G-02`、`ESS-H-01`、`MTH-G-01`。
- 权重矩阵：A 3.92 > D 3.51 > B 3.10 > C 3.07；D 因「不驱动升级」、C 因「无法定位到哪句话被支持」否决。

### 3.3 其余已定决策（本计划轮收敛）

| # | 决策 |
|---|---|
| 1 | 阅读策略 = **分层混合**：正向目标按节点主张经 TOC/索引定位章节精读；DDIA 先做 TOC + 术语 + 关键词**全书扫描定位**，再对命中段精读 |
| 2 | 质检 = **单路核验 + 程序化回盘 + 高风险项（direct 升级 / contradicted）第二路独立复核 + 主Agent 抽检** |
| 3 | 交付边界 = **全链路含公开层**（核验层 → 派生 → 门控 → 本地重生 → 公开投影 → 推公开仓/Pages） |
| 4 | **派生作用域 = 增量式**：只动「被已核验书覆盖」的节点；未覆盖的 100+ 节点保持原值不动 |
| 5 | 公开呈现 = **C-lite**：新建 `14-views/06-book-verification.html` 对照视图 + 节点页既有 `§信源与核验` 区块内加**一行**章节锚（不新增整块） |

### 3.4 跨 ADR 相互修正（必须记录）

ADR-002 把「GR-10 崩塌（严格 direct-only 下 pilot 仅 18/167 = 10.78%，全量理论上界 106/167 = 63.47%）」列为最大风险。但决策 3.3#4 的**增量式回写**消解了该风险：未覆盖节点的 `verified` 原值不动，`verified=true` 占比不降反微升（`CAS-X-02` 由 `"cited"` → `true`），**GR-10 的 ≥80% 继续成立**。因此指标解耦由「必需」降级为「**防御性预留**」；若后续阶段2/3 转为全量重算，必须启用解耦。

---

## 4. 阶段1 设计（可执行粒度）

### 4.1 架构总览（数据流）

```text
01-books/_files/                 (私有语料：PDF / EPUB / MD)
        │  分层混合阅读（3 路核验）
        ▼
01-books/_verify/                (私有核验层 = SSOT)
   ├── verification-ledger.json  (核验记录主表)
   ├── node-claim-map.json       (节点 → 原子主张拆分表，claim 为改写)
   ├── book-toc-index.json       (书 TOC / 章节索引，供锚点与导航)
   ├── reverse-gaps.json         (反向发现缺口清单 → 阶段3 输入)
   └── _meta/verify-contract.md + gate_verification.py
        │  derive_verification.py（确定性、无时间戳）
        ▼
10-dag-data/_verification-overrides.json   (派生覆盖集，仅含被覆盖节点)
        │  aggregate.py 应用覆盖（含日期坑修复）
        ▼
10-dag-data/methodology-dag.json  ──build.py──▶ 11/12/13/14/15 + index.html
        │                                          （含新视图 06 + 节点页章节锚行）
        ▼
16-checkpoint/{gate_verification, gate_layout, gate_sources, ...}  (门控)
        ▼
assemble_publish.py → _publish/ → GitHub Git Data API 推送 → Pages
```

### 4.2 核验层契约（proposed schema）

**`verification-ledger.json`**

```json
{
  "meta": { "schema_version": "1.0.0", "generated": "2026-09-11", "source_of_truth": true,
            "note": "核验层为唯一真相源；节点/信源表状态一律由此派生，禁手改" },
  "records": [
    {
      "record_id": "VR-0001",
      "node_id": "ESS-G-02",
      "source_id": "BK-007",
      "direction": "forward",
      "claim_id": "ESS-G-02#definition#1",
      "claim": "<改写摘要（非引文），与书原文最长公共子串 ≤20 字>",
      "anchor": { "chapter": "5", "section": "5.2", "section_title": "<章节标题>" },
      "page_anchor_private": { "edition": "1st/2017", "pages": "[72-78]" },
      "evidence_strength": "direct",
      "evidence_note": "<改写说明为何判为该强度>",
      "review": { "reviewed_by": "<subagent-id>", "review_date": "2026-09-11",
                  "second_pass": "none|passed|disputed", "second_pass_by": null }
    }
  ]
}
```

**`reverse-gaps.json`**（同时是阶段3 接口）

```json
{ "meta": { "schema_version": "1.0.0" },
  "gaps": [
    { "gap_id": "GAP-0001", "kind": "missed_citation|coverage_hole|concept_missing",
      "book_source_id": "BK-023",
      "anchor": { "chapter": "5", "section": "5.3", "section_title": "<...>" },
      "target": { "existing_node_id": "ESS-K-02", "proposed_node": null },
      "summary": "<改写摘要>", "proposed_action": "<建议：补引 / 新增节点 / 新增边>",
      "evidence_strength": "partial" } ] }
```

**字段硬约束**

| 项 | 规则 |
|---|---|
| `evidence_strength` | 封闭枚举 `direct/partial/inferred/contradicted`，禁自由文本（机检依据） |
| `claim` | **必须为改写**；与书原文最长公共子串 **≤20 字** |
| `anchor.chapter` | 非空；`section` 可空；`section_title` 取自书 TOC |
| `page_anchor_private` | **仅私有层**，永不进公开投影 |
| 升级记录 | `direct` 且触发升级者，必须同时具备 `anchor` 与 `direction`（「无锚点升级即 FAIL」） |
| `record_id` / `claim_id` | 全局唯一、稳定、可对账 |

### 4.3 落盘路径与隔离（**硬约束**）

- 核验层落 **`01-books/_verify/`**（私有）。
- **三重隔离同步**（缺一即违规）：
  1. 本地归档仓 `.gitignore`：`01-books/` 已整体忽略 → `_verify/` **自动覆盖**（需 `git check-ignore -v` 实测确认）。
  2. 公开仓 `_publish/.gitignore`：显式新增 `01-books/_verify/`。
  3. 装配层 `16-checkpoint/publish-manifest.json`：`classes.private` 新增 `"01-books/_verify/"`，`private_probe` 同步新增 `"01-books/_verify"`。
  > ⚠️ **关键**：`01-books/` 在装配清单中属 **`sanitize` 类**（会被发布），故**不能**依赖父目录语义，必须把 `_verify/` **显式**列入 `private`；否则核验层会被当作可脱敏件装配进公开仓。
- 跨阶段落盘补充：本地 `~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论/` 目录整体为归档仓，核验层随母库本地提交（**不推送**）。

### 4.4 阅读与核验流程（分层混合）

1. **建书 TOC 索引**（`book-toc-index.json`）：DDIA 由 `toc.md` + 章节标题提取；EPUB 由 nav/`toc.ncx`/XHTML 标题提取。
2. **拆主张**（`node-claim-map.json`）：对 18 个正向目标节点，按 §3.2 规则拆原子主张（≤8 条/节点），claim 文本为改写。
3. **正向核验**（CleanArch / SAiP）：主张 → TOC/索引/关键词定位候选章节 → 精读候选段 → 定强度 + 取章节锚。
4. **反向发现**（DDIA，及 CleanArch/SAiP 顺带）：
   - 先以 TOC + 术语表 + 关键词做**全书扫描**，产出「概念 ↔ 章节」候选映射；
   - 与现图谱概念集对账，产出三类 gap：`missed_citation`（该节点应引此书而未引）、`coverage_hole`（书中有而图谱无节点）、`concept_missing`（术语/概念缺口）；
   - 对命中段精读后定强度。
5. **高风险项第二路复核**：所有 `direct` 升级记录与全部 `contradicted` 记录，交**第二路独立子Agent**重判（不告知首路结论），主Agent 终裁分歧。
6. **抽检**：主Agent 对 `direct` 记录按 ≥20% 抽样回盘读锚点上下文。

### 4.5 委派分工（DAG）

```text
[W1] 契约与骨架（核验层 schema + 目录 + 三重隔离）        ── 前置，串行
      │
      ├─▶ [W2a] DDIA 反向发现（reading-worker）
      ├─▶ [W2b] CleanArch 正向+反向（reading-worker）      ── W2a/W2b/W2c 三路并行
      └─▶ [W2c] SAiP 正向+反向（reading-worker）
                  │
                  ▼
      [W3] 高风险项第二路复核（verifier-worker，独立视角）
                  │
                  ▼
      [W4] 派生脚本 derive_verification.py + aggregate 接入 + 日期坑修复   ── 串行
                  │
                  ▼
      [W5] 生成链改造（gen-views 06 + gen-nodes 锚行 + deliverables.json + L8 契约） ── 串行
                  │
                  ▼
      [W6] 门控实跑（新增 gate_verification + L1–L8 + 方法论四项）      ── 串行
                  │
                  ▼
      [W7] 公开层装配 + 推送（assemble_publish → Git Data API → Pages 复验） ── 串行
```

- 极简单步（如 `git check-ignore` 验证）由主Agent 自办，不委派。
- 每个写文件的子Agent 须遵循「**同域隔离 + 唯一写入方**」：`_verify/` 只由 W2a/W2b/W2c 各写自己的分片文件（如 `ledger.ddia.json`），由主Agent（或聚合脚本）合并为 `verification-ledger.json`，避免并发写同一文件。
- **委派 prompt 必须含**：角色路径/描述、Skill 清单、必读参考文件短路径（契约外置文件，防 prompt 过长截断）、交付契约、返回 JSON 格式、`⛔ 无 GATE 自评`。
- 子Agent 自述**一律回盘复验**（本项目历史已 3 次抓出误判，含一次主Agent 错误否定前序结论）。

### 4.6 派生机制

**新增 `16-checkpoint/derive_verification.py`**（仅标准库，确定性，无时间戳）：

- 输入：`01-books/_verify/verification-ledger.json`
- 输出：`10-dag-data/_verification-overrides.json`，结构 `{ node_id: { verified, confidence, review_date, errata[], _evidence: [record_id...] } }`
- 派生规则（增量式，对应决策 3.3#4）：

```text
for 每个被核验层覆盖的 node_id:
    若 存在 contradicted 记录:
        不升级；errata 追加 {misconception, verified_value, source_id}
        （若该节点原 verified=true 且 contradicted 命中其核心主张 → 降级为 false，并记入变更报告）
    否则若 存在 ≥1 direct 记录:
        verified = true；confidence = high
    否则:
        保持原值（partial/inferred 不驱动升级）
    review_date = 取该节点最新 record.review.review_date（多记录取最大，稳定排序）
未被覆盖的节点: 完全不写（保持原值）
```

**`16-checkpoint/aggregate.py` 改动**：

1. 在分片合并后、写盘前，**应用 `_verification-overrides.json`**（若文件不存在则跳过，保持向后兼容）。
2. **修掉日期坑**：现有第 308/337 行 `meta["updated"] = datetime.date.today().isoformat()` 使重聚合**跨日即改 SHA**（实测：现文件 `meta.updated = "2026-09-10"`，今日重聚合会变为 `2026-09-11`，破坏「幂等 + 无时间戳」口径）。修法：`meta.generated` / `meta.updated` 改从 `_base.json` 的**冻结常量**读取（或显式声明为 `"2026-09-11"` 基线值），并新增**「连跑两次 aggregate.py，`git diff --exit-code` 为空」**的幂等自证。
3. 上述改动会使 `methodology-dag.json` 指纹**一次性变更**（用户已接受），须同步**重设阶段基线**（见 §4.9）。

### 4.7 生成链与公开投影改造（C-lite）

| 产物 | 改动 |
|---|---|
| `16-checkpoint/gen-views.py` | 新增生成器分支产出 `14-views/06-book-verification.html`（书籍 ↔ 节点对照矩阵：行=BK 信源，列=节点或按域分区；格=强度/方向徽标；含「覆盖与缺口」区块） |
| `14-views/index.html` | 入口卡片新增 06 |
| `16-checkpoint/gen-nodes.py` | 在既有 `§信源与核验` 区块内**追加一行**：`书证锚：BK-007 Ch5.2（direct）`（仅章节级；**不含页码/摘句**） |
| `16-checkpoint/deliverables.json` | 新增 06 视图条目并调 `expected` 计数（现覆盖度 363/363 → 相应 +1） |
| `15-md/` | 按既有双轨规则补 `06` 对应 MD 镜像（与 HTML 块标题对齐） |
| `16-checkpoint/deliverables` / `manifest` 对账 | 更新 `_publish/PUBLISH-STATE.json`（经 `assemble_publish.py --apply` 再生，禁手抄） |
| `00-plan/stage6-content-ia-spec.md` | 追加 C-lite 版式契约（节点页锚行样式 + 06 视图块序列），供 L8 门控读取 |

> 生成物**延续幂等、无时间戳**约束；新增视图与节点页锚行必须可由脚本全量复现（CI `git diff --exit-code` 检测）。

### 4.8 门控设计

**新增 `16-checkpoint/gate_verification.py`**（本地跑；CI 缺私有核验层，显式 **SKIPPED** 且**绝不伪装 PASS**，沿用 L4/L5 口径）：

| 判据 | 内容 |
|---|---|
| **G-V1** | 核验层 JSON 合法 + schema 必填齐全 |
| **G-V2** | `evidence_strength` ∈ 封闭枚举；`direction` ∈ {forward, reverse} |
| **G-V3** | 每条记录 `anchor.chapter` 非空；`section_title` 非自由文本拼凑（须能回溯 `book-toc-index.json`） |
| **G-V4** | **无锚点升级 = 0**：所有触发升级的记录必须具备 `anchor` + `direction` |
| **G-V5** | `claim` 改写检查：与书原文**最长公共子串 ≤20 字**（EPUB/MD 可精确；PDF 抽取文本后近似，假阴性记 WARN） |
| **G-V6** | 编码：UTF-8 无 BOM、无 U+FFFD |
| **G-V7** | **幂等**：`derive_verification.py` 连跑两次产物逐字节一致；`aggregate.py` 连跑两次 `git diff` 为空 |
| **G-V8** | **对账**：被覆盖节点集合 == 派生变更集合（无遗漏、无越界） |

**既有门控同步**：

- **L2**（`validate_graph.py`）：节点 schema 未变，应继续 PASS；如 `errata` 新增项触发校验，需同步 schema 说明。
- **L7**（`gate_sources.py`）：BK 条目 `verified`/`confidence` 升级后重跑，零悬挂 / 可溯源率 100% 须维持。
- **L8**（`gate_layout.py`）：新增 06 视图 + 节点页锚行后，综合覆盖率须回到 100%、问题 0。
- **方法论四项**：层边界、术语一致、原则↔反例、权衡矩阵四项须重跑。
- **GR-10**：**增量式下继续保持 ≥80%**；「直接锚定覆盖率」**只报告不判**（ADR-002 决策）。

### 4.9 验收判据（pilot 完成口径）

- **结构**：UTF-8 无 BOM / 无 U+FFFD；内部断链 0；JSON 全合法。
- **数据**：`validate_graph.py` errors=0；`dag_acyclic=true`；`sources[]` 零悬挂；**变更集可对账**（仅被覆盖节点发生变化）。
- **核验层**：`gate_verification.py` **PASS**；「无锚点升级」= 0；每条升级记录可回溯到 章节锚 + 强度 + 复核人。
- **产出三件套**：
  1. **章节锚**：18 个正向目标节点全部产出核验记录（含未命中者，标注 `inferred`/无锚）；
  2. **勘误**：所有 `contradicted` 转化为 `errata`（附 list）；
  3. **缺口**：DDIA（及另两本）反向发现 `reverse-gaps.json` 非空，三类 gap 均有样本。
- **质检**：高风险项第二路复核完成，分歧率与终裁记录留档；主Agent `direct` 抽检 ≥20%。
- **门控**：L1–L8 + 方法论四项全 PASS（L4 允许「仅自动判据 PASS / 并入 VLM WARN」）；新增 G-V1–G-V8 全 PASS。
- **公开层**：06 视图与节点页锚行渲染正确；L8 覆盖率 100%；版权扫描无正文/页码/长引残留；公开面本机路径命中 0。
- **CI**：`git diff --exit-code` 为空；最近 run success；L4/L5/G-V 显式 SKIPPED。
- **报告**：核验统计（强度分布、方向分布、覆盖节点数、`contradicted` 数、gap 数）+ FP 抽检结果。

### 4.10 回滚与基线重置

- **基线与指纹**：本阶段会**一次性变更** `methodology-dag.json` 指纹（含日期坑修复的副作用）。须在完成后**重设阶段基线**：记录新 SHA-256、更新 `00-plan/stage6-baseline.md`（或新增 `stage7-baseline.md`）、同步 CI 预期。
- **回滚路径**：撤销 `_verification-overrides.json` 与生成物提交，恢复指纹 `58a7e3c3…` 基线；**私有核验层原样保留**（不回滚，避免重复劳动）。
- **回滚触发条件**：①派生无法在无时间戳下保持幂等；②章节锚公开被判越版权红线；③FP 抽检 >10% 且两轮校准无效。

---

## 5. 阶段2 / 阶段3 接口预留（不展开实现）

### 5.1 阶段2（内容增密）接口

- **消费**：`verification-ledger.json` 的 `claim_id` / `anchor` / `direction`；`node-claim-map.json` 的主张拆分。
- **冻结契约**：`claim_id` 命名规则（`<node_id>#<origin>#<n>`，`origin ∈ {definition, principle, mechanism, engineering, tradeoff, errata}`）、`anchor` 结构、`evidence_strength` 枚举。
- **准入**：内容增密改写必须能指向 ≥1 条已有锚点；新增表述须回写核验层（保持 SSOT）。
- **门控预留**：增密后正文长度（现 1501–1813 字）与「essence 层禁工具名/版本号」判据不回归。

### 5.2 阶段3（结构扩展）接口

- **消费**：`reverse-gaps.json`（`gap_id` / `kind` / `target` / `proposed_action`）。
- **准入契约（proposed）**：新增节点须满足 **≥1 条 `direct` 锚 + ≥2 个相互独立信源**；新增边须具备 `sources[]` 且不违反层间边方向（仅 `implements` / `derives_from`，单向、禁越级）。
- **门控预留**：新节点仍受 `^(ESS|MTH|TEC|CAS)-[A-Z]{1,2}-\d{2}$` ID 规则、边 ID `^E-\d{2,3}$`（上限 `E-999`）、`sources[]` ≥1 且零悬挂约束。
- **规模影响**：阶段3 会突破「167 节点」，届时 `deliverables.json` / `node-index.md` / `routing.md` / `cheatsheet.md` / `20-agent-skill` 需同步再生。

---

## 6. 风险与对策

| # | 风险 | 等级 | 对策 |
|---|---|---|---|
| 1 | **FP**（LLM 把「只说相关」判成 `direct`，抬高公开 `verified`） | 高 | 封闭枚举 + `≥1 direct 且 0 contradicted` 判据 + 高风险项第二路独立复核 + 主Agent 抽检 ≥20%；抽检 FP >10% 触发回滚条件 |
| 2 | **FN**（书确有而漏判，覆盖率系统性偏低） | 中 | 反向发现 + 抽样回检校正；`inferred` 与 `partial` 允许记录但不驱动升级，避免为覆盖率注水 |
| 3 | **幂等破坏**（派生脚本引入运行时钟 / 非稳定排序） | 高 | 冻结常量 + 稳定排序；G-V7 连跑两次字节一致；**已知 `aggregate.py` 日期坑，本阶段一并修复** |
| 4 | **版权越线**（claim 摘要接近原文；页码/摘句外泄） | 高 | G-V5 最长公共子串 ≤20 字；页码仅私有；公开投影只含章节级元数据；`gate_disclosure.py` 兜底 |
| 5 | **核验层误入公开仓**（`01-books/` 属 `sanitize` 类） | 高 | 显式加入 `publish-manifest.json` 的 `private` + `_publish/.gitignore` + `private_probe`；装配后跑 `--check` 与 `~` 命中 = 0 |
| 6 | **子Agent 并发写同一文件** | 中 | 分片写入（每路写自己的 ledger 分片），主Agent/聚合脚本合并；「唯一写入方」原则 |
| 7 | **子Agent 自述不实** | 中 | 一律回盘复验；门控实跑由主Agent 执行（子Agent 沙箱禁 python3，历史已两次出现「手工模拟 PASS」） |
| 8 | **主张粒度膨胀**（detail 每段 400–600 字） | 中 | 单节点主张上限 8 条 |
| 9 | **pilot 升级产出小**（`cited` 节点全为 CAS-X-*，仅 `CAS-X-02` 命中 CleanArch） | 低 | 已向用户明示：pilot 主产出是「章节锚 + 勘误 + 缺口清单」，非 `verified` 翻转 |
| 10 | **`agent-browser` 渲染瞬态白页**污染 L4/L5 | 低 | 观察到 FAIL 先重跑一次确认；建议顺带加「白页自动重试一次」 |

---

## 7. 执行清单（Build 阶段可直接复制）

> 设 `MROOT="$HOME/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"`

### 7.1 前置（隔离与骨架）

```bash
cd "$MROOT"
# 1) 核验层目录与契约
mkdir -p 01-books/_verify/_meta
# 2) 三重隔离验证（本地仓）
git check-ignore -v 01-books/_verify/verification-ledger.json
# 3) 公开仓隔离（改 publish-manifest.json 后）
grep -n '01-books/_verify' 16-checkpoint/publish-manifest.json
```

### 7.2 核验与派生

```bash
cd "$MROOT/16-checkpoint"
python3 derive_verification.py                       # 核验层 → _verification-overrides.json
python3 derive_verification.py --check               # G-V7 幂等自检
python3 aggregate.py                                 # 应用覆盖 + 日期坑修复
python3 aggregate.py && git -C "$MROOT" diff --exit-code   # 幂等自证
```

### 7.3 重生与门控

```bash
cd "$MROOT/16-checkpoint"
python3 build.py --config mother --quiet
python3 validate_graph.py --graph ../10-dag-data/methodology-dag.json \
  --canonical ../03-knowledge-map/canonical-sources.json
python3 gate_verification.py --check all             # 新增 G-V1..G-V8
python3 kb_gate.py --root "$MROOT" --layers structure,links \
  --exclude _backup-idmigration --exclude 02-research --exclude 01-books \
  --exclude 03-knowledge-map --exclude 00-plan --exclude 16-checkpoint \
  --exclude _publish --exclude 18-design --exclude .github
python3 gate_coverage.py && python3 gate_sources.py
python3 gate_layout.py --check all && python3 gate_methodology.py --check all
python3 gate_visual.py --check all                   # L4（本地；CI SKIPPED）
python3 gate_render.py --timeout 25                  # L5（本地；CI SKIPPED）
```

### 7.4 公开层装配与推送

```bash
cd "$MROOT"
python3 16-checkpoint/assemble_publish.py --check          # 对账 0/0/0
python3 16-checkpoint/assemble_publish.py --apply          # 预检 P1–P5 后落盘
python3 16-checkpoint/gate_disclosure.py                   # 披露门控
python3 16-checkpoint/assemble_publish.py --export DIR --assert-clean DIR
# 推送：沙箱禁 git push → GitHub Git Data API（POST /git/blobs → /git/trees → /git/commits → PATCH /git/refs/heads/main）
```

### 7.5 收尾

1. 清理 `/tmp` 与临时目录残留。
2. Mission 留档询问（question）→ 双版本报告 `report-phase7.md` + `report-phase7.html`（HTML 过质量门控：UTF-8 无替换字符 / div 开闭平衡 / 5 段完整）。
3. 按协议封装 Reflection 4 层，追加 `~/opencode/archive/Reflection/pending.json`（status=waiting，**仅主Agent**，fire-and-forget）。

---

## 8. 待用户决策 / 待用户提供

| # | 事项 | 选项 | 当前状态 |
|---|---|---|---|
| 1 | 本计划文档是否定稿（转 accepted） | 定稿 / 修订 | **待审阅** |
| 2 | 是否在 pilot 完成后自动进入阶段2 | 自动 / 另立窗口 | 未决 |
| 3 | 是否需要用户本人参与 `direct` 抽检 | 需要 / 仅主Agent 抽检 | 未决 |
| 4 | 全量 30 本是否同法推进（15–30 工日量级） | 是 / 分批 / 暂缓 | 未决（阶段1 后） |

> **无需用户提供材料**：30 本书语料已全部落私有层，本阶段不再有外部依赖。

---

## 9. 附：本计划所依据的关键实测数据

| 指标 | 实测值 | 来源 |
|---|---|---|
| 图谱规模 | 167 节点 / 360 边 / 18 组 / 18 案例 | `10-dag-data/methodology-dag.json` |
| 图谱指纹 | `58a7e3c3…`（`sha256`，阶段5 起未变） | `sha256sum` |
| 节点 `verified` | 布尔 `true` 149 / 字符串 `"cited"` 18 | 脚本统计 |
| 节点 `confidence` | `high` 151 / `medium` 16 | 脚本统计 |
| 引用 BK 的节点 | 106 / 167（BK 引用合计 159 处） | 脚本统计 |
| 信源表 | 253 canonical（BK 38） | `03-knowledge-map/canonical-sources.json` |
| BK 信源 `verified` | `true` 18 / `"cited"` 15 / `false` 5 | 脚本统计 |
| DDIA 正向目标 | **0**（纯反向发现样本） | 脚本统计 |
| CleanArch 正向目标 | 3（ESS-G-01、ESS-G-02、CAS-X-02） | 脚本统计 |
| SAiP 正向目标 | 15 | 脚本统计 |
| `cited` 节点构成 | **全部为 CAS-X-\***（自研案例），仅 `CAS-X-02` 引 CleanArch | 脚本统计 |
| `aggregate.py` 日期坑 | 第 308/337 行 `datetime.date.today()` → 跨日重聚合改 SHA | 源码 + `meta.updated` 实测 |
| 语料规模 | 30 本 / 75 文件 / 290MB（35 PDF + 13 EPUB + 26 MD） | `01-books/acquired-manifest.json` |
