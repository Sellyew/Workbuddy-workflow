---
name: humanize
description: 只读检查 `.tex`、`.qmd` 或 `.md` 文稿中的 AI 腔：套话过渡（"Moreover"、"Furthermore"、"It is important to note that"）、AI 陈词（"delve"、"navigate the complexities"、"tapestry"、"robust framework"）、破折号滥用、段落结构过于对称、三段式滥用、模糊限定堆叠、"not only X but also Y" 句式和公式化开篇。只产出报告，不做改写。不用于规避 AI 检测或披露；发表场所要求 AI 使用声明时必须披露，见 `/submission-disclosures`。用户说 "humanize"、"does this sound like AI?"、"check for AI tells"、"de-AI this draft"、"remove AI voice"、"audit my prose for sycophancy"、"这看起来像 AI 写的吗"、"检查 AI 腔" 或 "去 AI 味" 时使用，也可在投稿或发布工作论文前使用。
description_zh: 只读检查 `.tex`、`.qmd` 或 `.md` 文稿中的 AI 腔：套话过渡（"Moreover"、"Furthermore"、"It is important to note that"）、AI 陈词（"delve"、"navigate the complexities"、"tapestry"、"robust framework"）、破折号滥用、段落结构过于对称、三段式滥用、模糊限定堆叠、"not only X but also Y" 句式和公式化开篇。只产出报告，不做改写。不用于规避 AI 检测或披露；发表场所要求 AI 使用声明时必须披露，见 `/submission-disclosures`。用户说 "humanize"、"does this sound like AI?"、"check for AI tells"、"de-AI this draft"、"remove AI voice"、"audit my prose for sycophancy"、"这看起来像 AI 写的吗"、"检查 AI 腔" 或 "去 AI 味" 时使用，也可在投稿或发布工作论文前使用。
argument-hint: "[filename or 'all'] [--severity low|med|high]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/humanize` —— AI 腔审计（只检测、只标记）

读取指定文件或全部论文类文件，检查学术写作中常见的 AI 腔，并生成结构化报告。**本技能不改写文稿，作者要自己修改。**

**合规边界：** 本技能只用于改善可读性，**不用于规避 AI 检测或披露；发表场所要求 AI 使用声明时必须披露**。声明准备见 [`/submission-disclosures`](../submission-disclosures/SKILL.md)。

## 为什么有这个技能

审稿人和编辑越来越容易认出 AI 生成文字。这些标记不是单纯的风格偏好；在 LLM 的训练分布中，它们的出现频率明显高于人类学术写作。投稿前检查有五个理由：

1. **审稿人的怀疑会损害可信度。** 即使研究本身扎实，行文像 AI 草稿也会削弱读者的信任。
2. **期刊政策正在收紧。** 越来越多期刊要求披露 AI 的使用，有些还禁止 AI 起草文字。
3. **AI 腔可能暴露内容问题。** "Moreover"、"It is important to note" 这类套话几乎总是在掩盖尚未想清楚的逻辑。
4. **作者可以保留自己的声音。** 即使大量使用 AI 工具，也能通过手动修改去掉模型常用的措辞。
5. **问题标出来以后容易修改。** 难点在检测；报告列出位置后，删除或改写通常很直接。

## 本技能不是什么

- **不是改写器。** 没有 `--rewrite` 模式。自动改写会引入新的模型特征，也不能改变神经检测器依据的底层统计（见 `writing-with-ai.md`）。作者必须手动编辑，才能保留自己的声音。
- **不做实质审阅。** 论证结构、识别策略和引文问题请交给 `/review-paper`。
- **不是语法检查器。** 语法、错字、版面溢出和引文格式请交给 `/proofread`。
- **不是事实核查器。** 要核验引文和数值论断，请用 `/verify-claims` 做链式核实（Chain-of-Verification）。

`/humanize` 只检查文字声音。它可以与其他技能一起使用，但不能替代其中任何一个。

## 何时使用

- 投稿期刊之前。
- 发布工作论文、预印本或 SSRN 草稿之前。
- 用 AI 协助生成文字之后，例如起草 R&R 答复、归并文献综述或改写摘要。
- 长时间写作后自查。长时间接触 LLM 输出，自己的行文也可能逐渐带上相同模式。

## 何时不要用

- 不要用于 `.bib`、`.R` 或其他非行文文件，这些检测类别面向学术写作。
- 不要用于代码注释，代码注释有不同的标记。
- 不要用于界面或体验文案，它们遵循不同的语言规范。

