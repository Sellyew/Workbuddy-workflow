---
name: compress-session
description: 在自动压缩前，把当前对话提炼成结构化笔记，记录已经作出的决定、未决问题、带行号的文件指针和接下来的 1–3 个动作，并保存到 `quality_reports/session_logs/`。它不同于 `/checkpoint` 的显式停止点快照；本技能的价值是提供可审阅的结构化交接，并已与下文所述 PreCompact 提醒机制配对。上下文接近自动压缩阈值、长流程积累了大量决定，或用户说 "compress"、"distil this session"、"before we hit auto-compact"、"structured handoff before context resets"、"压缩会话"、"提炼这次对话" 或 "压缩前做一次交接" 时使用。
description_zh: 在自动压缩前，把当前对话提炼成结构化笔记，记录已经作出的决定、未决问题、带行号的文件指针和接下来的 1–3 个动作，并保存到 `quality_reports/session_logs/`。它不同于 `/checkpoint` 的显式停止点快照；本技能的价值是提供可审阅的结构化交接，并已与下文所述 PreCompact 提醒机制配对。上下文接近自动压缩阈值、长流程积累了大量决定，或用户说 "compress"、"distil this session"、"before we hit auto-compact"、"structured handoff before context resets"、"压缩会话"、"提炼这次对话" 或 "压缩前做一次交接" 时使用。
argument-hint: "[optional-topic-slug]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/compress-session` —— 蒸馏并结构化交接

`/compress-session` 生成一份可审阅的结构化笔记，明确记录当前决定、文件指针、未决问题和后续动作，让下一次会话不必依赖对原始对话的记忆。已核实的自动化配合点是下文的可选 PreCompact 钩子：它能在自动压缩前提醒用户运行本技能；自动压缩自身的内部保留策略不在本技能中作未经验证的断言。

## 本技能为何存在

Drew Breunig 在 ["How Long Contexts Fail"](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) 中指出，长上下文会话有四种失败模式：

1. **Poisoning**：后续轮次引用早期幻觉，放大错误。
2. **Distraction**：无关的早期上下文分散模型对当前任务的注意力。
3. **Confusion**：相互矛盾的事实不断累积，模型无法判断该相信哪一个。
4. **Clash**：多份计划、决定或需求说明同时存在，却没有明确协调。

本模板用 200 行的 `MEMORY.md` 上限防止 *distraction*，用计划落盘防止 *clash*。此前没有机制直接处理 *poisoning* 和 *confusion*，本技能补上了这一环。

## 与 `/checkpoint` 的区别

| | `/checkpoint` | `/compress-session` |
|---|---|---|
| **何时** | 显式的停止点（工作日结束、切换模型之前、与协作者交接之前） | 上下文即将自动压缩，或对话已经积累足够多的噪音，值得提炼时 |
| **保留什么** | 当前生效的计划、决定、文件指针、接下来的 1–3 个动作 | 同上，另加一行「作为噪音丢弃」，明确告诉下一次会话哪些内容被有意省略 |
| **输出位置** | `quality_reports/checkpoints/YYYY-MM-DD_<slug>.md` | `quality_reports/session_logs/YYYY-MM-DD_compression_<slug>.md` |
| **触发方式** | 用户在自然停顿处调用 | 用户在上下文疲劳显现时调用，或由下面可选的 PreCompact 提醒钩子提示（默认未接线） |
| **记忆更新** | 可选地自动提议 `[LEARN]` 条目 | 提议 0–3 条 `[LEARN]` 条目。提炼时容易发现可推广的经验；内容简单的会话可以不提议 |

两个技能都配合 `quality_reports/session_logs/` 下的叙事式会话日志使用，互不替代。

## 何时使用

- **上下文接近自动压缩。** `/context-status` 报告接近阈值。
- **长流程积累了噪音。** 例如花了 90 分钟调试一个错字，会话中留下许多不希望带入下一次会话的错误假设。
- **计划执行到一半需要交接。** 包括更换模型、机器或协作者。
- **PreCompact 提醒已触发。** 如果配置了下面的提醒钩子，它会提示你运行 `/compress-session`；技能本身不会自动运行。

