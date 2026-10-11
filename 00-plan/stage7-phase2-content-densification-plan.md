# 阶段7 · 阶段2 内容增密（计划）

> 母任务：0910-软件工程架构方法论 ｜ 生成日期：2026-09-11 ｜ 生成人：主Agent（Plan 周期 · grill-me 收敛，12 分支）
> 状态：**已定稿（accepted）** —— 2026-09-11 经用户裁决「定稿 + 出留档报告」；Build 周期另立窗口执行（勿在 Build 周期重新决策）
> 前置产物：`00-plan/stage7-book-absorption-plan.md`（三阶段总计划，§5.1 阶段2 接口）、`00-plan/stage7-baseline.md`、`18-design/adr/ADR-001.{json,md}` / `ADR-002.{json,md}`（均 accepted）
> 复杂度：`[COMPLEXITY: 18/20]` → Deep 推理深度（Build 阶段须沿用，不得重新评估）
> 上游传承：`[COMPLEXITY: 19/20]`（阶段7 阶段1）；本轮略降（无 ADR 新增选型，范围收敛至 26 节点）
> 路径约定（全文只在此处声明一次，正文一律写 `MISSION_ROOT/...` / `SUB_LIB_ROOT/...`，不含任何本机绝对路径）：
>
> ```text
> MISSION_ROOT = "~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"
> SUB_LIB_ROOT = "~/opencode/archive/Mission-file/2026-08/0823-12factor-methodology"
> ```

---

## 1. 当时情况

- **阶段7 阶段1（核验升级）已完成并上线**：私有核验层 `MISSION_ROOT/01-books/_verify/` 成为唯一真相源（SSOT），`derive_verification.py` 确定性派生、`gate_verification.py` 的 **G-V1..G-V8** 全 PASS；公开侧 C-lite 投影（`14-views/06-book-verification.html` + 节点页「书证核验」锚行）已推送，Pages 全 200。
- **现状实测**（本轮 Plan 周期回盘复验，2026-09-11）：
  - `MISSION_ROOT/10-dag-data/methodology-dag.json` 指纹 = `9ae4cc01f7b183f9a621997896a9033af6d9ca9ed38fee462077d8604496eba1`（与 `stage7-baseline.md` 一致）；
  - 本地归档仓 HEAD = `8ec6a41`（接力文档覆写），工作树干净；
  - 核验层 `verification-ledger.json` = **144 记录**（`direct 78 / partial 59 / inferred 7 / contradicted 0`；`forward 120 / reverse 24`；第二路 `passed 78 / disputed 18 / none 48`）；
  - 覆盖 **35 节点**，其中 **26 个持有 ≥1 条 `direct` 锚**（具备升级资格），**9 个仅 partial/inferred**（无 direct 支撑）；
  - `node-claim-map.json` = **18 节点 / 120 条主张**（`origin` 已按 definition/principle/mechanism/engineering/tradeoff/errata 拆分）；
  - `reverse-gaps.json` = **28 条**（`coverage_hole 10 / concept_missing 10 / missed_citation 8`）；
  - 节点正文长度 **1501–1813 字**（中位数 1536，均值 1566），契约区间为 **1500–3000 字**。
- **用户诉求**：阶段1 交付的是「章节锚 + 勘误 + 缺口清单」，**节点正文本身尚未被一手书证深化**。用户要求「了解并计划接续第二阶段」——即在不破坏阶段1 可审计性的前提下，用已核验的一手书证把节点正文写厚、写深。
- **本计划由来**：本轮以 grill-me 逐分支追问收敛出 12 项决策（见 §3），全部经用户裁决，勿在 Build 周期重新决策。

---

## 2. 目标与范围

### 2.1 本轮目标

以核验层的**主张锚（claim + anchor）**为定位，用**一手书证**深化 26 个有 `direct` 锚节点的 `definition` / `detail.{principle,mechanism,engineering,tradeoff}` 五段正文，并在**不扩 schema、不破坏 SSOT** 的前提下完成派生、门控、重生与公开层交付。

### 2.2 本轮范围（用户裁决：**先窄后宽**）

| 项 | 裁决 |
|---|---|
| 参与增密节点 | **26 个**（持有 ≥1 条 `direct` 锚） |
| 覆盖书 | DDIA（`BK-023`）/ Clean Architecture（`BK-007`）/ SAiP 4e（`BK-009`）三本 pilot |
| 剩余 27 本 | **不在本轮**，另立核验批次；后续批次完成后再对该批新覆盖节点批量增密 |
| 阶段3（结构扩展） | **不在本轮**（避免与阶段2 二次改动叠加） |

**26 个参与节点（按层）**

