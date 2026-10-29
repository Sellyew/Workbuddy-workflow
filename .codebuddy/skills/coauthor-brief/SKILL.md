---
name: coauthor-brief
description: 为多作者、多机器的项目生成一份共同作者 / 协作者交接简报 —— 概述自上一份简报以来有哪些变化（git 增量）、各产物（稿件、分析、幻灯片）的当前状态、未决问题、如何在本地复现，以及任何受限数据的访问步骤。当用户说 "coauthor brief"、"handoff brief"、"bring my coauthor up to speed"、"what changed since last week"、"onboard a collaborator"、"write a handoff for [name]"，或在把仓库发给共同作者之前使用。它不是一次提交、也不是一个检查点 —— 它是 `meta-governance.md` 只部分覆盖的那种跨机器、跨人的摘要。
description_zh: 为多作者、多机器的项目生成一份共同作者 / 协作者交接简报 —— 概述自上一份简报以来有哪些变化（git 增量）、各产物（稿件、分析、幻灯片）的当前状态、未决问题、如何在本地复现，以及任何受限数据的访问步骤。当用户说 "coauthor brief"、"handoff brief"、"bring my coauthor up to speed"、"what changed since last week"、"onboard a collaborator"、"write a handoff for [name]"，或在把仓库发给共同作者之前使用。它不是一次提交、也不是一个检查点 —— 它是 `meta-governance.md` 只部分覆盖的那种跨机器、跨人的摘要。
argument-hint: "[--since <tag|date|Ndays>] [--for <collaborator-name>] [--no-data-section]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# /coauthor-brief —— 协作者交接简报

产出一份 Markdown 简报，让共同作者（或另一台机器上的未来的你）几分钟内就能读懂 **改了些什么、每个产物处于什么状态、什么被卡住、以及如何在本地跑通流水线** —— 包括新协作者需要的受限数据访问步骤。[`meta-governance.md`](../../rules/meta-governance.md) 覆盖跨机器工作的*记忆*一侧（什么通过 git 同步、什么留在被 gitignore 的原生自动记忆里）；本技能覆盖*人*的一侧：按人、按会话的交接。

**核心原则：** `/checkpoint` 是给*你自己*续接用的；`/coauthor-brief` 是给*别人*起步用的。前者回答「我干到哪了」；后者回答「我要接手其中一块，需要知道什么」。

## 何时使用

- **把仓库（或一个 PR / 分支）发给共同作者之前**，你想让他上手，而不是去考古 git 日志。
- **给新 RA / 协作者做入职**，他需要把本地复现与受限数据步骤集中在一处。
- **长期多作者项目的定期同步** —— 「这是自上一份简报以来的增量」。
- **跨机器交接** —— 在办公室台式机上收尾、在笔记本上接着做，或把分析那一半交给一位用 Stata 而你自己用 R 的共同作者。

## 何时不要使用

- 为了*你自己*的续接点 —— 用 [`/checkpoint`](../checkpoint/SKILL.md)。
- 为了在自动压缩之前蒸馏一段嘈杂的会话 —— 用 [`/compress-session`](../compress-session/SKILL.md)。
- 为了提交信息本身 —— 那走 [`/commit`](../commit/SKILL.md)。

## 各阶段

### Phase 0 —— 确定「自」哪个点起算

按此优先顺序解析增量窗口：

1. 若给了 `--since <arg>` —— 一个 git 标签、一个 ISO 日期，或 `Ndays`（例如 `--since v1.2`、`--since 2026-05-01`、`--since 14days`）。
2. 否则取**上一份简报** —— `ls -t quality_reports/handoffs/*.md | head -1`；用它文件名里的日期作为下限。
3. 否则回落到 **14 天**，并在简报里说明这一点（一条没有边界的 `git log` 是噪声，不是信号）。

收集之前先回显解析出的窗口（「Brief covers changes since `<tag/date>` …」）。

### Phase 1 —— 收集增量 + 项目状态

只读收集。不适用就跳过对应来源（纯 R、纯 Stata、没有幻灯片），而不是凭空编造。

