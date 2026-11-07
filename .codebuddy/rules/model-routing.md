---
paths:
  - ".codebuddy/agents/**/*.md"
  - ".codebuddy/skills/**/SKILL.md"
---

# 逐代理模型路由（架构师 / 编辑分工）

> **[WorkBuddy 适配]** 上游规则以 Claude Code 的四个模型层和 `effort` 轴为基础，其中包括 `Fable`。
> 本平台**只有三档**：`default` / `lite` / `reasoning`，没有第四层。
> 本平台也有 `effort` 轴，但它独立于模型档位：代理在 frontmatter 中用 `effort:` 设置，取值范围为 `minimal`–`max`，另有 `/effort` 命令。它调整的是**思考预算**，不会改变模型档位。**写在技能中无效。**
> 两个轴彼此正交，因此下文先说明模型档位，最后单独说明 effort。
> 上游原文见 `UPSTREAM.md` 记录的上游仓库。

**应根据任务需要的判断能力选择模型档位。**机械任务使用 `lite`，审读与批评使用 `default`，只有高度依赖判断的任务才使用 `reasoning`。Aider 的架构师/编辑分工是这种分工在社区中的标准形式。

## 70/20/10 路由模式

| 占比 | 档位 | 用来做什么 |
|---:|---|---|
| ~70% | **`lite`** | 机械任务：文件改名、引文格式转换、TikZ 抽取、文献库校验、套用校对修正、简单检索和文件查找 |
| ~20% | **`default`** | 审读与批评：`r-reviewer`、`slide-auditor`、`proofreader`、`quarto-fixer`、`humanize-auditor` |
| ~10% | **`reasoning`** | 高度依赖判断的任务：`editor`、`methods-referee`、`domain-referee`、`claim-verifier`、`quarto-critic`、`tikz-reviewer`、`domain-reviewer`，以及负责非平凡关卡的 `verifier` |

在代理的 YAML frontmatter 中，用 `model:` 为每个代理设置档位：

```yaml
---
name: quarto-fixer
model: default      # 原来是 sonnet
---
```

技能也可以在 `SKILL.md` 的 frontmatter 中使用同一字段。任务本身跨越多个档位的技能可以不设置该字段，此时继承会话默认值。例如，`/review-paper --peer` 会派出使用不同档位的代理。

## effort 与档位是两个正交的轴

模型档位决定**使用哪个模型**，`effort` 决定**该模型投入多少思考**。两者都能控制成本，但不能互相替代：

- **`effort:` 只在代理中生效。**把它写入 `.codebuddy/agents/*.md` 的 frontmatter，可取 `minimal` / `low` / `medium` / `high` / `xhigh` / `max`。引擎会警告并忽略非法值。该字段通过 `setOverrideThinking(reasoningEffort)` 设置子代理会话的思考预算。
- **技能中的 `effort:` 不起作用。**技能加载器不会读取这个字段，`parseSkillFile` 只传递 `context` / `agent` / `model`。如果需要技能进行更深入的思考，应调整它所派代理的模型档位或 effort。
- **`/effort` 命令**调整当前会话的 effort 档位，并提供 `ultracode` 档；它不会修改代理的 frontmatter。

成本控制必须遵守以下顺序：

1. **先降低模型档位，再降低 effort。**换档会更换模型，不同档位的价差通常大于同一档位内不同思考预算的价差；即使把 `effort` 降到 `minimal`，使用的仍是同一个模型。
2. **关卡代理的模型档位和 effort 都不能降低。**`editor`、`domain-referee`、`methods-referee`、`claim-verifier` 应保持 `reasoning` + `effort: high`。原因见下面的反面模式。
3. **控制成本应优先缩小上下文，而不是降低模型档位。**独立上下文的子代理只阅读自己负责审读的材料，成本远低于让一个大模型读取整套仓库。这也是 `orchestrator-protocol.md` 的扇出既能降低成本又能提高质量的原因。

**不要再写「本平台没有 effort 轴」。**2026-10-30 早些时候曾出现这一错误判断，原因是只检查了代理**名录**的 schema，没有检查加载器。它曾导致 18 个代理的 `effort:` 被删除，之后又由同一批人恢复。证据与命令见 [`platform-facts.md`](../references/platform-facts.md)。

## 为什么不是所有代理都用 `reasoning`

把所有代理都固定在最高档看似简单，但会直接增加成本：

- **成本。**审稿人、编辑和核查者执行的是**有边界的单次审读**，不是长程自主工作。为它们使用最高档，相当于按长程任务的价格购买单次判断；在预算相同的情况下，可审读的论文数量会下降一个量级。
- **收益递减可以测量。**对于改名、格式转换和抽取等机械任务，`lite` 与 `reasoning` 的产出没有可测差别。应先测量再决定是否升档，不要仅凭「任务重要，所以应该用更贵的模型」作出判断。
- **多样性比单一模型的强度更有价值。**见下面的推论：真正保护结论的是**来自不同档位的多个视角**，不是让同一个最强模型重复自问自答三遍。

**什么时候应使用 `reasoning`：**当一次错误判断的代价高于一次运行的代价时，就应使用 reasoning。例如，假 PASS 可能放过编造的引文、站不住脚的识别策略或足以导致案头退稿的错误。下面「反面模式」点名的四个代理正承担这类工作。

