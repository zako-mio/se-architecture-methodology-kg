# 阶段6 内容版式架构契约（A 案 · 文档流优先 · 浅色 Codex）

> 状态：**权威契约**（W2 实现与 W3 门控均以本文为准）
> 生成：2026-09-11　生成者：阶段6 主Agent
> 决策来源：暂停点1 用户选定「仅 A 单套落地」+「文档页浅色 / 交互图保持暗色」
> 参考实现：`18-design/cand-A/{index,conflict}.html`（设计参考，非生成物）

---

## 0. 适用范围与不变式

**适用产物**：`11-node-pages/` · `12-groups/` · `14-views/` · `15-md/`（镜像）· `index.html` · 新增 `14-views/glossary.html`

**不适用（保持原状，零改动）**：`13-interactive/`（cytoscape 暗色总览）· `12factor` 子库（跨年份目录）

| 不变式 | 内容 |
|---|---|
| **I1** | `10-dag-data/` 下内容数据**字节不变**（`methodology-dag.json` SHA-256 必须仍为 `58a7e3c3…`） |
| **I2** | 不修改 `03-knowledge-map/glossary.md` 与 `canonical-sources.json` |
| **I3** | **内容逐字保真**：节点正文、边标签、案例、勘误一律取自数据原文，禁止改写/编造/推断性归类 |
| **I4** | **零 JS、自包含**：不得出现 `<script>`、外链 CSS/JS、web font（仅系统字体栈） |
| **I5** | **UTF-8 无 BOM、无 U+FFFD**；改生成链必须同步改 `16-checkpoint/` 源码，**禁手改生成物** |
| **I6** | **390px 页面级横向溢出 = 0**（容器内滚动允许，页面 `scrollWidth` 超出视口不允许） |
| **I7** | 深链不得再出现 `../../../2026-08/` 前缀 |

---

## 1. 设计 token（浅色 Codex）

```css
:root{
  --bg:#f5f1e8; --panel:#fffdf8; --border:#e2d9c8;
  --text:#2b2620; --dim:#6f6656;
  --accent:#9a5b1b; --accent2:#1f6f5c; --line:#d8cdb8;
  /* 语义补充（暗色站点的 --ok/--warn/--err 以浅色适配值替代） */
  --ok:#1f6f5c; --warn:#a8641a; --err:#a33a2e;
}
```
- 正文栈：`-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif`
- 标题栈：`Georgia,'Songti SC','Noto Serif CJK SC','SimSun',serif`
- 版心：单栏 **760px**；≥900px 时左侧 **sticky TOC**（宽约 210px），<900px 折为顶部折叠盒
- 章节编号 `§N` + 锚点 id `s1..sN` + `scroll-margin-top`（避开 sticky 顶栏）
- 顶栏：面包屑 + 站名 + 当前节点名 + 元信息（层/域/优先级）

## 2. 节点页块序列（唯一顺序）

| # | 块 | 数据来源 | 渲染形态 |
|---|---|---|---|
| §1 | 摘要与结论 | `definition` | `defcard`：`TL;DR · 一句话结论` 标签 + 正文 + 别名/英文/类型行 |
| §2 | 局部关系图 | 边 `from`/`to` 1–2 跳邻域 | `figbox > svg.nbhd`（**内联静态 SVG**）+ `legend` 6 类边色 |
| §3 | 原理 · 为什么 | `detail.principle` | 段落 + 引导句加粗 + 荧光 `hl` 关键词高亮 |
| §4 | 机制 · 如何运作 | `detail.mechanism` | 同上 |
| §5 | 工程 · 怎么落地 | `detail.engineering` | 同上 |
| §6 | 权衡卡 | `detail.tradeoff` | `tradeoff` 三栏 `gain/cost/counter`（**归栏规则见 §4**） |
| §7 | 学习路径条 | `prerequisite` 边（入向优先，拓扑序） | `pathbar > step`（含当前节点高亮 `cur`） |
| §8 | 冲突 / 对比表 | `contrasts` / `conflicts` 边 | 表格，每格取两端节点原文（首句） |
| §9 | 案例带 | `case[]` / 2 跳内 `case_instance` 边 | `case-band > case-card`；**须标注来源路径**（直接 case 或 2 跳派生） |
| §10 | 信源与核验 | `sources`/`verified`/`confidence`/`review_date`/`errata` | `evidence > .r` 键值行 |
| §11 | 原始关系清单 | 全部关联边 | `<details>` 渐进披露（默认折叠） |
| 附 | 对照资源 · 12factor 子库 | `16-checkpoint/xref-12factor.json` rows 命中 | 深链列表（**绝对 URL**，见 §6） |

**条件渲染**：§8 仅当节点参与 `contrasts`/`conflicts`；§9 仅当有 case（直接或 2 跳派生，派生须标注）；§7 仅当有 `prerequisite`。

## 3. 局部关系 SVG 规则

