---
name: diagnose
description: 用一套有纪律的"复现 → 最小化 → 提出假设 → 插桩 → 修复"循环，为一个失败或错误的实证结果定位根因，而不是乱猜乱戳。用户说 "why is my regression wrong"、"this number changed"、"my script errors out"、"the result won't reproduce"、"debug this"、"this estimate looks wrong"、"it worked yesterday" 时使用。为研究代码（R/Stata/Python）调校：类型强制转换、NA/合并膨胀、因子水平、聚类/标准误选择、加权、共线性/收敛、种子、包版本漂移。用 `--no-fix` 只定位根因，不改动共享或承重的文件。
argument-hint: "[file, script, or short description of the symptom] [--no-fix]"
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "Agent", "Task"]

---

# /diagnose —— 为一个错误或失败的结果定位根因

找出一次分析**为什么**报错、返回了错误的数字、或对不上账——用结构化的调试循环，而不是散弹式改动。改编自 [mattpocock/skills](https://github.com/mattpocock/skills) 中的 `diagnose` 模式，为实证研究代码重塑形态：这里的 bug 通常是一个*悄无声息*的错误数字，而不是崩溃。

纪律：**在能复现之前绝不改动，在能解释之前绝不修复。** 一个让症状消失、却叫不出根因的猜测式修复，正是错误数字被*洗白*进已发表表格的途径。

## 使用时机

- 一次回归 / 估计返回了你无法解释的数值，或在什么都不该变的时候变了。
- 某个脚本报错，而堆栈跟踪并未指向真正的原因。
- 某个结果"复现不出来"——重跑、换机器、或升级包之后数字不同。
- 某条复现性论断未能通过 `/audit-reproducibility`，而你需要定位究竟是*哪一步*漂移了。

**diagnose 是症状驱动、单目标的：一个错误数字 / 一次失败的运行。** 若任务不同，改用同类技能：

- [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) —— 核验稿件中*全部*数值论断是否与当前代码一致（论断驱动、整篇论文）。若你手上有*一条* FAIL 的论断、想定位是哪个流水线步骤产出的，`/audit-reproducibility` 会*交接给* `/diagnose`；若你想把每个表里的数字重新核一遍，从那里开始。
- [`/review-r`](../review-r/SKILL.md) —— **没有具体症状**时的代码质量审查。
- [`/capture-environment`](../capture-environment/SKILL.md) —— 当怀疑对象是版本/种子漂移时，给环境拍快照。

## 阶段

### Phase 0 —— 钉住症状（期望 vs. 实际）

在碰任何东西之前，先把 bug 陈述为一个可证伪的差距：

- **期望**：你相信正确的那个值/行为，以及*为什么*（上一次运行、论文某张表、一次手算、一个理论符号）。
- **实际**：现在观察到的值/错误，逐字照抄（完整信息，不要转述）。
- **容差**：区分"相同"与"不同"的阈值，取决于*期望*的来源——同机上一次运行 → 机器精度 + 显示舍入；已发表的表格 → 舍入 + 小幅余量（约 1e-3）；手算 → 约 0.01；理论预测 → 一个经济显著性带宽，而不是某个小数位。不要去追 1e-12 的浮点噪声；也不要把 5% 的差距挥手抹掉。（见 [`replication-protocol.md`](../../rules/replication-protocol.md)。）

若期望/实际说不清，这个任务是*理解*，不是诊断——先停下并澄清。

### Phase 1 —— 确定性地复现（拿到一个可靠的红灯）

一个不能按需复现的 bug 无法被修复，只能被藏起来。

1. 固定每一处非确定性来源：设种子、钉住工作目录、记录 `sessionInfo()` / `pip freeze` / Stata `version`（借力 [`/capture-environment`](../capture-environment/SKILL.md)）。
2. 重跑能暴露该 bug 的最小单元，确认它**每一次**都失败。间歇性失败本身就是一个假设（未初始化的 RNG、依赖顺序的合并、并行代码中的竞态）——记下它，并带进 Phase 3。

### Phase 2 —— 最小化为 MWE

一直缩，缩到 bug 暴露在明处：

- **数据**：裁到仍能复现的最小行/列（常常是一组、一个时期、几行）。
- **代码**：把流水线剥到从输入到错误输出的最短路径；凡症状离了它仍存在的，全部注释掉。
- 每一次*保留*了 bug 的删除都是信息；每一次*杀死*了 bug 的删除是更强的信号——记录是哪一种。

即使修复后来很琐碎，MWE 也是交付物：它才是让根因无可争辩的东西。

### Phase 3 —— 提出假设（先枚举，再排序）

在测试任何一条之前，先把候选原因列出来——一份写下来的清单胜过乱戳，因为它能防止你死盯第一个念头。对研究代码，把常见的嫌疑犯走一遍（下面这些都能**不带任何错误信息**地跑干净——它们是悄无声息的错误数字 bug）：

- **类型与强制转换** —— 数值被当成字符/因子读进来；整数溢出；日期解析错误；`TRUE/FALSE` ↔ `1/0`。
- **缺失值** —— `NA` 被悄悄丢弃，`na.rm` 把均值翻转，列表删除在流水线中途改变了样本。
- **连接与形状** —— 多对多合并把行数撑大；键重复；本假设平衡的面板其实不平衡。
- **设定** —— 聚类层级错、固定效应被吸收两次、滞后/领先错一位。
- **坏控制变量与对撞变量** —— 一个控制变量是处理后变量、是因果路径上的中介、或处理的后代（加进去会*引入*偏误，且看不见）。征兆：某个系数在控制变量进入时朝"反方向"动，或缩得不合情理。
- **数值稳定性与收敛** —— 优化器没收敛（看收敛码，不只看估计值）、Hessian 奇异/接近奇异、共线性（VIF 高、某列被丢弃）、容差设得太松、权重或系数极小/极大时下溢/上溢。
- **加权与聚合** —— 权重被悄悄丢弃/截断、权重被错误地重新归一、频率权重与概率权重与分析权重混淆、权重被施加在变换*之后*而非*之前*。
- **样本** —— 某个筛选在变换之前跑还是之后跑；离群值规则前后不一致。
- **环境** —— 包/Stata 版本升级改变了某个默认值；种子变了；locale/编码。

对一个真正含混的 bug，把前列的竞争假设扇出给并行的 `Agent` 子代理（一条假设一个，各在独立上下文中），每个都被要求*在 MWE 上设法证实自己那条原因*并回报——这是"一次性问三位同事"的循环优先版本（见 [`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)）。

### Phase 3b —— 归并假设（以免把一个猜测洗白）

每条假设（无论是手工测的，还是由扇出的 `Task` 测的）都返回 `{hypothesis, evidence for, evidence against, confidence, one-line conclusion}`。然后：

- **有一个明确的赢家**（高置信度、其余被证伪）→ 进入 Phase 4 去确认机制。
- **近乎平局**（前两名相差约 20 个百分点以内）→ *不要*挑一个；进入 Phase 4 的插桩来区分它们。
- **没有一条超过约 50%** → 报告含混并询问用户；不要拿一次抛硬币的结果去改代码。

### Phase 4 —— 插桩与定位（二分，别瞪着看）

低成本地测试排好序的假设：

- **二分流水线** —— 检查数据流中点处的中间值；bug 在该点的上游或下游。如此重复。二分查找用 `log2(n)` 步找到肇事行，而不是 `n` 步。
- **二分历史** —— 若"昨天还好好的"，就与最后一个好提交/输出相比，钉出引入它的那次改动。（`git bisect` 在这里没问题——它从不丢弃任何工作；破坏性的 git 命令由 `git-guardrails.py` 拦截，这一条不在其中。）
- **用诊断原语插桩**，而不是靠猜——在每个阶段检查：`str()` / `summary()` 看类型与 NA 模式；每次变换*前后*的行列计数；`table(factor)` 抓被悄悄丢掉的水平；`cor()` / VIF 抓意外共线性；权重诊断 `range(w)`、`sum(w)`、`table(is.na(w))`；以及回归的收敛标志。**那个计数意外下降、因子水平消失、相关系数跳变或权重变稀疏的阶段，就是肇事阶段。**

Phase 4 结束时，用一句话写出根因，点明确切的行/步骤与机制。

### Phase 5 —— 修复并验证（然后防回归）

**置信度门禁（反洗白规则）：** 除非根因已被叫出名字**且**其机制已明说，否则不要施加修复。若 Phase 3b 留下了平局，就按 `--no-fix` 行事：报告候选并询问。在一个未经证实的假设上改动研究代码，正是本技能要防的那种洗白。

除非设了 `--no-fix`：

1. 在根因处施加**最小**修复——而不是一个掩盖它的下游补丁（宁可修那个坏掉的合并，也不要在事后过滤它的重复行）。
2. 重跑 MWE → 确认在 Phase 0 容差内 `actual == expected`。
3. 重跑**完整的**单元以及任何依赖步骤 → 确认修复没有挪动别的数字。若该结果要喂给某条稿件论断，重新核它（交叉核对 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 中的 passport）。
4. 记下一条**预防**措施——那本该更早抓住它的断言/检查。每类 bug 一条具体防线：

   | bug 类别 | 单行防线 |
   |---|---|
   | 类型与强制转换 | 读取之后 `stopifnot(is.numeric(x))` |
   | 缺失值 | 显式 `na.rm = FALSE`；`stopifnot(sum(is.na(x)) == 0)` |
   | 连接与形状 | 合并前记录 `nrow`；1:1 连接用 `stopifnot(nrow(out) == nrow(left))` |
   | 加权 | `stopifnot(abs(sum(w) - 1) < 1e-8)` 或 `!anyNA(w)` |
   | 收敛 | 在使用估计值之前，断言优化器/模型的收敛标志为 OK |
   | 样本 | 一次显式 `filter()` 并写明理由，而不是在管道中途丢行 |
   | 环境 | 在 `renv.lock` 中钉住版本；每个脚本顶部 `set.seed()` |

   提出这条防线；不要悄悄装上一整套测试。

用 `--no-fix` 时，在根因被叫出之后就停下，把它作为报告交给用户自行修复。

## 完整示例

一个需求预测模型的留出 `MAE` 在一次数据刷新后从 `0.043` 跳到 `0.071`；设定里什么都没变。

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

# Phase 5 — minimal fix at the root (dedup the key), NOT a downstream row filter:
feats <- feats[!duplicated(feats$id), ]
# re-run: MAE back to 0.043 within tolerance; full pipeline re-checked, no other number moved.

# Prevention (Joins & shape guard):
stopifnot(nrow(merge(panel, feats, by = "id")) == nrow(panel))
```

## 输出 / 报告格式

把一份简短诊断写到 `quality_reports/diagnoses/YYYY-MM-DD_<slug>.md`（先建目录：`mkdir -p quality_reports/diagnoses`）。这些报告可能含**真实数据值与文件路径——它们是项目内部文件，和 session log 一样被 gitignore**。内容包含：

- **症状：** 期望 vs. 实际（+ 容差）。
- **MWE：** 能复现它的最小输入/代码。
- **根因：** 确切的行/步骤与机制。
- **修复：** 实际施加的 diff（或，在 `--no-fix` 下，建议的改动）。
- **验证：** MWE + 全量重跑的复核结果。
- **预防：** 那本该抓住它的防线。

外加一段聊天摘要，以那一句根因为开头。

## 跨语言说明

常见嫌疑犯的模型用 R 举例，但 bug 的*类别*与语言无关；诊断惯用法则因语言而异：

- **R** —— `anyNA()` / `table(is.na(x))`；因子会悄悄丢掉未使用的水平；`set.seed()`；`sessionInfo()`。
- **Stata** —— `tab v, missing` 与显式的 `.`/`.a–.z` 扩展缺失值；`set seed`；`version`；权重用 `[fw=]` 还是 `[pw=]` 还是 `[aw=]` 是高频的无声 bug。
- **Python** —— `df.isnull().sum()`；`numpy.nan` ≠ `None`；pandas 与 numpy 的 NaN 处理不同；`np.random.seed()` / 传入 `random_state`；`pip freeze`。

（其他领域的分叉者：五个结构性类别——类型、缺失值、连接、样本、环境——与学科无关；上面那些计量经济学的嫌疑犯是已做出来的实例。）

## 退出行为

| 结果 | 动作 |
|---|---|
| 根因已**叫出名字**（高置信度）、修复已施加、已复验 | 报告根因 + diff + 预防措施 |
| `--no-fix` | 停在已叫出名字的根因；写报告，对源码**不**做任何改动 |
| **Phase 0 受阻**（说不出期望/实际） | 停下，索取期望值——诊断需要一个靶子 |
| **Phase 1 受阻**（无法复现 / 非确定性） | 把非确定性*本身*作为结论报告（它就是这个 bug 类别）+ 如何让分析确定化；不要盲改 |
| Phase 3b **平局 / <50%** | 报告竞争假设并询问用户；不施加任何修复 |

## 参数

| 参数 | 作用 |
|---|---|
| `--no-fix` | 仅诊断：一路跑到叫出根因（Phase 0–4）并写报告，但对源码**不做**任何改动。适用于你想自己施加修复，或该文件是共享/承重的、自动改动并不合适时。 |

## Step 0 —— 动手之前先陈述契约

在提出或写下**任何**修复之前，用 3–5 条要点陈述，并**停下来等确认**：

1. 该函数或流水线的**文档化契约**是什么。
2. 报告者声称坏掉的是什么。
3. 所报场景是否**在契约之内**——一个违反契约的调用方，不是被调用方的 bug。
4. **正确行为**应当是什么。
5. 什么证据能定案。

这花三十秒，却能防住代价最高的一类白做：对一个被误解的契约做了自信的修复。在一个有记录的案例里，同一个语义要点不得不被纠正**两次**，修复范围才划对，因为代理对契约断言了一个立场，而不是复述它并提问。

> **严重度跟随契约。** 一个落在文档化契约之外的场景，至多是文档或校验问题，绝不是高严重度的正确性 bug。因为它*看起来*不对就把它抬高，正是一次修复最终改变了用户所依赖行为的方式。

## 把审计环节与修复环节分开

有记录的会话中，最强的结果都始于**调查**，而不是修复请求。比较乱的那些，则把审计与编辑混在了一起。

**审计环节——只读。** 产出一张发现表：`severity | file:line | claim | 我实际跑过的证据 | 建议修复`。凡未经执行验证的，标为 **UNVERIFIED**。什么都不改。

**修复环节——只对获批的行。** 由用户挑选哪些发现要修。这才使"拒绝一条发现"变得廉价，而拒绝发现正是范围得以受控的方式。

`--no-fix` 只跑审计环节。

## 交叉引用

- [`.codebuddy/skills/review-r/SKILL.md`](../review-r/SKILL.md) —— 没有具体症状时的代码质量审查（diagnose 是症状驱动的）。
- [`.codebuddy/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) —— 核验全部数值论断与代码是否一致；diagnose 定位的是*单条*失败的论断（也是 FAIL 之后自然的交接对象）。
- [`.codebuddy/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) —— 当怀疑对象是版本/种子漂移时，给环境拍快照。
- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 定义"同一个数字"的容差契约，以及"若不一致"时向本技能的交接。
- [`.codebuddy/rules/orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) —— Phase 3 中用于竞争假设测试的扇出原语。

## 本技能不做的事

- **审查没有症状的代码** —— 那是 [`/review-r`](../review-r/SKILL.md)。diagnose 需要一个期望对实际的差距去追。
- **重新审计论文中的每一条论断** —— 那是 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md)。diagnose 深挖一个 bug。
- **搭建测试套件** —— 它只提出那一条本该抓住*这个* bug 的防线；常备的测试基础设施是另一件开发工作。
- **提交修复** —— 建分支 / 提交是 [`/commit`](../commit/SKILL.md) 的职责。
