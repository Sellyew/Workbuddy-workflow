---
paths:
  - "scripts/**/*.R"
  - "Figures/**/*.R"
---

# 复现优先协议

**核心原则：** 先一分不差地复现原始结果，再做扩展。

---

## 阶段 1：清点与基线

在写任何 R 代码之前：

- [ ] 读论文的复现 README
- [ ] 清点复现包：语言、数据文件、脚本、输出
- [ ] 记录论文中的基准数值：

```markdown
## Replication Targets: [Paper Author (Year)]

| Target | Table/Figure | Value | SE/CI | Notes |
|--------|-------------|-------|-------|-------|
| Main ATT | Table 2, Col 3 | -1.632 | (0.584) | Primary specification |
```

- [ ] 把目标存进 `quality_reports/LectureNN_replication_targets.md`，或存成 RDS

---

## 阶段 2：翻译与执行

- [ ] 全部 R 编码标准遵循 `r-code-conventions.md`
- [ ] 一开始逐行翻译，复现期间不要「改进」
- [ ] 精确匹配原始设定（协变量、样本、聚类、标准误计算）
- [ ] 所有中间结果存为 RDS

### Stata 到 R 的翻译陷阱

<!-- 定制：补充你所在领域特有的陷阱 -->

| Stata | R | 陷阱 |
|-------|---|------|
| `reg y x, cluster(id)` | `feols(y ~ x, cluster = ~id)` | Stata 的聚类自由度调整与部分 R 包不同 |
| `areg y x, absorb(id)` | `feols(y ~ x \| id)` | 检查去均值方法是否一致 |
| PS 用 `probit` | `glm(family=binomial(link="probit"))` | 在某些命令里，R 默认的 logit 不等于 Stata 默认 |
| `bootstrap, reps(999)` | 视方法而定 | 精确对齐种子、次数与 bootstrap 类型 |

---

## 阶段 3：核对匹配