- `essence`（14）：`ESS-G-01` `ESS-G-02` `ESS-G-04` `ESS-I-02` `ESS-K-02` `ESS-L-05` `ESS-M-01` `ESS-M-02` `ESS-M-03` `ESS-M-04` `ESS-M-05` `ESS-O-01` `ESS-O-02` `ESS-O-03`
- `methodology`（10）：`MTH-G-02` `MTH-G-03` `MTH-G-06` `MTH-M-01` `MTH-M-02` `MTH-M-03` `MTH-M-06` `MTH-O-03` `MTH-O-05` `MTH-O-09`
- `technology`（2）：`TEC-K-05` `TEC-M-03`

**9 个本轮排除节点（写入遗留清单）**：`CAS-X-02` `ESS-G-03` `ESS-G-07` `ESS-H-02` `ESS-K-01` `MTH-K-06` `MTH-O-10` `MTH-O-11` `TEC-K-01`（仅有 partial/inferred 锚，无 direct 支撑 → 增密即注水；按原计划 §5.1「改写必须指向 ≥1 条**已有锚点**」口径，排除是唯一自洽解）。

> **注意（成本提示）**：26 个参与节点中，**仅 17 个有 `node-claim-map` 主张拆分**（18 个含被排除的 `CAS-X-02`）；另外 **9 个为 reverse-only**（`ESS-G-04` `ESS-K-02` `ESS-L-05` `ESS-M-01` `ESS-M-02` `ESS-M-04` `ESS-O-01` `MTH-O-09` `TEC-K-05`，各仅 1 条记录），需在 §4.4 步骤 0 的**主张完整性前置核查**中补齐五段主张集。

### 2.3 明确的非目标（本轮不做）

1. 不新增/删除节点、边、组（结构扩展归阶段3）。
2. 不修改节点 ID、`layer`、`domain`、`group`、`sources[]`、层间边方向（不新增 `sources[]`，避免与阶段3 边界模糊）。
3. 不新增公开面元素（无新视图、无新页面区块）。
4. 不改核验层的 `evidence_strength` 枚举、不引入 `contradicted` 之外的强度。
5. 不复核 27 本未核验书、不做全量重算。

---

## 3. 已定决策（本轮 grill-me 收敛，⛔ 勿重新决策）

| # | 决策 | 出处 |
|---|---|---|
| 1 | **范围与顺序 = 先窄后宽**：本轮只做 3 本 pilot 覆盖的节点；剩余 27 本另立批次，之后再对新覆盖节点批量增密 | Q1 |
| 2 | **落点形态 = 改写深化五段**（`definition` + `detail` 四段），**不扩 schema、不新增小节**；L2/L8 结构风险最低 | Q2 |
| 3 | **SSOT 回写口径**：段级 claim 锁定**强制**（每段 ≥1 claim；改写引入的实质新表述必新增 ledger claim + anchor + 第二路复核）；**无新事实时豁免**；句级映射降级为**抽检 WARN**（"实质句"不可机检）；改写前先跑 **claim 完整性前置核查** | Q3 |
| 4 | **生产拓扑 = A 两段式**：① 按书并行「证据展开」（只写各自证据分片，不改正文）② 按节点设**唯一写入方**综合改写五段 | Q4 |
| 5 | **增密强度 = D 双驱动**：目标区间 **2400–3000 字**（上限不破契约 3000）+ **注水比机检**（每 +200 字 ≥1 条 claim 支撑） | Q5 |
| 6 | **交付边界 = A 全链路含公开层**（核验层回写 → 派生 → 门控 → 重生 11–15+index → 公开投影 → 推公开仓/Pages，与 phase1 同构） | Q6 |
| 7 | **9 个无 direct 锚节点本轮排除**，保持原值不动，写入遗留清单 | Q7 |
| 8 | **门控 = A 双脚本按域拆分**：新建 `gate_densify.py`（G-D1..G-D5）+ 扩 `gate_verification.py`（G-V9） | Q8 |
| 9 | **公开呈现 = A 零新增元素**：正文变厚即成果；节点页锚行与 06 视图维持现状（仅内容可能因新增 claim 微调） | Q9 |
| 10 | **质检 = B 双层复核**：① 新增 claim 全部第二路独立复核（判强度）② 每节点成稿后「正文 vs 证据素材」保真复核（判越界）+ 主Agent 抽检 ≥20% | Q10 |
| 11 | **本轮交付物 = 只出方案文档**（本文件），不执行改写；Build 另开周期 | Q11 |
| 12 | **阶段3 不入本轮**；**Reflection 队列由用户 `/reflection` 自行处置**（本轮不自动处理 waiting 2） | Q12/Q13 |

### 3.1 与上游决策的一致性声明（必须记录）

