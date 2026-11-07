# TikZ 片段画廊

这些片段为常见学术图示提供可直接复制和修改的起点。每个片段都满足以下条件：

- 使用 `\documentclass{standalone}` 独立编译；可运行 `xelatex snippet.tex` 快速验证。
- 满足 [`tikz-prevention.md`](../../.codebuddy/rules/tikz-prevention.md)：显式设置节点尺寸（P1），添加坐标映射注释（P2），不用裸 `scale=X`（P3），每条边的标签都带方向关键词（P4）。
- 调色板直接写在片段文件中，因此每个片段都能独立编译。采用片段后，把颜色名改为你的 [`Preambles/header.tex`](../../Preambles/header.tex) 中定义的名称。

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

嵌入 Beamer 时，把 `\begin{tikzpicture} ... \end{tikzpicture}` 的内容复制到一个 `frame` 中。`standalone` 外壳只用于在编辑时单独编译片段。

## 改一个片段

1. **让坐标映射注释保持同步。** 重命名节点或移动坐标后，立即更新注释块。过期的注释块比没有注释块更容易误导后续修改。
2. **明确写出节点尺寸。** P1 仅约束带框的承载文字节点：固定尺寸使用 `minimum width` + `minimum height`；高度随文字增长使用 `text width` + `align`；任何多行内容必须使用 `text width`，不要求三个参数同时存在。
3. **不要加裸 `scale=X`。** P3 禁止裸 `scale=X`，不是一切缩放；允许 `scale=X, every node/.style={scale=X}` 与 `scale=X, transform shape`。如果图对目标位置来说太大，就按目标尺寸重新设计。不对称缩放会破坏标签的位置计算。
4. **拿不准时，跑一遍六遍检查。** 公式见 [`tikz-measurement.md`](../../.codebuddy/rules/tikz-measurement.md)。`/extract-tikz` 与 `/new-diagram` 技能会替你运行这些检查。

## 贡献

新增片段必须满足以下标准：

- 跨领域通用。新的 DAG 片段不限定研究领域；只适用于某个子领域的片段，应留在该项目的 fork 中，不要加入这里。
- 能用 `xelatex` 独立编译，并以 `\documentclass[border=4pt]{standalone}` 交付。
- 能通过 [`tikz-prevention.md`](../../.codebuddy/rules/tikz-prevention.md) 中 P3/P4 的预防性预检（`python scripts/check-tikz-prevention.py`）。
- 带有一条坐标映射注释，列出每个具名坐标，另用一行说明片段用途。
- 复制到 `frame` 后，能在 Beamer 的默认 frame 尺寸下正常渲染：4:3 为 12.8 × 9.6 cm，宽屏为 16 × 9 cm。

按标准工作流开 PR（见 `.github/CONTRIBUTING.md`）。
