---
paths:
  - "**/*simulation*.R"
  - "**/*_sim.R"
  - "**/*_mc.R"
  - "scripts/**/simulations/**"
  - "explorations/**/*.R"
---

# 蒙特卡洛模拟标准

**标准：** 模拟研究就是实验。它必须可以复现，估计目标必须没有歧义，每个重点报告的数字都必须同时报告相应的蒙特卡洛不确定性。

> **范围：** 本规则只规定*模拟特有*的要求。通用 R 标准见 [`r-code-conventions.md`](r-code-conventions.md) 与 [`r-reviewer`](../agents/r-reviewer.md) 第 9 类（错误处理）+ 第 11 类（数值纪律）清单，包括文件头、`library()` 置于顶部、相对路径、图形主题、不用浮点 `==`、分位数函数的概率截断和预分配。这里不再重述，但两处规则都必须遵守。

---

## 1. 模拟契约

每个蒙特卡洛脚本都必须明确说明五件事，并让这些说明可以接受检查：

1. **DGP**——用一个单独的参数化函数 `generate_data(params)` 返回数据集，不能把数据生成代码散落在运行循环中。
2. **真值**——目标参数的真实取值必须由 `params` 计算，不能从任何估计值反推，并要与结果一同保存。
3. **估计目标**——说明每个估计量针对哪个量，例如 ATT、ATE 或某个具体的事件研究系数。估计量针对的估计目标与 `真值`*不同*，就是 bug，不能当作「发现」。
4. **重复预算**——说明 `R`（重复次数），以及相应的主要指标蒙特卡洛标准误。
5. **假定体制**——说明估计量依赖哪些条件、本次运行的 DGP 是否满足每一项条件，以及如何核验。只要运行输出会用于支撑断言、把某项默认设置推向正式发布或离开本机，就必须给出这些内容；一次性探索运行除外（§2）。

## 2. 假定体制

每个估计量都依赖若干假定，DGP 要么满足这些假定，要么不满足。如果模拟不说明属于哪种情况，就等于报告了两个完全不同的实验之一，却不告诉读者是哪一个。**本文件中的其他检查都无法替代这项说明。** 即使 DGP 违反了估计量依赖的假定，运行仍可能通过其他所有检查，包括报告 MCSE、根据真值评估覆盖率、对齐估计目标，但结果只能说明那次假定违反，不能说明估计量本身的表现。

### 哪些运行欠一个体制块

**只要运行输出会用于支撑断言、把某项默认设置推向正式发布或离开本机，就需要体制块。** 这包括即将写入论文、幻灯片、README 或交给审稿人的数字，支持默认开启某项发布设置的证据，以及任何交给共同作者或打包用于复现的内容。这些运行都必须给出完整的体制块。

**一次性探索运行不需要体制块**，例如检查估计量能否运行、扫描网格以确定后续研究方向、对行为异常的 DGP 做二分。这里明确保留这项豁免，因为外部审稿人提出的反对意见很准确：如果把同样的要求强加给用完即弃的运行，它就会沦为形式。人们会敷衍遵守，进而整体绕过，连真正需要它的运行也不例外。如果一项规则的要求高到所有运行都难以承担，最终就会被普遍绕过。

**界线取决于输出用途，不取决于最初意图。** 探索运行的数字一旦要被引用，就越过了这条线，必须在引用数字**之前**补上体制块。如果事后再为已经记不清 DGP 的运行补写，得到的只是你以为自己做过的核验，而不是对实际运行的核验。

### 体制块

每个在范围内的脚本都在头部声明四件事：

| 字段 | 陈述什么 |
|---|---|
| **估计目标** | 目标量，以及它的真实取值如何由 `params` 计算（§1） |
| **维持的假定** | 所研究的估计量或流程所要求的**完整**清单——每一条，不是有趣的那几条 |
| **体制** | `IN-ASSUMPTION`，或本次运行所放松的**那一条**假定及其严重程度 |
| **已核验** | 逐条假定给出确立它的、DGP 中可检查的性质 |