- 邻域：以当前节点为中心，取 **1–2 跳**（1 跳全部 + 2 跳按度数剪枝，**上限 24 个节点**，超出时优先保留 1 跳与度数高者）。
- 节点：中心节点实心强调（`cur`），1 跳实心小点，2 跳空心小点；标签截断到 12 字（全名置 `<title>`）。
- 边：**6 类分色** — `prerequisite` / `implements` / `derives_from` / `case_instance` / `contrasts` / `conflicts`；`contrasts`/`conflicts`/`case_instance` 用**虚线**。
- **必须含** `<title>`/`aria-label` 与图例 `legend`；布局用确定性算法（固定初始角度按 id 排序 + 2 轮力导向迭代后取整），保证同一数据**可重复生成**（禁止随机种子）。
- 高度自适应：`viewBox` 由节点包围盒计算。

## 4. 权衡卡归栏规则（**保真红线**）

`tradeoff` 是单一自然段。三栏 `收益 gain` / `代价 cost` / `反例 counter` 的归栏**只允许依据原文显式证据**：

1. **允许**：原文含显式标记词时才归栏 —— 反例标记：`反例`/`误区`/`失败`/`反面`；代价标记：`代价`/`成本`/`风险`/`过度`/`不足`；收益标记：`收益`/`好处`/`价值`。
2. **不允许**：凭上下文推断句子的极性（例：不得因句子含「提升」就归入收益栏，也不得把任意句子塞进「反例」栏）。
3. **无显式证据时**：该栏不生成，剩余句子按原顺序进入 `原文要点` 中性列表（`<ul class="b">`），卡片标题仍为「权衡卡」。
4. 任何栏内文本**逐字引用原文**，仅允许插入 `…` 省略号标记截断，不得改字。

> 后续可选增强（不在 W2 范围）：以 LLM 派生 `16-checkpoint/tradeoff-split.json`（逐句三分类 + 证据句标注，可审阅、不改 DAG）来补全三栏；启用前须先落盘并人工抽检。

## 5. 术语内联

- **新产物**：`14-views/glossary.html`，由 `03-knowledge-map/glossary.md` 生成（11 个 H2 分区 + 表格条目）。
- **锚点规则**：按 glossary.md 中出现顺序，条目锚点 = `g-001`、`g-002`…（三位补零，**ASCII 安全**）。
- **内联规则**：节点页正文中，术语（`术语`列或 `English` 列，**长词优先**避免子串误命中）**仅在页内首次出现时**渲染为 `<a class="term" href="../14-views/glossary.html#g-0NN">`；后续出现保持纯文本。
- 禁止对 `definition` 之外的代码/ID/URL 文本做匹配；禁止跨 HTML 标签匹配。
- `disputed` 状态术语内联时须保留可辨识标记（标题属性注明「无权威共识，给推荐口径」）。

## 6. 跨库深链（12factor 子库）

- 唯一合法目标模板：`https://zako-mio.github.io/12-factor-methodology-kg/02-node-pages/{id}.html`
- 修改点：`16-checkpoint/xref-12factor.json` 的 `deep_link_template` 与 **38 行 `rows[].deep_link`** 全部替换。
- 生成物中**不得**再出现 `2026-08` 或 `../../..` 形式的子库路径。
- 说明：`10-dag-data` 不含该路径（实测 0 次），故不触碰 I1。

## 7. 响应式与无溢出硬约束

**实测根因**：A 参考实现中 `.nbhd{min-width:680px}`、`@media(max-width:900px){.nbhd{min-width:560px}}`、`@media(max-width:560px){.nbhd{min-width:460px}}` 导致 390px 下页面溢出（实测 A +124px / B +89px / C +67px）。

**规定修法**：
```css
.figbox{overflow-x:auto;-webkit-overflow-scrolling:touch;}
.nbhd{width:100%;height:auto;display:block;}
/* 移动端保留可读性：滚动发生在 .figbox 内，页面本身不溢出 */
@media(max-width:900px){ .nbhd{min-width:640px} }
@media(max-width:560px){ .nbhd{min-width:560px} }
```
**校验**：headless 390px 下 `document.documentElement.scrollWidth <= 391`；表格/长行用 `overflow-x:auto` 容器包裹。

## 8. `15-md` 镜像规则

- 同 §2 块序列，以 Markdown 标题 + 表格 + 清单呈现。
- 术语**不加外链**（保持纯文本），避免 MD 与 HTML 双轨链接漂移；§11 关系清单保留为表格。
- 生成器 `gen-md.py` 与 HTML 生成器共用同一数据派生函数（`gen_common.py`），保证双轨一致。

## 9. 组页 / 视图页 / 根索引

- 全部套用同 token 与顶栏/面包屑/页脚外壳；组页含成员表 + 组内关系图（复用 §3 的 SVG 构造器）；视图页保留原 6 视图语义（分层/学习路径/决策矩阵/跨体系对照/案例 + index）。
- 新增 `14-views/glossary.html` 纳入 `14-views/index.html` 导航。

## 10. 门控点位（`gate_layout.py` 将校验，W3 实现）

