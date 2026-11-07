---
paths:
  - "Figures/**/*.R"
  - "scripts/**/*.R"
  - "explorations/**/*.R"
---

# R 代码标准

**标准：** 代码质量应达到资深首席数据工程师与博士研究者的要求

> **范围：** 这些标准适用于**分析脚本**，包括数据处理、模拟和图形生成。此类脚本应在顶层调用一次 `set.seed()`，把 `library()` 放在顶部，并使用相对输出路径。R **包源码**（`R/`、`tests/`、`DESCRIPTION`、`NAMESPACE`、`man/`）适用另一套规则，见 [`r-package-conventions.md`](r-package-conventions.md)：用 roxygen 生成 `NAMESPACE`，不在 `R/` 中使用 `library()`，并遵守 CRAN 政策。§8 的数值纪律同时适用于两类代码。

---

## 1. 可复现性

- `set.seed()` 在顶部只调用一次（YYYYMMDD 格式）
- 所有包在顶部通过 `library()` 加载（不用 `require()`）
- 所有路径相对于仓库根目录
- 输出目录用 `dir.create(..., recursive = TRUE)`

## 2. 函数设计

- 使用 `snake_case` 命名，采用动词—名词结构
- 使用 Roxygen 风格文档
- 为参数设置默认值，不使用魔法数字
- 返回具名结果（列表或 tibble）

## 3. 领域正确性

<!-- 按你自己领域的已知陷阱定制 -->
- 核验估计量的实现与幻灯片里的公式一致
- 检查已知的包 bug（记录在下面的「常见陷阱」里）

## 4. 视觉识别

```r
# --- Your institutional palette ---
primary_blue  <- "#012169"
primary_gold  <- "#b9975b"
accent_gray   <- "#525252"
positive_green <- "#15803d"
negative_red  <- "#b91c1c"
```

### 自定义主题
```r
theme_custom <- function(base_size = 14) {
  theme_minimal(base_size = base_size) +
    theme(
      plot.title = element_text(face = "bold", color = primary_blue),
      legend.position = "bottom"
    )
}
```

### Beamer 的图形尺寸
```r
ggsave(filepath, width = 12, height = 5, bg = "transparent")
```

## 5. RDS 数据模式

**重新计算时保存 RDS；渲染幻灯片时加载预先算好的数据。**

```r
saveRDS(result, file.path(out_dir, "descriptive_name.rds"))
```

## 6. 常见陷阱

<!-- 把你所在领域特定的陷阱加在这里 -->
| 陷阱 | 影响 | 预防 |
|---------|--------|------------|
| 缺 `bg = "transparent"` | 幻灯片上出现白框 | 在 ggsave() 里总是写上 |
| 硬编码路径 | 换一台机器就跑不了 | 用相对路径 |

## 7. 行长与数学例外

**标准：** 每行不超过 100 个字符。

**数学公式可以超过 100 个字符，但必须同时满足以下三个条件：**

1. 断行会损害数学表达的可读性，例如影响函数、矩阵运算、有限差分近似或与论文方程一致的公式实现
2. 行内注释说明了这项数学运算：
   ```r
   # Sieve projection: inner product of residuals onto basis functions P_k
   alpha_k <- sum(r_i * basis[, k]) / sum(basis[, k]^2)
   ```
3. 该行位于数值计算密集的段落中，例如模拟循环、估计例程或推断计算

**对质量门禁的影响：**
- 非数学代码中的长行：审读者将其判为 Style 违规，扣 1 分；见 [`quality-gates.md`](quality-gates.md) 的 R Scripts 表。该表由 `scripts/quality_score.py` 生成，脚本本身不测量行长
- 数值计算密集且有注释说明的数学长行：不扣分

## 8. 数值纪律

完整清单见 [`r-reviewer.md`](../agents/r-reviewer.md) 第 11 类「数值纪律」。主要规则如下：

- **不要比较浮点数是否相等。** 绝不要对双精度数使用 `==`，应使用 `all.equal()` 或 `abs(a - b) < tol`。
- **把传给分位数函数的概率截断到开区间。** 把精确的 0 或 1 传给 `qnorm()` 等连续分布分位数函数会得到 `±Inf`。全项目统一使用以下 epsilon：

  ```r
  eps <- 1e-12
  p <- pmin(1 - eps, pmax(eps, p))   # now safe for qnorm(p)
  ```

- **计数使用整数字面量。** 写 `nrow <- 1000L`，不写 `1000`；写 `for (i in 1L:nL)`，避免类型被静默提升。
- **循环前预分配向量。** 使用 `numeric(n)` 或 `vector("list", n)`，绝不要用 `c()` 逐步扩展向量。
- **为自助法设置确定性种子。** 在自助法开始前设置种子；自助法嵌套时，对第 `b` 次重复分别将种子设为 `seed_base + b`。
- **显式写出 `na.rm = TRUE/FALSE`。** 数据可能含 NA 时，绝不要依赖 `mean()`、`sd()`、`sum()` 的默认值。
- **不要使用 `T` / `F`。** 它们是变量，不是常量，应写 `TRUE` / `FALSE`。

## 9. 代码质量清单

```
[ ] Packages at top via library()
[ ] set.seed() once at top (YYYYMMDD)
[ ] All paths relative
[ ] Functions documented (Roxygen)
[ ] Figures: transparent bg, explicit dimensions
[ ] RDS: every computed object saved
[ ] Comments explain WHY not WHAT
[ ] Numerical discipline: no float ==, Quantile-probability clamping with eps, pre-allocated vectors
```