1. **Git 增量** —— `git log --oneline --since=<point>`（或 `<tag>..HEAD`）、`git diff --stat <point>..HEAD`、`git branch --show-current`，以及 `git log --all --oneline -15` 看共同作者的并行分支。按领域给提交分组（稿件 / 分析 / 幻灯片 / 基础设施）。
2. **可复现性状态** —— 若 `quality_reports/passports/<slug>.yaml` 存在一份 passport，读出 PASS / FAIL / EXPLAINED / STALE / UNVERIFIED 汇总（[`audit-reproducibility`](../audit-reproducibility/SKILL.md)、[`replication-protocol.md`](../../rules/replication-protocol.md)）。记下这份分析是可复现就绪，还是仍有未决的 FAIL。
3. **未决的计划项** —— 最近的 `quality_reports/plans/*.md`（状态 + 任何「Open questions」/「Next」行）以及最新 `quality_reports/session_logs/*.md` 里的阻塞项。
4. **环境 / 锁文件** —— 定位协作者需要的环境快照：`renv.lock`（R）、`requirements.txt` / `environment.yml` / `uv.lock`（Python）、Stata 的 `version` 行 + `.do` 里的 `ssc install` 列表，或 [`/capture-environment`](../capture-environment/SKILL.md) 写下的任何东西。记录确切的还原命令。
5. **受限数据步骤** *（`--no-data-section` 时跳过）* —— 若仓库触及机密/受限数据，阅读 [`confidential-data.md`](../../rules/confidential-data.md)，概述新协作者需要的访问路径（DUA / IRB 批准、安全飞地或 openICPSR 受限凭据、数据存放在哪里、什么被 git 忽略、什么已提交）。**绝不把真实的受限数值、活动数据提取件的路径或凭据写进简报** —— 描述*获取访问的流程*，而不是数据。

### Phase 2 —— 写简报

用下面的模板。保持紧凑（约 1–2 屏）。具体的 `path:line` 指针胜过散文。

**给每一条状态陈述标注 `measured` 或 `inferred`。** *Measured* 指某条命令跑过、你报告的就是它的输出 —— **点名那条命令**。*Inferred* 指你是从读代码、读 diff 或某天早些时候的一次运行中相信它。两者都该出现在简报里；悄悄混在一起就不行，因为读者无法分辨哪些断言他可以不重查就据以行动。写 `replication-ready (measured: Rscript scripts/R/00_run_all.R — 0 FAIL)`，而不是 `replication-ready`。

**对被委派的工作逐项给出处置。** 凡交给共同作者、RA 或代理的东西，各自一行、各自一个状态 —— 完成（附证据）/ 进行中 / 受阻（卡在什么上）/ 未开始。*「基本做完了」* 不是一种处置：它把找出缺哪一块的活丢给读者，而那恰恰是简报存在的理由。

```markdown
---
date: YYYY-MM-DD
for: [collaborator name or "all coauthors"]
since: [tag | date | Ndays]
branch: [current branch]
---

# Co-Author Brief — [project / paper short name]

## What changed since [since-point]
[3–8 bullets, grouped by area. Each: what changed + why it matters to a reader, not raw commit subjects.]
- **Analysis:** re-ran the main specification on the de-duplicated sample (533 fanned-out rows dropped); headline estimate now −1.19 — see `scripts/R/03_analyze.R:147`.
- **Manuscript:** Table 2 + §4.2 rewritten to match; Figure 3 regenerated.
- **Slides:** untouched.

## Current state of each artifact
| Artifact | Path | State | Evidence (measured / inferred) |
|---|---|---|---|
| Manuscript | `manuscript.tex` | drafting §5 | inferred — §5 read, not compiled since the Table 2 rewrite |
| Analysis | `scripts/R/` | replication-ready | measured: `Rscript scripts/R/00_run_all.R`, passport 11 PASS / 1 EXPLAINED / 0 FAIL |
| Slides | `Slides/` | current | measured: `git log --since=<point> -- Slides/` returns nothing |

## Delegated work — one line per item
[Everything handed to a co-author, an RA, or an agent, dispositioned individually. No roll-ups.]
| Item | Owner | State | Evidence / blocker |
|---|---|---|---|
| Re-run Table 3 with the new sample filter | [name] | done | measured: output diff vs `output/tab3_prev.csv`, 2 cells moved |
| Appendix B proof of Lemma 2 | [name] | blocked | waiting on the boundedness condition in Q1 below |

## Open questions / decisions needed
[Things the co-author should weigh in on. Mark Q1, Q2…; flag which block progress.]

## Reproduce locally
1. Clone + branch: `git checkout <branch>`
2. Restore environment: `Rscript -e 'renv::restore()'` (or `pip install -r requirements.txt` / Stata `do scripts/stata/00_install.do`).
3. Run the pipeline: `Rscript scripts/R/00_run_all.R` (or Stata `do scripts/stata/99_run_all.do` / `make all`).
4. Verify: `/audit-reproducibility manuscript.tex` should report 0 FAIL.

## Restricted-data access (if applicable)
[Process to obtain access — DUA/IRB/enclave/openICPSR-restricted steps. NO actual data, paths to live extracts, or credentials. See confidential-data.md.]

## Recommended git topology for this project
- One **feature branch per author** (`feat/<author>-<topic>`); rebase on `main`, commit and open a PR with `/commit --pr`, and merge only when the co-authors agree.
- `MEMORY.md` is **committed** — generic learnings sync to everyone.
- Native auto memory (`~/.workbuddy/projects/<project>/memory/`) and `.codebuddy/state/` stay **local** — never expect a co-author to have yours (see meta-governance.md).
- Pull before you brief; brief before you hand off.
```

