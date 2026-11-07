---
name: disclosure-check
description: 在发布前预筛基于受限或机密数据生成的表、图和日志，检查是否违反统计披露限制。扫描小单元格计数、互补抑制缺口、主导性（p-percent / (n,k)）、可重识别的精确计数、PII 泄漏和未取整的敏感统计量；把每条发现分为 CRITICAL / WARNING / OK，任何 CRITICAL 都阻断发布。在存放或共享受限数据结果之前使用，或当用户说 "disclosure check"、"SDL scan"、"is this output safe to release"、"check for small cells"、"disclosure avoidance"、"pre-screen for the RDC"、"can I export this from the enclave"、"披露风险检查"、"小单元格检查"、"这些结果能发布吗" 或 "能导出飞地吗" 时使用。
description_zh: 在发布前预筛基于受限或机密数据生成的表、图和日志，检查是否违反统计披露限制。扫描小单元格计数、互补抑制缺口、主导性（p-percent / (n,k)）、可重识别的精确计数、PII 泄漏和未取整的敏感统计量；把每条发现分为 CRITICAL / WARNING / OK，任何 CRITICAL 都阻断发布。在存放或共享受限数据结果之前使用，或当用户说 "disclosure check"、"SDL scan"、"is this output safe to release"、"check for small cells"、"disclosure avoidance"、"pre-screen for the RDC"、"can I export this from the enclave"、"披露风险检查"、"小单元格检查"、"这些结果能发布吗" 或 "能导出飞地吗" 时使用。
argument-hint: "[outputs-dir] [--provider census|irs|irb|generic] [--threshold N] (outputs-dir defaults to output/)"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]

---

# `/disclosure-check` —— 统计披露限制预筛

本技能扫描基于**受限或机密数据**（Census FSRDC、IRS SOI、行政登记册、链式健康记录、专有企业面板）生成的分析产出，找出可能导致导出申请被拒的披露规避问题。它运行在数据提供方的官方披露审查*之前*，只是**预筛，不能替代官方审查**。

**核心原则：**未抑制的 `n=3` 单元格、能锁定某家企业的精确计数，或未通过 `p`-percent 主导性检查，都可能让个人或机构被重新识别。你应在自己的机器上发现这些问题，而不是等 RDC 分析师发出拒信。

## 何时使用

- **在从** Census FSRDC / 安全数据飞地 / RDC **申请导出之前。**
- **在把**受限数据结果**存放到** openICPSR、某份期刊，或飞地之外的某位共同作者之前。
- **在共享任何**源自机密微观数据的图、表或日志**之前。**
- **作为发布门禁。**在提交前／存放前调用，确保受限数据产出未经预筛就不会出库。这是任何受限数据项目数据管理计划的基础。

## 输入

从 `$ARGUMENTS` 解析位置参数与选项，分别赋给有名称的变量，不要读取 shell 的位置参数：

- 唯一可选的位置参数赋给 `outputs_dir`，默认是各语言流水线共用的 `output/`。若它不存在，但存在 v2.6 之前的 `scripts/<lang>/_outputs/`，则扫描后者并说明。也接受任何导出暂存目录，例如分析师为 RDC 准备的 `to_review/`。解析后校验目录存在且可读，并拒绝额外位置参数。
- `--provider` 的下一个参数赋给 `provider`，选择 Phase 0 加载的披露规则画像；只接受 `census` / `irs` / `irb` / `generic`。**各提供方的阈值与规则不能互换**；默认 `generic` 刻意采用保守规则。
- `--threshold` 的下一个参数赋给 `threshold`，必须是正整数；它覆盖最小单元格计数，默认 `n<10`。Census FSRDC 对机构常用 10，IRS 与许多 IRB 则不同。始终与提供方的*书面*规则保持一致。

未知选项、选项缺值、非法取值或路径校验失败时，停止并报告，不得带着猜测的参数扫描。

## 工作流

### Phase 0：加载提供方的披露规则

1. 阅读 [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md)，取得本项目的受限数据处理契约与规则画像占位。
2. 加载 `--provider` 画像。这是一份**占位配置**，fork 者必须依据自己的*已签*协议填写；Census、IRS 与 IRB 的规则不同，书面协议覆盖这里的所有默认值：
   - **最小单元格计数**（默认 `n<10`），
   - **主导性规则**：`p`-percent（最大应答者贡献超过总量的 `p`% 时，该单元格不安全）与 `(n,k)`（前 `n` 个单位超过总量的 `k`%），
   - 敏感统计量（计数、合计、比率）所需的**取整**，
   - 极端值的**顶编码 / 底编码**阈值，
   - 任何带地理编码统计量的**地理**最小人口。
3. 若已签规则没有记录相应取值，就使用保守的 `generic` 画像，并在报告中**显著标明**这些默认值必须替换为真实提供方阈值。

### Phase 1：扫描产出目录

用 glob 找出产出目录中的 `.tex`、`.csv`、`.txt`、`.log`、`.smcl`、`.out`、`.md` 表格与图数据文件。逐份检查：

