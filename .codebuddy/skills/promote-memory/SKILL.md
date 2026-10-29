---
name: promote-memory
description: 审读 WorkBuddy 原生自动记忆（`~/.workbuddy/projects/<project>/memory/`，机器本地）里的候选经验，并让它们并行通过一个五位评审员的评议会：通用性、时效性、冗余性、证据、格式。多数票（5 票中 3 票以上）把该条目提升进 MEMORY.md。当用户说 "promote memory"、"review my learnings"、"what should graduate to MEMORY.md"、"five-critic council"，或作为每月的记忆维护时使用。
description_zh: 审读 WorkBuddy 原生自动记忆（`~/.workbuddy/projects/<project>/memory/`，机器本地）里的候选经验，并让它们并行通过一个五位评审员的评议会：通用性、时效性、冗余性、证据、格式。多数票（5 票中 3 票以上）把该条目提升进 MEMORY.md。当用户说 "promote memory"、"review my learnings"、"what should graduate to MEMORY.md"、"five-critic council"，或作为每月的记忆维护时使用。
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

本模板的 [`meta-governance.md`](../../rules/meta-governance.md) 规则把记忆分成两层：

- **`MEMORY.md`**（已提交，≤ 200 行）—— 对所有 fork 本模板的人都有帮助的通用经验。
- **原生自动记忆**（`~/.workbuddy/projects/<project>/memory/` —— 机器本地，类型为 `user`/`feedback`/`project`/`reference`，主题文件无体积上限）—— 机器相关与用户相关的经验。

规则说通用模式应当通过 git 同步，个人模式留在本机。**它没说**的是*由谁来决定哪个是哪个*。`/promote-memory` 把这句判断操作化：并行生成五位评审员，每位只在单一维度上审读候选 `[LEARN]` 条目，按多数票（5 票中 3 票以上）提升。

## 何时使用

- **每月记忆维护。** 个人记忆积累得比 MEMORY.md 快；评议会定期收割真正通用的经验。
- **分享 fork 之前。** 有人正准备克隆你的模板 —— 他们该继承什么？
- **一个大项目交付之后。** 一篇论文或一轮课程的经验，值得在下一个项目开始添噪音之前先做一遍策展。
- **不要按日程跑。** 本技能由用户调用（`disable-model-invocation`），所以定时任务无法触发它，而它的候选住在机器本地的自动记忆里，云端例行任务看不到。给自己设一个月度提醒，在本地会话里跑；反正每一次提升都要等你批准。

## 何时不要使用

- **为一次纠正后产生的单独一条新 `[LEARN]`。** 让自动记忆自己记下就好；让它在盘上待着，等下次评议会跑。
- **为删除过期条目。** 按 `meta-governance.md` 手工编辑 MEMORY.md（加带日期的补记，或合并以守住上限）。`/promote-memory` 从不删除 —— 不过在接近上限时它会*提议*一次降级（第 4 步）。
- **为项目专属的语境。** 那属于 CODEBUDDY.md 或会话日志，不属于任何一层记忆。

## 五位评审员

每位评审员在一个隔离的独立上下文中运行（自己的一次 `Agent` 调用 —— 绝不是对话分叉）—— 它们看不到彼此的裁定，也看不到用户的草稿。每位对每个候选条目投一张 **YES/NO** 票，附一句理由。

### 1. 通用性评审员

> 「一位非经济学专业的 fork 者 —— 一位生物学博士生、一位社会学博士后、一位计算机讲师 —— 能从这条 `[LEARN]` 条目里获益吗？如果这条经验只针对*你*那套环境（你的参考文献路径、你机器上的 TeX 安装、你学科的记号），投 NO。」

### 2. 时效性评审员

> 「这条条目与代码库的当前状态矛盾吗？对该条目提到的文件路径、函数名或设置跑 `grep -r`。如果被引用的东西已经被改名、删除或显著改动，投 NO —— 这条条目已经过期，会误导未来的会话。」

### 3. 冗余性评审员

> 「这条经验是否已经写进 MEMORY.md、CODEBUDDY.md 或某条既有规则？读相关文件。如果是（哪怕是换了个说法），投 NO —— 重复会侵蚀索引的信号。」

