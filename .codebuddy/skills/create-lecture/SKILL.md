---
name: create-lecture
description: 根据来源论文和材料创建新的 Beamer 讲义 `.tex`，检查记号一致性并接入本项目导言区。用户说 "create a lecture on X"、"new lecture from these papers"、"start a deck on topic Y"、"scaffold a new Beamer file"、"build me a lecture from these PDFs"、"创建一讲课程"、"根据这些论文做讲义" 或 "新建 Beamer 讲义" 时使用。它用于搭建整套讲义，**不**用于编译已有 `.tex`，编译请用 `/compile-latex`。
description_zh: 根据来源论文和材料创建新的 Beamer 讲义 `.tex`，检查记号一致性并接入本项目导言区。用户说 "create a lecture on X"、"new lecture from these papers"、"start a deck on topic Y"、"scaffold a new Beamer file"、"build me a lecture from these PDFs"、"创建一讲课程"、"根据这些论文做讲义" 或 "新建 Beamer 讲义" 时使用。它用于搭建整套讲义，**不**用于编译已有 `.tex`，编译请用 `/compile-latex`。
argument-hint: "[Topic name]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task"]
disable-model-invocation: true
---

# 讲义创建工作流

创建一份清晰、符合教学目标的 Beamer 讲义。

**这是协作式迭代过程。授课者决定教学目标，WorkBuddy 协助思考和起草。**

---

## 约束（不可让步）

1. **先读知识库**，包括记号登记表、叙事弧和应用案例库
2. 每个新符号都要对照记号登记表检查
3. 先解释动机，再给出形式化内容，没有例外
4. 每个定义之后两页以内必须有算例
5. 每页最多使用 2 个彩色框
6. 不使用 `\pause` 或覆盖层命令，见项目规则
7. 在重大概念转折处安排过渡页
8. 全程至少贯穿 1 个持续展开的实证应用
9. 所有引文都要对照文献库核验
10. **每批处理 5-10 页**，交付一批就收集反馈，不要一次生成整套讲义

---

## 工作流

### Phase 0: 需求接收与语境（必须提交起飞前报告）

先读取输入，在回复中生成起飞前报告，然后才能进入 Phase 1。

需要读取：

- `.codebuddy/rules/knowledge-base-template.md`：记号登记表、叙事弧和应用案例
- `.codebuddy/rules/content-invariants.md`：管理幻灯片内容的 INV-1..INV-8
- 用户提供的所有来源论文和既有幻灯片
- 项目共享导言区 `Preambles/header.tex`（若 `CODEBUDDY.md` 指定其他路径，则以项目约定为准）；首讲没有往期讲义时必须在 Phase 0 先读取，不存在时按下方兜底取得最小导言区批准
- 上一讲的 `.tex`，重点是完整导言区、最后一节和结尾页，仅在其存在时读取；导言区接入与编译验证在 Phase 5 单独执行

必须包含以下起飞前报告块：

```markdown
## Pre-Flight Report

**Sources read:**
- [source 1]: [one-line takeaway — what notation, what result, what diagram]
- [source 2]: ...

**Notation registry check:**
- New symbols this lecture will introduce: [list]
- Symbols reused from prior lectures: [list, with the lecture each was introduced in]
- Conflicts detected: [none / specific clashes]

**Narrative position:** [Where does this lecture sit in the course arc? What did the previous lecture end on? What does the next lecture need you to set up?]

**Pedagogical goal:** [one sentence]

**Running application:** [which real-world example threads through this deck]
```

说明教学目标，取得用户确认后再继续。

**首讲兜底（全新 fork、知识库为空）。** 如果 `.codebuddy/rules/knowledge-base-template.md` 中的占位表格仍未填写，没有记号登记表条目和应用案例，`Slides/` 中也没有往期讲义，**不要**停下来等待。按以下步骤处理：

1. 说明模板仍为空，目前正在创建这门课的第一讲。
2. 根据用户主题提出一份**最小可用起步知识库**：5-8 个带约定的关键符号、1-2 个贯穿应用，以及一段简短叙事弧（引入 → 核心思想 → 含义），提交用户批准。
3. 把获批骨架写入知识库模板，供后续各讲继承。
4. 继续进入 Phase 1。

这样可避免 `/create-lecture` 在每个新 fork 中都无法启动。

