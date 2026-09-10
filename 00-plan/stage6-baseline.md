# 阶段6 基线冻结记录（W0）

> 生成时间：2026-09-11　生成者：阶段6 主Agent
> 用途：为「内容版式重构 + 版权审计 + 上传 GitHub」提供**回滚锚点**与**冻结证据**。
> 本文件是阶段6 的事实基线：任何后续声明与本文冲突时，以本文的实测值为准。

---

## 1. 回滚锚点

- 本地归档仓：`MISSION_ROOT/.git`（分支 `main`），首个 commit 即本基线。
- **本地仓永不推送**；公开仓是独立目录 `_publish/`（自带 `.git`，见 W5/W6）。
- 回滚命令：
  ```bash
  MROOT="~/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论"
  git -C "$MROOT" log --oneline            # 找到基线 commit
  git -C "$MROOT" checkout <baseline> -- 11-node-pages 12-groups 13-interactive 14-views 15-md index.html
  ```

---

## 2. 冻结指纹（SHA-256）

| 文件 | SHA-256 | MD5 |
|---|---|---|
| `10-dag-data/methodology-dag.json` | `58a7e3c397dc772344d71d8f98dd107ad5ac54a607bcea956a6a8994a258a390` | `f82c1b355a06a4367070ebe344ac587a` |
| `03-knowledge-map/canonical-sources.json` | `e7cd0eb7445595c2b4a653bf58760e071d801ad47842a2bc3f8c4d1187222c33` | `c3e969963b541bd40ce84f2477bdcfce` |
| `10-dag-data/node-content.json` | `077c89d5c92f1aeaf5926523b0028fa612e33ac760f1ef987c655242a2a00184` | — |
| `10-dag-data/_base.json` | `26e624726f28d6e4a0cd6ed5a6783c8d7b0965aad3643298d9326a3fd26dee3a` | — |

**验收硬约束**：阶段6 结束时上述**数据文件指纹必须不变**（本阶段只改呈现层与派生层，不改内容数据契约）。

---

## 3. `02-research/` 输入完整性清单（35 文件 · SHA-256）

审计期间本目录**一字不改**；脱敏产物另出 `02-research.public/`。以下为冻结证据。

