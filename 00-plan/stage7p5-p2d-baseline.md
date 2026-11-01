# 阶段7 阶段3 续做轮 P2d · BK-008（APoSD）OCR 入层 + 两个工具缺陷收口基线（append-only）

> 生成：2026-11-01（BK-008 无文本层 PDF → OCR → 核验入层；`apply_secondpass` 降级幂等修复；补录报告单槽改按修订件留存；ADR-008 准入补录；图谱再生；公开层同步）
> 前一份基线：`stage7p5-p2c-baseline.md`（图谱指纹 `c413c6fd…a6a8fc21`）
> **本基线取代上一份的「当前值」口径**；上一份文件保留不改（append-only）。

---

## 1. 指纹（9 文件 SHA-256）

| 文件 | SHA-256 | 相对上一份 |
|---|---|---|
| `01-books/_verify/verification-ledger.json` | **`495493ef7d3429772477049ecf7839e4e81857b08a4939812322018c62bd65aa`** | **变更**（`873b0ae2…`） |
| `01-books/_verify/node-claim-map.json` | **`4f73a2cb593b3cb80bc4a27e40de43de0e8921ed77f39a87ba0cf4f5f695efe4`** | **变更**（`f0c8addd…`） |
| `01-books/_verify/book-toc-index.json` | **`686abd7eb69fbb48e9103aad5806285b462fd60ab6f5b3f393d44933f185fded`** | **变更**（`fd77c0df…`） |
| `01-books/_verify/reverse-gaps.json` | **`0f788a4f2f4fc4b1590def1a424d2149da5081fb30ef49b11dc0545d78a856db`** | **变更**（`cd75c96f…`） |
| `10-dag-data/_verification-overrides.json` | **`6c634822504b10a361eb952cdde6cd94371122b5d34473586050df1686b3845d`** | **变更**（`6a7cdc16…`） |
| `10-dag-data/_verification-baseline.json` | `bfc6f6b5df531ce3d29491872d11cf7e011913fb1e3ad5d18d4e7747a0ff523d` | 不变 |
| `10-dag-data/book-verification.json` | **`92cf66b0da08fcc729825ed53067fd289ad717753a90521259778ba13cb1e8ad`** | **变更**（`cde38b28…`） |
| **`10-dag-data/methodology-dag.json`（图谱指纹）** | **`9212644f756e83b309b68cef77d50082293dbd104b192ab014196c2639bc647a`** | **变更**（`c413c6fd…`） |
| `01-books/_verify/_meta/verify-contract.md` | **`536028c9cbc9117d244c814be3290e3ed720010ce232872ead9bc222e6a0c962`** | **变更**（`1710faa9…`） |

> **图谱指纹本轮变更**（`c413c6fd…a6a8fc21` → `9212644f…9bc647a`）由核验层证据变化驱动
> （`aggregate.py` 把 `_verification-overrides.json` 并回节点）：**3 个此前零记录节点新增覆盖** ——
> `ESS-H-01`（信息隐藏）/ `ESS-H-05`（深模块与浅模块）/ `MTH-H-02`（信息隐藏模块化分解）——
> 其 `verified` 保持 `true`，`review_date` 前移至 `2026-11-01`；另有 4 个既有节点因新增记录而 `review_date` 前移。
> **结构始终未变**：**168 节点 / 364 边 / 18 组 / 18 案例**，`validate_graph.py` errors=0、warnings=0、`kahn 168/168`（无环）。

---

## 2. 核验层终值（16 本已核验书）

