---
paths:
  - "Figures/**/*.R"
  - "scripts/**/*.R"
  - "explorations/**/*.R"
---

# R 代码标准

**标准：** 资深首席数据工程师 + 博士研究者的质量

> **范围：** 这些标准适用于**分析脚本** —— 数据处理、模拟、图形生成（顶层一个 `set.seed()`、`library()` 放在顶部、相对输出路径）。R **包源码**（`R/`、`tests/`、`DESCRIPTION`、`NAMESPACE`、`man/`）见 [`r-package-conventions.md`](r-package-conventions.md)，那边规则不同（roxygen 生成的 `NAMESPACE`、`R/` 里不用 `library()`、CRAN 政策）。§8 的数值纪律两边都适用。

---

## 1. 可复现性

- `set.seed()` 在顶部只调用一次（YYYYMMDD 格式）
- 所有包在顶部通过 `library()` 加载（不用 `require()`）
- 所有路径相对于仓库根目录
- 输出目录用 `dir.create(..., recursive = TRUE)`

## 2. 函数设计

- `snake_case` 命名，动词-名词模式
- Roxygen 风格文档
- 有默认参数，不用魔法数字
- 具名返回值（列表或 tibble）

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

**重计算存成 RDS；幻灯片渲染加载预先算好的数据。**

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

**标准：** 行不超过 100 个字符。

**例外：数学公式** -- 行可以超过 100 字符，**当且仅当：**

1. 断行会损害数学的可读性（影响函数、矩阵运算、有限差分近似、与论文方程一致的公式实现）
2. 有一处行内注释说明该数学运算：
   ```r
   # Sieve projection: inner product of residuals onto basis functions P_k
   alpha_k <- sum(r_i * basis[, k]) / sum(basis[, k]^2)
   ```
3. 该行位于数值密集的段落（模拟循环、估计例程、推断计算）

**质量门禁影响：**
- 非数学代码里的长行：由审读者判定为 Style 违规（-1；见 [`quality-gates.md`](quality-gates.md) 里的 R Scripts 表，该表由 `scripts/quality_score.py` 生成，而脚本本身并不测量行长）
- 有注释说明的数学段落里的长行：不扣分

## 8. 数值纪律

完整清单见 [`r-reviewer.md`](../agents/r-reviewer.md) 第 11 类（「数值纪律」）。要点规则：

- **不用浮点相等。** 绝不要对双精度数用 `==`。用 `all.equal()` 或 `abs(a - b) < tol`。
- **CDF 截断**到开区间。把精确的 0 或 1 传给 `qnorm()` / `pbinom()` 等会产出 `±Inf`。全项目共用的 epsilon：

  ```r
  eps <- 1e-12
  p <- pmin(1 - eps, pmax(eps, p))   # now safe for qnorm(p)
  ```

- **计数用整数字面量。** `nrow <- 1000L`（不是 `1000`）、`for (i in 1L:nL)` —— 避免静默提升。
- **循环前预分配向量**（`numeric(n)`、`vector("list", n)`），绝不靠 `c()` 增长。
- **确定性的自助法种子。** 在自助法之前设种子；如果自助法是嵌套的，按重复设种子为 `seed_base + b`。
- **显式写 `na.rm = TRUE/FALSE`。** 对可能含 NA 的数据，绝不要依赖 `mean()`、`sd()`、`sum()` 的默认值。
- **不用 `T` / `F`。** 它们是变量，不是常量 —— 写 `TRUE` / `FALSE`。

## 9. 代码质量清单

```
[ ] Packages at top via library()
[ ] set.seed() once at top (YYYYMMDD)
[ ] All paths relative
[ ] Functions documented (Roxygen)
[ ] Figures: transparent bg, explicit dimensions
[ ] RDS: every computed object saved
[ ] Comments explain WHY not WHAT
[ ] Numerical discipline: no float ==, CDF clamping with eps, pre-allocated vectors
```
