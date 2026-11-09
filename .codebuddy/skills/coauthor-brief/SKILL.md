---
name: coauthor-brief
description: 为多作者、多机器项目生成共同作者／协作者交接简报，说明自上一份简报以来的 git 增量、稿件／分析／幻灯片的当前状态、未决问题、本地复现方法，以及受限数据的访问步骤。用户说 "coauthor brief"、"handoff brief"、"bring my coauthor up to speed"、"what changed since last week"、"onboard a collaborator"、"write a handoff for [name]"、"共同作者简报"、"协作者交接"、"上周以来改了什么"，或在把仓库发给共同作者之前使用。它既不是提交，也不是检查点，而是 `meta-governance.md` 只部分覆盖的跨机器、跨人摘要。
description_zh: 为多作者、多机器项目生成共同作者／协作者交接简报，说明自上一份简报以来的 git 增量、稿件／分析／幻灯片的当前状态、未决问题、本地复现方法，以及受限数据的访问步骤。用户说 "coauthor brief"、"handoff brief"、"bring my coauthor up to speed"、"what changed since last week"、"onboard a collaborator"、"write a handoff for [name]"、"共同作者简报"、"协作者交接"、"上周以来改了什么"，或在把仓库发给共同作者之前使用。它既不是提交，也不是检查点，而是 `meta-governance.md` 只部分覆盖的跨机器、跨人摘要。
argument-hint: "[--since <tag|date|Ndays>] [--for <collaborator-name>] [--no-data-section]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# /coauthor-brief —— 协作者交接简报

本技能生成一份 Markdown 简报，让共同作者或另一台机器上的自己在几分钟内了解**改了什么、各产物处于什么状态、什么阻碍了进展，以及如何在本地跑通流水线**，包括新协作者所需的受限数据访问步骤。[`meta-governance.md`](../../rules/meta-governance.md) 规定跨机器工作时*记忆*如何同步：通用经验通过 git 共享，原生自动记忆与本机 `.workbuddy/memory/` 项目日志留在各自机器。本技能处理*人*的交接，按协作者和会话组织信息。

**核心原则：** `/checkpoint` 帮助*自己*续接，`/coauthor-brief` 帮助*别人*接手。前者回答「我干到哪了」，后者回答「我要接手其中一块，需要知道什么」。

## 何时使用

- **把仓库（或一个 PR / 分支）发给共同作者之前**，让对方直接上手，不必翻查 git 历史。
- **给新 RA / 协作者做入职**，把本地复现与受限数据步骤集中在一处。
- **长期多作者项目定期同步**，说明自上一份简报以来的增量。
- **跨机器交接**，例如在办公室台式机收尾、到笔记本继续，或把分析部分交给使用 Stata 的共同作者，而自己使用 R。

## 何时不要使用

- 需要*自己*的续接点时，用 [`/checkpoint`](../checkpoint/SKILL.md)。
- 需要在自动压缩前提炼嘈杂会话时，用 [`/compress-session`](../compress-session/SKILL.md)。
- 需要提交信息时，用 [`/commit`](../commit/SKILL.md)。

## 各阶段

### Phase 0 —— 确定日期窗口与 diff 基线

按以下优先顺序确定增量窗口，并把窗口筛选与 diff 基线分开保存为 `window_point` 和 `diff_base`：

1. 若给了 `--since <arg>`，使用指定 git 标签、ISO 日期或 `Ndays`，例如 `--since v1.2`、`--since 2026-05-01`、`--since 14days`。
2. 否则使用**上一份简报**：运行 `ls -t quality_reports/handoffs/*.md | head -1`，取文件名中的日期作为下限。
3. 若仍无法确定，回退到 **14 天**，并在简报中说明。没有边界的 `git log` 只会带来噪声。

