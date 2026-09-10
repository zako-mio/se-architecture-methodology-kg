# 阶段4 · 统一 ID 命名空间设计与"重编号"安全迁移方案（v1.0）

> 母任务：0910-软件工程架构方法论 · 阶段4 建库设计交付物（本文件只出方案与工具设计，**不执行迁移**）
> 日期：2026-09-10　状态：设计稿
> 背景：阶段1 用全局 ID（`S1-STD-01`），阶段2 各包用局部 ID（`S1-01`/`S1-F01`/`P-S1-xx`/`R-XC-nn`），存在**跨包同名不同源**的碰撞（`sources-index.md §5`），若不统一，阶段5 建库必断链。
> 配套文件：`stage4-data-model.md`（节点 schema 引用规范 ID）、`dag-schema.example.json`（样例）

---

## 0. 问题陈述（为什么必须迁移）

| 问题 | 证据 | 后果 |
|---|---|---|
| 跨包裸 ID 碰撞 | `K/S2-01`=Google SRE Book，`J/S2-01`=Twelve-Factor，`N/S2-01`=Conway 原文 | 引用不可脱离包名，聚合即歧义 |
| 同形全局式 ID 却指向不同源 | `I/S2-BK-30`=Mike Cohn《Succeeding with Agile》；阶段1 `S2-BK-30`=《Team Topologies》 | 同名不同源，**无法映射为同一 ID** |
| 厂商段碰撞 | `I/S3-VEN-02..04`（Google Testing Blog/DORA/Sonar）vs `Q/S3-VEN-02..08`（AWS/GCP/ThoughtWorks） | 同一 ID 字符串承载 3 个不同实体 |
| 连续编号段其实碰撞 | `I/S2-WEB-12`=Test Pyramid（Fowler）；阶段1 `S2-WEB-12`=Wikipedia 条目组 | 易被误判为"续编号"而合并错误 |
| 同一实体重复出现 | `J/S2-01`=`S2-BK-31`=Twelve-Factor；`R/S4-PAP-01`=`S4-PAP-01` | 需合并为一条并保留别名 |

**结论**：迁移不是"改名"，而是**建一条以"实体身份"为准的统一命名空间**，再把所有引用脚本化改写。用户已明确"重写风险不低"，故本方案的核心是**一切改动可生成、可核对、可回滚、可重放**。

### 0.1 范围边界（与主设计文档的分工）

本项目存在**两套正交的 ID 命名空间**，本文件只负责其中一套：

| 命名空间 | 形态 | 归属文档 | 本文件角色 |
|---|---|---|---|
| **信源 ID**（证据来源） | `{类别}-{序号}`，如 `STD-001` | **本文件** | 定义 + 迁移方案 |
| **节点 ID**（知识节点） | `{层前缀}-{域}-{序号}`，如 `ESS-H-01` | **主设计 §八** | **不涉及** |

主设计 §八 已确立节点 ID 形态为 `{层前缀}-{域}-{序号}`（`ESS/MTH/TEC`），并要求"为阶段1 全局 ID（`S1-STD-*`）与阶段2 包限 ID建立映射表"。**本文件的信源 ID 命名空间与迁移方案，正是该"映射表"的落地设计**；两套命名空间互不冲突、可同时使用（节点 `sources[]` 引用信源 ID，节点自身用节点 ID）。本文件**不得**规定或改动节点 ID。

---

## 1. 统一 ID 命名空间设计（信源 ID）

### 1.1 命名形态

```
{类别}-{序号}        序号为 3 位零填充十进制
```

**类别（按"信源载体性质"划分，与来源包解耦）**：

| 类别 | 前缀 | 语义 | 覆盖原 ID |
|---|---|---|---|
| 国际标准 | `STD` | ISO/IEC/IEEE 等标准 | `S1-STD-*`、I 包 `S1-STD-11..20`、F 包标准 |
| 官方体系 | `OFF` | 官方知识体系/机构/门户 | `S1-OFF-*`、F/G/I 包官方页、`P-S1-01` 类 |
| 经典著作 | `BK` | 经典书籍 | `S2-BK-*`、J/K/L/M/N/P 包内书籍 |
| 权威文章 | `WEB` | 权威作者文章/官方章节 | `S2-WEB-*`、各包 bliki/官方章节 |
| 厂商体系 | `VEN` | 厂商架构中心 | `S3-VEN-*`、Q 包、G/K/L/N/P 包厂商页 |
| 学术论文 | `PAP` | 学术论文 | `S4-PAP-*`、各包论文 |
| 会议期刊 | `COM` | 会议/期刊入口 | `S4-COM-*` |
| 本地资产 | `LOC` | 本地语料/工具/方法论/实战留档 | `L-*`（含 `L-KG/SK/RL/MM/PA/BK`） |
| 交叉验证 | `XCV` | 交叉验证二手源 | `R-XC-*` |

