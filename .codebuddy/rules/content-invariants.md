---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
  - "Quarto/**/*.scss"
  - "Preambles/header.tex"
  - "scripts/R/**/*.R"
---

# 内容不变量（INV-1 至 INV-12）

这些编号规则约束本仓库产出的内容，不得让渡。评审代理、审稿人和审计代理指出问题时，应引用对应编号，例如「违反 INV-3」。本规则改编自 clo-author 的强制实施模式。

## 幻灯片不变量

- **INV-1：配色同步。**`Preambles/header.tex` 的颜色名必须与 `Quarto/theme-template.scss` 的 SCSS 变量保持一致，并用 `./scripts/check-palette-sync.sh` 校验。一侧新增颜色时，另一侧也必须同步添加。
- **INV-2：Beamer↔Quarto 记号一致。**Beamer `.tex` 幻灯片中的每个数学符号、变量名和下标，都必须原样出现在对应的 Quarto `.qmd` 镜像中。两侧记号不一致属于 CRITICAL 缺陷。
- **INV-3：Quarto CSS 覆盖契约。**需要覆盖 Bootstrap 默认值的样式，例如行内代码颜色和代码块背景，必须写入 `include-in-header` 的裸 `<style>` 标签，绝不能写进 SCSS 文件。SCSS 只承载无需压过 Bootstrap 层叠的样式，否则 Bootstrap 自己的选择器会因特异性更高而生效。
- **INV-4：TikZ 一律用 SVG。**浏览器无法内联渲染 PDF 图片，因此 Quarto/HTML 中的所有 TikZ 图都必须通过 `/extract-tikz` 生成为 SVG。绝不要把 `.pdf` 嵌入 `.qmd` 幻灯片。
- **INV-5：单一文献库。**`Bibliography_base.bib` 是权威文献库，不得为每一讲单独建立 `.bib` 文件，所有引文都必须能在这份文件中解析。用 `./scripts/check-citations.py` 校验；这项静态检查同时检查两侧，可在渲染前运行，代码块中的 `@scope/pkg` 不算引文。**引文无法解析不是排版警告**：`compile-beamer.sh` 会因此返回退出码 3，而 `quarto render` 仍只发出 WARNING，所以不能只看 `quarto` 的退出码。

## 幻灯片设计不变量

- **INV-6：禁用 `\pause` 与 overlay。**禁止使用 Beamer 的 `\pause`、`\only`、`\visible`、`\onslide` 命令。理由见 `.codebuddy/rules/no-pause-beamer.md`。
- **INV-7：每页最多 2 个彩色框。**滥用 `keybox`、`definitionbox` 或提示块环境会造成「框疲劳」，因此每页最多放两个。用 `./scripts/check-box-density.py` 校验；检查器同时统计两侧，Beamer 按 `\begin{frame}` 分帧，Quarto 按一/二级标题分页，框的名单取自 `Quarto/theme-template.scss`，不另建一份。**只检查溢出无法发现这类违规**：内容较短的一页即使放了三个框也可能不溢出，但已经违反规则。
- **INV-8：先动机，后形式化。**给出每个定义之前，必须先用例子、直觉或现实问题说明动机。不要呈现没有动机的数学。

## R 脚本不变量

- **INV-9：`set.seed()` 只在顶上调用一次。**每个使用随机性的 R 脚本，都必须在脚本顶部、任何随机代码之前，恰好调用一次 `set.seed(N)`，绝不能把它放进循环或函数内部。
- **INV-10：只用相对路径。**不得使用绝对路径，包括 `/Users/...`、`C:\...` 和 `~` 展开。所有路径都相对于仓库根目录，并用 `file.path()` 保证跨平台兼容。
- **INV-11：Beamer 图形用透明背景。**所有为 Beamer 幻灯片生成图形的 `ggsave()` 调用，都必须带 `bg = "transparent"`。
- **INV-12：所有图都用项目主题。**每张 ggplot 图都必须使用项目的自定义主题，任何已提交的图都不得保留 ggplot2 默认的灰底。
