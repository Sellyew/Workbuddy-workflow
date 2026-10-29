# TikZ 片段画廊

常见学术图示的复制粘贴起点。每个片段：

- 通过 `\documentclass{standalone}` 独立编译——用 `xelatex snippet.tex` 快速验证。
- 满足 [`tikz-prevention.md`](../../.codebuddy/rules/tikz-prevention.md)：显式的节点尺寸（P1）、坐标映射注释（P2）、不用 `scale=`（P3）、每条边标签都带方向关键词（P4）。
- 把调色板内联写在文件里，所以每个片段都能独立编译；采用某个片段时，把颜色改成你的 [`Preambles/header.tex`](../../Preambles/header.tex) 里的名字。

## 清单

| 片段 | 用途 |
| --- | --- |
| [`dag-basic.tex`](dag-basic.tex) | 三节点因果 DAG：X → Y，带混杂因素 U。 |
| [`dag-mediation.tex`](dag-mediation.tex) | X → M → Y，带直接路径。 |
| [`did-two-period.tex`](did-two-period.tex) | 两期 DiD，含处理组/对照组路径与反事实。 |
| [`event-study.tex`](event-study.tex) | 事件时间系数，带 95% CI 与 t = 0 处的参照线。 |
| [`timeline.tex`](timeline.tex) | 带注释事件的横向时间轴。 |
| [`regression-scatter.tex`](regression-scatter.tex) | 散点图，带 OLS 拟合线与置信带。 |
| [`flowchart-3step.tex`](flowchart-3step.tex) | 纵向流程图，带一个判断菱形。 |
| [`supply-demand.tex`](supply-demand.tex) | 供给与需求，需求曲线位移。 |

## 用法

**通过 `/new-diagram` 技能：**

```text
/new-diagram dag-basic Figures/Lecture02/identification.tex
```

**手工：**

```bash
cp templates/tikz-snippets/dag-basic.tex Figures/Lecture02/identification.tex
# edit node labels, coordinates; keep the coordinate map up to date
xelatex -interaction=nonstopmode Figures/Lecture02/identification.tex  # standalone compile
```

嵌入 Beamer 时，把 `\begin{tikzpicture} ... \end{tikzpicture}` 的内容复制进一个 `frame`。`standalone` 外壳只是为了让你在编辑时能把片段单独编译。

## 改一个片段

1. **让坐标映射注释保持同步。** 如果你重命名了某个节点或挪了坐标，立刻更新注释块。过期的注释块比没有注释块更糟。
2. **节点尺寸要写死写明。** `minimum width`、`minimum height`、`text width` 都是承重的——删掉它们就是违反了预防规则 P1。
3. **不要加 `scale=X`。** 如果图对它那个位置来说太大，就按目标尺寸重新设计。缩放会破坏每一处标签位置计算（预防规则 P3）。
4. **拿不准时，跑一遍六遍检查。** 公式见 [`tikz-measurement.md`](../../.codebuddy/rules/tikz-measurement.md)。`/extract-tikz` 与 `/new-diagram` 技能会替你跑这些检查。

## 贡献

要加一个新片段？标准是：

- 跨领域通用。新的 DAG 片段是领域中立的；只在某一个子领域里讲得通的片段，应该待在那个项目的 fork 里，而不是这里。
- 能用 `xelatex` 独立编译（片段以 `\documentclass[border=4pt]{standalone}` 交付）。
- 在构造上就通过 [`tikz-prevention.md`](../../.codebuddy/rules/tikz-prevention.md) 里的 P3 与 P4 grep 预检。
- 有一条坐标映射注释，列出每个具名坐标，外加一句一行意图说明。
- 复制进 `frame` 后，能在 Beamer 的默认 frame 尺寸下干净渲染（4:3 为 12.8 × 9.6 cm，宽屏为 16 × 9 cm）。

按标准工作流开 PR（见 `.github/CONTRIBUTING.md`）。
