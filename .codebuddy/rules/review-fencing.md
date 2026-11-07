---
paths:
  # DISPATCH-TIME. Fencing is decided when a reviewer is pointed at an
  # artifact, not when a skill is written, so the rule is scoped to the
  # artifacts and answer keys a fenced run touches — the session that runs
  # `/review-paper --peer` on a manuscript is the one that must read this.
  - "*.tex"
  - "*.qmd"
  - "master_supporting_docs/**"
  - "quality_reports/qualification/**"
  - "quality_reports/passports/**"
  - "quality_reports/replication-log.md"
  - "quality_reports/spec-ledger.md"
  - "quality_reports/audits/**"
  - "quality_reports/oracle_audits/**"
  # AUTHORING-TIME, one file: the input contract that already implements the
  # fence. A skill that grows a real fencing step joins this list AND the
  # RULE_KEYWORDS registry in scripts/check-skill-integrity.py, so the
  # rule-vs-implementation gate can see it.
  - ".codebuddy/agents/claim-verifier.md"
---

# 审读隔离——独立性是环境的属性

**审读者的盲区，只等于它的工作目录。**
[`verification-ladder.md`](../references/verification-ladder.md) 第 3 级提供三种保持审读独立的方法：让批评者与修复者形成角色张力、跨产物遍历，以及使用 CoVe 的独立上下文核验器。这三者都只影响**上下文**，不会改变审读者能够访问的文件系统。即使独立上下文中的审稿人从未接触先前对话，它仍能访问当前仓库检出，包括上一轮审稿报告、裁判判定、记录论文各项数值断言的护照，以及标记当前渲染构建来源的戳记。

如果代理能够用 `grep` 搜到答案，只在提示中要求它「独立审读」并不能保证独立。这种做法只是把独立性寄托在代理自觉遵守要求上。

> **这条规则：**派发一个对独立性至关重要的审读者之前，先检查它的*环境*可能泄露哪些信息，然后移除这些信息，不要只指示它不要查看。

**这条规则在哪里加载。**隔离是*派发时*的义务，因此，上面的 `paths:` 指向隔离运行会接触的稿件、资格台账、护照、复现日志、设定日志和审计报告。在 `manuscript.tex` 上派发审稿人的会话，就必须作出这项判断。本规则刻意**不**声称覆盖每个 `SKILL.md`，因为一条约束所有技能却没有技能实现的规则无法执行，`scripts/check-skill-integrity.py` 第 5 项检查也会让这种结构直接失败。某个技能真正实现隔离步骤后，必须把它同时加入 `paths:` 和该脚本的 `RULE_KEYWORDS`，让规则声明与实现相互校验。

## 中立副本

对独立性至关重要的审读者，只能收到**位于仓库检出之外的副本**。副本可以放在会话草稿区或工作树之外的任何目录，必须使用**中立文件名**，并确保审读者没有仓库访问权。

中立文件名不能透露判定。不要使用 `paper_round3_after_referee_fixes.tex` 或 `protocol_final_v2.md`，使用 `artifact-a.tex` 即可。文件名如果标明当前轮次，就已经向审读者泄露了上一轮的信息。

只要接下来会把审读输出与其他内容**比对**，就必须隔离环境：

| 隔离环境 | 仓库内审读即可 |
|---|---|
| 校准与冷读通读——*一位冷眼看到它的读者会得出什么结论？* | 产物自身的工作审读循环，那里仓库上下文**正是**要点 |
| 意在印证第一位意见的第二意见审读者 | 跨产物遍历——论文 → 表格 → 输出 → 脚本**需要**整棵树 |
| 任何被打分对照他人发现的审读者，或对照预先埋入缺陷集的审读者 | 确定性门禁——脚本没有可被带偏的印象 |
| 外部模型咨询（本身已是副本——名字同样保持中立） | 应用批评者已确认发现的修复者 |

这里区分的不是审读是否重要，而是**接下来是否要进行比对**。**两位审读者如果都读过第一位审读者的报告，就不能再算两位独立审读者。**把两者的意见平均，只会制造一致，不会发现真正的一致。

## 隔离买不到什么

**隔离可以让证据独立，但不能让错误独立。**两位隔离的审读者使用同一个模型查看同一份产物时，会共享同一个先验，包括同样的盲点、误读和自信的错误答案。分开会话并不能消除这些共性。因此，他们达成一致，比两位真正独立的读者达成一致更弱；隔离反而可能让这种一致*看起来*更有说服力。

由此得到三条结论：

- **改变真正影响错误的因素。**更换模型、透镜、角色或人类读者，才能获得独立性。用同一套配置再开一个会话，通常只是从同一分布中再取一个样本。N 次完全相同的隔离运行，测量的是审读者的方差，不是产物的正确性。
- **一致说明稳定，分歧提供信号。**同一模型达成一致，说明这种读法可以复现，不能说明它正确；分歧往往包含更多信息。
- **绝不能把同一模型的一致意见当作印证。**
  [`../references/external-oracle-process.md`](../references/external-oracle-process.md) 对外部裁判也提出同样警告：*一致不是确认；两个模型会在同一个错误答案上相关*。隔离环境不会削弱这条警告。一道机械检查比任意多位意见一致的审读者更有证明力。

这些限制都不能成为跳过隔离的理由。未隔离的审读者既存在相关错误，*又*读过答案；隔离至少能消除后一个问题。

