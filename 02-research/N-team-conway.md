# N 证据包：团队与康威定律（Teams & Conway）

- 采集日期：2026-09-10｜角色：组织与架构研究员（子Agent，自写角色）
- 信源：S2 = Conway 1968《How Do Committees Invent?》原文及作者页、Fowler bliki、Team Topologies 官方站点与书页；S3 = Thoughtworks Radar、DORA 官方（当前指标页/指标史/2024 报告）、SAFe；S4 = MacCormack-Baldwin-Rusnak 2012、Colfer-Baldwin 2016。共 13 源、22 定义、21 findings，关键定义均 ≥2 独立源交叉验证。

## 一、核心结论

1. **康威定律原句（回源论文结论段）**："organizations which design systems ... are constrained to produce designs which are copies of the communication structures of these organizations." Conway 用**同态（homomorphism）**数学论证：系统线性图与设计组织线性图保结构对应；每子系统各有独立设计组时两图完全相同。名称由 **Fred Brooks 在《人月神话》(1975)** 所取；1967 年投 HBR 被拒，1968 年 4 月由 Datamation 发表。
2. **实证支持与边界**：MacCormack et al.(2012) 支持"镜像假说"；但 Colfer & Baldwin (2016) 综述 **142 项研究**发现镜像普遍却**非普适**——技术动态产业中"部分镜像"更优，企业可借模块化或关系契约刻意"打破镜子"，开放协作软件项目亦系统性违反严格镜像。
3. **三种回应**：Ignore（拧扭架构，典型失败模式）/ Accept / **Inverse Conway Maneuver**（主动改变组织以催生目标架构，术语由 LeRoy & Simons 2010 提出，Thoughtworks Radar 评为 Trial，已退榜）。ICM 非万能：刚性遗留架构仅重组组织不解决问题，反增摩擦，且易被误用为"改组织架构图"。
4. **团队拓扑**：Team Topologies（Skelton & Pais, 2019）以**四团队类型 + 三交互模式**为组织设计约束；核心洞见是**认知负荷**，平台的首要价值即降低 stream-aligned 团队认知负荷。
5. **DORA 口径已变**：当前为**五指标**（3 throughput + 2 instability），研究反复证明速度与稳定非权衡；把指标当目标触发 Goodhart 定律与 gaming。

## 二、团队拓扑四类型 + 三交互模式

| 团队类型 | 定位/职责 | 主要交互模式 | 来源 |
|---|---|---|---|
| Stream-aligned | 对齐单一业务价值流，full-stack/full-lifecycle 端到端负责、无交接（You Build It You Run It），Two Pizza 规模 | 接收 XaaS / 跨团队 Collaboration | S2-04/05/06, S3-05 |
| Enabling | 帮 stream-aligned 排除障碍、发现缺失能力，教练式提升技能使其自主 | Facilitation（教练） | S2-04/05, S3-05 |
| Complicated-subsystem | 专攻需大量数学/计算/技术专长的高复杂子系统，降低使用方认知负荷 | X-as-a-Service（短期 Collaboration） | S2-04/05, S3-05 |
| Platform | 组合其他类型，为 stream-aligned 提供自服务内部产品（TVP），作为产品经营 | X-as-a-Service（构建期 Collaboration） | S2-04/05, S3-05 |

三种交互模式：**Collaboration**（限时高带宽）、**X-as-a-Service**（低交互、清晰边界）、**Facilitation**（教练/mentoring）。（S2-04, S2-05）

## 三、团队边界 ↔ 架构耦合对应关系

| 组织侧 | 架构侧 | 媒介/机制 | 来源 |
|---|---|---|---|
| 团队沟通结构 | 系统模块/接口结构 | 同态 homomorphism；接口协商只在有通信路径处发生 | S2-01 |
| 业务能力/价值流划分 | 可独立演进的服务边界 | Bounded Context + Ubiquitous Language 对齐价值流 | S2-03 |
| Stream-aligned 团队结构 | 面向业务、解耦的组件架构 | Team Topologies 承认康威定律，团队结构塑造架构 | S2-04 |
| 团队依赖/交接 | 模块耦合与集成复杂度 | 减少团队依赖→减少架构耦合；平台/服务化收敛依赖 | S2-05 |
| 组织镜像（mirroring） | 产品/技术依赖 | 治理结构、求解惯例、沟通模式约束解空间 | S4-01, S4-02 |

DORA 五指标（S3-02/03）：Throughput = change lead time、deployment frequency、failed deployment recovery time；Instability = change fail rate、deployment rework rate。演进链：2014 三指标→2015 四指标二元→2018 +availability/SDO→2021 reliability→**2023 MTTR 改名 FDRT**→**2024 +rework rate 成五指标**。旧"四键"口径须标版本，勿当现状。

## 四、未决问题（gaps）

Conway 原文为扫描重排版、Datamation 原始页码不可得；Team Topologies/Accelerate 等书本体受版权限制未提取正文；DORA 2025 各档 benchmark 量化阈值未取；本域缺 S1 标准（ISO 12207/42010 不覆盖团队组织），以 S2/S3/S4 支撑为主；ICM 企业级量化效果缺独立学术研究。详见 `N-team-conway.json`（含 6 组 principle↔counterexample 配对与 5 条 errata）。
