# 阶段7 阶段3 续做轮 P2e · BK-017（DDD）核验入层 + ADR-009 准入补录 + 两个工具兜底收口 基线（append-only）

> 生成：2026-11-02（BK-017《Domain-Driven Design》PDF 全书核验入层；9 条反向缺口经 ADR-009 判 T2 占号；`apply_secondpass` 兜底分支加显式 WARN；`merge_secondpass_worklists` 加「无变化不写盘」守卫；图谱再生；公开层同步）
> 前一份基线：`stage7p5-p2d-baseline.md`（图谱指纹 `9212644f…9bc647a`）
> **本基线取代上一份的「当前值」口径**；上一份文件保留不改（append-only）。

---

## 1. 指纹（9 文件 SHA-256）

| 文件 | SHA-256 | 相对上一份 |
|---|---|---|
| `01-books/_verify/verification-ledger.json` | **`77964962c3a1493b7740c2537d93a6a290c08190679f6aae3053734afd93e18d`** | **变更**（`495493ef…`） |
| `01-books/_verify/node-claim-map.json` | **`776a5f59533b7960621683a0cea3ca931d008a98a1466cadfeb8d14cc41b18a9`** | **变更**（`4f73a2cb…`） |
| `01-books/_verify/book-toc-index.json` | **`f18a1fbddfa18546e4779a87b04f46c560e5509ac0bbb9444208d9889dcba1ff`** | **变更**（`686abd7e…`） |
| `01-books/_verify/reverse-gaps.json` | **`65b6e11df28acfaaf8c478ad32cf5854f30b3b26e710c701b75138730a19d208`** | **变更**（`0f788a4f…`） |
| `10-dag-data/_verification-overrides.json` | **`ed734f9f726b812f250f0c8ad631f7a4d9b76fb36dc040b7499fd9517caeddf8`** | **变更**（`6c634822…`） |
| `10-dag-data/_verification-baseline.json` | `bfc6f6b5df531ce3d29491872d11cf7e011913fb1e3ad5d18d4e7747a0ff523d` | 不变 |
| `10-dag-data/book-verification.json` | **`eff8e18ad446a9ce5ab8afe19d80357ad30faf587ec7275ad141f39f7aaf1611`** | **变更**（`92cf66b0…`） |
| **`10-dag-data/methodology-dag.json`（图谱指纹）** | **`690cfbdbab7b5a054d12de1dfb078737dfbd91b42951579cc6a7141e3aa85405`** | **变更**（`9212644f…`） |
| `01-books/_verify/_meta/verify-contract.md` | **`9cd1ff281bf7dbefcf2da318d6428912c2e1fd6b39303df9a506247c1308a7fb`** | **变更**（`536028c9…`） |

> **图谱指纹本轮变更**（`9212644f…` → `690cfbdb…`）由核验层证据变化驱动（`aggregate.py` 把 `_verification-overrides.json` 并回节点）：
> **4 个此前零记录节点首次入层** —— `ESS-G-05`（架构风格）/ `ESS-H-09`（设计模式与反模式）/ `ESS-L-03`（架构侵蚀与漂移）/ `MTH-H-03`（战略式编程与持续设计投入）；
> 另有 8 个既有被覆盖节点因新增记录而 `review_date` 前移至 `2026-11-02`（`ESS-G-01` / `ESS-G-03` / `ESS-G-04` / `ESS-H-05` / `ESS-H-07` / `ESS-N-03` / `MTH-G-04` / `MTH-O-06`）。
> **结构始终未变**：**168 节点 / 364 边 / 18 组 / 18 案例**，`validate_graph.py` errors=0、warnings=0、`kahn 168/168`（无环）。

---

## 2. 核验层终值（17 本已核验书）

