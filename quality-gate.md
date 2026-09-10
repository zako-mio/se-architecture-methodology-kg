# 阶段1–6 · 质量门控报告（L1–L8 + 方法论专项 + 回放四硬指标）

- **日期**：2026-09-11（阶段6 收口，覆盖阶段1–5 建库与阶段6 版式重构/审计/发布全周期）
- **任务目录（MISSION_ROOT）**：`~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论`
- **复杂度继承**：`[COMPLEXITY: 19/20] → Deep`（全程 Deep 推理）
- **门控依据**：`00-plan/stage5-build-contract.md §六`（L1–L7 + 方法论四项 + §6.3 回放四硬指标）、`00-plan/stage6-content-ia-spec.md §10`（L8 版式点位）
- **门控执行方式**：全部由 `16-checkpoint/*.py` **现场实测**，命令与实测值见下表；`skipped ≠ PASS`。
- **门控综合结论**：**L1/L2/L3/L5/L6/L7/L8 + 方法论 4/4 PASS；L4 首次实装：仅自动判据 = PASS，并入 VLM 支路 = WARN（0 FAIL，无阻断）；回放四硬指标达标。** CI 中 **L4/L5 显式 SKIPPED（不伪装 PASS）**。

---

## 一、主图规模实测（真值）

| 维度 | 实测值 | 来源 |
|---|---:|---|
| nodes | **167** | `10-dag-data/methodology-dag.json` / `stats.md` |
| edges | **360** | 同上 |
| groups | **18**（+组总索引共 19 页） | 同上 |
| themes | 3 | 同上 |
| cases | **18** | 同上 |
| layer=essence | **51** | 同上 |
| layer=methodology | **67** | 同上 |
| layer=technology | **31** | 同上 |
| layer=null（案例层） | **18** | 同上 |
| canonical 信源 | **253** | `03-knowledge-map/canonical-sources.json` |
| 域分布 | F13 · G17 · H16 · I14 · J17 · K17 · L14 · M14 · N13 · O14 · X18(cases) | `stats.md` / 现场统计 |
| 孤立节点 | **0** | 现场统计（度=0 节点为 0，含 case 层） |
| 正文长度（definition + 四 detail） | min **1501** / 中位 **1536** / max **1813** 字；`<1500` = **0** | 现场统计 |
| `verified` 取值分布 | **`true` 149 / `"cited"` 18** | 现场统计（**必须 `is True` 判定**） |
| `verified=true` 占比（GR-10） | **149/167 = 89.22%**（阈值 ≥80%） | `gate_sources.py` |
| 可溯源率（sources 非空且可解析） | **167/167 = 100%**（阈值 ≥95%） | `gate_sources.py` |

> 起点（阶段5 开工时）= **23 节点 / 37 边 / 18 组**；阶段5 完成 Wave 1–4 后达 **167 / 360 / 18**。阶段6 只改呈现层与派生层，**不改数据契约**：全量重生后主图仍为 167/360、Kahn 167/167 无环，SHA-256 指纹 `58a7e3c3…` 不变。

---

## 二、L1–L8 分层门控（逐层 · 现场实测）

