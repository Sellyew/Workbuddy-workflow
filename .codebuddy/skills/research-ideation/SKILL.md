---
name: research-ideation
description: 根据主题、现象或数据集描述，生成结构化研究问题、可检验假设、数据需求和中性方法分类。用户说 "give me research ideas on X"、"brainstorm questions about Y"、"what could I study with this data?"、"I'm looking for a paper idea on..."、"generate hypotheses for..."、"给我一些研究想法"、"围绕这个主题头脑风暴"、"这份数据能研究什么" 或 "生成研究假设" 时使用。具体识别策略、假设和威胁交由研究者或 owner 已签核材料。只生成一次，不进行多轮打磨；需要打磨想法时请用 `/interview-me`。
description_zh: 根据主题、现象或数据集描述，生成结构化研究问题、可检验假设、数据需求和中性方法分类。用户说 "give me research ideas on X"、"brainstorm questions about Y"、"what could I study with this data?"、"I'm looking for a paper idea on..."、"generate hypotheses for..."、"给我一些研究想法"、"围绕这个主题头脑风暴"、"这份数据能研究什么" 或 "生成研究假设" 时使用。具体识别策略、假设和威胁交由研究者或 owner 已签核材料。只生成一次，不进行多轮打磨；需要打磨想法时请用 `/interview-me`。
argument-hint: "[topic, phenomenon, or dataset description] [--no-verify]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "WebSearch", "WebFetch", "Agent", "Task"]
---

# 研究构想

根据主题、现象或数据集，生成结构化研究问题、可检验假设、数据需求和中性方法分类。

**输入：** `$ARGUMENTS`，可以是一个主题（例如 "minimum wage effects on employment"）、一个现象（例如 "why do firms cluster geographically?"）或一段数据集描述（例如 "panel of US counties with pollution and health outcomes, 2000-2020"）。

---

## 步骤

1. **理解输入。** 阅读 `$ARGUMENTS` 和所有被引用的文件，检查 `master_supporting_docs/` 中是否有相关论文，并查看 `.codebuddy/rules/` 中的领域约定。

2. **生成 3-5 个研究问题**，按从描述性到因果性的顺序排列：
   - **描述性：** 模式是什么？例如 "How has X evolved over time?"
   - **相关性：** 哪些因素与之相关？例如 "Is X correlated with Y after controlling for Z?"
   - **因果性：** 效应是什么？例如 "What is the causal effect of X on Y?"
   - **机制：** 效应为什么存在？例如 "Through what channel does X affect Y?"
   - **政策：** 含义是什么？例如 "Would policy X improve outcome Y?"

3. **给每个 RQ 标出一个可能的论文类型**，类型取自 `methods-referee.md`：
   - `reduced-form`（DiD、IV、RD、事件研究、合成控制）
   - `structural`（估计一个完整设定的模型）
   - `theory+empirics`（正式模型 + 对其预测的实证检验）
   - `descriptive`（测量、数据构建、模式记录）
   - `formal-theory`（纯理论，本文不做实证检验）
   - `survey-experiment`（vignette、conjoint、list-experiment）
   - `unsure`（多种类型都合理时，用户之后可用 `/interview-me` 选定）

   根据 `.codebuddy/references/discipline-cards.md` 按领域调整类型分布。econ 与 poli-sci 的默认频率不同，例如 poli-sci 比 econ 更倾向于 `survey-experiment` 和 `formal-theory`。**括号中的方法名只作中性分类，不得据此选择或推荐 DiD、IV、RDD、合成控制等具体策略。**

4. **展开每个研究问题：**
   - **假设：** 一个带预期符号或量级的可检验预测
   - **数据要求：** 需要什么数据，能否获得
   - **相关文献：** 2-3 篇与研究问题相关的论文

   具体识别策略、关键假设和识别威胁不在本技能输出中，唯一例外是转述 owner 已签核材料中的相应内容并标注签核出处；不得自行生成、补充、选择或辩护。

5. **按可行性和贡献给问题排序。**

6. **把输出保存到** `quality_reports/research_ideation_[sanitized_topic].md`。

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

**Data Requirements:**
- [Dataset 1 — what it provides]
- [Dataset 2 — what it provides]

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

返回构想报告前，运行 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 中的落地后核验协议。研究构想尤其容易在两方面产生幻觉：

1. **否定性文献断言**："no prior work studies X" 经常是错的。
2. **数据集结构断言**："The CPS contains field `educ_attain`" 可能在变量名、覆盖年份或访问限制上自信地出错。

### 步骤

1. **抽取断言**：从构想报告草稿中抽出每条否定性文献断言，以及每个被点名且附带字段或覆盖范围的数据集断言。方法名只作中性分类，不生成识别策略、所需假设或识别威胁断言。
2. **生成核验问题**：每条断言对应一组问题。例如 "Has Card & Krueger, Autor, or anyone in the last 10 years studied X? Search Google Scholar + NBER working papers." 或 "Does IPUMS-CPS include the `educ_attain` variable 1990–2024?"
3. **启动 `claim-verifier`**：使用 `Agent` 工具并设置 `subagent_type=claim-verifier`，在独立上下文中运行。必须是一次具名 `Agent` 调用，不能使用会继承草稿的对话分叉。交给它断言、问题和来源指针；允许 WebSearch，优先使用 NBER/SSRN 链接和数据集码本。**不要**包含草稿。
4. **对账**：PASS 时附上绿色块；PARTIAL 时标记不确定的 RQ；FAIL 时重写受影响的 RQ、假设或数据集描述。

### 跳过条件

- `--no-verify` 参数
- 用户明确说 "I'll verify the literature myself"

---

## 原则

- **有创造力但脚踏实地。** 可以超越显而易见的问题，但每条建议都必须具备数据可行性。
- **保持方法边界。** 方法名只作中性分类；具体识别策略、假设和威胁交由研究者或 owner 已签核材料，本技能不作选择或辩护。
- **考虑数据可得性。** 没有可用数据，再漂亮的问题也无法执行。
- **尽量点名具体数据集**，例如 FRED、Census、PSID、行政数据。