| 项 | 值 |
|---|---|
| ledger 记录 | **719**（`direct 517 / partial 178 / inferred 24`）※ 轮前 698（503/171/24） |
| `node-claim-map` 的 claim 数 | **719**（与 ledger 逐条相等） |
| **claims 完整性差集** | **0** |
| 全层重复 `claim_id` | **0 组** |
| 覆盖节点 | **107**（= `_verification-overrides.json` 节点数）※ 轮前 103 |
| 缺口 | **159**（`missed_citation 71 / coverage_hole 51 / concept_missing 37`）※ 轮前 150（71/49/30） |
| 逐书记录数（**17 本**） | `saip 96 / team-topologies 81 / workbook 77 / sre-book 76 / evolutionary-arch 71 / ddia 58 / documenting-sa 37 / clean-architecture 35 / sweg 35 / refactoring 24 / release-it 24 / twelve-factor 24 / **ddd 21** / saip-ch4 21 / welc 18 / clean-code 14 / aposd 7` |
| `verified` | `true` **153** / `"cited"` **15**（GR-10 = 91.07%，**不变**：本轮新增覆盖的 4 节点原本已是 `verified=true`） |
| 单节点上限 | 超限 **0**；`DENSIFY_NODES` = **41**（未变） |
| 第二路复核 | **全部 `direct` 517 条均有 verdict（100%）**；`apply_secondpass --slug ddd` 报 `未复核 direct = 0`、`悬挂 verdict = 0`、`兜底判据 = 0` |
| 第二路总账 | `matched 517 / passed 466 / disputed 51`（轮前 `matched 496 / passed 450 / disputed 46`） |
| 第二路状态分布 | `passed 529 / disputed 60 / none 130` |

**本轮新书明细（BK-017 ddd，全书 446 页电子重排版）**：

```text
BK-017 ddd（1st/2003，e-text 446 页 / 17 章；无印刷页码）
  records 21（direct 14 / partial 7）；覆盖 12 节点，其中 4 个为图谱此前零记录节点：
    ESS-G-01 2 ｜ ESS-G-03 3 ｜ ESS-G-04 2 ｜ ESS-G-05 1 ｜ ESS-H-05 2 ｜ ESS-H-07 1
    ESS-H-09 2 ｜ ESS-L-03 2 ｜ ESS-N-03 1 ｜ MTH-G-04 2 ｜ MTH-H-03 2 ｜ MTH-O-06 1
  第二路复核 21 条全部有 verdict；passed 16 / 分歧 5（agree=false）
  保守终裁降级 4 条：VR-DDD-104（发布语言）/ VR-DDD-106（上下文映射）/ VR-DDD-108（一队一语言）/ VR-DDD-304（危机即机会）
  缺口 9 条（concept_missing 7 / coverage_hole 2）：
    GAP-DDD-101 / 102 / 103 / 201 / 202 / 203 / 302（concept_missing）
    GAP-DDD-301 / 303（coverage_hole）
```

**准入补录（ADR-009）**：

| 项 | 值 |
|---|---|
| 候选册条目 | **54 → 63**（`T1 1 / T2 49 / T3 13`） |
| 候选册覆盖缺口 | **55 → 64** |
| `reserved_ids_this_round` | **40 → 49**（新增 9 号） |
| 占号条目（id 非 null 且 status ∈ KEEP） | 41 → **50** |
| `released_ids_this_round` | 8（**未变**，本轮 0 个释放号被复用） |
| `reassignment_map` | 6（不变） |
| `amended_by` | `["ADR-006", "ADR-007", "ADR-008", "ADR-009"]` |
| 九条裁决 | 全部 **T2 / newly-allocated**：`GAP-DDD-101 ⇒ MTH-N-14`、`102 ⇒ MTH-G-14`、`103 ⇒ MTH-O-14`、`201 ⇒ MTH-O-15`、`202 ⇒ MTH-H-10`、`203 ⇒ MTH-H-11`、`301 ⇒ MTH-L-12`、`302 ⇒ MTH-G-15`、`303 ⇒ MTH-H-12` |
| 未登记 `proposed_node` | **0**（`writeback_gap_ids` 回写 9 条后复跑 0 变更） |

---

## 3. 门控全表（本轮实测）

