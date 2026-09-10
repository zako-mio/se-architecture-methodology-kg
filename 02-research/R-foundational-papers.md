# R 域｜奠基文献回源证据包摘要（R-foundational-papers）

> 配套机器可读版：`R-foundational-papers.json`。生成：学术文献溯源员 ｜ 访问日期：2026-09-10 ｜ 契约：`00-plan/contract.md`。目标：把知识地图中 `cited`（未回源）的经典文献升级为可核验，并澄清两条广为流传的误读。

## 一、核心结论

1. **Royce 1970 不是瀑布宣言。** 原文（11 页，全文检索）未出现 "waterfall" 一词；Figure 2 的 "grandiose approach" 单次流程正是 Royce 要修补的对象。Figure 3 明确描述相邻阶段间的**迭代**，Figure 4 承认迭代不限于相邻步骤；补救方案为五步（Figure 10），其中 **STEP 3 原文标题即 "DO IT TWICE"**——首次开发的系统，其交付版本应是关键设计/运行区域的“第二版”，先用缩小版/试点做最终产品的早期仿真。
2. **Lehman 定律条数需校正。** 1980 年《Programs, Life Cycles, and Laws of Software Evolution》（Proc. IEEE 68(9):1060-1076）原文为 **5 条定律**；“八条定律”的完整表述最早见于 Lehman 1996 的《Laws of Software Evolution Revisited》：3 条（1970s 中期）+ 2 条（1980）+ 1 条（1991 脚注）+ 2 条（1996 首次成文）。八条为：Continuing Change、Increasing Complexity、Self Regulation、Conservation of Organisational Stability、Conservation of Familiarity、Continuing Growth、Declining Quality、Feedback System；适用于 E-type 系统。
3. **Parnas 1998** 论证 SE 不应被当作 CS 的子领域，而应走传统工程专业教育路径；本次核验为 IEEE Software 1999 重印本（原刊 Annals of Software Engineering 6:19-37）。
4. **Brooks《No Silver Bullet》** 核心为“不存在单一手段能在十年内带来十倍提升”，并区分 essence 与 accident；本质复杂度的四属性原文为 **complexity / conformity / changeability / invisibility**（注意：属 essence 的属性，而非“本质与偶然各四要素”）。
5. **POSA Vol.1** 仅取 Wiley 官方免费样章（Chapter 1 + 目录 PDF，扫描件含水印）与官方配套站点；Microkernel 定义为“最小功能核 + 可插拔扩展插座”。全本受版权，未回源。
6. **SWEBOK V4（2024-10）** 官方页核验含 **18 个 KA**，较 V3 新增 Software Architecture、Software Engineering Operations、Software Security 三个 KA。

## 二、文献回源状态表

| 文献 | 主源/ID | tier | 状态 | 可访问性 | 交叉验证 |
|---|---|---|---|---|---|
| Royce 1970 | S4-PAP-04 | S4 | **verified**（全文） | free（机构镜像/Wayback） | 原文 + 维基瀑布条目 |
| Lehman 1980 | S4-PAP-03 | S4 | **abstract-only** | 付费（IEEE Xplore） | Crossref + Lehman1996 + 维基 |
| Lehman 1996（八定律复述） | R-XC-01 | S4 | **verified**（全文） | free（课程镜像） | 维基 |
| Parnas 1998 | S4-PAP-05 | S4 | **verified**（全文） | free（机构存档） | Crossref 元数据 |
| Parnas 1972 | S4-PAP-02 | S4 | **verified**（复用 H 包） | free（课程镜像） | H-implementation.json |
| Brooks 1987 | S4-PAP-01 | S4 | **verified**（全文） | free（社区镜像） | 原文 + 维基 |
| POSA Vol.1 | S2-BK-16 | S2 | **verified（official-sample）** | 官方样章 free，全本付费 | Wiley + software-pattern.org |
| SWEBOK V4 | S1-OFF-01 | S1 | **verified（官方页元数据）** | 页面 free，正文付费 | 官方页 + SEBoK + 维基 |

**unreachable：** 无（所有条目至少元数据可达；`cited` 已全部升级）。

## 三、未决问题（gaps）

- Lehman 1980 原刊全文未合法免费取得（abstract-only），条数结论依赖 Lehman 本人 1996 复述，未逐字核验 1980 正文。
- Royce 原刊（IEEE WESCON 1970 / ICSE 1987 重印）与 Brooks 1986 IFIP 版 / 1987 Computer 版均未做双版逐字对照。
- Parnas 1998 Annals 原版正文未取得（用 IEEE Software 重印本）；POSA 样章为无文本层扫描件，Microkernel 细节取自官方站点描述。
- SWEBOK V4 PDF 正文与各 KA 详解需会员/购买，18 KA 清单以官方页 + SEBoK 交叉。
- “Royce 被误读为瀑布”缺少同行评审史学专文作第三方交叉，当前为原文 + 维基。

## 四、版权与合规

未把任何受版权保护的论文/书籍全文写入 MISSION_ROOT。Royce/Brooks/Parnas/Lehman1996 PDF 仅临时下载到 `/tmp` 用于文本核验，任务结束即删除；POSA 仅记录 Wiley 官方样章 URL 与可达状态，未转写正文。
