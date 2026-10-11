# 阶段7 · 阶段3（轨C 首批准入 + 轨B 续做三本）基线冻结记录

> 生成时间：2026-10-11　生成者：主Agent（阶段7 阶段3 执行轮）
> 用途：为「轨C 阶段3 首批准入 + 轨B 续做 BK-021/BK-024/BK-020」提供**回滚锚点**与**冻结证据**。
> 本文件是本轮的事实基线：任何后续声明与本文冲突时，以本文的实测值为准。
> 前置基线：`stage7-baseline.md`（阶段1）/ `stage7p2-baseline.md`（阶段2）/ `stage7p3-baseline.md`（轨B）。
> 口径：本文件全部数值为**门控脚本与命令实跑输出**，逐条记录，非推演。

---

## 1. 指纹变更（SHA-256）

| 文件 | 轨B 冻结值（b11eae6c 轮） | 本轮实测值 | 变更原因 |
|---|---|---|---|
| `10-dag-data/methodology-dag.json` | `b11eae6c0793e08e13f48184c92d42e98150ba6c738cba1ffe6c4bfd6c197789` | **`f1f09a9beaef8603586cbd66b041eee0c7460d07592e9e4db658bc7c87303a39`** | 新增 `TEC-H-04` + 4 条边；10 个节点 `review_date` 更新；`CAS-X-04` `verified` `"cited"`→`true` |
| `10-dag-data/node-content.json` | `93813c864ab8be2e3bd46ab0fbdc39645ae83800f2b1c8e36c5a4371cddb299c` | **`58131a10994f5cc9165941380baf92ed6c83abcc25441e2a55caef3e8b9cf717`** | 新增 `TEC-H-04` 内容条目（`node_count` 167→168） |
| `10-dag-data/_base.json` | `470ca8cec54bf9b003790d8cf45d929f440f66c8574826ebd522f974d31e23dc` | `470ca8cec54bf9b003790d8cf45d929f440f66c8574826ebd522f974d31e23dc`（**未变**） | 本轮**未动骨架**（新建组数 0） |
| `01-books/_verify/verification-ledger.json` | `717073efb1fe53b2c297ff14ad27158573be27841fb18aed851a127280ffec46` | **`a2e87bfe13a1dc8503f50020cc8f975345adb2f6dc35864a8e4751edb5558da3`** | 新增 62 条记录（`VR-REF-*` 24 / `VR-RI-*` 24 / `VR-CC-*` 14），其中 3 条经第二路复核降级 |
| `01-books/_verify/node-claim-map.json` | `b2e5f4b2434ae2989cafeaf3dc175403e30190a061ac1977cee4c6e0fe605265` | **`5d78c38dbaab8d14a0689b36d9377fc7605a11e27a93bb44d046acdbb1554cc3`** | 新增 7 个覆盖节点的主张键（62 条） |
| `01-books/_verify/reverse-gaps.json` | `ab6aaedfe01935c81f535095ad9b25f77677de49d521da1e2020e53fcfc9b2ea` | **`6e068572fede09dc2b1bb66f2081635eda819cba4cc402ba81ac793d880328b4`** | 缺口 60→**106** 条（新增 46）；5 处提案号按 ADR-004 重指派 |
| `10-dag-data/_verification-overrides.json` | `b90906162993649327bc71a744e690c7c15ebfc2a55d518d2a09b0b564ab5656` | **`ff7af7f6a1d1bbdbcad1ba1bfa6444d91f3c99256a2b07b811ee0278eb5d0877`** | 覆盖集 57→**64** 节点 |
| `10-dag-data/book-verification.json` | `eee5a83b54405d756cbc456687bcbb6dfa57409eb0766af13409a1e9873c25fc` | **`63673b23ad33e82cb2dbf89f9d354c8402348b276f6173c3f3c8f317039ad505`** | 公开安全投影随核验层再生 |
| `01-books/_verify/book-toc-index.json` | `8dd456ed769e40fe16a85705f7be54593347295ded84a185d5024d282cfb590b` | **`91880ff3ff7ab78a70d59789b7fbfe3b83c78a51eb9e238a15535240485fe135`** | 新增 3 本书 TOC（BK-021 / BK-024 / BK-020） |

