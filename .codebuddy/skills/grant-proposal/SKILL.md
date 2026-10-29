---
name: grant-proposal
description: 以既有原语拼装一份贴合资助方形态的研究基金申请书草稿 —— 从 `/interview-me` 规格中取用识别策略，把数据管理计划委派给 `/data-management-plan`、把设施条件陈述委派给 `/capture-environment`，并输出一份资助方要求清单。当用户说 "draft a grant"、"write a proposal"、"NSF proposal"、"NIH aims"、"ERC application"、"foundation grant"、"specific aims" 或 "scaffold a grant proposal" 时使用。它不是投稿工具 —— 产出的是草稿，由用户自己上传到资助方门户。
description_zh: 以既有原语拼装一份贴合资助方形态的研究基金申请书草稿 —— 从 `/interview-me` 规格中取用识别策略，把数据管理计划委派给 `/data-management-plan`、把设施条件陈述委派给 `/capture-environment`，并输出一份资助方要求清单。当用户说 "draft a grant"、"write a proposal"、"NSF proposal"、"NIH aims"、"ERC application"、"foundation grant"、"specific aims" 或 "scaffold a grant proposal" 时使用。它不是投稿工具 —— 产出的是草稿，由用户自己上传到资助方门户。
argument-hint: "[--funder nsf|nih|erc|foundation] [--call <file>] [--input <spec>] [--out <dir>] [--no-verify]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
---

# /grant-proposal —— 研究基金申请书脚手架

从你已经具备的原语拼出一份贴合资助方形态的申请书草稿：`/interview-me` 的研究规格提供科学内容，`/data-management-plan` 提供 DMP，`/capture-environment` 提供设施/计算环境陈述，`/lit-review` 提供既有工作的框定。本技能负责组织与缝接 —— 它**不**向任何地方投稿，也不会在规格缺席时凭空发明识别策略。

**核心原则：** 申请书是一件*一致性*产物。目标、方法、预算、时间表与广泛影响必须彼此相符，也与底层的研究规格相符。本技能相对于一张空白模板的主要增值，是 Phase 3 的一致性检查（目标 ↔ 方法 ↔ 预算 ↔ 时间表）。

## 何时使用

- 从已有的研究想法起草 NSF / NIH / ERC / 基金会申请书。
- 把 `/interview-me` 规格（或 `/preregister` 的 PAP）转成一段值得资助的叙事。
- 拼装那些样板但必填的部分（DMP、设施、数据共享），让人类只写科学。
- 重新提交时，在审稿人「修改后再投」一轮之后重新搭目标。

## 何时不要使用

- 你需要把*科学本身*发明出来 —— 先跑 `/interview-me`；本技能拒绝捏造识别策略。
- 资助方是临床试验类，要求用它自己的方案模板（超出范围；用资助方的原生表单）。
- 你要一份可直接提交的成品 PDF —— 本技能写的是 Markdown 章节 + 一份清单；最终装配成资助方格式是你的活。

## 资助方画像

各资助方通过占位画像通用化。`--funder` 选择章节集合与命名；默认是 `nsf`。这些画像是没有提供招标文件时的兜底：项目自己的招标文件（`--call`）永远优先。

| 资助方 | 核心章节（按资助方命名） | 页数/格式信号 |
|---|---|---|
| **`nsf`** | Project Summary (Overview/Intellectual Merit/Broader Impacts) · Project Description · Broader Impacts · Data Management & Sharing Plan · Facilities/Equipment · Budget Justification | 15-page Project Description；DMSP required |
| **`nih`** | Specific Aims (1 p.) · Research Strategy (Significance/Innovation/Approach) · Vertebrate/Human Subjects (if any) · Data Management & Sharing · Facilities & Other Resources · Budget Justification | Aims page is load-bearing |
| **`erc`** | Extended Synopsis (B1) · Scientific Proposal (B2: state-of-art, objectives, methodology) · CV + track record · Resources/Budget · Data Management | PI-centric; "high-risk/high-gain" framing |
| **`foundation`** | Project Summary · Statement of Need · Goals & Objectives · Methods/Approach · Evaluation Plan · Budget Justification · Sustainability | Mission-fit framing; lighter methods |

经济学框定是主视角（DiD/事件研究、IV、RCT、面板；AEA Data Editor / openICPSR / DCAS 的数据共享预期），但章节骨架与学科无关 —— fork 本仓库的生物学者或计算机学者填的是同样的槽位。

## 工作流

### Phase 0 —— 探测资助方与规格

