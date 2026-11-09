---
name: init-research-project
description: 把 fork 得到的模板初始化为真实科研项目，逐项收齐项目信息、替换占位符、按学科调整规则与代理、运行环境自检，最后给出可执行的起步计划。用户说 "init"、"初始化项目"、"开一个新项目"、"start a new project"、"把这个模板变成我的项目" 时使用。NOT for 给已经在跑的项目加功能，这类需求使用对应技能（`/create-lecture`、`/preregister` 等）。
description_zh: 把 fork 得到的模板初始化为真实科研项目，逐项收齐项目信息、替换占位符、按学科调整规则与代理、运行环境自检，最后给出可执行的起步计划。用户说 "init"、"初始化项目"、"开一个新项目"、"start a new project"、"把这个模板变成我的项目" 时使用。NOT for 给已经在跑的项目加功能，这类需求使用对应技能（`/create-lecture`、`/preregister` 等）。
argument-hint: "[可选：项目简称]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
user-invocable: true
---

# 初始化科研项目

把模板的**占位符状态**变成可直接开展工作的项目状态。这不是展示「欢迎页」，而是**受控地填充项目信息**：每处改动都要有理由，没有问清的内容不能猜。

## 为什么要有这一步

模板包含 `[YOUR PROJECT NAME]`、`[你的单位]`、`[your-env]` 等占位符，以及一套**通用**规则和代理。未经初始化就开工，会带来三个问题：

- 规则虽然按 `paths:` 匹配成功，其中的示例却与研究主题无关。
- 代理在不了解学科规范的情况下审读稿件。
- 半年后，连自己也分不清哪些规则来自模板，哪些是后来写的。

本技能一次处理这三件事，并在 `quality_reports/` 留下记录。

## 阶段 0 —— 开始前检查（不通过就不往下走）

按顺序确认以下事项。任一项失败都要停下报告，不能先跳过、以后再补：

1. **项目是否尚未初始化？** 阅读 `CODEBUDDY.md` 第一段。如果 `[你的项目名称]` 等占位符已替换，说明项目可能初始化过。先问用户要**重新初始化**还是**只补缺项**，不要覆盖已有内容。
2. **环境自检。** 运行 `./scripts/validate-setup.sh`；Windows 下使用 `bash scripts/validate-setup.sh`，或按它报告的缺失项逐条确认。把输出原样贴给用户，不要概括成「一切正常」。
3. **门禁基线。** 运行 `python scripts/backtest.py`，**必须全绿**后才能开始修改。否则初始化后无法分清哪些失败来自模板，哪些由本次改动引入。

## 阶段 1 —— 收齐信息（一次问完，不要挤牙膏）

按下面的清单向用户提问。**能从仓库读出的信息不要重复询问**，例如可从 `README.md` 和已有 `Slides/` 推断的内容。`CITATION.cff` 记录的是模板及上游作品的引用信息，不能从中推断新项目的名称、作者或仓库地址。一次列全问题，等待用户集中回答。

| 项 | 落到哪里 | 说明 |
|---|---|---|
| 项目名称 | `CODEBUDDY.md`、`README.md` | 论文/课程的真名，不是代号 |
| 单位与作者 | `CODEBUDDY.md` | 只用于当前项目配置，不改模板的引用信息 |
| 学科 | `.codebuddy/references/journal-profiles.md`、`.codebuddy/agents/domain-reviewer.md` | 决定目标期刊集合与领域审读透镜 |
| 主要交付物 | `CODEBUDDY.md` 的「当前项目状态」表 | 讲义？论文？两者都有？ |
| 目标期刊 / 会议 | `.codebuddy/references/journal-profiles.md` | 直接决定 `--peer` 的校准 |
| 数据是否有访问限制 | `.codebuddy/rules/confidential-data.md`、`TROUBLESHOOTING.md` | 有就**必须先**配拒绝规则再放任何数据进来 |
| 是否用 Stata / R / Python | 对应 `*-conventions.md` | 不用的那套留着不碍事，但要告诉用户它存在 |
| 语言 | 中文写作还是英文写作 | 决定 `/humanize`、`/proofread` 的判据 |

