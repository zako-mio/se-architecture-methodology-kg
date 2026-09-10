# 接力 Prompt：软件工程 / 架构设计方法论母库 · 阶段6（上传 GitHub）+ 遗留收尾

> 用途：跨窗口接续任务。把本文档**整段**交给下一个会话的主Agent 作为任务输入即可。
> 生成时间：2026-09-10（阶段5 完成后）　生成者：上一窗口主Agent
> 上一版接力 prompt（阶段5 Wave1+）已由本版**全面覆写**。

---

## 0. 你的角色与任务

你是**主Agent（调度者）**：分析→拆解→委派子Agent→聚合→门控。**不亲自执行多步操作**。
**阶段5（建库 + 质量门控）已全部完成**（见 §3）。本任务：**阶段6 —— 上传 GitHub（公开仓库 + Pages + Actions 自动重建）**，并按需收尾 §10 的遗留项。

工作根目录（MISSION_ROOT）：
```
~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论/
```

---

## 1. 任务背景与目标

用户要建立一座**软件工程 / 架构设计方法论母库**，兼作两用：①自己学习（人读图谱）；②为 Agent 加持架构判断力（skill）。核心理念：软件工程=理解业务需求→可维护可扩展架构设计→落地运维→持续对抗"史山"的全生命周期管理；**库自身也要体现良好架构设计**。

用户原 6 阶段计划：①权威源初搜+本地查找对齐思路 → ②搜索+分析计划 → ③全面搜索+结构化存档 → ④调整计划+设计库架构 → ⑤建库+质量门控 → ⑥反思留档+上传 GitHub。
**当前 ①②③④⑤ 全部完成；你只做 ⑥（上传 GitHub）与遗留收尾。**

---

## 2. 已确认决策（⛔ 不要重新决策，除非用户要求）

| # | 决策 |
|---|---|
| 1 | 范围=**全生命周期方法论**；内容分**三层**：本质层 essence / 方法论层 methodology / 技术实践层 technology（隔离最易过时部分）+ 案例层 case |
| 2 | 与既有库关系：母库为根；**12factor 双层纳入**（38 节点作子库/实例库，`cross_reference` 对照 + 深链，**不内联**，原库独立） |
| 3 | 组织模型=**多维复合**：DAG 依赖 + 三层 + 横切主题 + 案例层 |
| 4 | 骨架主轴=**生命周期 × 三层「非对称矩阵」**：三层=规范轴，生命周期=语境轴 |
| 5 | 层间依赖倒置：`technology --implements--> methodology --derives_from--> essence`；**内层不得引用外层**；横切用属性+染色不建跨层边 |
| 6 | 检索层=**预留接口不建**（轻量 FTS5 为候选，挂起） |
| 7 | 信源 ID=**全局重编号单一命名空间**（414 old_id → 253 canonical，已完成） |
| 8 | 规模=**按节点粒度规则生长**（当前 167 节点） |
| 9 | 交付形态=**完整双轨+多视图**（交互 DAG/节点页/组页/分层视图/学习路径/决策矩阵/跨体系对照/案例视图 + MD 镜像 + 根索引） |
| 10 | Agent skill=**只出计划**（形态后定；推荐"轻量速查+路径路由"） |
| 11 | 建库方式=**复用 12factor 生成链并重构为通用框架**（已完成） |
| 12 | 门控=**kb-construction L1–L7 + 方法论专项四项**（已全部实现，L4 为 SKIPPED） |
| 13 | **版权红线（刚性）**：书籍/标准正文只入本地语料层，公开库只承载消化重组后的知识 + 自研脚本 |
| 14 | 命名：母库仓库（阶段6）=`zako-mio/se-architecture-methodology-kg`（公开） |
| 15 | 语言：中文为主，保留英文标准名/术语 |

**挂起待用户处理**：`01-books/gap-request.md` 中 30 本付费书的合法本地副本（P0 14 / P1 10 / P2 6）；用户提供后走 pdf-worker 解析。

---

## 3. 当前进度（全部实测）

