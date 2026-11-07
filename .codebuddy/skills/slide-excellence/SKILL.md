---
name: slide-excellence
description: 多代理综合审查幻灯片，覆盖视觉、教学法和校对，并按条件增加 TikZ、一致性和实质内容审查。用户说 "full review"、"excellence pass"、"comprehensive check"、"review everything"、"pre-release review"、"slide excellence"、"全面审幻灯片"、"授课前综合检查" 或 "交付前完整审查"，或在授课／交付一套幻灯片前使用。这是扇出（fan-out）包装器；只需单一透镜时，直接用 `/visual-audit`、`/pedagogy-review` 或 `/proofread`。
argument-hint: "[QMD or TEX filename] [--fast] [--skip-substance | --acknowledge-template-domain-reviewer]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent", "Task"]
---

# 幻灯片卓越审查

> **[本平台适配 · 2026-10-31] 这个技能刻意不声明 `context: fork`。**
> 声明该字段后，技能会进入 detached 子会话，而那个会话的工具集**没有 `Agent`**，
> 即使 `allowed-tools` 已申请也拿不到。本技能按条件扇出多个透镜，包括版面、教学法、
> 校对、TikZ 和 R 代码。每个透镜都必须在**独立上下文**中运行，避免相互污染，最后再归并结果。
> 没有 `Agent` 时，同一会话只能依次扮演这些透镜；报告看似完成了多角度审查，
> 实际只是同一双眼睛重复查看，而第二遍仍可能看不见第一遍漏掉的问题。
>
> 不 fork 也有代价：读文件、运行命令和试错等中间过程会占用主会话上下文，
> 长流程可能需要中途压缩一次。**这个代价换的是独立性，值。**
> 实测证据与复现命令见 [`platform-facts.md`](../../references/platform-facts.md) 的技能一节。

多个代理分别独立审查讲稿幻灯片，再由本技能归并（reduce）结果，形成多维度的综合审查。

> **我要的是哪一个幻灯片审查技能？**
>
> - **`/slide-excellence`**（本技能）：多代理扇出，覆盖视觉、教学法和校对，并按条件增加 TikZ、一致性和实质内容审查。最适合**授课前**或**交付前**检查。
> - **`/visual-audit`**：单一透镜，只看版式／溢出／字体／间距，速度较快。
> - **`/pedagogy-review`**：单一透镜，只看叙事／前备知识／示例演算／记号。
> - **`/proofread`**：单一透镜，只看语法／错字／溢出／术语。
> - **`/qa-quarto`**：通过批评者—修复者循环，对抗式检查 Beamer ↔ Quarto 一致性。
> - **`/devils-advocate`**：提出 5-7 个尖锐质询，不做完整审查。

**重要：**本编排器采用**条件式**派发，只启动能为给定文件提供有效结果的子代理。文件没有 TikZ 时不运行 `tikz-reviewer`，没有对应文件时不运行 `quarto-critic`。

## Step 1：确定文件

从 `$ARGUMENTS` 解析文件名，并在 `Quarto/` 或 `Slides/` 中解析路径。

按扩展名判断文件类型：

- `.tex` → Beamer
- `.qmd` → Quarto
- `.md` → Markdown 幻灯片

## Step 2：起飞前检查——探测条件

启动任何代理之前，先检查文件，确定哪些审查有实际意义：

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

对 `.tex` 文件启动实质内容审查代理前，先确认 `.codebuddy/agents/domain-reviewer.md` 已针对本项目定制。随附的 domain-reviewer 只是**模板**；原样运行只会得到「假设都陈述了吗？」之类的通用反馈，而不是真正的领域审查。

以下启发式命中任一条，就说明它仍是模板：

- 文件任意位置包含标记串 `AUTO-DETECT-TEMPLATE-MARKER`。随附模板含有该标记，定制时会删除或替换。检测采用子串匹配，标记可以跨行。
- 含有任一 `<!-- Customize: ... -->` 或 `[Customize: ...]` 占位符，两种形式都检查。
- 五个透镜的措辞与随附模板完全一致。与 v1.3.0 标签中的 `.codebuddy/agents/domain-reviewer.md` 做 diff，若零行变动，就仍是模板。

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

