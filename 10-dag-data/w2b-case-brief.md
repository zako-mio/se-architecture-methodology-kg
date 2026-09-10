# W2b 案例层批次简报（case 节点专用）

> 通用字段/边/纪律见 `10-dag-data/w1-production-brief.md`；本简报只列 case 层差异。
> 权威来源：`00-plan/stage5-build-contract.md`（§4.3 案例层规则、§7 版权红线）、`00-plan/stage4-data-model.md`（§2.5 cases[]、§4.4 case 列、GR-09/GR-13）。

---

## 1. case 节点字段差异

| 项 | case 节点规则 |
|---|---|
| `id` | `CAS-X-nn`（如 `CAS-X-01`；域位固定 `X`=跨域） |
| `type` | `"case"` |
| `layer` | **`null`**（案例不属三层） |
| `domain` | `"X"`（跨域） |
| `group` | `"GC-CASE"` |
| `stage` | `basic`/`intermediate`/`advanced` |
| `definition` | 15–300 字，一句话说明该案例是什么 |
| `detail` | `{principle, mechanism, engineering, tradeoff}`——**`tradeoff` 必填**（案例的取舍与代价，GR-13）；五段合计 1500–3000 字，单段 ≤600 |
| `sources` | 本地实战留档用 `LOC-*`（**必含本案例对应的 LOC id**，见分派单）；可追加相关 canonical 知识源 |
| `cross_cutting` | ⊆ `{"M","P","N","X"}`，≤3 |
| `verified`/`confidence`/`review_date` | `review_date="2026-09-10"` |
| `status` | `"active"` |
| `version`/`deprecated_at`/`superseded_by` | `null` |
| `case` | `[]`（案例节点自身不挂子案例） |
| `entry_links` | 本地留档**相对路径**或官方 URL（只放链接） |

## 2. 案例关系（`case_instance` 边）

- 每条 `case_instance` 边：`from` = 本案例节点 id，`to` = 既有知识节点 id（`ESS-*`/`MTH-*`/`TEC-*`），语义为「该案例**印证**或**违背**该知识点」。
- `type` = `"case_instance"`（**非硬依赖边**，不参与环检测）。
- 每个案例 **2–3 条** `case_instance` 边（印证为主，可含 1 条违背/张力）。
- 目标节点须在既有主图中存在（149 节点；可读 `10-dag-data/methodology-dag.json` 或 `10-dag-data/stats.md` 选点）。
- 主干节点的 `case` 字段与 `cases[]` 索引由 `aggregate.py` 在聚合时**自动回填/派生**，子Agent **不要**手改主干节点。

## 3. 版权红线

- 只放**链接与自研表述**；不复制书籍/源码正文；本地留档路径仅作 `entry_links`。

## 4. 自校验（返回前必须真跑）

```bash
python3 -c "import json;json.load(open('10-dag-data/_parts/{batch}.json',encoding='utf-8'))"
cd 16-checkpoint && python3 validate_graph.py --shard ../10-dag-data/_parts/{batch}.json --canonical ../03-knowledge-map/canonical-sources.json
```
要求 **errors=0**；另自检：`layer` 全为 `null`、`type` 全为 `case`、每案例 `tradeoff` 非空、每案例 2–3 条 `case_instance` 边、`sources` 全命中 canonical。
