# 接力 Prompt：阶段3 续做轮（第二轮）—— P2 轨B 三本核验收口 + P3 收尾

> 生成：2026-10-12（P0 claims 链修复 + P1 K 域上限 ADR-005 轮收尾）
> 本文件自包含：只需本文件 + 仓库即可开工。
> 母任务：`~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论`（下称 `MROOT`）
> **开工前必读**：`MROOT/00-plan/stage7p5p1-baseline.md`
> 上一份接力件：`MROOT/00-plan/NEXT-ROUND-PROMPT-2.md`（其 P0/P1 **已全部完成**，勿重做）

---

## A. 上一轮已完成（**勿重做**）

| 项 | 结果 |
|---|---|
| **P0** claims 完整性 | 差集 **73 → 0**；`build_claims()` 改为按 `claim_id` 跨 slug 并集；G-V1 增 3 项子判据；`negative_test_verification` **11/11** |
| **P0** 历史重复 `claim_id` | `ESS-O-02#principle#1` 双记录（语义不同，不合并）→ 后者重编号为 `#principle#3`；全层重复 **0** |
| **P1** K 域上限裁决 | **ADR-005** 过 `gate_architecture` **6/6**；`DENSIFY_NODES` **26 → 41**（`STAGE2_NODES` 26 ∪ `K_DOMAIN_NODES` 17）；ADR-003 加 `amended_by` |
| **P1** 42 条被裁证据回捞 | 从 DSH 会话转录**完整回捞 42/42**；按 ADR-005 边界**恢复 34 条在域**、**裁回 8 条域外**；ledger 522 → **556** |
| **P1** 第二路复核 | 24 条 direct 全部独立复核（2 工人）；**5 条降级**；direct 的 `second_pass` 覆盖率 **100%** |
| **P1** 公开层 | 推送 2 次；远端 HEAD `0ff129d6deb3`；573 blobs == 本地；CI **success**；Pages **200** |
| **P2** 语料 + 登记 | 三本语料/TOC/按章切片/4 处登记**全部就绪**；BK-036 暂存分片已产出并**通过机检**（21/21/4，7 节点，19 direct + 2 partial），**尚未合并** |

---

## B. 起点状态（实测）

```
本地 HEAD          = 44215a3（收尾提交见 §I）
图谱指纹            = a96354c791c0b2354f584a6df1d950549b45cbc577a2fea2c35ca04046378f85（**已变更**）
公开仓远端 HEAD     = 0ff129d6deb3e2051820bddda1b341426dc15b5d（573 blobs == 本地 ls-files 573）
CI                 = run 38189349224 success；Pages 200
```

- 图谱：**168 节点 / 364 边 / 18 组 / 18 案例**；`validate_graph` errors=0、无环
- 核验层：**556 记录**（`direct 379 / partial 155 / inferred 22`）；覆盖 **78 节点**；缺口 **119**
- `claims` 完整性差集 **0**；重复 `claim_id` **0**；超限节点 **0**；K 域最高 **12**（`ESS-K-02`）
- 已核验书：**10 本**
- **本地备份（唯一）**：`~/.dsh-backups/stage7p5-p1-20261012/`

---

## C. 🔴 环境事实（继承 + **本轮新增 11 条**）

