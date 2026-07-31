# ZQR.WORLD 审美巅峰跃迁分析

Date: 2026-07-27

Status: implemented 2026-08-01; original advisory baseline retained for traceability

Scope: `ShepherdQR.github.io` public surfaces, shared visual system, content projection, article reader, responsive behavior, and the companion AGI control-plane aesthetic canon

Site baseline: `b11b8791e50e4f2081516b96fc9f63c178bf3c79`

Control-plane baseline: `6e822ffb3e80e059241fba95c19c599b66763973`

Implementation record:

- [Active aesthetic governance](site-aesthetic-governance.md)
- [2026-08-01 exhibition decision](exhibitions/2026-08-01-aesthetic-summit-record.md)
- [48-view visual regression QA](visual-regression/2026-08-01-aesthetic-summit-qa.md)
- [Implementation closeout](task-closeouts/2026-08-01-site-aesthetic-summit-implementation-closeout.md)

## Decision

> `ZQR.WORLD` 的巅峰形态不是“更漂亮的博客”，也不是“更黑、更玻璃、更像控制台”，而是从一组双主题页面跃迁为一座可进入、可策展、可追溯、会承认修订、过期与拒绝的个人知识机构。

当前站点已经拥有优秀的受治理器物与馆藏基座：明确身份、Field/Museum 双材料、档案铭牌、制度器物、语义状态、长文 folio、响应式与本地可重建管线。真正的上限不再由颜色、阴影和动画决定，而由以下问题决定：

1. 每个页面是否有一个五秒内可辨认的主对象；
2. 每种颜色、空白、计数和状态是否只承担一种可信语义；
3. 站点投影是否忠实表达内容、证据、时间与权威边界；
4. Field、Atlas、Chronicle、Evidence、System、Archive 是否成为六种不同的认知器具；
5. 视觉质量是否像代码一样可重建、可回归、可否决。

建议采用 **“双材料、同语义、同机构”** 的峰值方向：

- `Field` 不是普通浅色主题，而是日光下的研究与修复室；
- `Museum` 不是普通暗色主题，而是夜间的制度展厅；
- 两者展示同一批知识对象、同一状态、同一来源和同一权威边界，只改变光照与材料温度；
- 页面不再靠卡片数量制造丰富，而靠对象、登记线、证据脊柱、来源轨道和有理由的留白建立秩序。

## Executive Summary

### 已经成立的高水平基座

- `System` 是当前完成度最高的页面：主器物、权威边界、演化纪事、人类门禁和 provenance 彼此同构，已经接近控制平面的“制度器物”标准（`field.html:23-38`）。
- Field/Museum 不是简单换色。Museum 会把五张研究卡改写为登记轨道，并把文章放入暗场中的纸质 folio（`includes/css/homepage.css:648-682`; `includes/css/pages.css:636-661`）。
- 站点视觉宪章已经明确拒绝 SaaS 卡墙、赛博霓虹、通用 AI 大脑、装饰性玻璃态和无穷动画（`architecture/site-control-plane-interface-2026-07-13.md:266-336`）。
- 共享 token、键盘焦点、320px 最小宽度、响应式与 reduced-motion 已具备扎实工程底座（`includes/css/system.css:1-68, 557-625`）。

### 距离巅峰最近、也最需要先修的地方

1. **对象阶跃尚未完成。** 当前站点更像“治理过的知识馆藏”，控制平面最新 V6 已前进到“策展机构本身成为对象”。继续调色、调圆角不会完成这一跃迁。
2. **真值与视觉还没有完全闭环。** 当前 `2026-07-12` 状态快照在报告日已超过 14 天 freshness threshold，但页面没有显示 stale；这违背了站点自己的验收契约。
3. **投影卫生正在削弱高级感。** 自动摘要仍泄露 `##`，首页和 Atlas 的最新对象直接展示 Markdown 结构符；Evidence 又把自动摘录与显式摘要合并成 “Summary 100%”。
4. **语义色仍有越权。** Museum 的 verified 状态复用青色交互信号；普通 blockquote 边线与阅读进度使用琥珀作装饰，而宪章规定琥珀只能属于人类门禁、待审或拒绝夸大。
5. **部分页面仍停留在通用组件语法。** Atlas 筛选器、Evidence 统计块、Field 研究卡和浅色文章外框仍依赖圆角面板、阴影和卡片网格；System 页面反而展示了更强的页面级构图。
6. **审美尚未进入回归管线。** 2026-07-13 closeout 明确记录没有自动截图或视觉回归；实测已经发现 Museum 首页 `Control pulse` 的标题与关键数值几乎消失。

### 推荐优先序

