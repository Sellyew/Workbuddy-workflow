---
name: audit-reproducibility
description: 交叉核对稿件中的数值论断与 R / Stata / Python 的实际产出，以强制执行 replication-protocol.md 的规则。按容差阈值对每条论断报告 PASS/FAIL。在投稿前、发布复现包（replication package）前使用。
argument-hint: "[manuscript path] [outputs-dir] (outputs-dir defaults to output/)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent", "Task"]

---

# 复现性审计

将稿件中的数值论断（点估计、标准误、p 值、计数）与分析流水线的实际输出逐一比对，并按照 [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) 定义的容差阈值，对每条论断报告 PASS / FAIL。

**核心原则：** 如果论文写 `ATT = -1.632 (0.584)`，而代码产出 `-1.628 (0.591)`，必须用**数值比较**确认差值处于文档规定的容差内，不能靠目测判断"看着差不多"。

**必须检查两个方向。** *纵向*检查把每条论断与生成它的输出核对；*横向*检查把它与**其他**所有展示同一数字的产物核对，包括附录表、幻灯片和海报。纵向检查可能通过，而某份幻灯片仍引用上个月的数值，只有横向检查能发现这种漂移。已声明的呈现位置记录在 passport 的 `appears_in` 列表中，见 [`replication-protocol.md` → The horizontal check](../../rules/replication-protocol.md#横向检查)。

## 使用时机

- **投稿前：** 发现"我更新了分析，却忘了更新表 2"这类 bug。
- **用同一批数字做报告或授课前：** 发现上次重跑后从未重新生成的幻灯片、海报或附录。
- **发布复现包前：** 验证代码确实能够复现论文。
- **大改之后：** 确认论文仍与最新代码一致。
- **`/commit` 中的质量门禁：** 稿件 + 分析有改动时，增加一次提交前调用。

## 输入

按 shell 引号规则对 `$ARGUMENTS` 分词，再按顺序解析位置参数并赋给 `manuscript_path` 与 `outputs_dir`，不要读取 shell 的位置参数；这与 `/replication-package` 的具名参数调用一致。含空格的 `manuscript_path`、`outputs_dir` 必须作为单个带引号参数传入，例如 `"manuscripts/my paper.tex" "output files"`。解析后，所有路径都必须以加引号的完整路径使用，例如 `"$manuscript_path"` 与 `"$outputs_dir"`，不得再次分词：

- `manuscript_path` —— 稿件路径（`.tex`、`.qmd`、`.md`、`.pdf`），必填。
- `outputs_dir`（可选）—— 输出目录路径，默认为 `output/`。R、经 [`/stata-replication`](../stata-replication/SKILL.md) 运行的 Stata，以及 Python 流水线都写入这里。也支持 `_targets/objects/`（R `targets` 工作流）和用户指定的其他输出目录。如果 `output/` 不存在，但存在 v2.6 之前的 `scripts/<lang>/_outputs/`，则使用后者，并在报告中说明。

缺少稿件或出现第三个位置参数时，停止并报告用法错误，不得猜测。后续阶段只使用 `manuscript_path` 与 `outputs_dir`，不再读取原始参数串。

## 工作流

### Phase 0：起飞前检查

1. 阅读 [`replication-protocol.md`](../../rules/replication-protocol.md)，获取当前生效的容差阈值。
2. 确认输出目录存在且非空。如果目录为空，或输出早于稿件、已经过期，提示用户先重跑流水线（例如 `Rscript scripts/R/00_run_all.R`），再开始审计。
3. 确认输出目录中有 `sessionInfo.txt` 或等效的环境快照。

### Phase 1：从稿件中提取论断

解析稿件中的数值论断，匹配以下模式：

- **点估计 + 标准误**：`ATT = -1.632 (0.584)`、`$\beta = 0.342$ (0.091)`、带星号显著性的 `hat{\tau} = 1.28**`
- **表格单元格**：LaTeX 表格环境中的 `& -1.632$^{***}$ & 0.584 &`
- **计数**：`our sample of 2,847 firms`、`$N = 2{,}847$`
- **摘要统计量**：`mean = 0.423`、`SD = 0.087`
- **P 值**：`p < 0.01`、`$p = 0.003$`

将每条论断记录为一个元组：

```
{
  claim_id: "Table2_col3_ATT",
  location: "Table 2, Column 3, row 'Treatment'",
  kind: "point_estimate" | "standard_error" | "p_value" | "count" | "percentage",
  reported_value: -1.632,
  uncertainty: 0.584,              # only for point estimates
  significance_stars: 3,            # 0-3 or None
  raw_context: "the ATT estimate of -1.632 (0.584) indicates..."
}
```

将提取的论断写入 `quality_reports/reproducibility_claims_[manuscript-name].json`，让用户在审计前复核提取结果。

### Phase 2：从输出中提取结果

在 `outputs_dir` 中扫描对应数值，按以下优先级读取：

1. **`.rds` 文件** —— 使用 `readRDS(path)$coef[["treatment"]]` 这类方式查找。可用 `Rscript -e "saveRDS(summary(readRDS(...)), '/tmp/audit.rds')"` 提取。
2. **`.tex` 表格** —— 直接解析 LaTeX 表格单元格，按列标题 + 行标签匹配。
3. **`.csv` 摘要文件** —— 用 pandas/readr 解析，再按键值查找。
4. **`.out` / `.log` 文件**（Stata、regress 输出）—— 用正则提取。
5. **`.json`** —— 直接按键查找。

将每个提取结果记录为：

```
{
  source: "output/results.rds",
  lookup_key: "fit_main$coefficients['treated']",
  value: -1.628,
  uncertainty: 0.591,
  p_value: 0.005
}
```

### Phase 2b：收集每一处已声明的呈现（passport 模式）

对 passport 中的每条论断，读取其 `appears_in` 列表，并从每个条目提取**实际呈现**的值：

```
{
  claim_id: "C3",
  displays: [
    { path: "manuscript.tex", locator: "Table 1, Col 2", display_precision: 3, shown: 0.342 },
    { path: "Slides/Lecture04_Results.tex", locator: "frame 'Main result'", display_precision: 2, shown: 0.34 }
  ]
}
```

本轮遵守以下规则：

- 主 `location:` 本身就是呈现位置之一。如果 `appears_in` 再次列出它，仍只计一处呈现，不能重复计数。
- **已声明但无法解析的呈现，包括文件缺失或 `locator` 处没有值，必须记为 `shown: NOT_FOUND`。** 它在 Phase 4c 中判为 FAIL，绝不能跳过，因为失配的 locator 往往正是过期数字的藏身之处。
- **没有** `appears_in` 列表的论断，横向状态是*未检查*，不是检查通过。按 Phase 5 的要求报告，不能默默判过。

### Phase 3：把论断与结果配对

精确标签无法对应时，使用以下模糊启发式：

- 名称相似性（`"treatment effect"` ~ `"ATT"` ~ `"treated"`）
- 量级相似性（若两个候选值与报告值相差在 10% 以内，优先取标准误更接近的那个）
- 来自论断 `raw_context` 字段的上下文线索（表号、行标签、描述）

为每条论断生成带置信度的候选匹配。置信度低于 0.7 时，标记为"UNMATCHED — manual review needed"，不能默默判过。

### Phase 4：容差检查

对每条已匹配论断，应用 `replication-protocol.md` 中的阈值：

| 类型 | 容差 | 示例 |
|---|---|---|
| 整数（N、计数） | 精确 | 2,847 必须等于 2,847 |
| 点估计 | `abs(reported - computed)` < 0.01 | -1.632 对 -1.628 → 差 = 0.004 → PASS |
| 标准误 | `abs(reported - computed)` < 0.05 | 0.584 对 0.591 → 差 = 0.007 → PASS |
| P 值 | 同一显著性水平 | p<0.01 且 p<0.01 → PASS；p<0.01 且 p=0.03 → FAIL |
| 百分比 | ±0.1pp | 42.3% 对 42.35% → PASS |

遵守用户在其 `replication-protocol.md` 分叉中设置的任何**容差覆盖**。用户可能因蒙特卡洛（Monte Carlo）噪声而放宽容差，也可能因行政数据而收紧容差。

### Phase 4b：处置结论 —— PASS / FAIL / EXPLAINED / UNMATCHED

每次容差检查都必须归为以下四种结论之一：

- **PASS** —— 在容差内。
- **FAIL** —— 超出容差，且未记录任何可辩护的替代方案。**阻断**（exit 1）。
- **EXPLAINED** —— 超出容差，**但**作者记录了能够解释差距的*具体、具名替代设定*，见降级规则。将其写入报告，并带入回复审稿人的材料；**不**阻断。
- **UNMATCHED** —— 未找到计算端的对应物（Phase 3 置信度 < 0.7）。永不自动降级。

**不一致不必然意味着失败。** 实证工作中，超容差常常来自*可辩护的替代设定*，而非 bug，例如 `reghdfe` 与 `feols` 的聚类自由度不同、带宽选择规则不同、蒙特卡洛种子/重复次数不同，或呈现时进行了舍入。本技能负责*揭示分歧*，交由人类审计者判断，而不是直接宣布代码正确、论文错误。下文"Stata 专项说明"中的自由度调整注记，就是具名替代方案的典型例子。

**稿件不是外部裁判（oracle）。** 计算值与稿件不一致时，既不能默认代码正确、论文过期，也不能反过来默认论文正确。重构可能破坏原本正确的表，此时*磁盘上的输出*才有 bug；论文也可能仍保留旧数字。计算值只是**挑战者**，不是真相。应报告为"{论文, 代码} 两者之一必须改变——先定位是哪一个"，绝不能要求"让代码回退到与论文一致"。否则可能为了让论文看似"能复现"，撤销真正的 bug 修复。

#### 降级规则：FAIL → EXPLAINED

只有为该确切论断记录了*具体且具名的替代方案*，FAIL 才**可以**降级为 EXPLAINED。记录位置是 passport 条目的 `notes:` 字段（passport 模式），或审计报告的作者注记列（默认模式）。有效注记示例：

> "reghdfe vs feols 聚类自由度调整；在 reghdfe 小样本校正下，发表值为 −1.19，与脚本的 −1.187 在舍入范围内。CODE-CORRECTED pending。"

作者负责**审计**：技能同时展示报告值与计算值，作者写下一行具名替代方案，技能记录并据此判定。结论必须标为 `PAPER-CORRECTED`、`CODE-CORRECTED` 或 `DEFENSIBLE-ALTERNATIVE`。

**硬性下限：以下情况永不可降级为 EXPLAINED。**

- 空白注记、"unclear"、"looks fine"，或任何未写出*具名具体替代设定*的注记。
- **UNMATCHED** 论断，因为没有可比较的计算对应物。
- 直接的数值矛盾，且未提供任何替代方案。

引用/存在性论断不在此范围内。它们由 `/verify-claims` 负责，并在该技能中采用同样的具名替代软化规则。

#### 反复出现的 EXPLAINED 是信号（两次即升级）

沿用 `review-paper --adversarial` 与 [`summary-parity.md`](../../rules/summary-parity.md) 的两次即升级（two-strikes）规则。如果**同一条**论断在**连续两次审计**中都降级为 EXPLAINED，且从未纠正为 PASS，说明作者反复援引替代方案，却始终不更新论文或代码，不能再视为已经解决。必须在 Phase 5 中显著提示：*"这个有争议的数字已被 EXPLAINED 两次，却从未纠正"*，避免长期分歧无限期隐藏在注记后。passport 模式通过比较当前 `status`/`notes` 与上次审计记录来识别这种情况。

### Phase 4c：横向检查——各呈现之间必须彼此一致

Phase 4 比较论断与代码，本阶段则将同一论断的各个呈现**相互比较**，两两检查 Phase 2b 收集的 `displays`：

1. **两侧都舍入到较粗的精度。** 两处呈现分别舍入到二者 `display_precision` 中**较小**的值，相等即为一致。幻灯片中的 `0.34` 与论文中的 `0.342` 按 2 位小数比较时一致；`0.29` 与 `0.342` 则不一致。
2. **不适用容差。** `tolerance:` 块只约束纵向比较，因为那里比较的是两个*测量值*。同一数字的两处呈现是两个*副本*，经第 1 步舍入后，要么相同，要么不同。
3. **处置结论沿用 Phase 4b 的词汇：**
   - **PASS** —— 每一对都一致。
   - **FAIL** —— 任一对不一致，或任一呈现为 `NOT_FOUND`。**永不可降级为 EXPLAINED**。具名替代设定可以解释代码与论文为何不同，却不能解释同一数字的两份副本为何不同。如果某处呈现确实展示*不同*设定，它属于另一条论断，应单独建立 passport 条目。
   - **UNCHECKED** —— 该论断未声明 `appears_in` 列表。报告但不阻断；修复方式是声明这些呈现。
4. **报告哪一侧发生变化，不判断哪一侧正确。** 指出与其他产物不一致的产物及其最后修改时间，由作者判断是幻灯片过期还是论文过期。不要手工修改一处呈现来迁就另一处，而应根据论断指向的输出重新生成两者（[`replication-protocol.md` → Anti-patterns](../../rules/replication-protocol.md#反模式)）。

### Phase 5：报告

写入 `quality_reports/reproducibility_audit_[manuscript-name].md`：

```markdown
# Reproducibility Audit: [Manuscript Title]

**Date:** [YYYY-MM-DD]
**Manuscript:** [path]
**Outputs directory:** [path]
**Tolerance source:** .codebuddy/rules/replication-protocol.md

## Summary

| Status | Count |
|---|---|
| PASS (vertical and horizontal) | N |
| FAIL (diff > tolerance, no named alternative) | M |
| EXPLAINED (out of tolerance, named alternative recorded) | E |
| UNMATCHED (manual review) | K |
| HORIZONTAL DRIFT (declared displays disagree, or a display not found) | H |
| HORIZONTALLY UNCHECKED (claim declares no `appears_in`) | U |
| **Overall verdict** | **PASS / FAIL** (FAIL iff M > 0 or H > 0; EXPLAINED does not fail the audit) |

## PASS (all within tolerance)
| Claim | Reported | Computed | Diff | Tolerance |
|---|---|---|---|---|
| Table2_col3_ATT | -1.632 (0.584) | -1.628 (0.591) | 0.004 / 0.007 | 0.01 / 0.05 |

## FAIL (outside tolerance — BLOCKER)
| Claim | Reported | Computed | Diff | Tolerance | Location in paper | Author note (name a concrete alternative to downgrade → EXPLAINED) |
|---|---|---|---|---|---|---|

## EXPLAINED (out of tolerance; defensible named alternative recorded — non-blocking, carry into response-to-referees)
| Claim | Reported | Computed | Named alternative (why the gap is defensible) | Resolution |
|---|---|---|---|---|
| Table3_col2_ATT | -1.187 | -1.19 | reghdfe vs feols clustering-df adjustment | DEFENSIBLE-ALTERNATIVE |

## UNMATCHED (manual review)
| Claim | Raw context | Candidate sources |
|---|---|---|

## HORIZONTAL DRIFT (one number, two values — BLOCKER)
| Claim | Display A | Display B | Compared at | Values | Which side moved |
|---|---|---|---|---|---|
| C3 | manuscript.tex — Table 1, Col 2 | Slides/Lecture04_Results.tex — frame 'Main result' | 2 decimals | 0.34 vs 0.29 | deck older than the claim's output_file |

## HORIZONTALLY UNCHECKED (no `appears_in` declared)
| Claim | Primary display | Other artifacts to declare |
|---|---|---|

## Environment
[sessionInfo excerpt]

## Next steps
1. Resolve each FAIL row — either correct the manuscript, rerun the analysis, or (if the gap is a defensible alternative spec) record a concrete named alternative to downgrade it to EXPLAINED.
2. Resolve each HORIZONTAL DRIFT row — regenerate the lagging display from the claim's output, never by retyping the other display's value. A `NOT_FOUND` display is fixed by correcting the `locator`, not by dropping the entry.
3. Review UNMATCHED rows — add explicit lookup keys or widen the search scope.
4. Declare `appears_in` for the HORIZONTALLY UNCHECKED rows — every artifact a reader sees the number in.
5. Review EXPLAINED rows before submission — each should map to a sentence in the response-to-referees.
6. After zero FAILs and zero HORIZONTAL DRIFT (EXPLAINED rows allowed), the paper is replication-ready.
```

### Phase 5b：追加到复现日志

上述报告和 passport 每次运行都会重写，不保留历史；日志则负责留存历史。无论默认模式还是 passport 模式，每次运行后都要向 `quality_reports/replication-log.md` **追加**一个区块。该文件会提交，因此共同作者或数据编辑无需阅读代码，也能了解检查内容、对应提交和每个数字的计算方式。

- **只追加。** 使用 `>>` 写入，绝不编辑或重排旧区块。纠错必须通过一次新运行完成，不能直接修改旧记录。仓库卫生门禁会拒绝编辑或删除已提交行的提交：提交前钩子对照最后一次提交检查，CI 对照工作合入的分支检查。它只能证明旧条目未被编辑，不能证明每次运行都已记录。披露脱敏是唯一例外：使用 `ALLOW_LOG_REWRITE=1` 提交，并在提交信息中说明原因。
- **记录修订戳。** 使用短提交哈希；如果 `quality_reports/` 之外有任何未提交内容（含未跟踪文件），添加 `-dirty`。这样，针对未提交代码的结论可以自证来源，而审计自己写入的报告文件不会触发该标记。不在 git 中或首次提交之前，戳记为 `no-commit`。
- **"如何计算"必须填写 Phase 2 实际使用的访问器或命令**，详细到足以让他人重新算出该数字。
- **受限数据：** 日志包含与报告相同的数字，因此与任何产出一样，只有通过披露审查后才能提交（[`confidential-data.md`](../../rules/confidential-data.md)）。

```bash
LOG=quality_reports/replication-log.md
[ -f "$LOG" ] || printf '%s\n' "# Replication log" "" \
  "Append-only record of /audit-reproducibility runs: what was checked, against which commit, and how each number was computed. Never edit a past entry; a correction is a new run." "" > "$LOG"
# -dirty = anything uncommitted outside quality_reports/, untracked files included (the audit writes its own files in quality_reports/)
if REV=$(git rev-parse --short HEAD 2>/dev/null); then
  [ -n "$(git status --porcelain -- . ':(exclude)quality_reports' 2>/dev/null)" ] && REV="$REV-dirty"
else
  REV="no-commit"   # not a git repository, or nothing committed yet
fi
printf '## %s — %s @ %s\n\n' "$(date +%F)" "<manuscript path>" "$REV" >> "$LOG"
# Quoted heredoc: nothing below is expanded, so an accessor's `$` or backtick is written as-is.
cat >> "$LOG" <<'EOF'
Outputs: `<outputs dir>` · Verdict: **<PASS|FAIL>** (<M> FAIL, <H> horizontal drift, <E> EXPLAINED, <K> unmatched)

| Claim | Location | Reported | Computed | How computed | Tolerance | Verdict |
|---|---|---|---|---|---|---|
| Table2_col3_ATT | main.tex: Table 2, col 3 | -1.632 | -1.628 | `readRDS("output/results.rds")$coef[["treatment"]]` | 0.01 | PASS |

EOF
```

每条已审计论断占一行，顺序与报告一致。

## 退出行为

- **全部 PASS（或 PASS + EXPLAINED）：** exit 0，打印摘要。
- **出现任何 HORIZONTAL DRIFT：** exit 1，按 FAIL 同等处理。两个产物对同一数字显示不同值，无论哪一个正确，都是缺陷。HORIZONTALLY UNCHECKED 行只发出警告（exit 0）并列出。
- **出现任何 FAIL：** exit 1，并将摘要打印到 stderr，使本技能可以作为 `/commit` 的提交前门禁；执行方式见 `replication-protocol.md`。**EXPLAINED 行不计为 FAIL，也绝不触发 exit 1**，只呈现，不阻断。真正的 FAIL（没有具名替代方案）以及捏造/UNMATCHED 论断仍会受到完整检查。
- **UNMATCHED > 0（且 FAIL = 0）：** exit 0 并附警告，用户必须人工复核。

## 源语言覆盖

本技能将稿件论断与三种源语言生态的输出比对，三者都写入同一个 `output/` 目录：

| 来源 | 默认输出目录 | 读取输出的方式 | 常见论断来源 |
|---|---|---|---|
| **R**（默认） | `output/` | `readRDS()`、`arrow::read_parquet()`、`vroom::vroom()` | `.rds` / `.parquet` / `.csv` / `tinytable` 生成的 `.tex` |
| **Stata**（v1.9.0） | `output/` | 从 R 用 `haven::read_dta()`，或从 Python 用 `pyreadstat.read_dta()` | `.dta` / `esttab` 生成的 `.tex` / `.smcl` 日志中的数值 |
| **Python** | `output/`（或 `_targets/`） | `pandas.read_parquet`、`pickle.load` | `.parquet` / `.pickle` / `.csv` |

**Stata 专项说明（v1.9.0）：**

- 使用 `haven::read_dta()`（R）或 `pyreadstat.read_dta()`（Python）读取 `.dta` 输出；如果稿件引用表格单元格数值，则解析对应的 `esttab` `.tex`。
- 稿件中的单元格 `\input{output/tab_main.tex}` 是最强的溯源信号，因为该单元格的值直接来自 .do 文件。应将 `.tex` 中的位置与 `03_analyze.do` 中的回归调用对应起来。
- `reghdfe` 与 base `reg, cluster()` 的聚类自由度调整可能不同。标准误若仅在第 2 位小数不一致，`replication-protocol.md` 中的容差可以覆盖；若在第 1 位小数就不一致，应检查自由度调整。

## passport 模式（v1.9.0）

如果 `quality_reports/passports/<paper-slug>.yaml` 存在，本技能以 **passport 模式**运行，不再只输出一次性报告，而是就地**读取、更新并重写**该 passport 文件。

- 对 passport 中每个 `claims:` 条目，执行与默认模式相同的数值审计：在 `location` 处从稿件提取报告值，在 `source_file:source_line` / `output_file:output_field` 处定位计算值，并与 `tolerance:` 比较。**随后**对该条目的 `appears_in` 列表执行 Phase 2b 与 4c 的横向扫描。
- 每条论断审计后，就地更新 `status`：
  - PASS → 论断在容差内，**且**每处已声明呈现按较粗精度比较都一致。
  - FAIL → 论断超出容差，**且**条目的 `notes` 未具名具体替代方案；**或**两处已声明呈现不一致；**或**某个 `appears_in` 条目无法在对应文件中定位。将不一致写入 `notes`：纵向 FAIL 记录报告值与计算值，横向 FAIL 记录两个呈现值及其路径。阻断（exit 1）。
  - EXPLAINED → 论断超出容差，**但**条目的 `notes` 已记录*具体具名的替代设定*，且非空白、不是"unclear"。技能下次运行时读取 `notes`，将同一条超容差论断判为 EXPLAINED 而非 FAIL，只呈现，不阻断。硬性下限仍然适用：UNMATCHED 论断或没有具名替代方案的注记仍判 FAIL。
  - STALE → 如果 `source_file`、`output_file` 或任一 `appears_in` 路径的修改时间晚于 `last_verified_on`，标为 STALE 并重跑审计逻辑。重跑后状态变为 PASS / FAIL / EXPLAINED，因此 STALE 只是瞬时状态。
- 更新每条论断的 `last_verified_on` 与 `last_verified_by: "/audit-reproducibility"`。
- 更新顶层的 `paper.last_audit`。

如果稿件中的论断没有对应 passport 条目，发出 UNVERIFIED 警告，提示作者补充。passport 范围由作者维护，不自动填充，以免错误推断。

passport 模式不会删除条目。如果某条论断从稿件中消失，其 passport 条目仍保留并标为 STALE，由作者决定删除（论断撤回），还是更新条目的 `location`（论断移位）。

它也不会自行添加 `appears_in` 条目。扫描中偶然发现的其他呈现，例如同一数值出现在未声明的幻灯片或附录中，只在 HORIZONTALLY UNCHECKED 表中作为建议报告，由作者决定是否声明。原因与不自动填充相同：如果推断出的呈现实际属于另一个量，横向检查会一直失败。

完整 schema 与集成点（`/commit`、`/review-paper`）见 [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) 的 "Claims Provenance: `passport.yaml`" 一节。

## 交叉引用

- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 容差契约 + passport schema。
- [`templates/passport-template.yaml`](../../../templates/passport-template.yaml) —— 新论文的起始模板；在 `appears_in` 列表中声明各呈现位置。
- [`.codebuddy/hooks/claim-reconcile.py`](../../hooks/claim-reconcile.py) —— 提供事件驱动提示：写入被跟踪的脚本、输出或已声明呈现时，指出需要重新审计的论断。它负责统计声明，本技能负责比对。
- [`.codebuddy/skills/review-r/SKILL.md`](../review-r/SKILL.md) —— 检查代码风格；本技能检查数值层面的可复现性。
- [`.codebuddy/skills/diagnose/SKILL.md`](../diagnose/SKILL.md) —— 论断判为 **FAIL**，且需要定位*哪个*流水线步骤产生超容差值时，交给 `/diagnose` 分析单论断根因：复现 → 最小化 → 二分。
- [`.codebuddy/skills/review-paper/SKILL.md`](../review-paper/SKILL.md) —— 内容审查；与本技能配合，完成投稿前审计。
- [`.codebuddy/skills/replication-package/SKILL.md`](../replication-package/SKILL.md) —— 组装 AEA DCAS 存档前，以本技能作为门禁。
- [`.codebuddy/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) · [`.codebuddy/skills/disclosure-check/SKILL.md`](../disclosure-check/SKILL.md) —— 后续的环境快照 + 受限数据筛查。

## 本技能不做的事

- **不重跑你的分析。** 本技能只比较*当前*输出与稿件论断。输出过期时，请先重跑流水线，起飞前阶段会发出警告。即使用户另行要求重跑，也应作为独立任务处理，不属于本技能的默认路径。
- **不检查设定是否错误。** 回归顺利编译并可复现地产出 `-1.632`，只能说明结果可复现；`-1.632` 是否是*正确的*估计目标（estimand），应由 `review-paper` / 领域审阅者判断。
- **不检查外部包版本。** `sessionInfo.txt` 快照让审阅者看到环境；用户使用 `renv.lock` 或 `DESCRIPTION` 文件自行钉住版本。
