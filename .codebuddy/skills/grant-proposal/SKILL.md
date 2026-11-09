---
name: grant-proposal
description: 用现有技能拼装符合资助方结构的研究基金申请书草稿：从 `/interview-me` 研究需求说明读取识别策略，把数据管理计划交给 `/data-management-plan`，把设施条件陈述交给 `/capture-environment`，并生成资助方要求清单。用户说 "draft a grant"、"write a proposal"、"NSF proposal"、"NIH aims"、"ERC application"、"foundation grant"、"specific aims"、"scaffold a grant proposal"、"起草基金申请"、"写研究申请书" 或 "搭一份申请书框架" 时使用。它不是投稿工具，只生成草稿，由用户自行上传到资助方门户。
description_zh: 用现有技能拼装符合资助方结构的研究基金申请书草稿：从 `/interview-me` 研究需求说明读取识别策略，把数据管理计划交给 `/data-management-plan`，把设施条件陈述交给 `/capture-environment`，并生成资助方要求清单。用户说 "draft a grant"、"write a proposal"、"NSF proposal"、"NIH aims"、"ERC application"、"foundation grant"、"specific aims"、"scaffold a grant proposal"、"起草基金申请"、"写研究申请书" 或 "搭一份申请书框架" 时使用。它不是投稿工具，只生成草稿，由用户自行上传到资助方门户。
argument-hint: "[--funder nsf|nih|erc|foundation] [--call <file>] [--input <spec>] [--out <dir>] [--no-verify]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
---

# /grant-proposal —— 研究基金申请书脚手架

利用已有技能生成符合资助方结构的申请书草稿：`/interview-me` 的研究需求说明提供科学内容，`/data-management-plan` 提供 DMP，`/capture-environment` 提供设施和计算环境陈述，`/lit-review` 负责界定既有研究。本技能只负责组织并衔接这些内容，**不**向任何平台投稿，也不会在缺少研究需求说明时编造识别策略。

**核心原则：** 申请书各部分必须一致。目标、方法、预算、时间表和广泛影响要彼此对应，也要符合底层研究需求说明。与空白模板相比，本技能的主要价值是 Phase 3 的一致性检查：目标 ↔ 方法 ↔ 预算 ↔ 时间表。

## 何时使用

- 根据已有研究想法起草 NSF / NIH / ERC / 基金会申请书。
- 把 `/interview-me` 研究需求说明或 `/preregister` 的 PAP 改写成值得资助的叙事。
- 生成 DMP、设施和数据共享等格式化但必填的部分，让申请人集中撰写科学内容。
- 重新提交时，根据审稿人「修改后再投」的意见重新组织目标。

## 何时不要使用

- 如果需要从零构思科学内容，先运行 `/interview-me`；本技能不会捏造识别策略。
- 临床试验类资助方要求使用自己的方案模板时，应使用该模板，本技能不覆盖这类需求。
- 如果需要可直接提交的成品 PDF，本技能并不适用。它只写 Markdown 章节和清单，最终仍需按资助方格式组装。

## 资助方画像

用占位画像适配不同资助方。`--funder` 决定章节集合和命名，默认值为 `nsf`。只有未提供招标文件时才使用这些画像；项目自己的招标文件（`--call`）始终优先。

| 资助方 | 核心章节（按资助方命名） | 页数/格式信号 |
|---|---|---|
| **`nsf`** | Project Summary (Overview/Intellectual Merit/Broader Impacts) · Project Description · Broader Impacts · Data Management & Sharing Plan · Facilities/Equipment · Budget Justification | Project Description 为 15 页；必须提供 DMSP |
| **`nih`** | Specific Aims (1 p.) · Research Strategy (Significance/Innovation/Approach) · Vertebrate/Human Subjects (if any) · Data Management & Sharing · Facilities & Other Resources · Budget Justification | Aims 页承担核心论证 |
| **`erc`** | Extended Synopsis (B1) · Scientific Proposal (B2: state-of-art, objectives, methodology) · CV + track record · Resources/Budget · Data Management | 以 PI 为中心；采用 "high-risk/high-gain" 框架 |
| **`foundation`** | Project Summary · Statement of Need · Goals & Objectives · Methods/Approach · Evaluation Plan · Budget Justification · Sustainability | 强调使命契合；方法部分较轻 |

