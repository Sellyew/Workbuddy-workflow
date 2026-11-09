---
name: interview-me
description: 通过互动访谈，把模糊的研究想法整理成结构化研究需求说明，涵盖研究问题、假设、识别、数据需求和实证策略。用户说 "interview me"、"help me think through this idea"、"I have a half-baked idea"、"formalize this into a project"、"walk me through framing a study"、"访谈我"、"帮我理清研究想法" 或 "把想法变成研究方案" 时使用。技能会多轮问答并把研究需求说明保存到磁盘。不用于文献综述（`/lit-review`），也不用于从零构想（`/research-ideation`）。
description_zh: 通过互动访谈，把模糊的研究想法整理成结构化研究需求说明，涵盖研究问题、假设、识别、数据需求和实证策略。用户说 "interview me"、"help me think through this idea"、"I have a half-baked idea"、"formalize this into a project"、"walk me through framing a study"、"访谈我"、"帮我理清研究想法" 或 "把想法变成研究方案" 时使用。技能会多轮问答并把研究需求说明保存到磁盘。不用于文献综述（`/lit-review`），也不用于从零构想（`/research-ideation`）。
argument-hint: "[brief topic or 'start fresh'] [--no-verify]"
allowed-tools: ["Read", "Write", "Agent", "Task"]
---

# 研究访谈

本技能通过结构化访谈，帮助研究者把研究想法转化为具体研究需求说明。

**输入：** `$ARGUMENTS` 可以是一段简短的主题描述，也可以是 "start fresh"，表示开放式探索。

---

## 它如何运作

这是一项**对话式**技能，不会立刻生成报告。它每次问一两个问题，再根据回答追问，逐步形成结构化研究需求说明。

**不要用 AskUserQuestion。**直接在文字回复中提问，每次一两个，等用户回答后再继续。

---

## 访谈结构

### Phase 1: 全局图景（1-2 个问题）
- "你想理解的是什么现象或谜题？"
- "这件事为什么重要？谁应当关心答案？"
- 用户回答后，可以追问："你对这篇论文*属于哪一类*有想法吗：reduced-form / structural / theory+empirics / descriptive / formal-theory / survey-experiment / unsure？"类型定义见 `.codebuddy/agents/methods-referee.md`，领域默认频率见 `.codebuddy/references/discipline-cards.md`。把答案写入研究需求说明的 `**Paper type:**` 表头字段。"unsure" 也是有效答案，记为 `**Paper type:** unsure`。

### Phase 2: 理论动机（1-2 个问题）
- "对 X 为什么会发生 / 是什么驱动了 Y，你的直觉是什么？"
- "标准理论会预测什么？你预期会有不同吗？"

### Phase 3: 数据与情境（1-2 个问题）
- "你能拿到什么数据，或者理想情况下你想要什么数据？"
- "有没有特定的情境、时段或制度环境是你聚焦的？"

### Phase 4: 识别（1-2 个问题）
- "有没有自然实验、政策变化，或可利用的变异来源？"
- "对因果解释最大的威胁是什么？"

### Phase 5: 预期结果（1-2 个问题）
- "你预期发现什么？什么会让你意外？"
- "结果对政策或理论意味着什么？"

### Phase 6: 贡献（1 个问题）
- "这与已有工作有什么不同？你填的是什么空白？"

---

## 访谈之后

信息足够时，通常是 5-8 轮往复，生成一份**研究需求说明**：

