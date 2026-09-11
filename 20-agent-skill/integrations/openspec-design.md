# openspec `design` 工件 · 架构门控集成契约

> 定位：把「方案设计 = 门控级」落到日常 openspec 开发流。
> 由行为层 `instructions/architecture-behavior.md` 全局触发；本文件是可执行细节契约。
> 强度：**强制**（`gate_architecture.py` PASS 前不得定稿 `design.md`）。

## 1. 触发条件

- 任务**生成或修改** openspec 的 `design` 工件时触发（`design` 为可选工件；其存在即视为架构相关）。
- 覆盖全部入口：`openspec-propose` / `openspec-new-change` / `openspec-continue-change` /
  `openspec-ff-change` / `openspec-update-change` 等任何产生 `design` 的路径。
  （触发器在**行为层**，不依赖对某个 openspec skill 的改动 —— 避免被 `openspec update` 覆写。）

## 2. 动作序列

1. 加载 `architecture-judgment` skill，按其 `workflow.md` 4 步执行（判类型 → 读速查 → 深链 → 产出 + 自检）。
2. 委派 `architect-worker` 产出：
   - `ADR`（必选）：落 `<change>/adr/ADR-xxx.json`（机检件）+ `ADR-xxx.md`（人读件）；
   - 多维权衡矩阵（涉选型时）：落 `<change>/adr/matrix.md`。
3. `design.md` 中引用同 change 下的 ADR（相对路径），并简述决策结论与命中的图谱场景/节点。

## 3. 门控（强制，不通过不放行）

```bash
python3 <SKILL>/_private/gate_architecture.py --kind adr \
  --input <change>/adr/ADR-xxx.json
# schema / graph 自动解析；亦可显式 --schema / --graph
```

- **PASS（退出码 0）** → 允许写入 / 定稿 `design.md`。
- **FAIL（退出码 1）** → 把门控输出回传 `architect-worker` 修正，**最多 2 轮**；仍不过则如实报告失败与原因，**不得降级为"口头通过"**。
- ⛔ **PASS 之前不得定稿 `design.md`**（"强制"的可达上限：openspec 为外部 CLI，由行为层明令 + 门控证据约束）。

## 4. 留档（双落）

- `change/adr/` 为**权威件**（随 change 自包含，`design.md` 相对引用）。
- 任务结束时，把 `change/adr/` 复制一份到**任务留档目录**（本机归档约定；按 `{YYYY-MM}/{MMDD-任务名}/adr/` 组织）。

## 5. 边界与不做

- 不修改 openspec 包，也不直接改其生成的 `openspec-*` skill（会被 `openspec update` 无条件覆写）。
- 不用 `openspec schema fork`（快照会随上游 schema 漂移；留待阶段 3 视需要评估）。
- 架构图不在本契约内产出；如需，由主 Agent 另委 `drawio-worker`（prompt 必含 `drawio-reference: 图表规范与导出验证`）。

## 6. 验证要点（供回归）

- 新建 change → design 阶段 → 产 `adr/ADR-xxx.json` → 跑 `--kind adr` → 输出 PASS/FAIL。
- 反例：ADR 缺字段 / 单备选 / 悬挂引用 / `TEC-` 越位 → 门控必须 FAIL。
