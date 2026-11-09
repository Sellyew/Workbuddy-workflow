---
name: respond-to-eval
description: 把学生课程评教中的自由文本和数值评分转化为可执行的教学改进计划，相当于教学场景的 /respond-to-referees。把评语聚类成主题，区分信号与噪声，将每个主题分为 Keep / Change / Investigate / Out-of-scope，并起草对应到课程大纲和幻灯片的具体改动。用户说 "respond to my evals"、"what do these course evaluations tell me"、"turn my teaching feedback into a plan"、"回应课程评教"、"分析学生评教" 或 "把教学反馈变成改进计划"，或一学期评教结果出来时使用。
description_zh: 把学生课程评教中的自由文本和数值评分转化为可执行的教学改进计划，相当于教学场景的 /respond-to-referees。把评语聚类成主题，区分信号与噪声，将每个主题分为 Keep / Change / Investigate / Out-of-scope，并起草对应到课程大纲和幻灯片的具体改动。用户说 "respond to my evals"、"what do these course evaluations tell me"、"turn my teaching feedback into a plan"、"回应课程评教"、"分析学生评教" 或 "把教学反馈变成改进计划"，或一学期评教结果出来时使用。
argument-hint: "[eval-file(s)] [prior-plan-path] [--min-mentions N] [--no-verify]"
allowed-tools: ["Read", "Write", "Grep", "Glob", "Bash", "Agent", "Task"]
---

# 回应评教

本技能把一学期的课程评教整理成有据可依的教学改进计划。它把自由文本评语聚类成主题，按提及该主题的独立学生数赋权，判断每个主题该如何处理，并把具体改动对应到课程大纲和幻灯片。这样，下学期的修订依据是一份清单，而不是一种感觉。

**姿态与 `/respond-to-referees` 一致：**一条愤怒评语不代表趋势；一条你不同意的评语则需要*调查*，既不能直接忽略，也不能自动照做。一个学生的挫败可能代表二十个没有发声的人，因此频率用于赋权，不用于排除主题。计划还要记录保留或改动每个主题的理由，让下一轮能继续检验这些判断。

## 何时使用

- 期末拿到数值评分 + 开放文本评语，需要形成修订计划。
- 汇编教学档案／终身教职材料，需要*展示*自己如何根据反馈采取行动。
- 学期中途收集早期反馈，需要在学期结束前纠偏。

不用于从头编写课程大纲（用 `/syllabus`），也不用于审读某套幻灯片的教学法（用 `/pedagogy-review`）。

## 输入

从 `$ARGUMENTS` 先解析 `--min-mentions` 与 `--no-verify`，再处理剩余位置参数，不要读取 shell 的位置参数。至少一个评教路径归入 `eval_paths`；若本次调用明确包含上一轮计划，最后一个位置参数赋给 `prior_plan_path`，否则 `prior_plan_path` 为空。无法判定最后一个路径是评教还是上一轮计划时，先询问用户，不得猜测。

- `eval_paths` —— 一个或多个评教文件：CSV/TSV 导出、粘贴评语的 `.txt`/`.md`，或 `.pdf`/`.docx` 报告。逐个校验文件存在、可读且格式受支持。
- `prior_plan_path`（可选）—— **上一轮**改进计划，用于比较上学期的改动是否落地；给出时必须存在且可读。
- `--min-mentions` 必须带正整数值并赋给 `min_mentions`；`--no-verify` 是独立布尔旗标。未知选项、选项缺值、非法阈值或多余参数均停止并报告。

对 `eval_paths` 中的每个 `eval_path` 分别读取或抽取：

| 格式 | 怎么读 |
| --- | --- |
| `.csv`、`.tsv`、`.txt`、`.md` | 直接 `Read`；对 CSV，注明哪一列是数值、哪一列是自由文本。 |
| `.pdf` | `TMP=$(mktemp -d)/evals.txt && pdftotext "$eval_path" "$TMP"`（poppler）。读/grep `"$TMP"`。 |
| `.docx` | `TMP=$(mktemp -d)/evals.txt && pandoc "$eval_path" -t plain -o "$TMP"`。 |

