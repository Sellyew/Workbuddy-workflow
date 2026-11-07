---
name: checkpoint
description: 在停下或交接前保存结构化状态快照，把当前生效计划、近期决策、带行号的文件指针、未决问题和接下来 1–3 个动作写入 `quality_reports/checkpoints/`。可选地提议若干条 `[LEARN]` 条目加入 MEMORY.md。用户说 "checkpoint"、"save state"、"snapshot before I stop"、"where am I"、"wrap up the session for handoff"、"保存检查点"、"记录当前状态" 或 "交接前快照"，或在长时间休息／切换模型／与协作者交接前使用。它补充叙事式会话日志，不替代会话日志。
description_zh: 在停下或交接前保存结构化状态快照，把当前生效计划、近期决策、带行号的文件指针、未决问题和接下来 1–3 个动作写入 `quality_reports/checkpoints/`。可选地提议若干条 `[LEARN]` 条目加入 MEMORY.md。用户说 "checkpoint"、"save state"、"snapshot before I stop"、"where am I"、"wrap up the session for handoff"、"保存检查点"、"记录当前状态" 或 "交接前快照"，或在长时间休息／切换模型／与协作者交接前使用。它补充叙事式会话日志，不替代会话日志。
argument-hint: "[short-topic-slug] [--no-memory]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Bash"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

<!-- 本模式改编自 Hugo Sant'Anna 的 clo-author v4.2.0（github.com/hugosantanna/clo-author），
     经许可使用。原 /checkpoint 的形态：项目级会话交接，含状态快照 + 记忆更新。
     本实现按本模板的叙事式会话日志 + 计划落盘 + 自动记忆架构，
     以原创文字重写。署名：Hugo Sant'Anna。 -->

# /checkpoint —— 结构化会话交接

本技能生成状态快照，让下一次会话在一分钟内继续工作，无论是你自己的后续会话、协作者会话，还是全新上下文的冷启动。`quality_reports/session_logs/` 仍负责叙事记录；`/checkpoint` 只保存*结构化*信息：事实、文件指针和下一步动作。

## 何时使用

- 长时间休息、切换模型档位（default ↔ lite ↔ reasoning）或结束一个工作日之前。
- 自动压缩即将丢失中途计划上下文之前，可配合 PreCompact 钩子使用。
- 把同一仓库的工作交接给协作者之前。
- 完成多会话计划中的一块工作后，避免下一次会话先问「我干到哪了」。

## 何时不要使用

- 需要叙事性记录*发生了什么*时，写入 `quality_reports/session_logs/`，见 `.codebuddy/rules/session-logging.md`。
- 需要提交信息时，使用 `/commit`，它会生成结构化提交正文。
- 需要记录备选方案之间的取舍时，依据 `templates/decision-record.md` 写入 `quality_reports/decisions/`。

三类产物各自承担不同任务：**session-log = 叙事**，**decision-record = 记录下的取舍**，**checkpoint = 可供续接的状态**。

## 工作流

### PHASE 1 —— 收集状态

按此顺序读取：

1. **最新计划**：`ls -t quality_reports/plans/*.md | head -1`。提取状态（DRAFT / APPROVED / COMPLETED）、标题、顶层待改文件清单，以及任何以 "Open questions" / "Risks" / "Next" 开头的行。
2. **最新会话日志**：`ls -t quality_reports/session_logs/*.md | head -1`。提取最近的 "Next steps" 或 "Blockers" 行。
3. **根目录 MEMORY.md**：读取磁盘上已有的 `[LEARN]` 条目，避免提出重复候选。
4. **Git 状态**：`git log --oneline -20`、`git status -s`、`git branch --show-current`。记录当前分支、最近 5 条主题和未提交文件数。
5. **工作文件**：无论分支何时创建，都运行 `git status --short` 与 `git diff HEAD`，按实际输出记录未提交改动；可用 `git diff --stat HEAD` 汇总文件。只有两者实际都为空时才写「无未提交改动」，分支年龄不构成跳过检查或判定无改动的依据。
6. **活跃 TODO**：若本次会话仍有 TodoWrite 清单在运行，记录进行中的事项和下一待办项。
7. **进行中的后台工作**：记录本次会话启动但*没有*等待完成的所有工作，包括长时计算作业、定时例行任务（`.codebuddy/references/scheduled-routines.md`）、排队中的渲染或编译，以及仍在审稿人或另一个模型手中的外部评审。每项都写清四件事：在跑什么、产物落在哪、用什么命令查询、什么结论表示结束。