- **P0：视觉真值基线。** 修复对比度、stale 状态、摘要污染、显式/派生摘要区分、状态色角色和正文 H1。
- **P1：制度化设计系统。** 从通用 `signal/amber/red` 迁移到角色 token；建立 Displayed / Current / Catalogued / Withheld 视觉语法；减少卡片依赖。
- **P2：页面对象阶跃。** 让 Field 成为当前展览，让 Atlas 成为关系拓扑，让 Evidence 成为证据脊柱，让 Archive 成为登记线，让 Article 成为有修订史的知识器物。
- **P3：完整材料与 QA。** 响应式图像衍生物、主题按需加载、构建期 Markdown、20 视图截图矩阵和完整视觉回归。

## 1. Research Question And Method

### 1.1 Research question

如何在不破坏 Markdown-first、静态 GitHub Pages、人类发布门禁与长文阅读性的前提下，把控制平面最新审美机制迁移到 `ZQR.WORLD`，并使站点从“强设计个人网站”跃迁为“制度诚实的个人知识机构”？

### 1.2 Method

本报告采用四层证据：

1. 控制平面具约束力的 V4/V5/V6 审美叙事线与 visual hard rules；
2. 控制平面 2026-07-26 最新 V6 成品、source note 和 QA；
3. 本站视觉契约、CSS、JavaScript、生成器和内容投影；
4. 2026-07-27 本地 Chromium 实测：
   - desktop: `1440 × 1100`;
   - mobile: `390 × 844`;
   - surfaces: Field, Atlas, Evidence, System, Article;
   - profiles: Field and Museum.

本报告不把固定尺寸海报 CSS 当作响应式网页方案，也不把外部设计趋势当作最终权威。它学习控制平面的机制，不复制其品牌或单一表面风格。

## 2. Source Register

在下表中，`control-plane::` 表示 companion repository `symbiotic-constraint-field-control-plane` 内的路径。

| ID | Source | Date/version | Used for | Confidence |
| --- | --- | --- | --- | --- |
| CP-V4 | `control-plane::policies/high-taste-aesthetic-narrative-line-v4.md:10-25, 47-109, 129-143` | V4 | 高品味不是风格；五类 lens；对象、材料、构图、时间与交互评价维度 | High |
| CP-V5 | `control-plane::policies/adaptive-aesthetic-intelligence-line-v5.md:9-39, 75-136` | V5 | 按主题重推导、topic-object brief、负面约束、人类审美仲裁 | High |
| CP-V6 | `control-plane::policies/curatorial-governance-aesthetic-line-v6.md:14-51, 53-96, 98-142, 144-190` | 2026-07-26 / V6 | 对象阶跃、负展柜、策展寄存器、角色色、留白权力、生产纪律 | High |
| CP-HARD | `control-plane::policies/visual-aesthetic-hard-rules.md:111-181, 194-250` | v0.1 + V4/V5 binding | 中央证据对象、反卡墙、材料/色彩、来源轨道、密度、可重建与候选比较 | High |
| CP-V6-ARTIFACT | `control-plane::artifacts/posters/2026-07-26-agi-structure-curatorial-16x9/` | 2026-07-26 | V6 的 hero、negative vitrine、registry、字体职责、确定性文字层与 QA | High |
| CP-SITE-PLAN | `control-plane::reports/target-onboarding/shepherdqr-site/03-site-publishing-forms-and-durable-development-plan-2026-07-16.md:23-34, 149-160, 217-230, 345-365` | 2026-07-16 | 站点长期价值、知识对象链、页面职责和明确拒绝项 | High |
| SITE-CONTRACT | `architecture/site-control-plane-interface-2026-07-13.md:75-154, 202-264, 266-336, 370-398` | 2026-07-13 | 当前六层信息架构、状态语义、双视觉、freshness 和验收边界 | High |
| SITE-SYSTEM | `includes/css/system.css` | inspected 2026-07-27 | 当前 token、状态 chip、焦点、响应式和 reduced-motion | High |
| SITE-SURFACES | `includes/css/homepage.css`, `includes/css/archive.css`, `includes/css/field.css`, `includes/css/pages.css`; root HTML surfaces | inspected 2026-07-27 | 页面构图、卡片语法、文章 folio、Museum 差异化和实现缺口 | High |
| SITE-DATA | `scripts/generate_homepage_data.py`, `includes/js/home-page.js`, `includes/js/stats-page.js`, `data/site-plane.json` | inspected 2026-07-27 | 摘要来源、taxonomy 映射、统计语义、快照 freshness | High |
| BROWSER-AUDIT | local Chromium at desktop/mobile viewports | 2026-07-27 | 实际构图、对比度、摘要污染、导航密度和主题表现 | High |

## 3. Current Baseline

### 3.1 当前不是“缺美学”，而是“美学尚未完全宪法化”

现站的基础明显高于普通个人博客：

