---
name: simulation-study
description: 在 R 中搭建并运行可复现的蒙特卡洛（Monte Carlo）模拟研究——声明式假设情形、参数化 DGP、估计量网格、带种子的重复循环，以及带有蒙特卡洛标准误的偏误、RMSE、经验标准误、覆盖率、规模/功效的汇总。用户说 "run a Monte Carlo simulation"、"simulation study"、"check the bias/coverage of an estimator"、"compare estimators in simulation"、"size and power simulation"、"Monte Carlo experiment"，或想展示某估计量的有限样本性质时使用。产出 `scripts/R/` 下带编号的 R 脚本，并把逐次重复的原始结果 + 汇总表保存到 `output/`。
argument-hint: "[estimator(s) and DGP to study, or path to a script/paper to simulate from]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task", "TaskOutput"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/simulation-study` —— 蒙特卡洛模拟研究

设计并运行蒙特卡洛实验，评估估计量的有限样本行为，再审查代码，找出会让模拟证据悄悄失效的 bug。

| 参数 | 说明 |
|---|---|
| `$ARGUMENTS` | 待研究的估计量与 DGP 的描述（例如"在弱工具变量 + 异方差下比较 2SLS 与 LIML"），或指向一个既有脚本/论文的指针，其模拟你想复现或扩展。 |

---

## 约束

- **遵循 [`.codebuddy/rules/simulation-conventions.md`](../../rules/simulation-conventions.md)**。其中关于 DGP、真值、估计目标、MCSE 和假设情形的模拟契约不可协商。
- **在脚本头部声明假设情形**，并遵守防火墙：超出假设的运行不能支持假设内的论断（[`simulation-conventions.md`](../../rules/simulation-conventions.md) §2）。
- **遵循 [`.codebuddy/rules/r-code-conventions.md`](../../rules/r-code-conventions.md)** 中的通用 R 标准，包括头部、顶部 `library()`、相对路径和数值约束。
- **将脚本保存到** `scripts/R/`，文件名要编号并能说明内容，例如 `scripts/R/sim_2sls_vs_liml.R`。
- **将输出保存到** `output/`，包括逐次重复的原始 tibble、汇总表和图。
- **对逐次重复的原始结果调用 `saveRDS()`**，不能只保存汇总，因为重新聚合和审查都需要原始结果。
- **呈现结果前运行 `sim-reviewer` 代理**审查生成的脚本，并处理 Critical/High 级别的发现。

---

## 工作流阶段

### Phase 0：开始前报告

**编写任何代码前，先输出开始前报告**，明确实验设计。这样可以避免最常见的失败：结果表看似完整，估计目标却不匹配，或把估计值误当作真值来计算覆盖率。

```markdown
## Pre-Flight Report — Simulation Design

