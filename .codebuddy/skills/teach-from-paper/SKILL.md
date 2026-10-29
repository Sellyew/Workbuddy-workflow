---
name: teach-from-paper
description: 把一篇研究论文变成教学材料——讲次提纲、值得讲的 3-5 个结果（含直觉）、可交给 `/create-lecture` 的幻灯片骨架、讨论题，以及习题简报。端到端读完论文，并对准指定的受众层级。当用户说 "turn this paper into a lecture"、"teach from this paper"、"build slides from this PDF"、"make teaching materials from X"、"I'm presenting this paper to my class" 时使用。
description_zh: 把一篇研究论文变成教学材料——讲次提纲、值得讲的 3-5 个结果（含直觉）、可交给 `/create-lecture` 的幻灯片骨架、讨论题，以及习题简报。端到端读完论文，并对准指定的受众层级。当用户说 "turn this paper into a lecture"、"teach from this paper"、"build slides from this PDF"、"make teaching materials from X"、"I'm presenting this paper to my class" 时使用。
argument-hint: "[paper-path] [--level undergrad|phd|seminar] [--minutes N] [--no-exercises]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]
---

# 从论文出发讲课

把一篇研究论文变成可直接开工的教学包：讲次提纲、一份可教结果短名单（把直觉讲透）、幻灯片骨架、讨论题，以及习题简报。交付物是提纲与简报——**不是**成型的课件；幻灯片骨架的形态就是为了直接交给 `/create-lecture`，习题简报则交给 `/scaffold-exercises`。

## 何时使用

- 你有一篇论文（PDF、`.tex`、`.md`），也有一个讲它的场合——一节课、一次读书会、一场求职演练报告。
- 你想抽出可教的内核并对准某个层级，而不是要一份泛泛的摘要。
- 你在为一份课件准备*计划*，希望由 `/create-lecture` 来做起草。

不用于：跨多篇论文的文献综述（用 `/lit-review`）；评判论文的正确性（用 `/review-paper`）；起草实际的 Beamer 幻灯片（用 `/create-lecture`）。

## 输入

- `$0` —— 论文路径。

| 格式 | 怎么读 |
| --- | --- |
| `.tex`、`.qmd`、`.md`、`.txt` | 直接用 `Read` 工具读。 |
| `.pdf` | `TMP=$(mktemp -d)/paper.txt && pdftotext "$0" "$TMP"`（poppler-utils），然后用 Read/Grep 读 `"$TMP"`。 |

若抽取失败或工具缺失，向用户要一个纯文本版本并停下。扫描版或部分扫描的 PDF 会以退出码 0 抽出空白页，所以还要把 `pdfinfo "$0" | grep Pages` 与确实返回了文字的页数（`awk 'BEGIN{RS="\f"} NF{n++} END{print n+0}' "$TMP"`）作比较；任何空白页都用 Read 直接读，或要一个文本版本；若你带着这些空白页继续，要说明哪几页没有读。做完之后删掉抽出的副本（`rm -rf "$(dirname "$TMP")"`）：它是一份文档的纯文本拷贝。整篇论文都进上下文窗口（1M）——抽取之前先端到端读完；不要扫一眼摘要就猜。

## 阶段

### Phase 0：读论文 + 确定受众层级（起飞前检查报告）

从头到尾读完论文。然后确定受众层级与时间预算——给了 `--level` / `--minutes` 就用，否则问一次。抽取之前回显一份起飞前检查报告：

```markdown
## Pre-Flight Report
**Paper:** [title, authors, year]
**One-line thesis:** [the paper's central claim in your words]
**Audience level:** undergrad | phd | seminar   (drives notation depth + which proofs survive)
**Time budget:** N minutes (~N/2 slides)
**Prerequisites assumed:** [concepts students must already have]
**Running example candidate:** [the paper's application that can thread the lecture]
```

在层级 + 主旨上取得一句认可，再往下走。层级决定下游的一切：本科保留直觉、砍掉证明；PhD 保留识别假设与一处关键推导；研讨课把「贡献 vs 文献」的框定摆到最前。

### Phase 1：抽出可教内核 + 直觉

