---
name: data-management-plan
description: 复用机密数据和环境留存的现有规则，起草符合资助方要求的数据管理计划，支持 NSF DMP、NIH 2023 年 DMS 政策、ERC 和 Horizon Europe。内容涵盖数据描述、格式/元数据、存储/备份、访问/共享、保存/归档与角色分工。用户说 "data management plan"、"DMP"、"DMSP"、"NIH data sharing plan"、"write the data plan for my grant"、"写数据管理计划" 时，或基金申请书需要数据管理章节时使用。本技能不投稿，只生成草稿，由用户粘贴到资助方门户（DMPTool、NIH ASSIST、Horizon Europe 门户）。
description_zh: 复用机密数据和环境留存的现有规则，起草符合资助方要求的数据管理计划，支持 NSF DMP、NIH 2023 年 DMS 政策、ERC 和 Horizon Europe。内容涵盖数据描述、格式/元数据、存储/备份、访问/共享、保存/归档与角色分工。用户说 "data management plan"、"DMP"、"DMSP"、"NIH data sharing plan"、"write the data plan for my grant"、"写数据管理计划" 时，或基金申请书需要数据管理章节时使用。本技能不投稿，只生成草稿，由用户粘贴到资助方门户（DMPTool、NIH ASSIST、Horizon Europe 门户）。
argument-hint: "[--funder nsf|nih|erc|horizon] [--input <spec-or-proposal>] [--no-verify]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]

---

# `/data-management-plan` —— 符合资助方要求的 DMP 生成器

生成可直接粘贴到资助方门户的数据管理计划。本技能只写正文和结构，**不**向任何平台提交。它复用 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) 的披露规避和 IRB 规则，以及 `/capture-environment` 与 `/replication-package` 的环境和复现包方案，再按资助方要求组织成文档。

## 何时使用

- **撰写基金申请书。** NSF、NIH、ERC、Horizon Europe 申请书分别需要 DMP（NSF）、DMS Plan（NIH 2023 政策）或 Data Management Plan（ERC/Horizon）。`/grant-proposal` 通过读取本 SKILL.md 的 Agent 按本技能撰写该章节；由于本技能只能由用户调用，它是照做，不是被调用。
- **受资助项目开始收集数据前。** 计划记录立项时的承诺，续期时要据此汇报。
- **涉及受限数据或人类受试者数据。** 访问/共享和保存两节会有实质变化，见 Phase 2。

## 何时不要使用

- 需要受 ICMJE / ClinicalTrials.gov 管辖的临床试验数据共享声明时，使用试验申办方模板。
- 不要用 DMP 替代 IRB 方案文本。DMP 只*引用* IRB 约束，不是方案本身。

## 输入

按 shell 引号规则对 `$ARGUMENTS` 分词，再只解析以下三个明确选项，不接受位置参数形式的资助方。含空格的 `--input` 等选项值必须作为单个带引号参数传入，例如 `--input "quality_reports/specs/my study.md"`；解析后，所有路径都必须以加引号的完整路径使用，不得再次分词。未知选项、缺少选项值、重复给出不一致的 `--funder` 或 `--input` 时，停止并报告用法错误，不要猜测：

- `--funder nsf|nih|erc|horizon`：目标资助方画像。省略时，Phase 0 从 `--input` 检测，或询问一次。
- `--input <path>`：研究规格（`/interview-me` 输出，位于 `quality_reports/specs/`）、申请书草稿或近似 `passport` 的描述。本技能从中提取数据类型、样本和识别策略。
- `--no-verify`：跳过 Phase 4 的引文/标准落地后核验，该选项继承自 `/preregister`。

## 工作流

### Phase 0 —— 检测资助方 + 数据敏感度

1. 确定资助方：优先使用 `--funder`，否则从 `--input` 推断，再否则询问一次。载入对应章节 schema：

   | 资助方 | 计划名称 | 必需章节（节选） |
   |---|---|---|
   | **NSF** | Data Management Plan（最多 2 页） | 数据类型 · 标准 · 访问/共享 · 复用/再分发 · 归档 |
   | **NIH** | DMS Plan（2023 政策） | 数据类型 · 工具/软件 · 标准 · 保存/访问/时间表 · 访问/分发 + 复用 · 监督 |
   | **ERC** | DMP（Horizon Europe 附件） | 逐数据集 FAIR · 数据摘要 · 让数据 FAIR · 资源分配 · 安全 · 伦理 |
   | **Horizon Europe** | DMP（DMP 模板） | 与 ERC 相同的 FAIR 优先结构；默认开放，"as open as possible, as closed as necessary" |