就此停止并返回这些选项。不要在未定制的模板上运行 `domain-reviewer`；由用户带上选定参数重新调用。

## Step 4：并行运行审查代理

只启动条件成立的代理：

**幻灯片（`.tex` 或 `.qmd`）常驻：**

- **代理 A：视觉审计**（`slide-auditor`）
  检查溢出、字体一致性、盒子疲劳、间距和图片。`$qa_report` 已设置时，即 `.qmd` 或带 Quarto 配对件的 `.tex`，把报告传给代理，利用实测溢出与截图；slide-qa 无法运行时，在摘要中说明。
  保存：`quality_reports/[FILE]_visual_audit.md`。

- **代理 B：教学法审查**（`pedagogy-reviewer`）
  检查 13 个教学法模式、叙事、节奏和记号。
  保存：`quality_reports/[FILE]_pedagogy_report.md`。

- **代理 C：校对**（`proofreader`）
  检查语法、错字、一致性、学术质量和引用。
  保存：`quality_reports/[FILE]_proofread_report.md`。

**条件式：**

- **代理 D：TikZ 审查**（`tikz-reviewer`），仅当 `has_tikz > 0`。
  基于测量审查碰撞，包括 Bézier、间隙、边界和边距。
  保存：`quality_reports/[FILE]_tikz_review.md`。

- **代理 E：内容一致性**（`quarto-critic`），仅当文件有对应件，即 `has_tex_pair` 或 `has_qmd_pair`。
  比较帧数、环境一致性，以及 `.tex` ↔ `.qmd` 之间的内容漂移。有 `$qa_report` 时传给代理。
  保存：`quality_reports/[FILE]_parity_report.md`。

- **代理 F：R 代码审查**（`r-reviewer`），仅当 `has_r == true`。
  审查任何内嵌 R 块或被引用脚本中的代码正确性。
  保存：`quality_reports/[FILE]_r_review.md`。

- **代理 G：实质内容审查**（`domain-reviewer`），`.tex` 必做，`.qmd` 可选，由 Step 3 门控。
  通过 5 个透镜框架审查领域正确性。
  保存：`quality_reports/[FILE]_substance_review.md`。

**去重：**若本会话已有技能为该文件生成报告，例如先运行过 `/proofread`，且报告比文件新，就直接复用并列明复用了哪些报告，不中途询问。若需要强制全新一轮，先把旧报告移出 `quality_reports/`，或 touch 幻灯片使其更新，再重新调用。

## Step 5：归并综合摘要（对类型化审查发现做 reduce）

