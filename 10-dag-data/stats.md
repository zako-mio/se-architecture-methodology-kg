# 母库主图 · 统计与拓扑说明

> 数据源：`10-dag-data/methodology-dag.json`（由 `16-checkpoint/aggregate.py` 聚合）
> 性质：阶段5 母库骨架 + 各波次分片合并结果；技术/案例层由后续波次补齐。

## 1. 计数

| 维度 | 数值 |
|---|---:|
| nodes | 167 |
| edges | 360 |
| groups | 18 |
| themes | 3 |
| cases | 18 |
| layer=essence | 51 |
| layer=methodology | 67 |
| layer=technology | 31 |
| layer=null（案例层） | 18 |
| verified=true | 149 / 167 |
| 含 errata 的节点 | 161 |

### 1.1 按 domain

| domain | 含义 | 节点数 | 节点 |
|---|---|---:|---|
| F | 概念与需求 | 13 | ESS-F-01, ESS-F-02, ESS-F-03, ESS-F-04, ESS-F-05, MTH-F-01, MTH-F-02, MTH-F-03, MTH-F-04, MTH-F-05, MTH-F-06, TEC-F-01, TEC-F-02 |
| G | 架构设计 | 17 | ESS-G-01, ESS-G-02, ESS-G-03, ESS-G-07, MTH-G-05, MTH-G-06, TEC-G-01, TEC-G-02, TEC-G-03, TEC-G-04, ESS-G-04, ESS-G-05, ESS-G-06, MTH-G-01, MTH-G-02, MTH-G-03, MTH-G-04 |
| H | 实现与构造 | 16 | ESS-H-01, ESS-H-02, ESS-H-03, ESS-H-04, ESS-H-08, ESS-H-09, MTH-H-03, MTH-H-04, TEC-H-01, TEC-H-02, TEC-H-03, ESS-H-05, ESS-H-06, ESS-H-07, MTH-H-01, MTH-H-02 |
| I | 测试 | 14 | ESS-I-01, ESS-I-02, ESS-I-03, ESS-I-04, MTH-I-01, MTH-I-02, MTH-I-03, MTH-I-04, MTH-I-05, MTH-I-06, MTH-I-07, TEC-I-01, TEC-I-02, TEC-I-03 |
| J | 部署 | 17 | ESS-J-01, ESS-J-02, ESS-J-03, ESS-J-04, MTH-J-01, MTH-J-02, MTH-J-03, MTH-J-04, MTH-J-05, MTH-J-06, MTH-J-07, TEC-J-01, TEC-J-02, TEC-J-03, TEC-J-04, TEC-J-05, TEC-J-06 |
| K | 运维 | 17 | ESS-K-01, ESS-K-02, ESS-K-03, ESS-K-04, MTH-K-01, MTH-K-02, MTH-K-03, MTH-K-04, MTH-K-05, MTH-K-06, MTH-K-07, TEC-K-01, TEC-K-02, TEC-K-03, TEC-K-04, TEC-K-05, TEC-K-06 |
| L | 演化与弃用 | 14 | ESS-L-01, ESS-L-02, ESS-L-03, ESS-L-04, ESS-L-05, MTH-L-01, MTH-L-02, MTH-L-03, MTH-L-04, MTH-L-05, MTH-L-06, MTH-L-07, TEC-L-01, TEC-L-02 |
| M | 质量属性 | 14 | ESS-M-01, ESS-M-02, ESS-M-03, ESS-M-04, ESS-M-05, MTH-M-01, MTH-M-02, MTH-M-03, MTH-M-04, MTH-M-05, MTH-M-06, TEC-M-01, TEC-M-02, TEC-M-03 |
| N | 团队与康威 | 13 | ESS-N-01, ESS-N-02, ESS-N-03, ESS-N-04, ESS-N-05, MTH-N-01, MTH-N-02, MTH-N-03, MTH-N-04, MTH-N-05, MTH-N-06, TEC-N-01, TEC-N-02 |
| O | 方法论主干 | 14 | ESS-O-01, ESS-O-02, ESS-O-03, MTH-O-01, MTH-O-02, MTH-O-03, MTH-O-04, MTH-O-05, MTH-O-06, MTH-O-07, MTH-O-08, MTH-O-09, MTH-O-10, MTH-O-11 |
| X | 跨域 | 18 | CAS-X-01, CAS-X-02, CAS-X-03, CAS-X-04, CAS-X-05, CAS-X-06, CAS-X-07, CAS-X-08, CAS-X-09, CAS-X-10, CAS-X-11, CAS-X-12, CAS-X-13, CAS-X-14, CAS-X-15, CAS-X-16, CAS-X-17, CAS-X-18 |

