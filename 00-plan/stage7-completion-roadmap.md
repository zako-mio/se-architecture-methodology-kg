# 软件工程架构方法论 · 完工路线图 + 阶段2 可执行细则

> 母任务：0910-软件工程架构方法论 ｜ 生成日期：2026-10-11 ｜ 生成人：主Agent（Plan 周期）
> 状态：**accepted** —— 2026-10-11 经用户裁决「全链路完工路线图 + 阶段2 立即可执行细则」，并批准**本会话直接开工 Build**
> 复杂度自评：**19/20**（影响范围 5 · 逻辑深度 5 · 操作数量 5 · 风险精度 4）→ 属高复杂度，按最深推理执行
> 性质：**架构判断（产出级）** —— 规模三问留痕见 §0；本文件**不是** ADR / 选型矩阵，故**不过 `gate_architecture.py`**、**不委派 `oc_architect`**
> 上游依据：`00-plan/stage7-book-absorption-plan.md`（三阶段总计划）、`00-plan/stage7-phase2-content-densification-plan.md`（阶段2 方案，accepted）、`00-plan/stage7-baseline.md`（阶段1 基线）、`00-plan/NEXT-SESSION-HANDOFF.md`（接力）
> 路径约定（全文只在此处声明一次，正文一律写 `MISSION_ROOT/...`，不含本机绝对路径）：
>
> ```text
> MISSION_ROOT = "~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"
> SUB_LIB_ROOT = "~/opencode/archive/Mission-file/2026-08/0823-12factor-methodology"
> ```
>
> **所有数值均为本轮实测（2026-10-11），非推演；与既有文档记载不一致处已单独标注。**

---

## §0 架构分档留痕（规模三问）

| # | 判定问 | 结论 | 依据 |
|---|---|---|---|
| Q1 | 是否改变**模块/服务边界或对外接口**（签名、契约、依赖方向）？ | **否**（阶段2 本阶段） | 阶段2 决策 #2「不扩 schema、不新增小节」、#9「零新增公开元素」；新增的 `_densify/` 是**私有中间层**，不改变任何既有公开契约 |
| Q2 | 变更是否**跨模块传播**（连带改到 ≥2 个模块/包）？ | **是** | 触及 4 个区：`01-books/_verify/`（SSOT）、`10-dag-data/`（数据层）、`16-checkpoint/`（派生+门控+装配）、`_publish/`（公开层）；阶段3 另触及 `20-agent-skill/` |
| Q3 | 反转成本是否**高于「改回配置/删文件」量级**？ | **是** | 阶段3 将突破 167 节点，需同步再生 `deliverables.json` / `node-index.md` / `SKILL.md` 并重设基线；阶段2 会变更图谱指纹 |

**定档**：命中 Q2/Q3 → 按 `routing.md` §9 定档为 **产出级**（工程步骤「实现/重构/技术债」列）。
- 本计划**不是** ADR / 选型矩阵 → **不过 `gate_architecture.py`**、**不委派 `oc_architect`**。
- 但计划内**明确标记**了 3 处未来升级为**门控级**的决策点（§5.3 阶段3 新节点准入），届时须补 ADR + 过门控。

---

## §1 现状（本轮实测，全部一手）

### 1.1 基线完整性 —— **8/8 指纹与 `stage7-baseline.md` 逐字节一致**

| 文件 | 实测 SHA-256 | 对基线 |
|---|---|---|
| `10-dag-data/methodology-dag.json` | `9ae4cc01…96eba1` | ✅ 一致 |
| `10-dag-data/node-content.json` | `38d5f98b…b7b2532` | ✅ 一致 |
| `10-dag-data/_base.json` | `8d100f2e…176e88` | ✅ 一致 |
| `01-books/_verify/verification-ledger.json` | `8ca515f8…ae79f8` | ✅ 一致 |
| `01-books/_verify/node-claim-map.json` | `ea2dad4a…612ef` | ✅ 一致 |
| `01-books/_verify/reverse-gaps.json` | `c61071fe…7c8514` | ✅ 一致 |
| `10-dag-data/_verification-overrides.json` | `3759f220…ac86df` | ✅ 一致 |
| `10-dag-data/book-verification.json` | `4c4d4a8e…942633` | ✅ 一致 |

**门控实跑（本轮亲跑，非引用文档）**：
- `gate_verification.py --check all` → **PASS=8 FAIL=0 WARN=0 SKIP=0**（G-V1..G-V8）
- `validate_graph.py` → `nodes=167 edges=360 kahn_visited=167/167`，`errors=0 warnings=0`，**PASS**
- `gate_coverage.py` → manifest **100.00%** / 四向 **100.00%** / GR-08 PASS / GR-09 11/31=35.48% PASS → **L6 PASS**

### 1.2 阶段2 **一行未执行**（确认）

