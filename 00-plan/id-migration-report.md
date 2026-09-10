# 信源统一 ID 迁移 · 执行回执（id-migration-report.md）

> 母任务：0910-软件工程架构方法论 · 阶段4
> 依据：`00-plan/id-migration-plan.md`（迁移方案与对抗策略）、`03-knowledge-map/sources-index.md`、`02-research/*.json`
> 执行日期：2026-09-10　执行者：数据迁移工程师（子 Agent）
> 状态：**迁移完成，全部门控通过（FAIL=0）**

---

## 1. 结论摘要

| 指标 | 数值 |
|---|---|
| 映射条目（old_id × source_pack） | **414** |
| 规范实体（canonical entities） | **253** |
| 迁移 `sources[].id` | 414 |
| 迁移引用（`source_id` / `source_ids[]` / `sources[]`） | 1346 |
| 新增 `legacy_id` | 414（100% 覆盖，旧 ID 全部留痕） |
| 引用未解析数 | **0** |
| 门控 FAIL / WARN | **0 / 0** |
| 回滚演练 | 通过（哈希全一致） |
| 重放确定性 | 通过（rollback→apply 后字节级哈希一致） |

规范命名空间：`STD / OFF / BK / WEB / VEN / PAP / COM / LOC / XCV` - `{3 位序号}`。

---

## 2. 产出物

| 类型 | 路径 |
|---|---|
| 映射表 | `00-plan/id-mapping.json` |
| 迁移脚本 | `16-checkpoint/migrate_ids.py` |
| 映射构建脚本 | `16-checkpoint/build_mapping.py` |
| 门控脚本 | `16-checkpoint/gate_migration.py` |
| 变更台账 | `16-checkpoint/migration-ledger.json` |
| 备份清单（SHA-256） | `16-checkpoint/backup-manifest.txt` |
| 备份目录 | `_backup-idmigration/{02-research,03-knowledge-map}/` |
| 本回执 | `00-plan/id-migration-report.md` |

被修改文件（16 个，均在备份内）：`02-research/{A,B,F,G,H,I,J,K,L,M,N,O,P,Q,R}-*.json` 14 个 + `03-knowledge-map/knowledge-map.json`。
**未触碰**：`report.md`、`00-plan/stage4-data-model.md`、`00-plan/stage4-architecture-design.md` 及所有设计文档正文。

---

## 3. 实体身份判定（迁移正确性根因）

按 `id-migration-plan.md §2.0` 三级判定，**不以旧 ID 字符串为准**：

1. **权威人工输入**：`sources-index.md §2` 的 70 条跨包复用边（脚本以 union-find 采信，不得覆盖）；
2. **阶段1 原始包归属**：`knowledge-map.json` 的 `evidence_ref` 反查出 A/B 包局部 ID → 阶段1 全局条目；多候选时以规范化 URL 消歧，仅 2 处人工覆写（`A/S4-04→S4-PAP-01`、`B/S1-03→S1-OFF-02`）；
3. **同 URL / 同 DOI 归并**：仅用于**阶段2 净新增实体**，且设"禁止桥接两个含 PHASE1 的分量"护栏——防止 `S4-PAP-04` 与 `R-XC-05`（同指向 Wikipedia Waterfall，但一为论文、一为百科交叉验证）经阶段2 节点被错误合并。

> 实体键写入映射表 `entity_key`（`url:` / `doi:` / `title+org+year:`）。

---

## 4. 映射统计

### 4.1 按来源包（entries）

| 包 | PHASE1 | A | B | F | G | H | I | J | K | L | M | N | P | Q | R |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 条目 | 158 | 21 | 27 | 17 | 17 | 18 | 33 | 13 | 12 | 24 | 13 | 13 | 27 | 7 | 14 |

> PHASE1=158 为 `knowledge-map.json` 实际 `sources[]` 数（已含合并入内的 P/R/S3-VEN 条目）；阶段2 12 包合计 208；A/B 48。总计 414。

### 4.2 按动作

