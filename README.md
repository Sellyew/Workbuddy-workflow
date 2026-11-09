# WorkBuddy 学术工作流：非官方中文移植

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

![Changelog](https://img.shields.io/badge/See-CHANGELOG-blue.svg)

![Contributing](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

> **持续维护中。** 本仓库是 [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow) 的非官方 WorkBuddy 中文移植。上游工作流的方法与设计来自 Pedro H. C. Sant'Anna；Sellyew 负责中文翻译、WorkBuddy 适配和维护。这个可直接 fork 的模板涵盖幻灯片、论文和数据分析等任务，你可以用它搭建自己的研究流程。最新变更见 [CHANGELOG.md](CHANGELOG.md)。

**在线站点：** [sellyew.github.io/Workbuddy-workflow](https://sellyew.github.io/Workbuddy-workflow/)

你可以 fork 这个模板，用 AI 辅助学术研究。无论是讲义幻灯片、研究论文、数据分析还是复现包，你只需说明目标，WorkBuddy 就会规划步骤、调度专职代理、修复问题并核验质量。你负责审查结果，裁决审读中暴露的分歧。原工作流来自原作者开设的一门博士课程，上游[社区](#社区与扩展)也在持续扩展它。

---

## 快速开始（5–10 分钟，首次安装另加约 30 分钟）

> **动手之前：** 最低要求是 WorkBuddy、git 与 Python 3。Python 3 用来运行钩子、质量打分器和门禁总检。门禁总检由 `./scripts/backtest.sh` 启动，共 12 个门禁。macOS/Linux 通常预装 Python 3，但仍需确认它能实际运行。若要完整运行自带的 `HelloWorld` 演示，还需要 XeLaTeX 和 Quarto，分别用于 Beamer 与 Quarto 示例。建议同时安装 R 与 GitHub CLI，完整清单见下方[前置条件](#前置条件)。最快的做法是先克隆，再运行 `./scripts/validate-setup.sh`。脚本会逐项报告缺少的工具，并给出安装链接。
>
> **只需要 Python/R/markdown？** 你不需要 XeLaTeX 或 Quarto。代理、规则、技能与编排模式也适用于其他文本和代码产物。跳过 `HelloWorld` 演示，直接使用 `/data-analysis`、`/review-paper`、`/lit-review` 或 `/review-r`。
>
> **第二次会话起：** 你会用到三层记忆。根 [MEMORY.md](MEMORY.md) 保存**人工筛选、可提交**的通用 `[LEARN]` 经验；WorkBuddy 原生自动记忆位于用户级 `~/.workbuddy/projects/<project>/memory/`，保存与机器和用户有关的经验；项目内 `.workbuddy/memory/` 保存本仓库的按日工作日志与本机状态。最后一层已被 gitignore 排除，请保留在本机，不要删除或提交。三者的区别见 [`.codebuddy/rules/meta-governance.md`](.codebuddy/rules/meta-governance.md)。

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

新建任务，点击输入框左下角的**选择工作空间**，选中刚才克隆的 `my-project` 目录，再把下面的提示词粘进输入框。WorkBuddy 只从工作空间根目录读取 `.codebuddy/` 与 `CODEBUDDY.md`。如果你在父目录中开会话，这些配置就不会加载。

**用 VS Code？** 可以用 VS Code 编辑项目文件，但 WorkBuddy 会话要在桌面客户端新建，并选择同一个项目目录。这里只给出桌面客户端的操作步骤。CodeBuddy 的 VS Code 插件是另一套产品。细节见[完整指南](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#sec-setup)。

> **减少权限询问。** WorkBuddy 桌面端只有两档权限，可在输入框旁的选择器中切换。**默认权限**按照 `.codebuddy/settings.json` 的 `permissions.allow` 放行常规操作，超出范围时仍会询问。**完全访问权限**跳过询问与安全检查，但 `deny` 规则与钩子仍然生效。只有在仓库可信且你清楚后果时，才使用后者。上游 Claude Code / CLI 文档里的「自动」「接受编辑」「Bypass」等属于另一产品线，不是桌面端的档位或操作步骤。本模板附带宽泛的兜底放行，包括 `Bash(*)`、`Edit(**)`、`Write(**)` 等 7 条通配符规则，所以默认权限下多数常规工作也不会询问。处理受限数据时，请另加拒绝规则，见 [TROUBLESHOOTING](TROUBLESHOOTING.md#让受限数据不进入模型)。

然后从指南里粘贴[起始提示词](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#sec-first-session)，填上你的项目细节：

> 我正要在这个仓库里开始做 **[项目名]**。**[用 2–3 句话描述你的项目。]** 我已经搭好了 WorkBuddy 的学术工作流……请读这些配置文件，并为我的项目做适配。进入计划模式，开始。

[完整指南](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#sec-first-session)里有带全部细节的完整起始提示词。

**这一步做了什么：** WorkBuddy 按需读取相关配置文件，填入你的项目名、机构与偏好，然后规划并执行任务。在你调用的技能范围内，它还会反复审读和核验。你批准计划并调用技能后，该技能会处理其职责范围内的后续工作。

> **要把 CODEBUDDY.md 大幅改造成非学术项目？** 本平台提供 `/init-research-project`。它根据你的项目信息填写 `CODEBUDDY.md` 里的占位符，并按学科调整规则与代理，供你继续修改。本模板预置的 CODEBUDDY.md 已覆盖学术场景。只有项目与学术场景差异很大时才需要它，例如不用 LaTeX 或 Quarto 的 Python/ML 项目。

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

## 技能：导入与使用

`.codebuddy/skills/` 是 WorkBuddy 官方支持的**项目技能**目录，其中的技能随仓库共享。项目级技能优先于用户级技能，用户技能库则可跨项目复用。本模板的项目技能位于 `.codebuddy/skills/<name>/SKILL.md`，fork 仓库后会一并获得。

- **怎么用（含本机 GUI 观察）**：输入 `/name` 显式触发，如 `/compile-latex HelloWorld`；也可以直接描述需求，让 WorkBuddy 自动匹配并调用。本机 GUI 观察中，自动补全列表未列出项目技能，但完整输入 `/hello` 后返回 `SKILL-SMOKE-OK`，并写出核验文件。列表不显示时仍可直接输入，无需重复安装，也无需把项目技能复制到用户技能库。
- **怎么自动匹配**：在本机 `.codebuddy/settings.local.json` 顶层设置 `"enableAllProjectSkills": true`，重新打开项目并新建会话；出现项目信任或技能批准提示时先完成批准。标有 `disable-model-invocation: true` 的技能只能显式调用。
- **有哪些**：下方「技能」总表逐项说明。
- **怎么新建**：本仓库的 `/new-skill` 是项目技能，负责按本仓库约定生成项目技能；WorkBuddy 内置的 `/skill-creator` 则是通用创建器，GUI 入口为**技能 → 添加技能 → 创建技能**。也可以把 `templates/skill-template.md` 复制到 `.codebuddy/skills/<name>/SKILL.md`。
- **怎么导入第三方**：从市场安装、上传或用通用创建器创建的技能，默认进入用户技能库，不会自动进入当前项目的 `.codebuddy/skills/`。若要随仓库共享，必须显式把技能放进项目目录。
- **怎么加载**：WorkBuddy 用技能元数据匹配需求，在触发时加载正文，并按需读取附属材料，不会每轮都从磁盘读取所有描述。

`allowed-tools` 是官方定义的工具白名单，只应列出技能实际需要的工具。它限制技能可以调用哪些工具，却不是绝对的安全边界；你仍需核验模型行为、权限规则和钩子。当前没有 L3 证据表明桌面端存在相反行为。技能修改后是否会热重载尚未证实，不要假定无需重启。若实际运行没有采用新正文，记录客户端与技能版本，再新开会话复测。字段写法见单一真源 [`.codebuddy/references/skill-fields.md`](.codebuddy/references/skill-fields.md)。

---

## 工作原理

### 目标优先、门禁兜底（v2.0 的转向）

你不必先写出完美的提示词。只要**说清目标，WorkBuddy 就能在门禁约束下反复推进工作**。专职代理负责执行，门禁检查结果是否合格，你裁决审读中发现的分歧。这套流程依靠以下四项机制：

- **门禁会实际执行，不只是提醒。** 运行 `./scripts/backtest.sh` 会执行 **12 个门禁**，检查表面同步、技能完整性、模型版本是否跟得上单一真源、链接与锚点解析、Agent Skills 规范合规、陈旧度、仓库卫生、派生计数、台账覆盖、钩子测试、可移植性和幻灯片内容不变量。

  陈旧度检查包括源码与已发布版本之间的分歧；派生计数按磁盘内容重算可枚举断言。台账覆盖要求资格台账与实际运行的检查双向一致，也要求 settings 声明的每个钩子都存在且可调用。路径错一个字符，也不会再让钩子静默失效。

  带固定种子的钩子测试组会让每个生效的防线钩子重新面对它要拦截的失败，同时运行无缺陷对照。可移植性回归集检查路径、编码、行尾和 git 输出在换机器后是否仍给出相同答案。本机缺少对应机制而无法运行的用例会逐条列出，并记为**有上限**的通过，不会悄悄并入 PASS。

  幻灯片内容不变量检查会确认每个引文键都能在唯一的文献库中解析，并检查每页彩色框是否超过 2 个。此前，这两条只有文字要求，没有脚本计数。运行一次 `./scripts/install-hooks.sh` 后，受版本控制的 pre-commit 钩子会在*每一次*提交时运行整套门禁和质量检查，质量分数须 ≥80。只有暂存内容包含钩子、对应 settings 或测试组本身时，pre-commit 才运行钩子测试组；CI 始终全部运行。这样，即使绕过技能，也不会绕过审读。

  `git-guardrails` 钩子会拦截破坏性 git 命令，包括 `reset --hard`、`clean -f`、`push --force`、`add -A`，并在工作树有未提交改动时拒绝 merge、rebase 或 pull。它检查当前工作树，不预测链式命令之后的状态，所以也会拒绝 `git stash && git merge`。你需要分开运行这两步；确需这样操作时，使用 `ALLOW_DIRTY_MERGE=1`。与其他同类钩子一样，它只对命令行做文本检查，无法看到藏在解释器、别名或脚本里的操作。它的 docstring 列出了可识别的形式。

  `root-of-trust-guard` 会拒绝常见的 shell 写入路径，防止这些命令直接改写定义门禁的文件：`.codebuddy/settings*.json`、`.codebuddy/hooks/`、`.githooks/`。受拦截的写入方式包括重定向、`tee`、`cp`/`mv`/`rm` 和就地 `sed`。它还会拆分 `bash -c` 与 `env -S` 的载荷，并把拆出的命令交给*同一份*破坏性 git 拒绝清单，因此 `bash -c 'git reset --hard'` 与 `bash -c 'git clean -fdx'` 不会再漏过这两道防线。

  **请把它看作尽力而为的文本检查，不要把它当作无法绕过的锁。** 它自身出错时会放行；受保护的文件仍可能通过模板明确允许的通道被替换，例如 `Edit`/`Write`/`MultiEdit`、分支切换、没有未提交改动的合并，或钩子自身的 bug。它真正改变的是修改通道：门禁改动会以可审读的 diff 出现，而不是被一次看不见的覆盖替换。它并不保证门禁无法禁用，也不提供恢复功能。转录和 `git reflog` 只能辅助审计轨迹和提交历史，两者都不保存未提交编辑或未跟踪文件的字节。评审运行时还会重新核验审阅者引入的任何「fatal」发现，确认后才计入。
- **每个门禁都验证过有效性，台账本身也受检查。** 在 [`quality_reports/qualification/LEDGER.md`](quality_reports/qualification/LEDGER.md) 中可查到每项资格认定植入了什么缺陷、检查是否按预期失败，以及召回率和误报率。这份台账会实际影响构建：已登记的检查在台账中没有对应行，构建就会失败；台账行点名不存在的检查器，也会失败。*尚未*验证的检查会按名列出，明确显示哪些验证还没完成。未经有效性验证的检查不是弱证据，而是没有证据。运行 [`/vaccinate`](.codebuddy/skills/vaccinate/SKILL.md) 可以验证一个检查。
- **编排运行时会实际调度审读。** 审读任务会通过相互独立的 Agent 调用并行派发给专职子代理，再按共享的发现 schema 归并，经幻觉门禁裁定，循环到空轮为止。详见 [`orchestrator-protocol.md`](.codebuddy/rules/orchestrator-protocol.md)。
- **错误和有依据的差异会区别处理。** 不一致并不总是失败。有据可依且*明确列出*的替代做法记为 `EXPLAINED`，并写入回复审稿人函；真正的错误仍按失败处理，必须解决后才能关闭。

这**不是**一个自主守护进程。每轮循环都由你或某项技能发起，你始终负责审计。定时自动化只处理周期性任务，并且只在有发现时通知。需要日程、指定目录与权限档位的作业使用 [automation](.codebuddy/references/scheduled-routines.md)，例如收件箱分诊和夜间可复现性检查；会话内的短轮询使用 `CronCreate`；需要跨晚持续运行的任务使用它的 `durable: true`。这三种原语都在你的机器上运行，因此机器必须保持开机。

### 任务托管模式

你先描述任务。对于复杂或含糊的请求，WorkBuddy 会先通过提问澄清目标，再把任务要求整理成需求说明，标明 MUST/SHOULD/MAY 优先级和 CLEAR/ASSUMED/BLOCKED 清晰度状态。你批准需求说明后，WorkBuddy 才规划步骤并调用合适的技能。对于 `/create-lecture` 这类需要用户调用的技能，它会告诉你该运行哪一个，例如 `/create-lecture`、`/qa-quarto`、`/review-paper --adversarial`。技能内部会依次实施、核验、审读、修复、再次核验并打分，达到质量标准后返回总结。你说「直接干」，它就运行完整循环；提交仍须显式调用 `/commit`，随后由 pre-commit 钩子检查。

### 专职代理

模板配有 18 个科研/审读代理和 1 个 Harness 自检代理 `ping`，共 19 个。每个科研/审读代理检查一个维度，`ping` 不承担科研或审读职责。几个有代表性的代理如下：

- **proofreader**：语法与错字
- **slide-auditor**：视觉布局
- **pedagogy-reviewer**：教学质量
- **r-reviewer**：R 代码质量
- **domain-reviewer**：幻灯片的领域正确性；这是模板，需按你的领域定制
- **domain-referee** / **methods-referee** / **editor**：稿件同行评审流水线，由 `/review-paper --peer` 调用

专职代理只检查自己擅长的维度。`/slide-excellence` 并行运行这些幻灯片审读代理，`/review-paper --peer` 运行论文审读流水线。同样的分工方式也适用于其他学术产物，包括稿件、数据流水线和项目申请书。

### 对抗式 QA

两个角色分工相反：**critic** 同时阅读 Beamer 与 Quarto，提出严格、具体的审查发现；**fixer** 按这些发现逐项修复。它们**循环到空轮**，也就是连续两轮没有新增 CRITICAL/MAJOR 发现后才停止。5 轮上限只是退路，不是主要停止条件。这个流程能发现单遍审读漏掉的错误。

### 质量审读

每个产物都会得到 0–100 的分数。分数低于阈值时，工作流会中止并列出审查发现，由你决定修复还是明确批准例外：

- **80**：提交阈值
- **90**：PR 阈值
- **95**：卓越（愿景目标）

> **阈值如何执行：** 这些阈值在 harness 层是建议值，但 `/commit` 技能会运行质量检查，并在失败时中止。自 v2.0 起，运行一次 `./scripts/install-hooks.sh` 还会安装实际的 pre-commit 钩子 `.githooks/pre-commit`。它会在*每一次*提交时运行门禁总检和质量门禁，质量分数须 ≥80。只有暂存内容包含钩子、对应 settings 或测试组本身时，才运行钩子测试组；CI 始终全部运行。因此，绕过技能也不会绕过审读。你可以用 `SKIP_QUALITY_GATE=1` 或 `git commit --no-verify` 按次绕过。

### 上下文存活

计划、需求说明与会话日志都保存在磁盘上，自动压缩或新会话不会抹掉它们。PreCompact 钩子会在 WorkBuddy 自动压缩前保存上下文快照，避免关键决策在压缩时丢失。MEMORY.md 则跨会话累积经验，让后续工作可以复用此前发现的模式。

遇到长流水线或计划中途交接等需要*主动*压缩的情况，`/compress-session`（v1.9.0）会把对话整理成结构化笔记，记录决策、下一步动作和**作为噪声丢弃的内容**，而不是让自动压缩直接截断。`/promote-memory`（v1.9.0）定期由五位评审筛选原生自动记忆中的候选条目，经你批准后，把通用经验写入已提交的 MEMORY.md。

### 核验纪律（v1.7.0+）

提交前会运行以下几层互补的核验：

- **`/verify-claims`**（v1.7.0）：使用链式核验，并由独立上下文中的核验者检查。核验者从未见过草稿，因此不能沿用草稿作者的自我确认。v1.9.0 加入 HIGH/MED/LOW-WARN 严重度分级。伪造引用、数值矛盾等 HIGH-WARN 发现按失败处理，必须解决后才能关闭，草稿不会被报告为已核验。`/commit` 不读取这些判定，所以你需要在提交前处理它们。
- **`/audit-reproducibility`**（v1.4.0；Stata 覆盖 v1.9.0）：把稿件中的每条数值断言与生成它的脚本输出交叉核对。v1.9.0 加入 `passport.yaml`，为每篇论文保存一份 YAML 状态文件，逐条标记 PASS/FAIL/STALE/UNVERIFIED。
- **`/humanize`**（v1.9.0）：在提交前检测套话过渡、限定词堆叠、谄媚等 AI 腔。它按设计只读，因为自动重写会降低质量。
- **`/review-paper --peer <journal> --variance N`**（v1.9.0）：运行 N 位审稿人，对审稿取向抽样，并报告**判定分布**而非点估计。AgentReview（EMNLP 2024）发现，37% 的判定仅因审稿取向抽样而变动，这项技能正是由此设计。

---

## 指南

完整说明见[**完整指南**](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html)，也可以直接阅读[源码](guide/workflow-guide.qmd)。

指南包括：

1. **这套工作流为什么存在**：要解决的问题与设计目标
2. **上手**：fork 仓库、粘贴提示词，再由 WorkBuddy 完成配置
3. **系统如何运作**：专职代理、对抗式 QA 与质量打分
4. **组成部分**：CODEBUDDY.md、规则、技能、代理、钩子与记忆
5. **工作流模式**：幻灯片、研究、可复现性、演示修辞、顺序对抗式审计等
6. **生态**：clo-author、claudeblattman、MixtapeTools、autoresearch、ClaudeCodeTools 的扩展，以及不断壮大的社区
7. **按你的领域定制**：创建自己的审阅者与知识库


### 2026 年的能力

指南介绍本平台的以下能力：

> 本节只说明本平台提供的功能，不照搬上游能力清单。每条平台事实的证据与核查日期见
> [`.codebuddy/references/platform-facts.md`](.codebuddy/references/platform-facts.md)。
> 那张表是唯一出处；本节与它冲突时，以它为准。

- **模型档位**：本平台只有**三档**。`default` 是审读与批评的默认档，`lite` 处理机械性工作，`reasoning` 处理需要较强判断力的任务，包括期刊编辑、审稿、事实核查、对抗式批评和 TikZ 空间推理。平台没有第四档，也不提供按型号选择版本的列表、价格表或别名表。各档职责、上游层级映射和档位修改方法见单一真源 [`model-versions.md`](.codebuddy/references/model-versions.md)。这里只介绍档位，不写具体型号，因此不会随型号更新而过时；单一真源超过有效期后，陈旧度门禁会使构建失败。
- **`/effort` 命令**：调整当前会话的思考预算，与模型档位相互独立。
- **代理的 `effort:` 字段**：可取 `minimal` / `low` / `medium` / `high` / `xhigh` / `max`，用于设置子代理的思考预算。**技能**中的这个字段不起作用，因为技能加载器不读取它。`maxEffortLevel` 上限键不存在，见[模型单一真源](.codebuddy/references/model-versions.md)。
- **`/goal <可核验条件>`（CLI 有官方支持；桌面端未证实）**：[CodeBuddy Code CLI 官方文档](https://www.workbuddy.cn/docs/cli/goal)介绍了跨轮目标评估与 Web UI / ACP 面板。本机桌面共享引擎也注册了命令，并实现了 `GoalService`，这属于 L2 证据；但没有桌面运行时观测，因此本节不把它写成桌面端可用步骤。证据见 [`platform-facts.md`](.codebuddy/references/platform-facts.md)。
- **并行任务视图**：`/review-paper --peer`、`/slide-excellence` 等并行审读任务显示在侧边栏的任务列表中。上游 CLI 提供 `claude agents` 单屏仪表盘，本平台桌面端没有这条命令，也不需要它。
- **控制成本的编排**：平台提供提示词缓存 TTL、70/20/10 模型路由（`lite` / `default` / `reasoning`），以及 `/cost` + `/usage` 监控。上游订阅的额度池与缓存时长规则不适用于本平台，本仓库也不代为说明。
- **技能 frontmatter**：平台实际读取的字段包括 `model`、`agent`、`disable-model-invocation`、`allowed-tools` 等。完整清单也列出了写了却不生效的字段，见单一真源 [`.codebuddy/references/skill-fields.md`](.codebuddy/references/skill-fields.md)。
- **权限档位**：桌面端只有**默认权限**与**完全访问权限**。前者对应 `sandbox.defaultPermission`，越界就询问；后者对应 `sandbox.fullAccessPermission`，不再询问。上游的手动、接受编辑、计划、自动、Bypass 五档没有在桌面端提供。桌面选择器也不提供 `--permission-mode` 与 `Shift+Tab`，后两者属于 [CodeBuddy Code CLI](https://www.workbuddy.ai/docs/cli/permission-modes)。
- **钩子处理类型**：平台支持 command、prompt 与 HTTP 处理类型，以及 20+ 种钩子事件。引擎实际识别 28 个事件，本仓库注册其中 7 个。**钩子载荷里没有 `effort.level`**。该字段属于会话状态，由 `statusline` 读取，不是钩子输入。
- **高级代理配置**：`model`、`effort`、`maxTurns`、`isolation: worktree`、`tools` / `disallowedTools`、`memory`、`background` 都写在 `.codebuddy/agents/*.md` 的 frontmatter 中。`model-routing.md` 规则明确规定了各代理的档位（v1.9.0）。
- **没有 `worktree.baseRef` 设置**：上游用这个键决定新 worktree 从远端默认分支（`fresh`）还是本地 HEAD（`head`）创建。本平台没有这个键，`baseRef` 只是内部 `git worktree add` 的一个实参。
- **上游内置技能在本平台不存在**：`/fewer-permission-prompts`、`/team-onboarding`、`/autofix-pr`、`/powerup`、Ultraplan 与 `/loop` 都无法在包中找到。`/loop` 只作为预设任务卡的示例文案出现。本平台使用 `.codebuddy/skills/` 里的技能完成对应工作。
- **插件**：使用 `/discover-plugins` 查找第三方扩展。
- **2026 年中的新增**（2026 年 6–9 月）：`/skill-doctor` 显示每项技能占用多少上下文、多久触发一次。插件评测在上游使用 `plugin eval`，本平台对应 `scripts/run-skill-eval.sh`，但需另装 CodeBuddy Code CLI。内置输出风格中，**Concise** 适合日常回答，**Learning** 会留一部分内容给你自己写，可与 `/scaffold-exercises` 搭配。子代理可以在后台运行，fork 模式默认开启。`/fork` 在后台会话中继续当前对话的副本，`/doctor` 检查配置，`autoUpdatesChannel: "stable"` 用于选择稳定更新通道。

---

## 用例

| 学术任务                 | 这套工作流如何帮忙                                                                                                                                             |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 讲义幻灯片（Beamer/Quarto） | 从创建、翻译、多代理审读到部署，全流程                                                                                                                                   |
| 研究论文                 | 文献综述、稿件审读、模拟同行评审（`/review-paper --peer [journal]`）、审稿取向方差报告（`--variance N`）                                                                           |
| 数据分析                 | 端到端 R 流水线（`/data-analysis`），或经 `stata-mcp` 的 Stata 流水线（`/stata-replication`，v1.9.0）、复现核验、可直接发表的输出                                                     |
| 蒙特卡洛模拟               | 可复现的模拟研究（`/simulation-study`，v1.10.0）——参数化 DGP、估计量网格、带蒙特卡洛标准误的偏差/RMSE/覆盖率/水平/功效，以及专门的 `sim-reviewer` 审读轮                                              |
| 包开发                  | R 包发布门禁（`/r-package-check`，v1.10.0）——`devtools::document()` + 测试 + `R CMD check --as-cran` + CRAN 政策分诊 + `r-package-reviewer`（Stata / Python 检查在路线图上） |
| 复现包                  | 符合 AEA 要求的打包、可复现性审计轨迹、`passport.yaml` 断言溯源（v1.9.0）                                                                                                    |
| 演示                   | 演示修辞原则、视觉审计、认知负荷审读                                                                                                                                    |
| 研究计划书                | 结构化起草，配对抗式批评                                                                                                                                          |
| 预注册                  | 可直接提交 OSF / AsPredicted / AEA RCT Registry 的文档（`/preregister --style`）——完整工作流见模式 16                                                                   |
| 投稿纪律                 | `/humanize`（检测 AI 腔）、`/verify-claims` 将 HIGH-WARN 发现按失败处理且必须解决后才能关闭（伪造引用不会被报告为已核验）、审稿取向方差                                                             |

**预置学科：** 经济学提供 Top-5 期刊画像和 R 惯例；政治学提供 APSR / AJPS / JOP 画像、形式理论与调查实验两类论文，以及 conjoint/`cjoint` 惯例。模板使用者可以组合期刊画像、论文类型和学科卡片，扩展到心理学、社会学或公共卫生。

### 一个仓库，多种项目类型

同一仓库可以支持整个研究计划，而不必一次只处理一篇论文。`CODEBUDDY.md`、规则、代理与质量门禁可同时用于课程与讲义、论文与审稿意见回复、数据分析与复现包。v1.10.0 还新增了**蒙特卡洛模拟研究**（`/simulation-study` + `sim-reviewer`）和 **R 包发布门禁**（`/r-package-check` + `r-package-reviewer`）。路线图包括 Stata / Python 包检查（SSC / PyPI）和个人生产力工作流。后续计划见 [`.codebuddy/references/v2.0-backlog.md`](.codebuddy/references/v2.0-backlog.md)。

---

## 包含什么

<details>
<summary><strong>本模板 19 个代理、63 个技能、37 条规则、11 个钩子</strong>（点击展开）</summary>

代理由 18 个科研/审读代理 + 1 个 Harness 自检代理 `ping` 组成；`ping` 不承担科研或审读职责。

### 代理（`.codebuddy/agents/`）

| 代理                                | 它做什么                                                                 |
| --------------------------------- | -------------------------------------------------------------------- |
| `proofreader`                     | 审查语法、错字、溢出与一致性                                                       |
| `slide-auditor`                   | 审计视觉布局，包括溢出、字体一致性与间距                                                 |
| `pedagogy-reviewer`               | 从 13 种模式审读教学法，包括叙事弧、记号密度与节奏                                          |
| `r-reviewer`                      | 审查 R 代码质量、可复现性与领域正确性                                                 |
| `tikz-reviewer`                   | 严格审查 TikZ 图的视觉效果                                                     |
| `beamer-translator`               | 把 Beamer 翻译成 Quarto                                                  |
| `quarto-critic`                   | 以 Beamer 为基准，对 Quarto 做对抗式 QA                                        |
| `quarto-fixer`                    | 按 critic 代理的发现逐项修复                                                   |
| `verifier`                        | 端到端核验任务是否完成                                                          |
| `domain-reviewer`                 | 领域实质审阅者的**模板**，需按你的领域定制                                              |
| `claim-verifier` (v1.7.0)         | 在独立上下文中进行链式核验的事实核查者，永远不是对话的 fork                                     |
| `editor` (v1.5.0)                 | 供 `/review-paper --peer` 使用的期刊编辑，负责初审、选择审稿人与综合意见                     |
| `domain-referee` (v1.5.0)         | 在 `--peer` 模式下按审稿取向预设进行实质审稿                                          |
| `methods-referee` (v1.5.0+)       | 按 6 种论文类型审查方法论                                                       |
| `humanize-auditor` (v1.9.0)       | 供 `/humanize` 调用的只读 AI 腔审计者                                          |
| `promote-memory-council` (v1.9.0) | 由五位评审决定是否把 `[LEARN]` 条目写入 MEMORY.md                                  |
| `sim-reviewer` (v1.10.0)          | 审查蒙特卡洛模拟：DGP/估计目标匹配、蒙特卡洛标准误、以真值计算覆盖率、断言↔表格一致                         |
| `r-package-reviewer` (v1.10.0)    | 审查 R 包源码：DESCRIPTION/NAMESPACE 卫生、roxygen 完整性、testthat 覆盖率、CRAN 政策红旗 |
| `ping`                            | **Harness 自检**子代理：被派发时回传固定标记，用于确认 `.codebuddy/agents/` 会被发现并加载       |

### 技能（`.codebuddy/skills/`）

| 技能                               | 它做什么                                                                                                                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/init-research-project`         | 把一个 fork 下来的模板初始化成真实项目：收齐项目信息、替换占位符、按学科裁剪规则、跑通环境自检、交出起步计划                                                                                                                 |
| `/compile-latex`                 | 3 遍 XeLaTeX 编译，配 bibtex                                                                                                                                                   |
| `/deploy`                        | 渲染 Quarto + 同步到 GitHub Pages                                                                                                                                              |
| `/extract-tikz`                  | TikZ 图到 PDF 再到 SVG 的流水线                                                                                                                                                   |
| `/proofread`                     | 对某个文件启动 proofreader                                                                                                                                                       |
| `/visual-audit`                  | 对一套幻灯片做视觉布局审计（行内跑 `slide-auditor` 的那些检查）                                                                                                                                  |
| `/pedagogy-review`               | 对某个文件启动 pedagogy-reviewer                                                                                                                                                 |
| `/review-r`                      | 启动 R 代码审阅者                                                                                                                                                                |
| `/qa-quarto`                     | 对抗式 critic-fixer 循环（循环到空轮；5 轮上限是退路）                                                                                                                                       |
| `/slide-excellence`              | 多代理联合审读                                                                                                                                                                   |
| `/translate-to-quarto`           | 完整翻译 Beamer 到 Quarto：先运行 Phase 0 开始前检查，再经过 12 个翻译阶段（1–11 以及一个 6.5 教学法审读）                                                                                                  |
| `/vaccinate`                     | 验证检查、门禁或 AI 审阅者能否检出目标失败：植入缺陷并设置无缺陷对照，再把召回率与误报率写入资格台账                                                                                                                      |
| `/adjudicate-review`             | 把 AI 审读、审稿意见、linter 或第二个模型给出的审查发现转化为经过核验的修复。对照源头核实前，每条发现都只是 CANDIDATE                                                                                                     |
| `/blast-radius`                  | 修改共享内容（返回值、schema、默认值、单位）前后，列出所有使用方并逐一运行                                                                                                                                  |
| `/credible-claims`               | 委派前写研究简报，委派后写断言记录，避免把「跑得更快」误当成「证据可信」                                                                                                                                      |
| `/differential-audit`            | 比较两套实现，适用于移植、复现、重构和版本升级，具体说明二者在哪些方面一致                                                                                                                                     |
| `/oracle-review`                 | 通过 Oracle CLI 调用另一家供应商的前沿模型作为外部审稿人，并裁决返回的审查发现                                                                                                                             |
| `/verify-artifact`               | 确认待发送文件与预期一致：重新构建、核验完整性并与源头比对                                                                                                                                             |
| `/voice-profile`                 | 从你以往的论文中归纳写作风格画像，再据此审读草稿；它关注作者风格，`/humanize` 只检测 AI 痕迹                                                                                                                    |
| `/validate-bib`                  | 把引用与参考文献表交叉核对                                                                                                                                                             |
| `/devils-advocate`               | 在确定设计决策前先质疑它                                                                                                                                                              |
| `/create-lecture`                | 完整的讲义创建工作流                                                                                                                                                                |
| `/commit`                        | 运行门禁后在分支上提交；`--pr` 还会推送并创建 PR。不会自动合并，合并需经你批准                                                                                                                              |
| `/lit-review`                    | 文献检索、综合与缺口识别                                                                                                                                                              |
| `/research-ideation`             | 生成研究问题与实证策略                                                                                                                                                               |
| `/interview-me`                  | 通过交互式访谈把一个研究想法正式化                                                                                                                                                         |
| `/review-paper`                  | 稿件审读：结构、计量、审稿人可能提的反对意见                                                                                                                                                    |
| `/data-analysis`                 | 端到端 R 分析，输出可直接发表                                                                                                                                                          |
| `/learn`                         | 把非显然的发现沉淀为可长期复用的技能                                                                                                                                                        |
| `/context-status`                | 显示会话健康度与上下文用量                                                                                                                                                             |
| `/deep-audit`                    | 对一个理论、一个证明、一篇论文、一个代码库或一组断言做对抗式审计——拆解、独立怀疑者、每条发现配一位独立裁判、修复、再核验；全仓库一致性是它的一个应用                                                                                               |
| `/permission-check`              | 当询问或拦截意外出现时，读钩子链与本地覆盖，指出是哪条守卫拦的以及哪些照上游写的开关在本平台根本不生效                                                                                                                       |
| `/audit-reproducibility`         | 对论文 ↔ 代码的数值断言强制执行容差阈值                                                                                                                                                     |
| `/new-diagram`                   | 从片段库里搭一张 TikZ 图，带预防检查 + 审读                                                                                                                                                |
| `/respond-to-referees`           | R\&R 回复函生成器（把审稿意见映射到修改）                                                                                                                                                   |
| `/seven-pass-review`             | 七遍对抗式稿件审读（通过相互独立的 Agent 调用并行派发给专职子代理）                                                                                                                                     |
| `/checkpoint`                    | 结构化的会话交接快照（状态 + 计划指针 + 下一步动作）。叙述式会话日志的搭档。                                                                                                                                 |
| `/preregister`                   | 从研究需求说明生成一份预注册文档（OSF / AsPredicted / AEA RCT Registry 风格）                                                                                                                 |
| `/verify-claims` (v1.7.0)        | 链式核验式事实核查（独立上下文的核验者）。HIGH/MED/LOW-WARN 严重度分级（v1.9.0）；HIGH-WARN 发现按失败处理，必须解决后才能关闭；在此之前，草稿不会被报告为已核验。                                                                        |
| `/humanize` (v1.9.0)             | 检测学术散文里的 AI 腔痕迹（10 个检测类别；只读，不重写）                                                                                                                                          |
| `/compress-session` (v1.9.0)     | 在自动压缩之前，把当前会话提炼成结构化笔记（决策、下一步动作、*按噪声丢弃的东西*）                                                                                                                                |
| `/promote-memory` (v1.9.0)       | 由五位评审投票决定哪些 `[LEARN]` 条目可以从原生自动记忆写入 MEMORY.md                                                                                                                             |
| `/stata-replication` (v1.9.0)    | 经 `stata-mcp` MCP 服务器的端到端 Stata 流水线（为 R 优先的项目镜像 `/data-analysis`）                                                                                                         |
| `/simulation-study` (v1.10.0)    | 搭建并跑一项可复现的蒙特卡洛研究——参数化 DGP、估计量网格、带种子的重复、带蒙特卡洛标准误的偏差/RMSE/覆盖率/水平/功效                                                                                                         |
| `/r-package-check` (v1.10.0)     | R 包发布门禁——`devtools::document()` + 测试 + `R CMD check --as-cran`，把 ERROR/WARNING/NOTE 对照 CRAN 政策分诊，再跑 `r-package-reviewer`                                                  |
| `/replication-package` (v2.0)    | 组装一份可直接投稿的 DCAS / openICPSR 复现包——标准 README、数据集清单、计算环境要求留存、表／图到脚本及行号的映射、受限数据存缴说明（`/audit-reproducibility` 为 FAIL 时阻塞）                                                      |
| `/challenge`                     | 用你没做的那些选择去压测一个发现——在离散分叉上做设定曲线，再用具名敏感性统计量（E-value、Cinelli–Hazlett RV、Oster δ）检验识别假设                                                                                        |
| `/capture-environment` (v2.0)    | 为复现包记录计算环境：renv.lock + sessionInfo.txt（R）、requirements.txt / environment.yml / uv.lock（Python）、Stata 版本 + ado 清单、种子/RNG，以及可选的固定版本 Dockerfile                              |
| `/power-analysis` (v2.0)         | 计算研究设计的功效 / 所需样本量 / 最小可检出效应——两臂 RCT（聚类/ICC、不等分配）、多臂校正、对非标准设计进行基于模拟的功效分析；喂给 `/preregister`                                                                                 |
| `/disclosure-check` (v2.0)       | 对受限/保密数据产出的统计披露限制预筛（小格子、互补抑制缺口、支配性、PII）；CRITICAL/WARNING/OK + 门禁                                                                                                          |
| `/grant-proposal` (v2.0)         | 通过组合基元搭一份 NSF/NIH/ERC/基金会的项目申请书（项目需求说明 → 目标/方法，委派 DMP + 设施，一致性通读 + 要求清单）                                                                                                  |
| `/data-management-plan` (v2.0)   | 符合资助方要求的数据管理计划（NSF / NIH DMS 2023 / ERC / Horizon Europe）——并入披露风险防控 + IRB 约束，以及一份复现包/环境计划；输出草稿 + 资助方清单                                                                    |
| `/coauthor-brief` (v2.0)         | 合作者交接简报——自上次简报以来改了什么、逐产物状态、未决问题、本地复现 + 受限数据获取步骤                                                                                                                           |
| `/triage-inbox` (v2.0)           | 可定时的学术收件箱 + 日历分诊，经 Gmail/Calendar MCP——把审稿邀请、R\&R/编辑、合作者往来、研讨会/会议邀请、经费与行政截止分类；每条各提一个需人放行的动作（起草回复、占用日历、搭一个审稿项目、`/coauthor-brief`、稍后提醒）；输出一份摘要 + 审稿义务跟踪表；MCP 缺席时优雅降级；永不自动发送 |
| `/diagnose` (v2.0)               | 给一个错误/失败的实证结果找根因——有纪律的复现 → 最小化 → 提出假设 → 插桩 → 修复循环；为研究代码的 bug 调校（类型转换、NA/合并爆炸、聚类/标准误选择、种子/包版本漂移）；`--no-fix` 只定位不改动                                                         |
| `/submission-disclosures` (v2.1) | 投稿时的披露段落：与目标期刊「已核验现行」政策匹配的 AI 使用披露、CRediT 贡献者角色、利益冲突、数据可得性声明（不是统计披露——那是 `/disclosure-check`）                                                                              |
| `/syllabus` (v2.0)               | 从一个主题或书单搭/重构一份课程大纲——课程描述 + 先修要求、逐周日程（主题→阅读→交付物）、可度量的学习目标、考核方案 + 评分细则、标准政策（迟交 / AI 使用 / 学术诚信 / 无障碍）、以及一份把各周映射到 `/create-lecture` 讲义的逐周工作表；懂经济学（博士计量/微观/宏观序列、本科）            |
| `/teach-from-paper` (v2.0)       | 端到端读一篇论文，并按指定受众的知识层级讲解这篇论文——讲义大纲（动机 → 设定 → 关键结果 → 方法 → 要点）、值得讲的 3-5 个结果及直觉、给 `/create-lecture` 的幻灯片骨架、讨论问题，以及给 `/scaffold-exercises` 的习题集简报                               |
| `/respond-to-eval` (v2.0)        | `/respond-to-referees` 的教学版——把课程评价意见聚类成主题，按频次加权（信号 vs 噪声），分为 Keep / Change / Investigate / Out-of-scope，并起草映射到大纲 + 讲义的具体改动；把方案存到 `quality_reports/teaching/`              |
| `/scaffold-exercises` (v2.0)     | 跨解析/实证/编程三类题型搭一套计分习题集，带详解与「这为什么重要」的说明，输出到单独的答案册                                                                                                                           |
| `/new-skill` (v2.0)              | 搭一个遵循本仓库约定的新技能——就用途、触发词与工具做访谈，按模板写出 `.codebuddy/skills/<name>/SKILL.md` 并运行 `check-skill-integrity.py`；README 行、计数与指南更新及复跑是独立的最终验收步骤                                      |
| `/issues` (v2.6)                 | 把 GitHub issues 当作项目的待办清单与记忆——每条已确认的发现，先在开着的与已关闭的 issue 里查重，再各自立一条；列出当前手头工作的未决项；关闭一条 issue 时用评论记下哪里错了、试过什么、怎么修的；每个草稿都先给你看，没有你的「可以」就什么都不发；往公开仓库发之前会警告                      |
| `/hello`                         | **Harness 自检**技能：被调用时回传固定标记并写出 `quality_reports/checkpoints/_SMOKE_HELLO.md`；由调用方用随机标记、调用前文件不存在检查与调用后内容/cwd/参数核验来判定发现和调用是否成功                                              |


### 研究工作流

| 功能 | 它做什么 |
|---------|-------------|
| 探索目录 | 结构化的 `explorations/` 沙箱，探索完成后可转入正式项目或归档 |
| 快速通道工作流 | 快速原型用 60/100 的质量阈值 |
| 简化编排器 | 实施 → 核验 → 打分 → 完成（不做多轮审读） |
| 增强的会话日志 | 记录改动、决策、核验的结构化表格 |
| 只在合并时报告 | 质量报告只在合并时产出 |
| 数学行宽例外 | 有文档记录的公式允许长行 |
| 工作流速查 | 一页纸的速查表，位于 `.codebuddy/WORKFLOW_QUICK_REF.md` |

### 规则（`.codebuddy/rules/`）

规则按路径作用域加载：**常开**规则在每个会话中加载，**按路径作用域**的规则只在 WorkBuddy 处理匹配文件时加载。指令文件越长，遵守度越差，因此应尽量精简。官方建议把 `CODEBUDDY.md` 控制在约 200 行以内。

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
| `tikz-prevention` (v1.3.0) | `Slides/**`、`Figures/**`、`Preambles/**` | TikZ 开始前 grep 检查（P3/P4 碰撞规避） |
| `agent-authored-code` (v2.5) | `**/*.sh`、`**/*.py`、`**/*.R`、`**/*.do` | 缺陷通常是我们的：任何批量编辑之前先试运行，在任何 `cd` 之前解析路径，用 PID 文件而不是 `pgrep` 监控，覆盖每一种终态 |
| `writing-with-ai` (v2.5) | `**/*.tex`、`**/*.qmd`、`**/*.md`、`**/*.Rmd` | 内部与对外文档之别；为什么模型无法让自己的输出不再像模型输出；可读的那条标准 |
| `issue-ledger` (v2.5) | `.github/**` | 规定哪些工作该创建 GitHub issue：已发布的缺陷、推迟的改进、阻塞性的 owner 决策，以及每轮审读的一条汇总 issue；绝不包含受限数据。同时规定证据标准，包括分母、正/负对照、明确的排除范围，以及关闭时的评论 |
| `tikz-measurement` (v1.3.0) | `Slides/**`、`Figures/**`、`Preambles/**`、`scripts/**` | 贝塞尔曲线深度计算 + 六遍碰撞协议（来自 MixtapeTools） |
| `content-invariants` (v1.6.x) | `.tex`、`.qmd`、`Preambles/`、`scripts/R/**` | 编号不变量 INV-1–INV-12（调色板同步、Beamer↔Quarto 记号一致、不用 overlay、每页最多两个 box、`set.seed` 只调一次、相对路径、……），critic 按编号引用它们 |
| `cross-artifact-review` (v1.4.0) | `master_supporting_docs/`、`.tex`、`.qmd` | 论文 ↔ 代码依赖图；自动调用 `/review-r` + `/audit-reproducibility` |
| `post-flight-verification` (v1.7.0) | 生成事实性断言的技能 | 链式核验协议，配一个独立上下文的核验者 |
| `summary-parity` (v1.7.0) | `CHANGELOG.md`、`README.md`、`.qmd`、技能/规则/代理的 `.md` | 对照完整正文重新核验摘要，防止两处内容逐渐偏离 |
| `model-routing` (v1.9.0) | `.codebuddy/agents/**/*.md`、`.codebuddy/skills/**/SKILL.md` | 70/20/10 架构师/编辑分工（`lite` / `default` / `reasoning`） |
| `review-fencing` (v2.5.1) | `.tex`/`.qmd`、`master_supporting_docs/`、`quality_reports/` 审计目录、`claim-verifier.md` | 通过环境保证审阅者独立：在检出目录之外保留中性副本，排除先前判定，让审阅者先自行阅读，并把正对照与已提交的标准答案文件隔开 |
| `stata-code-conventions` (v1.9.0) | `**/*.do`、`scripts/stata/**` | Stata 文件头骨架、编号流水线、esttab、聚类纪律、AEA 合规 |
| `simulation-conventions` (v1.10.0) | `**/*simulation*.R`、`**/*_sim.R`、`explorations/**` | 蒙特卡洛纪律：DGP/估计目标、L'Ecuyer 播种、蒙特卡洛标准误、以真值计算覆盖率、原始结果留存 |
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
| `constitutional-governance.md` | 定义不可妥协原则与偏好之分的模板 |
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
| Python 3 (3.9+) | 内部检查器（调色板同步、TikZ 预防） | macOS/Linux 通常预装，仍需确认；Windows 见 [python.org](https://www.python.org/) |
| XeLaTeX | LaTeX 编译（Beamer `HelloWorld`、真实讲义） | [TeX Live](https://tug.org/texlive/) 或 [MacTeX](https://tug.org/mactex/) |
| [Quarto](https://quarto.org) | 网页幻灯片（Quarto `HelloWorld`、真实讲义） | [quarto.org/docs/get-started](https://quarto.org/docs/get-started/) |
| R | 图与分析（`/data-analysis`、`scripts/R/` 模板） | [r-project.org](https://www.r-project.org/) |
| pdf2svg | 为 Quarto 把 TikZ 转 SVG（`/extract-tikz`） | `brew install pdf2svg`（macOS）、`apt install pdf2svg`（Debian） |
| [gh CLI](https://cli.github.com/) | PR / issue 工作流 | `brew install gh`（macOS）、`apt install gh`（Debian） |
| Playwright for Python（可选） | 浏览器实测的幻灯片 QA（`scripts/slide-qa.py`，由 `/visual-audit`、`/qa-quarto`、`/slide-excellence` 调用）；驱动你已安装的 Chrome | `python3 -m venv ~/.venvs/slide-qa && ~/.venvs/slide-qa/bin/pip install playwright`，然后 `export SLIDE_QA_PYTHON=~/.venvs/slide-qa/bin/python` |

**fork 本模板的最低要求：** WorkBuddy + git + Python 3（macOS/Linux 通常预装，但仍需确认版本与可执行性）。

**把自带 HelloWorld 演示端到端跑通的最低要求：** 加上 XeLaTeX（用于 `/compile-latex HelloWorld`）与 Quarto（用于 `/deploy HelloWorld`）。

**真实讲义可能还需要其他工具。** `scripts/R/` 分析需要 R，提取 TikZ 需要 pdf2svg，基于 PR 的提交流程需要 gh CLI，在浏览器中检查幻灯片溢出需要 Playwright。`./scripts/validate-setup.sh` 会报告 R、gh CLI 与 Playwright 是否已安装，但不检查 pdf2svg；后者请用 `command -v pdf2svg` 检查。

---

## 按你的领域做适配

1. **填好知识库**（`.codebuddy/rules/knowledge-base-template.md`），写入你的记号、应用与设计原则
2. **定制领域审阅者**（`.codebuddy/agents/domain-reviewer.md`），换上你所在领域特有的审读透镜
3. **更新调色板**：同时修改 [`Preambles/header.tex`](Preambles/header.tex)（Beamer/TikZ）与 [`Quarto/theme-template.scss`](Quarto/theme-template.scss)（Quarto 幻灯片）顶部的 HEX 值，确保两边一致，然后运行 `./scripts/check-palette-sync.sh` 核验。只改一边会在没有提示的情况下造成 Beamer 与 Quarto 渲染不一致。完整约定与 TikZ 样式库见 [`Preambles/README.md`](Preambles/README.md)。
4. **补上领域特有的 R 坑**，写进 `.codebuddy/rules/r-code-conventions.md`
5. **填好讲义映射**，写在 `.codebuddy/rules/beamer-quarto-sync.md`
6. **定制工作流速查**（`.codebuddy/WORKFLOW_QUICK_REF.md`），写入你的不可妥协项与偏好
7. **搭好探索目录**（`explorations/`），用于实验性工作

---

## 更多资源

- CODEBUDDY.md 的写法，包括指令文件的加载方式、体积上限与三层记忆的分工，见 [`.codebuddy/rules/meta-governance.md`](.codebuddy/rules/meta-governance.md)

---

## 由来

原工作流见 [`pedrohcgs/claude-code-my-workflow`](https://github.com/pedrohcgs/claude-code-my-workflow)，引用信息见 `CITATION.cff`。

---

## 社区与扩展

上游项目的采用记录显示，经济学、能源、政治学与工程学等领域的研究组曾 fork 并改造这套工作流。2026 年 3 月的调查记录了 **15+ 个研究组**；截至 2026-08-24，原仓库已有 **2,900 多次 fork** 和 1,500 多颗星。一次 fork 不等于一个研究组，调查数字与 fork 数不能混为一谈，也都不是本移植的采用数据。编排器、钩子、质量门禁等基础设施无需改动即可迁移。

**扩展工作流：**

- **[clo-author](https://github.com/hugosantanna/clo-author)**，作者 Hugo Sant'Anna（UAB）——以论文为中心的研究工作流，带 21 个专职代理（7 对 worker-critic，加上审稿人、数据工程师、核验者）、模拟盲审、AEA 复现合规与完整的研究生命周期管理。**本模板里的 `/review-paper --peer <journal>` 流水线经 Hugo 许可改编自 clo-author**（流水线形态、六路审稿取向分类、期刊校准 schema、论文类型分支）。谢谢 Hugo。
- **[claudeblattman](https://github.com/chrisblattman/claudeblattman)**，作者 Chris Blattman（U Chicago）——写给非技术型学者的综合指南：行政助理工作流、项目申请书写作、并行批评者配独立综合、自我改进的配置
- **[MixtapeTools](https://github.com/scunning1975/MixtapeTools)**，作者 Scott Cunningham（Baylor）——演示的修辞：漂亮、修辞上有效的学术报告的理念与实践
- **[autoresearch](https://github.com/karpathy/autoresearch)**，作者 Andrej Karpathy——以 `program.md` 为宪制文件的、基于约束的自主研究
- **[ClaudeCodeTools](https://github.com/aspi6246/ClaudeCodeTools)**——「The Editor」人格：七审顺序式论文审读协议

详细描述、设计原则与更多资源见[指南的生态一节](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#sec-ecosystem)。

---

## 版本与贡献

- **版本说明：** 当前发布与升级说明见 [CHANGELOG.md](CHANGELOG.md)，历史发布记录见 git tags/history。项目采用较宽松的 semver：破坏性变更会提升大版本号，你可以自行决定何时拉取更新。
- **怎么贡献：** 见 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)。欢迎提交可推广到其他项目的改进；只适用于你的 fork 的工作，请留在自己的仓库中。
- **维护与同步：** 维护者流程见 [docs/maintenance/UPSTREAM.md](docs/maintenance/UPSTREAM.md)。
- **固定到某个版本：** 运行 `git checkout $(git describe --tags --abbrev=0)` 可切换到最新的发布标签；也可用 `git tag --list` 查看标签，历史内容见 git tags/history。

---

## 许可

MIT License。见 [LICENSE](LICENSE)。