### 4. 证据评审员

> 「这条条目是否引用了催生它的那次事故、文件路径或具体案例？如果这条条目是 `[LEARN:foo] always do X`，而对*为什么*没有任何锚点，投 NO。未来的会话没有理由，就无法判断边界情形。」

### 5. 格式评审员

> 「这条条目是否符合它将落入的那一层的格式？MEMORY.md 条目是 `[LEARN:category] wrong → right`（见 [`MEMORY.md`](../../../MEMORY.md) 本身）；从原生自动记忆来的 feedback/project 候选应当带上自动记忆写入的 `**Why:**` + `**How to apply:**` 行，好让理由扛过这次搬家。如果它只是一段自由格式的笔记，投 NO —— 先修格式，再重新提交。」

### 评议会裁定

每位评审员返回 YES/NO + 理由。提升门槛是**多数（3 票以上 YES）**。

- **5 票 YES** —— 原样提升。
- **4 票 YES** —— 提升，附一行关于反对意见的说明。
- **3 票 YES** —— 提升，但先处理反对评审员的关切（通常是：删冗、补证据、修格式）。
- **2 票或更少 YES** —— 不提升。要么按反对评审员的反馈修好条目再重新提交，要么把它留在自动记忆里。

## 步骤

### 第 1 步：读候选条目

如果 `$ARGUMENTS` 是 `all`，读 `~/.workbuddy/projects/<project>/memory/` 下的每一个主题文件（跳过那里的 `MEMORY.md`：它只是一个指向各主题文件的索引）；每个主题文件是一个候选。否则把 `$ARGUMENTS` 当作对主题文件文件名、`description` 或类型的子串过滤器（例如 `latex` 匹配 `feedback_latex_texinputs.md`，`feedback` 匹配每一条 feedback 记忆）。自动记忆不以 `[LEARN:category]` 形式存储条目；只有到第 4 步出提案时，候选才会被改写成那个形状。

### 第 2 步：组建评议会

并行五次 `Agent` 调用，每位评审员一次，各自在独立上下文中：

- **通用性评审员** —— 上下文：候选条目 + 一段描写本模板受众是谁的文字（跨学科的学术研究者）。
- **时效性评审员** —— 上下文：候选条目 + 对该代码库执行 `Read` / `Grep` 的能力。应当显式检查条目提到的任何文件路径 / 函数名 / 设置。
- **冗余性评审员** —— 上下文：候选条目 + 当前的 `MEMORY.md` + `CODEBUDDY.md` + 相关规则文件。
- **证据评审员** —— 上下文：仅候选条目。投票依据是条目是否自我描述了它的动机。
- **格式评审员** —— 上下文：候选条目 + [`.codebuddy/rules/meta-governance.md`](../../rules/meta-governance.md) 作为 schema 参照。

五位评审员全部使用 **`lite` 档**（依据 [`.codebuddy/rules/model-routing.md`](../../rules/model-routing.md)：偏机械的审读工作）。如果用户为更难的判断想要 `default` 档，可以通过代理的 `model:` 字段覆盖。

### 第 3 步：汇总投票

收集裁定。对每个候选条目算出票数与逐位评审员的裁定。

### 第 4 步：呈现裁定

对每个条目：

```markdown
## `[LEARN:foo] <summary>`

**Vote:** 4-of-5 YES (promote with note)

| Critic | Vote | Rationale |
|---|:---:|---|
| Generality | YES | ... |
| Staleness | YES | ... |
| Redundancy | YES | ... |
| Evidence | NO  | Entry doesn't cite the originating incident. Add a one-line "Incident:" pointer before promoting. |
| Format | YES | ... |

**Recommendation:** Address Evidence critic, then promote.

**Proposed MEMORY.md addition:**
```text
[LEARN:foo] <full proposed text>
```
```