> **关键决策**：`P-S1/P-S2/P-S3/P-S4` 与 `R-*` **不新增顶层前缀**，而是按其**载体性质**落入 `STD/OFF/BK/WEB/VEN/PAP/LOC/XCV`。例如 `P-S3-01`（SonarQube 质量门控文档）→ `VEN`；`P-S4-08`（Li 2022 架构腐化）→ `PAP`；`R-XC-03`（SEBoK 概览页）→ `XCV`。这样类别维度与 tier 维度解耦，避免"P 域"这种**来源包维度**污染命名空间。
> 说明：`COM` 与 `LOC` 少于 3 位需求，仍统一 3 位（`COM-001`），保证正则一致。

### 1.2 与原 ID 的对照

| 原 ID 形态 | 规范 ID | 别名记录位置 |
|---|---|---|
| `S1-STD-01` | `STD-001` | `aliases:[{package:"PHASE1",id:"S1-STD-01"}]` |
| `S2-BK-31` | `BK-031` | `aliases:[{package:"PHASE1",id:"S2-BK-31"}]` |
| `J/S2-01`（=十二要素） | `BK-031` | `aliases:[{package:"J",id:"S2-01"},{package:"PHASE1",id:"S2-BK-31"}]` |
| `I/S2-BK-30`（Mike Cohn） | `BK-055`（示例） | `aliases:[{package:"I",id:"S2-BK-30"}]` |
| `Q/S3-VEN-02`（AWS） | `VEN-002` | `aliases:[{package:"Q",id:"S3-VEN-02"}]` |
| `I/S3-VEN-02`（Google Test Blog） | `VEN-010`（示例） | `aliases:[{package:"I",id:"S3-VEN-02"}]` |
| `R-XC-01` | `XCV-001` | `aliases:[{package:"R",id:"R-XC-01"}]` |
| `L-KG-01` | `LOC-001`（示例） | `aliases:[{package:"PHASE1",id:"L-KG-01"}]` |

### 1.3 序号分配策略（按类别 + 来源包分段预留）

**分配顺序（确定性）**：先阶段1 全局 ID（按原序号），再阶段2 包按字母序 `F,G,H,I,J,K,L,M,N,P,Q,R`，包内按局部 ID 排序。以"实体"为单位递增（同实体复用不占新号）。

**分段预留表**（`NNN` 窗口，块间留 ≥5 空位以吸收补录）：

| 类别 | 窗口 | 阶段1 | F | G | H | I | J | K | L | M | N | P | Q | R | 预留 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `STD` | 001–050 | 001–010 | 021–024 | — | — | 011–020 | — | — | — | — | — | 025–030 | — | — | 031–050 |
| `OFF` | 001–060 | 001–008 | 009–018 | 019–028 | — | 029–034 | — | — | — | — | — | 035–039 | — | — | 040–060 |
| `BK` | 001–120 | 001–035 | — | — | — | 036–040 | 041–045 | 046–048 | 049–054 | 055–056 | 057–059 | 060–065 | — | —* | 066–120 |
| `WEB` | 001–080 | 001–012 | — | — | 021–030 | 013–020 | — | — | 031–038 | 039–040 | 041–045 | 046–050 | — | — | 051–080 |
| `VEN` | 001–060 | 001 | — | 009 | — | 010–012 | — | 013–018 | 019–023 | — | 024–028 | 029–031 | 002–008 | — | 032–060 |
| `PAP` | 001–080 | 001–008 | 020–021 | — | 017–019 | — | — | — | 009–011 | 014–016 | 012–013 | 022–032 | — | —* | 033–080 |
| `COM` | 001–020 | 001–004 | — | — | — | — | — | — | — | — | — | — | — | — | 005–020 |
| `LOC` | 001–100 | 001–039 | — | — | — | — | — | — | — | — | — | — | — | — | 040–100 |
| `XCV` | 001–030 | — | — | — | — | — | — | — | — | — | — | — | — | 001–007 | 008–030 |

