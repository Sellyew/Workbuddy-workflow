---
name: slide-excellence
description: 多代理综合性幻灯片审查（视觉 + 教学法 + 校对，另按条件加上 TikZ / 一致性 / 实质内容）。用户说 "full review"、"excellence pass"、"comprehensive check"、"review everything"、"pre-release review"、"slide excellence"，或在授课 / 交付一套幻灯片之前使用。扇出（fan-out）包装器——只要单一透镜，请直接用 `/visual-audit`、`/pedagogy-review` 或 `/proofread`。
argument-hint: "[QMD or TEX filename] [--fast] [--skip-substance | --acknowledge-template-domain-reviewer]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent", "Task"]
context: fork
---

# 幻灯片卓越审查

对讲稿幻灯片做一次多维度的综合审查。多个代理各自独立分析该文件，然后归并（reduce）结果。

> **我要的是哪一个幻灯片审查技能？**
>
> - **`/slide-excellence`**（本技能）—— 多代理扇出（视觉 + 教学法 + 校对，另按条件加上 TikZ / 一致性 / 实质内容）。最适合**授课前**或**交付前**的检查。
> - **`/visual-audit`** —— 单一透镜，只看版式/溢出/字体/间距。快。
> - **`/pedagogy-review`** —— 单一透镜，叙事/前备知识/示例演算/记号。
> - **`/proofread`** —— 单一透镜，语法/错字/溢出/术语。
> - **`/qa-quarto`** —— 对抗式 Beamer ↔ Quarto 一致性（批评者-修复者循环）。
> - **`/devils-advocate`** —— 5-7 个尖锐质询，不是完整审查。

**重要：** 本编排器做的是**条件式**派发——它只启动那些对给定文件真能产出有用结果的子代理。它不会在一个零 TikZ 的文件上跑 `tikz-reviewer`，也不会在没有对应文件的幻灯片上跑 `quarto-critic`。

## Step 1：确定文件

从 `$ARGUMENTS` 中解析出文件名。在 `Quarto/` 或 `Slides/` 中解析路径。

判断文件类型：

- `.tex` → Beamer
- `.qmd` → Quarto
- `.md` → Markdown 幻灯片

## Step 2：起飞前检查——探测条件

在启动任何代理之前，先探明该文件，确定哪些审查有意义：

