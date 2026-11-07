---
paths:
  - "Slides/**/*.tex"
  - "Figures/**/*.tex"
  - "Preambles/**/*.tex"
---

# TikZ 预防规则

**编写 TikZ 时就要避免碰撞。**本规则与 `tikz-visual-quality.md` 的通用标准和 `tikz-measurement.md` 的修补公式互补。每次撰写或编辑 `\begin{tikzpicture}` 块时都要加载。

> 改编自 Scott Cunningham 的 `tikz_rules.md`，载于 [MixtapeTools](https://github.com/scunning1975/MixtapeTools)。已注明出处。

标签压住箭头、标签穿过形状边界、箭头彼此穿过时，LaTeX 编译器都**不会**发出警告。因此，必须在撰写或审读时发现每一个此类 bug。这些规则把检查提前到问题产生之时。

---

## 规则 P1：**带框**节点必须显式给尺寸（强制）

每个承载文字的*带框*节点都必须显式声明尺寸。这里的带框节点包括使用 `draw`、`fill` 或 TikZ 样式库中自定义节点样式绘制的节点，例如 `dag-node`、`flow-node`、`decision-node`，也包括 `rectangle`、`diamond`、`circle` 等任何带 `draw`/`fill` 的形状样式。如果尺寸完全隐式决定，文字可能超出框边缘而无人察觉。

```latex
% BAD — node size grows silently with text length
\node[draw, rounded corners] (X) {Pre-trends assumption};

% GOOD — explicit box; text wraps or the author notices
\node[draw, rounded corners, minimum width=3.2cm, minimum height=1.0cm,
      text width=3.0cm, align=center] (X) {Pre-trends assumption};
```

根据框的行为选择一种方式：

- `minimum width` + `minimum height`：用于尺寸不应取决于文字的框。
- `text width` + `align=center`（或 `left`）：用于高度应随文字增长的框。

任何多行内容，包括任何含 `\\` 的内容，都必须设置 `text width`。

### 范围——P1 **不**覆盖什么

P1 刻意**不**约束普通标签、坐标轴刻度、坐标轴标题和自由浮动的注释，例如 `\node[above] {label}`、`\node[below, font=\footnotesize] at (\x, -0.1) {\x}`。如果强制它们声明尺寸，每个坐标轴刻度都会增加不必要的语法负担，也会与片段库自身的用法冲突。

无框标签的正确位置由 P4 的方位关键词和 `tikz-measurement.md` 的度量规则保证，包括间隙计算与边界间隙。

---

## 规则 P2：坐标映射注释（≥3 个节点时强制）

任何包含三个或更多节点的图，都要在 `\begin{tikzpicture}` 前放置注释块，列出具名坐标，并用一句话说明图的意图。注释块既是读者的图例，也迫使作者按绝对坐标思考，避免坐标在相对引用中逐渐漂移。

```latex
% Diagram: Confounded DAG — X caused by U, Y caused by X and U.
% Coordinates: (x, y)
%   U at (3, 2)   -- confounder, top center
%   X at (0, 0)   -- treatment, lower left
%   Y at (6, 0)   -- outcome, lower right
\begin{tikzpicture}
  \node (U) at (3, 2) {U};
  ...
\end{tikzpicture}
```

---

## 规则 P3：单独用 `scale=X` 被禁——要连同节点一起缩放

真正的风险是**不对称缩放**：`scale=0.8` 会缩小坐标，却*不会*缩小文字。2 cm 的间隙因此变成 1.6 cm，原本放得下的 1.2 cm 标签可能发生重叠。度量规则要防止的碰撞，会因此悄悄出现。

**禁止：**使用 `\begin{tikzpicture}[scale=X]` 而不同时缩放节点。这种写法不安全。

**允许：**以下写法会同时缩放坐标*和*节点，因此可以保留间隙与标签之间的几何关系：

```latex
% Full-width diagrams — recommended default in tikz-visual-quality.md
\begin{tikzpicture}[scale=1.1, every node/.style={scale=1.1}]

% Or use transform shape to scale node contents with coordinates
\begin{tikzpicture}[scale=0.85, transform shape]
```

只要遵守这些写法，`tikz-visual-quality.md` 中的 `[scale=1.1]` 惯例就没有问题。如果只写 `scale=` 而不缩放节点，`/extract-tikz` 第 1 步的预防性预检会中止流水线。

---

## 规则 P4：每条边标签都要有方位关键词

每条挂在边上的标签都必须带方位关键词：`above`、`below`、`left`、`right` 或它们的复合形式。裸写 `node {label}` 会把文字放在箭头上，造成稳定碰撞，而编译不会报警。

```latex
% BAD — label sits on the arrow line
\draw[->] (A) -- (B) node[midway] {confounded};

% GOOD — explicit direction
\draw[->] (A) -- (B) node[midway, above] {confounded};
```

| 箭头朝向 | 优先关键词 |
|-------------------|-------------------|
| 水平 | `above` 或 `below` |
| 竖向 | `left` 或 `right` |
| 斜向 | 空白更多的那一侧 |
| 弯曲（`bend left/right`） | 弯曲外侧的 `above` |

平行箭头的标签要错开：一个使用 `pos=0.3`，另一个使用 `pos=0.7`，或者交替使用 `above`/`below`。

---

## 规则 P5：使用标准片段

`templates/tikz-snippets/` 为常见学术图提供了经过验证的起点，包括 DAG、DiD 图、事件研究、时间轴、流程图、供需图、回归散点和中介。每个片段都落实了规则 P1–P4，并附坐标映射。

推荐流程：

1. 使用 `/new-diagram <snippet-name>`，由 `/new-diagram` 技能根据片段库搭建脚手架。
2. 也可以手工复制片段：`cp templates/tikz-snippets/dag-basic.tex Figures/LectureN/my-dag.tex`。
3. 根据实际情况修改节点标签与坐标，**同时更新坐标映射。**
4. 完成以上步骤后，才调用 `/extract-tikz` 或 `/compile-latex`。

可以从零编写新图，但仍必须满足 P1–P4 *以及* `tikz-measurement.md` 中的度量规则。

---

## 规则 P6：一个 tikzpicture 只装一个想法

一个 `\begin{tikzpicture}` 应只表达一个想法。如果需要展示一个序列，例如逐步揭示 DAG 或比较前后状态，就使用多个 tikzpicture，每帧或每个子图一个，不要在同一个 tikzpicture 中堆满条件分支或 overlay 层。

这样可以把每张图控制在度量规则能够有效处理的规模内。

---

## 执行

- `/extract-tikz` 第 1 步在编译前运行检查器，`/new-diagram` 第 4 步在独立编译前运行同一个检查器：`python scripts/check-tikz-prevention.py`。这个 Python 解析器能够识别多行结构，不是逐行 grep，因此两个技能的检查行为不会分叉。检查器发现 P3 的裸 `scale=` 未缩放节点，或 P4 的边标签缺少方位关键词时，会中止并报告文件、行号和问题片段。它不检查 P1、P2 或 P5–P6，这些由审读者负责。`tikz-reviewer` 会在目视审读中标记 P1 的带框节点尺寸和 P2 的坐标映射，分别位于 `/extract-tikz` 步骤 8 和 `/new-diagram` 步骤 6。
- `tikz-reviewer` 报告 CRITICAL/MAJOR 问题时，按名称引用这些规则。
- 质量打分由 `scripts/quality_score.py` 定义，并镜像到 [`quality-gates.md`](quality-gates.md)。Quarto 评分细则会对一项 TikZ 标签重叠发现扣 −5 分，这通常说明某条 P1/P3/P4 违规已经影响最终产物。目前评分细则**不**按规则逐条扣分，也没有检测器生成重叠这一行；审读者的发现就是执行方式。
