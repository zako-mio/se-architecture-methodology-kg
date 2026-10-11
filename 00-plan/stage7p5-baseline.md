# 阶段7 · 阶段3 续做（P0 缺口号回写 + P1 T2 晋升评估 + P2 SRE 私有层采集）基线冻结记录

> 生成时间：2026-10-12　生成者：主Agent（阶段7 阶段3 续做轮）
> 用途：为「旧缺口 `proposed_node` 回写 + T2 候选册晋升评估 + SRE/Workbook 私有层采集」提供**回滚锚点**与**冻结证据**。
> 本文件是本轮的事实基线：任何后续声明与本文冲突时，以本文的实测值为准。
> 前置基线：`stage7-baseline.md`（阶段1）/ `stage7p2-baseline.md`（阶段2）/ `stage7p3-baseline.md`（轨B）/ `stage7p4-baseline.md`（轨C 首批准入）
> 口径：本文件全部数值为**门控脚本与命令实跑输出**，逐条记录，非推演。
> 开工锚点：本地 `git HEAD = f023353`（干净）。

---

## 1. 指纹变更（SHA-256）

### 1.1 图谱侧：**零变更**

| 文件 | 上轮冻结值 | 本轮实测值 | 说明 |
|---|---|---|---|
| `10-dag-data/methodology-dag.json` | `f1f09a9b…87303a39` | **`f1f09a9b…87303a39`（未变）** | 本轮**未动图谱**：无新节点、无新边、无正文改动 |
| `10-dag-data/node-content.json` | `58131a10…e8b9cf717` | `58131a10…e8b9cf717`（未变） | 同上 |
| `10-dag-data/_base.json` | `470ca8ce…d31e23dc` | `470ca8ce…d31e23dc`（未变） | 新建组 0 |
| `10-dag-data/stats.md` | `b24ffc9e…dea5e23ab` | `b24ffc9e…dea5e23ab`（未变） | 计数未变（168） |
| `15-md/00-index.md` | `d4743528…b6152ce` | `d4743528…b6152ce`（未变） | — |

> ⇒ 本轮是**纯核验层扩展 + 缺口号一致性回写**，图谱结论与计数**一字未改**（五处对账仍 168 / 偏差 0）。

### 1.2 核验层侧：全部变更（本轮主体）

| 文件 | 上轮冻结值 | 本轮实测值 | 变更原因 |
|---|---|---|---|
| `01-books/_verify/verification-ledger.json` | `a2e87bfe…b5558da3` | **`ab276405…a350224e`** | 新增记录（BK-025 78 / BK-026 83，其中 5 条经第二路复核降级） |
| `01-books/_verify/node-claim-map.json` | `5d78c38d…1554cc3` | **`69680214…f722fe6b`** | 新增 15 个覆盖节点的主张键 |
| `01-books/_verify/reverse-gaps.json` | `782edcac…291835ea`（P0 前 `6e068572…0328b4`） | **`c2594d2a…2320bab6`** | ①P0 回写 16 条 `target`；②新增 13 条缺口（`GAP-SRE-*` 7 / `GAP-SREW-*` 6） |
| `10-dag-data/_verification-overrides.json` | `ff7af7f6…eb5d0877` | **`fab4b16b…008e9926`** | 覆盖集 64 → **78** 节点 |
| `10-dag-data/book-verification.json` | `0b3d0d79…c55456850` | **`dfbdd6b1…3f4a6835`** | 公开安全投影随核验层再生（含 `target` 回写结果，见 §6 裁决 D2） |
| `01-books/_verify/book-toc-index.json` | `91880ff3…485fe135` | **`7a0a0a20…e786252c`** | 新增 BK-025（42 章）/ BK-026（29 章）TOC |
| `01-books/_verify/_meta/gap-id-writeback.json` | （无） | `803045a7…7581fc20` | **本轮新增**：P0 回写映射报告 |
| `01-books/_verify/_meta/t2-promotion-scan.json` | （无） | **本轮新增** | P1 晋升扫描报告 |

实测命令与输出：