- **ISO 日期 / `Ndays`：**提交日志始终以 `git log --oneline --since=<point>` 筛选；计算 diff 前，另用 `git rev-list -1 --before=<point> HEAD` 把 `window_point` 解析为实际提交 `diff_base`，不能直接把日期当作 diff 的 revision。
- **标签：**用 `git rev-parse --verify <tag>^{commit}` 直接解析为 `diff_base`，日志与 diff 均可使用 `<tag>..HEAD`；不要把标签传给 `--since` 当日期。
- **空窗口：**日志在窗口内没有提交时，明确写「no commits in window」。若 `rev-list` 没有解析出基线，或窗口内没有提交可供比较，就不要运行带空 revision 的 diff；把 diff 标为「无可用基线／无窗口内提交」，仍继续收集项目状态，不能编造改动。

开始收集前，先分别列出解析出的日志窗口与实际 diff 基线（「Log window: `<point>`；Diff base: `<commit/tag/unavailable>`」）。

### Phase 1 —— 收集增量 + 项目状态

只读收集信息。纯 R、纯 Stata、没有幻灯片等项目应跳过不适用的来源，不得编造。

1. **Git 增量**：日期／`Ndays` 窗口运行 `git log --oneline --since=<point>`，标签窗口运行 `git log --oneline <tag>..HEAD`；只有 Phase 0 已得到非空 `diff_base` 时，才运行 `git diff --stat <diff_base>..HEAD`。另运行 `git branch --show-current`，并用 `git log --all --oneline -15` 查看共同作者的并行分支。按稿件／分析／幻灯片／基础设施给提交分组；窗口无提交或基线不可用时，按 Phase 0 的空窗口规则记录，不运行残缺 diff。
2. **可复现性状态**：若存在 `quality_reports/passports/<slug>.yaml` passport，读取 PASS / FAIL / EXPLAINED / STALE / UNVERIFIED 汇总（[`audit-reproducibility`](../audit-reproducibility/SKILL.md)、[`replication-protocol.md`](../../rules/replication-protocol.md)），说明分析已达到可复现就绪，还是仍有未决 FAIL。
3. **未决的计划项**：读取最近的 `quality_reports/plans/*.md` 状态及任何「Open questions」/「Next」行，并读取最新 `quality_reports/session_logs/*.md` 中的阻塞项。
4. **环境 / 锁文件**：找出协作者需要的环境快照，包括 `renv.lock`（R）、`requirements.txt` / `environment.yml` / `uv.lock`（Python）、Stata 的 `version` 行 + `.do` 中的 `ssc install` 列表，或 [`/capture-environment`](../capture-environment/SKILL.md) 生成的记录。写明准确的还原命令。
5. **受限数据步骤** *（`--no-data-section` 时跳过）*：若仓库涉及机密／受限数据，阅读 [`confidential-data.md`](../../rules/confidential-data.md)，概述新协作者的访问路径，包括 DUA / IRB 批准、安全飞地或 openICPSR 受限凭据、数据存放位置、哪些内容被 git 忽略、哪些已提交。**绝不能把真实受限数值、活动数据提取件路径或凭据写进简报**。这里只描述*获取访问的流程*，不复制数据。

### Phase 2 —— 写简报

使用下面的模板，篇幅控制在约 1–2 屏。具体的 `path:line` 指针比泛泛描述更有用。

**每条状态陈述都要标注 `measured` 或 `inferred`。** *Measured* 表示命令已经实际运行，报告的就是它的输出，并且必须**点名命令**。*Inferred* 表示结论来自阅读代码、diff 或早前某次运行。两类信息都可以写入简报，但不能混淆，否则读者无法判断哪些断言可以直接据以行动。应写 `replication-ready (measured: Rscript scripts/R/00_run_all.R — 0 FAIL)`，不要只写 `replication-ready`。

**逐项说明被委派工作的处置。**凡交给共同作者、RA 或代理的任务，都单独一行，标为完成（附证据）／进行中／受阻（说明阻塞原因）／未开始。*「基本做完了」*不是有效处置，因为它仍让读者自己寻找缺口，而简报本应消除这项负担。

