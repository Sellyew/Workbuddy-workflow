---
name: respond-to-eval
description: 把学生课程评教（自由文本 + 数值）变成一份可执行的教学改进计划 —— 是 /respond-to-referees 在教学上的对应物。把评语聚类成主题，把信号与噪声分开，给每个主题分类为 Keep / Change / Investigate / Out-of-scope，并起草映射到课程大纲与幻灯片的具体改动。用户说 "respond to my evals"、"what do these course evaluations tell me"、"turn my teaching feedback into a plan"，或一学期的评教结果出来时使用。
description_zh: 把学生课程评教（自由文本 + 数值）变成一份可执行的教学改进计划 —— 是 /respond-to-referees 在教学上的对应物。把评语聚类成主题，把信号与噪声分开，给每个主题分类为 Keep / Change / Investigate / Out-of-scope，并起草映射到课程大纲与幻灯片的具体改动。用户说 "respond to my evals"、"what do these course evaluations tell me"、"turn my teaching feedback into a plan"，或一学期的评教结果出来时使用。
argument-hint: "[eval-file(s)] [prior-plan-path] [--min-mentions N] [--no-verify]"
allowed-tools: ["Read", "Write", "Grep", "Glob", "Bash", "Agent", "Task"]
---

# 回应评教

把一学期的课程评教转成一份站得住脚的教学改进计划。把自由文本评语聚类成主题，按有多少名独立学生提到给每个主题加权，给「该怎么办」分类，并把具体改动指向课程大纲与幻灯片 —— 让下学期的修订是一张清单，而不是一种感觉。

**姿态（呼应 `/respond-to-referees`）：** 一条愤怒的评语不是趋势，而一条你不同意的评语是要去*调查*的信号，不是忽略它或自动照做的许可。一个学生的挫败，可能是唯一一个愿意说出二十个人感受的人 —— 频率给主题加权，但它不把主题挡在门外。这里的真相是一个过程：计划记录下某个主题为什么被保留或被改动，让这份推理活到下一轮。

## 何时使用

- 期末，数值评分 + 开放文本评语到手，你想要的是一份修订计划，而不是一种情绪。
- 汇编教学档案 / 终身教职材料，你需要*展示*你对反馈采取了行动。
- 学期中途（早期反馈），在学期结束前纠偏。

不用于：从头写课程大纲（用 `/syllabus`），或评审某一套幻灯片的教学法（用 `/pedagogy-review`）。

## 输入

- `$0` —— 评教文件：CSV/TSV 导出、粘贴评语的 `.txt`/`.md`，或 `.pdf`/`.docx` 报告。
- `$1`（可选）—— **上一轮**的改进计划，让这一轮成为一次 diff（上学期的改动落地了吗？）

| 格式 | 怎么读 |
| --- | --- |
| `.csv`、`.tsv`、`.txt`、`.md` | 直接 `Read`；对 CSV，注明哪一列是数值、哪一列是自由文本。 |
| `.pdf` | `TMP=$(mktemp -d)/evals.txt && pdftotext "$0" "$TMP"`（poppler）。读/grep `"$TMP"`。 |
| `.docx` | `TMP=$(mktemp -d)/evals.txt && pandoc "$0" -t plain -o "$TMP"`。 |

若抽取失败或缺少某个工具，就向用户要一份纯文本导出并停下。扫描版或部分扫描的 PDF 会以退出码 0 抽出空白页，所以还要把 `pdfinfo "$0" | grep Pages` 与真正抽到文本的页数（`awk 'BEGIN{RS="\f"} NF{n++} END{print n+0}' "$TMP"`）比对；任何空白页都要用 Read 直接读，或要一份文本版，如果你不读就往下走，要说明哪些页没读。做完之后删掉抽出的副本（`rm -rf "$(dirname "$TMP")"`）：它是该文档的一份纯文本拷贝。

## 各阶段

### Phase 0: 载入评教 + 上一轮计划（起飞前检查）

读评教文件与上一轮计划（若给出）。在聚类之前产出一小段起飞前报告：

```markdown
## Pre-Flight Report
**Evals loaded:** N responses (M with free-text), instrument: [name/term]
**Numeric items:** [list each scale item + mean, and the institution/department mean if present]
**Prior plan:** [path, or "none — first round"] — changes promised last term: [bullet list]
**Course artifacts in scope:** [syllabus path] · [deck(s) under Slides/ or Quarto/]
```

数字给阅读定锚，但不压倒文本：一份 4.2/5 的评分配上十条 "I was lost by week 6" 的评语，就是均值正在掩盖的问题。

### Phase 1: 聚类主题 + 按频率加权

1. 把自由文本切成原子评语（一个学生可能提出多个主题；一条评语可能属于多个主题）。
2. 聚类成主题（例如 *节奏*、*习题集难度*、*评分清晰度*、*现实相关性*、*答疑时间*、*先修知识缺口*）。用授课教师自己的话给主题命名，而不是学生的话。
3. 为每个主题记录：**被提及次数**（不同学生数）、**代表性原文引用**（约 25 词，匿名化 —— 去掉姓名/可识别细节）、**情感倾向**（正面 / 负面 / 混合），以及**数值佐证**（若有某个量表项与之同向变动，是哪一个）。
4. **信号与噪声：** 提到它的不同学生数低于 `--min-mentions`（默认 2）的主题被标为 **low-frequency**，而不是被丢掉 —— 它进入 Phase 2 去做一次 Keep/Investigate 判定。频率给权重；它从不噤声。

### Phase 2: 分类 + 提出改动

给每个主题分配恰好一个标签（是 `/respond-to-referees` 覆盖矩阵的教学版）：

