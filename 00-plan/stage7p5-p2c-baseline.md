# 阶段7 阶段3 续做轮 P2c · 双书核验入层基线（append-only）

> 生成：2026-10-12（BK-013《Documenting Software Architectures》/ BK-022《Working Effectively with Legacy Code》核验入层 + ADR-007 准入补录 + 图谱再生 + 公开层同步）
> 前一份基线：`stage7p5-p2b-baseline.md`（图谱指纹 `83721ec6…50ff4940`）
> **本基线取代上一份的「当前值」口径**；上一份文件保留不改（append-only）。

---

## 1. 指纹（9 文件 SHA-256）

| 文件 | SHA-256 | 相对上一份 |
|---|---|---|
| `01-books/_verify/verification-ledger.json` | **`873b0ae27480101772116f1e7229e9b12b8bd89dd593ad0a3ffd6a5233b4f655`** | **变更**（`d49d142b…`） |
| `01-books/_verify/node-claim-map.json` | **`f0c8addd806f49725f65c10a015883c082ce1dcf68376e6488046e079b4c0914`** | **变更**（`e5851ba1…`） |
| `01-books/_verify/book-toc-index.json` | **`fd77c0df8041746cfa0c54bc0bf2bd4a79a3cfc388133c1c3bbeb03255a959f7`** | **变更**（`665056e6…`） |
| `01-books/_verify/reverse-gaps.json` | **`cd75c96f87021d69f9882f84eab5ef02c7acd4e05714334c7c4b8089b34993e2`** | **变更**（`a9bb052b…`） |
| `10-dag-data/_verification-overrides.json` | **`6a7cdc16f2f26f5e5201259db144c4f7efeaa8b8231bb5b8efd08abcf127a722`** | **变更**（`d49abb3e…`） |
| `10-dag-data/_verification-baseline.json` | `bfc6f6b5df531ce3d29491872d11cf7e011913fb1e3ad5d18d4e7747a0ff523d` | 不变 |
| `10-dag-data/book-verification.json` | **`cde38b289907fabccbb220cdb7ec35a59b946298e62296c90aa94bb4a2ce8fef`** | **变更**（`1464f8f2…`） |
| **`10-dag-data/methodology-dag.json`（图谱指纹）** | **`c413c6fda1020608dfbef659926b6b3fa0c73b897087213f33a3dbf4a6a8fc21`** | **变更**（`83721ec6…`） |
| `01-books/_verify/_meta/verify-contract.md` | **`1710faa904501fdecbf2c3c965bba584caad2407eab178ebc0a46f72a00892ce`** | **变更**（`ae094c47…`） |

> **图谱指纹本轮变更**（`83721ec6…50ff4940` → `c413c6fd…a6a8fc21`）：由核验层证据变化驱动
> （`aggregate.py` 把 `_verification-overrides.json` 并回节点）——**7 个节点新增覆盖**（`ESS-G-06` /
> `MTH-G-01` / `MTH-G-05` / `CAS-X-01` / `CAS-X-09` / `MTH-L-06` / `TEC-L-02`）使其 `verified` 由
> `"cited"` 变为 `true`、`confidence` 升 `high`、`review_date` 前移至 `2026-10-12`；另有既有节点
> 因新书记录加入而 `review_date` 前移。
> **结构始终未变**：**168 节点 / 364 边 / 18 组 / 18 案例**，`validate_graph.py` errors=0、warnings=0、`kahn 168/168`（无环）。

---

## 2. 核验层终值（15 本已核验书）