若抽取失败或缺少工具，就向用户索要纯文本导出并停止。扫描版或部分扫描的 PDF 即使抽出空白页，也可能以退出码 0 结束，因此还要比较 `pdfinfo "$eval_path" | grep Pages` 与真正抽到文本的页数（`awk 'BEGIN{RS="\f"} NF{n++} END{print n+0}' "$TMP"`）。空白页必须用 Read 直接读取，或向用户索要文本版；若未读取就继续，必须说明漏读了哪些页。完成后删除抽取副本（`rm -rf "$(dirname "$TMP")"`），因为它是文档的纯文本拷贝。

## 各阶段

### Phase 0: 载入评教 + 上一轮计划（开始前检查）

读取评教文件和上一轮计划（若给出）。聚类之前，先生成简短的开始前报告：

```markdown
## Pre-Flight Report
**Evals loaded:** N responses (M with free-text), instrument: [name/term]
**Numeric items:** [list each scale item + mean, and the institution/department mean if present]
**Prior plan:** [path, or "none — first round"] — changes promised last term: [bullet list]
**Course artifacts in scope:** [syllabus path] · [deck(s) under Slides/ or Quarto/]
```

数值帮助定位问题，但不能压过文本。若一份 4.2/5 的评分同时伴随十条 "I was lost by week 6" 评语，就说明均值掩盖了实际问题。

### Phase 1: 聚类主题 + 按频率加权

1. 把自由文本拆成原子评语。一个学生可以提出多个主题，一条评语也可以属于多个主题。
2. 聚类成主题，例如*节奏*、*习题集难度*、*评分清晰度*、*现实相关性*、*答疑时间*、*先修知识缺口*。主题名称使用授课教师自己的表述，不直接照搬学生原话。
3. 为每个主题记录：**被提及次数**（不同学生数）、**代表性原文引用**（约 25 词，匿名化并去掉姓名／可识别细节）、**情感倾向**（正面／负面／混合），以及**数值佐证**（若有同向变化的量表项，注明是哪一个）。
4. **区分信号与噪声：**提及人数低于 `--min-mentions`（默认 2）的主题标为 **low-frequency**，不能删除；它仍进入 Phase 2，接受 Keep/Investigate 判定。频率只影响权重，不会让主题失声。

### Phase 2: 分类 + 提出改动

每个主题必须且只能分配一个标签。这套分类是 `/respond-to-referees` 覆盖矩阵的教学版：

| 标签 | 含义 | 驱动什么 |
| --- | --- | --- |
| **Keep** | 运行良好；在你改动其他地方时保护它不被误伤。 | 一条「不要破坏」的备注。 |
| **Change** | 问题明确、已达成共识，且有你能点名的具体修法。 | 一处具体的课程大纲/幻灯片改动。 |
| **Investigate** | 是真信号，但根因不清楚，或你不同意所提的补救办法 —— 先收集证据（一次期中脉动调查、看一眼成绩分布、同行听课）再动手。 | 一个调查步骤，不是一次改动。 |
| **Out-of-scope** | 超出你的控制（教室、时间段、指定教材、先修课），或与你坚持的某个刻意教学选择相悖。 | 一份记录下来的理由，不是一处改动。 |

每个 **Change** 都要写到具体目标，例如 `syllabus §X`、`Slides/LectureNN.tex slide K`、一个新的详解例题或一次考核权重重配。这与 `/respond-to-referees` 对「我们在第 Y 页加了 X」的位置要求一致。对 **Investigate**，写明要收集的证据与判定规则；对 **Out-of-scope**，写下愿意在教学档案中公开说明的理由。

出现分歧时，要明确写出论证。例如："Students asked to drop proofs; retained because the course's stated objective is derivation fluency — added two scaffolded worked examples (LectureNN slide K) to ease the on-ramp instead"。这属于 Keep-with-mitigation，不能用 Out-of-scope 把问题搁置。

### Phase 3: 保存改进计划

把计划写到 `quality_reports/teaching/YYYY-MM-DD_[course]_improvement-plan.md`，结构如下：

