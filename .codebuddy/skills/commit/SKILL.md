---
name: commit
description: 提交当前工作——跑质量、一致性与护照三道门禁，必要时从 main 切分支，精确暂存文件，并写一条主体句说明「提交之后什么为真」的提交信息。只有带 --pr 或用户明确要求时才推送并开拉取请求；永不合并——只有在用户明确说要合并时才发生合并。仅在明确的提交意图下使用——用户说 "commit"、"let's commit this"、"open a PR"，或以 `/commit` 开头。不要因为含糊的收尾话（"we're done"、"wrap up"）而自动调用——那些必须先经明确确认。永不强制推送，永不跳过钩子。
description_zh: 提交当前工作——跑质量、一致性与护照三道门禁，必要时从 main 切分支，精确暂存文件，并写一条主体句说明「提交之后什么为真」的提交信息。只有带 --pr 或用户明确要求时才推送并开拉取请求；永不合并——只有在用户明确说要合并时才发生合并。仅在明确的提交意图下使用——用户说 "commit"、"let's commit this"、"open a PR"，或以 `/commit` 开头。不要因为含糊的收尾话（"we're done"、"wrap up"）而自动调用——那些必须先经明确确认。永不强制推送，永不跳过钩子。
argument-hint: "[optional: commit message] [--pr]"
allowed-tools: ["Bash", "Read", "Glob", "Agent", "Task"]
---

# 提交

先验证门禁，再提交。**提交不是拉取请求，拉取请求也不是合并。**
本技能在提交之后即止。只有带 `--pr` 或用户明确要求时，它才推送并开拉取请求；它**永不合并** —— 只有用户明确说要合并那个拉取请求时才发生合并（见下文「合并」）。Codex、Copilot 这类审阅者是在拉取请求开出之后才留言的；在他们报告之前就合并，等于跳过他们的审查。

## 步骤

### Step 0：质量门禁（提交前）

**在切分支之前运行。** 对每一个改动过、且有质量评分细则的 `.qmd`、`.tex` 或 `.R` 文件，运行：

```bash
python scripts/quality_score.py <changed-file-paths>
```

- 若任一文件得分低于 **80**，停下并报告审查发现。用户要么修掉问题，要么用 *"commit anyway"* 或 *"skip quality gate"* 这类说法明确豁免。一旦跑过 `./scripts/install-hooks.sh`，`.githooks/pre-commit` 会对暂存的 `.qmd`/`.tex`/`.R` 文件重跑同一条 ≥80 门禁，所以要把已获批的豁免带进 Step 4，写成 `SKIP_QUALITY_GATE=1 git commit ...`，并在提交信息里记下豁免理由。该变量只跳过质量评分；门禁总检照旧运行。绝不退回到 `git commit --no-verify`。
- 若所有文件都在 80 分以上，继续。

派生 **verifier** 代理（通过 `Agent` 工具，`subagent_type=verifier`），对改动文件跑编译/渲染检查。提交之前报告通过/失败。

### Step 0b：一致性门禁（提交前）

**无条件运行。** 完整的门禁总检 —— 全部 11 个门禁（surface-sync 校验的 `本模板 19 个代理、63 个技能、37 条规则、11 个钩子` 这类计数断言与带标记的表格、技能完整性、模型时效、链接、规范一致性、陈旧内容、仓库卫生、派生计数、台账覆盖、钩子回归集、可移植性回归集）：

```bash
./scripts/backtest.sh
```

- **Exit 0：** 全部门禁为绿 —— 继续。
- **Nonzero：** 至少一个门禁为红 —— 打印它的输出并停下。修好，再重跑。红着就不要越过这道门禁，哪怕说了 "commit anyway"：红门禁是下一个读者要继承的漂移，而小规模的计数漂移已经反复让后续 PR 付出代价。

### Step 0c：护照检查（提交前）

若本次 diff 触及一份在 `quality_reports/passports/` 里有护照的手稿（`.tex`/`.qmd`）、某份护照列出的任何 `source_file`、或某个断言声明为展示物的任何文件（它的 `location:`，或某个 `appears_in` 的 `path:`），就读那份护照：关键断言若为 `status: FAIL` 或 `STALE`，就是**必须修复** —— 停下，点名该断言，并在提交之前指向 `/audit-reproducibility`（或那个已失效的脚本）。触及展示物会触发这项检查，理由与触及脚本相同：改了某个数字在某件产物里的副本，就会让它与该数字的其他展示物脱同步 —— 同一提交里未必更新了那个持有相同数值的附录或幻灯片。没有护照时静默跳过。

### Step 1：检查当前状态

```bash
git status
git diff --stat
git log --oneline -5
```

### Step 2：建分支（在 main 上时）

绝不直接向 `main` 提交。若当前分支是 `main`，就建一个；若你已在特性分支上，就在那里提交。

```bash
git checkout -b <short-descriptive-branch-name>
```