```markdown
---
date: YYYY-MM-DD
for: [collaborator name or "all coauthors"]
since: [tag | date | Ndays]
diff-base: [resolved commit | unavailable — no baseline/no commits in window]
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
- Native auto memory (`~/.workbuddy/projects/<project>/memory/`) stays **local** to each user and machine.
- `.workbuddy/memory/` is the third layer: this checkout's gitignored daily project logs and local state. It stays **local**, is not a user-level auto-memory substitute, and must not be committed or expected on a co-author's machine.
- `.codebuddy/state/` also stays **local** — never expect a co-author to have yours (see meta-governance.md).
- Pull before you brief; brief before you hand off.
```

### Phase 3 —— 保存并小结

1. 写入 `quality_reports/handoffs/YYYY-MM-DD_coauthor-brief.md`；目录不存在时先创建。若设置了 `--for`，在 slug 后加 `…_coauthor-brief_<name>.md`。
2. 在对话中打印保存路径、解析出的日志窗口与实际 `diff_base`（或空窗口原因）、计数（概述的提交数／未决问题数／产物数），以及数据章节是包含还是跳过。

## 输出 / 报告格式

产出一份符合 Phase 2 模板的 Markdown 交接文档，保存到 `quality_reports/handoffs/YYYY-MM-DD_coauthor-brief.md`，并在对话中给出一行小结。不改动其他文件。

## 退出行为

- **简报已写出：**退出 0，给出保存路径与小结。
- **「自」点无法解析且窗口内没有 git 历史：**仍写出简报，明确注明「no changes in window」，不要直接失败。刚开始接手的共同作者仍需要状态 + 复现 + 数据三个章节。
- **检出受限数据仓库但缺 `confidential-data.md`：**写出简报，在数据章节保留 `TODO: complete per your DUA` 占位符并发出警告，**不要**猜测访问流程。

## 参数

| 参数 | 作用 |
|---|---|
| `--since` | 取值为 `tag` / `date` / `Ndays`，指定日志窗口起点；日期与 `Ndays` 通过 `git rev-list -1 --before=<point> HEAD` 另解析实际 diff 基线，标签则直接解析为提交。默认使用 `quality_reports/handoffs/` 中的上一份简报，否则回退到 14 天（Phase 0）。 |
| `--for` | 取 `<name>`，针对某位协作者裁剪简报，例如突出他仍需要的受限数据访问步骤。 |
| `--no-data-section` | 跳过「Restricted-data access」章节（Phase 1 第 5 项）。适用于仓库不涉及受限数据，或不想把访问流程写进可能被邮件转发的文档时。 |

## 交叉引用

- [`.codebuddy/rules/meta-governance.md`](../../rules/meta-governance.md) —— 跨机器记忆模型规定什么同步、什么留在本机；本简报把这套模型用于*人际交接*。
- [`.codebuddy/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) —— 生成「Reproduce locally」章节所指向的锁文件。
- [`.codebuddy/skills/checkpoint/SKILL.md`](../checkpoint/SKILL.md) —— 用于*自我*续接；本技能用于*他人*交接。
- [`.codebuddy/skills/compress-session/SKILL.md`](../compress-session/SKILL.md) —— 压缩前提炼嘈杂会话；上下文臃肿时可先运行它，再做简报。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 受限数据处理规则；数据章节只概述访问步骤，不暴露数据。

## 本技能不做的事

- **不推送、不开 PR、不合并。**它只写一份文档。建分支、提交与开 PR 由 [`/commit`](../commit/SKILL.md) 处理，是否合并由用户决定。
- **不运行流水线或审计数字。**它只*报告*已有 passport 状态，不重跑分析，也不重新核验论断；这些由 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 完成。
- **不采集环境。**它只定位并链接已有锁文件；生成锁文件是 [`/capture-environment`](../capture-environment/SKILL.md) 的工作。
- **不暴露受限数据。**它只描述*访问流程*，绝不会把机密数值、活动数据路径或凭据复制到可能通过邮件发送或提交到仓库的简报中。