任何一项因文件不存在等原因读取失败，都记为 "(none on disk)"，不得编造。

**漏记正在运行的作业，会让它变成孤儿。**下一次会话将看不到这项工作，产物也会落入无人查看的目录。作业可能被从头重启，也可能在中途被悄悄放弃；两种结果代价都很高，而且难以察觉。

### PHASE 2 —— 写检查点

**只写本次会话已经确证的内容。**下一次会话会通过 [`session-handoff.py`](../../hooks/session-handoff.py) 自动收到这个文件，因此这里的任何编造都会被当作事实。

- 只有本次会话实际读过的行才写 `path:line`，否则只写路径。
- 没有内容的段落直接省略，不要为了填满模板而补字；**In flight** 除外，它必须始终出现，没有作业时写 "(none)"。安静的会话应生成短文件，也不必提议 `[LEARN]`。
- `[Session handoff: …]` 或 `[Context Restored After Compaction]` 块中的文字属于上一份记录。只有本次会话重新核查或据此行动过，才能继续带入；否则按路径引用更早的文件。
- 若会话中改变过决定，只把最终决定写成当前决定。早先立场仅在需要时标为「已放弃」，并附原因。

先从 `$ARGUMENTS` 剥离 `--no-memory` 等已识别旗标，再把剩余参数规范化并拼接为 `checkpoint_slug`，绝不能把原始参数串直接用作文件名。写入 `quality_reports/checkpoints/YYYY-MM-DD_<checkpoint_slug>.md`。若剥离旗标后 slug 为空，从当前计划标题派生并提醒用户；无法派生时按疑难排查处理。文件使用以下模板：

```markdown
---
date: YYYY-MM-DD
branch: [current-branch]
plan: [path to active plan, or "(none)"]
session-log: [path to most recent session log, or "(none)"]
status: in_progress | paused | ready-to-merge
---

# Checkpoint — [short topic]

## Goal (one sentence)
[What this work is trying to accomplish]

## Where I am (one paragraph)
[Last completed step, current step, what's just-not-yet-done. Bullet points OK.]

## File pointers
[Concrete references to where the next session should resume — up to 8. `path:line` only for lines read in this session; otherwise the path alone.]
- `.codebuddy/skills/checkpoint/SKILL.md:42` — body draft, needs trigger-phrase tightening
- `quality_reports/plans/[slug].md:135` — verification section to refresh after impl
- `CHANGELOG.md` — Unreleased section, v1.8.0 entry not yet drafted

## In flight
[Jobs still running that this session did not wait for. One row each; write "(none)" if nothing is running — an empty section reads as an oversight.]

| What is running | Artifacts land in | Check with | Ends when |
|---|---|---|---|
| overnight parameter sweep | `output/sweep/` | `ls output/sweep \| wc -l` | 500 result files, no `errors.log` |
| external referee consult | `quality_reports/oracle_audits/2026-04-27_lemma3/` | `oracle session lemma3-r1 --render` | transcript archived + adjudicated |

## Recent decisions
[2–5 bullet points of *why* we did what we did this session. Things that wouldn't be obvious from the diff. Skip if none — do not pad.]

## Open questions
[Specific things you'd ask if someone else picked this up. Mark each as Q1, Q2 …]

## Next 1–3 actions
[Imperative form. Concrete. The next session opens this file and starts here.]
1. [...]
2. [...]
3. [...]

## Resume prompt
> Resuming from checkpoint `quality_reports/checkpoints/[filename]`. Read it, then continue with action 1.
```

文件控制在约 80 行以内。若状态超过这个篇幅，就把详细内容写入计划文件；检查点只作为指向计划的薄索引。

### PHASE 3 —— 提议记忆更新（若带 `--no-memory` 则跳过）

列出本次会话产生的 0–3 条候选 `[LEARN]` 条目。**未经用户批准，不要写入 MEMORY.md。**本阶段必须先提议，再按选择应用。

每条候选按以下格式呈现：