## 检测类别

humanize-auditor 代理检查以下类别：

### 1. 套话式过渡

以下表达出现在句首，或在段中充当连接语时，是高置信度的 AI 标记：

- `Moreover,` / `Furthermore,` / `Additionally,` / `In addition,`
- `It is important to note that` / `It is worth noting that` / `Notably,`
- `In conclusion,` / `In summary,` / `To summarise,`
- `On the other hand,`（并非对比两个明确对象时）
- `Building on this,` / `Building upon this,`
- `As we can see,` / `As is evident,` / `Indeed,`（叠加出现时）

**严重度：** 每 1000 词超过 1 处为 HIGH；每 2000 词 1 处为 MED；很少出现但确实存在为 LOW。

### 2. AI 陈词词典

与学术写作相比，下列词语和短语在 LLM 输出中出现得过多：

- "navigate the complexities", "navigate the landscape"
- "delve into", "delve deeper into"
- "tapestry of", "rich tapestry"
- "robust framework", "comprehensive framework", "holistic framework"
- "comprehensive approach" / "multifaceted approach" / "nuanced approach"（尤其是叠加出现时）
- "leverage"（在非金融、非工程语境中作动词）
- "in today's [X] landscape" / "in today's rapidly evolving"
- "play a crucial role" / "play a pivotal role" / "play a significant role"
- "shed light on"
- "underscore the importance" / "highlight the importance"
- "It is essential to" / "It is crucial to"

**严重度：** 出现在论文前三页，包括摘要和引言，为 HIGH；其他位置为 MED。

### 3. 破折号与标点滥用

- 单段使用超过 3 个破折号。
- 单段使用三个及以上分号。
- 各段反复使用刻意平行的三项列表和牛津逗号。

**严重度：** MED。破折号本身是正常的写作选择，只有滥用才算标记。

### 4. 对称的段落结构

段落都采用同一种内部结构：主题句 → 三个例子 → 总结句。结构本身没有问题；连续多段重复同一结构，才构成 AI 标记。

**检测：** 在任意三段窗口中，如果每段都符合「主题→例子→总结」的节奏，就标记。

**严重度：** 三段窗口为 MED；连续 5 段及以上为 HIGH。

### 5. 三段式滥用

"X, Y, and Z" 这类三元素列表是正常的修辞手法。以下情况才标记：

- 每页超过 4 处三段式。
- 本来自然只有 2 项或 4 项，却强行写成三项。
- 连续堆叠形容词三段式，例如 "clear, concise, and compelling" 或 "rigorous, robust, and reliable"。

**严重度：** 偶尔出现为 LOW；形成模式为 MED。

### 6. 堆叠模糊限定

一句中连续堆叠表示认知不确定的限定语：

- "might potentially be argued"
- "could possibly suggest"
- "may arguably"
- "perhaps potentially"

**严重度：** HIGH。这类堆叠几乎从来不是作者有意的选择，而是 LLM 在管理不确定性。

### 7. "NOT ONLY X, BUT ALSO Y" 句式

这个句式本身可以正常使用。以下情况属于 AI 标记：

- 全篇超过 2 处。
- X 与 Y 实际并不平行。
- 用它作为段落开头。

**严重度：** MED。

### 8. 公式化开篇

- 章节以 "This [paper / chapter / section / analysis] [does X]." 这类句子开头。
- 段首只是复述本节标题。
- 摘要以 "In this paper, we..." 开篇。某些子领域允许这种写法；在不常见的领域要标记待查，例如 AER 摘要很少这样写。

**严重度：** 除非每节都这样开头，否则为 LOW。

### 9. 连字符过度

长串复合修饰语成为段落的固定特征：

- "data-driven"、"evidence-based"、"well-suited"、"well-established"、"long-standing" 单独使用都没有问题；单段出现三个及以上时标记。

**严重度：** LOW。

### 10. 迎合 / 自我抬举框架

- "This important contribution"
- "This significant finding"
- "Our novel approach"
- 用 "groundbreaking" / "pioneering" 形容自己的引文

**严重度：** HIGH。这些表达像 AI 生成的宣传文案，容易引起审稿人反感。

## 步骤