1. 找出论文里**值得讲的 3-5 个结果**——不是每个命题，而是学生离开时该记住的那些。优先选头条结果、让它可信的那个识别假设，以及一处意外或局限。
2. 对每个结果，记录：**形式化陈述**（按受众层级修剪）、**直觉**（一口气说清为什么成立，不用代数）、**失效模式**（什么时候不成立）。
3. 把论文的记号映射成可教的东西；标出任何学生会被绊住的符号冲突。
4. 把**方法**（他们怎么得到结果）与**结论**（我们现在相信什么）分开——学生会把这两者混为一谈；讲次绝不能混。

### Phase 2：搭讲课提纲 + 幻灯片骨架

产出「动机 → 设定 → 关键结果 → 方法 → 结论」的弧线，再产出一份匹配时间预算的幻灯片骨架（约 2 分钟/页）。骨架的每一条都是标题 + 一行内容注记 + 图/示意占位符——够 `/create-lecture` 起草即可，不放散文。在形态上遵守项目的教学法不变量：形式化之前先动机，每个定义附近配一个算例，每个幕间配一页过渡。

### Phase 3：讨论题 + 习题简报

1. 写 **4-6 道讨论题**，按深度分级：理解 → 应用 → 批评（「这个识别在哪里会失效？」）。对准层级。
2. 写一份**习题简报**——勾勒 2-4 道题（题干 + 它训练什么能力 + 期望答案形态），**不是**完整解答。这是交给 `/scaffold-exercises` 的交接物，由它把题目、数据与答案册补全。若指定 `--no-exercises` 则跳过。

## 输出 / 报告格式

写入 `quality_reports/teach_from_paper_[sanitized-title].md`：

```markdown
# Teaching Package: [Paper Title]
**Audience:** [level] · **Budget:** [N min] · **Date:** [YYYY-MM-DD]

## 1. Lecture Outline
Motivation → Setup → Key Result → Method → Takeaways  (one line each)

## 2. Results Worth Presenting
### R1 — [name]
- **Statement:** … · **Intuition:** … · **Breaks when:** …
[R2..R5]

## 3. Slide Skeleton  (→ /create-lecture)
| # | Title | Content note | Figure/diagram |

## 4. Discussion Questions
1. [comprehension] … 5. [critique] …

## 5. Exercise Brief  (→ /scaffold-exercises)
- **E1:** [prompt] — drills [skill] — answer shape: [form]
```

## 退出行为

- 在聊天里呈现教学包，并确认写入了哪个文件路径。
- 明确点名两个交接：「幻灯片骨架已就绪——运行 `/create-lecture [Topic]`。习题简报已就绪——运行 `/scaffold-exercises`。」
- 若受众层级始终没被确认，**不要**交付——一份层级押错的课件是白做工。停下并询问。

## 参数

- `--level` —— `undergrad` | `phd` | `seminar`。决定记号深度、哪些证明保留、以及问题难度。省略时会交互式询问。
- `--minutes` —— 目标讲次长度；幻灯片页数大致为 `--minutes`/2。
- `--no-exercises` —— 跳过 Phase 3 的习题简报（保留讨论题）。

## 交叉引用

- `/create-lecture` —— 消费 Phase 2 的幻灯片骨架，起草实际的 Beamer 课件。见 [`.codebuddy/skills/create-lecture/SKILL.md`](../create-lecture/SKILL.md)。
- `/review-paper` —— 若你不确定结果是否站得住，在开讲*之前*评判论文的正确性。见 [`.codebuddy/skills/review-paper/SKILL.md`](../review-paper/SKILL.md)。
- `/lit-review` —— 用于把论文放进众多文献之中，而不是深讲一篇。见 [`.codebuddy/skills/lit-review/SKILL.md`](../lit-review/SKILL.md)。
- 习题简报（Phase 3 写出；输出的第 5 节）是 `/scaffold-exercises` 的输入契约，由它把习题集补全；本技能止步于简报。

## 本技能不做什么

- **不**起草成型幻灯片——那是 `/create-lecture`。幻灯片骨架是提纲，不是 Beamer。
- **不**写完整的习题解答——习题简报是给 `/scaffold-exercises` 的草图。
- **不**核验论文是否正确——若结果的有效性存疑，与 `/review-paper` 搭配。
- **不**读多篇论文，也不综述一个领域——一篇论文进，一个教学包出。