其余派生件：`10-dag-data/stats.md` = `b24ffc9e68690aed3471bf7ceb04d2399821f001968c606607286fcdea5e23ab`；
`15-md/00-index.md` = `d4743528ed8e297a11a6418277bcf5a658de517b334d6d0bce38b36afb6152ce`。

实测命令与输出：

```
$ python3 16-checkpoint/aggregate.py   # 连跑两次
H1=f1f09a9b…  H2=f1f09a9b…   → AGGREGATE IDEMPOTENT: PASS
$ python3 16-checkpoint/build.py --config mother --quiet   # 连跑两次
39 变更文件数不变          → BUILD IDEMPOTENT: PASS
$ python3 16-checkpoint/derive_verification.py --check
== 派生幂等自检 = PASS ==
```

> **指纹变更性质**：`git diff -U0` 字段级统计显示 `methodology-dag.json` 仅 **10 行 `review_date`** + **1 行 `verified`**
> （`CAS-X-04`：`"cited"` → `true`），无任何 `confidence` 改动、无既有节点正文改动。
> ⇒ 本轮轨B 是**纯证据层扩展 + 1 个案例节点状态提升**，未改动任何既有结论。

---

## 2. 数据规模（实测）

| 指标 | 轨B 实测值 | 本轮实测值 |
|---|---|---|
| 节点 / 边 | 167 / 360 | **168 / 364**（+`TEC-H-04` +4 边），`dag_acyclic=true`（Kahn 168/168） |
| 组 / 横切主题 / 案例 | 18 / 3 / 18 | **18 / 3 / 18**（**新建组 0**） |
| 层分布 | essence 51 + methodology 67 + technology 31 + case 18 | essence 51 + methodology 67 + **technology 32** + case 18 |
| `verified` 分布 | 布尔 `true` **149** / `"cited"` **18** | 布尔 `true` **151** / `"cited"` **17** |
| `confidence` 分布 | `high` 151 / `medium` 16 | `high` 151 / `medium` 16（**零翻转**） |
| `verified=true` 占比（GR-10） | 149/167 = 89.22% | **151/168 = 89.88%**（阈值 80%，PASS） |
| 可溯源率 | 167/167 = 100.00% | **168/168 = 100.00%**（PASS） |

> ⚠️ **约定变更（须留意）**：`"cited"` 由 18 降为 17 —— `CAS-X-04`（案例节点）因本轮取得 2 条 `direct` 书证记录，
> 按 ADR-002 的派生规则（`≥1 direct` 且 `0 contradicted` ⇒ `verified=true`）翻转为 `true`。
> ADR-002 未对案例层作专门裁决，故该翻转是机械派生的结果；**基线（阶段1）曾把「零翻转」列为保守性证据，本轮打破该性质**，特此留痕。

### 五处计数对账（P0 验收判据）

| # | 位置 | 实测值 |
|---|---|---|
| 1 | `meta.total_nodes` | **168** |
| 2 | 实际节点数 | **168** |
| 3 | `16-checkpoint/deliverables.json` `:9` `:10` `:16` `:23` | **168**（4 处） |
| 4 | `20-agent-skill/node-index.md` 表格行数 | **168** |
| 5 | `10-dag-data/stats.md` `nodes` 行 | **168** |
| — | **偏差** | **0** |

---

## 3. 核验层规模（实测）

| 指标 | 轨B | **本轮** | 说明 |
|---|---|---|---|
| 记录总数 | 341 | **403** | +62（`VR-REF-001..024` / `VR-RI-001..024` / `VR-CC-001..014`） |
| `evidence_strength` | direct 199 / partial 121 / inferred 21 | **direct 250 / partial 131 / inferred 22** | 3 条经第二路复核降级 |
| 覆盖节点 | 57 | **64** | +7 |
| `contradicted` | 0 | **0** | 无矛盾证据 |
| 缺口全表 | 60 | **106** | +46（`missed_citation` 56 / `coverage_hole` 34 / `concept_missing` 16） |
| 已核验书 | 5 本 | **8 本** | +`refactoring` `release-it` `clean-code` |
| 第二路复核 | 覆盖全部 direct | **覆盖全部 direct（54/54 = 100%）** | agree 51 / 降级 3 |