> `*`：`R/S2-BK-16`、`R/S4-PAP-01..05`、`R/S1-OFF-01` 为**同源复用**（直接沿用阶段1 全局 ID），映射后不占新号，故 BK/PAP 的 R 列无新段。
> 表中窗口为**预留上限**，实际分配以生成脚本按实体计数落位；**预留块间空位是硬要求**（便于后续补录不破坏既有号）。

### 1.4 规范信源记录 schema（`canonical-sources.json`）

```jsonc
{
  "namespace_version": "1.0.0",
  "generated": "2026-09-10",
  "total_entities": 0,
  "sources": [
    {
      "id": "BK-031",
      "category": "BK",
      "tier": "S2",
      "title": "The Twelve-Factor App",
      "en": "The Twelve-Factor App",
      "org": "Adam Wiggins (Heroku)",
      "year": "2011",
      "version": "Methodology (web)",
      "url": "https://12factor.net/",
      "doi": null,
      "status": "官方免费",
      "availability": "free-official",
      "priority": "必入",
      "verified": true,
      "confidence": "high",
      "review_date": "2026-09-10",
      "deprecated_at": null,
      "alias_ids": [
        { "package": "PHASE1", "id": "S2-BK-31" },
        { "package": "J", "id": "S2-01" },
        { "package": "PHASE1", "id": "L-BK-01" }
      ],
      "evidence_ref": ["D:运维-12Factor", "C:BK-01"],
      "provenance": ["J:J-deployment.json", "PHASE1:knowledge-map.json"]
    }
  ]
}
```

> `alias_ids` 是**全量旧 ID 的归宿**；任何旧引用都能经此反查，且 `stage4-data-model.md` 的节点 `sources[]` 只写 `id`（规范 ID）。

> **实际落点说明（2026-09-10 实测）**：本设计中的 `04-migration/...` 为阶段4 预留路径，**实际未创建**；`canonical-sources.json` 实际生成于 `03-knowledge-map/`（253 实体），迁移/建表脚本实际位于 `16-checkpoint/`（如 `build_canonical_sources.py`、`migrate_ids.py`、`gate_migration.py`），骨架/聚合脚本亦落 `16-checkpoint/`。本节 schema 设计保持不变，仅落点以此说明为准。

---

## 2. 重编号对抗策略（核心）

> 五道防线：**可生成 → 脚本改 → 门控验 → 可回滚 → 可重放**。任何一环缺失即不得声称迁移完成。

### 2.0 实体身份判定（迁移正确性的根）

**映射的唯一依据是"实体身份"，不是 ID 字符串。** 判定优先级：

1. **同 URL（去掉 query/fragment/`web.archive.org` 前缀归一化）** → 同实体；
2. **同 DOI** → 同实体；
3. **（标题 + 机构 + 年份）标准化后一致** → 同实体（人工确认兜底）；
4. 以上皆不同 → **不同实体**，各分配独立规范 ID（即使旧 ID 字符串相同，如 `I/S3-VEN-02` 与 `Q/S3-VEN-02`）。

`sources-index.md §2`（50 条复用映射）为**权威人工输入**，脚本以其为准，不得自行覆盖其结论。

### 2.1 防线一：生成 `old_id → canonical_id` 全量映射表

**工具**：`04-migration/scripts/build_canonical.py`

**输入**：`02-research/*.json` 的 `sources[]`、`03-knowledge-map/knowledge-map.json`、`03-knowledge-map/sources-index.md §2` 映射表。

**输出**：
1. `04-migration/canonical-sources.json`（§1.4，实体主表）；
2. `04-migration/old2new.json`（机器可读映射表）：

