---
name: promote-memory
description: 审读 WorkBuddy 原生自动记忆（`~/.workbuddy/projects/<project>/memory/`，机器本地）中的候选经验，让五位评审员并行评估通用性、时效性、冗余性、证据和格式。多数票（5 票中至少 3 票 YES）通过后，才可提议把条目提升到 MEMORY.md。用户说 "promote memory"、"review my learnings"、"what should graduate to MEMORY.md"、"five-critic council"、"提升记忆"、"审阅经验条目" 或 "哪些该写进 MEMORY.md" 时使用，也可用于每月记忆维护。
description_zh: 审读 WorkBuddy 原生自动记忆（`~/.workbuddy/projects/<project>/memory/`，机器本地）中的候选经验，让五位评审员并行评估通用性、时效性、冗余性、证据和格式。多数票（5 票中至少 3 票 YES）通过后，才可提议把条目提升到 MEMORY.md。用户说 "promote memory"、"review my learnings"、"what should graduate to MEMORY.md"、"five-critic council"、"提升记忆"、"审阅经验条目" 或 "哪些该写进 MEMORY.md" 时使用，也可用于每月记忆维护。
argument-hint: "[entry-substring or 'all']"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Glob", "Grep", "Agent", "Task", "Bash"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

<!-- 本模式改编自 Chris Blattman 的 claudeblattman v2.1「Five-critic council」
     （claudeblattman.com，2026 年 4 月的持续改进循环），并保留署名。Blattman 用它
     决定什么进入他的 MEMORY 层；我们把它改用于自动记忆 → MEMORY.md 的提升问题，
     该问题已在 .codebuddy/rules/meta-governance.md 中成文。 -->

# `/promote-memory` —— 记忆提升的五位评审员评议会

本模板的 [`meta-governance.md`](../../rules/meta-governance.md) 把记忆分为三层：

- **`MEMORY.md`**（根目录，人工筛选并提交，≤ 200 行且严格 < 25KB）：保存对所有 fork 本模板的人都有帮助的通用经验。
- **原生自动记忆**（`~/.workbuddy/projects/<project>/memory/`，机器本地，类型为 `user`/`feedback`/`project`/`reference`，主题文件无体积上限）：保存与机器和用户有关的经验。
- **项目层 `.workbuddy/memory/`**（已 gitignore）：保存这个工作副本的按日工作日志与本机状态，不随 fork 或普通 `git clone` 复制。

通用模式通过 git 同步，机器与用户经验留在原生自动记忆，项目工作过程留在项目层。`/promote-memory` 负责判断原生自动记忆中的哪些候选 `[LEARN]` 条目足以成为共享知识：五位评审员分别从单一维度审读，按多数票（5 票中至少 3 票 YES）决定是否提议提升。项目层日志不是本技能的候选来源。

## 何时使用

- **每月记忆维护。**个人记忆通常比 MEMORY.md 增长更快，评议会定期筛出真正通用的经验。
- **分享 fork 之前。**有人准备克隆你的模板时，判断哪些经验值得由对方继承。
- **一个大项目交付之后。**在下一个项目引入新噪声前，整理论文或课程留下的经验。
- **不要按日程自动运行。**本技能由用户调用（`disable-model-invocation`），定时任务无法触发；候选又保存在机器本地的自动记忆中，云端例行任务无法读取。可以给自己设月度提醒，在本地会话中运行。每次提升仍须等待用户批准。

## 何时不要使用

- **刚因一次纠正产生单独一条新 `[LEARN]` 时。**让自动记忆先记录并留在磁盘，等下次评议会再审。
- **需要删除过期条目时。**按 `meta-governance.md` 手工编辑 MEMORY.md，可加带日期的补记，也可合并条目以守住上限。`/promote-memory` 从不删除；接近上限时，它只会在第 4 步*提议*降级。
- **处理项目专属语境时。**那属于 CODEBUDDY.md、项目层工作日志或会话日志，不应提升为通用记忆。

## 五位评审员

每位评审员都通过自己的一次 `Agent` 调用，在隔离的独立上下文中运行，**绝不是对话分叉**。他们看不到彼此的裁定，也看不到用户草稿。每位评审员对每个候选投一张 **YES/NO** 票，并附一句理由。

### 1. 通用性评审员

> 「一位非经济学专业的 fork 者，例如生物学博士生、社会学博士后或计算机讲师，能从这条 `[LEARN]` 条目中获益吗？如果这条经验只针对*你*的环境，例如你的参考文献路径、你机器上的 TeX 安装或你学科的记号，投 NO。」

### 2. 时效性评审员

