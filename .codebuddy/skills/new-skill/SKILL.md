---
name: new-skill
description: 按本仓库约定搭出一个新技能——先就用途、触发短语与工具需求做访谈，然后从技能模板写出 `.codebuddy/skills/<name>/SKILL.md`，写出后运行 `check-skill-integrity` 核验其 frontmatter 与正文。当用户说 "write a skill"、"scaffold a skill"、"create a new skill"、"I keep doing X, make it a skill"、"new slash command"、"turn this workflow into a skill"、"新建技能"、"把这套流程做成技能"、"新斜杠命令" 时使用。不用于捕获一次性的会话发现——那是 `/learn`。
description_zh: 按本仓库约定搭出一个新技能——先就用途、触发短语与工具需求做访谈，然后从技能模板写出 `.codebuddy/skills/<name>/SKILL.md`，写出后运行 `check-skill-integrity` 核验其 frontmatter 与正文。当用户说 "write a skill"、"scaffold a skill"、"create a new skill"、"I keep doing X, make it a skill"、"new slash command"、"turn this workflow into a skill"、"新建技能"、"把这套流程做成技能"、"新斜杠命令" 时使用。不用于捕获一次性的会话发现——那是 `/learn`。
argument-hint: "[skill-name (kebab-case)] [--from-learn] [--dry-run]"
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
disable-model-invocation: true

---

# /new-skill —— 编写符合约定的技能

按本仓库的既有约定搭一个新技能：**简单接口背后的深模块**（Ousterhout，《A Philosophy of Software Design》——「deep modules」：一个小的表面，藏着可观的实现）。用户给出的是模糊意图；本技能把它访谈成一份紧凑的规格，写出 `.codebuddy/skills/<name>/SKILL.md`，再运行 `check-skill-integrity.py` 核验 frontmatter 与正文。技能文件创建与表面登记是两个完成状态：完整性通过不等于 `check-surface-sync.sh` 或全部门禁通过。

`/new-skill` 是本仓库的项目技能，负责落实本仓库的字段、章节与门禁约定。WorkBuddy 内置的 `/skill-creator` 才是通用创建器（GUI：技能 → 添加技能 → 创建技能）；不要用其中一个的行为推断另一个。

