---
name: disclosure-check
description: 在任何发布之前，对建立在受限或机密数据之上的分析产出（表、图、日志）预筛统计披露限制问题。扫描小单元格计数、互补抑制缺口、主导性（p-percent / (n,k)）、可重识别的精确计数、PII 泄漏，以及未取整的敏感统计量；把每条发现分类为 CRITICAL / WARNING / OK，并对任何 CRITICAL 设门禁。在存放或共享受限数据结果之前使用，或当用户说 "disclosure check"、"SDL scan"、"is this output safe to release"、"check for small cells"、"disclosure avoidance"、"pre-screen for the RDC" 或 "can I export this from the enclave" 时使用。
description_zh: 在任何发布之前，对建立在受限或机密数据之上的分析产出（表、图、日志）预筛统计披露限制问题。扫描小单元格计数、互补抑制缺口、主导性（p-percent / (n,k)）、可重识别的精确计数、PII 泄漏，以及未取整的敏感统计量；把每条发现分类为 CRITICAL / WARNING / OK，并对任何 CRITICAL 设门禁。在存放或共享受限数据结果之前使用，或当用户说 "disclosure check"、"SDL scan"、"is this output safe to release"、"check for small cells"、"disclosure avoidance"、"pre-screen for the RDC" 或 "can I export this from the enclave" 时使用。
argument-hint: "[outputs-dir] [--provider census|irs|irb|generic] [--threshold N] (outputs-dir defaults to output/)"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]

---

# `/disclosure-check` —— 统计披露限制预筛

扫描建立在**受限或机密数据**（Census FSRDC、IRS SOI、行政登记册、链式健康记录、专有企业面板）之上的分析产出，找出那些会让导出申请被拒的披露规避问题 —— 在它送到数据提供方官方披露审查*之前*。本技能是**预筛，不是**那次审查的替代品。

**核心原则：** 一个未被抑制的 `n=3` 单元格、一个能锁定到某一家企业的精确计数，或一次 `p`-percent 主导性失败，都可能重识别出某个人或某个机构。要在你的机器上抓住它，而不是在 RDC 分析师的拒信里。

## 何时使用

- **在从** Census FSRDC / 安全数据飞地 / RDC **申请导出之前。**
- **在把**受限数据结果**存放到** openICPSR、某份期刊，或飞地之外的某位共同作者之前。
- **在共享任何**源自机密微观数据的图、表或日志**之前。**
- **作为一个发布门禁。** 配一次提交前 / 存放前调用，这样没有哪份受限数据产出会在未预筛的情况下出库。这是任何受限数据项目的数据管理计划的基础。

## 输入

- `$0` —— 要扫描的产出目录。默认 `output/`，各语言的流水线都写入此处；若它不存在、但存在 v2.6 之前的 `scripts/<lang>/_outputs/`，则扫描后者并说明这一点。也接受任何导出暂存目录（例如分析师为 RDC 备好的 `to_review/` 文件夹）。
- `--provider` —— 选择加载哪一套披露规则画像（Phase 0）。取值之一：`census` / `irs` / `irb` / `generic`。**各提供方不同** —— 阈值与规则不可互换；默认的 `generic` 是刻意保守的那一套。
- `--threshold N` —— 覆盖最小单元格计数（默认 `n<10`）。Census FSRDC 对机构常用 10；IRS 与许多 IRB 不同。永远要与你提供方的*书面*规则对齐。

## 工作流

### Phase 0：加载提供方的披露规则

1. 阅读 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md)，取得本项目的受限数据处理契约与规则画像占位。
2. 加载 `--provider` 画像（一份**占位配置**，由 fork 者依据自己的*已签*协议填入 —— Census、IRS 与 IRB 的规则各不相同，且覆盖此处任何默认值）：
   - **最小单元格计数**（默认 `n<10`），
   - **主导性规则**：`p`-percent（若最大应答者贡献超过总量的 `p`%，该单元格不安全）与 `(n,k)`（前 `n` 个单位超过总量的 `k`%），
   - 敏感统计量（计数、合计、比率）所需的**取整**，
   - 极端值的**顶编码 / 底编码**阈值，
   - 任何带地理编码统计量的**地理**最小人口。
3. 若没有记录任何已签规则的取值，回落到保守的 `generic` 画像，并在报告里**显著标出**必须替换为真实提供方阈值。

### Phase 1：扫描产出目录

对产出目录做 glob，取 `.tex`、`.csv`、`.txt`、`.log`、`.smcl`、`.out`、`.md` 的表格与图数据文件。对每一份：

- **单元格计数** —— 解析表格单元格 / 频数列；标出任何 `0 < n < threshold` 且尚未被抑制的计数。
- **互补抑制缺口** —— 若某行/列中一个单元格被抑制，但边际合计与其余单元格让读者可以靠减法反推出来，那么这次抑制是**不完整的**。
- **主导性** —— 对任何可获得（或可推断出）单位级贡献的合计/均值单元格，施加 `p`-percent 与 `(n,k)` 规则。
- **可重识别的精确计数** —— 小整数（例如「4 hospitals」「1 firm」，或某个只有一个观测的最大值/最小值），能把某个单位单独点出来。
- **PII 泄漏** —— 用正则找姓名、SSN（`\d{3}-\d{2}-\d{4}`）、精确出生日期、地址、精确经纬度或细粒度地理编码、残留在产出里的记录 ID。
- **未取整的敏感统计量** —— 提供方要求取整、却仍精确未取整的计数/合计。

### Phase 2：把每条发现分类 —— CRITICAL / WARNING / OK