```bash
FILE="$resolved_path"

# Has TikZ diagrams?
has_tikz=$(grep -c '\\begin{tikzpicture}' "$FILE" 2>/dev/null); has_tikz=${has_tikz:-0}

# For .qmd: is there a paired .tex in Slides/?
has_tex_pair="false"
if [[ "$FILE" == *.qmd ]]; then
  base="$(basename "$FILE" .qmd)"
  # Common Beamer suffixes: _Topic, _Lecture, exact match
  for candidate in "Slides/${base}.tex" "Slides/Lecture${base}.tex"; do
    if [ -f "$candidate" ]; then
      has_tex_pair="true"
      tex_pair="$candidate"
      break
    fi
  done
fi

# For .tex: is there a paired .qmd in Quarto/?
has_qmd_pair="false"
if [[ "$FILE" == *.tex ]]; then
  base="$(basename "$FILE" .tex)"
  for candidate in "Quarto/${base}.qmd" "Quarto/${base#Lecture}.qmd"; do
    if [ -f "$candidate" ]; then
      has_qmd_pair="true"
      qmd_pair="$candidate"
      break
    fi
  done
fi

# Measure the Quarto render once — the file itself, or a .tex file's Quarto pair.
# The report goes to Agents A and E. slide-qa exits 0 (clean) or 1 (a finding:
# overflow, clipped content, or a broken asset) with a fresh report, 2 if it could
# not run (it deletes old reports first).
qa_report=""; qa_target=""
if [[ "$FILE" == *.qmd ]]; then qa_target="$FILE"
elif [ "$has_qmd_pair" = "true" ]; then qa_target="$qmd_pair"; fi
if [ -n "$qa_target" ]; then
  quarto render "$qa_target" >/dev/null 2>&1
  "${SLIDE_QA_PYTHON:-python}" scripts/slide-qa.py "$qa_target"
  if [ $? -ne 2 ]; then
    qa_report="quality_reports/audits/slide-qa/$(basename "$qa_target" .qmd)/report.md"
  fi
fi

# Has R code chunks or referenced R scripts?
has_r="false"
if grep -qE '```\{r|source\(.*\.R\)' "$FILE" 2>/dev/null; then
  has_r="true"
fi
```

报告探测结果：

```
File:         path/to/file.tex
Type:         Beamer (.tex)
TikZ blocks:  3
Quarto pair:  Quarto/Lecture2.qmd (found)
R chunks:     none
Slide QA:     quality_reports/audits/slide-qa/Lecture2/report.md (or: could not run — reason)
```

## Step 3：领域审阅者定制检查（`.tex` 必做）

在对 `.tex` 文件启动实质内容审查代理之前，先核实 `.codebuddy/agents/domain-reviewer.md` 是否已针对本项目定制。随附状态的 domain-reviewer 是一个**模板**——原样运行它，产出的只会是"假设都陈述了吗？"这类通用反馈，而不是真正的领域审查。

检测启发式（命中任一条 → 仍是模板）：

- 文件任意位置含标记串 `AUTO-DETECT-TEMPLATE-MARKER`（存在于随附模板中；定制时会被删除/替换）。检测是子串匹配——标记可以跨行。
- 含任一 `<!-- Customize: ... -->` 或 `[Customize: ...]` 占位符（两种形式都会检查）。
- 五个透镜与随附模板措辞完全一致（对着 v1.3.0 标签上的 `.codebuddy/agents/domain-reviewer.md` 做 diff —— 若零行变动，就还是模板）。

若模板标记存在：

```
⚠️  domain-reviewer.md has not been customized for your field.

Running it in its shipped state produces generic checks ("are assumptions
stated?") rather than field-specific review. Options:

  1. Customize .codebuddy/agents/domain-reviewer.md — replace the 5 lenses
     with checks for your field (the file's EXAMPLES block shows two
     disciplines to copy from).
  2. Run slide-excellence with --skip-substance to proceed without the
     substance-review agent. Other reviewers still run.
  3. Run slide-excellence with --acknowledge-template-domain-reviewer to
     proceed anyway (you'll get generic feedback from the substance agent).

```

就此停下，把这些选项返回——本技能运行在分叉上下文中，无法等待答复。不要在未定制的模板上运行 `domain-reviewer`；由用户带上自己选定的参数重新调用。

## Step 4：并行运行审查代理

只启动条件成立的代理：

**幻灯片（`.tex` 或 `.qmd`）常驻：**

- **代理 A：视觉审计**（`slide-auditor`）
  溢出、字体一致性、盒子疲劳、间距、图片。当 `$qa_report` 已设置时（`.qmd`，或带 Quarto 配对件的 `.tex`），把它传进去——实测溢出加截图；若 slide-qa 无法运行，在摘要中说明。
  保存：`quality_reports/[FILE]_visual_audit.md`。

- **代理 B：教学法审查**（`pedagogy-reviewer`）
  13 个教学法模式、叙事、节奏、记号。
  保存：`quality_reports/[FILE]_pedagogy_report.md`。

- **代理 C：校对**（`proofreader`）
  语法、错字、一致性、学术质量、引用。
  保存：`quality_reports/[FILE]_proofread_report.md`。

**条件式：**

- **代理 D：TikZ 审查**（`tikz-reviewer`）—— 仅当 `has_tikz > 0`。
  基于测量的碰撞审计（Bézier、间隙、边界、边距）。
  保存：`quality_reports/[FILE]_tikz_review.md`。

- **代理 E：内容一致性**（`quarto-critic`）—— 仅当该文件有对应件（`has_tex_pair` 或 `has_qmd_pair`）。
  帧数比较、环境一致性、`.tex` ↔ `.qmd` 之间的内容漂移。有 `$qa_report` 时传进去。
  保存：`quality_reports/[FILE]_parity_report.md`。

- **代理 F：R 代码审查**（`r-reviewer`）—— 仅当 `has_r == true`。
  对任何内嵌 R 块或被引用的脚本做代码正确性审查。
  保存：`quality_reports/[FILE]_r_review.md`。

- **代理 G：实质内容审查**（`domain-reviewer`）—— `.tex` 必做，`.qmd` 可选，由 Step 3 门控。
  通过 5 个透镜框架审查领域正确性。
  保存：`quality_reports/[FILE]_substance_review.md`。

**去重：** 若本会话中已有某个技能为该文件产出过报告（例如先跑了 `/proofread`），且该报告比文件更新，就复用它，并列出复用了哪些报告——本技能运行在分叉上下文中，无法停下来询问。要强制全新一轮，把旧报告移出 `quality_reports/`（或 touch 一下幻灯片使其更新），再重新调用。

## Step 5：归并综合摘要（对类型化审查发现做 reduce）

这是**扇出 → 归并**（[`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)）：每个代理按共享 schema（[`orchestration-schemas.md`](../../references/orchestration-schemas.md)）返回 `FINDING` 与 `SCORECARD`，本步骤做的是**把类型化的评分卡叠起来**，而不是用眼睛重读每份报告。总体质量得分是对 CRITICAL/MAJOR/MINOR 计数求和后的门禁判据。（条件式派发意味着被跳过的透镜贡献的是"无审查发现"，而不是拿零分去参与平均。）

只为实际运行过的代理列出小节。

```markdown
# Slide Excellence Review: [Filename]

**File:** [path]
**Type:** [Beamer / Quarto / Markdown]
**Detected:** TikZ=N | pair=[path or none] | R=[yes/no]
**Agents spawned:** [A, B, C, D, G] (skipped: E [no pair], F [no R])

## Overall Quality Score: [EXCELLENT / GOOD / NEEDS WORK / POOR]

| Dimension | Critical (`blocker`) | Major | Minor | Score/10 |
|-----------|----------|--------|-----|-----|
| Visual/Layout | | | | |
| Pedagogical | | | | |
| Proofreading | | | | |
| TikZ (if ran) | | | | |
| Substance (if ran) | | | | |

### Critical Issues (Immediate Action Required)
### Major Issues (Next Revision)
### Recommended Next Steps
```

## Step 6：报告 token / 时间预算

完成后，打印实际启动了什么：

```
Spawned N agents[; token usage: actual figure, if the harness reports it].
For cost-conscious reviews, run individual subagent skills directly
(/proofread, /visual-audit, /pedagogy-review).
```

## 参数一览

| 参数 | 作用 |
|---|---|
| `--skip-substance` | 不启动代理 G（domain-reviewer）。若你还没定制 domain-reviewer.md，这很有用。 |
| `--acknowledge-template-domain-reviewer` | 仍然用未定制的 domain-reviewer 继续；你接受实质内容审查将是通用的。 |
| `--fast` | 只启动一个综合代理直接读文件，而不用并行子代理。更便宜但不够彻底。 |

## 质量得分评分细则

| 得分 | Critical（`blocker`） | Major | 含义 |
|-------|----------|--------|---------|
| Excellent | 0 | 0 | 可以开讲 |
| Good | 0 | 1-5 | 先改 major（门禁读作 REVISE） |
| Needs Work | 0-5 | 6+，或任一含 critical | 需要大改——只要有 critical 残留，门禁就阻断 |
| Poor | 6+ | 任意 | 需要重构 |

任何 critical 发现都阻断，不论其他计数如何——与 [`orchestration-schemas.md`](../../references/orchestration-schemas.md) §3 同一门禁判据。

## 为什么条件式派发要紧

一个产不出有用结果的审查者，会消耗 token 和信任：`tikz-reviewer` 在无 TikZ 的幻灯片上什么也不返回，`quarto-critic` 没有配对文件就无对可比，未定制的 `domain-reviewer` 返回的是作者学会无视的"假设都陈述了吗？"式通用反馈。只启动文件用得上的透镜。

## 审查发现要被校验，不只是写下来（v2.5）

本技能的审查者按 [`finding-schema.json`](../../references/finding-schema.json) 中机器可校验的契约发出审查发现。报告是 JSON **数组**。

**在花审查功夫之前先对承载做冒烟测试**——一次扇出若干审查者却写不出合法报告的运行，等于整轮白费：

```bash
echo '[]' | python scripts/validate-findings.py
```

审查代理是只读的，所以**由本技能写文件**。对每个审查者的最终回复：把散文报告存到本技能为该审查者指定的报告路径，把它结尾的围栏 `json` 块复制到草稿文件，并在校验时填充 id：

```bash
python scripts/validate-findings.py --fill-ids block.json > <report>.json.tmp \
  && mv <report>.json.tmp <report>.json || rm -f <report>.json.tmp   # exit 0 required; a failed run keeps no file
python scripts/validate-findings.py --check-quotes <report>.json   # each quote must be the file's own text (orchestration-schemas.md §1)
```

一个没返回 `json` 块、或返回的块校验不通过的审查者，等于没审：带着校验器的错误文本重派一次，然后把这个透镜报告为缺失，而不是在没有它的情况下照样归并。

契约强制了什么，以及为什么：

- **`rule`** —— 被违反的、有文档的规则或标准。一条未援引任何规则的发现只是意见，而意见不能给提交设门禁。
- **`failing_case`** —— 一个具体的配置，在该配置下该论断破裂，或确切缺失的那条假设。*"这里可以更清楚"*通不过校验。
- **`id = sha1("<file>:<line>:<locus>")`** —— 确定性，因此跨轮去重是精确的，两次即升级规则是可机械检查的，而不是靠目测。
- **`mechanical`** —— 只有不会改变结果的修复（错字、交叉引用、格式、标签）才为 `true`。对估计目标（estimand）、假设、设定、推断程序、样本定义或报告口径，**永不**为 `true`：这些要交回研究者。

在校验*之前*先应用 [`orchestration-schemas.md` §7](../../references/orchestration-schemas.md) 中的**逐透镜举证责任**与**"不算数"过滤器**，这样已知的误报根本到不了裁判手里。校验环节是**偏向证伪**的，并负责设定每条发现的 `verdict`（审查者留空）：只有 `verdict: "confirmed"` 的发现才放行；凡它无法立足的，一律**丢弃**，不降级为警告。
