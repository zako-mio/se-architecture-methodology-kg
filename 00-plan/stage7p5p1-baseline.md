# 阶段7 阶段3 续做轮 · P0+P1 基线（append-only）

> 生成：2026-10-12（P0 claims 链修复 + P1 K 域上限 ADR-005 + 42 条证据回捞轮收尾）
> 前一份基线：`stage7p5-baseline.md`（指纹 `f1f09a9b…87303a39`）
> **本基线取代上一份的「当前值」口径**；上一份文件保留不改（append-only）。

---

## 1. 指纹（9 文件 SHA-256）

| 文件 | SHA-256 |
|---|---|
| `01-books/_verify/verification-ledger.json` | `d49d142bfa3e0e803980b8b9789dbdbacd2043e72e8e47fa69d21d498348e2c4` |
| `01-books/_verify/node-claim-map.json` | `e5851ba16350bb193593e9064bd974fada693696262ef29aff4fb34bd4e07c5d` |
| `01-books/_verify/book-toc-index.json` | `665056e6d93393172d16fa0ac6c76998c7efb987752ab6b9b5870236cee0c68b` |
| `01-books/_verify/reverse-gaps.json` | `07e95931ad2b84df2d3dc2f98239a10178871a06fbe04e6f4323376d1f88a463` |
| `10-dag-data/_verification-overrides.json` | `d49abb3e802f42c96dcbe4564100d8e39fe057ab5c72d2e30ab1fb89b3fb0c79` |
| `10-dag-data/_verification-baseline.json` | `bfc6f6b5df531ce3d29491872d11cf7e011913fb1e3ad5d18d4e7747a0ff523d` |
| `10-dag-data/book-verification.json` | `15f2c19c99ba347f31c3034797ee81a0962731bbcf787fce63fbfd42798b0870` |
| **`10-dag-data/methodology-dag.json`（图谱指纹）** | **`83721ec6d39b8138ce245852d85d11302b0155601c01102f0190c72d50ff4940`** |
| `01-books/_verify/_meta/verify-contract.md` | `ae094c47bdfb2339c465a0e207be4b5bee4e4437e435163191c2d44f672c2751` |

> **图谱指纹三次变更**：`f1f09a9b…87303a39` →（P1 证据恢复）`a96354c7…46378f85` →（BK-036/BK-031 合并）`9f87d1cd…6070cb68` →（BK-001 合并 + 三本第二路复核）**`83721ec6…50ff4940`**。
> 三次变更**均由核验层证据变化驱动**（`aggregate.py` 把 `_verification-overrides.json` 并回节点）：
> · 15 个节点的 `review_date` 由 `2026-09-10/11` 前移至 `2026-10-11`；
> · **`MTH-K-04` 的 `confidence` 由 `medium` 升为 `high`**（恢复的 direct 证据使其重新具备升级依据）；
> · 三本新书合并后覆盖节点 78 → **93**。
> 结构始终未变：168 节点 / 364 边 / 18 组 / 18 案例，`validate_graph.py` errors=0、`kahn 168/168`（无环）。

---

## 2. 核验层终值

| 项 | 值 |
|---|---|
| ledger 记录 | **636**（`direct 448 / partial 164 / inferred 24`） |
| `node-claim-map` 的 claim 数 | **636**（与 ledger 逐条相等） |
| **claims 完整性差集** | **0**（`ledger.claim_id − node-claim-map.claim_id = ∅`） |
| 全层重复 `claim_id` | **0 组** |
| 覆盖节点 | **93**（= `_verification-overrides.json` 节点数） |
| 缺口 | **133**（`missed_citation 66 / coverage_hole 43 / concept_missing 24`） |
| 逐书记录数（**13 本**） | `saip 96 / team-topologies 81 / workbook 77 / sre-book 76 / evolutionary-arch 71 / ddia 58 / clean-architecture 35 / **sweg 35** / refactoring 24 / release-it 24 / **twelve-factor 24** / **saip-ch4 21** / clean-code 14` |
| `verified` | `true` **151** / `"cited"` **17**（GR-10 = 89.88%） |
| 单节点上限 | 超限 **0**；`DENSIFY_NODES` = **41**（`STAGE2_NODES` 26 ∪ `K_DOMAIN_NODES` 17） |
| K 域逐节点 | `ESS-K-01 11 / ESS-K-02 12 / ESS-K-03 8 / ESS-K-04 11 / MTH-K-01 12 / MTH-K-02 11 / MTH-K-03 10 / MTH-K-04 12 / MTH-K-05 12 / MTH-K-06 7 / MTH-K-07 11 / TEC-K-01 7 / TEC-K-02 11 / TEC-K-03 11 / TEC-K-04 6 / TEC-K-05 6 / TEC-K-06 10`（最高 12 ≤ 16） |
| 域外贴限节点 | `MTH-J-07 8 / MTH-N-05 8 / TEC-J-04 8`（ADR-005 显式**不放宽**） |
| 第二路复核 | 全部 `direct` 的 `review.second_pass ∈ {passed, disputed}` **100%**（`direct` 448 条，缺口 0） |