1. **确定要审计的文件：**
   - 若 `$ARGUMENTS` 以文件名开头，只审计该文件。
   - 若 `$ARGUMENTS` 是 `all`，审计 `Slides/`、`Quarto/`、根目录与 `master_supporting_docs/` 下所有 `.qmd`、`.tex`、`.md` 文件。
   - 跳过 `.bib`、`.R`、`.py`、代码文件，以及 `scripts/` 下的任何文件。

2. **解析 `--severity` 标志**（默认报告全部）。
   - `--severity low` → 报告全部发现。
   - `--severity med` → 不报告 LOW 发现。
   - `--severity high` → 只报告 HIGH 发现。

3. **为每个文件启动 `humanize-auditor` 代理**，并提供这 10 个检测类别。

4. **接收代理返回的结构化报告**。每条发现使用以下格式：

   ```
   line N | category | severity | current text | suggested rewrite or "remove"
   ```

5. **把报告写入** `quality_reports/audits/humanize_<filename>_report.md`。报告包含：
   - 按类别统计 HIGH / MED / LOW 的数量
   - 逐条发现表
   - 总结建议（大致阈值）：
     - **每 1000 词超过 8 条 HIGH 发现**：行文像 AI 草稿。作者应重写受影响的章节，而不是逐个打补丁。
     - **每 1000 词 5–8 条 HIGH**：AI 腔明显。投稿前由作者手动编辑以改善可读性。
     - **每 1000 词少于 5 条 HIGH**：只需轻度清理，主要是表面问题。

6. **向用户汇报摘要：**
   - 每个类别的发现总数
   - 发现最集中的 3 个段落
   - 建议采取的行动：重写或手动编辑以改善可读性

## 配套使用

| 情况 | 做法 |
|---|---|
| 当你借助 AI 起草过行文 | 投稿前运行 `/humanize`，并配合 `/proofread` 检查语法、`/verify-claims` 核验引文。 |
| 当你用自己的语声写作 | 仍可运行 `/humanize`。长期与 AI 协作后，自己的行文也可能带上 LLM 的模式。 |
| 投稿前的审查 | `/review-paper --peer [journal] --variance 3` 检查实质内容，`/humanize` 只改善可读性，`/verify-claims` 核验事实。不得用 `/humanize` 规避 AI 检测或披露；场所要求声明时，必须用 [`/submission-disclosures`](../submission-disclosures/SKILL.md) 准备并披露。 |

## 反模式：没有 `--rewrite` 模式

我们刻意不提供 `/humanize --rewrite`。自动改写不仅可能损害行文，还会引入改写器自身的 AI 标记。正如 [`writing-with-ai.md`](../../rules/writing-with-ai.md) 所记录的，模型改写自己的输出后，检测器看到的仍然是模型输出。只检测和标记可以保留作者的声音，代价是作者要投入时间编辑。

如果你想用自动改写器处理某一段，更合适的做法通常是从头重写这一段，而不是逐个修补标记。

## 输出

- 报告写入 `quality_reports/audits/humanize_<filename>_report.md`（该子目录已 gitignore）。
- 对话中汇报分类计数、发现最集中的段落和建议采取的行动。
- **不修改被审计的文稿。** 用户阅读报告后自行修改。

## 尊重成文的个人语声画像

如果仓库根目录存在 `voice-profile.md`，**先读它**。作者明确保留的习惯，例如频繁使用破折号、第一人称或某个连接词，**不算发现**。把成文的个人偏好报成 AI 标记会造成误报；误报比漏报更容易损害报告的可信度。

用 [`/voice-profile`](../voice-profile/SKILL.md) 创建画像。本技能说明该删什么，那个技能说明该往哪里写。

## 本技能做不到什么（v2.5）

`/humanize` 只找**表面标记**，例如套话过渡、AI 陈词、模糊限定堆叠和对称的段落结构。修正这些问题能提高可读性，无论文字由谁写成都值得做。

**它不能让检测器不再把行文判为机器生成。** 曾有一篇文章经过多轮表面去 AI 化处理，随后交给神经 AI 文本检测器 Pangram，结果仍被判为 **100% AI 写作**。这类检测器依据 LLM 生成文本的 token 级统计特征；模型每次变换产生的仍是 LLM 文本，因此无法靠这种变换改变底层来源。

所以，**一份干净报告只说明行文可读，不说明它读起来像人。** 如果需要确认来源，作者应亲自写承担论证的句子，并使用真实检测器测量。见 [`writing-with-ai.md`](../../rules/writing-with-ai.md)。