- 复用 ADR-001「私有核验层为唯一真相源」：本轮新增的一切实质表述**必须回写核验层**，否则判 FAIL。
- 复用 ADR-002「主张级四级强度 + 双向」：证据展开产出的候选素材按同一封闭枚举标注强度；**新增 `direct` 仍走第二路复核**。
- 复用原计划决策 3.3#4「增量式派生作用域」：只有 26 个节点被写；其余 141 节点 `verified`/`confidence`/正文**零改动**。
- 复用全局决策 14「内容逐字保真」：本决策约束**生成链不得改写数据**；本轮改写发生在**数据层（`_parts/` 作者侧）**，生成链仍逐字搬运，二者不冲突。
- 复用阶段1 §F.4 根因教训：派生读取的「原值」**只能来自 `10-dag-data/_verification-baseline.json`（冻结，不覆盖）**，禁止从派生后的 dag 回读。

---

## 4. 阶段2 设计（可执行粒度）

### 4.1 架构总览（数据流）

```text
MISSION_ROOT/01-books/_files/                     (私有语料：DDIA MD ×26 / CleanArch EPUB→_text / SAiP EPUB→_text)
        │  ① 按书并行的「证据展开」阅读（读锚点章节 + 一跳上下文）
        ▼
01-books/_verify/_densify/                        (私有中间层：只增不改既有 SSOT 文件)
   ├── densify-contract.md                        (机读契约，§4.2)
   ├── precheck-coverage.json                     (步骤0：26 节点 × 5 段的主张覆盖核查)
   ├── evidence-{ddia,clean-architecture,saip}.json   (① 产物：书证素材 + 候选新 claim，按书分片)
   └── write-<node_id>.json                       (② 产物：唯一写入方的五段改写稿 + provenance + new_claims)
        │
        │  ② 主Agent 合并：new_claims → _parts/ledger-<slug>.json（唯一写入方 = 主Agent）
        ▼
01-books/_verify/_parts/{ledger,claims,toc,gaps}-<slug>.json   (SSOT 分片，被追加)
        │  derive_verification.py（既有，纯函数、无时间戳）
        ▼
01-books/_verify/verification-ledger.json + node-claim-map.json + reverse-gaps.json
10-dag-data/_verification-overrides.json           (26 节点；_evidence 增加、值不翻转)
        │
        │  ③ 正文写回：write-<node_id>.json 的 segments → 10-dag-data/_parts/*.json（对应节点所在分片）
        ▼
16-checkpoint/derive_densify.py                    (④ 派生 paragraph-claim-map.json + 注水比/字数对账)
        │  aggregate.py（既有，应用 _verification-overrides.json）
        ▼
10-dag-data/methodology-dag.json ──build.py──▶ 11/12/13/14/15 + index.html（正文变厚，无新元素）
        │
        ▼
16-checkpoint/{gate_densify.py(G-D1..G-D5), gate_verification.py(G-V1..G-V9)} + L1–L8 + 方法论四项
        ▼
assemble_publish.py → _publish/ → GitHub Git Data API 推送 → Pages 复验 → CI 对账
```

### 4.2 核验层扩展契约（`_densify/`，均为**私有层**）

**`densify-contract.md`（机读契约，Build 第一件事）** —— 固定以下字段与枚举。

**`evidence-<slug>.json`（① 按书证据素材分片，slug ∈ `ddia` / `clean-architecture` / `saip`）**

```json
{
  "meta": { "schema_version": "1.0.0", "book_source_id": "BK-009", "slug": "saip",
            "review_date": "2026-09-11", "note": "素材分片；只增不改既有账本" },
  "items": [
    {
      "evidence_id": "EV-SAIP-001",
      "node_id": "MTH-G-02",
      "origin": "mechanism",
      "claim_id": "MTH-G-02#mechanism#3",
      "is_new": false,
      "text": "<改写素材：可支撑正文的机制/权衡/反例说明，非引文，与书原文最长公共子串 ≤20 字>",
      "anchor": { "chapter": "5", "section": "5.2", "section_title": "<取自 book-toc-index.json>" },
      "proposed_strength": "direct",
      "read_scope": "<本次读了哪些章节/页段的可复核记录>"
    }
  ]
}
```

**`write-<node_id>.json`（② 按节点改写稿，唯一写入方产出）**

```json
{
  "node_id": "MTH-G-02",
  "segments": {
    "definition": "<改写后正文>", "principle": "...", "mechanism": "...",
    "engineering": "...", "tradeoff": "..."
  },
  "provenance": { "definition": ["EV-SAIP-001"], "principle": ["..."],
                  "mechanism": ["..."], "engineering": ["..."], "tradeoff": ["..."] },
  "new_claims": [
    { "claim_id": "MTH-G-02#mechanism#3", "text": "<改写，≤20 字子串>",
      "anchor": { "chapter": "5", "section": "5.2", "section_title": "<...>" },
      "evidence_strength": "direct", "direction": "forward" }
  ],
  "baseline_chars": 1519, "final_chars": 2530,
  "writer": "w-nodewriter-<batch>", "review_date": "2026-09-11"
}
```

