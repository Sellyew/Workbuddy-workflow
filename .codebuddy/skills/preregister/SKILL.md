---
name: preregister
description: 从一份研究规格或自由撰写的研究描述，起草结构化的预注册文档（OSF、AsPredicted 或 AEA RCT Registry 样式）。输出是一份 Markdown 文件，包含假设、设计、抽样计划、分析计划、排除项与推断标准，并标注 MUST / SHOULD / MAY 清晰度标记。当用户说 "preregister"、"draft a preregistration"、"OSF preregistration"、"AsPredicted"、"AEA RCT registry"、"PAP"、"preanalysis plan"，或在启动一个实验 / 数据收集 / 对分析者尚未见过的数据做分析之前使用。它不是注册平台投稿工具 —— 它产出一份由用户自己上传到 OSF / AsPredicted / AEA 的文档。
description_zh: 从一份研究规格或自由撰写的研究描述，起草结构化的预注册文档（OSF、AsPredicted 或 AEA RCT Registry 样式）。输出是一份 Markdown 文件，包含假设、设计、抽样计划、分析计划、排除项与推断标准，并标注 MUST / SHOULD / MAY 清晰度标记。当用户说 "preregister"、"draft a preregistration"、"OSF preregistration"、"AsPredicted"、"AEA RCT registry"、"PAP"、"preanalysis plan"，或在启动一个实验 / 数据收集 / 对分析者尚未见过的数据做分析之前使用。它不是注册平台投稿工具 —— 它产出一份由用户自己上传到 OSF / AsPredicted / AEA 的文档。
argument-hint: "[--style osf|aspredicted|aea-rct] [--input <spec-or-description>] [--no-verify]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Agent", "Task"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# /preregister —— 预注册文档生成器

产出一份注册平台可用的预注册文档。用户自己把它上传到真实注册平台（OSF / AsPredicted / AEA RCT Registry）—— 本技能负责写文字与结构，不向任何地方提交。

## 为什么要预注册

预注册是对你的假设、设计与分析计划的书面承诺，写在**你看到数据之前**（对观察性分析而言，写在分析已实现的结果之前）。它把验证性检验与探索性检验分开，保护你不受 p-hacking、HARKing 与分叉路径之害。不同领域用不同的注册平台：

- **政治学**、**心理学**、广义社会科学 → **OSF**（osf.io/registries）是默认。AsPredicted（aspredicted.org）是实验常用的一种短表。
- **经济学田野实验** → **AEA RCT Registry**（socialscienceregistry.org），自 2018 年起是投 AEA 期刊的强制要求。
- **公共卫生 / 临床试验** → ClinicalTrials.gov 或 ISRCTN（**本技能不覆盖** —— 用试验注册平台自己的模板）。

## 何时使用

- 启动一个实验（实验室、田野或问卷）之前。
- 为某个特定研究问题，在目标人群上收集观察数据之前。
- 分析你有权限访问、但尚未针对焦点假设检视过的数据之前。
- R&R 期间，审稿人要求一份书面的预分析计划时。

## 何时不要使用

- 在你已经看过实现结果、想「补做预注册」时 —— 那不是预注册。如果输入描述里包含结果，本技能会拒绝。
- 为探索性分析 —— 那些不需要预注册；它们需要透明的标注。
- 为元分析 —— 直接用 PROSPERO，不要用本模板。

## 工作流

### PHASE 1 —— 读输入

两种输入模式：

1. **`--input <path>`** —— 一份由 `/interview-me` 产出的研究规格（保存在 `quality_reports/specs/` 下）或任何结构化 Markdown 文件。读该规格并抽取：研究问题、假设（要有方向！）、数据来源、设计、样本、分析路径。如果规格记录了论文类型（`/interview-me` 把它写在 `**Paper type:**` 行上，例如 `survey-experiment`），用它来影响样式的选择。
2. **没有 `--input`** —— 提示用户给一段 1–3 段的研究描述，然后继续。如果描述缺一个有方向的假设，只问一次。不要编造。

拒绝条件（必须在任何起草之前检查）：

- 描述里含已实现的结果（"we found"、"the estimate is"、"p ="）→ 用这句话拒绝：「预注册是前瞻性的；这段描述里包含结果。你是不是想用 `/respond-to-referees`，或者写一节方法？」
- 描述里完全没有可检验的假设（纯探索性框架）→ 标记出来，并问用户是否要 OSF 模板的*探索性分析*版本（仍然有用，但不是一次注册的验证性检验）。

### PHASE 2 —— 选样式

按领域的默认值（`--style` 未给出时使用）：

