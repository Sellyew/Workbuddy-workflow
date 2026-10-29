---
name: syllabus
description: 从一份主题清单或阅读清单构建或重构课程大纲——课程描述 + 先修要求、逐周日程（主题 → 阅读 → 交付物）、可度量的学习目标、考核方案 + 评分细则、标准政策（迟交、AI 使用、学术诚信、无障碍），外加一份逐周工作清单，可直接交给 `/create-lecture`。当用户说 "build a syllabus"、"structure my course"、"turn this reading list into a schedule"、"draft a course outline"、"make a syllabus for Econ 7xx"、"map weeks to lectures" 时使用。懂经济学语境（PhD 计量/微观/宏观序列、本科），但足够通用，适用于任何领域。
description_zh: 从一份主题清单或阅读清单构建或重构课程大纲——课程描述 + 先修要求、逐周日程（主题 → 阅读 → 交付物）、可度量的学习目标、考核方案 + 评分细则、标准政策（迟交、AI 使用、学术诚信、无障碍），外加一份逐周工作清单，可直接交给 `/create-lecture`。当用户说 "build a syllabus"、"structure my course"、"turn this reading list into a schedule"、"draft a course outline"、"make a syllabus for Econ 7xx"、"map weeks to lectures" 时使用。懂经济学语境（PhD 计量/微观/宏观序列、本科），但足够通用，适用于任何领域。
argument-hint: "[course title or topic/reading list] [--weeks N] [--level phd|grad|undergrad] [--sessions-per-week N] [--no-policies]"
allowed-tools: ["Read", "Grep", "Glob", "Write"]

---

# 构建课程大纲

把一份光秃秃的主题清单或阅读清单变成可讲授的课程大纲：课程描述、有先后的逐周日程、可度量的目标、带评分细则的考核方案、每份大纲都需要的标准政策段落，以及一份「周次→讲次」工作清单，可直接喂给 `/create-lecture`。学术判断归授课教师；本技能负责把它结构化。

## 何时使用

- 你有一堆主题或论文，需要把它们排进一个学期。
- 你要把去年的大纲改成新的长度、层级或授课形态。
- 你希望在开始做幻灯片之前，就把日程的各周预先映射到讲次。

不用于构建幻灯片本身（`/create-lecture`）、审读一份课件的教学法（`/pedagogy-review`），或从零组装阅读清单（`/lit-review`）。

## Phase 0：需求收集（起草之前先问清）

一份大纲几乎完全由三个参数决定。先定下它们——有参数就用参数，没有就问。**三个都钉死之前，不要开始排顺序。**

1. **层级 + 受众** —— `--level`（`phd` / `grad` / `undergrad`）。经济学要说明是哪条序列（一年级计量、微观理论、宏观、领域课、本科中级）。层级决定阅读深度、证明与应用的配比，以及考核形式。
2. **长度 + 节奏** —— `--weeks`（默认 14）与 `--sessions-per-week`（默认 2）。同样长度的阅读研讨课与习题课，日程需要非常不同的安排。
3. **素材** —— 主题清单或阅读清单（`$ARGUMENTS`、一个文件路径，或一个 `.bib`）。若用户指向一个 `.bib` 或一个 PDF 文件夹，用 `Glob`/`Read` 盘点；若主题还是光秃秃的，请用户为每个主题给 1-2 篇锚定文献。

回显一份简短的**需求收集报告**（层级、周数、节奏、N 个主题 / N 篇阅读、任何缺口），并取得确认，再进入 Phase 1。

## Phase 1：把主题排进周次

1. **按依赖关系排序，不要按阅读清单原本的顺序。** 建一条先修链——基础工具排在用到它们的主题之前（例如渐近理论 → GMM → 应用；消费者理论 → 一般均衡 → 福利）。把后面周次会预设的内容前置。
2. **把阅读分配到各周。** 让每周负荷对该层级现实可行（PhD 领域课一周 2-4 篇论文；本科一周 1 章 + 1 个应用）。标出任何过载或过薄的周。
3. **把交付物摆到日历上。** 习题集排在其所练工具之后；期中排在自然的概念断点；审稿报告 / 复现 / 论文提案等里程碑拉开间距，避免相撞。标出阅读周与停课周。
4. **产出日程表**（每周：主题 → 阅读 → 交付物），在写目标之前取得确认——现在改顺序便宜，之后很贵。

