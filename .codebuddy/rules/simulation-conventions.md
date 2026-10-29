---
paths:
  - "**/*simulation*.R"
  - "**/*_sim.R"
  - "**/*_mc.R"
  - "scripts/**/simulations/**"
  - "explorations/**/*.R"
---

# 蒙特卡洛模拟标准

**标准：** 一项模拟研究就是一次实验。它必须可复现，它的估计目标必须无歧义，而且每个头条数字都必须自带它的蒙特卡洛不确定性。

> **范围：** 本规则只管*模拟特有*的纪律。通用 R 标准（文件头、`library()` 置于顶部、相对路径、图形主题、不用浮点 `==`、CDF 截断、预分配）在 [`r-code-conventions.md`](r-code-conventions.md) 与 [`r-reviewer`](../agents/r-reviewer.md) 第 9 类（错误处理）+ 第 11 类（数值纪律）清单里。不要在这里重述——两条都遵守。

---

## 1. 模拟契约

每个蒙特卡洛脚本都必须把五件事说清并可检查：

1. **DGP**——一个单独的参数化函数 `generate_data(params)`，返回一个数据集。数据生成不得散落在运行循环各处。
2. **真值**——目标参数的真实取值，由 `params` 计算得出（不是从任何估计值反推），与结果一同保存。
3. **估计目标**——每个估计量瞄准的是哪个量（例如 ATT、ATE、某个具体的事件研究系数）。一个瞄准的估计目标与`真值`*不同*的估计量是 bug，不是「发现」。
4. **重复预算**——`R`（重复次数）以及由此在头条指标上得到的蒙特卡洛标准误。
5. **假定体制**——该估计量维持哪些条件、本次运行的 DGP 是否满足每一条、以及这一点是如何核验的。任何其输出要支撑断言、要把某个默认为正式发布、或要离开这台机器的运行都必须给出；一次性的探索运行不必（§2）。

## 2. 假定体制

每个估计量都维持着若干假定。一个 DGP 要么满足它们，要么不满足——而一个从不说清是哪一种的模拟，是在报告两个完全不同的实验之一，却不告诉你是哪一个。**本文件里没有别的东西能抓住这一点。** 一个 DGP 违反了估计量所维持假定的运行，可以通过这里的其他每一项检查——报告了 MCSE、覆盖率对照真值打分、估计目标对齐——却仍然只是在提供关于那次违反的证据，而不是关于该估计量的证据。

### 哪些运行欠一个体制块

**那些其输出要支撑断言、要把某个默认为正式发布、或要离开这台机器的运行。** 一个即将进入论文、幻灯片、README 或审稿人手里的数字；把某个东西默认开启发布背后的证据；任何交给共同作者或打包用于复现的东西。这些欠下完整的一块。

**一次性的探索运行不欠**——检查估计量到底能不能跑、扫一张网格来确定往哪里看、对一个行为异常的 DGP 做二分。这条豁免是有意大声说出来的。一位外部审稿人的反对意见精准：若同样强加于用完即弃的运行，这就变成仪式，而仪式会被敷衍地遵守、然后被整体绕过——连那些真正需要它的运行也一起绕过。一条没人到处都负担得起的规则，在哪儿都不会被遵守。

**界线在输出，不在意图。** 一次探索运行，其数字即将被引用，就已经越过了这条线，并且必须在数字被引用**之前**补上那块——给一次你已记不清 DGP 的运行事后补装一个体制，产出的是你以为你做了什么，而不是对你做了什么做的核验。

### 体制块

每个在范围内的脚本都在头部声明四件事：

| 字段 | 陈述什么 |
|---|---|
| **估计目标** | 目标量，以及它的真实取值如何由 `params` 计算（§1） |
| **维持的假定** | 所研究的估计量或流程所要求的**完整**清单——每一条，不是有趣的那几条 |
| **体制** | `IN-ASSUMPTION`，或本次运行所放松的**那一条**假定及其严重程度 |
| **已核验** | 逐条假定给出确立它的、DGP 中可检查的性质 |