| 门控 | 结果 |
|---|---|
| `gate_architecture.py --kind adr --input ADR-009.json` | **PASS 6/6**（首轮即 6/6；G-A3 19 个节点引用 / G-A4 24 引用零悬挂 / G-A5 无 TEC- 越位 / G-A6 5 条质量场景） |
| `extract_pdf_book.py --negative-test`（ddd 章图） | **3/3 如期按应有理由拒写**（页数不符 / 标题不在声明页 / `pdf_page` 非递增） |
| `validate_staging_shards.py`（本书） | 首轮 problems 2 类 16 条（C 分片 6 条记录缺 `review`；4 条 gap `target` 双空）⇒ 主 Agent 修正后 **problems 0 / WARN 0**（21 记录 / 21 主张 / 9 缺口 / 上限全通过） |
| `gate_verification.py --check all` | **PASS 9/9**；G-V5「可用书文本源」**含 `BK-017`**（缺失 无，命中 ≥20 字子串 = 0）；G-V1 记录 719 / gap 159 / 完整性缺口 0 / 重复 0；G-V8 覆盖 107/107 |
| `apply_secondpass.py --negative-test` | **5/5 如期通过**（新增 N5：兜底分支须置位 `basis_fallback` 并 WARN；有字段时不置位） |
| `merge_secondpass_worklists.py --negative-test` | **2/2 如期通过**（N1 无变化不写盘：字节与 mtime 均不变；N2 真变化必须写盘，守卫非恒跳过） |
| `backfill_candidate_register.py --negative-test` | **3/3**（旧单槽迁移不被 no-op 覆盖 / 两轮报告共存 / 索引重写幂等） |
| `replay_admission.py` | 一致率 **100.00%** + 负例 **4/4**；口径核对「裁决表条目 63 = T1 1 + T2 49 + T3 13」 |
| `replay_admission.py --scan-promotion` | 候选 **49** / 可晋升 **0** / 负例 **3/3** / **新提案行 = 0** |
| `negative_test_verification.py` | **11/11** |
| `negative_test_densify.py` | **11/11** |
| `derive_verification.py --check` | PASS（幂等，6 产物全 up-to-date） |
| `aggregate.py` 连跑两次 | 哈希一致（`690cfbdb…`） |
| `build.py --config mother` 连跑两次 | 产出总哈希一致（**`12be31ae…`**，轮前 `0346f9c8…`） |
| `validate_graph.py` | errors=0、warnings=0、kahn 168/168 |
| `gate_densify.py --check all` | **PASS 5/5** |
| `gate_coverage.py` | L6 PASS（manifest 100% / 四向 100% / GR-08 GR-09 PASS） |
| `gate_sources.py` | L7 PASS（悬挂 0 / 可溯源 100% / verified **91.07%**） |
| `gate_layout.py --check all` | L8 PASS（覆盖率 2140/2140 = 100%） |
| `gate_methodology.py --check all` | 四项全 PASS |
| `kb_gate.py`（structure,links；按 `quality-gate.md` 的排除口径） | PASS 2/2（structure 442 项 0 问题 / links 5437 项 0 问题） |
| `gate_visual.py --check all` | **L4 PASS**（212/272 = 77.94%，0 FAIL，60 skip —— 与上一份基线**完全一致**；⚠️ 须放宽沙箱才能实测，`workspace-write` 档下 32/32 全 FAIL） |
| `gate_render.py --timeout 25` | **L5 PASS**（7/7 案例，skipped=0） |
| `check_corpus_overlap.py --target evidence` | **0 命中**（134 对象 / **9 265 553** distinct 20-gram，轮前 8 592 676） |
| `writeback_gap_ids.py --check` | PASS（命中 64/64、需变更 0 —— 幂等） |
| `normalize_gap_ids.py --check` | PASS（重指派 0 / 非法 0 / 撞号 0） |

---

## 4. 公开层对账

