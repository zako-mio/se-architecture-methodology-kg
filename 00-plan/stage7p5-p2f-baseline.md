# 阶段7 阶段3 续做轮 P2f · BK-028《Continuous Delivery》全书核验入层 + ADR-010 准入补录 + 两处判据收口 基线（append-only）

> 生成：2026-11-02（BK-028 EPUB 全书核验入层；14 条反向缺口经 ADR-010 判 7 T2 占号 / 7 T3 归并；`apply_secondpass` 降级判据收紧；`validate_staging_shards` 增 EPUB 切片回退）
> 前一份基线：`stage7p5-p2e-baseline.md`（图谱指纹 `690cfbdb…3aa85405`）
> **本基线取代上一份的「当前值」口径**；上一份文件保留不改（append-only）。

---

## 1. 指纹（9 文件 SHA-256）

| 文件 | SHA-256 | 相对上一份 |
|---|---|---|
| `01-books/_verify/verification-ledger.json` | **`a663a2bf86191ac8c15f0774b083baa46e4c0ceca283162be343cb2c1a5be855`** | **变更**（`77964962…`） |
| `01-books/_verify/node-claim-map.json` | **`c4eab2accf212b7002e9b6081fe97033aeca3f127b9827c9c7e0eeabda32f445`** | **变更**（`776a5f59…`） |
| `01-books/_verify/book-toc-index.json` | **`8e4ad47064d63e6c7af1f239036fa02c8da5872b6999a2b6a151f591dcbbd1c9`** | **变更**（`f18a1fbd…`） |
| `01-books/_verify/reverse-gaps.json` | **`9e318c5e9aee81caaec31c96c689242801e6da4eb6957e62eef5c07bf32e83b3`** | **变更**（`65b6e11d…`） |
| `10-dag-data/_verification-overrides.json` | **`5ded0c9f44b9250d754bb2d81acd3a8a11ac4ec128397d9296ecdf13eda43f96`** | **变更**（`ed734f9f…`） |
| `10-dag-data/_verification-baseline.json` | `bfc6f6b5df531ce3d29491872d11cf7e011913fb1e3ad5d18d4e7747a0ff523d` | 不变 |
| `10-dag-data/book-verification.json` | **`d966faa000894ebeb1de6b41d46cc753607bc19b88130d8d0ed92474eb6e3622`** | **变更**（`eff8e18a…`） |
| **`10-dag-data/methodology-dag.json`（图谱指纹）** | **`b87291244eeabdb2e1f931f07fc332705cfb9390da1e98d6e5bf70cffd5d8e86`** | **变更**（`690cfbdb…`） |
| `01-books/_verify/_meta/verify-contract.md` | **`e97e72ab1c0edb1d0f162c7b98f773e71ad04a58518b82028d2b29ee8ed28f8c`** | **变更**（`9cd1ff28…`） |

> **图谱指纹本轮变更**（`690cfbdb…` → `b8729124…`）由核验层证据变化驱动（`aggregate.py` 把 `_verification-overrides.json` 并回节点）：
> **15 个此前零记录节点首次入层** —— `ESS-J-03`（不可变基础设施）/ `ESS-J-04`（部署即变更管理）/ `MTH-I-02`（测试类型）/ `MTH-I-04`（测试金字塔与反模式）/ `MTH-I-05`（测试替身与测试策略）/ `MTH-I-06`（质量门控与持续集成）/ `MTH-I-07`（软件测试过程模型）/ `MTH-J-02`（发布工程）/ `MTH-J-03`（封闭构建）/ `MTH-J-05`（渐进暴露部署策略）/ `MTH-J-06`（发布与部署解耦）/ `TEC-J-02`（不可变基础设施实现）/ `TEC-J-03`（蓝绿部署）/ `TEC-J-05`（部署自动化）/ `TEC-J-06`（部署流水线工具化）；
> 另有 6 个既有覆盖节点因新增记录而 `review_date` 前移（`ESS-J-01` / `ESS-J-02` / `MTH-J-01` / `MTH-J-04` / `MTH-O-10` / `TEC-I-01`）。
> **结构始终未变**：**168 节点 / 364 边 / 18 组 / 18 案例**，`validate_graph.py` errors=0、warnings=0、`kahn 168/168`（无环）。