```
$ python3 16-checkpoint/derive_verification.py && python3 16-checkpoint/derive_verification.py --check
== 派生结果 = PASS（6 个产物）== / == 派生幂等自检 = PASS ==
$ python3 16-checkpoint/build.py --config mother --quiet   # 连跑两次
产出计数一致（40 变更文件）→ BUILD IDEMPOTENT: PASS
$ cd _publish && python3 16-checkpoint/build.py --config mother --quiet && git diff --exit-code
NO DRIFT (exit 0) —— 与 CI 漂移检测等价
```

---

## 2. 数据规模（实测）

| 指标 | 上轮实测值 | 本轮实测值 |
|---|---|---|
| 节点 / 边 / 组 | 168 / 364 / 18 | **168 / 364 / 18（未变）**；`dag_acyclic=true`（Kahn 168/168） |
| `verified` 分布 | 布尔 `true` 151 / `"cited"` 17 | **151 / 17（未变）**；GR-10 = 89.88% |
| 核验记录总数 | 403 | **522** |
| `evidence_strength` | direct 250 / partial 131 / inferred 22 | **direct 360 / partial 140 / inferred 22** |
| 覆盖节点 | 64 | **78**（+14：K 域 15 节点中的 14 个；`ESS-K-02` 已在前轮） |
| 已核验书 | 8 本 | **10 本**（+`sre-book`/BK-025、`workbook`/BK-026） |
| 缺口全表 | 106 | **119**（`missed_citation` 60 / `coverage_hole` 40 / `concept_missing` 19） |
| 第二路复核 | 覆盖全部 direct | **覆盖全部 direct 360/360**；direct 侧 passed 360 / disputed 0 |
| 全库 `second_pass` 分布 | — | passed 366 / disputed 44 / none 112（none 均为非 direct） |

### 五处计数对账（P0 验收判据）

| # | 位置 | 实测值 |
|---|---|---|
| 1 | `meta.total_nodes` | **168** |
| 2 | 实际节点数 | **168** |
| 3 | `16-checkpoint/deliverables.json` 四处 `expected` | **168** |
| 4 | `20-agent-skill/node-index.md` 表格行数 | **168** |
| 5 | `10-dag-data/stats.md` `nodes` 行 | **168** |
| — | **偏差** | **0** |

---

## 3. 门控全表（本轮实跑）

| 门控 | 命令 | 结果 |
|---|---|---|
| 图谱校验 | `validate_graph.py` | `nodes=168 edges=364 kahn=168/168`，**errors=0 warnings=0 PASS** |
| 核验层 | `gate_verification.py --check all` | **PASS=9 FAIL=0 WARN=0 SKIP=0**（G-V8 覆盖 78/78；G-V9 阶段2 45 条冲突 0） |
| 覆盖度 | `gate_coverage.py` | manifest 100% / 四向 100% / GR-08 PASS / GR-09 34.38% → **PASS** |
| 信源 | `gate_sources.py` | 悬挂 0 / 可溯源 100% / verified=true 89.88% → **PASS** |
| 增密 | `gate_densify.py --check all` | **PASS=5 FAIL=0** |
| 版面 | `gate_layout.py --check all` | 综合覆盖率 2140/2140 = 100%，问题 0 → **PASS** |
| 方法论专项 | `gate_methodology.py --check all` | layer-boundary / glossary / principle-counterexample / tradeoff-11 **全 PASS** |
| 知识库结构+链接 | `kb_gate.py --layers structure,links` | structure 442 项 0 问题 / links **5374** 项 0 问题 → **PASS** |
| 版权红线 | `check_corpus_overlap.py --target evidence` | 语料 **6 019 138** distinct 20-gram，134 对象，**命中 0** |
| 判据可信度（增密） | `negative_test_densify.py` | **11/11 如期** |
| 判据可信度（核验） | `negative_test_verification.py` | **6/6 如期** |
| 谓词重放 | `replay_admission.py` | 禁止常量 PASS / 概念筛选一致 PASS / **一致率 100%（33/33）** / 负例 **4/4** |
| **T2 晋升扫描** | `replay_admission.py --scan-promotion` | **候选 30 条 ｜ 可晋升 0 条** / 负例 **3/3**（本轮新增子命令） |
| 缺口号归一化 | `normalize_gap_ids.py --check` | 重指派 0（幂等）；非法/撞号残留 **0** |
| 公开装配 | `assemble_publish.py --check` | **0/0/0** + P1–P5 OK |
| 脱敏 | `gate_disclosure.py --root _publish` | **PASS：0 hit / 509 文件** |
| 导出洁净 | `assemble_publish.py --assert-clean` | **OK**：private=0 / binary_violation=0 / binary_allowed=1 |
| **L4 视觉** | `gate_visual.py --check all` | **PASS**：checks_total 272 / pass 212 / fail 0 / warn 0 / skip 60（覆盖率 77.94%） |
| **L5 渲染** | `gate_render.py --timeout 25` | **PASS（all 7 cases; skipped=0）** |