```text
推送           = （推送后回填本节终值）
远端 HEAD      =
remote blobs   =
CI             =
Pages 回验     =
装配           = --apply --refresh-sanitize 后 --check 三类差异 0/0/0；P1–P5 预检全 OK（575 文件）
gate_disclosure= PASS（0 hit / 514 file）
```

> ⚠️ 本节在首次推送后按实测回填；回填本身是一次**纯 `00-plan/**` 文档提交**（不触发 CI，须手动 dispatch run 并回验 Pages）。

---

## 5. 本轮新增/修改的可执行物

| 文件 | 性质 |
|---|---|
| `16-checkpoint/apply_secondpass.py` | **改（缺陷收口）**：兜底分支（`review.first_pass_strength` 与 verdict 的 `first_pass_strength` 双缺）由**静默退回当前强度**改为**显式 WARN + `basis_fallback` 计数**，并在 `--all` 汇总打印「兜底判据=N」；新增负例探针 N5（缺字段须置位、有字段不得置位）；探针由 4 条增至 5 条 |
| `16-checkpoint/merge_secondpass_worklists.py` | **改（缺陷收口）**：先序列化再与磁盘比对，**逐字节相同则跳过写盘**（原实现重写全部既有 `secondpass-*.json`，mtime 全变、SHA 快照看起来像被改动）；抽出 `run()` 便于探针复用；新增 `--negative-test` 2 条探针（N1 无变化不写盘且 mtime/字节不变；N2 真变化必须写盘） |
| `16-checkpoint/gate_verification.py` | 改：`SLUG_RECORD_PREFIX` / `SLUG_TEXT` / `SOURCE_SLUG` 各增 `ddd` / `BK-017`（6 处登记中的 3 处） |
| `16-checkpoint/merge_verify_staging.py` | 改：`BOOKS` 增 `ddd` |
| `16-checkpoint/check_corpus_overlap.py` | 改：`CORPUS` 增 `ddd.txt` |
| `18-design/adr/ADR-009.json` | **新增**：9 条新缺口提案的准入裁决（`amends: ["ADR-004"]`，9 条全 T2 占号） |
| `18-design/adr/ADR-004.json` | 改：候选册 54→63、`reserved_ids_this_round` 40→49、`amended_by` 增 ADR-009 |
| `01-books/_verify/_meta/pdf-chapters-ddd.json` | **新增**：章图（17 章 `pdf_page`；**不登记 `printed_page`**，因电子重排版无印刷页码） |
| `01-books/_verify/_text/ddd.txt` + `_text/_slices/ddd/ch-{1..17}.txt` | **新增**：全书语料（852 442 字符 / 17 章头）与 17 个章切片 |
| `01-books/_parts/toc-ddd.json` | **新增**：TOC 分片（17 章 + 节表；`coverage.kind = full-text`） |
| `01-books/_verify/_meta/adr009-inputs.json` / `adr009-decisions.json` | **新增**：ADR-009 输入包与裁决草案 |
| `01-books/_verify/_meta/adr-register-backfill-adr009.json` / 索引 | **新增/改**：按修订件留存的补录报告 + 索引（index `reports[4]`、`latest=ADR-009`） |
| `01-books/_verify/_meta/verify-contract.md` | 改：§0 登记表增 `ddd` 行 + 电子重排版注（无印刷页码、锚点口径） |
| `00-plan/stage7p5-p2e-baseline.md` | **新增**：本基线 |
| `00-plan/NEXT-ROUND-PROMPT-7.md` | **新增**：下一轮接力件（`classes.never`，不公开） |
| `16-checkpoint/publish-manifest.json` | 改：`classes.never` 增 `00-plan/NEXT-ROUND-PROMPT-7.md` |

---

## 6. 两个工具缺陷的实测证据（本轮核心）

