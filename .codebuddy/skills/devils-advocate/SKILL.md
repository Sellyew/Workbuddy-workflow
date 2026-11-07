---
name: devils-advocate
description: 围绕幻灯片的教学法选择提出 5-7 个对抗式问题，检查顺序、先修要求、认知负荷和动机。用户说 "devil's advocate"、"poke holes in this deck"、"push back on my slides"、"stress-test the design"、"what would a skeptical student ask?"、"唱反调"、"挑战这套幻灯片"、"挑挑教学设计的毛病" 或 "持怀疑态度的学生会怎么问" 时使用。只读提出挑战及建议，并总结优点与结论，比 `/pedagogy-review` 更轻量。
description_zh: 围绕幻灯片的教学法选择提出 5-7 个对抗式问题，检查顺序、先修要求、认知负荷和动机。用户说 "devil's advocate"、"poke holes in this deck"、"push back on my slides"、"stress-test the design"、"what would a skeptical student ask?"、"唱反调"、"挑战这套幻灯片"、"挑挑教学设计的毛病" 或 "持怀疑态度的学生会怎么问" 时使用。只读提出挑战及建议，并总结优点与结论，比 `/pedagogy-review` 更轻量。
argument-hint: "[Lecture filename]"
allowed-tools: ["Read", "Grep", "Glob"]
---

# 魔鬼代言人审读

批判性地检查幻灯片，用 5-7 个具体教学法问题挑战其设计。

**只读：** 本技能只读取幻灯片和规则，提出挑战及建议，并总结优点与结论，绝不修改文件。

**理念：** 通过积极对话，尽可能改进呈现方式。

---

## 准备

1. **读目标文件**，即被挑战的那一讲
2. **读知识库**，查看 `.codebuddy/rules/` 中的记号约定和叙事弧线
3. 如适用，**读相邻讲次**，检查叙事是否连贯

---

## 挑战类别

从以下类别生成 5-7 条挑战：

### 1. 顺序挑战

> 「如果我们先讲 X 再讲 Y，学生会不会理解得更好？」

### 2. 先修挑战

> 「讲到这里时，学生是否具备理解这套记号所需的背景？」

### 3. 缺口挑战

> 「给出这个形式化证明前，是否应该先提供一个直观例子？」

### 4. 替代呈现挑战

> 「这个概念还有另外 2 种可视化或呈现方式。」

### 5. 记号冲突挑战

> 「这个符号与前面讲次中的用法冲突。」

### 6. 认知负荷挑战

> 「这页引入了太多新符号，能否拆开？」

### 7. 成书视角挑战

> 「如果这一节要改写成书中一章，它能独立成立吗？」

---

## 输出格式

```markdown
# Devil's Advocate: [Lecture Title]

## Challenges

### Challenge 1: [Category] — [Short title]
**Question:** [The specific pedagogical question]
**Why it matters:** [What could go wrong]
**Suggested resolution:** [Specific action]
**Slides affected:** [Numbers or titles]
**Severity:** [High / Medium / Low]

[Repeat for 5-7 challenges]

## Summary Verdict
**Strengths:** [2-3 things done well]
**Critical changes:** [0-2 changes before teaching]
**Suggested improvements:** [2-3 nice-to-have changes]
```

---

## 原则

- **要具体：** 引用确切幻灯片和记号
- **要建设性：** 每条挑战都附一个建议的解决办法
- **要诚实：** 如果幻灯片确实做得好，就明确肯定
- **排优先级：** 记号冲突优先于错失的比喻
- **像学生那样思考：** 他们会在哪里失去思路？
