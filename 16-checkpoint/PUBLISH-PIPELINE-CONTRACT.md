# PUBLISH-PIPELINE-CONTRACT · 公开仓装配流水线契约 v1.0

> 本文是「全量落地 P0+P1+P2」两名子Agent 的共享契约。**只读本文件，禁止复制全文进 prompt**。
> 生成：2026-09-11 ｜ 关联设计见会话内《以架构设计思路给出解决方案》+ `00-plan/stage2-book-collection.md §5`

## 0. 目标与两条核心原则

把 `_publish/`（公开仓）从「手工装配」改为「**声明式分区 + 唯一入口装配 + 可机检对账**」。

1. **单一入口**：只有一个脚本能写 `_publish/`（`assemble_publish.py`），规则只有一个来源（`publish-manifest.json`）。
2. **默认拒绝（fail-closed）**：MROOT 顶层任何条目若未被 manifest 显式声明，装配即 **FAIL**，绝不默认搬运。
3. **可机械派生（2026-09-11 追加）**：公开仓内**不得存在只能手工维护的变体**。任何「公开侧改写」都必须能由源侧经规则派生；若发现手工变体（如脚本里的本机路径字面量），应**逆向吸收回源侧**使其可派生，而不是把公开副本声明为例外。
4. **二进制需显式放行**：公开面出现的任何二进制（png/pdf/whatnot）必须在 `binary_allowlist` 显式声明，否则装配与 `--assert-clean` 均 FAIL。

## 1. 现状事实（已实测，供实现参考）

- MROOT 429MB；`_publish/` 28MB / 505 文件（505 tracked，无未跟踪）；`_publish-staging/` 3.3MB / 67 文件。
- 现行装配规则（逆向）：`_publish = mirror(8 目录) ∪ sanitize(4 目录 + 3 根文件)`，**无脚本、无声明**。
- 已知漂移（本次暴露）：`00-plan/contract.md`、`01-books/gap-request.md` 同名不同内容；`00-plan/stage2-book-collection.md` 只在 staging。
- `_publish/` **专有文件（必须保留，不得删除/覆盖）**：`LICENSE`、`README.md`、`.nojekyll`、`.gitignore`、`.github/`。
- `16-checkpoint/` **非纯镜像**：`merge_pilot.py`、`validate_pilot_merge.py` 为本地专用（公开仓没有）。
- 脱敏链：`audit_publish.py --emit` → `_publish-staging/`（含 2 个元文件 `AUDIT-REPORT.json`、`PUBLISH-MANIFEST.md`，**不发布**）。

## 2. 文件清单（唯一交付面）

| 文件 | 归属任务 | 性质 |
|---|---|---|
| `16-checkpoint/publish-manifest.json` | A | 新增（唯一规则来源） |
| `16-checkpoint/assemble_publish.py` | A | 新增（唯一装配入口） |
| `_publish/PUBLISH-STATE.json` | A（首次 `--apply` 时生成） | 生成物，随公开仓提交 |
| `16-checkpoint/gate_disclosure.py` | B | 新增（披露口径门控） |
| `16-checkpoint/disclosure-allowlist.txt` | B | 新增（豁免清单） |
| `00-plan/public-wording-policy.md` | B | 新增（公开文档措辞规范） |
| `_publish/.github/workflows/rebuild.yml` | B | 编辑（接入对账 + 披露门控 + 白名单导出） |

⛔ 任务 A **不得**执行 `--apply`（首次真实装配由主Agent 在复核 `--check` 报告后执行）。
⛔ 两任务均**不得** git commit / push；不得改 `_publish/` 下除上述文件外的任何内容。

## 3. `publish-manifest.json` schema

