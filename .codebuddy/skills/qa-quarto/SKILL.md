---
name: qa-quarto
description: 对抗式 Quarto 与 Beamer 一致性 QA。批评代理把 Quarto HTML 渲染结果与 Beamer PDF 基准就内容与视觉一致性做比对；修复代理施加修改；循环至 APPROVED，或连续两轮都没有新发现为止（兜底上限 5 轮）。用户说 "qa the quarto"、"check parity"、"does the html match the pdf?"、"quarto matches beamer?" 时使用，或在一次 translate-to-quarto 运行之后使用。要求 `.qmd` 已渲染，且有一份 `.pdf` 基准。
description_zh: 对抗式 Quarto 与 Beamer 一致性 QA。批评代理把 Quarto HTML 渲染结果与 Beamer PDF 基准就内容与视觉一致性做比对；修复代理施加修改；循环至 APPROVED，或连续两轮都没有新发现为止（兜底上限 5 轮）。用户说 "qa the quarto"、"check parity"、"does the html match the pdf?"、"quarto matches beamer?" 时使用，或在一次 translate-to-quarto 运行之后使用。要求 `.qmd` 已渲染，且有一份 `.pdf` 基准。
argument-hint: "[LectureN]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task"]
---

# 对抗式 Quarto 与 Beamer QA 工作流

> **[本平台适配 · 2026-10-31] 这个技能刻意不声明 `context: fork`。**
> 声明了它，技能会被送进一个 detached 子会话执行，而**那个会话的工具集里没有 `Agent`**
> （同一目录下的 `allowed-tools` 明明申请了它，也拿不到）。这个技能的价值建立在
> 「批评者 → 修复者 → 重审」的空轮收敛
> 上：每个透镜要在**独立上下文**里跑，互不污染，最后归并。
> 拿不到 `Agent` 之后，这些透镜只能由同一个会话依次扮演一遍——报告上写着「多角度审过」，
> 实际上是同一双眼睛看了几遍，而同一双眼睛第二遍也看不见第一遍漏掉的东西。
>
> 代价说清楚：不 fork 意味着技能的中间过程（读文件、跑命令、试错）会占用主会话上下文，
> 长流程可能需要中途压缩一次。**这个代价换的是独立性，值。**
> 实测证据与复现命令见 [`platform-facts.md`](../../references/platform-facts.md) 的技能一节。

用迭代的批评／修复循环，把 Quarto HTML 幻灯片与其 Beamer PDF 基准做比对。

**理念：** Beamer PDF 是黄金标准。Quarto 译本在每一个维度上都至少要一样好。

---

## 工作流

```
Phase 0: Pre-flight → Phase 1: Critic audit → Phase 2: Fixer → Phase 3: Re-audit → Loop until APPROVED or dry (2 consecutive dry rounds; fallback cap 5)
```

## 硬门禁（不可协商）

| 门禁 | 条件 |
|------|-----------|
| **Overflow（溢出）** | 没有内容被裁切 |
| **Plot Quality（图形质量）** | 交互图表 >= 静态图 |
| **Content Parity（内容一致）** | 不缺幻灯片／公式／文字 |
| **Visual Regression（视觉回归）** | 所有维度上 Quarto >= Beamer |
| **Slide Centering（居中对齐）** | 内容居中，不跳动 |
| **Notation Fidelity（记号保真）** | 全部数学式与 Beamer 逐字一致 |

## 阶段 0：起飞前检查

1. 定位 Beamer（.tex/.pdf）与 Quarto（.qmd/.html）文件
2. 检查新鲜度（QMD 比 HTML 新就重渲染）
3. 如适用，核验 TikZ SVG
4. 度量这次渲染：`"${SLIDE_QA_PYTHON:-python}" scripts/slide-qa.py Quarto/[Lecture].html`。它在无头 Chrome 里加载整套幻灯片，写出 `quality_reports/audits/slide-qa/[Lecture]/report.md`，含每页溢出的像素值，以及每页一张截图。退出码 1 表示它发现了问题——溢出、内容被裁切、图片损坏，或文件缺失、大小写写错；退出码 2 表示它跑不起来（通常是缺 Playwright——脚本会打印一次性的 venv 安装命令和要设置的 `SLIDE_QA_PYTHON` 那一行）——照实说明，批评代理则回退为读源码。

