---
name: compress-session
description: 在自动压缩之前，把当前对话蒸馏成一份结构化笔记（已做的决策、未决问题、带行号的文件指针、接下来的 1–3 个动作），保存到 `quality_reports/session_logs/`。它与 `/checkpoint`（显式的停止点快照）不同，也与自动压缩（截断而非蒸馏）不同。当上下文接近自动压缩阈值、一条长流水线已经累积了很多决策，或用户说 "compress"、"distil this session"、"before we hit auto-compact"、"structured handoff before context resets" 时使用。
description_zh: 在自动压缩之前，把当前对话蒸馏成一份结构化笔记（已做的决策、未决问题、带行号的文件指针、接下来的 1–3 个动作），保存到 `quality_reports/session_logs/`。它与 `/checkpoint`（显式的停止点快照）不同，也与自动压缩（截断而非蒸馏）不同。当上下文接近自动压缩阈值、一条长流水线已经累积了很多决策，或用户说 "compress"、"distil this session"、"before we hit auto-compact"、"structured handoff before context resets" 时使用。
argument-hint: "[optional-topic-slug]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/compress-session` —— 蒸馏，不要截断

自动压缩是**有损的**：它保留近期的轮次、丢掉更早的，而且完全不保留会话中途*决定了什么*。`/compress-session` 是**蒸馏而非截断**的替代方案 —— 产出一份结构化笔记，让下一次会话能在一分钟内接着干。

## 本技能为何存在

Drew Breunig 的 ["How Long Contexts Fail"](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) 指出了长上下文会话的四种失败模式：

1. **Poisoning** —— 早期幻觉出来的内容被后面的轮次引用，错误被放大。
2. **Distraction** —— 无关的早期上下文稀释了模型对当前任务的注意力。
3. **Confusion** —— 相互矛盾的事实堆起来；模型不知道该信哪个。
4. **Clash** —— 多份计划、决策或规格累积起来，却没有被显式地调和。

本模板 200 行的 `MEMORY.md` 上限防的是 *distraction*。计划落盘的约定防的是 *clash*。目前没有任何东西防 *poisoning*，也没有任何东西直接对付 *confusion* —— 这就是本技能的用途。

## 与 `/checkpoint` 的区别

| | `/checkpoint` | `/compress-session` |
|---|---|---|
| **何时** | 显式的停止点（工作日结束、切换模型之前、与协作者交接之前） | 被迫 —— 上下文即将自动压缩，或者对话已经积累了足够多的噪音，蒸馏划得来 |
| **保留什么** | 生效中的计划、决策、文件指针、接下来的 1–3 个动作 | 同上，另加一行明示的「作为噪音丢弃」，好让下一次会话知道什么被*有意*没有保留 |
| **输出位置** | `quality_reports/checkpoints/YYYY-MM-DD_<slug>.md` | `quality_reports/session_logs/YYYY-MM-DD_compression_<slug>.md` |
| **触发方式** | 用户在自然的停顿处调用 | 用户在上下文疲劳显现时调用，或由下面可选的 PreCompact 提醒钩子提示（默认未接线） |
| **记忆更新** | 可选地自动提议 `[LEARN]` 条目 | 提议 0–3 条 `[LEARN]` 条目 —— 蒸馏正是可推广的经验浮出的时候，而一个安静的会话什么也不提议 |

两个技能都是 `quality_reports/session_logs/` 下叙事式会话日志工作流的伴侣。没有谁替代谁。

## 何时使用

- **上下文接近自动压缩。** `/context-status` 报告接近阈值。
- **一条长流水线已经积累了噪音。** 你花了 90 分钟调试一个其实只是错字的问题 —— 会话里全是你不想被压缩进下一次会话上下文的死胡同假设。
- **计划中途交接。** 换模型、换机器、换协作者。
- **PreCompact 提醒触发了。** 如果你接上了下面的提醒钩子，它会提示你跑 `/compress-session`；该技能从不自动运行。

## 何时不要使用

- **为了一个快速的停止点。** 用 `/checkpoint`。
- **为叙事式会话日志。** 那由 Stop 钩子增量完成（[session-logging.md](../../rules/session-logging.md)）；不需要技能。
- **为了开一个全新会话。** 用 `/clear`。`/compress-session` 是为了保住状态，不是为重置。

## 步骤

### 步骤 1 —— 确认是哪个会话

当前对话就是来源。`quality_reports/session_logs/` 下最新的日志可能属于更早的一次会话：把它当作上一份记录，按路径引用它，而不是当作本次会话的内容。

可选地把 `$ARGUMENTS` 用作输出文件名的话题 slug。

### 步骤 2 —— 蒸馏成结构化小节

**只写本次会话确立的东西。** 下一次会话会自动收到这个文件（[`session-handoff.py`](../../hooks/session-handoff.py)），所以这里编出来的任何内容到那边都会变成事实。

