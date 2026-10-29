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
[`verification-ladder.md`](../references/verification-ladder.md) 的第 3 级给了三种让审读者独立的办法——批评者/修复者的角色张力、跨产物遍历、以及 CoVe 的独立上下文核验器——三者都作用在**上下文**上。没有一个触及审读者脚下站着的文件系统。一位上下文一尘不染的独立上下文审稿人，手里仍然握着那份仓库检出，而那份检出里有上一轮的审稿报告、裁判的判定、记录论文所声称每一个数字的护照，以及记录当前渲染由什么构建出来的戳记。

在一个能 `grep` 出答案的代理身上提示「独立审读这份东西」，那不是独立。那是一套配了搜索工具的荣誉制。

> **这条规则：** 在派出一个对独立性至关重要的审读者之前，先问它的*环境*若去看会泄露什么——然后把那东西移走，而不是指示它别看。

**这条规则在哪里加载。** 隔离是*派发时*的义务，所以上面的 `paths:` 点名的是被隔离运行所指向的稿件、资格台账、护照、复现日志与设定日志，以及审计报告——在 `manuscript.tex` 上派发审稿人的那次会话，就是要做这个判断的那次。它刻意**不**声称覆盖每个 `SKILL.md`：一条约束所有技能、却没有一个技能实现它的规则，是一项无人执行的义务，而 `scripts/check-skill-integrity.py`（第 5 项检查）现在恰好会因为这种形状而失败。当某个技能长出了真正的隔离步骤，就把它加进 `paths:` **并**加进该脚本的 `RULE_KEYWORDS`，让声称与实现互相校验，而不是各自断言。

## 中立副本

对独立性至关重要的审读者，收到的是**放在仓库检出之外的副本**——会话草稿区，或工作树之外的任何目录——用**中立文件名**，且没有仓库访问权。

中立是指名字不携带判定：不是 `paper_round3_after_referee_fixes.tex`，不是 `protocol_final_v2.md`——`artifact-a.tex` 就够了。一个宣告自己是第几轮的文件名，已经告诉审读者上轮查出了什么。

只要审读者的输出即将被拿去与某物**比对**，隔离就有必要：

| 隔离环境 | 仓库内审读即可 |
|---|---|
| 校准与冷读通读——*一位冷眼看到它的读者会得出什么结论？* | 产物自身的工作审读循环，那里仓库上下文**正是**要点 |
| 意在印证第一位意见的第二意见审读者 | 跨产物遍历——论文 → 表格 → 输出 → 脚本**需要**整棵树 |
| 任何被打分对照他人发现的审读者，或对照预先埋入缺陷集的审读者 | 确定性门禁——脚本没有可被带偏的印象 |
| 外部模型咨询（本身已是副本——名字同样保持中立） | 应用批评者已确认发现的修复者 |

这个区分不是「重要审读对不重要审读」。它是「接下来有没有一次比对」。**两位都读过第一位报告的审读者，就是一位审读者**，把两者平均，报告出来的是被制造出来的一致，而不是被找出来的一致。

## 隔离买不到什么

**隔离让证据独立。它不让错误独立。** 两位被隔离的审读者用同一个模型看同一份产物，共享同一个先验——同样的盲点、同样的误读、同样自信的错误答案——而分开的会话并不能把它们分开。所以他们的一致，比两位独立读者的一致是更弱的证据；而隔离恰恰让这种一致*看起来*更强。

三条值得记住的后果：

- **去变那个真正能让错误变化的量。** 换模型、换透镜或角色、或换人类读者，才买得到独立性；同一套配置再开一个会话，多半只是买到同一分布的第二个样本。N 次完全相同的隔离运行，测的是审读者的方差，不是产物的正确性。
- **把一致读作稳定性，把分歧读作信号。** 同模型的一致说明这个读法可复现。它不说明它是对的，而分歧才是信息量大的那一半。
- **绝不把同模型的一致当作印证。**
  [`../references/external-oracle-process.md`](../references/external-oracle-process.md) 就外部裁判说过这一点——*一致不是确认；两个模型会在同一个错误答案上相关*——这条告诫在隔离之内并不减弱。一道机械检查压过任意多位意见一致的审读者。

以上没有一条是跳过隔离的理由。未隔离的审读者，错误是相关的，*而且*它读过答案；隔离去掉了两者之一。

## 先前的判定不得入内

先前的审稿报告、裁判判定、裁定表、以及上一轮的质量报告，都**不得**进入审读者的会话，除非协议有意喂给它——而有意喂的协议，会在运行之前以书面形式说明。

被批准的例外是 R&R 续审。[`/review-paper`](../skills/review-paper/SKILL.md) 在 `--peer --r2` / `--r3` 模式下重载上一轮报告、并刻意复用同一批审稿人与审稿取向，因为问题已经从*「这篇站得住吗？」*变成*「先前的每条关切是否都被解决了？」*——这个任务离开历史做不了。不属于该任务的一切，仍然隔离。

