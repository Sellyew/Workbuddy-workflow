---
name: new-diagram
description: 用片段库创建新的 TikZ 图，预先套用显式节点尺寸、坐标图和带方向的连线标签等防护规则。图可独立编译；技能会引用 tikz-measurement.md 调用 tikz-reviewer，并循环修订，直到 APPROVED。用户说“新建 TikZ 图”、“从片段画图”时使用。
description_zh: 用片段库创建新的 TikZ 图，预先套用显式节点尺寸、坐标图和带方向的连线标签等防护规则。图可独立编译；技能会引用 tikz-measurement.md 调用 tikz-reviewer，并循环修订，直到 APPROVED。用户说“新建 TikZ 图”、“从片段画图”时使用。
argument-hint: "[snippet-name] [output.tex] (both optional; interactive if omitted)"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Agent", "Task"]
disable-model-invocation: true
---

# 创建一张新的 TikZ 图

从 `templates/tikz-snippets/` 搭建图，先用防护规则检查，再独立编译并交给审读者度量，循环修订直到通过。请**优先使用本技能，不要从零手写 TikZ**；片段已经满足 `tikz-prevention.md` 要求的不变量。

## 输入

从 `$ARGUMENTS` 按 shell 风格引号解析位置参数：第一个可选参数是片段名，第二个可选参数是输出位置。多于两个位置参数、引号未闭合或出现未识别选项时，停止并报告用法错误，不要猜测参数含义。

- **片段名**：不含 `.tex`，必须精确对应 `templates/tikz-snippets/` 中的文件；拒绝路径分隔符和 `..`。省略时，列出片段库并请用户选择。
- **输出位置**：默认为 `Figures/new_diagram.tex`，必须以 `.tex` 结尾。相对路径以仓库根目录为基准解析为绝对路径；如果目标已存在，先询问用户，避免覆盖。

下文的 `<REPO_ROOT>`、`<SNIPPET>`、`<OUTPUT_TEX>`、`<OUTPUT_DIR>` 和 `<OUTPUT_STEM>` 都是占位符。每次调用 Bash、Edit 或 Agent 前，都从 `$ARGUMENTS` 重新解析并校验参数，再把占位符就地替换为完整值；其中输出路径、输出目录和不带扩展名的输出路径前缀必须是绝对路径。不要依赖上一次 Bash 调用留下的变量或工作目录。

## 工作流

### Step 1: 挑一个片段

```bash
ls -1 "<REPO_ROOT>/templates/tikz-snippets/"*.tex
```

当前片段库如下，说明见 [`templates/tikz-snippets/README.md`](../../../templates/tikz-snippets/README.md)：

- `dag-basic` —— 3 节点因果 DAG（X → Y，含混淆变量 U）
- `dag-mediation` —— X → M → Y，带直接路径
- `did-two-period` —— 两期双重差分
- `event-study` —— 事件时间系数与 95% 置信区间
- `timeline` —— 带错落事件的横向时间轴
- `regression-scatter` —— 散点 + OLS 拟合 + 置信带
- `flowchart-3step` —— 竖向流程，含判断菱形
- `supply-demand` —— 供需曲线与需求移动

如果片段名未提供或不在列表中，询问用户选择哪一个；提供了列表外的名称时，不要自动改成相近片段。

### Step 2: 把片段复制到输出路径

先重新解析 `$ARGUMENTS`，确认片段文件和输出位置，再把本次调用的所有占位符替换为完整路径。目标已存在时，必须先获得用户的覆盖确认，然后才执行复制。

```bash
test -f "<REPO_ROOT>/templates/tikz-snippets/<SNIPPET>.tex" || exit 2
if [ -f "<OUTPUT_TEX>" ]; then
  echo "Output path already exists: <OUTPUT_TEX>"
  exit 1
fi
mkdir -p "<OUTPUT_DIR>"
cp "<REPO_ROOT>/templates/tikz-snippets/<SNIPPET>.tex" "<OUTPUT_TEX>"
```

得到覆盖确认后，重新解析参数并另发一次只含 `mkdir -p "<OUTPUT_DIR>"` 与 `cp "<REPO_ROOT>/templates/tikz-snippets/<SNIPPET>.tex" "<OUTPUT_TEX>"` 的调用；不要沿用上一次调用的 shell 状态。

### Step 3: 按用户意图修改内容

先问用户图要表达什么，再用 `Edit` 工具编辑 `<OUTPUT_TEX>`：

1. 更新顶部注释块，让**意图句**符合用户目标。
2. 如果坐标改变，同步更新**坐标图**注释。
3. 重命名节点并改写标签。除非含义确实改变，否则保留节点样式，例如 `dag-node`、`flow-node`。
4. **不要**给 tikzpicture 选项添加裸 `scale=X`。坐标会缩放，文字却不会，因而容易碰撞。可以写成 `scale=X, every node/.style={scale=X}` 或 `scale=X, transform shape`。完整规则见 [`tikz-prevention.md` P3](../../rules/tikz-prevention.md)，`scale=1.1` 的约定见 `tikz-visual-quality.md`。
5. **每条**新连线标签都必须带方向关键词，例如 `above`、`below`、`left`、`right`、`above left`。`midway` 只表示路径位置，不表示方向；单独使用会违反 P4。