| # | 事实 |
|---|---|
| 1 | **子 Agent 无 shell** ⇒ 脚本主Agent 亲跑。`run_gate` **只允许配置 roots 内脚本**（实测 MROOT 外的 `gate_architecture.py` 被拒 `OUTSIDE_ROOTS`）⇒ 该门控用 **bash** 跑。 |
| 2 | **子 Agent 自述不可信**：计数权归主 Agent；自评一律机器复验。 |
| 3 | **工人会留残留**：本轮实测 `_tmp_rm_02b.py`、`adr005_verify2.py`、`_selfcheck_qasc_a.py`、`_lcs_probe_qasc.py`、`_tmp_adr005_*.py`。**收尾必扫根目录 + `16-checkpoint/` + `_review/staging/`**。 |
| 4 | 🔴 **工人会「无产出即沉默」**：BK-031 工人**因上下文耗尽**（`ran out of room`）零产出；BK-036 与 ADR-005 工人也一度长时间无输出。**对策：`send_message` 追问状态可唤醒它继续产出**（本轮两次实测有效）。派活后 5–10 分钟无产出先追问，再决定转交。 |
| 5 | 🔴 **给工人的语料必须窄**：BK-001 语料 **1.3 MB**，整读会耗尽上下文。**已生成按章切片**：`01-books/_verify/_text/_slices/<slug>/ch-<章号>.txt`（`slice_corpus_by_chapter.py --all`）。派活**只给目标章切片**。<br>⚠️ 切片目录会让「按目录无差别复制」的脚本崩溃：本轮 `negative_test_verification.py` 的 `stage()` 曾因 `_text/_slices/` 抛 `IsADirectoryError` 使**负例自检整体挂掉**（判据可信度归零）；已修为「只复制普通文件、跳过子目录」。**在 `_text/` 下新增子目录后，务必重跑负例自检**。 |
| 6 | 🔴 **`merge_verify_staging.py` 不是幂等同步**：`apply_secondpass.py` / `writeback_gap_ids.py` / `normalize_gap_ids.py` **只写 `_parts/`、不回写 staging** ⇒ staging 对已复核书**落后**；重跑 merge 会把第二路裁决与缺口号回写**整批回退**。已加 **fail-closed 护栏**（拒写 + 提示 `--force`）；**`--check` 报「有 N 件待写」属预期**。 |
| 7 | **`apply_secondpass.py` 曾非幂等**（留痕标记重复叠加，实测叠 3 份）；已修为「追加前先剥历史标记」。 |
| 8 | 🔴 **动核验层后必须跑 `aggregate.py`**（不只是 `build.py`）：它把 `_verification-overrides.json` 并回 DAG 节点（`review_date`/`confidence`/`errata`）⇒ **图谱指纹会变**（本轮 `MTH-K-04` 的 `confidence` 由 medium 升 high）。指纹变更须**新建基线文件**（append-only）。 |
| 9 | 🔴 **`/tmp` 会被环境清理**：本轮首份备份（11 MB）在会话间隙**消失**。备份一律放 `~/.dsh-backups/`。 |
| 10 | **DSH 会话转录是回捞数据的唯一来源**：`~/.dsh/sessions/<workspace>/<session>/session.v4.jsonl.zstd`，**多帧 zstd**；Python 无 zstd 模块 ⇒ 用 **ctypes 调 libzstd 流式解**（`ZSTD_findFrameCompressedSize` + `ZSTD_decompressStream`；`ZSTD_decompress` 对无 content-size 的帧不可用）。工具结果常**双重编码**（`\"record_id\": …`）⇒ 需**转义形态专用配对器**（见 `recover_trimmed_records.py`）。 |
| 11 | **在线采集三处坑**：① 接力件给的 BK-036 URL **404**，正确为 `https://people.ece.ubc.ca/matei/EECE417/BASS/ch04lev1sec3.html`；② `abseil.io` 的 `ch26` 是 `data-type="afterword"` 且仅 3 201 字符，需放宽容器类型与字符下限；③ **语料章头必须为 `=== <章号> \| <标题> ===`**（`validate_staging_shards.py` 依赖它切章级正文；用 `## N. Title` 会让节标题交叉校验**静默退化**）。 |
| 12 | **联网**：模型 API 与 `web_fetch` 不读代理环境变量；本轮三个站点**直连均 200**。 |
| 13 | **`git push` 被禁**：公开仓走 Git Data API（`push_publish.py`）；推送前**必须**在 `_publish` 内 `git add -A && git commit`；`--apply` 必传 `--message`。 |
| 14 | **CI 触发**：workflow `paths` 含 `10-dag-data/**` ⇒ 动了 DAG 就**自动触发**（本轮两次均自动成功）。只改生成物时须手动 `gh workflow run rebuild.yml`。 |
| 15 | **子 Agent 并发上限 5**（用户约束）。 |
| 16 | **`python -c` 写中文会截断多字节**：写独立 `.py` 文件，或用 `write`/`edit`。 |
| 17 | **两处反向漂移仍在**（未激活）：① opencode 侧比仓内源侧新；② `0911-opencode架构能力/tooling/` 的 `_private/*` 比已装侧旧（`gate_architecture.py` 30 589 B vs 54 235 B）。**再跑 stage-1 `--apply` 会重新引入降级**。 |

> **刚性协作模式**：计数权归主Agent，工人只写文本、不报数字；凡工人自评一律机器或第二路复验。

---

## D. P2 · 轨B 三本核验（**本轮主任务**）

### D.1 已完成的前置（勿重做）

4 处登记**全部就绪**：`gate_verification.py`（`SLUG_RECORD_PREFIX`/`SLUG_TEXT`/`SOURCE_SLUG`）、
`merge_verify_staging.py`（`BOOKS`）、`check_corpus_overlap.py`（`CORPUS`）、`verify-contract.md` 登记表。

