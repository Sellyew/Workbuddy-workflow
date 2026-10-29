---
name: research-ideation
description: 从一个主题、现象或数据集描述出发，生成结构化的研究问题、可检验的假设与候选实证策略。用户说 "give me research ideas on X"、"brainstorm questions about Y"、"what could I study with this data?"、"I'm looking for a paper idea on..."、"generate hypotheses for..." 时使用。一次性生成，不是多轮。要做想法打磨请用 `/interview-me`。
description_zh: 从一个主题、现象或数据集描述出发，生成结构化的研究问题、可检验的假设与候选实证策略。用户说 "give me research ideas on X"、"brainstorm questions about Y"、"what could I study with this data?"、"I'm looking for a paper idea on..."、"generate hypotheses for..." 时使用。一次性生成，不是多轮。要做想法打磨请用 `/interview-me`。
argument-hint: "[topic, phenomenon, or dataset description] [--no-verify]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "WebSearch", "WebFetch", "Agent", "Task"]
---

# 研究构想

从一个主题、现象或数据集出发，生成结构化的研究问题、可检验的假设与实证策略。

**输入：** `$ARGUMENTS` —— 一个主题（例如 "minimum wage effects on employment"）、一个现象（例如 "why do firms cluster geographically?"），或一段数据集描述（例如 "panel of US counties with pollution and health outcomes, 2000-2020"）。

---

## 步骤

1. **理解输入。** 读 `$ARGUMENTS` 与任何被引用的文件。检查 `master_supporting_docs/` 里有没有相关论文。检查 `.codebuddy/rules/` 里的领域约定。

2. **生成 3-5 个研究问题**，按从描述性到因果性排序：
   - **描述性：** 模式是什么？（例如 "How has X evolved over time?"）
   - **相关性：** 哪些因素与之相关？（例如 "Is X correlated with Y after controlling for Z?"）
   - **因果性：** 效应是什么？（例如 "What is the causal effect of X on Y?"）
   - **机制：** 效应为什么存在？（例如 "Through what channel does X affect Y?"）
   - **政策：** 含义是什么？（例如 "Would policy X improve outcome Y?"）

3. **给每个 RQ 标上一个可能的论文类型**（取自 `methods-referee.md`）：
   - `reduced-form`（DiD、IV、RD、事件研究、合成控制）
   - `structural`（估计一个完整设定的模型）
   - `theory+empirics`（正式模型 + 对其预测的实证检验）
   - `descriptive`（测量、数据构建、模式记录）
   - `formal-theory`（纯理论，本文不做实证检验）
   - `survey-experiment`（vignette、conjoint、list-experiment）
   - `unsure`（多种类型都说得通时 —— 用户之后可用 `/interview-me` 选定）

   用 `.codebuddy/references/discipline-cards.md` 按领域偏置这个分布（econ 与 poli-sci 的默认频率不同 —— 例如 poli-sci 比 econ 更偏向 `survey-experiment` 与 `formal-theory`）。

4. **为每个研究问题展开：**
   - **假设：** 一个可检验的预测，带预期符号/量级
   - **识别策略：** 如何确立因果（DiD、IV、RDD、合成控制等）
   - **数据要求：** 需要什么数据？拿得到吗？
   - **关键假设：** 策略要成立，必须满足什么？
   - **潜在陷阱：** 对识别的常见威胁
   - **相关文献：** 2-3 篇使用相似方法的论文

5. **给问题排序**，按可行性与贡献。

6. **保存输出**到 `quality_reports/research_ideation_[sanitized_topic].md`

---

## 输出格式

```markdown
# Research Ideation: [Topic]

**Date:** [YYYY-MM-DD]
**Input:** [Original input]

## Overview

[1-2 paragraphs situating the topic and why it matters]

## Research Questions

### RQ1: [Question] (Feasibility: High/Medium/Low)

**Type:** Descriptive / Correlational / Causal / Mechanism / Policy
**Paper type:** reduced-form / structural / theory+empirics / descriptive / formal-theory / survey-experiment / unsure

**Hypothesis:** [Testable prediction]

**Identification Strategy:**
- **Method:** [the identification approach you would defend in a seminar]
- **Treatment:** [What varies and when]
- **Control group:** [Comparison units]
- **Key assumption:** [the assumption the method's validity rests on, stated so it can be attacked]

**Data Requirements:**
- [Dataset 1 — what it provides]
- [Dataset 2 — what it provides]

**Potential Pitfalls:**
1. [Threat 1 and possible mitigation]
2. [Threat 2 and possible mitigation]

**Related Work:** [Author (Year)], [Author (Year)]

---

[Repeat for RQ2-RQ5]

## Ranking

| RQ | Feasibility | Contribution | Priority |
|----|-------------|-------------|----------|
| 1  | High        | Medium      | ...      |
| 2  | Medium      | High        | ...      |

## Suggested Next Steps

1. [Most promising direction and immediate action]
2. [Data to obtain]
3. [Literature to review deeper]
```

---

## 落地后核验（Post-Flight，强制，CoVe）

在交回构想报告之前，跑 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 里的落地后核验协议。研究构想在三个特定方面容易产生幻觉：

1. **否定性文献断言** —— "no prior work studies X" 经常是错的。
2. **数据集结构断言** —— "The CPS contains field `educ_attain`" 可能在变量名、覆盖年份或受限访问状态上自信地出错。
3. **估计量可行性断言** —— "this works with panel fixed effects" 可能把一条识别假设说错。

### 步骤

1. **抽取断言**：从构想报告草稿中抽出每一条否定性文献断言、每一个被点名且附带字段的数据集、每一个声称的识别策略 + 所需的数据结构。
2. **生成核验问题**，每条断言一组。例如："Has Card & Krueger, Autor, or anyone in the last 10 years studied X? Search Google Scholar + NBER working papers." / "Does IPUMS-CPS include the `educ_attain` variable 1990–2024?"
3. **生成 `claim-verifier`**：用 `Agent` 工具，`subagent_type=claim-verifier`，在独立上下文中 —— 一次具名的 `Agent` 调用，不是对话分叉（分叉会继承草稿）。交给它断言 + 问题 + 来源指针（允许 WebSearch，优先 NBER/SSRN 链接，优先数据集码本）。**不要**包含草稿。
4. **对账：** PASS → 附上绿色块；PARTIAL → 给不确定的 RQ 打标记；FAIL → 重写受影响的 RQ/假设/策略。

### 跳过条件

- `--no-verify` 参数
- 用户明确说 "I'll verify the literature myself"

---

## 原则

- **有创造力但脚踏实地。** 要越过显而易见的问题，但每条建议都必须在实证上可行。
- **像审稿人一样思考。** 对每个因果问题，立刻指出识别上的挑战。
- **考虑数据可得性。** 一个漂亮的问题如果没有可用数据，就不可执行。
- **尽量点名具体数据集**（FRED、Census、PSID、行政数据等）。
