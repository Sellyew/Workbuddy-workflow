---
paths:
  - "scripts/**/*.R"
  - "scripts/**/*.do"
  - "scripts/**/*.py"
---

# 推断与稳健性（多重检验 + 研究者自由度）

关于推断选择的建议性标准，这些选择决定一个结果能否在尖刻的审稿人手下存活——汇总在此，免得它们只以一句反对意见的形式留存。适用于实证分析脚本；稿件侧的检查在 [`/review-paper`](../skills/review-paper/SKILL.md)（维度 3），设计侧的承诺在 [`/preregister`](../skills/preregister/SKILL.md)。

## 多重假设检验

当一篇论文检验**多个假设**（多个结果变量、子样本、处理臂或设定）时，未校正的 p 值会夸大显著性。**按你控制的是什么来决定校正方法，并预注册这个族**：

- **族错误率（FWER）**——控制*任何*一次错误拒绝的概率。当哪怕一个假阳性代价都很高时（一个主结论）使用。
  - **Romano–Wolf** 逐步下降法（重抽样，利用跨方程的相关性——远不如 Bonferroni 保守；Stata `rwolf`/`rwolf2`，R `wildrwolf`）是小族里的现代默认做法。
  - Holm–Bonferroni 作为免分布假设的退路；朴素 Bonferroni 只用于极小的族。
- **错误发现率（FDR）**——控制被拒绝者中错误拒绝的*期望比例*。用于**大量**假设、且允许一些假阳性的场合（筛选、异质性扫描）。
  - Benjamini–Hochberg；**Anderson (2008) 的两阶段锐化 q 值**是应用微观的标准做法（Stata `qvalue`/`sharpenedq`）。
- **预注册族与校正方法**（校正的单位就是一个研究者自由度）。未校正与校正后的结果都要报；绝不要挑那个让结果活下来的族。

## 研究者自由度 / 设定稳健性

单一设定只是分叉小径花园里的一个点。把稳健性摆到明面上：

- **证明设定不是挑出来的**——画设定/多重宇宙曲线（扫遍站得住脚的控制变量集、样本限制、函数形式；报估计值的分布，而不是一个估计值）。
- **逐一剔除 / 强影响观测**——确认结果不是被少数几个单位或一个聚类驱动的。
- **推断稳健性**——更换聚类层级、聚类数少时用 wild-cluster bootstrap（`fwildclusterboot`/`boottest`）、设计支持时用随机化推断。

## 报告

- 开头就说明**族**和**校正方法**；未校正*和*校正后的 p 值/q 值都要报。
- 只会确认主结论的稳健性检验是演戏——报出结果*变弱*的那个设定，并解释它。

## 交叉引用
- [`.codebuddy/skills/review-paper/SKILL.md`](../skills/review-paper/SKILL.md) · [`.codebuddy/skills/preregister/SKILL.md`](../skills/preregister/SKILL.md) · [`.codebuddy/skills/power-analysis/SKILL.md`](../skills/power-analysis/SKILL.md)。
