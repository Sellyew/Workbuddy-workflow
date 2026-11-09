---
name: power-analysis
description: 为一个研究设计计算统计功效、所需样本量与最小可检测效应（MDE），然后写出一节可直接进注册库的功效说明。覆盖双臂 RCT（含聚类 / ICC 与不等分配）、多臂校正，以及面向非标准设计（DiD/事件研究、IV、面板）的基于模拟的功效方案。用户说 "power analysis"、"power calculation"、"MDE"、"minimum detectable effect"、"how big a sample do I need"、"is my study powered"、"power for an RCT"，或在 `/preregister` 需要为实验写功效一节时使用。产出功效/MDE 表、功效曲线，以及一段可粘贴进预注册的方法学段落。
description_zh: 为一个研究设计计算统计功效、所需样本量与最小可检测效应（MDE），然后写出一节可直接进注册库的功效说明。覆盖双臂 RCT（含聚类 / ICC 与不等分配）、多臂校正，以及面向非标准设计（DiD/事件研究、IV、面板）的基于模拟的功效方案。用户说 "power analysis"、"power calculation"、"MDE"、"minimum detectable effect"、"how big a sample do I need"、"is my study powered"、"power for an RCT"，或在 `/preregister` 需要为实验写功效一节时使用。产出功效/MDE 表、功效曲线，以及一段可粘贴进预注册的方法学段落。
argument-hint: "[--mode mde|n|power] [--design rct|cluster|multiarm|sim] [--input <spec-or-description>]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Edit", "Bash", "Agent", "Task"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/power-analysis` —— 研究设计的功效 / MDE

在事前设计中计算三个相互关联的量：**功效**、**所需 N** 和**最小可检测效应（MDE）**，并生成可直接粘贴到预注册中的功效说明。标准设计使用解析法，非标准设计使用模拟法，并复用 `/simulation-study` 的脚手架模式。

**核心原则：** 功效计算是*数据产生之前作出的设计承诺*。固定 {效应量, N, 功效} 中任意两个量，求出第三个；不要根据已经得到的估计值反推「功效」。那是没有信息量的事后功效，详见「本技能不做什么」。

## 何时使用

- **启动 RCT / 田野 / 调查实验之前**：选择能在 80–90% 功效下达到目标 MDE 的 N（或簇数）。
- **[`/preregister`](../preregister/SKILL.md) 用于 RCT 时**：AEA RCT Registry 与多数 IRB 都要求论证功效/MDE；`/preregister` 的 `aea-rct` 风格按本技能各阶段填写这一节。本技能只能由用户调用，因此 `/preregister` 会读取并遵循本技能，而不是调用它。
- **R&R 期间**：审稿人问 "was this study adequately powered to detect the effect you claim?" 时。
- **设计蒙特卡洛时**：在交给 `/simulation-study` 前设定 `R` 与样本量。

## 输入

`$ARGUMENTS` 可以包含参数；缺失信息在 Phase 0 中询问补全。

- `--mode mde|n|power` —— 给定 N+功效求 MDE、给定 MDE+功效求 N，或给定 N+MDE 求功效。默认 `mde`。
- `--design rct|cluster|multiarm|sim` —— 双臂 RCT、聚类 RCT（ICC）、多臂，或基于模拟。默认根据询问得到的设计推断。
- `--input <path>` —— 一份 [`/interview-me`](../interview-me/SKILL.md) 研究需求说明（位于 `quality_reports/specs/`），从中读取 RQ、结果变量与设计。

## 工作流

### Phase 0 —— 询问设计

收集设计参数。任何缺失项都**只问一次**，不能编造。必需项包括：

- **估计目标与检验：** 主要结果变量、单侧还是双侧检验、`alpha`（默认 0.05），以及目标是均值差、比例还是回归系数。
- **{效应量, N, 功效} 中的两个：** 效应要同时记录原始差值*和*标准单位（Cohen's d = 效应 / SD）；`power` 默认 0.80。
- **基线均值与 SD**（二值结果则为基线比例）：用于换算原始效应与标准化效应。
- **分配：** 处理组:对照组比例，默认 1:1。不等分配会损失功效，必须明确指出。
- **聚类：** 如果在群体层面（村庄、学校、诊所）随机化，需要 **ICC**（ρ）、平均簇规模（m）和簇数，并计算设计效应 `DEFF = 1 + (m − 1)·ρ` 与有效 N。
- **多重性：** 臂数 / 主要结果数、校正方法（Bonferroni、Holm，或不校正），以及功效按逐比较还是族错误率定义。

计算前先回显**起飞前报告**，列出设计、两个固定量、待求量、alpha、功效、分配、ICC/簇和多重性。估计目标或 SD 来源不清楚时，停下询问。

### Phase 1 —— 解析功效（标准设计）

双臂 RCT、聚类 RCT 和多臂比较使用解析法。优先使用 R 的 `pwr` / `WebPower`，或闭式的 `power.t.test` / `power.prop.test`；聚类设计用 `DEFF` 膨胀方差，或在有效 N 上运行 `pwr`。Stata 用户使用 `power twomeans` / `power twoproportions` / `power, cluster`；Python 使用 `statsmodels.stats.power`。将短脚本写入 `scripts/R/power_<slug>.R`（或 `.do` / `.py`），确保计算可复现，而不是只在控制台留下一个数字。

- **MDE 模式：** `MDE = (z_{1−α/2} + z_{1−β}) · SE(effect)`，其中 `SE` 由 SD、N、分配与 `DEFF` 构成。MDE 同时报告原始单位和标准化单位。
- **N 模式：** 给定目标 MDE，反解上式，求出总 N；聚类设计还要求出簇数。
- **功效模式：** 给定 N 和一个假设效应，计算实际达到的功效。
- **多臂：** 将 `alpha` 除以**族内比较数** `m`（Bonferroni `alpha/m`）：全臂对对照时 `m = K−1`，全两两比较时 `m = K(K−1)/2`。逐比较功效*与*族错误率功效都要报告。

遍历网格（N 或簇数 × 效应量），供 Phase 3 绘制功效曲线和 MDE-对-N 曲线。

### Phase 2 —— 基于模拟的功效（非标准设计）

如果设计**不是**标准的双臂比较，例如 DiD / 交错事件研究、IV / 2SLS、带序列相关的面板、非正态或删失结果变量，或估计量没有闭式 SE，就改用模拟。**原样复用 `/simulation-study` 脚手架**，见 [`simulation-study`](../simulation-study/SKILL.md) 与 [`.codebuddy/rules/simulation-conventions.md`](../../rules/simulation-conventions.md)：

1. 使用**带种子的参数化 DGP**，嵌入假设效应，并另设用于检验水平 size 的零假设 DGP。`set.seed(YYYYMMDD)` 只设一次；并行时使用 L'Ecuyer 流。
2. **估计量**必须使用真实数据分析时打算使用的同一个，例如 `fixest::feols` 双向固定效应、`did::att_gt`、`AER::ivreg`，并返回 `est, se, ci, p, reject`。
3. **功效 = 在 `alpha` 下拒绝 H0 的重复比例**；**水平 = 零假设 DGP 下的拒绝率**。相信功效前，先核验水平接近名义值。两者都要报告，并分别给出**蒙特卡洛标准误** = `sqrt(p(1−p)/R)`。
4. 遍历 N（或簇数 / 期数）以绘制功效曲线，并用 `saveRDS()` 将逐次重复的原始 tibble 保存到 `output/`。

模拟功效若没有 MCSE，或没有核验水平，就不能作为答案。

### Phase 3 —— 写出功效一节

在 `quality_reports/power/` 下生成：

- **`power_<slug>.md`**：一张表和一段方法学说明，格式如下。
- **`power_curve_<slug>.png`**：功效对 N（和/或 MDE 对 N）的曲线，并在目标功效和计划 N 处画参考线。
- `scripts/R/` 下的可复现脚本（或 `.do` / `.py`）。

```markdown
# Power Analysis: <study title>
**Date:** YYYY-MM-DD · **Design:** <rct|cluster|multiarm|sim> · **Method:** <analytical|simulation, R/Stata/Python>