---

## 2. 核验层终值（18 本已核验书）

| 项 | 值 |
|---|---|
| ledger 记录 | **759**（`direct 541 / partial 194 / inferred 24`）※ 轮前 719（517/178/24） |
| 方向分布 | `forward 679 / reverse 80` |
| `node-claim-map` 的 claim 数 | **759**（与 ledger 逐条相等） |
| **claims 完整性差集** | **0** |
| 全层重复 `claim_id` | **0 组** |
| 覆盖节点 | **122**（= `_verification-overrides.json` 节点数，168 的 72.62%）※ 轮前 107（63.69%） |
| 缺口 | **173**（`missed_citation 72 / coverage_hole 58 / concept_missing 43`）※ 轮前 159（71/51/37） |
| 逐书记录数（**18 本**） | `saip 96 / team-topologies 81 / workbook 77 / sre-book 76 / evolutionary-arch 71 / ddia 58 / **continuous-delivery 40** / documenting-sa 37 / clean-architecture 35 / sweg 35 / refactoring 24 / release-it 24 / twelve-factor 24 / ddd 21 / saip-ch4 21 / welc 18 / clean-code 14 / aposd 7` |
| `verified` | `true` **153** / `"cited"` **15**（GR-10 = 91.07%，**不变**：本轮新增覆盖的 15 节点原本已是 `verified=true`） |
| 单节点上限 | 超限 **0**；`DENSIFY_NODES` = **41**（未变）；本轮新增顶满节点 `TEC-I-01`（8/8） |
| 第二路复核 | **全部 `direct` 541 条均有 verdict（100%）**；`apply_secondpass --slug continuous-delivery` 报 `未复核 direct = 0`、`悬挂 verdict = 0`、`兜底判据 = 0` |
| 第二路总账 | `matched 557 / passed 498 / disputed 59`（轮前 `matched 517 / passed 466 / disputed 51`） |
| 第二路状态分布 | `passed 561 / disputed 68 / none 130` |

**本轮新书明细（BK-028 continuous-delivery，EPUB 全文 15 章 / 1 270 486 字符）**：

```text
BK-028 continuous-delivery（1st/2010，ePub 全文，无印刷页码）
  records 40（direct 24 / partial 16）；覆盖 21 节点，其中 15 个为图谱此前零记录节点：
    ESS-J-01 1 ｜ ESS-J-02 1 ｜ ESS-J-03 2 ｜ ESS-J-04 1 ｜ MTH-I-02 3 ｜ MTH-I-04 2
    MTH-I-05 1 ｜ MTH-I-06 2 ｜ MTH-I-07 1 ｜ MTH-J-01 2 ｜ MTH-J-02 4 ｜ MTH-J-03 4
    MTH-J-04 2 ｜ MTH-J-05 1 ｜ MTH-J-06 1 ｜ MTH-O-10 2 ｜ TEC-I-01 2 ｜ TEC-J-02 1
    TEC-J-03 2 ｜ TEC-J-05 3 ｜ TEC-J-06 2
  第二路复核 40/40（3 名独立复核工人）：passed 32 / 分歧 8
  保守终裁降级 16 条（direct → partial）：703/704/706/708/731/733/735/737/738/744/766/767/769/770/772/768
  缺口 14 条（concept_missing 6 / coverage_hole 7 / missed_citation 1）：
    GAP-CD-701…705 / 731…735 / 761…764
```

**准入补录（ADR-010，`gate_architecture --kind adr` **6/6 PASS**，首轮即过）**：

