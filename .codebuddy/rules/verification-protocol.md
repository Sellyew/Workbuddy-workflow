---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
  - "docs/**"
---

# 任务完成验证协议

**在报告某页幻灯片或整套幻灯片任务完成之前，先确认产出能构建、能渲染**——一套编译通过却缺了图、或某页溢出的幻灯片不算完成，而用户通常会在课堂上当着人发现它。

## 对 Quarto/HTML 幻灯片：
1. 运行 `./scripts/sync_to_docs.sh`（或 `./scripts/sync_to_docs.sh LectureN`）来渲染并部署
2. 度量这次渲染：`"${SLIDE_QA_PYTHON:-python}" scripts/slide-qa.py Quarto/LectureN.html` 在无头 Chrome 里加载幻灯片，写出 `quality_reports/audits/slide-qa/LectureN/report.md`，以及每页一张 `slide-NN.png` 截图。读取报告，以及被标记的、内容密集的幻灯片的截图。若它以 2 退出（跑不起来，通常是缺 Playwright；见 `TROUBLESHOOTING.md`），改为读取密集幻灯片的渲染 HTML，Read 用户提供的任何截图或 PDF 导出，并点名该由用户亲眼看哪几页——`open` 打开的窗口只有用户自己看得见
3. 读取 2-3 个图片文件、确认内容有效，以此验证图片能正常显示
4. 检查 HTML 源码里的图片路径是否正确
5. 溢出项取自 slide-qa 报告（退出码 1 会标记溢出、内容被裁切，或资源损坏、大小写写错）。若 slide-qa 跑不起来，就扫源文件里的密集幻灯片，并说明溢出是从源文件判断的
6. 验证环境对齐：每个 Beamer box 环境在 QMD 里都有对应的 CSS
7. 报告验证结果

## 对 LaTeX/Beamer 幻灯片：
1. 用 xelatex 编译并检查报错
2. 读取编译出的 PDF 中带图的那几页，确认它们渲染出来了
3. 检查 overfull hbox 警告

## 对 HTML/Quarto 里的 TikZ 图：
1. 浏览器**不能**内联显示 PDF 图片——一律转成 SVG
2. 用 SVG（矢量格式）获得清晰渲染：`pdf2svg input.pdf output.svg`
3. **绝不要用 PNG 画图**——PNG 是点阵，会显得糊
4. 验证 SVG 文件含有合法的 XML/SVG 标记
5. 通过 `sync_to_docs.sh` 把 SVG 复制到 `docs/Figures/LectureX/`
6. **新鲜度检查：** 使用任何 TikZ SVG 之前，先确认 extract_tikz.tex 与当前 Beamer 源一致

## 对 R 脚本：
1. 运行 `Rscript scripts/R/filename.R`
2. 验证输出文件（PDF、RDS）已生成且大小不为零
3. 抽查估计值，看量级是否合理

## 关于代码的断言要带上版本：

任何关于代码当前行为的陈述，都要带上读它时所在的版本——完整标准在 [`agent-authored-code.md`](agent-authored-code.md)，凡触及 `.sh`/`.py`/`.R`/`.do` 文件时它都会加载（本规则的管辖范围是幻灯片/HTML 交付物，所以这项义务属于代码工作真正发生的地方）。

## 常见坑：
- **HTML 里的 PDF 图**：浏览器不会内联渲染 PDF → 转成 SVG
- **相对路径**：`../Figures/` 从 `Quarto/` 出发可用，从 `docs/slides/` 出发不可用 → 用 `sync_to_docs.sh`
- **假定成功**：永远先验证输出文件存在**且**内容正确
- **过期的 TikZ SVG**：extract_tikz.tex 与 Beamer 源分叉 → 永远先做差异检查

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
