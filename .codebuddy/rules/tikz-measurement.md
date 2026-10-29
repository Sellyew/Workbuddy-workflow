---
paths:
  - "Slides/**/*.tex"
  - "Figures/**/*.tex"
  - "Preambles/**/*.tex"
  - "scripts/**/*.py"
  - "scripts/**/*.R"
---

# TikZ 与图形度量规则

**每个标签位置都要算。绝不靠肉眼估一条弯曲箭头。** 适用于 TikZ 图、matplotlib 图，以及带曲线注释的 ggplot 图。

> 改编自 Scott Cunningham 的 `tikz_rules.md`，载于 [MixtapeTools](https://github.com/scunning1975/MixtapeTools)。已注明出处。

LaTeX 与 Python 的编译器会把重叠的标签、穿过箭头的曲线渲染出来，却不给任何警告。审读者（`tikz-reviewer`）和任何看图的人能靠眼睛抓住它们，但事后修很贵。提前算位置很便宜。

撰写、提取（`/extract-tikz`）或审读（`tikz-reviewer`）时，把本文件当作参照。审读者报告碰撞时必须引用具体的公式或表格行。

---

## 六遍协议

对每张图按顺序跑这些检查。不要停在第一遍——后面的遍能抓住前面漏掉的碰撞。

### 第 0 遍——跨幻灯片一致性

当同一张图、同一个循环、同一个视觉元素出现在不止一页幻灯片上：

1. **颜色必须一致。** 第 31 页上标着 "Inspect" 的 `slate` 节点，在第 32 页必须仍是 `slate`。
2. **布局必须一致。** 同样的节点在同一位置，同样的间距，同样的字号。
3. **只有刻意的改动才是改动。** 如果第 32 页加了一个红色高亮来标记瓶颈，那个高亮应当是唯一的差别。

```bash
# Find frames sharing the same node names
grep -n "node.*<shared-name>" Slides/LectureN.tex
```

### 第 1 遍——贝塞尔曲线

```bash
grep -n "bend" Slides/LectureN.tex
```

对每条弯曲箭头：

**第 1 步。** 确定端点与弯曲角。

**第 2 步。** 计算最大曲线深度：

$$\text{max depth} = \frac{\text{chord length}}{2} \times \tan\!\left(\frac{\text{bend angle}}{2}\right)$$

**第 3 步。** 安全距离：

$$\text{safe distance} = \text{max depth} + 0.5\,\text{cm}$$

**第 4 步。** 任何在基线 `safe_distance` 以内（沿弯曲方向）的标签，**必须**移走。

**第 5 步。** 有没有其他箭头穿过这条曲线？如果回程曲线向下弯，而一条竖向箭头从中间穿过，它们就会相交。用翻转弯曲方向（`bend right` ↔ `bend left`）或让曲线绕开来修。

#### 预算好的弯曲表

| 弯曲角 | `tan(angle/2)` | 半弦长的乘数 |
|------------|---------------|---------------------------|
| 20° | 0.176 | × 0.18 |
| 25° | 0.222 | × 0.22 |
| 30° | 0.268 | × 0.27 |
| 35° | 0.315 | × 0.32 |
| 40° | 0.364 | × 0.36 |
| 45° | 0.414 | × 0.41 |

**算例。** 箭头跨 8.4 cm，用 `bend left=35`：

- 半弦：4.2 cm
- 深度：4.2 × 0.315 = **1.32 cm**
- 安全距离：1.32 + 0.5 = **1.82 cm**
- 任何标签都必须落在 `y ≤ −1.82`（不是 −1.2，不是 −1.5）

### 第 2 遍——节点之间的标签间隙

对每个摆在两个节点之间的标签：

$$
\begin{aligned}
\text{available gap} &= \text{center-to-center} - \tfrac{1}{2}\text{width}(A) - \tfrac{1}{2}\text{width}(B) \\
\text{usable space} &= \text{available gap} - 0.6\,\text{cm} \quad \text{(0.3 cm padding each side)}
\end{aligned}
$$

按字号估算标签宽度：

| 字号 | 每字符宽度 |
|-----------|---------------------|
| `\scriptsize` | 0.10 cm |
| `\footnotesize` | 0.12 cm |
| `\small` | 0.15 cm |
| `\normalsize` | 0.18 cm |

加粗：+10%。等宽：+15%。

如果 `label width > usable space`：碰撞必然发生。把标签移到上方或下方，或者缩短它。

**算例——"via the terminal" 问题。** 两个 5 cm 的框，中心分别在 `x = 0` 与 `x = 6.5`：

- 边缘到边缘的间隙：6.5 − 2.5 − 2.5 = 1.5 cm
- 可用空间：1.5 − 0.6 = 0.9 cm
- 标签 "via the terminal"（`\small` 下 16 个字符）：16 × 0.15 = 2.4 cm
- 2.4 > 0.9 → 碰撞 → 把标签移到两个框的上方。

### 第 3 遍——箭头标签定位

每个箭头标签都必须声明一个方位关键词（由 `tikz-prevention.md` 规则 P4 强制执行）。

- 水平箭头：`above` 或 `below`。
- 竖向箭头：`left` 或 `right`。
- 斜向：哪边空间更大就用哪边。
- 弯曲：放在弯曲*外侧*的 `above`。

### 第 4 遍——边界规则（标签对已绘形状）

**标签撞上形状边缘时，编译器零警告。** 每个靠近已绘形状的标签，都必须对照该形状算出的边界核验，而不是为视觉对齐去摆放。

**最小间隙：0.4 cm**（外侧或内侧）。

#### 圆

`\draw (cx, cy) circle (r);` → 边界从 `y = cy − r` 到 `y = cy + r`。

```latex
% WRONG — label at y = 2.0 sits exactly on top edge
\draw (4, 0.5) circle (1.5cm);   % top edge: 0.5 + 1.5 = 2.0
\node at (4, 2.0) {Sample};      % COLLISION

% RIGHT — 0.4 cm clearance
\node at (4, 2.4) {Sample};      % 2.0 + 0.4 ✓
```

#### 矩形 / `FancyBboxPatch`

左下角 `(x, y)`、宽 `w`、高 `h` → 上边缘在 `y + h`。同样的 0.4 cm 规则。

**推论——不要跨不同尺寸的形状去对齐 y 坐标。** 对某个形状安全的 `y`，可能撞上另一个。按形状各算边界。

#### 对 matplotlib / Python 图

同样的规则适用。带 `va='center'` 的 `ax.text()` 会向锚点上下各延伸约字高的一半。把文字放在 `FancyBboxPatch` 或 `Circle` 对象附近时要把这一点算进去。

### 第 4b 遍——Matplotlib `arc3` 箭头

Matplotlib 的 `connectionstyle='arc3,rad=R'` 有一个精确的贝塞尔等价形式。**放标签之前，永远先算出曲线经过哪里。**

控制点：

```python
# Start (x1, y1), End (x2, y2), bend parameter R
cx = (x1 + x2) / 2 + R * (y2 - y1)
cy = (y1 + y2) / 2 - R * (x2 - x1)
```

参数 `t ∈ [0, 1]` 处的曲线位置：

```
B(t) = (1 - t)^2 * P0 + 2 * (1 - t) * t * P1 + t^2 * P2
```

可直接复制的辅助函数——任何带 `arc3` 的 Python/matplotlib 图都放进去：

```python
import numpy as np

def arc3_control_point(x1, y1, x2, y2, rad):
    """Control point for matplotlib's arc3 connectionstyle."""
    dx, dy = x2 - x1, y2 - y1
    cx = (x1 + x2) / 2 + rad * dy
    cy = (y1 + y2) / 2 - rad * dx
    return cx, cy

def find_t_for_x(target_x, x1, cx, x2, num_samples=1000):
    """Bézier parameter t where x(t) ≈ target_x."""
    ts = np.linspace(0, 1, num_samples)
    xs = (1 - ts) ** 2 * x1 + 2 * (1 - ts) * ts * cx + ts ** 2 * x2
    return ts[np.argmin(np.abs(xs - target_x))]

def bezier_y_at_t(t, y1, cy, y2):
    """Y-coordinate of quadratic Bézier at parameter t."""
    return (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
```

把 arc3 箭头的标签放在两个形状之间间隙的中点：

```python
cx, cy   = arc3_control_point(x1, y1, x2, y2, rad)
t_mid    = find_t_for_x(gap_mid_x, x1, cx, x2)
curve_y  = bezier_y_at_t(t_mid, y1, cy, y2)
ax.text(gap_mid_x, curve_y + 0.35, label,
        ha="center", va="bottom",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1))
```

**偏移方向。** 曲线向上弯 → 标签在上（`va="bottom"`）。曲线向下弯 → 标签在下（`va="top"`）。直线 → 标签在上。

### 第 4c 遍——成对文本按锚点居中

多行文字从锚点伸出的距离比单行更远。因此对称的 y 坐标会产出视觉上不对称的布局。

```python
# WRONG — symmetric coordinates, visually asymmetric
title_y = box_mid_y + 0.7   # 2-line title with va='center' → top-heavy
math_y  = box_mid_y - 0.7   # 1-line math with va='center' → too low

# RIGHT — anchor outward from center
ax.text(x, box_mid_y + 0.15, "Title\nLine 2", va="bottom", ...)  # grows UP
ax.text(x, box_mid_y - 0.15, r"$\hat{\beta}$", va="top",    ...) # grows DOWN
```

### 第 5 遍——边距（强制）

每一对不同的视觉对象——标签、箭头、框、坐标轴线、刻度线、曲线端点——之间都必须有可见的边距。最小间隙：

| 对象对 | 最小间隙 |
|---|---|
| 标签 ↔ 标签 | 0.3 cm |
| 标签 ↔ 坐标轴线 | 0.3 cm |
| 标签 ↔ 箭头 | 0.3 cm |
| 箭头起点 ↔ 框边缘 | 0.15 cm |
| 标签 ↔ 已绘形状边界 | 0.4 cm（第 4 遍） |
| 任何对象 ↔ 幻灯片边缘 | 0.5 cm |

额外检查：

- 多行节点：加了 `align=center` 吗？
- 没有节点被幻灯片边缘裁掉（0.5 cm 边距）吗？
- 如果做了缩放：节点也一起缩放了吗，不只是坐标（见 `tikz-prevention.md` P3）？
- 全套幻灯片的箭头颜色与 stealth 尺寸一致吗？

### 第 5b 遍——绘制曲线（正态曲线、任意函数）

TikZ 的 `\draw plot` 会画曲线，但从不检查它与邻近对象是否碰撞。

**规则。** 对每条绘制的曲线，在存在其他对象的每个 x 坐标处算出它的 y 值。核验 0.3 cm 间隙。

对形如 `plot ({A*\x}, {B + C*exp(-\x*\x/2)})` 的高斯曲线：

- 峰值：`x = 0` 处 `y_peak = B + C`。
- 在 TikZ x 坐标 X 处：`x_norm = X / A`，`y = B + C * exp(-x_norm^2 / 2)`。

**算例。** 曲线 `plot ({1.5*\x}, {0.3 + 2.0*exp(-\x*\x/2)})`：

- 峰值：0.3 + 2.0 = 2.3
- 在 `x = 1.5` 处（一个标准差）：0.3 + 2.0 × 0.607 = 1.51
- 在 `x = 3.0` 处（两个标准差）：0.3 + 2.0 × 0.135 = 0.57
- 在 `x = 0` 附近、`y = 3.0` 的标签高出峰值 0.7 ✓
- 底边在 `y = 3.6` 的框高出峰值 1.3 ✓

### 第 6 遍——打开 PDF，用眼睛确认

调试用的包围盒有帮助：把可疑节点临时套上红色轮廓（`draw=red, very thin`），看清到底渲染成了什么。提交前去掉。

---

## 全片重新审计

做了**任何** TikZ 修复之后，重新审计整套幻灯片里的**每一张** TikZ 图。同一个错误模式会在各页重复，因为同一套代码结构被反复复用。`grep -n "bend"` 能找出所有曲线——逐条检查只要两分钟。

---

## 常见碰撞模式

1. **标签夹在宽框之间** → 超出间隙 → 移到上方/下方。
2. **带时期标签的时间轴** → 相邻标签重叠 → 上下错开。
3. **箭头很多的流程图** → 标签堆积 → 只标注不显然的转移。
4. **节点靠近幻灯片边缘** → 文字越出边界 → 显式 `text width`，0.5 cm 边距。
5. **回程箭头穿过竖向分支** → 曲线穿过另一条箭头 → 翻转弯曲方向。
6. **标签落在弯曲箭头的路径上** → 放在基线「下方」，但仍在曲线的扫掠范围内 → 用第 1 遍的深度公式，再加 0.5 cm 安全量。

---

## 与工作流的集成

- **`/extract-tikz` 与 `/new-diagram`** — 两者都在编译前跑一次预防性预检（`/extract-tikz` 第 1 步、`/new-diagram` 第 4 步），对照 [`tikz-prevention.md`](tikz-prevention.md) 里的规则（P3 裸 `scale=`、P4 缺少方位关键词）。两者调用同一个脚本 `scripts/check-tikz-prevention.py`，所以行为不会漂移。
- **`tikz-reviewer` 代理** — 跑这里的度量各遍（第 1 遍贝塞尔、第 2 遍间隙、第 3 遍关键词、第 4 遍边界、第 4b 遍 arc3、第 4c 遍文本对、第 5 遍边距、第 5b 遍绘制曲线、第 6 遍目视）。报告碰撞时必须引用具体的那一遍和公式。
- **`quality_score.py`** — 它的评分细则字典是打分源头；[`quality-gates.md`](quality-gates.md) 与之镜像。Quarto 细则定义了 −5 的 `tikz_label_overlap` 扣分（目前还没有自动检测器产出它——审读者的发现就是执行方式）；Beamer 细则没有重叠扣分。
