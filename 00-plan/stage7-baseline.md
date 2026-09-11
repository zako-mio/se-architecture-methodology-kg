# 阶段7 基线冻结记录

> 生成时间：2026-09-11　生成者：阶段7 门控执行员（子Agent）
> 用途：为「参考书吸收与知识库融合（阶段1 核验升级）」提供**回滚锚点**与**冻结证据**。
> 本文件是阶段7 的事实基线：任何后续声明与本文冲突时，以本文的实测值为准。
> 前置事实基线：`00-plan/stage6-baseline.md`（阶段6 冻结值）。
> 口径：本文件全部数值为**门控脚本实跑输出**，逐条记录，非推演。

---

## 1. 指纹变更（SHA-256）

| 文件 | 阶段6 冻结值 | 阶段7 实测值 | 变更原因 |
|---|---|---|---|
| `10-dag-data/methodology-dag.json` | `58a7e3c397dc772344d71d8f98dd107ad5ac54a607bcea956a6a8994a258a390` | `9ae4cc01f7b183f9a621997896a9033af6d9ca9ed38fee462077d8604496eba1` | 一次性变更：①`_base.json` 冻结日期常量由 `2026-09-10` → `2026-09-11`（`aggregate.py` 日期坑修复，见 §5）②应用 `_verification-overrides.json` 后节点 `review_date` 更新 |
| `10-dag-data/node-content.json` | `077c89d5c92f1aeaf5926523b0028fa612e33ac760f1ef987c655242a2a00184` | `38d5f98b9eb985c4bb40a849f9420dc6819c7048dac6c99cbc0c3d53be7b2532` | 随主图再生（`generated` 常量 + 覆盖字段） |
| `10-dag-data/_base.json` | `26e624726f28d6e4a0cd6ed5a6783c8d7b0965aad3643298d9326a3fd26dee3a` | `8d100f2eaf77aeced15c6010dafd120c0d1db9c150f6aa280e35c11d84176e88` | 仅 `meta.generated` / `meta.updated` 两行（`2026-09-10`→`2026-09-11`），承载冻结常量 |
| `03-knowledge-map/canonical-sources.json` | `e7cd0eb7445595c2b4a653bf58760e071d801ad47842a2bc3f8c4d1187222c33` | `e7cd0eb7445595c2b4a653bf58760e071d801ad47842a2bc3f8c4d1187222c33`（**未变**） | 信源主表本阶段未改 |

实测命令与输出：

```
$ git show f4fc157:10-dag-data/methodology-dag.json | sha256sum
58a7e3c397dc772344d71d8f98dd107ad5ac54a607bcea956a6a8994a258a390  -
$ sha256sum 10-dag-data/methodology-dag.json
9ae4cc01f7b183f9a621997896a9033af6d9ca9ed38fee462077d8604496eba1  .../methodology-dag.json
```

> **验收硬约束**：新指纹 `9ae4cc01…` 冻结；CI 漂移检测以本值为预期。`canonical-sources.json` 阶段6→7 指纹不变。

---

## 2. 数据规模（实测）

| 指标 | 阶段7 实测值 |
|---|---|
| 节点 / 边 | **167 / 360**，`dag_acyclic=true`（Kahn 167/167），`validate_graph` errors=0 |
| 组 / 横切主题 / 案例 | **18 / 3 / 18** |
| 层分布 | essence 51 + methodology 67 + technology 31 + case（`layer=null`）18 |
| `verified` 分布 | 布尔 `true` **149** / 字符串 `"cited"` **18**（与阶段6 完全一致，**无翻转**） |
| `confidence` 分布 | `high` **151** / `medium` **16** |
| `review_date` 分布 | `2026-09-11` **35**（被书证覆盖节点）/ `2026-09-10` **132**（未覆盖节点保持原值） |
| `verified=true` 占比（GR-10） | **149/167 = 89.22%**（阈值 ≥80%，PASS） |
| 可溯源率（`verified ∈ {true,"cited"}`） | **167/167 = 100.00%**（阈值 ≥95%，PASS） |