```markdown
# Research Requirements: [Title]

**Date:** [YYYY-MM-DD]
**Researcher:** [from conversation context]
**Paper type:** [reduced-form | structural | theory+empirics | descriptive | formal-theory | survey-experiment | unsure]

## Research Question

[Clear, specific question in one sentence]

## Motivation

[2-3 paragraphs: why this matters, theoretical context, policy relevance]

## Hypothesis

[Testable prediction with expected direction]

## Empirical Strategy

- **Method:** [e.g., regression discontinuity around an eligibility cutoff]
- **Treatment:** [What varies]
- **Control:** [Comparison group]
- **Key identifying assumption:** [What must hold]
- **Robustness checks:** [Placebo tests, bandwidth sensitivity, etc.]

## Data

- **Primary dataset:** [Name, source, coverage]
- **Key variables:** [Treatment, outcome, controls]
- **Sample:** [Unit of observation, time period, N]

## Expected Results

[What the researcher expects to find and why]

## Contribution

[How this advances the literature — 2-3 sentences]

## Open Questions

[Issues raised during the interview that need further thought]
```

**保存到：** `quality_reports/specs/research_spec_[sanitized_topic].md`。`/grant-proposal`、`/data-management-plan`、`/power-analysis` 与 `/preregister` 都从这个目录读取研究需求说明。

---

## 落地后核验（Post-Flight，强制，CoVe —— 研究需求说明含可独立核验的事实断言时适用）

研究需求说明可能包含论文引文、数据集结构、命名实体、数值或否定性文献论断，这些都容易编造。只要研究需求说明含有任何可依据来源独立核验的事实断言，保存前就必须执行 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 的落地后核验协议；没有论文引文并不等于没有待核验断言。

### 步骤（仅研究需求说明不含任何可独立核验的事实断言时默认跳过）

1. **抽取断言：**检查整份研究需求说明，找出每条论文引文（"Smith 2019 shows X"）、每项数据集结构断言（"the CPS has field `educ_attain`"）、每项否定性文献断言（"nobody has studied Y"），以及其他可独立核验的数值事实和命名实体；不能只扫描动机／贡献中的引文。
2. **生成核验问题：**为每条断言写出具体、可回答的问题，例如 "Does Smith (2019, *JEL*) Section 3 report finding X? Is the venue correct?"
3. **生成 `claim-verifier`**：用 `Agent` 工具设置 `subagent_type=claim-verifier`，发起一次使用独立上下文的具名调用，不能使用会继承草稿的对话分叉。只提供断言 + 问题 + 来源指针，包括 DOI、arXiv 链接和访谈中用户提供的 `master_supporting_docs/` PDF，不要提供已起草的研究需求说明。
4. **对账：**PASS 时，把绿色块附到研究需求说明上；PARTIAL 时，给无法核验的断言标出不确定性；FAIL 时，先根据核验者提供的证据重写受影响段落，再保存研究需求说明。

### 跳过条件

- **默认跳过：**仅当整份研究需求说明不含任何可独立核验的事实断言。
- **单独例外：**用户显式使用 `--no-verify` 参数；即使研究需求说明含有事实断言，也可按该旗标跳过，但必须说明未经独立核验。

---

## 决策记录（权衡浮现时）

研究者在访谈中明确选择某个备选方案时，例如识别策略（DiD vs IV vs RDD）、数据来源（行政 vs 调查）、结果度量或样本范围，就为每个选择另写一份 ADR 风格的**决策记录**。使用 [`templates/decision-record.md`](../../../templates/decision-record.md)，保存到 `quality_reports/decisions/YYYY-MM-DD_[short-topic].md`。必填字段为 Status / Problem / Options considered / Decision + rationale / Consequences / Rejected alternatives。

如果访谈只形成一个无人反对的方向，就跳过 ADR。ADR 记录的是*存在实际备选方案的选择*，不是用来宣告默认路径。

---

## 访谈风格

- **好奇，不说教。**你的任务是引出研究者的思考，不是把自己的想法塞给对方。
- **温和地探查薄弱处。**识别策略看似脆弱时，问「怀疑论者会怎么说……？」，不要直接断言「这行不通，因为……？」。
- **顺着回答追问。**每个问题都应承接上一次回答。
- **知道何时停。**研究者在 4-5 轮后已有清晰构想，就转入研究需求说明，不要过度访谈。
