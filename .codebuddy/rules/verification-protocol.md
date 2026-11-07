---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
  - "docs/**"
---

# 任务完成验证协议

**报告某页或整套幻灯片的任务完成之前，先确认产出能够构建和渲染。**编译通过但缺图，或某页内容溢出，都不能算完成；否则用户往往要到课堂上才会发现问题。

## 对 Quarto/HTML 幻灯片：
1. 运行 `./scripts/sync_to_docs.sh` 或 `./scripts/sync_to_docs.sh LectureN`，完成渲染和部署。
2. 度量这次渲染。运行 `"${SLIDE_QA_PYTHON:-python}" scripts/slide-qa.py Quarto/LectureN.html`，在无头 Chrome 中加载幻灯片，生成 `quality_reports/audits/slide-qa/LectureN/report.md`，并为每页生成一张 `slide-NN.png` 截图。先读取报告，再查看被标记页和内容密集页的截图。如果命令以 2 退出，说明它无法运行，通常是缺少 Playwright，见 `TROUBLESHOOTING.md`。此时改读内容密集页的渲染 HTML，用 Read 查看用户提供的任何截图或 PDF 导出，并明确列出需要用户亲眼检查的页面；`open` 打开的窗口只有用户自己看得见。
3. 读取 2-3 个图片文件并确认内容有效，验证图片能够正常显示。
4. 检查 HTML 源码中的图片路径是否正确。
5. 从 slide-qa 报告获取溢出项。退出码 1 表示存在溢出、内容裁切、资源损坏或大小写错误。如果 slide-qa 无法运行，就扫描源文件中的内容密集页，并明确说明溢出判断仅来自源文件。
6. 验证环境对齐：每个 Beamer box 环境在 QMD 中都有对应的 CSS。
7. 报告验证结果。

## 对 LaTeX/Beamer 幻灯片：
1. 用 xelatex 编译并检查报错。
2. 读取编译所得 PDF 中带图的页面，确认图片已经渲染。
3. 检查 overfull hbox 警告。

## 对 HTML/Quarto 里的 TikZ 图：
1. 浏览器**不能**内联显示 PDF 图片，必须一律转成 SVG。
2. 使用 SVG 矢量格式获得清晰渲染：`pdf2svg input.pdf output.svg`。
3. **绝不要用 PNG 画图**，因为 PNG 是点阵格式，会显得模糊。
4. 验证 SVG 文件含有合法的 XML/SVG 标记。
5. 通过 `sync_to_docs.sh` 把 SVG 复制到 `docs/Figures/LectureX/`。
6. **新鲜度检查：**使用任何 TikZ SVG 之前，先确认 extract_tikz.tex 与当前 Beamer 源一致。

## 对 R 脚本：
1. 运行 `Rscript scripts/R/filename.R`。
2. 验证输出文件（PDF、RDS）已经生成，且大小不为零。
3. 抽查估计值，确认量级合理。

## 关于代码的断言要带上版本：

陈述代码当前行为时，必须注明阅读代码时所在的版本。完整标准见 [`agent-authored-code.md`](agent-authored-code.md)；只要触及 `.sh`/`.py`/`.R`/`.do` 文件，该规则就会加载。本规则只管幻灯片/HTML 交付物，因此这项义务由实际开展代码工作的规则承担。

## 常见坑：
- **HTML 里的 PDF 图**：浏览器不会内联渲染 PDF，必须转成 SVG。
- **相对路径**：`../Figures/` 从 `Quarto/` 出发可用，从 `docs/slides/` 出发不可用，因此要用 `sync_to_docs.sh`。
- **假定成功**：永远先验证输出文件存在，**且**内容正确。
- **过期的 TikZ SVG**：extract_tikz.tex 与 Beamer 源可能分叉，因此永远先做差异检查。

## 验证清单：
```
[ ] Output file created successfully
[ ] No compilation/render errors
[ ] Images/figures display correctly
[ ] Paths resolve in deployment location (docs/)
[ ] Rendered output inspected, or the slides to eyeball named for the user
[ ] Any claim about code state carries the revision it was read at
[ ] Reported results to user
```