| 项 | 值 |
|---|---|
| 候选册条目 | **63 → 77**（`T1 1 / T2 56 / T3 20`） |
| 候选册覆盖缺口 | **64 → 78** |
| `reserved_ids_this_round` | **49 → 56**（新增 7 号） |
| 占号条目（id 非 null 且 status ∈ KEEP） | 50 → **57** |
| `released_ids_this_round` | **5**（未变；⚠️ P2e 基线把该值记作 8，本轮回盘实测为 5，**以本表为准**；ADR-009 的 `warnings` 亦记「释放清单维持 5 个」） |
| `reassignment_map` | 6（不变） |
| `amended_by` | `["ADR-006", "ADR-007", "ADR-008", "ADR-009", "ADR-010"]` |
| 七条 T2 占号 | `GAP-CD-703 ⇒ MTH-J-10`、`704 ⇒ MTH-O-16`、`733 ⇒ MTH-J-11`、`734 ⇒ MTH-I-08`、`761 ⇒ TEC-J-07`、`763 ⇒ MTH-J-12`、`764 ⇒ MTH-O-17` |
| 七条 T3 归并（no-id） | `701`（ESS-J-02）/ `702`（TEC-J-05 + ESS-J-03）/ `705`（MTH-I-05）/ `731`（MTH-I-05）/ `732`（TEC-J-05）/ `735`（MTH-I-02）/ `762`（MTH-O-10） |
| `replay_admission` | 概念 **77/77**，一致率 **100.00%**，负例 **4/4** |
| `--scan-promotion` | 候选 **56** / 可晋升 **0** / 负例 **3/3** / 新提案行 **0** |
| 未登记 `proposed_node` | **0**（`writeback_gap_ids` 回写 7 条后复跑 0 变更） |

---

## 3. 门控全表（本轮实测）

