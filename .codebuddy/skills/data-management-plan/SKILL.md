---
name: data-management-plan
description: 通过组合机密数据与环境留存的既有原语，起草一份符合资助方要求的数据管理计划（NSF DMP、NIH 2023 年 DMS 政策、ERC、Horizon Europe）。章节覆盖数据描述、格式/元数据、存储/备份、访问/共享、保存/归档与角色分工。用户说 "data management plan"、"DMP"、"DMSP"、"NIH data sharing plan"、"write the data plan for my grant"，或基金申请书需要数据管理一节时使用。不是投稿工具 —— 产出的是草稿，由用户粘贴进资助方门户（DMPTool、NIH ASSIST、Horizon Europe 门户）。
description_zh: 通过组合机密数据与环境留存的既有原语，起草一份符合资助方要求的数据管理计划（NSF DMP、NIH 2023 年 DMS 政策、ERC、Horizon Europe）。章节覆盖数据描述、格式/元数据、存储/备份、访问/共享、保存/归档与角色分工。用户说 "data management plan"、"DMP"、"DMSP"、"NIH data sharing plan"、"write the data plan for my grant"，或基金申请书需要数据管理一节时使用。不是投稿工具 —— 产出的是草稿，由用户粘贴进资助方门户（DMPTool、NIH ASSIST、Horizon Europe 门户）。
argument-hint: "[--funder nsf|nih|erc|horizon] [--input <spec-or-proposal>] [--no-verify]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]

---

# `/data-management-plan` —— 符合资助方要求的 DMP 生成器

产出一份可直接粘进资助方门户的数据管理计划。本技能只写正文与结构；它**不**向任何地方提交。它是一个**组合**技能 —— 把 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) 里的披露规避 / IRB 规则，以及 `/capture-environment` 与 `/replication-package` 的环境 + 复现包方案，折进一份贴合资助方形态的文档。

## 何时使用

- **写基金申请书时。** 每一份 NSF、NIH、ERC、Horizon Europe 申请书都需要 DMP（NSF）、DMS Plan（NIH 2023 政策）或 Data Management Plan（ERC/Horizon）。`/grant-proposal` 通过一个读本 SKILL.md 的 Agent 照着本技能写那一节（本技能只能由用户调用，所以是照着做，不是被调用）。
- **受资助项目的数据收集之前。** 这份计划是你在立项时作出的承诺，在续期时对照它汇报。
- **涉及受限数据或人类受试者数据时。** 访问/共享与保存两节会有实质变化 —— 见 Phase 2。

## 何时不要使用

- 需要受 ICMJE / ClinicalTrials.gov 管辖的临床试验数据共享声明 —— 用试验申办方的模板。
- 用来替代 IRB 方案文本 —— DMP *引用* IRB 约束；它不是方案本身。

## 输入

- `--funder` `nsf|nih|erc|horizon` —— 目标资助方画像（位置参数 `$0`）。省略时，Phase 0 从 `--input` 检测，或问一次。
- `--input <path>` —— 一份研究规格（`/interview-me` 输出，位于 `quality_reports/specs/` 下）、一份申请书草稿，或一段近似 `passport` 的描述。本技能从中提取数据类型、样本与识别策略。
- `--no-verify` —— 跳过 Phase 4 的引文/标准落地后核验（继承自 `/preregister`）。

## 工作流

### Phase 0 —— 检测资助方 + 数据敏感度

1. 确定资助方（`--funder`，否则从 `--input` 推断，否则问一次）。载入它的章节 schema：

   | 资助方 | 计划名称 | 必需章节（节选） |
   |---|---|---|
   | **NSF** | Data Management Plan（最多 2 页） | 数据类型 · 标准 · 访问/共享 · 复用/再分发 · 归档 |
   | **NIH** | DMS Plan（2023 政策） | 数据类型 · 工具/软件 · 标准 · 保存/访问/时间表 · 访问/分发 + 复用 · 监督 |
   | **ERC** | DMP（Horizon Europe 附件） | 逐数据集 FAIR · 数据摘要 · 让数据 FAIR · 资源分配 · 安全 · 伦理 |
   | **Horizon Europe** | DMP（DMP 模板） | 与 ERC 相同的 FAIR 优先结构；默认开放，"as open as possible, as closed as necessary" |

