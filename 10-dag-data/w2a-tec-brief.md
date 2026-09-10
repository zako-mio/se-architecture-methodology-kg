# W2a 技术层批次生产简报（technology 层专用）

> 通用字段/边/纪律见 `10-dag-data/w1-production-brief.md`；**本简报只列 technology 层差异**。
> 权威来源同前：`00-plan/stage5-build-contract.md`（§2.3/§2.6/§3.1/§4.3/§7）、`00-plan/stage4-data-model.md`（§2/§4.4）。

---

## 1. 层与技术节点差异

| 项 | technology 层规则 |
|---|---|
| `layer` | `"technology"` |
| `type` | `technology` 或 `tool`（本波用这两种） |
| `group` | `"GL-TECHNOLOGY"` |
| `version` | **必填**（`string`，语义化版本或发布标识，如 `Server 2026.4` / `2024-11` / `spec 2.0.0`）。**必须取自 canonical 源的标题/年份/版本字段**，不得杜撰 |
| `status` | `active` / `deprecated` / `superseded`（技术层生命周期） |
| `review_date` | `"2026-09-10"`（本轮采集日） |
| `deprecated_at` | `status=deprecated` 时填日期，否则 `null` |
| `superseded_by` | `status=superseded` 时填取代节点 id，否则 `null` |
| 正文 | 技术层**允许**出现工具名与版本号（与 essence 层相反） |
| `entry_links` | **只放官方文档/仓库 URL**（取自 canonical 源 `url` 字段） |

## 2. 边（technology 层关键）

- **层间边只允许 `implements`：`from` 必须是 technology 节点、`to` 必须是**既有 methodology 节点**（`MTH-*`），**单向**。
- **禁止** `technology → essence` 直连（越级）；若要关联本质层，只能经 methodology 中转。
- 技术层内可用 `supersedes`/`deprecated_by`（版本演化）、`combination`/`contrasts`/`conflicts`/`mitigates`。
- `case_instance`（案例→技术）本波不产。
- 硬依赖边 `{prerequisite,dependency,derives_from,refines}` 仍不得成环（本波技术批可只用 `implements` + 同层非硬边，避免引入环）。
- 每个技术节点**至少 1 条 `implements` 边**指向一个相关的既有 `MTH-*` 节点（可用主图锚点表）。

### 既有 methodology 锚点（`implements` 的目标，节选最相关）
- 实现/H：`MTH-H-01` 重构手法族 / `MTH-H-02` 信息隐藏模块化分解 / `MTH-H-03` 战略式编程 / `MTH-H-04` 代码复审与可读性治理
- 测试/I：`MTH-I-01` 测试层次 / `MTH-I-02` 测试类型 / `MTH-I-04` 测试金字塔 / `MTH-I-06` 质量门控与持续集成 / `MTH-I-07` 软件测试过程模型
- 部署/J：`MTH-J-01` 部署流水线 / `MTH-J-02` 发布工程 / `MTH-J-03` 封闭构建 / `MTH-J-05` 渐进暴露部署策略 / `MTH-J-06` 发布与部署解耦 / `MTH-J-07` 可回滚性
- 运维/K：`MTH-K-01` SLO 方法 / `MTH-K-02` 错误预算 / `MTH-K-03` 四大黄金信号 / `MTH-K-04` 可观测性信号关联 / `MTH-K-05` 事件响应复盘 / `MTH-K-06` 混沌工程 / `MTH-K-07` 容量与变更管理
- 架构/G：`MTH-G-01` ADR / `MTH-G-02` 质量属性场景与ATAM / `MTH-G-03` 架构风格选择 / `MTH-G-05` 架构文档化 / `MTH-G-06` 效用树与敏感点权衡点
- 演化/L：`MTH-L-01` 行为保持重构 / `MTH-L-02` 坏味道启发式 / `MTH-L-04` 演进式架构 / `MTH-L-05` 架构适应度函数 / `MTH-L-07` 弃用与日落策略
- 质量/M：`MTH-M-01` 质量属性战术映射 / `MTH-M-04` 质量模型应用 / `MTH-M-05` 可维护性评估
- 通用：`MTH-N-05` DORA 指标 / `MTH-O-11` 度量与反馈闭环 / `MTH-O-03` 技术选型够用原则

## 3. 版权红线（技术节点尤其关键）

- **只引官方公开文档链接**（厂商 docs、标准官方页、官方开源仓库），`entry_links` 存 URL，**不复制正文**。
- 一律改写为自研表述；短引用须注明出处并控制篇幅。
- 不下载受版权保护全文入库。

## 4. 自校验（返回前必须真跑）

```bash
python3 -c "import json;json.load(open('10-dag-data/_parts/{batch}.json',encoding='utf-8'))"
cd 16-checkpoint && python3 validate_graph.py --shard ../10-dag-data/_parts/{batch}.json --canonical ../03-knowledge-map/canonical-sources.json
```
要求 **errors=0**。另须用脚本自检：
- 每个技术节点 `version` 非空 / `status` / `review_date` 齐全；
- 每个技术节点**至少 1 条 `implements` 边**且方向为 tech→methodology（目标为既有 `MTH-*`）。