| action | 数量 | 含义 |
|---|---:|---|
| `rename` | 105 | 单旧 ID → 规范 ID（净新增或直接重编号） |
| `merge` | 160 | 多旧 ID 同实体 → 同一规范 ID（跨包复用） |
| `collision_split` | 149 | 同形旧 ID 跨包指向不同实体，拆分到不同规范 ID |

### 4.3 按类别（实体数）

| STD | OFF | BK | WEB | VEN | PAP | COM | LOC | XCV |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 28 | 25 | 38 | 45 | 39 | 28 | 4 | 39 | 7 |

---

## 5. 碰撞裁决记录

共识别 **38 组** `same_id_diff_entity_split` 碰撞（同形旧 ID 跨包指向不同实体，各分配独立规范 ID）。核心裁决（与 `sources-index.md §5` 对齐，均以 URL/DOI 为证据，未凭 ID 判断）：

| 旧 ID | 实体 A → 规范 | 实体 B → 规范 | 判定 |
|---|---|---|---|
| `I/S2-BK-30`（Mike Cohn） vs `PHASE1/S2-BK-30`（Team Topologies） | `BK-038` | `BK-030` | URL 不同，split |
| `I/S2-WEB-12`（Fowler Test Pyramid） vs `PHASE1/S2-WEB-12`（Wikipedia 条目组） | `WEB-024` | `WEB-012` | URL 不同，split |
| `I/S3-VEN-02`（Google Testing Blog） vs `Q|PHASE1/S3-VEN-02`（AWS WAF） | `VEN-017` | `VEN-002` | 同 ID 三源，split |
| `I/S3-VEN-03`（DORA） vs `Q|PHASE1/S3-VEN-03`（AWS WAF 白皮书） | `VEN-018` | `VEN-003` | split |
| `I/S3-VEN-04`（SonarQube） vs `Q|PHASE1/S3-VEN-04`（GCP WAF） | `VEN-019` | `VEN-004` | split |

其余 33 组为 §5.1 所述"跨包裸数字 ID"（`S1-01`、`S2-01`、`S3-01`、`S4-01` 等在 A/B/G/H/J/K/L/N 各指不同信源）。**合并（同实体）不在此列**，如 `J/S2-01`=`PHASE1/S2-BK-31`=`L-BK-01`→`BK-031`、`R/S4-PAP-01`=`PHASE1/S4-PAP-01`→`PAP-001`、`R/R-XC-03`=`F/S1-F04`→`OFF-xxx`。

---

## 6. 门控校验结果（实测）

```
$ python3 16-checkpoint/gate_migration.py
== 门控结果 ==
映射条目: 414 | 规范实体: 253
FAIL: 0
WARN: 0
ALL GATES PASS
exit=0
```

逐项：

| 检查 | 判据 | 结果 |
|---|---|---|
| G1 JSON 合法 | 16 文件均 `json.loads` 成功 | PASS |
| G2 引用零未解析 | `source_id`/`source_ids[]`/`sources[]` 值均为规范 ID 且存在于 canonical 集 | 未解析 = **0** |
| G3 编码纯净 | 无 U+FFFD / 无 BOM / 无空文件 | PASS |
| G4 计数一致 | 每包 `sources[]` 迁移前后条数比对 | 差 = **0**（16/16 一致） |
| G5 映射完备 | 备份中每个 `(pack, old_id)` 均有映射条目 | 缺项 = **0**（414/414） |
| G6 无旧 ID 残留 | `sources[].id` 及引用字段无旧形态 ID | 残留 = **0** |

引用解析明细（`unresolved` 全为 0）：

| 包 | A | B | F | G | H | I | J | K | L | M | N | O | P | Q | R | PHASE1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| refs | 48 | 49 | 42 | 73 | 81 | 41 | 74 | 86 | 101 | 74 | 55 | 320 | 106 | 40 | 33 | 123 |
| 包内解析 | 48 | 49 | 42 | 73 | 81 | 41 | 74 | 86 | 101 | 74 | 55 | 0\* | 106 | 40 | 33 | 123 |
| 未解析 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

\* O 包（方法论综合包，`sources` 为空）的 320 条 `source_ids` 全部为**跨包限定引用**（`A:S1-01`、`H:S2-01`、`I:S2-BK-01` …），迁移后全部解析为其规范 ID，无未解析。

