---
name: compile-latex
description: 用 XeLaTeX 编译 Beamer LaTeX 幻灯片，执行 3 遍编译和 bibtex。用户说 "compile"、"build the slides"、"rebuild the PDF"、"run latex"、"render the tex"、"编译幻灯片"、"重新生成 PDF" 时使用，也用于排查 `.tex` 文件为什么没有生成 PDF。作用于 `Slides/*.tex`。
description_zh: 用 XeLaTeX 编译 Beamer LaTeX 幻灯片，执行 3 遍编译和 bibtex。用户说 "compile"、"build the slides"、"rebuild the PDF"、"run latex"、"render the tex"、"编译幻灯片"、"重新生成 PDF" 时使用，也用于排查 `.tex` 文件为什么没有生成 PDF。作用于 `Slides/*.tex`。
argument-hint: "[filename without .tex extension] [--dry-run]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# 编译 Beamer LaTeX 幻灯片

用 XeLaTeX 编译 Beamer 幻灯片，并完整解析引文。

## 参数解析

先从 `$ARGUMENTS` 解析并剥离 `--dry-run`，设置命名开关 `dry_run`；该旗标可位于讲次名前后。剩余参数必须恰好是一个讲次名，赋给 `lecture_name`，并去掉可选的 `.tex` 后缀。未知旗标、缺少讲次名或有多个位置参数时，报告用法错误并停止。含空格的讲次名必须作为一个带引号参数传入，旗标不得进入讲次名或路径。

随后构造命名路径，后续每次调用都使用这些完整路径并加引号，不再拼接原始 `$ARGUMENTS`：

```bash
output_dir="Slides"
tex_path="$output_dir/$lecture_name.tex"
pdf_path="$output_dir/$lecture_name.pdf"
```

## 步骤

1. **运行编译脚本。**脚本会完成三遍编译和 bibtex，并按平台设置 `TEXINPUTS`：

```bash
if [ "$dry_run" = true ]; then
  "scripts/compile-beamer.sh" "$lecture_name" --dry-run
else
  "scripts/compile-beamer.sh" "$lecture_name"
fi
```

- `--dry-run`：只打印将使用的环境变量，包括分隔符、`TEXINPUTS`、`BIBINPUTS` 和是否运行 bibtex，不执行编译。它只设置 `dry_run`，不会拼进源文件或 PDF 路径。

退出码 `0` 表示通过，`1` 表示编译错误，`2` 表示用法错误或找不到文件，`3` 表示 **PDF 已生成但引文等内容检查未通过**。退出码 `3` 不能报告为编译成功。

脚本会报告页数、`Overfull \hbox` 条数以及未定义引文和未定义引用的数量；有未定义引文时，还会逐个列出键名。

2. **打开 PDF 目视检查（`dry_run` 为 false 时）：** 使用解析阶段生成的完整 `pdf_path`：
   ```bash
   open "$pdf_path"          # macOS
   # xdg-open "$pdf_path"    # Linux
   # start "" "$pdf_path"    # Windows
   ```

3. **报告以下结果：**
   - 编译成功还是失败。
   - overfull hbox 警告的条数。
   - 所有未定义的引文。
   - PDF 页数。

## 为什么不要手写 `TEXINPUTS=../Preambles:$TEXINPUTS`

这条从上游照搬的命令在 Windows 上是错的，而且报错很容易误导排查方向。

`kpathsea` 会用你给出的 `TEXINPUTS` **替换默认搜索路径，除非该值以路径分隔符结尾**。末尾分隔符表示在后面追加默认值，而默认值包含当前目录 `.`。漏掉末尾分隔符后，当前目录就不在搜索路径中，于是出现：

```
! I can't find file `Lecture1.tex'.
! Emergency stop.
```

文件明明存在，编译器却报告找不到。沿这个提示检查文件是否存在，只会走错方向。

分隔符也随平台变化：POSIX 的 kpathsea 使用 `:`，**Windows 版 TeX Live 使用 `;`**。Windows 上的 `:` 不会被当成分隔符，效果等同于漏掉末尾分隔符，因此仍会出现同一条误导性报错。`BIBINPUTS` 也遵循这套规则。

所以不要把这条命令手抄到任何文档中。`scripts/compile-beamer.sh` 会按平台选择分隔符，并确保两个变量都以分隔符结尾。必须手动编译时，至少要写对：

```bash
SEP=$([ "${OS:-}" = "Windows_NT" ] && echo ';' || echo ':')
TEXINPUTS="Preambles$SEP${TEXINPUTS:-}" BIBINPUTS=".$SEP${BIBINPUTS:-}" \
    xelatex -interaction=nonstopmode -output-directory="$output_dir" "$tex_path"
```

## 为什么要 3 遍？
1. 第一次 xelatex：生成带引文键的 `.aux` 文件。
2. bibtex：读取 `.aux`，生成带格式化参考文献的 `.bbl`。
3. 第二次 xelatex：并入参考文献。
4. 第三次 xelatex：用最终页码解析所有交叉引用。

## 重要
- **始终使用 XeLaTeX**，绝不用 pdflatex。
- **必须设置 `TEXINPUTS`**：Beamer 主题位于 `Preambles/`，变量值必须**以平台分隔符结尾**，原因见上一节。
- **必须设置 `BIBINPUTS`**：`.bib` 文件位于仓库根目录，变量值同样要以分隔符结尾。
- `scripts/compile-beamer.sh` 已处理这两项设置；手写命令是主要的踩坑来源。
