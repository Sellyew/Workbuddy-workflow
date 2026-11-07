---
paths:
  - "scripts/**/*.R"
  - "scripts/**/*.do"
  - "scripts/**/*.py"
---

# 推断与稳健性（多重检验 + 研究者自由度）

推断选择会影响结果能否经受严格审稿。本规则汇总相关的建议性标准，避免它们只留在零散的反对意见中。规则适用于实证分析脚本；稿件侧检查见 [`/review-paper`](../skills/review-paper/SKILL.md)（维度 3），设计侧承诺见 [`/preregister`](../skills/preregister/SKILL.md)。

## 多重假设检验

一篇论文检验**多个假设**时，例如使用多个结果变量、子样本、处理臂或设定，未校正的 p 值会夸大显著性。**先明确要控制哪一类错误，再选择校正方法，并预注册检验族**：

- **族错误率（FWER）**：控制出现*任何*一次错误拒绝的概率。即使只有一个假阳性，代价也很高时，例如涉及一个主结论，就使用这种方法。
  - **Romano–Wolf** 逐步下降法通过重抽样利用跨方程的相关性，远不如 Bonferroni 保守，是小族里的现代默认做法；Stata 用 `rwolf`/`rwolf2`，R 用 `wildrwolf`。
  - Holm–Bonferroni 可作为不依赖分布假设的备选方法；朴素 Bonferroni 只用于极小的族。
- **错误发现率（FDR）**：控制所有拒绝中错误拒绝所占的*期望比例*。面对**大量**假设且允许一些假阳性时，例如筛选或异质性扫描，使用这种方法。
  - 可使用 Benjamini–Hochberg；**Anderson (2008) 的两阶段锐化 q 值**是应用微观的标准做法，Stata 用 `qvalue`/`sharpenedq`。
- **预注册检验族与校正方法**，因为校正单位本身也是一种研究者自由度。未校正和校正后的结果都要报告，绝不能选择让结果得以成立的检验族。

## 研究者自由度 / 设定稳健性

单一设定只是分叉小径花园中的一个点。应把稳健性检查公开呈现出来：

- **证明设定不是挑出来的**：画设定/多重宇宙曲线，扫遍站得住脚的控制变量集、样本限制和函数形式，报告估计值的分布，而不是只报一个估计值。
- **逐一剔除 / 强影响观测**：确认结果并非由少数几个单位或一个聚类驱动。
- **推断稳健性**：更换聚类层级；聚类数少时使用 wild-cluster bootstrap（`fwildclusterboot`/`boottest`）；设计支持时使用随机化推断。

## 报告

- 开头就说明**检验族**和**校正方法**，同时报告未校正*和*校正后的 p 值/q 值。
- 只报告确认主结论的稳健性检验是在演戏。结果*变弱*的设定也要报告，并作出解释。

## 交叉引用
- [`.codebuddy/skills/review-paper/SKILL.md`](../skills/review-paper/SKILL.md) · [`.codebuddy/skills/preregister/SKILL.md`](../skills/preregister/SKILL.md) · [`.codebuddy/skills/power-analysis/SKILL.md`](../skills/power-analysis/SKILL.md)。
