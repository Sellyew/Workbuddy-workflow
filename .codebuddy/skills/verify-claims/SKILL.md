---
name: verify-claims
description: 对草稿或包含事实论断的文本运行验证链（Chain-of-Verification，CoVe）。在独立上下文中启动 `claim-verifier` 代理，绝不使用对话分叉，并确保它始终看不到草稿，然后报告哪些论断得到支持、被反驳或无法核验。用户说 "verify these citations"、"check the claims in X"、"did I hallucinate anything"、"fact-check this draft"、"run CoVe on this"、"核验这些引文"、"检查这篇草稿的事实" 或 "看看有没有编造内容" 时使用，也可在生成任何涉及论文、数据集或数值结果的事实话语后使用。不用于文风或语法审读（用 `/proofread`），也不用于实质审读（用 `/review-paper`）。
description_zh: 对草稿或包含事实论断的文本运行验证链（Chain-of-Verification，CoVe）。在独立上下文中启动 `claim-verifier` 代理，绝不使用对话分叉，并确保它始终看不到草稿，然后报告哪些论断得到支持、被反驳或无法核验。用户说 "verify these citations"、"check the claims in X"、"did I hallucinate anything"、"fact-check this draft"、"run CoVe on this"、"核验这些引文"、"检查这篇草稿的事实" 或 "看看有没有编造内容" 时使用，也可在生成任何涉及论文、数据集或数值结果的事实话语后使用。不用于文风或语法审读（用 `/proofread`），也不用于实质审读（用 `/review-paper`）。
argument-hint: "[file-or-text-path] [--source <path-or-url>] [--no-fail-closed]"
allowed-tools: ["Read", "Grep", "Glob", "Agent", "Task", "Write"]
---

# /verify-claims —— 对草稿做验证链

