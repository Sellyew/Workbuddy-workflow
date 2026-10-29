---
name: pedagogy-review
description: 对一套讲稿幻灯片（`.qmd` 或 `.tex`）做整体教学法审读。检查叙事弧线、先修假设、例题、记号清晰度，以及整讲层面的节奏。用户说 "pedagogy review"、"does this teach well?"、"is the flow right?"、"will students follow?"、"review the narrative" 时使用，或在首次讲授一套幻灯片之前使用。只读；产出报告。
description_zh: 对一套讲稿幻灯片（`.qmd` 或 `.tex`）做整体教学法审读。检查叙事弧线、先修假设、例题、记号清晰度，以及整讲层面的节奏。用户说 "pedagogy review"、"does this teach well?"、"is the flow right?"、"will students follow?"、"review the narrative" 时使用，或在首次讲授一套幻灯片之前使用。只读；产出报告。
argument-hint: "[QMD or TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# 讲稿幻灯片的教学法审读

做一次全面的教学法审读。

## 步骤

1. **确定** `$ARGUMENTS` 指定的文件
   - 若没有参数，问用户要审哪一讲
   - 若只有一个名字，到 `Quarto/` 或 `Slides/` 里找

2. **用完整文件路径启动 pedagogy-reviewer 代理**
   - 该代理检查 13 条教学法模式
   - 做整讲层面的分析（叙事弧线、节奏、视觉韵律、记号）
   - 从学生视角考虑（先修要求、可能的反对意见）

3. **代理返回它的报告**（代理是只读的）；本技能把它保存到：
   `quality_reports/[FILENAME_WITHOUT_EXT]_pedagogy_report.md`

4. **向用户呈报摘要：**
   - 遵循与违反的模式各有哪些（共 13 条）
   - 整讲层面的评价
   - 最要紧的建议（前 3-5 条）

## 重要说明

- 这是**只读审读**——不改任何文件
- 关注**教学法**，不是视觉版式（那个用 `/visual-audit`）
- 要做合并审读，改用 `/slide-excellence`