| 项 | 值 |
|---|---|
| ledger 记录 | **691**（`direct 499 / partial 168 / inferred 24`）※ 轮前 636（448/164/24） |
| `node-claim-map` 的 claim 数 | **691**（与 ledger 逐条相等） |
| **claims 完整性差集** | **0** |
| 全层重复 `claim_id` | **0 组** |
| 覆盖节点 | **100**（= `_verification-overrides.json` 节点数）※ 轮前 93 |
| 缺口 | **148**（`missed_citation 71 / coverage_hole 49 / concept_missing 28`）※ 轮前 133 |
| 逐书记录数（**15 本**） | `saip 96 / team-topologies 81 / workbook 77 / sre-book 76 / evolutionary-arch 71 / ddia 58 / **documenting-sa 37** / clean-architecture 35 / sweg 35 / refactoring 24 / release-it 24 / twelve-factor 24 / saip-ch4 21 / **welc 18** / clean-code 14` |
| `verified` | `true` **153** / `"cited"` **15**（GR-10 = 91.07%）※ 轮前 151 / 17 = 89.88% |
| 单节点上限 | 超限 **0**；`DENSIFY_NODES` = **41**（未变） |
| 第二路复核 | **全部 `direct` 499 条均有 verdict（100%）**；`apply_secondpass --all` 报 `未复核 direct = 0`、`悬挂 verdict = 0`、`downgraded = 0` |
| 第二路总账 | `matched 491 / passed 446 / disputed 45`（轮前 `matched 436 / passed 391 / disputed 45`） |

**本轮两本的明细**：

```text
BK-013 documenting-sa（2nd/2010，P1-19 PDF 591 页）
  records 37（direct 34 / partial 3），覆盖 7 节点，缺口 9
  ESS-G-06 6 ｜ MTH-O-09 8 ｜ MTH-G-01 6 ｜ CAS-X-09 5 ｜ MTH-G-05 4 ｜ CAS-X-01 4 ｜ ESS-G-07 4
BK-022 welc（1st/2004，P0-10 PDF 458 页）
  records 18（direct 17 / partial 1），覆盖 5 节点，缺口 6
  MTH-L-06 6 ｜ TEC-L-02 6 ｜ MTH-H-01 2 ｜ MTH-L-01 2 ｜ CAS-X-04 2
合计：records 55（direct 51）／新覆盖节点 7（93 → 100）／新增缺口 15（133 → 148）
```

**准入补录（ADR-007）**：

| 项 | 值 |
|---|---|
| 候选册条目 | **49 → 52**（`T1 1 / T2 38 / T3 13`） |
| 候选册覆盖缺口 | **50 → 53** |
| `reserved_ids_this_round` | **37 → 38**（新增 `MTH-G-13`） |
| `released_ids_this_round` | **5**（不变） |
| `reassignment_map` | 6（不变） |
| `amended_by` | `["ADR-006", "ADR-007"]` |
| 三条裁决 | `GAP-DSA-106` ⇒ **T2 / `MTH-G-13` / newly-allocated**；`GAP-DSA-003` ⇒ **T3 / no-id / 宿主 `MTH-G-05`**；`GAP-WELC-002` ⇒ **T3 / no-id / 宿主 `TEC-L-02`** |
| 未登记 `proposed_node` | **0**（轮前 0；本轮新增 3 条已由 ADR-007 收口） |

---

## 3. 门控全表（本轮实测）

| 门控 | 结果 |
|---|---|
| `gate_architecture.py --kind adr --input ADR-007.json` | **PASS 6/6**（首轮 5/6 FAIL G-A5，机械修掉 `decision` 中残留技术层号后复跑 6/6） |
| `gate_architecture.py --kind adr --input ADR-004.json` | PASS 6/6（补录后复查） |
| `gate_verification.py --check all` | **PASS 9/9** |
| `extract_pdf_book.py --negative-test` | **3/3 如期按应有理由拒写**（页数不符 / 标题不在声明页 / 页码非递增） |
| `validate_staging_shards.py`（两本新书） | problems **0**、WARN **0** |
| `replay_admission.py` | 一致率 **100.00%** + 负例 **4/4** |
| `replay_admission.py --scan-promotion` | 候选 **38** / 可晋升 **0** / 负例 **3/3**（**新提案行 = 0**，三条已入册） |
| `negative_test_verification.py` | **11/11** |
| `negative_test_densify.py` | **11/11** |
| `derive_verification.py --check` | PASS（幂等，6 产物全 up-to-date） |
| `aggregate.py` 连跑两次 | 哈希一致（幂等） |
| `build.py --config mother` 连跑两次 | 产出总哈希一致（`2ed6a2d9…`） |
| `validate_graph.py` | errors=0、warnings=0、kahn 168/168 |
| `gate_densify.py --check all` | **PASS 5/5** |
| `gate_coverage.py` | L6 PASS（manifest 100% / 四向 100% / GR-08 GR-09 PASS） |
| `gate_sources.py` | L7 PASS（悬挂 0 / 可溯源 100% / verified **91.07%**） |
| `gate_layout.py --check all` | L8 PASS（覆盖率 2140/2140 = 100%） |
| `gate_methodology.py --check all` | 四项全 PASS |
| `kb_gate.py`（structure,links） | PASS 2/2（**5 419** 检查项，问题 0） |
| `gate_visual.py --check all` | **L4 PASS**（212/272 = 77.94%，0 FAIL，60 skip —— 与上一份基线**完全一致**） |
| `gate_render.py --timeout 25` | **L5 PASS**（7/7 案例，skipped=0） |
| `check_corpus_overlap.py --target evidence` | **0 命中**（134 对象 / **8 561 894** distinct 20-gram，轮前 6 046 349） |
| `writeback_gap_ids.py --check` | PASS（命中 53/53、需变更 0 —— 幂等） |
| `normalize_gap_ids.py --check` | PASS（重指派 0 / 非法 0 / 撞号 0） |