```jsonc
{
  "namespace_version": "1.0.0",
  "generated": "2026-09-10",
  "entries": [
    { "package": "I", "local_id": "S2-WEB-12", "canonical_id": "WEB-020",
      "entity_key": "url:https://martinfowler.com/bliki/TestPyramid.html",
      "action": "new", "collision": true,
      "note": "与阶段1 S2-WEB-12(Wikipedia 条目组)同名不同源" },
    { "package": "I", "local_id": "S2-BK-01", "canonical_id": "BK-001",
      "entity_key": "url:https://abseil.io/resources/swe-book", "action": "reuse",
      "collision": false, "note": "同源复用阶段1 S2-BK-01" },
    { "package": "Q", "local_id": "S3-VEN-02", "canonical_id": "VEN-002",
      "entity_key": "url:https://docs.aws.amazon.com/wellarchitected/...", "action": "new",
      "collision": true, "note": "与 I/S3-VEN-02(Google Testing Blog)同名不同源" }
  ],
  "reuse_edges": [],
  "collisions": []
}
```

3. `04-migration/collision-report.json`（§2.6）。

**完备性断言（脚本内置）**：`Σ entries(local_id)` == 各包 `sources[]` 数之和 + 阶段1 全局条目数；每个 `local_id` 恰好一条 entry；每条 entry 的 `canonical_id` 必存在于 `canonical-sources.json`。

### 2.2 防线二：脚本自动重写所有引用（禁止手改）

**工具**：`04-migration/scripts/rewrite_refs.py`（默认 `--dry-run`，写盘需显式 `--apply`）。

**重写原则**：

1. **禁止全局裸 ID 正则替换**（会误伤碰撞 ID）；
2. **包内自洽优先**：重写 `02-research/{P}-*.json` 时，用**该包自己的**映射（local → canonical），因为包内 ID 只在本包内有意义；
3. **聚合文档按上下文消歧**：`03-knowledge-map/*`、`01-alignment.md`、`report.*` 中的 ID 按以下**有序规则**匹配，命中即停：
   - 规则 R1：`包/ID`（如 `I/S2-BK-30`）→ 直接映射（无歧义）；
   - 规则 R2：表格行内 `来源包` 列非空时的裸 ID → 按该列包名映射；
   - 规则 R3：**全局唯一**裸 ID（如 `S1-STD-01`、`S2-BK-31`）→ 直接映射；
   - 规则 R4：仍歧义 → **不替换，写入 `ambiguity-report.json` 并中止该文件**（人工裁决后重跑）。
4. **保留 alias**：JSON 中每个 `sources[].id` 改写为规范 ID，同时新增 `canonical_id` 且把旧值移入 `legacy_id`；MD 中旧 ID 就地替换为规范 ID（旧值由映射表留存，不在正文双写）。
5. **引用字段全覆盖**：`sources[].id`、`definitions[].source_id`、`findings[].source_ids[]`、`evidence_ref[]`、任何 `R/S4-PAP-*` 形态。

**改写台账**：`04-migration/rewrite-ledger.jsonl`，每行一次替换：

```jsonc
{ "file": "02-research/I-testing.json", "line": 120, "old": "I/S2-BK-30",
  "new": "BK-055", "rule": "R2", "context_sha1": "…" }
```

**幂等要求**：连续运行两次，第二次 `git diff` 必须为空（规范 ID 不含旧形态，规则天然幂等；脚本以此自检）。

### 2.3 防线三：重写后门控校验

**工具**：`04-migration/scripts/gate_migration.py`（返回非零即失败）

| 检查 | 判据 | 阈值 |
|---|---|---|
| **引用零未解析** | 扫描所有产出中 `^(STD\|OFF\|BK\|WEB\|VEN\|PAP\|COM\|LOC\|XCV)-\d{3}$` 引用，逐一在 `canonical-sources.json` 存在 | 未解析 = 0 |
| **无旧 ID 残留** | 全目录正则搜旧形态 `S[1-4]-(STD\|OFF\|BK\|WEB\|VEN\|PAP\|COM)-?\d+`、`P-S[1-4]-`、`R-XC-` 在**非别名/非映射文件**中出现 | 残留 = 0 |
| **计数一致** | 每包 `sources[]` 长度迁移前后不变；`canonical-sources.json` 实体数 == distinct entity_key 数；`Σ alias_ids` == distinct 旧条目出现数 | 差值 = 0 |
| **编码纯净** | U+FFFD 数、BOM 数 | 均为 0；全部 JSON 可 `json.loads` |
| **映射完备** | 每个旧 ID 恰有一条 entry；无孤立 canonical（无 alias 指向） | 缺项 = 0 |
| **台账完整** | `rewrite-ledger` 替换数 == 源文中旧 ID 出现数（允许人工白名单注释） | 差额 = 0 |
| **碰撞全裁决** | `collision-report` 每条 `action` 已定 | 未裁决 = 0 |

