# 契约：0910-软件工程架构方法论（阶段1）

> 本文件是阶段1所有子Agent 的共享契约。子Agent 只读本文件，禁止复制全文进 prompt。

## 0. 任务定位

- 母任务：建立「软件工程 / 架构设计方法论」知识库（最终母库，纳入 12factor 等既有库知识）。
- **本阶段（阶段1，Build）**：权威源初搜 + 本地查找 → 产出「思路对齐文档 + 权威知识地图 + 阶段2计划书」。
- 不做：不建库、不写生成脚本、不下结论性架构设计（阶段4 才做）。

## 1. 路径约定（MISSION_ROOT）

```
MISSION_ROOT = ~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论
├── 00-plan/        # 契约、阶段2计划书、路线图
├── 01-books/       # 书籍候选清单与可得性
├── 02-research/    # 阶段1证据包（本阶段子Agent 主产出）
└── 03-knowledge-map/ # 权威知识地图（信源分级清单）
```

## 2. 命名规范

- 文件：`{字母}-{主题}.{ext}`，如 `A-se-definition.json` / `A-se-definition.md`
- 语言：**中文为主**，保留英文标准名与术语原名（如 SWEBOK、ISO/IEC/IEEE 42010）。
- 编码：UTF-8 无 BOM；禁止写入替换字符（U+FFFD）。

## 3. 信源分级（只收 S1/S2，S3/S4 作补充）

| 级别 | 内容 | 示例 |
|---|---|---|
| **S1** | 国际标准 / 官方知识体系 | SWEBOK、ISO/IEC/IEEE 12207、ISO/IEC/IEEE 42010、ISO/IEC 25010、SEI、ACM/IEEE CS Curricula |
| **S2** | 经典著作（作者博客 / 官方章节 / 公开演讲；书本体仅本地语料层） | Clean Architecture、A Philosophy of Software Design、DDD、Refactoring、DDIA、Software Engineering at Google |
| **S3** | 官方厂商架构中心 | Microsoft Azure Architecture Center、AWS Well-Architected、Google Cloud、ThoughtWorks Tech Radar |
| **S4** | 学术论文 | ICSE / FSE / TSE / EMSE |

**禁止**：无出处的二手博客、AI 生成内容、营销软文。每条事实必须可溯源。

## 4. 产出格式

### 4.1 证据包 JSON（02-research/*.json）

```json
{
  "topic": "主题名",
  "generated_by": "agent-role",
  "sources": [
    {"id":"S1-01","title":"","org":"","year":"","url":"","tier":"S1","verified":true,"key_points":["",""]}
  ],
  "definitions": [
    {"term":"","definition":"","source_id":"S1-01"}
  ],
  "findings": [{"claim":"","source_ids":["S1-01"],"confidence":"high|medium|low"}],
  "gaps": [""],
  "notes": ""
}
```

### 4.2 摘要 MD（02-research/*.md）

每个证据包配一份 300-800 字中文摘要，含：核心结论、关键信源、未决问题。

## 5. 版权红线（刚性）

- **私有语料层**：`01-books/_files/`（书籍/标准正文、结构层快照）及其清单 `01-books/download-log.md`、`01-books/acquired-manifest.json`。这是**唯一**允许存放书籍本体的位置。
- **公开仓库**只承载「纳入、消化、重组后的知识与方法论」+ 我们自己的脚本，**永不承载书籍/标准正文**。
- **三层强制隔离**（全部可机检，非口头约定）：
  1. 本地仓 `.gitignore` 排除 `01-books/_files/` 与上述两个清单；
  2. 公开仓 `_publish/.gitignore` 同样排除；
  3. 装配层 `16-checkpoint/audit_publish.py` 的 `HARD_EXCLUDE_PREFIXES` 使这些路径**连扫描都不进入**（`--scan` 会报 `hard_excluded.files_skipped`），从源头杜绝二进制语料被 `--emit` 原样复制进 `_publish-staging/`。
- **复核命令**：两仓各跑 `git check-ignore -v 01-books/download-log.md`；装配层跑 `python3 16-checkpoint/audit_publish.py --scan`（要求 `_files/` 命中数为 0、`hard_excluded.files_skipped` 与磁盘实际数一致）。
- 子Agent 不得把书籍/标准正文写入 `_publish/`、`_publish-staging/` 或任何公开交付目录。

## 6. 证据纪律

- 每条 finding 必须带 source_ids；无源不写。
- 一手源（标准原文、官方页面）优先于二手转述。
- 无法核验的写进 `gaps`，不伪装成事实。
- 联网优先直连国内可达源；境外被墙站点用 `curl -x http://172.29.0.1:7890 <url>`。

## 7. 返回格式（所有子Agent）

```json
{"status":"success|partial|failed","summary":"200字以内","data":{},"files_created":[],"files_modified":[],"decisions":[],"warnings":[],"errors":[]}
```