```
f281ffb1400ca11e164b589321286569e53beb2a6edec9dde727e23c7b13a6c8  A-se-definition.json
f0ba3ce7634adde94806eb2f1b33a4a7a799ce0498911ec58a3e92b66b0557b8  A-se-definition.md
cc55974f90e39fdf726045b59f7a3f1a491be30a37eda47d2d33904e6b7d29c7  B-architecture-definition.json
bd79a3335c44f01e0df26d1e118c13c8bf690d4e0a44b0cd99a7a61964bb5916  B-architecture-definition.md
8b480525231ab9907df79cc793395bb70f7c5f655f2a51ffc91391a8fec65d52  C-local-inventory.json
53b48a62cba25239ac0ae52dbeb3fc7048226b2f959c4ffc0e9238dbfdf16f8c  C-local-inventory.md
58157cd3d1007cb1671942c4d2773191ec842bd7af4e8578fe766360a3081347  E-iso-standards.json
768a3319ad8658c1c1711a225384935ea6ed1f41ba46c723ac6035d1421341e7  E-iso-standards.md
a89c15e5cb43711202bbb688f2218c0ecde90185e4987de1279b6860ffc75acf  F-requirements.json
857f813d1d5a37505396ad2af2afe40db4725ed4760bffc8a49bec6d451606aa  F-requirements.md
5007a44fde94661b647c1499e927bb644b2bba14ea5ea87b381fba7e9cecee21  G-architecture.json
d21575aa615e5d68aa8426214f7679673da0e9a26205ed8bce976dcc19a0252f  G-architecture.md
673611985bb78c4201fc7a56cc9765ab4fb70d1804cdcdcebda305ba6183e837  H-implementation.json
5ca1c2019c9e74dbe82bf3c971337a32160c230d81df383f2be7cd5d529ef349  H-implementation.md
8a0c983a750c8bafce176503412f93ffbfcced05402a671453bdee2669e2823f  I-testing.json
e556596b4a66318b47f3f0d97015fbece034406b9184997edf1c80c7fab0dc21  I-testing.md
d05572dc31b1048b3d64d3882b0f551e9607ca57838438db678f47d5d7b56cec  J-deployment.json
06a138122456b02c6d832c14411fddb124d066294d2da5b9ed3096957c87366b  J-deployment.md
e53864ca21261d4d7cf6e6afb3ddb2634dab013e62a5798ea5a05a93b834f49d  K-operations.json
d3be3191cc40a0b0ddc593e532c10f582b6951c0a378a8c8af1f7346dc6e2ec3  K-operations.md
f6f7d2f3b0a1b8219b067af5ce24b6d6d484ef0b274f21d4b79c2dbfc21e53dd  L-evolution.json
f9dcdf6ff05f612617e9eeda56317d6d3f0f45c8410c588c1cb6e34ee8992f3f  L-evolution.md
9ae3fc36a30da9a27e7e372373350f30b87a71b3ac65d334f83a889dfa4e7d47  M-quality-ility.json
559093761872907036a564dc66920b9d909a39299dbfed09db4739756bef3de7  M-quality-ility.md
f377fd043b908c7ff14b8af9be0bcfaf9193fc06f2caf4c39bdcea4ed8efd0f7  N-team-conway.json
77fcbe420614dcd5100df7363b7860bfb9a65535573b9d4a598deedfc858e8b4  N-team-conway.md
66ad98cb3a6e63ae1b7ad95c0e59fe6fb888736e18ea78f3ee94d1488875a004  O-methodology.json
0c71ec8506009829812a103ce97c7e97fa9f056d84bed8bfe0b7f29d3e842033  O-methodology.md
2ccb1b2fc6e83c421cddd87ceecd9e5e3c79ab20f2bdd8b25e8f240ef1f1af00  P-techdebt.json
6fdda6fb8cde42d66f7cc1ef7e6e678685b4aa513dd460df124190148d204276  P-techdebt.md
a03f127ca851f5bf4459ba3fdc13755f351cb32bbcc305127d431979d60d3880  Q-vendor-architecture.json
011d5fb9a241a737a537fd1963af49280c06042529775cd0e42697e7070c7b83  Q-vendor-architecture.md
8076341a527894dfdaf81be84edfa7a405c4a9f098fec5de50319d6402c52ee7  R-foundational-papers.json
fd5a22c02d009db55f8474dfa4f929ba16b28b6c501fc10b91931d361f23e338  R-foundational-papers.md
24f87801f76989ca97c3da966d01896fff869b2d5fcad2644b6dcaeeeda89337  iso-access-notes.md
```

## 3b. `01-books/` 输入完整性清单（5 文件 · SHA-256）

```
dde3a75fceed3be47d5c853fcbb5da8680ae6fa04098a78b7683f64968978ac3  D-book-candidates.json
2376a93ff1db82108418c92e3119ba977aedd43be3289d48944e46c00f379edf  books-candidates.md
f3416b2e0b58dce33bb8651237c30f6c2d209c9a346ee2c43c11087c2475e046  fetch-log.md
92ac5f5fc6a350bf4149fa91c41c97d2a81d6545f2580dad4e123016a8f8c6e6  free-official-extracts.json
1a968519bb189c0a16279b135eb6eb95075dba93cbbba5798c8a878ca58cd221  gap-request.md
```

---

## 4. 数据规模实测（用于版式设计的素材预算）

