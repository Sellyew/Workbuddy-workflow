---
paths:
  - "Slides/**/*.tex"
  - "Figures/**/*.tex"
---

# TikZ 视觉质量标准

**每张 TikZ 图都必须先完成视觉打磨，才能算完成。**

## 标签定位

- 标签绝不能与曲线、线条、圆点、花括号或其他标签重叠。
- 两个标签的竖直位置接近时，将它们错开。
- 分组标签放在最后一个数据点右侧。
- 坐标轴标签放在箭头尖端。
- 注释标签紧贴花括号/箭头，并放在数据区域之外。
- 字号保持一致。

## 视觉语义

- **实心圆点/实线**表示观测到的结果、已实现的路径。
- **空心圆/虚线**表示反事实结果、未实现的路径。
- 颜色含义保持一致，分别表示正向、负向和中性。
- 在 Beamer 主题中定义颜色，以便复用。

### 线宽
- 坐标轴：`thick`
- 数据线：`thick`
- 注释箭头：`thick`（不是 `very thick`）
- 网格/参考线：`dashed, gray!40`

## 间距与比例

- 标准缩放：整幅图使用 `[scale=1.1, every node/.style={scale=1.1}]`，让节点始终随坐标一起缩放。裸写 `[scale=X]` 只缩小坐标，不缩小文字，因此被 [`tikz-prevention.md` P3](tikz-prevention.md) 禁止。
- 圆点半径：数据点使用 `4pt`。
- 任何标签与最近的图形元素之间，至少留出 0.2 个单位。
- 坐标轴必须延伸超出所有数据点。

## 清单

```
[ ] No label-label overlaps
[ ] No label-curve overlaps
[ ] Consistent dot style (solid=observed, hollow=counterfactual)
[ ] Consistent line style (solid=observed, dashed=counterfactual)
[ ] Color semantics correct
[ ] Arrow annotations point FROM label TO feature
[ ] Axes extend beyond all data points
[ ] Labels legible at presentation size
```

## 单一真源

**Beamer `.tex` 文件是所有 TikZ 图的权威来源。**
先编辑 Beamer 文件中的 TikZ，再逐字复制到 `extract_tikz.tex`。
