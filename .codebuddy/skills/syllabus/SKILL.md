---
name: syllabus
description: 从主题清单或阅读清单构建或重构课程大纲，包括课程描述 + 先修要求、逐周日程（主题 → 阅读 → 交付物）、可度量的学习目标、考核方案 + 评分细则、标准政策（迟交、AI 使用、学术诚信、无障碍），以及可直接交给 `/create-lecture` 的逐周工作清单。用户说 "build a syllabus"、"structure my course"、"turn this reading list into a schedule"、"draft a course outline"、"make a syllabus for Econ 7xx"、"map weeks to lectures"、"写课程大纲"、"安排学期课程" 或 "把阅读清单排成课表" 时使用。适用于经济学 PhD 计量／微观／宏观序列和本科课程，也适用于其他领域。
description_zh: 从主题清单或阅读清单构建或重构课程大纲，包括课程描述 + 先修要求、逐周日程（主题 → 阅读 → 交付物）、可度量的学习目标、考核方案 + 评分细则、标准政策（迟交、AI 使用、学术诚信、无障碍），以及可直接交给 `/create-lecture` 的逐周工作清单。用户说 "build a syllabus"、"structure my course"、"turn this reading list into a schedule"、"draft a course outline"、"make a syllabus for Econ 7xx"、"map weeks to lectures"、"写课程大纲"、"安排学期课程" 或 "把阅读清单排成课表" 时使用。适用于经济学 PhD 计量／微观／宏观序列和本科课程，也适用于其他领域。
argument-hint: "[course title or topic/reading list] [--weeks N] [--level phd|grad|undergrad] [--sessions-per-week N] [--no-policies]"
allowed-tools: ["Read", "Grep", "Glob", "Write"]

---

# 构建课程大纲

本技能把主题清单或阅读清单整理成可讲授的课程大纲，包含课程描述、有先后关系的逐周日程、可度量目标、带评分细则的考核方案、标准政策段落，以及可直接交给 `/create-lecture` 的「周次→讲次」工作清单。授课教师负责学术判断，本技能负责把判断组织成大纲。

## 何时使用

- 已有一批主题或论文，需要排进一个学期。
- 要调整去年的大纲，以适配新的学期长度、课程层级或授课形式。
- 希望在制作幻灯片前，先把每周日程映射到讲次。

不用于制作幻灯片（`/create-lecture`）、审读课件教学法（`/pedagogy-review`），或从零整理阅读清单（`/lit-review`）。

## Phase 0：需求收集（起草之前先问清）

大纲主要由三个参数决定。优先使用用户给出的参数，缺失时先询问。**三个参数全部确定前，不要安排顺序。**

1. **层级 + 受众**：`--level`（`phd` / `grad` / `undergrad`）。经济学课程要说明所属序列，例如一年级计量、微观理论、宏观、领域课或本科中级。层级决定阅读深度、证明与应用的比例，以及考核形式。
2. **长度 + 节奏**：`--weeks`（默认 14）和 `--sessions-per-week`（默认 2）。阅读研讨课与习题课即使长度相同，也需要不同的日程安排。
3. **素材**：主题清单或阅读清单，可来自 `$ARGUMENTS`、文件路径或 `.bib`。若用户指向 `.bib` 或 PDF 文件夹，用 `Glob`/`Read` 盘点；若只有简略主题，请用户为每个主题提供 1-2 篇锚定文献。

回显简短的**需求收集报告**，列出层级、周数、节奏、N 个主题 / N 篇阅读和任何缺口。取得确认后再进入 Phase 1。

## Phase 1：把主题排进周次

1. **按依赖关系排序，不要照搬阅读清单顺序。**建立先修链，把基础工具放在使用它们的主题之前，例如渐近理论 → GMM → 应用，消费者理论 → 一般均衡 → 福利。后面周次需要预设的内容必须前置。
2. **把阅读分配到各周。**每周负荷应符合课程层级：PhD 领域课一周 2-4 篇论文，本科一周 1 章 + 1 个应用。标出过载或过薄的周。
3. **把交付物放进日历。**习题集排在所练工具之后，期中放在自然的概念断点；审稿报告／复现／论文提案等里程碑要错开，避免集中相撞。标出阅读周与停课周。
4. **生成日程表**，每周列出主题 → 阅读 → 交付物。写学习目标前先取得确认，因为此时调整顺序成本最低。

## Phase 2：目标 + 考核

