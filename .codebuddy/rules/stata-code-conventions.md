---
paths:
  - "**/*.do"
  - "scripts/stata/**"
---

# Stata 代码规范

**可复现性是默认要求，不是可选功能。** 一个 `.do` 文件应当能从干净的 shell 直接运行，不需要手工干预。无论运行多少次，每个脚本都应结束于同一状态。

> 本规则与 [`r-code-conventions.md`](r-code-conventions.md) 对应，面向优先使用 Stata 的用户。在同一项目中同时使用 R 和 Stata 时，两条规则分别适用于对应文件。

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

每一行都有以下作用：

- **`version 18`**——固定 Stata 自带命令的语义，但不能固定 `reghdfe` 等用户贡献包的行为；还需同时记录并固定 `reghdfe` 及其依赖包的版本。
- **`clear all`**——清除上一次会话遗留的状态。
- **`set more off`**——避免脚本暂停等待按键。
- **`set seed` + `set sortseed`**——确保每个随机操作和每次 `sort` 都有确定结果。
- **`cap log close _all`**——预先关闭上一次会话留下的所有日志。
- **`log using ... , replace`**——捕获标准输出；`replace` 确保重跑时不会追加到旧日志。

每个 `.do` 文件以这几行结束：

```stata
log close
exit, clear STATA      // explicit clean exit; useful in batch mode
```

## 2. 编号流水线

脚本放在 `scripts/stata/`，按运行顺序编号：

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

99 号脚本负责**用一条命令完成复现**：在仓库根目录执行 `do scripts/stata/99_run_all.do`，生成论文引用的所有输出。AEA Data Editor 检查的正是这种结构。

## 3. 输出约定

所有输出都放在顶层 `output/` 目录，绝不能放进 `scripts/`。同一项目中的 R 或 Python 阶段也共用该目录。AEA Data Editor 建议不要把代码与其结果混放：

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

`sessionInfo_stata.txt` 是强制要求。采用这个文件名，是为了避免在混合项目中覆盖 R 的 `sessionInfo.txt`。生成方式如下：

```stata
* At end of 00_install.do (or via a dedicated sessioninfo subroutine):
log using "output/sessionInfo_stata.txt", text replace name(sessioninfo)
which estout
which reghdfe
which ivreg2
about
log close sessioninfo
```

这样，AEA、审稿人和未来的你都能查看实际使用的包版本。

## 4. 表格（estout / esttab）

论文中的任何表格都要用 `esttab` 生成。**绝不要在 LaTeX 里手工排版表格**。通过 `\input{}` 引入表格，可以确保单元格中的值来自实际估计：

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

然后在稿件里写入 `\input{output/tab_main.tex}`。每次运行 .do 文件，表格值都会自动更新。

## 5. 显著性星号约定

默认使用 `* 0.10 ** 0.05 *** 0.01`。这是经济学惯例，也与 AER / QJE / JPE / ECMA 的默认设置一致；政治学期刊 APSR / AJPS / JOP 也常使用同一套约定。即使看似显而易见，也要在表注中写明，因为审稿人会阅读表注。

单尾检验在已发表作品中较少见。此时使用 `* 0.05 ** 0.025 *** 0.005`，并在表注中解释原因。默认使用双尾检验。

## 6. 聚类与标准误约定

- **永远在处置分配的层级聚类**，或在依赖关系的最高合理层级聚类。绝不能在没有理由的情况下使用默认的 `, robust`。
- **`reghdfe` 默认对聚类做自由度调整**，但仍要核查。Stata 的 `, cluster()` 与 `reghdfe ... , cluster()` 在某些边缘情形下采用不同的自由度调整。文件顶部固定版本只能提供部分保障，其余保障来自显式的 `, dofadj() `。
- **聚类数很少时（< 50 组）使用聚类 bootstrap**：使用 `bootstrap ..., cluster(id) idcluster(newid)`；按被前缀命令的需要，用 `idcluster(newid)` 生成新的簇 ID。

## 7. 平衡 / 流失纪律