**第二路复核降级明细（保守终裁，只降不升）**

| record | 节点 | 首路 → 复核 | 理由 |
|---|---|---|---|
| `VR-CC-013` | `ESS-H-06` | direct → **inferred** | 声明锚点 6.2 只论对象/数据结构反对称性，全节及全书无「继承与组合的取舍」论述；`anchor_locatable=false` |
| `VR-RI-006` | `ESS-K-02` | direct → **partial** | 主张前半出自第 3 章末与第 5 章章首，声明的 `Wrapping Up` 小节只支持后半，需跨节拼接 |
| `VR-RI-012` | `MTH-K-06` | direct → **partial** | 三类注入与两类弱点实际在同章更早的 `Injecting Chaos` 小节，声明节位错位（章号 17 正确） |

> 首路过度断言率实测：REF **0/20**、RI **2/24**、CC **1/10** ⇒ 合计 **3/54 = 5.6%**（轨B 经验值 18%，本轮更低）。

---

## 4. 门控全表（本轮实跑）

| 门控 | 命令 | 结果 |
|---|---|---|
| 图谱校验 | `validate_graph.py` | `nodes=168 edges=364 kahn=168/168`，**errors=0 warnings=0 PASS** |
| 核验层 | `gate_verification.py --check all` | **PASS=9 FAIL=0 WARN=0 SKIP=0**（G-V8 覆盖 64/64；G-V9 阶段2 45 条冲突 0） |
| 覆盖度 | `gate_coverage.py` | manifest 100% / 四向 100% / GR-08 PASS / GR-09 11/32=34.38% → **PASS** |
| 信源 | `gate_sources.py` | 悬挂 0 / 可溯源 100% / verified=true 89.88% / disputed 标注 PASS |
| 增密 | `gate_densify.py --check all` | **PASS=5 FAIL=0**（G-D3 全局破界 0；G-D5 值翻转 0、其余节点改动 0） |
| 版面 | `gate_layout.py --check all` | 综合覆盖率 2140/2140 = 100%，问题 0 → **PASS** |
| 方法论专项 | `gate_methodology.py --check all` | layer-boundary / glossary / principle-counterexample / tradeoff-11 **全 PASS** |
| 知识库结构+链接 | `kb_gate.py --layers structure,links` | structure 442 项 0 问题 / links 5342 项 0 问题 → **PASS** |
| 版权红线 | `check_corpus_overlap.py --target evidence` | 语料 4 389 557 distinct 20-gram，134 对象，**命中 0** |
| 判据可信度（增密） | `negative_test_densify.py` | **11/11 如期** |
| 判据可信度（核验） | `negative_test_verification.py` | **6/6 如期** |
| **谓词重放** | `replay_admission.py` | 禁止常量 PASS / 裁决表 ⊆ 机械扩展 / **一致率 100%（33/33）** / 负例 **4/4** |
| 缺口号归一化 | `normalize_gap_ids.py` | 作用域 72 新缺口 / 跳过 34 旧缺口；**5 处重指派**；非法/撞号残留 **0** |
| 公开装配 | `assemble_publish.py --check` | **0/0/0** + P1–P5 OK |
| 脱敏 | `gate_disclosure.py --root _publish` | **PASS：0 hit / 508 文件** |
| 导出洁净 | `assemble_publish.py --assert-clean` | **OK**：private=0 / binary_violation=0 / binary_allowed=1 |
| **L4 视觉** | `gate_visual.py --check all` | **SKIP**（缺 `agent-browser`，**不计入 PASS**） |
| **L5 渲染** | `gate_render.py --timeout 25` | **FAIL(env)**（缺 `agent-browser`，**不得伪装 PASS**） |