使用**落地后核验协议**（[`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md)）核查草稿中的事实。

**输入：** `$ARGUMENTS`，即包含草稿的文件路径（markdown、.qmd、.tex、.md）或一个简写指针。可选参数：

- `--source <path-or-url>`：一个或多个来源材料指针，多个来源需重复写此参数。省略时，技能从上下文推断，例如被引用的论文或 arXiv URL。
- `--no-fail-closed`：只改变交付和自动修复策略，不改变 PASS / PARTIAL / FAIL 判定；未解决 HIGH 仍为 FAIL，绝不能把草稿改称“已核验”。慎用。

## 何时选用本技能

- **`/verify-claims`**（本技能）：对用户提供的任何草稿或文本块做一次临时事实核查，由用户显式调用。
- **其他在内部自动运行落地后核验的技能**（`/lit-review`、`/research-ideation`、`/respond-to-referees`、`/review-paper --peer`）：无需单独调用，因为它们已经执行核验。
- **`/proofread`**：检查语法、错字和溢出，使用不同的检查视角。
- **`/review-paper`**（默认模式）：评审全稿，不只核验论断。
- **`/validate-bib`**：检查引文是否存在且格式良好，包括结构和 DOI；本技能检查引文是否支持归属给它的论断。两者互补，投稿前都应运行。

## 工作原理

实现 Dhuliawala et al. 2023（[arXiv:2309.11495](https://arxiv.org/abs/2309.11495)）的 4 步 CoVe 循环，并通过架构强制执行独立上下文要求。

### Phase 0 —— 起飞前检查

确认：

- 草稿文件存在且可读
- 至少有一个来源指针可用，可由 `--source` 指定或从草稿自动检出
- `claim-verifier` 代理文件存在于 `.codebuddy/agents/claim-verifier.md`

任一条不满足，都要报告失败并**停止**。

### Phase 1 —— 提取论断

阅读草稿，识别以下事实性断言：

| 类型 | 例子 |
|------|---------|
| 引文 | "Smith (2019, *JEL*) shows X" |
| 数值事实 | "N = 10,000"、"ATT = 0.42" |
| 否定式文献 | "No prior work studies X" |
| 命名实体 | 研究者、论文标题、发表场合、包、估计量名称 |
| 数据集断言 | "The CPS contains field `educ_attain`" |

跳过观点、前瞻性建议和草稿自己引入的定义。

**对引文类论断，要提取论断与引文的配对，而不只是引文。** 记录草稿把什么论断归属给哪项工作，让核验者检查归属是否恰当，例如 Smith 2019 是否真的表明 X，而不只是检查论文是否存在。「Smith (2019) shows a positive wage effect」应转成 `{cite: Smith2019, attributed: "positive wage effect"}`。这正是 `/validate-bib` 移交过来的层次：validate-bib 确认引文存在且格式良好，本技能确认它支持相应论断。误引指论文存在但内容不同或结论相反，属于数值或方向性矛盾，应记为 HIGH-WARN；只有记录了具体 `author_alternative` 时，才降为 EXPLAINED。

输出一张论断表：

```markdown
| ID | Claim | Source hint |
|----|-------|-------------|
| C1 | ... | ... |
```

### Phase 2 —— 生成核验问题

每条论断对应一个问题。问题必须具体，并且只凭来源本身就能回答。

### Phase 3 —— 派生 `claim-verifier`（独立上下文 —— 绝不是对话分叉）

```
Agent: subagent_type=claim-verifier   # a named subagent starts fresh; a /fork copy would inherit the draft
Prompt: hand over claims table + verification questions + source material pointers.
        Do NOT include the draft text.
```

独立代理执行 CoVe 的独立作答步骤。它从未见过草稿，因此不会受到草稿确认偏误的影响。它返回结构化核验报告。

### Phase 4 —— 对账

核验者按以下严重度为每条论断给出判定：

- **HIGH-WARN**：参考文献系捏造，例如被引论文在所述发表场合或年份不存在；草稿断言被来源直接反驳；或核验者把 `not_found` 检索解读为幻觉引文。**失败即闭锁**：先展示这些问题，只要仍有一条，就绝不能把草稿作为已核验结果呈现。这是报告规则，不是机械门禁；`/commit` 和 pre-commit 钩子都不会读取这些判定，最终由作者决定，但所有遗留 HIGH-WARN 都必须写入用户可见的报告。
- **MED-WARN**：临时性基础设施或检索故障，例如核验者通常可借助缓存元数据绕过的付费墙、DOI 解析超时、PDF 只读取了一部分。向作者展示，但不作门禁拒绝。
- **LOW-WARN**：来源确实不可访问，例如有付费墙且不在缓存中、数据集私有、预印本服务器临时故障。标记 `cannot-verify` 并展示，不作门禁拒绝。
- **EXPLAINED**（v2.0）：作者已经用具体且具名的替代解释，事先说明数值或方向性矛盾，例如不同但合理的版本、设定、样本或取整惯例，并通过论断的 `author_alternative` 字段传给核验者。展示证据和记录的理由，**不设门禁**。但捏造引文永远不能记为 EXPLAINED，空泛或含糊的替代解释仍为 HIGH-WARN。这与 `audit-reproducibility` 对数值论断的 EXPLAINED 处理一致：存在合理且明确的替代解释时，不匹配不一定意味着失败。

对账时除了严重度，还必须分别报告以下数量，不能把它们混写成“已核验数”：

- `reviewed`：独立核验者实际完成审查并返回终态的论断数；每个已审查论断只能归入 `supported`、`contradicted`、`cannot-verify` 或 `EXPLAINED` 之一。
- `supported`：来源证据支持草稿论断的数量。
- `contradicted`：来源或来源记录直接反驳草稿论断的数量。
- `cannot-verify`：已尝试审查但来源不足或不可访问，因而无法判定的数量。
- 另行报告 `EXPLAINED` 和未审查/核验器错误数量；`reviewed` 不等于 `supported`，未完成审查的论断不得计入这四类终态。

EXPLAINED 不触发 FAIL；LOW-WARN 虽不作 FAIL 门禁，但对应 `cannot-verify ≥ 1`，结果至少为 PARTIAL：

| 状态计数 | 结果 | 报告怎么写 |
|---|---|---|
| 全部提取论断均已 reviewed，0 HIGH，0 MED，0 `cannot-verify` | **PASS**（绿色块） | 所有论断均完成核验，未发现未解决矛盾 |
| 0 HIGH，且 ≥ 1 MED、`cannot-verify`、未审查项或核验器错误 | **PARTIAL**（黄色块） | 分别列出四类计数与未完成原因；有 `cannot-verify` 时**不得写“草稿已核验”** |
| ≥ 1 HIGH | **FAIL**（红色块） | 只要 HIGH-WARN 还在，**绝不报为已核验**；`--no-fail-closed` 也不例外 |

`--no-fail-closed` 只控制失败后的交付与自动修复策略：默认遇到 FAIL 不把草稿作为可用结果交付，也不自动修复；使用该选项时，可在用户明确授权后带醒目 FAIL 警告交付，或继续自动修复受影响章节。它**不会**把 HIGH-WARN 降级、不会改变 FAIL / PARTIAL / PASS 判定，也不会把未解决 HIGH 的草稿改称“已核验”。自动修复后的论断必须重新核验，在重新核验解决前仍按未解决处理。该选项只适用于离线、对幻觉敏感且用户以书面形式接受风险的场合，务必慎用。

如果草稿可写、上述交付/自动修复策略允许且用户要求自动更正，根据核验者证据重新生成受影响章节，并重新运行核验。否则只返回报告，由用户决定如何处理。

## 示例

```
/verify-claims quality_reports/lit-review_measurement-error.md --source master_supporting_docs/author_2021_method.pdf --source master_supporting_docs/coauthor_2020_survey.pdf
```

预期输出（节选）：

```markdown
## Post-Flight Verification — lit-review_measurement-error.md

**Claims extracted:** 14
**reviewed:** 14 (fresh-context claim-verifier)
**supported:** 12
**contradicted:** 1 (HIGH-WARN)
**cannot-verify:** 1 (LOW-WARN)
**Outcome:** FAIL — C7 remains unresolved; C12 also remains unverifiable. The draft is not verified, including when `--no-fail-closed` is used.

### Discrepancies

- **C7** — draft claims "Coauthor (2020) *proposes* a bias-corrected estimator." Source Section 4 shows they propose a weighting estimator, not a bias-corrected one. Recommend correction.

### Unverifiable

- **C12** — draft cites "Third Author et al. 2024 (working paper)". No canonical URL in provided sources. Recommend user supply DOI or arXiv link.

### Supported

| ID | Claim | Evidence |
|----|-------|----------|
| C1 | "Author 2021 defines the calibration constant as a ratio of moments" | p. 5, eq. (3) |
| ... | ... | ... |
```

同一示例必须明确报告以下状态迁移，`--no-fail-closed` 不改变其中任何一个状态：

1. **C7 未解决（当前示例）：FAIL。** 即使 C12 仍未解决，也只能在 FAIL 中另列 `cannot-verify`，不能把结果写成 PARTIAL 或“已核验”。
2. **C7 已修正并经重新核验支持，但 C12 仍为 `cannot-verify`：PARTIAL。** 此时为 reviewed 14、supported 13、contradicted 0、cannot-verify 1；仍不得称整篇草稿“已核验”。
3. **C12 随后解决，且全部 14 条均已 reviewed 和 supported，0 HIGH、0 MED、0 `cannot-verify`、0 未审查项、0 核验器错误：才可能 PASS。** 仅仅执行过修正或启用 `--no-fail-closed` 都不足以进入 PASS。

## 失败模式与恢复

**核验者超时：** 显示警告块，结果至少为 PARTIAL；分别报告已完成的 `reviewed` / `supported` / `contradicted` / `cannot-verify` 数量和未审查数量，不得把草稿作为已核验结果交付。

**来源材料不可访问**（付费墙、404）：报告依赖这些来源的具体论断，标记 `cannot-verify`，并建议用户提供替代来源。

**草稿只含观点或前瞻性文字：** 报告「no verifiable factual claims extracted — nothing to check」并返回。

## 交叉引用

- [`.codebuddy/agents/claim-verifier.md`](../../agents/claim-verifier.md)：独立上下文核验者。
- [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md)：核验协议。
- MEMORY.md 中关于 Chain-of-Verification 与 critic-fixer、跨产物审读之别的 `[LEARN:pattern]`。
