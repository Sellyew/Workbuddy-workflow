---
name: scaffold-exercises
description: 搭一份分级习题集，含分节、题目、详解，以及针对分析题、实证题、编程题三类题型的简短「为什么重要」说明。用户说 "make a problem set on X"、"scaffold exercises for this lecture"、"create practice problems"、"generate homework with a solution key"、"build a graded assignment on topic Y" 时使用。输出一份干净的给学生版加一份单独的解答册 —— 不用于给提交的作业评分，也不用于自动批改学生答案。
description_zh: 搭一份分级习题集，含分节、题目、详解，以及针对分析题、实证题、编程题三类题型的简短「为什么重要」说明。用户说 "make a problem set on X"、"scaffold exercises for this lecture"、"create practice problems"、"generate homework with a solution key"、"build a graded assignment on topic Y" 时使用。输出一份干净的给学生版加一份单独的解答册 —— 不用于给提交的作业评分，也不用于自动批改学生答案。
argument-hint: "[topic] [--difficulty intro|core|advanced] [--count N] [--types analytical,empirical,coding] [--dataset path] [--no-solutions]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]

---

# `/scaffold-exercises` —— 习题集脚手架

将分级习题集写成两个文件：只含题目的**学生版**，以及包含详解和每题一行说明的**解答册**。本技能借鉴 `mattpocock/skills` 的模式，面向经济学教学，重点生成分级课程作业，题型可混合推导、估计与代码。