| Dimension | Current maturity | Evidence |
| --- | --- | --- |
| Identity and thesis | High | `Pursuing Immortality` 与中文约束主张建立清晰第一印象 |
| Information architecture | Medium-high | Field / Atlas / Evidence / System 已成立，但 Chronicle / Archive / Series 的层级仍压缩或重叠 |
| Material language | High on System; medium-high overall | System 的器物与边界同构；其他页面仍有面板化残留 |
| Typography | High | 大标题、中文长文、mono 元数据已有职责分工 |
| State semantics | Medium | 状态色和 as-of 存在，但 verified、stale、summary provenance 尚未闭环 |
| Long-form reading | Medium-high | Museum folio 很强；正文层级、目录与 form-aware 模板仍需收口 |
| Responsive/accessibility | High baseline | 390px 无横向溢出；skip link、focus、reduced motion 已存在 |
| Visual QA and performance | Low-medium | 无自动视觉回归；首屏隐藏图仍加载；大图成本高 |

### 3.2 System 是当前审美标杆

`field.html` 的成功不在于它使用了冷玻璃图，而在于页面每一部分都回答同一个制度问题：

- hero 是“局部真理宪章”器物；
- Boundary 将证据、生命周期和权威效果分开；
- Chronicle 保留 dated baseline；
- Gates 把未释放权威放在门外；
- Provenance 让来源轨道安静但不消失。

这正是“对象、材料、状态、时间、来源同构”。后续页面升级应以此为标杆，而不是以增加更多玻璃卡片为目标。

### 3.3 当前站点位于 L2 与 L3 之间

控制平面 V6 的对象阶梯是：

```text
L0 styled diagram
-> L1 governed artifact
-> L2 governed collection
-> L3 curatorial institution
```

本站 2026-07-13 视觉契约以 `agi-structure-plan-nine-grid-v2.png` 为 canonical reference，并围绕双主题展示一组治理过的对象（`SITE-CONTRACT:297-324`）。因此可作如下**推断**：

- 当前强项接近 L2：同馆、成组、同一材料与状态语义；
- 巅峰目标应进入 L3：站点的策展行为本身成为主对象，清楚表达什么被展示、什么只是登记、什么因证据或权威不足而被保留。

这意味着下一步不是“再做一次 dark mode polish”，而是改变页面的对象类别。

## 4. Control-Plane Aesthetic DNA

### 4.1 高品味不是预装风格

V4 明确拒绝把 dark、minimal、cinematic、museum-like 或 luxury 本身当作高品味；高品味来自对象、证据、材料、时间、构图、文字、互动和生产方法的一致（`CP-V4:10-25`）。

V5 进一步要求大型网站刷新先回答：

- 主题是什么；
- 主对象是什么；
- 它承担什么证据角色；
- 哪些 lens 真正适用；
- 哪些表面风格必须拒绝；
- 候选如何比较；
- 人类审美仲裁在哪里进入。

所以本站不能把控制平面黑色海报原样网页化。个人知识站的核心对象不是“运行中的 AGI”，而是长期修订的公共知识、研究证据、思想路径和人的主权。

### 4.2 对象主权

每个高可见页面都应在五秒内让读者知道“我正在看什么”。

- Field：当前知识场或当前展览；
- Atlas：关系拓扑与学习路径；
- Chronicle：带日期的演化脊柱；
- Evidence：证据、验证与反例器物；
- System：边界与局部所有权拓扑；
- Archive：完整 accession ledger；
- Article：一个有来源、版本、修订和状态的知识对象。

当页面只能被描述为“标题 + 若干卡片”，对象主权尚未成立。

### 4.3 策展寄存器

V6 的正式三寄存器可直接迁移为网站语法：

| Register | Site meaning | Visual grammar |
| --- | --- | --- |
| Displayed / 已陈列 | 已发布、证据与元数据足以承担公开解释的对象 | 完整对象、充分光照、实心 marker、明确来源 |
| Catalogued / 已登记 | 已命名、已界定，但尚未晋升为稳定结论的研究问题或记录 | 文字与索引为主、空心 marker、显示 claim ceiling |
| Withheld / 依宪保留 | 因证据、隐私、权威或人类门禁而明确不发布/不执行 | 有标签的留白、门禁原因、日期；绝不是 “coming soon” |

`Current / 当前` 可作为 Displayed 的临时强调层：它表示当前研究或编辑焦点，不等于更高权威。

`Superseded / 已替代` 属于历史生命周期，不应使用红色惩罚；应以中性档案语法保留旧版本和替代关系。

### 4.4 留白必须可读为决定

V6 的核心创新不是更多黑色，而是“负展柜”：一个明确框定、明确空置、写明原因和日期的位置。它只适用于真实的拒绝或门禁。

对本站的正确迁移：

- System 可保留一个 “runtime autonomy / target write / autonomous publish” 负展位；
- Research Log 可显示“证据不足，暂不晋升”的登记状态；
- 首页不应把普通空白或缺内容包装成制度留白；
- 如果遮住文字后，空白只像“页面没填满”，则留白权力测试失败。

### 4.5 材料必须承担语义

推荐把现有双主题重新定义为两种机构光照：

