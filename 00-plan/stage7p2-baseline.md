# 阶段7 · 阶段2 基线冻结记录（内容增密后）

> 生成时间：2026-10-11　生成者：主Agent（阶段2 执行轮）
> 用途：为「参考书吸收 · 阶段2 内容增密」提供**回滚锚点**与**冻结证据**。
> 本文件是阶段2 的事实基线：任何后续声明与本文冲突时，以本文的实测值为准。
> 前置基线：`00-plan/stage7-baseline.md`（阶段1 冻结值）。
> 口径：本文件全部数值为**门控脚本实跑输出**，逐条记录，非推演。

---

## 1. 指纹变更（SHA-256）

| 文件 | 阶段1 冻结值 | 阶段2 实测值 | 变更原因 |
|---|---|---|---|
| `10-dag-data/methodology-dag.json` | `9ae4cc01f7b183f9a621997896a9033af6d9ca9ed38fee462077d8604496eba1` | **`865e6a3d649281930b80107e8348f420ed51eb650be75f17e8a96fedbef4e915`** | 26 个参与节点五段正文深化 + 45 条新 claim 派生的 `review_date` |
| `10-dag-data/node-content.json` | `38d5f98b9eb985c4bb40a849f9420dc6819c7048dac6c99cbc0c3d53be7b2532` | `93813c864ab8be2e3bd46ab0fbdc39645ae83800f2b1c8e36c5a4371cddb299c` | 随主图再生 |
| `10-dag-data/_base.json` | `8d100f2eaf77aeced15c6010dafd120c0d1db9c150f6aa280e35c11d84176e88` | `470ca8cec54bf9b003790d8cf45d929f440f66c8574826ebd522f974d31e23dc` | **4 个骨架种子节点**（`ESS-G-01` `ESS-G-02` `ESS-O-01` `ESS-O-02`）的正文就地深化（`meta.*` 冻结常量未动） |
| `01-books/_verify/verification-ledger.json` | `8ca515f83ee4c985da0668947302f94b4a29c26d562de95e54e7ee3e3dae79f8` | `6e8597e2af9190fcae69976d92507fad50d4c9e5f52570289d69e499155450b6` | 新增 45 条 `VR-D2-` 记录 |
| `01-books/_verify/node-claim-map.json` | `ea2dad4a501089dc6805f388dab1c87d6c12df4f929affd517938f7c50d612ef` | `8aef4fa793d840a944af575c48271e164a5d7a0390b76e61dda1c43c2133971f` | 9 个 reverse-only 节点新建主张键 |
| `01-books/_verify/reverse-gaps.json` | `c61071fee17214be407d423a947969cc5bac1ae268c498e74eaca28ec17c8514` | `c61071fee17214be407d423a947969cc5bac1ae268c498e74eaca28ec17c8514`（**未变**） | 本阶段不改缺口清单 |
| `10-dag-data/_verification-overrides.json` | `3759f2202ad4a6a120d206e6fd72dad6f3d33017805674f87252f89cc4ac86df` | `695e03c157083f86cd1f179b05027772d7ce1c3ea80a1d20bcf44d696bf25c89` | 派生覆盖集随 ledger 再生 |
| `10-dag-data/book-verification.json` | `4c4d4a8ea96cc445189cb0f02c90ac883ddb7b1b0fb8f626b962e403e7942633` | `cd605174400a17fe611954ddcf4a149cd59b33feffa08cc34269b03879b1030b` | 公开安全投影随核验层再生 |

实测命令与输出：

```
$ sha256sum 10-dag-data/methodology-dag.json
865e6a3d649281930b80107e8348f420ed51eb650be75f17e8a96fedbef4e915  ...
$ python3 16-checkpoint/aggregate.py   # 连跑 3 次
H1=865e6a3d…  H2=865e6a3d…  H3=865e6a3d…   → AGGREGATE IDEMPOTENT: PASS
```

> **验收硬约束**：新指纹 `865e6a3d…` 冻结；CI 漂移检测以本值为预期。
> `reverse-gaps.json` 阶段1→2 指纹**不变**。

---

## 2. 数据规模（实测）