2. 从三个维度给数据分类，以驱动 Phase 2–3：
   - **公开**：开放调查、抓取的公开记录、模拟数据，限制最少。
   - **受限**：行政/税务/普查数据、专有数据、按 DUA 授权的数据，重点说明访问程序。
   - **人类受试者**：PII、关联生物样本、带标识符的调查，重点处理 IRB 和披露规避。

   数据属于受限*或*人类受试者时，设置 `sensitive = true` 并运行 Phase 2。纯公开数据的 Phase 2 只需一小段。

### Phase 1 —— 按资助方画像搭出章节

生成六个固定章节，并映射到资助方要求的标题。Phase 1–4 只在内存中维护草稿，不写盘，也不创建供核验器读取的临时文件：

1. **数据描述与类型**：说明数据内容、来源、体量和产出格式。要具体，例如面板/行政微观数据、RCT 结果、事件研究的事件文件、复现中间件 `.rds`/`.dta`/`.parquet`。
2. **格式与元数据标准**：尽量使用开放/非专有格式，`.csv`/`.parquet` 优于 `.dta`；说明码本以及 DDI / Dublin Core / 领域 schema。必须点名标准，不能只写「合适的元数据」。
3. **存储与备份**：说明项目期间如何使用加密的机构存储、3-2-1 备份和代码版本控制；受限原始数据不得放入 git。
4. **访问与共享**：说明谁能访问、何时访问、按什么条件访问。受限数据要写明**受限数据访问程序**，见 Phase 2。
5. **保存与归档**：指定一个仓库和一个持久标识符，见 Phase 3。
6. **角色与职责**：说明 PI 作为数据管家、数据管理员、机构支持和继任安排。

输入没有提供的必填字段，一律写 `[CLARIFY: <specific question>]`，不要编造；这与 `/preregister` 使用同一约定。

### Phase 2 —— 折入披露规避 + IRB 约束（仅当 `sensitive = true`）

从 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) 取出相关规则，写入**访问与共享**和**保存**两节：

- **受限数据要描述访问路径，而不是数据本身。** 说明数据提供方、DUA/受限使用协议，以及复现者如何取得访问，例如 FSRDC 申请、openICPSR 受限访问层级或提供方申请。寄存的是*访问路径*，*不是*数据本身。
- **人类受试者数据要处理 IRB 和最小化。** 引用 IRB 方案编号，缺失时写 `[CLARIFY:]`；说明管辖共享的同意条款和去标识化方案。共享产出必须按同意条款去标识化。
- **任何对外发布的微观数据或表格都要做披露规避。** 点名采用的技术，例如小格抑制（n < 阈值）、四舍五入、顶端截尾、加噪或聚合；表格输出还要说明最小单元格计数规则。实际发布前扫描交给 `/disclosure-check`，并在计划中写明「发布前的产出都要过 `/disclosure-check`」。

### Phase 3 —— 折入计算环境 + 复现包方案

DMP 不仅要承诺寄存数据，还要承诺*可复现性*：

- **环境留存。** 声明会留存计算环境，例如 R `sessionInfo()` / `renv.lock`、Stata 版本 + `.do` 依赖的 ado、Python `requirements.txt` / 容器，并指出 `/capture-environment` 是实现机制。AEA Data Editor / DCAS 标准期望如此。
- **复现包。** 承诺把包含代码、非受限数据、主运行脚本和 README 的复现包寄存到可信仓库，并指出 `/replication-package` 是构建器。
- **仓库选择**要与数据类别匹配：
  - 经济学 / 社会科学 → **openICPSR**（AEA 的主场；符合 DCAS）或 **Harvard Dataverse**。
  - 受限数据 → openICPSR 的*受限访问*层级，或提供方的安全飞地（FSRDC）；寄存代码 + 元数据，不寄存微观数据。
  - 领域仓库 → 按领域（例如 ICPSR 本体、GenBank、代码用 Zenodo），即资助方或社区期望的地方。
- 说明**持久标识符**（DOI）和**时间表**，例如 "at publication" 或 "within 12 months of project end"。NIH 期望不晚于发表或项目结束。

### Phase 4 —— 落地后核验（内存草稿的 CoVe 交接，用 `--no-verify` 跳过）

如果草稿按名称或编号引用资助方政策或标准，例如 "per NIH NOT-OD-21-013"、"DCAS v1"，由调用方从**内存草稿**抽取核验清单。每条包含：断言 ID 与事实断言、一个能由来源确认或反驳的具体核验问题、来源指针（政策/标准 URL，或输入文件路径及章节、页码、段落定位）。

随后通过 `Agent` 工具发起独立调用，设置 `subagent_type=claim-verifier`，只传这份“断言 + 核验问题 + 来源指针”清单。**不要传草稿、草稿路径或整段草稿上下文**，也不要使用会继承草稿的对话分叉。此时草稿尚未写盘，不得虚构一个路径让核验器读取。

