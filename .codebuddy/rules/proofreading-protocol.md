---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
  - "quality_reports/**"
---

# 校对代理协议（强制）

**每一个讲义文件在任何提交或 PR 之前都必须经过审读。**

**CRITICAL 规则：代理绝不可直接施加改动。它先把所有改动提出来供审读。**

## 代理检查什么

1. **语法** -- 主谓一致、缺冠词、介词错误
2. **错字** -- 拼写错误、查找替换造成的损坏、重复词
3. **溢出** -- overfull hbox（Beamer）、内容超出幻灯片边界（Quarto）
4. **一致性** -- 记号、引用风格（`\citet` 与 `\citep`、`[@key]`）、术语
5. **学术质量** -- 非正式缩写、漏词、别扭的措辞

## 三阶段工作流

### Phase 1：审读并提议（不做任何编辑）

每个代理：
1. 读完整的文件
2. 产出一份**报告**，包含每一处建议改动：
   - 位置（行号或幻灯片标题）
   - 现有文字
   - 建议修改
   - 类别（grammar / typo / overflow / consistency）
3. 把报告作为最终响应返回；`/proofread` 技能把它保存到 `quality_reports/`（例如 `quality_reports/LectureN_Topic_report.md`，若源文件是 `.qmd` 则为 `quality_reports/LectureN_Topic_qmd_report.md`）
4. **不修改任何源文件**

### Phase 2：审读并批准

用户审读提议的改动：
- 全部接受、有选择地接受，或要求修改
- **只有在明确批准之后**，代理才继续

### Phase 3：施加修复

只施加已批准的改动：
- 用 Edit 工具；对有多处实例的问题用 `replace_all: true`
- 核验每一处编辑都成功
- 报告完成摘要