## 为什么这条规则要紧

把机械任务路由到较低档位，通常可以节省 **50–80%** 的成本，而且不损失质量。相反，把所有任务都固定在最高档并不会让结论更可靠，只会减少能够执行的运行和审读，也会减少能够发现的问题。对研究工作来说，审读减少本身就是质量下降。

## 按任务类型给的路由配方

### 机械（`lite`）

- **TikZ → SVG 抽取**：如果把 `/extract-tikz` 的编译与转换步骤交给代理，就使用这一档。该技能目前以内联方式运行，唯一的代理 `tikz-reviewer` 使用 `reasoning` 档。
- **文献格式 / 引文改写**：如果增加修正路径，就使用这一档。`/validate-bib` 目前只报告问题，不自动修正。
- **记忆晋升投票**（`promote-memory-council`）。
- **套用校对修正**：修正属于「把 X 换成 Y」这类机械操作时使用。
- **文件改名 / 查找替换。**

### 审读 / 批评（`default`）

- **R 代码审查**（`r-reviewer`）。
- **幻灯片版面审计**（`slide-auditor`）。
- **校对检查**（`proofreader`）。
- **套用 Quarto 修正**：由 `quarto-critic` 驱动编辑时使用。
- **AI 腔审计**（`humanize-auditor`）。
- **Beamer ↔ Quarto 翻译**（`beamer-translator`）：翻译任务的边界足够明确，除非源 TeX 含不寻常的 TikZ。

### 高判断力（`reasoning`）

- **`/review-paper --peer` 的编辑**（`editor`）。
- **两位审稿代理**（`domain-referee`、`methods-referee`）。
- **独立上下文模式下的事实核查**（`claim-verifier`）。
- **Quarto 批评者**（`quarto-critic`）：对抗式对齐 QA 需要较强的判断能力，才能发现细微的视觉漂移。
- **TikZ 审阅者**（`tikz-reviewer`）：执行测量规则需要精确的空间推理。
- **领域审阅者**（`domain-reviewer`）。
- **`verifier`**：为非平凡提交把关时使用。

## 什么时候「不定档位」仍然合理

- 对行为尚不了解的**新代理**，先不设置档位，让它继承会话档位；运行一次后再决定路由。
- 同一次调用中的任务跨越多个档位的代理。这种情况很少见，通常说明代理应当拆分。
- 一次性的试验代理。

## 反面模式：把高判断力代理降档

**不要**为了省钱把 `claim-verifier`、`methods-referee`、`domain-referee`、`editor` 降到 `default`。这四个代理负责防止幻觉引文、薄弱识别和足以导致案头退稿的错误损害论文。为压低核查成本而降低核查者档位，并因此得到一次假 PASS，其代价会实质高于每篇论文都使用 `reasoning` 运行一遍的成本。

## 反面模式：自己既当架构师又当编辑

Aider 的模式让同一个模型同时规划和执行。我们刻意采用不同做法，因为同一模型自配对会产生相关误差。我们的分工让架构侧与编辑侧使用**不同档位**，这种多样性也是成本控制的一部分。

### 推论：挑战者 ≠ 审计者同档（这是一条防线，不是一项待建功能）

如果将来增加显式的*挑战者 → 审计者*步骤，例如「先审计再打分」或「真相是一个过程」这类验证器，让一个代理反驳断言、另一个代理裁决，那么挑战者**必须**使用与审计者不同的档位。同档模型会共享盲区，同档挑战者因此可能把相关误差包装成「独立确认」。

当前遵守这项约束不需要额外成本。它的作用是确保将来真正实现该步骤时，不会悄悄丢失多样性。**这项约束针对假设中的未来步骤，不是开工许可。**当前验证路径使用成本更低的「点名替代解释」机制，见 `replication-protocol.md` 与 `/verify-claims`。它不会增加第二个代理，也不会增加成本倍数。

## `/commit` 怎么用这条规则

`/commit` 会派出 `verifier` 代理，并将其固定在 `reasoning` 档。它检查退出码、计数和文件存在性；理论上 `default` 也能完成这些工作，但一次漏检就会让整个提交门禁失去意义，因此这里不降低档位。只有当你在自己的提交上测得 `default` 已足够可靠时，才可以降档。

## 交叉引用

- [`.codebuddy/rules/cross-artifact-review.md`](cross-artifact-review.md) —— 论文 ↔ 代码依赖图（与路由正交，但常在相同时刻被调用）。
- [`.codebuddy/rules/post-flight-verification.md`](post-flight-verification.md) —— CoVe / 独立上下文核查（按上面「反面模式：把高判断力代理降档」，`claim-verifier` 应留在 `reasoning`）。
- [`agent-fleet.md`](../references/agent-fleet.md) —— 每个代理钉在哪一档，与这里的分工一致。

> **只规定档位，不规定具体型号。**本规则只使用两组枚举：模型档位 `default` / `lite` / `reasoning`，以及 `effort` 的 `minimal`–`max`。它们是本平台稳定的接口。具体型号和版本会变化，也不由本仓库决定，因此不要在这里硬编码。