> `verified` 分布维持 `149/18` 即「增量式回写 + 保守终裁」的直接证据：35 个被覆盖节点中，34 个原值本就为 `true`、1 个（`CAS-X-02`）原值为 `"cited"`，终裁后**无任何节点因书证翻转为 `true`**（对比基线：`changed_verified=0`，`changed_confidence=0`）。

---

## 3. 阶段7 新增输入 / 产物的 SHA-256（逐文件实测）

### 3.1 私有核验层（`01-books/_verify/`）

| 文件 | SHA-256 |
|---|---|
| `_meta/verify-contract.md` | `245e8c17ccef3de573ce89fe90e081f8b69ed183bb82d48ca1bb18e324cbfc2b` |
| `_parts/ledger-ddia.json` | `2f73af0c5313573a3328fe8a59a8c662dd4f4b96afa17500bd2c236bca4e4e3c` |
| `_parts/ledger-clean-architecture.json` | `d864177bbe46ea7aff9c3d08b2c3d5a940e13bc4a816f737ff7a41b7a4cb5912` |
| `_parts/ledger-saip.json` | `e896bc5e75373451fed42e3c20897c0a0764f693918404bfbe0327990143aee5` |
| `verification-ledger.json` | `8ca515f83ee4c985da0668947302f94b4a29c26d562de95e54e7ee3e3dae79f8` |
| `node-claim-map.json` | `ea2dad4a501089dc6805f388dab1c87d6c12df4f929affd517938f7c50d612ef` |
| `book-toc-index.json` | `f5b68ed0b2399fb639e7546d44a64811fa0a73d96452bd6048400aa7fd343864` |
| `reverse-gaps.json` | `c61071fee17214be407d423a947969cc5bac1ae268c498e74eaca28ec17c8514` |
| `_review/secondpass-cleanarch-ddia.json` | `10f71cd8d39c7839fd117fa5c6aeee4e403641a3bf2090f73e15c6a5f333ec36` |
| `_review/secondpass-saip.json` | `ace349a7c930ae5aeff1afffd7803037435a86d1ae0b743e58d55ee7c2fbaf3f` |

> 私有层三重隔离：本地仓 `.gitignore:13`（`01-books/`）覆盖；公开仓 `_publish/.gitignore` 显式列 `01-books/_verify/`；装配层 `publish-manifest.json` `private` 类。实测 `git check-ignore -v 01-books/_verify/verification-ledger.json` → `.gitignore:13:01-books/`。

### 3.2 派生层与公开安全投影（`10-dag-data/`）

| 文件 | SHA-256 |
|---|---|
| `_verification-baseline.json` | `bfc6f6b5df531ce3d29491872d11cf7e011913fb1e3ad5d18d4e7747a0ff523d` |
| `_verification-overrides.json` | `3759f2202ad4a6a120d206e6fd72dad6f3d33017805674f87252f89cc4ac86df` |
| `book-verification.json` | `4c4d4a8ea96cc445189cb0f02c90ac883ddb7b1b0fb8f626b962e403e7942633` |

### 3.3 生成链与门控脚本（`16-checkpoint/`）

| 文件 | SHA-256 |
|---|---|
| `derive_verification.py` | `dce82e270feed6ba44f6e1c614653ba263e523a11b3fed87bdd5ca22c4a23f58` |
| `gate_verification.py` | `b13c4b5d8ba38f9d2d21f2f332fde75f94d792a68cc45367a85529be34cc3677` |

---

## 4. 核验规模（实测）

### 4.1 核验记录主表 `verification-ledger.json`

