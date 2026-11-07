---
name: validate-bib
description: 交叉核对参考文献条目与所有讲义文件中的引文。默认检查缺失/未使用条目和格式错误字段；`--semantic` 另查引文漂移、DOI 和样式一致性。用户说“检查参考文献”、“核对 BibTeX 引文”时使用。
description_zh: 交叉核对参考文献条目与所有讲义文件中的引文。默认检查缺失/未使用条目和格式错误字段；`--semantic` 另查引文漂移、DOI 和样式一致性。用户说“检查参考文献”、“核对 BibTeX 引文”时使用。
argument-hint: "[--semantic] [--skip-doi] [--cite-claim]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "WebFetch"]
---

# 校验参考文献

交叉核对讲义文件中的引文和参考文献条目，支持两种模式：

- **默认（结构检查）：** 检查缺失条目、未使用条目、格式错误字段和疑似错字。
- **`--semantic`：** 除结构检查外，还检查引文漂移（同一篇论文的重复条目），通过 crossref 核验 DOI，并检查每个文件内的引文样式是否一致。

报告保存在 `quality_reports/bib_audit_[structural|semantic].md`。

## 模式 1：结构检查（默认）

### 步骤

1. **读取参考文献文件**，提取所有引文键。

2. **扫描讲义文件中的引文键：**
   - `.tex`：`\cite{`、`\citet{`、`\citep{`、`\citeauthor{`、`\citeyear{`、`\textcite{`、`\parencite{`
   - `.qmd` / `.md`：`@key`、`[@key]`、`[@key1; @key2]`
   - 提取所有实际使用且不重复的引文键。

3. **交叉比对：**
   - **缺失条目（CRITICAL）：** 讲义已引用，但 `.bib` 中不存在。
   - **未使用条目（信息性）：** 存在于 `.bib`，但从未被引用。
   - **疑似错字：** 与某个 `.bib` 键的编辑距离不超过 2，例如 `Smith2020` 与 `Smth2020`。

4. **检查条目质量：**
   - 必需字段是否齐备（author, title, year, journal/booktitle）。
   - author 字段格式是否正确。
   - 年份是否在 1900 至当前年份之间。
   - 是否存在畸形字符或编码问题。
   - `doi` 字段是否已归一化，不带 `https://doi.org/` 前缀。

5. **把报告写入** `quality_reports/bib_audit_structural.md`。

### 扫描的文件

```
Slides/*.tex
Quarto/*.qmd
guide/*.qmd
master_supporting_docs/**/*.tex
```

### 参考文献位置

默认使用仓库根目录的 `Bibliography_base.bib`，可在 CODEBUDDY.md 中覆盖。

## 模式 2：语义检查（`--semantic`）

包含模式 1 的全部检查，并增加以下项目。

### 2a. 引文漂移检测

引文漂移指多个 `.bib` 条目用不同键描述同一篇论文，常见表现有：

- `Smith2020` 和 `Smith2020a` 的 DOI 或标题相同。
- `CallawaySantAnna2021` 和 `CS2021` 指向同一篇论文。
- 协作者合并过 `.bib` 文件。

**任一启发式命中即 FLAG：**

| 检查 | 信号 |
|---|---|
| 跨键同一 DOI | 硬重复（CRITICAL） |
| 标题相同（不分大小写、去标点） | 很可能重复（CRITICAL） |
| 作者+年份+期刊相同 | 可能重复（MEDIUM） |
| 标题在长度 ≥ 4 字符的 token 上 Jaccard > 0.85 | 软重复（LOW） |

对每对标记条目，列出两个键及各自的引用位置，并推荐规范键：优先选择引用次数最多的键，其次选择字母序最前的键。

### 2b. DOI 核验（可选；联网）

对每个带 `doi` 的条目，请求 `https://api.crossref.org/works/{doi}`，再比对：

- 第一作者的姓。
- 年份。
- 标题，归一化 token 上的 Jaccard > 0.7。
- container-title / 期刊，精确匹配或缩写匹配。

