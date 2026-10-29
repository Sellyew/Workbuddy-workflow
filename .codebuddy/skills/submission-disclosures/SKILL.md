---
name: submission-disclosures
description: 为稿件生成投稿时的那块声明——与目标期刊政策相匹配的 AI 使用声明、CRediT 作者贡献角色、利益冲突声明，以及数据可得性声明。用户说 "AI disclosure"、"disclosure statement"、"do I need to disclose Claude"、"CRediT roles"、"conflict of interest statement"、"data availability statement" 时使用，或在准备投稿材料包时使用。不负责受限数据输出的统计披露筛查——那是 /disclosure-check。
description_zh: 为稿件生成投稿时的那块声明——与目标期刊政策相匹配的 AI 使用声明、CRediT 作者贡献角色、利益冲突声明，以及数据可得性声明。用户说 "AI disclosure"、"disclosure statement"、"do I need to disclose Claude"、"CRediT roles"、"conflict of interest statement"、"data availability statement" 时使用，或在准备投稿材料包时使用。不负责受限数据输出的统计披露筛查——那是 /disclosure-check。
argument-hint: "[manuscript path] [journal short-name, e.g. AER] [--no-ai | --statements-only]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "WebSearch", "WebFetch"]

---

# /submission-disclosures —— 投稿时的声明块

一次起草期刊如今在投稿时要求（或强烈期待）的四段声明：**AI 使用声明**、**CRediT 贡献者角色**、**利益冲突**、**数据可得性**。期刊在 2025–2026 年间收紧了 AI 使用政策；在顶刊被查出未披露 AI，现在是研究诚信问题，而不是格式问题——所以这段声明应当*刻意*起草，而不是午夜在投稿系统里现编。

**本技能讲的是作者对期刊的披露。**它与 [`/disclosure-check`](../disclosure-check/SKILL.md) 无关，后者筛查受限数据的*输出*是否存在统计披露风险（小单元、PII）。同一个词，两个世界。

## 何时使用

- 正在准备投稿或重投材料包，而投稿系统要求 AI 使用／COI／数据可得性声明。
- 在一个自原投稿之后才采纳 AI 政策的期刊上做修改重投。
- 合作者问「我们需不需要说明在这篇上用了 Claude/Copilot/ChatGPT？」

## 阶段

### 阶段 1 —— 弄清期刊的实际政策

1. 若给了期刊简称，读它在 [`journal-profiles.md`](../../references/journal-profiles.md) 里的画像（Top-5 经济学期刊 + AEA 系政策说明 + 政治学前三）。
2. **在期刊自己的网站上核实当前政策**（`WebSearch`/`WebFetch`："<journal> artificial intelligence policy authors"、该刊的投稿指南页）。政策在 2025–2026 年间动得很快；一份缓存过的或凭记忆的政策不足以支撑一次投稿。把 URL 与检索日期记进产出。
3. 若不存在明确的 AI 政策，默认采用最严的共同底线（披露工具、使用范围、人的责任）——多披露不花钱；少披露要付代价。

### 阶段 2 —— 盘点实际用了什么

简短访谈（或在显而易见时从仓库推断——例如 `quality_reports/`、会话日志、一份 CODEBUDDY.md）：

- **哪些工具**（WorkBuddy、Copilot、ChatGPT、Grammarly 一类）以及**用来做什么**：写／改散文、写代码、审代码、文献检索、数据分析、翻译。
- **什么留给了人**：研究设计、识别策略的选择、解释、对每一个数字与引文的最终核验（在属实时，与本仓库自己的核验叙事挂钩——`/audit-reproducibility`、`/verify-claims`——*说出来*：「所有经 AI 辅助的数字都已对照代码独立核验」是长处，不是认罪）。
- **AI 没有用于什么**——在期刊在意的地方（例如多数政策禁止把 AI 列为作者，禁止未披露的 AI 生成图像／数据）。

### 阶段 3 —— 起草四段声明

写 `quality_reports/submission_disclosures_[manuscript-slug].md`，包含：

1. **AI 使用声明**——与期刊匹配的措辞：工具 + 版本、使用范围、以及「作者对全部内容承担全部责任、并已核验所有 AI 辅助产出」这句确认。诚实而具体；绝不要写成在仓库自己的日志已经说了别的时候还去过度声称（「未使用任何 AI」）的套话。
2. **CRediT 角色**——把 14 个角色的分类法映射到每位作者（就此做访谈；标出没有作者承担的角色）。
3. **利益冲突**——资金来源、有偿／无偿职位、数据提供方关系（IRB／数据使用协议常常限定必须声明什么；交叉参考 [`confidential-data.md`](../../rules/confidential-data.md)）。
4. **数据可得性**——与复现存档对齐：当目标是 AEA 系期刊时用 openICPSR/DCAS 的措辞（存档本身交给 [`/replication-package`](../replication-package/SKILL.md)；受限数据的获取措辞依 [`confidential-data.md`](../../rules/confidential-data.md)）。

用 `--statements-only` 时，把声明输出到对话里而不写文件。用 `--no-ai` 时，跳过第 1 段声明（用户断言未使用 AI 协助——在对话里注明：若仓库自己的会话日志明显与之矛盾，它们可能矛盾）。

### 阶段 4 —— 与稿件做一致性核对

在稿件里 grep 是否已有致谢／披露小节；标出矛盾（例如论文感谢了某位「研究助理」，而 COI 里没提；或已有一段 AI 声明与新写的这段相互矛盾）。**不要**悄悄覆盖——把差异摆出来。

## 退出行为

- **声明已起草、政策已核实：**写文件，打印四段声明 + 政策 URL／日期，并提醒用户这些声明是供*作者*审阅的草稿——签核是他们的。
- **期刊政策无法核实**（站点打不开、找不到政策）：输出严格默认版的声明，明确标注「默认措辞——投稿前请对照该刊当前的作者指南核实」。
- **盘点结果与 `--no-ai` 矛盾：**停下并摆出矛盾；绝不产出一段虚假的「未使用 AI」声明。

## 参数

- `--no-ai` —— 跳过 AI 使用声明（用户断言未使用）。若仓库证据明显与该断言矛盾，技能仍会警告。
- `--statements-only` —— 把声明打印到对话；不写文件。

## 交叉引用

- [`.codebuddy/skills/disclosure-check/SKILL.md`](../disclosure-check/SKILL.md) —— 受限数据输出的统计披露筛查（另一个「披露」；互不相关）。
- [`.codebuddy/skills/replication-package/SKILL.md`](../replication-package/SKILL.md) —— 数据可得性声明必须与之匹配的那份存档。
- [`.codebuddy/references/journal-profiles.md`](../../references/journal-profiles.md) —— 逐刊校准，含 AEA 的 DCAS 政策说明。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 受限数据对声明能说什么的约束。
- [`.codebuddy/skills/humanize/SKILL.md`](../humanize/SKILL.md) —— 检测散文里的 AI 腔；披露与文风是两项分开的义务。

## 本技能不做什么

- **不筛查输出的统计披露风险**——那是 [`/disclosure-check`](../disclosure-check/SKILL.md)。
- **不构建复现存档**——那是 [`/replication-package`](../replication-package/SKILL.md)；本技能只写指向它的那段声明。
- **不替你决定伦理。**它依据你报告的内容与仓库显示的内容起草诚实的声明；某次使用在一份含糊政策下是否*需要*披露，是作者的判断——拿不准时本技能默认披露。
- **不提交任何东西。**声明由用户亲手放进用户的投稿材料包。