### Phase 3 —— 保存并小结

1. 写到 `quality_reports/handoffs/YYYY-MM-DD_coauthor-brief.md`（缺 `quality_reports/handoffs/` 则创建）。若设了 `--for`，给 slug 加后缀（`…_coauthor-brief_<name>.md`）。
2. 在对话里打印：保存路径、解析出的「自」窗口、计数（概述的提交数 / 未决问题数 / 产物数），以及数据章节是包含还是跳过。

## 输出 / 报告格式

一份符合 Phase 2 模板的 Markdown 交接文档，位于 `quality_reports/handoffs/YYYY-MM-DD_coauthor-brief.md`，外加一行对话小结。不改动任何其他文件。

## 退出行为

- **简报已写出：** 退出 0，给出保存路径与小结点。
- **「自」点无法解析且窗口内没有 git 历史：** 仍然写出简报，附一条显式的「no changes in window」说明，而不是失败 —— 从零起步的共同作者仍需要状态 + 复现 + 数据三个章节。
- **检出受限数据仓库但缺 `confidential-data.md`：** 写出简报，在数据章节留一个 `TODO: complete per your DUA` 占位符，并给出警告 —— **不要**猜访问流程。

## 参数

| 参数 | 作用 |
|---|---|
| `--since` | 取值为 `tag` / `date` / `Ndays` —— 用来做 diff 的基线：一个 git 标签、一个 ISO 日期，或 `Ndays`（例如 `14days`）。默认：`quality_reports/handoffs/` 里的上一份简报，否则 14 天（Phase 0）。 |
| `--for` | `<name>` —— 把简报裁剪给某位特定协作者（例如把他还需要的受限数据访问步骤浮出来）。 |
| `--no-data-section` | 跳过「Restricted-data access」章节（Phase 1 第 5 项）；适用于仓库不碰受限数据、或你不想把访问流程写进一份可能被邮件转发的文档时。 |

## 交叉引用

- [`.codebuddy/rules/meta-governance.md`](../../rules/meta-governance.md) —— 本简报为*人*落地的那套跨机器记忆模型（什么同步、什么留在本机）。
- [`.codebuddy/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) —— 产出「Reproduce locally」章节所指向的锁文件。
- [`.codebuddy/skills/checkpoint/SKILL.md`](../checkpoint/SKILL.md) —— *自我*续接的伴侣（本技能是*他人*交接）。
- [`.codebuddy/skills/compress-session/SKILL.md`](../compress-session/SKILL.md) —— 压缩之前蒸馏一段嘈杂的会话（正交；上下文臃肿时先跑它再做简报）。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 受限数据处理；数据章节概述它的访问步骤而不暴露数据。

## 本技能不做的事

- **推送、开 PR 或合并。** 它只写一份文档。建分支、提交与开 PR 是 [`/commit`](../commit/SKILL.md) 的活；合并由用户决定。
- **跑流水线或审计数字。** 它*报告* passport 状态（若有）；它不重跑分析、也不重新核验论断 —— 那是 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md)。
- **采集环境。** 它只定位并链接已有的锁文件；生成它们是 [`/capture-environment`](../capture-environment/SKILL.md)。
- **暴露受限数据。** 它只描述*访问流程* —— 绝不把机密数值、活动数据路径或凭据抄进一份可能被邮件发送或被提交的简报。