- **单元格计数**：解析表格单元格／频数列，标出任何 `0 < n < threshold` 且尚未抑制的计数。
- **互补抑制缺口**：某行／列抑制了一个单元格，但读者仍能用边际合计减去其余单元格反推它时，抑制就**不完整**。
- **主导性**：对任何能获得或推断单位级贡献的合计／均值单元格，应用 `p`-percent 与 `(n,k)` 规则。
- **可重识别的精确计数**：小整数会单独点出某个单位，例如「4 hospitals」「1 firm」，或某个只有一个观测的最大值／最小值。
- **PII 泄漏**：用正则查找姓名、SSN（`\d{3}-\d{2}-\d{4}`）、精确出生日期、地址、精确经纬度或细粒度地理编码，以及残留在产出中的记录 ID。
- **未取整的敏感统计量**：提供方要求取整，但计数／合计仍保留精确值。

### Phase 2：把每条发现分类 —— CRITICAL / WARNING / OK

| 处置 | 含义 | 例子 |
|---|---|---|
| **CRITICAL** | 会过不了提供方的披露审查；阻断发布。 | `n=3` 单元格未抑制；互补抑制漏洞；`p`-percent 主导性失败；任何 PII；能识别出 ≤2 个单位的精确计数。 |
| **WARNING** | 看起来安全，但需要人的判断。 | 单元格恰好落在阈值上；未取整的合计刚超过某个取整基数；地理统计量贴近最小人口下限。 |
| **OK** | 在已加载的规则之内，无需动作。 | 计数 ≥ 阈值且已取整；主导性通过；无 PII。 |

两条发现相互作用时，例如一个单元格被抑制而边际仍可反推它，必须**合并报告**。门禁判断的是联合披露风险，不能孤立看待每个单元格。还要结合研究设计检查常见风险位置，包括按（队列 × 时期）计的 DiD／事件研究单元格计数、IV 第一阶段子样本、RCT 处理臂 × 分层平衡表，以及面板中的企业计数。

### Phase 3：提出补救

对每条 CRITICAL / WARNING，按以下优先顺序建议标准 SDL 修法：

- **抑制**有问题的单元格；若边际允许反推，也抑制它的补格。
- **取整**计数／合计到提供方规定的基数，例如最近的 10 或 15。
- **顶编码 / 底编码**极端值。
- **聚合**稀疏类别、粗化地理或放宽分箱，直到每个单元格都越过阈值。
- 若没有任何补救能同时保住安全与意义，就**丢弃**该统计量。

每条建议都要写明文件、单元格／位置、违反的规则和具体改法，但**不得自动修改**，披露决策由分析师作出。

### Phase 4：门禁

任何 **CRITICAL** 都导致非零退出。WARNING 只提示，不阻断。详见退出行为。

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

- **零 CRITICAL：**退出 0 并打印报告。WARNING 可以存在，只提示，不阻断。
- **任何 CRITICAL：**退出 1，并把摘要写到 stderr，使本技能可以作为发布／存放门禁。这与 [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) 的门禁语义一致：WARNING ≠ FAIL，只有 CRITICAL 阻断。
- **没有加载规则（generic 兜底）：**退出 0，同时给出**显著警告**：未提供真实提供方阈值；预筛已经运行，但使用的是保守默认值，不是实际协议。

## 参数

- `--provider` `<name>` —— 加载数据提供方的披露规则，例如 `census`、`irs`、`irb`。默认使用通用小单元格规则集。
- `--threshold` `<n>` —— 覆盖最小单元格计数阈值（默认 `n<10`）；应与数据使用协议中的实际规则一致。

## 交叉引用

- [`.codebuddy/rules/confidential-data.md`](../../rules/confidential-data.md) —— 受限数据处理契约，以及本技能加载的提供方规则画像。
- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 使用受限数据的论文，其复现包提供代码 + 访问路径，不提供微观数据；每个产出发布前都要预筛。
- [`.codebuddy/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) —— 核验稿件与代码之间的数值：对*保留*的数值运行它，对*发布*的数值运行本技能。
- [`.codebuddy/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md)、[`.codebuddy/skills/stata-replication/SKILL.md`](../stata-replication/SKILL.md) —— 生成供本技能筛查的 R / Stata / Python 输出。
- [AEA Data Editor checklist](https://aeadataeditor.github.io/) 与 [DCAS standard](https://datacodestandard.org/) —— 受限数据存放的披露 + 访问预期（openICPSR 受限访问 stub）。

## 本技能不做的事

- **不替代数据提供方的官方披露审查。**Census/RDC、IRS 与 IRB 的分析师负责权威审查；本技能只**预筛**，提高官方审查一次通过的可能性。这里的 PASS 不是发布许可。
- **不认证规则本身正确。**它应用你从*已签*协议中**加载**的阈值；`--provider` 画像一旦加载错误，扫描结果也会错误。应对齐书面协议，而不是默认值。
- **不搬移、加密或传输数据，也绝不从飞地外泄微观数据。**它只读取你指定的暂存产出。
- **不能保证发现所有披露风险。**跨已发布表格的差分、纵向重识别和基于模型的推断式披露，都可能绕过逐文件扫描。扫描通过是必要条件，不是充分条件。