**这里需要一张映射表，而不是一张清单。** 要判断运行能否支撑结论，必须看估计量条件与 DGP 之间的*对应关系*，不能把两张清单并排摆着就算完成。定理或所记载流程要求的每个条件各占一行，在对应位置写出 `generate_data()` 中确立该条件的性质。如果运行有意偏离某个条件，必须在 `Regime` 行把它点名为**有意的违反**，不能只是从 `Verified` 中删掉。没有对应 DGP 性质的条件只是一个愿望；没有对应条件的 DGP 特征只是一条变更记录。

**「DGP 设定正确」是断言，不是核验。** 只有明确指出 `generate_data()` 中让某项假定成立的性质，才算核验了这项假定。核验有两种有效形式：*由构造保证*，例如 DGP 从有限方差分布中抽取误差，因此矩条件成立；*由检查保证*，例如对一次大样本抽取作断言、检查条件数或对生成器做结构式阅读。「看起来是对的」不属于任何一种。

**每条假定必须单独占一行。** 如果把两条条件合并到一个标签下，例如「二阶矩*有限且*非奇异」，体制块可能只核验其中一条，看起来却已经完整。必须拆开两条条件，分别检查。

**一项检查只有在可能失败时才算检查。** 要写出阈值或比较，不能只写出待检查的性质。`stopifnot(rcond(J) > 1e-8)` 会在雅可比奇异时失败，`is.finite(kappa(J))` 则不会。实测中，一个恰好奇异的 2×2 矩阵，其 `kappa()` 返回 `1.478e+17`，结果是有限的，所以这种有限性检查恰恰会在本应发现的缺陷上通过。如果谓词在目标缺陷出现时仍为真，这种核验比没有核验更糟，因为头部会宣称这项假定已经检查过，见 [`research-agent-laws.md`](../references/research-agent-laws.md) 法则 5。如果不能说出检查所比较的数字，写下的就只是一句断言。

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

**硬规则：只有假定内的运行才能支撑假定内的断言。** 假定内断言包括估计量或流程在其承诺适用的条件下表现如何的任何断言，例如一致性、解析标准误的有效性、名义覆盖率，或将某项设置设为正式发布默认项的决定。每一条这类断言都**只能**引用体制行标为 `IN-ASSUMPTION` 的运行。

假定外的运行永远不能支撑假定内的断言，无论确认还是反驳都不行：

- 它不能确认假定内断言。假定被违反时，覆盖率接近名义水平，只能说明这次违反的情况，通常只能说明违反程度有多轻，不能说明该估计量的推断表现。
- 它不能反驳假定内断言。假定被违反时出现偏误，正是 DGP 按设计产生的结果。

因此，每张表都要标明体制，写在标题里；如果严重程度网格混合了不同体制，还要**逐行**标注。剂量–反应中的零剂量臂*就是*假定内的一行，必须如此标注。体制也要写入保存的摘要对象，让读者或六个月后的审稿人不必重跑，就能判断每一行可以支撑哪些断言。这相当于把 [`credible-claims`](../skills/credible-claims/SKILL.md) 的要求用于证据所来自的*体制*：断言强度绝不能超过其背后运行能够支撑的范围。

### 设计一次假定外的研究

1. **只放松一条假定。** 一次放松两条会让失败无法归因。你只能知道出了问题，却无法确定是哪条假定导致的，事后做再多分析也无法弥补。
2. **其余一切固定。** 保持同样的抽样方案、样本量、估计量网格和种子，让扰动成为两次运行之间唯一的差别。
3. **瞄准伪估计目标，并说明每个指标用的是哪个目标。** 假定被违反时，估计量不再瞄准 `真值`，而会收敛到在扰动后的 DGP 下满足其自身准则的量。根据扰动后的参数计算这个量，没有闭式解时就数值求解，再对照它评估指标。如果两个目标不同，就同时报告，因为它们回答不同的问题：相对原估计目标的偏离回答*假定它成立的人错得有多厉害*，伪估计目标的覆盖率回答*该估计量自己的推断对它现在瞄准的东西是否仍然有效*。如果一张表不说明使用哪个目标，就无法解读。
4. **宁可做剂量–反应，不要只做一个极端剂量。** 扫描严重程度网格。单一的严重违反只能证明估计量可以被破坏，这一点从来不是疑问。网格必须包含零剂量，因为它会重现假定内的运行，**是扰动机制的正对照。** 如果零剂量臂与假定内的数字不一致，说明扰动还影响了其他因素，其他每个剂量都无法解释。