| 书 | slug | source_id | record 前缀 | staging 前缀 | gap 前缀 | 语料 |
|---|---|---|---|---|---|---|
| Software Engineering at Google | `sweg` | BK-001 | `SWEG` | `sweg` | `GAP-SWEG-` | `_text/sweg.txt`（26 章切片） |
| The Twelve-Factor App | `twelve-factor` | BK-031 | `TFA` | `tfa` | `GAP-TFA-` | `_text/twelve-factor.txt`（12 章切片） |
| SAiP Ch4 质量属性场景 | `saip-ch4` | BK-036 | `QASC` | `qasc` | `GAP-QASC-` | `_text/saip-ch4.txt`（1 章切片） |

### D.2 逐本流程（10 步）

1. **派工**（`subagent`，**只给目标章切片**）产 `_review/staging/{ledger,claims,gaps}-<prefix>-a.json`：
   每节点 ≤ 上限；`claim` **必须改写**（与原文最长公共子串 ≤20 字）；`anchor.chapter` 须在 TOC 内、
   `anchor.section_title` 须语料真实存在；`claim_id` 的 `<n>` **用 300+ 号段**；`review.second_pass` 写 `"none"`。
2. **合并前机检**：`validate_staging_shards.py --slug <s> --prefix <p> --book-source-id BK-xxx`
3. `merge_verify_staging.py --only <slug>`（**新书可安全合并**；护栏只对已复核书生效）
4. **第二路复核**（覆盖**全部 direct**；prompt 必须要求 `anchor_locatable`）→ 合并 verdict → `apply_secondpass.py --all`（只降不升）
5. `derive_verification.py && derive_verification.py --check`
6. `gate_verification.py --check all`（9/9）→ `check_corpus_overlap.py --target evidence`（0 命中）
7. **`aggregate.py`** → `validate_graph.py`
8. **`build.py --config mother --quiet`**
9. 公开层：`assemble_publish.py --check`（0/0/0）→ `--apply --refresh-sanitize` → `gate_disclosure` →
   **`_publish` 内 `git add -A` 提交** → `push_publish.py --apply --message` → 必要时手动触发 CI
10. **重跑 P1 扫描**：`replay_admission.py --scan-promotion`

### D.3 本轮剩余的具体欠账

| # | 欠账 | 说明 |
|---|---|---|
| **D3-1** | **BK-036 合并 + 第二路复核** | 分片已就绪且机检 PASS。**合并前先处置 3 条 WARN**：`GAP-QASC-001/002/004` 的 `proposed_node` 未在 ADR-004 候选册登记 ⇒ 走 ADR-004 准入或改判 `existing_node_id`。 |
| **D3-2** | **BK-031 重做** | 上次因整读 27 K 语料 + 契约 + 体例耗尽上下文。改为：**只给 `_slices/twelve-factor/ch-<I…XII>.txt`**（每片 1.5–3.7 K），**按节点分批**（如 2 节点/工人）。目标节点：`ESS-J-01` `ESS-J-02` `MTH-J-01` `MTH-J-04` `MTH-O-03`(上限 16) `MTH-O-08`。 |
| **D3-3** | **BK-001 派工** | 语料 1.3 MB ⇒ **必须按章切片**派活。节点↔章：`ESS-I-01/ESS-I-03/ESS-I-04/MTH-I-01`（Ch11–14 测试）、`ESS-H-07/MTH-H-04`（Ch9 代码复审 / Ch10 文档）、`TEC-I-01`（Ch23 CI / Ch24 CD）、`MTH-O-04`（Ch16–18）。 |
| **D3-4** | 三本完成后 | 重跑 §D.2 第 5–10 步；`publish-manifest.json` 若需新公开件须显式声明。 |

---

## E. 数据契约要点（刚性，**本轮新增 3 条**）

