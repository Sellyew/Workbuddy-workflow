---
paths:
  - "**/*.do"
  - "scripts/stata/**"
---

# Stata 代码规范

**可复现性是默认，不是特性。** 一个 `.do` 文件应当能从干净的 shell 直接跑起来，无需任何手工干预。每个脚本无论跑多少次，都结束在同一状态。

> 本规则是 [`r-code-conventions.md`](r-code-conventions.md) 的镜像，面向以 Stata 为先的用户。在同一项目里同时用 R 和 Stata 的复刻者：两条规则各自适用于对应的文件。

## 1. 可复现性脚手架

每个 `.do` 文件都以同一个头部开始：

```stata
/*------------------------------------------------------------
File:       NN_descriptive_name.do
Purpose:    [one-sentence description]
Inputs:     [path to inputs]
Outputs:    [path to outputs]
Run order:  Standalone | After NN_prior.do
------------------------------------------------------------*/

version 18                        // pin Stata semantics
clear all
set more off
set seed 12345                    // pin RNG seed for any random ops
set sortseed 12345                // pin sort stability across versions
cap log close
cap log close _all                // belt-and-suspenders
log using "output/NN_log.smcl", replace
```

为什么每一行都在：

- **`version 18`**——语义显式。新版 Stata 会悄悄改变默认（例如 `reghdfe` 的聚类自由度调整）；钉住是唯一的防线。
- **`clear all`**——不残留上一次会话的状态。
- **`set more off`**——脚本不该为按键暂停。
- **`set seed` + `set sortseed`**——每个随机操作 + 每次 `sort` 都是确定性的。
- **`cap log close _all`**——预先关掉上一次会话留下的任何日志。
- **`log using ... , replace`**——捕获标准输出；`replace` 保证重跑不会追加。

每个 `.do` 文件以这几行结束：

```stata
log close
exit, clear STATA      // explicit clean exit; useful in batch mode
```

## 2. 编号流水线

脚本住在 `scripts/stata/`，按运行顺序编号：

```
scripts/stata/
├── 00_install.do        # ssc install packages, set globals, paths
├── 01_clean.do          # raw → cleaned panel
├── 02_descriptive.do    # summary tables, balance, attrition
├── 03_analyze.do        # main regression specs
├── 04_robustness.do     # alt specs, sensitivity
├── 05_tables_figures.do # estout/esttab + graph export
└── 99_run_all.do        # do "01_clean.do" / do "02_..." / ...
```

99 号脚本是**一条命令复现**：在仓库根目录执行 `do scripts/stata/99_run_all.do`，产出论文引用的每一个输出。AEA Data Editor 检查的正是这个形状。

## 3. 输出约定

所有输出落在顶层 `output/` 目录——绝不在 `scripts/` 以内，并与同一项目里任何 R 或 Python 阶段共用（AEA Data Editor 的建议：不要把代码与它的结果混放）：

```
output/
├── 01_log.smcl                 # captured stdout per script
├── clean_panel.dta             # cleaned data (regenerable intermediate; gitignored)
├── descriptives.csv            # summary stats
├── main_results.tex            # esttab → .tex for direct \input{} in paper
├── balance_table.tex
├── fig_eventstudy.pdf          # graph export, vector
└── sessionInfo_stata.txt       # capture stata version + installed pkg versions
```

`sessionInfo_stata.txt` 是强制的（这样命名是为了在混合项目里不覆盖 R 的 `sessionInfo.txt`）。这样生成：

```stata
* At end of 00_install.do (or via a dedicated sessioninfo subroutine):
log using "output/sessionInfo_stata.txt", text replace
which estout
which reghdfe
which ivreg2
about
log close
```

这让 AEA / 审稿人 / 未来的你看到实际用到的包版本。

## 4. 表格（estout / esttab）

论文里出现的任何表格都用 `esttab`。**绝不在 LaTeX 里手工排版表格**——`\input{}` 这一写法意味着表格单元格的值来自真正的估计：

```stata
quietly: reghdfe y x1 x2, absorb(unit time) cluster(unit)
eststo m1
quietly: reghdfe y x1 x2 controls, absorb(unit time) cluster(unit)
eststo m2

esttab m1 m2 using "output/tab_main.tex", replace ///
    booktabs label                              /// use the variable labels you set
    se(2) b(3)                                  /// SE in parens, 3-decimal coeffs
    star(* 0.10 ** 0.05 *** 0.01)              /// significance convention
    stats(N r2, fmt(%9.0fc %9.3f) labels("Observations" "R²")) ///
    nonotes addnote("Robust SEs clustered at unit level.")
```

然后在稿件里：`\input{output/tab_main.tex}`——每次 .do 文件运行，表格的值都机械地更新。

## 5. 显著性星号约定