2. 从三个轴给数据分类（驱动 Phase 2–3）：
   - **公开**（开放调查、抓取的公开记录、模拟数据）—— 限制最少。
   - **受限**（行政/税务/普查数据、专有数据、按 DUA 授权的数据）—— 访问程序为主。
   - **人类受试者**（PII、关联生物样本、带标识符的调查）—— IRB + 披露规避为主。

   若数据属于受限*或*人类受试者，置 `sensitive = true` 并跑 Phase 2。若纯属公开，Phase 2 就是一小段。

### Phase 1 —— 按资助方画像搭出章节

生成六个固定章节，映射到资助方要求的标题：

1. **数据描述与类型** —— 什么数据、来源、体量、产出格式。要具体：面板/行政微观数据、RCT 结果、事件研究的事件文件、复现中间件 `.rds`/`.dta`/`.parquet`。
2. **格式与元数据标准** —— 尽量用开放/非专有格式（`.csv`/`.parquet` 优于 `.dta`；码本；DDI / Dublin Core / 领域 schema）。点名标准，不要说「合适的元数据」。
3. **存储与备份** —— 项目期间：加密的机构存储、3-2-1 备份、代码版本控制（不把受限原始数据放进 git）。
4. **访问与共享** —— 谁能访问、何时、以什么条件。受限数据下这就是**受限数据访问程序**（见 Phase 2）。
5. **保存与归档** —— 一个具名仓库加一个持久标识符（见 Phase 3）。
6. **角色与职责** —— PI 作为数据管家、数据管理员、机构支持、继任安排。

对输入没有提供的任何必填字段，写 `[CLARIFY: <specific question>]` 而不是编造 —— 与 `/preregister` 同一约定。

### Phase 2 —— 折入披露规避 + IRB 约束（仅当 `sensitive = true`）

从 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) 取出相关规则，织进**访问与共享**和**保存**两节：

- **受限数据 → 描述访问路径，而不是数据本身。** 说明数据提供方、DUA/受限使用协议，以及复现者如何取得访问（例如 FSRDC 申请、openICPSR 受限访问层级、提供方申请）。数据本身*不*寄存；寄存的是*通往它的路径*。
- **人类受试者 → IRB + 最小化。** 引用 IRB 方案编号（或写 `[CLARIFY:]`）、管辖共享的同意条款，以及去标识化方案。共享的产出按同意条款去标识化。
- **任何对外发布的微观数据或表格都要做披露规避。** 点名技术：小格抑制（n < 阈值）、四舍五入、顶端截尾、加噪，或聚合。对表格输出，说明最小单元格计数规则。把实际的发布前扫描交给 `/disclosure-check`，并在计划里写明（「发布前的产出都要过 `/disclosure-check`」）。

### Phase 3 —— 折入计算环境 + 复现包方案

DMP 应当承诺*可复现性*，而不只是数据寄存：

- **环境留存。** 声明计算环境会被留存（R `sessionInfo()` / `renv.lock`、Stata 版本 + `.do` 依赖的 ado、Python `requirements.txt` / 容器）。指出 `/capture-environment` 作为机制。AEA Data Editor / DCAS 标准期望如此。
- **复现包。** 承诺把一个复现包（代码 + 非受限数据 + 主运行脚本 + README）寄存到可信仓库。指出 `/replication-package` 作为构建器。
- **仓库选择** —— 与数据类别相配：
  - 经济学 / 社会科学 → **openICPSR**（AEA 的主场；符合 DCAS）或 **Harvard Dataverse**。
  - 受限数据 → openICPSR 的*受限访问*层级，或提供方的安全飞地（FSRDC）；寄存代码 + 元数据，不寄存微观数据。
  - 领域仓库 → 按领域（例如 ICPSR 本体、GenBank、代码用 Zenodo），即资助方或社区期望的地方。
