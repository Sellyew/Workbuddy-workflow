---
name: qa-quarto
description: 对抗式检查 Quarto 与 Beamer 一致性。批评代理比较 Quarto HTML 渲染结果与 Beamer PDF 基准的内容和视觉效果；修复代理实施修改；循环直到 APPROVED，或连续两轮没有新增 CRITICAL/MAJOR，兜底上限 5 轮。用户说 "qa the quarto"、"check parity"、"does the html match the pdf?"、"quarto matches beamer?"、"检查 Quarto 一致性"、"HTML 和 PDF 一致吗"，或在一次 translate-to-quarto 运行后使用。要求 `.qmd` 已渲染，并有 `.pdf` 基准。
description_zh: 对抗式检查 Quarto 与 Beamer 一致性。批评代理比较 Quarto HTML 渲染结果与 Beamer PDF 基准的内容和视觉效果；修复代理实施修改；循环直到 APPROVED，或连续两轮没有新增 CRITICAL/MAJOR，兜底上限 5 轮。用户说 "qa the quarto"、"check parity"、"does the html match the pdf?"、"quarto matches beamer?"、"检查 Quarto 一致性"、"HTML 和 PDF 一致吗"，或在一次 translate-to-quarto 运行后使用。要求 `.qmd` 已渲染，并有 `.pdf` 基准。
argument-hint: "[LectureN]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "Task"]
---

# 对抗式 Quarto 与 Beamer QA 工作流

> **[本平台适配 · 2026-10-31] 这个技能刻意不声明 `context: fork`。**
> 声明该字段后，技能会进入 detached 子会话，而那个会话的工具集**没有 `Agent`**，
> 即使 `allowed-tools` 已申请也拿不到。本技能依靠「批评者 → 修复者 → 重审」
> 实现空轮收敛，每个透镜都必须在**独立上下文**中运行，避免相互污染，最后再归并结果。
> 没有 `Agent` 时，同一会话只能依次扮演这些透镜；报告看似完成了多角度审查，
> 实际只是同一双眼睛重复查看，而第二遍仍可能看不见第一遍漏掉的问题。
>
> 不 fork 也有代价：读文件、运行命令和试错等中间过程会占用主会话上下文，
> 长流程可能需要中途压缩一次。**这个代价换的是独立性，值。**
> 实测证据与复现命令见 [`platform-facts.md`](../../references/platform-facts.md) 的技能一节。

本技能通过迭代批评／修复循环，比较 Quarto HTML 幻灯片与 Beamer PDF 基准。

**理念：** Beamer PDF 是黄金标准，Quarto 译本在每个维度上都必须至少一样好。

---

## 输入

按 shell 引号规则对 `$ARGUMENTS` 分词，将可选位置参数 `LectureN` 赋给命名变量 `lecture`；未提供时设 `lecture=LectureN`。额外位置参数或任何未知旗标都必须拒绝：停止并报告用法错误，不得猜测。后续阶段只使用 `lecture`，不再读取原始参数串；所有由它派生的路径都必须以加引号的完整路径使用。

## 工作流

