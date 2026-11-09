---
name: preregister
description: 根据研究需求说明或自由撰写的研究描述，起草 OSF、AsPredicted 或 AEA RCT Registry 样式的结构化预注册文档。Markdown 输出包含假设、设计、抽样计划、分析计划、排除项和推断标准，并用 MUST / SHOULD / MAY 标记清晰度。用户说 "preregister"、"draft a preregistration"、"OSF preregistration"、"AsPredicted"、"AEA RCT registry"、"PAP"、"preanalysis plan"、"预注册这项研究"、"写预分析计划" 时，或在启动实验、收集数据、分析研究者尚未见过的数据之前使用。本技能不向注册平台投稿，只生成由用户自行上传到 OSF / AsPredicted / AEA 的文档。
description_zh: 根据研究需求说明或自由撰写的研究描述，起草 OSF、AsPredicted 或 AEA RCT Registry 样式的结构化预注册文档。Markdown 输出包含假设、设计、抽样计划、分析计划、排除项和推断标准，并用 MUST / SHOULD / MAY 标记清晰度。用户说 "preregister"、"draft a preregistration"、"OSF preregistration"、"AsPredicted"、"AEA RCT registry"、"PAP"、"preanalysis plan"、"预注册这项研究"、"写预分析计划" 时，或在启动实验、收集数据、分析研究者尚未见过的数据之前使用。本技能不向注册平台投稿，只生成由用户自行上传到 OSF / AsPredicted / AEA 的文档。
argument-hint: "[--style osf|aspredicted|aea-rct] [--input <spec-or-description>] [--no-verify]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Agent", "Task"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# /preregister —— 预注册文档生成器

生成可提交到注册平台的预注册文档，由用户自行上传到 OSF / AsPredicted / AEA RCT Registry。本技能只负责文字和结构，不向任何平台提交。

## 为什么要预注册

预注册是在**看到数据之前**书面承诺假设、设计和分析计划；观察性分析则要在看到已实现结果之前作出承诺。它区分验证性检验与探索性检验，防止 p-hacking、HARKing 和分叉路径影响研究结论。不同领域使用不同平台：

- **政治学**、**心理学**和广义社会科学通常默认使用 **OSF**（osf.io/registries）。AsPredicted（aspredicted.org）是实验常用的短表。
- **经济学田野实验**使用 **AEA RCT Registry**（socialscienceregistry.org）；自 2018 年起，投 AEA 期刊必须注册。
- **公共卫生 / 临床试验**使用 ClinicalTrials.gov 或 ISRCTN。**本技能不覆盖这些平台**，请使用试验注册平台自己的模板。

## 何时使用

- 启动实验室、田野或问卷实验之前。
- 为特定研究问题在目标人群上收集观察数据之前。
- 分析你有权访问、但尚未针对焦点假设检视的数据之前。
- R&R 期间，审稿人要求书面预分析计划时。

## 何时不要使用

- 已经看过实现结果，再想「补做预注册」时。那不是预注册；输入描述包含结果时，本技能会拒绝。
- 探索性分析不需要预注册，但需要透明标注。
- 元分析直接使用 PROSPERO，不用本模板。

## 工作流

### PHASE 1 —— 读输入

支持两种输入模式：

1. **`--input <path>`**：读取 `/interview-me` 生成的研究需求说明，通常保存在 `quality_reports/specs/`，也可读取任何结构化 Markdown 文件。提取研究问题、假设（必须有方向）、数据来源、设计、样本和分析路径。如果研究需求说明记录论文类型，`/interview-me` 会写在 `**Paper type:**` 行，例如 `survey-experiment`，可据此选择样式。
2. **没有 `--input`**：请用户提供 1–3 段研究描述后继续。如果缺少有方向的假设，只询问一次，不要编造。

起草前必须检查以下拒绝条件：

- 描述包含已实现的结果（"we found"、"the estimate is"、"p ="）时，用这句话拒绝：「预注册是前瞻性的；这段描述里包含结果。你是不是想用 `/respond-to-referees`，或者写一节方法？」
- 描述完全没有可检验假设，只是纯探索性框架时，明确指出，并询问用户是否要 OSF 模板的*探索性分析*版本。它仍然有用，但不属于注册的验证性检验。

### PHASE 2 —— 选样式

未提供 `--style` 时，按领域选择默认值：

| 领域信号 | 默认样式 |
|---|---|
| `**Paper type:** survey-experiment`，或政治学 / 心理学语境 | `osf` |
| 经济学的田野实验 / 标注为 "RCT" / 经 IRB 批准的随机化干预 | `aea-rct` |
| 九问速填表、实验室心理学实验、时间紧张 | `aspredicted` |
| 其他任何情况 | `osf` |

用户可用 `--style osf|aspredicted|aea-rct` 覆盖默认值。

### PHASE 3 —— 生成文档

