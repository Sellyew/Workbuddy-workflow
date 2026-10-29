# 学科卡片

简短的参考卡片，点名每个学科的主导论文类型频次、顶刊、预注册规范与方法惯例。当用户给出 `paper_type` 或领域提示但没指定目标期刊时，由 `/research-ideation`、`/interview-me` 和 `/preregister` 读取。

**范围。** v1.8.0 提供两张卡片：**经济学** 与 **政治学**。其他社会科学（心理学、社会学、公共卫生）无限期推迟（owner 定的范围，2026-06-10：经济学 + 密切相关的领域——没有 owner 的明确要求就不要建）。要加自己的学科，复制一节卡片，填好四个字段（论文类型频次、期刊、预注册规范、方法惯例），再从 `journal-profiles.md` 和 `methods-referee.md` 引用这个新短名。

**维护。** 当你往 `journal-profiles.md` 加一份期刊画像时，在这里交叉引用它。当你往 `methods-referee.md` 加一种论文类型时，也在这里交叉引用它。

---

## 经济学（`econ`）

**论文类型频次（Top-5 期刊里实证工作的粗略占比）。**

| 类型 | 占比 | 备注 |
|---|---|---|
| 简约式（reduced-form） | ~55% | DiD、IV、RD、事件研究、合成控制。主导形态。 |
| 结构式（structural） | ~20% | DSGE、一般均衡、产业组织的实证。集中在宏观／IO／劳动。 |
| 理论 + 实证 | ~15% | 带实证检验的理论论文，或带理论章节的实证论文。 |
| 描述性 | ~5% | 度量／数据构造。常走 AEA P&P 这条路。 |
| 形式理论 | ~5% | 纯理论（微观、IO、契约）。在 ECMA / TE / JET 更常见。 |

**主导期刊（已在 `journal-profiles.md` 中提供）。** AER、QJE、JPE、ECMA、ReStud。描述／度量类工作走 AEA P&P（会议论文集）。

**预注册规范。**
- **田野实验／RCT：** 自 2018 年起，投 AEA 系列期刊必须在 **AEA RCT Registry** 预注册。用 `/preregister --style aea-rct`。
- **实验室实验：** OSF / AsPredicted 越来越常见；尚未统一强制。
- **观察性／档案数据：** 预注册不常见；预分析计划出现在某些应用微观的角落。
- **复现包：** 强制执行 AEA Data and Code Availability Policy；在 openICPSR 完整存缴。

**方法惯例。**
- 显著性星号：AEA 系列期刊在表里**不**用星号（AEA 体例指引）。其他期刊（例如 ReStud、JPubE）仍允许。
- 标准误报告：预期在处置指派层级聚类；空间数据要求 Conley／空间标准误。
- 代码：R、Stata、Python、Julia 都接受；复现包必须自足且确定（`set.seed`）。

**交叉引用。** `methods-referee.md` 论文类型：reduced-form、structural、theory+empirics、descriptive、formal-theory。`journal-profiles.md`：AER、QJE、JPE、ECMA、ReStud。

---

## 政治学（`poli-sci`）

**论文类型频次（Top-3 期刊里实证工作的粗略占比）。**

| 类型 | 占比 | 备注 |
|---|---|---|
| 简约式（reduced-form） | ~40% | 因果推断（DiD、IV、RD）、观察性识别。AJPS 最强。 |
| 调查实验 | ~25% | 情境实验、联合分析、名单实验、析因设计。AJPS、JOP 强；APSR 在上升。 |
| 形式理论 | ~15% | 博弈论、机制设计、形式政治理论。APSR 最强。 |
| 描述性 | ~10% | 跨国／历史／案例描述。 |
| 理论 + 实证 | ~10% | 形式理论加对均衡预测的实证检验。 |

**主导期刊（已在 `journal-profiles.md` 中提供）。** APSR、AJPS、JOP。子领域刊物（IO、World Politics、JOP 的 research-notes 栏目）也很强。

**预注册规范。**
- **调查实验／实验室实验／田野实验：** OSF 或 AsPredicted 越来越被期待。**AJPS Replication Policy**（自 2015 年）要求录用时必须有复现档案，但预注册本身是社群规范，不是硬性要求。
- **观察性研究：** PAP（预分析计划）出现在应用工作里；尚未统一。
- **AEA RCT Registry** 是经济学的；政治学的田野实验更常用 OSF 或 EGAP 的仓库（egap.org）——不过 EGAP 已在 2022 年把它的注册库并入 OSF。

**方法惯例。**
- 显著性星号：**会**用（常见门槛 0.05/0.01/0.001）。引文格式遵循 APSA Style Manual。
- 标准误报告：调查实验在被试层级聚类，稳健标准误（HC2 或 HC3）是标准。
- 复现档案：AJPS Replication Policy 要求录用前存缴；APSR 与 JOP 建议如此。
- 代码：R 主导；Stata 在 IR／比较政治仍常见；Python 在文本即数据的工作上在上升。

**交叉引用。** `methods-referee.md` 论文类型：reduced-form、formal-theory、survey-experiment、theory+empirics、descriptive（结构式在政治学里罕见）。`journal-profiles.md`：APSR、AJPS、JOP。

---

## 技能如何使用这些卡片

- **`/research-ideation`** —— 当用户只给话题、没给学科时，技能可以从上下文（引文格式、词汇）推断一个。卡片提供默认的 `paper_type` 分布，用以偏置假设生成。
- **`/interview-me`** —— 第一阶段那个论文类型问题用卡片的频次表来排列选项顺序（按学科最可能者在前）。
- **`/preregister`** —— `--style` 默认取卡片预注册规范建议（例如政治学用 `osf`，经济学田野实验用 `aea-rct`）。
- **`/review-paper --peer`** **不**读这些卡片：`--peer` 要求从 `journal-profiles.md` 取一个期刊短名，起飞前检查遇到未知或缺失的期刊就停下。你自己用卡片的「主导期刊」清单来挑那个短名。

---

## 新增一张学科卡片

复制这个模板：

```markdown
## [Discipline name] (`short-slug`)

**Paper-type frequencies.**
| Type | Share | Notes |
|---|---|---|
| ... |

**Dominant journals (shipped in `journal-profiles.md`).** [list]. [Optional: subfield outlets.]

**Preregistration norms.**
- [registry conventions per study type]

**Method conventions.**
- [significance stars / SE conventions / replication norms / dominant code language]

**Cross-references.** `methods-referee.md` paper types: [list]. `journal-profiles.md`: [list].
```

然后：

1. 把上面的卡片节加进来（按短名字母序）。
2. 至少为 top-3 期刊在 `journal-profiles.md` 里加上具体的期刊画像。
3. 如果你的领域用到 `methods-referee.md` 里还没有的类别，就往那里加论文类型（例如社会学用 qualitative-case-study，公共卫生用 mixed-methods）。
4. 若 `/research-ideation` 与 `/interview-me` 应当尊重这些新默认值，就从它们那里交叉引用新的短名。

---

## 本文件在哪里

- **文件：** `.codebuddy/references/discipline-cards.md`
- **对应的 schema：** `.codebuddy/references/journal-profiles.md`（逐期刊）与 `.codebuddy/references/audit-pet-peeves.md`（活目录格式）。
- **消费者：** `/research-ideation`、`/interview-me`、`/preregister`。
