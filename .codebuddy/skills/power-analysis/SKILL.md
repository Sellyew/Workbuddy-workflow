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

计算事前设计计算里三个相互扣合的量 —— **功效**、**所需 N**、**最小可检测效应（MDE）** —— 并输出一节用户可直接粘贴进预注册的功效说明。标准设计用解析法；非标准设计用基于模拟的方法（复用 `/simulation-study` 的脚手架模式）。

**核心原则：** 功效计算是*数据存在之前作出的设计期承诺*。固定 {效应量, N, 功效} 中的任意两个，解出第三个；永远不要从已实现的估计值反推一个「功效」数字（那是事后功效，没有信息量 —— 见「本技能不做什么」）。

## 何时使用

- **启动 RCT / 田野 / 调查实验之前** —— 为在 80–90% 功效下达到目标 MDE 而选择 N（或簇数）。
- **被 [`/preregister`](../preregister/SKILL.md) 用于 RCT 时** —— AEA RCT Registry 与多数 IRB 都要求功效/MDE 论证；`/preregister` 的 `aea-rct` 风格按本技能的各阶段来填这一节（本技能只能由用户调用，所以是被阅读并遵循，而不是被调用）。
- **R&R 期间** —— 审稿人问 "was this study adequately powered to detect the effect you claim?" 时。
- **设计蒙特卡洛时** —— 在交给 `/simulation-study` 之前设定 `R` 与样本量。

## 输入

`$ARGUMENTS` 可带参数；缺失的部分在 Phase 0 里询问补全。

- `--mode mde|n|power` —— 给定 N+功效求 MDE、给定 MDE+功效求 N，或给定 N+MDE 求功效。默认 `mde`。
- `--design rct|cluster|multiarm|sim` —— 双臂 RCT、聚类 RCT（ICC）、多臂，或基于模拟。默认由询问到的设计推断。
- `--input <path>` —— 一份 [`/interview-me`](../interview-me/SKILL.md) 的规格（位于 `quality_reports/specs/` 下），从中取出 RQ、结果变量与设计。

## 工作流

### Phase 0 —— 询问设计

收集设计参数；对任何缺失项**只问一次**，而不是编造。必需项：

- **估计目标与检验：** 主要结果变量、单侧还是双侧检验、`alpha`（默认 0.05），以及目标是均值差、比例，还是回归系数。
- **{效应量, N, 功效} 中的两个：** 效应既记为原始差值*也*记为标准单位（Cohen's d = 效应 / SD）—— 两者都记；`power` 默认 0.80。
- **基线均值与 SD**（二值结果则为基线比例）—— 用于在原始效应与标准化效应之间换算。
- **分配：** 处理组:对照组比例（默认 1:1；不等分配会损失功效 —— 要指明）。
- **聚类：** 若随机化在群体层面（村庄、学校、诊所），需要 **ICC**（ρ）、平均簇规模（m）与簇数。计算设计效应 `DEFF = 1 + (m − 1)·ρ` 与有效 N。
- **多重性：** 臂数 / 主要结果数；校正方法（Bonferroni、Holm，或不校正），以及功效是逐比较的还是族错误率意义下的。

计算之前回显一份**起飞前报告**（设计、两个固定的量、正在求解的那个量、alpha、功效、分配、ICC/簇、多重性）。若估计目标或 SD 来源含混，停下并询问。

### Phase 1 —— 解析功效（标准设计）

双臂 RCT、聚类 RCT 与多臂比较用解析法计算。优先用 R 的 `pwr` / `WebPower`（或闭式 `power.t.test` / `power.prop.test`）；聚类设计用 `DEFF` 膨胀方差，或在有效 N 上跑 `pwr`。Stata 用户：`power twomeans` / `power twoproportions` / `power, cluster`；Python：`statsmodels.stats.power`。把一段短脚本写到 `scripts/R/power_<slug>.R`（或 `.do` / `.py`），让这次计算可复现，而不是控制台里的一次性数字。

- **MDE 模式：** `MDE = (z_{1−α/2} + z_{1−β}) · SE(effect)`，其中 `SE` 由 SD、N、分配与 `DEFF` 构成。MDE 以原始单位与标准化单位都报。
- **N 模式：** 对给定的目标 MDE，把上式反解出总 N（聚类时还有簇数）。
- **功效模式：** 给定 N 与一个假设的效应，返回达到的功效。
- **多臂：** 把 `alpha` 除以**族内比较数** `m`（Bonferroni `alpha/m`）：全臂对对照时 `m = K−1`，全两两比较时 `m = K(K−1)/2`。逐比较功效*与*族错误率功效都要报。

扫一遍网格（N 或簇数 × 效应量），好让 Phase 3 能画功效曲线与 MDE-对-N 曲线。

### Phase 2 —— 基于模拟的功效（非标准设计）