| 项 | 值 |
|---|---|
| ledger 记录 | **698**（`direct 503 / partial 171 / inferred 24`）※ 轮前 691（499/168/24） |
| `node-claim-map` 的 claim 数 | **698**（与 ledger 逐条相等） |
| **claims 完整性差集** | **0** |
| 全层重复 `claim_id` | **0 组** |
| 覆盖节点 | **103**（= `_verification-overrides.json` 节点数）※ 轮前 100 |
| 缺口 | **150**（`missed_citation 71 / coverage_hole 49 / concept_missing 30`）※ 轮前 148 |
| 逐书记录数（**16 本**） | `saip 96 / team-topologies 81 / workbook 77 / sre-book 76 / evolutionary-arch 71 / ddia 58 / documenting-sa 37 / clean-architecture 35 / sweg 35 / refactoring 24 / release-it 24 / twelve-factor 24 / saip-ch4 21 / welc 18 / clean-code 14 / **aposd 7**` |
| `verified` | `true` **153** / `"cited"` **15**（GR-10 = 91.07%，**不变**：本轮新增覆盖的 3 节点原本已是 `verified=true`） |
| 单节点上限 | 超限 **0**；`DENSIFY_NODES` = **41**（未变） |
| 第二路复核 | **全部 `direct` 503 条均有 verdict（100%）**；`apply_secondpass --all` 报 `未复核 direct = 0`、`悬挂 verdict = 0`、`downgraded = 0`（既有书口径） |
| 第二路总账 | `matched 496 / passed 450 / disputed 46`（轮前 `matched 491 / passed 446 / disputed 45`） |

**本轮新书明细（BK-008 aposd，作者免费 20 页抽取件）**：

```text
BK-008 aposd（2nd/2021 抽取件；印刷页 39–49 / 76 / 99–100 / 171–174）
  records 7（direct 4 / partial 3，其中 VR-APOSD-005 由第二路复核从 direct 降为 partial）
  覆盖 7 节点，其中 3 个为图谱此前零记录节点：
    ESS-H-01 1 ｜ ESS-H-05 1 ｜ MTH-H-02 1 ｜ MTH-O-06 1 ｜ ESS-H-07 1 ｜ ESS-G-04 1 ｜ MTH-O-09 1
  第二路复核 5 条 direct 全部有 verdict；agree 4 / 分歧 1（VR-APOSD-005：claim 的机制腿落在 12.6 节之外）
  缺口 2 条（均 concept_missing）：GAP-APOSD-001（注释即设计）/ GAP-APOSD-002（特例消除）
```

**准入补录（ADR-008）**：

| 项 | 值 |
|---|---|
| 候选册条目 | **52 → 54**（`T1 1 / T2 40 / T3 13`） |
| 候选册覆盖缺口 | **53 → 55** |
| `reserved_ids_this_round` | **38 → 40**（新增 `MTH-H-09` / `MTH-O-13`） |
| `released_ids_this_round` | **5**（不变） |
| `reassignment_map` | 6（不变） |
| `amended_by` | `["ADR-006", "ADR-007", "ADR-008"]` |
| 两条裁决 | `GAP-APOSD-001` ⇒ **T2 / `MTH-H-09` / newly-allocated**；`GAP-APOSD-002` ⇒ **T2 / `MTH-O-13` / newly-allocated** |
| 未登记 `proposed_node` | **0**（`writeback_gap_ids` 回写 2 条后复跑 0 变更） |

---

## 3. 门控全表（本轮实测）

