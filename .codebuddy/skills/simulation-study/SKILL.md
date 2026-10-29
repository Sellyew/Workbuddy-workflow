---
name: simulation-study
description: 在 R 中搭建并运行可复现的蒙特卡洛（Monte Carlo）模拟研究——声明式假设情形、参数化 DGP、估计量网格、带种子的重复循环，以及带有蒙特卡洛标准误的偏误、RMSE、经验标准误、覆盖率、规模/幂的汇总。用户说 "run a Monte Carlo simulation"、"simulation study"、"check the bias/coverage of an estimator"、"compare estimators in simulation"、"size and power simulation"、"Monte Carlo experiment"，或想展示某估计量的有限样本性质时使用。产出 `scripts/R/` 下带编号的 R 脚本，并把逐次重复的原始结果 + 汇总表保存到 `output/`。
argument-hint: "[estimator(s) and DGP to study, or path to a script/paper to simulate from]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task", "Monitor"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/simulation-study` —— 蒙特卡洛模拟研究

设计并运行一个蒙特卡洛实验，刻画某估计量的有限样本行为，然后审查它，找出那些会悄悄使模拟证据失效的 bug。

| 参数 | 说明 |
|---|---|
| `$ARGUMENTS` | 待研究的估计量与 DGP 的描述（例如"在弱工具变量 + 异方差下比较 2SLS 与 LIML"），或指向一个既有脚本/论文的指针，其模拟你想复现或扩展。 |

---

## 约束

- **遵循 [`.codebuddy/rules/simulation-conventions.md`](../../rules/simulation-conventions.md)** —— 模拟契约（DGP、真值、估计目标、MCSE、假设情形）不可协商。
- **在脚本头部声明假设情形**，并尊重防火墙——一次超出假设的运行，永远不能支撑一条假设内的论断（[`simulation-conventions.md`](../../rules/simulation-conventions.md) §2）。
- **遵循 [`.codebuddy/rules/r-code-conventions.md`](../../rules/r-code-conventions.md)** 中的通用 R 标准（头部、顶部 `library()`、相对路径、数值约束）。
- **保存脚本**到 `scripts/R/`，用带编号、能说明内容的文件名（例如 `scripts/R/sim_2sls_vs_liml.R`）。
- **保存输出**（逐次重复的原始 tibble、汇总表、图）到 `output/`。
- **对逐次重复的原始结果做 `saveRDS()`**，而不只是存汇总——重新聚合与审查环节都要用它们。
- **在呈现结果之前运行 `sim-reviewer` 代理**审查生成的脚本，然后处理 Critical/High 级别的发现。

---

## 工作流阶段

### Phase 0：起飞前报告

**在写任何代码之前，先产出一份起飞前报告**，表明你已经把实验钉死。这能防住最常见的失败模式——一张漂亮的结果表，建立在错配的估计目标、或"覆盖率对着估计值算"的 bug 之上。

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

若估计目标或它的真值含混不清，**停下并询问**，然后再写代码。

若某条假设无法验证——你说不出 DGP 中哪条性质确立了它——这次运行就**不是** `IN-ASSUMPTION`，且按防火墙，任何假设内的论断都不得以它为依据。在起飞前报告里说明这一点，而不是让头部去断言从未检查过的东西。

### Phase 1：DGP

写出**一个**参数化函数，返回一个数据集。并从参数计算、返回（或存储）**真实**的目标值。

```r
generate_data <- function(n, params) {
  # ... generate covariates, treatment, outcome from params ...
  list(data = df, truth = compute_truth(params))   # truth from params, never from an estimate
}
```

头部那些 **Verified** 行就是在这里挣来的：假设情形区块声称*经检查*成立的每一条假设，都要把该检查写进脚本（一次大样本抽样断言、一个条件数、对参数边界的 `stopifnot()`），并在设置阶段跑一次。一条只存在于注释里的验证，是被断言，不是被验证。

### Phase 2：估计量网格

每个估计量都是一个函数 `data -> list(est, se, ci_lo, ci_hi, converged)`。写明每一个所瞄准的估计目标；一个对着错配真值打分的估计量是 bug，不是审查发现。

### Phase 3：重复引擎

- `set.seed(YYYYMMDD)` **只调一次**。并行重复时用 `RNGkind("L'Ecuyer-CMRG")` 与 `furrr::furrr_options(seed = TRUE)`。
- 一次运行 = 生成数据 → 跑每个估计量 → 每个估计量记一行，带 `est, se, ci_lo, ci_hi, converged`。
- 预先分配 / 绑定结果为 `R × (#estimators)` 行的 tibble。跟踪未收敛情况；绝不悄悄丢弃。

### Phase 4：指标与汇总

按估计量 × 情形，对着**真值**：

- **偏误** = `mean(est) - truth`（+ MCSE = `sd(est)/sqrt(R)`）
- **经验标准误** = `sd(est)`；**RMSE** = `sqrt(mean((est - truth)^2))`
- **覆盖率** = `mean(ci_lo <= truth & truth <= ci_hi)`（+ MCSE = `sqrt(p(1-p)/R)`）
- **规模 / 幂** = 原假设 / 备择 DGP 下的拒绝率
- **失败数** = 未收敛重复的次数

构建一个整洁的汇总表；在每个头条指标旁报告 MCSE。

### Phase 5：图

用 `ggplot2` 配合项目主题：偏误 / 覆盖率 对 样本量（或情形），带参考线（0 偏误、名义覆盖率）。透明背景，显式尺寸（按 `r-code-conventions.md` §4）。

### Phase 6：保存与审查

1. 把**逐次重复的原始 tibble** 与**汇总表** `saveRDS()` 到 `output/`；并把汇总另写为 `.csv`/`.tex`。
2. 运行审查：

   ```
   Delegate to the sim-reviewer agent:
   "Review the simulation script at scripts/R/[name].R"
   ```

   该代理是只读的，返回其报告；把它保存到 `quality_reports/[name]_sim_review.md`。

3. 在呈现之前，处理 Critical/High 级别的发现（覆盖率对真值、估计目标错配、缺 MCSE、被丢弃的重复、未声明或未验证的假设情形）。
4. **把防火墙应用到呈现本身。** 你即将作出的每一条论断，都必须援引一次其假设情形撑得住的运行——一致性、有效的解析标准误、名义覆盖率、以及交付一个默认值，都要求 `IN-ASSUMPTION` 运行，别的都不行（[`simulation-conventions.md`](../../rules/simulation-conventions.md) §2）。在每个图表说明里带上假设情形——若某个严重度网格混用了两种情形，则逐行带上。

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

- **先声明假设情形，再尊重防火墙。** 一个违反维持假设的 DGP 产出的表，会让这里其他每一项检查都通过——而建立在它之上的假设内论断是不受支持的，无论数字看起来多干净。
- **真值来自 DGP，永不来自估计值。** 覆盖率指的是置信区间包含*真实*参数。
- **没有 MCSE 就没有结果。** 若两个估计量之差小于约 2× MCSE，就照实说。
- **存原始结果，不只存汇总。** 一个只存在于控制台里的数字，既无法审计，也上不了幻灯片。
- **数清你的失败。** 悄悄丢弃未收敛的重复会污染每一个指标。

## 长时间模拟：使用 Monitor 工具

大网格（许多情形 × 很大的 `R`）可能跑上很多分钟。用 Bash 加 `run_in_background: true` 后台启动，把 R 的 stdout 与 stderr 写入日志（例如 `Rscript scripts/R/[name].R > output/[name].log 2>&1`），并用 **Monitor 工具**跑一条命令，让该日志经 `grep --line-buffered` 流过，匹配进度里程碑（例如一次 `progressr` 更新）与失败特征（`Error`、`Execution halted`），而不是用 `sleep` 轮询。Monitor 没有 job-id 参数：它自己命令的 stdout 就是事件流。见 [`data-analysis/SKILL.md`](../data-analysis/SKILL.md) 与指南中的 Cost-Conscious Parallelism 一节。