1. **表头**：课程、学期、评教工具、回收率，以及数值摘要与基准的对照。
2. **上一轮计划回顾**（若给了 `prior_plan_path`）：逐项说明上学期承诺的改动已落地／部分落地／未做，并附本学期评教证据。
3. **主题矩阵**：每个主题一行，依次列出主题 · 提及数 · 情感倾向 · 数值佐证 · 分类 · 目标（课程大纲 §/幻灯片页） · 代表性引用。
4. **改动清单**：列出具体编辑，先按提及数、再按严重度排序，每项都指向课程大纲某节或某套幻灯片某页。
5. **调查清单**：列出待解问题和下一步要收集的证据。

这份计划是正式交付物，不是中间报告，因此保存在 `quality_reports/teaching/`，并作为下学期 `prior_plan_path` 的输入。

### Phase 3.5: 落地后核验（引用 + 目标）

计划最容易出现两类幻觉：(a) 归到学生名下但源文件不存在的原文引用；(b) 「编辑课程大纲 §X / LectureNN 第 K 页」等并不存在的目标。运行 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 的独立上下文核验协议：通过独立 `Agent` 调用生成 `claim-verifier`，不能使用对话分叉；提供这些引用 + 评教源文件，以及编辑目标 + 课程大纲／幻灯片路径。对账后，在定稿前更正或删除源文件中没有的引用和不存在的「第 K 页」。可用 `--no-verify` 跳过，但不推荐。

## 输出 / 报告

写完计划后，在**最终聊天消息**中给出以下内容，不要写进计划文件：

```
## Teaching-improvement summary — [course], [term]
Themes: K total — C Change · I Investigate · P Keep · O Out-of-scope
Top 3 changes (by mentions): 1) … 2) … 3) …
Open investigations: …
Prior plan: x of y promised changes landed.
```

若所有主题都已分类，且每个 Change 都指明了目标，就写 `All themes classified; every Change mapped to a syllabus or deck target.`

## 退出行为

- 只要还有主题未分类，报告就中止，不允许留下孤儿项；这与 `/respond-to-referees` 不允许关切未分类的要求一致。
- 对课程大纲和幻灯片只读。本技能只**规划**改动并写计划文件，不编辑教学材料；之后通过 `/create-lecture` 或直接编辑有意识地实施。
- 数值不能自动压过文本，文本也不能自动压过数值。两者冲突时归为 **Investigate**，不能让任何一方悄悄胜出。

## 参数

- `--min-mentions` —— 不同学生数阈值，低于它的主题被标为 *low-frequency*（默认 `2`）。调低它会浮出更多单例；它从不丢弃它们。
- `--no-verify` —— 跳过 Phase 3.5 对引用与编辑目标的落地后核验。对要进档案的计划不推荐。

## 交叉引用

- [`.codebuddy/skills/respond-to-referees/SKILL.md`](../respond-to-referees/SKILL.md) —— 研究场景的对应技能；本技能沿用其「映射—分类—回应」结构，以及「是信号就调查，不自动照做」的姿态。
- [`.codebuddy/skills/pedagogy-review/SKILL.md`](../pedagogy-review/SKILL.md) —— 某个 **Change** 指向具体幻灯片时，重讲前先运行 pedagogy-review。
- [`.codebuddy/skills/create-lecture/SKILL.md`](../create-lecture/SKILL.md) —— 用于实施计划中的幻灯片改动。
- [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) —— Phase 3.5 使用的独立上下文核验协议。
- [`templates/skill-template.md`](../../../templates/skill-template.md) —— 技能的内部风格规范。

## 本技能不做什么

- **不编辑课程大纲或任何幻灯片**，只生成计划，由你或 `/create-lecture` 实施。
- **不重新计算数值评分，也不重新加权评教工具**，只读取机构提供的数字。
- **不识别学生，也不尝试对评语去匿名化**；引用必须剥离可识别细节。
- **不根据分歧或单条评语自动采取行动**；两者都进入 **Investigate**，或留下明确理由。