`01-books/_verify/_densify/`、`16-checkpoint/derive_densify.py`、`16-checkpoint/gate_densify.py` **均不存在**。
26 个参与节点正文 **0/26** 落在目标区间 `[2400,3000]`（实测 min 1501 / median 1524 / max 1772）。
`node-claim-map.json` = 18 节点 / 120 主张；**9 个 reverse-only 节点确无主张拆分**，实测清单与方案一致：
`ESS-G-04` `ESS-K-02` `ESS-L-05` `ESS-M-01` `ESS-M-02` `ESS-M-04` `ESS-O-01` `MTH-O-09` `TEC-K-05`。

### 1.3 剩余书核验范围 —— 「27 本」**证实**

`canonical-sources.json` 253 信源（**BK 38**）；`01-books/acquired-manifest.json` = **30 本已获取**（P0-01..P2-30，75 文件 / 304MB，gate fails 0）；阶段1 已核验 3 本 → **剩余 27 本**。
其中 **11 本已有结构化抽文本**（`structure_snapshots`，`has_source_txt: true`）：`p0-06-fowler-eaa` `p0-09-fowler-refactoring` `p0-11-ddia-preview` `p1-12-devops-handbook` `p1-18-evolutionary-arch` `p1-19-sei-documenting` `p1-22-continuousdelivery` `p1-23-teamtopologies` `p1-24-eip-patterns` `p2-28-architect-elevator` + `12factor-official`。**其余 16 本需先抽文本**。

### 1.4 阶段3 缺口范围（实测）

`reverse-gaps.json` = 28 条：`coverage_hole 10 / concept_missing 10 / missed_citation 8`；强度 `direct 21 / partial 7`；书源 `BK-023 15 / BK-009 7 / BK-007 6`。
按 `proposed_action` 分类：**新增节点 17 条**（`direct 10` / `partial 7`）、新增术语 2 条、补引 7 条、其他 2 条。
→ 按阶段3 准入契约（≥1 `direct` 锚 + ≥2 独立信源），**仅 10 条具备资格**；另 7 条为 `partial`，**必须先补证或降级为「扩展现有节点」**，否则注水。

### 1.5 公开交付与 CI

- 公开仓 `zako-mio/se-architecture-methodology-kg`（branch `main`）；本地 `_publish/` HEAD = `deda112`，受控文件 **533**。
- CI `_publish/.github/workflows/rebuild.yml` 实跑 L2/L3/L8/L6/L7/方法论四项/disclosure + `build.py` 漂移检测；L4/L5 显式 SKIPPED。
- ⚠️ **CI 缺失**：`gate_verification.py` 在 `_publish/16-checkpoint/` **存在但 workflow 未调用**（文档称「CI 中 G-V 显式 SKIPPED」，实际是**完全没跑**）→ 需补 SKIPPED 步骤以符合契约。
- ⚠️ **`report-phase7p2-plan.{md,html}` 未声明进 `classes.sanitize`** → 当前 `assemble_publish.py --check` 必然非 0/0/0。且 `audit_publish.py` 的 `SCAN_ROOT_FILES`（`:48`）未含这两个文件 → **只加 sanitize 会被原样复制、不受脱敏机检**。

### 1.6 未提交文件

`git status`：`M 00-plan/NEXT-SESSION-HANDOFF.md`、`M report.html`、`?? 00-plan/stage7-phase2-content-densification-plan.md`、`?? report-phase7p2-plan.{md,html}`、`?? report.original.html`。
实测这 4 个待发布文件 **本机路径命中 = 0**（可安全发布）。`report.original.html` 性质待定（§9 A6）。

### 1.7 🔴 **关键环境纠正：子 Agent 无 shell，但有 write**

实测探针结论（本轮亲测）：子 Agent 工具集 = `read/glob/grep/write/edit/web_fetch/web_search/skill/subagent/...`，**没有 `bash`/`shell`/`python` 任何命令执行工具**。
这与 `NEXT-SESSION-HANDOFF.md` §H.4「`general` 子 Agent 可执行 `python3 script.py`」**直接矛盾**。

**对本轮计划的刚性影响**：
1. 一切确定性机制（`derive_*` / `aggregate.py` / `build.py` / 全部门控 / 装配 / 推送）**必须由主 Agent 串行亲跑**。
2. 子 Agent **可以直写文件** → 证据分片与改写稿可由子 Agent 落到**各自互不重叠的路径**（唯一写入方原则仍成立，只是不再经主 Agent 转写）。
3. 子 Agent **不得被要求跑任何脚本**；其产出仅限「读 → 写自己的分片」。
4. 子 Agent 并发上限 **5**（用户约束）。

---

## §2 完工路线图（四轨，按依赖排序）