**输入：** `$ARGUMENTS` —— 一个主题（例如 "instrumental variables"、"consumer theory"、"quantile regression"）加可选参数。见[参数](#参数)。

---

## 何时使用

- 你已有一讲或一份阅读材料，需要配套且带答案的作业。
- 你需要混合题型（推导、估计、写代码）和可控难度，并希望**单独**输出解答，避免学生版混入答案。

**不要**用本技能给提交的作业评分、自动批改答案或编制、生成或组织限时考试。它只生成*练习/分级*材料，不提供评估基础设施。

---

## 题型

| 题型 | 学生做什么 | 解答产物 |
| --- | --- | --- |
| **analytical** | 推导 / 证明 / 刻画（理论：优化、识别、比较静态） | 逐步推导，点名关键引理 |
| **empirical** | 在提供或模拟的数据集上估计 + 解释 | 预期估计值、符号/量级推理、常见错误提示 |
| **coding** | 用 R 或 Stata 实现一个估计量或模拟 | 可运行的参考代码片段 + 预期输出形状 |

实证题若没有提供数据集，就用固定种子（YYYYMMDD）生成一个小型**模拟**数据集，确保解答册结果确定且可复现。

---

## 工作流

### Phase 0: 设定主题、难度、题数、题型（起飞前检查）

先读取用户指定的素材（讲义 `.tex`/`.qmd`、论文、数据集头部），再在生成题目**之前**输出起飞前报告：

```markdown
## Pre-Flight Report — Problem Set

**Topic:** [topic]
**Source(s) read:** [lecture/paper/dataset — one-line takeaway each]
**Difficulty:** intro | core | advanced
**Counts by type:** analytical=N, empirical=N, coding=N  (total = `--count`)
**Dataset:** [provided path | simulated with seed YYYYMMDD | none]
**Learning objectives:** [2-4 bullets the set should exercise]
```

在这一阶段确定所有参数，交互式选择也应在生成前完成，不要中途再询问。如果主题模糊到无法写出学习目标，只问一个澄清问题并停下；否则继续。

### Phase 1: 生成题目

每道题都要有编号、分节标题、题干，以及所需的数据和记号，并遵守以下约定：

- **先动机后机械** —— 用一句话说明这道题为什么值得做，与 `create-lecture` 的教学法一致。
- **记号复用** —— 与源讲义保持符号一致，不要为已定义对象引入冲突符号。
- **难度校准** —— *intro* 检验一个概念；*core* 串联 2-3 步；*advanced* 要求一个不显然的洞见或识别论证。
- **自足** —— 每道题自行说明假设，不要使用「如第 4 讲所述」这类缺少上下文的引用。

### Phase 2: 生成详解 + 说明

每道题都要写：

1. **详解**：根据题型给出完整推导、预期估计值或可运行代码。编程题答案必须确实能运行；如果 `Bash` + R/Stata 可用，就执行代码并粘贴真实输出。
2. **「为什么重要」说明**：用 1-2 句话把答案与更广的概念联系起来。每题都要有简短理由，不能只给数字答案。

### Phase 3: 写学生版 + 解答册

输出两个文件。路径可以配置，默认放在 `quality_reports/teaching/`，与 `/respond-to-eval` 的教学计划并列。不要新建 `exercises/` 这类顶层目录；除非把它加入 `scripts/check-repo-hygiene.py` 的 `ROOT_ALLOW_DIRS`，否则提交会失败。

- `quality_reports/teaching/<topic-slug>_problems.md` —— **学生版**：分节、题目、任何数据，没有答案。
- `quality_reports/teaching/<topic-slug>_solutions.md` —— **解答册**：重述每道题，并给出详解和说明。

必须严格分开两个文件，绝不能把解答泄漏到学生版。使用 `--no-solutions` 时，只写学生版，然后停止。

---

## 输出 / 报告格式

学生版：

```markdown
# Problem Set: [Topic]  (Difficulty: core)

## Section 1 — Analytical
**1.** [Motivation sentence.] [Prompt.]

## Section 2 — Empirical
**2.** Using `data/<file>` (vars: ...), [estimate + interpret prompt].

## Section 3 — Coding (R)
**3.** [Implement-X prompt.]
```

解答册沿用相同编号，每题增加 `### Solution` 与 `> Why this matters:` 块。聊天回复最后用一行清单说明写入了哪些文件、各题型有多少题，以及代码答案是实际执行过还是仅完成起草。

---

## 退出行为

- 打印两个输出路径（绝对路径）、各题型计数；如果使用模拟数据集，还要打印种子。
- 如果某道编程题答案因缺少 R/Stata 或运行报错而无法执行，标记为 **DRAFTED — NOT RUN**，不得暗示它已经核验。
- 如果实证题引用了所提供数据集中不存在的变量，停下并指出不匹配，不能编造列。

---

## 参数

- `--difficulty` —— `intro` | `core` | `advanced`（默认 `core`）；按 Phase 1 所述调整解题步数与深度。
- `--count` —— 题目总数（默认 6）；按起飞前报告中的计数分配到各题型。
- `--types` —— `analytical,empirical,coding` 的逗号分隔子集（默认三者全要）。
- `--dataset` —— 实证题所用真实数据集的路径；省略则用带种子的 DGP 模拟一个。
- `--no-solutions` —— 只写学生版；跳过解答册（Phase 2/3 的解答文件）。

---

## 交叉引用

- [`.codebuddy/skills/create-lecture/SKILL.md`](../create-lecture/SKILL.md) —— 创建这些练习所配套的讲次；共享记号复用 + 动机先行两条约定。
- [`.codebuddy/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md) —— 参考解答需要完整 R 估计流水线时，用于实证题。
- [`.codebuddy/skills/simulation-study/SKILL.md`](../simulation-study/SKILL.md) —— 题目需要演示估计量的有限样本行为时，复用其带种子 DGP 的规范。
- [`.codebuddy/skills/lit-review/SKILL.md`](../lit-review/SKILL.md) —— 从该主题的近期论文中取材，设计进阶题。
- [`.codebuddy/skills/interview-me/SKILL.md`](../interview-me/SKILL.md) —— 先把模糊的「我想要一份关于……的习题集」转化为具体学习目标。
- [`templates/skill-template.md`](../../../templates/skill-template.md) —— 撰写/扩展本技能的内部风格规范。

---

## 本技能不做什么

- **不评分**：不给学生提交的作业评分，也不用答案自动批改。
- **不组织限时考试**，也不执行评估政策（分值权重、评分细则、监考）。
- **不发明数据**：实证题只使用提供的数据集或明确播种的模拟，绝不使用编造的数字。
- **不泄漏解答**到学生版，也不部署或发布任何内容（不调用 `/deploy`）。
- **不自动调用**其他技能：可以引用同级技能，但不会主动调用它们。