读取 `templates/preregistration-template.md`。模板包含三个样式小节，**只使用与所选样式匹配的小节**，不要合并，因为各注册平台的要求不同。先在内存中形成完整草稿，供 Phase 4–5 检查；此阶段不写盘，也不创建供核验器读取的临时草稿文件。

所有样式的文档 MUST 包含：

- 标题和作者。
- 日期和版本。
- 如果提供了 `--input`，还要包含指回来源研究需求说明的指针，保留可追溯性。

各样式的专属小节如下：

- **`osf`** —— Hypotheses (directional, numbered) · Design · Sampling Plan · Variables · Analysis Plan · Inference Criteria · Data Exclusions · Missing Data Handling · Exploratory Analyses (clearly labelled as such) · Other.
- **`aspredicted`** —— 按 AsPredicted 表单的 9 个编号字段：(1) data collection status, (2) hypothesis, (3) key dependent variable, (4) conditions, (5) analyses, (6) outliers/exclusions, (7) sample size + stopping rule, (8) anything else, (9) name (study not paper)。
- **`aea-rct`** —— Intervention · Outcomes (primary, secondary) · Primary hypotheses · Sample (target N, eligibility, randomization unit, randomization method) · IRB approval · Trial dates · Power calc · Pre-analysis plan attachment · Status (not yet on the air / ongoing / completed)。

每节标记为以下一种：

- **MUST**：注册平台要求，缺少后无法提交文档。
- **SHOULD**：强烈建议提供，审阅者通常会期待。
- **MAY**：可选，相关时填写。

复用 `templates/requirements-spec.md` 的 MUST/SHOULD/MAY 框架。输入未提供的每个 MUST 项都写 `[CLARIFY: <specific question>]`，不要编造内容。

### PHASE 4 —— 交叉核对（写盘之前）

任一项未通过，都不得把文档标为「ready」：

- **假设有方向。** 每条假设必须包含方向，例如 "higher than"、"increases"、"negatively predicts"；等价性检验中的 "no effect" 也可作为有方向的主张。没有方向的 "is associated with" 不予接受。
- **点名估计量。** 分析计划必须写出具体估计量（OLS、logit、fixest::feols、lme4::lmer、ATT difference-in-means …）和主要结果变量，只写 "Regression" 不够。
- **样本计划包含数字。** 文中必须有目标 N、停止规则或功效计算目标，"As many as possible" 不是抽样计划。RCT 和前瞻性设计要遵循 [`/power-analysis`](../power-analysis/SKILL.md) 的 `SKILL.md`，生成 MDE / 所需 N 以及可直接粘贴到该字段的功效段落。必须阅读该技能，因为它只能由用户调用，不能从这里调用。
- **事前确定排除规则。** 在看到数据*之前*写明离群值和排除规则，例如 "we will exclude observations with completion time < 1 minute"。含糊的 "we'll deal with outliers" 不合格。
- **内部一致。** 随机化设计的随机化单位要与分析单位一致，否则分析计划必须处理聚类；观察性设计必须写明识别策略。

每个未通过项都添加 `[CLARIFY: …]` 占位符。文档仍会写盘，但输出摘要必须标为「INCOMPLETE —— N 个 MUST 项未解决」。

### PHASE 5 —— 落地后核验（内存草稿的 CoVe 交接）

如果文档在理由小节引用既有文献，例如 "Building on Hainmueller et al. 2014, we expect …"，由调用方从**内存草稿**抽取核验清单。每条包含：断言 ID 与事实断言、一个能由来源确认或反驳的具体核验问题、来源指针（文献 URL/DOI，或输入文件路径及章节、页码、段落定位）。

随后通过 `Agent` 工具发起独立调用，设置 `subagent_type=claim-verifier`，只传这份“断言 + 核验问题 + 来源指针”清单。**不要传草稿、草稿路径或整段草稿上下文**，也不要使用会继承草稿的对话分叉。此时草稿尚未写盘，不得虚构一个路径让核验器读取。

核验器对每条断言返回 PASS / PARTIAL / FAIL 和证据。FAIL 时，依据证据在内存中重新生成受影响小节并重新核验，最多重试 2 次；PARTIAL 和仍无法核验的项目必须写入输出摘要。核验器报错、超时或返回畸形结果时，最终稿只能标为暂定，不能声称已经独立核验。

以下情况跳过落地后核验：

- 文档没有引用既有文献。
- 用户传入 `--no-verify`，该开关继承自 `/lit-review` 和 `/research-ideation` 的落地后核验。

### PHASE 6 —— 输出

完成 Phase 5 的独立核验和必要的内存修订后，才用 `Write` 工具把**最终稿**写入 `quality_reports/preregistrations/YYYY-MM-DD_<slug>.md`。如果跳过核验，也必须先完成 Phase 4 再写。该目录已 gitignore，因为预注册应加时间戳并上传到外部平台，而不是与代码一起提交。

在对话中打印：