| Quantity | Value |
|---|---|
| alpha (sided) | 0.05 (two-sided) |
| Target power | 0.80 |
| Baseline mean (SD) | <m0> (<sd>) |
| Allocation (T:C) | 1:1 |
| ICC / cluster size / #clusters | <ρ> / <m> / <J>  (DEFF = <…>) |
| Total N (analysis sample) | <N> |
| **MDE (raw / standardized)** | **<Δ> / <d>** |
| Achieved power at planned N | <…>  (± MCSE <…> if simulated) |

## Methods paragraph (paste into preregistration)
> Assuming a baseline outcome mean of <m0> (SD <sd>), 1:1 allocation, and a two-sided
> test at α = 0.05, a total sample of <N> [<J> clusters of <m>, ICC = <ρ>] yields 80%
> power to detect a minimum effect of <Δ> (<d> SD). [Simulation: under the hypothesized
> DGP, <P>% of <R> replications rejected H0 (MCSE <…>); size under the null was <…>.]
```

### Phase 4 —— 交接

如果由 `/preregister` 使用，将方法学段落 + MDE 行交回，用于预注册的功效一节。独立运行时，打印保存路径，并提醒用户：MDE 是一项*设计承诺*，必须在收集数据前记录。

## 退出行为

- **计算成功：** 退出 0；打印 MDE / N / 功效结果和保存路径。模拟模式还要在功效旁打印水平核验值。
- **设计欠定（{效应, N, 功效} 只给了一个）或 SD 来源含混：** 在 Phase 0 停下，只问一个具体问题，绝不猜测 SD 或 ICC。
- **模拟的水平核验失败**（零假设 DGP 下的经验水平远偏离名义值）：将功效标为 **UNRELIABLE** 并列出水平值；修好估计量/DGP 前，该功效数字不可信。

## 参数

- `--mode` `<mde|n|power>` —— 要求解的量：最小可检测效应、所需 N，或实际达到的功效。
- `--design` `<rct|cluster|multiarm|sim>` —— 设计类型：双臂 RCT、聚类/ICC、带校正的多臂，或面向非标准设计的模拟。
- `--input` `<spec>` —— `/interview-me` 研究需求说明或预注册草稿的路径，用于读取设计参数。

## 交叉引用

- [`.codebuddy/skills/preregister/SKILL.md`](../preregister/SKILL.md) —— 按本技能填写 `aea-rct`（以及 OSF）预注册的功效/MDE 一节；本技能交回方法学段落。
- [`.codebuddy/skills/simulation-study/SKILL.md`](../simulation-study/SKILL.md) —— Phase 2 复用的蒙特卡洛脚手架（带种子的 DGP、估计量网格、拒绝 H0 的百分比）。
- [`.codebuddy/rules/simulation-conventions.md`](../../rules/simulation-conventions.md) —— Phase 2 必须遵守的模拟契约（真相来自 DGP、MCSE、零假设下的水平）。
- [`.codebuddy/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md) · [`.codebuddy/skills/stata-replication/SKILL.md`](../stata-replication/SKILL.md) —— 已实现分析及其实际估计量/SE 所在之处；功效计算应使用同一个估计量。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 基线均值/SD/ICC 若来自受限访问数据，必须遵守披露规避限制。应引用已发表或预实验的矩，不要把原始机密统计量写入会向外上传的预注册。

## 本技能不做什么

- **不计算事后 / 观测功效。** 不根据已实现的结果计算「检测出当前估计值需要多少功效」，因为它只是 p 值的确定性函数，不能提供额外信息。功效只用于事前设计。
- **不替你选择效应量。** MDE 是*你的*设计承诺。本技能只计算假定效应（来自理论、预实验或元分析）对应的后果，不会编造一个看似合理的效应。
- **不提交到注册库。** 与 `/preregister` 一样，本技能只写文档，上传由用户完成。
- **不替代 `/simulation-study`。** Phase 2 只针对单个功效问题借用其脚手架；完整的偏误/RMSE/覆盖率研究仍由 `/simulation-study` 负责。