**是一张映射表，不是一张清单。** 给这次运行发执照的，是估计量条件与 DGP 之间的*对应*，从来不是两张并排放着的清单。所以逐条写：定理或所记载流程要求的每个条件各占一行，正对着它写 `generate_data()` 中确立它的那个性质——而运行在某个条件上偏离时，这次偏离要在 `Regime` 行里被点名为**有意的违反**，不能悄悄从 `Verified` 里消失。一个对面什么都没有的条件，记录的是一个愿望；一个对面没有条件的 DGP 特征，记录的是一份变更日志。

**「DGP 设定正确」是断言，不是核验。** 当你点得出 `generate_data()` 中让某条假定成立的那个性质时，这条假定才算被核验。两种形式算数：*由构造保证*（DGP 从有限方差的分布抽误差，因此矩条件成立）与*由检查保证*（一次大样本抽取的断言、一个条件数、一次对生成器的结构式阅读）。「看起来是对的」两者都不是。

**而且一条假定一行。** 两条条件合并到一个标签下——「二阶矩*有限且*非奇异」——产出的块只核验了其中一条，却看起来完整；拆开，各自得到自己的检查。

**一项检查只有在能变红时才算检查。** 写出阈值或那个比较，而不是写出那个性质：`stopifnot(rcond(J) > 1e-8)` 会在雅可比奇异时失败，`is.finite(kappa(J))` 不会——实测，一个恰好奇异的 2×2 矩阵的 `kappa()` 返回 `1.478e+17`，是有限的，于是这个有限性写法恰好在它本要抓的那个缺陷上通过。一个谓词对它所针对的缺陷为真的核验，比没有核验更糟，因为头部现在宣称这条假定被检查过了（[`research-agent-laws.md`](../references/research-agent-laws.md) 法则 5）。如果你说不出这项检查对比的那个数字，你写下的是一句断言。

```r
# --- Assumption regime -------------------------------------------------
# Estimand   theta0, the unique solution of E[psi(W; theta)] = 0 under the
#            DGP; computed in closed form from params (compute_truth()).
# Maintained assumptions of the estimator under study:
#   A1  i.i.d. sampling of W_i
#   A2  correct specification: the DGP's conditional mean IS the one psi assumes
#   A3  finite, positive-definite variance matrix Omega = E[psi psi'] at theta0
#   A4  nonsingular Jacobian G = E[d psi / d theta'] evaluated at theta0
#   A5  theta0 interior to the parameter space; psi differentiable there
# Regime     IN-ASSUMPTION -- A1-A5 all hold.
# Verified   A1  rows are drawn i.i.d. within a replication -- no group-level
#                or latent draw in generate_data() enters more than one row
#            A2  by construction -- the outcome equation and psi share one
#                functional form and one coefficient vector; asserted on a
#                1e6-row draw that mean(psi(W, truth)) is within 4 MCSE of 0
#            A3  Omega estimated on a 1e6-row draw (Gaussian errors,
#                sigma = params$sigma, so the fourth moments exist);
#                stopifnot(all(is.finite(Omega)),
#                          min(eigen(Omega, symmetric = TRUE,
#                                    only.values = TRUE)$values) > 1e-8)
#            A4  G formed analytically at theta0;
#                stopifnot(rcond(G) > 1e-8)   -- reciprocal condition against a
#                stated floor, NOT is.finite(kappa(G)): kappa() of an exactly
#                singular matrix is ~1.5e17, finite, so that form cannot fail
#            A5  params$theta lies strictly inside the search bounds --
#                stopifnot() at setup
# -----------------------------------------------------------------------
```

一次假定外的运行只改那个块里的两行：

```r
# Regime     OUT-OF-ASSUMPTION -- relaxes A2 only, at severity
#            delta in {0, 0.1, 0.25, 0.5}; A1, A3-A5 hold exactly as above.
# Target     the pseudo-estimand theta*(delta) -- the solution of
#            E[psi(W; theta)] = 0 under the perturbed DGP, obtained by
#            root-finding on a 1e7-row draw (no closed form).
```

