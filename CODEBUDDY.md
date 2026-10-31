# CODEBUDDY.md —— 用 WorkBuddy 做学术项目开发

<!-- 用法：把所有 [方括号占位符] 换成你自己的项目信息。
     Beamer 环境与 CSS 类按你的主题定制。
     本文件请控制在 200 行以内（官方建议）——它每次会话都会被加载。
     完整文档见 docs/workflow-guide.html。
     中文书写规范见 docs/translation-conventions.md。 -->

**项目：** [你的项目名称]
**单位：** [你的单位]
**分支：** main

---

## 范围纪律

**只做被要求的那件事，一件都不多做。** 不要附带 README、构建脚本、`.gitignore` 改动、辅助工具，或任何没被要求的额外脚手架。如果某个补充确实有价值，**把它作为建议列在最后**，由用户决定。

要一份 codebook 就是要一份 codebook。交付 codebook + README + 构建脚本 + gitignore 改动，意味着用户为了接受一件事要审四件事，而通常的结果是四件一起被扔掉。

**要在请求之外加任何东西之前，先问。** 一句话的询问比一次回滚便宜。

---

## 核心原则

- **先计划后执行** —— 非平凡任务先进入计划模式；计划存到 `quality_reports/plans/`
- **改完要验** —— 任务改动了 `.tex`、`.qmd` 或 `.R` 文件时，必须实际编译或渲染，确认输出后才可报完成
- **单一真源** —— Beamer `.tex` 是权威源，Quarto `.qmd` 由它派生
- **质量门禁** —— 低于 80/100 不许出库
- **[LEARN] 标签** —— 被纠正时，把 `[LEARN:category] 错 → 对` 写进 [MEMORY.md](MEMORY.md)

跨会话上下文存放在 [MEMORY.md](MEMORY.md)；历史计划、规格与会话日志在 [quality_reports/](quality_reports/)。

**我们如何验证** —— 承载验证纪律的参考文件与规则：

- [`verification-ladder.md`](.codebuddy/references/verification-ladder.md) —— 7 级阶梯，从*资格化检查器*到外部裁判，以及审读回路如何收敛。
- [`external-oracle-process.md`](.codebuddy/references/external-oracle-process.md) —— 如何跑一个独立的前沿模型裁判（通过 Oracle CLI 换一家厂商的模型；当前目标见其 §2），以及如何裁决它返回的东西。
- [`provenance-and-ground-truth.md`](.codebuddy/references/provenance-and-ground-truth.md) —— 给你的裁判命名与钉版、给分歧分类，以及净室边界。
- [`review-fencing.md`](.codebuddy/rules/review-fencing.md) —— 审阅独立性是环境的属性，不是一句嘱咐：检出目录之外的干净副本、扣留此前的裁决、把仓库里已提交的答案键隔离在外。
- [`release-engineering.md`](.codebuddy/references/release-engineering.md) —— 发布研究软件：消息与静默解决的普查、移植用的冻结特性矩阵、以哈希声明继承的测试、下游消费者按 commit SHA 钉版。

**我们如何写作** —— [`writing-with-ai.md`](.codebuddy/rules/writing-with-ai.md)：内部文档与对外文档的分野、为什么模型无法让自己的产出不再读起来像模型产出，以及任何署你名字的东西的可读标准。

**理论工作** —— [`theory-proving.md`](.codebuddy/references/theory-proving.md)：证明契约、用隔离探索者做组合搜索、给自己的引理找反例、对抗式审计，以及「AI 生成的证明是一个断言，不是一条定理」这条铁律。

**法则** —— [`research-agent-laws.md`](.codebuddy/references/research-agent-laws.md)：用代理跑科研基础设施的 21 条法则，每一条都由一次真实事故换来。

**我们如何记忆** —— 记录落在仓库里，不落在对话里：

- [`progress-reports.md`](.codebuddy/rules/progress-reports.md) —— GitHub issue 作缺陷记忆，`quality_reports/` 作工作记忆，`MEMORY.md` 作教训记忆。
- [`issue-ledger.md`](.codebuddy/rules/issue-ledger.md) —— 每一个已出库的 bug、被推迟的改进、卡住的所有者决策都开一个 GitHub issue，修好落地时手工关闭；取证标准与关闭评论的写法。
- [`repo-hygiene.md`](.codebuddy/rules/repo-hygiene.md) —— **草稿不许变成主干。** 每次提交由 `check-repo-hygiene.py` 强制。

任何工作要在 [`quality_reports/qualification/LEDGER.md`](quality_reports/qualification/LEDGER.md) 里有了一行才算清账 —— 跑 [`/vaccinate`](.codebuddy/skills/vaccinate/SKILL.md) 给它补一行。

---

## 目录结构

```
[YOUR-PROJECT]/
├── CODEBUDDY.md                 # 本文件（项目指令入口）
├── .codebuddy/                  # 规则、技能、代理、钩子
├── Bibliography_base.bib        # 集中管理的文献库
├── Figures/                     # 图与图片
├── Preambles/header.tex         # LaTeX 导言区
├── Slides/                      # Beamer .tex 文件
├── Quarto/                      # RevealJS .qmd 文件 + 主题
├── docs/                        # GitHub Pages（自动生成）
├── scripts/                     # 工具脚本 + 分析代码（按阶段编号）
├── output/                      # 生成的表格、图、日志（由代码创建）
├── quality_reports/             # 计划、会话日志、合并报告、决策记录
├── explorations/                # 研究沙盒（见规则）
├── templates/                   # 会话日志、质量报告模板
└── master_supporting_docs/      # 论文与既有幻灯片
```

---

## 命令