| 阶段 | 状态 | 产物 |
|---|---|---|
| 阶段1–4 | ✅ | 契约、思路对齐、权威知识地图、证据包 A–R、架构设计主文档、数据模型规范、ID 迁移 |
| **阶段5** | ✅ **完成** | 母库 **167 节点 / 360 边 / 18 组 / 18 案例**；门控 L1–L7+方法论全 PASS（L4 SKIPPED） |
| **阶段6** | ⏳ **待做** | README/LICENSE/Actions/GitHub 上传 + Pages |

**当前数据规模**：
- `10-dag-data/methodology-dag.json` = **167 节点 / 360 边 / 18 组 / 18 案例**；`dag_acyclic=true`。
- 分层：essence **51** + methodology **67** + technology **31** + case（layer=null）**18**。
- 域分布：F13 G17 H16 I14 J17 K17 L14 M14 N13 O14 X18(cases)。canonical 信源 **253**。
- 全库**无 <1500 字节点**（GR-11 达标）；`sources` 100% canonical；`verified=true` 89.22%。

**阶段5 门控实测**：L1 分片 0 错 / L2 全图 0 错 / L3 structure 0/400 + links 0/5219 / **L4 SKIPPED（未生成位图架构图）** / L5 headless 实渲染 7 用例 PASS / L6 覆盖 100% + GR-08 PASS + GR-09 35.48% / L7 可溯源 100% + verified 89.22% / 方法论四项 4/4。

---

## 4. 目录与关键文件

```
MISSION_ROOT/
├── 00-plan/                         # 契约与设计（必读）
│   ├── contract.md                  # 阶段1 契约（命名/信源分级/版权红线）
│   ├── stage4-architecture-design.md# ★ 架构设计主文档（12 章）
│   ├── stage4-data-model.md         # ★ 数据模型规范（node/edge 字段全集）
│   ├── stage5-build-contract.md     # ★★ 阶段5 建库 P0 契约（含 §〇.1 实现现状权威修正）
│   ├── dag-schema.example.json / id-migration-plan.md / id-migration-report.md / id-mapping.json
│   └── diagrams/stage4-architecture.{drawio,png}
├── 01-books/                        # 书单与可得性（gap-request.md：30 本待用户提供）
├── 02-research/                     # ★ 证据包 A–R（14 包 / 256 源）
├── 03-knowledge-map/
│   ├── canonical-sources.json       # ★★ 253 canonical 权威源主表（sources[] 只能引这里）
│   ├── knowledge-map.{md,json} / sources-index.md / topic-source-matrix.md / glossary.md
├── 10-dag-data/                     # ★ 建库数据
│   ├── _base.json                   # 骨架 11 节点 / 12 边（batch-plan 中的 W0-SKELETON）
│   ├── _parts/                      # ★ 所有分片（子Agent 只写这里，单文件 {nodes,edges}）
│   │   ├── pilot-essence.json / pilot-methodology.json
│   │   ├── W1-F/W1-M/W1-I/W1-J/W1-K/W1-L/W1-N/W1-O.json
│   │   ├── W1b-G.json / W1b-H.json
│   │   ├── W2-TEC-{H,I,J,K,GQ,LM,FN}.json
│   │   ├── W2-CASE-A.json / W2-CASE-B.json / W3-CASE-TEC.json
│   ├── methodology-dag.json         # ★ 唯一权威图（aggregate.py 产出，禁手改）
│   ├── node-content.json / stats.md # 派生镜像与统计
│   ├── _batch-plan.json             # ★ 批次跟踪（W0–W3 全 pass）
│   ├── w1-production-brief.md / w2a-tec-brief.md / w2b-case-brief.md   # 生产简报（子Agent 契约摘要）
├── 11-node-pages/                   # 167 节点页（含「对照资源 · 12factor 子库」区块）
├── 12-groups/                       # 18 组页 + 组总索引
├── 13-interactive/                  # 交互 DAG 总览（cytoscape + vendor/）
├── 14-views/                        # 6 视图（分层/学习路径/决策矩阵/跨体系对照/案例 + index）
├── 15-md/                           # AI 友好 Markdown 镜像（167 节点）
├── 16-checkpoint/                   # ★ 生成框架 + 门控脚本
│   ├── 生成链：config.py / gen_common.py / gen-{nodes,groups,views,md,interactive,index}.py / build.py
│   ├── 聚合/校验：aggregate.py / validate_graph.py / _base_extract.py / merge_pilot.py(历史)
│   ├── 门控：kb_gate.py / gate_render.py(L5) / gate_coverage.py(L6) / gate_sources.py(L7) / gate_methodology.py / gate_migration.py
│   └── 数据：deliverables.json / xref-12factor.json(38 行) / opc-mapping.json(36 行) / _render-shots/
├── _backup-idmigration/             # ID 迁移回滚备份（勿删）
├── report.md / report.html          # ★ 阶段5 报告双版本（五段式）
├── quality-gate.md                  # ★ 门控报告（L1–L7+方法论+四硬指标）
└── index.html                       # 根入口
```