### Step 4: 防护预检（强制）

运行与 `/extract-tikz` 共用的 Python 检查器。它是唯一能让两个技能一致执行 P3 和 P4 的工具：

```bash
python "<REPO_ROOT>/scripts/check-tikz-prevention.py" "<OUTPUT_TEX>"
```

- 退出码 `0`：通过，继续。
- 退出码 `1`：存在违规，stderr 会报告行号、规则和片段。修复 `<OUTPUT_TEX>` 并重跑，直到通过。
- 退出码 `2`：用法错误，例如文件缺失。

不要临时另写 grep 代替检查器。Python 检查器能正确解析跨多行的 `\begin{tikzpicture}[...]` 选项和 `\draw ... node {...}`，逐行 grep 会漏掉这些情况。

### Step 5: 独立编译

所有片段都使用 `\documentclass[border=4pt]{standalone}`，不需要 Beamer 帧或 `Preambles/header.tex` 即可编译：

```bash
xelatex -interaction=nonstopmode -output-directory="<OUTPUT_DIR>" "<OUTPUT_TEX>" > "<OUTPUT_DIR>/tikz-compile.log" 2>&1
```

检查退出码和 `<OUTPUT_STEM>.pdf` 的文件大小。编译失败时，阅读 `<OUTPUT_DIR>/tikz-compile.log`，再修复 `<OUTPUT_TEX>`。下一次重编译仍须从 `$ARGUMENTS` 重新构造这些绝对路径。

### Step 6: 由 tikz-reviewer 做视觉审读

用 `Task` 启动 `tikz-reviewer` 代理，设置 `subagent_type=tikz-reviewer`，传入本次重新构造的 `<OUTPUT_TEX>` 和 `<OUTPUT_STEM>.pdf` 两个绝对路径。审读者必须为每条 CRITICAL/MAJOR 发现引用 [`tikz-measurement.md`](../../rules/tikz-measurement.md) 中对应的通过项和公式；含糊报告会被退回。

按以下结果循环：

1. 返回 `APPROVED` 时，进入 Step 7。
2. 返回 `NEEDS REVISION` 或 `REJECTED` 时，修复 `<OUTPUT_TEX>`，重跑 Step 4 的防护预检和 Step 5 的编译，再次调用审读者。

**最多 5 轮。** 如果 5 轮后仍有 CRITICAL 问题，把情况告诉用户。此时可能需要重做片段或重新设计内容，而不是继续微调。

### Step 7: 可选——转成 SVG 供 Quarto 使用

如果用户要把图用于 Quarto 幻灯片，而不只是 Beamer，就把编译所得 PDF 转成 SVG：

```bash
pdf2svg "<OUTPUT_STEM>.pdf" "<OUTPUT_STEM>.svg" 1
```

基于片段的图都是单页，因此这里会生成一个与 `.tex` 同名的 `.svg`。`/extract-tikz` 则不同：它从 `Figures/LectureN/extract_tikz.tex` 主文件生成多页 PDF，输出命名为 `tikz_exact_00.svg, tikz_exact_01.svg, ...`，文件索引从 0 开始，PDF 页码从 1 开始。需要逐页揭示的多页输出时，改用 `/extract-tikz`。

### Step 8: 清理构建产物

```bash
rm -f "<OUTPUT_DIR>"/*.aux "<OUTPUT_DIR>"/*.log "<OUTPUT_DIR>"/*.out "<OUTPUT_DIR>"/*.synctex.gz
```

保留 `.pdf` 和已经生成的 `.svg`，下游工具需要使用它们。

### Step 9: 报告

汇总以下信息：

- 使用的片段和输出路径。
- 审读者判定与轮数。
- `.pdf` 大小和页数。
- `.svg` 路径（若已生成）。
- 提醒用户在目标 Beamer/Quarto 文件中用 `\input` 或 `\includegraphics` 引入这张图。

## 为什么从片段起步？

作者很难凭肉眼估计曲线和标签的位置，从零手写 TikZ 很容易产生碰撞。片段已经包含 `tikz-prevention.md` 要求的坐标图、显式节点尺寸和带方向的连线标签，因此结构上就能通过防护预检。你可以按需要偏离片段，但仍须遵守这些规则。

## 交叉引用

- [`.codebuddy/rules/tikz-prevention.md`](../../rules/tikz-prevention.md) —— P1–P6 编写规则。
- [`.codebuddy/rules/tikz-measurement.md`](../../rules/tikz-measurement.md) —— 六遍协议及其公式，审读者会引用它们。
- [`.codebuddy/rules/tikz-visual-quality.md`](../../rules/tikz-visual-quality.md) —— 通用视觉标准。
- [`.codebuddy/skills/extract-tikz/SKILL.md`](../extract-tikz/SKILL.md) —— 从既有 Beamer 讲义里抽取 TikZ，而不是新建。
- [`templates/tikz-snippets/README.md`](../../../templates/tikz-snippets/README.md) —— 片段库清单与改写指南。
