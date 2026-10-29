---
name: review-r
description: 针对 `.R` 脚本的只读 R 代码审读协议。检查代码质量、可复现性、领域正确性、tidyverse 惯用法与专业标准；产出一份报告，不改动文件。用户说 "review this R script"、"check the R code"、"audit the analysis code"、"code review on the R" 时使用，或在论文投稿过程中改动了某个 R 文件时使用。不负责运行代码——数值核验请与 `/audit-reproducibility` 搭配。
description_zh: 针对 `.R` 脚本的只读 R 代码审读协议。检查代码质量、可复现性、领域正确性、tidyverse 惯用法与专业标准；产出一份报告，不改动文件。用户说 "review this R script"、"check the R code"、"audit the analysis code"、"code review on the R" 时使用，或在论文投稿过程中改动了某个 R 文件时使用。不负责运行代码——数值核验请与 `/audit-reproducibility` 搭配。
argument-hint: "[filename or 'all' or 'LectureN']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# 审 R 脚本

跑这套完整的 R 代码审读协议。

## 步骤

1. **确定要审的脚本：**
   - 若 `$ARGUMENTS` 是具体的 `.R` 文件名：只审那个文件
   - 若 `$ARGUMENTS` 是 `LectureN`：审与该讲匹配的所有 R 脚本
   - 若 `$ARGUMENTS` 是 `all`：审 `scripts/R/` 与 `Figures/*/` 里的所有 R 脚本

2. **对每个脚本启动 `r-reviewer` 代理**，指示它：
   - 遵循代理说明里的完整协议
   - 读 `.codebuddy/rules/r-code-conventions.md` 了解当前标准
   - 把报告作为最终响应返回（以 findings 的 `json` 块结尾）；本技能把它保存到 `quality_reports/[script_name]_r_review.md`——代理是只读的

3. **所有审读完成之后**，呈报一份摘要：
   - 每个脚本发现的问题总数
   - 按严重度分解（Critical / High / Medium / Low）
   - 最要紧的 3 个问题

4. **不改动 R 源文件**——报告交给用户，由用户决定改什么。
   只产出报告。修改在用户审阅之后才施加。
