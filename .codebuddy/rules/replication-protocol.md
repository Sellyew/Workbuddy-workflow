---
paths:
  - "scripts/**/*.R"
  - "Figures/**/*.R"
---

# 复现优先协议

**核心原则：** 在扩展之前，先把原始结果一分不差地复现出来。

---

## 阶段 1：清点与基线

在写任何 R 代码之前：

- [ ] 读论文的复现 README
- [ ] 清点复现包：语言、数据文件、脚本、输出
- [ ] 记录论文里的黄金标准数字：

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
- [ ] 一开始逐行翻译——复现期间不要「改进」
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

验证朝两个方向跑。**纵向**上，每条断言都对照产生它的输出，按下面的容差检查。**横向**上，每条断言都对照所有展示同一个数字的*其他*产物——见[横向检查](#横向检查)。一个数值可以过掉每一道纵向检查，却仍是幻灯片上一个月前的旧值。

### 容差阈值

| 类型 | 容差 | 理由 |
|------|-----------|-----------|
| 整数（N、计数） | 完全一致 | 没有任何理由出现差异 |
| 点估计 | < 0.01 | 论文展示时的四舍五入 |
| 标准误 | < 0.05 | Bootstrap/聚类带来的波动 |
| P 值 | 显著性水平一致 | 精确 p 值可能略有差异 |
| 百分比 | < 0.1pp | 展示时的四舍五入 |

### 若出现不匹配

**不要进入扩展阶段。** 隔离出是哪一步引入了差异，检查常见成因（样本量、标准误计算、默认选项、变量定义），并且即使查不清也要把这次排查记录下来。要定位*哪一步*发生了漂移，交给 [`/diagnose`](../skills/diagnose/SKILL.md)（复现 → 最小化 → 二分流水线）——它是单条断言层面的根因工具，对应 `/audit-reproducibility` 的整篇论文检查。

**出现不匹配并不预设代码就是对的。** 磁盘上的输出是*挑战方*，不是外部裁判——一次重构可能弄坏了原本正确的表格，所以可能*稿件*里的数字才对，代码才是过期/有 bug 的那一侧。把它表述成「{论文, 代码} 中必有一个要改——隔离出是哪一个」，绝不要表述成「把代码改回去以对齐论文」。

**一个有依据的替代解释不等于失败。** 如果差距可以由*具体、具名的替代设定*解释（例如 `reghdfe` 与 `feols` 的聚类自由度、不同的带宽选择规则、蒙特卡洛种子/次数、展示时的四舍五入），就记下那个具名替代，并把该断言标为 **EXPLAINED** 而不是 FAIL——见下面的 `status` 语义。空白或含糊的备注（「不清楚」）永远不能把 FAIL 降级。

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

在复现通过验证之后（所有目标 PASS）：

- [ ] 提交复现脚本："Replicate [Paper] Table X -- all targets match"
- [ ] 现在再做课程相关的改动扩展（不同估计量、新图等）
- [ ] 每个扩展都建立在已核验的基线上

---

## 执行

本规则由 [`/audit-reproducibility`](../skills/audit-reproducibility/SKILL.md) 技能执行。它从稿件中解析数值断言，在 `output/`（或用户指定的输出目录）中定位对应取值，并按上面的容差阈值比对。这样运行：

- **提交之前** — `/audit-reproducibility path/to/manuscript.tex`
- **发布复现包之前** — 同样的调用；目标是零 FAIL。
- **作为 pre-commit 门禁** — 当 diff 同时触及稿件与分析文件时，接入 `/commit`。

该技能在任一容差被突破时以 1 退出，因此能干净地接入质量门禁。

---

## 断言溯源：`passport.yaml`

护照是每篇论文、每个分支各一份的 YAML 文件，位于 `quality_reports/passports/<paper-slug>.yaml`，为稿件中每条已核验的数值断言记录产生它的脚本调用与输出文件。这份约定刻意收窄：只管数值断言（点估计、标准误、p 值、样本量、表格/图中的百分比），不管散文断言（那由 `/verify-claims` 单独处理）。

`templates/passport-template.yaml` 是起始文件。复刻本仓库的人应当每篇论文复制一次。

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

上面的字段是**纵向**核验一条断言——论文里的数字对照产生它的输出。这没有触及多产物项目最稳定复现的那类故障：分析重跑了一遍，稿件表格由新输出重新生成，而引用同一个数字的幻灯片、附录或海报**没有**。每一道纵向检查照样通过。磁盘上两个产物如今对同一个量各说各话，而观众看到的是过期的那一个。

`appears_in` 补上了这个缺口：它让一个数字的第二、第三次展示成为*声明*，而不是记忆。对每条断言：

1. **定位每一处已声明的展示。** 打开每个 `appears_in[].path`，在其 `locator` 处读取取值。
2. **按较粗的精度两两比对。** 两个展示各自按两者中**较小**的 `display_precision` 四舍五入后相等，才算一致。幻灯片显示 `0.34`、论文显示 `0.342`，一致；幻灯片显示 `0.29`，不一致。以较粗的一侧为准，因为四舍五入差异是展示选择、数值差异是缺陷——这条规则把两者分开，无需任何人去争辩这一回。
3. **找不到的展示判 FAIL，绝不是跳过。** 若某个已声明的 `path` 缺失，或在其 `locator` 处没有任何取值匹配，该断言即判为 FAIL。一个悄悄不再匹配的定位器，正是过期数字藏身的状态；把它判为「跳过」，等于在检查最该响的时候让它闭嘴。

`tolerance:` 块只管**纵向**比对——包括它的 `display_rounding`，那描述的是*被报告数值*自身的精度，而 `display_precision` 描述的是某个产物对它的呈现。同一个数字的两处展示不是两次测量，而是两份副本，所以横向比对除第 2 步的舍入之外不容任何容差，也没有任何 `notes` 条目能把横向不一致降级为 EXPLAINED。如果幻灯片确实展示的是*不同*的设定，那就是另一条断言，应当有自己的护照条目。

没有 `appears_in` 列表的断言，只按它自己的 `location:` 声明来理解：纵向检查照旧运行，审计会把它报告为「横向未检查」，而不是「横向干净」。在此字段出现之前写的护照继续照常可用。

### `status` 语义

- **PASS** — 上次审计在容差内确认了该断言，且每一处已声明的展示在较粗精度下都一致。
- **FAIL** — 上次审计检测到超出容差的差异，**且** `notes` 中没有记录具体的具名替代；或两处已声明展示不一致；或某个 `appears_in` 条目在其文件中定位不到。除非显式覆盖，否则对受影响文件阻塞 `/commit`。
- **EXPLAINED** — 超出容差，**但** `notes` 记录了一条*具体、具名的替代设定*可以解释该差距（有依据的替代、论文已更正、或代码已更正）。在审计报告中浮出，并预期流入给审稿人的回复；**不**阻塞。硬性底线仍然成立：未匹配的断言，或没有具名替代的备注，仍判 FAIL——`/audit-reproducibility` 绝不会因为备注空白或含糊而降级。
- **STALE** — 底层的 `source_file` 或 `output_file`，**或任一 `appears_in` 路径**，在 `last_verified_on` 之后被修改过。重跑 `/audit-reproducibility` 刷新。展示被改动和脚本被改动一样，都是重新检查的理由：正是那次编辑让两个产物脱了拍。
- **UNVERIFIED** — 该断言被加入稿件，但从未跑过 `/audit-reproducibility`。不应出现在可提交的护照里。

### 集成

- **`/audit-reproducibility`** 在开始时读护照，在每条断言审计后写回。失败的断言连同其 `id` 与 `location` 一起报告，作者可以立刻在稿件里找到它们。
- **`/commit`**（步骤 0c）在以下情形读护照：diff 触及一份在 `quality_reports/passports/` 里有护照的稿件（`.tex`/`.qmd`）、触及护照列出的任一 `source_file`、或触及某条断言声明为展示的任一文件（它的 `location:` 或某个 `appears_in` 的 `path:`）。带有 `status: FAIL` 或 `STALE` 的承重断言属于**必须先修**：`/commit` 中止，点名该断言，并指向 `/audit-reproducibility`（或过期的脚本）。**EXPLAINED 的断言不会中止**——作者已经记录了有依据的具名替代。没有护照时，这项检查静默跳过。
- **`.codebuddy/hooks/claim-reconcile.py`**（PostToolUse）同时盯着两条链路并给出提示。写入被跟踪的 `source_file` / `output_file` 时，会点名那些数字可能已经移动的断言；写入某个在 `appears_in` 中声明的文件时，会点名那些*其他*展示**未被**编辑、现在可能已经不一致的断言（只声明了一处展示的断言没有兄弟展示，因此保持安静）。钩子按路径统计声明，从不读取取值。它标记的是两个产物可能脱拍的时点；比对本身——纵向与横向——在 `/audit-reproducibility` 中运行。
- **`/review-paper`** 本身不读护照。除非设置了 `--no-cross-artifact`，它会在稿件及其输出上自动调用 `/audit-reproducibility`：默认模式下作为第 6b 步，把诸如复现性 FAIL 这类致命发现并入审读报告顶部的 "Cross-Artifact Findings" 章节；在 `--peer` 模式下作为阶段 0 的起飞前检查，此时一个 FAIL 会成为编辑可以援引的证据。存在护照时，那次审计以护照模式运行，所以逐条断言的 PASS / FAIL / EXPLAINED / STALE / UNVERIFIED 状态活在它重写的护照里，而不在审读报告中。想了解数字在成稿时是否经过独立核验、哪些有争议的数字已带有书面理由的编辑或审稿人，在那里读。

### 灵感来源

这个模式借自 [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) 的 "Material Passport" 概念（一个贯穿其流水线的 YAML 状态文件）。他们的模式更重（13 份契约，贯穿约 6 个代理）；我们的刻意只限定在数值断言溯源。需要更广溯源追踪的复刻者可以扩展该模式，或直接搬用 ARS 的设计。

### 反模式

- **不要在 `/audit-reproducibility` 运行时自动填充**护照而不给用户看推断出的映射。源行推断是尽力而为；由作者确认。
- **不要在未跑实际数值审计的情况下把 UNVERIFIED 断言提升为 PASS。** 护照是「已核验状态」的产物；绕过核验就毁了它的用途。
- **不要靠手工编辑那个看起来不对的展示来消解横向不一致。** 两处不一致的展示不会告诉你*哪一个*是对的。从断言指向的输出重新推导两者，再重新检查。把论文的值敲进幻灯片，会让检查变绿，同时留下「论文才是过期一方」的可能。
- **不要把护照当作 `/verify-claims` 的替代品。** 护照处理带代码溯源的数值断言；`/verify-claims` 处理带文献溯源的引文与命名实体断言。两者都要跑。

## 自动记忆是一项未记录的上下文输入

WorkBuddy 的**原生自动记忆**默认开启，且是机器本地的（`~/.workbuddy/projects/<project>/memory/`）。它可以在任何复现你工作的人看不见的情况下塑造一次会话：几周前记录的一条偏好或一次更正，是复现者没有、也看不到的上下文。

这不是正确性缺陷——它是**可审计性**缺陷，解法是披露，不是禁欲：

- 对于会产生**被报告数字**的会话，在分析日志里注明自动记忆处于开启状态。一行就够。
- 如果某次运行必须能*仅凭仓库*精确重建——最终的复现包构建、提交前的数字冻结——就为那次运行关掉它：`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`。
- 任何真正属于项目、而非属于你这台机器的东西，都应当通过 [`/promote-memory`](../skills/promote-memory/SKILL.md) 提升进已提交的 `MEMORY.md`——那才是复现者真正读得到的地方。

原则与固定提交和 lockfile 背后是同一条：**如果它影响了结果，它就该对任何核查结果的人可见。**
