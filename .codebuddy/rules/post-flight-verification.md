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

**起飞前报告**的对称伙伴（技能级的 `## Phase 0`，例如 `/create-lecture`、`/data-analysis`；扇出形态则是 `.codebuddy/rules/orchestrator-protocol.md` §「RUN_CONFIG：在启动*之前*收集交互输入」里回显的 `RUN_CONFIG`）。起飞前检查证明输入在动手*之前*已被读过，落地后核验证明产出的事实性断言在起草*之后*成立——在技能把结果交回用户之前。

**改写自：** Dhuliawala 等，2023，"Chain-of-Verification Reduces Hallucination in Large Language Models"（[arXiv:2309.11495](https://arxiv.org/abs/2309.11495)）。**独立性技巧**——在一个不包含原始草稿的上下文中回答核验问题——在这里由架构强制执行：`claim-verifier` 作为自己的一次 `Agent` 调用运行，从独立上下文启动。它在字面意义上无法自我确认；它从没见过草稿。（*对话*分叉——`/fork`、一个 fork 模式的子任务——会继承对话，从而毁掉这一点；核验永远不要用分叉。）

## 本条规则的适用范围

任何产出中包含**可对着来源独立核验的事实性断言**的技能：

| 技能 | 高风险断言类型 |
|-------|----------------------|
| `/lit-review` | 引文（论文存在、作者、年份、发表处）；转述性断言（"Smith 2019 finds X"） |
| `/research-ideation` | 「有人检验过这个吗？」这类否定性文献断言；数据集结构断言；估计量可行性断言 |
| `/respond-to-referees` | 关于实际修订的「我们在第 Y 页加了 X」这类断言 |
| `/review-paper`（`--peer` 模式） | 来自 WebSearch 的新颖性探查断言（「这篇论文的贡献是新的」／「与 Jones 2020 相似」） |
| `/interview-me` | 研究规格中提到的论文（如果有引用） |

**不**适用于机械型技能（`/compile-latex`、`/deploy`、`/extract-tikz`、`/commit`）——它们的产出是编译结果，由外部过程（编译器）核验，而不是事实性文字。

## 四步 CoVe 协议

### Step 1 — 起草（技能正常的产出生成）

照常产出响应。即使草稿「显然正确」，也不要短路落地后核验。

### Step 2 — 抽取断言

从草稿中找出每一个形如以下的断言：

- **引文断言：** "Author (Year) shows X."
- **存在性断言：** "A dataset called X contains Y fields."
- **数值事实：** "N = 10,000" / "coefficient = 0.42" / "p < 0.01"
- **命名实体：** 研究者姓名、论文标题、发表处、包名
- **否定性文献断言：** "No prior work studies X."

跳过：
- **意见**（「这是一个有前景的方向」）—— 不可核验
- **建议**（「用户可以试试对数设定」）—— 面向未来
- **Claude 自己引入的定义**（「令 τ 表示处理效应」）

### Step 3 — 生成核验问题

为每条抽出的断言写一个具体、可回答的问题，其答案仅凭来源材料就能确认或反驳该断言。好问题明确点名来源。坏问题是开放式的。

| 坏问题 | 好问题 |
|-------------|--------------|
| 「Author (2021) 讲的是校准吗？」 | 「在 Author (2021) 中，第 4 节给出的估计量准确名称是什么？」 |
| 「这个估计量需要正则条件吗？」 | 「Author (2021) 第 4 节假设 2 要求的是单调响应，还是只要求连续？」 |

### Step 4 — 在独立上下文中作答，然后对账

通过 `Agent` 工具以 `subagent_type=claim-verifier` 生成 `claim-verifier`——具名子代理从**独立上下文**启动。**不要**使用对话分叉（`/fork`、fork 模式的子任务）：分叉会继承对话，连草稿一起继承，这会毁掉 CoVe 所依赖的独立性。交给它：断言、核验问题、来源材料指针。**不要包含草稿。**

收到一份核验报告。三种结果：

- **PASS**（没有断言被推翻，没有检索失败）：返回草稿；任何来源确实无法访问的断言（LOW-WARN、`cannot-verify`）带一个行内不确定标记，让用户知道要复核它。
- **PARTIAL**（一次暂时性检索失败——MED-WARN——且无矛盾）：返回草稿，并把这些断言标记为待复查。
- **FAIL**（至少一条断言与来源矛盾，或某条引文看起来是编造的——HIGH-WARN）：用核验者给出的证据**重新生成受影响的章节**。如果重试 2 次后仍失败，返回最好的那一版草稿，并把不一致之处以警告块的形式摆出来——不要把一条已知错误的断言悄悄发出去。

## 输出契约

每个适用本条规则的技能都必须在其响应中包含一个结构化的落地后核验块（用户可折叠；按需可见）：

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

- 如果核验代理报错、返回畸形输出或超时，**不要悄悄把草稿发出去。** 摆出这样一个块：
  > 「落地后核验失败（核验器错误：…）。草稿未经独立检查。请把输出视为暂定。」
- 这与起飞前检查的失败即关闭契约对称。幻觉防线恰恰在事情开始跑偏的时候最有价值——那正是静默失败最昂贵的时刻。

## 退出选项

`--no-verify` 标志在 `/lit-review`、`/research-ideation`、`/respond-to-referees` 和 `/interview-me` 中跳过落地后核验。适用于对速度敏感的迭代，或用户本人正在读来源材料的时候。要在每个技能的参数提示里写明这个退出选项。例外：`/review-paper` 没有 `--no-verify`；它的退出选项是 `--no-novelty-check`，直接跳过新颖性探查。只要探查跑了，落地后核验就是强制的。

## 交叉引用

- `.codebuddy/agents/claim-verifier.md` —— 独立上下文的核验器。
- `.codebuddy/rules/review-fencing.md` —— 同一纪律的环境一侧：独立上下文并不能把审读者所站的检出围栏起来。
- `.codebuddy/skills/verify-claims/SKILL.md` —— 面向用户的包装，用于对任意文本做临时核验。
- `.codebuddy/rules/orchestrator-protocol.md` —— 起飞前检查（输入一侧）：`RUN_CONFIG` 的起飞前报告，以及各技能的 `## Phase 0` 起飞前报告。
- `.codebuddy/rules/cross-artifact-review.md` —— 基于模式；落地后核验基于草稿。
- `.codebuddy/rules/summary-parity.md` —— 反对枚举式摘要与其正文漂移的规则；落地后核验是草稿内容上的事实等价物。