| 校验项 | 判据 |
|---|---|
| 每节点页含内联关系图 | `svg.nbhd` 计数 ≥1 |
| 摘要卡 | `class="defcard"` 存在 |
| 权衡卡 | `class="tradeoff"` 存在，且含 ≥1 个 `gain`/`cost`/`counter` 或 `原文要点` 列表 |
| TOC 与锚点 | `toc` 存在；每个 `§N` 有对应 `id="sN"`；锚点全部可解析（无悬挂） |
| 条件块 | 参与 conflicts/contrasts 的节点须含对比表；有 prerequisite 的须含 `pathbar` |
| 术语链接 | 所有 `a.term` 的 `href` 目标锚点在 `glossary.html` 中存在 |
| 自包含 | 0 `<script>`、0 外链资源（`src="http` / `href="http...css`）、0 `@import` |
| 编码 | 无 U+FFFD，UTF-8 无 BOM |
| 深链 | 生成物中 `2026-08/` 出现次数 = 0 |
| 无溢出 | 390px `scrollWidth <= 391`（渲染层，归 L4） |

## 11. 变更管理与回归

1. 改生成链 → 改 `16-checkpoint/*.py` 源码；重生后 `10-dag-data` 指纹必须不变。
2. 重生后必须跑：`validate_graph.py`（errors=0）、`kb_gate.py --layers structure,links`（0 错）、`gate_coverage.py`、`gate_sources.py`。
3. 回归失败即回滚：`git -C $MROOT checkout <baseline> -- 11-node-pages 12-groups 14-views 15-md index.html`。

## 12. C-lite：书证核验版式契约（阶段7 追加）

> 上游：`00-plan/stage7-book-absorption-plan.md` §3.3#5 / §4.7；`01-books/_verify/_meta/verify-contract.md` §9。
> 数据源（公开安全投影）：`10-dag-data/book-verification.json`（由 `16-checkpoint/derive_verification.py` 确定性生成）。

### 12.1 节点页 §10「信源与核验」书证锚行

| 项 | 规定 |
|---|---|
| 位置 | `§10 信源与核验` 区块内，「规范信源」行之后、「入口链接」行之前 |
| 标签 | `书证核验`（`.evidence .r > .k`，与「规范信源」同款式） |
| 格式 | `书证核验：BK-007 Ch5.2（direct）、Ch11（partial）；BK-009 Ch3.2（partial）` |
| 粒度 | **仅章节级锚**：`Ch<chapter>` 或 `Ch<section>`；同一节点内按 `source_id` 升序，锚按自然序（`_nat_key`）升序 |
| 强度 | 同一锚取最高优先级（`contradicted > direct > partial > inferred`）标注 |
| 条件渲染 | 该节点在投影 `by_node` 中**无记录则不渲染该行**（节点页保持原样） |
| 禁止 | 页码、页码区间、原文摘句、`claim` / `evidence_note` / `page_anchor_private` / `record_id` 一律不得出现 |
| 镜像 | `15-md/nodes/<id>.md` 同步输出 `- 书证核验：<同上纯文本>`，保证双轨一致 |

### 12.2 `14-views/06-book-verification.html` 块序列（唯一顺序）

| # | 块 | 数据来源 | 渲染形态 |
|---|---|---|---|
| §1 | 书籍 ↔ 节点对照矩阵 | `by_node` | 按层分组的多张表：行 = 参考书（BK-007/BK-009/BK-023，按 `source_id` 升序），列 = 该层被核验节点（含节点页链接）；格 = 强度徽标 + 章级锚 |
| §2 | 覆盖统计 | `by_node` | 每本书覆盖节点数、`direct/partial/inferred/contradicted` 分布、正向/反向分布；含合计行 |
| §3 | 反向发现缺口（阶段3 输入） | `gaps` | 表：`gap_id` / 类型 / 书 / 锚 / 目标 / 改写摘要 / 建议动作 |

- 视图入口 `14-views/index.html` 由 `config.py` 的 `views` 清单自动生成 06 卡片（标题「书籍↔节点对照」）。
- 数据源缺失时优雅降级为空状态页并打印 `[SKIP]`，不得崩溃。

### 12.3 公开字段白名单（`10-dag-data/book-verification.json`）

- `by_node[node_id][]` 允许字段：`source_id` / `book` / `chapter` / `section` / `section_title` / `evidence_strength` / `direction` / `second_pass` / `review_date`。
- `gaps[]` 允许字段：`gap_id` / `kind` / `book_source_id` / `chapter` / `section` / `target` / `summary` / `proposed_action` / `evidence_strength`（`summary` 为改写摘要，不属书正文）。
- **禁止字段**：`claim` / `evidence_note` / `page_anchor_private` / `record_id` / `claim_id` / 页码区间。
- 排序确定性：`by_node` 按 `node_id` 升序、节点内按 `(source_id, chapter, section)` 稳定排序；`gaps` 按 `gap_id` 升序；`meta.generated` 取冻结常量。
