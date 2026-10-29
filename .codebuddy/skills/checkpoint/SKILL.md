---
name: checkpoint
description: 在停下或交接之前保存一份结构化状态快照。把当前生效的计划、近期决策、文件指针（带行号）、未决问题，以及接下来的 1–3 个动作，写进 `quality_reports/checkpoints/` 下的检查点文件。可选地提议若干条 `[LEARN]` 条目加入 MEMORY.md。当用户说 "checkpoint"、"save state"、"snapshot before I stop"、"where am I"、"wrap up the session for handoff"，或在长时间休息 / 切换模型 / 与协作者交接之前使用。它是叙事式会话日志工作流的伴侣（不是替代）。
description_zh: 在停下或交接之前保存一份结构化状态快照。把当前生效的计划、近期决策、文件指针（带行号）、未决问题，以及接下来的 1–3 个动作，写进 `quality_reports/checkpoints/` 下的检查点文件。可选地提议若干条 `[LEARN]` 条目加入 MEMORY.md。当用户说 "checkpoint"、"save state"、"snapshot before I stop"、"where am I"、"wrap up the session for handoff"，或在长时间休息 / 切换模型 / 与协作者交接之前使用。它是叙事式会话日志工作流的伴侣（不是替代）。
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

产出一份状态快照，让下一次会话（你自己的、协作者的，或全新上下文的冷启动）能在一分钟内接着干。叙事式的 `quality_reports/session_logs/` 依旧单独存在 —— `/checkpoint` 写的是*结构化*那一侧：事实、文件指针、下一步动作。

## 何时使用

- 长时间休息之前、切换模型（Opus ↔ Sonnet ↔ Haiku）之前，或一个工作日结束时。
- 在自动压缩即将丢弃中途计划上下文之前（配合 PreCompact 钩子使用）。
- 把同一仓库的工作交接给协作者之前。
- 多会话计划中完成一块之后，即下一次会话开口第一个问题就是「我干到哪了」的时候。

## 何时不要使用

- 要记录叙事性的*发生了什么* —— 那属于 `quality_reports/session_logs/`（见 `.codebuddy/rules/session-logging.md`）。
- 要写提交信息 —— 那些走 `/commit`，它会自己写结构化的提交正文。
- 要记录关于备选方案的决策 —— 那些经 `quality_reports/decisions/` 写入 `templates/decision-record.md`。

三类产物互补：**session-log = 叙事**，**decision-record = 记录下的取舍**，**checkpoint = 可供续接的状态**。

## 工作流

### PHASE 1 —— 收集状态

按这个顺序读：

1. **最新计划** —— `ls -t quality_reports/plans/*.md | head -1`。提取：状态（DRAFT / APPROVED / COMPLETED）、标题、顶层待改文件清单，以及任何以 "Open questions" / "Risks" / "Next" 开头的行。
2. **最新会话日志** —— `ls -t quality_reports/session_logs/*.md | head -1`。提取：最近一次 "Next steps" 或 "Blockers" 行。
3. **根目录 MEMORY.md** —— 读盘上已有的 `[LEARN]` 条目表，免得你提议重复的条目。
4. **Git 状态** —— `git log --oneline -20`、`git status -s`、`git branch --show-current`。记录：当前分支、最近 5 条主题、未提交文件数。
5. **工作文件** —— `git diff --stat HEAD` 看本次会话改了哪些文件（若分支是刚切的，跳过；直说「本次会话无改动」）。
6. **活跃 TODO** —— 若本次会话里还有一份 TodoWrite 清单在跑，记录进行中与下一待办项。
7. **进行中的后台工作** —— 本次会话启动过、但*没有*等它完成的任何东西：一个长时计算作业、一个定时例行任务（`.codebuddy/references/scheduled-routines.md`）、一次排队中的渲染或编译、一次还在审稿人或另一个模型手上的外部评审。每一项都要记四件事：在跑什么、产物落在哪、用什么命令查它、什么结论算它结束。

以上任何一项读取失败（文件不存在），就记 "(none on disk)"，不要编造内容。

**漏掉一个正在跑的作业，就等于把它变成孤儿。** 下一次会话看不到这项工作的任何痕迹，产物落进一个没人盯的目录，作业要么被从头重启，要么被半途悄悄放弃 —— 两者都很贵，两者都不可见。

### PHASE 2 —— 写检查点

**只写本次会话确证过的东西。** 下一次会话会自动收到这个文件（[`session-handoff.py`](../../hooks/session-handoff.py)），所以这里编出来的任何内容，到那边都会被当成事实。

- 只有本次会话读过的行才写 `path:line`；否则只给路径。
- 没内容的段落就省略，不要填满 —— 但 **In flight** 例外，它永远出现，没有作业在跑时写 "(none)"。安静的会话得到一份短文件，也不提议 `[LEARN]`。
- `[Session handoff: …]` 或 `[Context Restored After Compaction]` 块里的文字是上一份记录。只有当本次会话重新核查过或据此行动过，才把某项往前带；否则按路径引用更早的那个文件。
- 会话改了主意时，最终决策就是当前那一个；早先的立场只作为「已放弃」出现，并附上原因。

