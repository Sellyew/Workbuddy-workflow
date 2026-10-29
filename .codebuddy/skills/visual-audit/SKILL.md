---
name: visual-audit
description: 对 Quarto `.qmd` 或 Beamer `.tex` 幻灯片做对抗式视觉版式审计。标出溢出、字号不一致、盒子疲劳、间距与对齐问题。用户说 "visual audit"、"check the layout"、"does this overflow?"、"look for visual issues"、"audit the slides" 时使用，或在一套幻灯片的外观被重做之后使用。不检查写作或教学法——请与 `/proofread` 或 `/pedagogy-review` 搭配。
description_zh: 对 Quarto `.qmd` 或 Beamer `.tex` 幻灯片做对抗式视觉版式审计。标出溢出、字号不一致、盒子疲劳、间距与对齐问题。用户说 "visual audit"、"check the layout"、"does this overflow?"、"look for visual issues"、"audit the slides" 时使用，或在一套幻灯片的外观被重做之后使用。不检查写作或教学法——请与 `/proofread` 或 `/pedagogy-review` 搭配。
argument-hint: "[QMD or TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# 幻灯片视觉审计

对一套幻灯片做一次彻底的视觉版式审计。

## 步骤

1. **读** `$ARGUMENTS` 指定的幻灯片文件

2. **对 Quarto（.qmd）文件：**
   - 用 `quarto render Quarto/$ARGUMENTS` 渲染
   - 度量这次渲染：`"${SLIDE_QA_PYTHON:-python}" scripts/slide-qa.py Quarto/<deck>.html`。它在无头 Chrome 里以全部分片可见的状态加载整套幻灯片，写出 `quality_reports/audits/slide-qa/<deck>/report.md`——每页越过每条边界的像素数、越界的元素、藏在滚动容器里的内容——外加每页一张截图，以及损坏的图片或路径缺失、大小写写错的本地文件（这些在 GitHub Pages 上会坏）。OVERFLOW 发现来自这份报告，损坏或大小写写错的资源同样算一条发现；其余检查靠读被标记的与内容密集的幻灯片的截图。
   - 若它以 2 退出（通常是缺 Playwright——脚本会打印一次性的 venv 安装命令和要设置的 `SLIDE_QA_PYTHON` 那一行），照实说明，回退为读那些密集幻灯片的渲染后 HTML 与用户提供的任何截图，并点名哪几页该由用户亲眼看

3. **对 Beamer（.tex）文件：**
   - 编译（见 `/compile-latex`），在日志里查 overfull hbox 警告，并 Read 带图或内容密集的那几页 PDF

4. **逐页审计：**

   **溢出：**内容超出幻灯片边界
   **字号一致性：**行内覆盖字号、字号不一致
   **盒子疲劳：**一页上 3 个以上彩色盒子（INV-7 允许两个）、盒子类型用错
   **间距：**缺负边距、缺 fig-align
   **版式：**缺过渡页、缺引导句、语义化配色

5. **产出一份报告**，按幻灯片组织，含严重度与建议

6. **遵循间距优先原则：**
   1. 用负边距压缩纵向间距
   2. 合并列表
   3. 把独立公式改成行内
   4. 缩小图片／SVG 尺寸
   5. 最后手段：缩小字号（绝不低于 0.85em）
