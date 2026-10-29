# 我的 WorkBuddy 配置

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Changelog](https://img.shields.io/badge/See-CHANGELOG-blue.svg)](CHANGELOG.md)
[![Contributing](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](.github/CONTRIBUTING.md)

> **持续维护中。** 一份我如何用 WorkBuddy 做学术工作的总结——幻灯片、论文、数据分析等等——打包成你可以直接 fork 的形态，用于你自己的研究。最新变更见 [CHANGELOG.md](CHANGELOG.md)。

**在线站点：** [sellyew.github.io/Workbuddy-workflow](https://sellyew.github.io/Workbuddy-workflow/)

一块可以直接 fork 的、AI 辅助学术工作的地基。你说出你想要什么——讲义幻灯片、一篇研究论文、一次数据分析、一个复现包——WorkBuddy 就规划做法、调度专职代理、修掉问题、核验质量、交付结果。像一个把整活全包下来的承包商。它源自一门真实开过的博士课程，并由一个不断壮大的[社区](#社区与扩展)持续扩展。

---

## 快速开始（5–10 分钟，首次安装另加约 30 分钟）

> **动手之前：** 最低要求是 WorkBuddy、git 与 Python 3。Python 3 负责跑钩子、门禁总检（`./scripts/backtest.sh`——11 个门禁）与质量打分器，macOS/Linux 上已预装。若要把自带的 `HelloWorld` 演示端到端跑通，还需要 XeLaTeX（Beamer 示例）与 Quarto（Quarto 示例）。推荐装 R 与 GitHub CLI。完整清单见下方[前置条件](#前置条件)。最快的路径：先克隆，再跑 `./scripts/validate-setup.sh`——它会逐项报告缺什么，并给安装链接。
>
> **只需要 Python/R/markdown？** 你不需要 XeLaTeX 或 Quarto。代理、规则、技能与编排模式对任何文本/代码产物都适用。跳过 `HelloWorld` 演示，直接去 `/data-analysis`、`/review-paper`、`/lit-review` 或 `/review-r`。
>
> **第二次会话起：** [MEMORY.md](MEMORY.md)（已提交）收集对所有 forker 都有帮助的通用 `[LEARN]` 条目；机器相关的笔记则累积在 WorkBuddy 的原生自动记忆里（`~/.workbuddy/projects/<project>/memory/`，本机存放，永不提交）。两者的区别见 [`.codebuddy/rules/meta-governance.md`](.codebuddy/rules/meta-governance.md)。

### 1. Fork 并克隆

```bash
# Fork this repo on GitHub (click "Fork" on the repo page), then:
git clone https://github.com/YOUR_USERNAME/Workbuddy-workflow.git my-project
cd my-project
./scripts/validate-setup.sh        # reports missing tools with install links
./scripts/install-hooks.sh         # activates the pre-commit gate on every commit
```

把 `YOUR_USERNAME` 换成你的 GitHub 用户名。

### 2. 在 WorkBuddy 里打开这个目录

新建任务，点输入框左下角的**选择工作空间**，选中刚才克隆的 `my-project` 目录，然后把下面的提示词粘进输入框。WorkBuddy 从工作空间的根目录读取 `.codebuddy/` 与 `CODEBUDDY.md`——在父目录里开会话，等于这些配置一份都没读到。

**用 VS Code？** 改用 WorkBuddy 面板打开即可。一切行为相同——细节见[完整指南](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#sec-setup)。

> **避开提示词疲劳。** 新的交互式会话默认以**自动模式**启动（由分类器把关——多数操作直接执行，有风险的才询问）；自动模式不可用时，手动模式会对每个有风险的工具调用逐次询问。若你仍看到过多询问，切换到**自动接受编辑**模式（一个快捷键；见指南的[权限模式一节](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#settings---permissions-and-hooks)），或在 WorkBuddy 里把模式切到「接受编辑」。**Bypass** 模式跳过权限询问与安全检查（拒绝规则仍然生效），Anthropic 把它限定在隔离容器与虚拟机内；它从 CLI 参数、`--settings` 或用户/托管设置（`~/.workbuddy/settings.json`）生效——写在项目 `.codebuddy/settings.json` 里的 bypass 默认值不被承认（会话以手动模式启动）。本模板的 `.codebuddy/settings.json` 不设默认模式（终端会话拿到平台的自动模式）；本仓库不提供 `.vscode/settings.json`：那几个键属于上游 Claude Code 的 VS Code 扩展，本客户端不读，留着只是一个不会生效的开关——另外 `.codebuddy/settings.json` 附带宽泛的兜底放行（`Bash(*)`、`Edit(**)`、`Write(**)`——7 条通配符规则，不是一份精选清单），所以在手动模式下几乎什么都不询问；自动模式会撤掉这条一刀切的 `Bash(*)`，改为把 shell 命令送进它的分类器。在处理受限数据？加上拒绝规则——见 [TROUBLESHOOTING](TROUBLESHOOTING.md#keep-restricted-data-off-the-model)。

然后从指南里粘贴[起始提示词](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#sec-first-session)，填上你的项目细节：

> 我正要在这个仓库里开始做 **[项目名]**。**[用 2–3 句话描述你的项目。]** 我已经搭好了 WorkBuddy 的学术工作流……请读这些配置文件，并为我的项目做适配。进入计划模式，开始。

[完整指南](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#sec-first-session)里有带全部细节的完整起始提示词。

**这一步做了什么：** WorkBuddy 读全部配置文件，填入你的项目名、机构与偏好，然后进入承包商模式——规划、实施，并在（你所调用技能的）范围内跑「审读 + 核验」循环。你批准计划、调用一项技能，剩下的由该技能在其范围内处理。

> **要把 CODEBUDDY.md 大幅改造成非学术项目？** 本平台的对应做法是 `/init-research-project`——它按你的项目信息填好 `CODEBUDDY.md` 里的占位符，并按学科裁剪规则与代理，作为起点。本模板预置的 CODEBUDDY.md 已经覆盖了学术场景——只有当你 fork 出来的东西差异很大时（例如一个不用 LaTeX 或 Quarto 的 Python/ML 项目）才需要它。

### 3. 验证你的环境

在动手做真正的讲义之前，先确认环境能用：

```bash
./scripts/validate-setup.sh        # Checks XeLaTeX, Quarto, Python, git, etc.
```

然后在 WorkBuddy 里：

```text
/compile-latex HelloWorld          # Compiles Slides/HelloWorld.tex to PDF
/deploy HelloWorld                 # Renders Quarto/HelloWorld.qmd to HTML
```

两项都成功的话，删掉 `Slides/HelloWorld.tex` 与 `Quarto/HelloWorld.qmd`，开始你的真实工作。

---

## 工作原理

### 目标优先、门禁兜底（v2.0 的转向）

你不需要打磨一条完美的提示词——你**说清目标，让工作在门禁之下朝目标循环推进**。专职代理干活；强制执行的门禁判定做得够不够好；它们暴露出来的分歧由你裁决。有三样东西让这件事可信：

- **真的门禁，不是提醒。** 一条命令——`./scripts/backtest.sh`——跑 **11 个门禁**：表面同步、技能完整性、模型版本对单一真源的时效性、链接与锚点解析、Agent Skills 规范合规、陈旧度（含源码与已发布版本之间的分歧）、仓库卫生、派生计数（可枚举断言按磁盘重算）、台账覆盖（资格台账与实际在跑的检查必须双向一致，且 settings 里声明的每一项钩子都必须存在且可调用——一个字符的路径笔误不再静默地让钩子失效）、一套带种子的钩子测试组（每次运行都把每个生效的防线钩子对着它所针对的失败重新触发一遍，并配上干净对照），以及一套可移植性回归集（路径、编码、行尾、git 输出在换一台机器之后仍然给出同一个答案；本机缺少对应机制而跑不到的用例会被逐条点名，并记成一次**有上限**的通过，而不是悄悄并进 PASS）。一个受版本控制的 pre-commit 钩子（跑一次 `./scripts/install-hooks.sh`）会在*每一次*提交上跑它，加上质量检查（≥80）（仅当有钩子、其 settings 或测试组本身被暂存时才跑钩子测试组；CI 永远全跑）——绕开技能不再绕开审读。`git-guardrails` 钩子拦下破坏性 git（`reset --hard`、`clean -f`、`push --force`、`add -A`），并在工作树脏时拒绝 merge、rebase 或 pull——它读的是当下的树，而不是去预测一条链式命令会对树做什么，所以 `git stash && git merge` 同样被拒，你得把这两步分开跑（确实要这么干就用 `ALLOW_DIRTY_MERGE=1`）；和它的兄弟一样，这是对命令行做文本检查，所以藏在解释器、别名或脚本里的操作在它视野之外，它的 docstring 写明了是哪些形式。它的兄弟 `root-of-trust-guard` 拒绝通往定义门禁本身那些文件的常见 shell 写入路径（`.codebuddy/settings*.json`、`.codebuddy/hooks/`、`.githooks/`）——重定向、`tee`、`cp`/`mv`/`rm`、就地 `sed`——并且因为它已经为这些规则拆开 `bash -c` 与 `env -S` 的载荷，它会把拆开的载荷交给*同一份*破坏性 git 拒绝清单，所以 `bash -c 'git reset --hard'` 与 `bash -c 'git clean -fdx'` 不再从这两道防线之间漏过去。**把它读作绊线，而不是锁；把它的名字读作文件名，而不是一句断言：**它是一次尽力而为的文本扫描，自身出错时放行，而它看守的文件仍可经本模板刻意允许的通道被替换——一次 `Edit`/`Write`/`MultiEdit`、一次分支切换、一次干净的合并，或钩子自身的 bug。它换来的是*通道*的改变——对门禁的改动以可审读的 diff 形式到达，而不是一次看不见的覆盖——而不是「门禁无法被禁用」的保证。这里也不做任何恢复：转录与 `git reflog` 只是审计轨迹与提交历史的辅助，两者都不持有未提交编辑或未跟踪文件的字节。评审运行时会把任何由审阅者引入的「fatal」发现再核验一遍，然后才计入。
- **门禁皆已合格化，而台账本身也是一道门禁。** 每一个都曾被植入一个缺陷、并确认会变红，其召回率与误报率记录在 [`quality_reports/qualification/LEDGER.md`](quality_reports/qualification/LEDGER.md)——而这份台账现在是真的承重的，不是愿景式的：一个已登记的检查若在那里没有对应行，构建就失败；某一行点名了一个不存在的检查器，同样失败。*尚未*合格化的检查会按名字列在那里，作为可见的欠账——因为一个未经合格化的检查不是弱证据，而是没有证据。跑 [`/vaccinate`](.codebuddy/skills/vaccinate/SKILL.md) 来合格化一个。
- **一套真的编排运行时。** 审读会扇出给 fork 出来的专职代理，按共享的发现 schema 归并，经幻觉门禁裁定，循环到空轮为止——见 [`orchestrator-protocol.md`](.codebuddy/rules/orchestrator-protocol.md)。
- **把真相当成一个流程。** 不一致并不总是失败：一个有据可依、*被点名*的替代做法记为 `EXPLAINED`，并带进你的回复审稿人函；而真正的错误仍然按失败关闭处理。

这**不是**一个自主守护进程——循环永远由你或某项技能发起，而你始终是审计者。定时自动化只处理周期性的杂活，且只在有发现时通知——云端 [Routines](.codebuddy/references/scheduled-routines.md) 用于已提交仓库的检查（每周文献增量），Desktop 定时任务用于任何触及本地数据的事（收件箱分诊，以及夜间的可复现性检查）。

### 承包商模式

你描述一个任务。对复杂或含糊的请求，WorkBuddy 先写一份需求规格，带 MUST/SHOULD/MAY 优先级与清晰度状态（CLEAR/ASSUMED/BLOCKED）。你批准规格，然后 WorkBuddy 规划做法并跑对的技能——或者，对 `/create-lecture` 这类由用户调用的技能，告诉你该跑哪一个（例如 `/create-lecture`、`/qa-quarto`、`/review-paper --adversarial`）。该技能在内部实现编排运行时——实施、核验、审读、修复、再核验、打分——并在工作达到质量标准时返回一份总结。说一句「直接干」，它就跑完整循环；提交仍然需要明确的 `/commit`（之后由 pre-commit 钩子把关）。

### 专职代理

不是一个通用审阅者，而是 18 个专注的代理，各查一个维度。几个有代表性的：

- **proofreader**——语法/错字
- **slide-auditor**——视觉布局
- **pedagogy-reviewer**——教学质量
- **r-reviewer**——R 代码质量
- **domain-reviewer**——领域内的正确性，面向幻灯片（模板——按你的领域定制）
- **domain-referee** / **methods-referee** / **editor**——稿件同行评审流水线（`/review-paper --peer`）

每个在自己那一小块上都强过通才。`/slide-excellence` 技能并行跑这些幻灯片审读代理；`/review-paper --peer` 跑论文审读流水线。同一个模式可推广到任何学术产物——稿件、数据流水线、项目申请书。

### 对抗式 QA

两个角色彼此对立：**critic** 同时读 Beamer 与 Quarto，产出尖刻的发现。**fixer** 精确实现 critic 找到的东西。它们**循环到空轮**——连续两轮不再冒出新问题即收敛（5 轮上限是退路，不是主要停止条件）。这能抓住单遍审读漏掉的错误。

### 质量审读

每个产物都会拿到一个分数（0–100）。低于阈值的分数会中止工作流并浮出审查发现——由用户决定是修还是明确覆盖：

- **80**——提交阈值
- **90**——PR 阈值
- **95**——卓越（愿景式）

> **关于表述的诚实：** 阈值在 harness 层面是建议性的——`/commit` 技能会跑质量检查并在失败时中止。**而且**，自 v2.0 起，跑一次 `./scripts/install-hooks.sh` 会装上一个真的 pre-commit 钩子（`.githooks/pre-commit`），它在*每一次*提交上跑门禁总检套件（仅当有钩子、其 settings 或测试组本身被暂存时才跑钩子测试组；CI 永远全跑）加上质量（≥80）门禁，所以绕开技能不再绕开审读。用 `SKIP_QUALITY_GATE=1` 或 `git commit --no-verify` 按次退出。

### 上下文存活

计划、规格与会话日志能挺过自动压缩与会话边界。PreCompact 钩子在 WorkBuddy 的自动压缩触发之前存下一份上下文快照，确保关键决策永不丢失。MEMORY.md 跨会话累积经验，于是在一个会话里发现的模式会滋养后续工作。

对*强制*压缩（长流水线、计划中途交接），`/compress-session`（v1.9.0）把对话蒸馏成一份结构化笔记——决策、下一步动作、以及**按噪声丢弃的东西**——而不是让自动压缩去截断。`/promote-memory`（v1.9.0）定期通过一个五评审议事会，把原生自动记忆里的通用经验收割进已提交的 MEMORY.md。

### 核验纪律（v1.7.0+）

提交之前会跑多个互补的核验层：

- **`/verify-claims`**（v1.7.0）——链式核验，配一个独立上下文的核验者，它没法自我确认，因为它从没见过草稿。v1.9.0 加入 HIGH/MED/LOW-WARN 严重度分级；HIGH-WARN 发现（伪造引用、数值矛盾）按失败关闭处理——草稿永远不会被报告为已核验；`/commit` 不读这些判定，所以提交前把它们处理掉是你的事。
- **`/audit-reproducibility`**（v1.4.0；Stata 覆盖 v1.9.0）——稿件里的每一条数值断言都要与产出它的脚本输出交叉核对。v1.9.0 加入 `passport.yaml`——一份按论文的 YAML 状态文件，逐条断言标 PASS/FAIL/STALE/UNVERIFIED。
- **`/humanize`**（v1.9.0）——在提交前检测 AI 腔的痕迹（套话过渡、限定词堆叠、谄媚）。按设计是只读的；自动重写会降低质量。
- **`/review-paper --peer <journal> --variance N`**（v1.9.0）——跑 N 位审稿人，审稿取向为抽样所得，并报告一个**判定分布**，而不是一个点估计。动机来自 AgentReview（EMNLP 2024）发现 37% 的判定纯粹因审稿取向抽样而变动。

---

## 指南

想要一份完整的走查，读[**完整指南**](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html)（或看[源码](guide/workflow-guide.qmd)）。

它涵盖：
1. **这套工作流为什么存在**——问题与愿景
2. **上手**——fork、粘一条提示词，剩下的 WorkBuddy 来搭
3. **系统如何运作**——专职代理、对抗式 QA、质量打分
4. **积木**——CODEBUDDY.md、规则、技能、代理、钩子、记忆
5. **工作流模式**——幻灯片、研究、可复现性、演示修辞、顺序对抗式审计等等
6. **生态**——来自 clo-author、claudeblattman、MixtapeTools、autoresearch、ClaudeCodeTools 的扩展，以及一个不断壮大的社区
7. **按你的领域定制**——造你自己的审阅者与知识库

### 2026 年的能力

指南覆盖本平台的最新能力：

- **模型档位**——本平台只有**三档**：`default`（审读与批评的默认档）、`lite`（机械劳动）、`reasoning`（高判断力：期刊编辑、审稿人、事实核查、对抗式批评、TikZ 空间推理）。没有第四档，也没有按型号点版本的阵容、价格表与别名表。各档的职责、上游层级怎么映射过来、怎么改档位，都在单一真源 [`model-versions.md`](.codebuddy/references/model-versions.md) 里——这里的表述停留在档位抽象上，所以不会过时；而单一真源自身的有效期一过，陈旧度门禁就会让构建失败。
- **没有 effort 轴**——本平台没有 `low` / `medium` / `high` / `xhigh` / `max` 这条 effort 轴，也没有 `maxEffortLevel` 这个天花板开关：深度由档位决定，要更少思考就降档，要更多就升档。frontmatter 里写着 `effort:` 不会报错，但也不会起作用——留着等于给自己一个假开关（见[模型单一真源](.codebuddy/references/model-versions.md)）。
- **`/goal <可核验条件>`**（v1.9.0；Anthropic 2026 年 5 月）——跨多轮持续工作，直到一个快模型确认条件成立。与 `/commit` 的质量门禁搭配，用于「核验过终态」的运行。
- **并行任务视图**——并行审读工作（`/review-paper --peer`、`/slide-excellence`）在侧边栏的任务列表里看。上游 CLI 有一个 `claude agents` 单屏仪表盘，本平台桌面端没有这条命令，也不需要它。
- **成本自觉的编排**——提示词缓存 TTL、70/20/10 模型路由（`lite` / `default` / `reasoning`）、`/cost` + `/usage` 监控。（上游订阅的额度池与缓存时长规则不适用于本平台，本仓库也不代为说明。）
- **技能 frontmatter**——`effort`、`context: fork`、`agent`、`hooks`、`disable-model-invocation`（v1.8.0+）、`disallowed-tools`（*真正的*工具限制——`allowed-tools` 只是预先批准）、`paths`（glob 作用域的自动激活）以及动态内容（`$ARGUMENTS`、`!command` 语法）
- **权限模式**——手动（配置值 `default`）、接受编辑、计划、**自动**（由分类器把关；新的交互式终端会话与 VS Code 会话都以它为内置起始模式）、Bypass
- **钩子处理类型**——command、prompt 与 HTTP 处理类型，配 20+ 钩子事件；钩子能看见 `effort.level` 与 `$CLAUDE_EFFORT`（2026 年 4 月第 19 周）
- **高级代理配置**——model、maxTurns、隔离、工具限制；`model-routing.md` 规则把逐代理的层级写成成文规定（v1.9.0）
- **Worktree 基线**（v1.9.0；Anthropic 2026 年 4 月）——`worktree.baseRef` 设定控制新 worktree 用 `fresh`（默认；远端默认分支）还是 `head`（本地 HEAD）
- **内置技能**——`/fewer-permission-prompts`、`/team-onboarding`、`/autofix-pr`、`/powerup`、Ultraplan、`/loop`（自我调速）
- **插件**——`/discover-plugins` 用来找第三方扩展
- **2026 年中的新增**（2026 年 6–9 月）——`/skill-doctor`（每项技能在上下文里花多少、多久触发一次）、插件评测（上游 `plugin eval`；本平台的对应工具是 `scripts/run-skill-eval.sh`，需另装 CodeBuddy Code CLI）、内置输出风格（**Concise** 用于日常；**Learning** 留一部分给你自己写——与 `/scaffold-exercises` 搭配）、子代理在后台运行且 fork 模式默认开启、`/fork`（在一个后台会话里继续对话的副本）、`/doctor`（配置体检），以及截止周用的 `autoUpdatesChannel: "stable"`

---

## 用例

| 学术任务 | 这套工作流如何帮忙 |
|---------------|----------------------|
| 讲义幻灯片（Beamer/Quarto） | 从创建、翻译、多代理审读到部署，全流程 |
| 研究论文 | 文献综述、稿件审读、模拟同行评审（`/review-paper --peer [journal]`）、审稿取向方差报告（`--variance N`） |
| 数据分析 | 端到端 R 流水线（`/data-analysis`），或经 `stata-mcp` 的 Stata 流水线（`/stata-replication`，v1.9.0）、复现核验、可直接发表的输出 |
| 蒙特卡洛模拟 | 可复现的模拟研究（`/simulation-study`，v1.10.0）——参数化 DGP、估计量网格、带蒙特卡洛标准误的偏差/RMSE/覆盖率/水平/功效，以及专门的 `sim-reviewer` 审读轮 |
| 包开发 | R 包发布门禁（`/r-package-check`，v1.10.0）——`devtools::document()` + 测试 + `R CMD check --as-cran` + CRAN 政策分诊 + `r-package-reviewer`（Stata / Python 检查在路线图上） |
| 复现包 | 符合 AEA 要求的打包、可复现性审计轨迹、`passport.yaml` 断言溯源（v1.9.0） |
| 演示 | 演示修辞原则、视觉审计、认知负荷审读 |
| 研究计划书 | 结构化起草，配对抗式批评 |
| 预注册 | 可直接提交 OSF / AsPredicted / AEA RCT Registry 的文档（`/preregister --style`）——完整工作流见模式 16 |
| 投稿纪律 | `/humanize`（检测 AI 腔）、`/verify-claims` 的 HIGH-WARN 失败关闭报告（伪造引用永远不会被报告为已核验）、审稿取向方差 |

**预置学科：** 经济学（Top-5 期刊画像、R 惯例）与政治学（APSR / AJPS / JOP 画像、形式理论 + 调查实验两类论文、conjoint/`cjoint` 惯例）。Forker 可通过期刊画像 + 论文类型 + 学科卡片扩展到心理学 / 社会学 / 公共卫生。

### 一个仓库，多种项目类型

这套工作流被设计成**一整个研究纲领的单一枢纽**——而不是一次处理一篇论文。同一份 `CODEBUDDY.md`、规则、代理与质量门禁同时服务课程与讲义、论文与审稿意见回复、数据分析与复现包、**蒙特卡洛模拟研究**（`/simulation-study` + `sim-reviewer`）以及 **R 包发布门禁**（`/r-package-check` + `r-package-reviewer`）——都是 v1.10.0 新增的。*在路线图上：* Stata / Python 包检查（SSC / PyPI）与个人生产力工作流。下一步做什么见 [`.codebuddy/references/v2.0-backlog.md`](.codebuddy/references/v2.0-backlog.md)。

---

## 包含什么

<details>
<summary><strong>本模板 19 个代理、63 个技能、37 条规则、11 个钩子</strong>（点击展开）</summary>

### 代理（`.codebuddy/agents/`）

<!-- surface-sync-table: agents -->
| 代理 | 它做什么 |
|-------|-------------|
| `proofreader` | 语法、错字、溢出、一致性审读 |
| `slide-auditor` | 视觉布局审计（溢出、字体一致性、间距） |
| `pedagogy-reviewer` | 13 种模式的教学法审读（叙事弧、记号密度、节奏） |
| `r-reviewer` | R 代码质量、可复现性与领域正确性 |
| `tikz-reviewer` | 毫不留情的 TikZ 图视觉批评 |
| `beamer-translator` | Beamer 到 Quarto 的翻译专家 |
| `quarto-critic` | 以 Beamer 为基准对比 Quarto 的对抗式 QA |
| `quarto-fixer` | 实现 critic 代理给出的修复 |
| `verifier` | 端到端的任务完成核验 |
| `domain-reviewer` | 你所在领域的实质审阅者的**模板** |
| `claim-verifier` (v1.7.0) | 在独立上下文里做链式核验的事实核查者（永远不是对话的 fork） |
| `editor` (v1.5.0) | 给 `/review-paper --peer` 用的期刊编辑（初审 + 选审稿人 + 综合） |
| `domain-referee` (v1.5.0) | `--peer` 模式下带审稿取向预设的实质审稿人 |
| `methods-referee` (v1.5.0+) | 认识论文类型的方法论审稿人（6 种论文类型） |
| `humanize-auditor` (v1.9.0) | 被 `/humanize` 调用的只读 AI 腔审计者 |
| `promote-memory-council` (v1.9.0) | 把 `[LEARN]` 条目提升进 MEMORY.md 的五评审议事会 |
| `sim-reviewer` (v1.10.0) | 蒙特卡洛模拟审阅者——DGP/估计目标匹配、蒙特卡洛标准误、覆盖率对真相、断言↔表格一致 |
| `r-package-reviewer` (v1.10.0) | R 包源码审阅者——DESCRIPTION/NAMESPACE 卫生、roxygen 完整性、testthat 覆盖率、CRAN 政策红旗 |
| `ping` | **Harness 自检**子代理：被派发时回传固定标记，用于确认 `.codebuddy/agents/` 真的会被发现并加载 |

### 技能（`.codebuddy/skills/`）

<!-- surface-sync-table: skills -->
| 技能 | 它做什么 |
|-------|-------------|
| `/init-research-project` | 把一个 fork 下来的模板初始化成真实项目：收齐项目信息、替换占位符、按学科裁剪规则、跑通环境自检、交出起步计划 |
| `/compile-latex` | 3 遍 XeLaTeX 编译，配 bibtex |
| `/deploy` | 渲染 Quarto + 同步到 GitHub Pages |
| `/extract-tikz` | TikZ 图到 PDF 再到 SVG 的流水线 |
| `/proofread` | 对某个文件启动 proofreader |
| `/visual-audit` | 对一套幻灯片做视觉布局审计（行内跑 `slide-auditor` 的那些检查） |
| `/pedagogy-review` | 对某个文件启动 pedagogy-reviewer |
| `/review-r` | 启动 R 代码审阅者 |
| `/qa-quarto` | 对抗式 critic-fixer 循环（循环到空轮；5 轮上限是退路） |
| `/slide-excellence` | 多代理联合审读 |
| `/translate-to-quarto` | 完整的 Beamer 到 Quarto 翻译——Phase 0 起飞前检查，加 12 个翻译阶段（1–11 以及一个 6.5 教学法审读） |
| `/vaccinate` | 测量某个检查、门禁或 AI 审阅者是否真能检出它针对的失败——植入缺陷 + 一个干净对照，把召回率与误报率写进资格台账 |
| `/adjudicate-review` | 把进来的审查发现——AI 审读、审稿意见、linter、第二个模型——变成已核验的修复。每条发现在对着源头查过之前都只是 CANDIDATE |
| `/blast-radius` | 改动任何共享之物（返回值、schema、默认值、单位）前后，枚举每一个消费方并真的把它们跑一遍 |
| `/credible-claims` | 委派之前写研究简报，之后写断言记录。免得「跑得更快」被误当成「证据可信」 |
| `/differential-audit` | 比较两套实现——一次移植、一次复现、一次重构、一次版本升级——让「一致」真的有含义 |
| `/oracle-review` | 跑一位外部前沿模型审稿人（WorkBuddy → 经 Oracle CLI 调另一家供应商的前沿模型），并对回来的东西做裁决 |
| `/verify-artifact` | 证明你即将发出的文件就是你以为的那个东西——重建、核验完整性、与源头比对 |
| `/voice-profile` | 从你自己以往的论文里抽出写作声音画像，再拿草稿对着它审——是 `/humanize` 的正面版本，后者只检测 AI 痕迹 |
| `/validate-bib` | 把引用与参考文献表交叉核对 |
| `/devils-advocate` | 在定下设计决策之前先挑战它 |
| `/create-lecture` | 完整的讲义创建工作流 |
| `/commit` | 跑门禁，然后在分支上提交；`--pr` 还会推送并开一个 PR。永不合并——合并等你点头 |
| `/lit-review` | 文献检索、综合与缺口识别 |
| `/research-ideation` | 生成研究问题与实证策略 |
| `/interview-me` | 通过交互式访谈把一个研究想法正式化 |
| `/review-paper` | 稿件审读：结构、计量、审稿人可能提的反对意见 |
| `/data-analysis` | 端到端 R 分析，输出可直接发表 |
| `/learn` | 把非显然的发现沉淀为可长期复用的技能 |
| `/context-status` | 显示会话健康度与上下文用量 |
| `/deep-audit` | 对一个理论、一个证明、一篇论文、一个代码库或一组断言做对抗式审计——拆解、独立怀疑者、每条发现配一位独立裁判、修复、再核验；全仓库一致性是它的一个应用 |
| `/permission-check` | 当询问或拦截意外出现时，读钩子链与本地覆盖，指出是哪条守卫拦的、以及哪些照上游写的开关在本平台根本不生效 |
| `/audit-reproducibility` | 对论文 ↔ 代码的数值断言强制执行容差阈值 |
| `/new-diagram` | 从片段库里搭一张 TikZ 图，带预防检查 + 审读 |
| `/respond-to-referees` | R&R 回复函生成器（把审稿意见映射到修改） |
| `/seven-pass-review` | 七遍对抗式稿件审读（并行 fork 子代理） |
| `/checkpoint` | 结构化的会话交接快照（状态 + 计划指针 + 下一步动作）。叙述式会话日志的搭档。 |
| `/preregister` | 从研究规格生成一份预注册文档（OSF / AsPredicted / AEA RCT Registry 风格） |
| `/verify-claims` (v1.7.0) | 链式核验式事实核查（独立上下文的核验者）。HIGH/MED/LOW-WARN 严重度分级（v1.9.0）；HIGH-WARN 在报告里按失败关闭（草稿永远不会被呈现为已核验）。 |
| `/humanize` (v1.9.0) | 检测学术散文里的 AI 腔痕迹（10 个检测类别；只读，不重写） |
| `/compress-session` (v1.9.0) | 在自动压缩之前，把当前会话蒸馏成结构化笔记（决策、下一步动作、*按噪声丢弃的东西*） |
| `/promote-memory` (v1.9.0) | 五评审议事会，投票决定哪些 `[LEARN]` 条目从原生自动记忆毕业进 MEMORY.md |
| `/stata-replication` (v1.9.0) | 经 `stata-mcp` MCP 服务器的端到端 Stata 流水线（为 R 优先的项目镜像 `/data-analysis`） |
| `/simulation-study` (v1.10.0) | 搭建并跑一项可复现的蒙特卡洛研究——参数化 DGP、估计量网格、带种子的重复、带蒙特卡洛标准误的偏差/RMSE/覆盖率/水平/功效 |
| `/r-package-check` (v1.10.0) | R 包发布门禁——`devtools::document()` + 测试 + `R CMD check --as-cran`，把 ERROR/WARNING/NOTE 对照 CRAN 政策分诊，再跑 `r-package-reviewer` |
| `/replication-package` (v2.0) | 组装一份可直接投稿的 DCAS / openICPSR 复现包——标准 README、数据集清单、计算环境要求留存、表/图 → 脚本:行号 映射、受限数据存缴说明（`/audit-reproducibility` 为 FAIL 时阻塞） |
| `/challenge` | 用你没做的那些选择去压测一个发现——在离散分叉上做设定曲线，再用命名敏感性统计量（E-value、Cinelli–Hazlett RV、Oster δ）对着识别假设盘问 |
| `/capture-environment` (v2.0) | 为复现包快照计算环境——renv.lock + sessionInfo.txt（R）、requirements.txt / environment.yml / uv.lock（Python）、Stata 版本 + ado 清单、种子/RNG、可选的钉版 Dockerfile |
| `/power-analysis` (v2.0) | 为研究设计算功效 / 所需样本量 / 最小可检出效应——两臂 RCT（聚类/ICC、不等分配）、多臂校正、非标准设计的基于模拟的功效；喂给 `/preregister` |
| `/disclosure-check` (v2.0) | 对受限/保密数据产出的统计披露限制预筛（小格子、互补抑制缺口、支配性、PII）；CRITICAL/WARNING/OK + 门禁 |
| `/grant-proposal` (v2.0) | 通过组合基元搭一份 NSF/NIH/ERC/基金会的项目申请书（规格 → 目标/方法，委派 DMP + 设施，一致性通读 + 要求清单） |
| `/data-management-plan` (v2.0) | 符合资助方要求的数据管理计划（NSF / NIH DMS 2023 / ERC / Horizon Europe）——并入避披露 + IRB 约束，以及一份复现包/环境计划；输出草稿 + 资助方清单 |
| `/coauthor-brief` (v2.0) | 合作者交接简报——自上次简报以来改了什么、逐产物状态、未决问题、本地复现 + 受限数据获取步骤 |
| `/triage-inbox` (v2.0) | 可定时的学术收件箱 + 日历分诊，经 Gmail/Calendar MCP——把审稿邀请、R&R/编辑、合作者往来、研讨会/会议邀请、经费与行政截止分类；每条各提一个需人放行的动作（起草回复、占用日历、搭一个审稿项目、`/coauthor-brief`、稍后提醒）；输出一份摘要 + 审稿义务跟踪表；MCP 缺席时优雅降级；永不自动发送 |
| `/diagnose` (v2.0) | 给一个错误/失败的实证结果找根因——有纪律的复现 → 最小化 → 提出假设 → 插桩 → 修复循环；为研究代码的 bug 调校（类型转换、NA/合并爆炸、聚类/标准误选择、种子/包版本漂移）；`--no-fix` 只定位不改动 |
| `/submission-disclosures` (v2.1) | 投稿时的披露段落：与目标期刊「已核验现行」政策匹配的 AI 使用披露、CRediT 贡献者角色、利益冲突、数据可得性声明（不是统计披露——那是 `/disclosure-check`） |
| `/syllabus` (v2.0) | 从一个主题或书单搭/重构一份课程大纲——课程描述 + 先修要求、逐周日程（主题→阅读→交付物）、可度量的学习目标、考核方案 + 评分细则、标准政策（迟交 / AI 使用 / 学术诚信 / 无障碍）、以及一份把各周映射到 `/create-lecture` 讲义的逐周工作表；懂经济学（博士计量/微观/宏观序列、本科） |
| `/teach-from-paper` (v2.0) | 端到端读一篇论文，并把它讲给指定受众层级——讲义大纲（动机 → 设定 → 关键结果 → 方法 → 要点）、值得讲的 3-5 个结果及直觉、给 `/create-lecture` 的幻灯片骨架、讨论问题，以及给 `/scaffold-exercises` 的习题集简报 |
| `/respond-to-eval` (v2.0) | `/respond-to-referees` 的教学版——把课程评价意见聚类成主题，按频次加权（信号 vs 噪声），分为 Keep / Change / Investigate / Out-of-scope，并起草映射到大纲 + 讲义的具体改动；把方案存到 `quality_reports/teaching/` |
| `/scaffold-exercises` (v2.0) | 跨解析/实证/编程三类题型搭一套计分习题集，带详解与「这为什么重要」的说明，输出到单独的答案册 |
| `/new-skill` (v2.0) | 搭一个遵循本仓库约定的新技能——就用途、触发词与工具做访谈，按模板写出 `.codebuddy/skills/<name>/SKILL.md`，其 frontmatter/正文一次通过 `check-skill-integrity.py`，随后提醒你补上表面表格的行 |
| `/issues` (v2.6) | 把 GitHub issues 当作项目的待办清单与记忆——每条已确认的发现，先在开着的与已关闭的 issue 里查重，再各自立一条；列出当前手头工作的未决项；关闭一条 issue 时用评论记下哪里错了、试过什么、怎么修的；每个草稿都先给你看，没有你的「可以」就什么都不发；往公开仓库发之前会警告 |
| `/hello` | **Harness 自检**技能：被调用时回传固定标记并写出 `quality_reports/checkpoints/_SMOKE_HELLO.md`，用于确认 `.codebuddy/skills/` 真的会被发现、`/name` 真的能触发 |

### 研究工作流

| 功能 | 它做什么 |
|---------|-------------|
| 探索目录 | 结构化的 `explorations/` 沙箱，带毕业/归档生命周期 |
| 快速通道工作流 | 快速原型用 60/100 的质量阈值 |
| 简化编排器 | 实施 → 核验 → 打分 → 完成（不做多轮审读） |
| 增强的会话日志 | 记录改动、决策、核验的结构化表格 |
| 只在合并时报告 | 质量报告只在合并时产出 |
| 数学行宽例外 | 有文档记录的公式允许长行 |
| 工作流速查 | 一页纸的速查表，位于 `.codebuddy/WORKFLOW_QUICK_REF.md` |

### 规则（`.codebuddy/rules/`）

规则按路径作用域加载：**常开**规则每个会话都加载；**按路径作用域**的规则只在 WorkBuddy 处理匹配文件时加载。指令文件越长，遵守度越差（官方指引：把 `CODEBUDDY.md` 控制在约 200 行以内），所以少即是多。

**常开**（无 `paths:` frontmatter——每个会话都加载）：

| 规则 | 它强制什么 |
|------|-----------------|
| `plan-first-workflow` | 非平凡任务进入计划模式 + 上下文保全 |
| `session-logging` | 三个记日志的触发点：计划后、增量、会话结束 |
| `progress-reports` | GitHub 当记忆——issue 是缺陷记忆，`quality_reports/` 是工作记忆，`MEMORY.md` 是教训记忆 |
| `repo-hygiene` | 草稿区不得变成主干——由 `check-repo-hygiene.py` 在每次提交时强制执行 |
| `prompt-shaping` (v2.0) | 日常习惯——动手之前先把随意/含糊的请求塑形（取代已退役的 `/prompt` + `/prompt-only` 技能） |

**按路径作用域**（只在处理匹配文件时加载）：

| 规则 | 触发于 | 它强制什么 |
|------|------------|-----------------|
| `orchestrator-protocol` | `.codebuddy/skills/`、`.codebuddy/agents/`、编排相关参考 | 目标优先的审读运行时：扇出 → 归并 → 裁定（+ 幻觉门禁）→ 空轮收敛——在编写扇出技能与审阅代理时加载；那些技能直接链接它 |
| `meta-governance` | 顶层文档、`guide/`、`docs/`、`templates/`、`.codebuddy/`、门禁脚本 | 模板与在用项目的区分——只用于维护者工作 |
| `verification-protocol` | `.tex`、`.qmd`、`docs/` | 任务完成清单 |
| `single-source-of-truth` | `Figures/`、`.tex`、`.qmd` | 不重复内容；以 Beamer 为准 |
| `quality-gates` | `.tex`、`.qmd`、`*.R` | 80/90/95 打分 + 容差阈值 |
| `r-code-conventions` | `*.R` | R 编码标准 + 数学行宽例外 |
| `tikz-visual-quality` | `.tex` | TikZ 图的视觉标准 |
| `beamer-quarto-sync` | `.tex`、`.qmd` | 把 Beamer 的改动自动同步到 Quarto |
| `pdf-processing` | `master_supporting_docs/` | 大 PDF 的安全处理 |
| `proofreading-protocol` | `.tex`、`.qmd`、`quality_reports/` | 先提议，经批准后再应用 |
| `no-pause-beamer` | `.tex` | Beamer 里不用 overlay 命令 |
| `replication-protocol` | `*.R` | 扩展之前先复现原始结果 |
| `knowledge-base-template` | `.tex`、`.qmd`、`*.R` | 记号/应用登记表的模板 |
| `orchestrator-research` | `*.R`、`explorations/` | 研究用的简化编排器（不做多轮审读） |
| `exploration-folder-protocol` | `explorations/` | 实验工作的结构化沙箱 |
| `exploration-fast-track` | `explorations/` | 轻量探索工作流（60/100 阈值） |
| `tikz-prevention` (v1.3.0) | `Slides/**`、`Figures/**`、`Preambles/**` | TikZ 起飞前 grep 检查（P3/P4 碰撞规避） |
| `agent-authored-code` (v2.5) | `**/*.sh`、`**/*.py`、`**/*.R`、`**/*.do` | 缺陷通常是我们的：任何批量编辑之前先试运行，在任何 `cd` 之前解析路径，用 PID 文件而不是 `pgrep` 监控，覆盖每一种终态 |
| `writing-with-ai` (v2.5) | `**/*.tex`、`**/*.qmd`、`**/*.md`、`**/*.Rmd` | 内部与对外文档之别；为什么模型无法让自己的输出不再像模型输出；可读的那条标准 |
| `issue-ledger` (v2.5) | `.github/**` | 哪些工作该立 GitHub issue（已发布的缺陷、推迟的改进、阻塞性的 owner 决策、每轮审读一条汇总 issue；绝不含受限数据），证据标准——分母、正/负对照、明确的非范围——以及关闭时的评论 |
| `tikz-measurement` (v1.3.0) | `Slides/**`、`Figures/**`、`Preambles/**`、`scripts/**` | 贝塞尔曲线深度计算 + 六遍碰撞协议（来自 MixtapeTools） |
| `content-invariants` (v1.6.x) | `.tex`、`.qmd`、`Preambles/`、`scripts/R/**` | 编号不变量 INV-1–INV-12（调色板同步、Beamer↔Quarto 记号一致、不用 overlay、每页最多两个 box、`set.seed` 只调一次、相对路径、……），critic 按编号引用它们 |
| `cross-artifact-review` (v1.4.0) | `master_supporting_docs/`、`.tex`、`.qmd` | 论文 ↔ 代码依赖图；自动调用 `/review-r` + `/audit-reproducibility` |
| `post-flight-verification` (v1.7.0) | 生成事实性断言的技能 | 链式核验协议，配一个独立上下文的核验者 |
| `summary-parity` (v1.7.0) | `CHANGELOG.md`、`README.md`、`.qmd`、技能/规则/代理的 `.md` | 反打地鼠：把摘要对着它的正文重新核验一遍 |
| `model-routing` (v1.9.0) | `.codebuddy/agents/**/*.md`、`.codebuddy/skills/**/SKILL.md` | 70/20/10 架构师/编辑分工（`lite` / `default` / `reasoning`） |
| `review-fencing` (v2.5.1) | `.tex`/`.qmd`、`master_supporting_docs/`、`quality_reports/` 审计目录、`claim-verifier.md` | 审阅者的独立性是环境的属性——在检出目录之外留一份中性副本、排除先前的判定、先给自读、把正对照与已提交的答案册隔开 |
| `stata-code-conventions` (v1.9.0) | `**/*.do`、`scripts/stata/**` | Stata 文件头骨架、编号流水线、esttab、聚类纪律、AEA 合规 |
| `simulation-conventions` (v1.10.0) | `**/*simulation*.R`、`**/*_sim.R`、`explorations/**` | 蒙特卡洛纪律：DGP/估计目标、L'Ecuyer 播种、蒙特卡洛标准误、覆盖率对真相、原始结果留存 |
| `r-package-conventions` (v1.10.0) | `R/**`、`tests/**`、`DESCRIPTION`、`NAMESPACE`、`man/**` | R 包源码标准：`R/` 里不用 `library()`、roxygen NAMESPACE、Imports/Suggests、testthat 3e、CRAN 政策 |
| `confidential-data` (v2.0) | `data/**`、`**/*.dta`、`**/restricted/**`、`**/confidential/**` | 受限/IRB 数据协议：绝不提交原始数据、发布前做披露清关、对受限数据安全的多作者 git 拓扑 |
| `inference-robustness` (v2.0) | `scripts/**/*.R`、`scripts/**/*.do`、`scripts/**/*.py` | 多重检验（FWER/Romano-Wolf vs FDR/Anderson 锐化 q，族要预注册）+ 设定曲线 / 逐一剔除 / wild-cluster bootstrap 稳健性 |

### 模板（`templates/`）

| 模板 | 它做什么 |
|----------|-------------|
| `session-log.md` | 结构化的会话日志格式 |
| `quality-report.md` | 合并时质量报告的格式 |
| `exploration-readme.md` | 探索项目的 README 模板 |
| `archive-readme.md` | 归档文档模板 |
| `requirements-spec.md` | MUST/SHOULD/MAY 需求框架，带清晰度状态 |
| `constitutional-governance.md` | 定义不可谈判原则与偏好之分的模板 |
| `skill-template.md` | 学术技能创建模板，带领域相关示例 |
| `decision-record.md` | 架构决策记录（ADR）模板 |
| `journal-profile-template.md` | 供 `/review-paper --peer` 编辑校准用的期刊画像 |
| `preregistration-template.md` (v1.8.0) | 预注册文档骨架（OSF / AsPredicted / AEA RCT） |
| `passport-template.yaml` (v1.9.0) | 逐论文的 YAML 护照，记录数值断言的溯源（`/audit-reproducibility` 使用） |
| `response-to-referees.md` | R&R 回复文档骨架 |
| `executor-contract.md` (v2.5.1) | 给被委派任务的可派发目标契约——目标、验收门槛、确切路径、必须通过的门禁、输出契约，以及执行者可拒绝的机制 |
| `screening-rubric.md` (v2.5.1) | 筛选评分细则——在筛选跑起来之前写好，带逐候选证据、一张裁决表与一次派发者抽查 |

</details>

---

## 前置条件

| 工具 | 用于 | 安装 |
|------|-------------|---------|
| WorkBuddy（本平台客户端） | 全部 | 随客户端安装——本仓库不代管产品安装链接 |
| git | 克隆 + 版本控制 | [git-scm.com](https://git-scm.com/downloads) |
| Python 3 (3.9+) | 内部检查器（调色板同步、TikZ 预防） | macOS/Linux 已预装；Windows 见 [python.org](https://www.python.org/) |
| XeLaTeX | LaTeX 编译（Beamer `HelloWorld`、真实讲义） | [TeX Live](https://tug.org/texlive/) 或 [MacTeX](https://tug.org/mactex/) |
| [Quarto](https://quarto.org) | 网页幻灯片（Quarto `HelloWorld`、真实讲义） | [quarto.org/docs/get-started](https://quarto.org/docs/get-started/) |
| R | 图与分析（`/data-analysis`、`scripts/R/` 模板） | [r-project.org](https://www.r-project.org/) |
| pdf2svg | 为 Quarto 把 TikZ 转 SVG（`/extract-tikz`） | `brew install pdf2svg`（macOS）、`apt install pdf2svg`（Debian） |
| [gh CLI](https://cli.github.com/) | PR / issue 工作流 | `brew install gh`（macOS）、`apt install gh`（Debian） |
| Playwright for Python（可选） | 浏览器实测的幻灯片 QA（`scripts/slide-qa.py`，由 `/visual-audit`、`/qa-quarto`、`/slide-excellence` 调用）；驱动你已安装的 Chrome | `python3 -m venv ~/.venvs/slide-qa && ~/.venvs/slide-qa/bin/pip install playwright`，然后 `export SLIDE_QA_PYTHON=~/.venvs/slide-qa/bin/python` |

**fork 本模板的最低要求：** WorkBuddy + git + Python 3（macOS/Linux 上 Python 已经装好了）。

**把自带 HelloWorld 演示端到端跑通的最低要求：** 加上 XeLaTeX（用于 `/compile-latex HelloWorld`）与 Quarto（用于 `/deploy HelloWorld`）。

**你的真实讲义可能还需要更多**——`scripts/R/` 分析要 R；用 TikZ 提取就要 pdf2svg；用基于 PR 的提交流程就要 gh CLI；想在浏览器里测幻灯片溢出的就要 Playwright。`./scripts/validate-setup.sh` 会报告 R、gh CLI 与 Playwright 是否已装；它不检查 pdf2svg（用 `command -v pdf2svg` 查）。

---

## 按你的领域做适配

1. **填好知识库**（`.codebuddy/rules/knowledge-base-template.md`），写入你的记号、应用与设计原则
2. **定制领域审阅者**（`.codebuddy/agents/domain-reviewer.md`），换上你所在领域特有的审读透镜
3. **更新调色板**——这是一份**双面契约**：同时改动 [`Preambles/header.tex`](Preambles/header.tex)（Beamer/TikZ）**与** [`Quarto/theme-template.scss`](Quarto/theme-template.scss)（Quarto 幻灯片）顶部的 HEX 值，让两边一致。然后跑 `./scripts/check-palette-sync.sh` 核验。漏掉一面会静默产出 Beamer 与 Quarto 渲染不一致。完整契约与 TikZ 样式库见 [`Preambles/README.md`](Preambles/README.md)。
4. **补上领域特有的 R 坑**，写进 `.codebuddy/rules/r-code-conventions.md`
5. **填好讲义映射**，写在 `.codebuddy/rules/beamer-quarto-sync.md`
6. **定制工作流速查**（`.codebuddy/WORKFLOW_QUICK_REF.md`），写入你的不可谈判项与偏好
7. **搭好探索目录**（`explorations/`），用于实验性工作

---

## 更多资源

- 如何写好 CODEBUDDY.md——指令文件的加载方式、体积上限与两层记忆的分工，见 [`.codebuddy/rules/meta-governance.md`](.codebuddy/rules/meta-governance.md)

---

## 由来

本仓库是 [`pedrohcgs/claude-code-my-workflow`](https://github.com/pedrohcgs/claude-code-my-workflow) 的中文移植版——把同一套基础设施改用 WorkBuddy 平台，并翻成中文，作为个人学习用途维护。方法、设计与原创内容归原作者 Pedro H. C. Sant'Anna；要引用这套工作流本身，请引用那个原始仓库（`CITATION.cff` 指向它）。

原始基础设施提取自 Emory University 的 **Econ 730: Causal Panel Data** 课程，由 Pedro Sant'Anna 用 Claude Code 在 6 个以上会话里开发而成。那门课产出了 6 套完整的博士讲义、带 plotly 图表的交互式 Quarto 版本，以及完整的 R 复现包——全部通过这套多代理工作流管理。这些模式与领域无关：同样的代理、规则与编排器，对任何学术项目都适用。

---

## 社区与扩展

经济学、能源、政治学与工程学的研究组都 fork 并改造过这套工作流——**2026 年 3 月的调查里有 15+ 个研究组**；此后**上游仓库**已越过 **2,900 次 fork** 与 1,500 颗星（GitHub，2026-08-24——一次 fork 不等于一个研究组，所以调查数字与 fork 数要当成两回事来读）。基础设施（编排器、钩子、质量门禁）无需改动即可迁移。

**扩展工作流：**

- **[clo-author](https://github.com/hugosantanna/clo-author)**，作者 Hugo Sant'Anna（UAB）——以论文为中心的研究工作流，带 21 个专职代理（7 对 worker-critic，加上审稿人、数据工程师、核验者）、模拟盲审、AEA 复现合规与完整的研究生命周期管理。**本模板里的 `/review-paper --peer <journal>` 流水线经 Hugo 许可改编自 clo-author**（流水线形态、六路审稿取向分类、期刊校准 schema、论文类型分支）。谢谢 Hugo。
- **[claudeblattman](https://github.com/chrisblattman/claudeblattman)**，作者 Chris Blattman（U Chicago）——写给非技术型学者的综合指南：行政助理工作流、项目申请书写作、并行批评者配独立综合、自我改进的配置
- **[MixtapeTools](https://github.com/scunning1975/MixtapeTools)**，作者 Scott Cunningham（Baylor）——演示的修辞：漂亮、修辞上有效的学术报告的理念与实践
- **[autoresearch](https://github.com/karpathy/autoresearch)**，作者 Andrej Karpathy——以 `program.md` 为宪制文件的、基于约束的自主研究
- **[ClaudeCodeTools](https://github.com/aspi6246/ClaudeCodeTools)**——「The Editor」人格：七审顺序式论文审读协议

详细描述、设计原则与更多资源见[指南的生态一节](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#sec-ecosystem)。

---

## 版本与贡献

- **有什么新东西：** 见 [CHANGELOG.md](CHANGELOG.md)。我们遵循宽松的 semver——破坏性变更会跳大版本，好让你自己决定什么时候拉更新。
- **怎么贡献：** 见 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)。欢迎针对可推广改进的 PR；fork 特有的工作留在你自己的 fork 里。
- **钉到某个版本：** `git checkout $(git describe --tags --abbrev=0)` 钉到最新的发布标签；每个版本包含什么见 [CHANGELOG.md](CHANGELOG.md)。

---

## 许可

MIT License。见 [LICENSE](LICENSE)。