| Layer | Field / 日光研究室 | Museum / 夜间展厅 | Shared invariant |
| --- | --- | --- | --- |
| Ground | warm paper, ink, archival rule | obsidian, graphite, platinum hairline | 内容和状态不变 |
| Evidence object | diagram, folio, index, marginalia | conserved artifact, vitrine, accession label | 来源可追踪 |
| Long reading | paper surface | archival folio inside dark hall | 正文对比度与行长不牺牲 |
| Metadata | quiet mono | quiet mono | 只用于 id、日期、状态和路径 |
| Accent | mineral green / structural blue | glacial cyan / verified green | 角色先于色值 |
| Gate/refusal | restrained amber/red | restrained amber/red | 不得作装饰 |

### 4.6 可重建性是审美的一部分

控制平面的生产纪律是：

```text
AI image generation -> no-text material layer only
deterministic renderer -> language, labels, states, signature
Markdown + QA -> design intent, mapping, audit trail
```

网站对应版本应是：

```text
Markdown / JSON source
-> deterministic build
-> semantic HTML and role tokens
-> responsive image derivatives
-> validator + screenshot matrix + human pairwise review
```

## 5. Gap Matrix

| Priority | Dimension | Current evidence | Peak gap | Required decision |
| --- | --- | --- | --- | --- |
| P0 | Museum contrast | Museum 将 `--paper-0` 变为 `#0b1112`，但 dark `Control pulse` 的标题和数值仍用 `var(--paper-0)`（`system.css:43-68`; `homepage.css:99-108, 212-250, 627-645`） | 关键状态在真实渲染中几乎消失 | 引入 artifact-local foreground tokens，并做 computed contrast 回归 |
| P0 | Freshness truth | baseline `as_of=2026-07-12`，threshold 14 days；报告日已相隔 15 天（`data/site-plane.json:46,190`） | 页面只显示 dated projection，没有 visibly stale；违反 `SITE-CONTRACT:387-388` | 构建或运行时计算 stale，Field/Evidence/System 同步降级显示 |
| P0 | Summary hygiene | `markdown_excerpt()` 只删除第一个标题（`generate_homepage_data.py:65-79`） | 最新摘要仍含 `##`，破坏出版完成感并进入 metadata/Atom | 删除所有结构符或取首个非标题段；featured 要求显式摘要 |
| P0 | Summary provenance | 生成器给所有条目补摘录，Evidence 直接统计非空 summary | “Summary 100%” 把 19 个显式摘要与 144 个派生摘录混为一谈 | 生成 `summarySource: explicit | derived` 并分别计数 |
| P0 | State color | verified/active/completed 使用 `--signal`；Museum 的 `--signal` 是 glacial cyan（`system.css:43-68, 436-461`） | verified 与 research/current 信号混色 | 建立 `--state-verified/gate/blocked/simulation/current/catalogued` |
| P0 | Heading semantics | renderer 只剥离首个匹配 H1；目录只收 H2/H3；正文无现代 H1 规则 | 多 H1 破坏文章对象层级和移动端节奏 | 构建期标题规范化 + validator hard warning threshold |
| P2 | Object class | 首页为 hero + control card + research cards；Evidence 为 metrics + panel grid | 页面仍可被概括成卡片集合 | 让每个 surface 拥有唯一主对象和空间语法 |
| P1 | Knowledge topology | 163 objects 中只有 19 个 tags、19 个 series；五线推断只覆盖约 18 个对象，Books 映射为 0 | “阅读、文学与诗 3 objects” 与 127 Books 的真实 corpus 不一致 | 新增显式 `field_ids` / narrative mapping，并显示 `mapped / total` |
| P2 | Surface separation | Atlas 与 Archive 合并；Chronicle 嵌入 System；Evidence 主要是统计板；Series 占主导航 | 六层架构没有六种认知体验 | 逻辑分离六 surface；不要求六个顶级导航，但要有六种明确模式 |
| P2 | Card grammar | `.field-card`, `.atlas-controls`, `.stats-block`, light `.article-frame` 依赖圆角、阴影、blur（`homepage.css:271-298`; `archive.css:89-103,343-351`; `pages.css:627-634`） | 与“中央对象，不是 generic card wall” hard rule 冲突 | 用 registry、rail、folio、topology、instrument 替代主构图卡片 |
| P2 | Article semantics | 所有内容形态共用同一 shell；相邻文章仍是 card 语法，form 差异主要停留在正文内容 | 诗、读书、研究日志、Visual Essay 的对象差异被抹平 | 建立 form-aware article variants，共享 shell 与 provenance |
| P3 | Performance/material truth | 首页隐藏 Museum 图片仍下载；两张主图约 7.78 MiB；Thoughts 0028 三图约 23.44 MiB | 视觉奢华由超大源图支付，移动端材料逻辑不可信 | archival master + AVIF/WebP derivatives + theme-lazy loading + image budget |
| P3 | CSS lineage | `pages.css` 保留旧全局层，现代层后置覆盖；`series.css` 又建一套 token | 细节 tolerance 与 shared shell 被历史层削弱 | 拆出 legacy exception stylesheet；Series 回到共享 shell |
| P0/P3 | Visual QA | closeout 明确无自动 screenshot regression | 对比度错误只能靠偶然人工发现 | P0 建最小基线；P3 扩展为 5 surfaces × 2 profiles × 2 viewports 的 20-view matrix |