> `skipped ≠ PASS`：L4/L5 本机环境缺口，如实标注未验证。

---

## 5. 公开层对账（实测）

| 项 | 值 |
|---|---|
| 装配 | `--apply --refresh-sanitize` → 写入 556 文件，删除 0，自检三类差异均 0 |
| `_publish` git | commit `8e59d37`；`git ls-files` = **562** |
| 远端 commit | **`2319cede5603a201384e8f5622762f16c43e97c3`**（parent `ce39c6353938`） |
| 远端 tree | `675bf8a0e1265f8580f43d5628277f010a78d5f8`，**562 blobs == 本地 `ls-files` 562** |
| CI | run `38146381308` → **success** |
| Pages | `/`、`/11-node-pages/TEC-H-04.html`、`/15-md/nodes/TEC-H-04.md`、`/10-dag-data/methodology-dag.json` 均 **HTTP 200** |
| 导出目录 | `_pages-export/` 用后即删（已清理） |

---

## 6. 能力包派生（P2，实测）

**两段派生链（本轮厘清，接力文档只写了第一段）**

```
20-agent-skill/  ──[install-skill.py]──▶  ~/.config/opencode/skills/architecture-judgment/
   （仓内源侧，含 <MISSION_ROOT> 占位符）        （opencode 侧，占位符替换为绝对路径 + 注入 _private/）
                 ──[~/.dsh/skills/opencode/install.py]──▶  ~/.dsh/skills/opencode/architecture-judgment/
                                                              （DSH 侧，含 description-trim / coupling-rewrite / adapt-note）
```

| 项 | 结果 |
|---|---|
| `install-skill.py --dry-run --force` | 仅 20 行差异（计数 + TEC-H-04 条目），11 文件未变 |
| `install-skill.py --apply --force` | 写入 17 文件（更新 6 / 未变 11），`_private/CRITERIA.md` 保留 |
| DSH `install.py` | 46 skills 派生成功 |
| DSH `reconcile.py`（完整） | **PASS：all reconciliation checks passed**（46 skills + resources 逐字节可复现，0 problems） |
| 两侧比对 | `20-agent-skill/` 与 `~/.config/opencode/…/` 路径归一后**逐字节一致** |

### 🔴 本轮发现的两处**反向漂移**（已无损处置，务必继承）

1. **内容反向漂移**：`~/.config/opencode/skills/architecture-judgment/` 含仓内源侧**没有**的 0916 任务内容
   （规模三问定档、`architect-worker` 获放行门控脚本、ledger 回报通道、最小补丁续跑、`_private/CRITERIA.md` 引用）。
   **直接 `install-skill.py --apply` 会覆盖丢失这些内容**。
   ⇒ 处置：**三方合并**（base = `a595722` 源侧 / ours = 本轮源侧 / theirs = 目标侧路径归一后），
     5 个文件有反向漂移（`SKILL.md` / `checklist.md` / `routing.md` / `workflow.md` / `integrations/openspec-design.md`），
     其中 `SKILL.md` 有 1 处冲突（保留目标侧 bullet + 采用本轮计数 32）已人工解；**零丢失**。
2. **私有层反向漂移**：DSH 侧 `_private/{gate_architecture.py, local-bindings.json}` 比 `0911-opencode架构能力/tooling/`
   **更新**（54 235 B vs 30 589 B；含 `GATE_LEDGER` / `ARTIFACT_ROOT`），来源为
   `2026-10/1011-deepseek harness-提示词迁移工程-从opencode/_build/opencode-port/_out/architecture-judgment/_private/`。
   ⇒ 处置：把 1011 构建产物回植到 `~/.config/opencode/…/_private/`，再重跑 DSH 派生 ⇒ `reconcile` 幂等通过。

