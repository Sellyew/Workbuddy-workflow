---
name: commit
description: 提交当前工作：先跑质量、一致性和护照三道门禁，必要时从 main 创建分支，精确暂存文件，并用主题句说明提交后什么事实成立。只有指定 --pr 或用户明确要求时才推送并创建拉取请求；只有用户明确要求合并时才合并。仅在用户有明确提交意图时使用，例如说 "commit"、"let's commit this"、"open a PR"、"提交这些改动"，或以 `/commit` 开头。不要因为 "we're done"、"wrap up"、"收尾吧" 等含糊收尾话自动调用，必须先得到明确确认。永不强制推送，永不跳过钩子。
description_zh: 提交当前工作：先跑质量、一致性和护照三道门禁，必要时从 main 创建分支，精确暂存文件，并用主题句说明提交后什么事实成立。只有指定 --pr 或用户明确要求时才推送并创建拉取请求；只有用户明确要求合并时才合并。仅在用户有明确提交意图时使用，例如说 "commit"、"let's commit this"、"open a PR"、"提交这些改动"，或以 `/commit` 开头。不要因为 "we're done"、"wrap up"、"收尾吧" 等含糊收尾话自动调用，必须先得到明确确认。永不强制推送，永不跳过钩子。
argument-hint: "[optional: commit message] [--pr]"
allowed-tools: ["Bash", "Read", "Glob", "Agent", "Task"]
---

# 提交

先验证门禁，再提交。**提交不是拉取请求，拉取请求也不是合并。**

本技能在提交后停止。只有指定 `--pr` 或用户明确要求时，才推送并创建拉取请求；**绝不自行合并**，只有用户明确要求合并某个拉取请求时才合并，见下文「合并」。Codex、Copilot 等审阅者会在拉取请求创建后留言；在他们报告前合并，等于跳过审查。

## 步骤

### 参数解析（先于所有步骤）

先按 shell 风格引号解析 `$ARGUMENTS`。把每个独立的 `--pr` token 记录为「提交后创建拉取请求」的布尔开关并**从参数列表移除**；只有移除后剩余的 token 才按原顺序组成提交信息。剩余内容为空或只有空白时，不把它当作用户提交信息，而是在 Step 4 分析暂存改动并自动生成主题。

### Step 0：质量门禁（提交前）

**在创建分支前运行。** 对每个已修改且有质量评分细则的 `.qmd`、`.tex` 或 `.R` 文件运行：

```bash
python scripts/quality_score.py <changed-file-paths>
```

- 任一文件得分低于 **80** 时，停下并报告审查发现。用户可以修复问题，也可以明确说 *"commit anyway"* 或 *"skip quality gate"* 来豁免。运行过 `./scripts/install-hooks.sh` 后，`.githooks/pre-commit` 会对暂存的 `.qmd`/`.tex`/`.R` 文件重跑同一项 ≥80 门禁。因此，已获批准的豁免必须带入 Step 4，写成 `SKIP_QUALITY_GATE=1 git commit ...`，并在提交信息中记录理由。该变量只跳过质量评分，门禁总检仍会运行。绝不能退回使用 `git commit --no-verify`。
- 所有文件都达到 80 分以上时，继续。

通过 `Agent` 工具启动 **verifier** 代理，设置 `subagent_type=verifier`，对改动文件运行编译/渲染检查，并在提交前报告通过或失败。

### Step 0b：一致性门禁（提交前）

**无条件运行完整门禁总检。** 全部 12 个门禁包括：surface-sync 校验的 `本模板 19 个代理、63 个技能、37 条规则、11 个钩子` 等计数断言和带标记表格、技能完整性、模型时效、链接、规范一致性、陈旧内容、仓库卫生、派生计数、台账覆盖、钩子回归集、可移植性回归集、幻灯片内容不变量：

```bash
./scripts/backtest.sh
```

- **Exit 0：** 全部门禁通过，继续。
- **Nonzero：** 至少一个门禁失败，打印输出并停下。修复后重跑。即使用户说了 "commit anyway"，也不能越过失败门禁；失败意味着下一个读者会继承漂移，而小规模计数漂移已多次让后续 PR 付出代价。

### Step 0c：护照检查（提交前）

如果本次 diff 触及以下任何文件，就读取对应护照：在 `quality_reports/passports/` 中有护照的手稿（`.tex`/`.qmd`）、护照列出的任何 `source_file`，或断言声明为展示物的文件，包括其 `location:` 或某个 `appears_in` 的 `path:`。关键断言若为 `status: FAIL` 或 `STALE`，**必须修复**：停下并点名断言，在提交前指向 `/audit-reproducibility` 或已失效的脚本。

展示物也触发检查，是因为修改某个数字在一件产物中的副本，会使它与该数字的其他展示物失去同步；同一提交未必同时更新包含该数值的附录或幻灯片。没有护照时静默跳过。

### Step 1：检查当前状态

```bash
git status
git diff --stat
git log --oneline -5
```

### Step 2：建分支（在 main 上时）

