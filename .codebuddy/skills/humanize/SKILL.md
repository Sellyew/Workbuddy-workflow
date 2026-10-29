---
name: humanize
description: 对 `.tex`、`.qmd` 或 `.md` 文本做只读的 AI 腔审计 —— 套话式过渡（"Moreover"、"Furthermore"、"It is important to note that"）、AI 陈词词典（"delve"、"navigate the complexities"、"tapestry"、"robust framework"）、破折号滥用、对称的段落结构、三段式滥用、堆叠的模糊限定、"not only X but also Y" 句式、以及公式化开篇。产出报告；不做改写。用户说 "humanize"、"does this sound like AI?"、"check for AI tells"、"de-AI this draft"、"remove AI voice"、"audit my prose for sycophancy" 时使用，或在投稿前 / 发布工作论文前使用。
description_zh: 对 `.tex`、`.qmd` 或 `.md` 文本做只读的 AI 腔审计 —— 套话式过渡（"Moreover"、"Furthermore"、"It is important to note that"）、AI 陈词词典（"delve"、"navigate the complexities"、"tapestry"、"robust framework"）、破折号滥用、对称的段落结构、三段式滥用、堆叠的模糊限定、"not only X but also Y" 句式、以及公式化开篇。产出报告；不做改写。用户说 "humanize"、"does this sound like AI?"、"check for AI tells"、"de-AI this draft"、"remove AI voice"、"audit my prose for sycophancy" 时使用，或在投稿前 / 发布工作论文前使用。
argument-hint: "[filename or 'all'] [--severity low|med|high]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Agent", "Task"]
disallowed-tools: ["Edit", "MultiEdit"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/humanize` —— AI 腔审计（只检测、只标记）

读取目标文件（或全部类论文文件），按学术行文里公认的 AI 腔标记做审计，并写一份结构化报告。**本技能不做改写。** 由作者自己动手改。

## 为什么有这个技能

审稿人和编辑越来越能认出 AI 生成的文字。这些标记不是风格偏好 —— 它们是 LLM 训练分布产出频率显著高于人类学术作者的统计特征。投稿前审计的五个理由：

1. **审稿人的怀疑是一笔税。** 哪怕实质很好，只要行文读起来像 AI 草拟，就得付一笔可信度税。
2. **期刊政策在收紧。** 越来越多的刊物要求披露，或禁止 AI 草拟的文字。
3. **AI 标记暗示内容虚弱。** 套话式过渡（"Moreover"、"It is important to note"）几乎总是在遮盖作者没想透的逻辑缺口。
4. **你不是那些标记。** 即便重度使用 AI 工具的作者，也能靠剥掉模型的词汇指纹来保住自己的语声。
5. **一旦看得见，修起来很便宜。** 成本在检测，不在改写 —— 报告一旦标出这些标记，清除是机械劳动。

## 本技能不是什么

- **不是改写器。** 没有 `--rewrite` 模式。自动改写器会引入它自己的标记，也无法改变神经检测器看到的东西（见 `writing-with-ai.md`）；作者靠手工编辑来保住自己的语声。
- **不是实质审阅者。** 论证结构、识别策略、引文，请用 `/review-paper`。
- **不是语法检查器。** 语法、错字、版面溢出、引文格式，请用 `/proofread`。
- **不是事实核查器。** 引文与数值论断的链式核实（Chain-of-Verification），请用 `/verify-claims`。

`/humanize` 是*语声*这一路透镜。和其他几路一起跑 —— 它们谁也替代不了谁。

## 何时使用

- 投稿期刊之前。
- 发布工作论文 / 预印本 / SSRN 草稿之前。
- 任何借助 AI 生成过行文之后（R&R 答复草稿、文献综述归并、摘要改写）。
- 长时间写作之后作为一次自我纪律 —— 整天盯着 LLM 输出，你自己的行文也会向 LLM 的模式漂移。

## 何时不要用

- 用在 `.bib`、`.R` 或其他非行文文件上 —— 这些检测器是为学术行文调的。
- 用在代码注释上 —— 那里的标记不一样。
- 用在界面/体验文案上 —— 语声规范不同。

## 检测类别

humanize-auditor 代理检查以下几组类别：

### 1. 套话式过渡

在句首或段中以连接组织身份出现时，属于高置信度的 AI 标记：

- `Moreover,` / `Furthermore,` / `Additionally,` / `In addition,`
- `It is important to note that` / `It is worth noting that` / `Notably,`
- `In conclusion,` / `In summary,` / `To summarise,`
- `On the other hand,`（当并不是在对比两件具名事物时）
- `Building on this,` / `Building upon this,`
- `As we can see,` / `As is evident,` / `Indeed,`（叠加出现）

**严重度：** 超过每 1000 词 1 处即为 HIGH。每 2000 词 1 处为 MED。罕见但确实存在为 LOW。

### 2. AI 陈词词典

相对学术行文而言，在 LLM 输出中统计上过度出现的词与短语：

- "navigate the complexities", "navigate the landscape"
- "delve into", "delve deeper into"
- "tapestry of", "rich tapestry"
- "robust framework", "comprehensive framework", "holistic framework"
- "comprehensive approach" / "multifaceted approach" / "nuanced approach"（尤其是叠加出现时）
- "leverage"（在非金融 / 非工程语境里作动词）
- "in today's [X] landscape" / "in today's rapidly evolving"
- "play a crucial role" / "play a pivotal role" / "play a significant role"
- "shed light on"
- "underscore the importance" / "highlight the importance"
- "It is essential to" / "It is crucial to"

**严重度：** 出现在论文前三页（摘要、引言）为 HIGH。其他位置为 MED。

### 3. 破折号与标点滥用

- 破折号滥用 —— 单段超过 3 个破折号即为标记。
- 分号堆叠 —— 单段三个及以上分号。
- 三重牛津逗号结构 —— 段段重复、刻意平行排列的三项列表。

**严重度：** MED。破折号是正当的作者选择；标记的是滥用，不是所有使用。

### 4. 对称的段落结构

段落具有相同的微架构：主题句 → 三个例子 → 一句总结。真正构成 AI 标记的是这种结构在连续段落中重复 —— 而不是结构本身。

**检测：** 任何三段窗口，若每段都符合「主题→例子→总结」的节奏，就标记。

**严重度：** 三段窗口为 MED；连续 5 段以上为 HIGH。

### 5. 三段式滥用

"X, Y, and Z" 这类三元素列表是正当的修辞手法。构成标记的是：

- 每页超过 4 处三段式。
- 用在本来自然是 2 项或 4 项的地方。
- 形容词三段式叠加（"clear, concise, and compelling"；"rigorous, robust, and reliable"）。

**严重度：** 罕见为 LOW；成模式为 MED。

### 6. 堆叠模糊限定

单句中堆叠认识论上的模糊限定：

- "might potentially be argued"
- "could possibly suggest"
- "may arguably"
- "perhaps potentially"

**严重度：** HIGH —— 这些几乎从来不是作者的选择；那是 LLM 的不确定性管理。

### 7. "NOT ONLY X, BUT ALSO Y" 句式

节制使用是正当的句式。AI 标记是：

- 全篇超过 2 处。
- 用在 X 与 Y 其实并不平行的时候。
- 用作段落开头。

**严重度：** MED。

### 8. 公式化开篇

- 形如 "This [paper / chapter / section / analysis] [does X]." 的章节开头。
- 复述节标题的段落开头。
- 摘要以 "In this paper, we..." 开篇（在某些子领域是正当的；在不典型的领域要标记待查，例如 AER 摘要很少这么写）。

**严重度：** 除非每一节都这样开头，否则为 LOW。

### 9. 连字符过度

长串复合修饰语成为段落签名：

- "data-driven"、"evidence-based"、"well-suited"、"well-established"、"long-standing" —— 单个都没问题；若单段出现三个及以上则标记。

**严重度：** LOW。

### 10. 迎合 / 自我抬举框架

- "This important contribution"
- "This significant finding"
- "Our novel approach"
- 把自引说成 "groundbreaking" / "pioneering"

**严重度：** HIGH —— 这些读起来像 AI 生成的宣传文案；审稿人反应会很差。

## 步骤

1. **确定要审计的文件：**
   - 若 `$ARGUMENTS` 以文件名开头：只审计该文件。
   - 若 `$ARGUMENTS` 是 `all`：审计 `Slides/`、`Quarto/`、根目录与 `master_supporting_docs/` 下所有 `.qmd`、`.tex`、`.md` 文件。
   - 跳过 `.bib`、`.R`、`.py`、代码文件，以及 `scripts/` 下的任何文件。

2. **解析 `--severity` 标志**（默认：报告全部）。
   - `--severity low` → 报告全部发现。
   - `--severity med` → 抑制 LOW 发现。
   - `--severity high` → 仅报告 HIGH 发现。

3. **对每个文件启动 `humanize-auditor` 代理**，带上这 10 个检测类别。

4. **接收代理返回的结构化报告**。每条发现的格式：

   ```
   line N | category | severity | current text | suggested rewrite or "remove"
   ```

5. **写报告**到 `quality_reports/audits/humanize_<filename>_report.md`。内容包含：
   - 按类别计数（HIGH / MED / LOW）
   - 逐条发现表
   - 总结建议（大致阈值）：
     - **每 1000 词超过 8 条 HIGH 发现**：行文读起来像 AI 草拟。作者应重写受影响的各节，而不是打补丁。
     - **每 1000 词 5–8 条 HIGH**：明显的 AI 语声。投稿前把标记清掉。
     - **每 1000 词少于 5 条 HIGH**：轻度清理；基本是外观问题。

6. **向用户汇报摘要：**
   - 每个类别的发现总数
   - 最集中的段落（前 3 处）
   - 行动建议（重写 vs. 清标记 vs. 外观修补）

## 配套使用

| 情况 | 做法 |
|---|---|
| 当你借助 AI 起草过行文 | 投稿前跑 `/humanize`。与 `/proofread`（语法）和 `/verify-claims`（引文）配合。 |
| 当你用自己的语声写作 | 照样跑 `/humanize` —— 长时间与 AI 协作之后，你自己的行文也会向 LLM 的模式漂移。 |
| 投稿前的审查 | `/review-paper --peer [journal] --variance 3` 管实质，`/humanize` 管语声，`/verify-claims` 管事实。 |

## 反模式：没有 `--rewrite` 模式

我们刻意不提供 `/humanize --rewrite`。自动改写行文以清除 AI 标记，往往会把行文改坏 —— 改写器会引入它*自己的* AI 标记 —— 而且，正如 [`writing-with-ai.md`](../../rules/writing-with-ai.md) 所记录的，模型对自己输出的改写，在检测器眼里仍然是模型输出。检测—标记这个模式保住了作者的语声；代价是你的编辑时间，而这正是我们愿意付的代价。

如果你发现自己正伸手去够一个自动改写器，那就是该把这一段从头重写的信号 —— 而不是一条条去补标记。

## 输出

- 报告写到 `quality_reports/audits/humanize_<filename>_report.md`（该子目录已 gitignore）。
- 向对话汇报摘要：按类别计数、最集中的段落、行动建议。
- **不改任何文件。** 用户读报告，自行应用修改。

## 尊重成文的个人语声画像

若仓库根目录存在 `voice-profile.md`，**先读它**。作者已声明是刻意为之的习惯 ——
频繁的破折号、第一人称、某个特定的连接词 —— **不算发现**。把一项成文的偏好
当成 AI 标记来报是误报，而误报侵蚀报告公信力
的速度比漏报更快。

用 [`/voice-profile`](../voice-profile/SKILL.md) 建一份。本技能说的是该删什么；
那个技能说的是该往哪儿写。

## 本技能做不到什么（v2.5）

`/humanize` 找的是**表面标记** —— 套话式过渡、AI 陈词词典、堆叠的模糊限定、
对称的段落结构。修掉它们能提升可读性，
而这件事无论文字是谁写的都值得做。

**它不能让行文在检测器眼里不再像机器生成的。** 有一篇文章经过数轮表面去 AI 化打磨，
投给 Pangram —— 一个神经 AI 文本检测器 ——
结果被判为 **100% AI 写作**。这类检测器依据的是 LLM 生成的 token 级
统计特征，而任何模型施加的变换都保留这些特征 —— 因为
每一次变换产出的仍然是 LLM 生成的文本。

所以：**这里的一份干净报告只意味着行文读起来好，不意味着读起来像人。** 如果
溯源重要，就由作者亲手写那些承重的句子，并用真实检测器测量。见
[`writing-with-ai.md`](../../rules/writing-with-ai.md)。