| 门控 | 结果 |
|---|---|
| `gate_architecture.py --kind adr --input ADR-010.json` | **PASS 6/6**（首轮；G-A3 24 个节点引用 / G-A4 41 引用零悬挂 / G-A5 无 TEC- 越位 / G-A6 5 条质量场景） |
| `slice_corpus_by_chapter.py --negative-test`（本轮新增开关） | **4/4**（N1 无匹配拒写 / N2 章号非递增拒写 / N3 章数与 expect 不符拒写 / N4 旧判据反证：不带 `--pattern` 时 `ddd` 的 17 个切片逐字节不变） |
| `validate_staging_shards.py`（本书） | 首轮 **PASS 0 问题**（40 记录 / 40 主张 / 14 缺口 / 上限全通过）；两处分片跨节点重复由 merge 去重 |
| `gate_verification.py --check all` | **PASS 9/9**；G-V5「可用书文本源」**含 `BK-028`**（缺失 无，命中 ≥20 字子串 = 0）；G-V1 记录 759 / gap 173 / 完整性缺口 0 / 重复 0；G-V8 覆盖 **122/122** |
| `apply_secondpass.py --negative-test` | **8/8 如期通过**（新增 N6：`agree=true` 但强度更低须降级；N7：`agree=false` 且同强度须降至 partial；N8：一致且同强度不得降级） |
| `merge_secondpass_worklists.py --negative-test` | **2/2**（实测：写盘 1 / 无变化跳过 7 —— 本轮 7 本既有书的 `secondpass-*.json` 逐字节未被改写） |
| `backfill_candidate_register.py --negative-test` | **3/3** |
| `extract_pdf_book.py --negative-test` | **3/3**（页数不符 / 标题不在声明页 / `pdf_page` 非递增） |
| `negative_test_verification.py` | **11/11** |
| `negative_test_densify.py` | **11/11** |
| `gate_densify.py --check all` | **PASS 5/5** |
| `gate_coverage.py` | L6 PASS（manifest 100.00% / 四向 100.00% / GR-08 GR-09 PASS） |
| `gate_sources.py` | L7 PASS（悬挂 0 / 可溯源 100.00% / verified **91.07%**） |
| `gate_layout.py --check all` | L8 PASS（覆盖率 **2140/2140 = 100.00%**，问题 0） |
| `gate_methodology.py --check all` | 四项全 PASS |
| `kb_gate.py`（structure,links；按 `quality-gate.md` 排除口径） | PASS 2/2（structure **924** 项 0 问题 / links **10964** 项 0 问题） |
| `gate_visual.py --check all`（默认 8 页样本） | **L4 PASS**（212/272 = 77.94%，0 FAIL，60 skip —— 与上一份基线**完全一致**） |
| `gate_visual.py --pages <本轮 15 个新覆盖节点页 + 06 视图>`（**扩展抽样，⚠️ 非默认口径**） | 531/578 = 91.87%，**1 FAIL**：`MTH-I-05.html @1280` 的 `pixel.svg-ink` = 0.89% < 1.50%（该节点只有 1 条边 ⇒ 关系图稀疏，见 §6-③） |
| `gate_visual.py --pages <全部 168 节点页>`（**扩展抽样，⚠️ 非默认口径**） | 5370/5712 = 94.01%，**6 FAIL**：4 条 `pixel.svg-ink`（`MTH-I-05` 0.89% / `ESS-J-02` 1.29% / `ESS-M-02` 1.36% / `MTH-F-03` 1.45%，全是 1–2 条边的稀疏节点）+ 2 条 `MTH-G-01 @390` 的 `runtime.h-overflow` / `runtime.overflow-leak`（长不可断 token 溢出，见 §6-④） |
| `gate_render.py --timeout 25` | **L5 PASS**（7/7 案例，skipped=0） |
| `check_corpus_overlap.py --target evidence` | **0 命中**（134 对象 / **10 182 794** distinct 20-gram，轮前 9 265 553） |
| `writeback_gap_ids.py --check` | PASS（命中 78/78、需变更 0 —— 幂等） |
| `normalize_gap_ids.py --check` | PASS（重指派 0 / 非法 0 / 撞号 0） |
| `derive_verification.py --check` | PASS（幂等，6 产物全 up-to-date） |
| `aggregate.py` 连跑两次 | 哈希一致（`b8729124…`） |
| `build.py --config mother` 连跑两次 | 产出总哈希一致（**`c894c4a2…`**，口径＝`10-dag-data`+`11/12/13/14/15`+`index.html` 全文件 sha256 的 sha256；轮前同口径未记，故不比对） |
| `validate_graph.py` | errors=0、warnings=0、kahn 168/168 |

---

## 4. 公开层对账