| 指标 | 阶段2 实测值 |
|---|---|
| 节点 / 边 | **167 / 360**，`dag_acyclic=true`（Kahn 167/167），`validate_graph` **errors=0 warnings=0** |
| 组 / 横切主题 / 案例 | **18 / 3 / 18** |
| 层分布 | essence 51 + methodology 67 + technology 31 + case（`layer=null`）18 |
| **26 参与节点终稿字数** | **2423–2998**（min `MTH-G-03` 2423 / max `MTH-G-06` 2998）；**26/26 ∈ [2400,3000]** |
| 全局字数区间 | 全部 167 节点 ∈ [1500,3000]（G-D3 全局区间破界 0） |
| `verified` 分布 | 布尔 `true` **149** / 字符串 `"cited"` **18**（**无翻转**，与阶段1 完全一致） |
| `confidence` 分布 | `high` **151** / `medium` **16**（**无翻转**） |
| `verified=true` 占比（GR-10） | **149/167 = 89.22%**（阈值 ≥80%，PASS；与阶段1 持平） |
| 可溯源率 | **167/167 = 100.00%**（阈值 ≥95%，PASS） |

> 26 节点 `verified`/`confidence` **值零翻转**（G-D5 实测），即本阶段是**纯内容深化**，
> 未借增密之名改动核验结论——这是「增量式回写」的直接证据。

---

## 3. 核验层规模（实测）

| 指标 | 阶段1 | 阶段2 | 说明 |
|---|---|---|---|
| 记录总数 | 144 | **189** | +45 条 `VR-D2-` 阶段2 新增 |
| `evidence_strength` | direct 78 / partial 59 / inferred 7 | **direct 117 / partial 63 / inferred 9** | 新增 39 direct + 4 partial + 2 inferred |
| `direction` | forward 120 / reverse 24 | forward 165 / reverse 24 | 新增全为 forward |
| 覆盖节点数 | 35 | **35**（不变） | 阶段2 只增密既有覆盖节点 |
| 升级节点数（≥1 direct 且 0 contradicted） | 26 | **26**（不变） | |
| `contradicted` | 0 | **0** | |

**阶段2 新增记录号段**：`VR-D2-001` … `VR-D2-045`（9 个 reverse-only 节点 × 5 条）。

---

## 4. 门控基线（阶段2 实测，**全部主Agent 亲跑**）

| 层 | 阶段2 实测值 | 结论 |
|---|---|---|
| **G-D1** | 26 参与节点 × 5 段 `provenance` 非空；claim_id 零悬挂 | **PASS** |
| **G-D2** | 注水比 `ceil(Δ字/200) ≤ provenance distinct claim_id`，26/26 满足 | **PASS** |
| **G-D3** | 终稿 ∈[2400,3000] **26/26**；全局区间破界 0；排除节点改动 0 | **PASS** |
| **G-D4** | 节点正文 vs 三书原文 ≥20 字子串命中 **0** | **PASS** |
| **G-D5** | 变更集 **26/26**；遗漏 0；越界 0；值翻转 0；其余 141 节点改动 0 | **PASS** |
| **G-V1..G-V9** | **PASS=9 FAIL=0 WARN=0 SKIP=0** | **PASS** |
| **L2** 全图审计 | `nodes=167 edges=360 kahn=167/167 errors=0 warnings=0` | **PASS** |
| **L3** 结构 + 断链 | structure **434** / 问题 **0**；links **5208** / 问题 **0** | **PASS** |
| **L6** 覆盖度 | manifest **100.00%** / 四向 **100.00%** / GR-08 PASS / GR-09 PASS | **PASS** |
| **L7** 信源 | 悬挂 **0**；可溯源 **100.00%**；`verified=true` **89.22%** | **PASS** |
| **L8** 版式 | 综合覆盖率 **2128/2128 = 100.00%**，问题 **0** | **PASS** |
| **方法论专项** | 层边界 / 术语一致 / 原则↔反例 / 11 维权衡 | **4/4 PASS** |
| **幂等** | `build.py` / `aggregate.py` / `derive_verification.py --check` / `derive_densify.py --check` 连跑 diff 为空 | **PASS** |

### 4.1 负向测试（判据可信度，首次建立）

`16-checkpoint/negative_test_densify.py`：**11/11 如期**——8 个违规全部被拦
（空 provenance / 幽灵 claim / 注水 / 字数不足 / 排除节点被改 / 正文命中原文 / 变更集不符 /
`second_pass=none`），3 个正例全部 PASS。**判据可证伪，非恒真。**

### 4.2 已知遗留（WARN，非 FAIL）