核验器对每条断言返回 PASS / PARTIAL / FAIL 和证据。FAIL 时，依据证据在内存中修正受影响章节并重新核验，最多重试 2 次；PARTIAL 和仍无法核验的项目必须明确报告。

核验状态与输出状态必须显式记录，不得省略或用草稿保存成功代替：

- 核验器**报错、超时或返回畸形结果**时，设置 `verification_status=UNVERIFIED`、`output_status=TENTATIVE`，在最终稿和 Post-Flight Verification 块中写明故障；不得声称已经独立核验，也不得输出 `DMP READY`。
- 重试后仍有未解决 FAIL 时，设置 `verification_status=FAIL`、`output_status=TENTATIVE`；仍有 PARTIAL 或无法核验的项目时，输出同样保持 `TENTATIVE`。
- 使用 `--no-verify` 跳过核验时，设置 `verification_status=UNVERIFIED`，输出不得标为 `DMP READY`。

### Phase 5 —— 输出

完成 Phase 4 的独立核验和必要的内存修订后，才用 `Write` 工具把**最终稿**写入 `quality_reports/dmp/YYYY-MM-DD_<funder>_<slug>.md`，并用 `Write` 在旁边创建资助方清单。核验故障或跳过核验时也保留草稿，但必须按 Phase 4 写入 `TENTATIVE` / `UNVERIFIED` 状态；不得把保存草稿误报为核验通过。

```
✓ DMP draft saved: quality_reports/dmp/<file>.md
  Output status: <DMP READY | TENTATIVE | INCOMPLETE>
  Verification status: <PASS | PARTIAL | FAIL | UNVERIFIED>  (or "none to verify")
  Funder: <nsf|nih|erc|horizon>   Data class: <public|restricted|human-subjects>
  Sections: <count> total — <complete> complete, <clarify> with [CLARIFY:] placeholders
  Disclosure/IRB folded in: <yes (Phase 2) | n/a — public data>
  Repository: <openICPSR | Dataverse | domain repo>   PID: <DOI planned | [CLARIFY:]>
  Next: resolve [CLARIFY:] items and any non-PASS verification status, then paste into <DMPTool | NIH ASSIST | Horizon portal>
```

**资助方清单**使用表格，逐项列出必需章节、是否齐备，以及状态为完整还是 `[CLARIFY:]`，让用户一眼判断计划能否通过资助方合规检查。对话中还要附上 **Post-Flight Verification** 块，列出抽取断言数、独立核验数、PASS / PARTIAL / FAIL 结果、已核实证据，以及无法核验或已在最终稿中修正的分歧；跳过核验时明确说明原因。

## 退出行为

- **只有所有必需章节齐备、零 `[CLARIFY:]`，且核验无故障、无未解决 FAIL** → 才允许 "DMP READY"，清单全绿。核验器报错、超时、畸形结果、跳过核验，或仍有 PARTIAL / FAIL 时均不得标为 READY。
- **核验器报错、超时或返回畸形结果** → 必须输出 `Output status: TENTATIVE` 与 `Verification status: UNVERIFIED`，并列出故障原因。
- **有任何必需章节未解决** → "INCOMPLETE — N MUST items unresolved"，在清单里列出。草稿仍然写出（好让用户补），但不标为就绪。
- 本技能**不阻塞**任何流程，只生成文档。真正的门禁在资助方，不在本技能。

## 交叉引用

- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— Phase 2 折入的受限数据 / IRB / 披露规避规则。
- `.codebuddy/skills/disclosure-check/SKILL.md` —— 计划承诺对发布前产出所做的那道披露扫描。
- `.codebuddy/skills/capture-environment/SKILL.md` —— Phase 3 引用的环境留存机制。
- `.codebuddy/skills/replication-package/SKILL.md` —— Phase 3 承诺的那个复现包构建器。
- `.codebuddy/skills/grant-proposal/SKILL.md` —— 为申请书的数据管理一节照着本技能做（通过一个读本 SKILL.md 的 Agent）。
- [`.codebuddy/skills/preregister/SKILL.md`](../preregister/SKILL.md) —— 同类的文档生成器；共享 MUST/`[CLARIFY:]` + 落地后核验两条约定。
- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 寄存的包必须满足的可复现性契约。

## 本技能不做什么

- **不提交计划。** 它只写 Markdown 草稿，由用户粘贴到 DMPTool / NIH ASSIST / Horizon 门户。
- **不运行披露扫描，也不构建复现包。** 它只在计划中*承诺*使用 `/disclosure-check`、`/capture-environment` 和 `/replication-package`，并引用这些技能，不执行它们。
- **不写 IRB 方案。** 它引用方案编号和同意条款，方案需另行撰写。
- **资助方强制指定仓库时，不替你另选。** 如果 NIH 为数据类型指定了领域仓库，该规定优先于 Phase 3 的默认值。本技能会标为 `[CLARIFY:]`，不会猜测。