---

## 3. 门控全表（本轮实测）

| 门控 | 结果 |
|---|---|
| `gate_verification.py --check all` | **PASS 9/9**（G-V1 含 claims 完整性 + claim_id 唯一性 + 档位集合自洽性） |
| `negative_test_verification.py` | **11/11 如期**（含 `claims_incomplete`、`duplicate_claim_id`、`k_domain_at_cap_16=PASS`、`k_domain_over_cap_17=FAIL`、`out_of_domain_over_cap_9=FAIL`） |
| `derive_verification.py --check` | PASS（幂等） |
| `gate_densify.py --check all` | **PASS 5/5** |
| `negative_test_densify.py` | **11/11** |
| `gate_coverage.py` | L6 PASS（GR-08 100% / GR-09 34.38% ≥ 30%） |
| `gate_sources.py` | L7 PASS（悬挂 0 / 可溯源 100% / verified 89.88%） |
| `gate_layout.py --check all` | L8 PASS（覆盖率 2140/2140 = 100%） |
| `gate_methodology.py --check all` | 四项全 PASS |
| `kb_gate.py`（structure,links） | PASS 2/2（442 / 5374 检查项，问题 0） |
| `gate_visual.py --check all` | **L4 PASS**（212/272，0 FAIL，60 skip） |
| `gate_render.py --timeout 25` | **L5 PASS**（7/7 case） |
| `check_corpus_overlap.py --target evidence` | **0 命中**（134 对象 / 6 046 349 distinct 20-gram） |
| `replay_admission.py` | 一致率 **100%** + 负例 **4/4** |
| `writeback_gap_ids.py --check` / `normalize_gap_ids.py --check` | PASS |
| `validate_graph.py` | errors=0、warnings=0、kahn 168/168 |
| `aggregate.py` 连跑两次 | 哈希一致（幂等） |
| `gate_architecture.py --kind adr --input ADR-005.json` | **PASS 6/6** |
| `gate_architecture.py --kind adr --input ADR-003.json` | PASS 6/6（加 `amended_by` 后仍通过） |

---

## 4. 公开层对账

```
公开仓远端 HEAD  = 6499c3962f3e（tree 33e44236a8e3）
remote blobs     = 576  ==  本地 _publish ls-files 576
CI（rebuild）    = run 38191360446 success（前两次 38188672569 / 38189349224 亦 success）
Pages            = index.html / 11-node-pages/MTH-K-04.html / 10-dag-data/methodology-dag.json 均 200
装配             = 0/0/0（--check 三类差异 0）；gate_disclosure PASS（0 hit / 512 file）
```

> **本轮共推送 3 次**：① P1 证据恢复的生成物；② 图谱终值（P1 后的 DAG）；③ **轨B 三本核验入层**（ledger 636 / 覆盖节点 93 / 第二路复核 100%）。
> 每次均先在 `_publish` 内 `git add -A && git commit`，再用 `push_publish.py --apply --message`；三次 CI 均自动触发并 **success**。

---

## 5. 本轮新增/修改的可执行物

| 文件 | 性质 |
|---|---|
| `16-checkpoint/fill_missing_claims.py` | 新增：补齐「ledger 有记录、claims 分片缺失」的主张（含无 staging 书的手写 SSOT 例外） |
| `16-checkpoint/fix_duplicate_claim_ids.py` | 新增：历史重复 `claim_id` 确定性重编号（同步 ledger 分片 + staging + secondpass verdict） |
| `16-checkpoint/recover_trimmed_records.py` | 新增：从 DSH 会话转录（多帧 zstd，ctypes libzstd 流式）回捞被裁记录 + 域外裁回 |
| `16-checkpoint/make_secondpass_worklist.py` | 新增：为恢复记录生成第二路复核工单 |
| `16-checkpoint/merge_secondpass_worklists.py` | 新增：合并复核工单结论进 `secondpass-<slug>.json`（claim_id 按当前 ledger 归一化） |
| `16-checkpoint/extract_web_book.py` | 新增：在线书 DOM 抽取（oreilly/article/body 三种容器；章头格式 `=== N \| Title ===`） |
| `16-checkpoint/slice_corpus_by_chapter.py` | 新增：按章切片语料（供子 Agent 窄读，规避上下文耗尽） |
| `16-checkpoint/derive_verification.py` | 改：`build_claims()` 由「首 slug 胜出」改为**按 claim_id 跨 slug 并集去重** |
| `16-checkpoint/gate_verification.py` | 改：G-V1 增 claims 完整性 / claim_id 唯一性 / 档位集合自洽性；`STAGE2_NODES` 与 `K_DOMAIN_NODES` 拆分，`DENSIFY_NODES` 26→41 |
| `16-checkpoint/merge_verify_staging.py` | 改：**第二路复核护栏**（拒写会回退 second_pass 的书，须 `--force`） |
| `16-checkpoint/apply_secondpass.py` | 改：追加留痕前先剥历史标记（**幂等修复**，此前实测叠 3 份） |
| `16-checkpoint/negative_test_verification.py` | 改：支持期望 PASS；新增 5 条用例（8→11 例） |
| `18-design/adr/ADR-005.json/.md` | 新增：K 域 17 节点纳入 densify（上限 16），`amends: ["ADR-003"]` |
| `18-design/adr/ADR-003.json` | 改：加 `amended_by` / `amendment_note` |
| `01-books/_verify/_meta/verify-contract.md` | 改：§5.1/§5.2/§8/§10（生成链顺序与护栏、无 staging 例外、新 slug 登记表） |

