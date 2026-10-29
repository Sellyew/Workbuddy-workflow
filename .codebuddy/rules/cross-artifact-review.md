---
description: Paper ↔ code cross-artifact review — when /review-paper runs, auto-invoke /review-r on referenced scripts and /audit-reproducibility on the pair. Surface cross-artifact findings alongside the paper review.
paths: ["master_supporting_docs/**/*.tex", "master_supporting_docs/**/*.qmd", "Slides/**/*.tex", "*.tex", "*.qmd"]
---

# 跨产物审查规程

论文不是孤岛。它的断言依赖于产出它们的代码。只审论文不审代码，等于只审了半个产物。

## 依赖图

```
manuscript.tex ──cites──> Table 2
Table 2        ──from──> output/results.rds
results.rds    ──by──> scripts/R/03_analyze.R
03_analyze.R   ──uses──> output/clean.rds
clean.rds      ──by──> scripts/R/02_clean.R
02_clean.R     ──reads──> data/raw.csv
```

`02_clean.R` 里的一个缺陷会让 Table 2 失效。只审 `manuscript.tex` 而不碰代码，会完全漏掉这一类错误。

## 适用时机

当 `/review-paper` 作用在一份引用了分析脚本的稿件上时适用。检测是**基于模式**的——如果稿件没有下列任何信号，就不会发生跨产物工作（`--no-cross-artifact` 也就等于空操作）。对于没有这些检测信号的论文，想强制触发，可让 `/review-paper` 指向一份用 `\input{}` 引入脚本输出的稿件，或者在 `/review-paper` 之外直接调用 `/review-r` 与 `/audit-reproducibility`。

检测信号：

- `\input{output/...}`, `\input{tables/...}`, or (pre-v2.6 layout) `\input{scripts/R/...}`
- `%% source: scripts/R/03_analyze.R` 注释
- 正文里的数值断言（ATT、系数、N、p 值）**同时**存在同级的 `scripts/R/` / `scripts/stata/` / `scripts/python/` 目录
- 论文里的表格标签与 `output/` 下的文件名对应

检测刻意保守——一篇没有代码的理论论文不应触发本规程，即便它所在仓库里有为别的工作准备的脚本。

## 规程

当 `/review-paper` 检测到上述任一信号：

### 1. 找出被引用的脚本

在稿件中查找：

- `\input{path}` 命令（从文件拉进来的表格、图）
- `%% from: scripts/...` 行注释
- 与 `output/` 下文件名对应的表格标签（例如 `Table:main_ATT` ↔ `results_main.rds`）

整理出产出本论文内容的脚本清单。

### 2. 自动调用 `/review-r`

对每个识别出的 R 脚本，在各自的独立上下文子代理里启动 `/review-r`。报告保存到 `quality_reports/cross_artifact_[paper]/review_r_[script].md`。

### 3. 自动调用 `/audit-reproducibility`

运行一次 `/audit-reproducibility $manuscript output/`。保存到 `quality_reports/cross_artifact_[paper]/reproducibility.md`。

### 4. 呈报跨产物审查发现

在论文审查报告里新增一节：

```markdown
## Cross-Artifact Findings

**Scripts reviewed:** N (see `quality_reports/cross_artifact_[paper]/`)
**Reproducibility:** PASS / FAIL — k of m claims within tolerance
**Code quality (merged from /review-r reports):** C critical, M major, L minor

### Critical cross-artifact issues (paper + code together)
| Paper claim | Code location | Issue |
|---|---|---|

### Code-only issues (won't block paper, but file a follow-up)
…

### Paper-only issues (code is clean)
[Rest of the paper review goes here]
```


### 5. 退出行为

- `/audit-reproducibility` 报出的任何 CRITICAL（容差判定 FAIL）→ 在论文审查中升级为 CRITICAL。
- 影响论文断言的代码 CRITICAL 缺陷 → 在论文审查中升级。
- 与论文断言无关的代码 CRITICAL 缺陷 → 另立行动项。

## 退出选项

- `/review-paper --no-cross-artifact` 跳过依赖图。适用于没有代码的理论论文、评论或预印本。

## 交叉引用

- `.codebuddy/skills/review-paper/SKILL.md` —— 编排器。
- `.codebuddy/skills/review-r/SKILL.md` —— 代码审查器。
- `.codebuddy/skills/audit-reproducibility/SKILL.md` —— 数值断言校验器。
- `.codebuddy/rules/replication-protocol.md` —— 容差契约。

## 本规则不做要求的事

- 运行 R / Stata / Python（那是 `/audit-reproducibility` 的活儿，它读既有输出）。
- 用 git blame 做考古——我们审的是当前状态。
- 判断论文作者代码写得好不好，与判断他们的*结果*是否站得住脚是两件事。我们首先关心后者。

## `--peer` 模式下的次序

在 `/review-paper --peer [journal]` 模式下，跨产物审查在编辑的案头审查**之前**运行（作为 Phase 0）。这让编辑拿到可复现性证据——承重断言上任何 FAIL 都够得上案头退稿。编辑的案头审查在相关时会在 desk_review.md 里引用具体的 `/audit-reproducibility` 发现。

在默认模式与 `--adversarial` 模式下，跨产物审查仍在 Step 6b 运行（论文审查之后）。两种次序都成立；`--peer` 的起飞前检查次序之所以存在，是因为编辑会根据数据错误的证据做案头退稿决定。
