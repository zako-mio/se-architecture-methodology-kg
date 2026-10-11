# 阶段7 · 轨B 基线冻结记录（高价值书核验后）

> 生成时间：2026-10-11　生成者：主Agent（阶段7 轨B 执行轮）
> 用途：为「轨B 高价值书核验」提供**回滚锚点**与**冻结证据**。
> 本文件是轨B 的事实基线：任何后续声明与本文冲突时，以本文的实测值为准。
> 前置基线：`00-plan/stage7-baseline.md`（阶段1）/ `00-plan/stage7p2-baseline.md`（阶段2）。
> 口径：本文件全部数值为**门控脚本与命令实跑输出**，逐条记录，非推演。

---

## 1. 指纹变更（SHA-256）

| 文件 | 阶段2 冻结值 | 轨B 实测值 | 变更原因 |
|---|---|---|---|
| `10-dag-data/methodology-dag.json` | `865e6a3d649281930b80107e8348f420ed51eb650be75f17e8a96fedbef4e915` | **`b11eae6c0793e08e13f48184c92d42e98150ba6c738cba1ffe6c4bfd6c197789`** | **仅 23 个节点的 `review_date`**（2026-09-10 → 2026-10-11）；`verified` / `confidence` **零翻转** |
| `10-dag-data/node-content.json` | `93813c864ab8be2e3bd46ab0fbdc39645ae83800f2b1c8e36c5a4371cddb299c` | `93813c864ab8be2e3bd46ab0fbdc39645ae83800f2b1c8e36c5a4371cddb299c`（**未变**） | 本轮**未改任何节点正文** |
| `10-dag-data/_base.json` | `470ca8cec54bf9b003790d8cf45d929f440f66c8574826ebd522f974d31e23dc` | `470ca8cec54bf9b003790d8cf45d929f440f66c8574826ebd522f974d31e23dc`（**未变**） | 本轮**未动骨架** |
| `01-books/_verify/verification-ledger.json` | `6e8597e2af9190fcae69976d92507fad50d4c9e5f52570289d69e499155450b6` | **`717073efb1fe53b2c297ff14ad27158573be27841fb18aed851a127280ffec46`** | 新增 152 条记录（`VR-TT-*` 81 + `VR-EA-*` 71），其中 18 条经第二路复核降级 |
| `01-books/_verify/node-claim-map.json` | `8aef4fa793d840a944af575c48271e164a5d7a0390b76e61dda1c43c2133971f` | **`b2e5f4b2434ae2989cafeaf3dc175403e30190a061ac1977cee4c6e0fe605265`** | 23 个新覆盖节点新建主张键（152 条） |
| `01-books/_verify/reverse-gaps.json` | `c61071fee17214be407d423a947969cc5bac1ae268c498e74eaca28ec17c8514` | **`ab6aaedfe01935c81f535095ad9b25f77677de49d521da1e2020e53fcfc9b2ea`** | 新增 32 条缺口（BK-030 16 + BK-011 16） |
| `10-dag-data/_verification-overrides.json` | `695e03c157083f86cd1f179b05027772d7ce1c3ea80a1d20bcf44d696bf25c89` | **`b90906162993649327bc71a744e690c7c15ebfc2a55d518d2a09b0b564ab5656`** | 覆盖集 35 → **57 节点** |
| `10-dag-data/book-verification.json` | `cd605174400a17fe611954ddcf4a149cd59b33feffa08cc34269b03879b1030b` | **`eee5a83b54405d756cbc456687bcbb6dfa57409eb0766af13409a1e9873c25fc`** | 公开安全投影随核验层再生 |
| `01-books/_verify/book-toc-index.json`（本轮补入基线表） | —— | `8dd456ed769e40fe16a85705f7be54593347295ded84a185d5024d282cfb590b` | 新增 2 本书 TOC（BK-030 / BK-011） |

实测命令与输出：

```
$ sha256sum 10-dag-data/methodology-dag.json
b11eae6c0793e08e13f48184c92d42e98150ba6c738cba1ffe6c4bfd6c197789  ...
$ python3 16-checkpoint/aggregate.py   # 连跑两次
H1=b11eae6c…  H2=b11eae6c…   → AGGREGATE IDEMPOTENT: PASS
$ python3 16-checkpoint/build.py --config mother --quiet   # 连跑两次
62 变更文件数不变          → BUILD IDEMPOTENT: PASS
```

> **指纹变更性质**：`git diff -U0` 字段级统计显示变更**只有** 23 行 `"review_date"`（改前 2026-09-10 / 改后 2026-10-11），
> **无任何 `verified` / `confidence` / 正文改动**。即轨B 是**纯证据层扩展**，未改动任何既有结论。

---

## 2. 数据规模（实测）

