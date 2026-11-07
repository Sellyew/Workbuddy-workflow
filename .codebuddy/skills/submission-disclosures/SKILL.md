---
name: submission-disclosures
description: 为稿件生成投稿所需的声明，包括与目标期刊政策匹配的 AI 使用声明、CRediT 作者贡献角色、利益冲突声明和数据可得性声明。用户说 "AI disclosure"、"disclosure statement"、"do I need to disclose Claude"、"CRediT roles"、"conflict of interest statement"、"data availability statement"、"投稿声明"、"AI 使用披露"、"作者贡献"、"利益冲突" 或 "数据可得性"，或在准备投稿材料包时使用。不负责受限数据输出的统计披露筛查，那是 /disclosure-check。
description_zh: 为稿件生成投稿所需的声明，包括与目标期刊政策匹配的 AI 使用声明、CRediT 作者贡献角色、利益冲突声明和数据可得性声明。用户说 "AI disclosure"、"disclosure statement"、"do I need to disclose Claude"、"CRediT roles"、"conflict of interest statement"、"data availability statement"、"投稿声明"、"AI 使用披露"、"作者贡献"、"利益冲突" 或 "数据可得性"，或在准备投稿材料包时使用。不负责受限数据输出的统计披露筛查，那是 /disclosure-check。
argument-hint: "[manuscript path] [journal short-name, e.g. AER] [--no-ai | --statements-only]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "WebSearch", "WebFetch"]

---

# /submission-disclosures —— 投稿时的声明块

本技能一次起草期刊投稿时要求或强烈建议提供的四段声明：**AI 使用声明**、**CRediT 贡献者角色**、**利益冲突**和**数据可得性**。期刊在 2025–2026 年间收紧了 AI 使用政策。顶刊把未披露 AI 使用视为研究诚信问题，而不只是格式问题，因此作者应认真起草声明，不要等到投稿前才在系统里临时编写。

**本技能处理作者向期刊披露的信息。**它不负责 [`/disclosure-check`](../disclosure-check/SKILL.md) 的工作，后者检查受限数据*输出*是否存在小单元、PII 等统计披露风险。两者名称相近，但边界不同。

## 何时使用

- 准备投稿或重投材料包，而投稿系统要求 AI 使用／COI／数据可得性声明。
- 向原投稿后才采纳 AI 政策的期刊修改重投。
- 合作者询问是否需要说明本研究使用了 Claude/Copilot/ChatGPT。

## 阶段

### 阶段 1 —— 弄清期刊的实际政策

1. 若给了期刊简称，先读 [`journal-profiles.md`](../../references/journal-profiles.md) 中对应画像（Top-5 经济学期刊 + AEA 系政策说明 + 政治学前三）。
2. **在期刊官网核实当前政策。**用 `WebSearch`/`WebFetch` 检索 "<journal> artificial intelligence policy authors" 和该刊投稿指南。政策在 2025–2026 年间变化很快，缓存或记忆中的政策不足以支撑投稿。把 URL 与检索日期写进产出。
3. 若期刊没有明确的 AI 政策，默认采用最严格的共同底线：披露工具、使用范围和人的责任。多披露不增加成本，少披露可能付出代价。

### 阶段 2 —— 盘点实际用了什么

通过简短访谈盘点实际使用情况；情况明显时，也可从 `quality_reports/`、会话日志或 CODEBUDDY.md 等仓库记录推断：

- **使用了哪些工具**（WorkBuddy、Copilot、ChatGPT、Grammarly 等），分别用于什么：写／改散文、写代码、审代码、文献检索、数据分析、翻译。
- **哪些工作由人完成**：研究设计、识别策略选择、解释，以及对每个数字与引文的最终核验。若属实，可结合本仓库的 `/audit-reproducibility`、`/verify-claims` 核验记录明确写出，例如「所有经 AI 辅助的数字都已对照代码独立核验」。这是在说明核验工作，不是在认罪。
- **AI 没有用于什么**，尤其是期刊关注的事项。例如，多数政策禁止把 AI 列为作者，也禁止未披露的 AI 生成图像／数据。

### 阶段 3 —— 起草四段声明

写 `quality_reports/submission_disclosures_[manuscript-slug].md`，包含：

1. **AI 使用声明**：按期刊政策写明工具 + 版本、使用范围，以及「作者对全部内容承担全部责任、并已核验所有 AI 辅助产出」。措辞必须诚实具体；仓库日志已经记录 AI 使用时，绝不能套用「未使用任何 AI」之类的相反说法。
2. **CRediT 角色**：通过访谈把 14 个角色分配给每位作者，并标出无人承担的角色。
3. **利益冲突**：说明资金来源、有偿／无偿职位和数据提供方关系。IRB／数据使用协议常会限定必须声明的内容，需交叉参考 [`confidential-data.md`](../../rules/confidential-data.md)。
4. **数据可得性**：与复现存档保持一致。目标是 AEA 系期刊时，使用 openICPSR/DCAS 的措辞；存档由 [`/replication-package`](../replication-package/SKILL.md) 构建，受限数据的获取措辞依 [`confidential-data.md`](../../rules/confidential-data.md)。

使用 `--statements-only` 时，只在对话中输出声明，不写文件。使用 `--no-ai` 时，跳过第 1 段声明，即用户断言未使用 AI 协助；对话中要注明，仓库会话日志若明显相反，两者可能存在矛盾。

### 阶段 4 —— 与稿件做一致性核对

在稿件中搜索已有的致谢／披露小节，标出矛盾。例如，论文感谢了某位「研究助理」，COI 却未提及；或者已有 AI 声明与新声明不一致。**不要**悄悄覆盖原内容，应把差异交给作者处理。

## 退出行为

- **声明已起草、政策已核实：**写文件，打印四段声明 + 政策 URL／日期，并提醒用户这些只是供*作者*审阅的草稿，最终签核由作者完成。
- **期刊政策无法核实**（站点打不开、找不到政策）：输出严格默认版声明，明确标注「默认措辞——投稿前请对照该刊当前的作者指南核实」。
- **盘点结果与 `--no-ai` 矛盾：**停下并说明矛盾，绝不生成虚假的「未使用 AI」声明。

## 参数

- `--no-ai` —— 跳过 AI 使用声明（用户断言未使用）。若仓库证据明显与该断言矛盾，技能仍会警告。
- `--statements-only` —— 把声明打印到对话；不写文件。

## 交叉引用

- [`.codebuddy/skills/disclosure-check/SKILL.md`](../disclosure-check/SKILL.md) —— 受限数据输出的统计披露筛查，与作者向期刊披露是两件事。
- [`.codebuddy/skills/replication-package/SKILL.md`](../replication-package/SKILL.md) —— 构建数据可得性声明必须与之匹配的存档。
- [`.codebuddy/references/journal-profiles.md`](../../references/journal-profiles.md) —— 逐刊校准，含 AEA 的 DCAS 政策说明。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 受限数据对声明内容的约束。
- [`.codebuddy/skills/humanize/SKILL.md`](../humanize/SKILL.md) —— 检测散文里的 AI 腔；披露与文风是两项独立义务。

## 本技能不做什么

- **不筛查输出的统计披露风险**，那是 [`/disclosure-check`](../disclosure-check/SKILL.md)。
- **不构建复现存档**，那是 [`/replication-package`](../replication-package/SKILL.md)；本技能只写指向存档的声明。
- **不替作者作伦理判断。**它根据作者报告和仓库记录起草诚实声明。含糊政策下某次使用是否*必须*披露，由作者判断；拿不准时，本技能默认披露。
- **不提交任何材料。**用户亲自把声明放入投稿材料包。
