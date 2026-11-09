---
description: 论文 ↔ 代码的跨产物审查——当 /review-paper 运行时，自动调用 /review-r 审读被引用的脚本，并对这一对产物运行 /audit-reproducibility。跨产物审查发现随论文审查一起呈报。
paths: ["master_supporting_docs/**/*.tex", "master_supporting_docs/**/*.qmd", "Slides/**/*.tex", "*.tex", "*.qmd"]
---

# 跨产物审查规程

论文中的断言依赖生成相应结果的代码。只审论文而不审代码，就会遗漏产物的一半。

## 依赖图

```
manuscript.tex ──cites──> Table 2
Table 2        ──from──> output/results.rds
results.rds    ──by──> scripts/R/03_analyze.R
03_analyze.R   ──uses──> output/clean.rds
clean.rds      ──by──> scripts/R/02_clean.R
02_clean.R     ──reads──> data/raw.csv
```

`02_clean.R` 中的一个缺陷就可能使 Table 2 失效。只审 `manuscript.tex` 而不检查代码，会完全漏掉这类错误。

## 适用时机

`/review-paper` 审读一份引用分析脚本的稿件时，适用本规程。规程根据**模式**检测依赖：稿件不含下列任何信号时，不会开展跨产物工作，`--no-cross-artifact` 也不会产生实际作用。对于没有这些信号但仍需跨产物审查的论文，可以让 `/review-paper` 指向一份通过 `\input{}` 引入脚本输出的稿件，也可以绕过 `/review-paper`，直接调用 `/review-r` 与 `/audit-reproducibility`。

检测信号：

- `\input{output/...}`、`\input{tables/...}`，以及 v2.6 之前布局中的 `\input{scripts/R/...}`
- `%% source: scripts/R/03_analyze.R` 注释
- 正文包含数值断言（ATT、系数、N、p 值），**并且**同级存在 `scripts/R/`、`scripts/stata/` 或 `scripts/python/` 目录
- 论文中的表格标签与 `output/` 下的文件名对应

检测规则有意保持保守。理论论文即使没有代码，也不应仅因仓库中存在其他工作的脚本而触发本规程。

## 规程

当 `/review-paper` 检测到上述任一信号：

### 1. 找出被引用的脚本

在稿件中查找：

- `\input{path}` 命令（从文件拉进来的表格、图）
- `%% from: scripts/...` 行注释
- 与 `output/` 下文件名对应的表格标签（例如 `Table:main_ATT` ↔ `results_main.rds`）

据此列出为本论文生成内容的脚本。

### 2. 自动调用 `/review-r`

对每个识别出的 R 脚本，分别在独立上下文的子代理中启动 `/review-r`。报告保存到 `quality_reports/cross_artifact_[paper]/review_r_[script].md`。

### 3. 自动调用 `/audit-reproducibility`

运行一次 `/audit-reproducibility $manuscript output/`。报告保存到 `quality_reports/cross_artifact_[paper]/reproducibility.md`。

### 4. 呈报跨产物审查发现

在论文审查报告中新增一节：

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

- `/audit-reproducibility` 报告的任何 CRITICAL，即容差判定 FAIL，都要在论文审查中升级为 CRITICAL。
- 影响论文断言的代码 CRITICAL 缺陷，要在论文审查中升级。
- 与论文断言无关的代码 CRITICAL 缺陷，要另立行动项。

## 退出选项

- `/review-paper --no-cross-artifact` 跳过依赖图。适用于没有代码的理论论文、评论或预印本。

## 交叉引用

- `.codebuddy/skills/review-paper/SKILL.md` —— 编排器。
- `.codebuddy/skills/review-r/SKILL.md` —— 代码审查器。
- `.codebuddy/skills/audit-reproducibility/SKILL.md` —— 数值断言校验器。
- `.codebuddy/rules/replication-protocol.md` —— 容差契约。

## 本规则不做要求的事

- 运行 R / Stata / Python。这属于 `/audit-reproducibility` 的职责，它读取既有输出。
- 用 git blame 追溯历史。本规程审查当前状态。
- 评价论文作者的代码水平与判断其*结果*是否可靠是两件事。本规程首先关注后者。

## `--peer` 模式下的次序

在 `/review-paper --peer [journal]` 模式下，跨产物审查作为 Phase 0，先于编辑的案头审查运行。这样，编辑可以先取得可复现性证据；承重断言出现任何 FAIL，都足以支持案头退稿。相关情况下，编辑会在 desk_review.md 中引用具体的 `/audit-reproducibility` 发现。

在默认模式与 `--adversarial` 模式下，跨产物审查仍在 Step 6b 运行，即论文审查之后。两种次序都有效；`--peer` 把跨产物审查放在开始前，是因为编辑会依据数据错误的证据决定是否案头退稿。