## 6. Peak Vision: A Personal Knowledge Institution

### 6.1 北极星

峰值对象不是 homepage、dark theme 或 AGI diagram，而是：

> **一座由人类拥有的、会持续修订的公共知识策展机构。**

它以 Markdown 为藏品源，以 build/validator 为修复与登记流程，以 Field/Atlas/Chronicle/Evidence/System/Archive 为六种公共解释器，以发布门禁保证“展出不产生额外权威”。

### 6.2 三档阅读距离

控制平面要求视觉对象在 3 秒、30 秒和 3 分钟三个距离成立。网站可落实为：

| Distance | Reader should learn | Design proof |
| --- | --- | --- |
| 3 seconds | 这里是谁、研究什么、当前主对象是什么 | thesis + one current object + one state/date |
| 30 seconds | 对象的状态、来源、边界和进入路径 | accession label + register + provenance rail |
| 3 minutes | 如何追溯证据、修订、相关系列与下一门禁 | article/series/archive relations + revision history |

当前首页 3 秒层很强，但 30 秒层被 `Control pulse` 卡片和五张研究卡分割；峰值方案应把它们收束为一个 current exhibition 与一条 registry。

### 6.3 推荐方向比较

| Candidate | Strength | Risk | Verdict |
| --- | --- | --- | --- |
| A · Pure Field | 最适合长文、文学和日常阅读；温暖、可信、维护简单 | 制度器物、时间密度与对象主权不足；易退回“高雅博客” | 保留为材料 profile，不作为唯一方向 |
| B · Pure Museum | 识别度最强；证据、门禁和来源语义天然清楚 | 阅读疲劳；容易让个人知识站看起来像运行中的 AGI 控制台；大图和暗场成本高 | 只用于少量高后果 surface/hero |
| C · Institutional Bitemporality | 同一机构在日光研究室与夜间展厅中的两种光照；阅读与制度语义兼得 | 需要更严格的 component/state contract 和 visual QA | **Recommended** |

Candidate C 不取消 profile switch，而是让切换从“换皮”升级为“改变光照，不改变机构语义”。

## 7. Surface-by-Surface Blueprint

### 7.1 Field: Current Exhibition

当前优势：主标题极强，身份清晰，Field/Museum 首屏均有辨识度。

目标结构：

1. 一个当前主论题；
2. 一个 current evidence object；
3. 一条 compact registry：as-of、state、source、claim ceiling、next human gate；
4. 五条 narrative lines 作为关系场或登记轨道，不再是五张等价卡；
5. 最近证据作为 acquisition log；
6. 作者与四条原则作为 charter，而不是普通 About。

具体调整：

- 把 `Control pulse` 从独立深色卡改成 hero 的右侧 accession/provenance rail；
- Field profile 用纸面/细规则，Museum profile 才展示材料器物，但 DOM 与层级一致；
- 显示 `mapped / total corpus`，避免 “3 objects” 被误读为全站只有 3 个文学对象；
- 减少 hero 未标注的空白；若保留大空场，必须由日期、来源或 withheld 语义使其成为决定；
- 移动端在首个 viewport 内至少露出 current object 的标签或上缘，而不是只看到文案与按钮。

### 7.2 Atlas: Relationship Instrument

当前 Atlas 的标题、年份 ledger 和条目排版很好；上限主要受 sticky rounded filter panel 与 taxonomy coverage 限制。

目标结构：

- 顶部是三条 curated path，而不是立即出现全部筛选器；
- 筛选器改成 archival index rail：搜索、field、form、year、series、tag；
- 内容区可切换 `Constellation / Ledger`：
  - Constellation 展示关系与学习路径；
  - Ledger 保留高密度完整清单；
- 每个结果显示 state marker、summary source、revision/supersession；
- Series 是 Atlas 的二级策展路径，除非连续两个季度证明其独立导航价值。

### 7.3 Chronicle: Temporal Spine

Chronicle 不一定立刻成为顶级导航，但必须成为独立空间语法：

- vertical or horizontal dated spine；
- accepted、refused、rolled_back、superseded、candidate 清楚区分；
- 历史记录保持 `as-known-at`，新结论用 relation 覆盖，不静默重写；
- 当前节点使用 cyan/current，不使用 green/verified；
- 只在真实门禁处使用 amber/red。

### 7.4 Evidence: Evidence Spine, Not KPI Dashboard

