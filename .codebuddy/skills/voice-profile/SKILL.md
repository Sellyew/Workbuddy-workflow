---
name: voice-profile
description: 从你自己过往的论文中提取一份书面文风画像，再用它让新草稿读起来像你。通过子代理逐份读取语料，在磁盘上产出一份可复用的画像（词汇、句子节奏、你怎么开头和收尾、模糊限定的习惯、刻意的怪癖），并据此审计一份草稿。用户说 "make this sound like me"、"match my voice"、"profile my writing"、"why does this draft not sound like my papers"，或在起草将署其名的文字之前使用。是 /humanize 的正面补充，后者只检测 AI 痕迹。
description_zh: 从你自己过往的论文中提取一份书面文风画像，再用它让新草稿读起来像你。通过子代理逐份读取语料，在磁盘上产出一份可复用的画像（词汇、句子节奏、你怎么开头和收尾、模糊限定的习惯、刻意的怪癖），并据此审计一份草稿。用户说 "make this sound like me"、"match my voice"、"profile my writing"、"why does this draft not sound like my papers"，或在起草将署其名的文字之前使用。是 /humanize 的正面补充，后者只检测 AI 痕迹。
argument-hint: "[corpus directory | --audit draft.tex]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
disallowed-tools: ["Edit", "MultiEdit"]
disable-model-invocation: true
metadata:
  protocol: evidence-grounding
---

# 文风画像 —— 朝着某个东西写，而不只是躲开痕迹

[`/humanize`](../humanize/SKILL.md) 是**负向**的：它找出 AI 痕迹，告诉你该删什么。那样留下的草稿只是*没那么糟*。

这是**正向**的：一份关于*你*实际怎么写下去的书面描述，从你自己已发表的作品里提取，于是草稿可以对着一个目标来衡量，而不是对着一张禁忌清单。

> **它不做什么。** 文风画像让文字读起来像你的文字。它**不能**让模型生成的文本在神经检测器眼里不再像模型生成 —— 任何 LLM 对自己输出施加的加工都做不到这件事。见 [`writing-with-ai.md`](../../rules/writing-with-ai.md)。用它以自己的语域把文章写好；承重的句子要自己动笔。

## 构建画像

### 1. 汇集语料，并清点数量

3 到 12 篇**你自己**的、你是主要作者的作品。已发表论文最好 —— 它们经过编辑。若你在多种体裁写作（论文、审稿报告、基金申请、教学笔记），要混合取材；画像应当注明你的语域在哪里发生变化。

```bash
find <corpus-dir> -maxdepth 1 \( -name '*.pdf' -o -name '*.tex' \) | wc -l
```

*（用 `find`，不用 glob —— 在 zsh 里未匹配的 glob 会让整条命令中止，报出 0，正好毁掉这一步本就是要拿到的那个计数。）*

**先清点再开工。** 十一篇的语料和四篇是不同的活，而做到一半才发现这件事，正是一个会话被重置的方式。

### 2. 每份文档一个子代理 —— 绝不把整个语料载入一个上下文

按 [`pdf-processing.md`](../../rules/pdf-processing.md)：在独立上下文中**每份文档一个子代理**。每个只读**自己那个文件**，按下方的固定 schema 写一份约 300 词的笔记到 `notes/voice/<name>.md`，并**只返回文件名**。

主会话随后只读这些笔记。一次性载入整个语料，已经反复导致会话在部分工作已丢失之后被重置。

**单文档笔记 schema** —— 每次都是同样六个标题，好让综合环节能相互比较：

```
## Lexicon      words and phrases used repeatedly; words conspicuously avoided
## Rhythm       typical sentence length; variance; where long sentences appear
## Openings     how sections and paragraphs begin; how the paper opens
## Transitions  the actual connectives used, verbatim, with rough frequency
## Hedging      how uncertainty is expressed; how strong claims are made
## Quirks       anything distinctive — punctuation habits, first person, humour, footnotes
```

### 3. 综合，并标出什么是*稳定*的

只读笔记。一个特征只有在语料**大多数**篇目里都出现时，才配进画像，而不是因为某一篇偶然这么写过一次。能记频率就记频率：*"'note that' appears in 7 of 9 papers; 'delve' appears in none."*

写到仓库根的 `voice-profile.md`（已在该仓库卫生门禁的白名单里）。包含：

- **标志性词汇**与**避用清单** —— 作者明显不用的词。
- **句子节奏**，带一个数字：中位长度，以及长句落在哪里。
- **结构习惯** —— 引言如何搭建、贡献段落在什么位置、结果如何框定。
- **模糊限定的语域** —— 作者实际的校准用语，通常比模型的默认更窄。
- **刻意的怪癖，并标注为刻意。** *"Uses em-dashes frequently and on purpose"* 能阻止 `/humanize` 把一个习惯当成 AI 痕迹报出来。
- **语域按体裁的迁移点。**

### 4. 接进工作流

`/humanize` 在存在 `voice-profile.md` 时读取它，并**尊重已记录的偏好** —— 一个你声明为刻意的怪癖就不再是发现。让起草工作在动笔前对着画像，而不是事后再对。

## 审计一份草稿

传入 `--audit` 加文件名，即可把现有草稿与画像比对，而不是构建一份画像：

```
/voice-profile --audit main.tex
```

逐节报告：与画像的距离，并附具体证据 —— 超出你惯用范围的词汇、比你基线更密的模糊限定、你不用的过渡词、已经变平的句子节奏。**每条发现都引用它所违反的那一行画像**，所以它是推导而非品味。

**只读。** 自动改写文字会降低其质量、引入新的痕迹，而且改变不了检测器看到的东西。报告说清哪里、为什么；改由作者自己动手。

## 参数

| 参数 | 作用 |
|---|---|
| `--audit` | 传入文件名：把现有草稿与画像比对，而不是构建一份画像。 |

## 反面模式

- **给不是你主笔的合著作品做画像。** 你会把别人的文风提取出来。
- **把画像当规则手册。** 它描述你做过什么，不是你必须做什么。文风会变；写了几篇新论文之后重新做一次画像。
- **用 AI 辅助的草稿来构建它。** 画像会把模型的语域编码成你的 —— 语料必须是你自己写的东西。
- **用它去通过检测器。** 它是写作辅助，不是洗稿步骤。若某个发表场合要 AI 使用声明，就写一份（[`/submission-disclosures`](../submission-disclosures/SKILL.md)）。

## 交叉引用

- [`writing-with-ai.md`](../../rules/writing-with-ai.md) —— 可读性与溯源的区分，以及面向人的可读标准
- [`/humanize`](../humanize/SKILL.md) —— 负向的那一半；画像存在时会读它
- [`/proofread`](../proofread/SKILL.md) —— 语法与一致性，是另一只透镜
- [`pdf-processing.md`](../../rules/pdf-processing.md) —— 每份文档一个子代理的模式