**字段硬约束**

| 项 | 规则 |
|---|---|
| `origin` | 封闭枚举 `definition / principle / mechanism / engineering / tradeoff / errata`（与 `claim_id` 命名同源） |
| `proposed_strength` / `evidence_strength` | 封闭枚举 `direct / partial / inferred / contradicted` |
| `claim_id` | `<node_id>#<origin>#<n>`，全局唯一稳定；复用既有者 `is_new=false` |
| `text` / `segments` | **必须为改写**；与书原文**最长公共子串 ≤20 字**（G-D4 机检） |
| `anchor` | 必填 `chapter`（可空**仅当** `inferred` 且书无章节结构）；`section_title` 须能回溯 `book-toc-index.json` |
| `page_anchor_private` | 若引用页码，仅入 `_densify/` 私有层，**永不进公开投影** |
| 新增 claim | 必有 `anchor` + `direction` + 第二路复核结论，否则 G-V9 FAIL |
| 单节点主张上限 | ≤ **8 条**（沿用 ADR-002，含本轮新增） |
| 确定性 | 全部脚本**无时间戳**（禁 `datetime.date.today()` / `time.time()`）；`review_date` 用契约冻结常量；排序稳定；`json.dump(ensure_ascii=False, indent=2)` + 末尾换行 |

### 4.3 落盘路径与隔离（**硬约束，已实测零改动**）

- 新目录 `MISSION_ROOT/01-books/_verify/_densify/`（私有中间层）。
- **三重隔离现状实测（无需改动）**：
  1. 本地归档仓：`git check-ignore -v 01-books/_verify/_densify/evidence-saip.json` → 命中 `.gitignore:13:01-books/` ✅
  2. 公开仓 `_publish/.gitignore`：`01-books/_verify/` 已显式列入 ✅
  3. 装配层 `16-checkpoint/publish-manifest.json`：`classes.private` 含 `"01-books/_verify/"`，`private_probe` 含 `"01-books/_verify"` ✅（`_densify/` 落在其下，自动覆盖）
- **正文写入点**：`MISSION_ROOT/10-dag-data/_parts/*.json`（节点作者侧分片）——**只由主Agent 在合并阶段写入**，子Agent 只写 `_densify/write-<node_id>.json`。
- ⛔ 禁止手改 `methodology-dag.json` / `node-content.json` / `verification-ledger.json` / `_verification-overrides.json`（均为派生/聚合产物）。

### 4.4 生产流程（两段式）

**步骤 0 — 主张完整性前置核查（主Agent 自办，脚本化）**
对 26 个节点逐一检查五段是否各有 ≥1 条 claim 依据，产出 `_densify/precheck-coverage.json`。
- 17 个已有 `node-claim-map` 的节点：直接核对；
- **9 个 reverse-only 节点（各仅 1 条记录）**：标注"待证据展开补齐五段"；
- 该报告是步骤 ① 的输入（阅读任务清单）。

**步骤 ① — 证据展开（3 路并行 `reading-worker`，按书分工）**
- 输入：该书的全部 ledger 记录（`node_id` / `claim_id` / `anchor`）+ `precheck-coverage.json` 中该书负责的缺口项；
- 阅读：**锚点章节 + 一跳上下文**（DDIA 读 `01-books/_files/P0-11/ddia-zh-src/*.md`；CleanArch 读 `_verify/_text/clean-architecture.txt`；SAiP 读 `_verify/_text/saip.txt`；必要时回 EPUB 原文）；
- 产出：`_densify/evidence-<slug>.json`——把每条 claim 展开为**可支撑正文的素材**（机制细节 / 权衡 / 反例 / 适用边界），并显式标注 `is_new`（是否超出阶段1 已有主张）；
- 约束：只写自己的分片（**同域隔离 + 唯一写入方**）；不改任何既有 SSOT 文件。

**步骤 ② — 节点综合改写（按节点唯一写入方，分批并行）**
- 输入：该节点的全部 `evidence-*` items（跨书合并）+ 该节点当前五段正文 + `_verification-baseline.json` 原值；
- 产出：`_densify/write-<node_id>.json`；
- 约束：**正文表述不得越出所引素材范围**（越界即视为引入新事实 → 必须落 `new_claims` 并回写）；`essence` 层禁工具名/版本号；`technology` 层保留 version；
- 分批：26 节点按层/域分批（建议 3–4 节点/批，批间可并行），每节点一文件天然隔离。

