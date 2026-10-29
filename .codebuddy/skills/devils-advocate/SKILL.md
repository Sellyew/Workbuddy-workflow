---
name: devils-advocate
description: 对一套幻灯片的教学法选择提出 5-7 个对抗式问题——顺序、先修要求、认知负荷、动机。用户说 "devil's advocate"、"poke holes in this deck"、"push back on my slides"、"stress-test the design"、"what would a skeptical student ask?" 时使用。只读；只提出问题，逼你重新想。比 `/pedagogy-review` 更轻。
description_zh: 对一套幻灯片的教学法选择提出 5-7 个对抗式问题——顺序、先修要求、认知负荷、动机。用户说 "devil's advocate"、"poke holes in this deck"、"push back on my slides"、"stress-test the design"、"what would a skeptical student ask?" 时使用。只读；只提出问题，逼你重新想。比 `/pedagogy-review` 更轻。
argument-hint: "[Lecture filename]"
allowed-tools: ["Read", "Grep", "Glob"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# 魔鬼代言人审读

批判性地检查一套幻灯片，用 5-7 个具体的教学法问题挑战它的设计。

**理念：**「我们通过积极的对话达成尽可能好的呈现。」

---

## 准备

1. **读目标文件**（被挑战的那一讲）
2. **读知识库**：`.codebuddy/rules/` 里的记号约定与叙事弧线
3. 如适用，**读相邻讲次**看叙事是否连贯

---

## 挑战类别

从下面这些类别里生成 5-7 条挑战：

### 1. 顺序挑战
> 「如果我们先讲 X 再讲 Y，学生会不会理解得更好？」

### 2. 先修挑战
> 「讲到这儿，学生具备这套记号所需的背景吗？」

### 3. 缺口挑战
> 「这个形式化证明之前，是不是该先给一个直观的例子？」

### 4. 替代呈现挑战
> 「这个概念还有另外 2 种可视化／呈现方式。」

### 5. 记号冲突挑战
> 「这个符号与前面讲次里的用法冲突。」

### 6. 认知负荷挑战
> 「这页新符号太多了。能不能拆开？」

### 7. 成书视角挑战
> 「如果这一节要变成书里的一章，它立得住吗？」

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

- **要具体：**引用确切的幻灯片与记号
- **要建设性：**每条挑战都附一个建议的解决办法
- **要诚实：**如果这套幻灯片确实好，就说好
- **排优先级：**记号冲突 > 错失的比喻
- **像学生那样想：**他们在哪里会走丢？