**严重程度：**

- 作者或标题不符 → CRITICAL，可能指向错误论文。
- 年份不符 → MEDIUM，可能来自预印本与已发表版本的差异，也可能是错字。
- 期刊不符 → LOW，可能是合法的预印本变体。

**速率限制：** 每次运行最多查询 50 次，调用间隔 0.5s，缓存写入 `quality_reports/.doi_cache.json`。

**关闭方式：** 离线或没有 WebFetch 的环境中使用 `--skip-doi`。

### 2c. 每个文件内的样式一致性

逐文件统计引文命令，包括 `\citet` vs `\citep` vs `\cite`，以及 `@key` vs `[@key]`。如果文件混用样式且没有明显规律，就标记为低严重程度，例如同一份讲义出现 20 次 `\citep` 和 3 次 `\cite`。

### 2d. 引文—论断合理性（仅标记）

该检查由 `--cite-claim` 启用。对每个文件引用最多的前 10 篇作品，用 WebFetch 获取 crossref 摘要，与正文语境并排展示。**不自动判断**论断是否匹配，由人决定。

> **这里只检查存在性和结构，不判断引文是否恰当。** 被引论文是否*真的说了*正文归给它的内容，应由 [`/verify-claims`](../verify-claims/SKILL.md) 判断。该技能阅读原文，依据引文和页码给出 supports / partial / contradicts；如果存在站得住脚的具名替代解释，也可判为 EXPLAINED。`--cite-claim` 只展示摘要；需要判定时，请运行 `/verify-claims`。

### 报告结构（`quality_reports/bib_audit_semantic.md`）

```markdown
# Bibliography Semantic Audit

**Date:** YYYY-MM-DD
**Bibliography:** Bibliography_base.bib (N entries)
**Files scanned:** [list]

## Summary

| Check | Critical | Medium | Low |
|---|---|---|---|
| Structural | | | |
| Citation drift | | | |
| DOI verification | | | |
| Style consistency | 0 | 0 | |

## Critical Issues

### Duplicate entries
| Keys | Signal | Citations | Recommended canonical |
|---|---|---|---|

### DOI mismatches
| Key | Field | .bib value | crossref value |
|---|---|---|---|

## Medium / Low issues
…

## Next steps
1. Resolve duplicates — pick canonical key, update citations, remove orphans.
2. Fix DOI mismatches — verify paper in crossref or strip the wrong DOI.
3. Review style-consistency notes.
```

## 参数

| 参数 | 作用 |
|---|---|
| `--semantic` | 在结构检查之上加语义检查：引文漂移检测、DOI 核验、样式一致性。 |
| `--skip-doi` | 跳过 2b 的 DOI 联网核验，用于离线或没有 WebFetch 的环境。 |
| `--cite-claim` | 对每个文件引用最多的前 10 篇作品呈现 crossref 摘要与正文语境；只标记，不自动判断。 |

## 退出行为

- **结构检查：** 退出码为 0，问题列在报告中。
- **语义检查：** 只有 LOW 级发现时退出码为 0；出现任何 CRITICAL 时退出码为 1，可用作投稿前门禁。

## 交叉引用

- `.codebuddy/skills/review-paper/SKILL.md` —— 投稿前完整检查时的搭档。
- `.codebuddy/skills/audit-reproducibility/SKILL.md` —— 数值论断一侧的对应技能。
- `.codebuddy/skills/verify-claims/SKILL.md` —— 负责引文**恰当性**，即被引论文是否支持该论断。本技能检查引文*存在且格式正确*，`/verify-claims` 检查引文是否*站得住*。

## 本技能不做什么

- 不判断引文是否用在正确*语境*中，也不判断被引论文是否*真的说了*正文归给它的内容。这属于 `/verify-claims`，见 2d；本技能只检查存在性和结构。
- 不自动修改 `.bib` 文件，所有修改都只是建议。
- 不检查非 DOI 标识符（ISBN、arXiv、SSRN），这些属于路线图。