| 门控 | 结果 |
|---|---|
| `gate_architecture.py --kind adr --input ADR-008.json` | **PASS 6/6**（首轮即 6/6；G-A3 19 个节点引用 / G-A4 零悬挂 / G-A5 无 TEC- 越位） |
| `gate_architecture.py --kind adr --input ADR-004.json` | PASS 6/6（补录后复查） |
| `gate_verification.py --check all` | **PASS 9/9**；G-V5「可用书文本源」**含 `BK-008`**（缺失 无，命中 0）；G-V1 记录 698 / gap 150 / 完整性缺口 0 / 重复 0 |
| `extract_ocr_book.py --negative-test` | **5/5 如期按应有理由拒写**（页数不符 / 标题不在声明页 / `pdf_page` 非递增 / 空页识别失败 / `printed_page` 非递增） |
| `apply_secondpass.py --negative-test` | **4/4 如期通过**（已降级重跑不反转 / 未低于原判不升降 / 连跑逐字节一致 / 旧判据反证可复现反转） |
| `backfill_candidate_register.py --negative-test` | **3/3 如期通过**（旧单槽迁移不被 no-op 覆盖 / 两轮报告共存 / 索引重写幂等） |
| `validate_staging_shards.py`（本书） | problems **0**、WARN **0**（7 记录 / 7 主张 / 2 缺口 / 上限全通过） |
| `replay_admission.py` | 一致率 **100.00%** + 负例 **4/4** |
| `replay_admission.py --scan-promotion` | 候选 **40** / 可晋升 **0** / 负例 **3/3** |
| `negative_test_verification.py` | **11/11** |
| `negative_test_densify.py` | **11/11** |
| `derive_verification.py --check` | PASS（幂等，6 产物全 up-to-date） |
| `aggregate.py` 连跑两次 | 哈希一致（幂等） |
| `build.py --config mother` 连跑两次 | 产出总哈希一致（`0346f9c8…`） |
| `validate_graph.py` | errors=0、warnings=0、kahn 168/168 |
| `gate_densify.py --check all` | **PASS 5/5**（变更集 26 = 期望 26） |
| `gate_coverage.py` | L6 PASS（manifest 100% / 四向 100% / GR-08 GR-09 PASS） |
| `gate_sources.py` | L7 PASS（悬挂 0 / 可溯源 100% / verified **91.07%**） |
| `gate_layout.py --check all` | L8 PASS（覆盖率 2140/2140 = 100%） |
| `gate_methodology.py --check all` | 四项全 PASS |
| `kb_gate.py`（structure,links；按 `quality-gate.md` 的排除口径） | PASS 2/2（structure 922 项 0 问题 1 提醒 / links 10 904 项 0 问题） |
| `gate_visual.py --check all` | **L4 PASS**（212/272 = 77.94%，0 FAIL，60 skip —— 与上一份基线**完全一致**） |
| `gate_render.py --timeout 25` | **L5 PASS**（7/7 案例，skipped=0） |
| `check_corpus_overlap.py --target evidence` | **0 命中**（134 对象 / **8 592 676** distinct 20-gram，轮前 8 561 894） |
| `writeback_gap_ids.py --check` | PASS（命中 55/55、需变更 0 —— 幂等） |
| `normalize_gap_ids.py --check` | PASS（重指派 0 / 非法 0 / 撞号 0） |

---

## 4. 公开层对账

