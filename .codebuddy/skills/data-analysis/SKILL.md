---
name: data-analysis
description: 端到端 R 数据分析流水线——探索 → 清洗 → 回归 → 可发表的表格与图形。当用户说 "analyze this dataset"、"run a regression on X"、"explore this CSV"、"full analysis workflow"、"get me summary stats and a regression"，或指向某个 `.csv`/`.rds`/`.dta` 并索要实证结果时使用。在 `scripts/R/` 下生成带编号的 R 脚本，输出写入 `output/`。
description_zh: 端到端 R 数据分析流水线——探索 → 清洗 → 回归 → 可发表的表格与图形。当用户说 "analyze this dataset"、"run a regression on X"、"explore this CSV"、"full analysis workflow"、"get me summary stats and a regression"，或指向某个 `.csv`/`.rds`/`.dta` 并索要实证结果时使用。在 `scripts/R/` 下生成带编号的 R 脚本，输出写入 `output/`。
argument-hint: "[dataset path or description of analysis goal]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task", "Monitor"]
---

# 数据分析工作流

在 R 中跑完端到端的数据分析：加载、探索、分析，并产出可发表的输出。

**输入：** `$ARGUMENTS` —— 一个数据集路径（例如 `data/county_panel.csv`），或对分析目标的描述（例如 "regress wages on education with state fixed effects using CPS data"）。

---

## 约束

- **遵循 R 代码约定**，见 `.codebuddy/rules/r-code-conventions.md`
- **把所有脚本保存到** `scripts/R/`，文件名要有描述性
- **把所有输出**（图、表、RDS）保存到 `output/`
- **每个计算出的对象都用 `saveRDS()` 保存** —— Quarto 幻灯片可能会用到它们
- **所有图都用项目主题**（在 `.codebuddy/rules/` 里查自定义主题）
- **在报出结果之前，对生成的脚本跑 r-reviewer**

---

## 工作流阶段

### Phase 0：起飞前检查报告

**在写任何分析代码之前，先产出一份起飞前检查报告（Pre-Flight Report），表明你读过输入。** 这能避免常见的失败模式：代理编造变量名，或跳过项目约定。

输出块（写在给用户的回复里，位于 Phase 1 之前）：

```markdown
## Pre-Flight Report

**Dataset:** [path]
- Variables found: [list from head()/names()]
- Rows: [count]
- Key types: [e.g., "outcome=numeric, treatment=binary, state=factor"]
- Missing-data summary: [% missing per key var]

**Project conventions read:**
- `.codebuddy/rules/r-code-conventions.md` — [one-line summary of most relevant rule]
- `.codebuddy/rules/content-invariants.md` — [INV-9, INV-10, INV-11, INV-12 applicable]

**Task interpretation:** [one sentence restating what the user asked for]

**Plan:** [3-5 bullet outline of the R script structure]
```

如果任一输入读不出来（文件缺失、格式不可读），先停下问用户，再继续。

### Phase 1：环境与数据加载

1. 创建 R 脚本，写好头部（标题、作者、用途、输入、输出）
2. 在顶部加载所需包（用 `library()`，绝不用 `require()`）
3. 在顶部一次性设定种子，用 YYYYMMDD 格式（按 `r-code-conventions.md`），例如 `set.seed(20260415)`（INV-9）
4. 加载并检查数据集

### Phase 2：探索性数据分析

生成诊断输出：
- **汇总统计：** `summary()`、缺失率、变量类型
- **分布：** 关键连续变量的直方图
- **关系：** 散点图、相关矩阵
- **时间模式：** 若为面板数据，画出随时间变化的趋势
- **组间比较：** 若有处理组/对照组，比较处理前的均值

把所有诊断图保存到 `output/diagnostics/`。

### Phase 3：主分析

根据研究问题：
- **回归分析：** 面板数据用 `fixest`，横截面用 `lm`/`glm`
- **标准误：** 在合适层级聚类（并记录为什么这样聚）
- **多组设定：** 从简单开始，逐步加入控制变量
- **效应量：** 除原始系数外，同时报告标准化效应

#### 设定台账——每一次估计，无论保留与否

本阶段估计的每一个设定，包括被弃用的和失败的，都在运行时向 `quality_reports/spec-ledger.md` 追加一行。这正是审稿人那句「你还试过什么？」所应得到的记录：它让搜索过程可见，而不是阻止搜索；它只记录设定，不建议该跑哪一个。

- **只追加。** 绝不编辑或删除已有行；更正就是新增一行。改动已提交行的提交会过不了仓库卫生门禁。
- **Status** 取 `kept`、`dropped` 或 `failed`；**Why** 说明任何未保留项的原因。
- **Estimate** 可留空。在受限数据上，先把该格留空，直到数字通过披露审查（[`confidential-data.md`](../../rules/confidential-data.md)）。
- 公式里的 `|` 要转义成 `\|`，否则表格会断。含反引号的设定（例如 Stata 局部宏 `` `x' ``）要放进双反引号跨度里：``` `` reg y `controls' `` ```。