```
✓ Preregistration draft saved: quality_reports/preregistrations/<file>.md
  Style: <osf|aspredicted|aea-rct>
  Sections: <count> total — <complete> complete, <clarify> with [CLARIFY:] placeholders
  Citations verified: <PASS>/<PARTIAL>/<FAIL>  (or "no citations to verify")
  Next: review the [CLARIFY:] placeholders, fill in, then upload to <registry-url>
```

写明注册平台 URL：OSF → `osf.io/registries`，AsPredicted → `aspredicted.org`，AEA RCT → `socialscienceregistry.org`。同时附上 **Post-Flight Verification** 块，列出抽取断言数、独立核验数、PASS / PARTIAL / FAIL 结果、已核实证据，以及无法核验或已在最终稿中修正的分歧；跳过核验时明确说明原因。

## 参数

| 参数 | 作用 |
|---|---|
| `--style` | 选注册样式：`osf`、`aspredicted` 或 `aea-rct`；不给则按领域信号取默认。 |
| `--input` | 读一份研究需求说明或结构化 Markdown 作为输入，而不是靠对话里的描述。 |
| `--no-verify` | 跳过 PHASE 5 的引文落地后核验。 |

## 交叉引用

- `templates/preregistration-template.md` —— 本技能使用的三份样式模板。
- `templates/requirements-spec.md` —— 这里复用的 MUST/SHOULD/MAY 标注语言。
- `.codebuddy/skills/interview-me/SKILL.md` —— 产出本技能经 `--input` 使用的那份研究需求说明。
- `.codebuddy/skills/power-analysis/SKILL.md` —— 被遵循（而非被调用）以提供样本计划字段（RCT）的 MDE / 所需 N + 功效段落。
- [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) —— PHASE 5 的内存草稿 CoVe 与独立 `claim-verifier` 交接契约。
- `.codebuddy/references/discipline-cards.md` —— 驱动 `--style` 选择的领域默认值。
- `.codebuddy/rules/replication-protocol.md` —— 预注册是*向前*的承诺；replication-protocol 是*向后*的契约。

## 示例

### 示例 1 —— 从研究需求说明出发的政治学问卷实验
**用户说：** "Preregister this study"（附带 `--input quality_reports/specs/2026-04-15_priming-effects.md`）
**动作：**
1. 读取研究需求说明，发现 `**Paper type:** survey-experiment`，因此默认使用 `osf`。
2. 提取 2 条有方向的假设、MTurk N=1,200，以及带处理虚拟变量的 OLS。
3. 生成 OSF 文档，填好所有 MUST 小节，留 1 个 MAY 为空。
4. 除研究需求说明外没有既有文献引用，因此跳过落地后核验。
**结果：** 保存到 `quality_reports/preregistrations/2026-04-15_priming-effects.md`，由用户上传到 OSF。

### 示例 2 —— 经济学田野实验，AEA RCT Registry
**用户说：** "Draft an AEA RCT preregistration for the cash-transfer pilot"（附带 `--style aea-rct --input quality_reports/specs/2026-03-10_ct-pilot.md`）
**动作：**
1. 读取研究需求说明：随机化单位 = village，主要结果 = consumption。
2. 生成 AEA RCT 字段；研究需求说明缺少 IRB 编号，因此写 `[CLARIFY: IRB approval number]`。
3. 交叉核对估计量（cluster-robust OLS）、主要结果和排除规则（intent-to-treat），均已写明，通过。
4. 没有既有文献引用，因此跳过落地后核验。
**结果：** 文档已写出；输出摘要标出 1 个 `[CLARIFY:]` 项，投 AEA 前必须填好。

### 示例 3 —— 自由撰写的描述，AsPredicted 短表
**用户说：** "Preregister my next priming experiment, AsPredicted style"（无 `--input`）
**动作：**
1. 请用户提供 1–3 段描述。
2. 用户提供的假设缺少方向，因此只问一次：「方向？」
3. 用户澄清后，填充 9 个 AsPredicted 字段。
4. 缺少样本量停止规则，因此写 `[CLARIFY: target N or stopping rule]`。
**结果：** 短表已写出，标出 1 个 MUST 的 `[CLARIFY:]`，并提醒用户粘贴到 AsPredicted 前填好。

## 疑难排查

**「描述里包含结果」**：这是有意拒绝。把结果移到方法和结果写作中，预注册必须面向未来。

**引文落地后核验返回 FAIL**：`claim-verifier` 在 WebSearch / 语料中找不到被引论文。可能论文真实存在但核验者漏检，这在非常新或付费墙后的论文中较常见，此时请显式提供 URL；也可能引文本身就是幻觉。上传前必须人工检查。

**不同注册平台要求不同的内容**：如果本技能的映射过粗，使用注册平台自己的模板。这三种样式覆盖约 90% 的社会科学预注册；PROSPERO、ClinicalTrials.gov、ISRCTN 等边缘情形需要平台原生表单。

**输出目录不存在**：全新 fork 应有 `quality_reports/preregistrations/.gitkeep`；如果缺失，技能会在写入前创建目录。