> 「这条条目与代码库当前状态矛盾吗？对条目提到的文件路径、函数名或设置运行 `grep -r`。若被引用对象已经改名、删除或显著改动，投 NO，因为过期条目会误导未来会话。」

### 3. 冗余性评审员

> 「这条经验是否已经写进 MEMORY.md、CODEBUDDY.md 或某条既有规则？读取相关文件。若已有相同内容，即使措辞不同也投 NO，因为重复会削弱索引中的有效信号。」

### 4. 证据评审员

> 「这条条目是否说明*为什么*、何时适用、何时不适用，并给出当前可复核的证据，例如现存文件、可运行命令或当前行为？若它只写 `[LEARN:foo] always do X`，或只能依赖无法公开复核的单次事故，投 NO。事故指针可作补充，但不是晋升硬条件；私有或本机证据留在原处。」

### 5. 格式评审员

> 「五票阶段审查原始候选的现有结构，不要求它已有 `[LEARN:category]`。候选是否遵循原生自动记忆的结构（见 [`meta-governance.md`](../../rules/meta-governance.md)）？来自原生自动记忆的 feedback/project 候选，应保留自动记忆写入的 `**Why:**` + `**How to apply:**` 行，让理由随条目一起迁移。若候选只是缺少主题或正文的碎片，或 feedback/project 候选缺少上述原生结构，投 NO；原始候选没有 `[LEARN:category]` 标签不是 NO 的理由。第 4 步形成拟提升文本后，再检查它是否以 `[LEARN:category] <原则/总结>` 开头、类别是否与 MEMORY.md 邻近条目一致，以及是否说明通用理由、适用边界和当前可复核证据（见 [`MEMORY.md`](../../../MEMORY.md)）；证据可以是现存文件、可运行命令或当前行为，不强制采用 wrong → right。不要把后一阶段的目标格式检查记成对原始候选的否决票。」

### 评议会裁定

每位评审员返回 YES/NO + 理由。提升门槛是**多数（至少 3 票 YES）**。

- **5 票 YES**：原样提议提升。
- **4 票 YES**：提议提升，并附一行反对意见说明。
- **3 票 YES**：先处理反对评审员的关切，通常包括删冗、补证据或修格式，再提议提升。
- **2 票或更少 YES**：不提升。按反馈修好后重新提交，或把条目留在自动记忆中。

## 步骤

### 第 1 步：读候选条目

若 `$ARGUMENTS` 是 `all`，读取 `~/.workbuddy/projects/<project>/memory/` 下的每个主题文件，每个文件作为一个候选；跳过该目录的 `MEMORY.md`，因为它只是指向主题文件的索引。否则，把 `$ARGUMENTS` 当作主题文件名、`description` 或类型的子串过滤器。例如，`latex` 匹配 `feedback_latex_texinputs.md`，`feedback` 匹配每条 feedback 记忆。自动记忆不以 `[LEARN:category]` 格式存储条目；直到第 4 步形成提案时，才把候选项改写成这种格式。

### 第 2 步：组建评议会

并行发起五次 `Agent` 调用，每位评审员一次，各自使用独立上下文：

- **通用性评审员**：提供候选条目和本模板受众说明，即跨学科学术研究者。
- **时效性评审员**：提供候选条目，并允许它对代码库执行 `Read` / `Grep`。它必须显式检查条目提到的任何文件路径／函数名／设置。
- **冗余性评审员**：提供候选条目、当前 `MEMORY.md`、`CODEBUDDY.md` 和相关规则文件。
- **证据评审员**：提供候选条目，并允许它对条目点名的当前文件、命令或行为做只读复核。通用理由、适用边界和当前可复核证据是评审对象；单次事故引用不是硬条件。
- **格式评审员**：提供候选条目和 [`.codebuddy/rules/meta-governance.md`](../../rules/meta-governance.md) 作为 schema 参照。

五位评审员默认使用 **`lite` 档**，因为 [`.codebuddy/rules/model-routing.md`](../../rules/model-routing.md) 将这类工作归为偏机械的审读。用户若希望用 `default` 档处理更复杂的判断，可以通过代理的 `model:` 字段覆盖。

### 第 3 步：汇总投票

收齐裁定，为每个候选统计票数，并逐位列出评审员的判断。

### 第 4 步：呈现裁定

对每个条目：

```markdown
## `[LEARN:foo] <原则/总结>`

**Vote:** 4-of-5 YES (promote with note)

| Critic | Vote | Rationale |
|---|:---:|---|
| Generality | YES | ... |
| Staleness | YES | ... |
| Redundancy | YES | ... |
| Evidence | NO  | Entry lacks a reusable rationale, applicability boundary, or currently checkable evidence. Add those before promoting; an incident citation is optional. |
| Format | YES | ... |

**Recommendation:** Address Evidence critic, then promote.

**Proposed MEMORY.md addition:**
```text
[LEARN:foo] <原则/总结>
**Why:** <通用理由>
**How to apply:** <适用边界>
**Evidence:** <现存文件、可运行命令或当前行为>
```
```