## 何时不要使用

- **只记录一个快速停止点。** 用 `/checkpoint`。
- **撰写叙事式会话日志。** Stop 钩子会增量完成这项工作（[session-logging.md](../../rules/session-logging.md)），无需调用技能。
- **开始全新会话。** 用 `/clear`。`/compress-session` 用于保留状态，不用于重置状态。

## 步骤

### 步骤 1 —— 确认是哪个会话

当前对话才是信息来源。`quality_reports/session_logs/` 下最新的日志可能属于更早的会话，应把它当作上一份记录并按路径引用，不能当成本次会话的内容。

可以把 `$ARGUMENTS` 用作输出文件名中的话题 slug。

### 步骤 2 —— 蒸馏成结构化小节

**只写本次会话已经确认的内容。** 下一次会话会自动读取这个文件（[`session-handoff.py`](../../hooks/session-handoff.py)），这里编造的内容到时会变成事实。

- 只有本次会话实际读过的内容才写 `path:line`；否则只给路径。
- 没有内容的小节直接省略，不要为填满模板而编写内容。内容简单的会话可以只生成短文件，也不必提出 `[LEARN]`。
- `[Session handoff: …]` 或 `[Context Restored After Compaction]` 块中的文字属于上一份记录。只有本次会话重新核查过或据此采取过行动，才继续保留相关事项；否则按路径引用更早的文件。
- 如果会话中改变过决定，只把最终决定列为当前决定；早先立场标为「已放弃」并说明原因。

生成一份包含以下小节的笔记：

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

写入 `quality_reports/session_logs/YYYY-MM-DD_compression_<topic>.md`，slug 取自 `$ARGUMENTS` 或当前计划名。

### 步骤 4 —— 给出摘要

向用户报告：

- 保存路径。
- 各项数量：作出的决定、改动的文件、未决问题和接下来的动作。
- 任何需要用户在下一次会话前审阅的 HIGH 影响 LEARN 提案。

由用户审阅，不会自动并入 MEMORY.md。用户批准后，再按用户指示把提案追加到 MEMORY.md，方式与 `/checkpoint` 的 PHASE 3 相同；机器专属条目留在原生自动记忆中。`/promote-memory` 不读取这个文件，它的候选只来自原生自动记忆（`~/.workbuddy/projects/<project>/memory/`）。

## 与 PreCompact 钩子配对

如果 fork 本仓库的人希望在压缩前有机会运行 `/compress-session`，可以添加一个 PreCompact 钩子，让每个会话**阻断一次压缩**。PreCompact 触发时，退出码 2 会阻断压缩并显示钩子的 stderr 消息；第二次尝试会放行，因此压缩不会一直被卡住。这与 `pre-compact.py` 可选的 DRAFT 阻断采用同一种「只一次」模式。普通的 `exit 0` 提醒要等到压缩已经运行时才到达，那时已经无法采取行动。

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

钩子只负责暂停和提醒。用户运行 `/compress-session` 后再次压缩。我们有意不让钩子自动调用技能，因为那会绕过用户审阅。

## 反模式

- **不要把 `/compress-session` 当作 `/checkpoint` 的日常替代品。** 检查点成本低、可以频繁使用；压缩更重，应留给必须压缩的场景。
- **不要让「作为噪音丢弃」一节无限增长。** 如果同一个死胡同连续三次出现在压缩记录中，说明文档或工作流存在结构问题，应当修正，而不是反复丢弃同一内容。
- **不要收录完整的原始对话。** 那会违背提炼信息的目的。

## 输出

- 压缩文件位于 `quality_reports/session_logs/YYYY-MM-DD_compression_<topic>.md`（已 gitignore，会话状态不纳入版本管理）。
- 对话摘要包含各项计数和 HIGH 影响的 `[LEARN]` 提案。
- 除压缩文件外，不改动其他文件。