---

## 6. 回滚路径

- **备份（唯一）**：`~/.dsh-backups/stage7p5-p1-20261012/`（11 MB；`_parts` / `_meta` / `_review` / `_text` / `10-dag-data`）。
  > ⚠️ 本轮**首份**备份 `/tmp/round-p0p2-backup-20261012/` 在会话间隙被环境清理（`/tmp` 易失），已重建到 `~/.dsh-backups/`。
- **会话转录（回捞数据源）**：`~/.dsh/sessions/--home-zako-mio-opencode-archive-Mission-file-2026-09-0910-…--/`（71 个会话，多帧 zstd）。
- **`01-books/` 无 git 历史**（本地仓与 `_publish` 双重 gitignore）⇒ 只能靠上述备份回滚。
- 本地归档仓：`git log --oneline -3` = `44215a3` → `05cd956` → `364abfc`。

---

## 7. 待裁决 / 未完成

1. **P2 已完成（轨B 三本全部入层）**：
   · **BK-036（`saip-ch4`）**：21 记录 / 7 节点 / 4 缺口；第二路复核 19 条 direct（**1 降级** `VR-QASC-008` → inferred，锚点不可定位）。
   · **BK-031（`twelve-factor`）**：24 记录 / 6 节点 / 4 缺口；第二路复核 21 条 direct（**0 降级**）。
   · **BK-001（`sweg`）**：35 记录 / 8 节点 / 6 缺口；第二路复核 34 条 direct（**4 降级**：`VR-SWEG-003/113/116` → partial、`VR-SWEG-101` → inferred 且锚点不可定位）。
   · 合计入层 **80 条记录**（ledger 556 → 636）、覆盖节点 78 → **93**、缺口 119 → **133**；公开层已推送（见 §4）。
   · ⚠️ **合并过程中的一处自愈**：BK-001 part a 工人**在其自述产出后重写了 `ledger-sweg-a.json`**（19 → 16 条，去掉 `VR-SWEG-017/018/019`）。主 Agent 以「staging 为权威」**重跑了 `merge_verify_staging.py --only sweg`**，使 `_parts` 与 staging 一致；由此产生的 3 条悬挂 verdict 由 `apply_secondpass.py` 记为 unmatched（已核验：最终 `direct` 448 条 **verdict 覆盖 100%**）。
2. **域外贴限证据**：`MTH-J-07 / MTH-N-05 / TEC-J-04` 各 8 条，恢复的 8 条域外记录已按 ADR-005 边界裁回，**须另立 ADR** 才能恢复。
3. **新缺口提案未登记**（WARN，共 **7 条**）：`GAP-QASC-001/002/004`（BK-036）、`GAP-TFA-003/004`（BK-031）、`GAP-SWEG-102/103`（BK-001）的 `proposed_node` 未在 ADR-004 候选册登记 ⇒ 须走 ADR-004 准入或改判 `existing_node_id`。
4. **J#3（P0-09 真第 2 版）**：本轮 bounded 尝试结论 = **未采集**。检索仅见 [martinfowler.com 官方书页](https://martinfowler.com/books/refactoring.html)（无全文）与若干**未授权**「免费 PDF」聚合站；按项目版权纪律（`unknown-thirdparty`）**不采用**。维持 `1st/1999` + `edition_mismatch=true`（已如实标注，manifest 未改）。
5. **J#4/J#5/J#7**：维持默认（只私有层 / 保持现状 / 不碰），本轮无动作。