> ⚠️ **L4/L5 的环境前提（本轮实测）**：`gate_visual` / `gate_render` 用 headless Chromium（`agent-browser`），
> 其 socket 目录为 `$HOME/.agent-browser` ⇒ **工作区只读沙箱下会 32/32 全 FAIL**
> （`Socket directory ... is not writable: Read-only file system`），**不是内容缺陷**。
> 须以放宽沙箱（工作区外可写）重跑方可得到真实判定。

---

## 4. 公开层对账

```text
推送           = 1 次（Git Data API）：parent ccad1873a9eb / base_tree 513f88528a64
                 → new_commit 96a89ae7453b / new_tree 3f782b674728
                 （`_publish` 本地提交 32f3eb9；推送前已在 `_publish` 内 git add -A && git commit）
远端 HEAD      = 96a89ae7453bdfa071a09a6458f5faf048770a15
remote blobs   = 579  ==  本地 _publish ls-files 579
CI             = run 38234154454（push 自动触发，36s）**success**
                 （本轮改了 10-dag-data/** 与 16-checkpoint/**，故**自动触发**，无需手动 workflow_dispatch）
Pages 回验     = / 、00-plan/stage7p5-p2c-baseline.md 、00-plan/NEXT-SESSION-HANDOFF.md 、
                 11-node-pages/ESS-G-06.html 、11-node-pages/TEC-L-02.html 、
                 10-dag-data/methodology-dag.json 、14-views/06-book-verification.html 、
                 16-checkpoint/extract_pdf_book.py   均 **200**
                 ；00-plan/NEXT-ROUND-PROMPT-3.md / -4.md / -5.md 均 **404**（`never` 类生效）
装配           = --apply --refresh-sanitize 后 --check 三类差异 0/0/0；P1–P5 预检全 OK（573 文件）
gate_disclosure= PASS（0 hit / 513 file）
```

> **纠正确认**：本轮改动了 `10-dag-data/**` 与 `16-checkpoint/**` ⇒ CI **自动触发**（实测 run 38234154454 在推送后 25s 内出现），
> 与「只改 `00-plan/**` 的推送不触发 CI」不矛盾；若下轮只改文档，仍须手动 `gh workflow run rebuild.yml` 并回验 Pages。

---

## 5. 本轮新增/修改的可执行物