**12factor 子库（独立，勿改内容）**：
```
~/opencode/archive/Mission-file/2026-08/0823-12factor-methodology/
  01-dag-data/methodology-dag.json（38 节点 / 61 边 / 16 组）
  02-node-pages/<id>.html（深链目标）
```

---

## 5. 数据契约（刚性，违者门控不过）

### 节点字段（详见 `stage4-data-model.md`）
`id / name / en / aliases / type / subtype / group / layer / domain / stage / priority / definition / detail{principle,mechanism,engineering,tradeoff} / cross_cutting[] / case[] / sources[] / verified / confidence / review_date / status / version / deprecated_at / superseded_by / errata[] / tags / entry_links`

### ID 方案
- 节点：`ESS|MTH|TEC|CAS-{域}-{序号}`（域=F..O/X；案例域固定 X，如 `CAS-X-01`）。
- 信源：`STD/OFF/BK/WEB/VEN/PAP/COM/LOC/XCV-{三位序号}`（canonical）。
- 边：`E-{2~3 位数字}`（`^E-\d{2,3}$`，**上限 E-999**）；已用块见 `_batch-plan.json`。

### 内容契约
- **五段式**：`definition`（顶层）+ `detail.principle/mechanism/engineering/tradeoff`；每节点 **1500–3000 字**（软目标）。
- **每节点必带 ≥1 权衡或反例**（GR-13）；`type=principle`/`case` 强制 `detail.tradeoff`。
- `sources[]` 必须能在 `03-knowledge-map/canonical-sources.json` 解析（**零悬挂**）。
- **层间边仅** `implements`(tech→method) / `derives_from`(method→essence)，**单向、禁越级**；`case_instance` 端点为 layer=null 时豁免跨层判定。
- `technology/tool` 必填 `version`；`essence` 层正文**禁出现工具名/版本号**。

### §〇.1 实现现状（权威修正，详见 `stage5-build-contract.md §〇.1`）
- 分片目录 = **`10-dag-data/_parts/`**，每批**单文件** `{batch_id}.json`（`{nodes,edges}`）——**非** `shards/` + `.nodes/.edges` 双文件。
- canonical 主表 = **`03-knowledge-map/canonical-sources.json`**——**非** `04-migration/`（该目录未创建）。
- 聚合/校验 = `16-checkpoint/{aggregate.py,validate_graph.py}` + 骨架 `10-dag-data/_base.json`。

---

## 6. 下一步任务（阶段6 + 遗留）

### 阶段6 · 上传 GitHub（主任务）
1. **本地准备**：`README.md`（项目介绍 + 结构 + 门控结果 + 使用方式）、`LICENSE`（建议 CC-BY-4.0 或 MIT，含版权说明）、`.gitignore`（**必须含 `16-checkpoint/__pycache__/`**、临时文件）、`.nojekyll`、确认 `index.html` 为根入口。
2. **GitHub Actions**：`.github/workflows/rebuild.yml` 自动重建（`cd 16-checkpoint && python3 build.py --config mother`）并可部署 Pages。
3. **发布前审计（刚性）**：
   - **版权红线**：确认推入公开仓的**只有消化重组后的知识 + 自研脚本**；**不得**包含 `01-books/` 内任何书籍/标准正文、`02-research/` 中的受限原文。必要时用 `.gitignore` 排除或仅推送交付物目录（`10–17` + `index.html` + README/LICENSE）。
   - 断链复测（`kb_gate.py --layers links`）与敏感信息扫描。