```text
                    ┌─ 轨A：阶段2 内容增密（26 节点）        ← 本轮立即开工
基线 167/360  ──────┼─ 轨B：剩余 27 本核验（分批）
（已冻结验证）       ├─ 轨C：阶段3 结构扩展（10 条 direct 缺口）
                    └─ 轨D：能力包同步（20-agent-skill，轨C 后）
                                │
                    收尾：指纹重设 + 双版本报告 + 留档
```

| 轨 | 内容 | 规模 | 依赖 | 档位 |
|---|---|---|---|---|
| **A** | 阶段2 内容增密（26 节点五段改写 + 核验层回写 + 派生 + 门控 + 公开层） | 26 节点 / 3 书 | 无（基线已验） | 产出级 |
| **B** | 剩余 27 本核验（`_parts/{ledger,claims,toc,gaps}-<slug>.json` 扩展） | 27 本 / 30 本已获取 | 独立于 A，可并行 | 产出级 |
| **C** | 阶段3 结构扩展（新增 ≤10 节点 + 边 + 组） | 10 条 direct 缺口 | **必须在 A 之后**（避免同节点二次改动叠加） | **门控级**（§5.3） |
| **D** | 能力包同步（`node-index.md` / `routing.md` / `cheatsheet.md` / `SKILL.md` 计数再生） | 4 文件 + `deliverables.json` | 必须在 C 之后 | 按需级 |

**顺序刚性**：A → C → D；B 与 A **可并行**（不同文件域），但**两者都会触发 `derive_verification.py`** → **回写与派生必须串行**（见 §3.5 冲突消解）。

---

## §3 轨A · 阶段2 可执行细则（本会话 Build 依据）

> 复用已 accepted 的 `00-plan/stage7-phase2-content-densification-plan.md` 全部决策（12 项 + ADR-001/002 一致性声明），**不重新决策**。以下只补**实测发现的偏差**与**可执行修正**。

### 3.1 修正①：`node-claim-map.json` 不由 ledger 派生 → 必须显式写 `claims-<slug>.json`

**实测根因**（`16-checkpoint/derive_verification.py:111` `build_claims`）：`node-claim-map.json` 的来源是 **`_parts/claims-<slug>.json`**，**不是** `ledger-<slug>.json`；且合并语义为**首 slug 优先**（`SLUG_ORDER = ("clean-architecture","ddia","saip")`，`:30`），同 `node_id` **后者被静默丢弃**。

**后果**：若只把 `new_claims` 追加进 `ledger-<slug>.json`，`node-claim-map.json` **不会新增任何主张**，而 G-D1/G-D2 依赖它 → **门控必 FAIL**。

**修正**：`write-<node_id>.json` 的 `new_claims` 必须**同时**落两处，且 `claims` 侧**必须写入该节点已存在的那个 slug 分片**：

| 节点所在 slug | 归属文件 |
|---|---|
| `ESS-G-01` `ESS-G-02` `ESS-I-02` `ESS-M-03` `ESS-M-05` `ESS-O-02` `ESS-O-03` `MTH-G-02` `MTH-G-03` `MTH-G-06` `MTH-M-01` `MTH-M-02` `MTH-M-03` `MTH-M-06` `MTH-O-03` `MTH-O-05` `TEC-M-03` | `claims-saip.json`（实测 15 键） |
| 9 个 reverse-only 节点（`ESS-G-04` `ESS-K-02` `ESS-L-05` `ESS-M-01` `ESS-M-02` `ESS-M-04` `ESS-O-01` `MTH-O-09` `TEC-K-05`） | **该节点 ledger 记录所在 slug**（步骤0 前置核查逐节点解析 `record_id` 前缀 `VR-CA-`/`VR-DDIA-`/`VR-SAIP-` 定 slug，**不得按书推测**） |

> 注：`claims-ddia.json` 当前 = `{}`（空对象）。DDIA 新增主张需先建节点键；因首 slug 优先，**DDIA 不能对已有 saip/CA 节点补主张** —— 这类主张必须改挂到该节点的既有 slug 分片。

### 3.2 修正②：正文写回点已实测定位

节点正文位于 `10-dag-data/_parts/<batch>.json` 的 `nodes[]`（list 形式，元素含 `definition` + `detail.{principle,mechanism,engineering,tradeoff}`）。实测三个样本的归属：
`ESS-M-05 → W1-M.json`、`TEC-K-05 → W2-TEC-K.json`、`MTH-G-02 → pilot-methodology.json`。
**步骤0 必须产出 26 节点 → 分片文件的完整映射表**（`_densify/precheck-coverage.json` 内），写入方按表定位，**不得按域猜测**。

### 3.3 修正③：字数可机读，无需重算

`10-dag-data/node-content.json` 的每条 `node_contents[]` **已含 `char_count`** 字段（= 五段字符数之和，实测与逐段求和一致）。`derive_densify.py` 的 `baseline_chars` **直接读该字段**，避免重复实现分段逻辑。