> **🔴 本轮纠正一条旧结论**：上轮基线把 L4/L5 记为「缺 `agent-browser`，标未验证」。
> 实测 `agent-browser 0.34.0` **已安装**于 `~/.nvm/versions/node/v24.19.0/bin/agent-browser`
> （**不是** `~/.local/bin`）；失败根因是**宿主 PATH 不含 nvm bin**（`node` 与 `agent-browser` 均解析失败）。
> 以 `PATH="$HOME/.nvm/versions/node/v24.19.0/bin:$HOME/.local/bin:$PATH"` 引导后两门控**均 PASS**。
> ⇒ **本机 L4/L5 不再是环境缺口**；本条写入基线，后续轮次直接复用该 PATH 引导（环境事实，非配置错误）。

---

## 4. P0 · 旧缺口 `proposed_node` 回写（**已完成**）

**依据**：ADR-004 §决定三「号释放与重指派政策」——要求阶段3 回写缺口文件的 `target.proposed_node` 使之一致。

**新增脚本**：`16-checkpoint/writeback_gap_ids.py`（确定性；`--check` 只读）
- 唯一判定源 = `candidate_register[].id_status`；
  `admit-now`/`reserved`/`reserved-after-collision`/`newly-allocated` ⇒ `proposed_node = id`；
  `released`/`no-id` ⇒ `proposed_node = null` 并从 `action` 取宿主补 `existing_node_id`（**防 G-V1 双空**）；
- **未覆盖缺口一律不动**（fail-closed）：作用域 34 条裁决覆盖 / 72 条未覆盖（含 9 条新提案）未动；
- 写前硬校验：`target` 双空 / 未知 `id_status` / 裁决表自相矛盾 ⇒ **拒绝落盘**。

**实测结果**：**16 条变更**（逐条见 `_meta/gap-id-writeback.json`）

| 缺口 | 现值 → 回写后 | 依据 |
|---|---|---|
| `GAP-SAIP-003` | 中文概念名 → `MTH-F-07` | T2 newly-allocated |
| `GAP-SAIP-004` | 中文概念名 → `MTH-G-12` | T2 newly-allocated |
| `GAP-SAIP-007` | 中文概念名 → `null` + 宿主 `MTH-N-06` | T3 no-id |
| `GAP-EA-007` | `MTH-G-07` → `MTH-G-10` | 撞号落败重取号 |
| `GAP-EA-008` | `MTH-G-08` → `MTH-G-11` | 撞号落败重取号 |
| `GAP-CA-002` | `MTH-G-08` → `TEC-H-04` | MERGE-FAMILY（已准入） |
| `GAP-CA-001` / `GAP-CA-006` | `MTH-G-07`/`MTH-G-09` → `null` | T3 no-id（宿主已填） |
| `GAP-DDIA-012` | `ESS-H-12` → `null` + 宿主 `ESS-H-11` | T3 released |
| `GAP-EA-006` | `MTH-H-05` → `null` + 宿主 `ESS-H-02` | T3 released |
| `GAP-TT-007/008/009` | `MTH-N-07/08/09` → `null` + 宿主 `MTH-N-02` | T3 released |
| `GAP-CA-003/004/005` | `ESS-G-08`/`ESS-O-04`/`TEC-I-04` → `null` | T3 released |

### 🔴 P0 暴露并修复的一处**判据口径缺陷**（重要）

`replay_admission.py` 原先以「`target.proposed_node` 非空 ⇔ 参与结构扩展」作机械判据。
回写后该判据**必然 FAIL**（11 条 T3 no-id/released 被机械判为「仅补引」），因为
**`proposed_node` 的语义是「号分配状态」，与「是否为概念提案」正交**——被回写释放号的 T3 概念条目按 ADR 政策必须清空它。