| 指标 | 轨B 实测值 |
|---|---|
| 节点 / 边 | **167 / 360**（**未变**），`dag_acyclic=true`（Kahn 167/167） |
| 组 / 横切主题 / 案例 | **18 / 3 / 18** |
| 层分布 | essence 51 + methodology 67 + technology 31 + case（`layer=null`）18 |
| `verified` 分布 | 布尔 `true` **149** / 字符串 `"cited"` **18**（**零翻转**，与阶段2 完全一致） |
| `confidence` 分布 | `high` **151** / `medium` **16**（**零翻转**） |
| `verified=true` 占比（GR-10） | **149/167 = 89.22%**（与阶段2 持平，PASS） |
| 可溯源率 | **167/167 = 100.00%**（PASS） |

---

## 3. 核验层规模（实测）

| 指标 | 阶段2 | **轨B** | 说明 |
|---|---|---|---|
| 记录总数 | 189 | **341** | +152 条（`VR-TT-001..144` / `VR-EA-001..144`） |
| `evidence_strength` | direct 117 / partial 63 / inferred 9 | **direct 199 / partial 121 / inferred 21** | 含 18 条第二路复核降级（direct→partial） |
| `direction` | forward 165 / reverse 24 | forward 317 / reverse 24 | 新增全为 forward |
| 覆盖节点数 | 35 | **57** | +23（TT 12 + EA 11，与既有覆盖集重叠 1） |
| 升级节点数（≥1 direct 且 0 contradicted） | 26 | **44** | 第二路复核后 `MTH-G-04` 失去全部 direct，未升级 |
| `contradicted` | 0 | **0** | 本轮无反驳记录，故无 errata |
| 已核验书（slug） | 3 | **5** | +`team-topologies`(BK-030) +`evolutionary-arch`(BK-011) |

**本轮记录号段**：`VR-TT-001..144`（TT）、`VR-EA-001..144`（EA）。

**缺口清单**：28 → **60** 条（`coverage_hole 27 / missed_citation 19 / concept_missing 14`；
`direct 53 / partial 7`）。提案新节点 **29 个**（按 id 字符串归并口径）。

---

## 4. 第二路独立复核（本轮新增闸门，**100% 覆盖 direct 记录**）

| 项 | TT | EA | 合计 |
|---|---|---|---|
| 复核范围（first-pass `direct`） | 63 | 37 | **100** |
| 维持 `direct`（agree） | 51 | 31 | **82** |
| **降为 `partial`（disagree，保守终裁降级）** | 12 | 6 | **18（18%）** |
| `anchor_locatable=false` | 3 | 0 | 3 |

> **判据可信度证据**：独立复核抓出 **18% 的过度断言**，与路线图 §7 记录的历史 FP 率（18.75%）同量级。
> 降级为**只降不升**的保守终裁（`apply_secondpass.py`），并留痕于 `evidence_note`。
> 3 条锚点错位中 2 条已回修（`VR-TT-011` ch8→7、`VR-EA-117` 2.13→2.12），1 条（`VR-TT-035` 内容在「结论」章）留痕待回修。

---

## 5. 门控基线（轨B 实测，**全部主Agent 亲跑**）

| 层 | 实测值 | 结论 |
|---|---|---|
| **G-V1..G-V9** | **PASS=9 FAIL=0 WARN=0 SKIP=0**（341 记录 / 60 gap / 57 覆盖 / 44 升级） | **PASS** |
| **G-V5**（版权） | 可用书文本源 BK-007/009/011/023/030；**≥20 字子串命中 0** | **PASS** |
| **G-D1..G-D5** | **PASS=5 FAIL=0 WARN=0 SKIP=0**（变更集 26，越界 0） | **PASS** |
| **L2** 全图审计 | `nodes=167 edges=360 kahn=167/167 errors=0 warnings=0` | **PASS** |
| **L3** 结构 + 断链 | structure **438** / 问题 **0**；links **5263** / 问题 **0** | **PASS** |
| **L6** 覆盖度 | manifest **100.00%** / 四向 **100.00%** / GR-08 PASS / GR-09 PASS | **PASS** |
| **L7** 信源 | 悬挂 **0**；可溯源 **100.00%**；`verified=true` **89.22%** | **PASS** |
| **L8** 版式 | 综合覆盖率 **2128/2128 = 100.00%**，问题 **0** | **PASS** |
| **方法论专项** | 层边界 / 术语一致 / 原则↔反例 / 11 维权衡 | **4/4 PASS** |
| **版权红线**（证据素材） | `check_corpus_overlap.py --target evidence`：134 对象 / 语料 2 810 114 distinct 20-gram / **命中 0** | **PASS** |
| **判据可信度** | `negative_test_densify.py` **11/11 如期**；`negative_test_verification.py` **6/6 如期** | **PASS** |
| **幂等** | `derive_verification.py --check` / `aggregate.py` / `build.py` 连跑 diff 为空 | **PASS** |
| **ADR-004** | `gate_architecture.py --kind adr` **6/6 PASS** | **PASS** |