**步骤 ③ — 主Agent 合并与回写（唯一写入方）**
1. 汇总全部 `new_claims` → 按 `book_source_id` 追加到 `_verify/_parts/ledger-<slug>.json`（并按需更新 `claims-<slug>.json`）；
2. 把 `write-<node_id>.json` 的 `segments` 写回 `10-dag-data/_parts/*.json` 对应节点；
3. 运行 `derive_verification.py`（产出 ledger / node-claim-map / overrides）；
4. 运行 `derive_densify.py`（产出 `paragraph-claim-map.json` + 对账报告）。

**步骤 ④ — 双层复核（质检）**
- 层 1：**全部新增 claim** 交第二路独立子Agent 重判强度（不告知首路结论）；分歧由主Agent 保守终裁（沿用阶段1 §F.2 口径：宁可降级为 `partial`）；
- 层 2：**每节点成稿后**交第二路独立子Agent 做「正文 vs 证据素材」保真复核，判定是否存在**越出素材的表述**（不重读全书，只比对素材与正文）→ 命中项回退改写或降级为 `partial`；
- 层 3：主Agent 对 `direct` 断言按 **≥20%** 抽检回盘。

**步骤 ⑤ — 门控 → 重生 → 装配 → 推送**（见 §7.3–§7.5）

### 4.5 委派分工（DAG）

```text
[W0] 契约与骨架：_densify/ 目录 + densify-contract.md + precheck 脚本 + precheck-coverage.json   ── 前置，串行（主Agent 自办）
      │
      ├─▶ [W1a] DDIA 证据展开（reading-worker，BK-023，18 记录）
      ├─▶ [W1b] CleanArch 证据展开（reading-worker，BK-007，30 记录）    ── W1a/W1b/W1c 三路并行
      └─▶ [W1c] SAiP 证据展开（reading-worker，BK-009，96 记录）
                  │
                  ▼
      [W2] 节点综合改写（node-writer × N，按节点唯一写入方；26 节点分 7–9 批）        ── 分批并行
                  │
                  ▼
      [W3a] 新增 claim 强度第二路复核（verifier-worker，独立视角）
      [W3b] 正文 vs 素材保真复核（verifier-worker，独立视角）                      ── W3a/W3b 并行
                  │
                  ▼
      [W4] 主Agent 合并回写 + derive_verification + derive_densify + aggregate       ── 串行
                  │
                  ▼
      [W5] 门控实跑（gate_densify G-D1..G-D5 + gate_verification G-V9 + L1–L8 + 方法论四项）── 串行（**主Agent 亲跑**）
                  │
                  ▼
      [W6] 重生 + 装配 + 推送 + Pages 复验 + CI 对账                                  ── 串行
```

- **委派 prompt 必含**：角色路径/描述、Skill 清单、**必读参考文件短路径**（`densify-contract.md` + 生产简报，**禁内联长契约**防 JSON 截断）、交付契约、返回 JSON 格式、`⛔ 无 GATE 自评`。
- **子Agent 权限事实**（阶段7 实测）：`architect-worker` 的 `bash` 全禁 → **门控必须由主Agent 亲跑**；`general` 可执行 `python3 script.py`（仅 `python -c` / `rm -rf` / `git push` 被禁）。
- **子Agent 自述一律回盘复验**（项目历史已 3 次抓出误判）。

### 4.6 派生与生成链改造

**新增 `MISSION_ROOT/16-checkpoint/derive_densify.py`**（仅标准库、确定性、无时间戳）：
- 输入：`_densify/write-*.json` + `verification-ledger.json` + `_verification-baseline.json`；
- 产出：
  1. `_densify/paragraph-claim-map.json`（`{node_id: {segment: [claim_id...]}}` + 每节点字数增量/注水比统计）；
  2. `_densify/densify-report.json`（对账：变更节点集 / 遗漏 / 越界 / 字数分布 / 注水比）；
- 判据计算：`注水比 = ceil(字数增量 / 200) ≤ |distinct claim_id in provenance|`。

**生成链改动（**最小化**）**
| 产物 | 改动 |
|---|---|
| `16-checkpoint/gen-nodes.py` / `gen-md.py` | **无改动**（正文本就来自数据层；章节锚行逻辑不变） |
| `16-checkpoint/gen-views.py` | **无改动**（06 视图结构不变；仅其数据源 `book-verification.json` 的 `_evidence` 计数可能变化） |
| `16-checkpoint/deliverables.json` | **无改动**（无新页面，`expected` 计数不变，L6 仍 365/365） |
| `10-dag-data/_verification-baseline.json` | **绝不覆盖**（阶段1 §F.4 根因防线） |

> 结论：本轮是**数据层增密**，生成链仅「重新运行」，这是决策 #2（不扩 schema）与 #9（零新增元素）的直接红利。

### 4.7 门控设计