## 阶段 1：首轮审读

启动 `quarto-critic` 代理，全面比对 Beamer 与 Quarto，把阶段 0 的 slide-qa 报告路径传给它，供 Overflow 门禁用。报告保存到 `quality_reports/[Lecture]_qa_critic_round1.md`。

## 阶段 2：修复循环

若未 APPROVED，启动 `quarto-fixer` 代理施加修改（Critical → Major → Minor），重渲染并核验。

## 阶段 3：复审

对修复代理的重渲染结果重跑 `scripts/slide-qa.py`，然后用新报告重新启动批评代理核验修改。必要时回到阶段 2。

## 迭代上限——空轮收敛

这是 [`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) 里的**空轮收敛**原语：批评代理返回 `FINDING`（硬门禁表就是 CRITICAL 的汇总，见 [`orchestration-schemas.md`](../../references/orchestration-schemas.md)）；循环**在连续 2 个空轮之后收敛**——空轮指一轮下来新增 0 条 CRITICAL/MAJOR 发现（按 `id = sha1(file:line:locus)` 去重）——而不是停在某个固定轮数。

- **兜底上限：**5 轮为一个不收敛的循环设界，然后带剩余问题升级给用户。
- **两次命中：**同一个门禁在第 N 轮和第 N+2 轮都失败，就标记给用户，而不是再打一次补丁（[`summary-parity.md`](../../rules/summary-parity.md)）。
- 当且仅当每个硬门禁都通过、且不剩任何 CRITICAL 或 MAJOR 发现时为 APPROVED（minor 的列出来给用户）。

## 最终报告

保存到 `quality_reports/[Lecture]_qa_final.md`，含硬门禁状态、迭代摘要与剩余问题。

## 发现要经校验，而不只是写出来（v2.5）

本技能的审读者按 [`finding-schema.json`](../../references/finding-schema.json) 里机器校验的契约输出发现。报告是 JSON **数组**。

**在投入审读成本之前先冒烟测试这套装置**——一次运行扇出一批审读者、然后写不出一份合法报告，等于把整轮白费：

```bash
echo '[]' | python scripts/validate-findings.py
```

审读代理是只读的，所以**由本技能写文件**。对每个审读者的最终响应：把散文报告保存到本技能为该审读者指定的报告路径，把它结尾那段围栏 `json` 块拷到草稿文件，并在校验时填入 id：

```bash
python scripts/validate-findings.py --fill-ids block.json > <report>.json.tmp \
  && mv <report>.json.tmp <report>.json || rm -f <report>.json.tmp   # exit 0 required; a failed run keeps no file
python scripts/validate-findings.py --check-quotes <report>.json   # each quote must be the file's own text (orchestration-schemas.md §1)
```

没有返回 `json` 块的审读者，或返回的块未通过校验，就等于没审：带着校验器的错误文本重新派发一次，然后把该透镜记为缺失，而不是在没有它的情况下归并。

契约强制了什么，以及为什么：

- **`rule`**——被违反的成文规则或标准。一条没有引用任何规则的发现只是意见，而意见不为提交把关。
- **`failing_case`**——一个具体的配置，在该配置下该断言会破，或确切缺失的前提。*"This could be clearer"* 通不过校验。
- **`id = sha1("<file>:<line>:<locus>")`**——确定性的，所以跨轮去重是精确的，两次即止规则可以被检查而不是靠肉眼。
- **`mechanical`**——只有不能改变结果的修改（错字、交叉引用、格式、标签）才为 `true`。对估计目标、假设、设定、推断程序、样本定义或报告语言，**永远**不为 true：那些要退回给研究者。

在校验*之前*先施加 [`orchestration-schemas.md` §7](../../references/orchestration-schemas.md) 里的**逐透镜证据负担**和**「不算数」过滤器**，这样已知的误报根本到不了裁决者面前。核验这一遍是**偏向反驳的**，并设定每条发现的 `verdict`（审读者留空）：只有 `verdict: "confirmed"` 的发现才会发布；任何它无法找到依据的都丢弃，而不是降级成警告。