| 层 | 检查项 | 命令 | 实测值 | 结论 |
|---|---|---|---|---|
| **L1 生成时自验证** | JSON 合法、schema/枚举、`sources[]` canonical 可解析、边端点、层间方向、硬依赖无环 | `validate_graph.py --shard <分片>`（逐分片） | **23 个分片**（22 `_parts/*.json` + `_base.json`）全部 `errors=0`；逐批 PASS/FAIL = **23/0** | **PASS** |
| **L2 全量审计** | 字段完整性、ID 唯一、计数一致（`meta.total_*`==实际）、跨产物一致、Kahn 无环 | `validate_graph.py --graph 10-dag-data/methodology-dag.json --canonical 03-knowledge-map/canonical-sources.json` | `nodes=167 edges=360 kahn_visited=167/167`，`errors=0 warnings=0` | **PASS** |
| **L3 结构 + 断链** | UTF-8/无 U+FFFD、空文件、空正文、内部断链 | `kb_gate.py --root <MROOT> --layers structure,links --exclude _backup-idmigration --exclude 02-research --exclude 01-books --exclude 03-knowledge-map --exclude 00-plan --exclude 16-checkpoint` | 母库自身口径：structure 检查项=**412** 问题=**0**；links 检查项=**5134** 问题=**0** | **PASS** |
| **L4 视觉**（首次实装） | 截图像素计数 + headless 运行时结构 + DOM 紧致文本盒 2D 相交 + 外部 VLM 交叉：无截断/无真实文本重叠/无横向溢出/字号行高/结构块可见 | `gate_visual.py --check all`（+ `--vlm-result` 回流 VLM 支路） | **仅自动判据（像素 + DOM 运行态）272 项 / 212 PASS / 0 FAIL / 0 WARN / 60 SKIP → PASS**；**并入 VLM 支路后 278 项 / 217 PASS / 0 FAIL / 1 WARN / 60 SKIP → WARN（无 FAIL）**（VLM 支路 5 PASS + 1 WARN）；唯一 VLM WARN = glossary 超宽表格在 `overflow-x:auto` 容器内滚动（契约 §7 允许，非缺陷） | **PASS / WARN**（无 FAIL） |
| **L5 渲染** | cytoscape 实渲染（headless Chromium via agent-browser）：canvas 节点/边计数、成员集、JS 错误、边端点 | `gate_render.py --timeout 25` | **7 用例全 PASS**：默认组级 `zcount=18`；下钻 `GL-ESSENCE 51/51`、`GL-METHOD 67/67`、`GL-TECHNOLOGY 31/31`、`GC-CASE 18/18`、`GD-G 17/17`、`GD-F 13/13`，成员集==`groups[].node_ids`；`skipped=0`；JS 错误 0；悬空端点 0 | **PASS** |
| **L6 覆盖度** | manifest 交付物清单 + 四向覆盖（DAG↔节点页↔MD↔案例）+ GR-08 + GR-09 | `gate_coverage.py` | manifest **363/363 = 100%**（节点页 167 / MD 167 / 组页 19 / 视图 7 / 交互 1 / 根入口 1 / xref 1）；四向综合 **100%**（缺失 0、孤儿 0）；GR-08 **PASS**（O/X 显式豁免）；GR-09 **11/31 = 35.48% ≥30% PASS** | **PASS** |
| **L7 信源** | canonical 可解析、可溯源率、`verified=true` 占比、disputed 术语标注 | `gate_sources.py` | canonical 引用 **1446** 条（node.sources 605 / errata 222 / edge.sources 619），**悬挂 = 0**；可溯源率 **167/167 = 100%**；`verified=true` **149/167 = 89.22% ≥80%**；disputed 术语 4 个、命中 5 处、**未标注 = 0** | **PASS** |
| **L8 版式**（新增） | 关系图 / 摘要卡 / 权衡卡（严格标记词归栏）/ TOC 锚点 / 条件块 / 术语链接 / 自包含 / 编码 / 深链 / 双轨一致 | `gate_layout.py --check all` | 综合覆盖率 **2124/2124 = 100.00%**，问题 **0**；节点页 167、HTML 生成物 194、文档（HTML+MD）367、glossary 锚点 152，逐项全 PASS | **PASS** |