## Phase 2：目标 + 考核

1. **写可度量的学习目标。** 一套课程级目标，加上每单元目标，每条都用一个可观测的动词（推导、估计、复现、批评、证明）——不要用「理解」或「熟悉」。把每条目标挂到交付它的那一周（或那几周）上。
2. **设计考核方案。** 挑选契合该层级的形式（方法课：习题集 + 期末；领域课/PhD 课：审稿报告 + 复现 + 论文；本科：考试 + 项目）。写明权重合计 100%，并检查每条目标都被某种考核覆盖。
3. **为最高权重的交付物写一份评分细则**（论文、项目或审稿报告）——维度 × 等级，带分数区间。保持简短具体。

## Phase 3：产出课程大纲 + 讲次工作清单

1. **按下面的输出格式组装大纲文档**（若指定 `--no-policies` 则跳过政策）。
2. **生成逐周的 `/create-lecture` 工作清单** —— 每个教学周一行，映射到一个课件名、它的目标、以及它的锚定阅读，这样授课教师可以按顺序把每一行交给 `/create-lecture`。这是从大纲到幻灯片的桥。

## 输出格式

写入 `quality_reports/teaching/[course]_syllabus.md`（或用户指定的路径；不要写仓库根目录，那里的 `syllabus.md` 会作为根目录杂物过不了仓库卫生门禁）：

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

在聊天消息里（不是文件里）以一份**缺口汇总**收尾：没有阅读的周、没有被考核的目标、交付物相撞，或因时间不足而丢弃的主题——每一项怎么解决由授课教师决定。

## 参数

- `--weeks` —— 学期长度，按教学周计（默认 14）。
- `--level` —— `phd` / `grad` / `undergrad`；决定阅读深度与考核形式。
- `--sessions-per-week` —— 每周上课次数（默认 2）；影响每周负荷。
- `--no-policies` —— 省略标准政策段落（当机构模板已经提供时使用）。

## 退出行为

- Phase 0 会一直停住，直到层级、长度与素材三者都定下——分叉运行或无人值守运行绝不猜这些。若素材为空，索要一份主题/阅读清单，然后停下。
- 每个阶段都以用户确认为门禁（日程先于目标，目标先于政策）；在 Phase 1 改顺序是便宜地提供的。
- 交付物是大纲文件加工作清单；聊天消息始终带缺口汇总，即使为空也一样（`No gaps — every week has a reading and every objective is assessed.`）。
- 本技能只处理文本；它从不编译、渲染或构建幻灯片。

## 交叉引用

- `/create-lecture`（[`.codebuddy/skills/create-lecture/SKILL.md`](../create-lecture/SKILL.md)）—— 自然的下一步；把工作清单的行一周一周地喂给它。
- `/lit-review`（[`.codebuddy/skills/lit-review/SKILL.md`](../lit-review/SKILL.md)）—— 在排顺序*之前*构建或扩展阅读清单。
- `/interview-me`（[`.codebuddy/skills/interview-me/SKILL.md`](../interview-me/SKILL.md)）—— 若课程目标还含糊，先把它们形式化。
- `/pedagogy-review`（[`.codebuddy/skills/pedagogy-review/SKILL.md`](../pedagogy-review/SKILL.md)）—— 课件成型后审读叙事/节奏；大纲的弧线是它据以核验的输入。
- 撰写约定：[`templates/skill-template.md`](../../../templates/skill-template.md)。

## 本技能不做什么

- 不写幻灯片内容，也不搭 `.tex`/`.qmd` 课件骨架——那是 `/create-lecture`。
- 不检索也不甄选阅读——与 `/lit-review` 搭配。
- 不评分、不生成习题集、不做答案册。
- 不把机构政策断言为强制约束——政策段落是可编辑的模板文字，授课教师必须与本系规则对齐。
- 不杜撰引文；日程里的每一篇阅读都来自用户提供的素材。