**新增 `MISSION_ROOT/16-checkpoint/gate_densify.py`（G-D1..G-D5；CI 中显式 SKIPPED，绝不伪装 PASS）**

| 判据 | 内容 | 层级 |
|---|---|---|
| **G-D1** | **段级 claim 覆盖非空**：26 节点 × 5 段，每段 `provenance` 非空，且其中全部 `claim_id` 可在 `verification-ledger.json` 解析（**零悬挂**） | FAIL |
| **G-D2** | **注水比**：每节点 `ceil(字数增量/200) ≤ 该节点 provenance 覆盖的 distinct claim 数` | FAIL |
| **G-D3** | **字数区间**：26 节点终稿 ∈ **[2400, 3000]**；且全局契约区间 `[1500, 3000]` 不破（9 个排除节点保持原值） | FAIL |
| **G-D4** | **版权红线扩展**：**节点正文** vs 三本书原文（`_text/clean-architecture.txt`、`_text/saip.txt`、`_files/P0-11/ddia-zh-src/*.md`）的**最长公共子串 ≥20 字命中 = 0** | FAIL |
| **G-D5** | **对账**：变更节点集 **== 26 个参与节点集**（遗漏 0 / 越界 0）；26 节点的 `verified`/`confidence` **值不翻转**（`_evidence` 允许增加）；其余 141 节点零改动 | FAIL |

**扩展 `MISSION_ROOT/16-checkpoint/gate_verification.py` 新增 G-V9**

| 判据 | 内容 | 层级 |
|---|---|---|
| **G-V9** | **回写完整性**：阶段2 新增的每条 claim 必须有 `anchor` + `direction` + `second_pass ∈ {passed, disputed}`（不得为 `none`）；`claim_id` 全局唯一；`origin` ∈ 封闭枚举 | FAIL |

**既有门控同步（必须重跑，不得跳过）**

- **G-V1..G-V8**：全量重跑（`derive_verification.py --check` 幂等 + 对账 26/26）。
- **L1**（分片自验证）/ **L2**（全图审计 `nodes=167 edges=360 kahn=167/167`）/ **L3**（结构+断链 0）/ **L6**（覆盖度 100%）/ **L7**（`sources[]` 零悬挂、可溯源 100%）。
- **L8**（版式）：正文变长后**必须回到覆盖率 100%、问题 0**——本轮最大版式回归风险点。
- **L4 / L5**：本地补跑（CI SKIPPED）；L4 观察到 FAIL **先重跑一次确认**（阶段性白页瞬态）。
- **方法论四项**：层边界 / 术语一致 / 原则↔反例 / 11 维权衡，**特别关注 `essence` 层禁工具名/版本号不得回归**。
- **GR-10**：`verified=true` 占比不得下降（增量式下应保持 89.22% 或微升）。

### 4.8 验收判据（Build 完成口径）

- **结构**：UTF-8 无 BOM、无 U+FFFD；内部断链 0；JSON 全合法。
- **数据**：`validate_graph.py` errors=0；`dag_acyclic=true`；`sources[]` 零悬挂；**变更集 == 26 节点**。
- **增密三件套**：① 26 节点全部产出 `write-<node_id>.json`；② 每条新增 claim 可回溯「章节锚 + 强度 + 复核人」；③ `paragraph-claim-map.json` 五段全覆盖、零悬挂。
- **门控**：`gate_densify.py` **PASS 5/5**；`gate_verification.py` **PASS 9/9**；L1–L8 + 方法论四项全 PASS（`skipped ≠ PASS`）。
- **质检**：层1 新增 claim 全复核完成、分歧率与终裁留档；层2 保真复核 26/26；主Agent `direct` 抽检 ≥20%。
- **幂等**：`derive_verification.py --check` / `derive_densify.py --check` / `aggregate.py` 连跑稳定，`git diff --exit-code` 为空。
- **版权红线**：正文 ≥20 字子串命中 0；公开层无 `claim`/页码/摘句；公开面无本机路径。
- **公开层**：Pages 首页 / 节点页 / 组页 / 术语表 / MD 镜像 / 交互图 / 06 视图 均 HTTP **200**。
- **装配与 CI**：`assemble_publish.py --check` **0/0/0** 且 P1–P5 OK；`PUBLISH-STATE.file_count` 对账；最近 run success 且显式打印 L4/L5/G-V/G-D SKIPPED。
- **报告**：核验统计（字数增量、注水比分布、新增 claim 数、强度分布）+ 双层复核 FP 抽检结果，双版本（`.md` + `.html`，过 `gate_report.py` 5/5）。

### 4.9 回滚与基线重置