## 3. 可复现性与种子

- `set.seed(YYYYMMDD)` 只在顶部设**一次**，绝不能放在重复循环或 DGP 中。
- **并行运行使用单个种子无法复现。** 当重复并行运行时（`future`/`furrr`、`parallel`、`foreach`），使用独立流：

  ```r
  RNGkind("L'Ecuyer-CMRG")
  set.seed(20260531)
  # furrr: carry streams explicitly
  results <- furrr::future_map(seq_len(R), run_one_rep,
                               .options = furrr::furrr_options(seed = TRUE))
  ```

- 把种子与 `R` 写入保存的输出对象，使每个结果都能追溯到产生它的确切运行。

## 4. 重复次数与蒙特卡洛标准误（MCSE）

**没有 MCSE 的模拟结果只是意见。** 永远报告主要指标的蒙特卡洛不确定性，并选择足够大的 `R`，使 MCSE 相对于所声称的效应足够小。

| 指标 | 蒙特卡洛标准误 | 经验法则 |
|---|---|---|
| 偏误 / 均值估计 | `sd(estimates) / sqrt(R)` | 写在每个偏误数字旁边 |
| 覆盖率 `p` | `sqrt(p * (1 - p) / R)` | 覆盖率接近 0.95 时要 MCSE ≈ 0.005（±0.5 pp），需 `R ≈ 1900`；要 ±1 pp，需 `R ≈ 475` |
| 拒绝率 / 功效 | `sqrt(p * (1 - p) / R)` | 同覆盖率 |
| RMSE | 对重复做 bootstrap 或 delta 法 | 至少报告 `R`，让读者能估量它 |

如果两个估计量之差不到几个 MCSE，就要明确说明，不能仅凭数值更小就认定其中一个「更好」。

## 5. 指标：算对它们

所有指标都要对照**真值**定义，绝不能对照另一个估计：

- **偏误** = `mean(est) - truth`。
- **经验标准误** = 各次重复的 `sd(est)`（真实的抽样波动）。
- **RMSE** = `sqrt(mean((est - truth)^2))`。
- **覆盖率** = 置信区间**包含 `truth`** 的重复所占比例，即 `mean(ci_lo <= truth & truth <= ci_hi)`。模拟中最常见的单个 bug，就是拿置信区间去对点估计，或对一个标错的「真」值。
- **水平 / 功效** = 原假设 DGP 下的检验拒绝率是水平，备择 DGP 下的检验拒绝率是功效。水平必须在原假设字面成立的 DGP 下评估。

## 6. 存储：存原始，不只是汇总

- 用 `saveRDS()` 保存**逐次重复的原始结果**，不能只保存汇总表。原始结果使用一个 tibble，每次重复 × 估计量一行，包含 `est`、`se`、`ci_lo`、`ci_hi`、`converged`。重新聚合、新增指标和 `sim-reviewer` 都需要这个原始对象。
- 汇总表同时保存为 `.rds` **和**一份人类可读的 `.csv`/`.tex`，输出到仓库规范路径 `output/`。
- 绝不能让重点报告的数字只存在于控制台输出中，否则既无法审计，也无法重新渲染到幻灯片上。

## 7. 性能与稳健性

