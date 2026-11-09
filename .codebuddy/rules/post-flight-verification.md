---
paths:
  - ".codebuddy/skills/lit-review/SKILL.md"
  - ".codebuddy/skills/research-ideation/SKILL.md"
  - ".codebuddy/skills/respond-to-referees/SKILL.md"
  - ".codebuddy/skills/review-paper/SKILL.md"
  - ".codebuddy/skills/interview-me/SKILL.md"
alwaysApply: false
---

# 落地后核验（反幻觉）

落地后核验与**起飞前报告**相互对应。起飞前报告包括技能级的 `## Phase 0`，例如 `/create-lecture`、`/data-analysis`；在扇出流程中，则是 `.codebuddy/rules/orchestrator-protocol.md` §「RUN_CONFIG：在启动*之前*收集交互输入」所回显的 `RUN_CONFIG`。起飞前检查确认系统在动手*之前*已经读取输入，落地后核验确认产出中的事实性断言在起草*之后*仍然成立，然后技能才能把结果交给用户。

**改写自：** Dhuliawala 等，2023，"Chain-of-Verification Reduces Hallucination in Large Language Models"（[arXiv:2309.11495](https://arxiv.org/abs/2309.11495)）。**独立性技巧**要求在不包含原始草稿的上下文中回答核验问题，本规则通过架构强制执行这一点：`claim-verifier` 作为一次独立的 `Agent` 调用运行，并从独立上下文启动。它从未见过草稿，因此其核验不是对原草稿判断的自我确认。*对话*分叉，包括 `/fork` 和 fork 模式的子任务，会继承对话并破坏这种独立性；核验绝不能使用分叉。

## 本条规则的适用范围

本规则适用于所有产出包含**可依据来源独立核验的事实性断言**的技能：

| 技能 | 高风险断言类型 |
|-------|----------------------|
| `/lit-review` | 引文（论文存在、作者、年份、发表处）；转述性断言（"Smith 2019 finds X"） |
| `/research-ideation` | 「有人检验过这个吗？」这类否定性文献断言；数据集结构断言；估计量可行性断言 |
| `/respond-to-referees` | 关于实际修订的「我们在第 Y 页加了 X」这类断言 |
| `/review-paper`（`--peer` 模式） | 来自 WebSearch 的新颖性探查断言（「这篇论文的贡献是新的」／「与 Jones 2020 相似」） |
| `/interview-me` | 研究需求说明中提到的论文（如果有引用） |

本规则**不**适用于机械型技能，包括 `/compile-latex`、`/deploy`、`/extract-tikz`、`/commit`。这些技能的产出是编译结果，应由编译器等外部过程核验，而不是作为事实性文字核验。

## 四步 CoVe 协议

### Step 1 — 起草（技能正常的产出生成）

照常生成响应。即使草稿看似「显然正确」，也不能跳过落地后核验。

### Step 2 — 抽取断言

从草稿中找出每一个形如以下的断言：

- **引文断言：** "Author (Year) shows X."
- **存在性断言：** "A dataset called X contains Y fields."
- **数值事实：** "N = 10,000" / "coefficient = 0.42" / "p < 0.01"
- **命名实体：** 研究者姓名、论文标题、发表处、包名
- **否定性文献断言：** "No prior work studies X."

跳过：
- **意见**，例如「这是一个有前景的方向」，因为无法核验。
- **建议**，例如「用户可以试试对数设定」，因为它面向未来。
- **WorkBuddy 自己引入的定义**，例如「令 τ 表示处理效应」。

### Step 3 — 生成核验问题

为每条抽取出的断言写一个具体、可回答的问题。仅凭来源材料，问题的答案就必须能够确认或反驳该断言。好问题会明确点名来源，坏问题则过于开放。

| 坏问题 | 好问题 |
|-------------|--------------|
| 「Author (2021) 讲的是校准吗？」 | 「在 Author (2021) 中，第 4 节给出的估计量准确名称是什么？」 |
| 「这个估计量需要正则条件吗？」 | 「Author (2021) 第 4 节假设 2 要求的是单调响应，还是只要求连续？」 |

### Step 4 — 在独立上下文中作答，然后对账

使用 `Agent` 工具并设置 `subagent_type=claim-verifier`，调用 `claim-verifier`。这个具名子代理从**独立上下文**启动。**不要**使用 `/fork` 或 fork 模式的子任务等对话分叉，因为它们会连同草稿一起继承对话，破坏 CoVe 所依赖的独立性。交给子代理的内容只包括断言、核验问题和来源材料指针，**不要包含草稿。**

核验报告有三种结果：

- **PASS**：没有断言被推翻，也没有检索失败。返回草稿；如果某些断言的来源确实无法访问，即 LOW-WARN、`cannot-verify`，就在相应位置标记不确定性，提醒用户复核。
- **PARTIAL**：发生一次暂时性检索失败，即 MED-WARN，且没有矛盾。返回草稿，并把这些断言标为待复查。
- **FAIL**：至少一条断言与来源矛盾，或某条引文看似编造，即 HIGH-WARN。根据核验者提供的证据，**重新生成受影响的章节**。重试 2 次后仍然失败时，返回最好的草稿版本，并用警告块明确列出所有不一致之处，不能悄悄发布已知错误的断言。

## 输出契约

每个适用本规则的技能，都必须在响应中包含结构化的落地后核验块。该块可以由用户折叠，并按需显示：

```markdown
## Post-Flight Verification

**Claims extracted:** N
**Verified independently:** N (fresh-context `claim-verifier` agent)
**Outcome:** PASS | PARTIAL | FAIL → regenerated

### Verified

| ID | Claim | Evidence |
|----|-------|----------|
| C1 | [claim] | [source + loc] |

### Unverifiable (user review recommended)

- **C4** — [reason, e.g., paywalled source]

### Discrepancies (regenerated)

- **C3** — original draft: "N = 10,000"; source shows: "N = 1,000". Corrected in final response.
```

## 失败即关闭语义

- 如果核验代理报错、返回畸形输出或超时，**不要悄悄发布草稿。**必须显示以下提示：
  > 「落地后核验失败（核验器错误：…）。草稿未经独立检查。请把输出视为暂定。」
- 这与起飞前检查的失败即关闭契约相对应。流程开始出错时，幻觉防线最有价值；此时静默失败的代价也最高。

## 退出选项

在 `/lit-review`、`/research-ideation`、`/respond-to-referees` 和 `/interview-me` 中，`--no-verify` 标志会跳过落地后核验。它适用于对速度敏感的迭代，或用户本人正在阅读来源材料的情况。每个技能的参数提示都必须写明这个退出选项。`/review-paper` 是例外：它没有 `--no-verify`，而是通过 `--no-novelty-check` 直接跳过新颖性探查。只要运行了探查，就必须执行落地后核验。

## 交叉引用

- `.codebuddy/agents/claim-verifier.md` —— 独立上下文的核验器。
- `.codebuddy/rules/review-fencing.md` —— 同一纪律的环境一侧：独立上下文并不能把审读者所站的检出围栏起来。
- `.codebuddy/skills/verify-claims/SKILL.md` —— 面向用户的包装，用于对任意文本做临时核验。
- `.codebuddy/rules/orchestrator-protocol.md` —— 起飞前检查（输入一侧）：`RUN_CONFIG` 的起飞前报告，以及各技能的 `## Phase 0` 起飞前报告。
- `.codebuddy/rules/cross-artifact-review.md` —— 基于模式；落地后核验基于草稿。
- `.codebuddy/rules/summary-parity.md` —— 反对枚举式摘要与其正文漂移的规则；落地后核验是草稿内容上的事实等价物。
