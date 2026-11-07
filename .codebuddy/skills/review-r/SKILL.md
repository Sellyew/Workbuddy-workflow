---
name: review-r
description: 只读审读 `.R` 脚本，检查代码质量、可复现性、领域正确性、tidyverse 惯用法和专业标准，只写报告，不改文件。用户说 "review this R script"、"check the R code"、"audit the analysis code"、"code review on the R"、"审一下这段 R 代码"、"检查分析代码" 时使用；论文投稿过程中改动 R 文件后也使用。本技能不运行代码，数值核验请配合 `/audit-reproducibility`。
description_zh: 只读审读 `.R` 脚本，检查代码质量、可复现性、领域正确性、tidyverse 惯用法和专业标准，只写报告，不改文件。用户说 "review this R script"、"check the R code"、"audit the analysis code"、"code review on the R"、"审一下这段 R 代码"、"检查分析代码" 时使用；论文投稿过程中改动 R 文件后也使用。本技能不运行代码，数值核验请配合 `/audit-reproducibility`。
argument-hint: "[filename or 'all' or 'LectureN']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
---

# 审 R 脚本

按以下协议完整审读 R 代码。

## 步骤

1. **确定审读范围：**
   - `$ARGUMENTS` 是具体的 `.R` 文件名时，只审该文件。
   - `$ARGUMENTS` 是 `LectureN` 时，审与该讲匹配的所有 R 脚本。
   - `$ARGUMENTS` 是 `all` 时，审 `scripts/R/` 与 `Figures/*/` 里的所有 R 脚本。

2. **为每个脚本启动 `r-reviewer` 代理**，并要求它：
   - 按代理说明中的完整协议审读。
   - 阅读 `.codebuddy/rules/r-code-conventions.md`，以其中的现行标准为准。
   - 在最终响应中返回报告，末尾附 findings 的 `json` 块。代理只读，本技能负责把报告保存到 `quality_reports/[script_name]_r_review.md`。

3. **等所有审读结束后**，汇总报告：
   - 每个脚本发现的问题总数。
   - 按严重度分类的数量（Critical / High / Medium / Low）。
   - 最需要优先处理的 3 个问题。

4. **不要改动 R 源文件。** 只把报告交给用户，由用户决定修改内容；经用户审阅后，才能实施修改。
