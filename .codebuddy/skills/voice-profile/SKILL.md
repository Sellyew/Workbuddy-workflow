---
name: voice-profile
description: 从你自己过往的论文中提取一份书面文风画像，再用它让新草稿读起来像你。通过子代理逐份读取语料，在磁盘上产出一份可复用的画像（词汇、句子节奏、你怎么开头和收尾、模糊限定的习惯、刻意的怪癖），并据此审计一份草稿。用户说 "make this sound like me"、"match my voice"、"profile my writing"、"why does this draft not sound like my papers"，或在起草将署其名的文字之前使用。是 /humanize 的正面补充，后者只检测 AI 痕迹。
description_zh: 从你自己过往的论文中提取一份书面文风画像，再用它让新草稿读起来像你。通过子代理逐份读取语料，在磁盘上产出一份可复用的画像（词汇、句子节奏、你怎么开头和收尾、模糊限定的习惯、刻意的怪癖），并据此审计一份草稿。用户说 "make this sound like me"、"match my voice"、"profile my writing"、"why does this draft not sound like my papers"，或在起草将署其名的文字之前使用。是 /humanize 的正面补充，后者只检测 AI 痕迹。
argument-hint: "[corpus directory | --audit draft.tex]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
disable-model-invocation: true
metadata:
  protocol: evidence-grounding
---

# 文风画像 —— 朝着某个东西写，而不只是躲开痕迹

[`/humanize`](../humanize/SKILL.md) 从**负向**入手：找出 AI 痕迹，告诉你该删什么，但删完不等于草稿已经像你的文字。

本技能从**正向**入手：根据你自己已发表的作品，描述*你*实际如何写作。这样，草稿就有了可以对照的目标，而不只是一张禁忌清单。

> **它不做什么。** 文风画像可以让文字更接近你的文风，却**不能**让模型生成的文本在神经检测器眼中不再像模型生成。任何 LLM 加工自身输出的方式都做不到这一点，详见 [`writing-with-ai.md`](../../rules/writing-with-ai.md)。请用画像改善自己的语域；承担论证的句子仍要自己写。

## 构建画像

### 1. 汇集语料，并清点数量

选取 3 到 12 篇由**你主笔**的作品，优先选择经过编辑的已发表论文。如果你写多种体裁（论文、审稿报告、基金申请、教学笔记），语料也应覆盖这些体裁，并在画像中注明语域如何随体裁变化。

```bash
find <corpus-dir> -maxdepth 1 \( -name '*.pdf' -o -name '*.tex' \) | wc -l
```

*（这里用 `find`，不用 glob。在 zsh 中，未匹配的 glob 会让整条命令中止并报 0，反而毁掉这一步要取得的计数。）*

**先清点再开工。** 处理十一篇与处理四篇所需的工作不同；做到一半才发现语料规模，可能导致会话重置。

### 2. 每份文档一个子代理 —— 绝不把整个语料载入一个上下文

按 [`pdf-processing.md`](../../rules/pdf-processing.md) 的要求，在独立上下文中**为每份文档启动一个子代理**。每个子代理只读**分配给自己的文件**，按下方的固定 schema 将约 300 词的笔记写入 `notes/voice/<name>.md`，并且**只返回文件名**。

主会话随后只读取这些笔记。过去反复出现因一次载入整个语料而重置会话、丢失部分工作的情况。

**单文档笔记 schema** —— 每份笔记都使用同样的六个标题，便于综合时相互比较：

```
## Lexicon      words and phrases used repeatedly; words conspicuously avoided
## Rhythm       typical sentence length; variance; where long sentences appear
## Openings     how sections and paragraphs begin; how the paper opens
## Transitions  the actual connectives used, verbatim, with rough frequency
## Hedging      how uncertainty is expressed; how strong claims are made
## Quirks       anything distinctive — punctuation habits, first person, humour, footnotes
```

### 3. 综合，并标出什么是*稳定*的

综合时只读笔记。一个特征只有出现在语料的**大多数**篇目中，才能写入画像；某一篇偶然出现的写法不算。能统计频率就记录频率，例如：*"'note that' appears in 7 of 9 papers; 'delve' appears in none."*

将画像写到仓库根目录的 `voice-profile.md`，该路径已列入仓库卫生门禁白名单。画像包括：

- **标志性词汇**与**避用清单**，后者记录作者明显不用的词。
- **句子节奏**，给出中位长度等数字，并说明长句通常出现在哪里。
- **结构习惯**，包括引言如何展开、贡献段落的位置、结果如何框定。
- **模糊限定的语域**，记录作者实际使用的校准用语；其范围通常比模型默认用语更窄。
- **刻意的怪癖，并明确标为刻意。** 例如 *"Uses em-dashes frequently and on purpose"*，可避免 `/humanize` 把个人习惯误报为 AI 痕迹。
- **语域随体裁变化的位置。**

### 4. 接进工作流

如果 `voice-profile.md` 存在，`/humanize` 会读取它并**尊重其中记录的偏好**。你明确标为刻意的怪癖，不再作为发现报告。起草前就应参考画像，不要等写完才对照。

## 审计一份草稿

传入 `--audit` 和文件名，可以把现有草稿与画像比对，而不构建新画像：

```
/voice-profile --audit main.tex
```

按节报告草稿与画像的差距，并给出具体证据，例如超出你惯用范围的词汇、比基线更密集的模糊限定、你不使用的过渡词、趋于单一的句子节奏。**每条发现都要引用画像中被违反的那一行**，让判断有据可查，而不是只凭品味。

**只读。** 自动改写可能降低文字质量、引入新的痕迹，也改变不了检测器看到的内容。报告负责说明位置和原因，作者负责修改。

## 参数

| 参数 | 作用 |
|---|---|
| `--audit` | 传入文件名：把现有草稿与画像比对，而不是构建一份画像。 |

## 反面模式

- **给不是你主笔的合著作品做画像。** 这样提取到的可能是别人的文风。
- **把画像当规则手册。** 画像描述你过去的写法，不规定你必须怎么写。文风会变化，写完几篇新论文后应重新构建画像。
- **用 AI 辅助的草稿来构建它。** 这会把模型的语域误记成你的语域；语料必须由你自己撰写。
- **用它去通过检测器。** 这是写作辅助，不是洗稿步骤。发表场所要求 AI 使用声明时，就应提供声明（[`/submission-disclosures`](../submission-disclosures/SKILL.md)）。

## 交叉引用

- [`writing-with-ai.md`](../../rules/writing-with-ai.md) —— 可读性与溯源的区分，以及面向人的可读标准
- [`/humanize`](../humanize/SKILL.md) —— 负向的那一半；画像存在时会读它
- [`/proofread`](../proofread/SKILL.md) —— 语法与一致性，是另一只透镜
- [`pdf-processing.md`](../../rules/pdf-processing.md) —— 每份文档一个子代理的模式