**接近上限时，增加条目就必须考虑删除。**MEMORY.md 不超过 200 行**且**严格小于 25KB，通常先达到字节上限。若现有文件加上拟增条目后会超过约 190 行或约 24KB（`wc -c MEMORY.md`），报告还要指出**当前最弱的条目**作为降级候选，并附证据。降级理由可以是条目过期，例如点名的文件、开关或模型已不存在；被更新规则推翻；或只适用于本机而非通用场景。随后询问用户，是把它移入自动记忆还是删除。判断条目是否值得保留时，问：*删掉它会在很多任务上导致出错吗？*

### 第 5 步：用户批准提升

用户审阅报告并明确批准可提升的条目。技能随后把批准条目写入 MEMORY.md，在对应自动记忆主题文件中标记 `# promoted YYYY-MM-DD` 以便审计，并给出摘要。

**即使 5 票全 YES，也不要自动提升。**用户批准是最后一道门。

## 输出

- 在对话中给出逐条目的评议会报告，包括裁定、理由和建议。
- 用户批准后，更新 MEMORY.md，把条目追加到相应 `[LEARN:category]` 小节；同时更新自动记忆主题文件，标记条目已提升。
- 写一份 `quality_reports/memory_promotion_<date>.md` 审计文件，记录整场评议会，供事后取证。

## 反模式

- **5 票全 YES 就自动提升。**评审员一致同意仍可能判错，用户的领域判断是最后一道门。
- **反复对同一条目重跑评议会，期待不同结果。**若 4 位评审员持续投 NO，条目就不属于 MEMORY.md；留在自动记忆中并停止。
- **因为条目「看起来显然」就跳过证据评审员。**证据决定条目能否跨 fork 者迁移；对你显然，不代表对他们显然。
- **通过本技能降级条目。**本技能只负责提升，降级需要手工编辑 + 提交。

## 交叉引用

- [`.codebuddy/rules/meta-governance.md`](../../rules/meta-governance.md) —— 本技能所执行的三层记忆契约。
- [`.codebuddy/agents/promote-memory-council.md`](../../agents/promote-memory-council.md) —— 五位评审员的实现；一个代理文件包含五份角色说明，通过 `Agent` 工具并行派发。
- [`.codebuddy/rules/model-routing.md`](../../rules/model-routing.md) —— 评审员默认使用 `lite` 档的依据。
- `/learn`（既有技能）—— 捕获新的 `[LEARN]` 条目；`/promote-memory` 决定哪些条目可以毕业。

## 候选来源（v2.5）

候选只来自**原生自动记忆**：`~/.workbuddy/projects/<project>/memory/`。WorkBuddy 在工作过程中写入这些条目，类型为 `user` / `feedback` / `project` / `reference`；该目录的 `MEMORY.md` 是索引，不是内容本身。项目层 `.workbuddy/memory/` 保存按日工作日志与本机状态，不能直接整份提升为共享知识。

提升时仍要回答同一个问题：*另一位领域不同、fork 了本模板的研究者，知道这件事会过得更好吗？*若会，它属于已提交的 `MEMORY.md`；若它只涉及这台机器、这份数据集或这个人的偏好，就留在本机。

**已退役：** `.codebuddy/state/personal-memory.md`。本机经验与共享知识分离的设计仍然有效，WorkBuddy 现在原生提供本机记忆层，因此手工维护的文件已多余。既有文件仍可作为普通文件读取，但没有机制继续写入。

## 捕获门禁 —— 在任何东西被记住之前

提升决定什么成为*共享*知识，捕获门禁决定什么**值得记录**。候选项必须全部通过以下五个问题：

1. **耐久**：六个月后仍然成立吗，还是只适用于今天这个分支？
2. **非显然**：一位胜任的人会在五分钟内自己重新发现它吗？
3. **稳定**：它描述的是一条规则，还是一个会被某个修复抹掉的症状？
4. **具体**：它能指导行动吗，还是只表达一种心情？*"Be careful with merges"* 就是一种心情。
5. **尚未被捕获**：已有条目覆盖它吗？若有，应扩充原条目。

> **禁止写入「以防万一」的记忆。**它们会污染索引，让有用条目难以找到。没人信任的记忆库，最终也没人阅读。

从本机观察到已提交知识的提升，是一项**经过审阅的行为，而不是自动保存**。五位评审员评议会因此存在；即使全票通过，用户仍是最后一道门。
