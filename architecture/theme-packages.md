# ZQR.WORLD 主题包合同

状态：已实现，contractVersion 1。生效：2026-10-11。

用户授权替换 Field / Museum；既有正文、图片、链接和来源语义继续保留。

## 内容与展示

Markdown/front matter 是内容源。构建生成 homepage-data.js、静态文章、Atom 与
Sitemap。主题不改写标题、正文、配图、日期、分类、canonical 或来源。正文与控制器
是语义 HTML；Canvas 仅绘制装饰线场。

| ID | 名称 | 外观与场景 |
| --- | --- | --- |
| weave | 相位织场（默认） | 苍青织面、缓慢流动的光学路径、清晰文档 |
| twilight | 暮色观测 | 暮色层片、曲线边缘与暖色阅读焦点 |
| tomography | 思想层析 | 烟紫平行页片、稳定的静态层次 |

真实内容驱动的文档浏览器支持上下篇按钮与左右方向键。首页使用既有精选条目加
最近七篇去重后的集合；Atlas 使用同一份筛选结果。文章预览使用既有最小 WebP
衍生图，正文链接仍指向原 canonical。主题切换不重置选择、筛选、列表模式或内容 DOM。

## 注册与文件

themes/registry.json 是包目录与默认 ID 的注册入口。
themes/<id>/theme.json 声明：

- id、label、description、version、contractVersion。
- stylesheet、可选 scene：themes/ 内的实际文件。
- colorScheme、surfaces、fallbackTheme。
- maxPackageBytes、motionPolicy。

scripts/build_themes.py 校验合同、路径、默认与回退 ID，生成 themes/registry.js。
构建同时生成 includes/js/image-sources.js，把文章预览指向已有最小 WebP。
执行 python scripts/build_site.py 会自动完成这些步骤。
浏览器按选择加载包 CSS 与场景，不预加载其他主题的呈现资源。

## 运行时与偏好

includes/js/theme.js 是统一入口，使用 html[data-theme]。
localStorage 的 zqr-display-v1 保存主题、阅读模式、正文字号和动态偏好。
未知或旧 ID 回退到默认；存储不可用不妨碍当前页面切换。

“外观”对话框提供三个主题、18/20/22px 字号、跟随系统/关闭动态。
“专注阅读”独立于主题：收敛为浅纸阅读、释放场景、隐藏目录侧栏，
保持正文与图片。选择跨主题、跨页面保留。

新 CSS 成功后才替换旧 CSS。当前已有主题时，新样式失败保留旧外观；
首载失败则尝试包声明的 fallbackTheme，且不循环重试。
场景失败时保留 HTML 与包外观，提供降级提示。
快速切换使用递增代次，过期请求不会覆盖新选择、场景或状态播报。

主题控制器发布 zqr:themechange；文档浏览器发布 zqr:documentchange，
detail 包含 host、item 副本、index、count。这些事件只描述展示状态。

## 场景生命周期

场景入口是浏览器 ES module，导出：

~~~js
export function mount({ hosts, reducedMotion, signal, getDocuments }) {
    // Only create theme-owned decoration inside data-theme-scene hosts.
    // getDocuments() provides shallow copies of the common read model.
    return { dispose() { /* remove nodes, listeners and animation frames */ } };
}
~~~

当前包使用 themes/shared/scene.js：Canvas 2D 线场配合 CSS perspective 页片。
这是轻量网页呈现，不等同于概念稿的摄影级实时折射。

换主题、进入专注阅读和离开页面时 abort/dispose，恢复 BFCache 时重新挂载。
不可见区域及隐藏标签页停止 RAF。系统减少动态或用户关闭动态时只画静态场景；
Tomography 背景本来就是静态。减少动态也会取消选文过渡。

## 布局与语义

themes/shared/layout.css 定义公共插槽、移动布局、不透明阅读面、外观对话框、
打印与强制颜色表现。包 CSS 负责语义 token 和有界形态差异。
文章图片没有附加调色滤镜，正文不会被唯一地画进 Canvas。

暗色包提供含义一致的可读状态色，文字标签继续存在。System 与文章中的局部真理
宪章仍作为内容保留；已解除旧 Museum 首页强制展件规则。
内容图不再依据某个主题而隐藏或降为 dormant。

首页优先精选与近作，站点边界在页脚可展开。Atlas 研究线索转为辅助入口，
列表和筛选仍覆盖全部语料。四类集合页使用清晰列表。
历史独立 HTML 不在现代模板范围内；全部 canonical Markdown 文章使用新主题系统。

## 升级方式

1. 新建主题目录，提供 theme.json、以自身 ID 为作用域的 CSS 和可选场景。
2. 将 ID 加入 registry.json。更换默认时同步根页面默认属性与 visual_system 声明；
   验证器检查它们与注册表的一致性。
3. 构建并检查包合同，以真实内容和所有页面模板验证。
4. 提交包、注册表和构建产物，沿用 GitHub Pages 发布。

新空间形式仍需要设计与实现，但内容作者无需复制或重写 Markdown。
改变共有阅读器属于合同变化，应更新合同版本并跨包验证。

## 验证

~~~powershell
python -B scripts/test_templates.py
python -B scripts/test_article_durability.py
python -B scripts/test_themes.py
python -B scripts/build_site.py
python -B scripts/image_pipeline.py --check
python -B scripts/validate_site.py --max-warnings 50
python -B scripts/validate_aesthetic_system.py
~~~

scripts/test_theme_browser.cjs 使用 Playwright 与本地静态服务器。
环境提供 Playwright 时，将 NODE_PATH 指向其 node_modules，再执行
node scripts/test_theme_browser.cjs；BASE_URL 可覆盖默认的本地 8000 端口。
公开站点没有增加 Node 或 Playwright 运行依赖。

浏览器检查覆盖选择、键盘、跨页偏好、筛选不变、场景释放、减少动态、
快速切换、资源失败、存储拒绝、静态正文、窄屏与打印。
审美验证器报告本地文件体积估算，不代表网络实测、GPU 指标或用户体验评分。

本地临时笔记 qrthoughts/Temp.md 保留且忽略，不进入发布语料；其他 dated
Markdown 继续按原 front matter 合同校验。