- **基线**：本轮会变更 `methodology-dag.json` 指纹（26 节点正文 + `meta` 不变）。完成后须**重设阶段基线**（记录新 SHA-256、新增 `00-plan/stage7p2-baseline.md`、同步 CI 预期）。
- **回滚路径**：撤销 `10-dag-data/_parts/*.json` 的 26 节点改动与 `_verification-overrides.json` 的增量 → 指纹回到 `9ae4cc01…`；**私有 `_densify/` 原样保留**（避免重复劳动）。
- **回滚触发条件**：① G-D4 正文红线命中 >0 且两轮改写无效；② 层2 保真复核越界率 >10%；③ L8 版式无法回到 100%。

---

## 5. 阶段3 接口（保持预留，本轮不展开）

- 输入保持 `MISSION_ROOT/01-books/_verify/reverse-gaps.json`（28 条：`coverage_hole 10 / concept_missing 10 / missed_citation 8`）。
- 准入契约仍为 proposed：新增节点须 ≥1 条 `direct` 锚 + ≥2 个相互独立信源；新增边须具备 `sources[]` 且不违反层间边方向。
- **本轮的接口产出**：`_densify/` 中按书整理的证据素材可作为阶段3「补引 / 新增节点」的候选池（只增不改，不预先决策）。
- **顺序刚性**：阶段3 必须在阶段2 之后，避免同一节点被二次改动叠加。

---

## 6. 风险与对策

| # | 风险 | 等级 | 对策 |
|---|---|---|---|
| 1 | **正文幻觉/越界**（改写引入书证不支持的内容） | **高** | 决策 #3 强制回写 + 决策 #10 层2 保真复核 + G-D1/G-D2 + 主Agent 抽检 ≥20% |
| 2 | **FP 判级**（复现阶段1 的 18.75%） | 高 | 封闭枚举 + 新增 claim 全量第二路复核 + 保守终裁降级口径 |
| 3 | **版权红线**（正文近似原文） | 高 | **G-D4 把 ≥20 字子串判据从 `claim` 扩展到节点正文** + `gate_disclosure.py` 兜底 |
| 4 | **注水**（为凑 2400 字灌水） | 中 | G-D2 注水比机检（每 +200 字 ≥1 claim） |
| 5 | **L8 版式回归**（正文变长撑破版式） | 中 | L8 全量重跑；先本地小批验证再全量重生 |
| 6 | **`essence` 层工具名回归** | 中 | 方法论专项「层边界」重跑；写入方 prompt 显式禁令 |
| 7 | **同节点并发写冲突** | 中 | 决策 #4 唯一写入方（子Agent 只写 `write-<node_id>.json`，正文由主Agent 合并） |
| 8 | **幂等破坏**（新增脚本引入时钟/非稳定排序） | 高 | 冻结常量 + 稳定排序 + `--check` 自证；严禁回退 `aggregate.py` 日期坑修复 |
| 9 | **同域二次改动**（阶段3 复用同批节点） | 中 | 阶段3 本轮不启动；接口只做只增不改 |
| 10 | **9 个无锚节点被"顺手"改写** | 中 | G-D5 对账硬拦（越界 0） |

---

## 7. 执行清单（Build 阶段可直接复制）

> 设 `MROOT="$HOME/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"`；除注明外均在 `$MROOT/16-checkpoint/` 下执行。

### 7.1 前置（骨架与核查）

```bash
cd "$MROOT"
mkdir -p 01-books/_verify/_densify
git check-ignore -v 01-books/_verify/_densify/evidence-saip.json   # 须命中 .gitignore:13:01-books/
grep -n '01-books/_verify' 16-checkpoint/publish-manifest.json      # 须含 classes.private + private_probe
python3 16-checkpoint/derive_densify.py --precheck                  # 步骤0：26 节点 × 5 段主张覆盖
```

### 7.2 合并回写与派生

```bash
cd "$MROOT/16-checkpoint"
python3 derive_verification.py                    # 分片 → 合并 SSOT + 覆盖集 + 公开投影
python3 derive_verification.py --check            # 幂等自证
python3 derive_densify.py                         # paragraph-claim-map + 对账报告
python3 derive_densify.py --check                 # 幂等自证
python3 aggregate.py                              # 应用覆盖集 → 权威主图（勿手改输出）
python3 aggregate.py && git -C "$MROOT" diff --exit-code   # 幂等自证
```

### 7.3 重生与门控