当前 Evidence 首部的大数字排版优秀，但下方 rounded panel grid 更像统计 dashboard。

峰值方案：

- 保留一个 corpus readout 横条；
- 将 metadata、authority、collections、years、baseline、recent objects 串成一条证据脊柱；
- 每项显示 source、calculation、as-of 和 coverage ceiling；
- 把 `Explicit summary` 与 `Derived excerpt` 分开；
- 增加 narrative mapping coverage、revision chain、stale objects、broken provenance 等机构质量指标；
- 不用绿色表示“数字很好”，绿色只表示已验证证据。

### 7.5 System: Charter Room

System 是现有标杆，应以少改动、高精度为原则：

- 保留 hero 器物、边界、loop、Chronicle、gates、provenance；
- 增加稀疏 topology，说明 human、site、control plane、target repos 的局部所有权；
- 加入 stale state，并在过期时降低“current”视觉权重；
- 负展柜只保留一个，明确写出 autonomous publishing/runtime/target write 的拒绝条件；
- 不新增 activate、connect、grant、publish 等伪运行控件。

### 7.6 Archive: Accession Ledger

Archive 应从 Atlas 中逻辑分离，即便短期仍共享路由或组件：

- 完整 reverse-chronological ledger；
- neutral marker 表示 archived/superseded；
- revision/successor links；
- 允许高密度、低装饰、快速扫描；
- 不承担关系图谱、精选路径或排名。

### 7.7 Article: Knowledge Object And Folio

现有 Museum folio 是正确方向，但需要从“统一 shell”进入“对象类型适配”：

| Form | Primary visual object |
| --- | --- |
| Exposition / Essay | thesis + section architecture + provenance margin |
| Research Log | dated attempts, uncertainty, eliminated paths, next gate |
| Project / Experiment | artifact, reproduction path, validation, failure boundary |
| Visual Essay | responsive material object + textual claim + static fallback |
| Book / Reading Constellation | work metadata + comparison axis + author judgment |
| Poetry / Literature | text block, cadence, edition/context; avoid technical chrome overload |

所有 form 共享：

- title、date、status、summary source；
- provenance / revision / supersession rail；
- accessible heading hierarchy；
- neutral object index；
- previous/next relationship；
- print style；
- Field/Museum identical content semantics。

立即修正：

- article object index 保持 neutral rule，active section 使用 current/signal 角色色，不引入 amber 装饰；
- reading progress 从 `signal -> amber` gradient 改为 neutral/current 单一角色色（`pages.css:910-925`）；
- blockquote 的琥珀边线只用于明确 caution/gate；普通引文使用 neutral rule（`pages.css:782-788`）；
- image-heavy、诗歌或短铭文不强行显示失真的 “1 min read”。

## 8. Design-System Governance

### 8.1 Role tokens

从通用气氛 token 迁移到语义 token：

```css
--surface-field;
--surface-folio;
--surface-vitrine;
--text-primary;
--text-secondary;
--text-archival;
--state-displayed;
--state-current;
--state-catalogued;
--state-verified;
--state-gate;
--state-blocked;
--state-simulation;
--state-superseded;
--rule-hairline;
--focus-ring;
```

角色建议：

| Role | Color family | Prohibited use |
| --- | --- | --- |
| Displayed / earned | ivory/ink | 不代表“最新” |
| Current / research path | glacial cyan | 不代表 verified |
| Verified | mineral green | 不作普通链接/hover |
| Structural/math | restrained blue | 不代表 simulation unless labeled |
| Human gate/review | amber | 不作进度条、目录装饰、普通强调 |
| Blocked/refused/revoked | red | 不作品牌装饰、hover、营销 CTA |
| Catalogued/dormant | graphite/hollow | 不伪装成 disabled error |

### 8.2 Typography

采用职责分工，不追求字体数量：

- 中文论题与长文：serif，承担思想与阅读；
- Latin display / accession label：serif small caps，承担机构铭牌；
- sans：导航、解释、交互；
- mono：id、date、state、path、receipt，禁止扩张成通用“科技感”。

当前 `--font-display`, `--font-sans`, `--font-mono` 已有好基础（`system.css:30-32`）。实施时优先校准字号、字重、行高和中英混排；若自托管字体，必须做中文 subset、fallback 与加载预算，不得以 FOIT 换“高级感”。

### 8.3 Geometry

- 主构图以 column、rail、ledger、folio 和 topology 为单位；
- 26px 大圆角只保留给真正可触摸的独立对象，不作为默认容器；
- Museum 采用 0–2px 器物边界，Field 采用纸页/细规则；
- shadow 表达层级与材料厚度，不表达“这是一个组件”；
- controls 可以有小圆角，但筛选器整体不应成为漂浮玻璃卡；
- 所有 hairline、crop、seam、caption 与 signature 属于同一细节系统。

### 8.4 Image and material pipeline

当前源图应保留为 archival master，但不应直接成为网页默认传输：

