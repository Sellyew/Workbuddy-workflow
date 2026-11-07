---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
---

# Beamer → Quarto 自动同步规则

**改动有 Quarto 镜像的 Beamer `.tex` 文件时，必须在同一任务中把等价改动写入 `.qmd`，并在报告完成前构建两者。**用户依赖这对文件保持同步，不应由用户提醒。只报告漂移而不修复，会让镜像停留在旧状态。Quarto 镜像可以合法保留哪些专属装饰，见下文「优先级」。

## 讲次映射

<!-- 把这张表改成你自己的讲次 -->
| 讲次 | Beamer | Quarto |
|---------|--------|--------|
| 1 | `Slides/Lecture1_Topic.tex` | `Quarto/Lecture1_Topic.qmd` |
| 2 | `Slides/Lecture2_Topic.tex` | `Quarto/Lecture2_Topic.qmd` |
<!-- 新建讲次时在这里加行 -->

## 工作流（每次都走）

1. 修改 Beamer `.tex`。
2. **立刻**对 Quarto `.qmd` 作出等价修改。
3. 编译 Beamer，运行 xelatex 三遍。
4. 渲染 Quarto，运行 `./scripts/sync_to_docs.sh LectureN`。
5. 完成上述步骤后，才能报告任务完成。

## LaTeX → Quarto 对照参考

| Beamer | Quarto 对应写法 |
| ------ | ----------------- |
| `\muted{text}` | `[text]{style="color: #525252;"}` |
| `\key{text}` | `[**text**]{.emorygold}` |
| `\textcolor{positive}{text}` | `[text]{.positive}` |
| `\textcolor{negative}{text}` | `[text]{.negative}` |
| `\item text` | `- text` |
| `\begin{highlightbox}` | `::: {.highlightbox}` |
| `\begin{methodbox}` | `::: {.methodbox}` |
| `$formula$` | `$formula$`（与 Beamer 相同） |

## 不要同步的情形

- Quarto 文件还不存在。
- 改动只涉及 LaTeX 侧的基础设施，如 preamble、主题文件。
- 用户明确要求跳过 Quarto 同步。

## Quarto 文件有手工后期改动时的优先级

人工修改 Quarto 文件后，本规则要求自动同步，而 [`single-source-of-truth.md`](single-source-of-truth.md) 规定 Beamer 为权威，两者可能冲突。此时按以下顺序处理：

1. **Beamer 仍是权威。**直接在 Quarto 中增加*内容*，例如新幻灯片或不同公式，违反 SSOT。必须先把这些改动回灌到 Beamer，再向下同步。
2. **允许仅涉及呈现的分歧。**HTML 专属的提示块可以只存在于 Quarto，例如 `.smaller`、`{.scrollable}`、plotly 嵌入。传播 Beamer 改动时，自动同步不得删除这些内容，覆盖前必须先 diff。
3. **遇到含糊之处，从 Beamer 重新生成 Quarto 文件。**例如用 `/translate-to-quarto [file]` 输出到草稿区路径，再与现有 Quarto 做 diff，以便按结构比对。随后手工合并，保留仅用于 HTML 的装饰。
4. **两个文件已经结构性漂移时，按缺陷处理。**幻灯片数对不上、小节次序不同都属于这种情况。先修 Beamer，再用 `/translate-to-quarto` 从头重新生成 Quarto。

## 何时更新这张表

完成一份新的 Quarto 译文后，把它加入上面的映射表。