### 3.4 执行步骤（W0→W6，含并发上限 5）

**W0 · 骨架与契约（主Agent 串行，全 shell）**
1. `mkdir -p 01-books/_verify/_densify`
2. 三重隔离实测：`git check-ignore -v 01-books/_verify/_densify/evidence-saip.json` → 须命中 `.gitignore:13:01-books/`；`grep -n '01-books/_verify' 16-checkpoint/publish-manifest.json` → 须含 `classes.private` + `private_probe`。
3. 写 `_verify/_densify/densify-contract.md`（固化 §E.3 字段/枚举 + **§3.1 双落点规则** + **§3.2 映射表要求**）。
4. 实作 `16-checkpoint/derive_densify.py --precheck` → 产出 `_densify/precheck-coverage.json`：
   - 26 节点 × 5 段的主张覆盖矩阵；
   - **26 节点 → `_parts/` 分片映射**；
   - **9 个 reverse-only 节点的 slug 归属**（解析 `record_id` 前缀）；
   - 缺口清单（哪段无 claim 依据）→ 作为 W1 阅读任务输入。

**W1 · 证据展开（3 路并行，≤5 并发）** —— 子 Agent **可写**（无 shell）
- 每路读锚点章节 + 一跳上下文，**只写** `_verify/_densify/evidence-<slug>.json`（`ddia` / `clean-architecture` / `saip`）。
- 语料：DDIA `01-books/_files/P0-11/ddia-zh-src/*.md`（26 文件）；CleanArch `_verify/_text/clean-architecture.txt`（536KB）；SAiP `_verify/_text/saip.txt`（1069KB）。
- 主Agent 回盘抽检：素材是否越出锚点章节、`is_new` 标注是否可信。

**W2 · 节点综合改写（分批并行，≤5 并发，4 节点/批 → 7 批）** —— 子 Agent **可写**
- 每批一个子 Agent，**按节点唯一写入方**：写 `_verify/_densify/write-<node_id>.json`（**路径天然不重叠**）。
- 输入：跨书合并的 `evidence-*` items + 该节点现五段 + `_verification-baseline.json` 原值。
- 硬约束：越出素材即须落 `new_claims`；`essence` 层禁工具名/版本号；`technology` 层保留 `version`；每节点主张 **≤8 条**。
- ⚠️ **批划分必须按 §3.1 的 slug 归属分组**：同 slug 的节点即使内容无关也**不可跨批并发写**（防同文件写冲突）。若一批内混入两个 slug，则该批的 `new_claims` 由主Agent 串行回写（见 W3）。

**W3 · 合并回写（主Agent 串行，唯一写入方）**
1. 汇总 `new_claims` → **双落点**：`_parts/ledger-<slug>.json`（追加 record）+ `_parts/claims-<slug>.json`（追加到**既有节点键**的 `claims[]`；9 个 reverse-only 节点**新建节点键**）。
2. `write-<node_id>.json` 的 `segments` → 写回 `10-dag-data/_parts/<batch>.json` 对应节点（按 §3.2 映射表）。
3. `python3 derive_verification.py` → `--check`
4. `python3 derive_densify.py` → `--check`
5. `python3 aggregate.py` → `aggregate.py && git -C "$MROOT" diff --exit-code`（幂等自证）

**W4 · 双层复核（并行，≤5 并发）** —— 子 Agent 读 + 写复核件
- 层1：**全部新增 claim** 交第二路独立子 Agent 重判强度（不告知首路结论）→ 写 `_verify/_review/densify-secondpass.json`；分歧由主Agent **保守终裁**（宁可降 `partial`）。
- 层2：**每节点成稿**交第二路做「正文 vs 证据素材」保真复核（不重读全书）→ 写 `_verify/_review/densify-fidelity.json`；越界项回退改写或降级 `partial`。
- 层3：主Agent 对 `direct` 断言抽检 **≥20%**。

**W5 · 门控（主Agent 亲跑，串行）** —— 见 §3.6
**W6 · 重生 → 装配 → 推送（主Agent 串行）** —— 见 §3.7

### 3.5 轨A × 轨B 并行冲突消解（若同时启动 B）

A 与 B 都会调用 `derive_verification.py`，而该脚本**全量重建** 4 件 SSOT。规则：
- B 的 ledger/claims 分片（新 slug）与 A 的追加（既有 3 slug）**文件域不重叠** → 生产阶段可并行；
- **回写后只跑一次 `derive_verification.py`**（合并 A+B 的全部新记录），禁止两轨各自派生后再互相覆盖；
- 主Agent 维护**单一派生锁**：任何 `derive_*`/`aggregate.py` 调用前先确认无其它轨处于回写中。

