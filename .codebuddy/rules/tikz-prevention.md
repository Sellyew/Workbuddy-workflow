---
paths:
  - "Slides/**/*.tex"
  - "Figures/**/*.tex"
  - "Preambles/**/*.tex"
---

# TikZ 预防规则

**写一开始就不会碰撞的 TikZ。** 与 `tikz-visual-quality.md`（通用标准）和 `tikz-measurement.md`（修补时的公式）互补。每当你在撰写或编辑一个 `\begin{tikzpicture}` 块时就加载。

> 改编自 Scott Cunningham 的 `tikz_rules.md`，载于 [MixtapeTools](https://github.com/scunning1975/MixtapeTools)。已注明出处。

LaTeX 编译器对标签压在箭头上、标签穿过形状边界、箭头穿过箭头，都**不**警告。这类 bug 每一个都必须在撰写时或审读时抓住。这些规则把捕捉点前移。

---

## 规则 P1：**带框**节点必须显式给尺寸（强制）

每个*带框*的承载文字的节点——用 `draw`、`fill`、TikZ 样式库里的自定义节点样式（例如 `dag-node`、`flow-node`、`decision-node`）画的，或任何像 `rectangle`、`diamond`、`circle` 这类带 `draw`/`fill` 的形状样式——都必须显式声明尺寸。隐式定尺寸意味着文字可以长出框边缘而无人察觉。

```latex
% BAD — node size grows silently with text length
\node[draw, rounded corners] (X) {Pre-trends assumption};

% GOOD — explicit box; text wraps or the author notices
\node[draw, rounded corners, minimum width=3.2cm, minimum height=1.0cm,
      text width=3.0cm, align=center] (X) {Pre-trends assumption};
```

二选一：

- `minimum width` + `minimum height`——用于尺寸不应取决于文字的框。
- `text width` + `align=center`（或 `left`）——用于高度应随文字增长的框。

任何多行内容（含 `\\` 的任何东西）都要求 `text width`。

### 范围——P1 **不**覆盖什么

普通标签、坐标轴刻度、坐标轴标题、以及自由浮动的注释（`\node[above] {label}`、`\node[below, font=\footnotesize] at (\x, -0.1) {\x}` 等）刻意**不**受 P1 约束。对它们强加尺寸会让每个坐标轴刻度都变成语法负担，并与片段库自身的用法冲突。

对那些不带框的标签，正确性由 P4（方位关键词）以及 `tikz-measurement.md` 里的度量规则（间隙计算、边界间隙）来保证。

---

## 规则 P2：坐标映射注释（≥3 个节点时强制）

任何有三个或更多节点的图，都要在 `\begin{tikzpicture}` 之前放一个注释块，列出具名坐标，并写一句说明意图的话。这是给读者的图例；它也迫使作者用绝对坐标思考，而不是任由坐标相对漂移。

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

真正的失效模式是**不对称缩放**：`scale=0.8` 缩小坐标，但*不*缩小文字。2 cm 的间隙变成 1.6 cm；原本放得下的 1.2 cm 标签现在就重叠了。这会悄悄产出度量规则正是为了防止的那些碰撞。

**禁止。** `\begin{tikzpicture}[scale=X]` 且没有配套的节点缩放。这是不安全的写法。

**允许——对称的写法。** 它们把坐标*和*节点一起缩放，所以间隙/标签的几何关系得以保留：

```latex
% Full-width diagrams — recommended default in tikz-visual-quality.md
\begin{tikzpicture}[scale=1.1, every node/.style={scale=1.1}]

% Or use transform shape to scale node contents with coordinates
\begin{tikzpicture}[scale=0.85, transform shape]
```

守住这几种写法时，`tikz-visual-quality.md` 里的 `[scale=1.1]` 惯例没有问题。写裸 `scale=` 而不缩放节点时，`/extract-tikz`（第 1 步）里的预防性预检会中止流水线。

---

## 规则 P4：每条边标签都要有方位关键词

挂在边上的每个标签都必须带一个方位关键词（`above`、`below`、`left`、`right`，或复合形式）。裸写 `node {label}` 会把文字放在箭头上——稳定碰撞，静默编译。

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

对平行箭头，把标签错开：一个用 `pos=0.3`，另一个用 `pos=0.7`，或者交替 `above`/`below`。

---

## 规则 P5：使用标准片段

`templates/tikz-snippets/` 里放着常见学术图的已验证起点（DAG、DiD 图、事件研究、时间轴、流程图、供需图、回归散点、中介）。每个片段都内嵌了规则 P1–P4 并带一张坐标映射。

推荐流程：

1. `/new-diagram <snippet-name>`——`/new-diagram` 技能从片段库里搭脚手架。
2. 或手工复制片段：`cp templates/tikz-snippets/dag-basic.tex Figures/LectureN/my-dag.tex`。
3. 改节点标签与坐标以适配你的情形。**让坐标映射保持最新。**
4. 到这时才调用 `/extract-tikz` 或 `/compile-latex`。

从零写一张全新的图是允许的，但仍必须满足 P1–P4 *以及* `tikz-measurement.md` 里的度量规则。

---

## 规则 P6：一个 tikzpicture 只装一个想法

一个 `\begin{tikzpicture}` 应当只编码一个想法。如果你要展示一个序列（DAG 的逐步揭示、前/后对比），就用多个 tikzpicture——每帧或每个子图一个——而不是一个装满了条件分支或 overlay 层的 tikzpicture。

这样每张图都足够小，度量规则才处理得动。

---

## 执行

- `/extract-tikz`（第 1 步，编译前）与 `/new-diagram`（第 4 步，其独立编译前）都跑同一个检查器 `python scripts/check-tikz-prevention.py`，它是一个能识别多行的 Python 解析器，而不是逐行 grep，所以两个技能不会漂移。它在 P3（裸 `scale=` 无节点缩放）与 P4（边标签没有方位关键词）上中止，并报告出问题的文件、行号与片段。它不检查 P1、P2 或 P5–P6：那些属于审读者的关切，`tikz-reviewer` 在它的目视审读中标记 P1（带框节点尺寸）与 P2（坐标映射）（`/extract-tikz` 的步骤 8、`/new-diagram` 的步骤 6）。
- `tikz-reviewer` 在报告 CRITICAL/MAJOR 问题时按名字引用这些规则。
- 质量打分定义在 `scripts/quality_score.py`，并在 [`quality-gates.md`](quality-gates.md) 中镜像。Quarto 评分细则对一条 TikZ 标签重叠发现扣 −5（那通常是某条 P1/P3/P4 违反一路走到产线的症状）；它目前**不**按规则逐条扣分，也没有检测器产出重叠那一行——审读者的发现就是执行方式。