- **阶段1 遗留重复 claim_id**：`ESS-O-02#principle#1` 同时被 `VR-CA-030`（CleanArch，partial）与
  `VR-DDIA-009`（DDIA，direct）使用；`node-claim-map.json` 中该节点 principle 段实际为 `#2`。
  G-V9 已收敛为「只对**阶段2 新增记录**的冲突判 FAIL」，此项报 **WARN/阶段1遗留**，待另案修复。
- **CI 中 L4 / L5 / G-V / G-D 显式 SKIPPED**（标准 runner 缺 Pillow/numpy/agent-browser，
  且公开侧无私有核验层）——**绝不伪装 PASS**；推送前须本地补跑。

---

## 5. 公开层（实测）

- 公开仓 `zako-mio/se-architecture-methodology-kg`（branch `main`）
- 推送后远端 HEAD = **`560236a74099921e09fc3cfea7108c40eb93a91a`**（Git Data API 推送）
- 远端 blob 数 **545** == 本地 `git ls-files` **545**（对账一致）
- `PUBLISH-STATE.json` `file_count = 539`（期望集；另 6 个为 preserve 专有件）
- `assemble_publish.py --check` = **0/0/0**，P1–P5 全 OK
- `gate_disclosure.py` = **PASS（0 hit / 501 files）**
- CI run **`38134616240`** = **success**（28s）
- Pages 复验（9 类页面）：首页 / 节点页（`ESS-G-01` `MTH-O-09`）/ 组页 / 术语表 / MD 镜像 /
  交互图 / 06 视图 / `report-phase7p2-plan.html` **全部 HTTP 200**

**新增公开件**：`report-phase7p2-plan.md` / `.html`（已声明进 `classes.sanitize`，
并同步扩展 `audit_publish.py` 的 `SCAN_ROOT_FILES` 以纳入脱敏机检）。
`report.original.html` 归入 `never`（历史备份，不公开）。

---

## 6. 回滚与基线重置

- **回滚路径**：撤销 `10-dag-data/_parts/*.json` 与 `_base.json` 的 26 节点正文改动、
  删除 `_parts/ledger-*.json` 与 `_parts/claims-*.json` 中的 45 条 `VR-D2-` 增量
  → 重跑 `derive_verification.py` + `aggregate.py` → 指纹回到 `9ae4cc01…`。
  私有 `_densify/`（契约 / 证据 / 分段稿 / write 文档）**原样保留**，避免重复劳动。
- **回滚触发**：① G-D4 正文红线命中 >0 且两轮改写无效；② 层2 保真复核越界率 >10%；
  ③ L8 版式无法回到 100%。
- **本基线已冻结**：新指纹 `865e6a3d…`；CI 漂移检测以本值为预期。

---

## 7. 阶段2 新增脚本与产物（私有层，除注明外不公开）

| 脚本（`16-checkpoint/`，公开） | 用途 |
|---|---|
| `derive_densify.py` | `--precheck` 前置核查 / 派生 `paragraph-claim-map.json` + `densify-report.json` / `--check` 幂等 |
| `gate_densify.py` | G-D1..G-D5 增密门控（fail-closed） |
| `merge_densify.py` | 合并回写（ledger + claims 双落点 + 正文分片），`--check`/`--apply` |
| `assemble_write_docs.py` | `_seg/` 分段小文件 → `write-<node>.json` 确定性装配 |
| `register_densify_claims.py` | 把所引证据中的新 claim 登记为 `new_claims` |
| `check_corpus_overlap.py` | 证据 + 正文的版权红线机检 |
| `negative_test_densify.py` | 门控负向测试（判据可信度） |
| `gen_densify_briefs.py` | 生成 W1/W2 生产简报 |
| `push_publish.py` | GitHub Git Data API 推送（沙箱禁 `git push`） |

| 私有产物（`01-books/_verify/_densify/`） | 说明 |
|---|---|
| `densify-contract.md` | 增密层契约（字段/枚举/落点，frozen） |
| `precheck-coverage.json` | 26 节点 × 5 段主张覆盖 + 正文分片/claims slug 落点映射 |
| `evidence-*.json`（6 分片）+ `sparse-*.json`（2 分片） | **173 条**证据素材，0 版权命中 |
| `_seg/` | 26 节点 × (5 段 txt + meta.json) = **156 文件** |
| `write-*.json` | 26 份节点改写稿 |
| `paragraph-claim-map.json` / `densify-report.json` | 派生对账产物 |
| `_briefs/` | W1/W2 生产简报 |
