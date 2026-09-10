# 实现与构造（Implementation & Construction）——权威源摘要

> 配套证据包：`H-implementation.json`；信源 18 条（S1=2、S2=11、S3=2、S4=3）；核心结论 27 条、定义 20 条、原则↔反例配对 13 条。

## 一、核心结论

**1. 模块化与信息隐藏。** Parnas(1972) 原文核验：模块化效果取决于「划分判据」。按处理步骤/流程图分解（conventional）时，核心数据结构变更会波及所有模块；按 **information hiding** 分解时，每个模块隐藏一个「困难或可能变化的设计决策」，变更只波及单模块。关键澄清：Parnas 的 module 是 **责任分配**（responsibility assignment），不是子程序；设计决策超越执行时间，故模块不必对应处理步骤。作者还自评 KWIC 的 circular-shift 模块规定顺序属「design error」——隐藏边界本身需持续裁剪。

**2. 内聚/耦合与度量。** 概念由 Constantine 于 1960 年代末提出、Stevens/Myers/Constantine(1974) 正式发表：coupling=模块间依赖度，cohesion=模块内关联度，目标是**低耦合高内聚**。内聚谱系 Coincidental→Functional；耦合谱系 Content→Data；Page-Jones 的 **connascence** 提供更强/局部/degree 的三维分析。定量化为 Chidamber-Kemerer(1994) 六度量：WMC/DIT/NOC/**CBO/RFC**（耦合）/**LCOM**（内聚反向）。标准落点：ISO 25010:2023 的 maintainability→**Modularity**（改一组件对其它影响最小）。

**3. 整洁代码与可读性。** Fowler：code smell 是「对应深层问题的表层迹象」（Kent Beck 命名），不等于问题本身，是重构的启发式信号。Clean Code（Martin）主张函数短、只做一件事；Ousterhout 明确反对——函数到几十行后再缩小收益有限，更多函数意味着更多接口与文档，且反对「少用注释」。Google 以「**Code is read far more than it is written**」为主线，用 readability 强制评审+导师制传播实践（实证净提升速度，但需人力线性扩展）。

**4. 设计模式与反模式。** GoF(1994) 23 模式按目的分 Creational/Structural/Behavioral，两条核心原则：**面向接口编程**、**优先组合而非继承**。反模式（Koenig 1995 命名，1998 年《AntiPatterns》普及）是「常见但适得其反的解法」；Big Ball of Mud（Foote & Yoder, PLoP'97）是其高频形态。模式并非免腐化：系统综述（Almadi et al. 2021）证实 GoF 模式自身会出现 bad smells 并提高维护成本。

**5. Ousterhout：深模块与抽象。** 设计目标是降低 **complexity**（表现为 change amplification / cognitive load / unknown unknowns，成因为 dependencies / obscurity）。**deep module**=接口简单而功能强大；**shallow module**=接口复杂而功能不足（classitis）。主张「somewhat general-purpose」：功能贴合当前需求、接口保持通用；「general-purpose APIs result in more information hiding」。但抽象有代价——Spolsky 定律：**所有非平凡抽象都有一定程度的泄漏**。

## 二、原则 ↔ 反例配对表

| 原则 | 反例/失败模式 | 源 |
|---|---|---|
| information hiding（Parnas） | fragile base class：继承暴露父类实现，基类改动使派生类故障 | S2-01/06, S4-03 |
| encapsulation / 稳定接口 | leaky abstraction：底层性能/故障泄漏（TCP/SQL/NFS） | S2-07 |
| high cohesion | God object / Large Class / Coincidental cohesion | S2-09, S3-01 |
| low coupling | Content/Common coupling、Feature Envy、Inappropriate Intimacy | S2-09, S3-01 |
| deep modules | shallow modules / classitis / pass-through methods | S2-02 |
| DRY | over-abstraction / wrong abstraction（AHA、Rule of Three） | S2-04, S3-01 |
| YAGNI | Speculative Generality / Inner-platform effect / Abstraction inversion | S2-11, S3-01 |
| Design Patterns（GoF） | 模式过度使用、额外间接层、模式自身 bad smells | S2-06, S4-02 |
| favor composition over inheritance | 脆弱基类；「inheritance breaks encapsulation」 | S2-06, S4-03 |
| SRP | Divergent Change、God object | S2-05, S3-01 |
| Clean Code 短函数 | Ousterhout：过小函数增接口/文档、失去独立性（disputed） | S2-05, S2-02 |
| strategic programming | tactical tornado / Big Ball of Mud / 软件熵 | S2-02, S2-08 |
| Modularity（ISO 25010） | Big Ball of Mud、架构腐化（erosion/drift） | S1-02, S2-08 |

## 三、关键信源

- **S1**：SWEBOK V4.0（Software Design Ch.3 / Software Construction Ch.4，官方参考含 GoF）、ISO/IEC 25010:2023（maintainability 子特性）。
- **S2**：Parnas(1972 全文)、Ousterhout《A Philosophy of Software Design》2nd ed.+官方 extract、Fowler CodeSmell、Hunt&Thomas(DRY)、Martin(Clean Code/SOLID)、GoF(1994)、Spolsky(Leaky Abstractions)、Foote&Yoder(Big Ball of Mud)、Stevens/Myers/Constantine(1974)、Google SWE at Google(Ch.3)、Jeffries/Beck(YAGNI)。
- **S3/S4**：refactoring.guru、sourcemaking（线索层）；Chidamber-Kemerer(1994, TSE)、Almadi et al.(2021, Sustainability)、Mikhajlov & Sekerinski(1998, ECOOP)。

## 四、勘误（errata）

1. GoF 原著 **23** 个模式；refactoring.guru 列 **22** 个（省略 Interpreter），引用需区分来源。
2. 信息隐藏思想最早见于 Parnas **1971 IFIP** 论文，1972 CACM 为奠基性正式发表。
3. Parnas 的 module 是**责任分配**，不是「一/多个子程序」。
4. DRY 针对**知识重复**而非一切代码重复；「prefer duplication over the wrong abstraction」（Sandi Metz）。

## 五、未决问题（gaps）

1. **APoSD 第 4 章**（deep/shallow 完整定义）不在作者官方 extract 中，书本体受版权未回源；deep/shallow 定义基于官方 extract + 作者页 + 详读摘要交叉，非逐字原文。
2. GoF、Clean Code、Pragmatic Programmer、Refactoring 等**书本体未回源**，经 Wikipedia 条目与 SWEBOK 官方书单核验，未见原著内页。
3. CK94 与 fragile base class 论文 PDF 为**扫描图像无文本层**，度量清单经 Maynooth 技术报告 + Crossref 元数据核验，公式细节未获取。
4. Almadi et al.(2021) MDPI 正文 **403**，仅经 Crossref 摘要核验，坏味道清单未获取。
5. SWEBOK Ch.3/Ch.4 **正文未下载**，构造过程官方定义原文待补。
6. 内聚/耦合与 CK 度量多为**相对/序数指标**，无普适阈值，「多高算高」依赖语境。
7. refactoring.guru / sourcemaking 按计划书**仅作线索源**，未作独立权威证据。