| 标签 | 含义 | 驱动什么 |
| --- | --- | --- |
| **Keep** | 运行良好；在你改动其他地方时保护它不被误伤。 | 一条「不要破坏」的备注。 |
| **Change** | 问题明确、已达成共识，且有你能点名的具体修法。 | 一处具体的课程大纲/幻灯片改动。 |
| **Investigate** | 是真信号，但根因不清楚，或你不同意所提的补救办法 —— 先收集证据（一次期中脉动调查、看一眼成绩分布、同行听课）再动手。 | 一个调查步骤，不是一次改动。 |
| **Out-of-scope** | 超出你的控制（教室、时间段、指定教材、先修课），或与你坚持的某个刻意教学选择相悖。 | 一份记录下来的理由，不是一处改动。 |

对每个 **Change**，写出一处映射到目标的具体修订：`syllabus §X` / `Slides/LectureNN.tex slide K` / 一个新的详解例题 / 一次考核权重重配 —— 与 `/respond-to-referees` 处理「我们在第 Y 页加了 X」同一套指向位置的纪律。对 **Investigate**，点名你要收集的证据与判定规则。对 **Out-of-scope**，写下那句你愿意在档案里站得住的理由。

分歧要显性且带论证："Students asked to drop proofs; retained because the course's stated objective is derivation fluency — added two scaffolded worked examples (LectureNN slide K) to ease the on-ramp instead" 属于 Keep-with-mitigation，而不是 Out-of-scope 式的弃置。

### Phase 3: 保存改进计划

把计划写到 `quality_reports/teaching/YYYY-MM-DD_[course]_improvement-plan.md`。结构：

1. **表头** —— 课程、学期、评教工具、回收率、数值摘要对基准。
2. **上一轮计划回顾**（若给了 `$1`）—— 对上学期承诺的每项改动：已落地 / 部分落地 / 未做，并附本学期评教里的证据。
3. **主题矩阵** —— 每个主题一行：主题 · 提及数 · 情感倾向 · 数值佐证 · 分类 · 目标（课程大纲 §/幻灯片页） · 代表性引用。
4. **改动清单** —— 具体编辑，按提及数、再按严重度排序，每条都指向课程大纲某一节或某套幻灯片的某一页。
5. **调查清单** —— 待解问题 + 下一步要收集的证据。

这份计划是交付物，不是过路报告，所以它放在 `quality_reports/teaching/` 下，并成为下学期 `$1` 的输入。

### Phase 3.5: 落地后核验（引用 + 目标）

计划里容易出幻觉的内容是 (a) 归到学生名下的原文引用，以及 (b) 「编辑课程大纲 §X / LectureNN 第 K 页」这类必须真的存在的目标。跑 [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) 里的独立上下文核验协议：生成 `claim-verifier`（独立上下文，绝不是对话分叉），交给它这些引用 + 评教源文件，以及这些编辑目标 + 课程大纲/幻灯片路径。对账 —— 源文件里没有的引用、或并不存在的「第 K 页」，在计划定稿之前被更正或删掉。可退出此步：`--no-verify`（不推荐）。

## 输出 / 报告

写完计划之后，在你的**最终聊天消息**里（不是计划文件之内）摆出这段：

```
## Teaching-improvement summary — [course], [term]
Themes: K total — C Change · I Investigate · P Keep · O Out-of-scope
Top 3 changes (by mentions): 1) … 2) … 3) …
Open investigations: …
Prior plan: x of y promised changes landed.
```

若所有主题都已分类、且每个 Change 都点名了目标，就说 `All themes classified; every Change mapped to a syllabus or deck target.`

## 退出行为

- 有主题没有分类会让报告中止 —— 没有孤儿，正如 `/respond-to-referees` 不容许未分类的关切。
- 对课程大纲与幻灯片只读：本技能**规划**改动并写出计划文件；它不编辑教学材料。改动之后再有意识地施加（用 `/create-lecture` 或直接编辑）。
- 数字绝不自动压倒文本，文本也绝不自动压倒数字；冲突变成 **Investigate**，而不是让某一方悄悄胜出。

## 参数

- `--min-mentions` —— 不同学生数阈值，低于它的主题被标为 *low-frequency*（默认 `2`）。调低它会浮出更多单例；它从不丢弃它们。
- `--no-verify` —— 跳过 Phase 3.5 对引用与编辑目标的落地后核验。对要进档案的计划不推荐。

## 交叉引用

- [`.codebuddy/skills/respond-to-referees/SKILL.md`](../respond-to-referees/SKILL.md) —— 研究侧的对应物；本技能借用它「映射—分类—回应」的形态，以及「是信号就去调查，不自动照做」的姿态。
- [`.codebuddy/skills/pedagogy-review/SKILL.md`](../pedagogy-review/SKILL.md) —— 一旦某个 **Change** 指向某套具体幻灯片，重讲之前先对它跑一遍 pedagogy-review。
- [`.codebuddy/skills/create-lecture/SKILL.md`](../create-lecture/SKILL.md) —— 用来执行计划提出的幻灯片层面改动。
- [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) —— Phase 3.5 复用的独立上下文核验协议。
- [`templates/skill-template.md`](../../../templates/skill-template.md) —— 技能的内部风格规范。

## 本技能不做什么

- 它**不**编辑课程大纲或任何幻灯片 —— 它产出一份计划；由你（或 `/create-lecture`）去施加。
- 它**不**计算新的数值评分，也不重新加权评教工具；它照读机构给出的数字。
- 它**不**识别学生，也不试图对评语做去匿名化 —— 引用都剥离了可识别细节。
- 它**不**对分歧或单条评语自动采取行动；两者都归入 **Investigate** 或一份记录下来的理由。
