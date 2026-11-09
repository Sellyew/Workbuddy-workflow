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

**只做用户要求的事，不要扩大范围。** 不要附带修改 README、构建脚本或 `.gitignore`，也不要添加辅助工具和其他未要求的脚手架。如果某个补充确有价值，**把它作为建议列在最后**，由用户决定是否采用。

用户要求一份 codebook，就只交付 codebook。若同时交付 README、构建脚本和 .gitignore 改动，用户就要为了一项需求审查四项改动，往往会全部放弃。

**添加任何超出请求的内容之前，先询问用户。** 先问一句，比事后回滚更省事。

---

## 核心原则

- **先计划后执行**：非平凡任务先进入计划模式，计划存到 `quality_reports/plans/`
- **改完要验**：改动 `.tex` 后必须实际编译，改动 `.qmd` 后必须实际渲染，改动 `.R` 后必须实际运行；都要核对输出，确认结果正确才可报告完成
- **单一真源**：Beamer `.tex` 是权威源，Quarto `.qmd` 由它派生
- **质量门禁**：低于 80/100 不得交付
- **[LEARN] 标签**：被纠正时记录 `[LEARN:category] 错 → 对`；适用于所有模板使用者的通用经验，经人工筛选后写入根 [MEMORY.md](MEMORY.md)

跨会话上下文分三层。根 [MEMORY.md](MEMORY.md) 保存人工筛选、可提交的通用经验；原生自动记忆位于用户级 `~/.workbuddy/projects/<project>/memory/`；项目内 `.workbuddy/memory/` 保存本仓库的按日工作日志与本机状态。最后一层已被 gitignore 排除，应保留在本机但不提交。历史计划、需求说明与其他会话日志位于 [quality_reports/](quality_reports/)。

**我们如何验证**：以下参考文件与规则规定了验证要求：

- [`verification-ladder.md`](.codebuddy/references/verification-ladder.md)：7 级阶梯说明如何验证检查器、引入外部裁判，以及让审读循环收敛。
- [`external-oracle-process.md`](.codebuddy/references/external-oracle-process.md)：说明如何通过 Oracle CLI 调用另一家厂商的前沿模型作为独立裁判，以及如何裁决它返回的结果。当前目标见其 §2。
- [`provenance-and-ground-truth.md`](.codebuddy/references/provenance-and-ground-truth.md)：说明如何命名裁判并固定版本、如何给分歧分类，以及净室边界。
- [`review-fencing.md`](.codebuddy/rules/review-fencing.md)：通过环境保证审阅独立，而不是只提醒审阅者保持独立。具体做法包括在检出目录之外保存未受审读影响的副本、不提供此前的裁决，并隔离仓库中已提交的标准答案文件。
- [`release-engineering.md`](.codebuddy/references/release-engineering.md)：研究软件的发布要求，包括普查用户消息和静默决策、为移植冻结特性矩阵、按名称和哈希声明继承的测试，以及让下游消费者按 commit SHA 固定版本。

**我们如何写作**：[`writing-with-ai.md`](.codebuddy/rules/writing-with-ai.md) 区分内部文档与对外文档，解释为什么模型无法让自己的产出不再像模型产出，并规定任何署你名字的文档应达到的可读性标准。

**理论工作**：[`theory-proving.md`](.codebuddy/references/theory-proving.md) 规定证明契约，说明如何用隔离的探索者做组合搜索、为自己的引理寻找反例，以及开展对抗式审计。AI 生成的证明只是一个断言，不能直接当作定理。

**法则**：[`research-agent-laws.md`](.codebuddy/references/research-agent-laws.md) 总结了用代理运行科研基础设施的 21 条法则，每条都来自真实事故。

**我们如何记忆**：记录应写入磁盘，不能只留在对话里。通用经验与本机日志分层存放：

- [`progress-reports.md`](.codebuddy/rules/progress-reports.md)：GitHub issue 记录缺陷，`quality_reports/` 记录工作过程，`MEMORY.md` 记录经验教训。
- [`issue-ledger.md`](.codebuddy/rules/issue-ledger.md)：每个已发布的 bug、推迟的改进和因等待负责人决定而受阻的事项都要创建 GitHub issue，修复完成后手工关闭。文件还规定取证标准与关闭评论的写法。
- [`repo-hygiene.md`](.codebuddy/rules/repo-hygiene.md)：**草稿不得进入主干。** 每次提交由 `check-repo-hygiene.py` 强制检查。

任何被用于放行工作的检查器、门禁或审读代理，都必须在 [`quality_reports/qualification/LEDGER.md`](quality_reports/qualification/LEDGER.md) 中有台账行。缺少记录时，运行 [`/vaccinate`](.codebuddy/skills/vaccinate/SKILL.md) 补充。

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

