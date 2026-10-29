---
paths:
  - "Slides/**/*.tex"
  - "Figures/**/*.tex"
---

# TikZ 视觉质量标准

**每张 TikZ 图在可以算完成之前，都必须先在视觉上打磨到位。**

## 标签定位

- 标签绝不能与曲线、线条、圆点、花括号或其他标签重叠
- 两个标签处在相近的竖直位置时，把它们错开
- 分组标签：放在最后一个数据点的右侧
- 坐标轴标签：放在箭头尖端
- 注释标签：紧贴花括号/箭头，置于数据区域之外
- 字号保持一致

## 视觉语义

- **实心圆点/实线** = 观测到的结果、已实现的路径
- **空心圆/虚线** = 反事实结果、未实现的路径
- 用一致的颜色承载语义（正向、负向、中性）
- 在 Beamer 主题中定义颜色以便复用

### 线宽
- 坐标轴：`thick`
- 数据线：`thick`
- 注释箭头：`thick`（不是 `very thick`）
- 网格/参考线：`dashed, gray!40`

## 间距与比例

- 标准缩放：整幅图用 `[scale=1.1, every node/.style={scale=1.1}]`——始终让节点随坐标一起缩放（裸写 `[scale=X]` 被 [`tikz-prevention.md` P3](tikz-prevention.md) 禁止，因为它只缩小坐标、不缩小文字）
- 圆点半径：数据点用 `4pt`
- 任何标签与最近的图形元素之间至少 0.2 个单位
- 坐标轴延伸超出所有数据点

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
先在 Beamer 文件里编辑 TikZ，再逐字复制到 `extract_tikz.tex`。