```json
{
  "version": "1.0",
  "root": ".",
  "staging_dir": "_publish-staging",
  "target_dir": "_publish",
  "classes": {
    "private":  ["01-books/_files/", "01-books/download-log.md", "01-books/acquired-manifest.json"],
    "never":    ["_publish/", "_publish-staging/", "_backup-idmigration/", "18-design/",
                 "16-checkpoint/_render-shots/", "__pycache__/", "ARCHIVE-INDEX.md", ".git/"],
    "preserve": ["LICENSE", "README.md", ".nojekyll", ".gitignore", ".github/",
                 "PUBLISH-STATE.json", "AUDIT-REPORT.json", "PUBLISH-MANIFEST.md"],
    "sanitize": ["00-plan/", "01-books/", "02-research/", "03-knowledge-map/",
                 "report.md", "report.html", "quality-gate.md"],
    "mirror":   ["11-node-pages/", "12-groups/", "13-interactive/", "14-views/",
                 "15-md/", "index.html", "20-agent-skill/"],
    "mask":     ["10-dag-data/",
                 {"path": "16-checkpoint/", "exclude": ["merge_pilot.py", "validate_pilot_merge.py", "_render-shots/"]}]
  },
  "binary_allowlist": ["00-plan/diagrams/"],
  "private_probe": ["01-books/_files", "download-log.md", "acquired-manifest.json"],
  "binary_exts": [".pdf",".epub",".mobi",".azw3",".djvu",".zip",".gz",".7z",".png",".jpg",
                  ".jpeg",".gif",".webp",".ico",".woff",".woff2",".ttf",".otf",".mp3",
                  ".mp4",".xlsx",".docx",".pptx"]
}
```

语义（**刚性**）：
- `private`：永不进入 `_publish`；命中 `private_probe` 一律 FAIL。
- `never`：本地专用，不搬运、不参与对账。
- `preserve`：公开仓专有，**既不写入也不删除**（装配器必须把它们排除在「删除多余」之外）。
- `sanitize`：来源 = `staging_dir/<rel>`（即 audit 脱敏产物）。staging 缺该文件 → FAIL（不可用未脱敏原文顶替）。
- `mirror`：来源 = MROOT 同路径**原样**复制（要求源侧已验证无本机路径）。
- `mask`：来源 = MROOT 同路径，**复制时对本机路径脱敏**（与 `audit_publish.py` 的 `HOME_PATH_RE`/`WIN_PATH_RE` 同源同规则，由 `import audit_publish` 复用；UTF-8 解码失败的文件按二进制原样复制）。实测：`10-dag-data` 3 文件与 `16-checkpoint/audit_publish.py` 在原实现中正是该变换的产物。
- **默认拒绝**：MROOT 顶层每个条目必须恰好被一个类覆盖；未被声明或重复声明 → FAIL 并列出条目名。
- `binary_allowlist`：显式放行的二进制路径前缀（如站点引用的示意图）；未列入者一律 FAIL。

## 4. `assemble_publish.py` CLI 契约

```
python3 16-checkpoint/assemble_publish.py --check            # 对账（只读）；有差异 exit 1
python3 16-checkpoint/assemble_publish.py --apply            # 装配（先预检，后落盘）
python3 16-checkpoint/assemble_publish.py --apply --dry-run  # 只打印计划，不写盘
python3 16-checkpoint/assemble_publish.py --check-public     # CI 模式：无 MROOT，仅用 target/PUBLISH-STATE.json 校验 target
python3 16-checkpoint/assemble_publish.py --export DIR       # 导出 Pages 白名单到 DIR
python3 16-checkpoint/assemble_publish.py --assert-clean DIR # 断言 DIR 无私有路径命中、无 binary_exts 文件
python3 16-checkpoint/assemble_publish.py --refresh-sanitize # 先跑 audit_publish.py --emit 再继续
```

**`--check` 输出三类差异**（每条给出相对路径）：
- `missing`：期望在 `_publish` 存在但缺失
- `extra`：在 `_publish` 存在但既非期望、也非 `preserve`（= 应删）
- `modified`：两边都有但内容不同