### 3.6 门控设计（实测校准）

**新增 `16-checkpoint/gate_densify.py`（G-D1..G-D5；CI 显式 SKIPPED，绝不伪装 PASS）**

| 判据 | 内容 | 本轮实测校准 |
|---|---|---|
| **G-D1** | 26 节点 × 5 段 `provenance` 非空；全部 `claim_id` 可在 `verification-ledger.json` **且** `node-claim-map.json` 解析（零悬挂） | **须同时查两表**（§3.1 修正：只查 ledger 会漏检 claims 分片缺失） |
| **G-D2** | `ceil(字数增量/200) ≤ distinct claim 数` | `字数增量` 用 `char_count`（§3.3） |
| **G-D3** | 26 节点终稿 ∈ `[2400,3000]`；全局 `[1500,3000]` 不破；9 个排除节点保持原值 | 实测 0/26 已在区间 → **全部需增密** |
| **G-D4** | **节点正文** vs 三书原文 **最长公共子串 ≥20 字命中 = 0** | 新增（原仅查 `claim`）；三书语料路径已实测可用 |
| **G-D5** | 变更节点集 **== 26**（遗漏 0 / 越界 0）；26 节点 `verified`/`confidence` **值不翻转**；其余 141 节点零改动 | 注意 `verified` 有布尔 `true` 与字符串 `"cited"` 两种取值，**须用 `is True` 严格判断** |

**扩展 `16-checkpoint/gate_verification.py` 新增 G-V9**：机制已实测 —— `ALL_CRITERIA` 列表（`:42`）+ `check_gvN` 函数 + 注册表（`:309`）+ docstring。新增 G-V9 为**局部改动**（1 函数 + 2 处登记）。
**G-V9 内容**：阶段2 新增每条 claim 必有 `anchor` + `direction` + `second_pass ∈ {passed, disputed}`（不得 `none`）；`claim_id` 全局唯一；`origin` ∈ 封闭枚举。

**既有门控全部重跑**：G-V1..G-V8（含 `derive --check` 幂等）、L1/L2/L3/L6/L7/L8、方法论四项、GR-10（`verified=true` 占比不得下降，当前 89.22%）；L4/L5 本地补跑（FAIL 先重跑一次确认瞬态白页）。

**负向测试（判据可信度，必做）**：对 G-D1..G-D5 与 G-V9 各构造 ≥1 个**必 FAIL 的负例**（如故意删除一个 provenance、故意让某段字数 2399、故意复制 20 字原文子串、故意把某 claim 的 `second_pass` 设为 `none`），确认门控**真的拦得住** —— 防止恒真判据/假绿。

### 3.7 公开层（实测缺口修正）

1. **`publish-manifest.json`** `classes.sanitize` 显式新增 `report-phase7p2-plan.md` / `report-phase7p2-plan.html`；**并把这两个文件加入 `audit_publish.py` 的 `SCAN_ROOT_FILES`**（否则只加 sanitize 会被原样复制、不过脱敏机检）。
2. **`_publish/.github/workflows/rebuild.yml` 补两步 SKIPPED**：`gate_verification.py`（G-V1..G-V9）与 `gate_densify.py`（G-D1..G-D5），显式打印 SKIPPED 原因，**不计 PASS**。
3. `build.py --config mother --quiet` 重生 11–15 + `index.html`（幂等，`git diff --exit-code` 须空）。
4. `assemble_publish.py --check` → 须 **0/0/0 + P1–P5 OK** → `--apply` → `gate_disclosure.py --root _publish` → `--export` → `--assert-clean`。
5. 推送：**`git push` 被禁** → GitHub Git Data API（blobs → trees → commits → PATCH refs）；回验远端 tree 文件数 == 本地 `git ls-files | wc -l`、`gh run list --limit 3` success、Pages 七类页面 HTTP 200。

### 3.8 验收判据（无新鲜证据不得声称完成）

- 结构：UTF-8 无 BOM / 无 U+FFFD；内部断链 0；JSON 全合法。
- 数据：`validate_graph.py` errors=0、`dag_acyclic=true`、`sources[]` 零悬挂；**变更集 == 26 节点**。
- 增密：26 节点终稿 ∈ `[2400,3000]`；`paragraph-claim-map.json` 五段全覆盖、零悬挂；注水比达标。
- 门控：`gate_densify.py` **PASS 5/5**；`gate_verification.py` **PASS 9/9**；L1–L8 + 方法论四项全 PASS（`skipped ≠ PASS`）；**负向测试全部如期 FAIL**。
- 幂等：`derive_verification.py --check` / `derive_densify.py --check` / `aggregate.py` / `build.py` 连跑 `git diff --exit-code` 为空。
- 版权：正文 ≥20 字子串命中 0；公开层无 `claim`/页码/摘句；公开面无本机路径。
- 公开层：Pages 七类页面 HTTP 200；装配 0/0/0；CI success 且显式打印 L4/L5/G-V/G-D SKIPPED。
- 收尾：`00-plan/stage7p2-baseline.md` 新建（新指纹 + 输入 SHA-256 + 门控表）；双版本报告过 `gate_report.py` 5/5；本地归档提交。

