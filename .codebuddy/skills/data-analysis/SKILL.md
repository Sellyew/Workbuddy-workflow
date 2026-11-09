---
name: data-analysis
description: 运行端到端 R 数据分析：探索、清洗、回归，并生成可用于发表的表格和图形。用户说 "analyze this dataset"、"run a regression on X"、"explore this CSV"、"full analysis workflow"、"get me summary stats and a regression"、"分析这个数据集"、"跑一个回归" 或 "探索这个 CSV"，或指向 `.csv`/`.rds`/`.dta` 文件并索要实证结果时使用。在 `scripts/R/` 下生成带编号的 R 脚本，输出写入 `output/`。
description_zh: 运行端到端 R 数据分析：探索、清洗、回归，并生成可用于发表的表格和图形。用户说 "analyze this dataset"、"run a regression on X"、"explore this CSV"、"full analysis workflow"、"get me summary stats and a regression"、"分析这个数据集"、"跑一个回归" 或 "探索这个 CSV"，或指向 `.csv`/`.rds`/`.dta` 文件并索要实证结果时使用。在 `scripts/R/` 下生成带编号的 R 脚本，输出写入 `output/`。
argument-hint: "[dataset path or description of analysis goal]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task", "TaskOutput"]
---

# 数据分析工作流

用 R 完成从加载、探索到分析的完整流程，并生成可用于发表的输出。

**输入：** `$ARGUMENTS`，可以是数据集路径（例如 `data/county_panel.csv`），也可以是分析目标（例如 "regress wages on education with state fixed effects using CPS data"）。

---

## 约束

- **遵循 R 代码约定**，见 `.codebuddy/rules/r-code-conventions.md`
- **把所有脚本保存到** `scripts/R/`，文件名要能说明用途
- **把所有输出**（图、表、RDS）保存到 `output/`
- **用 `saveRDS()` 保存每个计算对象**，供 Quarto 幻灯片后续使用
- **所有图都使用项目主题**，自定义主题见 `.codebuddy/rules/`
- **报告结果前，先让 r-reviewer 审查生成的脚本**

---

## 工作流阶段

### Phase 0：开始前检查报告

**编写任何分析代码前，先输出开始前检查报告（Pre-Flight Report），证明你已经读取输入。** 这一步可以避免代理编造变量名或忽略项目约定。

在给用户的回复中输出以下块，位置必须在 Phase 1 之前：

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

如果任何输入无法读取，例如文件缺失或格式不可读，先停下来询问用户，不要继续。

### Phase 1：环境与数据加载

1. 创建 R 脚本，在头部写明标题、作者、用途、输入和输出
2. 在顶部加载所需包，使用 `library()`，绝不用 `require()`
3. 按 `r-code-conventions.md` 在顶部设置一次种子，日期采用 YYYYMMDD 格式，例如 `set.seed(20260415)`（INV-9）
4. 加载并检查数据集

### Phase 2：探索性数据分析

生成以下诊断输出：

- **汇总统计：** `summary()`、缺失率、变量类型
- **分布：** 关键连续变量的直方图
- **关系：** 散点图、相关矩阵
- **时间模式：** 如果是面板数据，画出随时间变化的趋势
- **组间比较：** 如果有处理组和对照组，比较处理前均值

把所有诊断图保存到 `output/diagnostics/`。

### Phase 3：主分析

主分析必须遵循研究设计、带日期的现行 owner 签核和已批准实现。估计器、标准误与聚类方式、控制变量集合与设定顺序、效应量及报告方式均来自这些材料，本技能不自行选择或推荐。

开始每项估计前，记录研究设计出处、签核日期与已批准实现。任一依据缺失时，留下 `CLARIFY: [缺失的研究设计、现行签核或已批准实现]`，暂停相应估计并向用户澄清；不得用默认估计器、聚类方式或控制变量顺序补齐。其他不依赖该决定的已批准步骤仍可继续。

#### 设定台账——每一次估计，无论保留与否

本阶段每估计一个设定，无论后来保留、弃用还是失败，都要在运行时向 `quality_reports/spec-ledger.md` 追加一行。这样审稿人问「你还试过什么」时，就有完整记录可查。台账让搜索过程可见，但不阻止搜索，也不建议应该运行哪个设定。

