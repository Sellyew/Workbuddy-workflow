---
name: proofread
description: 对讲稿 `.tex` 或 `.qmd` 文件做一遍只读校对。检查语法、错字、溢出、术语一致性，以及学术写作质量；产出一份报告，不改动文件。用户说 "proofread"、"check for typos"、"look for grammar issues"、"copy-edit this"、"any writing errors?" 时使用，或在一讲发布之前使用。
description_zh: 对讲稿 `.tex` 或 `.qmd` 文件做一遍只读校对。检查语法、错字、溢出、术语一致性，以及学术写作质量；产出一份报告，不改动文件。用户说 "proofread"、"check for typos"、"look for grammar issues"、"copy-edit this"、"any writing errors?" 时使用，或在一讲发布之前使用。
argument-hint: "[filename or 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
---

# 校对讲稿文件

按校对协议检查讲稿，报告发现的所有问题，**不**修改任何源文件。

## 步骤

1. **确定检查范围：**
   - 如果 `$ARGUMENTS` 是具体文件名，只检查该文件。
   - 如果 `$ARGUMENTS` 是 "all"，检查 `Slides/` 与 `Quarto/` 中的所有讲稿文件。

2. **为每个文件启动 proofreader 代理**，检查以下五类问题：

   **语法：**主谓和时态是否一致，冠词与介词使用是否正确。
   **错字：**拼写错误、查找替换留下的残留文字、重复用词。
   **溢出：**overfull hbox（LaTeX）、内容超出幻灯片边界（Quarto）。
   **一致性：**引文格式、记号和术语是否统一。
   **学术质量：**是否有口语化表达、漏词或拗口句式。

3. **生成详细报告**，按文件列出每条发现，并写明：
   - 位置（行号或幻灯片标题）
   - 当前文字（问题所在）
   - 建议改法（应改成什么）
   - 类别与严重度

4. **将每份报告保存**到 `quality_reports/`：
   - `.tex` 文件保存为 `quality_reports/FILENAME_report.md`。
   - `.qmd` 文件保存为 `quality_reports/FILENAME_qmd_report.md`。

5. **不要修改源文件。** 本技能只生成报告；用户审阅报告后，再另行修改。

6. **向用户汇报摘要：**
   - 每个文件的问题总数。
   - 各类别的问题数量。
   - 最需要优先处理的问题。