## 先前的判定不得入内

先前的审稿报告、裁判判定、裁定表和上一轮质量报告都**不得**进入审读者的会话，除非协议有意提供。协议如果有意提供，就必须在运行前以书面形式说明。

R&R 续审是经批准的例外。[`/review-paper`](../skills/review-paper/SKILL.md) 在 `--peer --r2` / `--r3` 模式下会重新加载上一轮报告，并刻意复用同一批审稿人和审稿取向。此时，任务已经从*「这篇站得住吗？」*变为*「先前的每条关切是否都解决了？」*，没有历史信息就无法完成。与该任务无关的所有信息仍须隔离。

**有意提供必须公开声明。**协议如果只是把报告留在审读者能够找到的位置，就不是有意提供，而是在泄露信息。

## 先形成自己的读法

审读者必须先形成并**记录**自己的读法，然后才能查看计划、修订说明、作者回复或变更日志。它应先判断那里*应该*有什么，再了解作者承诺了什么，否则评估的就是文本是否符合承诺，而不是内容是否充分（[`verification-ladder.md`](../references/verification-ladder.md) 第 3 级）。

阅读顺序本身就是这项机制的核心。同样两份文档只要交换顺序，审读者就可能只会核对并打勾。

## 隔离正对照

**已提交的期望值就是答案。**要求代理复现一个固定数字之前，必须先确认代理无法从所在环境读取这个固定值。正对照的全部意义就在于验证这种复现。如果代理从受跟踪文件中找到固定数字后再报告，它展示的只是 `grep`，不是复现。原本用于认定检查资格的对照，也会因此以错误的理由通过。核验必须**重新推导，而不是重新询问**（[`research-agent-laws.md`](../references/research-agent-laws.md) 法则 1）。

本模板自身提交了五份答案：

| 答案 | 固定了什么 |
|---|---|
| `quality_reports/passports/<paper-slug>.yaml` | 每条已核验数值断言的期望值（[`replication-protocol.md`](replication-protocol.md)） |
| `quality_reports/replication-log.md` | 每条已审计断言被报告的值与计算出的值，以及计算它的那个确切访问器（[`/audit-reproducibility`](../skills/audit-reproducibility/SKILL.md)） |
| `quality_reports/spec-ledger.md` | 每次运行设定的估计值，当其可选的 `Estimate` 单元格被填写时（[`/data-analysis`](../skills/data-analysis/SKILL.md)） |
| `.render-stamp` | 当前渲染必须匹配的源与输出指纹 |
| `quality_reports/qualification/LEDGER.md` | 某次资格认定运行埋了哪些缺陷，以及检查器对照它们打了多少分 |

项目中其他固定的内容也要加入清单，包括基线清单、容差登记表、期望输出夹具和 golden 文件。然后，要么向代理提供不含这些答案的检出，要么为本次复现准备单独的草稿目录。**未隔离的正对照是一道未经资格认定的检查**（[`verification-ladder.md`](../references/verification-ladder.md) 第 0 级）。

**把隔离方式写入该行的 `Artifact` 单元格。**[`LEDGER.md`](../../quality_reports/qualification/LEDGER.md) 没有单独的隔离字段，本规则也不新增字段。`Artifact` 本来就用于说明「这次运行收到了什么」，可以写*「仓库之外的一份夹具克隆」*、*「用 `HOOK_DIR` 选中的一份钩子目录副本」*或*「合成事件，无仓库访问权」*。在单元格中明确写出隔离方式，这一行就能说明运行是否独立。如果 `Artifact` 只列出被测文件，读者就无法判断是否实施了隔离。

**独立上下文不等于环境隔离。**[`/vaccinate`](../skills/vaccinate/SKILL.md) 通过一次全新的独立 `Agent` 调用盲跑检查器，并对产物的*副本*打分。这只能清空审读者的上下文，不能改变它的工作目录。只要期望值仍提交在树中的任何位置，副本就必须放在**检出之外**，否则子代理仍能读到答案。

## 已经隔离好的部分

模板已经正确隔离了一项输入，本规则只是把这项做法推广到环境。[`claim-verifier`](../agents/claim-verifier.md) 只收到**断言和来源材料指针**，不会收到草稿或生成草稿的推理轨迹。即使调用方误把草稿放进上下文，它也被要求忽略草稿（[`post-flight-verification.md`](post-flight-verification.md)）。这项输入契约实现了环境隔离：核验器手中没有草稿的推理，因此无法直接为其盖章。中立副本则把同样的纪律应用到仓库检出。

## 交叉引用

- [`../references/verification-ladder.md`](../references/verification-ladder.md) — 第 0 级（给检查器做资格认定）、第 3 级（本规则所推广的三种上下文级机制）
- [`post-flight-verification.md`](post-flight-verification.md) — CoVe 协议与独立上下文核验器
- [`../agents/claim-verifier.md`](../agents/claim-verifier.md) — 本规则所推广的输入契约
- [`../references/external-oracle-process.md`](../references/external-oracle-process.md) — 外部咨询：让裁判致盲，核验传输
- [`../skills/vaccinate/SKILL.md`](../skills/vaccinate/SKILL.md) — 埋设缺陷的资格认定，未隔离的答案在那里是致命的
- [`../references/research-agent-laws.md`](../references/research-agent-laws.md) — 法则 1（重新推导，不要重新询问）、法则 13（让裁判致盲）