```text
推送           = 4 次（Git Data API）+ 5 次 Contents API 删除提交
  ① 主体：parent 74e0faacc1b8 / base_tree d2671b0e9664 → new_commit 875d43f873c1 / new_tree f4feb6e05d5b
     （`_publish` 本地提交 2ebb389；推送前已在 `_publish` 内 git add -A && git commit）
  ② 文档对账回填：parent 875d43f873c1 → new_commit cc1992dff551 / new_tree cec14cf896d2
     （`_publish` 提交 85357b1；**纯 00-plan/** ⇒ 未自动触发，手动 dispatch run 41290940423 success）
  ③ 下架泄漏：parent cc1992dff551 → new_commit c44e83b5cfe8 / new_tree beba0879a24
     （`_publish` 提交 7577d72；含 `16-checkpoint/**` 改动 ⇒ **自动触发** run 41291433407 success）
  ④ 收尾文档：parent d5e5c6d8（删除后的 HEAD）→ new_commit ace01c17e6aa / new_tree c03f0ff24008
     （`_publish` 提交 0e97d9d；**纯 00-plan/** ⇒ 未自动触发，手动 dispatch run 41292109595 success）
  ⑤ 终态对账：parent ace01c17e6aa → new_commit 1abd2edb143d（`_publish` 提交紧随；纯文档 ⇒
     手动 dispatch run 41292548004 success）
  ⑥-⑩ 显式删除 5 个泄漏 blob（`gh api -X DELETE .../contents/<path>`）：
     c7199fdd → 7b8e026c → befa7bb5 → f23f3d10 → **d5e5c6d8436b**（其后由推送④⑤接回主线）
远端 HEAD      = 1abd2edb143dbeaec99057c36d437b7a68359d0b
                 （⚠️ 本文件在推送⑤之后还有一次**纯文档**本地提交以写入本节终值 ⇒ 公开站点版本落后本地一次，
                  差异仅为本节文本；远端 HEAD 以 `gh api repos/.../commits/main` 为准）
remote blobs   = 581  ==  本地 _publish ls-files 581（575 受控文件 + 6 项 preserve 类）
                 ① 前为 586（受控 580），下架 `16-checkpoint/_ocr` 与 `_snap` 共 5 个 blob
CI             = push 自动触发：run **41290533613 success**（30s，push①）/ **41291433407 success**（32s，push③；
                 同秒其余 3 个删除提交 run 被 cancelled，属 GitHub 合并行为）
                 ；纯文档推送不触发 ⇒ 手动 run **41290940423 success**（35s，push②）/ **41292109595 success**（30s，push④）
Pages 回验     = / 、00-plan/stage7p5-p2d-baseline.md 、00-plan/NEXT-SESSION-HANDOFF.md 、
                 11-node-pages/ESS-H-01.html 、ESS-H-05.html 、MTH-H-02.html 、
                 10-dag-data/methodology-dag.json 、14-views/06-book-verification.html 、
                 16-checkpoint/extract_ocr_book.py 、16-checkpoint/apply_secondpass.py   均 **200**
                 ；00-plan/NEXT-ROUND-PROMPT-5.md / -6.md 均 **404**（`never` 类生效）
                 ；**泄漏回验**：16-checkpoint/_ocr/{aposd-extract.raw.json,aposd-extract.err} 与
                 16-checkpoint/_snap/{parts,parts.postfix,secondpass}.sha256 均 **404**（已下架）
装配           = --apply --refresh-sanitize 后 --check 三类差异 0/0/0；P1–P5 预检全 OK（575 文件）
gate_disclosure= PASS（0 hit / 514 file）
```

> 🔴 **本轮发生并已处置的一起真实泄漏（务必继承）**：把 OCR 临时工作目录建在 **`16-checkpoint/`（mask 类，会发布）**
> 下，导致 `_ocr/aposd-extract.raw.json`（**OCR 出来的书页原文 39 KB**）与 3 个 `_snap/*.sha256` 随 push #1 进了公开仓。
> 处置：① `publish-manifest.json` 的 `classes.never` 增 `16-checkpoint/_ocr/` 与 `_snap/`；② 从 `_publish` 工作树移除
> （commit 7577d72）并推送（push #3）；③ 因 `push_publish.py` 用 `base_tree`、**不能删远端文件**，逐条
> `gh api -X DELETE` 下架 5 个 blob；④ 删除提交触发 CI 41291433407 success、Pages 回验泄漏路径全部 **404**。
> ⚠️ **但 blob 仍在公开仓 git 历史中**（commit 875d43f8 / cc1992df / c44e83b5）⇒ 彻底清除须 force-push（**未做**，见 §7-8）。
> **教训**：临时/中间产物一律建在 `01-books/`（private）或仓外的 `~/.dsh-backups/`，**绝不要**建在 mask/mirror 类目录下。


> **注**：本文件在推送后仍可能有末次本地 `docs:` 提交（本节文本），故公开站点版本可能落后本地一次；
> 若紧接着做了纯 `00-plan/**` 的第二次推送，CI **不会**自动触发，须手动 `gh workflow run rebuild.yml` 并回验 Pages。

---

## 5. 本轮新增/修改的可执行物

| 文件 | 性质 |
|---|---|
| `16-checkpoint/extract_ocr_book.py` | **新增**：无文本层 PDF 的 OCR 结果 → 语料（章头驱动；5 条 fail-closed；`--check` 与 `--negative-test` 5 条负例探针） |
| `16-checkpoint/apply_secondpass.py` | **改（缺陷收口）**：降级/保留判据由「当前强度」改为「复核前强度」（`review.first_pass_strength` → verdict 的 `first_pass_strength` → 兜底当前值），修「已降级记录重跑留痕语义反转」；新增 `already_downgraded` 计数与 `--negative-test` 4 条探针 |
| `16-checkpoint/backfill_candidate_register.py` | **改（缺陷收口）**：补录报告由单槽改为「一修订件一报告 + 索引」（`adr-register-backfill-<adrNNN>.json` + `adr-register-backfill.json` 索引），兼容旧单槽迁移、先写者胜防 no-op 覆盖；新增 `--negative-test` 3 条探针 |
| `16-checkpoint/gate_verification.py` | 改：`SLUG_RECORD_PREFIX` / `SLUG_TEXT` / `SOURCE_SLUG` 各增 `aposd` / `BK-008`（6 处登记中的 3 处） |
| `16-checkpoint/merge_verify_staging.py` | 改：`BOOKS` 增 `aposd` |
| `16-checkpoint/check_corpus_overlap.py` | 改：`CORPUS` 增 `aposd.txt` |
| `18-design/adr/ADR-008.json` | **新增**：2 条新缺口提案的准入裁决（`amends: ["ADR-004"]`，双 T2 占号） |
| `18-design/adr/ADR-004.json` | 改：候选册 52→54、`reserved_ids_this_round` 38→40、`amended_by` 增 ADR-008 |
| `01-books/_verify/_meta/pdf-chapters-aposd.json` | **新增**：章图（pdf 页 + 印刷页码 + 节表；**唯一承载页码处**，私有层） |
| `01-books/_verify/_text/aposd.txt` + `_text/_slices/aposd/ch-{6,9,12,21}.txt` | **新增**：OCR 语料与章切片（私有层） |
| `01-books/_verify/_text/_ocr/aposd-extract.ocr.json` | **新增**：OCR 原始结果（可复算，私有层） |
| `01-books/_verify/_meta/adr008-inputs.json` | **新增**：ADR-008 输入包（2 条提案原文 + 号占用现算表） |
| `01-books/_verify/_meta/adr-register-backfill-adr007.json` / `-adr008.json` / 索引 | **新增/改**：按修订件留存的补录报告 + 索引（ADR-006 版保留） |
| `01-books/_verify/_meta/verify-contract.md` | 改：§0 登记表增 `aposd` 行 + OCR 一路说明与语料口径警示 |
| `00-plan/stage7p5-p2d-baseline.md` | **新增**：本基线 |
| `00-plan/NEXT-ROUND-PROMPT-6.md` | **新增**：下一轮接力件（`classes.never`，不公开） |
| `16-checkpoint/publish-manifest.json` | 改：`classes.never` 增 `00-plan/NEXT-ROUND-PROMPT-6.md` |

### 5.1 两个工具缺陷的实测证据（本轮核心）

| 缺陷 | 修前实测 | 修后实测 |
|---|---|---|
| `apply_secondpass --all` 对已降级记录非幂等 | 重跑会把「按保守终裁降级」改写为「未低于原判，保留原强度」；历史污染**不止上一轮发现的 sweg 3 条**：`evolutionary-arch 6 / team-topologies 11 / saip 9 / release-it 2 / sre-book 2 / workbook 3`，全层实测 **33 条**留痕处于反转态（sweg 的 3 条因上一轮已从备份还原，故本轮无需更正） | 修后 `--all` 把这 33 条**按事实还原为降级口径**（`evidence_strength` 值不变、结构逐字节等价，仅 `evidence_note`）；复跑第二次 **60/60 分片逐字节不变**；4/4 负例探针（含旧判据反证 N4）如期 |
| `adr-register-backfill.json` 单槽 | 每轮补录覆盖上一轮（ADR-006 版曾被 ADR-007 覆盖成空壳：`entries_added=0`、`entries=[]`） | 现为「一修订件一报告 + 索引」：`adr006`（1 508 B，保留）、`adr007`（8 126 B，旧单槽明细已迁移回来）、`adr008`（6 902 B）、索引 `reports[3]` `latest=ADR-008`；3/3 负例探针如期 |

> ⚠️ **33 条留痕更正的处置声明**：本轮**主动**改变了 6 个既有分片的 `evidence_note`（共 33 条），
> 属**缺陷修复后的数据更正**而非新增证据；`evidence_strength` / `anchor` / `review` 一律未动，
> `derive` 后的公开投影（`book-verification.json`）不含 `evidence_note`，故对公开层无影响。
> 更正前的字节快照：`~/.dsh-backups/stage7p5-p2d-20261101/parts/`。

---

## 6. 回滚路径

- **备份**：`~/.dsh-backups/stage7p5-p2d-20261101/`（72 MB；`_parts`、`_review`、`_meta`、`_text`、`10-dag-data`、`18-design`、`16-checkpoint`）。
- **回退顺序**：`_parts/{ledger,claims,gaps,toc}-aposd.json` 删除 → `_meta/pdf-chapters-aposd.json`、`_text/aposd.txt`、`_text/_slices/aposd/`、`_text/_ocr/aposd-extract.ocr.json` 删除 → 6 处登记回退 → `18-design/adr/ADR-008.json` 删除 + ADR-004 复原候选册/reserved/amended_by（或以备份 `18-design/adr/ADR-004.json` 覆盖）→ `writeback_gap_ids` 复原 `gaps-aposd.json`（随分片删除一并消失）→ `derive_verification` → `aggregate` → `build` → 公开层重装配重推。
- **两个工具缺陷的代码回滚**：`apply_secondpass.py` / `backfill_candidate_register.py` 从 `16-checkpoint/` 备份还原；**注意**：还原后 `--all` 会再次把 33 条留痕反转，故回滚须连同 `_parts` 备份一起还原。
- **`01-books/` 无 git 历史**（本地仓与 `_publish` 双重 ignore）⇒ 只能靠上述备份回滚。
- 本地归档仓：以 `git log --oneline -3` 为准。

---

## 7. 待裁决 / 未完成

1. **BK-008 只有作者免费抽取件**（印刷页 39–49 / 76 / 99–100 / 171–174，覆盖第 6 章全文、9.8–9.9、12 章片段、第 21 章）：全书需购买 ⇒ **本书的核验天然只覆盖 4 个章节片段，反向扫描同为部分覆盖**。已入层 7 条记录并如实标注语料口径；若要全书级核验，须先解决合法语料来源。
2. **`BK-016`（POSA Vol.1）仍未采集**（不变）：canonical `verified=false` / `confidence=low`，需先补采集。
3. **T2 → T1 晋升**：本轮候选册 T2 由 38 增至 **40**（两条新 T2 均为单源）；`--scan-promotion` 仍为「可晋升 0」。晋升属结构变更，须另立 ADR。
4. **域外贴限证据**：`MTH-J-07` / `MTH-N-05` / `TEC-J-04` 各 8 条，维持 ADR-005 边界（用户默认：维持）。
5. **公开仓历史 blob（旧）**：`NEXT-ROUND-PROMPT-3.md` 等仍在公开仓 git 历史中；彻底清除需 force-push（**未做**，用户默认不处理）。
6. **`apply_secondpass` 的兜底分支**：当 `review.first_pass_strength` 与 verdict 的 `first_pass_strength` **双缺**时仍退回「当前强度」判据（老数据兜底）；实测 789/789 条 verdict 均带该字段，故未触发。若要彻底消除，需给该分支加显式 WARN。
7. **`merge_secondpass_worklists.py` 仍会重写全部既有 `secondpass-*.json`**（内容逐字节相同）：属可接受但须跑前快照（本轮未跑该脚本，直接由主 Agent 合并 3 名工人的 verdict）。
8. 🔴 **本轮新增的历史遗留：泄漏的 OCR 书页原文仍在公开仓历史**（`16-checkpoint/_ocr/aposd-extract.raw.json`，39 KB，含 BK-008 抽取件的 OCR 结果）。HEAD 与 Pages 均已 404，但 blob 存于 commit `875d43f8` / `cc1992df` / `c44e83b5`。**彻底清除须 force-push 重写历史**（`git filter-repo` 或 `gh api` 重建），属不可逆操作 ⇒ **须用户裁决**。风险等级高于第 5 条（那是内部 Prompt，本条是被授权仅免费抽取的书页原文）。
