# 决策矩阵摘要 · 域 × 层 × 横切主题

> 派生自视图 `14-views/03-decision-matrix.html`（同源 DAG `10-dag-data/methodology-dag.json`）。
> 用途：按生命周期域与层系统排查覆盖，并在横切主题上核对是否遗漏。
> 节点名/id 对照见 `node-index.md`；深链模板 `.../11-node-pages/<ID>.html`。

## §1 生命周期域 × 层 落点矩阵

| 域 | 本质层 essence | 方法论层 methodology | 技术实践层 technology |
|---|---|---|---|
| F 概念与需求（13） | `ESS-F-01` `ESS-F-02` `ESS-F-03` `ESS-F-04` `ESS-F-05` | `MTH-F-01` `MTH-F-02` `MTH-F-03` `MTH-F-04` `MTH-F-05` `MTH-F-06` | `TEC-F-01` `TEC-F-02` |
| G 架构设计（17） | `ESS-G-01` `ESS-G-02` `ESS-G-03` `ESS-G-07` `ESS-G-04` `ESS-G-05` `ESS-G-06` | `MTH-G-05` `MTH-G-06` `MTH-G-01` `MTH-G-02` `MTH-G-03` `MTH-G-04` | `TEC-G-01` `TEC-G-02` `TEC-G-03` `TEC-G-04` |
| H 实现与构造（16） | `ESS-H-01` `ESS-H-02` `ESS-H-03` `ESS-H-04` `ESS-H-08` `ESS-H-09` `ESS-H-05` `ESS-H-06` `ESS-H-07` | `MTH-H-03` `MTH-H-04` `MTH-H-01` `MTH-H-02` | `TEC-H-01` `TEC-H-02` `TEC-H-03` |
| I 测试（14） | `ESS-I-01` `ESS-I-02` `ESS-I-03` `ESS-I-04` | `MTH-I-01` `MTH-I-02` `MTH-I-03` `MTH-I-04` `MTH-I-05` `MTH-I-06` `MTH-I-07` | `TEC-I-01` `TEC-I-02` `TEC-I-03` |
| J 部署（17） | `ESS-J-01` `ESS-J-02` `ESS-J-03` `ESS-J-04` | `MTH-J-01` `MTH-J-02` `MTH-J-03` `MTH-J-04` `MTH-J-05` `MTH-J-06` `MTH-J-07` | `TEC-J-01` `TEC-J-02` `TEC-J-03` `TEC-J-04` `TEC-J-05` `TEC-J-06` |
| K 运维（17） | `ESS-K-01` `ESS-K-02` `ESS-K-03` `ESS-K-04` | `MTH-K-01` `MTH-K-02` `MTH-K-03` `MTH-K-04` `MTH-K-05` `MTH-K-06` `MTH-K-07` | `TEC-K-01` `TEC-K-02` `TEC-K-03` `TEC-K-04` `TEC-K-05` `TEC-K-06` |
| L 演化与弃用（14） | `ESS-L-01` `ESS-L-02` `ESS-L-03` `ESS-L-04` `ESS-L-05` | `MTH-L-01` `MTH-L-02` `MTH-L-03` `MTH-L-04` `MTH-L-05` `MTH-L-06` `MTH-L-07` | `TEC-L-01` `TEC-L-02` |
| M 质量属性（14） | `ESS-M-01` `ESS-M-02` `ESS-M-03` `ESS-M-04` `ESS-M-05` | `MTH-M-01` `MTH-M-02` `MTH-M-03` `MTH-M-04` `MTH-M-05` `MTH-M-06` | `TEC-M-01` `TEC-M-02` `TEC-M-03` |
| N 团队与康威（13） | `ESS-N-01` `ESS-N-02` `ESS-N-03` `ESS-N-04` `ESS-N-05` | `MTH-N-01` `MTH-N-02` `MTH-N-03` `MTH-N-04` `MTH-N-05` `MTH-N-06` | `TEC-N-01` `TEC-N-02` |
| O 方法论主干（14） | `ESS-O-01` `ESS-O-02` `ESS-O-03` | `MTH-O-01` `MTH-O-02` `MTH-O-03` `MTH-O-04` `MTH-O-05` `MTH-O-06` `MTH-O-07` `MTH-O-08` `MTH-O-09` `MTH-O-10` `MTH-O-11` | —（O 域无技术实践节点） |
| X 跨域/案例（18） | — | — | —（仅案例 `CAS-X-01`…`CAS-X-18`） |