| 领域信号 | 默认样式 |
|---|---|
| `**Paper type:** survey-experiment`，或政治学 / 心理学语境 | `osf` |
| 经济学的田野实验 / 标注为 "RCT" / 经 IRB 批准的随机化干预 | `aea-rct` |
| 九问速填表、实验室心理学实验、时间紧张 | `aspredicted` |
| 其他任何情况 | `osf` |

用户可用 `--style osf|aspredicted|aea-rct` 覆盖。

### PHASE 3 —— 生成文档

读 `templates/preregistration-template.md`。模板有三个样式小节；**只用与所选样式匹配的那一节**（不要合并 —— 各注册平台不一样）。

所有样式共有，文档 MUST 包含：

- 标题与作者。
- 日期与版本。
- 回指来源规格的指针（如果给了 `--input`），好让可追溯性存活下来。

样式专属小节：

- **`osf`** —— Hypotheses (directional, numbered) · Design · Sampling Plan · Variables · Analysis Plan · Inference Criteria · Data Exclusions · Missing Data Handling · Exploratory Analyses (clearly labelled as such) · Other.
- **`aspredicted`** —— 按 AsPredicted 表单的 9 个编号字段：(1) data collection status, (2) hypothesis, (3) key dependent variable, (4) conditions, (5) analyses, (6) outliers/exclusions, (7) sample size + stopping rule, (8) anything else, (9) name (study not paper)。
- **`aea-rct`** —— Intervention · Outcomes (primary, secondary) · Primary hypotheses · Sample (target N, eligibility, randomization unit, randomization method) · IRB approval · Trial dates · Power calc · Pre-analysis plan attachment · Status (not yet on the air / ongoing / completed)。

给每一节标注以下之一：

- **MUST** —— 注册平台要求；没有它文档无法提交。
- **SHOULD** —— 强烈建议；审阅者会期待它。
- **MAY** —— 可选；相关就写。

复用 `templates/requirements-spec.md` 里的 MUST/SHOULD/MAY 框架。对输入没有提供的每一个 MUST，写 `[CLARIFY: <specific question>]`，而不是编造内容。

### PHASE 4 —— 交叉核对（写盘之前）

以下任一项不通过，就拒绝把文档标为「ready」：

- **假设的方向性。** 每条假设必须含一个方向（"higher than"、"increases"、"negatively predicts"；在等价性检验下，"no effect" 作为有方向的主张也可接受）。拒绝没有符号的 "is associated with"。
- **估计量被点名。** 分析计划要点名一个具体的估计量（OLS、logit、fixest::feols、lme4::lmer、ATT difference-in-means …）和一个主要结果变量。只写 "Regression" 不够。
- **样本计划是数字化的。** 目标 N、停止规则或功效计算目标出现在文中。"As many as possible" 不是一份抽样计划。对 RCT 与前瞻性设计，按 [`/power-analysis`](../power-analysis/SKILL.md) 的 `SKILL.md`（去读它 —— 该技能仅由用户调用，所以不能从这里调用）产出 MDE / 所需 N，以及一段可直接粘贴进该字段的功效段落。
- **排除规则事前写定。** 离群值与排除规则在数据被看到*之前*写明（"we will exclude observations with completion time < 1 minute"）。含糊的 "we'll deal with outliers" 不合格。
- **内部一致性。** 若设计是随机化的，随机化单位与分析单位一致，或者分析计划处理了聚类。若是观察性的，要写明识别策略。

每一项不通过，文档就得到一个 `[CLARIFY: …]` 占位符；文档仍写盘，但在输出摘要里标为「INCOMPLETE —— N 个 MUST 项未解决」。

### PHASE 5 —— 落地后核验

如果文档在理由小节引用了既有文献（例如 "Building on Hainmueller et al. 2014, we expect …"），通过 `Agent` 工具调用 `/verify-claims` 对这些引用做事实核验。传入草稿路径和一份明确的引文清单。`claim-verifier` 代理（独立上下文，从不看草稿）对每条引文返回 PASS / PARTIAL / FAIL。输出摘要里要浮现任何 FAIL/PARTIAL。

以下情况跳过落地后核验：

- 文档里没有既有文献引用。
- 用户传了 `--no-verify`（该开关继承自 `/lit-review` 与 `/research-ideation` 的落地后核验）。

### PHASE 6 —— 输出

写到 `quality_reports/preregistrations/YYYY-MM-DD_<slug>.md`（已 gitignore —— 预注册本就是要打上时间戳并上传到外部平台，而不是与代码一起提交）。

打印到对话：