**有意就意味着公开声明。** 一个只是把报告留在审读者能找到的地方的协议，不是有意喂给它，而是泄露给它。

## 先形成自己的读法

审读者在被展示计划、修订说明、作者回复或变更日志之前，先形成并**记录**自己的读法。让它先判断那里*应该*有什么，再去知道承诺了什么，否则它评的是符合度，而不是充分性（[`verification-ladder.md`](../references/verification-ladder.md) 第 3 级）。

顺序就是全部机制。同样两份文档换个顺序，产出的就是一个只会打勾的审读者。

## 隔离正对照

**一个已提交的期望值就是答案。** 在要求代理复现一个被固定下来的数字之前——那正是正对照的全部意义——先确认从代理所站的位置读不到这个固定值。一个在受跟踪文件里找到固定数字再报出来的代理，展示的是 `grep`，不是复现；而那道本该用来给检查做资格认定的对照，现在因为错误的理由显示为绿。用**重新推导，而不是重新询问**来核验（[`research-agent-laws.md`](../references/research-agent-laws.md) 法则 1）。

本模板自己就提交了五份答案：

| 答案 | 固定了什么 |
|---|---|
| `quality_reports/passports/<paper-slug>.yaml` | 每条已核验数值断言的期望值（[`replication-protocol.md`](replication-protocol.md)） |
| `quality_reports/replication-log.md` | 每条已审计断言被报告的值与计算出的值，以及计算它的那个确切访问器（[`/audit-reproducibility`](../skills/audit-reproducibility/SKILL.md)） |
| `quality_reports/spec-ledger.md` | 每次运行设定的估计值，当其可选的 `Estimate` 单元格被填写时（[`/data-analysis`](../skills/data-analysis/SKILL.md)） |
| `.render-stamp` | 当前渲染必须匹配的源与输出指纹 |
| `quality_reports/qualification/LEDGER.md` | 某次资格认定运行埋了哪些缺陷，以及检查器对照它们打了多少分 |

把你项目里另外固定的东西也补上：基线清单、容差登记表、期望输出夹具、golden 文件。然后要么交给代理一份不含它们的检出，要么给这次复现一个自己的草稿目录。**未隔离的正对照是一道没做资格认定的检查**（[`verification-ladder.md`](../references/verification-ladder.md) 第 0 级）。

**把隔离写进该行的 `Artifact` 单元格。** [`LEDGER.md`](../../quality_reports/qualification/LEDGER.md) 没有单独的隔离字段，本规则也不去发明一个：`Artifact` 就是那列本来就在说明「这次运行被交了什么」的字段——*「仓库之外的一份夹具克隆」*、*「用 `HOOK_DIR` 选中的一份钩子目录副本」*、*「合成事件，无仓库访问权」*。用这样的话把隔离写在那里，这一行自己就陈述了它的独立性。`Artifact` 单元格只写了被测文件的行，没有声明任何隔离，读者无从判断到底用了没有。

**分叉的上下文不是隔离。** [`/vaccinate`](../skills/vaccinate/SKILL.md) 在一个全新的 `Agent` 分叉里盲跑检查器，并对产物的*副本*打分——那清空的是审读者的上下文，不是它的工作目录。当期望值被提交在树里任何地方时，副本也必须放在**检出之外**，否则分叉照样能读到答案。

## 已经隔离好的部分

模板已经正确地隔离了一项输入，本规则是对它的推广，而不是提出新想法。[`claim-verifier`](../agents/claim-verifier.md) 收到的是**断言加上来源材料指针，别无其他**——从不收草稿，从不收产生它的推理轨迹——并被指示即使调用方把草稿漏进上下文也要忽略（[`post-flight-verification.md`](post-flight-verification.md)）。那是以输入契约表达的环境隔离：核验器无法给草稿的推理盖章，因为它手里没有那份推理。把同一套纪律向外推——契约对草稿做的事，中立副本对检出做。

## 交叉引用

- [`../references/verification-ladder.md`](../references/verification-ladder.md) — 第 0 级（给检查器做资格认定）、第 3 级（本规则所推广的三种上下文级机制）
- [`post-flight-verification.md`](post-flight-verification.md) — CoVe 协议与独立上下文核验器
- [`../agents/claim-verifier.md`](../agents/claim-verifier.md) — 本规则所推广的输入契约
- [`../references/external-oracle-process.md`](../references/external-oracle-process.md) — 外部咨询：让裁判致盲，核验传输
- [`../skills/vaccinate/SKILL.md`](../skills/vaccinate/SKILL.md) — 埋设缺陷的资格认定，未隔离的答案在那里是致命的
- [`../references/research-agent-laws.md`](../references/research-agent-laws.md) — 法则 1（重新推导，不要重新询问）、法则 13（让裁判致盲）