**注意门控自身也要门控**：若门控报告"未解析数"与预期差距悬殊（如 65 vs 0），先怀疑**门控正则/排除逻辑**，而非交付物（经验教训：子串 `in` 做路径排除易误伤，改用精确路径判断）。

### 2.4 防线四：备份与回滚

**备份（迁移前强制）**：
1. `git commit -m "pre-id-migration snapshot"` 并打 tag `pre-id-migration`；
2. 对将被改写的文件生成 `.bak`：`cp X X.bak`（尤其 `02-research/*.json`、`03-knowledge-map/*`）；
3. 记录 `04-migration/backup-manifest.json`（文件路径 + SHA-256）。

**回滚**：
- 首选 `git reset --hard pre-id-migration`（整目录原子回滚）；
- 无 git 时：`for f in *.bak; do mv "$f" "${f%.bak}"; done` + 删除 `04-migration/` 新增产物；
- **回滚演练为验收项**（AC6）：apply → 校验 → rollback → 比对 SHA-256 与迁移前一致。

> `04-migration/` 全部为**新增目录**，回滚只需删除，不触碰被改写文件之外的内容。

### 2.5 防线五：分批 / 分文件执行与回执

按**文件组**分批，组间串行，组内可并行：

| 批次 | 范围 | 依赖 |
|---|---|---|
| B0 | 生成 canonical + old2new + collision-report | 无 |
| B1 | `02-research/*.json`（14 包，包内自洽） | B0 |
| B2 | `03-knowledge-map/knowledge-map.json` | B1 |
| B3 | `03-knowledge-map/sources-index.md`、`topic-source-matrix.md`、`glossary.md` | B2 |
| B4 | `00-plan/01-alignment.md`、`stage2-search-plan.md`、`report.md` | B3 |

**每批回执** `04-migration/receipts/{batch}.json`：

```jsonc
{ "batch": "B1", "files": 14, "replacements": 208, "unresolved": 0,
  "u_fffd": 0, "status": "pass", "gate_cmd": "python3 gate_migration.py --batch B1",
  "finished_at": "2026-09-10T20:00:00+08:00" }
```

**任一批 status != pass → 停止后续批次并回滚该批**。

### 2.6 碰撞处理（同 ID 指向不同源）

**裁决类型**：

| action | 触发 | 处理 |
|---|---|---|
| `duplicate_entity_merge` | 同实体（URL/DOI 一致） | 合并为 1 条，旧 ID 全入 `alias_ids`（如 `J/S2-01`+`S2-BK-31`→`BK-031`） |
| `same_id_diff_entity_split` | 同旧 ID 字符串、不同实体 | **各分配独立规范 ID**，`collision-report` 记录（见下表） |
| `rename` | 无碰撞的净新增 | 直接分配新号 |
| `manual_review` | 标题相近但 URL 不同、疑似同源 | 挂起人工裁决，未裁决前**不得进入 B1** |

**已确认必须 `split` 的碰撞（来自 `sources-index.md §5`）**：

| 碰撞 ID 字符串 | 实体 A → 规范 ID | 实体 B → 规范 ID | 判定 |
|---|---|---|---|
| `S2-BK-30` | 阶段1/`L`：Team Topologies → `BK-030` | `I`：Mike Cohn《Succeeding with Agile》→ 新 `BK-05x` | URL 不同，split |
| `S2-WEB-12` | 阶段1：Wikipedia 条目组 → `WEB-012` | `I`：Fowler Test Pyramid → 新 `WEB-0xx` | URL 不同，split |
| `S3-VEN-02..04` | `Q`：AWS/GCP/ThoughtWorks（3 实体） | `I`：Google Testing Blog / DORA / SonarQube（3 实体） | 6 实体共享 3 ID，**6 个独立规范 ID** |
| 裸 `S1-01/S2-01/S3-01/S4-01` | `G/H/J/K/L/N` 各自实体 | 同名不同源 | 全部按实体 split |
| `R/S4-PAP-01` | 阶段1 `S4-PAP-01` | （同实体） | **merge**，非 split |
| `R/S3-VEN-02`（若出现） | 注意与 Q/I 三方去重 | — | 人工确认 |

> 碰撞报告须给出每条的 `entity_key`（URL/DOI）作为证据，**不允许仅凭 ID 判断**。