当设计**不是**干净的双臂比较时 —— DiD / 交错事件研究、IV / 2SLS、带序列相关的面板、非正态或删失的结果变量，或任何没有闭式 SE 的估计量 —— 切换到模拟。**原样复用 `/simulation-study` 脚手架**（见 [`simulation-study`](../simulation-study/SKILL.md) 与 [`.codebuddy/rules/simulation-conventions.md`](../../rules/simulation-conventions.md)）：

1. **带种子的参数化 DGP**，把假设的效应嵌进去（以及用于检验水平 size 的零假设 DGP）。`set.seed(YYYYMMDD)` 只设一次；并行时用 L'Ecuyer 流。
2. **估计量** = 你真会在真实数据上用的那个（例如 `fixest::feols` 双向固定效应、`did::att_gt`、`AER::ivreg`），返回 `est, se, ci, p, reject`。
3. **功效 = 在 `alpha` 下拒绝 H0 的重复比例**；**水平 = 零假设 DGP 下的拒绝率**（在相信功效之前先核验它接近名义值）。两者都报，并各带**蒙特卡洛标准误** = `sqrt(p(1−p)/R)`。
4. 扫 N（或簇数 / 期数）以描出功效曲线；用 `saveRDS()` 把逐次重复的原始 tibble 存到 `output/`。

没有 MCSE、或没做水平核验的模拟功效数字，还不算答案。

### Phase 3 —— 写出功效一节

在 `quality_reports/power/` 下产出交付物：

- **`power_<slug>.md`** —— 一张表加一段方法学说明（见下）。
- **`power_curve_<slug>.png`** —— 功效对 N（和/或 MDE 对 N），并在目标功效与设计计划 N 处画参考线。
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

若由 `/preregister` 调用，把方法学段落 + MDE 行交回去，用于预注册的功效一节。若独立运行，打印保存路径，并提醒用户：MDE 是一份*设计承诺*，要在数据收集之前记录下来。

## 退出行为

- **计算成功：** 退出 0；打印 MDE / N / 功效结果、保存路径，以及（模拟模式下）功效旁边的水平核验值。
- **设计欠定（{效应, N, 功效} 只给了一个）或 SD 来源含混：** 在 Phase 0 停下，只问一个具体问题 —— 绝不猜 SD 或 ICC。
- **模拟的水平核验失败**（零假设 DGP 下的经验水平远偏离名义值）：把功效报为 **UNRELIABLE**，并把水平值摆出来；在估计量/DGP 修好之前，这个功效数字不可信。

## 参数

- `--mode` `<mde|n|power>` —— 解什么：最小可检测效应、所需 N，还是达到的功效。
- `--design` `<rct|cluster|multiarm|sim>` —— 设计族 —— 双臂 RCT、聚类/ICC、带校正的多臂，或面向非标准设计的基于模拟。
- `--input` `<spec>` —— 一份 `/interview-me` 规格或预注册草稿的路径，从中读设计参数。

## 交叉引用

- [`.codebuddy/skills/preregister/SKILL.md`](../preregister/SKILL.md) —— 照着本技能来填 `aea-rct`（以及 OSF）预注册的功效/MDE 一节；本技能交回方法学段落。
- [`.codebuddy/skills/simulation-study/SKILL.md`](../simulation-study/SKILL.md) —— Phase 2 复用的蒙特卡洛脚手架（带种子的 DGP、估计量网格、拒绝 H0 的百分比）。
- [`.codebuddy/rules/simulation-conventions.md`](../../rules/simulation-conventions.md) —— Phase 2 必须遵守的模拟契约（真相来自 DGP、MCSE、零假设下的水平）。
- [`.codebuddy/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md) · [`.codebuddy/skills/stata-replication/SKILL.md`](../stata-replication/SKILL.md) —— 已实现的分析（及其实际估计量/SE）所在之处；功效计算应当用同一个估计量。
- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 当基线均值/SD/ICC 取自受限访问数据时，适用披露规避的限制；要引用已发表或预实验的矩，而不是把原始机密统计量嵌进（向外上传的）预注册。

## 本技能不做什么

- **事后 / 观测功效。** 它拒绝从已实现的结果计算「我们要检测出自己这个估计值所需要的功效」—— 那是 p 值的确定性函数，什么都告诉不了你。功效只存在于事前。
- **替你挑效应量。** MDE 是*你的*设计承诺；本技能计算一个假定效应（来自理论、预实验或元分析）的后果，它不发明一个说得过去的效应。
- **提交到注册库。** 与 `/preregister` 一样，它写一份文档；上传是用户的事。
- **替代 `/simulation-study`。** Phase 2 只为单个功效问题借用那套脚手架；完整的偏误/RMSE/覆盖率研究是 `/simulation-study` 的活。