| 项 | 规则 |
|---|---|
| 节点 ID | `^(ESS\|MTH\|TEC\|CAS)-[A-Z]{1,2}-\d{2}$`；前缀须与 `node.layer` 一致 |
| 边 ID / 字段 | `^E-\d{2,3}$`；边字段用 **`from`/`to`** |
| **claims 完整性** | `ledger.claim_id ⊆ node-claim-map.claim_id`（**G-V1 强制，差集须 0**） |
| **`claim_id` 唯一** | 全局唯一；重复 ⇒ **FAIL** |
| **档位集合自洽** | `DENSIFY_NODES == STAGE2_NODES \| K_DOMAIN_NODES`（G-V1 强制）；`DENSIFY_NODES` 必须保持**字面 set 字面量**（校验器用正则解析） |
| 单节点上限 | 阶段2 参与节点 **16**、**K 域全 17 节点 16**、其余 **8**（ADR-003 / ADR-005） |
| 前缀纪律 | **前缀不得互为前缀**（`sre` ⊂ `srew` 曾串号；故 BK-036 用 `QASC` 而非 `SAIPCH4`） |
| `claim` | 必须改写；与书原文最长公共子串 **≤20 字** |
| 第二路复核 | 覆盖**全部** `direct`；prompt **必须要求 `anchor_locatable`** |
| 生成链顺序 | 工人 → staging → `merge` → `apply_secondpass`（只写 `_parts`）→ 缺口号脚本（只写 `_parts`）→ `derive` → **`aggregate`** → `build` → 公开层 |
| 确定性 | 脚本**无时间戳**；`ensure_ascii=False, indent=2` + 末尾换行 |
| 语料章头 | `=== <章号> \| <标题> ===` |

权威契约：`MROOT/01-books/_verify/_meta/verify-contract.md`（**13 slug** 登记表 + §10 生成链顺序与护栏）

**三重隔离（缺一即违规）**：① 本地仓 `.gitignore:13` 忽略 `01-books/`；② `_publish/.gitignore:15` 忽略 `01-books/_verify/`；③ `publish-manifest.json` 的 `classes.private` 含二者 + `private_probe`。

---

## F. 命令清单

> `MROOT="$HOME/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"`；除注明外均在 `$MROOT` 下执行。

```bash
# —— 采集（三本已采完，勿重跑）——
python3 16-checkpoint/extract_web_book.py --book sweg            # 26 章（~2 分钟）
python3 16-checkpoint/slice_corpus_by_chapter.py --all           # 按章切片（供工人窄读）

# —— 核验链 ——
python3 16-checkpoint/validate_staging_shards.py --slug <s> --prefix <p> --book-source-id BK-xxx
python3 16-checkpoint/merge_verify_staging.py --only <slug>      # 新书可合并；已复核书会被护栏拒写
python3 16-checkpoint/apply_secondpass.py --all                  # 只降不升；已幂等
python3 16-checkpoint/derive_verification.py && python3 16-checkpoint/derive_verification.py --check
python3 16-checkpoint/gate_verification.py --check all           # 须 9/9
python3 16-checkpoint/check_corpus_overlap.py --target evidence  # 须 0 命中

# —— 图谱 ——
python3 16-checkpoint/aggregate.py && python3 16-checkpoint/aggregate.py   # 连跑两次比对哈希
python3 16-checkpoint/validate_graph.py --graph 10-dag-data/methodology-dag.json \
  --canonical 03-knowledge-map/canonical-sources.json
python3 16-checkpoint/build.py --config mother --quiet           # 🔴 动核验层必跑

# —— 全门控（主Agent 亲跑）——
python3 16-checkpoint/gate_densify.py --check all && python3 16-checkpoint/gate_coverage.py
python3 16-checkpoint/gate_sources.py && python3 16-checkpoint/gate_layout.py --check all
python3 16-checkpoint/gate_methodology.py --check all
python3 16-checkpoint/kb_gate.py --root "$MROOT" --layers structure,links \
  --exclude _backup-idmigration --exclude 02-research --exclude 01-books \
  --exclude 03-knowledge-map --exclude 00-plan --exclude 16-checkpoint \
  --exclude _publish --exclude 18-design --exclude .github
python3 16-checkpoint/negative_test_verification.py              # 须 11/11
python3 16-checkpoint/negative_test_densify.py                   # 须 11/11
python3 16-checkpoint/replay_admission.py && python3 16-checkpoint/replay_admission.py --scan-promotion
export PATH="$HOME/.nvm/versions/node/v24.19.0/bin:$HOME/.local/bin:$PATH"
python3 16-checkpoint/gate_visual.py --check all                 # 须 PASS
python3 16-checkpoint/gate_render.py --timeout 25                # 须 PASS

# —— 架构 ADR 门控（MROOT 外脚本，须用 bash；run_gate 会拒）——
python3 ~/.dsh/skills/opencode/architecture-judgment/_private/gate_architecture.py \
  --kind adr --input 18-design/adr/ADR-005.json

# —— 公开层 ——
python3 16-checkpoint/assemble_publish.py --check                # 须 0/0/0 + P1–P5 OK
python3 16-checkpoint/assemble_publish.py --apply --refresh-sanitize
python3 16-checkpoint/gate_disclosure.py --root "$MROOT/_publish"
cd "$MROOT/_publish" && git add -A && git commit -m "..."        # 推送前必做！
cd "$MROOT" && python3 16-checkpoint/push_publish.py --apply --message "<本轮提交信息>"
gh run list --repo zako-mio/se-architecture-methodology-kg --limit 3
gh run watch <id> --repo zako-mio/se-architecture-methodology-kg --exit-status
# 回验：gh api .../branches/main --jq .commit.sha ；tree blob 数须 == 本地 ls-files
#       curl -o /dev/null -w '%{http_code}' https://zako-mio.github.io/se-architecture-methodology-kg/<path>

# —— 本地归档 ——
cd "$MROOT" && git add -A && git commit -m "<scope>: <description>" && git log --oneline -3
```

