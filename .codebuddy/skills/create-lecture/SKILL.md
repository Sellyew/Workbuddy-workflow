---
name: create-lecture
description: 由来源论文与材料创建一份新的 Beamer 讲义 `.tex`，内建记号一致性检查并接好本项目的导言区。当用户说 "create a lecture on X"、"new lecture from these papers"、"start a deck on topic Y"、"scaffold a new Beamer file"、"build me a lecture from these PDFs" 时使用。它搭建的是整套讲义——**不**用于编译已有的 `.tex`（那用 `/compile-latex`）。
description_zh: 由来源论文与材料创建一份新的 Beamer 讲义 `.tex`，内建记号一致性检查并接好本项目的导言区。当用户说 "create a lecture on X"、"new lecture from these papers"、"start a deck on topic Y"、"scaffold a new Beamer file"、"build me a lecture from these PDFs" 时使用。它搭建的是整套讲义——**不**用于编译已有的 `.tex`（那用 `/compile-latex`）。
argument-hint: "[Topic name]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task"]
disable-model-invocation: true
---

# 讲义创建工作流

创建一份漂亮、教学上过硬的 Beamer 讲义。

**这是一个协作式的迭代过程。愿景由授课者主导；Claude 是思考伙伴。**

---

## 约束（不可让步）

1. **先读知识库**——记号登记表、叙事弧、应用案例库
2. 每个新符号都必须对照记号登记表检查
3. 先给动机，再上形式化——没有例外
4. 每个定义的两页之内要有算例
5. 每页最多 2 个彩色框
6. 不用 `\pause` 或覆盖层命令（见项目规则）
7. 在重大概念转折处放过渡页
8. 全程至少贯穿 1 个进行中的实证应用
9. 所有引文都对照文献库核验
10. **以 5-10 页为一批工作**——交付一批就收集反馈，不要一口气全倒出来

---

## 工作流

### Phase 0: 需求接收与语境（必须提交起飞前报告）

先读输入，然后在你的回复里产出一份起飞前报告，之后才开始 Phase 1。

要读的输入：
- `.codebuddy/rules/knowledge-base-template.md` —— 记号登记表、叙事弧、应用案例
- `.codebuddy/rules/content-invariants.md` —— 管辖幻灯片内容的 INV-1..INV-8
- 用户提供的任何来源论文／既有幻灯片
- 上一讲的 `.tex`（最后一节 + 结尾页，若存在）

必需的起飞前报告块：

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

说明教学目标，取得用户确认，再往下走。

**首讲兜底（全新 fork、知识库为空）。** 若 `.codebuddy/rules/knowledge-base-template.md` 里的占位表格仍未填（没有记号登记表条目、没有应用案例、`Slides/` 里没有往期讲义），**不要**停下来干等。改为：

1. 说明模板还是空的，我们正在创建这门课的第一讲。
2. 依据用户的主题提出一份**最小可用起步知识库**：5-8 个带约定的关键符号、1-2 个贯穿应用、一段简短叙事弧（引入 → 核心思想 → 含义）。提交批准。
3. 把获准的骨架写进知识库模板，让后续各讲继承它。
4. 继续进入 Phase 1。

这样可避免 `/create-lecture` 对每个新 fork 者都死锁。

### Phase 1: 论文分析（提供了论文时）
- 切块，抽取核心思想
- 把论文记号映射为课程记号
- 识别值得上幻灯片的内容
- 提交摘要以获批准

### Phase 2: 结构提案
- 提出大纲（五幕式或三段式模板）
- 列出所需的 TikZ 图与 R 图
- 列出要引入的新记号
- **门禁：用户在进入 Phase 3 之前批准**

### Phase 3: 起草幻灯片（迭代）
- 以 5-10 页为一批工作
- 检查记号，套用创作模式
- 起草过程中做质量检查

### Phase 4: 图与代码
- R 脚本遵循约定
- TikZ 图放在 Beamer 源码里（单一真源）
- 保存 RDS，供日后接 Quarto

### Phase 5: 打磨与编译
- 完整三遍编译
- 运行 Devil's Advocate
- 运行实质内容审读（若已配置领域审读者）
- 把新记号更新进知识库

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

- [`.codebuddy/skills/translate-to-quarto/SKILL.md`](../translate-to-quarto/SKILL.md) —— 把完成的 Beamer 讲义移植为 Quarto RevealJS 镜像。
- [`.codebuddy/skills/qa-quarto/SKILL.md`](../qa-quarto/SKILL.md) —— 对抗式 Beamer↔Quarto 一致性（空轮收敛）。
- [`.codebuddy/skills/deploy/SKILL.md`](../deploy/SKILL.md) —— 渲染并发布讲义到 GitHub Pages。
- [`.codebuddy/skills/scaffold-exercises/SKILL.md`](../scaffold-exercises/SKILL.md) —— 配合本讲的习题集与解答。