> **L4 / L5 在 CI 中显式 SKIPPED（不伪装 PASS）**：GitHub Actions 标准 runner 不预装 `Pillow` / `numpy` / `agent-browser`（headless Chromium），故按 `rebuild.yml` 打印明确跳过原因，**不计为 PASS**。本地补跑命令见 §九。
>
> **L4 口径**：`gate_visual.py --check all` 的**仅自动判据（像素 + DOM 运行态）**为 **272 项 / 212 PASS / 0 FAIL / 0 WARN / 60 SKIP**，判定 **PASS**；并入外部 VLM 支路结果（`16-checkpoint/_render-shots/visual/vlm-result.json`，5 PASS + 1 WARN）后为 **278 项 / 217 PASS / 0 FAIL / 1 WARN / 60 SKIP**，综合判定 **WARN**（阈值规则：无 FAIL → 退出码 0；存在 FAIL 或全 SKIP → 1）。唯一 WARN 为 VLM 对 `14-views/glossary.html`「超宽表格在 `overflow-x:auto` 容器内横向滚动」的粗检提示，属契约 §7 明确允许的行为，**不是缺陷**，故不判 FAIL。
>
> **已知脆弱点（诚实披露）**：`agent-browser` 偶发渲染瞬态（页面渲染为纯白、视口切换未生效），会使 `pixel.*` 产生**假 FAIL**（本轮实测 1 次，随后 4 次交替重跑稳定复现预期结果）。**观察到 L4 FAIL 时应先重跑一次确认**，不要立即当作页面缺陷上报；建议后续在 `gate_visual.py` 增加「白页/零墨迹 → 自动重试一次」机制。
> **本轮改造要点**：旧 1D 像素判据「同行两段墨迹被 1–3px 背景隔断」被量化证伪（正常排版 `GL-ESSENCE@1280` 命中 40 行，gap 分布 `{1px:25, 2px:14, 3px:2}` 全为中文正常字距）→ 换为 **DOM Range 紧致文本盒 2D 真实相交**（`ox>1px && oy>1px && 相交面积>6px²`，含祖先/后代、同父内联片段、overflow 裁切、显式 z-index 分层排除）；旧像素判据退役为 DOM 不可用时的降级提示并记 `SKIP`。负向测试已通过（注入绝对定位覆盖层可被抓出）。

---

## 三、方法论专项门控（四项 · 现场实测）

命令：`python3 16-checkpoint/gate_methodology.py --check all`

| # | 专项 | 实测值 | 结论 |
|---|---|---|---|
| ① | **层边界判定规则校验** | 边总数=360；`implements`(tech→method)=59；`derives_from`(method→essence)=69；案例层豁免=69；技术→本质越级=0；内层引用外层=0；违规=0 警告=0 | **PASS** |
| ② | **术语一致性** | glossary disputed=4（微服务/可观测性/可扩展性/可演化性），引用命中 5 处且均经 errata 显式讨论；冲突 err=0，警告 warn=0 | **PASS** |
| ③ | **原则↔反例配对完整性** | 显式映射表 `16-checkpoint/opc-mapping.json`；O-PC 覆盖 **36/36**；悬空节点=0；无反例/类型不匹配=0 | **PASS** |
| ④ | **11 维权衡覆盖** | O-TD **11/11** 均有落点（MTH-O-01..11） | **PASS** |

**方法论专项综合 = PASS（4/4）**

---

## 四、回放四硬指标（§6.3 终门）

| # | 硬指标 | 阈值 | 实测值 | 结论 |
|---|---|---|---|---|
| 1 | **覆盖度** | ≥90% | manifest **100.00%**（363/363）；四向综合 **100.00%** | **达标** |
| 2 | **门控全过** | 启用层全 PASS（skipped 显式记录） | L1/L2/L3/L5/L6/L7/L8 + 方法论 4/4 **全 PASS**；**L4：仅自动判据 PASS / 并入 VLM 后 WARN（0 FAIL，首次实装）**；CI 中 L4/L5 显式 SKIPPED | **达标** |
| 3 | **信源可溯源率** | ≥95% | canonical 命中 **100.00%**（悬挂 0）；`verified=true` **89.22%**（≥80%） | **达标** |
| 4 | **人工抽查无重大语义错误** | 抽样复核 | 抽检节点（ESS-H-03 / MTH-O-08 / TEC-K-01 / ESS-L-02 / MTH-N-05 / CAS-X-05）+ 勘误回源（Lehman 八定律 1996、Royce/ATAM 迭代评审）；五段式齐全、`sources[]` 均可解析、反例/权衡在位，**无重大语义错误** | **达标** |

> 抽查口径说明：本次抽查为**定向抽样**（覆盖 essence/methodology/technology/case 四类层 + 已知易错历史条目），非全量语义审阅；全量语义由 L7（信源锚定）+ 方法论专项（术语/反例/权衡）+ L8（版式保真）机器化兜底。

