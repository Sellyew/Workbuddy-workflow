---
name: translate-to-quarto
description: 把 Beamer `.tex` 讲稿转换成 Quarto RevealJS `.qmd` 镜像，依次提取 TikZ、逐页翻译、转换引文并自动检查 QA 一致性。用户说 "translate to quarto"、"port to revealjs"、"make an html version"、"convert this beamer to quarto"、"mirror this lecture in qmd"、"把 Beamer 转成 Quarto"、"做一个 HTML 版讲稿" 时使用，也适用于准备把 Beamer 幻灯片发布到网上的场景。产出保存在 `Quarto/`。
description_zh: 把 Beamer `.tex` 讲稿转换成 Quarto RevealJS `.qmd` 镜像，依次提取 TikZ、逐页翻译、转换引文并自动检查 QA 一致性。用户说 "translate to quarto"、"port to revealjs"、"make an html version"、"convert this beamer to quarto"、"mirror this lecture in qmd"、"把 Beamer 转成 Quarto"、"做一个 HTML 版讲稿" 时使用，也适用于准备把 Beamer 幻灯片发布到网上的场景。产出保存在 `Quarto/`。
argument-hint: "[LectureN_Topic.tex]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task"]
---

# Beamer → Quarto 翻译工作流

> **[本平台适配 · 2026-10-31] 这个技能刻意不声明 `context: fork`。**
> 声明后，技能会在 detached 子会话中执行，而**该会话的工具集没有 `Agent`**，
> 即使同目录的 `allowed-tools` 已申请也拿不到。这个技能需要 `beamer-translator`
> 逐页翻译，再做教学法和校对审读。每个透镜都要在**独立上下文**中运行，
> 避免相互污染，最后才归并结果。
> 没有 `Agent` 时，同一会话只能依次扮演这些透镜。报告看似经过多角度审读，
> 实际仍是同一双眼睛重复检查，第二遍也很难发现第一遍漏掉的问题。
>
> 不 fork 的代价也要说清楚：读文件、运行命令和试错等中间过程会占用主会话上下文，
> 长流程可能需要中途压缩一次。**用这项代价换取审读独立性是值得的。**
> 实测证据和复现命令见 [`platform-facts.md`](../../references/platform-facts.md) 的技能一节。

把 Beamer LaTeX 讲稿完整转换成 Quarto RevealJS HTML 幻灯片。

**Beamer `.tex` 是单一真源：**`.qmd` 负责镜像它；翻译中发现的更正要回写到 `.tex`，见 Phase 10。

---

## Phase 0 — 起飞前检查

### 0A. 环境对齐审计
扫描 Beamer 中的全部自定义环境，确认主题 SCSS 有对应 CSS；如有缺失，**先**补齐。

### 0B. TikZ 新鲜度核验
运行 `/extract-tikz`，确认 SVG 与当前 Beamer 源一致。

### 0C. RDS 数据清单
列出交互图表需要的全部 RDS 文件。

### 0D. 引文键映射
提取 Beamer 中的全部引文，并映射到参考文献键。

## Phase 1 — 翻译前准备
- 通读 Beamer 源并数清 frame 数。
- 盘点图形：TikZ 转 SVG，R 图转 plotly，其他图形转 SVG。

## Phase 2 — 创建带 YAML 头的 QMD 文件
- 使用标准 RevealJS YAML，包含主题、logo、页脚和参考文献。
- 如有需要，添加加载 R 数据的 setup 块。

## Phase 3 — 逐页翻译
- 交给 `beamer-translator` 代理处理。
- frame 与 slide 一比一对应。
- 数学式逐字保留，环境保持对齐，不缩小字号。

## Phase 4 — TikZ 图集成
按从 0 开始的索引引用已提取的 SVG。

## Phase 5 — R 图集成（Plotly 优先）
优先用 RDS 数据制作交互式 plotly；TikZ 和复杂图使用静态 SVG。

## Phase 6 — 首次渲染与内容保真检查
渲染后数清幻灯片数量，再逐页检查内容问题。

## Phase 6.5 — 教学法审读
在视觉打磨前，先运行 pedagogy-reviewer。

## Phase 7 — 视觉打磨
调整语义化配色、过渡页和引导句。

## Phase 8 — 校对
对 QMD 文件运行 `/proofread`。

## Phase 9 — 最终核验与部署
渲染后亲自检查实际产物，包括渲染 HTML 以及用户提供的截图或 PDF 导出，确认每张图都存在、没有溢出，而且所有环境都有样式。

## Phase 10 — Beamer 源同步
把所有更正回写到 Beamer 源。

## Phase 11 — 一致性 QA + 文档
对新镜像运行 `/qa-quarto`，检查 Beamer↔Quarto 一致性。随后更新 CODEBUDDY.md 中该讲次的行和会话日志，并告诉用户可以把这套幻灯片交给 `/commit`。本技能不提交，也不开 PR。
