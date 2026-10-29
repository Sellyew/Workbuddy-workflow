---
name: compile-latex
description: 用 XeLaTeX 编译一套 Beamer LaTeX 幻灯片（3 遍 + bibtex）。用户说 "compile"、"build the slides"、"rebuild the PDF"、"run latex"、"render the tex" 时使用，或问某个 `.tex` 文件为什么不产出 PDF 时使用。作用于 `Slides/*.tex`。
description_zh: 用 XeLaTeX 编译一套 Beamer LaTeX 幻灯片（3 遍 + bibtex）。用户说 "compile"、"build the slides"、"rebuild the PDF"、"run latex"、"render the tex" 时使用，或问某个 `.tex` 文件为什么不产出 PDF 时使用。作用于 `Slides/*.tex`。
argument-hint: "[filename without .tex extension]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# 编译 Beamer LaTeX 幻灯片

用 XeLaTeX 编译一套 Beamer 幻灯片，并完整解析引文。

## 步骤

1. **进入 Slides/ 目录**，用三遍序列编译：

```bash
cd Slides
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode $ARGUMENTS.tex
BIBINPUTS=..:$BIBINPUTS bibtex $ARGUMENTS
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode $ARGUMENTS.tex
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

**替代方式（latexmk）：**
```bash
cd Slides
TEXINPUTS=../Preambles:$TEXINPUTS BIBINPUTS=..:$BIBINPUTS latexmk -xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

2. **检查警告：**
   - 在输出里 grep `Overfull \\hbox` 警告
   - grep `undefined citations` 或 `Label(s) may have changed`
   - 报告发现的任何问题

3. **打开 PDF** 做目视核验：
   ```bash
   open Slides/$ARGUMENTS.pdf          # macOS
   # xdg-open Slides/$ARGUMENTS.pdf    # Linux
   ```

4. **报告结果：**
   - 编译成功／失败
   - overfull hbox 警告的条数
   - 任何未定义的引文
   - PDF 页数

## 为什么要 3 遍？
1. 第一次 xelatex：生成带引文键的 `.aux` 文件
2. bibtex：读 `.aux`，生成带格式化参考文献的 `.bbl`
3. 第二次 xelatex：把参考文献并入
4. 第三次 xelatex：用最终的页码解析所有交叉引用

## 重要
- **永远用 XeLaTeX**，绝不用 pdflatex
- **TEXINPUTS** 是必需的：你的 Beamer 主题在 `Preambles/` 里
- **BIBINPUTS** 是必需的：你的 `.bib` 文件在仓库根目录