读数提示：本质层给判据、方法论层给过程、技术实践层给可替代工具；O 域（主干）只在本质与方法论两层出现，
X 域只承载案例，用于印证或反证主干节点，不阻塞主 DAG。

## §2 横切主题覆盖（不建跨层边，用属性表达）

| 主题 | 节点数 | 锚点节点 | 何时核对 |
|---|---:|---|---|
| M · 质量属性 | 96 | `ESS-O-02` `ESS-M-01` `ESS-M-05` `MTH-M-01` `MTH-G-06` | 决策涉及性能/可靠性/可维护性等 ilities 时 |
| P · 技术债 | 31 | `ESS-L-01` `ESS-L-02` `MTH-L-03` `MTH-H-01` `TEC-H-02` | 涉及遗留治理、债务量化、重构优先级时 |
| N · 团队与康威 | 29 | `ESS-N-01` `MTH-N-01` `MTH-N-02` `MTH-O-06` `TEC-N-02` | 涉及团队边界、认知负荷、组织对齐时 |

覆盖核对法：先按 §1 定位域，再检查该域节点是否落在涉及的横切主题上；若决策横跨多主题，优先读锚点节点。
完整 96/31/29 落点清单见 `14-views/03-decision-matrix.html` §2。

## §3 决策启发式（从节点正文提炼的默认取舍）

| 取舍 | 默认倾向 | 依据节点 |
|---|---|---|
| 覆盖 vs 精度 | 漏失常不可补救而噪声可过滤，默认偏覆盖，再分层门控收敛 | `MTH-O-01` |
| 能力 vs 成本 vs 速度 | 区分一次性成本与持续成本，速度与稳定可兼得 | `MTH-O-04` |
| 简单 vs 功能丰富 | 理解成本是真实成本，先跑通最简可工作方案 | `MTH-O-08` `MTH-O-09` |
| 性能 vs 可修改性 | 显式化为敏感点/权衡点，按可度量判据排序 | `MTH-O-05` `MTH-M-06` |
| 发布 vs 稳定 | 用错误预算把「创新 vs 稳定」转为客观发布决策 | `MTH-K-01` `MTH-K-02` |
| 边界切多细 | 沿「可能变化的设计决策」切，按认知负荷约束边界 | `MTH-O-06` `ESS-H-01` |
| 复用 vs 封装 | 优先组合而非继承，维持封装边界与替换能力 | `ESS-H-06` |
| 自建 vs 采购/引入 | 按适用域匹配，额外能力都伴随新的复杂度 | `MTH-O-03` |

## §4 案例索引（按场景找同型案例）

- 选型对比：`CAS-X-12` MCP 四件套选型对比
- 重构/深改：`CAS-X-04` 网申 v2 深度重构
- 耦合分析：`CAS-X-05` preset 通道耦合分析
- 升级级联治理：`CAS-X-06` RC5→RC7、`CAS-X-07` 两次级联升级
- 插件深度裁决：`CAS-X-08` dsh-manager 插件深度分析
- 分层与文档化：`CAS-X-09` harness 源码架构解析
- 架构逆向：`CAS-X-01` 去中心化聊天、`CAS-X-13` Claude Code
- 规约驱动：`CAS-X-14` OpenSpec 规约驱动解析
- 知识图谱工程：`CAS-X-15` Open Code Review 图谱
- 跨学科方法：`CAS-X-16` 控制理论⊗Agent 设计
- 端到端交付：`CAS-X-17` 技术知识中枢交付法、`CAS-X-18` AI Agent 架构 DAG 复盘

## §5 视图与入口

- 分层视图：`14-views/01-layer.html`
- 学习路径：`14-views/02-learning-path.html`
- 决策矩阵（完整）：`14-views/03-decision-matrix.html`
- 案例视图：`14-views/05-cases.html`
- 全局术语表：`14-views/glossary.html`
- 交互 DAG 总览：`13-interactive/index.html`
