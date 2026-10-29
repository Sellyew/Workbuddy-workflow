---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
---

# Beamer → Quarto 自动同步规则

**当你改动一个有 Quarto 镜像的 Beamer `.tex` 文件时，要在同一任务里把等价的改动落到 `.qmd`，并在报告完成之前把两者都构建一遍。**用户依赖这一对保持同步，不该由他来提；只报告漂移而不修，镜像就停在旧状态。镜像可以合法携带的 Quarto 专属装饰，见下文「优先级」。

## 讲次映射

<!-- 把这张表改成你自己的讲次 -->
| 讲次 | Beamer | Quarto |
|---------|--------|--------|
| 1 | `Slides/Lecture1_Topic.tex` | `Quarto/Lecture1_Topic.qmd` |
| 2 | `Slides/Lecture2_Topic.tex` | `Quarto/Lecture2_Topic.qmd` |
<!-- 新建讲次时在这里加行 -->

## 工作流（每次都走）

1. 把修改应用到 Beamer `.tex`
2. **立刻**把等价修改应用到 Quarto `.qmd`
3. 编译 Beamer（xelatex 三遍）
4. 渲染 Quarto（`./scripts/sync_to_docs.sh LectureN`）
5. 这之后才报告任务完成

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
| `$formula$` | `$formula$`（同上） |

## 不要同步的情形

- Quarto 文件还不存在
- 改动只涉及 LaTeX 侧的基础设施（preamble、主题文件）
- 被明确告知跳过 Quarto 同步

## Quarto 文件有手工后期改动时的优先级

在人手工改过 Quarto 文件之后，本规则（自动同步）与 [`single-source-of-truth.md`](single-source-of-truth.md)（Beamer 为权威）可能冲突。处理办法：

1. **Beamer 仍是权威。**往 Quarto 里手改并增加*内容*（新幻灯片、不同公式）违反 SSOT，应先回灌到 Beamer，再向下重新同步。
2. **允许只关乎呈现的分歧。**HTML 专属的提示块（例如 `.smaller`、`{.scrollable}`、plotly 嵌入）可以只存在于 Quarto。传播 Beamer 改动时，自动同步不应删掉它们——覆盖之前先 diff。
3. **遇到含糊处，从 Beamer 重新生成 Quarto 文件**（例如用 `/translate-to-quarto [file]` 输出到草稿区路径，再与现有 Quarto 做 diff），这样能结构化地比对。手工合并，保留仅 HTML 的装饰。
4. **如果两个文件已经结构性漂移**（幻灯片数对不上、小节次序不同），按缺陷处理：先修 Beamer，再用 `/translate-to-quarto` 从头重新生成 Quarto。

## 何时更新这张表

新建一份 Quarto 译文之后，把它加进上面的映射表。