| 指标 | 实测值 |
|---|---|
| 记录总数 | **144** |
| `evidence_strength` 分布 | `direct` **78** / `partial` **59** / `inferred` **7** / `contradicted` **0** |
| `direction` 分布 | `forward` **120** / `reverse` **24** |
| `source_id` 分布 | `BK-009` **96** / `BK-007` **30** / `BK-023` **18** |
| `second_pass` 分布 | `passed` **78** / `disputed` **18** / `none` **48** |
| `review_date` | 全部记录 = `2026-09-11` |
| 被覆盖节点数 | **35** |
| 升级节点数（G-V4 口径：≥1 `direct` 且 0 `contradicted`） | **26** |
| `contradicted` 节点数 | **0** |

### 4.2 反向缺口 `reverse-gaps.json`（同时是阶段3 接口）

| 指标 | 实测值 |
|---|---|
| 缺口总数 | **28** |
| `kind` 三类分布 | `coverage_hole` **10** / `concept_missing` **10** / `missed_citation` **8** |
| `book_source_id` 分布 | `BK-023` **15** / `BK-009` **7** / `BK-007` **6** |
| `evidence_strength` 分布 | `direct` **21** / `partial` **7** |

### 4.3 派生覆盖 `_verification-overrides.json`

| 指标 | 实测值 |
|---|---|
| 覆盖节点数 | **35**（与 ledger 被覆盖节点集合一致，G-V8 对账 0 遗漏 / 0 越界） |
| `verified` 值分布 | `true` **34** / `"cited"` **1**（`CAS-X-02`） |
| `confidence` 值分布 | `high` **35** |
| `errata` 条数 | **0**（无 `contradicted` 记录 → 无勘误项） |
| 相对 `_verification-baseline.json` 的实际变更 | `changed_verified = 0`，`changed_confidence = 0` |

### 4.4 公开安全投影 `book-verification.json`

`by_node` = **35** 节点；`gaps` = **28**。仅含章节级引用元数据（信源 id + 章/节编号与标题 + 强度 + 方向 + 复核状态 + 日期），不含 claim 文本 / 页码 / 摘句。

### 4.5 正向目标覆盖（计划 §4.9 三件套）

- 章节锚：18 个正向目标节点全部产出核验记录（含未命中者以 `partial`/`inferred` 记录，不驱动升级）。
- 勘误：`contradicted = 0` → `errata` 空集（如实报告，非缺陷）。
- 缺口：DDIA（BK-023）15 + SAiP（BK-009）7 + CleanArch（BK-007）6 = 28，三类 gap 均有样本。

---

## 5. 纠偏记录（对前序实现的实测修正）

| # | 原问题 | 实测真相 / 修正 | 处置证据 |
|---|---|---|---|
| ① | `aggregate.py` 运行时钟缺陷：`meta["updated"] = datetime.date.today().isoformat()` 使**跨日重聚合即改 SHA**（阶段6 文件 `meta.updated=2026-09-10`，次日重聚合会变 `2026-09-11`） | 改为从 `_base.json` 的**冻结常量**读取日期；`aggregate.py` 全文已无 `datetime.date.today()` / `date.today` | `grep -n "date" aggregate.py` 无 today；`_base.json` diff 仅 `generated`/`updated` 两行 `2026-09-10`→`2026-09-11` |
| ② | 派生器**循环依赖**：从「派生后 dag」回读原 `verified/confidence`，重跑结果依赖上一次产物（非纯函数） | 引入 `_verification-baseline.json`（源 = `git HEAD:10-dag-data/methodology-dag.json`，`source_sha256=58a7e3c3…`）**冻结基线**；`derive_verification.py` 以 `(baseline, ledger)` 为输入，派生成为**纯函数**；基线缺失才回退读当前 dag 并打 `WARN` | `derive_verification.py:37/231/248/315`；`_verification-baseline.json` SHA `bfc6f6b5…` |
| ③ | 第一路核验把 18 条「仅概念相关」判为 `direct`（FP 风险，会抬高公开 `verified`） | 第二路独立复核（`w3-v1-saip-secondpass` / `w3-v2-ca-ddia-secondpass`）抓出 **18 条 direct 假阳性**，主Agent 保守终裁**降级为 `partial`** | 18 条 `second_pass=disputed` 现全为 `partial`（BK-007 5 / BK-023 4 / BK-009 9）；`changed_verified=0` → `verified` 分布维持 **149/18** |