---

## G. 验收判据（**无新鲜验证证据不得声称完成**）

- **结构**：UTF-8 无 BOM、无 U+FFFD；内部断链 0；JSON 全合法。
- **数据**：`validate_graph.py` errors=0；`dag_acyclic=true`；`sources[]` 零悬挂。
- **核验**：`gate_verification.py` **9/9**；`ledger.claim_id − node-claim-map.claim_id = 0`；重复 `claim_id = 0`；超限节点 **0**。
- **第二路复核**：全部 `direct` 的 `review.second_pass ∈ {passed, disputed}`（**100%**）。
- **版权**：`check_corpus_overlap.py` **0 命中**；公开层无 `claim`/页码/摘句。
- **门控**：G-D 5/5；L2/L3/L6/L7/L8 + 方法论四项全 PASS；**L4/L5 须 PASS（不得标 SKIP）**；**`skipped ≠ PASS`**。
- **判据可信度**：`negative_test_verification` **11/11**；`negative_test_densify` **11/11**；`replay_admission` 一致率 **100%** + 负例 **4/4**；**新增判据必须同时提交负例**。
- **幂等**：`derive --check` / `aggregate` 连跑 / `build` 连跑 diff 为空；`apply_secondpass --all` 连跑不叠加标记。
- **计数**：五处对账偏差 0；新建组 0（除非显式裁决）。
- **公开层**（若动）：装配 0/0/0；`gate_disclosure` PASS；**CI success**；Pages 200；推送前 `_publish` 内 `git add -A`；`--message` 必传。
- **收尾**：更新 `NEXT-SESSION-HANDOFF.md`；**指纹变更则新建基线文件**；**清理工人残留**（§C#3）。

---

## H. 待用户决策

| # | 事项 | 选项 | 默认 |
|---|---|---|---|
| 1 | **域外贴限证据**（`MTH-J-07`/`MTH-N-05`/`TEC-J-04` 共 8 条被裁证据） | 另立 ADR 放宽 / 维持 8 条 | **维持**（ADR-005 已显式排除） |
| 2 | BK-036 的 3 条新缺口提案（`GAP-QASC-001/002/004`） | 走 ADR-004 准入 / 改判 `existing_node_id` / 留作 WARN | **走 ADR-004 准入评估** |
| 3 | `P0-09` 真第 2 版语料（Refactoring 2nd/2018） | 采购/借阅后采集 / 维持 1st/1999 | **维持**（bounded 尝试仅见未授权「免费 PDF」站，按版权纪律不采用） |
| 4 | SRE/Workbook 派生内容进公开层（ND） | 维持只私有层 / 连公开层 | **维持私有层** |
| 5 | `_verification-overrides.json` 含 `_evidence` 已在公开层 | 改为不公开 / 保持现状 | **保持现状** |
| 6 | `0911-opencode架构能力/tooling/` 私有层旧版 | 更新为 1011 版本 / 不碰 | **不碰** |

---

## I. 收尾动作（必做）

1. **清理残留**：工作区根目录、`16-checkpoint/`、`01-books/_verify/_review/staging/`（残留模式：`_tmp*`、`adr005_*`、`_selfcheck_*`、`_lcs_probe_*`）。
2. **本地归档提交** → 记录 `git log --oneline -3`。
3. **更新接力文档** `00-plan/NEXT-SESSION-HANDOFF.md`（覆写顶部「本轮增量」块）。
4. **若指纹变更**：新建基线文件（9 文件 SHA-256 + 门控全表 + 公开层对账 + 回滚路径）。
5. **备份**：`~/.dsh-backups/<轮次>-<日期>/`（**不要用 `/tmp`**）。
6. **报告**：若用户要求留档，产双版本（`.md` + `.html`，过 `gate_report.py` 5/5、5 段完整），路径须符合 `Mission-file/{YYYY-MM}/{MMDD-任务名}/`。

