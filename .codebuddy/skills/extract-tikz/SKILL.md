---
name: extract-tikz
description: 从 Beamer `.tex` 源提取 TikZ 图，编译成一个多页 PDF，再逐页转换为从 0 编号的 SVG。用户说 "extract the tikz"、"regenerate the diagrams"、"rebuild the SVGs"、"sync tikz to quarto"、"提取 TikZ 图"、"重新生成 SVG" 时使用；编辑 Beamer 讲稿中的 TikZ 块后，如果该讲稿还有 Quarto 镜像，也要使用。
description_zh: 从 Beamer `.tex` 源提取 TikZ 图，编译成一个多页 PDF，再逐页转换为从 0 编号的 SVG。用户说 "extract the tikz"、"regenerate the diagrams"、"rebuild the SVGs"、"sync tikz to quarto"、"提取 TikZ 图"、"重新生成 SVG" 时使用；编辑 Beamer 讲稿中的 TikZ 块后，如果该讲稿还有 Quarto 镜像，也要使用。
argument-hint: "[LectureN, e.g., Lecture2]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Agent", "Task"]
---

# 把 TikZ 图提取为 SVG

从 Beamer 源提取 TikZ 图，编译成一个多页 PDF，再逐页转换为从 0 编号的 SVG，供 Quarto 幻灯片使用。

## 参数解析

从 `$ARGUMENTS` 解析唯一的位置参数并赋给 `lecture_name`。含空格的讲次名必须作为一个带引号参数传入；缺少讲次名、有多个位置参数或出现任何未知旗标时，报告用法错误并停止。旗标不得进入讲次名或任何路径。

解析后立即构造命名路径，后续所有命令都使用完整且加引号的路径，不再拼接原始 `$ARGUMENTS`：

```bash
output_dir="Figures/$lecture_name"
extract_tex="$output_dir/extract_tikz.tex"
extract_pdf="$output_dir/extract_tikz.pdf"
```

Beamer 真源在第 0 步解析为 `beamer_source`。

> **要新建一张图，而不是提取现有图？**请用 [`/new-diagram`](../new-diagram/SKILL.md)。它从 `templates/tikz-snippets/` 搭建，并预先套用预防规则。

## 步骤

### 第 0 步：新鲜度检查（强制）

**编译前，先确认 `extract_tikz.tex` 与当前 Beamer 源一致。**

1. 用 `Glob` 以 `Slides/${lecture_name}*.tex` 找到 Beamer 源，并把唯一匹配路径赋给 `beamer_source`；没有匹配或有多个匹配时停止并报告，不得猜测。
2. 用 `Read` 工具读取 `"$beamer_source"`，在内存中提取所有 `\begin{tikzpicture}` 块。
3. 与 `"$extract_tex"` 比对。
4. 只要有**任何**差异，就用 `Edit` 工具更新 `"$extract_tex"`，使其中的图块与 Beamer 真源一致；这里只同步提取源，不反向修改 Beamer。
5. 如果 `"$extract_tex"` 不存在，就用 `Write` 工具创建它，写入独立编译所需的文档骨架和来自 Beamer 真源的图块。Write 用于创建提取文件，不能代替后续对 Beamer 真源的修订。

### 第 1 步：预防性预检（强制——违反即中止）

编译前，核验 `"$extract_tex"` 中的每个 `\begin{tikzpicture}` 块都符合 [`.codebuddy/rules/tikz-prevention.md`](../../rules/tikz-prevention.md)。预检使用与 `/new-diagram` 共用的 Python 脚本，确保两个技能执行同一套规则：

```bash
python "scripts/check-tikz-prevention.py" "$extract_tex"
```

检查内容包括：

