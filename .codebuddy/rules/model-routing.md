---
paths:
  - ".codebuddy/agents/**/*.md"
  - ".codebuddy/skills/**/SKILL.md"
---

# 逐代理模型路由（架构师 / 编辑分工）

> **[WorkBuddy 适配]** 上游这一条规则是围绕 Claude Code 的四个模型层（含 `Fable`）与 `effort` 轴写的。
> 本平台**只有三档**——`default` / `lite` / `reasoning`——第四层不存在。
> `effort` 轴**存在，但在另一个维度上**：它是代理 frontmatter 的 `effort:`（`minimal`–`max`），
> 另有一条 `/effort` 命令；它调的是**思考预算**，不改模型档位。**技能里写它无效。**
> 两个轴正交，所以下面先讲档位，末尾单独讲 effort。
> 上游原文见 `UPSTREAM.md` 记录的上游仓库。

**把模型档位匹配到工作的认知需求。** 机械劳动走 `lite`；审读与批评用 `default`；高判断力的活儿才用 `reasoning`。Aider 的架构师/编辑分工是这件事的社区标准形态。

## 70/20/10 路由模式

| 占比 | 档位 | 用来做什么 |
|---:|---|---|
| ~70% | **`lite`** | 机械劳动——文件改名、引文格式转换、TikZ 抽取、文献库校验、校对修正的套用、简单的检索 / 文件查找 |
| ~20% | **`default`** | 审读与批评——`r-reviewer`、`slide-auditor`、`proofreader`、`quarto-fixer`、`humanize-auditor` |
| ~10% | **`reasoning`** | 高判断力——`editor`、`methods-referee`、`domain-referee`、`claim-verifier`、`quarto-critic`、`tikz-reviewer`、`domain-reviewer`、非平凡关卡上的 `verifier` |

在代理的 YAML frontmatter 里用 `model:` 逐代理设定：

```yaml
---
name: quarto-fixer
model: default      # 原来是 sonnet
---
```

技能用同样的字段在 `SKILL.md` 的 frontmatter 里设定。工作本来就跨档的技能可以不定（等于继承会话默认），比如 `/review-paper --peer` 派出的是混合阵容。

## effort 与档位是两个正交的轴

档位选**哪个模型**；`effort` 调**这个模型想多深**。两者都能省钱，但它们不互相替代：

- **`effort:` 只在代理里生效。** 写在 `.codebuddy/agents/*.md` 的 frontmatter 里，
  取值 `minimal` / `low` / `medium` / `high` / `xhigh` / `max`；非法值引擎会告警并忽略。
  它经 `setOverrideThinking(reasoningEffort)` 落到子代理会话的思考预算上。
- **技能里写 `effort:` 不起作用。** 技能加载器不读这个字段——`parseSkillFile` 只带
  `context` / `agent` / `model`。想让某个技能跑得更深，改它派出的代理的档位或 effort。
- **`/effort` 命令**改的是当前会话的档位，带一个 `ultracode` 档；它不动代理的
  frontmatter。

成本纪律因此有三条，顺序不能反：

1. **先降档，再降 effort。** 换档是换模型，跨档的价差通常大于同一档内思考预算的价差；
   而`effort` 的下限（`minimal`）仍然花在同一个模型上。
2. **关卡两个都不降。** `editor`、`domain-referee`、`methods-referee`、`claim-verifier`
   留在 `reasoning` + `effort: high`。详见下面的反面模式。
3. **省钱的第一手段是缩小上下文，不是降档。** 独立上下文的子代理只读它要审的那份材料，
   比把整套仓库塞给一个大模型便宜得多——这也是 `orchestrator-protocol.md` 的扇出之所以
   同时省钱和提质的原因。

**不要再写「本平台没有 effort 轴」。** 那是 2026-10-30 早些时候的一条错误判断
（原因：只查了代理**名录**的 schema，没查加载器），它导致 18 个代理的 `effort:` 被删、
又被同一批人恢复。证据与命令见 [`platform-facts.md`](../references/platform-facts.md)。

## 为什么不是所有代理都用 `reasoning`

最省事的做法是把整支代理舰队钉在最高档，代价也最直接：

- **成本。** 审稿人、编辑、核查者都是**有界的单次审读**，不是长程自主工作。给它们最高档，付的是长程任务的价钱，买的是单次判断——同一份预算下你能跑的论文数会掉一个量级。
- **收益递减是可测的。** 机械活儿（改名、格式转换、抽取）在 `lite` 上和在 `reasoning` 上产出没有可测差别。先测，再决定要不要升档；不要凭「重要所以要贵」的直觉升。
- **多样性比单点强度更值钱。** 见下面的corollary：真正保护结论的是**不同档位的多个视角**，不是同一个最强模型自问自答三遍。

**什么时候 `reasoning` 是对的：** 判断错一次的代价高于跑一次的代价——假 PASS 会放过一处幻觉引文、一处站不住的识别策略、一处会被 desk-reject 的错误。这些正是下面「反面模式」里点名的四个代理。