```bash
cd "$MROOT/16-checkpoint"
python3 build.py --config mother --quiet
python3 validate_graph.py --graph ../10-dag-data/methodology-dag.json \
  --canonical ../03-knowledge-map/canonical-sources.json
python3 gate_densify.py --check all               # 新增 G-D1..G-D5
python3 gate_verification.py --check all          # G-V1..G-V9
python3 kb_gate.py --root "$MROOT" --layers structure,links \
  --exclude _backup-idmigration --exclude 02-research --exclude 01-books \
  --exclude 03-knowledge-map --exclude 00-plan --exclude 16-checkpoint \
  --exclude _publish --exclude 18-design --exclude .github
python3 gate_coverage.py && python3 gate_sources.py
python3 gate_layout.py --check all && python3 gate_methodology.py --check all
python3 gate_visual.py --check all                # L4（本地；CI SKIPPED）
python3 gate_render.py --timeout 25               # L5（本地；CI SKIPPED）
```

### 7.4 公开层装配与推送

```bash
cd "$MROOT"
python3 16-checkpoint/assemble_publish.py --check          # 对账 0/0/0
python3 16-checkpoint/assemble_publish.py --apply          # 预检 P1–P5 后落盘
python3 16-checkpoint/gate_disclosure.py --root "$MROOT/_publish"
python3 16-checkpoint/assemble_publish.py --export "$MROOT/_pages-export"
python3 16-checkpoint/assemble_publish.py --assert-clean "$MROOT/_pages-export"
# 推送：沙箱禁 git push → GitHub Git Data API（blobs → trees → commits → PATCH refs）
# 回验：远端 tree 对账 + `gh run list --limit 3` success + Pages 七类页面 200
```

### 7.5 收尾

1. 清理 `/tmp` 与临时目录残留（脚本、日志、中间 JSON、导出目录）。
2. 重设阶段基线 `00-plan/stage7p2-baseline.md`（新指纹 + 输入 SHA-256 + 门控表）。
3. Mission 留档询问（`question`）→ 双版本报告（`.md` + `.html`，过 `gate_report.py` 5/5，5 段完整）。
4. 按协议封装 **Reflection 4 层**，追加 `~/opencode/archive/Reflection/pending.json`（`status=waiting`，**仅主Agent**，fire-and-forget）。

---

## 8. 待用户决策 / 待用户提供

| # | 事项 | 选项 | 默认 |
|---|---|---|---|
| 1 | 本方案文档是否定稿（转 `accepted`） | 定稿 / 修订 | 待审阅 |
| 2 | 节点写入方的批大小 | 3 / 4 / 6 节点每批 | 4 |
| 3 | 是否需要用户本人参与 `direct` 抽检 | 需要 / 仅主Agent 抽检 | 仅主Agent |
| 4 | 本轮完成后是否自动进入 Build | 自动 / 另立窗口 | 另立窗口（决策 #11） |
| 5 | Reflection 队列（waiting 2） | 现在审 / 稍后 | 稍后（决策 #12） |

> **无需用户提供材料**：三本 pilot 语料均在私有层（DDIA 26 MD + CleanArch/SAiP 抽文本），本阶段无外部依赖。

---

## 9. 附：本计划所依据的关键实测数据（2026-09-11 回盘复验）

| 指标 | 实测值 | 来源 |
|---|---|---|
| 图谱规模 | 167 节点 / 360 边 / 18 组 / 18 案例 | `10-dag-data/methodology-dag.json` |
| **当前指纹** | `9ae4cc01f7b183f9a621997896a9033af6d9ca9ed38fee462077d8604496eba1` | `sha256sum` |
| 本地归档仓 HEAD | `8ec6a41`（工作树干净） | `git log --oneline -3` |
| 核验记录 | 144（`direct 78 / partial 59 / inferred 7 / contradicted 0`） | `verification-ledger.json` |
| 方向分布 | `forward 120 / reverse 24` | 同上 |
| 第二路复核分布 | `passed 78 / disputed 18 / none 48` | 同上 |
| 覆盖节点 | 35（**26 有 direct 锚 / 9 无**） | 脚本统计 |
| 主张拆分表 | 18 节点 / **120 条**主张（`_densify` 前置需补 9 个 reverse-only 节点） | `node-claim-map.json` |
| 缺口清单 | 28（`coverage_hole 10 / concept_missing 10 / missed_citation 8`） | `reverse-gaps.json` |
| 节点正文字数 | 1501–1813（中位数 1536，均值 1566）；契约 1500–3000 | 脚本统计 |
| 三本 pilot 语料 | DDIA `_files/P0-11/ddia-zh-src/`（26 MD）+ EPUB；CleanArch `_verify/_text/clean-architecture.txt`（536KB）；SAiP `_verify/_text/saip.txt`（1069KB） | `ls` |
| `_densify/` 隔离 | 本地 `.gitignore:13:01-books/` 已命中；装配 `classes.private` 含 `01-books/_verify/` | `git check-ignore -v` + `publish-manifest.json` |
| 阶段1 FP 率（质检先验） | 18.75%（18/96 direct 判假阳性，形态=「原句+推断扩展」复合主张） | 阶段1 §F.5 |
