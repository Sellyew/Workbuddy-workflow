---
name: new-skill
description: 按本仓库约定创建新技能。先访谈用途、触发短语和工具需求，再从技能模板生成 `.codebuddy/skills/<name>/SKILL.md`，最后运行 `check-skill-integrity` 核验 frontmatter 与正文。用户说 "write a skill"、"scaffold a skill"、"create a new skill"、"I keep doing X, make it a skill"、"new slash command"、"turn this workflow into a skill"、"新建技能"、"把这套流程做成技能"、"新斜杠命令" 时使用。不用于记录一次性的会话发现，那是 `/learn` 的职责。
description_zh: 按本仓库约定创建新技能。先访谈用途、触发短语和工具需求，再从技能模板生成 `.codebuddy/skills/<name>/SKILL.md`，最后运行 `check-skill-integrity` 核验 frontmatter 与正文。用户说 "write a skill"、"scaffold a skill"、"create a new skill"、"I keep doing X, make it a skill"、"new slash command"、"turn this workflow into a skill"、"新建技能"、"把这套流程做成技能"、"新斜杠命令" 时使用。不用于记录一次性的会话发现，那是 `/learn` 的职责。
argument-hint: "[skill-name (kebab-case)] [--from-learn] [--dry-run]"
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
disable-model-invocation: true

---

# /new-skill —— 编写符合约定的技能

按本仓库约定创建新技能，做到**简单接口背后的深模块**。这一说法来自 Ousterhout 的《A Philosophy of Software Design》：用较小的外部接口承载充分的实现。本技能通过访谈把用户的模糊意图整理成紧凑任务要求，写出 `.codebuddy/skills/<name>/SKILL.md`，再运行 `check-skill-integrity.py` 核验 frontmatter 和正文。技能文件创建与表面登记是两个不同的完成状态；完整性检查通过，不代表 `check-surface-sync.sh` 或全部门禁已经通过。

`/new-skill` 是本仓库的项目技能，只负责按本仓库的字段、章节和门禁约定生成项目技能。WorkBuddy 内置的 `/skill-creator` 是通用创建器，GUI 入口为「技能 → 添加技能 → 创建技能」。项目技能写入 `.codebuddy/skills/` 并随仓库共享；通用创建器生成的技能默认进入可跨项目使用的用户技能库，不会自动写入当前项目。项目级技能优先于用户级技能，不要用其中一个入口的行为推断另一个。

