# 会话日志

**位置：** `quality_reports/session_logs/YYYY-MM-DD_description.md`
**模板：** `templates/session-log.md`

## 三个触发点（全部主动执行）

### 1. 计划后日志

计划一经批准，立即记录目标、方法、理由和关键上下文。

### 2. 增量记录

每作出一项设计决策、解决一个问题、收到一次用户纠正或改变一次方法，就追加 1-3 行，不要攒到最后补记。

### 3. 会话结束日志

收尾时，记录高层摘要、质量评分、未决问题和阻塞项。

## 质量报告

**只在合并时**生成质量报告，不要在每次提交或 PR 时生成。
保存到 `quality_reports/merges/YYYY-MM-DD_[branch-name].md`，使用 `templates/quality-report.md`。