1. **写可度量的学习目标。**分别写课程级目标和单元目标，每条使用可观察的动词，例如推导、估计、复现、批评、证明，不写「理解」或「熟悉」。把每条目标关联到实现它的周次。
2. **设计考核方案。**选择适合课程层级的形式：方法课可用习题集 + 期末，领域课／PhD 课可用审稿报告 + 复现 + 论文，本科可用考试 + 项目。权重合计必须为 100%，并检查每条目标都有对应考核。
3. **为权重最高的交付物写评分细则**，例如论文、项目或审稿报告。按维度 × 等级列出分数区间，保持简短具体。

## Phase 3：产出课程大纲 + 讲次工作清单

1. **按下面的输出格式组装大纲文档**；若指定 `--no-policies`，跳过政策部分。
2. **生成逐周 `/create-lecture` 工作清单。**每个教学周一行，列出课件名、目标和锚定阅读，供授课教师按顺序交给 `/create-lecture`。这份清单连接大纲与幻灯片制作。

## 输出格式

写入 `quality_reports/teaching/[course]_syllabus.md`，或用户指定的路径。不要写入仓库根目录；根目录的 `syllabus.md` 会被仓库卫生门禁视为杂物。

```markdown
# [Course title] — [Term, Year]
[Level · meeting cadence · units]

## Course description
[2-4 sentences: what the course is, what students leave able to do.]

## Prerequisites
[Courses / skills assumed. Be specific — "first-year metrics or equivalent".]

## Learning objectives
By the end of this course, students will be able to:
- [observable verb] … (Weeks N-M)

## Weekly schedule
| Week | Topic | Readings | Deliverable |
|------|-------|----------|-------------|
| 1 | … | … | — |

## Assessment
| Component | Weight | Maps to objectives |
|-----------|-------:|--------------------|
| … | …% | … |

### Rubric — [highest-stakes deliverable]
| Criterion | Excellent | Adequate | Weak |
|-----------|-----------|----------|------|

## Policies
Late work · AI / LLM use · academic integrity · accessibility / accommodations · attendance.

## Week → lecture work-list (hand to `/create-lecture`)
| Week | Deck name | Objective(s) | Anchor reading |
|------|-----------|--------------|----------------|
```

最后在**聊天消息**中给出**缺口汇总**，不要写进文件。列出没有阅读的周、未被考核的目标、相撞的交付物，以及因时间不足而舍弃的主题。每项如何解决，由授课教师决定。

## 参数

- `--weeks` —— 学期长度，按教学周计（默认 14）。
- `--level` —— `phd` / `grad` / `undergrad`；决定阅读深度与考核形式。
- `--sessions-per-week` —— 每周上课次数（默认 2）；影响每周负荷。
- `--no-policies` —— 省略标准政策段落（当机构模板已经提供时使用）。

## 退出行为

- Phase 0 会等到层级、长度和素材全部确定后才继续；分叉运行或无人值守运行绝不能猜测这些参数。素材为空时，索要主题／阅读清单并停止。
- 每个阶段都要经用户确认才能进入下一阶段：先确认日程，再写目标，最后写政策。Phase 1 是调整顺序成本最低的阶段。
- 交付物包括大纲文件和工作清单。聊天消息必须带缺口汇总，即使没有缺口，也要写 `No gaps — every week has a reading and every objective is assessed.`
- 本技能只处理文本，从不编译、渲染或构建幻灯片。

## 交叉引用

- `/create-lecture`（[`.codebuddy/skills/create-lecture/SKILL.md`](../create-lecture/SKILL.md)）—— 下一步使用的技能；把工作清单逐周交给它。
- `/lit-review`（[`.codebuddy/skills/lit-review/SKILL.md`](../lit-review/SKILL.md)）—— 在排序*之前*构建或扩展阅读清单。
- `/interview-me`（[`.codebuddy/skills/interview-me/SKILL.md`](../interview-me/SKILL.md)）—— 课程目标仍含糊时，先通过访谈明确目标。
- `/pedagogy-review`（[`.codebuddy/skills/pedagogy-review/SKILL.md`](../pedagogy-review/SKILL.md)）—— 课件完成后审读叙事／节奏；大纲的整体安排是它的核验依据。
- 撰写约定：[`templates/skill-template.md`](../../../templates/skill-template.md)。

## 本技能不做什么

- 不写幻灯片内容，也不创建 `.tex`/`.qmd` 课件骨架，这些由 `/create-lecture` 完成。
- 不检索或甄选阅读材料，应与 `/lit-review` 搭配。
- 不评分、不生成习题集、不编写答案册。
- 不把机构政策写成强制要求。政策段落只是可编辑模板，授课教师必须与本系规则核对。
- 不编造引文；日程中的每篇阅读都必须来自用户提供的素材。