### 3.9 回滚与基线

- **回滚路径**：撤销 `10-dag-data/_parts/*.json` 的 26 节点改动 + `_verification-overrides.json` 增量 → 指纹回到 `9ae4cc01…`；私有 `_densify/` **原样保留**（避免重复劳动）。
- **回滚触发**：① G-D4 正文红线命中 >0 且两轮改写无效；② 层2 保真复核越界率 >10%；③ L8 版式无法回到 100%。
- **基线重设**：完成后记录新 SHA-256，新建 `00-plan/stage7p2-baseline.md`，同步 CI 预期。

---

## §4 轨B · 剩余 27 本核验（分批方案）

**B1 · 已有抽文本的 10 本（快速通道）**：`p0-06` `p0-09` `p1-12` `p1-18` `p1-19` `p1-22` `p1-23` `p1-24` `p2-28` + `12factor-official` —— 直接进证据展开，**无需抽取**。
**B2 · 需先抽文本的 17 本**：EPUB/PDF → `_verify/_text/<slug>.txt`（复用阶段1 抽取脚本模式），再进证据展开。
**B3 · 新增 slug 的契约扩展**：`SLUG_ORDER` / `SLUG_SOURCE` 当前硬编码 3 本（`derive_verification.py:30-31`）→ 扩展为数据驱动（读 `_parts/toc-*.json` 的 `source_id`），否则新书分片**不会进入派生**。
**B4 · 准入门控**：新书核验沿用 G-V1..G-V9；新 slug 须补 `toc-<slug>.json`（否则 `section_title` 无法回溯）。

> 轨B 的**范围/顺序**建议：先 B1（10 本，边际成本最低）→ 再按「节点引用密度 × 信源等级」排序 B2。**该排序属用户决策点**（§9 A4）。

---

## §5 轨C · 阶段3 结构扩展

### 5.1 输入与准入（实测校准）

28 条缺口 → **新增节点 17 条**（`direct 10` / `partial 7`）、新增术语 2 条、补引 7 条、其他 2 条。
阶段3 准入契约：新增节点须 **≥1 `direct` 锚 + ≥2 相互独立信源**；新增边须具 `sources[]` 且不违层间边方向（仅 `implements` 技术→方法 / `derives_from` 方法→本质，单向、禁越级）。

**合格集（10 条 direct 新增节点）**，其中 6 条已有明确 ID 提案：
`ESS-G-08` `ESS-G-09` `ESS-H-10` `ESS-H-11` `ESS-H-12` `ESS-H-13` `ESS-O-04` `MTH-G-07` `MTH-G-08` `MTH-G-09` `TEC-I-04` + 4 条具名提案（`ASR` / `ADD` / 架构师角色 / 战术子节点）。
→ **须先做「节点去重与 ID 分配」**：现有 167 节点中是否已有等价概念（如 `ESS-H-02` 内聚耦合、`MTH-M-01` 战术）需逐条比对，**避免重复造节点**。

**不合格集（7 条 `partial`）**：**不得直接建节点**。处置二选一：① 补证到 `direct` 后入阶段3；② 降级为「扩展现有节点正文」（可并入轨A 的后续批次）。

### 5.2 规模影响（实测硬编码清单）

突破 167 节点后**必须同步**的位置（实测）：

| 文件 | 位置 | 性质 |
|---|---|---|
| `16-checkpoint/deliverables.json` | `:9` `:10` `:16` `:23`（4 处 `167`） | **功能性** —— 不改则 `gate_coverage.py` 必 FAIL |
| `20-agent-skill/SKILL.md` | `:4` `:19` `:91` | 文档计数 |
| `20-agent-skill/node-index.md` | `:1` `:3` | 标题计数 |
| `15-md/00-index.md` | `:3`（`节点 167 \| 边 360 \| 组 18`） | 生成物，随 `build.py` 再生 |

> `routing.md` / `cheatsheet.md` 实测**不含** `167` 字面量（`grep` 无命中），但**若新增节点落进场景路由，需补条目**（内容性变更，非计数）。

### 5.3 🔺 门控级触发点（须补 ADR）

阶段3 的「**新节点 ID 分配规则 + 组归属 + 准入阈值（`partial` 是否可建节点）**」改变**图谱对外契约**（`deliverables.json` 计数、`20-agent-skill` 接口、公开站点结构）→ **命中规模三问 Q1**。
**处置**：阶段3 启动前须产 **ADR-003**（新节点准入与 ID 分配），并过 `gate_architecture.py --kind adr`；**未过不得动结构**。本计划**不代拟**该 ADR（属阶段3 自身产出）。