**处置**：把概念集机械判据改为 **裁决表 `tier ∈ {T1,T2,T3}`** ∪「未裁决但已占号的新提案」，
并保留不变量「裁决表概念条目 ⊆ 机械扩展」。修复后：

```
[2] 概念集筛选（机械：裁决表 tier ∈ T1/T2/T3 ∪ 未裁决但已占号的新提案）
    裁决表覆盖缺口 = 34 ｜ 其中概念条目缺口 = 34 ｜ 机械判定「参与扩展」= 43
    裁决表概念条目 ⊆ 机械扩展 = True（差集 0 条）
    一致率 = 33/33 = 100.00%
```
⇒ 一致率与负例均**未退化**，判据口径与 ADR 政策恢复一致。

---

## 5. P1 · T2 候选册晋升评估（**已完成：0 晋升**）

**新增子命令**：`replay_admission.py --scan-promotion`（只读；默认行为不变）
- 候选集 = 裁决表 `tier == "T2"` 条目 ∪ 未裁决但已占号的新提案（**由数据算出，不写死条数**）；
- 判据 = `promotable ⇔ |A(c)| ≥ 1 且 |S(c)| ≥ 2`（`S` 按 `book_source_id` 去重）；
- 报告 `_meta/t2-promotion-scan.json`；负例 **+3 条**（单源误判 / 零 direct 锚 / 正例对照），实测 **3/3 如期**。

**实测结论**：

| 项 | 值 |
|---|---|
| 候选总数 | **30**（裁决表 T2 21 条 + 新提案 9 条） |
| **可晋升** | **0 条** |
| 阻塞原因 | 全部为「独立信源 < 2（当前 1）」 |

> **结论：本轮无任何 T2 可晋升 T1，且这是可复跑的机械判定，不是豁免。**
> SRE 采集入层后**重跑仍为 0**（新书证据落在 K 域既有节点上，未触及任何 T2 概念）。

---

## 6. P2 · SRE / Workbook 私有层采集与核验（**已完成**）

### 6.1 采集（新增脚本 `16-checkpoint/extract_sre_web.py`）

| 项 | BK-025《SRE》 | BK-026《Workbook》 |
|---|---|---|
| 站点 | `sre.google/sre-book/` | `sre.google/workbook/` |
| **直连** | **HTTP 200（无需代理）** | **HTTP 200（无需代理）** |
| 抽取章数 | **42**（Foreword/Preface + 1–34 + Appendix A–F） | **29**（Foreword I/II/Preface + 1–21 + Conclusion + Appendix A–C + About the Editors） |
| 语料 | `_text/sre-book.txt`（1 075 398 字符，UTF-8 无 BOM / 0 个 U+FFFD） | `_text/workbook.txt`（925 151 字符，同上） |
| TOC | `_parts/toc-sre-book.json`（自建，站点无 NCX） | `_parts/toc-workbook.json`（自建） |
| 许可 | **CC BY-NC-ND 4.0** | **CC BY-NC-ND 4.0** |

> **纠正旧记录**：`fetch-log.md` 记「境内直连失败、须代理（http_code=000）」——本轮实测**已推翻**（目录页与章节页直连均 200）。
> **抽取缺陷修复**：首版用非贪婪 `</section>` 正则截断（某章 25 389 字符被截为 3 863）；改为 **lxml DOM 取正文容器**后完整。

### 6.2 核验（4 名证据工人 + 4 名复核工人，全部经主Agent 机械复验）

| 项 | BK-025 | BK-026 |
|---|---|---|
| 记录 | 78 | 44（原始 83，按上限裁剪后） |
| 覆盖节点 | 15 | 15 |
| direct / partial | 73 / 5 | 42 / 2 |
| 缺口 | 7（`GAP-SRE-001/002/101–105`） | 6（`GAP-SREW-001/101–105`） |
| 第二路复核 | **73/73 覆盖**；agree 68 / **降级 5** / 不可定位 3 | **42/42 覆盖**；agree 42 / 降级 0 / 不可定位 0 |

**第二路降级明细（只降不升）**