1. 解析 `--funder`（或从请求措辞推断；默认 `nsf`）。起草之前先回显所选画像。
2. 定位研究规格：`--input <path>`，否则取 `/interview-me` 最近写出的 `quality_reports/specs/research_spec_*.md`。若两者都没有，**停下并建议 `/interview-me`** —— 不要发明科学。
3. 从规格中提取：研究问题、假设（带方向）、识别策略（DiD / IV / RDD / RCT / 结构式）、数据来源、样本、预期结果、贡献。若存在，记录规格里的 `**Paper type:**` 值（`/interview-me` 写的那行表头；手写规格里的 `paper_type:` 字段同样接受）。
4. **项目自己的招标文件。** 询问一次实际的 solicitation、NOFO、RFP 或 work-programme 文本（`--call <file>`，PDF 或纯文本 —— Read 两者都能处理）。拿到之后，从中取必需的章节与文书、页数或字数上限、评审标准，引用它的原话并附页码；**绝不改写任何上限的措辞**。没拿到时，用通用画像继续，并在输出表头里说明这一点。
5. 扫描 `quality_reports/` 里可复用的相邻产物：一份 `/lit-review` 综合（既有工作）、一份 `/preregister` 的 PAP（分析计划）、一个 `passport.yaml` 或 `/data-analysis` 的产出（初步结果）。

### Phase 1 —— 从模板与规格搭出各章节

生成该资助方的章节集合。把规格内容映射进槽位：

- **Specific Aims / Project Summary** —— 研究问题 + 2–3 条带编号、带方向的目标，取自规格的假设。
- **Background & Significance** —— 动机 + 既有工作；若有 `/lit-review` 综合，从中取引文（除非被要求，否则不要重新检索）。
- **Research Design & Methods** —— 从规格逐字搬用识别策略（估计目标、处理/对照、识别假设、稳健性与安慰剂策略、聚类）。具体点名估计量（例如 `fixest::feols`、`AER::ivreg`、Stata `reghdfe`）。
- **Preliminary Results** —— 概述已有的 `/data-analysis` / passport 产出；否则写 `[PRELIMINARY RESULTS: none yet — describe planned pilot]`。
- **Timeline & Milestones** —— 按季度/年、对齐到目标的表（每个目标都要有一个里程碑）。
- **Broader Impacts / Significance** —— 与资助方相称的框定（NSF Broader Impacts、NIH Significance、基金会 mission-fit 各用各的框架）。
- **Budget Justification 骨架** —— 人员 / 数据获取 / 算力 / 差旅 / 传播的条目占位，每条都挂到一个目标上。

凡规格没有提供的 MUST 槽位，写 `[CLARIFY: <specific question>]` —— 绝不捏造。沿用 [`templates/requirements-spec.md`](../../../templates/requirements-spec.md) 里的 MUST / SHOULD / MAY 清晰度用语。

### Phase 2 —— 拼装 DMP 与计算环境陈述（委派）

1. **Data Management (& Sharing) Plan** —— 派生一个 `Agent`，读取 [`/data-management-plan`](../data-management-plan/SKILL.md) 的 `SKILL.md`，带上规格里的资助方 + 数据来源照着做（那个技能只能由用户调用 —— `disable-model-invocation` —— 所以是照着做，而不是调用它）。它返回 DMP 章节（仓库选择 —— openICPSR / Dataverse / Zenodo，访问/保留，FAIR/DCAS 对齐）。若任何数据来源敏感（受限使用的行政数据、PII、IRB 受限），让它遵守 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md)，并用安全飞地 / FSRDC 描述访问方式，而不是开放发布。**不要起草一份承诺公开机密数据的共享计划。**
2. **Facilities / Computational-Environment statement** —— 经 `Agent` 工具调用 [`/capture-environment`](../capture-environment/SKILL.md)，让它产出算力/软件/依赖陈述（集群、R/Stata/Python 工具链、`renv.lock` / `DESCRIPTION` / `requirements.txt` 溯源），供 Facilities 章节使用。

若某个被委派的技能不可用，留一个 `[DELEGATE: /data-management-plan]` 占位符，而不是把它该产出的东西写一半。

### Phase 3 —— 一致性检查（目标 ↔ 方法 ↔ 预算 ↔ 时间表）

这是拉开差距的一步。交叉核对拼装好的草稿，报告不匹配处：

- **目标 ↔ 方法** —— 每个目标都有一个点名的方法/估计量；不存在不为任何目标服务的孤立方法。
- **方法 ↔ 预算** —— 每条成本都追溯到某个目标（例如 RCT 目标意味着一条受试者激励行；行政数据意味着一条获取/飞地行；大规模模拟意味着一条算力行）。
- **目标 ↔ 时间表** —— 每个目标至少有一个里程碑；没有哪个里程碑是无主的。
- **DMP ↔ 方法** —— 方法里点名的数据与 DMP 里描述的数据一致；机密来源没有被承诺为开放。
- **页数/格式预算** —— 标出可能溢出页数上限的章节 —— 有招标文件时用它自己的上限，否则用画像的（NSF 15 页 Project Description，NIH 1 页 Aims）。有招标文件时，还要确认每个必需章节都在、每条评审标准在某处都有应答，并引用招标文件的页码。