4. **建仓与推送**：`zako-mio/se-architecture-methodology-kg`（**公开**）。
   - ⚠️ 首次推送含 `.github/workflows/` 需 `gh auth refresh --scopes workflow`（**走代理 172.29.0.1:7890**）。
   - 推送后开启 Pages。
5. **验收**：仓库可访问、Pages 可打开、Actions 绿、无书籍/标准正文。

### 遗留项（按用户优先级选做）
- **L4 视觉门控**：若重新生成位图架构图/决策矩阵图 → 需实现 `gate_visual.py`（VLM + 像素计数）并补跑。
- **12factor 反向深链**：当前仅母库→子库（29 节点页 / 70 条深链全可达）；子库→母库回链未做。
- **30 本付费书**：用户提供合法本地副本后走 pdf-worker 解析（`01-books/gap-request.md`）。
- **检索层 D2**：挂起，需用户决策后启用（schema 预留见 `stage4-data-model.md §5`）。
- **Agent skill 形态**：当前只到计划，需用户敲定（推荐"轻量速查 + 路径路由"）。

---

## 7. 执行纪律

1. **委派**：子Agent 写分片→主Agent 合并（避免并发写同名文件）。
2. **先落盘再返回**：子Agent 必须先写文件再回 JSON 契约；主Agent **核对磁盘不信返回文本**。
3. **批次跟踪**：`10-dag-data/_batch-plan.json`；每波前读盘核对。
4. **门控分层**：单批 L1+L3；全量 L1–L7；渲染层 L5 用 headless（`gate_render.py` 已封装 agent-browser）；`skipped ≠ PASS`。
5. **编码安全**：优先 `edit` 工具；禁 `python -c` 内联管道写中文（用独立 `.py`）；改 JSON 后必验合法性 + 无 U+FFFD。
6. **低成本**：只读操作用 glob/grep；不重复检索已采集内容；子Agent 提示词引用短路径 + 生产简报（`w1/w2a/w2b-*-brief.md`），禁内联长契约。
7. **Variant**：复杂度继承 `[COMPLEXITY: 19/20] → Deep`，全程 Deep。

---

## 8. 命令与工具

```bash
MROOT="~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"

# 全量重建交付物（读 10-dag-data → 写 11–15 + index.html）
cd "$MROOT/16-checkpoint" && python3 build.py --config mother --quiet

# 聚合分片 → 主图（幂等；同时重建 node-content.json / stats.md / cases[]）
cd "$MROOT/16-checkpoint" && python3 aggregate.py

# 数据校验（全图 / 单分片）
cd "$MROOT/16-checkpoint" && python3 validate_graph.py --graph ../10-dag-data/methodology-dag.json --canonical ../03-knowledge-map/canonical-sources.json
cd "$MROOT/16-checkpoint" && python3 validate_graph.py --shard ../10-dag-data/_parts/W1-M.json --canonical ../03-knowledge-map/canonical-sources.json

# 门控
cd "$MROOT/16-checkpoint" && python3 kb_gate.py --root "$MROOT" --layers structure,links \
  --exclude _backup-idmigration --exclude 02-research --exclude 01-books \
  --exclude 03-knowledge-map --exclude 00-plan --exclude 16-checkpoint
cd "$MROOT/16-checkpoint" && python3 gate_render.py                    # L5（headless agent-browser）
cd "$MROOT/16-checkpoint" && python3 gate_coverage.py                  # L6
cd "$MROOT/16-checkpoint" && python3 gate_sources.py                   # L7
cd "$MROOT/16-checkpoint" && python3 gate_methodology.py --check all   # 方法论专项四项
```