### 防火墙

**硬规则：只有假定内的运行才可以支撑假定内的断言。** 假定内断言是指任何关于估计量或流程在它承诺表现的地方表现如何的断言——一致性、解析标准误的有效性、名义覆盖率，或把某个默认为正式发布的决定。每一条都**只能**引用体制行写着 `IN-ASSUMPTION` 的运行。

假定外的运行永远不能支撑假定内的断言，两个方向都不行：

- 它不能确认一条。在假定被违反时接近名义的覆盖率，是关于那次违反的事实——通常是关于它有多轻——不是关于该估计量的推断。
- 它不能反驳一条。假定被违反时的偏误，是 DGP 在做它生来就要做的事。

所以每张表都要带上它的体制——写在标题里，并且在严重程度网格混合它们的地方**逐行**标注（剂量–反应里的零剂量臂*就是*一行假定内行，必须如此标注）。也把它带进保存的摘要对象里，这样读者——或六个月后的审稿人——不必重跑任何东西就能判断哪些行给哪些断言发执照。这是把 [`credible-claims`](../skills/credible-claims/SKILL.md) 的纪律应用于证据所来自的那个*体制*：断言永远不能强于它背后的那次运行。

### 设计一次假定外的研究

1. **只放松一条假定。** 一次放松两条会让失败无从归因——你只知道有东西坏了，永远不知道是哪个，而事后再多的分析也修不回来。
2. **其余一切固定。** 同样的抽样方案、同样的样本量、同样的估计量网格、同样的种子。扰动是两次运行之间唯一的差别。
3. **瞄准伪估计目标，并说明每个指标用的是哪个目标。** 在假定被违反时，估计量不再瞄准`真值`；它收敛到在扰动后的 DGP 下解出其自身准则的那个量。从扰动后的参数算出那个量（没有闭式解就数值求解），并对照它打分——两个目标不同时就把两个都报告，因为它们回答不同的问题：相对原估计目标的偏离回答的是*假定它成立的人错得有多厉害*，伪估计目标的覆盖率回答的是*该估计量自己的推断对它现在瞄准的东西还管不管用*。一张不说清自己用了哪个目标的表，读不了。
4. **宁可做剂量–反应，不要只做一个极端剂量。** 扫一张严重程度网格；单一严重违反只说明估计量可以被弄坏，而那从来不成问题。要包含零剂量，它会重现假定内的运行——**这是对扰动机制的正对照。** 如果零剂量臂与假定内的数字不一致，说明扰动漏进了别的东西，其他每个剂量都无法解释。

## 3. 可复现性与种子

- `set.seed(YYYYMMDD)` 只在顶部设**一次**——绝不在重复循环里或 DGP 里。
- **并行运行用单个种子不可复现。** 当重复并行跑（`future`/`furrr`、`parallel`、`foreach`）时，使用独立流：

  ```r
  RNGkind("L'Ecuyer-CMRG")
  set.seed(20260531)
  # furrr: carry streams explicitly
  results <- furrr::future_map(seq_len(R), run_one_rep,
                               .options = furrr::furrr_options(seed = TRUE))
  ```

- 把种子与 `R` 记进保存的输出对象，这样一个结果可以追溯到产生它的那次确切运行。

## 4. 重复次数与蒙特卡洛标准误（MCSE）

**没有 MCSE 的模拟结果是意见。** 永远报告头条指标的蒙特卡洛不确定性，并把 `R` 选到它相对于你所声称的效应足够小。

