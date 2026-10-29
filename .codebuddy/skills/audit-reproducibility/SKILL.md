---
name: audit-reproducibility
description: 交叉核对稿件中的数值论断与 R / Stata / Python 的实际产出，以强制执行 replication-protocol.md 的规则。按容差阈值对每条论断报告 PASS/FAIL。在投稿前、发布复现包（replication package）前使用。
argument-hint: "[manuscript path] [outputs-dir] (outputs-dir defaults to output/)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent", "Task", "Monitor"]

---

# 复现性审计

把稿件中的数值论断（点估计、标准误、p 值、计数）与分析流水线实际产出的结果做比对。对每条论断，按 [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) 中定义的容差阈值报告 PASS / FAIL。

**核心原则：** 若论文写 `ATT = -1.632 (0.584)`，而代码产出 `-1.628 (0.591)`，我们要**数值上**验证两者之差落在文档化的容差之内。不再有"看着差不多"的目测。

**两个方向，不是一个。** *纵向*上，每条论断与产出它的那份输出核对。*横向*上，它与**其他**每一个显示同一个数字的产物核对——附录表、幻灯片、海报。纵向检查会安然通过，而某份幻灯片仍在引用上个月的数值；只有横向检查能抓到它。已声明的呈现位置记录在 passport 的 `appears_in` 列表中——见 [`replication-protocol.md` → The horizontal check](../../rules/replication-protocol.md#横向检查)。

## 使用时机

- **投稿前。** 抓"我更新了分析，却忘了更新表 2"这类 bug。
- **用同一批数字做报告或授课前。** 抓上一次重跑之后从未重新生成的幻灯片、海报或附录。
- **发布复现包前。** 验证代码确实能复现论文。
- **大改之后。** 确保论文仍与最新代码一致。
- **`/commit` 中的质量门禁。** 在稿件 + 分析有改动时，配一次提交前调用。

## 输入

- `$0` —— 稿件路径（`.tex`、`.qmd`、`.md`、`.pdf`）。必填。
- `$1` —— 输出目录路径。默认为 `output/`，各语言的流水线都写入此处（R、经 [`/stata-replication`](../stata-replication/SKILL.md) 的 Stata、Python）。可识别的替代位置：`_targets/objects/`（R `targets` 工作流），以及用户指定的输出所在的任意目录。若 `output/` 不存在、但存在 v2.6 之前的 `scripts/<lang>/_outputs/`，则用后者，并在报告中说明。

## 工作流

### Phase 0：起飞前检查

1. 阅读 [`replication-protocol.md`](../../rules/replication-protocol.md)，取得当前生效的容差阈值。
2. 确认输出目录存在且非空。若为空或已过期（早于稿件），提示用户先重跑流水线（例如 `Rscript scripts/R/00_run_all.R`）再审计。
3. 确保输出目录中存在 `sessionInfo.txt` 或等效的环境快照。

### Phase 1：从稿件中提取论断

解析稿件中的数值论断。要匹配的模式：

- **点估计 + 标准误**：`ATT = -1.632 (0.584)`、`$\beta = 0.342$ (0.091)`、带星号显著性的 `hat{\tau} = 1.28**`
- **表格单元格**：LaTeX 表格环境中的 `& -1.632$^{***}$ & 0.584 &`
- **计数**：`our sample of 2,847 firms`、`$N = 2{,}847$`
- **摘要统计量**：`mean = 0.423`、`SD = 0.087`
- **P 值**：`p < 0.01`、`$p = 0.003$`

把每条论断记录为一个元组：

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

把提取出的论断写入 `quality_reports/reproducibility_claims_[manuscript-name].json`，便于用户在审计前复核提取结果。

### Phase 2：从输出中提取结果

在 `$1` 中扫描对应数值。优先级顺序：

1. **`.rds` 文件** —— `readRDS(path)$coef[["treatment"]]` 式查找。可用 `Rscript -e "saveRDS(summary(readRDS(...)), '/tmp/audit.rds')"` 提取。
2. **`.tex` 表格** —— 直接解析 LaTeX 表格单元格；按列标题 + 行标签匹配。
3. **`.csv` 摘要文件** —— 用 pandas/readr 解析，键值查找。
4. **`.out` / `.log` 文件**（Stata、regress 输出）—— 正则提取。
5. **`.json`** —— 直接按键查找。

把每个提取到的结果记录下来：

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

对 passport 中的每条论断，读取其 `appears_in` 列表，并在每个条目处摘下**按呈现形式**的值：

```
{
  claim_id: "C3",
  displays: [
    { path: "manuscript.tex", locator: "Table 1, Col 2", display_precision: 3, shown: 0.342 },
    { path: "Slides/Lecture04_Results.tex", locator: "frame 'Main result'", display_precision: 2, shown: 0.34 }
  ]
}
```

本轮规则：

- 主 `location:` 是这些呈现位置之一，不是另立之物——若 `appears_in` 重复了它，那也只是一处呈现，不是两处。
- **已声明却无法解析的呈现——文件缺失，或 `locator` 处没有值——记为 `shown: NOT_FOUND`。** 它在 Phase 4c 中判为 FAIL。绝不跳过它：一个已悄悄失配的 locator，正是过期数字藏身之处。
- **没有** `appears_in` 列表的论断在横向上是*未检查*，不是横向干净。按此报告（见 Phase 5），而不是默默判过。

### Phase 3：把论断与结果配对

精确标签对不上时，用模糊启发式：

- 名称相似性（`"treatment effect"` ~ `"ATT"` ~ `"treated"`）
- 量级相似性（若两个候选值与报告值相差在 10% 以内，优先取标准误更接近的那个）
- 来自论断 `raw_context` 字段的上下文线索（表号、行标签、描述）

对每条论断产出一个带置信度的候选匹配。置信度低于 0.7 的论断标记为"UNMATCHED — manual review needed"，而不是默默判过。

### Phase 4：容差检查

对每条已匹配的论断，应用 `replication-protocol.md` 中的阈值：

| 类型 | 容差 | 示例 |
|---|---|---|
| 整数（N、计数） | 精确 | 2,847 必须等于 2,847 |
| 点估计 | `abs(reported - computed)` < 0.01 | -1.632 对 -1.628 → 差 = 0.004 → PASS |
| 标准误 | `abs(reported - computed)` < 0.05 | 0.584 对 0.591 → 差 = 0.007 → PASS |
| P 值 | 同一显著性水平 | p<0.01 且 p<0.01 → PASS；p<0.01 且 p=0.03 → FAIL |
| 百分比 | ±0.1pp | 42.3% 对 42.35% → PASS |

尊重用户写进其 `replication-protocol.md` 分叉中的任何**容差覆盖**（他们可能为蒙特卡洛（Monte Carlo）噪声放宽，或为行政数据收紧）。

### Phase 4b：处置结论 —— PASS / FAIL / EXPLAINED / UNMATCHED

一次容差检查归结为四种处置结论之一：

- **PASS** —— 在容差内。
- **FAIL** —— 超出容差，且未记录任何可辩护的替代方案。**阻断**（exit 1）。
- **EXPLAINED** —— 超出容差，**但**作者记录了能够解释该差距的*具体、具名的替代设定*（见降级规则）。在报告中呈现，并带入回复审稿人的材料；**不**阻断。
- **UNMATCHED** —— 未找到计算端的对应物（Phase 3 置信度 < 0.7）。永不自动降级。

**不一致并不自动等于失败。** 在实证工作中，最常见的超容差结果是*可辩护的替代设定*，而不是 bug —— `reghdfe` 与 `feols` 的聚类自由度、不同的带宽选择规则、不同的蒙特卡洛种子/重复次数，或呈现舍入。本技能的职责是*把分歧摆上台面*供人类审计者判断，而不是宣布代码对、论文错。（下文"Stata 专项说明"中的自由度调整注记即具名替代方案的典型例子。）

**稿件不是外部裁判（oracle）。** 当计算值与稿件不一致时，不要推定代码正确、论文过期——也不要推定反过来。一次重构可能弄坏了原本正确的表（*磁盘上的输出*才是有 bug 的那个），也可能论文带着一个旧数字。计算值只是**挑战者**，不是真相。把不一致报告为"{论文, 代码} 两者之一必须改变——先定位是哪一个"，绝不要写成"让代码回退到与论文一致"。这避免了为让论文"能复现"而回退一个真正的 bug 修复的陷阱。

#### 降级规则：FAIL → EXPLAINED

只有当针对该确切论断记录了*具体且具名的替代方案*时，一个 FAIL 才**可以**降级为 EXPLAINED——记录在 passport 条目的 `notes:` 字段（passport 模式）或审计报告的作者注记列（默认模式）。一个有效注记的例子：

> "reghdfe vs feols 聚类自由度调整；在 reghdfe 小样本校正下，发表值为 −1.19，与脚本的 −1.187 在舍入范围内。CODE-CORRECTED pending。"

作者是**审计者**：技能把双向对比摆出来（报告值与计算值都展示）；人写出一行具名替代方案；技能记录它，并从此遵循它。给结论打上 `PAPER-CORRECTED`、`CODE-CORRECTED` 或 `DEFENSIBLE-ALTERNATIVE` 标签。

**硬性下限——永不可降级为 EXPLAINED：**

- 空白注记、"unclear"、"looks fine"，或任何没有*具名具体替代设定*的注记。
- 一条 **UNMATCHED** 论断（没有可比较的计算对应物）。
- 平白的数值矛盾且未提供任何替代方案。

（引用/存在性论断不在此范围内——`/verify-claims` 负责那些，并在它那一侧施加同样的具名替代软化。）

#### 反复出现的 EXPLAINED 是信号（两次即升级）

复用 `review-paper --adversarial` 与 [`summary-parity.md`](../../rules/summary-parity.md) 的两次即升级（two-strikes）规则：若**同一条**论断在**连续两次审计**中都被降级为 EXPLAINED、且从未被纠正为 PASS（作者一再援引替代方案，却从不更新论文或代码），就不要再把它当作已悄悄解决。在 Phase 5 中显著呈现——*"这个有争议的数字已被 EXPLAINED 两次，却从未纠正"*——如此，一处长期存在的分歧就无法无限期地藏在一个已记录的注记后面。passport 模式下，通过把当前的 `status`/`notes` 与上次审计的记录相比来检测。

### Phase 4c：横向检查——各呈现之间必须彼此一致

Phase 4 把论断与代码相比。本阶段把论断的各个呈现**彼此**相比，就 Phase 2b 收集到的 `displays` 两两比较：

1. **两侧都舍入到较粗的精度。** 两处呈现各自舍入到二者 `display_precision` 中**较小**的那个值后若相等，即算一致。幻灯片里的 `0.34` 对论文里的 `0.342`，按 2 位小数一致；`0.29` 对 `0.342` 则不一致。
2. **不适用容差。** `tolerance:` 块管辖的是纵向比较，那里比较的是两个*测量值*。同一个数字的两处呈现是两个*副本*——经第 1 步舍入之后，它们要么相同，要么不同。
3. **处置结论，沿用 Phase 4b 的词汇：**
   - **PASS** —— 每一对都一致。
   - **FAIL** —— 任一对不一致，或任一呈现为 `NOT_FOUND`。**永不可降级为 EXPLAINED**：具名替代设定解释的是代码与论文为何不同，对"同一数字的两份副本为何不同"无话可说。若某处呈现确实展示了*不同*的设定，那是另一条论断，应自立 passport 条目。
   - **UNCHECKED** —— 该论断未声明 `appears_in` 列表。报告但不阻断；修法是声明这些呈现。
4. **报告是哪一侧变了，不是哪一侧对。** 点名那个与其余不一致的产物，以及它最后被动过的时间；由作者判定是幻灯片过期还是论文过期。不要手工改一处呈现去迁就它的兄弟——从论断所指向的输出把两者重新推导出来（[`replication-protocol.md` → Anti-patterns](../../rules/replication-protocol.md#反模式)）。

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

上面的报告与 passport 每次运行都会被重写，因此二者都不留历史。日志留。每次运行之后——默认模式与 passport 模式皆然——**追加**一个区块到 `quality_reports/replication-log.md`。该文件会被提交，因此共同作者或数据编辑不必读代码，就能看到检查了什么、对着哪个提交、每个数字如何得来。

- **只追加。** 用 `>>` 写入；绝不编辑或重排过去的区块。纠错是一次新的运行，不是一次编辑。仓库卫生门禁会让编辑或删除已提交行的提交失败——在提交前钩子处对着最后一次提交检查，在 CI 中对着工作合入的分支检查。它证明的是没有条目被编辑过，而不是每次运行都被记录。披露脱敏是唯一的例外：用 `ALLOW_LOG_REWRITE=1` 提交，并在提交信息里写明原因。
- **盖上修订戳。** 短提交哈希；当 `quality_reports/` 之外有任何未提交内容（含未跟踪文件）时加 `-dirty`——这样针对未提交代码的结论会自证来源，而审计自己写出的报告文件不会触发它。不在 git 中，或首次提交之前，戳记为 `no-commit`。
- **"如何计算"写的是 Phase 2 实际用过的那个访问器或命令**——足以让另一个人重算出那一个数字。
- **受限数据：** 日志承载与报告相同的数字，因此与任何产出一样，只在披露审查通过后才提交（[`confidential-data.md`](../../rules/confidential-data.md)）。

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

每条已审计论断一行，顺序与报告一致。

## 退出行为

- **全部 PASS（或 PASS + EXPLAINED）：** exit 0，打印摘要。
- **出现任何 HORIZONTAL DRIFT：** exit 1，与 FAIL 同等对待——两个产物对同一个数字显示不同取值，无论哪一个对，都是缺陷。HORIZONTALLY UNCHECKED 行只警告（exit 0）并列出。
- **出现任何 FAIL：** exit 1，摘要打印到 stderr。这使本技能可作为 `/commit` 的提交前门禁使用——执行范式见 `replication-protocol.md`。**EXPLAINED 行不计为 FAIL，也绝不触发 exit 1**——它们只是被呈现，不阻断。门禁对真正的 FAIL（没有具名替代方案）与捏造/UNMATCHED 论断保有其全部牙齿。
- **UNMATCHED > 0（且 FAIL = 0）：** exit 0 并附警告——用户必须人工复核。

## 源语言覆盖

本技能把稿件论断与三种源语言生态的产出相比。三者都写入同一个 `output/` 目录：

| 来源 | 默认输出目录 | 读取输出的方式 | 常见论断来源 |
|---|---|---|---|
| **R**（默认） | `output/` | `readRDS()`、`arrow::read_parquet()`、`vroom::vroom()` | `.rds` / `.parquet` / `.csv` / `tinytable` 生成的 `.tex` |
| **Stata**（v1.9.0） | `output/` | 从 R 用 `haven::read_dta()`，或从 Python 用 `pyreadstat.read_dta()` | `.dta` / `esttab` 生成的 `.tex` / `.smcl` 日志中的数值 |
| **Python** | `output/`（或 `_targets/`） | `pandas.read_parquet`、`pickle.load` | `.parquet` / `.pickle` / `.csv` |

**Stata 专项说明（v1.9.0）：**

- `.dta` 输出经 `haven::read_dta()`（R）、`pyreadstat.read_dta()`（Python）读取，或在稿件引用的是表格单元格数值时，解析对应的 `esttab` `.tex`。
- 稿件的单元格 `\input{output/tab_main.tex}` 是最强的溯源信号——该单元格的值机械地来自 .do 文件。把 `.tex` 中的位置与 `03_analyze.do` 中的回归调用对上。
- 聚类自由度调整在 `reghdfe` 与 base `reg, cluster()` 之间可能不同。若标准误在第 2 位小数处不符，`replication-protocol.md` 中的容差能覆盖；若在第 1 位小数处就不符，去查自由度调整。

## passport 模式（v1.9.0）

当 `quality_reports/passports/<paper-slug>.yaml` 存在时，本技能以 **passport 模式**运行：它不再输出一份一次性报告，而是就地**读取、更新并重写**该 passport 文件。

- 对 passport 中每个 `claims:` 条目，执行与默认模式相同的数值审计（在 `location` 处从稿件提取报告值，在 `source_file:source_line` / `output_file:output_field` 处定位计算值，与 `tolerance:` 比较），**然后**对该条目的 `appears_in` 列表执行 Phase 2b 与 4c 的横向扫描。
- 每条论断审计后，就地更新 `status`：
  - PASS → 论断在容差内**且**每一处已声明的呈现按较粗精度一致。
  - FAIL → 论断超出容差**且**其条目的 `notes` 未具名具体替代方案；**或**两处已声明的呈现不一致；**或**某个 `appears_in` 条目在其文件中定位不到。把不一致记入 `notes`——纵向 FAIL 记报告值对计算值，横向 FAIL 记两个呈现值及其路径。阻断（exit 1）。
  - EXPLAINED → 论断超出容差，**但**该条目的 `notes` 已记录*具体具名的替代设定*（非空白，不是"unclear"）。技能在下一次运行时读 `notes`，把同一条超容差论断判为 EXPLAINED 而非 FAIL——呈现，不阻断。硬性下限依然适用：UNMATCHED 论断、或没有具名替代方案的注记，仍判 FAIL。
  - STALE → 若 `source_file`、`output_file` 或任一 `appears_in` 路径的修改时间晚于 `last_verified_on`，标记为 STALE 并重跑审计逻辑（重跑之后，状态变为 PASS / FAIL / EXPLAINED——STALE 是瞬时的）。
- 每条论断更新 `last_verified_on` 与 `last_verified_by: "/audit-reproducibility"`。
- 在顶层更新 `paper.last_audit`。

若在稿件中检测到一条没有对应 passport 条目的论断，发出 UNVERIFIED 警告——作者应当补上它（passport 的范围由作者策展，不自动填充，以避免错误推断）。

passport 模式不删除 passport 条目。若某条论断从稿件中消失，该 passport 条目保留并带 STALE 状态——由作者决定是删除（论断撤回）还是更新条目的 `location`（论断移位）。

它也不会自行添加 `appears_in` 条目。扫描偶然注意到的一处呈现——同一个数值出现在某份幻灯片或附录中，而 passport 从未声明——会在 HORIZONTALLY UNCHECKED 表中作为建议报告；由作者来声明。理由与上文的不自动填充规则相同：一处被推断出来、实际上却是另一个量的呈现，会让横向检查永远失败。

完整 schema 与集成点（`/commit`、`/review-paper`）见 [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) 的 "Claims Provenance: `passport.yaml`" 一节。

## 交叉引用

- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 容差契约 + passport schema。
- [`templates/passport-template.yaml`](../../../templates/passport-template.yaml) —— 为新论文复制用的起始文件；`appears_in` 列表就是声明各呈现位置的地方。
- [`.codebuddy/hooks/claim-reconcile.py`](../../hooks/claim-reconcile.py) —— 事件驱动的提示：写入被跟踪的脚本、输出或已声明的呈现时，会点名需要重新审计的论断。它数的是声明；做比对的是本技能。
- [`.codebuddy/skills/review-r/SKILL.md`](../review-r/SKILL.md) —— 抓代码风格问题；本技能抓的是数值层面的可复现性。
- [`.codebuddy/skills/diagnose/SKILL.md`](../diagnose/SKILL.md) —— 当某条论断判为 **FAIL**、而你需要定位是*哪一个*流水线步骤产出了这个超容差值时，交接给 `/diagnose`（单论断根因：复现 → 最小化 → 二分）。
- [`.codebuddy/skills/review-paper/SKILL.md`](../review-paper/SKILL.md) —— 内容审查；与技能配合即为一次完整的投稿前审计。
- [`.codebuddy/skills/replication-package/SKILL.md`](../replication-package/SKILL.md) —— 在组装 AEA DCAS 存档之前，以本技能为门禁。
- [`.codebuddy/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) · [`.codebuddy/skills/disclosure-check/SKILL.md`](../disclosure-check/SKILL.md) —— 下游的环境快照 + 受限数据筛查。

## 本技能不做的事

- **重跑你的分析。** 本技能把*当前*输出与稿件论断相比。若输出已过期，请先重跑流水线（起飞前阶段会警告）。
- **抓错误的设定。** 一次编译干净、产出可复现的 `-1.632` 的回归是可复现的。而 `-1.632` 是否是*正确的*估计目标（estimand），那是 `review-paper` / 领域审阅者的问题。
- **检查外部包版本。** `sessionInfo.txt` 快照让审阅者能看到环境；钉住版本是用户自己的事（用 `renv.lock` 或 `DESCRIPTION` 文件）。

## 长批量重跑：使用 Monitor 工具（2026 年 4 月）

当 `/audit-reproducibility` 被要求核验一篇论文中*全部*数值论断时，最稳妥的做法是重跑整条流水线（`00_run_all.R` 或等效物），再把重新生成的输出与稿件数值相比。对超过几分钟的流水线，后台启动重跑，并用 Anthropic 的 **Monitor 工具**（2026 年 4 月第 15 周）流式读取 stdout。这样审计可以在流中就对错误作出反应，而不必等整条流水线跑完才注意到某一步失败。