### Step 3：把文件加入暂存区

逐个加入指定文件（绝不用 `git add -A`）：

```bash
git add <file1> <file2> ...
```

不要把 `.codebuddy/settings.local.json` 或任何含密钥的文件加入暂存区。

### Step 4：用有描述性的提交信息提交

若提供了 `$ARGUMENTS`，就把它当作提交信息。否则分析暂存的改动，写一条解释*为什么*、而不只是*做了什么*的信息。

**主题行陈述提交之后为真的事** —— 一句平实的、读者能去验证的行为陈述。*"Fixed review feedback"* 和 *"Updated the checker"* 只在讲你的下午，什么也没告诉读者；*"The parity gate refuses a fixture whose hash is unregistered"* 是一条他们可以对着代码核对的断言。过程叙述 —— 出自哪一轮评审、谁要求的、试了几次 —— 该进正文就进正文；正文照旧承载*为什么*，主题行承载断言。

```bash
git commit -m "$(cat <<'EOF'
<commit message here>
EOF
)"
```

### Step 5：推送并开拉取请求 —— 只有带 `--pr` 或用户要求时才做

没有 `--pr`、用户也没要拉取请求时，跳过这一步：提交留在本地，报告里说明这一点。

```bash
git push -u origin <branch-name>
gh pr create --title "<short title>" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points>

## Changed defaults
<"None", or each default a forker will notice changing: a setting, a threshold, a hook that now fires, a path that moved>

## Test plan
<checklist>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Step 6：汇报

报告提交（哈希与主题）、分支，以及 —— 若开了拉取请求 —— 它的 URL。明说没有合并任何东西。

## 合并 —— 仅当用户这么说时

合并从来不是本技能的一个步骤。只有用户明确要求合并某个具体拉取请求时才合并（"merge #155"）；"ship it"、"done" 或 "commit" 都不是合并指令。合并之前，确认该拉取请求的 CI 为绿，且它的各条评审（人工、Codex、Copilot）都已读过并答复。

```bash
gh pr merge <pr-number> --merge --delete-branch
git checkout main
git status --porcelain          # must print nothing before the next line runs
git pull
```

**这一步要预期工作树是脏的 —— Step 3 正是为此而设。** 逐个暂存文件意味着：会话碰过但没暂存的东西、以及每一件未跟踪的产物，在你走到这一步时都还在树里。本模板附带的 `git-guardrails` 钩子只要 `git status --porcelain` 非空，就**拒绝** `git pull`（以及 `merge`、`rebase`），因为一次叠在未提交工作之上的 pull 事后无法复核 —— 你再也分不清哪个 hunk 来自远端。把 stash 串进同一命令行也没用：钩子读的是树，它不预测这一行会对树做什么。

先刻意清空树，再 pull：

```bash
git stash push -u -m "post-merge: unstaged leftovers"   # -u, or untracked files stay behind
git pull
git stash pop
```

`git pull --autostash` 是一条命令的替代方案，但只适用于脏东西全为**已跟踪**文件的树。`git stash` 不会暂存未跟踪文件，所以对着一行 `??` 做 autostash，等于在这项检查存在就是为了拒绝的那棵脏树上开始 pull —— 因此只要有任何 `??` 条目，钩子就读 porcelain 并**拒绝** `--autostash`。走到这一步，这通常是常态，所以上面显式的 `-u` stash 是默认路线，`--autostash` 是「`git status --porcelain` 完全没有 `??` 行」时的捷径。Git 自己也独立地认同这点：若进来的提交要在一个你正以未跟踪状态持有的路径上新增文件，它会在 autostash 已经取走之后中止合并（*"untracked working tree files would be overwritten"*）。两条路线都必须是**独立**命令 —— 把 stash 和 pull 串到一行上会被直接拒绝，因为一个已识别的历史操作只有作为独立简单命令时才会到达读树的环节。

`ALLOW_DIRTY_MERGE=1` 是给「你看过并且能大声说出理由」的脏状态留的舱口。它不是常规补救手段；因为阻断碍事就去抓它，正是这项检查存在要防的行为。

## 要点

- **永不跳过 Step 0。** 质量门禁在坏的编译、错的引文、硬编码路径到达 `main` 之前就拦下它们。若用户坚持跳过，把他们的豁免理由记进提交信息。
- 绝不直接向 `main` 提交；先切分支。
- 未经要求绝不推送、绝不开拉取请求、绝不合并 —— 见 Step 5 与「合并」。
- 暂存时排除 `settings.local.json` 与敏感文件。
- 用户确实要求合并时，用 `--merge`（不要 `--squash` 或 `--rebase`），除非他们另有说明。
- 若提供了 `$ARGUMENTS` 作为提交信息，就原样使用。

## 参数

| 参数 | 作用 |
|---|---|
| `--pr` | 提交之后推送分支并开拉取请求（Step 5）。永不合并。 |
