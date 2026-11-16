# 开放知识地图

2026-11-16 · 分类版本 `2026.11.16`

首页以人类与 AI 的全部知识领域为持续维护目标。当前版本提供 30 个领域、220 个分支，与公开书籍、思考、学习和影像笔记建立多重主题关联。分类树可以继续增加层级；分类覆盖与个人研究积累分别表达。

## 完备性验收的范围

“覆盖”指下面指定版本、指定层级的每个目录条目，都有明确且经过检查的导航落点。它不代表所有知识已经穷尽、所有分支都有笔记、内容为真，或各领域已经得到同等深入的研究。

| 来源 | 版本及范围 | 对照条目 | 公开原文 |
| --- | --- | ---: | --- |
| OECD FORD | Frascati Manual 2015，表 2.2，印刷页 59；全部科研二级领域 | 42 | [OECD PDF](https://www.oecd.org/content/dam/oecd/en/publications/reports/2015/10/frascati-manual-2015_g1g57dcb/9789264239012-en.pdf) |
| UNESCO ISCED-F | 2013 分类，2015 详细说明，附录 I；全部实质详细领域 | 80 | [UNESCO PDF](https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/04/international-standard-classification-of-education-fields-of-education-and-training-2013-detailed-field-descriptions-2015-en.pdf) |
| 中国研究生教育目录 | 2022 版；117 个一级学科和全部 67 个专业学位类别 | 184 | [教育部所属学信网完整目录](https://yzst.chsi.com.cn/kyzx/jybzc/202209/20220913/2293267493.html) |
| 合计 | 三套目录之间可以重叠，不表示 306 个互不相交的领域 | **306** | 访问日期：2026-11-16 |

UNESCO 的未进一步界定、其他、跨学科与未知代码保存在来源文件的 `extendedCodes` 中，不计入 80 项实质领域。中国专业学位中的 `1051`、`1052`、`1055` 出现在一级学科条目的括注中，也纳入核对。目录中的 `0834`、`1010` 缺号保留原状。

[美国国会图书馆分类](https://www.loc.gov/catdir/cpso/lcco/)用于盲点检查，特别检查军事、农业、图书情报、地理和实践服务；不作为已逐项核验的第四套完整清单。[中国 2026 本科目录发布信息](https://www.moe.gov.cn/jyb_xwfb/gzdt_gzdt/s5987/202604/t20260428_1435016.html)显示现行专业目录继续演化；本版没有声称逐项对照全部 883 种本科专业。

网站的 30 个领域和六组视觉分区是编辑设计，不能称为上述机构认可的官方新分类。映射采用 `navigation-coverage`，支持一对多，避免把网站分支与标准条目称为严格等价。OECD 的残余“其他”项明确记录宽泛映射说明。

## 数据与构建

- `data/knowledge-taxonomy.json`：稳定 ID、领域、可递归的子分支、相邻领域、新兴问题入口与旧 ID 跳转。
- `data/knowledge-standards.json`：原始代码和名称、来源版本、URL、访问日期、范围和扩展代码。
- `data/knowledge-crosswalk.json`：306 项目录到具体网站节点的对应关系。
- `data/knowledge-assignments.json`：已有公开笔记的显式编辑关联；每篇笔记保留一个 `type:id` 身份，可关联多个节点。
- `scripts/build_knowledge_atlas.py`：校验来源代码集合、映射、引用与 ID；生成 `knowledge-atlas-data.js` 和首页 marker 内的静态 HTML。
- `includes/js/knowledge-atlas.js`：渐进增强的地图、搜索、筛选、历史导航和多层展开。
- `includes/css/knowledge-atlas.css`：使用现有三套主题的语义颜色与字体，不改变文章阅读器。

常规命令：

```powershell
python scripts/test_knowledge_atlas.py
python scripts/build_site.py
python scripts/validate_site.py
python scripts/validate_aesthetic_system.py
```

构建不需要联网或 PDF 解析工具。官方目录是经过人工核对后提交的本地基线。独立的标准代码集合在验证器中固定，删去来源条目或同时删掉对应映射不能让覆盖检查假通过。数量检查也不能替代语义审核；本次独立审核修正了岗位技能、数字素养、外国语言文学、环境科学与博物馆等映射。

## 发布新笔记

优先在 Markdown front matter 中指定主题，覆盖外部编辑关联：

```yaml
knowledge_ids: ["math.geometry", "computing.algorithms"]
contribution_origin: "unspecified"
evidence_status: "unreviewed"
```

后两项可省略。来源枚举为 `human / ai / collaborative / unspecified`；证据状态为 `unreviewed / conjecture / argument / formal-proof / empirical / contested / superseded`。这些状态是作者声明，不能由所属 AI 领域、文章语气或生成工具自动推断。

旧笔记的关联依据标题、摘要以及必要的正文检查，是编辑归类，不是全文命题抽取，也不代表作者背书书中观点。一个主题包含多条关联时，其祖先领域按文章身份去重计数。

尚未指定主题的新笔记仍然生成和公开，进入“待归档笔记”入口；不会丢失，也不会被默认塞进文学。完整发布验收要求为当前全部公开笔记完成归类，相关测试会提醒未处理项。

## 面向未来的扩展

1. 新领域可以增设顶层节点；已有分支可以递归细分，深度不固定为两层。
2. ID 是稳定身份，名称可以修改。分支 ID 以父节点 ID 加点号开头，例如 `math.analysis.new-question.detail`。
3. 研究问题允许多重归属。来源与验证状态作为另一维度，跨越人类、AI 与协作成果。
4. 移动或合并节点时，在 `redirects` 中将旧 ID 直接指向现存节点；同步更新文章关联、对应表与前沿入口。构建拒绝悬空跳转与跳转链。
5. 新增节点不要求先存在于旧标准中。更新外部目录时，保留原版本、核对变化，并明确改变验收基线。
6. 新兴问题入口不是证明完备性的兜底桶。它连接已有具体节点；未能归类的对象仍需要显式提出和审核新节点。

URL 使用 `domain`、`branch`、`q`、`kind`，支持分享、刷新和浏览器前进后退。新分支深链不依赖单独生成文章目录。缺失或失效的 ID 会回到全图并说明情况。

## 视觉与无障碍

矩形地图采用稳定顺序，面积不按笔记数量变化。微小标记只表示已有笔记；“尚无公开笔记”不表示该领域没有知识。领域标题、分支、问题、条目依次展开；相邻领域提供横向入口。

主题切换只改变材料和颜色，不重置地图位置、搜索或筛选。键盘使用原生链接和按钮；结果数量通过 live region 播报。320px 手机布局改为两列，宽屏保留整体结构；减少动画偏好同时约束悬停过渡。

无 JavaScript、地图数据加载失败时，构建生成的分领域 `<details>` 与真实文章链接仍可使用。静态回退和互动界面由同一份数据生成。

## 验证边界

`test_knowledge_atlas.py` 覆盖独立来源清单、失效映射、全部公开笔记可达、多重归属去重、未知来源不被推断、新领域、递归分支和旧 ID。

`test_knowledge_browser.cjs` 覆盖真实 Edge 中的导航、搜索、类型筛选、URL、空领域、非法输入、数据失败回退、主题保留、多尺寸布局和模拟未来扩展。原有 `test_theme_browser.cjs` 继续覆盖文章、文库、三主题、降级及阅读偏好。

这些检查验证结构和行为。审美验收另查看桌面、手机及主题截图；既不把截图当成研究质量的证据，也不把目录映射称为终极知识本体。
