---
name: visual-audit
description: 对 Quarto `.qmd` 或 Beamer `.tex` 幻灯片做对抗式视觉版式审计，只标出实际存在的配色、间距、溢出、重叠和错位问题。用户说 "visual audit"、"check the layout"、"does this overflow?"、"look for visual issues"、"audit the slides"、"视觉审计"、"检查幻灯片版式"、"内容有没有溢出" 或 "看看有没有视觉问题" 时使用，也可在重做整套幻灯片外观后使用。不检查写作或教学法，需与 `/proofread` 或 `/pedagogy-review` 配合。
description_zh: 对 Quarto `.qmd` 或 Beamer `.tex` 幻灯片做对抗式视觉版式审计，只标出实际存在的配色、间距、溢出、重叠和错位问题。用户说 "visual audit"、"check the layout"、"does this overflow?"、"look for visual issues"、"audit the slides"、"视觉审计"、"检查幻灯片版式"、"内容有没有溢出" 或 "看看有没有视觉问题" 时使用，也可在重做整套幻灯片外观后使用。不检查写作或教学法，需与 `/proofread` 或 `/pedagogy-review` 配合。
argument-hint: "[QMD or TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]
---

# 幻灯片视觉审计

只检查幻灯片中实际存在的配色、间距、溢出、重叠和错位问题。

**只读审计：** 不修改幻灯片源文件，报告写入 `quality_reports/audits/`。

## 步骤

1. **读取** `$ARGUMENTS` 指定的幻灯片文件。

2. **对 Quarto（.qmd）文件：**
   - 用 `quarto render Quarto/$ARGUMENTS` 渲染。
   - 度量渲染结果：`"${SLIDE_QA_PYTHON:-python}" scripts/slide-qa.py Quarto/<deck>.html`。它在无头 Chrome 中展开所有分片并加载整套幻灯片，生成 `quality_reports/audits/slide-qa/<deck>/report.md`。报告记录每页越过各边界的像素数、越界元素和滚动容器中的隐藏内容，同时为每页生成截图。OVERFLOW 发现以这份报告为准；其余视觉检查只采用与实际配色、间距、溢出、重叠和错位有关的证据，通过阅读被标记页和内容密集页的截图完成。
   - 如果脚本以 2 退出，通常表示缺少 Playwright。脚本会打印一次性的 venv 安装命令和需要设置的 `SLIDE_QA_PYTHON` 行。如实说明这一情况，改为阅读内容密集页的渲染 HTML 和用户提供的截图，并明确指出哪些页面需要用户亲眼检查。

3. **对 Beamer（.tex）文件：**
   - 按 `/compile-latex` 编译，在日志中检查 overfull hbox 警告，并用 Read 查看 PDF 中带图或内容密集的页面。

4. **逐页审计，仅限实际视觉问题：**

   **配色：** 只报告渲染结果中实际存在的配色错误或不一致，不评价配色所承载的教学设计。
   **间距：** 只报告实际过宽或过窄的间距；缺少负边距或 `fig-align` 本身不是缺陷。
   **溢出：** 内容超出幻灯片边界，或存在渲染报告确认的隐藏内容。
   **重叠与错位：** 只报告渲染结果中实际可见或由像素度量确认的元素重叠与错位。
   **教学法移交：** 过渡页、引导句及其缺失交 `/pedagogy-review`；本技能不把它们记为视觉发现，也不检查写作或教学法。

5. **生成报告**，按幻灯片组织，只包含上述实际配色、间距、溢出、重叠和错位发现及其严重度和建议；过渡页与引导句问题移交 `/pedagogy-review`，不在本报告中作教学法评价。

6. **只对已确认的实际配色、间距、溢出、重叠或错位问题给出修复建议：**
   1. 可选地使用负边距压缩纵向间距；没有负边距不是问题，也不预设必须添加
   2. 合并列表
   3. 把独立公式改成行内公式
   4. 缩小图片或 SVG 尺寸
   5. 将配色修正到项目实际约定，并重新渲染确认没有引入溢出、重叠或错位