# 门禁总检：检查仓库内部是否自洽、各项描述当前是否仍然成立
# （surface-sync + skill-integrity + model-versions + links + spec-conformance
#   + staleness + repo-hygiene + derived-counts + ledger-coverage + hook-battery
#   + portability + slide-content）
# 任何改动之后都跑一次。Python 与 Bash 是同一实现的两个入口。
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

`/commit` 会强制执行质量阈值，不达标就停止，只有显式豁免才能继续。运行 `./scripts/install-hooks.sh` 后，git pre-commit 钩子 `.githooks/pre-commit` 也会在每次提交时检查 12 个门禁和质量分数，质量分数须 ≥80。只有暂存区包含钩子、对应 settings 或钩子回归集本身时，才运行钩子回归集；CI 始终全部运行。请谨慎使用 `SKIP_QUALITY_GATE=1` 或 `--no-verify` 绕过检查。

---

## 技能速查

全部技能见 [README.md](README.md#技能codebuddyskills) 的总表。**技能如何导入、新建和使用，见 [README.md](README.md#技能导入与使用)。** 以下按工作流列出最常用的技能：

- **幻灯片 / 教学：** `/create-lecture` `/compile-latex` `/deploy` `/qa-quarto` `/slide-excellence` `/syllabus` `/teach-from-paper` `/scaffold-exercises`
- **论文 / 审稿：** `/review-paper`（`--peer`）`/seven-pass-review` `/respond-to-referees` `/verify-claims` `/proofread` `/humanize` `/submission-disclosures`
- **数据 / 可复现性：** `/data-analysis` `/simulation-study` `/audit-reproducibility` `/diagnose` `/replication-package` `/capture-environment` `/power-analysis` `/disclosure-check`
- **研究 / 写作：** `/interview-me` `/lit-review` `/research-ideation` `/preregister` `/grant-proposal` `/data-management-plan`
- **验证 / 严谨性：** `/vaccinate` `/challenge` `/oracle-review` `/adjudicate-review` `/differential-audit` `/blast-radius` `/verify-artifact` `/credible-claims` `/deep-audit`
- **元 / 工作流：** `/commit` `/learn` `/new-skill` `/checkpoint` `/context-status` `/deep-audit` `/coauthor-brief` `/triage-inbox` `/issues`

Stata 使用 `/stata-replication`，R 包使用 `/r-package-check`，TikZ 使用 `/extract-tikz`、`/new-diagram`。完整索引见 README。

---

## 平台约定（WorkBuddy 原生）

- **项目配置根是 `.codebuddy/`**：其中包括 `rules/` `agents/` `skills/` `hooks/` `references/` `output-styles/`。
- **官方支持项目技能**：`.codebuddy/skills/` 随仓库共享，项目级技能优先于用户级技能，用户技能库可跨项目使用。从市场安装、上传或用通用创建器创建的技能，默认进入用户技能库；若要随仓库共享，必须显式放进项目目录。
- **两个创建入口分工不同**：`/new-skill` 是本仓库的项目技能，按本仓库约定生成项目技能；WorkBuddy 内置 `/skill-creator` 是通用创建器，GUI 入口为技能 → 添加技能 → 创建技能。
- **技能按需加载**：元数据用于匹配，正文在触发时加载，附属材料按需读取。UI 或菜单不显示某项技能，不代表它无法被发现或通过 `/name` 调用。
- **热重载未证实**：不要写「无需重启」。若实际运行没有采用新正文，记录客户端与技能版本，再新开会话复测。
- **`allowed-tools` 是工具白名单**：它限制技能可以调用的工具，只应列出实际需要的工具。它不是绝对安全边界，模型行为、权限规则与钩子仍须核验；目前没有 L3 证据表明桌面端存在相反行为。
- **子代理模型只有三档**：`default` / `lite` / `reasoning`。`effort:` 可取 `minimal`–`max`，用于调整同一档内的思考预算；代理可以设置，技能不能设置。应根据任务的认知需求选择模型档位与 effort，不要照搬 opus / sonnet / haiku 的说法。
- **规则按 `paths:` 实时生效**：修改文件时，匹配的规则会立即注入，不必重开会话。
- **计划文件保存在用户级** `~/.workbuddy/plans/`；项目内留档使用 `quality_reports/plans/`。
- **记忆分三层**：根 `MEMORY.md` 保存人工筛选、可提交的通用经验；原生自动记忆位于用户级 `~/.workbuddy/projects/<project>/memory/`；项目内 `.workbuddy/memory/YYYY-MM-DD.md` 等文件保存本仓库的按日工作日志与本机状态。最后一层已被 gitignore 排除，应保留在本机但不提交。
- **钩子协议与上游一致**：`PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `SessionStart` / `PreCompact` / `Stop` / `Notification` 都统一通过 `.codebuddy/hooks/lib/hook-runner.sh` 入口调用。

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
