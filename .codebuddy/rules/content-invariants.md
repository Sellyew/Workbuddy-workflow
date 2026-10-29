---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
  - "Quarto/**/*.scss"
  - "Preambles/header.tex"
  - "scripts/R/**/*.R"
---

# 内容不变量（INV-1 至 INV-12）

针对本仓库产出的内容、按编号列出的不可让渡规则。评审代理、审稿人和审计代理在指出问题时，应以编号引用这些不变量（例如「违反 INV-3」）。改编自 clo-author 的强制实施模式。

## 幻灯片不变量

- **INV-1：配色同步。**`Preambles/header.tex` 里的颜色名必须与 `Quarto/theme-template.scss` 里的 SCSS 变量一致。用 `./scripts/check-palette-sync.sh` 校验。往一边新增的颜色，必须同时加到另一边。
- **INV-2：Beamer↔Quarto 记号一致。**Beamer `.tex` 幻灯片里的每个数学符号、变量名和下标，都必须原样出现在它的 Quarto `.qmd` 镜像里。两者之间的记号漂移是 CRITICAL 缺陷。
- **INV-3：Quarto CSS 覆盖契约。**必须覆盖 Bootstrap 默认值的样式（例如行内代码颜色、代码块背景）写进 `include-in-header` 的裸 `<style>` 标签里，绝不写进 SCSS 文件。SCSS 只用于不需要压过 Bootstrap 层叠的样式——否则 Bootstrap 自己的选择器会在特异性之争里赢。
- **INV-4：TikZ 一律用 SVG。**浏览器无法内联渲染 PDF 图片。Quarto/HTML 里的所有 TikZ 图必须是 SVG，通过 `/extract-tikz` 生成。绝不要把 `.pdf` 嵌进 `.qmd` 幻灯片。
- **INV-5：单一文献库。**`Bibliography_base.bib` 是权威文献库。不允许每讲一个 `.bib` 文件。所有引文都必须能在这一份文件里解析到。

## 幻灯片设计不变量

- **INV-6：禁用 `\pause` 与 overlay。**禁止使用 Beamer 的 `\pause`、`\only`、`\visible`、`\onslide` 命令。理由见 `.codebuddy/rules/no-pause-beamer.md`。
- **INV-7：每页最多 2 个彩色框。**滥用 `keybox`、`definitionbox` 或提示块环境会造成「框疲劳」。每页最多两个。
- **INV-8：先动机，后形式化。**每个定义之前必须先有一个引出动机的例子、直觉或现实问题。不做没有动机的数学。

## R 脚本不变量

- **INV-9：`set.seed()` 只在顶上调用一次。**每个使用随机性的 R 脚本都必须在脚本顶上、任何随机代码之前，恰好调用一次 `set.seed(N)`。绝不放在循环或函数内部。
- **INV-10：只用相对路径。**不允许绝对路径（`/Users/...`、`C:\...`、`~` 展开）。所有路径相对于仓库根目录。跨平台兼容用 `file.path()`。
- **INV-11：Beamer 图形用透明背景。**所有为 Beamer 幻灯片产出图形的 `ggsave()` 调用都必须带 `bg = "transparent"`。
- **INV-12：所有图都用项目主题。**每张 ggplot 图都必须用项目的自定义主题。任何已提交的图里都不应出现 ggplot2 默认的灰底。