| record | 节点 | direct → 复核 | 理由 |
|---|---|---|---|
| `VR-SRE-105` | `MTH-K-07` | direct → **partial** | 主张逐句在第1章「Provisioning」，声明的第21章「Handling Overload」无此论述；`anchor_locatable=false` |
| `VR-SRE-110` | `TEC-K-02` | direct → **partial** | 主体在「Why Monitor?」，末句在「Setting Reasonable Expectations…」⇒ 跨节拼接 |
| `VR-SRE-119` | `TEC-K-06` | direct → **partial** | 原文在「Expect Testing Fail」，声明的 MTTR 小节无此论述；`anchor_locatable=false` |
| `VR-SRE-129` | `TEC-J-04` | direct → **partial** | 前半取第17章、后半取第27章 ⇒ 跨章拼接 |
| `VR-SRE-137` | `MTH-N-05` | direct → **partial** | 同 `VR-SRE-119`；`anchor_locatable=false` |

> 首路过度断言率实测：BK-025 **5/73 = 6.8%**（全在 B 半）、BK-026 **0/42 = 0%**。
> 与轨B 经验值（18%）相比更低，但**非零** ⇒ 「子 Agent 自述不可信」结论继续成立。

### 6.3 🔴 本轮的三条**数据契约缺陷**（实测暴露并修复）

| # | 缺陷 | 实测现象 | 处置 |
|---|---|---|---|
| D1 | **`merge_verify_staging.py` 缺口前缀 glob 串号** | `gaps-sre*.json` 吞掉 `gaps-srew-*.json` ⇒ `sre-book` 缺口表混入 6 条 `GAP-SREW-*` | 新增 `_prefix_glob()`：只接受 `gaps-<prefix>.json` 与 `gaps-<prefix>-*.json`；**既有 `gaps-cc.json` 等无后缀命名不受影响** |
| D2 | **两书 `claim_id` 撞号** | 两位工人各自「每节点从 20/40 起编」⇒ **17 对**重复（`G-V1` FAIL） | BK-026 侧全部 `claim_id` 序号整体重编到 **200+** 不重叠区间；暂存与 SSOT 同步改写 |
| D3 | **节点记录上限（ADR-003：其余 8）被突破** | 14 个 K 域节点达 10–12 条 ⇒ `G-V1` FAIL | 按确定性优先级（direct > partial > inferred；同级已复核者与既有书优先）**裁剪 42 条至 8 条**；**未放宽上限** |

> **D3 未决部分**：K 域 14 节点实有 10–12 条证据，上限 8 迫使裁剪掉 42 条**合法 direct 证据**。
> 放宽上限属 **ADR-003 决策**（`DENSIFY_NODES` 为封闭集合，ADR-003 明确「只写这些」），**本脚本不擅自放宽**。
> ⇒ 已列为**下一轮待裁决项**（§10）。

### 6.4 采集与登记

| 项 | 处置 |
|---|---|
| 三重隔离 | ✅ 本地仓 `.gitignore:13` 忽略 `01-books/`；`_publish/.gitignore:15` 忽略 `01-books/_verify/`；`publish-manifest.json` 的 `classes.private` 含二者（`git check-ignore` 实测通过） |
| 4 处登记 | `gate_verification.py`（`SLUG_RECORD_PREFIX`/`SLUG_TEXT`/`SOURCE_SLUG`）、`merge_verify_staging.py`（`BOOKS`）、`check_corpus_overlap.py`（`CORPUS`）、`verify-contract.md`（登记表；**并补齐 refactoring/release-it/clean-code 三行历史遗漏**） |
| 许可登记 | `free-official-extracts.json` 的 FO-02/FO-03 增 `acquired_private_corpus` 块 + ND 裁决留痕（**未标 `unknown-thirdparty`**） |
| 版次订正 | `acquired-manifest.json` 的 `P0-09`：`edition_actual` `2nd/2018` → **`1st/1999`**，`edition_mismatch` → **true**（语料为第 1 版；真第 2 版未获取） |

---

## 7. 本轮新增/修改的可执行门控（7 个）