| 缺陷 | 修前实测 | 修后实测 |
|---|---|---|
| `apply_secondpass` 兜底分支静默 | 当 `review.first_pass_strength` 与 verdict 的 `first_pass_strength` 双缺时，退回「当前强度」为判据，**无任何信号**；旧缺陷（P2c/P2d）正是在这种静默下把降级留痕反转 | 修后该分支置位 `basis_fallback` 并向 stderr 打 WARN，`--all` 汇总打印「兜底判据=N」。实测全层 789 条 verdict 均带该字段 ⇒ `--all` 复跑 **兜底判据 = 0**、60/64 分片逐字节不变；N5 探针（缺字段=1 / 有字段=0）如期 |
| `merge_secondpass_worklists` 重写全部既有件 | 每次运行重写全部 `secondpass-*.json`（内容逐字节相同，但 mtime 全变，SHA 快照复验看起来像被改动） | 修后实测 `写盘 0 / 无变化跳过 6`，既有 36 个 `secondpass-*.json` 的 SHA-256 **逐一不变**；新增 `secondpass-ddd.json` 1 件（唯一写入）；N1/N2 两条探针如期 |

---

## 7. 回滚路径

- **备份**：`~/.dsh-backups/stage7p5-p2e-20261102/`（`_parts`、`_review`、`_meta`、`_text`、`10-dag-data`、`18-design`、`16-checkpoint`、`00-plan`）。
- **回退顺序**：`_parts/{ledger,claims,toc,gaps}-ddd.json` 删除 → `_meta/pdf-chapters-ddd.json`、`_text/ddd.txt`、`_text/_slices/ddd/` 删除 → 6 处登记回退 → `18-design/adr/ADR-009.json` 删除 + ADR-004 复原候选册/`reserved_ids_this_round`/`amended_by`（或以备份 `18-design/adr/ADR-004.json` 覆盖）→ `derive_verification` → `aggregate` → `build` → 公开层重装配重推。
- **两个工具缺陷的代码回滚**：`apply_secondpass.py` / `merge_secondpass_worklists.py` 从 `16-checkpoint/` 备份还原；还原后 `apply_secondpass --all` 会再次**静默**走兜底分支（但数据值不变），`merge_secondpass_worklists` 会恢复「重写全部既有件」的旧行为。
- **`01-books/` 无 git 历史**（本地仓与 `_publish` 双重 ignore）⇒ 只能靠上述备份回滚。
- 本地归档仓：以 `git log --oneline -3` 为准。

---

## 8. 待裁决 / 未完成

1. **`BK-016`（POSA Vol.1）仍未采集**（不变）：canonical `verified=false` / `confidence=low`，需先补采集（合法渠道）。
2. **T2 → T1 晋升**：本轮候选册 T2 由 40 增至 **49**（9 条新 T2 均为单源）；`--scan-promotion` 仍为「可晋升 0」。晋升属结构变更，须另立 ADR。
3. **域外贴限证据**：`MTH-J-07` / `MTH-N-05` / `TEC-J-04` 各 8 条，维持 ADR-005 边界（用户默认：维持）。
4. **公开仓历史 blob（旧）**：`NEXT-ROUND-PROMPT-3.md` 与上一轮泄漏的 OCR 书页原文仍在公开仓 git 历史中；彻底清除需 force-push（**未做**，用户默认不处理）。
5. **9 条新 T2 的落点风险**：`GAP-DDD-103` 与 `GAP-DDD-201` 同挂 `MTH-O-06`；`GAP-DDD-202` 落点 `ESS-H-09` 语义距离最远（若复核认为应改挂 `ESS-H-01` / `ESS-H-08`，只需改 `target.existing_node_id`，档位与号不受影响）。
6. **`MTH-G-04` 已达单节点上限**（6 + 2 = 8 = `CLAIM_CAP`）：后续任何书再想给该节点补记录，须先走 ADR-003 的增密档位申请。
7. **`ESS-N-03` 与 `MTH-O-06` 亦已达上限**（各 7 + 1 = 8）：同上，后续补记录须先提档或换落点。
8. **BK-017 的 `verified` 标记**：canonical 中 `BK-017` 仍为 `verified= cited` / `confidence=medium`（不是本轮遗漏——canonical 的 `verified` 字段与核验层「已核验书」是两套口径，本轮未改 canonical）。
