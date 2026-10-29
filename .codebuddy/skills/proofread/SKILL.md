---
name: proofread
description: 对讲稿 `.tex` 或 `.qmd` 文件做一遍只读校对。检查语法、错字、溢出、术语一致性，以及学术写作质量；产出一份报告，不改动文件。用户说 "proofread"、"check for typos"、"look for grammar issues"、"copy-edit this"、"any writing errors?" 时使用，或在一讲发布之前使用。
description_zh: 对讲稿 `.tex` 或 `.qmd` 文件做一遍只读校对。检查语法、错字、溢出、术语一致性，以及学术写作质量；产出一份报告，不改动文件。用户说 "proofread"、"check for typos"、"look for grammar issues"、"copy-edit this"、"any writing errors?" 时使用，或在一讲发布之前使用。
argument-hint: "[filename or 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# 校对讲稿文件

对讲稿文件跑校对协议。它产出一份列出所有问题的报告，**不**改动任何源文件。

## 步骤

1. **确定要审的文件：**
   - 若 `$ARGUMENTS` 是具体文件名：只审那个文件
   - 若 `$ARGUMENTS` 是 "all"：审 `Slides/` 与 `Quarto/` 里的所有讲稿文件

2. **对每个文件启动 proofreader 代理**，它检查：

   **语法：**主谓一致、冠词（a/an/the）、介词、时态一致
   **错字：**拼写错误、查找替换留下的残渣、重复的词
   **溢出：**overfull hbox（LaTeX）、内容超出幻灯片边界（Quarto）
   **一致性：**引文格式、记号、术语
   **学术质量：**口语化表达、漏词、别扭的句式

3. **产出详细报告**，逐文件列出每一条发现，含：
   - 位置（行号或幻灯片标题）
   - 当前文字（哪里不对）
   - 建议改法（应该是什么）
   - 类别与严重度

4. **把每份报告保存**到 `quality_reports/`：
   - 对 `.tex` 文件：`quality_reports/FILENAME_report.md`
   - 对 `.qmd` 文件：`quality_reports/FILENAME_qmd_report.md`

5. **不改动源文件**——修改在用户审阅报告之后才施加。
   只产出报告。修改在用户审阅之后另行施加。

6. **向用户呈报摘要：**
   - 每个文件发现的问题总数
   - 按类别的分解
   - 最要紧的问题高亮列出