| 指标 | 蒙特卡洛标准误 | 经验法则 |
|---|---|---|
| 偏误 / 均值估计 | `sd(estimates) / sqrt(R)` | 写在每个偏误数字旁边 |
| 覆盖率 `p` | `sqrt(p * (1 - p) / R)` | 覆盖率接近 0.95 时要 MCSE ≈ 0.005（±0.5 pp），需 `R ≈ 1900`；要 ±1 pp，需 `R ≈ 475` |
| 拒绝率 / 功效 | `sqrt(p * (1 - p) / R)` | 同覆盖率 |
| RMSE | 对重复做 bootstrap 或 delta 法 | 至少报告 `R`，让读者能估量它 |

如果两个估计量之差不到几个 MCSE，就说出来——不要把更小的那个数字当作「更好」。

## 5. 指标：算对它们

对照**真值**定义，永不对照另一个估计：

- **偏误** = `mean(est) - truth`。
- **经验标准误** = 各次重复的 `sd(est)`（真实的抽样波动）。
- **RMSE** = `sqrt(mean((est - truth)^2))`。
- **覆盖率** = 置信区间**包含 `truth`** 的重复所占比例——即 `mean(ci_lo <= truth & truth <= ci_hi)`。模拟里最常见的单个 bug，就是拿置信区间去对点估计，或去对一个标错的「真」值。
- **水平 / 功效** = 检验在原假设 DGP 下的拒绝率（水平）与在备择 DGP 下的拒绝率（功效）。水平必须在原假设字面成立的那个 DGP 下评估。

## 6. 存储：存原始，不只是汇总

- 用 `saveRDS()` 保存**逐次重复的原始结果**（一个 tibble：每次重复 × 估计量一行，含 `est`、`se`、`ci_lo`、`ci_hi`、`converged`），而不只是汇总表。重新聚合、新增指标、以及 `sim-reviewer` 都需要这个原始对象。
- 汇总表存成 `.rds` **以及**一份人类可读的 `.csv`/`.tex`。输出进 `output/`（仓库的规范路径）。
- 绝不要让头条数字只存在于控制台输出里——它无法被审计，也无法重新渲染到幻灯片上。

## 7. 性能与稳健性

- **预分配**；绝不在循环内用 `c()`/`append()` 增长结果向量（见 `r-code-conventions.md` §8）。
- 显式统计并报告**失败/未收敛的重复**（`converged` 标记）——悄悄丢弃它们会让每个指标都有偏。
- 不要每次重复都 `print()`/`cat()`。用一条进度条（`progressr`），或者干脆不用。
- 在计算汇总之前，对估计中的 `NA`/`NaN`/`Inf` 加以防护；决定并记录它们算作失败还是被排除。

## 8. 常见陷阱

| 陷阱 | 影响 | 预防 |
|---|---|---|
| DGP 悄悄违反了某条维持的假定 | 其他每项检查都通过；结果讲的是那次违反，不是估计量 | 体制块；逐条核验假定而不是断言它 |
| 假定内的断言引自假定外的运行 | 关于估计量的承诺，踩在承载不了它的证据上 | 防火墙（§2） |
| 一次放松两条假定 | 失败无从归因——你说不出是哪条弄坏的 | 每次运行只放松一条，扫严重程度网格 |
| 在循环里 `set.seed()` | 重复之间完全相同/相关；方差被低估 | 顶部设一次种子；并行用 L'Ecuyer 流 |
| 覆盖率对照估计而不是真值 | 覆盖率按构造接近名义——毫无意义 | `mean(ci_lo <= truth & truth <= ci_hi)` |
| 不报 MCSE | 在噪声之内说「估计量 A 打败 B」 | 报告偏误/覆盖率/功效上的 MCSE |
| 估计量瞄准的估计目标与`真值`不同 | 看似「偏误」，实为目标不匹配 | 声明每个估计量的估计目标；与真值对齐 |
| 原始逐次结果被丢弃 | 无法重新聚合或审计 | `saveRDS()` 原始 tibble |
| 丢弃失败重复却不记录 | 所有指标上的存活偏差 | 跟踪并报告 `converged` 计数 |

## 9. 清单