本步骤采用**扇出 → 归并**（[`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)）。每个代理按共享 schema（[`orchestration-schemas.md`](../../references/orchestration-schemas.md)）返回 `FINDING` 与 `SCORECARD`；归并者**叠加类型化评分卡**，而不是用眼睛重读每份报告。总体质量得分由 CRITICAL/MAJOR/MINOR 计数求和后按门禁判据确定。条件式派发跳过的透镜必须写为「未运行、不贡献发现、不参与评分，覆盖缺口单列」，绝不表示「无问题」或「无审查发现」，也不以零分参与平均。

只为实际运行的代理列出结果小节；跳过的透镜单独列入覆盖缺口，不生成零计数行或分数。

```markdown
# Slide Excellence Review: [Filename]

**File:** [path]
**Type:** [Beamer / Quarto / Markdown]
**Detected:** TikZ=N | pair=[path or none] | R=[yes/no]
**Agents spawned:** [A, B, C, D, G] (skipped: E [no pair], F [no R])

## Coverage Gaps (skipped lenses)
- [Lens] — 未运行：[reason]；不贡献发现、不参与评分。这是覆盖缺口，不表示无问题。

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

完成后，打印实际启动的代理：

```
Spawned N agents[; token usage: actual figure, if the harness reports it].
For cost-conscious reviews, run individual subagent skills directly
(/proofread, /visual-audit, /pedagogy-review).
```

## 参数一览

| 参数 | 作用 |
|---|---|
| `--skip-substance` | 不启动代理 G（domain-reviewer）。适用于尚未定制 domain-reviewer.md 的情况。 |
| `--acknowledge-template-domain-reviewer` | 仍使用未定制的 domain-reviewer 继续；你接受实质内容审查只会给出通用反馈。 |
| `--fast` | 只启动一个综合代理直接读取文件，不使用并行子代理。成本更低，但审查不够彻底。 |

## 质量得分评分细则

| 得分 | Critical（`blocker`） | Major | 含义 |
|-------|----------|--------|---------|
| Excellent | 0 | 0 | 可以开讲 |
| Good | 0 | 1-5 | 先改 major（门禁读作 REVISE） |
| Needs Work | 0-5 | 6+，或任一含 critical | 需要大改；只要有 critical 残留，门禁就阻断 |
| Poor | 6+ | 任意 | 需要重构 |

任何 critical 发现都会阻断，不受其他计数影响；这与 [`orchestration-schemas.md`](../../references/orchestration-schemas.md) §3 使用同一门禁判据。

## 为什么条件式派发要紧

无法提供有效结果的审查者只会消耗 token 和信任：没有 TikZ 时，`tikz-reviewer` 无内容可审；没有配对文件时，`quarto-critic` 无从比较；未定制的 `domain-reviewer` 只返回「假设都陈述了吗？」之类通用反馈，作者最终会选择忽略。因此，只启动文件实际需要的透镜。

## 审查发现要被校验，不只是写下来（v2.5）

审查者必须按照 [`finding-schema.json`](../../references/finding-schema.json) 中机器可校验的契约发出发现。报告是 JSON **数组**。

**投入审查成本前，先对承载机制做冒烟测试。**若一次扇出多个审查者，最后却写不出合法报告，整轮工作都会浪费：

```bash
echo '[]' | python scripts/validate-findings.py
```

审查代理只读，因此**由本技能写文件**。收到每个审查者的最终响应后，把散文报告保存到指定路径，把响应末尾的围栏 `json` 块复制到草稿文件，并在校验时填充 id：

```bash
python scripts/validate-findings.py --fill-ids block.json > <report>.json.tmp \
  && mv <report>.json.tmp <report>.json || rm -f <report>.json.tmp   # exit 0 required; a failed run keeps no file
python scripts/validate-findings.py --check-quotes <report>.json   # each quote must be the file's own text (orchestration-schemas.md §1)
```

审查者未返回 `json` 块，或返回内容未通过校验，就等于没有完成审查。带上校验器错误文本重新派发一次；若仍失败，把该透镜报告为缺失，不得在缺少它的情况下归并。

契约要求及理由如下：

- **`rule`**：被违反且有文档记录的规则或标准。未援引规则的发现只是意见，不能给提交设门禁。
- **`failing_case`**：一个会使论断失效的具体配置，或确切缺失的假设。*"这里可以更清楚"*无法通过校验。
- **`id = sha1("<file>:<line>:<locus>")`**：同一轮内按此 id 精确去重；跨轮以 `file` + `locus` 判断发现身份，因为修复会改变行号。两次即升级规则也按 `file` + `locus` 机械检查，不靠目测。
- **`mechanical`**：只有不会改变结果的修复，例如错字、交叉引用、格式和标签，才为 `true`。涉及估计目标（estimand）、假设、设定、推断程序、样本定义或报告口径时，**永不**为 `true`；这些必须交回研究者。

校验*之前*，先应用 [`orchestration-schemas.md` §7](../../references/orchestration-schemas.md) 的**逐透镜举证责任**和**「不算数」过滤器**，避免已知误报进入裁判环节。校验阶段应**优先尝试证伪**，并设置每条发现的 `verdict`，审查者留空。只有 `verdict: "confirmed"` 的发现可以放行；无法立足的一律**丢弃**，不能降级为警告。