```
Phase 0: Pre-flight → Phase 1: Critic audit → Phase 2: Fixer → Phase 3: Re-audit → Loop until APPROVED or dry (2 consecutive rounds with no new CRITICAL/MAJOR; fallback cap 5)
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

## 阶段 0：开始前检查

1. 定位 Beamer（.tex/.pdf）与 Quarto（.qmd/.html）文件。
2. 检查新鲜度；QMD 比 HTML 新时重新渲染。
3. 如适用，核验 TikZ SVG。
4. 度量本次渲染：`"${SLIDE_QA_PYTHON:-python}" scripts/slide-qa.py "Quarto/${lecture}.html"`。脚本在无头 Chrome 中加载整套幻灯片，写出 `quality_reports/audits/slide-qa/[Lecture]/report.md`，包含每页溢出的像素值和每页一张截图。退出码 1 表示发现问题，包括溢出、内容裁切、图片损坏、文件缺失或大小写错误。退出码 2 表示无法运行，通常因为缺少 Playwright；脚本会打印一次性的 venv 安装命令和需要设置的 `SLIDE_QA_PYTHON` 行。必须照实报告，此时批评代理改为读取源码。

## 阶段 1：首轮审读

启动 `quarto-critic` 代理，全面对比 Beamer 与 Quarto，并把阶段 0 的 slide-qa 报告路径传给它，供 Overflow 门禁使用。报告保存到 `quality_reports/[Lecture]_qa_critic_round1.md`。

## 阶段 2：修复循环

若结果不是 APPROVED，启动 `quarto-fixer` 代理按 Critical → Major → Minor 的顺序实施修改，然后重新渲染并核验。

## 阶段 3：复审

对修复代理重新渲染的结果再次运行 `scripts/slide-qa.py`，再把新报告交给重新启动的批评代理核验修改。必要时返回阶段 2。

## 迭代上限——空轮收敛

本技能采用 [`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) 的**空轮收敛**原语。批评代理返回 `FINDING`，硬门禁表是 CRITICAL 的汇总，见 [`orchestration-schemas.md`](../../references/orchestration-schemas.md)。**同一轮内按 `id = sha1(file:line:locus)` 去重；跨轮按 `file` + `locus` 判断是否新增**，因为修复会移动行号，不能拿含行号的 id 做跨轮身份。循环在**连续 2 个空轮后收敛**；空轮指与此前轮次按 `file` + `locus` 比较后，新增 0 条 CRITICAL/MAJOR 发现。循环不会仅因达到固定轮数而停止。

- **兜底上限：**不收敛的循环最多运行 5 轮，随后带着剩余问题升级给用户。
- **两次命中：**同一发现按 `file` + `locus` 判定，在第 N 轮和第 N+2 轮都存在时，标记给用户，不再打第三次补丁；不得按是否属于同一门禁判定（[`summary-parity.md`](../../rules/summary-parity.md)）。
- 当且仅当每个硬门禁都通过，且没有剩余 CRITICAL 或 MAJOR 发现时，结果才是 APPROVED；minor 发现仍列出给用户。

## 最终报告

保存到 `quality_reports/[Lecture]_qa_final.md`，包含硬门禁状态、迭代摘要和剩余问题。

## 发现要经校验，而不只是写出来（v2.5）

审读者必须按照 [`finding-schema.json`](../../references/finding-schema.json) 的机器校验契约输出发现。报告是 JSON **数组**。

**投入审读成本前，先对这套装置做冒烟测试。**若扇出审读者后无法写出合法报告，整轮工作都会浪费：

```bash
echo '[]' | python scripts/validate-findings.py
```

审读代理只读，因此**由本技能写文件**。收到每个审读者的最终响应后，把散文报告保存到指定路径，把响应末尾的围栏 `json` 块复制到草稿文件，并在校验时填入 id：

```bash
python scripts/validate-findings.py --fill-ids block.json > <report>.json.tmp \
  && mv <report>.json.tmp <report>.json || rm -f <report>.json.tmp   # exit 0 required; a failed run keeps no file
python scripts/validate-findings.py --check-quotes <report>.json   # each quote must be the file's own text (orchestration-schemas.md §1)
```

审读者未返回 `json` 块，或返回内容未通过校验，就等于没有完成审读。带上校验器错误文本重新派发一次；若仍失败，把该透镜记为缺失，不得在缺少它的情况下归并。

契约要求及理由如下：

- **`rule`**：被违反的成文规则或标准。没有引用规则的发现只是意见，不能为提交把关。
- **`failing_case`**：一个会使断言失效的具体配置，或确切缺失的前提。*"This could be clearer"* 无法通过校验。
- **`id = sha1("<file>:<line>:<locus>")`**：确定性 id 用于同一轮内精确去重；跨轮改用 `file` + `locus`，因为修复会改变行号。两次即止规则也按跨轮身份机械检查，不靠肉眼。
- **`mechanical`**：只有不可能改变结果的修改，例如错字、交叉引用、格式和标签，才为 `true`。涉及估计目标、假设、设定、推断程序、样本定义或报告语言时，**永远**不为 true；这些必须退回研究者。

校验*之前*，先应用 [`orchestration-schemas.md` §7](../../references/orchestration-schemas.md) 的**逐透镜证据负担**和**「不算数」过滤器**，避免已知误报进入裁决。核验阶段应**优先尝试反驳**，并设置每条发现的 `verdict`，审读者留空。只有 `verdict: "confirmed"` 的发现可以发布；无法找到依据的发现一律丢弃，不能降级为警告。