默认是 `* 0.10 ** 0.05 *** 0.01`（经济学惯例；与 AER / QJE / JPE / ECMA 的默认一致）。政治学期刊（APSR / AJPS / JOP）也常用同一套。即使「显而易见」，也要在表注里写明这个约定——审稿人会读表注。

单尾的情形（已发表作品中少见），用 `* 0.05 ** 0.025 *** 0.005`，并在表注里解释原因。默认用双尾。

## 6. 聚类与标准误约定

- **永远在处置分配的层级聚类**（或可依赖性的最高合理层级）。绝不在没有理由的情况下用默认的 `, robust`。
- **`reghdfe` 默认做自由度调整的聚类**，但要核查——Stata 的 `, cluster()` 与 `reghdfe ... , cluster()` 在某些边缘情形下用了不同的自由度调整。文件顶部的版本钉住是部分防线；显式的 `, dofadj() ` 是其余部分。
- **聚类数很少时（< 50 组）用 bootstrap 聚类**：用 `cluster bootstrap`，不是 `bootstrap, cluster()`。

## 7. 平衡 / 流失纪律

对每个 RCT 或准实验设计：

- **平衡表**用 `iebaltab`（世界银行的 `ietoolkit` 包）。不要自己造。
- **流失表**——每轮缺失比例，按处置状态平衡。同样的 `iebaltab` 调用，换一个结果变量。
- **操纵检验**（调查实验）——各臂的通过率。写进论文，不只是在 .do 里。

## 8. 图（graph export）

```stata
graph export "output/fig_eventstudy.pdf", replace as(pdf)
graph export "output/fig_eventstudy.png", replace as(png) width(2000)
```

矢量的（PDF 给论文）和点阵的（PNG 给幻灯片）都要。不要依赖自动生成的 `.gph`——它跨 Stata 版本不可移植。

## 9. 常见的 Stata → R / Stata → AEA 陷阱

| 陷阱 | 修法 |
|---|---|
| `reg y x, cluster(id)` 没有显式自由度调整 | 用 `reghdfe` 拿到显式自由度；在表注里说明所做的调整 |
| Bootstrap 次数在多次运行间不一致 | 文件顶部 `set seed` + `set sortseed`；用 `bootstrap, reps(N) seed(X)` |
| `replace` 改动观测数据 | 一律 `gen new_var = ... `，检查过再 `drop` |
| `merge 1:1` 没有 `assert` | `merge 1:1 id using foo, assert(3)`——键不匹配就大声失败 |
| 在缺失值上写 `if` | Stata 在不等于比较里把 `.` 当作 `+∞`。要「非缺失且大于 5」就写 `if x > 5 & x != .` |
| `egen sum(x)` 已过时 | `egen total(x)` 是现代写法；`egen sum()` 仍可用，但 `bysort id: egen y = total(x)` 是更稳的写法 |

## 10. AEA Data Editor 合规

[AEA Data Editor 清单](https://aeadataeditor.github.io/)要求：

- 仓库根目录的 `README.md`，说明数据来源、计算要求、运行指引。
- 一条命令复现全部结果（`do scripts/stata/99_run_all.do`）。
- 所有脚本编号并排序。
- 一份等价的 `requirements.txt`——对 Stata 而言，就是 §3 的 `sessionInfo_stata.txt` 加上 `00_install.do` 里的 `ssc install` 命令清单。
- 许可证（MIT / GPL / 类似）。
- 没有硬编码路径——用全局量，或用相对仓库根目录的相对路径。

## 执行

- [`/stata-replication`](../skills/stata-replication/SKILL.md) 是 Stata 版的 `/data-analysis`。它产出的 .do 文件符合本规范。
- [`/audit-reproducibility`](../skills/audit-reproducibility/SKILL.md) 除 R 的 `.rds` 之外也处理 Stata 的 `.dta` 输出（经由 `haven` 或 `pyreadstat`）。
- [`/review-r`](../skills/review-r/SKILL.md) 只面向 R；目前还没有 Stata 代码审读技能。

## 交叉引用

- [`r-code-conventions.md`](r-code-conventions.md) — 面向 R 优先流水线的同类纪律。
- [`replication-protocol.md`](replication-protocol.md) — 跨 R / Stata / Python 适用的容差契约。
- [`../references/release-engineering.md`](../references/release-engineering.md) — 把 `.ado` 包或复现包作为带版本产物发布：message 与 silent-resolution 普查、preflight 归档、生成的 status 契约、下游钉版本。
- [stata-mcp on GitHub](https://github.com/SepineTam/stata-mcp) — 让 WorkBuddy 执行 Stata `.do` 文件的 MCP 服务器。装法见 [`stata-replication`](../skills/stata-replication/SKILL.md) 的前置条件：插件页 → MCP 服务器 → 配置 MCP，或把它写进用户级 `~/.workbuddy/mcp.json`。（上游的 `claude mcp add --scope user` 在本平台没有对应命令。）