### 1.2 按边类型

| type | 条数 | 是否硬依赖边 |
|---|---:|:--:|
| case_instance | 69 | 否 |
| combination | 36 | 否 |
| conflicts | 4 | 否 |
| contrasts | 14 | 否 |
| cross_reference | 1 | 否 |
| dependency | 24 | 是 |
| derives_from | 69 | 是 |
| enables | 13 | 否 |
| implements | 59 | 否 |
| prerequisite | 58 | 是 |
| refines | 13 | 是 |

### 1.3 按横切主题（cross_cutting）

| 主题 | 节点数 | 节点 |
|---|---:|---|
| M | 96 | ESS-O-02, ESS-F-01, ESS-F-03, MTH-F-05, ESS-I-01, ESS-I-02, ESS-I-03, ESS-I-04, MTH-I-01, MTH-I-02, MTH-I-03, MTH-I-04, MTH-I-05, MTH-I-06, MTH-I-07, ESS-J-04, MTH-J-05, MTH-J-07, ESS-K-01, ESS-K-02, ESS-K-03, ESS-K-04, MTH-K-01, MTH-K-02, MTH-K-03, MTH-K-04, MTH-K-05, MTH-K-06, MTH-K-07, ESS-L-05, MTH-L-04, MTH-L-05, ESS-M-01, ESS-M-02, ESS-M-03, ESS-M-04, ESS-M-05, MTH-M-01, MTH-M-02, MTH-M-03, MTH-M-04, MTH-M-05, MTH-M-06, ESS-O-03, MTH-O-01, MTH-O-05, MTH-O-09, MTH-O-11, MTH-G-05, MTH-G-06, ESS-H-08, ESS-H-09, MTH-H-04, CAS-X-02, CAS-X-03, CAS-X-05, CAS-X-08, CAS-X-10, CAS-X-11, CAS-X-12, CAS-X-13, CAS-X-14, CAS-X-15, CAS-X-16, CAS-X-17, CAS-X-18, TEC-F-01, TEC-G-01, TEC-G-02, TEC-G-03, TEC-H-01, TEC-H-02, TEC-H-03, TEC-I-01, TEC-I-02, TEC-I-03, TEC-J-01, TEC-J-02, TEC-J-03, TEC-J-04, TEC-J-06, TEC-K-01, TEC-K-02, TEC-K-03, TEC-K-04, TEC-K-05, TEC-K-06, TEC-L-01, TEC-M-01, TEC-M-02, TEC-M-03, ESS-G-04, ESS-G-05, MTH-G-01, MTH-G-02, MTH-G-03 |
| P | 31 | ESS-L-01, ESS-L-02, ESS-L-03, ESS-L-04, ESS-L-05, MTH-L-01, MTH-L-02, MTH-L-03, MTH-L-06, MTH-L-07, MTH-O-10, ESS-H-09, MTH-H-03, CAS-X-04, CAS-X-05, CAS-X-06, CAS-X-07, CAS-X-08, CAS-X-10, CAS-X-12, CAS-X-14, CAS-X-15, CAS-X-16, TEC-F-02, TEC-H-01, TEC-H-02, TEC-H-03, TEC-J-02, TEC-L-02, TEC-M-02, MTH-H-01 |
| N | 29 | ESS-N-01, MTH-I-03, MTH-K-05, ESS-N-02, ESS-N-03, ESS-N-04, ESS-N-05, MTH-N-01, MTH-N-02, MTH-N-03, MTH-N-04, MTH-N-05, MTH-N-06, MTH-O-06, MTH-O-09, MTH-O-11, MTH-H-04, CAS-X-11, CAS-X-13, CAS-X-17, CAS-X-18, TEC-N-01, TEC-N-02, TEC-J-05, TEC-J-06, TEC-K-03, TEC-K-05, TEC-K-06, MTH-G-04 |

## 2. Kahn 拓扑无环验证