---

## §6 轨D · 能力包同步

- `20-agent-skill/node-index.md`（167 行索引）、`SKILL.md`、`routing.md`、`cheatsheet.md` 随新节点再生/补条目。
- 源侧（本仓 `20-agent-skill/`）改完后**须重跑安装派生**（`install-skill.py`，装到 `~/.dsh/skills/opencode/architecture-judgment/`），否则 DSH 侧仍是旧包。
- ⚠️ 本会话加载的 skill 来自 `~/.dsh/skills/opencode/architecture-judgment/`（**派生安装副本**），与仓内 `20-agent-skill/` 源侧可能漂移；**改后必须比对两侧**。

---

## §7 风险与对策（含本轮新发现）

| # | 风险 | 等级 | 对策 |
|---|---|---|---|
| 1 | **`claims-<slug>.json` 漏写** → `node-claim-map.json` 无新主张 → G-D1/G-D2 FAIL | **高**（本轮新发现） | §3.1 双落点硬约束；`derive_densify.py --precheck` 前置核查；G-D1 同时查 ledger 与 claim-map |
| 2 | **slug 冲突静默丢主张**（首 slug 优先） | **高**（本轮新发现） | 新主张必须挂到该节点**既有 slug**；precheck 逐节点解析 `record_id` 前缀定 slug |
| 3 | **子 Agent 无 shell 却被要求跑脚本** → 假 PASS / 空转 | **高**（本轮新发现） | §1.7 刚性纪律：一切脚本由主Agent 亲跑；委派 prompt 显式声明「禁止跑脚本」 |
| 4 | **正文幻觉/越界**（改写引入书证不支持内容） | **高** | 决策 #3 强制回写 + W4 层2 保真复核 + G-D1/G-D2 + 主Agent 抽检 ≥20% |
| 5 | **FP 判级**（复现阶段1 的 18.75%） | 高 | 封闭枚举 + 新增 claim 全量第二路复核 + 保守终裁降级口径 |
| 6 | **版权红线**（正文近似原文） | 高 | G-D4 把 ≥20 字子串判据从 `claim` 扩展到**节点正文** + `gate_disclosure.py` 兜底 |
| 7 | **注水**（为凑 2400 字灌水） | 中 | G-D2 注水比机检（每 +200 字 ≥1 claim） |
| 8 | **L8 版式回归**（正文变长撑破版式） | 中 | L8 全量重跑；先小批验证再全量重生 |
| 9 | **`essence` 层工具名回归** | 中 | 方法论专项「层边界」重跑；写入方 prompt 显式禁令 |
| 10 | **同节点并发写冲突** | 中 | 唯一写入方（子Agent 只写 `write-<node_id>.json`，正文由主Agent 合并）；批划分按 slug 分组 |
| 11 | **幂等破坏**（新增脚本引入时钟/非稳定排序） | 高 | 冻结常量 + 稳定排序 + `--check` 自证；严禁回退 `aggregate.py` 日期坑修复 |
| 12 | **`assemble --check` 非 0/0/0**（新报告未声明） | 高 | §3.7 步骤1：先补 `sanitize` + `SCAN_ROOT_FILES`，再 `--apply` |
| 13 | **CI 未跑 G-V/G-D 却未标 SKIPPED** | 中 | §3.7 步骤2 补 SKIPPED 步骤 |
| 14 | **阶段3 重复造节点**（现有节点已含等价概念） | 中 | §5.1 强制去重比对；ADR-003 门控 |
| 15 | **9 个无 direct 锚节点被「顺手」改写** | 中 | G-D5 对账硬拦（越界 0） |

---

## §8 测试与验证策略（判据可信度）

1. **负向测试**：G-D1..G-D5 + G-V9 各构造 ≥1 必 FAIL 负例，确认拦得住（防恒真判据/假绿）。
2. **幂等测试**：`derive_verification.py --check`、`derive_densify.py --check`、`aggregate.py`、`build.py` 连跑两次 → `git diff --exit-code` 为空。
3. **对账测试**：变更集 == 26 节点（G-D5）；overrides 节点集 == ledger 覆盖集（G-V8）。
4. **回归测试**：L1–L8 + 方法论四项 + GR-10（`verified=true` ≥89.22%）。
5. **回滚演练**：确认撤销路径后指纹可回到 `9ae4cc01…`（在私有 `_densify/` 保留的前提下）。
6. **抽样回盘**：主Agent 对 `direct` 断言抽检 ≥20%，对子 Agent 自述一律复算。

---

## §9 待用户决策 / 需要用户提供