主要以经济学为视角（DiD/事件研究、IV、RCT、面板，以及 AEA Data Editor / openICPSR / DCAS 的数据共享预期），但章节骨架不限学科。fork 本仓库的生物学者或计算机学者也可以填写相同槽位。

## 工作流

### Phase 0 —— 探测资助方与研究需求说明

1. 解析 `--funder`，或根据请求措辞推断；默认使用 `nsf`。起草前先回显所选画像。
2. 定位研究需求说明：优先使用 `--input <path>`，否则读取 `/interview-me` 最近生成的 `quality_reports/specs/research_spec_*.md`。两者都没有时，**停止并建议运行 `/interview-me`**，不要编造科学内容。
3. 从研究需求说明中提取研究问题、带方向的假设、识别策略（DiD / IV / RDD / RCT / 结构式）、数据来源、样本、预期结果和贡献。如果研究需求说明中有 `**Paper type:**` 值，也要记录。这是 `/interview-me` 写入的表头行；手写研究需求说明中的 `paper_type:` 字段同样有效。
4. **读取项目自己的招标文件。** 询问一次实际的 solicitation、NOFO、RFP 或 work-programme 文本，可通过 `--call <file>` 提供 PDF 或纯文本，Read 都能处理。拿到文件后，提取必需章节和文书、页数或字数上限、评审标准，引用原文并附页码；**绝不改写任何上限的措辞**。未拿到时继续使用通用画像，并在输出表头注明。
5. 扫描 `quality_reports/` 中可复用的相关产物：`/lit-review` 综合用于既有研究，`/preregister` 的 PAP 用于分析计划，`passport.yaml` 或 `/data-analysis` 产出用于初步结果。

### Phase 1 —— 从模板与研究需求说明搭出各章节

生成所选资助方的章节集合，并把研究需求说明内容映射到对应槽位：

- **Specific Aims / Project Summary**：研究问题，加上从研究需求说明的假设中提炼的 2–3 条带编号、带方向的目标。
- **Background & Significance**：研究动机和既有工作。如果有 `/lit-review` 综合，直接使用其中的引文；除非用户要求，否则不要重新检索。
- **Research Design & Methods**：逐字采用研究需求说明中的识别策略，包括估计目标、处理/对照、识别假设、稳健性与安慰剂策略、聚类。明确写出估计量，例如 `fixest::feols`、`AER::ivreg`、Stata `reghdfe`。
- **Preliminary Results**：概述已有 `/data-analysis` 或 passport 产出；如果没有，写 `[PRELIMINARY RESULTS: none yet — describe planned pilot]`。
- **Timeline & Milestones**：按季度或年份列出与目标对应的表，每个目标至少有一个里程碑。
- **Broader Impacts / Significance**：采用适合资助方的框架，分别对应 NSF Broader Impacts、NIH Significance 或基金会 mission-fit。
- **Budget Justification 骨架**：列出人员、数据获取、算力、差旅和传播等条目占位，每项都关联到一个目标。

研究需求说明未提供的 MUST 槽位写为 `[CLARIFY: <specific question>]`，绝不捏造。沿用 [`templates/requirements-spec.md`](../../../templates/requirements-spec.md) 中的 MUST / SHOULD / MAY 清晰度用语。

### Phase 2 —— 拼装 DMP 与计算环境陈述（委派）

1. **Data Management (& Sharing) Plan**：启动一个 `Agent`，让它读取 [`/data-management-plan`](../data-management-plan/SKILL.md) 的 `SKILL.md`，根据研究需求说明中的资助方和数据来源执行。该技能只能由用户调用（`disable-model-invocation`），所以这里要求代理照其内容执行，而不是调用技能。代理返回 DMP 章节，涵盖仓库选择（openICPSR / Dataverse / Zenodo）、访问和保留，以及 FAIR/DCAS 对齐。如果任何数据来源涉及敏感信息，例如受限行政数据、PII 或 IRB 受限数据，代理必须遵守 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md)，用安全飞地或 FSRDC 描述访问方式，而不是承诺开放发布。**不要起草承诺公开机密数据的共享计划。**
2. **Facilities / Computational-Environment statement**：通过 `Agent` 工具调用 [`/capture-environment`](../capture-environment/SKILL.md)，生成算力、软件和依赖陈述，包括集群、R/Stata/Python 工具链，以及 `renv.lock` / `DESCRIPTION` / `requirements.txt` 溯源，供 Facilities 章节使用。