**首讲导言区兜底（无往期讲义）。** 首讲没有往期 `.tex` 时，先在 Phase 0 按项目约定读取共享导言区（通常为 `Preambles/header.tex`），列出其中可复用的宏包、自定义宏、主题和资源路径。若共享导言区不存在，提出一份**最小导言区**，只含 `\documentclass`、Beamer 主题、必需宏包、自定义宏与资源路径的最小集合，并说明拟写入路径；取得用户批准后才创建并作为本讲及后续讲义的共享来源。随后才能做宏、路径与编译核对。不得跳过批准，也不得在 Phase 5 再要求寻找不存在的往期讲义。

### Phase 1: 论文分析（提供了论文时）

- 分块阅读并提取核心思想
- 把论文记号映射为课程记号
- 找出值得放入幻灯片的内容
- 提交摘要供用户批准

### Phase 2: 结构提案

- 提出大纲，可采用五幕式或三段式模板
- 列出所需 TikZ 图和 R 图
- 列出将引入的新记号
- **门禁：用户批准后才能进入 Phase 3**

### Phase 3: 起草幻灯片（迭代）

- 每批处理 5-10 页
- 检查记号并套用创作模式
- 起草过程中同步检查质量

### Phase 4: 图与代码

- R 脚本遵循项目约定
- TikZ 图保留在 Beamer 源码中，作为单一真源
- 保存 RDS，供日后接入 Quarto

### Phase 5: 导言区接入与编译验证

1. **读取项目编译约定。** 读取 `CODEBUDDY.md` 和 [`/compile-latex`](../compile-latex/SKILL.md)，确认项目指定的编译器、命令、输出目录、环境变量与文献工具，不套用通用默认命令。
2. **确定导言区来源。** 有往期讲义时，找一份同课程现有 `.tex`，完整读取其 `\documentclass` 至 `\begin{document}`，并对照项目共享导言区列出宏包、自定义宏、主题与资源路径。首讲无往期讲义时，直接使用 Phase 0 已读取的项目共享导言区，或使用 Phase 0 已提出、获用户批准并创建的最小导言区；**不再寻找往期讲义**。新讲义复用已确定的来源，不凭空另建一套导言区。
3. **配置输入路径。** 按实际项目结构配置宏包、导言区、图片和文献的输入路径（例如项目约定的 `TEXINPUTS`、`\graphicspath` 与文献路径），并在编译记录中写明实际取值；不要用不存在的模板路径。
4. **编译前核对。** 检查新讲义调用的每个宏均有定义、所需宏包均可由配置路径找到、宏包顺序与已确定的共享或获批最小导言区兼容，并核对源文件、资源目录和输出目录确实存在。任何一项未解决都先停止编译并报告。
5. **完成上述核对后再编译验证。** 按项目命令完整编译三遍，检查编译错误、未解析引用与文献、overfull 警告及预期 PDF 是否生成；不能把“源码已写出”当成“编译已通过”。
6. 运行 Devil's Advocate；如果已配置领域审读者，运行实质内容审读；把新记号更新到知识库。

---

## 创建后检查清单

```
[ ] Lecture compiles without errors
[ ] No overfull hbox > 10pt
[ ] All citations resolve
[ ] Every definition has motivation + worked example
[ ] Max 2 colored boxes per slide
[ ] 2-3 Socratic questions embedded
[ ] Transition slides between sections
[ ] At least 1 running application threaded throughout
[ ] New notation added to knowledge base
[ ] Session log updated
[ ] Devil's Advocate run
```

## 交叉引用

- [`.codebuddy/skills/translate-to-quarto/SKILL.md`](../translate-to-quarto/SKILL.md)：把完成的 Beamer 讲义移植为 Quarto RevealJS 镜像。
- [`.codebuddy/skills/qa-quarto/SKILL.md`](../qa-quarto/SKILL.md)：以空轮收敛方式检查 Beamer↔Quarto 的对抗式一致性。
- [`.codebuddy/skills/deploy/SKILL.md`](../deploy/SKILL.md)：渲染讲义并发布到 GitHub Pages。
- [`.codebuddy/skills/scaffold-exercises/SKILL.md`](../scaffold-exercises/SKILL.md)：生成与本讲配套的习题集和解答。
