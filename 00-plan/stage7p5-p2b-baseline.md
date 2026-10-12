# 阶段7 阶段3 续做轮 P2b · 准入补录基线（append-only）

> 生成：2026-10-12（16 条未登记缺口提案准入补录：ADR-006 + 候选册 33→49 + WARN 11→0）
> 前一份基线：`stage7p5p1-baseline.md`（图谱指纹 `83721ec6…50ff4940`）
> **本基线取代上一份的「当前值」口径**；上一份文件保留不改（append-only）。

---

## 1. 指纹（9 文件 SHA-256）

| 文件 | SHA-256 | 相对上一份 |
|---|---|---|
| `01-books/_verify/verification-ledger.json` | `d49d142bfa3e0e803980b8b9789dbdbacd2043e72e8e47fa69d21d498348e2c4` | 不变 |
| `01-books/_verify/node-claim-map.json` | `e5851ba16350bb193593e9064bd974fada693696262ef29aff4fb34bd4e07c5d` | 不变 |
| `01-books/_verify/book-toc-index.json` | `665056e6d93393172d16fa0ac6c76998c7efb987752ab6b9b5870236cee0c68b` | 不变 |
| `01-books/_verify/reverse-gaps.json` | **`a9bb052b2bdf2d8d9839f7cfe0cf7ccbfd583daa7236611c7d190cbb22d4a5f0`** | **变更**（`07e95931…`） |
| `10-dag-data/_verification-overrides.json` | `d49abb3e802f42c96dcbe4564100d8e39fe057ab5c72d2e30ab1fb89b3fb0c79` | 不变 |
| `10-dag-data/_verification-baseline.json` | `bfc6f6b5df531ce3d29491872d11cf7e011913fb1e3ad5d18d4e7747a0ff523d` | 不变 |
| `10-dag-data/book-verification.json` | **`1464f8f20b62fb72b266885bd8e5e7941b9e9688f37bbc65a1bf983eb1ab5506`** | **变更**（`15f2c19c…`） |
| **`10-dag-data/methodology-dag.json`（图谱指纹）** | **`83721ec6d39b8138ce245852d85d11302b0155601c01102f0190c72d50ff4940`** | **不变**（本轮**零结构变更**） |
| `01-books/_verify/_meta/verify-contract.md` | `ae094c47bdfb2339c465a0e207be4b5bee4e4437e435163191c2d44f672c2751` | 不变 |

> 两处变更**均由缺口号回写驱动**（`target.proposed_node` 由中文概念名/撞号/释放号改为正式保留号），**不触及图谱结构**。故本轮**无需重建生成物的结构一致性**，但**基线必须新建**（append-only 口径）。
> 结构始终未变：**168 节点 / 364 边 / 18 组 / 18 案例**，`validate_graph.py` errors=0、`kahn 168/168`（无环）。

---

## 2. 候选册与核验层终值

| 项 | 值 |
|---|---|
| `candidate_register` 条目 | **49**（T1 **1** / T2 **37** / T3 **11**）※ 轮前 33（T1 1 / T2 21 / T3 11） |
| 候选册覆盖缺口 | **50**（轮前 34） |
| `reserved_ids_this_round` | **37**（轮前 21） |
| `released_ids_this_round` | **5**（轮前 8；出列 `ESS-H-12` / `MTH-H-05` / `TEC-I-04`，三者被本轮重新占用） |
| `reassignment_map` | **6**（轮前 4；新增 2 条撞号重取） |
| `amended_by` | `["ADR-006"]` |
| ledger 记录 | **636**（`direct 448 / partial 164 / inferred 24`）—— 不变 |
| 覆盖节点 / 缺口 | **93** / **133** —— 不变 |
| `direct` 第二路复核 | **100%**（448/448 `passed`）—— 不变 |
| 带 `proposed_node` 的缺口 | **39**（其中 **0** 条未登记，轮前 16 条未登记） |

**本轮 16 条最终号表**：

```text
CC-009 MTH-H-05   CC-010 MTH-H-06   CC-011 ESS-H-12*  CC-012 MTH-H-07   CC-013 MTH-H-08
CC-014 ESS-H-14   REF-008 ESS-H-15  REF-016 TEC-L-04  RI-016 TEC-K-07
QASC-001 MTH-M-07 QASC-002 MTH-M-08 QASC-004 ESS-M-06
SWEG-102 TEC-I-04* SWEG-103 TEC-H-05
TFA-003 MTH-J-08†  TFA-004 MTH-J-09†
（* 释放号复用；† 撞在用节点重取）
```

---

## 3. 门控全表（本轮实测）

| 门控 | 结果 |
|---|---|
| `gate_architecture.py --kind adr --input ADR-006.json` | **PASS 6/6**（新增修订件） |
| `gate_architecture.py --kind adr --input ADR-004.json` | PASS 6/6（补录后复查） |
| `gate_verification.py --check all` | **PASS 9/9**（G-V1 含 claims 完整性 / claim_id 唯一性 / 档位集合自洽性） |
| `replay_admission.py` | 一致率 **100%**（49/49）+ 负例 **4/4**；裁决表 49 = T1 1 + T2 37 + T3 11 |
| `replay_admission.py --scan-promotion` | 候选 **37** / 可晋升 **0** / 负例 **3/3**（NT5 未被跳过） |
| `negative_test_verification.py` | **11/11** |
| `negative_test_densify.py` | **11/11** |
| `derive_verification.py --check` | PASS（幂等） |
| `aggregate.py` 连跑两次 | 哈希一致（幂等）；DAG 指纹不变 |
| `validate_graph.py` | errors=0、warnings=0、kahn 168/168 |
| `gate_densify.py --check all` | **PASS 5/5** |
| `gate_coverage.py` | L6 PASS（GR-08 100% / GR-09 34.38% ≥ 30%） |
| `gate_sources.py` | L7 PASS（悬挂 0 / 可溯源 100% / verified 89.88%） |
| `gate_layout.py --check all` | L8 PASS（覆盖率 2140/2140 = 100%） |
| `gate_methodology.py --check all` | 四项全 PASS |
| `kb_gate.py`（structure,links） | PASS 2/2（5 397 检查项，问题 0） |
| `gate_visual.py --check all` | **L4 PASS** |
| `gate_render.py --timeout 25` | **L5 PASS**（7/7 案例，skipped=0） |
| `check_corpus_overlap.py --target evidence` | **0 命中** |
| `writeback_gap_ids.py --check` | PASS（50/50 命中、变更 0 —— 幂等） |
| `normalize_gap_ids.py --check` | PASS（重指派 0 / 非法 0 / 撞号 0） |
| `validate_staging_shards.py`（6 书） | WARN **11 → 0**；problems 未新增（clean-code 14 / refactoring 19 为既有章头缺失） |