### 2.7 工具链一览

| 工具 | 职责 | 关键参数 |
|---|---|---|
| `04-migration/scripts/build_canonical.py` | 建实体主表 + old2new + 碰撞报告 | `--root <MISSION_ROOT>` |
| `04-migration/scripts/rewrite_refs.py` | 脚本化改写引用 | `--dry-run`（默认）/`--apply` /`--batch B1..B4` |
| `04-migration/scripts/gate_migration.py` | 门控校验 | `--batch` /`--all` /`--check <name>` |
| `04-migration/scripts/rollback.sh` | 回滚 | `--tag pre-id-migration` |

---

## 3. 验收标准（"迁移成功"的可测量判据）

| 编号 | 判据 | 测量方法 | 通过阈值 |
|---|---|---|---|
| **AC1** | 映射完备 | `Σ entries` vs 各包 sources 计数 + 阶段1 条目 | 差值 = 0；每旧 ID 恰 1 entry |
| **AC2** | 引用零未解析 | `gate_migration.py --check refs` | 未解析 = 0 |
| **AC3** | 无旧 ID 残留 | 非映射文件全目录扫描旧形态 | 残留 = 0 |
| **AC4** | 计数一致 | 迁移前后每包 `sources[]` 长度比对 | 差 = 0；canonical 实体数 == distinct entity_key |
| **AC5** | 编码纯净 | U+FFFD / BOM / JSON 解析 | 全 0；JSON 全合法 |
| **AC6** | 可回滚 | apply → rollback 演练，比对 `backup-manifest` SHA-256 | 哈希全一致 |
| **AC7** | 碰撞全裁决 | `collision-report` 无 `manual_review` 未决项 | 未裁决 = 0 |
| **AC8** | 幂等 | 连续两次 `--apply` | 第二次 `git diff` 为空 |
| **AC9** | 回执齐全 | `receipts/*.json` 覆盖 B0–B4 | 全 `status=pass` |
| **AC10** | 图可消费 | `dag-schema.example.json` 中 `sources[]` 规范 ID 可在 `canonical-sources.json` 全部命中 | 命中率 = 100% |

> **迁移完成的单一判据**：AC1–AC10 **全绿**。任一未达标即视为未完成，不得进入阶段5 图谱生产。
> 全绿后，`canonical-sources.json` 成为**唯一信源真相**（single source of truth），旧映射表转为只读审计档案。

---

## 4. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| 碰撞 ID 被误合并 | 实体丢失、溯源断裂 | 实体身份判定（URL/DOI）优先；`same_id_diff_entity_split` 强制 |
| 聚合 MD 裸 ID 歧义 | 错改 | R4 规则：歧义即中止并要求人工裁决，**不猜** |
| 门控假阳性/假阴性 | 误判通过 | 门控自身先小样验证；精确路径排除（非子串 `in`） |
| 计数口径分歧 | 掩盖缺漏 | 冻结计数基准：阶段1=158 条、阶段2=208 条（**见下注**） |
| 回滚不彻底 | 二次污染 | 只新增 `04-migration/`；回滚 = git reset 或 `.bak` 还原 + 删新增 |
| 迁移后继续用旧 ID | 死灰复燃 | 门控 AC3 在阶段5 每次构建前重跑 |

> **计数基准注**：`report.md` 称"阶段2 12 包 / 256 源"，而 `sources-index.md §0` 统计为 **208**（F17+G17+H18+I33+J13+K12+L24+M13+N13=160，+P27+Q7+R14=48）。二者不一致（256 疑含阶段1 或误加）。**迁移前必须由主Agent 终裁唯一基准**（建议以 `sources-index.md §0` 的 208 为准，并修正 `report.md`），否则 AC1/AC4 失去参照。

---

## 5. 执行前置条件（gate to execute）

1. 本方案与 `stage4-data-model.md` 均通过评审；
2. `report.md` 计数口径已由主Agent 终裁并与 `sources-index.md` 对齐；
3. git 仓库可用且已提交 `pre-id-migration` 快照；
4. `04-migration/` 目录不存在（避免污染）；
5. 工具脚本已实现并通过 AC6 回滚演练的**空跑**。

> **本文件不含任何已执行的迁移动作**；未满足以上 5 条前，禁止运行 `rewrite_refs.py --apply`。