> 结论：本阶段真实产出是「章节锚 + 反向缺口 + 复核记录」，**不是 `verified` 翻转**；`verified=true` 分布与阶段6 逐字节等价（149/18），公开指标无注水。

---

## 6. 门控实测表（L1–L8 + 方法论四项 + G-V1..G-V8）

> 执行环境：本地归档仓（`MROOT`），Python 标准库 + Pillow 12.3.0 + numpy 2.5.2 + agent-browser（Chromium）**均可用**。

| 层 | 实测值（脚本原始输出摘要） | 结论 | SKIPPED 原因 |
|---|---|---|---|
| **L1** 分片自验证 | 23 分片（22 `_parts/*.json` + `_base.json`）**errors=0**；分片模式跨分片端点仅计 warning（预期） | **PASS** | — |
| **L2** 全图审计 | `nodes=167 edges=360 kahn_visited=167/167`，`errors=0 warnings=0` | **PASS** | — |
| **L3** 结构 + 断链（母库口径） | structure 检查项 **427** / 问题 **0**；links 检查项 **5189** / 问题 **0** | **PASS** | — |
| **L4** 视觉 | **272** 项 / 212 PASS / **0 FAIL / 0 WARN / 60 SKIP**；用时 26.6s | **PASS** | 60 SKIP = 该页**无对应元素**的判据（如 glossary 页无 svg / 无 `.defcard`），非能力缺失 |
| **L5** 渲染（headless Chromium） | **7 用例全 PASS**；`skipped=0`；JS 错误 0；悬空端点 0 | **PASS** | — |
| **L6** 覆盖度 | manifest **365/365 = 100.00%**（8 项）；四向 **100.00%**；GR-08 PASS；GR-09 **11/31 = 35.48% ≥30%** | **PASS** | — |
| **L7** 信源 | canonical 引用 **1446**（node 605 / errata 222 / edge 619），悬挂 **0**；可溯源 **100.00%**；`verified=true` **89.22%**；disputed 漏标 **0** | **PASS** | — |
| **L8** 版式 | 综合覆盖率 **2128/2128 = 100.00%**，问题 **0**（节点页 167 / HTML 生成物 195 / 文档 368 / glossary 锚点 152） | **PASS** | — |
| **方法论①** layer-boundary | 边 360；越级 0；内层引用外层 0；违规 0 | **PASS** | — |
| **方法论②** glossary | disputed 术语 4（微服务/可观测性/可扩展性/可演化性），引用命中 5 均已标 errata；漏标 0 | **PASS** | — |
| **方法论③** principle-counterexample | O-PC 覆盖 **36/36**，悬空 0，反例缺失 0 | **PASS** | — |
| **方法论④** tradeoff-11 | O-TD **11/11** 全部解析到对应 MTH 节点 | **PASS** | — |
| **G-V1** | 核验层 JSON 合法 + 必填齐全：记录 **144** / gap **28**；问题 **0** | **PASS** | — |
| **G-V2** | `evidence_strength` / `direction` / `gap.kind` 封闭枚举：非枚举命中 **0** | **PASS** | — |
| **G-V3** | 每条记录 `anchor.chapter` 非空：违规 **0** | **PASS** | — |
| **G-V4** | 无锚点升级 = **0**（升级节点 **26**，均具 `anchor`+`direction`） | **PASS** | — |
| **G-V5** | claim 改写检查：可用书文本源 BK-007/BK-009/BK-023；缺失 **无**；命中 ≥20 字连续子串 **0** | **PASS** | — |
| **G-V6** | 编码 UTF-8 无 BOM / 无 U+FFFD：检查 **17** 文件；问题 **0** | **PASS** | — |
| **G-V7** | 幂等：`derive_verification.py --check` 退出码 **0**；6 产物均 `[IDEMPOTENT]` + `[up-to-date]` | **PASS** | — |
| **G-V8** | 对账：应覆盖 **35** / 实际覆盖 **35**；遗漏 **0**；越界 **0** | **PASS** | — |