- **只追加。** 绝不编辑或删除已有行；需要更正时新增一行。如果一次提交改动了已经提交的行，仓库卫生门禁会拒绝该提交。
- **Status** 取 `kept`、`dropped` 或 `failed`；**Why** 说明未保留任何项的原因。
- **Estimate** 可以留空。使用受限数据时，先留空这一格，直到数字通过披露审查（[`confidential-data.md`](../../rules/confidential-data.md)）。
- 公式中的 `|` 要转义成 `\|`，否则表格会断。含反引号的设定（例如 Stata 局部宏 `` `x' ``）要放进双反引号跨度里：``` `` reg y `controls' `` ```。

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
| scripts/R/03_analyze.R:42 | [outcome] | [approved specification] | [approved sample] | kept | [reason from research design] | [estimate after disclosure review] |
EOF
```

### Phase 4：可发表的输出

**表格：**

- 回归表用 `modelsummary`（首选）或 `stargazer`
- 表格内容、效应量以及标准误、区间、显著性等报告方式，均由研究设计、带日期的现行 owner 签核和已批准实现决定；不得自行添加显著性星号
- 导出 `.tex` 供 LaTeX 引用，同时导出 `.html` 便于快速查看

**图形：**

- 用 `ggplot2` 加项目主题
- 为兼容 Beamer，设 `bg = "transparent"`
- 坐标轴标签要规范，句首大写并带单位
- 导出时写明尺寸：`ggsave(width = X, height = Y)`
- 同时保存 `.pdf` 和 `.png`

### Phase 5：实际运行、保存与复核

1. 脚本必须对所有关键对象使用 `saveRDS()`，包括回归结果、汇总表和处理后的数据，并按需用 `dir.create(..., recursive = TRUE)` 创建 `output/` 子目录。
2. **保存结果与委派复核之前，必须通过 Bash 实际运行** `Rscript scripts/R/[script_name].R` 并记录完整日志和退出码。不得只读代码、做语法检查或声称已经运行。
3. **失败即停止：** 只有退出码为 0 才继续。逐个检查脚本声明的预期输出文件存在且非空（例如 `test -s output/analysis/[file]`）；再用实际 `Rscript -e` 调用 `readRDS()` 读取每个关键 RDS，并检查预期类型/维度。任一运行、文件或读取检查失败，都停止后续复核与结果报告，向用户给出日志和失败检查，不得把产物当作有效结果。
4. 上述检查全部通过后，才让 r-reviewer 代理审查生成的脚本：

```
Delegate to the r-reviewer agent:
"Review the script at scripts/R/[script_name].R"
```

5. 处理复核中任何 Critical 或 High 级别的问题。每次修改脚本后，都必须重新执行第 2–3 步的实际 `Rscript` 运行与产物检查，再重新复核。

---

## 脚本结构

按这个模板编写：

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
library(modelsummary)
# [仅加载研究设计、现行签核和已批准实现要求的其他包]

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

- **复现，不要猜。** 用户指定了某个回归，就原样运行那个回归。
- **展示分析过程。** 进入回归前，先打印汇总统计。
- **检查问题。** 留意多重共线性、离群值和完全预测。
- **使用相对路径。** 所有路径都相对于仓库根目录。
- **不要硬编码。** 样本限制、日期范围等都用变量表示。

## 长时间拟合：后台 Bash + TaskOutput

回归、模拟或自助法循环如果需要运行几分钟以上，用 Bash 以 `run_in_background: true` 启动，再用 **TaskOutput** 获取状态和输出。操作如下：

1. 用 Bash 的 `run_in_background: true` 在后台启动，并把全部输出写入日志：`mkdir -p output && Rscript scripts/R/03_analyze.R > output/03_analyze.log 2>&1`。记录 Bash 返回的 `task_id`；进程退出时，后台任务会自动通知你。
2. 用该 `task_id` 调用 TaskOutput。需要等待完成时使用 `block: true`；只需查看当前状态时使用 `block: false`。完成后读取完整日志，并仍按 Phase 5 检查退出码、预期文件非空和关键对象可读。
3. 根据实际任务输出决定继续运行还是调整方向；不要用 `sleep` 轮询循环，也不要另设日志监视进程。

这样既不需要反复空等，也不会丢失最终退出状态。它与指南的 [Cost-Conscious Parallelism](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#cost-conscious-parallelism) 一节配合使用时尤其有用。