如果某个被委派的技能不可用，保留 `[DELEGATE: /data-management-plan]` 占位符，不要自行写出一半内容充数。

### Phase 3 —— 一致性检查（目标 ↔ 方法 ↔ 预算 ↔ 时间表）

交叉核对组装好的草稿，报告以下不匹配：

- **目标 ↔ 方法**：每个目标都有明确的方法或估计量；没有不服务任何目标的孤立方法。
- **方法 ↔ 预算**：每项成本都能追溯到目标。例如 RCT 目标需要受试者激励条目，行政数据需要获取或飞地条目，大规模模拟需要算力条目。
- **目标 ↔ 时间表**：每个目标至少有一个里程碑，每个里程碑都归属于某个目标。
- **DMP ↔ 方法**：方法中列出的数据与 DMP 描述一致，机密来源没有被承诺开放。
- **页数/格式预算**：标出可能超过页数上限的章节。有招标文件时使用其中的上限，否则使用画像上限，例如 NSF 15 页 Project Description、NIH 1 页 Aims。有招标文件时，还要确认所有必需章节均已包含、每条评审标准均有回应，并引用招标文件页码。

### Phase 4 —— 落地后核验 + 输出

- **落地后（CoVe）**：如果 Background/Significance 引用既有文献，运行 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 的 Post-Flight 协议。通过 `Agent` 工具启动 `claim-verifier` 核验引文，必须使用独立上下文，绝不能使用对话分叉。报告 PASS / PARTIAL / FAIL / ERROR / INCOMPLETE。核验器超时、崩溃、返回无效报告，或重试尚未完成、已耗尽仍未获得有效结果时，记为 ERROR 或 INCOMPLETE，绝不能按通过处理。使用 `--no-verify` 时在表头和 Post-Flight 区明确标注 `UNVERIFIED — 未经核验（--no-verify）`，不得写 PASS；没有引文时标注 `NOT RUN — no citations`。
- **写出**：把各章节写入 `--out`，默认 `quality_reports/grants/YYYY-MM-DD_<slug>/`。每章一个 Markdown 文件，另附 `checklist.md`。

## 输出 / 报告格式

生成一份拼接各章节的 `proposal_draft.md` 和一份 `checklist.md`：

```markdown
# Grant Proposal Draft — [Title]
**Funder:** NSF | NIH | ERC | foundation     **Date:** YYYY-MM-DD
**Source spec:** quality_reports/specs/research_spec_<slug>.md
**Call:** <path> (read YYYY-MM-DD) | NOT PROVIDED — structure from the generic <funder> profile
**Verification:** PASS / PARTIAL / FAIL / ERROR / INCOMPLETE / NOT RUN — no citations / UNVERIFIED — 未经核验（--no-verify）
**Draft status:** DRAFT READY / DRAFT COMPLETE — UNVERIFIED / INCOMPLETE

## Funder-Requirements Checklist
| Requirement | Status | Source |
|---|---|---|
| Project Summary / Specific Aims | DRAFTED | Phase 1 |
| Research Design & Methods | DRAFTED | spec |
| Data Management & Sharing Plan | DELEGATED | /data-management-plan |
| Facilities / Computational Env | DELEGATED | /capture-environment |
| Budget Justification | SKELETON | Phase 1 |
| Broader Impacts / Significance | DRAFTED | Phase 1 |
| [n] [CLARIFY:] items unresolved | TODO | — |

## Coherence Report
- Aims ↔ Methods: PASS / [n issues]
- Methods ↔ Budget: PASS / [n issues]
- Aims ↔ Timeline: PASS / [n issues]
- DMP ↔ Methods (confidential-data check): PASS / [n issues]
- Page-budget flags: [sections at risk of overflow]

## Post-Flight Verification
Claims extracted: N · Reviewed: N · Supported: N · Contradicted: N · Cannot-verify: N · Outcome: PASS / PARTIAL / FAIL / ERROR / INCOMPLETE / NOT RUN — no citations / UNVERIFIED
Retry status: not needed / complete / pending / exhausted without a valid report
```

## 退出行为

**状态优先级：`INCOMPLETE` 最高。** 只要存在下列任一未完成条件，就只能报告 `INCOMPLETE`，不得同时报告 `DRAFT READY` 或 `DRAFT COMPLETE — UNVERIFIED`；后两种状态只在各自的全部条件满足时使用。