```bash
# LaTeX（三遍编译 + bibtex，只用 XeLaTeX；脚本负责平台相关的 TEXINPUTS/BIBINPUTS）
scripts/compile-beamer.sh file

# 把 Quarto 部署到 GitHub Pages
./scripts/sync_to_docs.sh LectureN

# 质量评分
python scripts/quality_score.py Quarto/file.qmd

# 调色板同步（LaTeX ↔ SCSS）
./scripts/check-palette-sync.sh

# 门禁总检：这个仓库内部自洽、并且当下为真吗？
# （surface-sync + skill-integrity + model-versions + links + spec-conformance
#   + staleness + repo-hygiene + derived-counts + ledger-coverage + hook-battery）
# 任何改动之后都跑一次。Python 版可跨平台，bash 版是上游原件。
python scripts/backtest.py
./scripts/backtest.sh
```

**调色板契约：** `Preambles/header.tex` 里的颜色名必须与 `Quarto/theme-template.scss` 的 SCSS 变量一致。见 [`Preambles/README.md`](Preambles/README.md)。

---

## 质量阈值（建议值）

| 分数 | 关卡 | 含义 |
|-------|------|---------|
| 80 | 提交 | 够格存下来 |
| 90 | PR | 可以部署 |
| 95 | 卓越 | 追求目标 |

由 `/commit` 强制（不达标即停并要求显式覆盖）**并且** —— 在你跑过 `./scripts/install-hooks.sh` 之后 —— 由真实的 git pre-commit 钩子（`.githooks/pre-commit`）强制：它在每次提交时跑 11 个门禁（仅当暂存区里有钩子、其 settings 或钩子回归集本身时才跑钩子回归集；CI 永远全跑）外加质量门禁（≥80）。要绕过请谨慎：`SKIP_QUALITY_GATE=1` 或 `--no-verify`。

---

## 技能速查

全部技能的总表在 [README.md](README.md#技能codebuddyskills)。按工作流分，最常用的：

- **幻灯片 / 教学：** `/create-lecture` `/compile-latex` `/deploy` `/qa-quarto` `/slide-excellence` `/syllabus` `/teach-from-paper` `/scaffold-exercises`
- **论文 / 审稿：** `/review-paper`（`--peer`）`/seven-pass-review` `/respond-to-referees` `/verify-claims` `/proofread` `/humanize` `/submission-disclosures`
- **数据 / 可复现性：** `/data-analysis` `/simulation-study` `/audit-reproducibility` `/diagnose` `/replication-package` `/capture-environment` `/power-analysis` `/disclosure-check`
- **研究 / 写作：** `/interview-me` `/lit-review` `/research-ideation` `/preregister` `/grant-proposal` `/data-management-plan`
- **验证 / 严谨性：** `/vaccinate` `/challenge` `/oracle-review` `/adjudicate-review` `/differential-audit` `/blast-radius` `/verify-artifact` `/credible-claims` `/deep-audit`
- **元 / 工作流：** `/commit` `/learn` `/new-skill` `/checkpoint` `/context-status` `/deep-audit` `/coauthor-brief` `/triage-inbox` `/issues`

Stata（`/stata-replication`）、R 包（`/r-package-check`）、TikZ（`/extract-tikz`、`/new-diagram`）等 —— 完整索引见 README。

---

## 平台约定（WorkBuddy 原生）

- **项目配置根是 `.codebuddy/`**：`rules/` `agents/` `skills/` `hooks/` `references/` `output-styles/`。
- **子代理模型只有三档**：`default` / `lite` / `reasoning`，另有 `effort:`（`minimal`–`max`）调同一档内的思考预算——代理可设、技能不可设。把认知需求映射到这两根轴，别再照搬 opus / sonnet / haiku 的说法。
- **规则按 `paths:` 实时生效**：改文件时匹配的规则即刻注入，不必重开会话。
- **计划文件落在用户级** `~/.workbuddy/plans/`；项目内留档用 `quality_reports/plans/`。
- **记忆落在** `.workbuddy/memory/YYYY-MM-DD.md`（按日追加）与 `.workbuddy/memory/MEMORY.md`（长期）。
- **钩子协议与上游一致**：`PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `SessionStart` / `PreCompact` / `Stop` / `Notification`，统一经 `.codebuddy/hooks/lib/hook-runner.sh` 入口调用。

---

<!-- 定制：把占位行（[your-env]、[.your-class]）换成你自己的。
     加完自己的之后，把标了「(示例 —— 删掉)」的行删掉。 -->

## Beamer 自定义环境

| 环境 | 效果 | 适用场景 |
| --- | --- | --- |
| `[your-env]` | [说明] | [什么时候用] |
| `keybox` | 金色底框 | 要点 *(示例 —— 删掉)* |
| `definitionbox[Title]` | 蓝色描边的带标题框 | 正式定义 *(示例 —— 删掉)* |

## Quarto CSS 类

| 类 | 效果 | 适用场景 |
| --- | --- | --- |
| `[.your-class]` | [说明] | [什么时候用] |
| `.smaller` | 字号 85% | 密集内容 *(示例 —— 删掉)* |
| `.positive` | 绿色加粗 | 正向注释 *(示例 —— 删掉)* |

---

## 当前项目状态

| 讲次 | Beamer | Quarto | 主要内容 |
| --- | --- | --- | --- |
| HelloWorld *(样例 —— 就绪后删掉)* | `HelloWorld.tex` | `HelloWorld.qmd` | 用来验证环境的最小幻灯片 |
| 1：[主题] | `Lecture01_Topic.tex` | `Lecture1_Topic.qmd` | [简要说明] |
