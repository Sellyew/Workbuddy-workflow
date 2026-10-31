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

1. **跑编译脚本**——它负责三遍序列、bibtex、以及平台相关的 `TEXINPUTS`：

```bash
scripts/compile-beamer.sh $ARGUMENTS
```

加 `--dry-run` 只打印它将要用的环境变量（分隔符、`TEXINPUTS`、`BIBINPUTS`、是否会跑 bibtex）。退出码：`0` 通过、`1` 编译有错误、`2` 用法错误或找不到文件。

脚本已经把报告打好：页数、`Overfull \hbox` 条数、未定义引文与未定义引用的数量；有未定义引文时它逐个列出键名。

2. **打开 PDF** 做目视核验：
   ```bash
   open Slides/$ARGUMENTS.pdf          # macOS
   # xdg-open Slides/$ARGUMENTS.pdf    # Linux
   # start Slides\\$ARGUMENTS.pdf      # Windows
   ```

3. **报告结果：**
   - 编译成功／失败
   - overfull hbox 警告的条数
   - 任何未定义的引文
   - PDF 页数

## 为什么不要手写 `TEXINPUTS=../Preambles:$TEXINPUTS`

这条命令是从上游照搬的，它在 Windows 上是错的，而且错法很能误导人。

`kpathsea` 对 `TEXINPUTS` 的语义是：**你给的值替换默认搜索路径，除非它以路径分隔符结尾**——结尾的分隔符表示「在这之后追加默认值」。默认值里含 `.`，也就是当前目录。所以少写那个结尾分隔符，当前目录就从搜索路径里消失，于是：

```
! I can't find file `Lecture1.tex'.
! Emergency stop.
```

报错说「文件不存在」，而文件就在那里。照它去查文件会一无所获。

更麻烦的是分隔符本身**平台相关**：POSIX 的 kpathsea 用 `:`，而 **Windows 版 TeX Live 用 `;`**。在 Windows 上写 `:` 不会被当成分隔符，等价于「没有结尾分隔符」，于是落到同一条误导性报错上。`BIBINPUTS` 同理。

所以不要在任何文档里手抄这条命令——用 `scripts/compile-beamer.sh`，它按平台选分隔符，并保证两者都以分隔符结尾。手动编译时至少要写对：

```bash
cd Slides
SEP=$([ "${OS:-}" = "Windows_NT" ] && echo ';' || echo ':')
TEXINPUTS="../Preambles$SEP${TEXINPUTS:-}" BIBINPUTS="..$SEP${BIBINPUTS:-}" \
    xelatex -interaction=nonstopmode $ARGUMENTS.tex
```

## 为什么要 3 遍？
1. 第一次 xelatex：生成带引文键的 `.aux` 文件
2. bibtex：读 `.aux`，生成带格式化参考文献的 `.bbl`
3. 第二次 xelatex：把参考文献并入
4. 第三次 xelatex：用最终的页码解析所有交叉引用

## 重要
- **永远用 XeLaTeX**，绝不用 pdflatex
- **`TEXINPUTS` 是必需的**：你的 Beamer 主题在 `Preambles/` 里，且它必须**以平台分隔符结尾**（见上一节）
- **`BIBINPUTS` 是必需的**：你的 `.bib` 文件在仓库根目录，同样要以分隔符结尾
- 这两件事都由 `scripts/compile-beamer.sh` 处理；手写命令是踩坑的主要来源
