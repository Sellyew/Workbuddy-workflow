---
name: scaffold-exercises
description: 搭一份分级习题集，含分节、题目、详解，以及针对分析题、实证题、编程题三类题型的简短「为什么重要」说明。用户说 "make a problem set on X"、"scaffold exercises for this lecture"、"create practice problems"、"generate homework with a solution key"、"build a graded assignment on topic Y" 时使用。输出一份干净的给学生版加一份单独的解答册 —— 不用于给提交的作业评分，也不用于自动批改学生答案。
description_zh: 搭一份分级习题集，含分节、题目、详解，以及针对分析题、实证题、编程题三类题型的简短「为什么重要」说明。用户说 "make a problem set on X"、"scaffold exercises for this lecture"、"create practice problems"、"generate homework with a solution key"、"build a graded assignment on topic Y" 时使用。输出一份干净的给学生版加一份单独的解答册 —— 不用于给提交的作业评分，也不用于自动批改学生答案。
argument-hint: "[topic] [--difficulty intro|core|advanced] [--count N] [--types analytical,empirical,coding] [--dataset path] [--no-solutions]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]

---

# `/scaffold-exercises` —— 习题集脚手架

把一份分级习题集生成为两个文件：一份干净的**学生版**（只有题目）和一份**解答册**（详解 + 每题一行说明）。模式取自 `mattpocock/skills`，改造为经济学教学用途 —— 主视角是混合了推导、估计与代码的分级课程作业。