**L4/L5 说明**：本轮依赖齐备，**无 SKIPPED-因缺依赖**，亦**未出现** `agent-browser` 白页假 FAIL，故未触发「原样重跑确认」流程（无 FAIL 可确认）。

**门控汇总：L1–L8 全 PASS；方法论四项 4/4 PASS；G-V1..G-V8 8/8 PASS。**

---

## 7. 回滚锚点

- **阶段6 完成快照**：commit `f4fc157`（`stage6: content-layout redesign …`）——该快照的 `10-dag-data/methodology-dag.json` 实测 SHA-256 = `58a7e3c3…`（阶段5 冻结基线）。
- **阶段7 起点**：工作树 HEAD = `ab1c154`（阶段6 后遗留处理轮收尾；stage7 改动全部为**未提交**的工作区变更）。
- **回滚命令**（恢复到阶段6 数据/生成物 + 移除阶段7 派生件；**私有核验层不回滚**）：

  ```bash
  MROOT="~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"
  # 1) 数据与生成物回退到阶段6 快照（含版本与公开装载状态）
  git -C "$MROOT" checkout f4fc157 -- 10-dag-data 11-node-pages 12-groups 13-interactive \
      14-views 15-md index.html 16-checkpoint/deliverables.json 16-checkpoint/publish-manifest.json \
      00-plan/stage6-content-ia-spec.md
  # 2) 移除阶段7 新增、checkout 不会删除的派生件
  rm -f "$MROOT/10-dag-data/_verification-overrides.json" \
        "$MROOT/10-dag-data/book-verification.json" \
        "$MROOT/10-dag-data/_verification-baseline.json"
  # 3) 私有核验层 01-books/_verify/ 原样保留（避免重复劳动）
  git -C "$MROOT" status --short
  ```

- **回滚触发条件**（摘自 `stage7-book-absorption-plan.md §4.10`）：
  1. 派生无法在无时间戳下保持幂等（G-V7 FAIL 且不可修复）；
  2. 章节锚公开被判越版权红线（`gate_disclosure.py` FAIL 且不可脱敏）；
  3. `direct` 抽检 FP >10% 且两轮校准无效。
- **回滚后校验**：`sha256sum 10-dag-data/methodology-dag.json` 应回到 `58a7e3c3…`；`validate_graph.py --graph` errors=0；`gate_verification.py` 因 `_verification-overrides.json` 缺失应显式 SKIP（不得伪装 PASS）。

---

## 8. 验收状态小结

| 判据 | 实测 | 结论 |
|---|---|---|
| 结构：UTF-8 无 BOM / 无 U+FFFD / JSON 合法 / 断链 0 | L3 links 5189/0；L6 全 JSON 合法 | 达标 |
| 数据：`validate_graph` errors=0 / `dag_acyclic=true` / 零悬挂 / 变更集可对账 | L2 / L7 / G-V8 | 达标 |
| 核验层：G-V1–G-V8 PASS / 无锚点升级 0 / 升级可回溯 | 8/8 PASS | 达标 |
| 三件套：章节锚 / 勘误 / 缺口 | 35 节点记录；errata 0；gap 28 | 达标（勘误空集如实报告） |
| 门控：L1–L8 + 方法论四项 + G-V | L1–L8 全 PASS；方法论 4/4；G-V 8/8 | 达标 |
| 指纹：`methodology-dag.json` 一次性变更并重设基线 | `9ae4cc01…` | 已冻结 |
