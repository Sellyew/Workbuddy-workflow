---
name: interview-me
description: 互动式访谈，把模糊的研究想法固化成结构化规格（研究问题、假设、识别、数据需求、实证策略）。用户说 "interview me"、"help me think through this idea"、"I have a half-baked idea"、"formalize this into a project"、"walk me through framing a study" 时使用。多轮问答；规格落盘保存。不用于文献综述（`/lit-review`），也不用于从零构想（`/research-ideation`）。
description_zh: 互动式访谈，把模糊的研究想法固化成结构化规格（研究问题、假设、识别、数据需求、实证策略）。用户说 "interview me"、"help me think through this idea"、"I have a half-baked idea"、"formalize this into a project"、"walk me through framing a study" 时使用。多轮问答；规格落盘保存。不用于文献综述（`/lit-review`），也不用于从零构想（`/research-ideation`）。
argument-hint: "[brief topic or 'start fresh'] [--no-verify]"
allowed-tools: ["Read", "Write", "Agent", "Task"]
---

# 研究访谈

主持一场结构化访谈，帮研究者把一个研究想法固化成具体规格。

**输入：** `$ARGUMENTS` —— 一段简短的主题描述，或 "start fresh" 表示开放式探索。

---

## 它如何运作

这是一个**对话式**技能。它不立刻产出报告，而是通过一次问一两个问题、根据回答往深处追问，逐步搭出一份结构化研究规格。

**不要用 AskUserQuestion。** 直接在文字回复里提问，一次一两个。等用户回答之后再继续。

---

## 访谈结构

### Phase 1: 全局图景（1-2 个问题）
- "你想理解的是什么现象或谜题？"
- "这件事为什么重要？谁应当关心答案？"
- 用户回答之后，可再问："你对这篇论文*属于哪一类*有想法吗 —— reduced-form / structural / theory+empirics / descriptive / formal-theory / survey-experiment / unsure？"（类型定义见 `.codebuddy/agents/methods-referee.md`，领域默认频率见 `.codebuddy/references/discipline-cards.md`。）把答案记进保存的规格里 `**Paper type:**` 表头字段；"unsure" 完全可以，记为 `**Paper type:** unsure`。

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

一旦信息足够（通常是 5-8 轮往复），产出一份**研究规格文档**：

```markdown
# Research Specification: [Title]

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

**保存到：** `quality_reports/specs/research_spec_[sanitized_topic].md` —— `/grant-proposal`、`/data-management-plan`、`/power-analysis` 与 `/preregister` 读取的那个目录。

---

## 落地后核验（Post-Flight，强制，CoVe —— 规格引用既有工作时适用）

研究规格的**动机**与**贡献**两节通常会按作者 + 年份引用既有论文。这些引文容易产生幻觉。保存规格之前，若规格含任何引文，就跑 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 里的落地后核验协议。

### 步骤（规格零引文时跳过）

1. **抽取断言：** 动机 / 贡献一节里的每一条论文引文（"Smith 2019 shows X"）、任何数据集结构断言（"the CPS has field `educ_attain`"）、任何否定性文献断言（"nobody has studied Y"）。
2. **生成核验问题：** 每条断言一组具体、可回答的问题。"Does Smith (2019, *JEL*) Section 3 report finding X? Is the venue correct?"
3. **生成 `claim-verifier`**：用 `Agent` 工具，`subagent_type=claim-verifier`，在独立上下文中 —— 一次具名的 `Agent` 调用，不是对话分叉（分叉会继承草稿）。交给它断言 + 问题 + 来源指针（DOI、arXiv 链接，以及访谈中用户提供的 `master_supporting_docs/` PDF）。不要包含已起草的规格。
4. **对账：** PASS → 把绿色块附到规格上。PARTIAL → 给无法核验的引文打上不确定标记。FAIL → 在保存规格之前，用核验者给的证据重写受影响的段落。

### 跳过条件

- 规格零论文引文（纯方法学规格，没有文献引用）。
- `--no-verify` 参数。
- 用户在访谈中明确说过 "I'll verify the literature myself."

---

## 决策记录（权衡浮现时）

若访谈中研究者明确在备选方案间做了选择 —— 识别策略（DiD vs IV vs RDD）、数据来源（行政 vs 调查）、结果度量、样本范围等 —— 就为每个选择再写一份 ADR 风格的**决策记录**。用 [`templates/decision-record.md`](../../../templates/decision-record.md)，存到 `quality_reports/decisions/YYYY-MM-DD_[short-topic].md`。必填字段：Status / Problem / Options considered / Decision + rationale / Consequences / Rejected alternatives。

若访谈只产出一个无人反对的方向，就跳过 ADR —— ADR 用于*有活备选方案的决策*，不用于宣告默认路径。

---

## 访谈风格

- **好奇，不说教。** 你的活是把研究者的思考引出来，不是把自己的想法塞进去。
- **温和地探薄弱处。** 若识别策略听起来脆弱，问「怀疑论者会怎么说……？」，而不是「这行不通，因为……？」。
- **顺着回答搭。** 每个问题都应当从上一次回答里长出来。
- **知道何时停。** 若研究者在 4-5 轮之后已有清晰构想，就进入规格。不要过度访谈。