---

## 4. 公开层对账（**含本轮两处机制纠正**）

```text
推送           = 1 次（Git Data API）：new_commit d54698e3aeb7，tree ef85fb855f92，parent 6499c3962f3e
                 CI（rebuild）= run 38223829041 success（31s）
删除           = 1 次（Contents API DELETE）：commit 9a38db50（下架 NEXT-ROUND-PROMPT-3.md）
远端 HEAD      = 9a38db50dbb9829ea99897b74cd8489db673953f
remote blobs   = 576  ==  本地 _publish ls-files 576
Pages          = index.html 200
装配           = --apply --refresh-sanitize 后 --check 三类差异 0/0/0（570 期望 + 6 preserve）
gate_disclosure= PASS（0 hit / 511 file）
```

> **纠正①（假绿）**：`assemble_publish.py --check` 的 `sanitize` 类取自 `_publish-staging/`，只有 `--refresh-sanitize` 才按当前源重生成 ⇒ **只跑 `--check` 会对「仅改了 `00-plan/*.md`」的轮次给出假绿**。终局对账必须 `--apply --refresh-sanitize` 之后再 `--check`。
> **纠正②（不能下架）**：`push_publish.py` 用 `base_tree` + 本地 `git ls-files` 构树，**远端已有而本地没有的文件会被自动保留** ⇒ 「归 `classes.never`」只阻止新增，**下架须显式 DELETE**（本轮已对 `NEXT-ROUND-PROMPT-3.md` 执行）。
> ⚠️ 该文件的 blob 仍在公开仓 **git 历史**中（未做 history rewrite）。

---

## 5. 本轮新增/修改的可执行物

| 文件 | 性质 |
|---|---|
| `16-checkpoint/backfill_candidate_register.py` | **新增**：把修订型 ADR 的 `backfill_entries` + `id_allocation_delta` 并入 ADR-004 候选册；fail-closed（tier / id_status / 号形态 / 层前缀 / 图谱占用 / 释放号复用三条件）+ 幂等 + no-op 守卫；3 条负例探针实测拒写 |
| `16-checkpoint/publish-manifest.json` | 改：`classes.never` 补 `00-plan/NEXT-ROUND-PROMPT-3.md` / `-4.md` |
| `18-design/adr/ADR-006.json` / `.md` | **新增**：16 条未登记提案的准入裁决与取号（`amends: ["ADR-004"]`） |
| `18-design/adr/ADR-004.json` / `.md` | 改：候选册 33→49、号表增量、`amended_by: ["ADR-006"]` |
| `01-books/_verify/_meta/adr006-inputs.json` | **新增**：ADR-006 输入包（16 条缺口原文 + 取号上下文），私有层 |
| `01-books/_verify/_meta/adr-register-backfill.json` | **新增**：补录报告（含 3 条释放号复用的原概念留痕） |

---

## 6. 回滚路径

- **备份**：`~/.dsh-backups/stage7p5-p2b-20261012/`（38 MB；`01-books/_verify/_parts`、`_meta`、`_review`、`_text`、`10-dag-data`、`18-design` + `ADR-004.pre-backfill.json` / `ADR-006.pre-patch.json` + `pre-state-validate-staging.txt`）。
- **回退顺序**：`_parts/gaps-*.json` 回滚 → `18-design/adr/ADR-004.json` 回滚（或删 16 条 `amended_by=ADR-006` 条目 + 还原号表）→ `derive_verification` → `aggregate` → `build` → 公开层重装配。
- **`01-books/` 无 git 历史**（本地仓与 `_publish` 双重 ignore）⇒ 只能靠上述备份回滚。
- 本地归档仓：`git log --oneline -3`。

---

## 7. 待裁决 / 未完成

1. **D3-2 域外贴限证据**：`MTH-J-07` / `MTH-N-05` / `TEC-J-04` 各 8 条，维持 ADR-005 边界（**用户默认：维持**）；恢复须另立 ADR。
2. **D3-4 轨B 下一批书**：BK-013（`P1-19` PDF 591 页，**有文本层**）/ BK-022（`P0-10` PDF 458 页，**有文本层**）可用 `pdftotext` 直接抽取，**无需 OCR**；BK-008 仅 20 页无文本层抽取件（需 OCR + 补采全文）；BK-016（POSA Vol.1）**未采集**（仅被知识图引用）。
3. **公开层历史 blob**：`NEXT-ROUND-PROMPT-3.md` 仍在公开仓 git 历史中；彻底清除需 `force-push` 重写历史（**未做**，用户未要求）。
4. **16 条 T2 的补证义务**：均需取得**第二独立信源**后方可晋升 T1（入图）。
