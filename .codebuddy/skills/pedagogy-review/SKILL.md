---
name: pedagogy-review
description: 对一套讲稿幻灯片（`.qmd` 或 `.tex`）做整体教学法审读。检查叙事弧线、先修假设、例题、记号清晰度，以及整讲层面的节奏。用户说 "pedagogy review"、"does this teach well?"、"is the flow right?"、"will students follow?"、"review the narrative"、"审一下教学法"、"学生能跟上吗"，或要求首次授课前审一遍幻灯片时使用。只审读并产出报告，不修改幻灯片。
description_zh: 对一套讲稿幻灯片（`.qmd` 或 `.tex`）做整体教学法审读。检查叙事弧线、先修假设、例题、记号清晰度，以及整讲层面的节奏。用户说 "pedagogy review"、"does this teach well?"、"is the flow right?"、"will students follow?"、"review the narrative"、"审一下教学法"、"学生能跟上吗"，或要求首次授课前审一遍幻灯片时使用。只审读并产出报告，不修改幻灯片。
argument-hint: "[QMD or TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
---

# 讲稿幻灯片的教学法审读

从整讲出发审读教学法，判断学生能否跟上叙事、理解记号并消化例题。

## 步骤

1. **确定** `$ARGUMENTS` 指定的文件
   - 若没有参数，问用户要审哪一讲
   - 若只有一个名字，到 `Quarto/` 或 `Slides/` 里找

2. **用完整文件路径启动 pedagogy-reviewer 代理**
   - 该代理检查 13 条教学法模式
   - 分析整讲的叙事弧线、节奏、视觉韵律与记号
   - 从学生视角检查先修要求和可能的疑问

3. **代理返回它的报告**（代理是只读的）；本技能把它保存到：
   `quality_reports/[FILENAME_WITHOUT_EXT]_pedagogy_report.md`

4. **向用户呈报摘要：**
   - 遵循与违反的模式各有哪些（共 13 条）
   - 整讲层面的评价
   - 最要紧的建议（前 3-5 条）

## 重要说明

- 本技能不修改幻灯片，只写审读报告
- 它关注**教学法**；视觉版式请用 `/visual-audit`
- 需要合并多个审查视角时，改用 `/slide-excellence`