| # | 事项 | 选项 | 默认 | 状态 |
|---|---|---|---|---|
| A1 | 计划范围 | 全链路路线图 + 阶段2 细则 / 仅阶段2 / 仅路线图 | —— | ✅ **已裁决**：全链路 + 阶段2 细则 |
| A2 | 计划定稿后是否本会话开工 Build | 本会话开工 / 另立窗口 | —— | ✅ **已裁决**：本会话直接开工 |
| A3 | 节点写入方批大小 | 3 / **4** / 6 节点每批 | **4** | 沿用既有默认 |
| A4 | 轨B 剩余 27 本的**核验顺序** | B1 先（10 本有抽文本）/ 按引用密度 / 暂不启动 | **B1 先** | 待确认 |
| A5 | 轨B 是否与轨A 并行启动 | 并行 / 阶段2 后 | **阶段2 后** | 沿用决策 27 |
| A6 | `report.original.html`（untracked）性质与去留 | 提交归档 / 忽略 / 删除 | **待定** | 待确认 |
| A7 | `direct` 抽检是否需用户参与 | 需要 / **仅主Agent** | **仅主Agent** | 沿用既有默认 |
| A8 | 阶段3 是否本轮启动 | 启动 / **阶段2 后** | **阶段2 后** | 沿用决策 38 |

> **无需用户提供材料**：三本 pilot 语料均在私有层（DDIA 26 MD + CleanArch/SAiP 抽文本），阶段2 无外部依赖。

---

## §10 附：本计划依据的关键实测数据（2026-10-11 回盘复验）

| 指标 | 实测值 | 来源 |
|---|---|---|
| 图谱规模 | 167 节点 / 360 边 / 18 组 / 18 案例 | `methodology-dag.json` |
| **当前指纹** | `9ae4cc01f7b183f9a621997896a9033af6d9ca9ed38fee462077d8604496eba1` | `sha256sum` |
| 基线一致性 | **8/8 文件 SHA-256 与 `stage7-baseline.md` 逐字节一致** | `sha256sum` × 8 |
| 门控 G-V1..G-V8 | **PASS=8 FAIL=0 WARN=0 SKIP=0** | 本轮亲跑 |
| L2 全图审计 | `nodes=167 edges=360 kahn=167/167 errors=0 warnings=0` | 本轮亲跑 |
| L6 覆盖度 | manifest 100.00% / 四向 100.00% / GR-09 35.48% | 本轮亲跑 |
| 核验记录 | 144（`direct 78 / partial 59 / inferred 7 / contradicted 0`） | `verification-ledger.json` |
| 方向分布 | `forward 120 / reverse 24` | 同上 |
| 第二路复核分布 | `passed 78 / disputed 18 / none 48` | 同上 |
| 覆盖节点 | 35（**26 有 direct 锚 / 9 无**） | 脚本统计 |
| 主张拆分表 | 18 节点 / **120 条**主张；**9 个 reverse-only 无拆分** | `node-claim-map.json` |
| 26 节点正文字数 | min 1501 / median 1524 / max 1772；**0/26 落在 [2400,3000]** | `node-content.json` `char_count` |
| 缺口清单 | 28（`coverage_hole 10 / concept_missing 10 / missed_citation 8`） | `reverse-gaps.json` |
| 缺口动作分类 | 新增节点 17（`direct 10` / `partial 7`）/ 新增术语 2 / 补引 7 / 其他 2 | 同上 |
| 已获取书 | **30 本**（P0-01..P2-30，75 文件 / 304MB）；已核验 3 → **剩余 27** | `acquired-manifest.json` |
| 已有抽文本的书 | **11 本**（`has_source_txt: true`） | `structure_snapshots` |
| 公开仓 | `zako-mio/se-architecture-methodology-kg`（main）；`_publish/` HEAD `deda112`，受控 533 文件 | `git -C _publish` |
| 阶段1 FP 率（质检先验） | 18.75%（18/96 direct 判假阳性） | 阶段1 §F.5 |
| 子 Agent 能力（本轮探针） | **无 shell**；有 `read/glob/grep/write/edit/web_*` | 探针子 Agent 回报 |

---

## §11 建议执行顺序（本会话 Build）

1. W0 骨架与契约 + `derive_densify.py --precheck`（主Agent，串行）
2. W1 三路证据展开（并行 ≤5）
3. W2 分批节点改写（并行 ≤5，7 批）
4. W3 合并回写 + 派生 + 聚合（主Agent，串行）
5. W4 双层复核 + 抽检（并行 ≤5）
6. `gate_densify.py` + `gate_verification.py` G-V9 实作 + 负向测试（主Agent）
7. W5 全门控实跑（主Agent，串行）
8. W6 重生 → 装配 → 推送 → Pages/CI 复验（主Agent，串行）
9. 收尾：`stage7p2-baseline.md` + 双版本报告 + 本地归档提交 + 留档询问