- `topos-asi-shadow-luxury-image-v2.png`: 6,003,782 bytes；
- `QirongZHANG.png`: 2,148,914 bytes；
- `agi-structure-plan-nine-grid-v1.png`: 9,250,309 bytes；
- `agi-structure-plan-nine-grid-v2.png`: 9,321,747 bytes。

实施规则：

1. 生成 960 / 1440 / 2160 宽 AVIF/WebP 衍生物；
2. 设置 `width`, `height`, `srcset`, `sizes`, `loading`, `decoding`；
3. Field 不加载 Museum-only specimen；
4. 首屏主对象可有 `fetchpriority=high`，其他对象 lazy；
5. 生成图只承担无文字材料层，所有标题、状态和来源由 HTML 确定性渲染；
6. Visual Essay 必须有 static fallback 和 alt/long description。

## 9. Motion, Accessibility, And Performance

### Motion

保留当前克制原则：

- 只允许状态切换、筛选结果和 reading progress 的有限过渡；
- 不使用无限扫描、pulse、shimmer、particles、parallax；
- `prefers-reduced-motion` 继续 hard-disable 动画；
- motion 不能暗示系统正在自主运行。

### Accessibility

- body text contrast ≥ 4.5:1；
- large text and UI boundaries ≥ 3:1；
- 所有状态除颜色外还有文字、形状或 marker；
- 320px 起无水平溢出；
- focus visible 不被 Museum theme 吞没；
- skip link、heading outline、landmarks、aria-live 保持可用；
- article index、filter、theme switch 全键盘可达。

### Performance

建议预算：

| Surface | Initial transfer target | Notes |
| --- | ---: | --- |
| Field profile homepage | ≤ 1.5 MiB | 不加载 Museum specimen |
| Museum profile homepage | ≤ 3 MiB | 使用响应式衍生物，不传 archival master |
| Normal article | ≤ 1.5 MiB before optional media | 正文必须在 CDN/JS 失败时可读 |
| Visual Essay initial viewport | ≤ 4 MiB | 后续图像 lazy；原图提供显式下载 |

构建期 HTML 是最终耐久方向：远程 `marked` 失败时，正文的机构级排版不应消失。运行时 JavaScript 只负责目录、进度、筛选与渐进增强。

## 10. Phased Roadmap

### P0 — Aesthetic Truth Baseline

Estimated scope: 1–3 focused implementation days.

1. 修复 Museum `Control pulse` 前景 token 与所有关键组件对比度。
2. 实现 freshness calculation；过期后 Field/Evidence/System 显示 `stale / requires re-observation`。
3. 修复 `markdown_excerpt()`：
   - 删除所有标题结构符；
   - 优先首个非标题段；
   - featured/newest 若无显式 summary，validator 给出 warning。
4. 生成 `summarySource`，Evidence 分开显示 explicit/derived。
5. 拆分 state role tokens；清除普通 blockquote/progress 的装饰性 amber。
6. 构建期规范化正文 H1/H2，并扩展 validator。
7. 建立最小 screenshot matrix 与 contrast smoke。

Stopping condition: 所有 P0 acceptance metrics 通过，页面结构不做大改。

### P1 — Constitutional Design System

Estimated scope: 1–2 weeks.

1. 先写 topic-object aesthetic brief，比较至少两个候选，而不是直接改 CSS。
2. 定义 Displayed / Current / Catalogued / Withheld / Superseded 的数据与视觉契约。
3. 将 shared tokens 改为 role tokens。
4. 建立 registry、provenance rail、evidence spine、folio、state marker、negative vitrine 六个核心 primitive。
5. 收口 Series 和 article shell；隔离 legacy CSS。
6. 新增显式 narrative mapping 与 taxonomy coverage。

Stopping condition: component/state contract 稳定，Field/Museum 的同语义测试通过。

### P2 — Signature Surface Recomposition

Estimated scope: 2–4 weeks, staged.

1. Field：current exhibition + registry，移除五张等价卡的主构图地位。
2. Atlas：relationship mode + ledger mode。
3. Evidence：从 panel grid 改为 evidence spine。
4. Article：推出 2–3 个最高价值 form variants，不一次铺开全部形态。
5. System：补 sparse topology、stale 和单一 negative vitrine。
6. Archive/Chronicle：形成各自空间语法，可先共享数据层。

Stopping condition: 3 秒/30 秒/3 分钟阅读测试和人类 pairwise review 通过。

### P3 — Material And Institutional Durability

Estimated scope: one quarter, incremental.

1. responsive image derivatives and budgets；
2. theme-aware lazy loading；
3. build-time Markdown HTML；
4. revision / errata / supersession chain；
5. full 20-view visual regression；
6. print styles, offline fallback, performance budgets；
7. quarterly human taste review and supersedable exhibition record。

Stopping condition: 每次视觉变更都能由 source、build、validator、screenshots 和 owner decision 重建。