| 处置 | 含义 | 例子 |
|---|---|---|
| **CRITICAL** | 会过不了提供方的披露审查；阻断发布。 | `n=3` 单元格未抑制；互补抑制漏洞；`p`-percent 主导性失败；任何 PII；能识别出 ≤2 个单位的精确计数。 |
| **WARNING** | 看起来安全，但需要人的判断。 | 单元格恰好落在阈值上；未取整的合计刚超过某个取整基数；地理统计量贴近最小人口下限。 |
| **OK** | 在已加载的规则之内，无需动作。 | 计数 ≥ 阈值且已取整；主导性通过；无 PII。 |

当两条发现相互作用时（一个被抑制的单元格 + 一个可回收的边际），把它们**一并**报告 —— 门禁关心的是联合披露风险，而不是孤立地看每个单元格。要有经济学意识：按（队列 × 时期）计的 DiD / 事件研究单元格计数、IV 第一阶段子样本、RCT 处理臂 × 分层平衡表，以及面板里的企业计数，都是惯犯。

### Phase 3：提出补救

对每条 CRITICAL / WARNING，按偏好顺序提出标准 SDL 修法：

- **抑制** 出问题的单元格（以及它的补格，如果边际允许反推）。
- **取整** 计数/合计到提供方的基数（例如取到最近的 10 或 15）。
- **顶编码 / 底编码** 极端值。
- **聚合** —— 合并稀疏类别、粗化地理、放宽分箱，直到每个单元格都越过阈值。
- **丢弃** 该统计量，如果没有任何补救能同时保住安全与意义。

每条建议都点名文件、单元格/位置、它违反了哪条规则，以及具体改法 —— 但从不自动施加（披露决策归分析师）。

### Phase 4：门禁

任何 **CRITICAL** 都非零退出。WARNING 只浮出，不阻断。见退出行为。

## 输出 / 报告格式

写出 `quality_reports/disclosure_check_[outputs-dir-slug].md`：

```markdown
# Disclosure Check: [outputs dir]

**Date:** [YYYY-MM-DD]
**Provider profile:** census | irs | irb | generic   (rules source: confidential-data.md)
**Min cell count:** [N]   **Dominance:** p=[p]%, (n,k)=([n],[k]%)   **Rounding base:** [b]

## Summary
| Disposition | Count |
|---|---|
| CRITICAL | M |
| WARNING | W |
| OK | P |
| **Verdict** | **PASS / FAIL** (FAIL iff M > 0) |

## CRITICAL (blocks release)
| File | Location | Rule violated | Observed | Suggested remediation |
|---|---|---|---|---|
| tab3_by_cohort.tex | row "2008", col "n" | min cell (n<10) | n=4 | suppress cell + suppress complement in margin |

## WARNING (human judgment)
| File | Location | Concern | Suggested action |
|---|---|---|---|

## OK
[counts only, or a short list]

## Next steps
1. Resolve every CRITICAL — suppress / round / top-code / aggregate, then re-run.
2. Review WARNINGs with the agreement's written rules in hand.
3. Re-run until zero CRITICAL, THEN submit to the provider's OFFICIAL disclosure review.
```

## 退出行为

- **零 CRITICAL：** 退出 0；打印报告。（允许 WARNING —— 它们只浮出，不阻断。）
- **任何 CRITICAL：** 退出 1；摘要写到 stderr。这让本技能可用作发布 / 存放门禁。与 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 的门禁语义一致：WARNING ≠ FAIL，只有 CRITICAL 阻断。
- **没有加载规则（generic 兜底）：** 退出 0，并给出**显著警告**：未提供真实提供方阈值 —— 预筛跑过了，但用的是保守默认值，不是实际协议。

## 参数

- `--provider` `<name>` —— 加载该数据提供方的披露规则（例如 `census`、`irs`、`irb`）。默认：通用小单元格规则集。
- `--threshold` `<n>` —— 覆盖最小单元格计数阈值（默认 `n<10`）；对齐你数据使用协议里的实际规则。

## 交叉引用

- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 受限数据处理契约 + 本技能加载的提供方规则画像。
- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 对受限数据的论文，复现包给的是代码 + 访问路径，不是微观数据；发布每个产出之前都先预筛。
- [`.codebuddy/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) —— 稿件↔代码的数值核验：对*保留*的数值跑它，对*发布*的数值跑本技能。
- [`.codebuddy/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md)、[`.codebuddy/skills/stata-replication/SKILL.md`](../stata-replication/SKILL.md) —— 产出本技能所筛的 R / Stata / Python 输出。
- [AEA Data Editor checklist](https://aeadataeditor.github.io/) 与 [DCAS standard](https://datacodestandard.org/) —— 受限数据存放的披露 + 访问预期（openICPSR 受限访问 stub）。

## 本技能不做的事

- **它不替代数据提供方的官方披露审查。** Census/RDC、IRS 与 IRB 的分析师做权威审查；本技能**预筛**，让官方审查更可能一次通过。这里的 PASS 不是发布许可。
- **它不认证你的规则是对的。** 它施加的是你从*已签*协议里**加载**的阈值；若加载的 `--provider` 画像是错的，扫描就是错的。要与书面协议对齐，而不是与某个默认值对齐。
- **它不搬移、加密或传输数据，** 绝不从飞地外泄微观数据 —— 它只读你指定给它的暂存产出。
- **它抓不到每一种披露风险。** 跨已发布表格的差分、纵向重识别、基于模型的推断式披露，都可能绕过逐文件扫描。跑干净是必要条件，不是充分条件。
