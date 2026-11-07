---
name: context-status
description: 显示当前上下文状态与会话健康状况。用于查看上下文用量/检查会话状态，判断自动压缩是否临近，以及哪些状态已被确认保留。
description_zh: 显示当前上下文状态与会话健康状况。用于查看上下文用量/检查会话状态，判断自动压缩是否临近，以及哪些状态已被确认保留。
allowed-tools: ["Read", "Bash", "Glob"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# /context-status —— 检查会话健康状况

本技能汇总当前会话状态，包括上下文用量估计、生效中的计划和保留下来的状态。

**只读诊断：**本技能只读取状态，不修改任何文件。

## 本技能显示什么

1. **上下文用量估计**：上下文窗口大约已使用多少
2. **在用计划**：当前计划文件及其状态
3. **会话日志**：最近的会话日志
4. **保留状态**：哪些内容能在压缩后继续保留

## 工作流

### 第 1 步：查看上下文估计值

上下文监视钩子把估计值写入本项目会话目录下的 `context-pct.txt`，并把计数器与阈值旗标写入 `context-monitor-cache.json`：

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

实际读取并确认 PreCompact 钩子与压缩后恢复配置是否存在，不能仅凭文档或命令名称推断。只有两者都确认存在时，才能输出「已配置压缩前保存与压缩后恢复；执行是否成功仍需实际核验」；组件存在只说明已配置保存／恢复，不代表执行必然成功。任一缺失或无法确认时，必须明确输出「Session state preservation is NOT guaranteed」，并指出未确认的组件。

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

Preservation Check
  • Pre-compact hook: [confirmed present | missing/unconfirmed]
  • Post-compact restore: [confirmed present | missing/unconfirmed]
  • Session state: [已配置保存/恢复；执行是否成功仍需实际核验 | preservation is NOT guaranteed]
```

## 说明

- 上下文百分比取自 WorkBuddy 自己的 `context_window.used_percentage`（状态行显示它的地方）。钩子的 `context-pct.txt` 保存的是按转录文本大小估算的值，必要时退化为工具调用次数计数。内建的 `/context` 显示精确用量
- WorkBuddy 自动触发实际压缩
- 计划、日志和 MEMORY.md 等文件若已实际存在，会保存在磁盘上；这不证明 PreCompact 与恢复机制会保存当前会话状态，必须按第 4 步分别确认