**Research question:** [what finite-sample property is being demonstrated]
**Target estimand:** [ATT / ATE / coefficient θ — and how its TRUE value is computed from the DGP params]
**Maintained assumptions:** [the FULL list the estimator(s) under study require — A1 … An, every one]
**Regime:** [IN-ASSUMPTION — all hold | OUT-OF-ASSUMPTION — relaxes A[k] only, severity grid {…}, targeting pseudo-estimand …]
**Verification:** [per assumption, the checkable property of the DGP that establishes it — by construction or by an assertion]
**DGP:** [structure + the parameters that define it; what is held fixed vs. varied]
**Estimator grid:** [list each estimator + which estimand it targets + how it returns est/se/CI]
**Design grid:** [sample sizes, parameter values, scenarios to sweep]
**Replications R:** [value] → implied MCSE on coverage ≈ sqrt(0.95·0.05/R) = [value]
**Metrics:** bias, empirical SE, RMSE, coverage, size/power — each with MCSE
**Conventions read:** simulation-conventions.md, r-code-conventions.md
```

如果估计目标或其真值不明确，**先停下询问**，再写代码。

如果你无法说明 DGP 的哪条性质可以验证某项假设，这次运行就**不是** `IN-ASSUMPTION`。按照防火墙，它不能支持任何假设内论断。必须在开始前报告中写明这一点，不能在脚本头部声称从未检查过的假设已经成立。

### Phase 1：DGP

编写**一个**参数化函数来返回数据集，并根据参数计算、返回或存储**真实**目标值。

```r
generate_data <- function(n, params) {
  # ... generate covariates, treatment, outcome from params ...
  list(data = df, truth = compute_truth(params))   # truth from params, never from an estimate
}
```

头部的 **Verified** 行必须由实际检查支撑。假设情形区块中每项声称*经检查*成立的假设，都要在脚本中实现相应检查，例如大样本抽样断言、条件数或对参数边界的 `stopifnot()`，并在设置阶段运行一次。只写在注释里的验证只是断言，不算验证。

### Phase 2：估计量网格

将每个估计量写成函数 `data -> list(est, se, ci_lo, ci_hi, converged)`，并注明每个估计量针对的估计目标。若用错配的真值给估计量评分，就是 bug，不只是审查发现。

### Phase 3：重复引擎

- `set.seed(YYYYMMDD)` **只调用一次**。并行重复时使用 `RNGkind("L'Ecuyer-CMRG")` 与 `furrr::furrr_options(seed = TRUE)`。
- 每次运行都按生成数据 → 运行每个估计量 → 每个估计量记录一行的顺序执行，并保存 `est, se, ci_lo, ci_hi, converged`。
- 预先分配或绑定一个 `R × (#estimators)` 行的 tibble。跟踪所有未收敛情况，绝不能悄悄丢弃。

### Phase 4：指标与汇总

按估计量 × 情形分组，并相对**真值**计算：

- **偏误** = `mean(est) - truth`（+ MCSE = `sd(est)/sqrt(R)`）
- **经验标准误** = `sd(est)`；**RMSE** = `sqrt(mean((est - truth)^2))`
- **覆盖率** = `mean(ci_lo <= truth & truth <= ci_hi)`（+ MCSE = `sqrt(p(1-p)/R)`）
- **规模 / 幂** = 原假设 / 备择 DGP 下的拒绝率
- **失败数** = 未收敛重复的次数

生成整洁的汇总表，在每个头条指标旁报告 MCSE。

### Phase 5：图

使用 `ggplot2` 和项目主题，绘制偏误 / 覆盖率对样本量（或情形）的图，并添加参考线（0 偏误、名义覆盖率）。背景透明，尺寸显式指定，遵循 `r-code-conventions.md` §4。

### Phase 6：保存与审查

1. 用 `saveRDS()` 将**逐次重复的原始 tibble** 和**汇总表**保存到 `output/`，并将汇总另存为 `.csv`/`.tex`。
2. 运行审查：

   ```
   Delegate to the sim-reviewer agent:
   "Review the simulation script at scripts/R/[name].R"
   ```

   该代理只读并返回报告；主会话负责将报告保存到 `quality_reports/[name]_sim_review.md`。

3. 呈现结果前，处理 Critical/High 级别的发现，包括覆盖率未对真值计算、估计目标错配、缺少 MCSE、丢弃重复、未声明或未验证假设情形。
4. **呈现结果时也要遵守防火墙。** 每项论断都必须引用假设情形足以支持它的运行。一致性、有效解析标准误、名义覆盖率和默认值交付都只能依据 `IN-ASSUMPTION` 运行（[`simulation-conventions.md`](../../rules/simulation-conventions.md) §2）。每个图表说明都要注明假设情形；严重度网格若混用两种情形，就逐行注明。

---

## 脚本结构

```r
# ============================================================
# [Title] — Monte Carlo simulation
# Author: [project context]
# Purpose: [property being demonstrated]
# Estimand: [target + how truth is computed]
# Maintained assumptions: [A1 ... An — the FULL list the estimator requires]
# Regime: [IN-ASSUMPTION | OUT-OF-ASSUMPTION: relaxes A[k] only, severity ...,
#          targeting pseudo-estimand ...]
# Verified: [per assumption, the property that was actually checked, not asserted]
# Outputs: output/[name]_raw.rds, [name]_summary.{rds,csv}
# ============================================================

# 0. Setup ----
library(tidyverse)
library(furrr)            # parallel reps (optional)
plan(multisession)        # enable parallel workers; omit this line to run sequentially
RNGkind("L'Ecuyer-CMRG")
set.seed(20260531)        # once, YYYYMMDD (simulation-conventions.md §3)
R   <- 2000L              # MCSE on coverage near .95 ≈ 0.005
dir.create("output", recursive = TRUE, showWarnings = FALSE)

# 1. DGP ----
generate_data <- function(n, params) { ... }     # returns list(data, truth)

# 2. Estimators ----
estimators <- list(tsls = est_tsls, liml = est_liml)    # each -> est, se, ci, converged

# 3. Run one replication ----
run_one_rep <- function(rep_id, n, params) { ... }      # -> tibble rows (one per estimator)

# 4. Replicate ----
raw <- future_map_dfr(seq_len(R), run_one_rep, n = n, params = params,
                      .options = furrr_options(seed = TRUE))

# 5. Summarize (vs truth, with MCSE) ----
# Group by EVERY design-grid dimension you sweep (estimator, n, scenario, ...) so
# each group has a single true value. Use per-row `truth` — never `truth[1]` — so a
# truth that varies across the grid can't be silently mis-scored. Score only the
# converged reps; report failures separately.
summary_tbl <- raw |>
  filter(converged) |>
  group_by(estimator) |>                       # add n, scenario, ... as needed
  summarise(
    R_eff    = n(),
    bias     = mean(est - truth),
    emp_se   = sd(est),
    rmse     = sqrt(mean((est - truth)^2)),
    coverage = mean(ci_lo <= truth & truth <= ci_hi),
    .groups  = "drop"
  ) |>
  mutate(
    bias_mcse = emp_se / sqrt(R_eff),
    cov_mcse  = sqrt(coverage * (1 - coverage) / R_eff)
  )

failures <- raw |> group_by(estimator) |> summarise(n_fail = sum(!converged), .groups = "drop")

# Size/power: add `power = mean(reject)` (+ `sp_mcse = sqrt(power*(1-power)/R_eff)`)
# to the summary above — each estimator must emit a per-rep `reject = p_value < alpha`
# column. Size = rejection rate under the null DGP; power = under the alternative.

# 6. Export ----
saveRDS(raw, "output/[name]_raw.rds")
saveRDS(summary_tbl, "output/[name]_summary.rds")
write_csv(summary_tbl, "output/[name]_summary.csv")
```

---

## 要点

- **先声明假设情形，再遵守防火墙。** 即使 DGP 违反维持假设，其他检查也可能全部通过；但无论数字多整齐，这次运行都不能支持假设内论断。
- **真值来自 DGP，永不来自估计值。** 覆盖率指置信区间包含*真实*参数的比例。
- **没有 MCSE 就没有结果。** 如果两个估计量之差小于约 2× MCSE，就如实说明。
- **存原始结果，不只存汇总。** 只出现在控制台里的数字既无法审计，也无法用于幻灯片。
- **数清你的失败。** 悄悄丢弃未收敛重复会使所有指标失真。

## 长时间模拟：后台 Bash + TaskOutput

大网格（许多情形 × 很大的 `R`）可能运行很多分钟。操作如下：

1. 用 Bash 的 `run_in_background: true` 在后台启动，并把 R 的 stdout 和 stderr 写入日志：`mkdir -p output && Rscript scripts/R/[name].R > output/[name].log 2>&1`。记录 Bash 返回的 `task_id`；进程退出时，后台任务会自动通知你。
2. 收到完成通知后，用该 `task_id` 调用 **TaskOutput** 读取退出状态和输出；需要等待完成时使用 `block: true`，只需查看当前状态时使用 `block: false`。然后检查日志中的进度里程碑（例如一次 `progressr` 更新）和错误特征（`Error`、`Execution halted`），并按 Phase 6 检查预期的原始结果、汇总表和图等产物存在且非空、关键 RDS 可读。
3. 不要用 `sleep` 轮询循环，也不要另设日志监视进程。详见 [`data-analysis/SKILL.md`](../data-analysis/SKILL.md) 和指南中的 Cost-Conscious Parallelism 一节。