- 硬依赖边集合 `{prerequisite, dependency, derives_from, refines}`：**164** 条。
- 非硬依赖边：196 条（不参与环检测）。
- 参与顶层排序的节点：167 / 167。
- 拓扑序（Kahn 出队顺序）：`ESS-H-04 → ESS-G-01 → MTH-F-01 → MTH-F-03 → MTH-F-05 → ESS-I-03 → MTH-I-03 → MTH-I-06 → MTH-J-03 → MTH-J-04 → MTH-J-05 → MTH-J-07 → MTH-K-03 → MTH-K-06 → MTH-K-07 → MTH-L-02 → MTH-L-03 → MTH-L-05 → MTH-L-06 → ESS-M-03 → MTH-M-02 → MTH-M-03 → MTH-M-05 → MTH-M-06 → MTH-N-01 → MTH-N-04 → MTH-N-05 → MTH-N-06 → MTH-O-02 → MTH-O-04 → MTH-O-05 → MTH-O-08 → MTH-O-10 → MTH-G-05 → MTH-G-06 → MTH-H-03 → MTH-H-04 → CAS-X-01 → CAS-X-02 → CAS-X-03 → CAS-X-04 → CAS-X-05 → CAS-X-06 → CAS-X-07 → CAS-X-08 → CAS-X-09 → CAS-X-10 → CAS-X-11 → CAS-X-12 → CAS-X-13 → CAS-X-14 → CAS-X-15 → CAS-X-16 → CAS-X-17 → CAS-X-18 → TEC-F-01 → TEC-F-02 → TEC-N-01 → TEC-N-02 → TEC-G-01 → TEC-G-02 → TEC-G-03 → TEC-G-04 → TEC-H-01 → TEC-H-02 → TEC-H-03 → TEC-I-01 → TEC-I-02 → TEC-I-03 → TEC-J-01 → TEC-J-02 → TEC-J-03 → TEC-J-04 → TEC-J-05 → TEC-J-06 → TEC-K-01 → TEC-K-02 → TEC-K-03 → TEC-K-04 → TEC-K-05 → TEC-K-06 → TEC-L-01 → TEC-L-02 → TEC-M-01 → TEC-M-02 → TEC-M-03 → ESS-G-04 → MTH-G-04 → MTH-H-01 → MTH-H-02 → ESS-H-03 → ESS-G-05 → MTH-F-02 → MTH-I-05 → MTH-I-04 → MTH-I-07 → MTH-J-01 → MTH-J-06 → ESS-J-04 → MTH-K-04 → MTH-K-05 → ESS-L-03 → MTH-L-04 → MTH-L-01 → MTH-L-07 → ESS-M-04 → MTH-M-04 → MTH-M-01 → MTH-N-02 → MTH-O-07 → MTH-O-06 → MTH-O-03 → MTH-O-09 → MTH-O-11 → ESS-G-06 → MTH-G-02 → ESS-H-08 → ESS-N-01 → ESS-H-01 → MTH-F-04 → MTH-I-01 → ESS-J-01 → MTH-J-02 → ESS-K-03 → ESS-K-02 → MTH-K-02 → ESS-L-04 → MTH-N-03 → ESS-M-05 → MTH-O-01 → ESS-G-07 → MTH-G-01 → MTH-G-03 → ESS-H-09 → ESS-N-02 → ESS-H-05 → ESS-H-06 → MTH-F-06 → MTH-I-02 → ESS-J-02 → ESS-J-03 → ESS-K-04 → MTH-K-01 → ESS-L-05 → ESS-M-01 → ESS-N-05 → ESS-H-07 → ESS-H-02 → ESS-F-05 → ESS-I-02 → ESS-K-01 → ESS-M-02 → ESS-N-04 → ESS-F-02 → ESS-I-01 → ESS-N-03 → ESS-F-01 → ESS-I-04 → ESS-F-03 → ESS-F-04 → ESS-O-01 → ESS-O-02 → ESS-L-01 → ESS-O-03 → ESS-G-03 → ESS-L-02 → ESS-G-02`
- 结论：**无环（DAG）**。

## 3. 引用完整性（零悬挂）

- canonical 信源主表 = `03-knowledge-map/canonical-sources.json`，共 **253** 个实体。
- 节点 `sources[]`、`errata[].source_id`、边 `sources[]` 全部命中 canonical 集合。
- 悬挂引用：**0**。

## 4. 分层与坐标说明

- 本质层 51 节点；方法论层 67 节点；技术层 31 节点；案例层 18 节点。
- 层间边：`implements`（tech→method）59 条、`derives_from`（method→essence）69 条；层间方向规则由校验器强制。
- `GD-*`（domain）与 `GCC-*`（crosscut）为**派生索引**分组，允许与 layer 分组重叠，仅用于视图聚合；横切主题用 `node.cross_cutting` 属性表达，不建跨层边。

## 5. 门控

门控由 `16-checkpoint/validate_graph.py` 独立执行；本文件不作 PASS/FAIL 断言。