- **P3：使用 `scale=X`，却没有缩放节点。**裸 `scale=` 只缩坐标，不缩文字。允许写成 `scale=X, every node/.style={scale=X}` 或 `scale=X, transform shape`。即使 `\begin{tikzpicture}[...]` 选项跨多行，检查器也会解析完整选项块。
- **P4：边标签缺少方位关键词。**`\draw` 中每个边标签 `node` 都必须带 `above`、`below`、`left`、`right` 或其复合形式，例如 `above left`。`midway` 只表示位置，不表示方位。检查器扫描完整的 `\draw ...;` 语句，因此即使 `\draw` 与下一行的 `node[...]{...}` 分开，也能正确关联。

预检**不**检查 P1（带框节点的显式尺寸）和 P2（坐标映射注释）。这两项属于结构要求，由 `tikz-reviewer` 在第 8 步标记。

退出码 `0` 表示全部文件通过；`1` 表示存在一处或多处 P3/P4 违规，stderr 会列出文件、行号、片段和规则；`2` 表示用法错误。

退出码非零时，必须中止并报告问题行，请用户修改作为单一真源的 Beamer 源。**不要**编译。

### 第 2 步：确认该讲次自己的 Figures 输出目录

所有提取与编译产物都写入 `"$output_dir"`。不要 `cd`，也不要在后续命令中退回到未加引号的文件名。

### 第 3 步：编译 extract_tikz.tex 文件
```bash
# kpathsea 的路径分隔符平台相关：POSIX 用 ':'，Windows 版 TeX Live 用 ';'。
# 而且末尾那个分隔符不能省——缺了它，默认搜索路径（含 '.'）会被整个替换掉。
SEP=$([ "${OS:-}" = "Windows_NT" ] && echo ';' || echo ':')
TEXINPUTS="Preambles$SEP${TEXINPUTS:-}" xelatex -interaction=nonstopmode -output-directory="$output_dir" "$extract_tex"
```

### 第 4 步：数清页数
```bash
pdfinfo "$extract_pdf" | grep "Pages:"
```

### 第 5 步：按 0 起索引把每页转成 SVG

**关键：PDF 页码从 1 开始，输出的 SVG 文件索引却从 0 开始！**

```bash
PAGES=$(pdfinfo "$extract_pdf" | grep "Pages:" | awk '{print $2}')
for i in $(seq 1 "$PAGES"); do
  idx=$(printf "%02d" $((i-1)))
  svg_path="$output_dir/tikz_exact_$idx.svg"
  pdf2svg "$extract_pdf" "$svg_path" "$i"
done
```

### 第 6 步：同步到 docs/ 以便部署
```bash
"scripts/sync_to_docs.sh" "$lecture_name"
```

### 第 7 步：核验 SVG 文件
- 阅读 2-3 个 SVG 文件，确认包含合法的 SVG 标记。
- 确认文件大小合理，不能是 0 字节。

### 第 8 步：视觉质量审读（tikz-reviewer）

用 `Agent` 工具启动 **tikz-reviewer** 代理，设置 `subagent_type=tikz-reviewer`，审读 TikZ 源块中的标签重叠、几何错误和视觉不一致。审读者会引用 [`.codebuddy/rules/tikz-measurement.md`](../../rules/tikz-measurement.md) 中的具体遍次和公式。如果返回 **NEEDS REVISION** 或 **REJECTED**，就按以下步骤修订：

1. 用 `Edit` 工具把建议的修改应用到作为单一真源的 `"$beamer_source"`；视觉修订必须落在这里。
2. 用 `Edit` 工具将更新后的块同步到 `"$extract_tex"`；若该提取文件尚不存在，才改用 `Write` 按第 0 步创建。
3. 重跑第 1 步的预防性预检，再编译。
4. 重新生成并同步 SVG。
5. 再次调用 tikz-reviewer。

tikz-reviewer 返回 **APPROVED** 时停止，最多 5 轮。

### 第 9 步：报告结果

## 单一真源提醒
TikZ 图**必须**先改 Beamer `.tex` 文件，再逐字复制到 `extract_tikz.tex`。见 `.codebuddy/rules/single-source-of-truth.md`。
