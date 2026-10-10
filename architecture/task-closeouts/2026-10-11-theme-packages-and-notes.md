# 2026-10-11｜主题包升级与笔记发布

## 范围与授权

用户授权将审美方案落实为可切换主题包，明确不再要求保留 Field / Museum，并要求
将本地未提交的读书笔记和 Thoughts 一起提交到远端。交付目标为 origin/master；
GitHub Pages 从 master 根目录发布到 https://zqr.world/。

本次基线为 46fda2d251b827b972fe7047e1d8e5a0fc884513。实施前已核对远端 master
与本地基线一致。旧审美治理文档保留为历史记录，现行合同见
[theme-packages.md](../theme-packages.md)。

## 实现

- 三个 1.0.0 主题包：相位织场（默认）、暮色观测、思想层析。
- 统一注册表、按选择加载的 CSS/场景、设备偏好、字体、动态与专注阅读。
- 主题切换保留当前内容、筛选和阅读设置；快速切换、样式失败、场景失败与存储拒绝
  有明确行为，旧场景会释放。
- 首页优先显示真实精选文章与近作；文库提供空间浏览、关系和完整列表。
- 文章保持不透明 HTML 阅读面、原始图文与稳定 canonical；189 篇静态正文可在
  JavaScript 不可用时阅读。
- 场景为 Canvas 2D 与 CSS perspective 的轻量实现，不是概念稿的摄影级实时折射。
- 三套主题覆盖现代首页、Atlas、集合、Evidence、System、Chronicle、Series、
  canonical 文章及 legacy render 阅读器。历史独立 HTML 不在现代模板迁移范围。
- 新增包维护文档、包合同测试与可复用浏览器检查；CI 检查覆盖主题文件。

## 内容发布

新增 12 篇：

| 类型 | ID | 标题 | 发布日期 |
| --- | --- | --- | --- |
| Books | 0139 | 习近平用典 | 2026-09-12 |
| Books | 0140 | 人工智能+企业转型：策略-路径-典型案例 | 2026-09-25 |
| Books | 0141 | 灞桥折柳 | 2026-09-25 |
| Books | 0142 | 诗论 | 2026-09-25 |
| Books | 0143 | 坍塌 | 2026-09-25 |
| Books | 0144 | 2020年中国诗歌精选 | 2026-09-25 |
| Books | 0145 | 张爱玲 | 2026-09-27 |
| Books | 0146 | 度量世界 | 2026-10-01 |
| Books | 0147 | 巴比伦与巴比伦人赞歌 | 2026-10-01 |
| Thoughts | 0036 | 第三次论我的政绩观 | 2026-09-25 |
| Thoughts | 0037 | 新跃迁边缘感性直观 | 2026-09-25 |
| Thoughts | 0038 | 党建思想学习研讨发言 | 2026-10-02 |

同时交付 Books 0056、0096、0100、0137 的用户已有补充，并重建相应页面。
全部 192 份本地 Markdown（含 README、草稿/临时文件）与实施开始时的 SHA-256
一致：没有替用户改写正文、front matter 或作者时间。

qrthoughts/Temp.md 自述为 temporary notes，没有发布 front matter，保留本地并
通过精确路径忽略/排除校验，不提交远端。其余 dated 笔记正常验证。
Books 0146 中的 TODO 标题属于 status=published 的原稿内容，原样保留。

## 本地验证

| 检查 | 结果 |
| --- | --- |
| 构建 | 189 Markdown-backed items、189 canonical 文章 |
| test_templates.py | 9 passed |
| test_article_durability.py | 6 passed |
| test_themes.py | 6 passed |
| test_theme_browser.cjs | 107 checks passed |
| image_pipeline.py --check | OK |
| validate_site.py | 0 errors，99 warnings |
| validate_aesthetic_system.py | 0 errors，0 warnings |
| JavaScript syntax | 20 files passed |
| Python syntax | scripts 下全部通过 |
| 作者 Markdown 完整性 | 192 files unchanged |

99 条提示主要为原稿中的多个 H1、注释时间与 front matter 不一致等；未用构建时间
覆盖作者时间。另有用户原始 Books0056 文件末尾空行提示；任务代码的 diff --check
通过，未为消除提示而改动作者原稿。

浏览器使用真实 Chromium/Edge，覆盖桌面、390px 手机与900px窄桌面、三主题、
键盘选文、外观对话框、字号、跨深路径页面偏好、Atlas 筛选/列表保持、快速 CSS
切换、延迟场景回包、样式/场景失败、存储拒绝、减少动态、场景销毁、无 JS 正文、
legacy 读取与打印。截图复核发现的手机导航逐字换行已修正并增加断言。

本地文件预算估算每套首页约 0.55 MB（含公共依赖及最大候选预览图）；这是保守
文件体积估算，不是网络、GPU、帧率或读者体验评分。

## 证据

- [浏览器检查清单](../visual-regression/2026-10-11-theme-packages/browser-checks.json)
- [验证摘要](../visual-regression/2026-10-11-theme-packages/verification.json)
- [相位织场桌面](../visual-regression/2026-10-11-theme-packages/home-weave-desktop.png)
- [暮色观测桌面](../visual-regression/2026-10-11-theme-packages/home-twilight-desktop.png)
- [思想层析桌面](../visual-regression/2026-10-11-theme-packages/home-tomography-desktop.png)
- [手机首页](../visual-regression/2026-10-11-theme-packages/home-weave-mobile.png)
- [手机阅读](../visual-regression/2026-10-11-theme-packages/article-twilight-mobile.png)
- [文库](../visual-regression/2026-10-11-theme-packages/atlas-tomography-desktop.png)

本机更完整的临时日志位于 output/playwright/theme-upgrade/，该目录不提交。
本报告与代码、内容一同进入发布提交；可用 git log --follow -- 本报告路径定位该
提交。推送后的 CI 与线上核对结果另保存在本机 release-receipt.json，并在本次对话
交付时报告。

## 回退与后续边界

外观可在界面内切到另外一个已注册主题，内容不变。代码级回退应 revert 本次发布
提交并重建/发布；因为该提交也含新笔记，整体 revert 会一并回退这些内容，若只回退
主题，应保留 qrthoughts 的新增/修改，并用上一版模板重新生成文章。

本阶段到实现、验证和 Git 交付完成为止，不创建自动化，不继续扩展新的视觉方向。

