---
name: teach-from-paper
description: 把一篇研究论文变成教学材料——讲次提纲、值得讲的 3-5 个结果（含直觉）、可交给 `/create-lecture` 的幻灯片骨架、讨论题，以及习题简报。端到端读完论文，并对准指定的受众层级。当用户说 "turn this paper into a lecture"、"teach from this paper"、"build slides from this PDF"、"make teaching materials from X"、"I'm presenting this paper to my class" 时使用。
description_zh: 把一篇研究论文变成教学材料——讲次提纲、值得讲的 3-5 个结果（含直觉）、可交给 `/create-lecture` 的幻灯片骨架、讨论题，以及习题简报。端到端读完论文，并对准指定的受众层级。当用户说 "turn this paper into a lecture"、"teach from this paper"、"build slides from this PDF"、"make teaching materials from X"、"I'm presenting this paper to my class" 时使用。
argument-hint: "[paper-path] [--level undergrad|phd|seminar] [--minutes N] [--no-exercises]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]
---

# 从论文出发讲课

把一篇研究论文整理成可以直接使用的教学包，包括讲次提纲、值得讲解的结果及其直觉、幻灯片骨架、讨论题和习题简报。交付的是提纲与简报，**不是**成型课件。幻灯片骨架可直接交给 `/create-lecture`，习题简报则交给 `/scaffold-exercises`。

## 何时使用

- 你有一篇论文（PDF、`.tex`、`.md`），准备用于一节课、一次读书会或一场求职演练报告。
- 你需要提炼论文中适合教学的内容，并针对特定层级讲解，而不是只做泛泛的摘要。
- 你在为课件制定*计划*，准备让 `/create-lecture` 负责起草。

本技能不用于跨多篇论文的文献综述（用 `/lit-review`）、评判论文正确性（用 `/review-paper`）或起草实际的 Beamer 幻灯片（用 `/create-lecture`）。

## 输入

从 `$ARGUMENTS` 解析一个必填论文路径与下述选项，将路径赋给命名变量 `paper_path`，不要读取 shell 的位置参数。校验 `paper_path` 是已存在、可读的文件，且扩展名为 `.pdf`、`.tex`、`.qmd`、`.md` 或 `.txt`；缺少路径、路径无效、出现额外位置参数或未知选项时，停止并报告。`--level` 只接受 `undergrad`、`phd` 或 `seminar`，`--minutes` 必须是正整数，否则同样停止并报告。

| 格式 | 怎么读 |
| --- | --- |
| `.tex`、`.qmd`、`.md`、`.txt` | 直接用 `Read` 工具读。 |
| `.pdf` | `TMP=$(mktemp -d)/paper.txt && pdftotext "$paper_path" "$TMP"`（poppler-utils），然后用 Read/Grep 读 `"$TMP"`。 |

如果文本抽取失败或工具缺失，请向用户索要纯文本版本并停下。扫描版或部分扫描的 PDF 即使退出码为 0，也可能抽出空白页。因此，要比较 `pdfinfo "$paper_path" | grep Pages` 显示的总页数与实际返回文字的页数（`awk 'BEGIN{RS="\f"} NF{n++} END{print n+0}' "$TMP"`）。空白页应直接用 Read 读取原件，或向用户索要文本版本；如果仍在缺少这些页面的情况下继续，必须说明哪些页没有读到。完成后删除抽取副本（`rm -rf "$(dirname "$TMP")"`），因为它是文档的纯文本拷贝。整篇论文都要进入上下文窗口（1M）；先端到端读完，再提取教学要点，不要只看摘要就猜测全文。

## 阶段

### Phase 0：读论文 + 确定受众层级（开始前检查报告）

先从头到尾读完论文，再确定受众层级和时间预算。用户提供了 `--level` / `--minutes` 就直接使用，否则只询问一次。提取教学要点前，先给出开始前检查报告：