> ⚠️ **遗留风险（未修，须下一轮注意）**：`install-skill.py`（0911 tooling）的 `PRIVATE_FILES` 仍会把
> **旧版** `_private/*` 覆盖到 opencode 侧。**再次运行 stage-1 `--apply` 会重新引入该降级**。
> 根治办法：更新 `0911-opencode架构能力/tooling/{gate_architecture.py,local-bindings.json}` 为 1011 版本
> （属另一任务目录，本轮**未擅自修改**）。

---

## 7. 本轮新增/修改的可执行门控（3 个）

| 脚本 | 性质 | 作用 |
|---|---|---|
| `16-checkpoint/replay_admission.py` | **新增** | ADR-004 准入谓词重放验收：概念筛选不变量 + T1/T2/T3 逐概念重放（一致率须 100%）+ 4 条负例 + 禁止快照常量自检 |
| `16-checkpoint/normalize_gap_ids.py` | **新增** | 按 ADR-004 §决定三 规则 6 归一化**新缺口**提案号（撞 T2 保留号/非法值 → 最小可用号）；作用域守卫：跳过 ADR 裁决表已覆盖的旧缺口 |
| `16-checkpoint/build_book_toc.py` | **修改** | ① NCX 标题 HTML 实体解码；② **0 章 fail-closed 护栏**（实测该脚本对既有 EPUB 非幂等，见下） |
| `16-checkpoint/apply_secondpass.py` | **修改** | `SLUGS` 硬编码 tt/ea → **数据驱动**（`--all` 原先静默跳过新书） |
| `16-checkpoint/check_corpus_overlap.py` | **修改** | `CORPUS` 追加 3 本新书语料（证据素材亦过版权红线） |
| `16-checkpoint/gate_verification.py` | **修改** | `SLUG_RECORD_PREFIX` / `SLUG_TEXT` / `SOURCE_SLUG` 三处登记新书 |
| `16-checkpoint/merge_verify_staging.py` | **修改** | `BOOKS` 表追加 3 本（**文档未列的第 4 处登记点**） |

### 🔴 实测教训：`build_book_toc.py` 对既有 EPUB **非幂等**

重生成时，`P0-02_clean-architecture_2017.epub` 的 NCX 解析返回 **0 章**（原 35 章），
`P0-04_software-architecture-in-practice-4e.epub` 返回 **221 章**（原 26 章）。
且 `01-books/` 被本地仓 `.gitignore:13` 整体忽略 ⇒ **无本地版本控制可回滚**。
⇒ 处置：从 `book-toc-index.json`（合并索引，保留了原 TOC）**忠实还原**；已加 0 章 fail-closed 护栏。
**未修的部分**：SAIP 那类「非 0 但差异巨大」的情形护栏拦不住 —— 重生成既有书 TOC 前须先备份。

---

## 8. 回滚路径

```bash
# 本地归档仓：回滚到本轮开工前
git -C "$MROOT" revert --no-edit 1d300c5 5bf5d64     # 或 git reset --hard a595722（丢弃本轮全部）
# 图谱与派生件由生成链再生（勿手改）
python3 16-checkpoint/aggregate.py && python3 16-checkpoint/build.py --config mother --quiet
# 公开层：远端 ref 回退（Git Data API）
gh api repos/zako-mio/se-architecture-methodology-kg/git/refs/heads/main \
  -X PATCH -f sha=ce39c6353938d2ff8b1c0cda5d2439b90e0b50d6 -F force=true
# 能力包：两段派生重跑（注意 §6 的两处反向漂移）
```

**批次级回滚（轨C 单节点）**：删 `10-dag-data/_parts/W2-TEC-H.json` 中的 `TEC-H-04` 节点与
`E-996..E-999` 四条边 → `deliverables.json` 四处 `expected` 回 167 → 生成链再生 → 门控须仍 PASS。

---

## 9. 待裁决 / 下一轮注意（P3 收尾 7 条裁决结果）