**接近上限时，增加就意味着删除。** MEMORY.md 的上限是 200 行**且** 25KB，而通常是字节上限先顶住。当现有文件加上拟增条目会超过约 190 行或约 24KB（`wc -c MEMORY.md`）时，报告还要点名**当前最弱的条目**作为降级候选 —— 过期（点名的文件、开关或模型已不存在）、被更新的规则推翻，或属于本地而非通用 —— 连同证据一起给出，并问用户是把它移进自动记忆还是删掉。保留一条条目的检验标准：*删掉它会在很多任务上导致出错吗？*

### 第 5 步：用户批准提升

用户审阅报告，明确批准哪些条目可以提升。技能把批准的条目写进 MEMORY.md，在其自动记忆主题文件里给同样的条目打上 `# promoted YYYY-MM-DD` 标记以便审计，并给出一份摘要。

**不要**自动提升 —— 即便是 5 票全 YES。用户的批准是最后一道门。

## 输出

- 逐条目的评议会报告（裁定、理由、建议）—— 到对话里。
- 批准后：MEMORY.md 更新（追加到相应的 `[LEARN:category]` 小节），自动记忆主题文件更新（条目标为已提升）。
- 一份 `quality_reports/memory_promotion_<date>.md` 审计文件，记录整场评议会，以备事后取证。

## 反模式

- **在 5 票全 YES 时自动提升。** 即便评审员一致同意也可能判错；用户的领域判断是最后一道门。
- **反复对同一条目重跑评议会**，指望得到不同的结果。如果 4 位评审员持续投 NO，这条条目就不属于 MEMORY.md —— 留在自动记忆里，停止。
- **因为条目「看起来显然」就跳过证据评审员。** 证据正是让条目能跨 fork 者移植的东西；对你显然 ≠ 对他们显然。
- **通过本技能做降级。** 它只做提升。降级是手工编辑 + 提交。

## 交叉引用

- [`.codebuddy/rules/meta-governance.md`](../../rules/meta-governance.md) —— 本技能所操作化的两层记忆契约。
- [`.codebuddy/agents/promote-memory-council.md`](../../agents/promote-memory-council.md) —— 五位评审员的实现（一个代理文件含五份角色说明，通过 `Agent` 工具并行派发）。
- [`.codebuddy/rules/model-routing.md`](../../rules/model-routing.md) —— 评审员为何默认用 `lite` 档。
- `/learn`（既有技能）—— 捕获新的 `[LEARN]` 条目；与 `/promote-memory` 配对（后者决定什么毕业）。

## 候选来源（v2.5）

候选来自**原生自动记忆** —— `~/.workbuddy/projects/<project>/memory/`。WorkBuddy 在工作过程中自己写入这些条目，类型为 `user` / `feedback` / `project` / `reference`，而那里的 `MEMORY.md` 是一个索引，不是内容本身。

提升的问题没有变，而且它正是全部要点：*一位在另一个领域、fork 了本模板的研究者，知道这件事会过得更好吗？* 会，它就属于已提交的 `MEMORY.md`；如果它说的是这台机器、这份数据集或这个人的偏好，它就留在本机。

**已退役：** `.codebuddy/state/personal-memory.md`。两层记忆的想法是对的；WorkBuddy 现在原生提供本机这一层，所以手工搭的那个文件是多余的。已存在的那份仍可作为普通文件读取，但没有东西往里写。

## 捕获门禁 —— 在任何东西被记住之前

提升决定什么成为*共享*知识。这道门禁决定什么**值得记录**。五个问题；一个候选项必须全部通过：

1. **耐久** —— 六个月后它仍然成立吗，还是只是关于今天这个分支？
2. **非显然** —— 一位胜任的人会不会五分钟内自己就重新发现它？
3. **稳定** —— 它描述的是一条规则，还是一个会被某个修复抹掉的症状？
4. **具体** —— 它是可执行的吗，还是一种心情？*"Be careful with merges"* 是一种心情。
5. **尚未被捕获** —— 已有条目覆盖它了吗？那就扩充那一条。

> **「以防万一」的记忆一律禁止。** 它们污染索引，让有用的条目变得找不到。一个没人信任的记忆库，就是一个没人读的记忆库。

从本机观察到已提交知识的提升是一次**经过审阅的行为，而不是自动保存** —— 这正是五位评审员评议会存在的原因，也是为什么即便全票通过，用户仍是最后一道门。
