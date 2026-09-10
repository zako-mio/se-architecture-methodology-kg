# W1 批次生产简报（子Agent 通用操作契约）

> 权威来源：`00-plan/stage5-build-contract.md`（§〇.1 实现现状 / §二 节点契约 / §三 边规则 / §五 落盘纪律 / §七 版权红线）
> 与 `00-plan/stage4-data-model.md`（§2 字段表 / §4.2 GR 规则 / §4.3 正则 / §4.4 必填矩阵）。
> 本简报是其**操作摘要**；如有出入，以两文件为准。子Agent 须先 `read` 上述两文件的对应章节，再按本简报作业。

---

## 1. 输出（唯一文件，先落盘再返回）

- 文件：`10-dag-data/_parts/{batch_id}.json`
- 结构：
```jsonc
{
  "batch_id": "W1-X", "wave": "W1", "domain": "X",
  "layers": ["essence", "methodology"],
  "produced_by": "<role>", "generated": "2026-09-10",
  "nodes": [ /* 8–12 个 */ ],
  "edges": [ /* 见 §3 */ ]
}
```
- **只写这一个文件**；严禁改 `methodology-dag.json`、`_base.json`、其他 `_parts/*`、`00-plan/`、`02-research/`、`03-knowledge-map/`。

## 2. 节点字段（逐项照 stage4-data-model.md §2/§4.4）

必填：`id` `name` `en` `aliases` `type` `subtype` `group` `layer` `domain` `stage` `priority` `definition` `detail{principle,mechanism,engineering,tradeoff}` `cross_cutting` `case` `sources` `verified` `confidence` `review_date` `status` `version` `deprecated_at` `superseded_by` `tags` `entry_links` `errata`

| 字段 | 取值/约束 |
|---|---|
| `id` | `^(ESS\|MTH\|TEC\|CAS)-[A-Z]{1,2}-\d{2}$`；本批前缀见分派单 |
| `name` | 中文 2–20 字，同域内唯一 |
| `type` | essence 层→`principle`（或 `bridge`）；methodology 层→`method`（或 `bridge`） |
| `group` | essence→`"GL-ESSENCE"`；methodology→`"GL-METHOD"` |
| `layer` | `"essence"` / `"methodology"`（本波不含 technology） |
| `domain` | 本批域代码 |
| `stage` | `basic`/`intermediate`/`advanced` |
| `priority` | `P0`/`P1`/`P2`/`P3` |
| `definition` | 15–300 字符，一句话单一主张 |
| `detail.*` | **单段 ≤600 字符**（GR-04）；`definition`+四段 **合计 1500–3000 字**（GR-11） |
| `detail.tradeoff` | **必填且非空**（GR-12 原则节点强制 / GR-13 全节点）；建议同时给 `errata` 反例 |
| `cross_cutting` | 数组 ⊆ `{"M","P","N","X"}`，≤3 个，可 `[]` |
| `case` | `[]` |
| `sources` | **1–8 个 canonical id**，必须命中 `03-knowledge-map/canonical-sources.json`；优先取本域证据包 `sources[].id` |
| `verified` | `true`/`false`/`"cited"` |
| `confidence` | `high`/`medium`/`low` |
| `review_date` | `"2026-09-10"` |
| `status` | `"active"` |
| `version` | `null` |
| `deprecated_at` | `null` |
| `superseded_by` | `null` |
| `entry_links` | 只放官方 URL（可选） |

- **层边界**：`essence` 层正文**不得出现任何工具名与版本号**；`methodology` 层不绑具体版本。
- **版权红线**：不复制标准/书籍正文，一律改写自研表述；不下载受版权保护全文。

## 3. 边

- 字段：`{id, from, to, type, label(中文≤40字), sources:[...]}`；`from`/`to` 须可解析（本批节点或既有主图节点）。
- `id` 形如 `E-\d{2,3}`，用本批**指定块**（不得越界）。
- 允许类型：`prerequisite` / `dependency` / `refines` / `derives_from`(**method→essence 单向**) / `contrasts` / `conflicts` / `combination` / `enables` / `mitigates` / `case_instance`。
- **层间边只允许** `derives_from`（methodology→essence，方向必须正确）；同层跨域用 `prerequisite`/`dependency`/`refines`。
- 硬依赖边 `{prerequisite,dependency,derives_from,refines}` **不得成环**。
- 建议：essence 组内 3–6 条；methodology→essence 2–5 条；methodology 组内 2–5 条。

## 4. 自校验（返回前必须真跑并贴输出）

```bash
python3 -c "import json;json.load(open('10-dag-data/_parts/{batch}.json',encoding='utf-8'))"
cd 16-checkpoint && python3 validate_graph.py --shard ../10-dag-data/_parts/{batch}.json --canonical ../03-knowledge-map/canonical-sources.json
```
要求 **errors=0**；跨分片端点（指向既有主图节点）显示为 `EDGE_ENDPOINT_EXTERNAL` 属**预期 warning**，须在回执列明。

## 5. 编码安全

- 写文件用 `write`/`edit` 工具（UTF-8 安全）；**禁止** `python -c` 内联管道写中文；如需脚本，写成独立 `.py` 再执行。
- 写完必须验证 JSON 合法 + 无 U+FFFD。

## 6. 返回格式

```json
{"status":"success|partial|failed","summary":"200字以内","data":{"batch_id":"...","node_count":N,"essence_count":N,"methodology_count":N,"edge_count":N,"self_check":{"json":"OK","validate_graph_errors":0,"validate_graph_warnings":[],"acyclic":true}},"files_created":["<绝对路径>"],"files_modified":[],"decisions":[],"warnings":[],"errors":[]}
```