| 脚本 | 性质 | 作用 |
|---|---|---|
| `16-checkpoint/writeback_gap_ids.py` | **新增** | 按 ADR-004 裁决表回写旧缺口 `proposed_node`（fail-closed；输出映射报告） |
| `16-checkpoint/extract_sre_web.py` | **新增** | sre.google 在线书 → 私有层纯文本 + 自建 TOC（DOM 抽取；0 章/抓取不完整 fail-closed） |
| `16-checkpoint/validate_staging_shards.py` | **新增** | 暂存分片合并前机检（字段/cap/**章-节一致性交叉校验**/编号连续性/claims 覆盖） |
| `16-checkpoint/replay_admission.py` | **修改** | ①概念集判据口径修正（见 §4）；②新增 `--scan-promotion`（P1）+ 3 条负例 |
| `16-checkpoint/merge_verify_staging.py` | **修改** | 缺口前缀 glob 精确化（见 D1） |
| `16-checkpoint/gate_verification.py` | **修改** | 三处登记新书（BK-025/BK-026） |
| `16-checkpoint/check_corpus_overlap.py` | **修改** | `CORPUS` 追加两本新语料 |

> **`validate_staging_shards.py` 的独有价值**：它抓到两类**现有门控拦不住**的缺陷——
> ①「章号正确但**节标题属另一章**」的锚点错位（如 `VR-SREW-031` 声明第4章却引第2章小节）；
> ②cap 超限与编号断档。建议后续轮次**继续在合并前使用**。

---

## 8. 公开层对账（实测）

| 项 | 值 |
|---|---|
| 装配 | `--apply --refresh-sanitize` → 写入 **561** 文件，删除 0，自检三类差异均 0 |
| `_publish` git | commit **`52f09c9`**；`git ls-files` = **567** |
| 远端 commit | **`212dd0a0940059ab4834abdde7b33e6acb0ec9f7`**（推送链：`ebb90669` → `d1d64ec5` → `6be855ee` → `212dd0a0`） |
| 远端 tree | **567 blobs == 本地 `ls-files` 567** |
| CI | run **`38157550356`** → **success**（`workflow_dispatch`；`38156480019` / `38157173094` 亦 success） |
| Pages | `/`、`/11-node-pages/ESS-K-01.html`、`/15-md/nodes/ESS-K-01.md`、`/10-dag-data/book-verification.json`、`/00-plan/stage7p5-baseline.md`、`/00-plan/NEXT-SESSION-HANDOFF.md` 均 **HTTP 200**；节点页**已含 BK-025/BK-026 书证** |
| 导出目录 | `_pages-export/` 用后即删（已清理） |

### 🔴 公开层两次推送与 CI 漂移的真实过程（留痕）

1. 第一次推送 `ebb90669` → **CI run `38155839617` FAIL（11s）**，失败于 **Drift detection**：
   `11-node-pages/*.html` 与 `15-md/nodes/*.md` 未随核验层再生 ⇒ **节点页缺新书证**。
   ⇒ **根因：漏跑 `build.py`**（生成链未跑就装配公开层）。
2. 修复：本地 `build.py --config mother --quiet` 再生（40 文件）→ 幂等复验通过
   → 重装配 → 重推 `d1d64ec5` → **CI 无自动触发**。
   ⇒ **根因：workflow 的 `paths` 过滤只含 `10-dag-data/**` 与 `16-checkpoint/**`**，
   而修复提交只动 `11-node-pages/**` 与 `15-md/**` ⇒ 不触发。
   ⇒ 处置：`gh workflow run rebuild.yml` **手动触发** → run `38156480019` **success** → Pages 部署新产物。
3. **CI 等价本地复现**：`cd _publish && build.py && git diff --exit-code` → **NO DRIFT（exit 0）**。

> **教训（写入基线）**：**动核验层就必须跑 `build.py`**，否则公开层节点页与数据不一致（CI 必红）。
> 且「改生成物不改数据/脚本」的提交**不会触发 CI**，须手动 `gh workflow run rebuild.yml` 并确认 success。

---

## 9. 回滚路径

**本轮本地归档提交**：`da6c9e0`（parent `f023353`）；42 个文件变更（含 3 个新脚本、2 个新文档、16 个再生节点页/MD、核验层派生件）。