```
[LEARN:category] proposed: <one-line headline>
Why: <one sentence on what makes this non-obvious>
Apply where: <which future situations would benefit>
```

若用户回答 "yes" / "all" / "1 and 3"，就按 `[LEARN]` 格式追加到根目录、受版本管理的 MEMORY.md。若候选只适用于某台机器，例如路径、工具版本或个人偏好，就交给原生自动记忆保存，详见 `.codebuddy/rules/meta-governance.md`。

候选不得超过 3 条。若超过 3 条，通常说明本次会话更需要叙事记录；应指出这一点，并建议改为更新会话日志。

### PHASE 4 —— 输出摘要

在对话中打印：

```
✓ Checkpoint saved: quality_reports/checkpoints/YYYY-MM-DD_<slug>.md
  Branch: <branch>     Status: <in_progress|paused|ready-to-merge>
  Active plan: <path or none>     Open questions: <count>
  Resume: 下一次在同一个目录里新建任务时，会话交接钩子会把这份检查点递过去一次
          （7 天内有效，除非期间又写了更新的检查点或 /compress-session 注记）。
          若你是接着旧任务继续聊而不是新建任务，钩子不会递送 —— 直接让 WorkBuddy
          读这个文件，或粘贴它的 "Resume prompt"。
```

若提议过记忆候选，还要说明用户接受了哪些条目。

## 交叉引用

- `.codebuddy/rules/session-logging.md` —— 叙事侧伴侣。检查点只按路径引用最新会话日志，**不要重复**讲述会话过程。
- `.codebuddy/rules/plan-first-workflow.md` —— 检查点读取当前计划；若没有计划，建议用户先进入计划模式，再调用 `/checkpoint`。
- `templates/decision-record.md` —— 记录*为什么选 A 不选 B*，不记录*我们在哪*。
- `.codebuddy/references/scheduled-routines.md` —— 生命周期超过当前会话的例行任务；仍在运行的任务都列入「In flight」。
- `.codebuddy/hooks/pre-compact.py` —— 设置 `CLAUDE_PRECOMPACT_BLOCK_ON_DRAFT=1` 时，PreCompact 钩子会针对每份 DRAFT 计划阻断一次压缩。触发阻断后，应运行 `/checkpoint`。

## 示例

### 示例 1 —— 日终交接
**用户说：** "checkpoint v180-polisci"
**动作：**
1. 读取 `quality_reports/plans/2026-04-27_v180-polisci-apr2026.md`（当前生效，DRAFT）。
2. 读取 `quality_reports/session_logs/2026-04-27_v180-polisci-apr2026.md`。
3. 记录分支 `feat/v1.8.0-polisci-apr2026`，领先 main 4 个提交，改动 8 个文件。
4. 写入 `quality_reports/checkpoints/2026-04-27_v180-polisci.md`，文件指针指向写了一半的 `methods-referee.md` 和尚未开工的 `journal-profiles.md` 政治学板块。
5. 提议 1 条 `[LEARN:scope]` 候选条目，说明学科广度的线性成本。
**结果：**下一次会话新建任务后，交接钩子把 `quality_reports/checkpoints/2026-04-27_v180-polisci.md` 交给它，然后从动作 1 开始。

### 示例 2 —— 中途切换模型
**用户说：** "I want to switch to lite for the cheap doc edits — checkpoint first"
**动作：**
1. 收集状态。
2. 写检查点，设置 `status: paused`。
3. 跳过记忆提议，因为改动很小，只是换模型继续。
**结果：**状态已经保存到磁盘；lite 会话读取检查点后继续，不必重新加载整份计划。

## 疑难排查

**找不到当前计划。**`/checkpoint` 仍会写一份薄检查点，设置 `plan: (none)`。但通常应先进入计划模式，因为没有计划引用的检查点能提供的续接信息有限。

**缺话题 slug。**若从 `$ARGUMENTS` 剥离 `--no-memory` 等旗标后没有剩余参数，或规范化后的 `checkpoint_slug` 为空，从当前计划文件名派生并去掉日期前缀。若两者都没有，向用户索要，不得编造。

**输出太长。**先精简「Recent decisions」和「Open questions」。详细计划应放入计划文件，检查点应能在一屏内读完。
