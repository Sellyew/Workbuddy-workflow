---
name: extract-tikz
description: 从 Beamer `.tex` 源中提取 TikZ 图，逐个编译为独立 PDF，再转成 SVG，索引从 0 起。用户说 "extract the tikz"、"regenerate the diagrams"、"rebuild the SVGs"、"sync tikz to quarto" 时使用，或在编辑了同时有 Quarto 镜像的 Beamer 讲稿中的 TikZ 块之后使用。
description_zh: 从 Beamer `.tex` 源中提取 TikZ 图，逐个编译为独立 PDF，再转成 SVG，索引从 0 起。用户说 "extract the tikz"、"regenerate the diagrams"、"rebuild the SVGs"、"sync tikz to quarto" 时使用，或在编辑了同时有 Quarto 镜像的 Beamer 讲稿中的 TikZ 块之后使用。
argument-hint: "[LectureN, e.g., Lecture2]"
allowed-tools: ["Read", "Bash", "Glob", "Agent", "Task"]
---

# 把 TikZ 图提取为 SVG

从 Beamer 源中提取 TikZ 图，编译为多页 PDF，再把每一页转成 SVG，供 Quarto 幻灯片使用。

> **是要新建一张图而不是提取？**用 [`/new-diagram`](../new-diagram/SKILL.md)——它从 `templates/tikz-snippets/` 脚手架生成，并预先套用了预防规则。

## 步骤

### 第 0 步：新鲜度检查（强制）

**编译之前，先确认 `extract_tikz.tex` 与当前 Beamer 源一致。**

1. 找到 Beamer 源：`ls Slides/$ARGUMENTS*.tex`
2. 从 Beamer 中提取所有 `\begin{tikzpicture}` 块
3. 与 `Figures/$ARGUMENTS/extract_tikz.tex` 比对
4. 若存在**任何**差异：从 Beamer 源更新 extract_tikz.tex
5. 若 extract_tikz.tex 不存在：从头创建它

### 第 1 步：预防性预检（强制——违反即中止）

编译之前，核验 `Figures/$ARGUMENTS/extract_tikz.tex` 里的每个 `\begin{tikzpicture}` 块都满足 [`.codebuddy/rules/tikz-prevention.md`](../../rules/tikz-prevention.md) 中的预防规则。这项预检是一个与 `/new-diagram` 共用的小 Python 脚本，好让两个技能强制执行同样的行为：

```bash
python scripts/check-tikz-prevention.py "Figures/$ARGUMENTS/extract_tikz.tex"
```

它检查什么：

- **P3——`scale=X` 却没有缩放节点。**裸 `scale=` 只缩小坐标，不缩小文字。允许的形式：`scale=X, every node/.style={scale=X}` 或 `scale=X, transform shape`。检查器会解析完整的 `\begin{tikzpicture}[...]` 选项块，即使它跨多行。
- **P4——边标签缺方位关键词。**每个边标签（`\draw` 里的 `node`）都必须带 `above`、`below`、`left`、`right`，或它们的复合形式（如 `above left`）。单写 `midway` 只是一个位置，不是方位。检查器扫描完整的 `\draw ...;` 语句，所以 `\draw` 写在一行、`node[...]{...}` 写在下一行也仍能关联上。

注意预检**不**强制什么：P1（带框节点的显式尺寸）与 P2（坐标映射注释）是结构性的，由 `tikz-reviewer` 在第 8 步标记，不在这里。

退出码：`0` = 全部文件通过，`1` = 有一处或多处 P3/P4 违规（stderr 列出文件、行号、片段、规则），`2` = 用法错误。

若非零退出：中止，报告出问题的行，并请用户修改 Beamer 源（单一真源）。**不要**编译。

### 第 2 步：进入该讲次自己的 Figures 目录
```bash
cd Figures/$ARGUMENTS
```

### 第 3 步：编译 extract_tikz.tex 文件
```bash
TEXINPUTS=../../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode extract_tikz.tex
```

### 第 4 步：数清页数
```bash
pdfinfo extract_tikz.pdf | grep "Pages:"
```

### 第 5 步：按 0 起索引把每页转成 SVG

**关键：PDF 的页是从 1 起数的，但输出的 SVG 文件名是从 0 起数的！**

```bash
PAGES=$(pdfinfo extract_tikz.pdf | grep "Pages:" | awk '{print $2}')
for i in $(seq 1 $PAGES); do
  idx=$(printf "%02d" $((i-1)))
  pdf2svg extract_tikz.pdf tikz_exact_$idx.svg $i
done
```

### 第 6 步：同步到 docs/ 以便部署
```bash
cd ../..
./scripts/sync_to_docs.sh $ARGUMENTS
```

### 第 7 步：核验 SVG 文件
- 读 2-3 个 SVG 文件，确认它们含有合法的 SVG 标记
- 确认文件大小合理（不是 0 字节）

### 第 8 步：视觉质量审读（tikz-reviewer）

在 TikZ 源块上生成 **tikz-reviewer** 代理（用 `Agent` 工具、`subagent_type=tikz-reviewer`），抓标签重叠、几何错误与视觉不一致。审读者会引用 [`.codebuddy/rules/tikz-measurement.md`](../../rules/tikz-measurement.md) 里的具体遍次与公式。若它返回 **NEEDS REVISION** 或 **REJECTED**，就循环：

1. 把建议的修改施加到 Beamer `.tex` 源（单一真源）。
2. 把更新后的块重新拷到 `extract_tikz.tex`。
3. 重跑预防性预检（第 1 步）并编译。
4. 重新生成 SVG，重新同步。
5. 重新调用 tikz-reviewer。

当 tikz-reviewer 返回 **APPROVED** 时停止（最多 5 轮）。

### 第 9 步：报告结果

## 单一真源提醒
TikZ 图**必须**先在 Beamer `.tex` 文件里改，再逐字拷到 `extract_tikz.tex`。见 `.codebuddy/rules/single-source-of-truth.md`。
