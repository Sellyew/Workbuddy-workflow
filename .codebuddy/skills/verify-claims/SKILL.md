---
name: verify-claims
description: 对草稿或一段含事实性论断的文本运行验证链（Chain-of-Verification，CoVe）。在独立上下文中派生 `claim-verifier` 代理（绝不是对话分叉），让它从头到尾看不到草稿 —— 然后报告哪些论断被支持、被反驳，或无法核验。当用户说 "verify these citations"、"check the claims in X"、"did I hallucinate anything"、"fact-check this draft"、"run CoVe on this"，或在任何断言了论文、数据集或数值结果之事实的文本生成之后使用。不用于文风/语法审读（用 `/proofread`）或实质审读（用 `/review-paper`）。
description_zh: 对草稿或一段含事实性论断的文本运行验证链（Chain-of-Verification，CoVe）。在独立上下文中派生 `claim-verifier` 代理（绝不是对话分叉），让它从头到尾看不到草稿 —— 然后报告哪些论断被支持、被反驳，或无法核验。当用户说 "verify these citations"、"check the claims in X"、"did I hallucinate anything"、"fact-check this draft"、"run CoVe on this"，或在任何断言了论文、数据集或数值结果之事实的文本生成之后使用。不用于文风/语法审读（用 `/proofread`）或实质审读（用 `/review-paper`）。
argument-hint: "[file-or-text-path] [--source <path-or-url>] [--no-fail-closed]"
allowed-tools: ["Read", "Grep", "Glob", "Agent", "Task", "Write"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# /verify-claims —— 对草稿做验证链

用**落地后核验协议**（[`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md)）对草稿做事实核查。

**输入：** `$ARGUMENTS` —— 含草稿的文件路径（markdown、.qmd、.tex、.md）或一个简写指针。可选参数：

- `--source <path-or-url>` —— 一个或多个来源材料指针（多个就重复写）。省略时，技能从上下文推断（例如被引用的论文、引用的 arXiv URL）。
- `--no-fail-closed` —— 把 FAIL 结果降级为警告，且不重新生成。慎用。

## 何时选用本技能

- **`/verify-claims`**（本技能）—— 对用户交给你的任何草稿或文本块做临时性事实核查。一次性，由用户调用。
- **其他在内部自动跑落地后核验的技能**（`/lit-review`、`/research-ideation`、`/respond-to-referees`、`/review-paper --peer`）—— 不必单独调用；它们已经跑过了。
- **`/proofread`** —— 语法、错字、溢出。不同的透镜。
- **`/review-paper`**（默认模式）—— 全稿评审，不只是论断核验。
- **`/validate-bib`** —— 检查引文是否*存在*且格式良好（结构 + DOI）。本技能检查它们是否*站得住*（被引的论文支持所归属的论断）。互补 —— 投稿前两个都跑。

## 工作原理

实现 Dhuliawala et al. 2023（[arXiv:2309.11495](https://arxiv.org/abs/2309.11495)）的 4 步 CoVe 循环，并在架构上强制那个独立上下文技巧。

### Phase 0 —— 起飞前检查

确认：
- 草稿文件存在且可读
- 至少有一个来源指针可用（`--source` 指定，或从草稿自动检出）
- `claim-verifier` 代理文件存在于 `.codebuddy/agents/claim-verifier.md`

任一条不满足 → 把失败摆出来，**不要**继续。

### Phase 1 —— 提取论断

读草稿。识别以下类型的事实性断言：

| 类型 | 例子 |
|------|---------|
| 引文 | "Smith (2019, *JEL*) shows X" |
| 数值事实 | "N = 10,000"、"ATT = 0.42" |
| 否定式文献 | "No prior work studies X" |
| 命名实体 | 研究者、论文标题、发表场合、包、估计量名称 |
| 数据集断言 | "The CPS contains field `educ_attain`" |

跳过：观点、前瞻性建议、草稿自己引入的定义。

**对引文类论断，要提取的是论断↔引文的配对 —— 不只是引文。** 记下草稿把*什么*归属给*哪一项工作*，这样核验者检查的是**恰当性**（Smith 2019 是否真的*表明*了 X？），而不只是存在性。「Smith (2019) shows a positive wage effect」变成 `{cite: Smith2019, attributed: "positive wage effect"}`。这正是 `/validate-bib` 明确移交过来的那一层：validate-bib 确认引文*存在且格式良好*；本技能确认它*站得住*。误引（论文存在但说的是别的，或说的正相反）恰恰就是数值/方向性矛盾 → HIGH-WARN，除非记录了一个具体的 `author_alternative`（那才降为 EXPLAINED）。

输出一张论断表：

```markdown
| ID | Claim | Source hint |
|----|-------|-------------|
| C1 | ... | ... |
```

### Phase 2 —— 生成核验问题

每条论断一个问题。要具体，且只凭来源本身就能回答。

### Phase 3 —— 派生 `claim-verifier`（独立上下文 —— 绝不是对话分叉）

```
Agent: subagent_type=claim-verifier   # a named subagent starts fresh; a /fork copy would inherit the draft
Prompt: hand over claims table + verification questions + source material pointers.
        Do NOT include the draft text.
```

被分叉出的代理执行 CoVe 的独立作答步骤。它从未见过草稿，因此无法确认偏误。它返回一份结构化的核验报告。

### Phase 4 —— 对账

核验者按以下严重度层级，给出每条论断的判定：

- **HIGH-WARN** —— 捏造的参考文献（被引论文在所述发表场合/年份并不存在）、草稿断言被来源直接反驳，或核验者把 `not_found` 检索解读为幻觉引文。**失败即闭锁** —— 先摆出这些，且只要有一条还在，就绝不可把草稿当作已核验呈现。这是一条报告规则，不是机械门禁：`/commit` 与 pre-commit 钩子里没有任何东西读这些判定，所以由作者决定，而留下的 HIGH-WARN 会写进用户看到的那份报告里。
- **MED-WARN** —— 临时性基础设施/检索故障（核验者通常能靠缓存元数据绕过的付费墙、DOI 解析超时、PDF 只读了一部分）。摆给作者；不做门禁拒绝。
- **LOW-WARN** —— 来源确实不可访问（有付费墙且不在缓存里、私有数据集、预印本服务器临时故障）。带 `cannot-verify` 标记摆出；不做门禁拒绝。
- **EXPLAINED**（v2.0）—— 作者已用一个具体的具名替代解释*事先辩明*的数值/方向性矛盾（不同但站得住脚的版本、设定、样本或取整惯例），经论断的 `author_alternative` 字段传给核验者。连同证据与记录下的理由一起摆出；**不设门禁**。硬底线仍在：*捏造*的引文永远不是 EXPLAINED，空泛/含糊的替代解释仍是 HIGH-WARN。这与 `audit-reproducibility` 对数值论断的 EXPLAINED 处置一致 —— 当有站得住脚的替代解释被点名时，不匹配并不总是失败。

按层级对全部已提取论断汇总判定（EXPLAINED 与 LOW 一样，算作不设门禁）：

| 层级计数 | 结果 | 报告怎么写 |
|---|---|---|
| 0 HIGH，0 MED，≥ 0 LOW/EXPLAINED | **PASS**（绿色块） | 草稿已核验 |
| 0 HIGH，≥ 1 MED，任意 LOW/EXPLAINED | **PARTIAL**（黄色块） | 已核验，但有警告 |
| ≥ 1 HIGH | **FAIL**（红色块） | 只要 HIGH-WARN 还在，**绝不报为已核验**（除非 `--no-fail-closed`） |

`--no-fail-closed` 把 HIGH-WARN 判定当作普通警告报告，而不是失败闭锁。慎用 —— 它是为离线 / 对幻觉敏感、且用户以书面形式接受风险的场合准备的。

若草稿可写、且用户要求自动更正，用核验者的证据重新生成受影响章节。否则返回报告，让用户决定。

## 示例

```
/verify-claims quality_reports/lit-review_measurement-error.md --source master_supporting_docs/author_2021_method.pdf --source master_supporting_docs/coauthor_2020_survey.pdf
```

预期输出（节选）：

```markdown
## Post-Flight Verification — lit-review_measurement-error.md

**Claims extracted:** 14
**Verified independently:** 14 (fresh-context claim-verifier)
**Outcome:** FAIL — 12 verified, 1 contradicted by its source (HIGH-WARN), 1 unverifiable (LOW-WARN); the draft is not reported as verified until C7 is corrected

### Discrepancies

- **C7** — draft claims "Coauthor (2020) *proposes* a bias-corrected estimator." Source Section 4 shows they propose a weighting estimator, not a bias-corrected one. Recommend correction.

### Unverifiable

- **C12** — draft cites "Third Author et al. 2024 (working paper)". No canonical URL in provided sources. Recommend user supply DOI or arXiv link.

### Verified

| ID | Claim | Evidence |
|----|-------|----------|
| C1 | "Author 2021 defines the calibration constant as a ratio of moments" | p. 5, eq. (3) |
| ... | ... | ... |
```

## 失败模式与恢复

**核验者超时：** 摆出一个警告块，把草稿作为暂定结果返回。不要悄悄交付。

**来源材料不可访问**（付费墙、404）：报告依赖它的那些具体论断，标为 `cannot-verify`，建议用户提供替代来源。

**草稿只含观点 / 前瞻性文字：** 报告「no verifiable factual claims extracted — nothing to check」并返回。

## 交叉引用

- [`.codebuddy/agents/claim-verifier.md`](../../agents/claim-verifier.md) —— 独立上下文的核验者。
- [`.codebuddy/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) —— 该协议。
- MEMORY.md 中关于 Chain-of-Verification 与 critic-fixer、跨产物审读之别的那条 `[LEARN:pattern]`。