## 为什么这条规则要紧

在机械层上路由通常能省 **50–80%** 的成本，且无质量损失。反过来，把所有东西钉在最高档不会让结论更可靠，只会让你跑得更少、审得更少、发现得更少——而「审得少」在研究工作里就是质量下降。

## 按任务类型给的路由配方

### 机械（`lite`）

- **TikZ → SVG 抽取** —— 如果你把 `/extract-tikz` 的编译与转换步骤外包给代理（该技能目前内联跑；它唯一的代理 `tikz-reviewer` 是 `reasoning` 档）。
- **文献格式 / 引文改写** —— 如果你加一条修正路径（`/validate-bib` 只报告、不自动修）。
- **记忆晋升投票**（`promote-memory-council`）。
- **校对修正的套用**（当修正是「把 X 换成 Y」这种机械操作时）。
- **文件改名 / 查找替换。**

### 审读 / 批评（`default`）

- **R 代码审查**（`r-reviewer`）。
- **幻灯片版面审计**（`slide-auditor`）。
- **校对检查**（`proofreader`）。
- **Quarto 修正套用**（当修正是由 `quarto-critic` 驱动的编辑时）。
- **AI 腔审计**（`humanize-auditor`）。
- **Beamer ↔ Quarto 翻译**（`beamer-translator`）—— 翻译足够有界，除非源 TeX 里有不寻常的 TikZ。

### 高判断力（`reasoning`）

- **`/review-paper --peer` 的编辑**（`editor`）。
- **两位审稿代理**（`domain-referee`、`methods-referee`）。
- **独立上下文模式下的事实核查**（`claim-verifier`）。
- **Quarto 批评者**（`quarto-critic`）—— 对抗式对齐 QA 需要高判断力才能抓到细微的视觉漂移。
- **TikZ 审阅者**（`tikz-reviewer`）—— 执行测量规则需要精确的空间推理。
- **领域审阅者**（`domain-reviewer`）。
- **`verifier`** —— 在为非平凡提交把关时。

## 什么时候「不定档位」仍然合理

- 你还没摸过脾气的**新代理** —— 先不定（继承会话），跑一次，再路由。
- 同一次调用里工作跨档的代理（少见；通常是该拆分的信号）。
- 一次性的试验代理。

## 反面模式：把高判断力代理降档

**不要**为了省钱把 `claim-verifier`、`methods-referee`、`domain-referee`、`editor` 降到 `default`。这四个是保护论文不被幻觉引文 / 薄弱识别 / desk-reject 级错误毁掉的代理。一个太便宜的核查者给出一次假 PASS 的代价，实质高于每篇论文都用 `reasoning` 跑一遍的代价。

## 反面模式：自己既当架构师又当编辑

Aider 的模式是同一个模型既规划又执行。我们刻意不这样做——同模型自配对产生的是相关误差。我们的分工让架构侧与编辑侧跑**不同档位**；这种多样性本身就是成本故事的一部分。

### 推论：挑战者 ≠ 审计者同档（这是一条防线，不是一项待建功能）

如果将来有人真的加上一步显式的*挑战者 → 审计者*（例如「先审计再打分」／「真相是一个过程」这类验证器：一个代理反驳某个断言，另一个代理裁决），那么挑战者**必须**跑在与审计者不同的档位——两个同档模型共享盲区，于是同档的挑战者会把相关误差洗成「独立确认」。

今天遵守它不花任何成本；它存在的意义是：等那一天真的动手时，多样性这个性质不会被悄悄弄丢。**这是对某个假设中的未来步骤的约束，不是开工许可** —— 当前的验证路径用的是更便宜的「点名替代解释」机制（见 `replication-protocol.md` 与 `/verify-claims`），它不增加第二个代理，也不增加成本倍数。

## `/commit` 怎么用这条规则

`/commit` 会派出 `verifier` 代理，钉在 `reasoning` 档：它的检查项是退出码、计数、文件存在性。理论上 `default` 也能干，但一次漏检会让整个提交门禁失去意义，所以不省这一档。等你在自己的提交上量到 `default` 足够后，再降。

## 交叉引用

- [`.codebuddy/rules/cross-artifact-review.md`](cross-artifact-review.md) —— 论文 ↔ 代码依赖图（与路由正交，但常在相同时刻被调用）。
- [`.codebuddy/rules/post-flight-verification.md`](post-flight-verification.md) —— CoVe / 独立上下文核查（按上面「反面模式：把高判断力代理降档」，`claim-verifier` 应留在 `reasoning`）。
- [`agent-fleet.md`](../references/agent-fleet.md) —— 每个代理钉在哪一档，与这里的分工一致。

> **讲档位，不讲具体型号。** 本条规则只用两组枚举：档位 `default` / `lite` / `reasoning`，
> 与 `effort` 的 `minimal`–`max`——它们是本平台稳定的东西。具体型号与版本会变，
> 且不由本仓库决定；不要在这里硬编码型号。
