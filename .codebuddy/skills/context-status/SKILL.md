---
name: context-status
description: 显示当前上下文状态与会话健康状况。用来查看已经用了多少上下文、自动压缩是否临近，以及哪些状态会被保留。
description_zh: 显示当前上下文状态与会话健康状况。用来查看已经用了多少上下文、自动压缩是否临近，以及哪些状态会被保留。
allowed-tools: ["Read", "Bash", "Glob"]
disallowed-tools: ["Edit", "MultiEdit"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# /context-status —— 检查会话健康状况

显示当前会话状态，含上下文用量估计、在用的计划与保留状态。

## 本技能显示什么

1. **上下文用量估计** —— 大致用掉了上下文窗口的百分之多少
2. **在用计划** —— 当前计划文件与状态
3. **会话日志** —— 最近的会话日志
4. **保留状态** —— 什么能熬过压缩

## 工作流

### 第 1 步：查看上下文估计值

上下文监视钩子把它的估计写进本项目会话目录下的 `context-pct.txt`（并把它的计数器与阈值旗标写进 `context-monitor-cache.json`）：

```bash
d=~/.workbuddy/sessions/$(printf '%s' "${CODEBUDDY_PROJECT_DIR:-$PWD}" | python -c 'import sys,hashlib;print(hashlib.md5(sys.stdin.read().encode()).hexdigest()[:8])')
cat "$d/context-pct.txt" 2>/dev/null; cat "$d/context-monitor-cache.json" 2>/dev/null | head -20
```

### 第 2 步：找在用计划

```bash
ls -lt quality_reports/plans/*.md 2>/dev/null | head -3
```

### 第 3 步：找会话日志

```bash
ls -lt quality_reports/session_logs/*.md 2>/dev/null | head -1
```

### 第 4 步：报告状态

按下面的格式输出：

```
📊 Session Status
─────────────────────────────────
Context Usage:  ~XX% (estimated)
Auto-compact:   [approaching | not imminent]

📋 Active Plan
File:   quality_reports/plans/YYYY-MM-DD_description.md
Status: [draft | approved | in_progress | completed]
Task:   [current unchecked task or "none"]

📝 Session Log
File:   quality_reports/session_logs/YYYY-MM-DD_description.md

✓ Preservation Check
  • Pre-compact hook: [configured | missing]
  • Post-compact restore: [configured | missing]
  • Session state will be saved before compaction
```

## 说明

- 上下文百分比取自 WorkBuddy 自己的 `context_window.used_percentage`（状态行显示它的地方）；钩子的 `context-pct.txt` 存的是按转录文本大小估出来的值（退化为工具调用次数计数）。内建的 `/context` 显示精确用量
- 实际的压缩由 WorkBuddy 自动触发
- 所有重要状态都落到磁盘（计划、日志、MEMORY.md）