- 说明**持久标识符**（DOI）与**时间表**（例如 "at publication" 或 "within 12 months of project end" —— NIH 期望不晚于发表或项目结束）。

### Phase 4 —— 落地后核验（用 `--no-verify` 跳过）

若草稿按名称/编号引用了某条资助方政策或标准（例如 "per NIH NOT-OD-21-013"、"DCAS v1"），通过 `Agent` 工具调用 `/verify-claims`，确认这条政策引用确实存在。分叉出去的 `claim-verifier` 看不到草稿。把任何 FAIL/PARTIAL 摆出来。

### Phase 5 —— 输出

把草稿写到 `quality_reports/dmp/YYYY-MM-DD_<funder>_<slug>.md`，并在旁边写一份资助方清单。

```
✓ DMP draft saved: quality_reports/dmp/<file>.md
  Funder: <nsf|nih|erc|horizon>   Data class: <public|restricted|human-subjects>
  Sections: <count> total — <complete> complete, <clarify> with [CLARIFY:] placeholders
  Disclosure/IRB folded in: <yes (Phase 2) | n/a — public data>
  Repository: <openICPSR | Dataverse | domain repo>   PID: <DOI planned | [CLARIFY:]>
  Policy citations verified: <PASS>/<PARTIAL>/<FAIL>  (or "none to verify")
  Next: resolve [CLARIFY:] items, then paste into <DMPTool | NIH ASSIST | Horizon portal>
```

**资助方清单**是一张表：每个必需章节 → 是否齐备？→ 完整 / `[CLARIFY:]`，让用户一眼看出这份计划能否通过资助方的合规检查。

## 退出行为

- **所有必需章节齐备，零 `[CLARIFY:]`** → "DMP READY"，清单全绿。
- **有任何必需章节未解决** → "INCOMPLETE — N MUST items unresolved"，在清单里列出。草稿仍然写出（好让用户补），但不标为就绪。
- 本技能**不阻塞**任何东西 —— 它产出一份文档。门禁在资助方那边，不在我们这边。

## 交叉引用

- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— Phase 2 折入的受限数据 / IRB / 披露规避规则。
- `.codebuddy/skills/disclosure-check/SKILL.md` —— 计划承诺对发布前产出所做的那道披露扫描。
- `.codebuddy/skills/capture-environment/SKILL.md` —— Phase 3 引用的环境留存机制。
- `.codebuddy/skills/replication-package/SKILL.md` —— Phase 3 承诺的那个复现包构建器。
- `.codebuddy/skills/grant-proposal/SKILL.md` —— 为申请书的数据管理一节照着本技能做（通过一个读本 SKILL.md 的 Agent）。
- [`.codebuddy/skills/preregister/SKILL.md`](../preregister/SKILL.md) —— 同类的文档生成器；共享 MUST/`[CLARIFY:]` + 落地后核验两条约定。
- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 寄存的包必须满足的可复现性契约。

## 本技能不做什么

- **提交计划。** 它写一份 Markdown 草稿；用户把它粘进 DMPTool / NIH ASSIST / Horizon 门户。
- **跑披露扫描或构建复现包。** 它把项目*承诺*给 `/disclosure-check`、`/capture-environment` 与 `/replication-package`，并引用它们 —— 但不执行它们。
- **写 IRB 方案。** 它引用方案编号与同意条款；方案是另行撰写的。
- **在资助方强制指定时替你选仓库。** 若 NIH 为你的数据类型点名了某个领域仓库，那条强制规定优先于 Phase 3 的默认值 —— 本技能把它标成 `[CLARIFY:]`，而不是猜。