### Phase 4 —— 落地后核验 + 输出

- **落地后（CoVe）：** 若 Background/Significance 引用了既有文献，跑 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 里的 Post-Flight 协议 —— 经 `Agent` 工具在引文上派生 `claim-verifier`（独立上下文，绝不是对话分叉）。呈现 PASS / PARTIAL / FAIL。在 `--no-verify` 或零引文时跳过。
- **写出** 各章节到 `--out`（默认 `quality_reports/grants/YYYY-MM-DD_<slug>/`），每章一个 Markdown 文件，外加 `checklist.md`。

## 输出 / 报告格式

一份 `proposal_draft.md`（各章节拼接）外加一份 `checklist.md`：

```markdown
# Grant Proposal Draft — [Title]
**Funder:** NSF | NIH | ERC | foundation     **Date:** YYYY-MM-DD
**Source spec:** quality_reports/specs/research_spec_<slug>.md
**Call:** <path> (read YYYY-MM-DD) | NOT PROVIDED — structure from the generic <funder> profile

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
Claims extracted: N · Verified: N · Outcome: PASS / PARTIAL / FAIL
```

## 退出行为

- **所有 MUST 槽位已填 + 一致性 PASS：** 报告「DRAFT READY —— 先复核 [CLARIFY:] 各项，再在资助方门户里装配」。
- **存在未决的 [CLARIFY:] / [DELEGATE:] 项或一致性问题：** 报告「INCOMPLETE —— N 项未解决」并列出它们。本技能从不像 `/audit-reproducibility` 那样阻断（它是起草工具，不是门禁）—— 它把问题摆出来，由作者解决。
- **找不到研究规格：** 在 Phase 0 停下并建议 `/interview-me`。什么都不写。

## 参数

| 参数 | 作用 |
|---|---|
| `--funder` | 取值 `nsf` / `nih` / `erc` / `foundation` —— 选择塑造章节结构与要求清单的资助方画像。 |
| `--call` | `<file>` —— 项目的 solicitation / NOFO / RFP（PDF 或纯文本）。它的必需章节、上限与评审标准覆盖通用画像。默认：无 —— 使用通用画像，并在表头说明。 |
| `--input` | `<spec>` —— `/interview-me` 研究规格的路径，用来播种目标与方法。默认：最新的 `quality_reports/specs/research_spec_*.md`；若不存在，停下并建议 `/interview-me`。 |
| `--out` | `<dir>` —— 章节文件的写入目录。默认 `quality_reports/grants/YYYY-MM-DD_<slug>/`（每章一个 Markdown 文件，外加 `checklist.md`）。 |
| `--no-verify` | 跳过 Phase 4 的落地后核验（引文为零时同样跳过）。 |

## 交叉引用

- [`.codebuddy/skills/interview-me/SKILL.md`](../interview-me/SKILL.md) —— 产出本技能所消费的研究规格；若不存在，先跑它。
- [`.codebuddy/skills/data-management-plan/SKILL.md`](../data-management-plan/SKILL.md) —— DMP/DMSP 章节的 Phase 2 委派对象。
- [`.codebuddy/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) —— 设施/计算环境陈述的 Phase 2 委派对象。
- [`.codebuddy/skills/lit-review/SKILL.md`](../lit-review/SKILL.md) —— 提供 Background & Significance 的既有工作框定。
- [`.codebuddy/skills/preregister/SKILL.md`](../preregister/SKILL.md) —— PAP 可以为分析计划播种；预注册是一个受资助项目随后履行的前瞻承诺。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 规定敏感数据来源在 DMP 与预算中如何出现。
- [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) —— Phase 4 的引文事实核查。

## 本技能不做的事

- **向任何地方投稿。** 它写 Markdown + 一份清单；装配并上传到 Research.gov / ASSIST / ERC 门户 / 基金会系统是你的事。
- **发明科学。** 没有规格就没有申请书。它不会捏造识别策略、假设或目标。
- **自己写 DMP 或设施陈述。** 那些委派给 `/data-management-plan` 与 `/capture-environment`；本技能只把它们的产出缝进资助方的章节集合。
- **计算预算。** 它只搭出挂到目标上的条目；实际金额、间接成本率与投入比例是 PI 和资助办公室的事。
- **保证符合页数上限。** 它标出可能的溢出；最终裁到资助方的精确格式是手工活。