- 只有本次会话读过的行才写 `path:line`；否则只给路径。
- 没内容的小节就省略，不要填满。一个安静的会话得到一份短文件，也没有 `[LEARN]` 提案。
- `[Session handoff: …]` 或 `[Context Restored After Compaction]` 块里的文字是上一份记录。只有当本次会话重新核查过或据此行动过，才把某项往前带；否则按路径引用更早的文件。
- 会话改了主意时，最终的决策就是当前那一个；早先的立场只作为「已放弃」出现，并附上原因。

产出一份含这些小节的笔记：

```markdown
# Session Compression — <YYYY-MM-DD> <topic-slug>

**Source:** <session-log file or "current conversation">
**Token budget at compression:** <approximate %>
**Why compress now:** <approaching auto-compact | mid-plan handoff | accumulated noise | user-requested>

## Active state

- **Plan:** [link to active plan in `quality_reports/plans/` or "no active plan"]
- **Branch:** <git branch>
- **Last commit:** <SHA + subject>
- **Working tree:** <clean | N modified files>

## Decisions made (this session)

1. [Decision]. **Why:** [one sentence]. **Where recorded:** [file:line, plan, or memory].
2. ...

## Files touched

- [path:line] — [what changed, one sentence]
- ...

## Open questions

- [Question]. **Blocker?** [Yes/No]. **Where to resume:** [pointer].
- ...

## Next actions (1–3 only)

1. [Specific next step with file pointer]
2. ...

## Discarded as noise

Things explored during this session that should NOT carry forward — failed hypotheses, abandoned approaches, debugging dead-ends. Listing them explicitly defends against [Breunig's "poisoning" failure mode](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) (hallucinated / wrong content from early turns getting quoted later).

- [Hypothesis / approach / dead-end] — [why it didn't work]
- ...

## Proposed `[LEARN]` entries

Lessons worth promoting to MEMORY.md (machine-specific ones stay in native auto memory). User reviews; nothing auto-merged.

- `[LEARN:<category>]` <lesson>. **Evidence:** <pointer>.
- ...
```

### 步骤 3 —— 保存

写到 `quality_reports/session_logs/YYYY-MM-DD_compression_<topic>.md`（slug 取自 `$ARGUMENTS` 或当前计划名）。

### 步骤 4 —— 给出摘要

向用户报告：

- 保存路径。
- 计数（做出的决策、改动的文件、未决问题、接下来的动作）。
- 任何应当在下一次会话之前先审阅的 HIGH 影响 LEARN 提案。

用户审阅。什么都不自动并入 MEMORY.md：用户批准的提案按用户的指示追加进 MEMORY.md（与 `/checkpoint` 的 PHASE 3 一样），而机器专属的那条留给原生自动记忆。`/promote-memory` 不读这个文件；它的候选只来自原生自动记忆（`~/.workbuddy/projects/<project>/memory/`）。

## 与 PreCompact 钩子配对

想要在压缩之前真正有机会跑 `/compress-session` 的 fork 者，可以加一个 PreCompact 钩子，**每个会话阻断一次压缩**。在 PreCompact 时，退出码 2 会阻断并显示钩子的 stderr 消息；第二次尝试会放行，所以压缩永远不会被卡死 —— 与 `pre-compact.py` 可选开启的 DRAFT 阻断同一种「只一次」模式。（一个朴素的 `exit 0` 提醒会在压缩已在运行时才到达，来不及动作。）

```json
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "sid=$(python -c \"import sys,json; print(json.load(sys.stdin).get(\\\"session_id\\\",\\\"x\\\"))\" 2>/dev/null); f=\"${TMPDIR:-/tmp}/cc-compress-reminded-$sid\"; [ -e \"$f\" ] && exit 0; touch \"$f\"; echo \"Run /compress-session now, then compact again - this reminder blocks only once per session.\" >&2; exit 2",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

钩子只做暂停和提醒；用户跑 `/compress-session`，然后再次压缩。我们有意不让钩子*自动调用*该技能 —— 那会绕过用户的审阅环节。

## 反模式

- **不要把 `/compress-session` 当作 `/checkpoint` 的常规替代品。** 检查点便宜且频繁；压缩更重，留给被迫压缩时用。
- **不要让「作为噪音丢弃」这一节无限增长。** 如果同一个死胡同连续三次压缩都出现，底层的混乱是结构性的 —— 去修文档或工作流，不要一直重复丢弃。
- **不要包含原始完整对话** —— 那会毁掉目的。蒸馏才是重点。

## 输出

- 压缩文件位于 `quality_reports/session_logs/YYYY-MM-DD_compression_<topic>.md`（已 gitignore —— 会话状态，不纳入版本管理）。
- 对话里的摘要：计数 + HIGH 影响的 `[LEARN]` 提案。
- 压缩文件之外不做任何文件改动。