- **`INCOMPLETE`：** 存在 MUST 槽位未填、未决的 `[CLARIFY:]` / `[DELEGATE:]` 项或一致性问题；存在未解决 HIGH/FAIL；核验为 PARTIAL / FAIL / ERROR / INCOMPLETE；核验器错误或无效返回；重试尚未完成或耗尽后仍无有效结果。逐项列出并报告「INCOMPLETE —— N 项未解决 / 核验未完成或未通过」。使用 `--no-verify` 时若仍有上述任何一项，也同样报告 `INCOMPLETE`。
- **`DRAFT READY`：** 仅当所有 MUST 槽位已填、`[CLARIFY:]` / `[DELEGATE:]` 未决数均为零、一致性全部 PASS，且核验为 PASS 或 `NOT RUN — no citations` 时使用。报告「DRAFT READY —— 无未决澄清或委派项；仍须按资助方格式人工复核并装配」，不得同时提示有未决 `[CLARIFY:]`。
- **`DRAFT COMPLETE — UNVERIFIED`：** 仅当使用 `--no-verify`，且除核验外的完成条件全部满足时使用，即所有 MUST 槽位已填、无未决 `[CLARIFY:]` / `[DELEGATE:]`、一致性全部 PASS。在摘要和核验区重复标注「DRAFT COMPLETE — UNVERIFIED（未经核验）」，不使用 DRAFT READY、PASS 或“已核验”措辞。
- **找不到研究需求说明**：在 Phase 0 停止并建议 `/interview-me`，不写任何内容。

## 参数

| 参数 | 作用 |
|---|---|
| `--funder` | 取值 `nsf` / `nih` / `erc` / `foundation`，选择决定章节结构和要求清单的资助方画像。 |
| `--call` | `<file>`，项目的 solicitation / NOFO / RFP，支持 PDF 或纯文本。其中的必需章节、上限和评审标准覆盖通用画像。默认不提供，使用通用画像并在表头注明。 |
| `--input` | `<spec>`，`/interview-me` 研究需求说明的路径，用于生成目标和方法。默认使用最新的 `quality_reports/specs/research_spec_*.md`；不存在时停止并建议 `/interview-me`。 |
| `--out` | `<dir>`，章节文件的写入目录。默认 `quality_reports/grants/YYYY-MM-DD_<slug>/`，每章一个 Markdown 文件，另附 `checklist.md`。 |
| `--no-verify` | 跳过 Phase 4 的落地后核验；所有输出醒目标注 `UNVERIFIED — 未经核验`，不得写 PASS、“已核验”或 DRAFT READY。仅在其他完成条件全部满足时报告 DRAFT COMPLETE — UNVERIFIED，否则 INCOMPLETE 优先。没有引文时也跳过，但标为 `NOT RUN — no citations`。 |

## 交叉引用

- [`.codebuddy/skills/interview-me/SKILL.md`](../interview-me/SKILL.md)：生成本技能读取的研究需求说明；不存在时先运行它。
- [`.codebuddy/skills/data-management-plan/SKILL.md`](../data-management-plan/SKILL.md)：Phase 2 委派生成 DMP/DMSP 章节。
- [`.codebuddy/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md)：Phase 2 委派生成设施和计算环境陈述。
- [`.codebuddy/skills/lit-review/SKILL.md`](../lit-review/SKILL.md)：为 Background & Significance 界定既有研究。
- [`.codebuddy/skills/preregister/SKILL.md`](../preregister/SKILL.md)：PAP 可提供分析计划；预注册是受资助项目随后要履行的前瞻承诺。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md)：规定敏感数据来源如何写入 DMP 和预算。
- [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md)：Phase 4 的引文事实核查。

## 本技能不做的事

- **不向任何平台投稿。** 它只写 Markdown 和清单；组装并上传到 Research.gov / ASSIST / ERC 门户或基金会系统由用户完成。
- **不编造科学内容。** 没有研究需求说明就不生成申请书，也不会捏造识别策略、假设或目标。
- **不自行撰写 DMP 或设施陈述。** 这些内容委派给 `/data-management-plan` 和 `/capture-environment`，本技能只负责把产出接入资助方章节。
- **不计算预算。** 它只生成关联到目标的条目；实际金额、间接成本率和投入比例由 PI 与资助办公室决定。
- **不保证符合页数上限。** 它只标出可能溢出的位置；最终仍需人工按资助方的精确格式裁剪。