### 6.1 幂等（AC8）

`--apply` 后再次运行：`{"ids_rewritten":0,"refs_rewritten":0,"legacy_added":0}`，`unresolved:0`。

---

## 7. 回滚方法与演练（AC6）

**备份**：迁移前将全部待改文件按相对路径复制到 `_backup-idmigration/`，并记录 SHA-256 于 `16-checkpoint/backup-manifest.txt`。

**回滚命令**（本目录无 git，采用文件还原）：

```bash
cd <MISSION_ROOT>
cp -p _backup-idmigration/02-research/*.json            02-research/
cp -p _backup-idmigration/03-knowledge-map/knowledge-map.json 03-knowledge-map/
# 校验还原一致性
(cd _backup-idmigration && find . -type f | sort | xargs sha256sum) | diff - <(sort 16-checkpoint/backup-manifest.txt)
```

**演练实测**（本轮执行）：

1. apply → 记录 16 文件迁移后 SHA-256；
2. `cp -p` 还原全部备份 → 与 `backup-manifest.txt` **哈希全一致**；
3. 重新 `migrate_ids.py --apply` → 再取哈希 → 与步骤 1 **逐字节一致**（重放确定性）。

> 回滚 = 还原备份 + 删除新增产物（`00-plan/id-mapping.json`、`00-plan/id-migration-report.md`、`16-checkpoint/`）；不改动被迁移文件之外内容。

---

## 8. 关键决策与已知边界

1. **不裸正则全局替换**：全程按 `(source_pack, old_id)` 与 `PKG:old_id` 精确查表替换，同形碰撞 ID（如 `S3-VEN-02` 在 I 与 Q）分别命中各自条目，未发生误伤。
2. **`legacy_id` 全量留痕**：每个 `sources[]` 条目新增 `legacy_id` 保留原始 ID；`id` 改为规范 ID。旧→新全量映射另存于 `id-mapping.json`。
3. **`evidence_ref` 未改写**（有意）：`knowledge-map.json` 的 `evidence_ref` 是 A–E 原始证据包的**溯源字段**，取值高度异构（`D:通论-SE@Google`、`C:KG-01`、`E:42010-2022`、`Q:VEN-02`、`task-required`），并非 `sources[].id` 引用。按任务范围（`sources[].id` 与 `source_ids` 引用）未动，避免破坏溯源。若后续要求 AC3 全目录零旧形态，可另立映射针对该字段做一次性改写。
4. **类别由"载体性质"判定**：阶段1 条目按原前缀映射；阶段2 净新增按 tier + 机构/出版商/DOI 启发式归类。少数边界（RFC、在线章节、从业者站点）的 `BK/WEB/STD/OFF` 归属为主观，**不影响引用解析与迁移正确性**（规范 ID 稳定、确定性），后续可按需微调编号。
5. **范围**：`C-local-inventory.json`、`E-iso-standards.json` 无信源 ID 引用（其 `sources` 为 URL 快照列表），未改；`O-methodology.json` 仅含跨包 `source_ids`，一并迁移；`report.md` 与设计文档正文遵约束未改。
6. **计数基准**：`report.md`（256）与 `sources-index.md §0`（208）口径不一致的问题仍在（本任务禁止改 `report.md`）。本迁移以**各文件 `sources[]` 实际条数为冻结基准**（备份留痕，G4 逐包比对），不受口径分歧影响。

---

## 9. 复核清单

- [x] 414 条 old_id 全部有映射，无遗漏
- [x] 253 个规范实体，命名空间合法
- [x] 1346 条引用全部解析，未解析 = 0
- [x] `sources[]` 条数迁移前后一致
- [x] 无 U+FFFD / BOM / 空文件；JSON 全合法
- [x] 幂等、回滚、重放确定性均通过
- [x] `legacy_id` 100% 留痕
- [x] 碰撞全裁决（38 组，0 未决）

*本回执由迁移脚本与门控脚本的实际输出生成，所有数字均可由 `16-checkpoint/gate_migration.py` 复现。*
