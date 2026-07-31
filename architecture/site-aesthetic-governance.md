# ZQR.WORLD 审美治理与陈列复审契约

Status: active, supersedable

Effective date: 2026-08-01

Review cadence: quarterly, and before any material change to a root surface

## 1. Topic-object brief

- Topic: 一个由人类拥有、以 Markdown 与证据长期积累的公共知识机构。
- Primary object: 当前公共陈列，而不是运行中的 AGI 控制台。
- Evidence role: 展示来源、时间、摘要来源、叙事映射、修订关系与权威上限。
- Applicable lenses: object, evidence, material, temporal, institutional, editorial.
- Rejected surface shortcuts: SaaS card wall、装饰性玻璃、霓虹赛博朋克、通用 AI 大脑、伪实时遥测、以 amber/red 作为品牌色。

## 2. Candidate comparison and decision

| Candidate | Central object | Strength | Failure risk | Decision |
| --- | --- | --- | --- | --- |
| A · Current Exhibition + Registry | 一项当前论题、一个证据对象、一条来源登记线 | 五秒内辨认主对象；与静态知识发布职责一致 | 若 registry 退化成 KPI，仍会像 dashboard | adopted |
| B · Knowledge Field + Evidence Spine | 五条叙事线组成的关系场 | 能表达跨学科连接 | 首屏容易失去单一主对象；移动端可能只剩抽象说明 | retained as Atlas/Evidence grammar |

采用 A 作为 Field 的主构图；B 的优点分别进入 Atlas 的关系模式与 Evidence 的证据脊柱。该选择可由后续季度记录显式替代，不静默改写。

## 3. Non-regression invariant

Museum profile 必须继续展示【局部真理宪章】并把它视为核心展件，而不是普通卡片、背景纹理或可有可无的装饰。

验收要求：

1. 切换到 Museum 后，首页首屏出现题为“局部真理宪章”的完整器物与 accession label。
2. System / Charter Room 始终保留同一宪章对象与局部所有权语义。
3. Field 初次加载不请求 Museum-only 大图；切换 Museum 后按需载入响应式衍生物。
4. 光照与材料可以变化，标题、状态、来源和权威边界不得变化。

## 4. Curatorial state contract

| State | Meaning | Required carriers |
| --- | --- | --- |
| Displayed | 已发布且来源、元数据足以承担公共解释 | 实心 marker、文字标签、来源 |
| Current | Displayed 中的临时编辑焦点，不代表更高权威 | current marker、空间优先级、文字标签 |
| Catalogued | 已命名登记，尚未晋升为稳定结论 | 空心 marker、claim ceiling |
| Withheld | 因证据、隐私、权威或人类门禁而明确不展示/不执行 | 原因、日期、gate marker、可读留白 |
| Superseded | 被后继对象替代但仍保留的历史记录 | neutral marker、successor relation |

颜色不能成为唯一载体。Verified 使用矿物绿，Current 使用冰青；amber 只属于人类复审/门禁，red 只属于 blocked/refused/revoked。

## 5. Surface ownership

- Field: Current Exhibition + registry。
- Atlas: Constellation 与 Ledger 两种模式；Series 是二级策展路径。
- Chronicle: as-known-at 时间脊柱。
- Evidence: source / calculation / as-of / ceiling 串联的 evidence spine。
- System: Charter Room、局部所有权 topology 与唯一 negative vitrine。
- Archive: Atlas 的完整 reverse-chronological ledger 模式。
- Article: form-aware folio，加 provenance / revision / supersession rail。

## 6. Material and performance budgets

| Surface | Initial transfer budget | Material rule |
| --- | ---: | --- |
| Field homepage | 1.5 MiB | 不载入 Museum-only specimen |
| Museum homepage | 3 MiB | 使用 WebP/AVIF 衍生物，不把 archival PNG 当默认传输 |
| Normal article | 1.5 MiB before optional media | 构建期正文在远程脚本失败时仍可读 |
| Visual essay viewport | 4 MiB | 后续媒体 lazy；原图只能显式下载 |

所有内容图像应声明 width、height、srcset、sizes、loading 与 decoding；archival master 保留为来源，不直接承担默认网页传输。

## 7. Review protocol

每次 material visual change 必须保存：

1. topic-object brief 与至少两个候选；
2. 采用/拒绝动作及理由；
3. 5 surfaces × 2 profiles × 2 viewports 的 20-view screenshot matrix；
4. contrast、320px overflow、keyboard/focus、reduced-motion、print/offline 与 transfer budget 结果；
5. owner verdict；
6. 一个可被后继记录替代的 dated exhibition record。

机器检查可以否决明显失败，不能替代人的最终审美判断。

## 8. Supersession

后继记录必须写明 `supersedes`、保留本文件、解释哪些不变量继续有效。除非 owner 明确推翻，Museum 的【局部真理宪章】核心展件约束继续生效。