本技能改编自 [mattpocock/skills](https://github.com/mattpocock/skills) 的 *write-a-skill* 模式，并按本仓库的 frontmatter、章节和门禁约定调整。

## 何时使用

- 你反复向 WorkBuddy 解释同一套包含 3 步以上的工作流，想把它固化成可复用的斜杠命令。
- 你需要领域专属的检查或输出格式，例如引文风格、复现门禁或新的审读透镜。
- 你希望新技能与 `.codebuddy/skills/` 中的现有技能保持一致，包括章节、交叉引用风格和能通过门禁的 frontmatter。

如果只是发现了一件**本会话**中不显然的事，想把它留下来，请改用 `/learn`。`/learn` 记录一次发现，`/new-skill` 则有意设计一个接口。加上 `--from-learn` 后，本技能可以把 `/learn` 形状的存根升级为完整合规的技能。

## 阶段

### Phase 0 —— 确定名称并检查重名

1. 解析 `$ARGUMENTS`。平台提供完整参数字符串，不提供 `$0` / `$1` 位置参数。取**首个非选项 token** 作为技能名；`--from-learn` 和 `--dry-run` 都不带值，可以放在名称前后。名称必须是单个 kebab-case token。如果出现第二个位置参数、未知选项或无法确定的结构，先停下询问，不要猜；未给名称时直接询问。拒绝非 kebab-case 名称、与现有 `.codebuddy/skills/<name>/` 重名的名称，以及会遮蔽内置命令（`commit`、`learn`、……）的名称。先运行 `ls .codebuddy/skills/` 检查，发现占用就停下。
2. 阅读 [`templates/skill-template.md`](../../../templates/skill-template.md)，获取规范结构和 frontmatter 字段参考。
3. 略读目标领域附近的 2-3 个同类技能。例如先用 `Glob .codebuddy/skills/*/SKILL.md`，再 `Read` 最接近的几个，让新技能沿用真实约定，而不是凭空另造。

### Phase 1 —— 访谈（写作*之前*先收集齐）

技能无法在写作中途停下来提问，所以要把所有交互一次前置，遵循 [orchestrator-protocol.md](../../rules/orchestrator-protocol.md) 的 RUN_CONFIG 纪律。一次问清：

1. **用途**：用一句话说明它完成什么、为什么需要它。
2. **何时该触发**：用户在需要它时会处于哪 2-4 个*情境*，例如「准备投稿」或「两次运行之间某个数字变了」，再补充一两个用户真会说的中文示例。这些内容会成为 `description` 的「Use when…」子句。重点是点名意图类别，不是罗列近义词。元数据负责匹配，正文在触发时加载，附属材料按需读取；把最关键的用途放在最前，不要引入其他产品的截断长度或字段语义。
3. **输入 / 参数**：位置参数和所有**参数**分别是什么，每个参数都必须记录为 `--token`。
4. **工具**：正文需要 Read、Write、Grep/Glob 或 `Bash` 吗？需要用 Agent 扇出子代理吗？需要通过 `WebSearch`/`WebFetch` 联网吗？只声明实际使用的工具。
5. **输出**：写文件（写到哪里）、在聊天中报告，还是就地编辑？是否应当只读？
6. **范围边界**：明确**不**做的一两件事，以及这些事项分别由哪个同类技能负责。
7. **副作用**：哪些步骤会发送、发布或上传内容，包括邮件、GitHub、外部模型和云同步，或产生无法由 git 撤销的影响？每个这样的步骤都要先向用户说明具体动作，等到 yes 才执行；受限数据还要遵守 [`confidential-data.md`](../../rules/confidential-data.md)。
8. **新鲜的眼睛**：技能是否会批评本会话产出的内容？这部分必须在独立上下文的子代理中运行，绝不使用对话分叉，见 [`post-flight-verification.md`](../../rules/post-flight-verification.md)。

开始写作前，给出一份**设计简报**，请用户确认。

### Phase 2 —— 写 SKILL.md（深模块、简接口）

依据模板生成 `.codebuddy/skills/<name>/SKILL.md`，并遵守这些约定：

- frontmatter 包含 `name`、`description`、`argument-hint`、`allowed-tools`，以及仅在技能确实需要不同模型档位时设置的 `model`。`description` 用第三人称，先说明功能，再按意图类别说明何时使用。`model` 的钉定会*覆盖*会话设置，无论调高还是调低，见 `model-routing.md`。**技能里不要写 `effort`**：技能加载器不读取它，写了既不报错也不生效；代理会读取该字段，但技能不是代理。如果技能会写出持久且承重的文件，按模板「何时该禁用」规则添加 `disable-model-invocation: true`。此后其他技能无法调用它，只能 Read 它的 `SKILL.md` 并照做。
- 正文包含**何时使用**、**目标与交付物**、**每条约束连同它的理由**、**如何核验做完了**、**输出 / 报告格式**、**退出行为**、**交叉引用**（指向真实同类文件）、**本技能不做什么**；宣传了任何参数时，还要有一节 **## 参数**。只有顺序确实重要时才给阶段编号，例如先访谈再写作、先核验再报告。当前模型已经善于规划，为判断类任务写死分步脚本往往会降低输出质量，而不是提高安全性。
- 让 `SKILL.md` 能一次坐下读完，篇幅远少于约 500 行。长评分细则、完整算例和参考表移到旁边的文件，例如 `references/`，再添加链接，确保只在需要时加载。
- 保持*接口*小、*实现*深：只提供少数参数，把主要工作放在阶段内部，不要为每个内部选择都增加旋钮。

### Phase 3 —— 技能文件完整性验收（第一个完成状态）

`check-skill-integrity.py` 强制检查以下对齐关系，本阶段必须全部满足。检查器位于 `scripts/check-skill-integrity.py`，`./scripts/backtest.sh` 会运行所有门禁：

- **参数双向对齐。** `argument-hint` 中的每个参数都**必须**在正文中以裸反引号 token 出现，正文中记录的每个参数也**必须**出现在 `argument-hint` 中。因此 `--from-learn` 和 `--dry-run` 既列在 hint 中，也要在 `## 参数` 下说明。hint 中残留过时参数，与漏记参数一样会导致门禁失败。
- **allowed-tools 对齐（仓库文档契约）。** 检查器要求正文点名的工具也列入 `allowed-tools`。阶段需要扇出子代理时，列表必须有 `Agent`；从不扇出就不要列。本技能只列 `Read, Write, Glob, Grep, Bash`，正好是各阶段实际使用的工具，不做子代理扇出。这层对齐管理的是**白名单与文档一致性**：正文需要的工具必须进入 `allowed-tools`；实际执行仍要核验模型行为、权限规则和钩子，不能把对齐当成绝对安全保证。
- **锚点解析。** 内部 `[text](path#anchor)` 链接必须能解析，只能链接到确实存在的标题。

运行 `python scripts/check-skill-integrity.py --verbose`，修复所有 P0/P1 后复跑。此时只能报告「技能文件已创建，`check-skill-integrity` 通过（或失败）」，不得声称 surface-sync 或全部门禁通过。

### Phase 4 —— 提醒：表面登记与最终验收（独立第二步）

技能列入表面清单后，读者才能发现它，而且清单计数必须与磁盘实际数量一致。`check-surface-sync.sh` 运行两项检查。**表格行门禁**要求 `README.md` 中 `<!-- surface-sync-table: skills -->` 表格与磁盘技能一一对应，每个技能恰好一行数据。**计数断言**要求所有陈述技能数量的清单措辞，例如「N 个代理、M 个技能、……」，在 `README.md`、`CODEBUDDY.md`、`guide/workflow-guide.qmd`、两份渲染后的指南副本（`guide/workflow-guide.html`、`docs/workflow-guide.html`）、`docs/index.html`、`templates/skill-template.md` 和 `.codebuddy/skills/commit/SKILL.md` 中，都等于技能目录数量。

打印可直接粘贴的 README 行，并 REMIND 用户完成这个独立步骤：

1. 在 **README.md** 的技能表中加一行：`` | `/<name>` | <what it does> | ``。该表受门禁约束。
2. 在指南 `guide/workflow-guide.qmd` 的 `## 全部技能 {#all-skills}` 附录表中加一行。该表没有 surface-sync 标记，漏行不会有门禁发现。
3. 更新所有技能计数。运行 `python scripts/check-surface-sync.py`，每行 `asserts N skills (actual: M)` 都会指出需要更新的 file:line。
4. 仅当新技能属于最常用技能时，才可把它加入 CODEBUDDY.md 的「## 技能速查」项目符号清单；该清单没有门禁检查。
5. 指南先改 `guide/workflow-guide.qmd`，再运行 `quarto render guide/workflow-guide.qmd`、`cp guide/workflow-guide.html docs/workflow-guide.html` 和 `python scripts/stamp-render.py`，让两份 HTML 副本与渲染戳记保持同步。
6. README 行、计数和指南全部更新后，复跑 `./scripts/check-surface-sync.sh` 与 `python scripts/check-skill-integrity.py`。两者都以 0 退出，才能声明 **surface-sync 与技能完整性通过**。
7. 只有随后运行完整门禁总检（`python scripts/backtest.py`，或 POSIX 环境的 `./scripts/backtest.sh`）并以 0 退出，才能声明**全部门禁通过**；两项局部检查不能替代总检。
8. 检查技能成本和触发情况：`/skill-doctor` 显示上下文成本与使用情况；评测用例存在后，用 `./scripts/run-skill-eval.sh` 运行它们。

## 输出 / 报告格式

- 在 `.codebuddy/skills/<name>/SKILL.md` 创建新文件。
- 在聊天中汇总确定的名称、设计简报、`check-skill-integrity` 的实际结果，以及可直接粘贴的 README 行。摘要必须区分「技能文件创建」与「表面登记 / 最终门禁」；对应更新和复跑完成前，后两者一律标为尚未验收，不能写成已通过。
- 带 `--dry-run` 时，只把拟定的 SKILL.md 发到聊天中，不写任何内容。

## 退出行为

- **技能文件已创建、`check-skill-integrity` 通过：** 以 0 退出，给出路径、完整性检查结果和 README 行；明确提醒 surface-sync 与全部门禁尚未验收，以及各自需要的更新和复跑。不得使用「门禁全绿」。
- **表面登记与最终验收已完成：** 只有用户或维护者已补齐 README 行、计数和指南，且 surface-sync 复跑通过，才能报告表面同步通过；只有完整门禁总检也以 0 退出，才能另报全部门禁通过。
- **名称重名或不符合 kebab-case：** 在 Phase 0 停下并指出冲突，不写任何内容。
- **`check-skill-integrity.py` 报 P0/P1：** 就地修复并重跑后再返回，绝不交付连自身门禁都未通过的技能。
- **`--dry-run`：** 打印草稿，不写任何内容，以 0 退出。

## 参数

- `--from-learn` —— 不带值的选项，可放在名称前后；以现有 `/learn` 风格存根或本会话发现作为访谈起点，把它升级为完整合规的技能，而不是从空白开始。
- `--dry-run` —— 不带值的选项，可放在名称前后；在聊天中生成 SKILL.md 内容供审阅，不写磁盘，也不改任何表面表格。

名称取 `$ARGUMENTS` 中首个非选项 token。选项不会消耗后一个 token，因此 `/new-skill --dry-run example-skill` 的名称仍是 `example-skill`。

## 交叉引用

- [`templates/skill-template.md`](../../../templates/skill-template.md) —— 规范结构、frontmatter 字段参考，以及本技能遵守的「何时该设 `disable-model-invocation`」规则。
- [`.codebuddy/skills/learn/SKILL.md`](../learn/SKILL.md) —— 捕获一次会话发现（更轻的同类技能）；`--from-learn` 升级它的产出。
- [`.codebuddy/skills/coauthor-brief/SKILL.md`](../coauthor-brief/SKILL.md) —— 一个可模仿的结构示例（访谈 → 写作 → 参数 → 退出行为的形态）。
- [`.codebuddy/rules/orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) —— 为什么访谈要在写作*之前*收集齐所有交互。
- `scripts/check-skill-integrity.py` 与 `scripts/check-surface-sync.sh`（两者都由 `scripts/backtest.sh` 运行）—— 分别对应技能文件完整性与表面登记两个验收状态。

## 本技能不做什么

- **不捕获会话发现。** 那是 [`/learn`](../learn/SKILL.md) 的职责；本技能设计接口，`/learn` 记录发现。
- **不替你编辑 README 技能表或 CODEBUDDY.md 速查清单。** 它只*打印* README 行并提醒你。登记并重跑 `./scripts/check-surface-sync.sh` 是有意保留的人工步骤，避免表面门禁被悄悄满足。
- **不编写代理、规则或钩子。** 它只创建技能；代理放在 `.codebuddy/agents/`，规则放在 `.codebuddy/rules/`。
- **不提交任何内容。** 分支、提交和 PR 由 [`/commit`](../commit/SKILL.md) 负责；是否合并由用户决定。
