---
name: translate-to-quarto
description: 把一份 Beamer `.tex` 讲稿译成 Quarto RevealJS `.qmd` 镜像。分多个阶段：提取 TikZ → 逐页翻译 → 引文转换 → 自动 QA 一致性检查。用户说 "translate to quarto"、"port to revealjs"、"make an html version"、"convert this beamer to quarto"、"mirror this lecture in qmd" 时使用，或在一套 Beamer 幻灯片已可发布到网上时使用。产出落在 `Quarto/`。
description_zh: 把一份 Beamer `.tex` 讲稿译成 Quarto RevealJS `.qmd` 镜像。分多个阶段：提取 TikZ → 逐页翻译 → 引文转换 → 自动 QA 一致性检查。用户说 "translate to quarto"、"port to revealjs"、"make an html version"、"convert this beamer to quarto"、"mirror this lecture in qmd" 时使用，或在一套 Beamer 幻灯片已可发布到网上时使用。产出落在 `Quarto/`。
argument-hint: "[LectureN_Topic.tex]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task"]
context: fork
---

# Beamer → Quarto 翻译工作流

把一份 Beamer LaTeX 讲稿完整译成 Quarto RevealJS HTML 幻灯片。

**Beamer `.tex` 是单一真源：**`.qmd` 镜像它，翻译过程中发现的更正回写到 `.tex`（Phase 10）。

---

## Phase 0 — 起飞前检查

### 0A. 环境对齐审计
扫描 Beamer 里的所有自定义环境。核验你的主题 SCSS 里有对应的 CSS。若有缺失，**先**把它们建出来。

### 0B. TikZ 新鲜度核验
跑 `/extract-tikz`，核验 SVG 与当前 Beamer 源一致。

### 0C. RDS 数据清单
列出交互图表所需的全部 RDS 文件。

### 0D. 引文键映射
从 Beamer 中提取全部引文，映射到参考文献键。

## Phase 1 — 翻译前准备
- 通读 Beamer 源，数清 frame 数
- 盘点图形（TikZ → SVG，R 图 → plotly，其他 → SVG）

## Phase 2 — 创建带 YAML 头的 QMD 文件
- 标准 RevealJS YAML，含主题、logo、页脚、参考文献
- 如需要，写一个装载 R 数据的 setup 块

## Phase 3 — 逐页翻译
- 交给 `beamer-translator` 代理
- frame 与 slide 一比一映射
- 数学式逐字保留，环境对齐，不缩小字号

## Phase 4 — TikZ 图集成
按从 0 起的索引引用已提取的 SVG。

## Phase 5 — R 图集成（Plotly 优先）
用 RDS 数据做交互式 plotly，TikZ／复杂图用静态 SVG。

## Phase 6 — 首次渲染与内容保真检查
渲染，数幻灯片数，逐页过一遍检查问题。

## Phase 6.5 — 教学法审读
在视觉打磨之前跑 pedagogy-reviewer。

## Phase 7 — 视觉打磨
语义化配色、过渡页、引导句。

## Phase 8 — 校对
对 QMD 文件跑 `/proofread`。

## Phase 9 — 最终核验与部署
渲染，然后自己检查渲染出来的东西（渲染后的 HTML，加上用户提供的任何截图或 PDF 导出）——每张图都在，没有溢出，所有环境都有样式。

## Phase 10 — Beamer 源同步
把任何更正施加回 Beamer 源。

## Phase 11 — 一致性 QA + 文档
对新镜像跑 `/qa-quarto` 检查 Beamer↔Quarto 一致性。然后更新 CODEBUDDY.md 里该讲次那一行与会话日志，并告诉用户这套幻灯片已可以交给 `/commit`——本技能不提交、不开 PR。