| 文件 | 性质 |
|---|---|
| `16-checkpoint/extract_pdf_book.py` | **新增**：PDF → 纯文本抽取器（章图驱动；页数 / 标题落位 / 页码递增三条 fail-closed；`--check` 与 `--negative-test` 3 条负例探针） |
| `16-checkpoint/gate_verification.py` | 改：`SLUG_RECORD_PREFIX` / `SLUG_TEXT` / `SOURCE_SLUG` 各增 `documenting-sa`/`welc`（**6 处登记中的 3 处**） |
| `16-checkpoint/merge_verify_staging.py` | 改：`BOOKS` 增 `dsa`/`welc` |
| `16-checkpoint/check_corpus_overlap.py` | 改：`CORPUS` 增两份新语料 |
| `18-design/adr/ADR-007.json` / `.md` | **新增**：3 条新缺口提案的准入裁决（`amends: ["ADR-004"]`） |
| `18-design/adr/ADR-004.json` | 改：候选册 49→52、`reserved_ids_this_round` 37→38、`amended_by` 增 ADR-007 |
| `01-books/_verify/_meta/pdf-chapters-documenting-sa.json` / `-welc.json` | **新增**：章图（页码 + 印刷页码；**唯一承载页码处**，私有层） |
| `01-books/_verify/_meta/adr007-inputs.json` | **新增**：ADR-007 输入包（3 条提案原文 + 号占用现算表） |
| `01-books/_verify/_meta/adr-register-backfill.json` | 改：本轮补录报告（⚠️ 该文件为**单槽**，已覆盖 ADR-006 版；旧版另存 `adr-register-backfill-adr006.json`） |
| `01-books/_verify/_meta/gap-id-writeback.json` | 改：缺口号回写报告 |
| `01-books/_verify/_meta/verify-contract.md` | 改：§0 登记表增 2 行 + PDF 一路说明 + **登记处 6 处（非 4 处）**与伪绿警示 + §10 只并新书姿势 |
| `00-plan/stage7p5-p2c-baseline.md` | **新增**：本基线 |
| `00-plan/NEXT-ROUND-PROMPT-5.md` | **新增**：下一轮接力件（`classes.never`，不公开） |
| `16-checkpoint/publish-manifest.json` | 改：`classes.never` 增 `00-plan/NEXT-ROUND-PROMPT-5.md` |

---

## 6. 回滚路径

- **备份**：`~/.dsh-backups/stage7p5-p2c-20261012/`（66 MB；`01-books/_verify/{_parts,_meta,_review,_text}`、`10-dag-data`、`18-design`、`16-checkpoint`）。
- **回退顺序**：`_parts/{ledger,claims,gaps}-{documenting-sa,welc}.json` 删除 → `_meta/pdf-chapters-*` 与 `_text/{documenting-sa,welc}.txt`、`_text/_slices/{…}` 删除 → 6 处登记回退 → `18-design/adr/ADR-007.*` 删除 + ADR-004 删 `amended_by=ADR-007` 条目并复原 `reserved_ids_this_round` → `derive_verification` → `aggregate` → `build` → 公开层重装配重推。
- **`01-books/` 无 git 历史**（本地仓与 `_publish` 双重 ignore）⇒ 只能靠上述备份回滚。
- 本地归档仓：以 `git log --oneline -3` 为准。

---

## 7. 待裁决 / 未完成

1. **`apply_secondpass.py --all` 对「已降级」记录非幂等（本轮实测）**：重跑会把既有
   `【第二路复核】判为 partial（原判 direct），按保守终裁降级。` 改写成
   `【第二路复核】结论有分歧但未低于原判（复核=partial），保留原强度。`
   （**数据值不变**，留痕语义反转）。本轮已从备份还原 `ledger-sweg.json`（3 处）并以
   `--slug`/新书范围收口；⚠️ **根治需给脚本加幂等判据**（下轮）。
2. **`merge_secondpass_worklists.py` 会重写全部既有 `secondpass-<slug>.json`**（内容逐字节相同，实测 30/30 不变）——属可接受但需留意。
3. **`adr-register-backfill.json` 是单槽报告**：每轮补录会覆盖上一轮（本轮已另存 ADR-006 版）。建议改为按修订件命名（下轮）。
4. **域外贴限证据**：`MTH-J-07` / `MTH-N-05` / `TEC-J-04` 各 8 条，维持 ADR-005 边界（用户默认：维持）。
5. **公开层历史 blob**：`NEXT-ROUND-PROMPT-3.md` 仍在公开仓 git 历史中；彻底清除需 force-push（**未做**）。
6. **T2 → T1 晋升**：候选册 38 条 T2 均需第二独立信源方可晋升；`--scan-promotion` 现为「可晋升 0」。
7. **下一批书**：`BK-008`（需 OCR 且非全书）/ `BK-016`（POSA Vol.1 未采集）；轨B 高密度书已核验 15 本。