| 指标 | 实测值 |
|---|---|
| 节点 / 边 | 167 / 360，`dag_acyclic=true`，`validate_graph` errors=0 |
| 层分布 | essence 51 + methodology 67 + technology 31 + case（layer=null）18 |
| 边字段 | **`from` / `to`**（非 `source`/`target`）、`id`/`type`/`label`/`directed`/`weight`/`sources` |
| 边类型分布 | derives_from 69 · **case_instance 69** · implements 59 · **prerequisite 58** · combination 36 · dependency 24 · **contrasts 14** · enables 13 · refines 13 · **conflicts 4** · cross_reference 1 |
| 邻域规模（用于局部 SVG） | 1 跳：min 1 / 中位 4 / max 13 ；2 跳：min 2 / **中位 14** / max 45 |
| 孤立节点 | **0**（度=0 节点为 0，含 case 层） |
| 正文长度（definition + 4 detail 字段） | min 1501 / **中位 1536** / max 1813 字 |
| detail 字段键 | `principle` / `mechanism` / `engineering` / `tradeoff`（四字段全覆盖） |
| 有 case / aliases / tags 的节点 | 41 / 167 / 167 |
| priority 分布 | P0 78 · P1 78 · P2 11 |
| stage 分布 | basic 32 · intermediate 90 · advanced 45 |
| 参与 prerequisite 的节点 | 74（→ 学习路径条） |
| 参与 conflicts/contrasts 的节点 | 35（→ 对比表卡） |
| glossary 词条 | 174（→ 术语内联） |
| `verified` 取值分布 | **`true` 149 个 / `"cited"` 18 个**（敏感度：必须用 `is True` 判断，用真值判断会把 `"cited"` 误计为 true） |
| `verified=true` 占比（GR-10） | **149/167 = 89.22%**（阈值 ≥80%，PASS） |
| 可溯源率（`verified ∈ {true,"cited"}`） | **167/167 = 100%**（阈值 ≥95%，PASS） |

### 4b. 页面骨架实测（改造对象，取 `MTH-F-02.html`）

`crumb → h1 + badges → navseq → section(What: h2 + brieflead) → section(Why: h2 + whybox>p) → section(How: h2 + 2×bullet) → section(权衡: h2 + bullet) → section(相关边: h2 + chips) → section(信源与核验: h2 + evidence rows) → footer`

问题量化：全页仅 **1 个 `<p>`**、**24 个 `div`**、**6 个 `h2`**、**0 图 0 表**、**无 TOC/锚点/章节编号**；每个 `detail` 字段被压成一段 400–600 字不间断卡片。

---

## 5. 纠偏记录（对前序文档/主Agent 口述的实测修正）

| 原表述 | 实测真相 | 处置 |
|---|---|---|
| 接力文档：`verified=true` 89.22% | **接力文档正确**：实测 `true` 149 个 + `"cited"` 18 个 = 167，故 89.22% 成立 | 主Agent 曾误用真值判断得出「167/167=100%」并据此写「疑为另一口径」——该纠偏**本身是错的**，已于本节撤回；修正后两口径均 PASS（GR-10 89.22%≥80%；可溯源率 100%≥95%） |
| 接力文档：首次推送需 `gh auth refresh --scopes workflow` | `gh auth status` 实测 scope **已含 `workflow`** | 跳过该步骤 |
| 接力文档：跨库深链 70 条 / 30 文件 | 实测 **108 处**，分布 11-node-pages(29 文件) + 14-views(1) + 10-dag-data(1) | 以 108 为准全量替换 |
| 主Agent 口述：2 跳邻域中位 ~10 节点 | 实测 **中位 14** | 以 14 为准做 SVG 布局上限设计 |
| 主Agent 口述：节点正文中位 ~2300 字 | 实测正文中位 **1536 字**（2308 为 HTML 正文含导航/证据后的字符数） | 以 1536 为准 |

---

## 6. 阶段6 执行层自决项（主Agent 承担，可被否决）

| # | 决策 |
|---|---|
| 17 | 新增 `16-checkpoint/gate_layout.py` 版式门控（结构块存在性 / SVG 内联有效 / 术语链接数 / 对比表布尔） |
| 18 | 新增契约 `00-plan/stage6-content-ia-spec.md`（版式规范，生成链与后续节点维护共同遵循） |
| 19 | `15-md` 镜像同步结构化块（双轨一致性原则） |
| 20 | 术语内联 = 每术语在页内**首次出现**时链 glossary |
| 21 | 不改 `10-dag-data` 数据契约；派生素材由构建期计算 |
| 22 | `12-groups` / `14-views` / `index.html` 同步套用新版式 |
| 23 | 结构化块数据依据：prerequisite 74 节点→学习路径条；conflicts/contrasts 35 节点→对比表卡；case_instance 41 节点→案例带；局部关系 SVG 全量 167 |