---

## 五、HTML 双交付质量门控（报告自身）

校验方式：独立只读脚本读取 `report.html`，断言 `\ufffd` 不存在、`<div>` 开闭平衡、5 个段标题齐备、无外链资源依赖（自包含）。

| 检查项 | 断言 | 实测 | 结论 |
|---|---|---|---|
| UTF-8 无 BOM | 文件头无 `\xef\xbb\xbf` | `True` | **PASS** |
| UTF-8 无替换字符 | `'\ufffd' not in html` | `0` | **PASS** |
| div 开闭平衡 | `html.count('<div') == html.count('</div>')` | 相等 | **PASS** |
| 五段标题完整 | ≥5 个章节标题（一~五） | 5/5 | **PASS** |
| 自包含 | 无 `<script>` / 外链 CSS/JS / web font | `True` | **PASS** |

---

## 六、阶段6 变更摘要

阶段6 在本门控体系上的净变化（相对阶段5 快照）：

1. **新增 L8 版式门控** `gate_layout.py`：把契约 §1–§11 块序列、权衡卡**严格标记词归栏**、TOC/锚点、术语内联、自包含、编码、深链、HTML↔MD 双轨一致固化为机器可检；实测 **2124/2124 = 100%**。
2. **首次实装 L4 视觉门控** `gate_visual.py`：像素计数 + headless 运行时结构 + DOM 紧致文本盒 2D 相交 + 外部 VLM 交叉；仅自动判据 **272 项 / 212 PASS / 0 FAIL / 0 WARN / 60 SKIP → PASS**，并入 VLM 后 **278 项 / 217 PASS / 0 FAIL / 1 WARN / 60 SKIP → WARN**（0 FAIL）。本轮把旧 1D 像素重叠判据（量化证伪：正常排版 `GL-ESSENCE@1280` 命中 40 行、gap 分布 `{1px:25,2px:14,3px:2}` 全为中文正常字距）替换为 **DOM Range 紧致盒 2D 相交**，并退役为 DOM 不可用时的降级提示（记 `SKIP`）；负向测试已通过。（阶段5 记为 SKIPPED，与本轮 WARN 不矛盾——阶段5 尚无该产物层。）
3. **L2/L5/L6/L7/方法论** 在阶段6 全量重生后复跑仍全 PASS（数据契约未变）。
4. **L6 manifest 口径更新**：交付物由 362 增至 **363**（`14-views/` 因新增 `glossary.html` 由 6 → 7）。
5. **CI 声明**：`rebuild.yml` 中 L4/L5 **显式 SKIPPED**（环境依赖缺失），绝不伪装 PASS。
6. **版权/脱敏**：`audit_publish.py` 长引移出 42 处 / 20493 字、本机路径脱敏 209 处；`_publish-staging/` 保留 `PUBLISH-MANIFEST.md` + `AUDIT-REPORT.json`；`needs_review` 1 项待裁决。

---

## 七、与 `_publish` 副本口径差异

同一 L3 命令在**母库根**与**公开集根**上因排除目录不同，检查项数不同（**问题数均恒为 0**）：

| 口径 | 命令要点 | structure 检查项 | links 检查项 | 问题 |
|---|---|---:|---:|---:|
| **母库自身口径**（本报告采用） | root=MROOT，排除 `_backup-idmigration/02-research/01-books/03-knowledge-map/00-plan/16-checkpoint/_publish/18-design/.github` | **412** | **5134** | 0 |
| 母库全树（task 原命令，**含 `_publish` 副本叠加**） | root=MROOT，不排除 `_publish` | **851** | **10343** | 0 |
| **`_publish` 副本口径**（README §六） | root=`_publish`，排除 `.github/02-research/01-books/03-knowledge-map/00-plan/16-checkpoint` | **410** | **5134** | 0 |