- 12factor 参考仓库（子库，勿改内容）：`~/opencode/archive/Mission-file/2026-08/0823-12factor-methodology/`
- 本地知识资产盘点：`02-research/C-local-inventory.json`

---

## 9. 已知坑与教训（务必继承）

1. **iso.org 是 WAF 403**，标准元数据走 `web.archive.org` + `committee.iso.org` + `iso25000.com`；**不要再重试 iso.org**。
2. **sre.google 直连超时**，须 `curl -x http://172.29.0.1:7890 -A "<browser UA>"`。
3. **`merge_pilot.py` / `validate_pilot_merge.py` 是历史硬编码脚本**（只认两个 pilot 文件、canonical 必须==253）——**勿再用**；现行工具是 `aggregate.py` / `validate_graph.py`。
4. **canonical 源主表以 `canonical-sources.json`(253) 为准**，不是 `knowledge-map.json`(158)。
5. **边 id 上限 E-999**（`^E-\d{2,3}$`）；新增边前先扫已用区间，避免越界/碰撞。历史 `EB-P01..P11` 已归一化为 `E-101..E-111`。
6. **kb_gate nav 层对本框架非适用**——门控用 `structure,links`。
7. **`16-checkpoint/__pycache__` 必须进 .gitignore**；`_render-shots/` 可按需排除。
8. **12factor 深链是跨年份目录**：母库在 `2026-09/`、子库在 `2026-08/`，正确相对路径为 `../../../2026-08/0823-12factor-methodology/02-node-pages/<id>.html`（契约原 `../../` 写法致 38 处断链，已修复）。
9. **`/usr/bin/chromium-browser` 与 `/snap/bin/chromium` 在本机不可用**（snap/WSL 报错）；L5 渲染统一用 **`agent-browser` CLI**（npm 全局，`open/eval/close`，已封装进 `gate_render.py`）。
10. **交互图下钻视图 `zcount` = 成员节点 + 边上下文 stub 节点**，**不等于** `groups[].node_ids` 长度；L5 判据应为「成员集 == node_ids」（`gate_render.py` 已按此实现，另有 `--strict-zcount` 演示字面口径）。
11. **子Agent 单次 `write` 超参上限会被截断**（长 JSON 分片）→ 用脚本化分片写入或 `edit` 分段。
12. **内容合并与索引聚合不宜并行**（会产生"未落盘"误报）——聚合步骤串行或收尾重扫磁盘。
13. **软目标不阻断 ≠ 可忽略**：GR-11 字数（1500–3000）不触发 error/warning，Wave 0 骨架曾遗留 11 个 281–424 字节点被静默忽略（已补齐）。建议后续把 GR-11 常态输出为 warning 清单。
14. **勘误已入库**：Lehman 8 定律成文于 1996（非 1980）；Royce 1970 无 "waterfall" 且强调迭代——沿用勿回退。

---

## 10. 待用户提供 / 决策

- 30 本付费书合法本地副本（`01-books/gap-request.md`，P0 14 本优先）→ 提供后 pdf-worker 解析。
- 是否启用检索层（D2，当前挂起）。
- Agent skill 最终形态（当前只到计划）。
- 是否补做 L4 视觉门控 与 12factor 反向深链。
- 阶段6 是否一口气做完或分批暂停（用户偏好"每阶段暂停"）。

---

## 11. 验收标准（阶段6 + 每波自检）

- **阶段6**：公开仓库 `zako-mio/se-architecture-methodology-kg` 可访问；Pages 可打开；Actions 绿；**无书籍/标准正文入库**；README 含结构与门控结果。
- 结构：UTF-8 无 BOM 无 U+FFFD；断链 0；JSON 全合法。
- 数据：`validate_graph.py` errors=0；`dag_acyclic=true`；`sources[]` 零悬挂。
- 门控：L1–L7（L4 若启用）+ 方法论四项全 PASS；`skipped` 显式记录。
- **无新鲜验证证据不得声称完成**；任务末尾：清理 `/tmp`；执行 Mission 留档询问；按协议封装 Reflection 4 层写入 `~/opencode/archive/Reflection/pending.json`。