绝不直接向 `main` 提交。当前分支是 `main` 时先创建分支；已经在特性分支上时，直接在该分支提交。

```bash
git checkout -b <short-descriptive-branch-name>
```

### Step 3：把文件加入暂存区

逐个暂存指定文件，绝不用 `git add -A`：

```bash
git add <file1> <file2> ...
```

不要暂存 `.codebuddy/settings.local.json` 或任何含密钥的文件。

### Step 4：用有描述性的提交信息提交

使用「参数解析」阶段移除 `--pr` 后留下的提交信息，不得再把原始 `$ARGUMENTS` 整体传给 `git commit`。剩余信息为空时，分析暂存改动并自动生成主题，写清*为什么*修改，而不只是*做了什么*。

**主题行要陈述提交后成立的事实**，也就是一句平实、可供读者验证的行为陈述。*"Fixed review feedback"* 和 *"Updated the checker"* 只描述作者做过什么，没有告诉读者代码现在怎样；*"The parity gate refuses a fixture whose hash is unregistered"* 则是读者可以对照代码核验的断言。来自哪轮评审、谁提出要求、尝试了几次等过程信息，必要时写入正文。正文说明*为什么*，主题行承载行为断言。

```bash
git commit -m "$(cat <<'EOF'
<commit message here>
EOF
)"
```

### Step 5：推送并开拉取请求 —— 只有带 `--pr` 或用户要求时才做

没有 `--pr`，用户也没有要求拉取请求时，跳过此步。提交只留在本地，并在报告中明确说明。

```bash
git push -u origin <branch-name>
gh pr create --title "<short title>" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points>

## Changed defaults
<"None", or each default a forker will notice changing: a setting, a threshold, a hook that now fires, a path that moved>

## Test plan
<checklist>

🤖 Generated with WorkBuddy
EOF
)"
```

### Step 6：汇报

报告提交哈希和主题、分支，以及拉取请求 URL（若已创建），并明确说明没有合并任何内容。

## 合并 —— 仅当用户这么说时

合并不是本技能的固定步骤。只有用户明确要求合并某个具体拉取请求时才执行，例如 "merge #155"；"ship it"、"done" 或 "commit" 都不是合并指令。合并前，确认该拉取请求的 CI 全部通过，并且人工、Codex、Copilot 等评审都已阅读并答复。

```bash
gh pr merge <pr-number> --merge --delete-branch
git checkout main
git status --porcelain          # must print nothing before the next line runs
git pull
```

**这里要预期工作树仍有未暂存内容，Step 3 正是为此设计。** 逐个暂存文件意味着，会话改过但未暂存的内容和所有未跟踪产物仍留在工作树中。只要 `git status --porcelain` 非空，本模板附带的 `git-guardrails` 钩子就会**拒绝** `git pull`、`merge` 和 `rebase`。在未提交工作上执行 pull 后，无法复核哪些 hunk 来自远端。把 stash 串进同一命令行也没有用，因为钩子读取的是工作树，不会预测该命令行接下来如何改变它。

先有意清理工作树，再 pull：

```bash
git stash push -u -m "post-merge: unstaged leftovers"   # -u, or untracked files stay behind
git pull
git stash pop
```

`git pull --autostash` 是一条命令的替代方案，但只适用于未提交内容全部位于**已跟踪**文件的工作树。`git stash` 不会暂存未跟踪文件，所以存在 `??` 条目时，autostash 仍会在本检查试图拒绝的脏树上开始 pull。因此，只要有 `??`，钩子就会读取 porcelain 并**拒绝** `--autostash`。这通常是常态，所以默认使用上面显式的 `-u` stash；只有 `git status --porcelain` 完全没有 `??` 行时，才把 `--autostash` 作为捷径。Git 本身也有同样限制：如果传入提交要在未跟踪文件占用的路径上新增文件，即使 autostash 已执行，合并也会中止并报告 *"untracked working tree files would be overwritten"*。stash 和 pull 必须作为**独立**命令执行；串在同一行会被拒绝，因为只有独立简单命令形式的已识别历史操作，才会进入读取工作树的环节。

`ALLOW_DIRTY_MERGE=1` 只留给你已经检查并能明确说明理由的脏状态，不是常规补救手段。因为阻断碍事就使用它，正是这项检查要防止的行为。

## 要点

- **永不跳过 Step 0。** 质量门禁会在错误编译、错误引文和硬编码路径进入 `main` 前拦截。用户坚持跳过时，把豁免理由记入提交信息。
- 绝不直接向 `main` 提交，先创建分支。
- 未经要求，绝不推送、创建拉取请求或合并，见 Step 5 和「合并」。
- 暂存时排除 `settings.local.json` 和敏感文件。
- 用户确实要求合并时，使用 `--merge`，不要用 `--squash` 或 `--rebase`，除非用户另有说明。
- 提交信息只能来自移除 `--pr` 后的剩余参数；为空时自动生成主题。

## 参数

| 参数 | 作用 |
|---|---|
| `--pr` | 提交之后推送分支并开拉取请求（Step 5）。永不合并。 |