**`--apply` 流程（顺序不可变）**：
1. 解析 manifest → 计算期望集合（path → 来源）
2. **预检闸**（任一失败即中止，**不写任何字节**）：
   - P1 默认拒绝覆盖检查（顶层条目全覆盖）
   - P2 期望集合 `private_probe` 命中数 == 0
   - P3 期望集合内二进制必须全部落在 `binary_allowlist`（未声明即 FAIL）
   - P4 sanitize 类所需 staging 文件全部存在
   - P5 `preserve` 路径不进入期望集合
3. 落盘：写/覆盖期望文件 → 删除 `extra`（`preserve` 除外）
4. 生成 `_publish/PUBLISH-STATE.json`
5. 自检：内部重跑 `--check`，有差异则报 FAIL（exit 1）

**幂等性（刚性）**：产物中**不得含任何时间戳/随机量**；连续两次 `--apply` 后 `git -C _publish diff --exit-code` 必须为 0。

## 5. `PUBLISH-STATE.json` schema

```json
{
  "version": "1.0",
  "generated_by": "assemble_publish.py",
  "manifest_version": "1.0",
  "file_count": 0,
  "files": {
    "<relpath>": {"sha256": "...", "class": "mirror|sanitize", "src": "<MROOT 相对路径>", "src_sha256": "..."}
  },
  "forbidden": {"private_probe_hits": 0, "binary_files": 0}
}
```
- **禁止写入时间戳**（否则破坏幂等）。
- `--check-public` 用它做纯 target 侧校验：target 每个文件都在 `files` 中且 sha256 一致 → 否则 exit 1；`files` 中声明但磁盘缺失 → exit 1。

## 6. `gate_disclosure.py` 契约

- 扫描 target 内**文本类**文件（`.md/.html/.json/.txt/.yml/.yaml/.css/.js/.svg`），命中「披露口径」词表即 FAIL。
- 词表以「元组分片 + 运行时拼接」方式写在 `gate_disclosure.py` 常量里（脚本源文件不含任何禁用词的明文，避免自命中）；本文件不逐字复述词表，**以脚本常量为唯一真相源**。词表覆盖四类：①采集渠道/来源类 ②版权风险类 ③私密清单文件名类 ④境外镜像域名类。
- `16-checkpoint/disclosure-allowlist.txt`：每行一条 `相对路径 :: 单条豁免词` 或 `相对路径 :: *`；命中豁免即跳过。
- CLI：`--root DIR`（默认 `.`）、`--quiet`、`--json`；有命中 exit 1。
- 注意：脚本**自身**不得包含上述词（否则自检失败）；用转义/分片构造词表。

## 7. CI 变更（任务 B，仅改 `_publish/.github/workflows/rebuild.yml`）

在既有步骤**之后**、`Setup Pages` **之前**插入三步，并把上传路径改为白名单导出目录：

```yaml
      - name: Publish state reconciliation (public mirror vs PUBLISH-STATE.json)
        run: python3 16-checkpoint/assemble_publish.py --check-public

      - name: Gate — disclosure wording
        run: python3 16-checkpoint/gate_disclosure.py --root . --quiet

      - name: Build Pages artifact (whitelist export)
        run: |
          python3 16-checkpoint/assemble_publish.py --export .pages-export
          python3 16-checkpoint/assemble_publish.py --assert-clean .pages-export
```
并把 `actions/upload-pages-artifact` 的 `path: .` 改为 `path: .pages-export`。

## 8. 通则

- 编码：UTF-8 无 BOM；改文件优先用 `edit` 工具；禁止 `python -c` 内联管道写中文。
- 纯 stdlib（与 `16-checkpoint/` 既有风格一致，CI 只装 Python 3.12）。
- 每步实测留证（命令 + 输出），不臆断。
- 自查：JSON 合法性 + `python3 -m py_compile`；伪幂等测试（无时间戳即可复算一致）。