| # | 事项 | 本轮裁决 | 依据 / 备注 |
|---|---|---|---|
| 1 | 轨C 首批准入是否执行 | ✅ **已执行** | `TEC-H-04` 入图，计数 167→168，五处对账偏差 0 |
| 2 | 是否先采集 `BK-025`（SRE）/ `BK-026`（Workbook） | ✅ **已评估可行性**（见下） | 全文可得 + 许可已确认；实际采集留下一轮 |
| 3 | 轨B 续做范围 | ✅ **前 3 本**（BK-021/024/020） | 用户裁决；零解析成本 |
| 4 | `BK-008`（APoSD，本地仅 20 页无文本层） | ⏸ **暂不做** | 语料不足，需 OCR 且非全书 |
| 5 | `_verification-overrides.json` 含 `_evidence` 却已公开 | ⏸ **保持现状，另案处理** | 用户裁决；该不一致自轨B 即存在 |
| 6 | 阶段1 遗留重复 `claim_id`（`ESS-O-02#principle#1`） | ⏸ **继续 WARN** | G-V9 如实报 WARN，不阻断 |
| 7 | L4/L5 环境缺口（缺 `agent-browser`） | ⏸ **继续标未验证** | 不得伪装 PASS |

### §9.2 SRE 语料采集可行性评估（本轮实测，外部核查）

| 项 | BK-025《Site Reliability Engineering》 | BK-026《The Site Reliability Workbook》 |
|---|---|---|
| 全文在线 | ✅ `https://sre.google/sre-book/table-of-contents/`（**44** 个章节页） | ✅ `https://sre.google/workbook/table-of-contents/`（**30** 个章节页） |
| 直连可达 | ✅ HTTP **200**（0.38s，**无需代理**） | ✅ HTTP **200** |
| 正文可抽 | ✅ 抽样章 `monitoring-distributed-systems` → 可见正文 **30 369 字符** | 同构（同一站点） |
| 许可 | **CC BY-NC-ND 4.0**（O'Reilly 出版，页面显式标注） | **CC BY-NC-ND 4.0** |
| 采集成本 | 低（静态 HTML，无需 OCR/代理） | 低 |

> ⚠️ **ND（NoDerivatives）是约束点**：本项目产出的「改写主张」与节点正文属**派生内容**。
> 现有三重隔离已把 `claim` 排除在公开投影之外（公开白名单仅
> `source_id/book/chapter/section/section_title/evidence_strength/direction/second_pass/review_date`），
> 但**节点正文是公开的**。⇒ 若纳入 SRE，须单独裁决「SRE 派生的节点正文是否进入公开层」。
> **建议**：先只做私有层采集 + 核验，公开层处置另案裁决；采集前保留该许可声明到
> `acquired-manifest.json` 的 `licenses` 字段（勿标 `unknown-thirdparty`）。

### 其他须下一轮注意的事项

- **旧缺口 `proposed_node` 回写未做**：ADR-004 §决定三要求阶段3 回写缺口文件使号到概念映射一致。
  本轮只归一化**新缺口**（5 处）；旧 5 本中 `GAP-SAIP-003/004/007` 的 `proposed_node` 仍是**中文概念名**（非 id），
  应按 ADR 裁决回写为 `MTH-F-07`（ASR）/ `MTH-G-12`（ADD）/ T3 宿主。**属阶段3 独立任务。**
- **`apply_secondpass.py` 的 ca/ddia 第二路文件为合并命名** `secondpass-cleanarch-ddia.json`，
  与 `secondpass-<slug>.json` 不匹配 ⇒ `--all` 对这两本报 SKIP。
  既有状态已正确（`direct 且 second_pass=none` = 0），属**潜在重跑缺口**而非数据缺口。
- **`merge_verify_staging.py` 重合并是破坏性的**：TT/EA 的 staging 是第二路复核**之前**的状态，
  对其重合并会**丢失已回写的复核裁决**。只对未复核的新书用 `--only`。
- **子 Agent 无 shell**：本轮 3 名核验工人与 3 名复核工人均无 bash，一切脚本由主Agent 亲跑；
  工人自述一律经机械复验（62 记录 / 62 claims / 46 gaps 的键集、编号连续性、claims↔ledger 逐字一致、
  章号 ∈ TOC、上限、claim_id 无冲突，全部 0 问题）。
