# A · 何为软件工程（Software Engineering）——证据包摘要

> 阶段1 权威源调研（据实、不杜撰）。配套证据包：`A-se-definition.json`（21 条信源 / S1×12 / S2×5 / S4×4）。本包不覆盖“架构设计”主题。

## 一、核心结论

**1. 定义（多源交叉，high）**。软件工程的权威定义是“将系统化、规范化、可量化的方法应用于软件的开发、运行与维护；即把工程应用于软件”（IEEE Std 610.12-1990）。该定义经 SWEBOK、SEVOCAB(ISO/IEC/IEEE 24765)、SE2014 采纳，是学界与标准界的共同基线。Sommerville 教材补充为“关注软件生产所有方面的工程学科，从系统规格说明到投入使用后的维护”。Google 的产业视角进一步指出：软件工程不只是写代码，而是组织长期构建与维护代码的全部工具与流程（“Programming Over Time”）。

**2. 学科范畴（high）**。SWEBOK 是软件工程知识体系的基线标准（ISO/IEC TR 19759），由 IEEE 计算机学会出版：V3 划定 15 个知识域（需求、设计、构造、测试、维护、配置管理、工程管理/过程、模型与方法、质量、职业实践、经济、计算/数学/工程基础），V4（2024-10）扩展为 18 个，新增软件架构、软件工程运维、软件安全等。CS2023 将“编程 vs 软件工程”的差异精炼为两个维度——**时间**（多版本、长期存活）与**人员**（团队协作）。

**3. 起源与演化（high）**。学科以 1968 年 NATO 软件工程会议（Garmisch）与 1969 年罗马会议为起点；“software engineering”术语作为故意带挑战性的会议名称，来源归于 F. L. Bauer。1968 报告第 7 章明确记录了“software crisis / software gap”的争论（成本/进度超支、质量低、难维护、项目失控），且与会者对其严重程度存在分歧。范式上，瀑布模型常追溯至 Royce(1970)，2001 年敏捷宣言提出四大价值与十二原则，标志向迭代、增量、响应变化的转向。

**4. 与 CS/编程的关系（high）**。SE 以计算机科学为主要基础（SE2014 指出其最大知识组件为 computing essentials），但不等同于 CS：SE 引入工程流程、团队协作与时间/变更维度；Parnas 主张 SE 应作为与土木、机械等并列的工程学科。

**5. 生命周期与质量（high）**。ISO/IEC/IEEE 12207 定义的是“过程”而非固定“阶段”，不规定具体生命周期模型；2026 版与 15288 统一为四组过程（协议、组织项目使能、技术管理、技术），过程数由 43 统一为 30。阶段示例（ISO/IEC TS 24748-1）：concept、development、production、utilization、support、retirement。ISO/IEC 25010:2023 产品质量模型由九大特性构成（2011 版为八特性：Usability→Interaction capability、Portability→Flexibility、新增 Safety）。

**6. 可维护性/可扩展性/可演化性（high/medium）**。可维护性（maintainability）被 IEEE 14764 定义为“软件产品被修改的能力”，修改含纠错、改进及适配环境/需求变化；ISO 25010 下其子特性为模块性、可复用性、可分析性、可修改性、可测试性。维护分类为纠正性、适应性、完善性、预防性，占生命周期成本主要份额（>80% 为非纠正性，理解约占工作量一半）。Lehman 八条演化定律表明软件必须持续适应，否则质量与满意度下降——**维护即演化式（继续）开发**。“可扩展性/可演化性”并非标准顶层术语，其地位由“可修改性/灵活性/可复用性”等子特性与演化定律承载。

## 二、关键信源

- **S1（12 条）**：SWEBOK V3/V4（IEEE CS）、ISO/IEC/IEEE 12207:2017 与 12207:2026、ISO/IEC 25010:2023、SE2014（ACM/IEEE-CS）、CS2023 SE KA、NATO 1968 原始报告、IEEE 610.12-1990、ISO/IEC/IEEE 24765:2017、SEI（CMU）、敏捷宣言 2001、ISO/IEC/IEEE 14764。
- **S2/S4（9 条）**：Sommerville 教材、Software Engineering at Google、iso25000.com（AENOR）、Sonar ISO 25010 说明、Wikipedia 条目组；Lehman 1980、Royce 1970、Parnas 1998、Brooks 1987。

## 三、未决问题（gaps）

1. iso.org 标准页对本机 403，ISO 标准正文未逐字核对，经 OBP 摘要与标准门户交叉核验；2. SWEBOK V4 官方页不可达，KA 清单未取正文；3. Royce/Lehman/Parnas/Brooks 经典论文未回源原文；4. CS2023 采用 Beta v2 文本；5. extensibility/evolvability 无标准级独立定义（属架构 Agent 范畴）。