```text
推送           = 1 次（Git Data API）
  parent f87d60f7c21b / base_tree d84fb4de00e8 → new_tree 76419b4e68b1 / new_commit e744ad95c461
  （`_publish` 本地提交 f040805；推送前已在 `_publish` 内 git add -A && git commit）
  受控文件      = 583 个（本地 ls-files 583 == 远端 blobs 583）
远端 HEAD      = e744ad95c461b9342462218bf90166d1989a1f89
CI             = push 自动触发：run **41397813893 success**（32s；`10-dag-data/**` 与 `16-checkpoint/**` 命中 push.paths）
Pages 回验     = / 、00-plan/stage7p5-p2f-baseline.md 、00-plan/NEXT-SESSION-HANDOFF.md 、
                 11-node-pages/MTH-J-02.html 、11-node-pages/ESS-J-03.html 、11-node-pages/MTH-I-05.html 、
                 14-views/06-book-verification.html 、10-dag-data/methodology-dag.json 、
                 10-dag-data/book-verification.json   均 **200**
                 ；00-plan/NEXT-ROUND-PROMPT-7.md / -8.md 均 **404**（`never` 类生效）
装配           = --apply --refresh-sanitize 后 --check 三类差异 0/0/0；P1–P5 预检全 OK（577 文件）
gate_disclosure= PASS（0 hit / 516 file）
```

> 本节终值已按实测回填；回填本身是一次**纯 `00-plan/**` 文档提交**（不触发 CI，须手动 dispatch run 并回验 Pages）。
> 另：上一轮 P2e 基线 §4「推送②」那段回填此前只落本地、未进公开层（其文末自我标注了「站点落后一次」），**本轮推送已一并补上**。

```text
推送②（本节回填）  = （回填后另行记录）
```

---

## 5. 本轮新增/修改的可执行物

| 文件 | 性质 |
|---|---|
| `16-checkpoint/slice_corpus_by_chapter.py` | **改（能力补齐）**：新增 `--pattern`（自定章头正则，须 2 个捕获组）/ `--expect-chapters` / `--negative-test`；三条 fail-closed（无匹配 / 章号非严格递增 / 章数与 expect 或 `toc-<slug>.json` 不符 ⇒ 拒写、退出码 3、一个文件都不落）。原因：EPUB 一路（`extract_book_text.py`）**不产 `=== 章号 | 标题 ===` 章头**，既有 7 本 EPUB 书因此从未切章。 |
| `16-checkpoint/validate_staging_shards.py` | **改（伪红收口）**：节一致性校验的「章级正文」来源由「正文 `===` 章头」扩展为「章头缺失时回退 `_text/_slices/<slug>/ch-<n>.txt`」。改前 EPUB 书 40 条记录 **全部** 报「无法读取所声明章的正文」；改后 `ddd`（有章头）实测仍 0 问题，回归无变化。 |
| `16-checkpoint/apply_secondpass.py` | **改（判据收紧）**：① 复核强度低于验前强度 ⇒ 一律降级（原实现只在 `agree=false` 时读强度，导致「同意但证据不足」的 8 条被静默保留 direct）；② `agree=false` ⇒ 终裁强度至多 `partial`（原实现允许「否决但同强度」保留 direct，1 条）。探针 **5 → 8 条**（新增 N6/N7/N8，含防恒降反证）。 |
| `16-checkpoint/gate_verification.py` | 改：`SLUG_RECORD_PREFIX` / `SLUG_TEXT` / `SOURCE_SLUG` 各增 `continuous-delivery` / `BK-028` |
| `16-checkpoint/merge_verify_staging.py` | 改：`BOOKS` 增 `cd` |
| `16-checkpoint/check_corpus_overlap.py` | 改：`CORPUS` 增 `continuous-delivery.txt` |
| `18-design/adr/ADR-010.json` | **新增**：14 条新缺口的准入裁决（`amends: ["ADR-004"]`；7 T2 占号 / 7 T3 归并） |
| `18-design/adr/ADR-004.json` | 改：候选册 63→77、`reserved_ids_this_round` 49→56、`amended_by` 增 ADR-010 |
| `01-books/_verify/_parts/toc-continuous-delivery.json` | **新增**：TOC 分片（15 章 / 373 节；`coverage.kind = full-text-epub`；**不登记页码**） |
| `01-books/_verify/_text/continuous-delivery.txt` + `_text/_slices/continuous-delivery/ch-{1..15}.txt` | **新增**：全书语料（1 270 486 字符 / 11 747 行）与 15 个章切片 |
| `01-books/_verify/_meta/adr-register-backfill-adr010.json` / 索引 | **新增/改**：按修订件留存的补录报告 + 索引（index `reports[5]`、`latest=ADR-010`） |
| `01-books/_verify/_meta/verify-contract.md` | 改：§0 增 `continuous-delivery` 行 + **§0.1 三个 `verified` 的口径边界**（裁定「维持双轨」的书面落点） |
| `00-plan/stage7p5-p2f-baseline.md` | **新增**：本基线 |
| `00-plan/NEXT-ROUND-PROMPT-8.md` | **新增**：下一轮接力件（`classes.never`，不公开） |
| `16-checkpoint/publish-manifest.json` | 改：`classes.never` 增 `00-plan/NEXT-ROUND-PROMPT-8.md` |

---

## 6. 本轮核心证据（四个实测发现）

1. **EPUB 书从未被切章 —— 「给工人章切片」这条纪律在 EPUB 一路是空转的**：`extract_book_text.py` 只按 spine 拼接，不产 `===` 章头；`slice_corpus_by_chapter.py` 只认 `===` 章头。实测 `_text/_slices/` 下只有 web/PDF/OCR 九本书，7 本 EPUB 书（tt/ea/ref/ri/cc/ca/saip）**没有任何切片**。本轮补上 `--pattern` 通道（BK-028 用 `^Chapter (\d+)\. (.+)$`，前置目录的 `Chapter N:` 冒号形态被点号天然排除）。
2. **`apply_secondpass` 有两条静默放宽路径**（本轮实测命中 9 条）：① `agree=true` 但复核判 evidence 只够 `partial` ⇒ 原实现不看该强度，direct 原样保留（本轮 8 条）；② `agree=false` 且复核强度 = 验前强度 ⇒ 原实现保留 direct，等于「结论被否决但强度不变」（本轮 1 条）。修后本轮降级 **16 条**（direct → partial），且 `--slug` 复跑 `downgraded=0 / 已降级复算=16`（幂等）。
3. **`pixel.svg-ink`（≥1.5%）对稀疏节点是**假红**：关系图的墨迹占比随邻居数下降，1–2 条边的节点（`MTH-I-05` 1 边 / `ESS-M-02` 1 边 / `ESS-J-02` 2 边 / `MTH-F-03` 2 边）实测 0.89%–1.45%，稳定低于阈值。全量 168 页抽样 **4/168 命中且全部是稀疏节点**；本轮新增的 15 页里仅 `MTH-I-05` 命中。**默认 8 页样本不含任何稀疏节点**，所以默认口径的 L4 始终 PASS —— 这解释了为什么该判据长期未暴露此问题。**处置：不改判据（改阈值需重做负例），登记为已知假红，建议下一轮按「邻居数 ≥3 才判 svg-ink」收口。**
4. **`MTH-G-01` 移动端横向溢出（既有缺陷，非本轮引入）**：@390 视口 `scrollWidth > innerWidth`，`runtime.overflow-leak` 同报。定位候选是正文里 69 字符不可断 token（`modularity/reusability/analysability/modifiability/testability`）与两个长 URL。该节点内容本轮未改，属阶段 5 以来的既有版式缺陷；同样因为默认样本不含该页而未被发现。**处置：登记，建议下一轮给 `.evidence` / 正文加 `overflow-wrap:anywhere` 并补 L8 复验。**

> 补充：`gate_verification` 的 G-V7 曾报 `book-toc-index.json` 为 `[stale]` 却仍判 PASS —— 该状态在「`_parts/toc-*.json` 新增但未跑 derive」时出现，属**真实的伪绿缝隙**（derive 一跑即消失）。本轮已 valid → derive → 复验收敛，登记为判据待加固项。

---

## 7. 回滚路径

- **备份**：`~/.dsh-backups/stage7p5-p2f-20261102/`（`_parts`、`_review`、`_text`、`_meta`、`10-dag-data`、`18-design`、`16-checkpoint`、`00-plan`；另含 `_snap/` 前后快照与 `_tools/` 的三个一次性脚本）。
- **回退顺序**：`_parts/{ledger,claims,toc,gaps}-continuous-delivery.json` 删除 → `_text/continuous-delivery.txt`、`_text/_slices/continuous-delivery/` 删除 → 6 处登记回退 → `18-design/adr/ADR-010.json` 删除 + ADR-004 复原（或以备份 `18-design/adr/ADR-004.json` 覆盖）+ `_meta/adr-register-backfill-adr010.json` 删除、索引 `reports[]` 去掉末项 → `derive_verification` → `aggregate` → `build` → 公开层重装配重推。
- **三处代码回滚**：`slice_corpus_by_chapter.py` / `validate_staging_shards.py` / `apply_secondpass.py` 从 `16-checkpoint/` 备份还原；还原后 EPUB 书将再次「无切片可切」、EPUB 书的分片机检将再次全量报「无法读取章正文」、`apply_secondpass` 将退回两条静默放宽路径。
- **`01-books/` 无 git 历史**（本地仓与 `_publish` 双重 ignore）⇒ 只能靠上述备份回滚。
- 本地归档仓：以 `git log --oneline -3` 为准。

---

## 8. 待裁决 / 未完成

1. **F 域 12 节点仍零书证**（`ESS-F-01..05` / `MTH-F-01..04,06` / `TEC-F-01..02`）：其 `sources[]` 全为 `OFF/STD/PAP/SEBoK/SWEBOK`，30 本语料中**没有任何需求工程书**（`P2-25` Sommerville 仅样章 Ch01/12/20/26–31，不含需求章）。这是**材料缺**，不是遗漏：补它需要新增 canonical 书目（BK 38→39）+ 研究包补录（门控级）。候选材料：Sommerville《Software Engineering》10th 全书 / Wiegers《Software Requirements》3rd / Cockburn《Writing Effective Use Cases》。
2. **`MTH-G-01` 移动端溢出 + 4 个稀疏节点的 `svg-ink` 假红**（§6-③④）：两条都建议下一轮修，但都**不在默认样本集**内 ⇒ 修完必须把这两个页面加入 `DEFAULT_PAGES` 或另建扩展样本，否则「修了也不知道」。
3. **`TEC-I-01` 已达单节点上限**（6 + 2 = 8 = `CLAIM_CAP`）：本轮为塞下 CD 的第二条 CI 证据，删掉了首路最泛的一条（`VR-CD-707`，CI 服务"长驻进程 + 界面"两段式描述），并把 A 分片号段重排为连续。后续任何书再想给该节点补记录，须先走 ADR-003 的增密档位申请或换落点。
4. **`GAP-CD-761`（有状态数据版本化迁移）与候选册 `MTH-L-08`（GAP-EA-009，BK-011）语义最近**：若复核判定同一被定义项，合并后 `|S|=2` ⇒ 会从 T2 变 **T1**（结构变更），须走一次结构扩展波次并释放 `TEC-J-07`。ADR-010 的 `warnings` 已登记。
5. **`GAP-CD-764` 的域判定（O 还是 K）**：ADR-010 判 `methodology/O`（取 `MTH-O-17`）；若复核主张运维域 `K`，须改号并同步 `reserved_ids_this_round`。
6. **T2 → T1 晋升**：候选册 T2 由 49 增至 **56**（7 条新 T2 均单源）；`--scan-promotion` 仍「可晋升 0」。晋升属结构变更，须另立 ADR。
7. **域外贴限证据**：`MTH-J-07` / `MTH-N-05` / `TEC-J-04` 各 8 条，维持 ADR-005 边界（用户既定：维持）。本轮 CD 的金丝雀内容按此改落 `MTH-J-05` / `TEC-J-03`，并在 `evidence_note` 留痕。
8. **公开仓历史 blob（旧）**：`NEXT-ROUND-PROMPT-3.md` 与 P2d 泄漏的 OCR 抽取件原文仍在公开仓 git 历史（commit `85357b1` / `2ebb389` / `e14ee0e`）。**本轮裁定：不做 force-push**——泄漏物是**作者免费抽取件的 OCR 文本**（非付费书正文）+ 一份内部接力件，风险等级低；清除须重写历史并打断 CI 与全部历史引用。留档为已知风险。
9. **canonical `verified` 与核验层两套口径**：本轮裁定**维持双轨**，书面边界已写入 `verify-contract.md §0.1`（不动机器可读字段）。
10. **`BK-016`（POSA Vol.1）仍未采集**：其唯一未覆盖引用节点 `ESS-G-05` 已被 DDD 覆盖；待用户提供合法副本。