---

## J. 关键文件导航

```text
MROOT/
├── 00-plan/
│   ├── NEXT-SESSION-HANDOFF.md              # 接力文档（每轮须更新）
│   ├── NEXT-ROUND-PROMPT-3.md               # ★ 本文件（归 classes.never，不公开）
│   ├── NEXT-ROUND-PROMPT-2.md               # 上一份（P0/P1 已完成，作对照）
│   ├── stage7p5p1-baseline.md               # ★ 本轮基线（指纹 a96354c7…）
│   ├── stage7p5-baseline.md                 # 上一份基线（指纹 f1f09a9b…）
│   └── stage7-completion-roadmap.md         # 四轨路线图（§1.2/§4 已被证伪，勿采信）
├── 01-books/                                # 私有（三重隔离）
│   ├── _verify/
│   │   ├── _meta/verify-contract.md         # ★ 权威机读契约（13 slug 登记表 + §10 生成链顺序）
│   │   ├── _meta/trimmed-recovery.json      # ★ 42 条被裁记录的回捞报告（含域外裁回 8 条）
│   │   ├── _meta/claims-fill-report.json    # 补写报告（24 条）
│   │   ├── _parts/{ledger,claims,toc,gaps}-<slug>.json   # 13 slug
│   │   ├── _text/<slug>.txt                 # 语料（含 `_slices/<slug>/ch-*.txt` 按章切片）
│   │   ├── _review/staging/                 # 暂存分片（BK-036 的 qasc 分片已就绪）
│   │   └── _review/secondpass-<slug>.json   # 第二路复核裁决
│   └── free-official-extracts.json          # FO-01（BK-001 章节表来源）
├── 10-dag-data/                             # 权威图 + 分片（禁手改派生物）
├── 16-checkpoint/                           # ★ 生成链 + 门控 + 审计
│   ├── recover_trimmed_records.py           # ★ 会话转录回捞（多帧 zstd + 转义形态）
│   ├── fill_missing_claims.py               # ★ claims 补齐
│   ├── fix_duplicate_claim_ids.py           # ★ 重复 claim_id 重编号
│   ├── extract_web_book.py                  # ★ 在线书采集（三种容器）
│   ├── slice_corpus_by_chapter.py           # ★ 按章切片（工人窄读用）
│   ├── make_secondpass_worklist.py / merge_secondpass_worklists.py
│   ├── validate_staging_shards.py           # 合并前机检（依赖 `=== N | T ===` 章头）
│   ├── merge_verify_staging.py              # 暂存 → SSOT（**含第二路护栏**）
│   ├── apply_secondpass.py                  # 第二路裁决回写（**只写 `_parts`**）
│   ├── derive_verification.py               # 核验层派生（build_claims 已修）
│   ├── gate_verification.py                 # G-V1..G-V9（含档位集合与自洽校验）
│   ├── check_corpus_overlap.py              # 版权红线机检
│   ├── assemble_publish.py / push_publish.py
│   └── negative_test_{densify,verification}.py
├── 18-design/adr/                           # ADR-001..005(.json/.md)
└── 20-agent-skill/                          # architecture-judgment 能力包（源侧）
```

---

## K. 一句话总结

**本轮 = 把 BK-036/BK-031/BK-001 三本走完 §D.2 十步（BK-036 分片已就绪，先合并；BK-031/BK-001 用按章切片重派工），然后按 §I 收尾。**

四条不可忘：

1. **给工人的语料必须是章切片** —— 整读 1.3 MB 语料会让工人 `ran out of room` 零产出（本轮实测）。
2. **对已复核书禁止重跑 `merge_verify_staging.py`** —— staging 落后于 `_parts`，重合并会回退第二路裁决与缺口号回写（护栏已加，`--check` 的 stale 是预期）。
3. **动核验层必跑 `aggregate.py` 再跑 `build.py`** —— 否则图谱指纹与生成物不一致；指纹变更须新建基线（append-only）。
4. **备份不要放 `/tmp`** —— 本轮首份 11 MB 备份被环境清理；一律放 `~/.dsh-backups/`。
