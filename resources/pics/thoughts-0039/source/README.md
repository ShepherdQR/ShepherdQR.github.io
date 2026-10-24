# 曾总您好：六种阅读版的排版源文件

对应文章：[/thoughts/0039/](https://zqr.world/thoughts/0039/)。最终选用 `01-brief.png`。

六份 HTML 对应上一级目录的六张 PNG。它们使用本地 HTML/CSS 排版，文字可以直接修改；每份都在签名下方的右侧显示 `zqr.world`。

导出约定：

- 浏览器视口宽度 540 CSS px，设备像素比 2，得到 1080 px 宽的 PNG。
- 等待 `document.fonts.ready`，按 `.sheet` 的完整高度截取。
- 原排版使用 Noto Sans SC / Noto Serif SC，后备字体为微软雅黑 / 宋体；更换字体会影响断行，需重新检查。
- 浏览器打印使用相同的 540 px 宽度和页面实际高度、零边距、保留背景色。
- 站点的响应式图片通过 `scripts/image_pipeline.py` 生成并登记在 `resources/pics/derivatives/manifest.json`。

六种风格的分析、原始记录和发送开场白保存在文章 Markdown 中；这些源文件只负责图片排版。
