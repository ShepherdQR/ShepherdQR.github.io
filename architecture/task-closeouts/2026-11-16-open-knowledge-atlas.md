# 开放知识地图交付记录

日期：2026-11-16。范围：按用户授权核对分类、实现首页、验证并推送 GitHub Pages 的 `master` 分支。

## 交付内容

- 首页建立 30 个领域、220 个分支的知识地图，203 篇已有公开内容均有明确主题归属。
- 官方来源清单与 306 项导航对应关系可检查；覆盖 OECD 42、UNESCO 80、中国研究生目录 117 个一级学科及 67 个专业学位类别。
- 支持逐层展开、真实笔记、主题多重归属、搜索、内容筛选、深链接、浏览器历史、空领域和相邻领域。
- 新领域可独立加入；分支可递归细分；旧 ID 可以迁移至现存节点。构建拒绝悬空引用。
- 保留三主题、原有阅读页面、个人研究路线、长期阅读入口及无 JavaScript 静态浏览。

分类范围、完整来源、编辑规则和后续维护见[开放知识地图合同](../knowledge-atlas.md)。这里的“完整”限定为指定版本的目录入口覆盖，不能外推为全部知识已被收录或验证。

## 验证结果

| 检查 | 结果 |
| --- | --- |
| Python 编译、客户端 JS 语法 | 通过 |
| `test_templates.py` | 9 项通过 |
| `test_themes.py` | 6 项通过 |
| `test_article_durability.py` | 6 项通过 |
| `test_knowledge_atlas.py` | 10 项通过 |
| `build_site.py` | 203 篇文章及地图生成成功 |
| `validate_site.py` | 0 错误；工作语料仍有 127 项标题/时间等规范警告 |
| `validate_aesthetic_system.py` | 0 错误、0 警告；首页资源估算在预算内 |
| `image_pipeline.py --check` | 通过 |
| 真实 Edge 地图专项 | 29 项通过 |
| 真实 Edge 主题与文章回归 | 114 项通过 |

浏览器测试覆盖 320、390、768、1024、1440 像素；包括正常导航、刷新、历史返回、空结果、输入转义、筛选数量播报、同分支搜索范围、无 JS、数据加载失败、四层新分支与旧链接。模拟新领域只存在于测试上下文，没有伪装成网站实际知识。

独立只读审查覆盖分类清单、映射语义及实现；修正了岗位技能、数字素养、外国文学、环境科学、博物馆和递归路径等问题。审查未代替浏览器执行或视觉检查。

已查看并保留以下视觉证据：

- [桌面地图](../visual-regression/2026-11-16-knowledge-atlas/map-desktop.png)
- [手机地图](../visual-regression/2026-11-16-knowledge-atlas/map-mobile.png)
- [手机领域页](../visual-regression/2026-11-16-knowledge-atlas/domain-mobile.png)
- [地图检查明细](../visual-regression/2026-11-16-knowledge-atlas/atlas-checks.json)
- [主题检查明细](../visual-regression/2026-11-16-knowledge-atlas/theme-checks.json)

## 生成一致性与范围隔离

开始时 `master` 基线为 `09c53601add5044ecb0937a90e5bf2ccfe11a635`。工作区已有工作空间文件改名；执行期间 `Books:0159` 的源笔记也出现独立编辑。这些源文件及其 `books/0159/index.html`、`homepage-data.js`、`includes/atom.xml` 变动保留在工作区，不属于本次地图提交。

地图最终发布投影以基线已提交的 203 篇语料为输入重新生成，并与同输入的构建结果逐项比较。避免将并行编辑中的摘要意外带入本次发布。之后正常构建会继续使用当前 Markdown；新的笔记内容由它自己的发布任务处理。

最终地图输入 SHA-256：

```text
67986302bb30e10731e5989fe0443d8dd60bf4e9a894c0e061a2ba4381b26e77  data/knowledge-taxonomy.json
10b9830d5e332dc46d2f633d522e9faadb57cc9123c926f78d2cb99c96630488  data/knowledge-standards.json
3b556d24cf7ababaa5b010b3e2dc8c05f55889a874001ab40d3d0606f1083165  data/knowledge-crosswalk.json
82077c4b24291a3ecb39cdd1c438ecc501783edc87de74b617aaa38f779c0d69  data/knowledge-assignments.json
```

## 发布与回退

已核实远端为 `ShepherdQR/ShepherdQR.github.io`，GitHub Pages 从 `master` 发布到 [zqr.world](https://zqr.world/)。本记录随实现一并提交；发布 SHA 以包含本文件的 Git 提交为准。推送后继续检查对应的 Site hardening 工作流、Pages 构建与线上内容；会话最终回执给出实际结果。

如需回退，使用 `git revert <本次地图提交SHA>`，再推送并确认 Pages 完成；不要使用破坏性重置，也不要回退并行笔记编辑。原有文库、书籍和文章 URL 没有迁移。

本阶段完成后不创建自动化、不执行新的研究任务、不修改全局记忆。