**输入：** `$ARGUMENTS` —— 一个主题（例如 "instrumental variables"、"consumer theory"、"quantile regression"）加可选参数。见[参数](#参数)。

---

## 何时使用

- 你有一讲或一份阅读材料，想要一份配套的、带答案的作业。
- 你想要混合题型（推导、估计、写代码），难度可控，且解答**单独**输出，让学生版文件保持干净。

**不要**用它给提交的作业评分、自动批改答案，或搭一份限时考试 —— 它脚手架的是*练习/分级*材料，不是评估基础设施。

---

## 题型

| 题型 | 学生做什么 | 解答产物 |
| --- | --- | --- |
| **analytical** | 推导 / 证明 / 刻画（理论：优化、识别、比较静态） | 逐步推导，点名关键引理 |
| **empirical** | 在提供或模拟的数据集上估计 + 解释 | 预期估计值、符号/量级推理、常见错误提示 |
| **coding** | 用 R 或 Stata 实现一个估计量或模拟 | 可运行的参考代码片段 + 预期输出形状 |

若实证题没有提供数据集，就生成一个小的**模拟**数据集，用固定种子（YYYYMMDD），让解答册是确定的、可复现的。

---

## 工作流

### Phase 0: 设定主题、难度、题数、题型（起飞前检查）

读用户指出的任何素材（讲义 `.tex`/`.qmd`、一篇论文、一个数据集头部），并在生成题目**之前**产出一份起飞前报告：

```markdown
## Pre-Flight Report — Problem Set

**Topic:** [topic]
**Source(s) read:** [lecture/paper/dataset — one-line takeaway each]
**Difficulty:** intro | core | advanced
**Counts by type:** analytical=N, empirical=N, coding=N  (total = `--count`)
**Dataset:** [provided path | simulated with seed YYYYMMDD | none]
**Learning objectives:** [2-4 bullets the set should exercise]
```

在这里把每个参数都定下来（交互式选择在生成之前收集，而不是跑到一半再问）。若主题太模糊、写不出目标，问一个澄清问题就停。否则继续。

### Phase 1: 生成题目

为每道题写出编号、分节标题、题干，以及它需要的任何数据/记号。约定：

- **先动机后机械** —— 用一句话说明这道题为什么值得做，与 `create-lecture` 的教学法一致。
- **记号复用** —— 符号对齐源讲义；对已定义的对象绝不引入冲突符号。
- **难度校准** —— *intro* 检验一个概念；*core* 串联 2-3 步；*advanced* 要求一个不显然的洞见或识别论证。
- **自足** —— 每道题自陈其假设；不要「如第 4 讲所述」这类悬空引用。

### Phase 2: 生成详解 + 说明

对每道题写：

1. 一份**详解** —— 完整推导、预期估计值，或可运行的代码（取决于题型）。编程题的解答必须真的能跑；若 `Bash` + R/Stata 可用，就执行那段代码并把真实输出粘进来。
2. 一段**「为什么重要」说明** —— 1-2 句话把答案与更广的概念连起来（这是引入的模式的特征：每道题都附一段简短理由，而不只是一个数字）。

### Phase 3: 写学生版 + 解答册

输出两个文件（路径可配置；默认放在 `quality_reports/teaching/` 下，与 `/respond-to-eval` 的教学计划并列。像 `exercises/` 这样的新顶层目录一旦提交就会让 `scripts/check-repo-hygiene.py` 失败，除非它被加进该脚本的 `ROOT_ALLOW_DIRS`）：

- `quality_reports/teaching/<topic-slug>_problems.md` —— **学生版**：分节、题目、任何数据，没有答案。
- `quality_reports/teaching/<topic-slug>_solutions.md` —— **解答册**：每题重述、其详解、其说明。

这个切分是承重的：绝不把解答泄漏进学生版文件。带 `--no-solutions` 时，只写学生版就停。

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

解答册镜像同样的编号，每题加 `### Solution` 与 `> Why this matters:` 块。用一行清单结束你的聊天回复：写了哪些文件、按题型的题目数，以及代码解答是被执行了还是只起草了。

---

## 退出行为

- 打印两个输出路径（绝对路径）、分题型的计数，以及数据集是模拟时的种子。
- 若某道编程题的解答无法执行（没有 R/Stata，或运行报错），标它为 **DRAFTED — NOT RUN**，而不是暗示它已被核验。
- 若某道实证题引用了所提供数据集里不存在的变量，停下并指出这处不匹配，而不是凭空发明列。

---

## 参数

- `--difficulty` —— `intro` | `core` | `advanced`（默认 `core`）；按 Phase 1 所述校准步深。
- `--count` —— 题目总数（默认 6）；按起飞前报告的计数分配到各题型。
- `--types` —— `analytical,empirical,coding` 的逗号分隔子集（默认三者全要）。
- `--dataset` —— 实证题所用真实数据集的路径；省略则用带种子的 DGP 模拟一个。
- `--no-solutions` —— 只写学生版；跳过解答册（Phase 2/3 的解答文件）。

---

## 交叉引用

- [`.codebuddy/skills/create-lecture/SKILL.md`](../create-lecture/SKILL.md) —— 搭出这些练习所要练的那一讲；共享记号复用 + 动机先行两条约定。
- [`.codebuddy/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md) —— 适用于参考解答需要完整 R 估计流水线的实证题。
- [`.codebuddy/skills/simulation-study/SKILL.md`](../simulation-study/SKILL.md) —— 当某道题要演示估计量的有限样本行为时；复用其带种子 DGP 的纪律。
- [`.codebuddy/skills/lit-review/SKILL.md`](../lit-review/SKILL.md) —— 从该主题的近期论文里取材出进阶题。
- [`.codebuddy/skills/interview-me/SKILL.md`](../interview-me/SKILL.md) —— 先把一个模糊的「我想要一份关于……的习题集」变成具体的学习目标。
- [`templates/skill-template.md`](../../../templates/skill-template.md) —— 撰写/扩展本技能的内部风格规范。

---

## 本技能不做什么

- **不评分**：不给学生提交的作业评分，也不拿答案自动批改。
- **不组织限时考试**，也不执行评估政策（分值权重、评分细则、监考）。
- **不发明数据** —— 实证题使用提供的数据集或明确播种的模拟，绝不用编造的数字。
- **不泄漏解答**进学生版文件，也不部署/发布任何东西（不调 `/deploy`）。
- **不自动调用**其他技能 —— 它引用同级技能，但不调用它们。