```
[ ] DGP is one parameterized generate_data() function
[ ] truth computed from params, stored with results
[ ] each estimator's estimand stated and aligned with truth
[ ] does this run's output support a claim, promote a default, or leave the machine?
    if no, the regime items below are optional (§2); everything else still applies
[ ] regime block in the header: estimand, ALL maintained conditions, regime, verification
[ ] one condition per assumption line -- no two merged under one label
[ ] each condition mapped to the DGP property opposite it; deliberate violations named
    in the regime line, not omitted
[ ] each maintained assumption verified by a named property, not asserted, and
    every check states a threshold it can fail against (rcond(J) > 1e-8, not
    is.finite(kappa(J)))
[ ] within-assumption claims (consistency, analytic SEs, coverage, a shipped default)
    cite an IN-ASSUMPTION run and nothing else
[ ] out-of-assumption run relaxes ONE assumption, over a severity grid including the
    null dose, scored against a named target
[ ] set.seed() once at top (YYYYMMDD); L'Ecuyer streams if parallel
[ ] R chosen for adequate MCSE; MCSE reported on bias/coverage/power
[ ] coverage = CI contains truth (not the estimate)
[ ] failed/non-converged reps counted and reported
[ ] per-rep raw results saved via saveRDS() to output/
[ ] no per-replication console printing
```

## 交叉引用

- [`r-code-conventions.md`](r-code-conventions.md) — 通用 R 标准（种子格式、预分配、数值纪律）。
- [`../agents/sim-reviewer.md`](../agents/sim-reviewer.md) — 执行本规则的代理。
- [`../agents/r-reviewer.md`](../agents/r-reviewer.md) — 第 9 类（错误处理）+ 第 11 类（数值纪律）。
- [`replication-protocol.md`](replication-protocol.md) — 先复现再扩展的容差契约（当一次模拟在复现一张已发表的表时适用）。
- [`../skills/credible-claims/SKILL.md`](../skills/credible-claims/SKILL.md) — 断言永远不能强于它背后的那次运行；防火墙（§2）就是把这条纪律应用于假定体制。

## 并行必须可证明地与运行形状无关

**按任务播种，不按 worker 播种。** 预生成**每次重复一条 RNG 流**（L'Ecuyer `"L'Ecuyer-CMRG"`），这样第 *k* 次重复无论在哪个核上跑、无论有几个核，抽到的都是同一批数字。

按 worker 播种——`mc.set.seed`、`clusterSetRNGStream`，或「在 worker 内部设种子」——**会把你的结果悄悄绑到执行形状上**。同一个脚本在笔记本和集群上于是跑出不同的数字，而且没有任何东西警告你。这是一个复现者会发现、而你不会发现的复现性故障。

```r
# Correct: one stream per replication, independent of core count
RNGkind("L'Ecuyer-CMRG")
set.seed(20260821)
streams <- vector("list", n_reps)
s <- .Random.seed
for (k in seq_len(n_reps)) { streams[[k]] <- s; s <- parallel::nextRNGStream(s) }

run_one <- function(k) { .Random.seed <<- streams[[k]]; simulate_once() }
results <- parallel::mclapply(seq_len(n_reps), run_one, mc.cores = n_cores)
```

**在相信一整轮批量运行之前先证明它。** 在两种核数下跑前 N 次重复，断言逐位一致：

```r
a <- run_campaign(n_reps = 20, n_cores = 2)
b <- run_campaign(n_reps = 20, n_cores = 4)
stopifnot(identical(a, b))   # fails loudly if results depend on run shape
```

这是**给你自己那套装置的正对照**——双核/四核检查很便宜，几秒钟跑完，而且是唯一能把「播种正确」与「播种方式碰巧在这台机器上看着没问题」区分开的东西。把它记进资格台账。

Stata：在循环内按重复从一张预生成的列表里设 `seed`，不要在 `parallel` 块之前设一次。Python：用 `numpy.random.SeedSequence(...).spawn(n_reps)`——每次重复一个子序列，绝不每个 worker 一个。
