---
name: new-diagram
description: 从片段库中搭建一张新的 TikZ 图，并预先套上防护规则（显式节点尺寸、坐标图、带方向的连线标签）。它能独立编译，带着 tikz-measurement.md 中的引文调用 tikz-reviewer，并在修订上循环直到 APPROVED。
description_zh: 从片段库中搭建一张新的 TikZ 图，并预先套上防护规则（显式节点尺寸、坐标图、带方向的连线标签）。它能独立编译，带着 tikz-measurement.md 中的引文调用 tikz-reviewer，并在修订上循环直到 APPROVED。
argument-hint: "[snippet-name] [output.tex] (both optional; interactive if omitted)"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Agent", "Task"]
disable-model-invocation: true
---

# 创建一张新的 TikZ 图

从 `templates/tikz-snippets/` 搭建一张图，用防护规则检查它，独立编译，带着度量引文跑审读者，并循环到这张图通过为止。请**用它代替**从零手写 TikZ；这些片段内嵌了 `tikz-prevention.md` 所要求的不变量。

## 输入

- `$0`（可选）—— 片段名（不含 `.tex`）。须是 `templates/tikz-snippets/` 中的某个文件名。若省略，列出片段库并请用户选择。
- `$1`（可选）—— 输出路径。默认为 `Figures/new_diagram.tex`——若该目标已存在，先问用户，以免覆盖。

## 工作流

### Step 1: 挑一个片段

```bash
ls -1 templates/tikz-snippets/*.tex
```

当前片段库（说明见 [`templates/tikz-snippets/README.md`](../../../templates/tikz-snippets/README.md)）：

- `dag-basic` —— 3 节点因果 DAG（X → Y，含混淆变量 U）
- `dag-mediation` —— X → M → Y，带直接路径
- `did-two-period` —— 两期双重差分
- `event-study` —— 事件时间系数与 95% 置信区间
- `timeline` —— 带错落事件的横向时间轴
- `regression-scatter` —— 散点 + OLS 拟合 + 置信带
- `flowchart-3step` —— 竖向流程，含判断菱形
- `supply-demand` —— 供需曲线与需求移动

若 `$0` 不在此列，或未提供，问用户要用哪一个。

### Step 2: 把片段复制到输出路径

```bash
SRC="templates/tikz-snippets/$0.tex"
DST="${1:-Figures/new_diagram.tex}"

# Confirm before overwriting
if [ -f "$DST" ]; then
  echo "Output path already exists: $DST"
  # Ask the user whether to overwrite. Do NOT clobber silently.
fi

mkdir -p "$(dirname "$DST")"
cp "$SRC" "$DST"
```

### Step 3: 按用户意图修改内容

问用户这张图要表达什么。用 `Edit` 工具编辑 `$DST`：

1. 更新顶部的注释块，让**意图句**与用户的目标一致。
2. 若坐标有变，更新**坐标图**注释。
3. 重命名节点、改写标签。除非含义真的变了，保留节点样式（`dag-node`、`flow-node` 等）。
4. **不要**给 tikzpicture 选项加裸的 `scale=X`。坐标会缩，文字不会——碰撞随之而来。允许的写法：`scale=X, every node/.style={scale=X}` 或 `scale=X, transform shape`。完整规则见 [`tikz-prevention.md` P3](../../rules/tikz-prevention.md)，`scale=1.1` 的约定见 `tikz-visual-quality.md`。
5. **每一条**新连线标签都必须带方向关键词（`above`、`below`、`left`、`right`、`above left` 等）。单写 `midway` 只是路径位置，不是方向——属 P4 违规。

### Step 4: 防护预检（强制）

运行 `/extract-tikz` 所用的同一个共享 Python 检查器——它是让 P3 与 P4 在两个技能间被一致执行的唯一工具：

```bash
python scripts/check-tikz-prevention.py "$DST"
```

- 退出码 `0` → 通过，继续。
- 退出码 `1` → 有违规（stderr 会报出行号、规则、片段）。修 `$DST` 并重跑，直到归零。
- 退出码 `2` → 用法错误（文件缺失等）。