说明：
- `links` 项数在「母库自身口径」与「`_publish` 副本口径」下同为 **5134**（扫描的是同一批生成物集合）；`structure` 项数相差 2，源于两个根目录顶层文件的细微差异。
- 全树命令因把 `_publish/` 内的整份公开集副本再扫一遍，故检查项数近似翻倍（851/10343）——这是**副本叠加**而非缺陷，本报告 L3 以**母库自身口径**为准。
- `_publish` 副本的 L4/L5/L8 与母库同源生成物一致；公开集内文档（README 等）另有独立脱敏复扫（本机路径 0 / U+FFFD 0 / 疑似凭据 0）。

---

## 八、软目标、遗留与豁免记录（透明披露）

1. **GR-11 字数（1500–3000 字，软目标 / 告警不阻断）**：`validate_graph.py` 不将 GR-11 计入 error/warning。阶段5 已把 Wave 0 骨架 11 个种子节点由 281–424 字补齐至 1604–1772 字；阶段6 现场复算全库 **`nodes < 1500 字` = 0**。建议后续把 GR-11 常态输出为 warning 清单。
2. **L4：仅自动判据 PASS、并入 VLM 后 WARN（均无 FAIL）**：自动判据 0 WARN；并入后唯一 1 条 WARN 为 VLM 提示 glossary 超宽表格在 `overflow-x:auto` 容器内滚动（契约 §7 明确允许容器内滚动），**不是缺陷**，故不判 FAIL。旧 `pixel.overlap-suspect` 1D 像素启发式已退役（量化证伪：正常中文排版字距本就落在 1–3px），改由 DOM Range 紧致盒 2D 相交判定；DOM 可用时旧判据记 `SKIP`。**无 FAIL**。
3. **L4/L5 CI SKIPPED**：CI 无 Pillow/numpy/agent-browser，显式跳过且不计 PASS；推送前须本地补跑。
4. **`needs_review` 1 项待裁决**：`02-research/E-iso-standards.json` 长引移出占比 56%（第三方标准正文偏多），建议人工裁决是否整文件剔除。
5. **12factor 反向深链未做**：当前仅母库→子库单向；子库→母库回链待后续。
6. **30 本付费书语料待用户提供**：`01-books/gap-request.md`（P0 14 / P1 10 / P2 6），提供后走 pdf-worker 解析。
7. **检索层 D2 挂起**、**Agent skill 形态**：阶段6 已落地 `20-agent-skill/`（轻量速查 + 路径路由），检索层预留接口仍不建。

---

## 九、门控命令汇总（可复现 · 现场实测）

```bash
MROOT="~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"
cd "$MROOT/16-checkpoint"

# L1 分片自验证（逐分片）
python3 validate_graph.py --shard ../10-dag-data/_parts/<批次>.json --canonical ../03-knowledge-map/canonical-sources.json

# L2 全图审计
python3 validate_graph.py --graph ../10-dag-data/methodology-dag.json --canonical ../03-knowledge-map/canonical-sources.json

# L3 结构 + 断链（母库自身口径）
python3 kb_gate.py --root "$MROOT" --layers structure,links \
  --exclude _backup-idmigration --exclude 02-research --exclude 01-books \
  --exclude 03-knowledge-map --exclude 00-plan --exclude 16-checkpoint \
  --exclude _publish --exclude 18-design --exclude .github

# L4 视觉（本地；CI 中 SKIPPED）
python3 gate_visual.py --check all
python3 gate_visual.py --check all --vlm-result _render-shots/visual/vlm-result.json

# L5 渲染（headless Chromium via agent-browser；CI 中 SKIPPED）
python3 gate_render.py --timeout 25

# L6 覆盖度
python3 gate_coverage.py

# L7 信源
python3 gate_sources.py

# L8 版式
python3 gate_layout.py --check all

# 方法论专项四项
python3 gate_methodology.py --check all
```

> 复现约束：`gate_visual.py` / `gate_render.py` 依赖 Pillow + numpy + `agent-browser`（headless Chromium），须位于 `$HOME` 可访问路径；本机实跑通过。L4 外部 VLM 支路结果经 `--vlm-result` 回流后计入门控汇总。