- **预分配**；绝不在循环内用 `c()`/`append()` 增长结果向量（见 `r-code-conventions.md` §8）。
- 显式统计并报告**失败/未收敛的重复**（`converged` 标记）。悄悄丢弃它们会让每个指标都有偏。
- 不要每次重复都 `print()`/`cat()`。使用一条进度条（`progressr`），或者不使用进度输出。
- 计算汇总前，先检查并处理估计结果中的 `NA`/`NaN`/`Inf`；决定并记录它们应计为失败还是被排除。

## 8. 常见陷阱

| 陷阱 | 影响 | 预防 |
|---|---|---|
| DGP 悄悄违反了某条维持的假定 | 其他每项检查都会通过，但结果只能说明那次违反，不能说明估计量 | 填写体制块；逐条核验假定，不能只作断言 |
| 假定内的断言引自假定外的运行 | 关于估计量的断言超出证据能够支撑的范围 | 防火墙（§2） |
| 一次放松两条假定 | 无法判断失败由哪条假定引起 | 每次运行只放松一条，扫严重程度网格 |
| 在循环里 `set.seed()` | 各次重复完全相同或相关；方差被低估 | 顶部设一次种子；并行用 L'Ecuyer 流 |
| 覆盖率对照估计而不是真值 | 覆盖率因构造方式接近名义水平，失去意义 | `mean(ci_lo <= truth & truth <= ci_hi)` |
| 不报 MCSE | 差异仍处于噪声范围时宣称「估计量 A 优于 B」 | 报告偏误/覆盖率/功效上的 MCSE |
| 估计量瞄准的估计目标与 `真值`不同 | 把目标不匹配误报为「偏误」 | 声明每个估计量的估计目标；与真值对齐 |
| 原始逐次结果被丢弃 | 无法重新聚合或审计 | `saveRDS()` 原始 tibble |
| 丢弃失败重复却不记录 | 所有指标都会产生存活偏差 | 跟踪并报告 `converged` 计数 |

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

- [`r-code-conventions.md`](r-code-conventions.md) — 通用 R 标准，包括种子格式、预分配和数值纪律。
- [`../agents/sim-reviewer.md`](../agents/sim-reviewer.md) — 执行本规则的代理。
- [`../agents/r-reviewer.md`](../agents/r-reviewer.md) — 第 9 类（错误处理）+ 第 11 类（数值纪律）。
- [`replication-protocol.md`](replication-protocol.md) — 先复现再扩展的容差约定，适用于模拟复现已发表表格的情况。
- [`../skills/credible-claims/SKILL.md`](../skills/credible-claims/SKILL.md) — 断言强度不能超过其背后运行能够支撑的范围；防火墙（§2）将这项要求应用于假定体制。

## 并行必须可证明地与运行形状无关

**按任务播种，不按 worker 播种。** 为每次重复预先生成**一条 RNG 流**（L'Ecuyer `"L'Ecuyer-CMRG"`），使第 *k* 次重复无论在哪个核上运行、无论使用几个核，都抽取同一批数字。

按 worker 播种，包括 `mc.set.seed`、`clusterSetRNGStream` 或「在 worker 内部设种子」，**会在没有提示的情况下把结果绑定到运行方式上**。同一个脚本因此在笔记本和集群上产生不同数字，却不会发出任何警告。复现者会发现这个复现性故障，而你自己可能不会发现。

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

**在相信整轮批量运行之前，先证明这一点。** 在两种核数下运行前 N 次重复，并断言结果逐位一致：

```r
a <- run_campaign(n_reps = 20, n_cores = 2)
b <- run_campaign(n_reps = 20, n_cores = 4)
stopifnot(identical(a, b))   # fails loudly if results depend on run shape
```

这是**你的并行环境所需的正对照**。双核/四核检查成本很低，几秒钟即可完成，也是唯一能区分「播种正确」与「播种方式碰巧在这台机器上看似正常」的方法。把结果记入资格台账。

Stata：在循环内按重复从预生成的列表中设置 `seed`，不要在 `parallel` 块之前只设一次。Python：使用 `numpy.random.SeedSequence(...).spawn(n_reps)`，每次重复一个子序列，绝不能每个 worker 一个。