对每个 RCT 或准实验设计：

- **平衡表**使用 `iebaltab`，它来自世界银行的 `ietoolkit` 包。不要自行另造。
- **流失表**报告每轮缺失比例，并按处置状态检验平衡。使用同样的 `iebaltab` 调用，只更换结果变量。
- **操纵检验**用于调查实验，报告各实验组的通过率。结果要写进论文，不能只留在 .do 文件中。

## 8. 图（graph export）

```stata
graph export "output/fig_eventstudy.pdf", replace as(pdf)
graph export "output/fig_eventstudy.png", replace as(png) width(2000)
```

矢量图和点阵图都要导出：PDF 用于论文，PNG 用于幻灯片。不要依赖自动生成的 `.gph`，因为它不能跨 Stata 版本移植。

## 9. 常见的 Stata → R / Stata → AEA 陷阱

| 陷阱 | 修法 |
|---|---|
| `reg y x, cluster(id)` 没有显式自由度调整 | 使用 `reghdfe` 并明确自由度调整；在表注中说明调整方法 |
| Bootstrap 次数在多次运行间不一致 | 在文件顶部设置 `set seed` + `set sortseed`；使用 `bootstrap, reps(N) seed(X)` |
| `replace` 改动观测数据 | 一律先写 `gen new_var = ... `，检查后再 `drop` |
| `merge 1:1` 没有 `assert` | 使用 `merge 1:1 id using foo, assert(3)`，键不匹配时立即报错 |
| 在缺失值上写 `if` | Stata 在不等式比较中把 `.` 当作 `+∞`。要表达「非缺失且大于 5」，就写 `if x > 5 & x < .`，以排除 `.` 与 `.a`–`.z` |
| `egen sum(x)` 已过时 | 现在使用 `egen total(x)`；`egen sum()` 仍可用，但 `bysort id: egen y = total(x)` 更稳妥 |

## 10. AEA Data Editor 合规

[AEA Data Editor 清单](https://aeadataeditor.github.io/)要求：

- 在仓库根目录提供 `README.md`，说明数据来源、计算要求和运行方法。
- 用一条命令复现全部结果：`do scripts/stata/99_run_all.do`。
- 为所有脚本编号并排序。
- 提供一份与 `requirements.txt` 等价的文件。对 Stata 而言，就是 §3 的 `sessionInfo_stata.txt`，再加上 `00_install.do` 中的 `ssc install` 命令清单。
- 提供许可证，例如 MIT / GPL 或类似许可证。
- 不得硬编码路径。使用全局量，或相对于仓库根目录的相对路径。

## 执行

- [`/stata-replication`](../skills/stata-replication/SKILL.md) 是与 `/data-analysis` 对应的 Stata 技能，生成的 .do 文件符合本规范。
- [`/audit-reproducibility`](../skills/audit-reproducibility/SKILL.md) 除处理 R 的 `.rds` 外，也通过 `haven` 或 `pyreadstat` 处理 Stata 的 `.dta` 输出。
- [`/review-r`](../skills/review-r/SKILL.md) 只审读 R 代码；目前还没有 Stata 代码审读技能。

## 交叉引用

- [`r-code-conventions.md`](r-code-conventions.md) — 适用于 R 优先流水线的同类要求。
- [`replication-protocol.md`](replication-protocol.md) — 适用于 R / Stata / Python 的容差约定。
- [`../references/release-engineering.md`](../references/release-engineering.md) — 将 `.ado` 包或复现包发布为带版本的产物：普查 message 与 silent-resolution、归档 preflight、约定生成的 status，以及固定下游版本。
- [stata-mcp on GitHub](https://github.com/SepineTam/stata-mcp) — 让 WorkBuddy 执行 Stata `.do` 文件的 MCP 服务器。安装方法见 [`stata-replication`](../skills/stata-replication/SKILL.md) 的前置条件：依次进入插件页、MCP 服务器、配置 MCP，或把它写入用户级 `~/.workbuddy/mcp.json`。本平台没有与上游 `claude mcp add --scope user` 对应的命令。