```
✓ Preregistration draft saved: quality_reports/preregistrations/<file>.md
  Style: <osf|aspredicted|aea-rct>
  Sections: <count> total — <complete> complete, <clarify> with [CLARIFY:] placeholders
  Citations verified: <PASS>/<PARTIAL>/<FAIL>  (or "no citations to verify")
  Next: review the [CLARIFY:] placeholders, fill in, then upload to <registry-url>
```

写明注册平台 URL：OSF → `osf.io/registries`，AsPredicted → `aspredicted.org`，AEA RCT → `socialscienceregistry.org`。

## 参数

| 参数 | 作用 |
|---|---|
| `--style` | 选注册样式：`osf`、`aspredicted` 或 `aea-rct`；不给则按领域信号取默认。 |
| `--input` | 读一份研究规格或结构化 Markdown 作为输入，而不是靠对话里的描述。 |
| `--no-verify` | 跳过 PHASE 5 的引文落地后核验。 |

## 交叉引用

- `templates/preregistration-template.md` —— 本技能使用的三份样式模板。
- `templates/requirements-spec.md` —— 这里复用的 MUST/SHOULD/MAY 标注语言。
- `.codebuddy/skills/interview-me/SKILL.md` —— 产出本技能经 `--input` 使用的那份规格。
- `.codebuddy/skills/power-analysis/SKILL.md` —— 被遵循（而非被调用）以提供样本计划字段（RCT）的 MDE / 所需 N + 功效段落。
- `.codebuddy/skills/verify-claims/SKILL.md` —— PHASE 5 调用它做引文的落地后核验。
- `.codebuddy/references/discipline-cards.md` —— 驱动 `--style` 选择的领域默认值。
- `.codebuddy/rules/replication-protocol.md` —— 预注册是*向前*的承诺；replication-protocol 是*向后*的契约。

## 示例

### 示例 1 —— 从规格出发的政治学问卷实验
**用户说：** "Preregister this study"（附带 `--input quality_reports/specs/2026-04-15_priming-effects.md`）
**动作：**
1. 读规格；`**Paper type:** survey-experiment` → 默认样式 `osf`。
2. 抽出 2 条有方向的假设、MTurk N=1,200、带处理虚拟变量的 OLS。
3. 生成 OSF 文档，所有 MUST 小节都填好，留 1 个 MAY 为空。
4. 除规格外没有既有文献引用 —— 跳过落地后核验。
**结果：** 保存到 `quality_reports/preregistrations/2026-04-15_priming-effects.md`。用户上传到 OSF。

### 示例 2 —— 经济学田野实验，AEA RCT Registry
**用户说：** "Draft an AEA RCT preregistration for the cash-transfer pilot"（附带 `--style aea-rct --input quality_reports/specs/2026-03-10_ct-pilot.md`）
**动作：**
1. 读规格；随机化单位 = village，主要结果 = consumption。
2. 生成 AEA RCT 字段。规格里缺 IRB 编号 → `[CLARIFY: IRB approval number]`。
3. 交叉核对：估计量（cluster-robust OLS）、主要结果已写明、排除规则（intent-to-treat）已写明。通过。
4. 没有既有文献引用 —— 跳过落地后核验。
**结果：** 文档写出。输出摘要标记出 1 个 `[CLARIFY:]` 项，要在投 AEA 之前填好。

### 示例 3 —— 自由撰写的描述，AsPredicted 短表
**用户说：** "Preregister my next priming experiment, AsPredicted style"（无 `--input`）
**动作：**
1. 提示用户给 1–3 段的描述。
2. 用户给了一段；假设缺方向 → 问一次：「方向？」
3. 用户澄清；填充 9 个 AsPredicted 字段。
4. 样本量停止规则缺失 → `[CLARIFY: target N or stopping rule]`。
**结果：** 短表写出；标记出 1 个 MUST 的 `[CLARIFY:]`；告知用户在粘进 AsPredicted 之前填好。

## 疑难排查

**「描述里包含结果」** —— 这是设计使然。把结果移到方法 + 结果的写作里；预注册是前瞻性的。

**引文落地后核验返回 FAIL** —— `claim-verifier` 在 WebSearch / 语料里找不到被引的论文。要么引文是真的而核验者漏掉了（在非常新 / 付费墙后的工作上常见 —— 请显式给出 URL 引用），要么这条引文是幻觉。上传之前人工检查一遍。

**不同注册平台要求不同的东西** —— 如果本技能的映射太粗，就用注册平台自己的模板。这三种样式覆盖了约 90% 的社会科学预注册；边缘情形（PROSPERO、ClinicalTrials.gov、ISRCTN）需要注册平台的原生表单。

**输出目录不存在** —— 全新的 fork 上应当存在 `quality_reports/preregistrations/.gitkeep`；若缺失，技能会在写之前创建该目录。