```bash
LEDGER=quality_reports/spec-ledger.md
[ -f "$LEDGER" ] || printf '%s\n' "# Specification ledger" "" \
  "Every specification estimated, kept or not, one row each, appended as it is run. Never edit a past row; a correction is a new row." "" \
  "| Date | Commit | Script:line | Outcome | Specification | Sample | Status | Why | Estimate |" \
  "|---|---|---|---|---|---|---|---|---|" > "$LEDGER"
if REV=$(git rev-parse --short HEAD 2>/dev/null); then       # -dirty = anything uncommitted outside quality_reports/, untracked files included
  [ -n "$(git status --porcelain -- . ':(exclude)quality_reports' 2>/dev/null)" ] && REV="$REV-dirty"
else
  REV="no-commit"
fi
printf '| %s | %s ' "$(date +%F)" "$REV" >> "$LEDGER"          # one printf + one heredoc per specification
cat >> "$LEDGER" <<'EOF'
| scripts/R/03_analyze.R:42 | log_wage | `feols(log_wage ~ treat + age \| id + year, cluster = ~id)` | panel 2010-2019 | kept | main specification | 0.082 (0.021) |
EOF
```

### Phase 4：可发表的输出

**表格：**
- 回归表用 `modelsummary`（首选）或 `stargazer`
- 包含全部标准要素：系数、标准误、显著性星号、N、R 方
- 导出 `.tex` 供 LaTeX 引用，同时导出 `.html` 便于快速查看

**图形：**
- 用 `ggplot2` 加项目主题
- 为兼容 Beamer，设 `bg = "transparent"`
- 坐标轴标签要规范（句首大写、带单位）
- 导出时写明尺寸：`ggsave(width = X, height = Y)`
- 同时保存 `.pdf` 和 `.png`

### Phase 5：保存与复核

1. 对所有关键对象用 `saveRDS()`（回归结果、汇总表、处理后的数据）
2. 按需用 `dir.create(..., recursive = TRUE)` 创建 `output/` 子目录
3. 对生成的脚本跑 r-reviewer 代理：

```
Delegate to the r-reviewer agent:
"Review the script at scripts/R/[script_name].R"
```

4. 处理复核中任何 Critical 或 High 级别的问题。

---

## 脚本结构

按这个模板来：

```r
# ============================================================
# [Descriptive Title]
# Author: [from project context]
# Purpose: [What this script does]
# Inputs: [Data files]
# Outputs: [Figures, tables, RDS files]
# ============================================================

# 0. Setup ----
library(tidyverse)
library(fixest)
library(modelsummary)

set.seed(20260415)  # YYYYMMDD per r-code-conventions.md (INV-9)

dir.create("output/analysis", recursive = TRUE, showWarnings = FALSE)

# 1. Data Loading ----
# [Load and clean data]

# 2. Exploratory Analysis ----
# [Summary stats, diagnostic plots]

# 3. Main Analysis ----
# [Regressions, estimation]

# 4. Tables and Figures ----
# [Publication-ready output]

# 5. Export ----
# [saveRDS for all objects, ggsave for all figures]
```

---

## 要点

- **复现，不要猜。** 用户指定了某个回归，就原样跑那个回归。
- **把过程摊开。** 在跳到回归之前先打印汇总统计。
- **检查问题。** 留意多重共线性、离群值、完全预测。
- **用相对路径。** 所有路径相对于仓库根目录。
- **不写硬编码值。** 样本限制、日期范围等都用变量表示。

## 长时间拟合：使用 Monitor 工具（2026-04）

对于要跑几分钟以上的回归、模拟或自助法循环，用 Bash 以 `run_in_background: true` 启动，然后用 Anthropic 的 **Monitor 工具**把 R 的 stdout 实时流进对话。套路如下：

1. 用 Bash 的 `run_in_background: true` 后台启动，把所有输出送进日志：`mkdir -p output && Rscript scripts/R/03_analyze.R > output/03_analyze.log 2>&1`。进程退出时后台任务会自行通知你。
2. 启动 Monitor，命令跟踪该日志并过滤里程碑与失败，例如 `tail -f output/03_analyze.log | grep --line-buffered -E "Coefficients table written|Error|Execution halted"`。Monitor 没有 job-id 参数：它自己 `command` 的 stdout 就是事件流。`tail -f` 永不退出，所以把 `timeout_ms` 设得高于预期运行时长（或用 `persistent: true`），并在任务结束后用 TaskStop 停掉监视。
3. 依据流里露出的信息决定继续还是纠正方向。

这样既避免了轮询循环这一反模式（`sleep 30; check; sleep 30; check`），也避免把缓存耗在空等上。与指南的 [Cost-Conscious Parallelism](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#cost-conscious-parallelism) 一节配合使用时尤其有用。
