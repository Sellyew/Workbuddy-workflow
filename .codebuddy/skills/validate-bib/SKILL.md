---
name: validate-bib
description: 把参考文献条目与所有讲义文件里的引文做交叉核对。默认做结构检查（缺失/未使用条目、格式错误的字段）；`--semantic` 增加引文漂移检测、DOI 核验与样式一致性检查。
description_zh: 把参考文献条目与所有讲义文件里的引文做交叉核对。默认做结构检查（缺失/未使用条目、格式错误的字段）；`--semantic` 增加引文漂移检测、DOI 核验与样式一致性检查。
argument-hint: "[--semantic] [--skip-doi] [--cite-claim]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "WebFetch"]
---

# 校验参考文献

把讲义文件里的引文与参考文献条目做交叉核对。两种模式：

- **默认（结构检查）：** 缺失的条目、未使用的条目、格式错误的字段、疑似错字。
- **`--semantic`：** 增加引文漂移检测（同一篇论文的重复条目）、经 crossref 的 DOI 核验，以及每个文件内的引文样式一致性。

报告保存到 `quality_reports/bib_audit_[structural|semantic].md`。

## 模式 1：结构检查（默认）

### 步骤

1. **读参考文献文件**，抽出所有引文键。

2. **在讲义文件里扫描引文键：**
   - `.tex`：`\cite{`、`\citet{`、`\citep{`、`\citeauthor{`、`\citeyear{`、`\textcite{`、`\parencite{`
   - `.qmd` / `.md`：`@key`、`[@key]`、`[@key1; @key2]`
   - 抽出所有用到的不重复引文键。

3. **交叉比对：**
   - **缺失条目（CRITICAL）：** 讲义里引用了，`.bib` 里没有。
   - **未使用条目（信息性）：** 在 `.bib` 里，但从未被引用。
   - **疑似错字：** 与某个 `.bib` 键的编辑距离在 2 以内（例如 `Smith2020` 与 `Smth2020`）。

4. **检查条目质量：**
   - 必需字段齐备（author, title, year, journal/booktitle）。
   - author 字段格式正确。
   - 年份在 1900–当前之间。
   - 没有畸形字符 / 编码问题。
   - `doi` 字段已归一化（不带前缀 `https://doi.org/`）。

5. **写报告**到 `quality_reports/bib_audit_structural.md`。

### 扫描的文件

```
Slides/*.tex
Quarto/*.qmd
guide/*.qmd
master_supporting_docs/**/*.tex
```

### 参考文献位置

默认是仓库根目录的 `Bibliography_base.bib`；可通过 CODEBUDDY.md 覆盖。

## 模式 2：语义检查（`--semantic`）

模式 1 的全部内容，外加：

### 2a. 引文漂移检测

多个 `.bib` 条目用不同的键描述同一篇论文。症状：

- `Smith2020` + `Smith2020a`，DOI 或标题相同。
- `CallawaySantAnna2021` + `CS2021` 都指向同一篇论文。
- 协作者合并过的 `.bib` 文件。

**检测启发式（任一命中 → FLAG）：**

| 检查 | 信号 |
|---|---|
| 跨键同一 DOI | 硬重复（CRITICAL） |
| 标题相同（不分大小写、去标点） | 很可能重复（CRITICAL） |
| 作者+年份+期刊相同 | 可能重复（MEDIUM） |
| 标题在长度 ≥ 4 字符的 token 上 Jaccard > 0.85 | 软重复（LOW） |

对每一对被打上标记的条目：列出两个键、各自在哪里被引用，并推荐一个规范键（优先引用次数最多的，其次字母序最前）。

### 2b. DOI 核验（可选；联网）

对每个带 `doi` 的条目，取 `https://api.crossref.org/works/{doi}` 并比对：

- 第一作者的姓
- 年份
- 标题（归一化 token 上的 Jaccard > 0.7）
- container-title / 期刊（精确或缩写）

**严重程度：**

- 作者或标题不符 → CRITICAL（错的论文）
- 年份不符 → MEDIUM（预印本 vs 已发表，或错字）
- 期刊不符 → LOW（合法的预印本变体）

**速率限制：** 每次运行最多 50 次查询，调用之间延迟 0.5s。缓存于 `quality_reports/.doi_cache.json`。

**关闭方式：** `--skip-doi` 用于离线或没有 WebFetch 的环境。

### 2c. 每个文件内的样式一致性

对每个文件，统计引文命令（`\citet` vs `\citep` vs `\cite`；`@key` vs `[@key]`）。对样式混用、又没有明显规律的文件打 FLAG（例如同一份讲义里 20 次 `\citep` 与 3 次 `\cite`）。低严重程度。

### 2d. 引文—论断合理性（仅标记）

由 `--cite-claim` 门控。对每个文件引用最多的前 10 篇作品，WebFetch 取 crossref 摘要，并把它与正文语境并排呈现。**不做自动判断** —— 由人决定论断是否对得上。

> **这是存在性与结构，不是恰当性。** 判断被引论文是否*真的说了*正文断言归给它的内容，是 [`/verify-claims`](../verify-claims/SKILL.md) 的活 —— 它读原文，并把 supports / partial / contradicts 的判定建立在引文 + 页码上（对站得住脚的具名替代解释有 EXPLAINED 这个出口）。`--cite-claim` 只呈现摘要；要判定，请跑 `/verify-claims`。

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

- **结构检查：** 退出码 0；报告会列举问题。
- **语义检查：** 只有 LOW 级发现时退出码 0；出现任何 CRITICAL 时退出码 1。可作为投稿前门禁使用。

## 交叉引用

- `.codebuddy/skills/review-paper/SKILL.md` —— 投稿前完整检查时的搭档。
- `.codebuddy/skills/audit-reproducibility/SKILL.md` —— 数值论断一侧的对应技能。
- `.codebuddy/skills/verify-claims/SKILL.md` —— 引文**恰当性**一侧的对应技能（被引论文支持这个论断吗？）。本技能检查引文*存在且格式正确*；`/verify-claims` 检查它*站得住*。

## 本技能不做什么

- 判断一条引文是否用在正确的*语境*里 —— 被引论文是否真的*说了*论断归给它的内容。那是 `/verify-claims` 的活（见 2d）；本技能只做存在性与结构。
- 自动修你的 `.bib` 文件 —— 所有修改都是建议。
- 检查非 DOI 标识符（ISBN、arXiv、SSRN）—— 属路线图。