```markdown
## Pre-Flight Report
**Paper:** [title, authors, year]
**One-line thesis:** [the paper's central claim in your words]
**Audience level:** undergrad | phd | seminar   (drives notation depth + which proofs survive)
**Time budget:** N minutes (~N/2 slides)
**Prerequisites assumed:** [concepts students must already have]
**Running example candidate:** [the paper's application that can thread the lecture]
```

请用户用一句话确认层级和主旨后再继续。层级会决定后续所有取舍：本科课保留直觉、删去证明；PhD 课保留识别假设和一处关键推导；研讨课优先交代「贡献 vs 文献」的框定。

### Phase 1：抽出可教内核 + 直觉

1. 找出论文中**值得讲的 3-5 个结果**。不必覆盖每个命题，重点是学生课后应该记住的内容。优先考虑头条结果、支撑其可信度的识别假设，以及一处意外发现或局限。
2. 对每个结果，记录**形式化陈述**（按受众层级简化）、**直觉**（不用代数，一口气说明为什么成立）和**失效模式**（何时不成立）。
3. 将论文记号转换成适合教学的表达，并标出可能让学生困惑的符号冲突。
4. 区分**方法**（作者如何得到结果）与**结论**（我们现在相信什么）。学生容易混淆两者，讲课时必须分清。

### Phase 2：搭讲课提纲 + 幻灯片骨架

按「动机 → 设定 → 关键结果 → 方法 → 结论」组织讲授顺序，再按时间预算生成幻灯片骨架，约 2 分钟/页。每条骨架只写标题、一行内容注记和图/示意占位符，足以让 `/create-lecture` 起草即可，不要写成散文。结构要遵守项目的教学法不变量：形式化之前先交代动机，每个定义附近配一个算例，每个幕间配一页过渡。

### Phase 3：讨论题 + 习题简报

1. 按理解 → 应用 → 批评（「这个识别在哪里会失效？」）的深度，写 **4-6 道讨论题**，难度与受众层级相符。
2. 写一份**习题简报**，勾勒 2-4 道题，每题包括题干、训练的能力和期望答案形态，**不写**完整解答。将它交给 `/scaffold-exercises`，由后者补全题目、数据与答案册。指定 `--no-exercises` 时跳过此项。

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

- 在聊天中展示教学包，并确认实际写入的文件路径。
- 明确说明两个交接：「幻灯片骨架已就绪——运行 `/create-lecture [Topic]`。习题简报已就绪——运行 `/scaffold-exercises`。」
- 如果受众层级始终未获确认，**不要**交付；层级判断错误会让整份课件白做。此时应停下询问。

## 参数

- `--level` —— `undergrad` | `phd` | `seminar`。决定记号深度、保留哪些证明以及问题难度。省略时会交互式询问。
- `--minutes` —— 目标讲次长度；幻灯片页数大致为 `--minutes`/2。
- `--no-exercises` —— 跳过 Phase 3 的习题简报（保留讨论题）。

## 交叉引用

- `/create-lecture` —— 读取 Phase 2 的幻灯片骨架，起草实际的 Beamer 课件。见 [`.codebuddy/skills/create-lecture/SKILL.md`](../create-lecture/SKILL.md)。
- `/review-paper` —— 如果不确定结果是否站得住，在开讲*之前*评判论文的正确性。见 [`.codebuddy/skills/review-paper/SKILL.md`](../review-paper/SKILL.md)。
- `/lit-review` —— 用于把论文放进相关文献中，而不是深入讲解一篇论文。见 [`.codebuddy/skills/lit-review/SKILL.md`](../lit-review/SKILL.md)。
- 习题简报（Phase 3 写出；输出的第 5 节）是 `/scaffold-exercises` 的输入契约，由它补全习题集；本技能只负责简报。

## 本技能不做什么

- **不**起草成型幻灯片，这由 `/create-lecture` 负责。幻灯片骨架只是提纲，不是 Beamer。
- **不**写完整的习题解答，习题简报只是交给 `/scaffold-exercises` 的草图。
- **不**核验论文是否正确；如果结果的有效性存疑，应搭配 `/review-paper`。
- **不**读取多篇论文，也不综述整个领域；每次只把一篇论文整理成一个教学包。