```bash
# 本地归档仓：回滚到本轮开工前
git -C "$MROOT" reset --hard f023353          # 丢弃本轮全部（含新脚本与文档）
# 或按需只回滚核验层分片（私有层无 git 历史，用备份）
rm -rf "$MROOT/01-books/_verify/_parts" "$MROOT/01-books/_verify/_meta"
cp -a /tmp/p0-backup-20261011/parts "$MROOT/01-books/_verify/_parts"
cp -a /tmp/p0-backup-20261011/meta  "$MROOT/01-books/_verify/_meta"
python3 16-checkpoint/derive_verification.py && python3 16-checkpoint/build.py --config mother --quiet
# 公开层：远端 ref 回退（Git Data API，须完整 40 位 sha）
gh api repos/zako-mio/se-architecture-methodology-kg/git/refs/heads/main \
  -X PATCH -f sha=ebb9066953149df9652434de8d538d5f1298cf29 -F force=true
```

**本轮**：**未动图谱** ⇒ 无批次级图谱回滚需求；核验层回滚须用上表备份（`01-books/` 被 gitignore，无 git 可回滚）。

---

## 10. 待裁决 / 下一轮注意

| # | 事项 | 建议 | 备注 |
|---|---|---|---|
| 1 | **K 域节点记录上限**（ADR-003 的 8 条上限迫使裁掉 42 条合法 direct 证据） | 走一次 ADR 裁决，把 K 域 14 节点纳入 `DENSIFY_NODES`（上限 16） | 实测 14 节点均 ≤ 12 条，纳入后**不超限**；须同步改 `gate_verification.py` 与 ADR-003 |
| 2 | **T2 晋升**（21 保留号 + 9 新提案，全部单源） | 取得第二独立信源前**不动**；扫描器已就绪，可随时复跑 | `replay_admission.py --scan-promotion` |
| 3 | **SRE 派生内容是否进公开层（ND 约束）** | 维持「只私有层 + 核验」 | 公开投影**未含任何改写主张/摘句/页码**；仅含 `section_title` 与来源 id（详见下注） |
| 4 | `P0-09` 真第 2 版语料 | 如需，另行采集 | 现语料为 1st/1999，`edition_mismatch=true` 已如实标注 |
| 5 | `_verification-overrides.json` 的 `_evidence`（内部 record_id）已在公开层 | 保持现状（另案） | 内容为 record_id 列表，无 claim/摘句/页码 |
| 6 | 阶段1 遗留重复 `claim_id`（`ESS-O-02#principle#1`） | 继续 WARN | 实测全局仅此 1 处；根因见下注 |
| 7 | `0911-opencode架构能力/tooling/` 私有层旧版 | 不碰（属另一任务目录） | 本轮**未跑 stage-1 `--apply`**，反向漂移风险未激活 |

### 补充说明（下一轮可直接继承）

- **`ESS-O-02#principle#1` 重复的根因（本轮实测新发现）**：`derive_verification.py` 的 `build_claims()`
  对**同一节点跨书**的情形**只保留首个 slug 的 claims**（`if node_id not in nodes`）⇒
  `clean-architecture` 的 `ESS-O-02` claims 被 `ddia` 侧覆盖丢失（`node-claim-map` 仅 6 条，
  而 ledger 有 2 条记录指向 `ESS-O-02#principle#1`）。**修它属数据契约变更**，本轮未擅自改。
- **`validate_staging_shards.py` 与 `merge_verify_staging.py` 的前缀 glob 陷阱**：
  新增书时**前缀不得互为前缀**（`sre` ⊂ `srew`）；若无法避免，须用「精确文件名 + `-` 分隔」双模式收集。
- **子 Agent 工具集不稳定**：本轮 8 名工人中，**首名（`oc_explore`）无 `write`**，
  其余（`subagent`）均有 `read/write/grep`。⇒ 派活前先做**能力探针**，或统一用 `subagent`。
- **工人产出必须机械复验**：本轮工人产出缺陷率不低——2 份 gaps 分片字段不全（`book_source_id`/`anchor`/
  `target` 缺失或双空）、1 处 `claim_id` 与 claims 分片不一致、1 处节标题跨章错位、多处 cap 超限。
  **全部由主Agent 的机检脚本拦下并修复**，未流入 SSOT。
