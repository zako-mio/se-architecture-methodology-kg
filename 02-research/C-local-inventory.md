# 本机本地信源盘点 — 软件工程 / 架构设计方法论

> 产出：阶段1 · 02-research/C-local-inventory
> 盘点人：知识资产盘点员（自写角色）｜日期：2026-09-10
> 扫描方式：只读（ls/glob/grep/find），未修改任何被扫描文件

## 一、核心结论

本机**没有**软件工程/架构设计经典书籍本体（预期「无」已被全盘 find 核实：*.pdf/*.epub/*.mobi/*.azw3 约 201 个文档中，仅有 `0823-12factor项目` 内的 `12factor.epub/.mobi`，无 Clean Architecture / APoSD / DDD / DDIA / SE@Google / SWEBOK）。因此阶段2 的书籍语料须按 `01-books` 候选清单另行获取，并严守版权红线（书本体只入本地语料层，永不进公开仓库）。

与母库主题强相关的资产集中在三类：**知识图谱库（结构+脚本+门控）**、**建库方法论 skill**、**真实工程架构分析留档**。这三类足以支撑母库的「工程底座 + 内容框架 + 案例库」，缺失的只是 S1 标准与 S2 经典书正文（需联网采集）。

## 二、分类盘点表

| 类别 | 编号 | 资产 | 类型 | 相关度 | 可复用点 |
|---|---|---|---|---|---|
| KG 库 | KG-01 | 0823-12factor-methodology | 知识图谱 | high | DAG 数据模型 + gen-*.py 生成链 + 七项门控 + 桥接主题设计 |
| KG 库 | KG-02 | 0820-algorithm-knowledge-graph | 知识图谱 | medium | 三级下钻结构 + 全自动生成链 + cytoscape vendor |
| KG 库 | KG-03 | 0826-RL推理显存面试知识库 | 知识图谱 | medium | 章节模板 + 学术风 CSS + 交叉验证信源规范 + 门控脚本 |
| KG 库 | KG-04 | 0813-知识库建库工程 | 知识图谱/教材 | high | **架构权衡思维 11 维统一骨架** + 建库全流程 |
| Skill | SK-01 | kb-construction | 方法论 | high | 五类谱系分流 + L1-L7 门控 + 信源分级/范式矩阵 + kb_gate.py |
| Skill | SK-02 | dag-tutorial-authoring | 方法论 | medium | 新手可读性递进结构 + 双轨验证 |
| Skill | SK-03 | cytoscape-dag-visualization | 方法论 | medium | 交互依赖图 DATA 注入/环修复/VLM 验证 |
| Skill | SK-04 | multi-window-dag-delivery | 方法论 | high | **三硬依据 E1/E2/E3** + 多窗口接力源码库分析 |
| 角色 | RL-01~03 | software/backend/multi-agent architect | 角色 | high | 架构角色 prompt 描述行，注入子Agent |
| 角色 | RL-04~10 | onboarding/reviewer/minimal-change/git/senior/prototyper/PM | 角色 | med/low | 工程实践视角补充分片 |
| 记忆 | MM-01 | MEMORY.md | 记忆 | high | 权衡矩阵选型法 / 覆盖率审计 / 双轨一致性 / 共享路径反推根因 |
| 实战 | PA-01 | 0820-去中心化聊天架构分析 | 架构案例 | high | 设计文档→18 模块依赖 DAG + 数据流 DAG |
| 实战 | PA-02 | 0805-OpenJobAutofill逆向分析 | 架构案例 | high | 适配器驱动 + 事件驱动架构全套文档 + drawio |
| 实战 | PA-03 | 0812-网申v3调取复制版 | 架构案例 | high | 契约先行 + 数据驱动解耦架构 |
| 实战 | PA-04 | 0806-网申扩展v2实现 | 重构案例 | high | 症状→根因→重构 的架构设计思路 |
| 实战 | PA-05 | 0816-dsh启动失败修复/N7-架构 | 架构案例 | high | 通道/层耦合 + 冷恢复路径建模 |
| 实战 | PA-06~08 | plugin-dag rc7/rc2、dsh-manager | 依赖分析 | high | 插件 DAG 级联升级 + 三硬依据证据链 |
| 实战 | PA-09~13 | harness源码解析/Hermes/MCP/claude-code/OpenSpec | 架构案例 | high/med | 源码模块分层、七层架构、Agent 架构逆向 |
| 实战 | PA-15~18 | open-code-review/控制理论Agent/技术中枢/项目复盘 | 架构案例 | high/med | 代码审查 KG、跨学科理论迁移、统一索引方法论 |
| 书籍 | BK-01~02 | 12factor.epub、AI Agents in Depth | 书/语料 | med/low | 12 Factor 原文（本地语料层） |

## 三、复用优先级（喂给阶段3）

1. **工程底座**：复用 KG-01 的 DAG 数据模型 + 生成链 + 门控，避免重造知识图谱基础设施。
2. **内容框架**：复用 KG-04「架构权衡思维 11 维」（每维：有什么可权衡 / 如何权衡 / 为何如此权衡 / 你的场景）作为架构决策方法论主干。
3. **编排方法**：注入 SK-01 五类谱系 + L1-L7 门控 + `reference/source-grading.md` 信源分级，作为母库生产流程。
4. **依赖证据模型**：SK-04/PA-08 的「三硬依据」作为架构依赖可溯源框架。
5. **案例库**：PA-01…PA-18 提炼为母库真实案例章节；RL-01/02/03 用于子Agent 专业化注入。

## 四、未决问题（gaps）

- 缺 S1 标准（SWEBOK、ISO/IEC/IEEE 42010/12207/25010）与 S2 经典书籍正文，需联网采集（阶段2）。
- `0817-plugin-dag` 目录为空，内容疑似已迁移至 `0819-plugin-dag-rc7`，引用时以 rc7/rc2 为准。
- 部分实战留档含第三方源码/规范（Hermes、MCP），引用需注意出处与版权。