不要就地重新实现一遍 grep。Python 检查器能正确处理多行的 `\begin{tikzpicture}[...]` 选项与多行的 `\draw ... node {...}`，这些是逐行 grep 看不见的。

### Step 5: 独立编译

所有片段都是 `\documentclass[border=4pt]{standalone}`，因此无需 Beamer 帧、也无需 `Preambles/header.tex` 即可编译：

```bash
cd "$(dirname "$DST")"
xelatex -interaction=nonstopmode "$(basename "$DST")" > /tmp/tikz-compile.log 2>&1
```

检查退出码与 `*.pdf` 文件大小。若编译失败，读 `/tmp/tikz-compile.log` 并修 `.tex` 源码。

### Step 6: 由 tikz-reviewer 做视觉审读

用 `Task` 派生 `tikz-reviewer` 代理（`subagent_type=tikz-reviewer`）。把 `.tex` 源码与编译出的 `.pdf` 路径传给它。审读者现在必须为每一条 CRITICAL/MAJOR 发现引用 [`tikz-measurement.md`](../../rules/tikz-measurement.md) 中对应的通过项与公式——含糊的报告会被打回。

循环：

1. 若 `APPROVED` → 进入 Step 7。
2. 若 `NEEDS REVISION` 或 `REJECTED` → 对 `$DST` 施加修复，重跑 Step 4（防护预检），重新编译（Step 5），再次调用审读者。

**最多 5 轮。** 若 5 轮之后审读者仍在报 CRITICAL 问题，把情况摆给用户——可能需要重做片段或重新设计所要求的内容，而不只是微调。

### Step 7: 可选——转成 SVG 供 Quarto 使用

若用户打算把这张图用在 Quarto 幻灯片里（不只是 Beamer），把编译出的 PDF 转成 SVG：

```bash
pdf2svg "${DST%.tex}.pdf" "${DST%.tex}.svg" 1
```

基于片段的图都是单页，所以产出一个与 `.tex` 同名的单个 `.svg` 在这里是对的。这与 `/extract-tikz` 不同：后者从 `Figures/LectureN/extract_tikz.tex` 主文件产出多页 PDF，并把输出命名为 `tikz_exact_00.svg, tikz_exact_01.svg, ...`（文件名从 0 起，对应从 1 起编号的 PDF 页）。若你需要逐页揭示式的多页输出，改用 `/extract-tikz`。

### Step 8: 清理构建产物

```bash
cd "$(dirname "$DST")"
rm -f *.aux *.log *.out *.synctex.gz
```

保留 `.pdf` 与 `.svg`（若已生成）。它们是下游工具要用的东西。

### Step 9: 报告

打印一份摘要：

- 所用片段 → 输出路径
- 审读者判定与轮数
- `.pdf` 大小与页数
- `.svg` 路径（若已生成）
- 提醒在目标 Beamer/Quarto 文件里用 `\input` 或 `\includegraphics` 引入这张图

## 为什么从片段起步？

从零手写 TikZ 几乎必然产出碰撞，因为作者无法用肉眼估出曲线和标签会落在哪里。片段内嵌了 `tikz-prevention.md` 所要求的不变量——坐标图、显式节点尺寸、带方向的连线标签——所以这张图在构造上就通过了防护预检。你随时可以偏离片段；规则仍然适用。

## 交叉引用

- [`.codebuddy/rules/tikz-prevention.md`](../../rules/tikz-prevention.md) —— P1–P6 编写规则。
- [`.codebuddy/rules/tikz-measurement.md`](../../rules/tikz-measurement.md) —— 六遍协议及其公式，审读者会引用它们。
- [`.codebuddy/rules/tikz-visual-quality.md`](../../rules/tikz-visual-quality.md) —— 通用视觉标准。
- [`.codebuddy/skills/extract-tikz/SKILL.md`](../extract-tikz/SKILL.md) —— 从既有 Beamer 讲义里抽取 TikZ，而不是新建。
- [`templates/tikz-snippets/README.md`](../../../templates/tikz-snippets/README.md) —— 片段库清单与改写指南。