验证要沿两个方向进行。**纵向**验证把每条断言与产生它的输出对照，并按下面的容差检查。**横向**验证把每条断言与展示同一个数字的所有*其他*产物对照，见[横向检查](#横向检查)。一个数值可能通过所有纵向检查，却仍是幻灯片上一个月前的旧值。

### 容差阈值

| 类型 | 容差 | 理由 |
|------|-----------|-----------|
| 整数（N、计数） | 完全一致 | 没有任何理由出现差异 |
| 点估计 | < 0.01 | 论文展示时的四舍五入 |
| 标准误 | < 0.05 | Bootstrap/聚类带来的波动 |
| P 值 | 显著性水平一致 | 精确 p 值可能略有差异 |
| 百分比 | < 0.1pp | 展示时的四舍五入 |

### 若出现不匹配

**不要进入扩展阶段。** 找出引入差异的步骤，检查样本量、标准误计算、默认选项和变量定义等常见原因。即使最后没有查清，也要记录这次排查。若要定位*哪一步*发生漂移，使用 [`/diagnose`](../skills/diagnose/SKILL.md)，按复现、最小化、二分流水线的顺序排查。它负责查找单条断言的根因，`/audit-reproducibility` 则负责整篇论文的检查。

**出现不匹配时，不能预设代码就是对的。** 磁盘上的输出只是用来质疑稿件的证据，不是最终裁判。重构可能破坏原本正确的表格，所以也可能是*稿件*中的数字正确，而代码已经过期或存在 bug。应当表述为「{论文, 代码} 中必有一个要改，先隔离出是哪一个」，绝不能直接说「把代码改回去以对齐论文」。

**有依据的替代解释不等于失败。** 如果差距可以由*具体、具名的替代设定*解释，例如 `reghdfe` 与 `feols` 的聚类自由度、不同的带宽选择规则、蒙特卡洛种子/次数或展示时的四舍五入，就记录该替代设定，并把断言标为 **EXPLAINED**，而不是 FAIL。具体语义见下面的 `status`。空白或含糊的备注，例如「不清楚」，永远不能用来降级 FAIL。

### 复现报告

保存到 `quality_reports/LectureNN_replication_report.md`：

```markdown
# Replication Report: [Paper Author (Year)]
**Date:** [YYYY-MM-DD]
**Original language:** [Stata/R/etc.]
**R translation:** [script path]

## Summary
- **Targets checked / Passed / Failed:** N / M / K
- **Overall:** [REPLICATED / PARTIAL / FAILED]

## Results Comparison

| Target | Paper | Ours | Diff | Status |
|--------|-------|------|------|--------|

## Discrepancies (if any)
- **Target:** X | **Investigation:** ... | **Resolution:** ...

## Environment
- R version, key packages (with versions), data source
```

---

## 阶段 4：到这时才扩展

复现通过验证后，也就是所有目标均为 PASS：

- [ ] 提交复现脚本："Replicate [Paper] Table X -- all targets match"
- [ ] 现在再做课程相关的改动扩展（不同估计量、新图等）
- [ ] 每个扩展都建立在已核验的基线上

---

## 执行

本规则由 [`/audit-reproducibility`](../skills/audit-reproducibility/SKILL.md) 技能执行。它从稿件中解析数值断言，在 `output/` 或用户指定的输出目录中找到对应取值，再按上面的容差阈值比对。运行时机如下：

- **提交之前** — `/audit-reproducibility path/to/manuscript.tex`
- **发布复现包之前** — 使用同样的调用，目标是零 FAIL。
- **作为 pre-commit 门禁** — 当 diff 同时触及稿件与分析文件时，接入 `/commit`。

只要有一项超出容差，该技能就以 1 退出，因此可以直接接入质量门禁。

---

## 断言溯源：`passport.yaml`

每篇论文的每个分支各有一份护照。它是位于 `quality_reports/passports/<paper-slug>.yaml` 的 YAML 文件，记录稿件中每条已核验数值断言所对应的脚本调用和输出文件。这项约定只处理数值断言，包括点估计、标准误、p 值、样本量、表格/图中的百分比；散文断言由 `/verify-claims` 单独处理。

`templates/passport-template.yaml` 是起始文件。fork 本仓库的使用者应当为每篇论文复制一次。

### 结构

```yaml
paper:
  slug: <paper-slug>                              # used in filename + report headings
  title: <full paper title>
  branch: <git branch on which this passport is current>
  last_audit: <ISO-8601 timestamp>
  last_audit_by: "/audit-reproducibility"         # or human, or another skill

claims:
  - id: C1                                        # stable identifier (used in cross-references)
    claim: "ATT = -1.632 (SE 0.584, N=4291)"     # exact text or paraphrase from manuscript
    location: "manuscript.tex:Table 2, Col 3"     # primary display (kept; source of truth for the paper)
    appears_in:                                   # EVERY artifact that displays this number
      - path: manuscript.tex                      #   file a reader sees it in
        locator: "Table 2, Col 3"                 #   where inside that file
        display_precision: 3                      #   decimals SHOWN here (0 = integer)
      - path: Slides/Lecture04_Results.tex
        locator: "frame 'Main result', highlight box"
        display_precision: 2                      #   coarser → this pair compares at 2
    source_file: scripts/R/03_analyze.R           # script that produced the value
    source_line: 147                              # nearest line in the script
    output_file: output/main_model.rds # where the value lives on disk
    output_field: att_overall                      # field within the output (e.g., list element, column)
    tolerance:
      point_estimate: 0.01                         # absolute floor (atol); see typed rule below
      standard_error: 0.05
      rtol: 0.001                                  # optional relative component: pass if
                                                   #   |x - y| <= atol + rtol * |reported|
      units: "log points"                          # units + display rounding make the
      display_rounding: 3                          #   comparison meaningful across scales
      n: exact
    last_verified_on: <ISO-8601>
    last_verified_by: "/audit-reproducibility"
    status: PASS                                   # PASS | FAIL | EXPLAINED | STALE | UNVERIFIED
    notes: |
      Optional notes — e.g., "matches paper to 3 decimals; SE differs in 4th
      decimal due to clustering df adjustment, within tolerance."
      To downgrade a FAIL to EXPLAINED, this field MUST name a concrete
      alternative spec, e.g. "reghdfe vs feols clustering-df adjustment;
      under the reghdfe small-sample correction the published −1.19 matches
      the script."
```

### 横向检查

上面的字段用于**纵向**核验一条断言，即把论文中的数字与产生它的输出对照。但多产物项目中最容易反复出现的一类故障，纵向核验无法发现：分析已经重跑，稿件表格也由新输出重新生成，引用同一个数字的幻灯片、附录或海报却**没有**更新。此时每道纵向检查仍会通过，磁盘上的两个产物却对同一个量给出不同数值，观众看到的恰好是过期产物。

`appears_in` 用来补上这个缺口。它把同一数字的第二、第三次展示明确写成*声明*，不再依赖记忆。对每条断言：

1. **定位每一处已声明的展示。** 打开每个 `appears_in[].path`，在其 `locator` 处读取取值。
2. **按较粗的精度两两比对。** 两处展示分别按两者中**较小**的 `display_precision` 四舍五入，结果相等才算一致。幻灯片显示 `0.34`、论文显示 `0.342`，两者一致；幻灯片显示 `0.29`，两者不一致。以较粗一侧为准，是因为四舍五入差异属于展示选择，数值差异才是缺陷。这条规则直接区分两者，无需逐案争论。
3. **找不到的展示判 FAIL，绝不能跳过。** 如果已声明的 `path` 缺失，或其 `locator` 处没有匹配的取值，该断言就判为 FAIL。定位器悄悄不再匹配，正是过期数字得以隐藏的状态；把它判为「跳过」，等于让检查在最需要报警时保持沉默。

`tolerance:` 块只控制**纵向**比对，包括其中的 `display_rounding`。它描述*被报告数值*自身的精度，`display_precision` 则描述某个产物如何呈现它。同一数字的两处展示不是两次测量，而是两份副本，所以横向比对除第 2 步的舍入外不允许任何容差，也没有任何 `notes` 条目能把横向不一致降级为 EXPLAINED。如果幻灯片展示的确实是*不同*设定，那属于另一条断言，应当有自己的护照条目。

没有 `appears_in` 列表的断言，只按其 `location:` 声明理解。纵向检查照常运行，但审计会报告「横向未检查」，而不是「横向干净」。在此字段出现之前编写的护照仍可照常使用。

### `status` 语义

- **PASS** — 上次审计确认该断言在容差内，且每一处已声明的展示在较粗精度下都一致。
- **FAIL** — 上次审计发现差异超出容差，**且** `notes` 没有记录具体的具名替代；或者两处已声明的展示不一致；或者某个 `appears_in` 条目无法在其文件中定位。除非显式覆盖，否则 `/commit` 会阻止提交受影响文件。
- **EXPLAINED** — 差异超出容差，**但** `notes` 记录了一条可以解释差距的*具体、具名的替代设定*，包括有依据的替代设定，以及论文或代码已更正的情形。该状态会在审计报告中单独列出，并预期写入给审稿人的回复，**不会**阻止提交。硬性底线不变：未匹配的断言，或没有具名替代的备注，仍判 FAIL。`/audit-reproducibility` 绝不会因为备注空白或含糊而降级。
- **STALE** — 底层的 `source_file` 或 `output_file`，**或任一 `appears_in` 路径**，在 `last_verified_on` 之后被修改。重跑 `/audit-reproducibility` 即可刷新。展示发生修改与脚本发生修改一样，都需要重新检查，因为这类编辑会使两个产物失去同步。
- **UNVERIFIED** — 断言已加入稿件，但从未运行 `/audit-reproducibility`。可提交的护照中不应出现这种状态。

### 集成

- **`/audit-reproducibility`** 开始时读取护照，每审计完一条断言就写回。报告失败断言时同时给出 `id` 与 `location`，作者可以立即在稿件中找到它们。
- **`/commit`**（步骤 0c）在以下情形读取护照：diff 触及一份在 `quality_reports/passports/` 中有护照的稿件（`.tex`/`.qmd`），触及护照列出的任一 `source_file`，或触及某条断言声明为展示的任一文件，包括它的 `location:` 或某个 `appears_in` 的 `path:`。带有 `status: FAIL` 或 `STALE` 的关键断言属于**必须先修**：`/commit` 会中止，点名该断言，并指向 `/audit-reproducibility` 或过期的脚本。**EXPLAINED 的断言不会中止**，因为作者已经记录了有依据的具名替代。没有护照时，这项检查静默跳过。
- **`.codebuddy/hooks/claim-reconcile.py`**（PostToolUse）同时监视两条链路并给出提示。写入被跟踪的 `source_file` / `output_file` 时，它会指出哪些断言的数字可能已经变化；写入某个在 `appears_in` 中声明的文件时，它会指出哪些断言的*其他*展示**没有**被编辑、现在可能已经不一致。只声明了一处展示的断言不存在需要核对的其他展示，因此不会触发后一种提示。钩子按路径统计声明，从不读取取值。它只标记两个产物可能失去同步的时点，纵向和横向比对都由 `/audit-reproducibility` 执行。
- **`/review-paper`** 本身不读取护照。除非设置 `--no-cross-artifact`，否则它会对稿件及其输出自动调用 `/audit-reproducibility`：默认模式下作为第 6b 步，把复现性 FAIL 等致命发现并入审读报告顶部的 "Cross-Artifact Findings" 章节；`--peer` 模式下作为阶段 0 的起飞前检查，此时 FAIL 会成为编辑可以援引的证据。存在护照时，审计以护照模式运行，因此逐条断言的 PASS / FAIL / EXPLAINED / STALE / UNVERIFIED 状态保存在它重写的护照中，而不是审读报告中。编辑或审稿人若想了解数字在成稿时是否经过独立核验，以及哪些有争议的数字已有书面理由，应到护照中查看。

### 灵感来源

这个模式借自 [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) 的 "Material Passport" 概念，即一个贯穿其流水线的 YAML 状态文件。他们的模式规模更大，包含 13 份契约，贯穿约 6 个代理；我们则刻意只处理数值断言溯源。需要更广溯源追踪的使用者可以扩展这个模式，也可以直接采用 ARS 的设计。

### 反模式

- **不要在 `/audit-reproducibility` 运行时自动填充护照，却不向用户展示推断出的映射。** 源行推断只是尽力而为，必须由作者确认。
- **不要在未运行实际数值审计的情况下把 UNVERIFIED 断言提升为 PASS。** 护照记录的是已核验状态，绕过核验会使它失去用途。
- **不要靠手工修改看似错误的展示来消除横向不一致。** 两处展示不一致并不能说明*哪一个*正确。应当根据断言指向的输出重新推导两者，再重新检查。直接把论文的值填入幻灯片，虽然能让检查通过，却仍无法排除论文才是过期一方的可能。
- **不要用护照替代 `/verify-claims`。** 护照处理带代码溯源的数值断言，`/verify-claims` 处理带文献溯源的引文与命名实体断言。两者都要运行。

## 自动记忆是一项未记录的上下文输入

WorkBuddy 的**原生自动记忆**默认开启，并保存在本机 `~/.workbuddy/projects/<project>/memory/`。它会影响会话，而任何复现你工作的人都可能看不见这种影响。几周前记录的一条偏好或一次更正，就是复现者没有也看不到的上下文。

这不是正确性缺陷，而是**可审计性**缺陷。解决办法是披露，不是禁用：

- 对于会产生**被报告数字**的会话，在分析日志中注明自动记忆处于开启状态，一行即可。
- 如果某次运行必须能*仅凭仓库*精确重建，例如最终的复现包构建或提交前的数字冻结，就在分析日志中明确记录「自动记忆开启」，让复现者知道这次运行受到未记录上下文的影响。本平台没有 `CLAUDE_CODE_DISABLE_AUTO_MEMORY` 这个开关，它是上游 Claude Code 的环境变量。
- 任何真正属于项目而非本机的内容，都应通过 [`/promote-memory`](../skills/promote-memory/SKILL.md) 提升进已提交的 `MEMORY.md`，因为复现者实际能读到的是后者。

这项原则与固定提交和 lockfile 的原则相同：**如果它影响结果，就必须让核查结果的人看见。**
