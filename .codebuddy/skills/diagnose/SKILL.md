---
name: diagnose
description: 用有纪律的「复现 → 最小化 → 提出假设 → 插桩 → 修复」循环，找出实证结果失败或出错的根因，避免盲目猜测和改动。用户说 "why is my regression wrong"、"this number changed"、"my script errors out"、"the result won't reproduce"、"debug this"、"this estimate looks wrong"、"it worked yesterday"、"回归结果为什么不对"、"这个数字变了"、"脚本报错了" 或 "结果复现不了" 时使用。面向研究代码（R/Stata/Python），覆盖类型强制转换、NA/合并膨胀、因子水平、聚类/标准误选择、加权、共线性/收敛、种子和包版本漂移。用 `--no-fix` 只定位根因，不改动共享或关键文件。
argument-hint: "[file, script, or short description of the symptom] [--no-fix]"
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "Agent", "Task"]

---

# /diagnose —— 为一个错误或失败的结果定位根因

用结构化调试流程解释分析为什么报错、返回错误数字或无法对账，不要靠零散改动碰运气。本技能改编自 [mattpocock/skills](https://github.com/mattpocock/skills) 的 `diagnose` 模式，并针对实证研究代码作了调整：这里的 bug 往往不会导致崩溃，而会悄悄产生错误数字。

必须遵守：**能复现之前不要改动，能解释之前不要修复。** 如果只靠猜测让症状消失，却说不出根因，错误数字就可能借此进入已发表的表格。

## 使用时机

- 回归或估计返回无法解释的数值，或在本不该变化时发生变化。
- 脚本报错，但堆栈跟踪没有指向真正原因。
- 重跑、换机器或升级包后，结果无法复现或数字不同。
- 某项复现性论断未通过 `/audit-reproducibility`，需要确定具体是哪一步发生了漂移。

**diagnose 由症状驱动，一次只处理一个目标：一个错误数字或一次失败的运行。** 其他任务请使用相应技能：

- [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 核验稿件中全部数值论断是否与当前代码一致，按论断检查整篇论文。如果你只有一条 FAIL 论断，想定位产生它的流水线步骤，`/audit-reproducibility` 会交接给 `/diagnose`；如果要重新核验每张表的数字，请从它开始。
- [`/review-r`](../review-r/SKILL.md) 用于没有具体症状时的代码质量审查。
- [`/capture-environment`](../capture-environment/SKILL.md) 用于怀疑版本或种子漂移时记录环境快照。

## 阶段

### Step 0 —— 动手之前先陈述契约

开始诊断前，先用 3–5 条要点说明以下事项，并停下来等待确认：

1. 该函数或流水线的文档化契约是什么。
2. 报告者声称哪里出了问题。
3. 所报场景是否在契约之内。违反契约的调用方问题，不等于被调用方有 bug。
4. 正确行为应该是什么。
5. 什么证据可以定案。

这一步只需三十秒，却能避免代价最高的无效工作：因误解契约而自信地实施错误修复。一个有记录的案例中，同一语义要点不得不纠正两次，修复范围才最终划对，因为代理没有复述契约并提问，而是直接断言了自己的理解。

> **严重度跟随契约。** 落在文档化契约之外的场景，至多是文档或校验问题，绝不是高严重度的正确性 bug。仅因它看起来不对就提高严重度，可能导致修复改变用户依赖的行为。

### Phase 0 —— 钉住症状（期望 vs. 实际）

改动任何内容前，先把 bug 写成一个可证伪的差距：

- **期望**：你认为正确的值或行为是什么，依据是什么，例如上一次运行、论文中的表、手算结果或理论符号。
- **实际**：目前观察到的值或错误，完整逐字记录，不要转述。
- **容差**：根据期望来源设定区分「相同」和「不同」的阈值。同机上一次运行，考虑机器精度和显示舍入；已发表表格，考虑舍入和约 1e-3 的小幅余量；手算结果，约 0.01；理论预测，采用经济显著性带宽，而不是某个小数位。不要追查 1e-12 的浮点噪声，也不要忽略 5% 的差距。见 [`replication-protocol.md`](../../rules/replication-protocol.md)。

如果无法说清期望和实际，当前任务是理解问题，不是诊断。先停下来澄清。

### Phase 1 —— 确定性地复现（拿到一个可靠的红灯）

无法按需复现的 bug 无法可靠修复，只能暂时掩盖。

1. 固定所有非确定性来源：设置种子、固定工作目录、记录 `sessionInfo()` / `pip freeze` / Stata `version`，可借助 [`/capture-environment`](../capture-environment/SKILL.md)。
2. 重跑能暴露 bug 的最小单元，确认它每次都失败。间歇性失败本身也是一个假设，可能来自未初始化的 RNG、依赖顺序的合并或并行代码竞态。记录下来，并带入 Phase 3。

### Phase 2 —— 最小化为 MWE

持续缩减，直到 bug 清楚暴露：

- **数据**：裁到仍能复现问题的最小行列集合，通常只需一组、一个时期或几行。
- **代码**：把流水线缩减为从输入到错误输出的最短路径；凡是删掉后症状仍存在的部分，都可以注释掉。
- 每次删除后 bug 仍然保留，都能提供信息；删除后 bug 消失，则是更强的信号。记录每次结果。

即使最终修复很简单，MWE 仍是交付物，因为它让根因可以得到明确验证。

### Phase 3 —— 提出假设（先枚举，再排序）

测试任何假设前，先列出所有候选原因。把清单写下来可以避免只盯着第一个念头。研究代码中应检查以下常见原因，它们都可能在不报任何错误的情况下产生错误数字：

- **类型与强制转换**：数值被读成字符或因子；整数溢出；日期解析错误；`TRUE/FALSE` ↔ `1/0`。
- **缺失值**：`NA` 被悄悄丢弃，`na.rm` 改变均值，列表删除在流水线中途改变样本。
- **连接与形状**：多对多合并增加行数；键重复；原以为平衡的面板实际不平衡。
- **设定**：聚类层级错误、固定效应被吸收两次、滞后或领先错一位。
- **坏控制变量与对撞变量**：控制变量是处理后变量、因果路径上的中介或处理的后代，加入后会引入偏误，而且不一定有明显提示。征兆包括系数在控制变量加入后朝「反方向」移动，或缩得不合情理。
- **数值稳定性与收敛**：优化器未收敛，要检查收敛码而非只看估计值；Hessian 奇异或接近奇异；共线性，例如 VIF 高或某列被丢弃；容差过松；权重或系数极小、极大时下溢或上溢。
- **加权与聚合**：权重被悄悄丢弃或截断；错误地重新归一；混淆频率权重、概率权重和分析权重；在变换之后而非之前施加权重。
- **样本**：筛选发生在变换之前还是之后；离群值规则前后不一致。
- **环境**：包或 Stata 版本升级改变默认值；种子变化；locale 或编码变化。

对于真正含糊的 bug，可以把前列竞争假设并行交给多个 `Agent` 子代理，每条假设一个代理，各自使用独立上下文。要求每个代理在 MWE 上验证自己负责的原因并回报证据。这相当于优先执行「一次性问三位同事」的循环，见 [`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)。

### Phase 3b —— 归并假设（以免把一个猜测洗白）

每条假设无论由主线程还是并行独立 `Agent` 子代理测试，都返回 `{hypothesis, evidence for, evidence against, confidence, one-line conclusion}`。随后按结果处理：

- **有明确赢家**：根因已明确且有高置信度证据，其余假设已被证伪，进入 Phase 4 确认机制。
- **接近平局或没有假设超过约 50%**：不要任选其一，也不要立即以询问代替测试；进入 Phase 4，优先用安全插桩区分候选假设。
- **安全插桩后仍无法区分**：展示各假设的现有证据与缺口，再询问用户；不靠一次近似随机选择来改代码。

### Phase 4 —— 插桩与定位（二分，别瞪着看）

接近平局或没有假设超过约 50% 时，**先做安全插桩**：优先使用只读检查、打印中间计数和在临时副本上运行，不修改共享数据或源码。只有这些测试仍无法区分候选假设，才报告歧义并询问用户。

用低成本测试检查排好序的假设：

- **二分流水线**：检查数据流中点的中间值，判断 bug 位于上游还是下游，然后重复。二分查找用 `log2(n)` 步定位出错行，而不是 `n` 步。
- **二分历史**：如果「昨天还好好的」，与最后一个正常提交或输出比较，找出引入问题的改动。这里可以使用 `git bisect`，它不会丢弃工作；破坏性 git 命令由 `git-guardrails.py` 拦截，`git bisect` 不在其中。
- **用诊断原语插桩，不要靠猜。** 在每个阶段检查：`str()` / `summary()` 查看类型和 NA 模式；每次变换前后检查行列计数；`table(factor)` 检查是否丢失水平；`cor()` / VIF 检查意外共线性；用 `range(w)`、`sum(w)`、`table(is.na(w))` 检查权重；检查回归收敛标志。计数意外下降、因子水平消失、相关系数跳变或权重变稀疏的阶段，就是问题所在。

Phase 4 结束时，只有**根因已明确且有高置信度证据**，才用一句话说明根因，指出确切行或步骤及其作用机制；否则保留竞争假设并询问用户。

### Phase 5 —— 修复并验证（然后防回归）

**置信度门禁：** 只有**根因已明确且有高置信度证据**并能解释其机制，才能实施修复。如果 Phase 4 的安全插桩后仍是平局或无法区分，就按 `--no-fix` 处理，报告候选假设与证据缺口并询问用户。基于未经证实的假设修改研究代码，正是本技能要避免的做法。

除非设置了 `--no-fix`，否则按以下顺序操作：

1. 在根因处做**最小**修复，不要在下游打补丁掩盖问题。例如应修复错误合并，而不是事后过滤重复行。
2. 重跑 MWE，确认在 Phase 0 的容差内 `actual == expected`。
3. 重跑完整单元及所有依赖步骤，确认修复没有改变其他数字。如果结果用于稿件中的论断，按照 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 的 passport 重新核验。
4. 记录一项预防措施，即本可更早发现问题的断言或检查。每类 bug 对应一条具体防线：

   | bug 类别 | 单行防线 |
   |---|---|
   | 类型与强制转换 | 读取之后 `stopifnot(is.numeric(x))` |
   | 缺失值 | 显式 `na.rm = FALSE`；`stopifnot(sum(is.na(x)) == 0)` |
   | 连接与形状 | 合并前记录 `nrow`；1:1 连接用 `stopifnot(nrow(out) == nrow(left))` |
   | 加权 | `stopifnot(abs(sum(w) - 1) < 1e-8)` 或 `!anyNA(w)` |
   | 收敛 | 在使用估计值之前，断言优化器/模型的收敛标志为 OK |
   | 样本 | 一次显式 `filter()` 并写明理由，而不是在管道中途丢行 |
   | 环境 | 在 `renv.lock` 中钉住版本；每个脚本顶部 `set.seed()` |

   只提出这条防线，不要悄悄安装整套测试。

使用 `--no-fix` 时，根因已明确且有高置信度证据后即停止，把报告交给用户自行修复。

## 完整示例

一个需求预测模型的留出 `MAE` 在数据刷新后从 `0.043` 跳到 `0.071`，设定没有变化。

```r
# Phase 1 — reproduce: set.seed(1); same script, same number every run. Red is stable.

# Phase 2 — MWE: one region, two horizons still shows the jump.
#           Strip to: read panel -> merge features -> lm(). Bug survives the merge step.

# Phase 4 — instrument: row counts before/after each step
nrow(panel)                          # 12,400  (expected)
nrow(merge(panel, feats, by="id"))   # 12,933  <-- inflated! a many-to-many merge

# Root cause: the refresh left duplicate feats rows for a subset of ids; the
# join fans those ids out, 12,400 -> 12,933 (+533 rows), re-weighting the MAE
# toward the duplicated units.

# Phase 5 — assert keys and expose every conflict before resolving it:
stopifnot(!anyDuplicated(panel$id))
conflict_ids <- unique(feats$id[duplicated(feats$id) |
                              duplicated(feats$id, fromLast = TRUE)])
conflicts <- feats[feats$id %in% conflict_ids, ]
print(conflicts)  # inspect source, updated_at and conflicting values

# Documented contract: registry source wins, then latest updated_at.
# If that rule has no unique winner, STOP and ask the user; never keep an
# arbitrary first row via duplicated().
feats <- do.call(rbind, lapply(split(feats, feats$id), function(z) {
  if (nrow(z) == 1L) return(z)
  preferred <- if (any(z$source == "registry")) {
    z[z$source == "registry", , drop = FALSE]
  } else {
    z
  }
  winners <- preferred[preferred$updated_at == max(preferred$updated_at), , drop = FALSE]
  if (nrow(winners) != 1L) stop("Ambiguous merge key; ask user: ", z$id[1])
  winners
}))
stopifnot(!anyDuplicated(feats$id))
# re-run: MAE back to 0.043 within tolerance; full pipeline re-checked, no other number moved.

# Prevention (Joins & shape guard):
stopifnot(nrow(merge(panel, feats, by = "id")) == nrow(panel))
```

## 输出 / 报告格式

把简短诊断写入 `quality_reports/diagnoses/YYYY-MM-DD_<slug>.md`，先创建目录：`mkdir -p quality_reports/diagnoses`。报告可能包含真实数据值和文件路径，因此属于项目内部文件，与 session log 一样被 gitignore。内容包括：

- **症状：** 期望 vs. 实际及容差。
- **MWE：** 能复现问题的最小输入和代码。
- **根因：** 确切行或步骤及其机制。
- **修复：** 实际应用的 diff；使用 `--no-fix` 时写建议改动。
- **验证：** MWE 和全量重跑的复核结果。
- **预防：** 本可发现问题的防线。

只有根因已明确且有高置信度证据时，聊天摘要才以一句话根因开头；未定位、平局或受阻时，以实际状态开头，并如实列出竞争假设、证据缺口或所需输入，不得写成已找到根因。

## 跨语言说明

上面的常见原因用 R 举例，但 bug 类别与语言无关，具体诊断方法则因语言而异：

- **R**：`anyNA()` / `table(is.na(x))`；因子会悄悄丢掉未使用的水平；`set.seed()`；`sessionInfo()`。
- **Stata**：`tab v, missing` 与显式的 `.`/`.a–.z` 扩展缺失值；`set seed`；`version`；`[fw=]`、`[pw=]`、`[aw=]` 的权重选择经常在不报错的情况下出错。
- **Python**：`df.isnull().sum()`；`numpy.nan` ≠ `None`；pandas 与 numpy 的 NaN 处理不同；`np.random.seed()` 或传入 `random_state`；`pip freeze`。

其他领域 fork 本仓库时，可以保留类型、缺失值、连接、样本和环境这五个结构类别；上面列出的计量经济学原因只是已经实现的示例。

## 退出行为

| 结果 | 动作 |
|---|---|
| **根因已明确且有高置信度证据**、修复已施加、已复验 | 报告根因、diff 和预防措施 |
| `--no-fix` | 明确根因后停止；写报告，对源码不做任何改动 |
| **Phase 0 受阻**（说不出期望/实际） | 停止并索取期望值，诊断需要明确目标 |
| **Phase 1 受阻**（无法复现 / 非确定性） | 把非确定性本身作为结论报告，并说明如何让分析确定化；不要盲改 |
| Phase 3b **平局 / <50%** | 先进入 Phase 4 做安全插桩；仍无法区分才报告竞争假设、证据缺口并询问用户，不实施修复 |

## 参数

| 参数 | 作用 |
|---|---|
| `--no-fix` | 只诊断：执行到根因已明确且有高置信度证据（Phase 0–4）并写报告，但不修改源码。适用于希望自行修复，或文件由多人共享、承担关键功能，不适合自动修改的情况。 |

## 把审计环节与修复环节分开

有记录的会话表明，效果最好的工作都从调查开始，而不是直接收到修复请求；混乱的会话则把审计和编辑混在一起。

**审计环节只读。** 产出发现表：`severity | file:line | claim | 我实际跑过的证据 | 建议修复`。未经执行验证的内容标为 **UNVERIFIED**，不修改任何内容。

**修复环节只处理获批行。** 由用户选择要修复的发现。这样用户可以低成本拒绝某条发现，也能控制修改范围。

`--no-fix` 只运行审计环节。

## 交叉引用

- [`.codebuddy/skills/review-r/SKILL.md`](../review-r/SKILL.md)：没有具体症状时审查代码质量；diagnose 则由症状驱动。
- [`.codebuddy/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md)：核验全部数值论断与代码是否一致；diagnose 深入定位单条失败论断，也是 FAIL 后的自然交接对象。
- [`.codebuddy/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md)：怀疑版本或种子漂移时记录环境快照。
- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md)：定义「同一个数字」的容差契约，以及结果不一致时如何交接给本技能。
- [`.codebuddy/rules/orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)：Phase 3 测试竞争假设时使用的并行原语。

## 本技能不做的事

- **审查没有症状的代码**：使用 [`/review-r`](../review-r/SKILL.md)。diagnose 需要明确的期望与实际差距。
- **重新审计论文中的每条论断**：使用 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md)。diagnose 只深入处理一个 bug。
- **搭建测试套件**：它只提出本可发现当前 bug 的一条防线；常备测试基础设施属于另一项开发工作。
- **提交修复**：建分支和提交由 [`/commit`](../commit/SKILL.md) 负责。