## 11. Acceptance Metrics

### Truth and projection

- baseline 超过 freshness threshold 后 24 小时内自动显示 stale；
- homepage/Atlas/metadata/Atom 中自动摘要出现 `#`, fenced code, raw link syntax 的数量为 0；
- Evidence 分别显示 explicit summary 与 derived excerpt；
- narrative lines 显示 `mapped / total`，不把局部映射伪装成 corpus 总量；
- Displayed 项均能追溯到 Markdown/JSON source；否则降级为 Catalogued。

### Semantic aesthetics

- amber/red 的每次出现都能在 DOM class/data-state 或 source note 中解释；
- verified 不再复用 current/research signal；
- 关闭颜色后，Displayed / Current / Catalogued / Withheld 仍能通过形状、marker、位置或文字区分；
- 每个 root surface 能在五秒内指出唯一主对象；
- above-the-fold 不出现由四张以上等价圆角卡组成的主构图。

### Visual QA

Baseline matrix:

```text
Field / Atlas / Evidence / System / representative Article
× Field / Museum
× 1440×1100 / 390×844
= 20 screenshots
```

每个候选记录：

- viewport and profile；
- central object；
- provenance visibility；
- contrast and smallest-label legibility；
- grayscale/value-map result；
- overflow, overlap, crop, seam；
- hover, focus, empty, stale, blocked and reduced-motion states；
- adapted moves, rejected moves and human verdict。

### Accessibility and engineering

- `git diff --check`;
- deterministic build produces no unrelated drift；
- `python -B scripts/validate_site.py --max-warnings 50` passes；
- template tests and JavaScript syntax checks pass；
- body contrast ≥ 4.5:1, large/UI ≥ 3:1；
- 320px no horizontal overflow；
- keyboard/focus/reduced-motion smoke passes；
- image and initial-transfer budgets pass；
- CDN or runtime Markdown failure does not erase article content after build-time rendering lands。

## 12. Risks And Forbidden Shortcuts

| Shortcut | Why it fails |
| --- | --- |
| 把全站改成黑底玻璃 | 复制材料而非机制，伤害长文与文学内容 |
| 增加更多圆角卡和 glow | 以组件数量替代主对象，违反 evidence-object hard rule |
| 把个人站做成 live AGI console | 视觉暗示超出 L1 只读权威，混淆公共知识与运行态 |
| 用 amber/red 做品牌强调 | 破坏门禁与拒绝语义 |
| 把普通空白叫作负展柜 | 没有真实 gate/charter 的空白只是未完成布局 |
| 一次新建十多个页面/类型 | 维护负担替代知识结构；应先用 form 和 view 演进 |
| 为“高级感”引入 SPA/CMS/framework | 破坏当前静态、可审计、低依赖优势 |
| 原图直接上首屏 | 把材料质量建立在不可持续传输成本上 |
| 自动评分决定最终方向 | 控制平面明确保留人类审美仲裁 |
| 只改 CSS 不改数据投影 | `##` 摘要、虚假 coverage 和 stale 状态会继续破坏可信度 |

## 13. Recommended Next Task

下一项不应是整站重构，而应是一个可独立交付的：

> **P0 Aesthetic Truth Baseline / 审美真值基线**

建议交付物：

1. Museum contrast 修复；
2. role-based state tokens；
3. stale projection；
4. clean excerpt + `summarySource`；
5. article heading normalization；
6. 20-view baseline 中先完成 8 个关键截图：
   - Field home desktop/mobile；
   - Museum home desktop/mobile；
   - Atlas desktop；
   - Evidence desktop；
   - System desktop；
   - representative Article desktop；
7. validation and a short closeout。

完成 P0 后，再制作两个首页对象阶跃候选：

- Candidate A: `Current Exhibition + Registry`;
- Candidate B: `Knowledge Field + Evidence Spine`.

用同一内容、同一 viewport、同一状态和同一来源做 pairwise review，再由 owner 选择 P2 的主方向。

## 14. Final Assessment

本站离巅峰已经不是“美不美”的距离，而是：

> **每一处美是否都忠实承载对象、状态、来源、时间、边界与权威。**

当前最可贵的资产不是某个色值、某张九宫格或某个 dark-mode 组件，而是已经形成的制度诚实：证据先于完成，消息不产生权威，局部真理不被覆盖，演化必须可回滚。

审美达到巅峰的时刻，将不是页面看起来最“贵”的时刻，而是读者无需阅读长篇解释，也能从对象、光照、留白、登记线、状态 marker 和来源轨道中准确感到：

- 什么已经赢得展示；
- 什么仍在研究；
- 什么只是登记；
- 什么因证据或权威不足而被保留；
- 谁拥有最后决定；
- 这次陈列何时会被复审与替代。

这才是控制平面审美在 `ZQR.WORLD` 上最完整、也最不可替代的迁移。
