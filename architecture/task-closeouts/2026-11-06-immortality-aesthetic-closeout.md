# 首页标语恢复与全站美学升级

日期：2026-11-06（Asia/Shanghai）。阶段：实现、验证、本地提交；不推送。

## 结果与设计

首页的 `Pursuing Immortality` 原本只存在于 title 和 OG 元数据中，现在恢复为首屏
可见 H1。英文采用两行衬线排版与暖金斜体，中文“思想，彼此照亮。”作为次标题。
文本保留在静态 HTML 中，关闭 JavaScript 仍然显示。

全站采用深墨青、暖纸色和克制的细线层次。统一主要页面 1320px 版心、导航、
小字层级和列表间距；精选文章从大弧面改成轻微错层书页，背景线场减淡。
文章保持不透明浅纸阅读面；系列、文库、证据、关于、时间线及文章页沿用同一套
主题 token。三主题均升级至 1.1.0，切换、搜索筛选、阅读字号与减少动态偏好继续保留。

另修复共享样式中错误的 `.article-index` 选择器，改为实际 `.article-toc`，
使专注阅读和打印正确隐藏目录，并去掉目录链接继承的橙色虚线。
独立只读复查发现并修正了手机系列卡片内边距、关于页手机与打印最小高度的级联覆盖。
追加 320px 检查时发现系列列表继承的编号缩进挤压最小列宽，已清理列表默认缩进，
并将列宽下限限制在可用空间内。

## 文件范围与本地提交

- `index.html`：标语、中文次标题与首屏页尾署名。
- `includes/css/homepage.css`：首页字体、节奏与移动布局。
- `themes/shared/layout.css`：全站布局、阅读面、导航、目录和无障碍状态。
- 三套 `themes/*/theme.css`、`theme.json` 与生成的 `themes/registry.js`：配色、形态、版本。
- `includes/css/series.css`：系列页字体、文字缩放和悬停样式作用域。
- `scripts/test_theme_browser.cjs`：补充专注阅读隐藏真实目录的行为检查。

用户明确同意已有内容一并提交。内容独立提交为 `f1cd7ba`
（`Add pending reading notes and rebuild public corpus`）：Books 0151–0157、0140 更新、
相应 Markdown、地图、README 示例、首页数据、Atom、Sitemap 和生成页面，共 200 篇公开对象。
仅清理三篇新笔记的空行尾空白和多余 EOF 空行，保留正文与 Markdown 硬换行。

美学改动以 `Restore homepage motto and refine the site visual system` 单独提交。
两笔均为本地提交；本机 `.code-workspace` 删除/新增保留在工作区，不纳入站点提交。

## 实际验证

| 检查 | 结果 |
| --- | --- |
| `python -B scripts/build_site.py` | 200 篇 Markdown 数据与静态页面生成成功 |
| `python -B scripts/test_templates.py` | 9 项通过 |
| `python -B scripts/test_article_durability.py` | 6 项通过 |
| `python -B scripts/test_themes.py` | 6 项通过 |
| `python -B scripts/image_pipeline.py --check` | 图片清单通过 |
| `python -B scripts/validate_site.py --max-warnings 0` | 0 错误、120 条内容提醒 |
| `python -B scripts/validate_aesthetic_system.py` | 0 错误、0 提醒；首页静态资源估算约 565 KB |
| `node scripts/test_theme_browser.cjs` | 108 项通过，覆盖主题/筛选/键盘/深链接/偏好/打印/失败回退 |
| 本地视觉矩阵 | 84 组通过，无横向溢出、浏览器异常；无 JS 标语可见 |
| 手机与打印级联补查 | 320px 系列卡片内边距、关于页手机/打印最小高度通过 |

矩阵覆盖首页、文库、Books、系列列表、系列详情、文章、证据、关于、时间线，
各自三主题 × 1440/390/320px；首页额外覆盖 900px，并检查完整标语位于首屏。
实际浏览器为本机 Edge，通过 bundled Playwright 驱动，静态服务绑定 `127.0.0.1:8765`。
本地复现功能检查时设置 `BASE_URL` 为该地址，`NODE_PATH` 指向可用的 Playwright 包目录。

这些结果证明所检查的行为与布局，不构成用户偏好实验或全浏览器质量评分。
120 条提醒涉及已有内容的标题/日期/摘要等，本轮未作批量内容改写。
资源大小是本地依赖估算，不是网络速度或 GPU 性能测量。

## 可恢复证据

证据目录：`architecture/visual-regression/2026-11-06-immortality/`。

- [首页升级前](../visual-regression/2026-11-06-immortality/before-home.png)
- [首页桌面](../visual-regression/2026-11-06-immortality/home-weave-1440.png) / [手机](../visual-regression/2026-11-06-immortality/home-weave-390.png)
- [浅色主题](../visual-regression/2026-11-06-immortality/home-tomography-1440.png)
- [文库](../visual-regression/2026-11-06-immortality/archive-weave-1440.png) / [文章](../visual-regression/2026-11-06-immortality/article-weave-1440.png)
- [系列手机](../visual-regression/2026-11-06-immortality/series-weave-390.png) / [关于](../visual-regression/2026-11-06-immortality/field-weave-1440.png)
- [功能检查](../visual-regression/2026-11-06-immortality/browser-checks.json) / [视觉矩阵](../visual-regression/2026-11-06-immortality/visual-checks.json)

## 回退与停止边界

可按提交标题定位美学提交，再执行 `git revert <美学提交哈希>` 保留内容提交并回退视觉升级。
如需撤回本轮内容，可单独 revert `f1cd7ba`。操作前核对工作区，保留本机 workspace 文件变动。
本轮到本地提交为止；线上发布需后续指令，本轮未推送、未部署、未创建后续任务。
