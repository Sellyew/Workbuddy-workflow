# 会话日志

**位置：** `quality_reports/session_logs/YYYY-MM-DD_description.md`
**模板：** `templates/session-log.md`

## 三个触发点（全部主动执行）

### 1. 计划后日志

计划获批后，立即记下：目标、方法、理由、关键上下文。

### 2. 增量记录

每当做出一个设计决策、解决一个问题、用户纠正了某处、或方法发生变化时，追加 1-3 行。不要攒批。

### 3. 会话结束日志

收尾时：高层摘要、质量评分、未决问题、阻塞项。

## 质量报告

**只在合并时**生成——不是每次提交或 PR 都生成。
保存到 `quality_reports/merges/YYYY-MM-DD_[branch-name].md`，使用 `templates/quality-report.md`。