### 5.1 已知遗留（**不伪装 PASS**）

- **L4（`gate_visual`）= SKIP、L5（`gate_render`）= FAIL(env)**：本机缺 `agent-browser` CLI
  （与 `stage7p2-baseline.md` §4.2 记录的既有环境缺口同源）。**未验证**，不得计入 PASS。
- **阶段1 遗留重复 claim_id**：`ESS-O-02#principle#1`（`VR-CA-030` / `VR-DDIA-009`），G-V9 报 WARN/阶段1遗留。

---

## 6. 公开层（实测）

- 公开仓 `zako-mio/se-architecture-methodology-kg`（branch `main`）
- 推送后远端 HEAD = **`af2c75672a813ca3dff1b629d7ad24df30bd2e2d`**（Git Data API 推送，parent `560236a7`）
- 远端 **blob 数 557 == 本地 `git ls-files` 557**（对账一致）
- `PUBLISH-STATE.json` `file_count = 551`（期望集；另 6 个为 preserve 专有件）
- `assemble_publish.py --check` = **0/0/0**，P1–P5 全 OK
- `gate_disclosure.py` = **PASS（0 hit / 506 files）**
- CI run **`38139423384`** = **success**（29s）
- Pages 复验（9 类端点）：首页 / 节点页（`ESS-N-01` `MTH-G-04`）/ 06 视图 / MD 镜像 / 组页 /
  `report-phase7p2.html` / `00-plan/stage7p3-trackB-gap-handoff.md` **全部 HTTP 200**

### 6.1 本轮修的**前置缺陷**（非本轮引入）

1. `report-phase7p2.md` / `.html` 已提交但未在任何类声明 → `assemble_publish --check` 的 P1 **FAIL**（未声明 2 项）。
   → 补入 `classes.sanitize` + 扩展 `audit_publish.py` 的 `SCAN_ROOT_FILES`。
2. `00-plan/stage2-search-plan.md` / `contract.md` 的公开副本含**内网定向代理地址**（上一轮遗留）。
   → `audit_publish.py` 新增 `INFRA_RE` 统一脱敏为 `<private-host>`（机械派生，与 mask 链同源）。
3. `00-plan/NEXT-ROUND-PROMPT.md` 属公开目录却为**窗口间内部交接 Prompt** → 归入 `classes.never`。

---

## 7. 回滚与基线重置

- **回滚路径**：删除 `01-books/_verify/_parts/{ledger,claims,gaps}-{team-topologies,evolutionary-arch}.json`
  与 `toc-*` 两个新 slug 分片 → 重跑 `derive_verification.py` + `aggregate.py` + `build.py`
  → 指纹回到 `865e6a3d…`。
  `16-checkpoint/` 的 5 个新脚本、`_text/` 两本书抽文本、`_review/staging/` 与 `_review/secondpass-*.json`
  **原样保留**（避免重复劳动）。
- **回滚触发**：① G-V5 版权红线命中 >0；② 第二路复核降级率 >30%（判据或首路系统性失准）；
  ③ L6/L7/L8 无法回到 100%。
- **本基线已冻结**：新指纹 `b11eae6c…`；CI 漂移检测以本值为预期。

---

## 8. 本轮新增脚本与产物

| 脚本（`16-checkpoint/`，随公开层发布） | 用途 |
|---|---|
| `extract_book_text.py` | EPUB → 纯文本（私有核验语料），确定性、无时钟 |
| `build_book_toc.py` | EPUB NCX → `_parts/toc-<slug>.json` |
| `merge_verify_staging.py` | 核验暂存分片 → `_parts` SSOT 分片（唯一写入方=主Agent，fail-closed） |
| `apply_secondpass.py` | 第二路复核裁决回写（**只降不升**的保守终裁） |
| `negative_test_verification.py` | 核验层门控负例自检（**6/6 如期**，含「新书语料真的接进 G-V5」反例） |
| `push_publish.py`（加固） | blobs 上传对**瞬时 EOF** 退避重试（认证类错误不重试） |

| 私有产物 | 说明 |
|---|---|
| `01-books/_verify/_text/{team-topologies,evolutionary-arch}.txt` | 两本书 EPUB 抽文本（470 365 / 542 901 字符） |
| `01-books/_verify/_parts/{ledger,claims,toc,gaps}-{team-topologies,evolutionary-arch}.json` | 2 个新 slug × 4 件 SSOT 分片 |
| `01-books/_verify/_review/staging/*` | 6 个核验暂存分片（可追溯分工） |
| `01-books/_verify/_review/secondpass-{team-topologies,evolutionary-arch}.json` | 100 条独立复核裁决 |
| `18-design/adr/ADR-004.{json,md}` + `ADR-004-inputs.md` | 阶段3 前置 ADR（门控级，6/6 PASS） |
| `00-plan/stage7p3-trackB-gap-handoff.md` | 缺口与阶段3 准入交接件 |
