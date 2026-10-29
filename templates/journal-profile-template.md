# 期刊画像模板

把下面这一块复制进 `.codebuddy/references/journal-profiles.md`（放在相应的地区/领域小节下），并填满每个字段。6 种审稿取向的权重必须加起来等于 1.0。

```markdown
### Journal Full Name (SHORT)

**Short name:** `SHORT`

**Focus.** [1-2 sentences: what this journal publishes and what it does NOT publish.]

**Bar.** [1-2 sentences: what it takes to clear the desk. Mention acceptance rate if known.]

**Domain-referee adjustments.**
- Contribution 30 → [new] ([reason])
- Lit positioning 25 → [new] ([reason])
- Substance 20 → [new] ([reason])
- External validity 15 → [new] ([reason])
- Fit 10 → [new] ([reason])

**Methods-referee adjustments.**
- [Dimension] [default] → [new] ([reason, e.g., "identification bar is higher at this journal"])
- [Paper-type-specific: e.g., "If paper type is `structural`: Parameter ID 30 → 35"]

**Typical concerns.** (3-5 direct-quote questions this journal's referees ask)
- "[Quote]"
- "[Quote]"
- "[Quote]"

**Referee-pool weights.** (must sum to 1.0)
- STRUCTURAL: 0.__
- CREDIBILITY: 0.__
- MEASUREMENT: 0.__
- POLICY: 0.__
- THEORY: 0.__
- SKEPTIC: 0.__

**Table format override.** [Optional: any journal-specific formatting rule. E.g., "No significance stars (APA 7th edition)" or "Three-decimal point estimates". Leave "None specific" if no override.]

---
```

## 审稿取向参考

`--peer` 流水线里用到的 6 种审稿取向：

| 审稿取向 | 口头禅 |
|---|---|
| STRUCTURAL | 「机制在哪？模型在哪？」 |
| CREDIBILITY | 「给我看研究设计。实验是什么？」 |
| MEASUREMENT | 「这是怎么度量的？样本流失 / 构念效度呢？」 |
| POLICY | 「这在你样本之外成立吗？那又如何？」 |
| THEORY | 「理论预测了什么？」 |
| SKEPTIC | 「什么能让这个结论消失？」 |

这些取向刻意做到跨领域通用。对非经济学领域，它们仍然适用——调整权重，别改标签。

## 领域特有的论文类型

`methods-referee` 代理按论文类型分支。默认类型（以经济学为中心）是：

- `reduced-form`——DiD、IV、RD、事件研究等。
- `structural`——结构估计、DSGE、一般均衡校准等。
- `theory+empirics`——理论模型，配对其预测的实证检验。
- `descriptive`——度量、数据构建、模式记录。
- `formal-theory`——博弈论 / 公理化模型，无实证（v1.8.0）。
- `survey-experiment`——带随机化操纵的调查或框定实验（v1.8.0）。

对非经济学领域，把你自己领域的类型加进 `.codebuddy/agents/methods-referee.md`：复制那份评分细则块，改各维度权重。例子：

- **生物学：** `observational / experimental / computational / review`。
- **政治学：** `case-study / comparative`（注意：`formal-theory` 与 `survey-experiment` 已自带，v1.8.0）。
- **心理学：** `experimental / correlational / meta-analysis / pre-registered-replication`。

## 交叉引用

- `.codebuddy/references/journal-profiles.md`——在用的校准文件。
- `.codebuddy/agents/editor.md`——读画像，抽取审稿取向。
- `.codebuddy/skills/review-paper/SKILL.md`——`--peer [SHORT]` 的入口。