**如果用户说「你先按常见的来」**，可以代填，但必须逐项列出代填内容，并标注「这是我替你定的，改起来是一行」。不能静默代填。

## 阶段 2 —— 填充（按这个顺序，逐项留痕）

1. **`CODEBUDDY.md`**：替换项目名和单位，删除 `HelloWorld` 样例行，把「当前项目状态」表换成真实的第一行。
2. **保留 `CITATION.cff` 不变。**它说明如何引用这套模板及上游原作，不是新项目的元数据。不得替换其中的标题、作者、年份、`repository-code` 或 `url`，也不得填入 `[BLOCKED]`。如果用户需要为新研究项目单独提供引用信息，先另行确认，再创建独立文件。
3. **按学科调整：**
   - `journal-profiles.md`：保留与用户学科相关的画像，其余标为「本学科未用」，不要删除，便于以后合并上游同步。
   - `domain-reviewer.md`：把通用透镜换成用户学科的审读透镜，并说明每条要求为什么具有学科特异性。
4. **受限数据**（仅当阶段 1 回答「有」）：先在 `.codebuddy/settings.json` 添加 **deny 规则**，再继续其他步骤，顺序不能颠倒。
5. **`README.md`**：只修改「这个项目是什么」，不要重写模板说明。后者属于上游内容，重写会让同步变成整份文件的人工合并。
6. **`MEMORY.md`**：如果模板自带的示例 `[LEARN]` 条目不是你的经验教训，就清除它们，但保留格式。

## 阶段 3 —— 验证（做了才算完）

按顺序运行以下命令。任一项失败，都要修复后再报告完成：

```bash
python scripts/backtest.py            # 门禁全绿
bash scripts/backtest.sh              # 上游原件（POSIX bash 环境下）
./scripts/validate-setup.sh           # 环境自检
```

再人工确认三件事：

- `CODEBUDDY.md` 中**不再有** `[方括号占位符]`。用 `grep -n '\[.*\]' CODEBUDDY.md` 逐条检查，只允许保留示例表格里标了「删掉」的几行。
- 修改过的规则文件仍能通过 `python scripts/check-skill-integrity.py`；改过标题时，必须同步更新锚点。
- **没有改坏任何计数断言**：`python scripts/verify-count-gates.py` 应当 12/12 变红。

## 阶段 4 —— 交出起步计划

初始化结束时，不要只说「好了，你可以开始了」，而要给出**下一步的三个具体动作**，例如：

1. 把第一份真实材料放进 `master_supporting_docs/`，然后运行 `/create-lecture` 或 `/preregister`。
2. 如果研究问题还不清楚，用 `/interview-me` 梳理。
3. 运行一次 `/commit`，让质量门禁从**第一次**提交开始生效。

把计划写入 `quality_reports/plans/`，并在 `MEMORY.md` 追加 `[LEARN:project] 初始化于 YYYY-MM-DD：学科=…，交付物=…`，方便半年后追溯。

## 边界（不要做的事）

- **不要 `git commit`。** 初始化不等于提交；是否提交由用户通过 `/commit` 决定。
- **不要把 `CITATION.cff` 当作项目占位符。** 上游作者和地址属于引用归属，必须保留；受限数据、项目尚未公开或仓库地址未知都不构成修改它的理由。
- **不要删规则或技能。** 用不上就标注，不要删除。否则上游同步时它们会悄悄恢复，而你以为它们已经不存在。
- **不要为了「看起来整洁」重排目录。** 目录结构本身就是门禁检查的契约。
- **阶段 0 的门禁仍失败时，不要开始填充。** 否则模板原有问题与本次引入的问题会混在一起，之后难以追责和排查。