改编自 [mattpocock/skills](https://github.com/mattpocock/skills) 中的 *write-a-skill* 模式，按本仓库的 frontmatter、章节与门禁约定重塑。

## 何时使用

- 你反复向 WorkBuddy 解释同一套 3 步以上的工作流，想把它固化成可复用的斜杠命令。
- 你需要一个领域专属的检查或输出格式（引文风格、复现门禁、一个新的审读透镜）。
- 你想要一个新技能，与 `.codebuddy/skills/` 里的现有技能保持一致——同样的章节、同样的交叉引用风格、同样能过门禁的 frontmatter。

**改用 `/learn`** 当你只是*本会话*刚发现了一件不显然的事、想把它留住——`/learn` 捕获一次发现；`/new-skill` 则是有意设计一个接口。加上 `--from-learn`，本技能会把一个 `/learn` 形状的存根升级成完整合规的技能。

## 阶段

### Phase 0 —— 确定名称并检查重名

1. 从 `$ARGUMENTS` 解析输入；平台提供的是完整参数字符串，不提供 `$0` / `$1` 位置参数。取**首个非选项 token** 作为技能名称，`--from-learn` 与 `--dry-run` 是不带值的选项，可位于名称之前或之后。名称须为单个 kebab-case token；出现第二个位置参数、未知选项或无法确定的结构时，先停下询问，不要猜测。未给名称就直接问。拒绝非 kebab-case 的名称、与既有 `.codebuddy/skills/<name>/` 撞车的名称，或遮蔽内置命令（`commit`、`learn`、……）的名称——先 `ls .codebuddy/skills/`，已被占用就停下。
2. 读 [`templates/skill-template.md`](../../../templates/skill-template.md)，取得规范结构与 frontmatter 字段参考。
3. 略读目标领域附近 2-3 个同类技能（例如 `Glob .codebuddy/skills/*/SKILL.md`，再 `Read` 最接近的几个），让新技能借用真实约定，而不是凭空发明的约定。

### Phase 1 —— 访谈（写作*之前*先收集齐）

技能没法在写的过程中停下来提问，所以把所有交互一次性前置（[orchestrator-protocol.md](../../rules/orchestrator-protocol.md) 的 RUN_CONFIG 纪律）。一次问完：

1. **用途** —— 一句话：它达成什么，为什么存在？
2. **何时该触发** —— 用户在需要它时处于哪 2-4 个*情境*（例如「准备投稿」「两次运行之间某个数字变了」），再加一两个用户真会说的中文示例。这些会成为 `description` 的「Use when…」子句。要点是点名意图类别，而不是罗列近义词：元数据用于匹配，正文在触发时加载，附属材料按需读取——把最关键的用途放在最前，不要引入其他产品的截断长度或字段语义。
3. **输入 / 参数** —— 位置参数与任何**参数**（每一个都必须成为被记录的 `--token`）。
4. **工具** —— 正文要 Read 吗？Write 吗？Grep/Glob 吗？跑 `Bash` 吗？扇出到子代理（Agent）吗？通过 `WebSearch`/`WebFetch` 上网吗？只声明它实际用到的。
5. **输出** —— 一个写出的文件（写哪儿？）、一份聊天报告，还是就地编辑？它应当是只读的吗？
6. **范围边界** —— 它明确**不**做的那一两件事（以及那些事归哪个同类技能管）。
7. **副作用** —— 哪些步骤会发送、发布或上传任何东西（邮件、GitHub、外部模型、云同步），或无法被 git 撤销？每个这样的步骤都要先向用户说明它将做什么，等到 yes 再执行；受限数据遵守 [`confidential-data.md`](../../rules/confidential-data.md)。
8. **新鲜的眼睛** —— 该技能会批评本会话产出的东西吗？那部分要在独立上下文的子代理中运行，绝不用对话分叉（[`post-flight-verification.md`](../../rules/post-flight-verification.md)）。

在动手写之前，回显一段**设计简报**供确认。

### Phase 2 —— 写 SKILL.md（深模块、简接口）

从模板写出 `.codebuddy/skills/<name>/SKILL.md`，包含这些约定章节：

- frontmatter：`name`、`description`（第三人称——先说它做什么，再按意图类别说何时使用）、`argument-hint`、`allowed-tools`，以及 `model`（仅当该技能确实需要一个不同于会话的档位时；见 `model-routing.md`——技能的钉定会*覆盖*会话，向下也向上。**技能里不要写 `effort`**：技能加载器不读它——写了不会报错，也不会起作用（代理读它，但技能不是代理））。若它会写出一个持久的、承重的文件，就加 `disable-model-invocation: true`（模板的「何时该禁用」规则）——并注意此后其他技能就无法调用它；它们必须 Read 它的 `SKILL.md` 并照做。
- 正文小节：**何时使用**；**目标与交付物**；**每条约束连同它的理由**；**如何核验做完了**；**输出 / 报告格式**；**退出行为**；**交叉引用**（指向真实的同类文件）；**本技能不做什么**；以及一节 **## 参数**（仅当宣传了任何参数时）。只在顺序确实要紧的地方给阶段编号（先访谈再写作，先核验再报告）——当前的模型规划得很好，而给判断类任务写一套分步脚本会让输出更差，不是更安全。
- 让 `SKILL.md` 一次坐得下来读得完（远少于约 500 行）。把长评分细则、完整算例与参考表移到它旁边的文件里（例如 `references/`）并链接过去，这样它们只在需要时才载入。
- 让*接口*小（几个参数）、*实现*深（重量在阶段里）——抵制为每一个内部选择都开一个旋钮。

### Phase 3 —— 技能文件完整性验收（第一个完成状态）

`check-skill-integrity.py` 强制两处对齐，本阶段必须满足（检查器是 `scripts/check-skill-integrity.py`；`./scripts/backtest.sh` 会跑每一道门禁）：

- **参数对齐（双向）。** `argument-hint` 里的每个参数都**必须**在正文中以裸反引号 token 出现，正文里记录的每个参数也**必须**出现在 `argument-hint` 中。所以 `--from-learn` 与 `--dry-run` 既列在 hint 里，*也*在 `## 参数` 下有所描述。hint 里一个过时的参数，和漏掉一个参数一样会让门禁失败。
- **allowed-tools 对齐（仓库文档契约）。** 检查器要求正文点名的工具也列入 `allowed-tools`。若某个阶段扇出到子代理，列表里就必须有 `Agent`；若从不扇出，就不要列它。本技能列出的恰好是 `Read, Write, Glob, Grep, Bash`——即它各阶段实际用到的工具；它不做子代理扇出。这里的对齐管理**白名单与文档一致性**：正文需要的工具必须进入 `allowed-tools`；实际执行仍须核验模型行为、权限规则与钩子，不能把这层对齐当作绝对安全保证。
- **锚点解析。** 内部的 `[text](path#anchor)` 链接必须能解析——只链接到确实存在的标题。

跑 `python scripts/check-skill-integrity.py --verbose`，修掉任何 P0/P1 后复跑。此时只能报告「技能文件已创建，`check-skill-integrity` 通过（或失败）」；不得报告 surface-sync 或全部门禁通过。

### Phase 4 —— 提醒：表面登记与最终验收（独立第二步）

在技能被列出来之前，读者发现不了它，而且清单计数必须与磁盘上的实际数量一致。`check-surface-sync.sh` 跑两项表面检查。**表格行门禁**要求 `README.md` 里的 `<!-- surface-sync-table: skills -->` 表格与磁盘上的技能一一对应，每个技能恰好一行数据。**计数断言**要求每一处陈述技能数量的清单措辞（例如「N 个代理、M 个技能、……」）在 `README.md`、`CODEBUDDY.md`、`guide/workflow-guide.qmd`、两份渲染后的指南副本（`guide/workflow-guide.html`、`docs/workflow-guide.html`）、`docs/index.html`、`templates/skill-template.md` 与 `.codebuddy/skills/commit/SKILL.md` 中，都等于技能目录的数量。

打印出可直接粘贴的 README 行，并 REMIND 用户完成这一独立步骤：

1. 在 **README.md** 的技能表里加一行：`` | `/<name>` | <what it does> | ``（受门禁约束的那张表）。
2. 在指南 `guide/workflow-guide.qmd` 的 `## 全部技能 {#all-skills}` 附录表里加一行。那张表没有 surface-sync 标记，所以漏行没有门禁能抓住。
3. 把每一处技能计数都加上去。跑 `python scripts/check-surface-sync.py`：每一行 `asserts N skills (actual: M)` 都点名了一个待更新的 file:line。
4. 可选地把该技能加进 CODEBUDDY.md 的「## 技能速查」项目符号清单——只有当它属于最常用的技能之列时；没有门禁检查那个清单。
5. 对指南先改 `guide/workflow-guide.qmd`，再运行 `quarto render guide/workflow-guide.qmd`、`cp guide/workflow-guide.html docs/workflow-guide.html` 与 `python scripts/stamp-render.py`，让两份 HTML 副本与渲染戳记同步。
6. 上述 README 行、计数与指南更新全部落地后，复跑 `./scripts/check-surface-sync.sh` 与 `python scripts/check-skill-integrity.py`。两者都以 0 退出，才可声明 **surface-sync 与技能完整性通过**。
7. 只有随后运行完整门禁总检（`python scripts/backtest.py`，或 POSIX 环境的 `./scripts/backtest.sh`）并以 0 退出，才可声明**全部门禁通过**；两项局部检查不能替代总检。
8. 检查该技能的成本与触发情况：`/skill-doctor` 显示它的上下文成本与使用情况；`./scripts/run-skill-eval.sh` 在它的评测用例存在后跑那些用例。

## 输出 / 报告格式

- 在 `.codebuddy/skills/<name>/SKILL.md` 生成一个新文件。
- 一份聊天摘要：定下的名称、设计简报、`check-skill-integrity` 的实际结果，以及可直接粘贴的 README 行。摘要把「技能文件创建」与「表面登记 / 最终门禁」分开：后两者在对应更新和复跑完成前一律标为尚未验收，不得写成已通过。
- 带 `--dry-run`：只把拟定的 SKILL.md 发到聊天里，什么都不写。

## 退出行为

- **技能文件已创建、`check-skill-integrity` 通过：** 以 0 退出，给出路径、完整性检查结果与 README 行；明确提醒 surface-sync 与全部门禁尚未验收，以及它们各自要求的更新和复跑。不得使用「门禁全绿」。
- **表面登记与最终验收已完成：** 只有用户或维护者已补齐 README 行、计数和指南，并且 surface-sync 复跑通过，才报告表面同步通过；只有完整门禁总检也以 0 退出，才另报全部门禁通过。
- **名称重名或非 kebab-case：** 在 Phase 0 停下并点名冲突；什么都不写。
- **`check-skill-integrity.py` 报 P0/P1：** 就地修好并重跑，再返回；绝不交回一个连自己门禁都过不了的技能。
- **`--dry-run`：** 打印草稿，什么都不写，以 0 退出。

## 参数

- `--from-learn` —— 不带值的选项，可放在名称之前或之后；以既有的 `/learn` 风格存根（或本会话的发现）为访谈的种子，把它升级成完整合规的技能，而不是从空白开始。
- `--dry-run` —— 不带值的选项，可放在名称之前或之后；在聊天里产出 SKILL.md 内容供审阅，不写到磁盘，也不碰任何表面表格。

名称取 `$ARGUMENTS` 中首个非选项 token。选项不消耗后一个 token；因此 `/new-skill --dry-run example-skill` 的名称仍是 `example-skill`。

## 交叉引用

- [`templates/skill-template.md`](../../../templates/skill-template.md) —— 规范结构、frontmatter 字段参考，以及本技能遵守的「何时该设 `disable-model-invocation`」规则。
- [`.codebuddy/skills/learn/SKILL.md`](../learn/SKILL.md) —— 捕获一次会话发现（更轻的同类技能）；`--from-learn` 升级它的产出。
- [`.codebuddy/skills/coauthor-brief/SKILL.md`](../coauthor-brief/SKILL.md) —— 一个可模仿的结构示例（访谈 → 写作 → 参数 → 退出行为的形态）。
- [`.codebuddy/rules/orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) —— 为什么访谈要在写作*之前*收集齐所有交互。
- `scripts/check-skill-integrity.py` 与 `scripts/check-surface-sync.sh`（两者都由 `scripts/backtest.sh` 运行）—— 分别对应技能文件完整性与表面登记两个验收状态。

## 本技能不做什么

- **捕获会话发现** —— 那是 [`/learn`](../learn/SKILL.md)。本技能设计接口；`/learn` 记录一条发现。
- **替你编辑 README 技能表（或 CODEBUDDY.md 的速查清单）。** 它只*打印* README 行并提醒你；登记它（并重跑 `./scripts/check-surface-sync.sh`）是有意保留的人工步骤，这样表面门禁永远不会被悄悄满足。
- **编写代理、规则或钩子。** 它只搭技能；代理放 `.codebuddy/agents/`，规则放 `.codebuddy/rules/`。
- **提交任何东西。** 分支、提交与 PR 是 [`/commit`](../commit/SKILL.md) 的活；合不合由用户决定。