写入 `quality_reports/checkpoints/YYYY-MM-DD_$ARGUMENTS.md`（slug 取自 `$ARGUMENTS`；若无参数，从当前计划的标题派生，并提醒用户）。文件用这个模板：

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

把文件控制在约 80 行以内。若状态大到装不下，正确去处是计划文件（不是检查点）；检查点只是指向计划的薄索引。

### PHASE 3 —— 提议记忆更新（若带 `--no-memory` 则跳过）

列出本次会话产生的 0–3 条候选 `[LEARN]` 条目。**未经用户批准不要写入 MEMORY.md** —— 这一步是「先提议、后应用」：

每条候选都这样呈现：

```
[LEARN:category] proposed: <one-line headline>
Why: <one sentence on what makes this non-obvious>
Apply where: <which future situations would benefit>
```

如果用户说 "yes" / "all" / "1 and 3" —— 按 `[LEARN]` 格式追加到 MEMORY.md（根目录那份，受版本管理的那份）。若候选是机器专属的（路径、工具版本、个人偏好），交给原生自动记忆持有（机器本地，见 `.codebuddy/rules/meta-governance.md`）。

候选保持在 3 条以下。若超过 3 条，多半是本次会话的叙述不够 —— 指出这一点，并建议改为更新会话日志。

### PHASE 4 —— 输出摘要

打印到对话：

```
✓ Checkpoint saved: quality_reports/checkpoints/YYYY-MM-DD_<slug>.md
  Branch: <branch>     Status: <in_progress|paused|ready-to-merge>
  Active plan: <path or none>     Open questions: <count>
  Resume: 下一次在同一个目录里新建任务时，会话交接钩子会把这份检查点递过去一次
          （7 天内有效，除非期间又写了更新的检查点或 /compress-session 注记）。
          若你是接着旧任务继续聊而不是新建任务，钩子不会递送 —— 直接让 WorkBuddy
          读这个文件，或粘贴它的 "Resume prompt"。
```

如果提议过记忆候选，说明用户接受了哪几条（若有）。

## 交叉引用

- `.codebuddy/rules/session-logging.md` —— 叙事侧伴侣。**不要重复** —— 检查点按路径引用最新会话日志，它不复述会话故事。
- `.codebuddy/rules/plan-first-workflow.md` —— 检查点读当前计划；若无计划，建议用户先进入计划模式再调用 `/checkpoint`。
- `templates/decision-record.md` —— 用于*为什么选 A 不选 B*，不用于*我们在哪*。
- `.codebuddy/references/scheduled-routines.md` —— 活过会话生命周期的例行任务；那边在跑的东西都属于「In flight」栏。
- `.codebuddy/hooks/pre-compact.py` —— 设了 `CLAUDE_PRECOMPACT_BLOCK_ON_DRAFT=1` 时，PreCompact 钩子会为每份 DRAFT 计划阻断一次压缩。那个阻断触发时，该跑的就是 `/checkpoint`。

## 示例

### 示例 1 —— 日终交接
**用户说：** "checkpoint v180-polisci"
**动作：**
1. 读 `quality_reports/plans/2026-04-27_v180-polisci-apr2026.md`（当前生效，DRAFT）。
2. 读 `quality_reports/session_logs/2026-04-27_v180-polisci-apr2026.md`。
3. 记录：分支 `feat/v1.8.0-polisci-apr2026`，领先 main 4 个提交，改动 8 个文件。
4. 写 `quality_reports/checkpoints/2026-04-27_v180-polisci.md`，文件指针指向写了一半的 `methods-referee.md` 和尚未开工的 `journal-profiles.md` 政治学板块。
5. 提议 1 条 `[LEARN:scope]` 候选条目，关于学科广度的线性成本。
**结果：** 下一次会话：新建一个任务 —— 交接钩子会把 `quality_reports/checkpoints/2026-04-27_v180-polisci.md` 交给它 —— 然后从动作 1 开始。

### 示例 2 —— 中途切换模型
**用户说：** "I want to switch to Sonnet for the cheap doc edits — checkpoint first"
**动作：**
1. 收集状态。
2. 写检查点，`status: paused`。
3. 跳过记忆提议（改动很小 —— 只是换模型继续）。
**结果：** 状态已在盘上；Sonnet 会话读检查点后继续，无需重新加载整份计划。

## 疑难排查

**找不到当前计划。** `/checkpoint` 仍会写一份薄检查点，`plan: (none)`，但正确做法通常是先进入计划模式 —— 没有计划引用做依托的检查点是弱的。

**缺话题 slug。** 若 `$ARGUMENTS` 为空，从当前计划文件名派生（去掉日期前缀）。若两者都没有，向用户索要一个，不要编造。

**输出太长。** 先精简「Recent decisions」和「Open questions」。计划该进计划文件；检查点应当能一屏放下。
