---
paths:
  - ".codebuddy/skills/**/SKILL.md"
  - ".codebuddy/agents/**/*.md"
  - ".codebuddy/references/orchestration-schemas.md"
  - ".codebuddy/references/finding-schema.json"
  - ".codebuddy/references/agent-fleet.md"
---

# 编排器协议：审读运行时

**审读—修复循环是一份真实的运行时契约，由主线程中的独立 `Agent` 调用实现。**技能通过独立的 Agent 调用并行派发审读器，审读器返回*结构化*审查发现（[`orchestration-schemas.md`](../references/orchestration-schemas.md)），系统再用确定性门禁归并这些发现，通过幻觉防线裁决，并循环至空轮收敛。**触发**不在自动执行范围内：用户或一次技能调用必须显式启动循环，没有任何机制会自行启动它。这条边界是有意设计的，见「不自动的部分」。

## 相称性 —— 让流程与利害相称

**请先阅读本节，再使用下面的运行时。**这套流程较重，不能不加区分地用于所有任务。一位审读本模板的外部审稿人直言，它*「把太多探索性和协作性的状态当成发布工程来对待」*。如果只机械遵循表面流程，最终会出现敷衍的产物、规避定义的措辞、普遍滥用的例外，或者让使用者在探索性工作中干脆弃用整个模板。因此，运行时本身必须遵守以下原则：

| 场景 | 恰当姿态 |
|---|---|
| 破坏性的 git 操作；对控制机制本身的改动 | 硬门禁，或明确的外部授权 |
| 进入公开论文、发布或交接的断言 | 可复现的溯源与具名的核验 |
| 提升某个默认值；预注册评估 | 预先写定的通过／失败／升级规则 |
| 探索性分析与阶段性协作 | 精确的状态报告，**最小仪式** |
| 高召回的发现型筛选 | 保留歧义，不用默认判定去消解它 |

使用这张表时，有两点尤其重要。**任何场景都不能省略精确的状态报告。**说明实际到达的状态不增加成本（[`research-agent-laws.md`](../references/research-agent-laws.md) 法则 19），却能让轻量探索性运行至少保持可信。**产出一升级，场景也随之升级。**探索性运行中的数字一旦准备进入论文，这项工作就不再只是探索；必须在数字被引用*之前*满足上一行的要求，不能事后补齐。

## 循环（契约）

```
Skill invoked (with a RUN_CONFIG)
  │
  Step 1: IMPLEMENT / DRAFT
  │
  Step 2: VERIFY — compile, render, check outputs   (retry ≤ 2)
  │
  Step 3: FAN-OUT REVIEW — parallel independent Agent reviewers, each returns FINDINGs
  │
  Step 4: REDUCE + JUDGE — stack scorecards; gate predicate → verdict;
  │        run the post-judge hallucination gate on judge-introduced CRITICALs
  │
  Step 5: FIX — apply `mechanical: true` findings; everything touching an
  │        estimand / assumption / specification / inference / reporting
  │        language returns to the researcher (critical → major → minor)
  │
  Step 6: SCORE — quality_score.py / hard-gate roll-up
  │
  └── converged?  (2 consecutive rounds add 0 new CRITICAL/MAJOR — see loop-until-dry)
        YES → present summary
        NO  → back to Step 3, in FRESH context
              (hard fallback cap reached → present with remaining issues)
```

## 运行时原语

这些原语共同构成运行时，每个扇出型技能都是它们的组合。技能不应在散文中重新定义这些原语，而应引用本节和 [`orchestration-schemas.md`](../references/orchestration-schemas.md)。

### 1. 扇出

**在一条消息中并行**派发 N 个审读器，也就是发起 N 次 `Agent` 调用。每次调用都使用自己的独立上下文，绝不是对话分叉。这样既能保持主线程清晰，也能让每个审读器把完整预算用于自己的透镜。`Agent` 子代理是**可移植的原语**：每个 WorkBuddy 安装都提供它，因此模板依赖 `Agent`，不依赖受会话条件限制的 Workflow 工具。*如果 Workflow 工具可用，例如 `ultracode` 或动态工作流会话，技能也可以用它实现同样的扇出→归并→裁决流程，但它只能是可选加速器，不能成为必需项。*

> **[本平台适配 · 2026-10-31] 扇出只在主线程可用，`context: fork` 的技能里拿不到。**
> 声明 `context: fork` 的技能会进入 detached 子会话，而该子会话的工具集
> **没有 `Agent`**，即使在 `allowed-tools` 中申请也一样。因此，子会话无法执行本节所述的
> N 次并行派发，只能让多个透镜在同一会话中依次扮演。实测证据见
> [`platform-facts.md`](../references/platform-facts.md) 的技能一节。
> **判据**：先判断技能是否依赖扇出。依赖扇出就不要写 `context: fork`，
> `qa-quarto`、`slide-excellence`、`translate-to-quarto` 已按此处理；只有不依赖扇出、
> 且中间过程确实会撑爆主上下文的技能，才使用 fork。

[`agent-fleet.md`](../references/agent-fleet.md) 规定哪个代理负责哪个透镜，以及使用哪个模型档位。如果审读者可见的内容可能污染某个透镜的判断，例如先前判定、修订标记或作者摘要，就必须隔离其运行环境，见 [`review-fencing.md`](review-fencing.md)。

### 2. 归并（按类型，不靠肉眼）

每个审读器都按共享 schema 返回 `FINDING` 和 `SCORECARD`。综合器**堆叠这些带类型的对象**，再施加**门禁谓词**：`CRITICAL>0 → BLOCK`，`MAJOR>0 → REVISE`，否则 `PASS`。判定由审查发现确定性地计算得出，不是对产物重新作出主观判断。

### 3. 裁决 + 幻觉门禁

综合器或编辑可以*降级*或*去重*各透镜提出的审查发现。但是，对于综合器或编辑**自行引入、且任何透镜都未提出的 CRITICAL**，必须通过裁决后的幻觉门禁（[`orchestration-schemas.md` §4](../references/orchestration-schemas.md)）：发起一次具名的独立 Agent 调用，让独立上下文中的 `claim-verifier` 重新核验，不能使用会继承裁决者所见内容的对话分叉。找不到依据时，把它降为 `[JUDGE-HALLUCINATED]` 并重新计算。自主审读处理可信度敏感的产物时，必须依靠这道门禁保持可信。

### 4. 空轮收敛

不要用定制的「最多 5 轮」逻辑停止循环，而应根据**收敛**情况停止：出现**连续 2 个空轮**后停止，空轮指一轮新增 0 条 CRITICAL/MAJOR。**去重必须精确，不能依赖模糊匹配（v2.5）。**每条发现都携带 `id = sha1("<file>:<line>:<locus>")`，所以同一轮内，即使不同透镜重复发现同一个缺陷，也会得到相同 id。跨轮次时，修复者的编辑会改变行号，因此根据 `file` + `locus` 判断是否为新发现（[`orchestration-schemas.md`](../references/orchestration-schemas.md) §3）。如果一轮没有发现任何带新 `file` + `locus` 的问题，这一轮就是空轮。限制条件如下：

- **兜底上限**：`RUN_CONFIG.max_rounds` 默认值为 5，用于限制不收敛的循环。
- **缺少透镜时不算空轮**：任何一轮中，只要某个透镜没有完成审读，重新派发一次后仍没有合法的 findings 数组，这一轮就不是空轮，也不计入连续两轮。如果某个透镜始终不返回，循环会持续到兜底上限，报告必须点名该透镜。
- **两次命中**：*同一条*发现，即相同的 `file` + `locus`，在第 N 轮和第 N+2 轮都存在时，必须升级给用户，不能第三次直接打补丁。这项判断可以机械检查，不靠肉眼（[`summary-parity.md`](summary-parity.md)）。
- **花费上限**：达到 `RUN_CONFIG.spend_cap_tokens` 默认约 500k 时，先警告再询问。它限制的是花费，不是上下文；每次重审都使用全新上下文。
- **失控兜底**：绝不能超过 harness 的子代理硬上限。任何 ≥7× 的扇出，都要先在一个小节上进行成本试点，再扫描全部内容。

### 5. 校验审查发现（v2.5）

`FINDING` 契约由**机器校验**，不是自由文本。审读器只读，每个审读器都在响应末尾返回一个不带 id 的 JSON **数组**。派发的技能负责填入 id 并校验，见 `orchestration-schemas.md` §1「谁写文件」：

```bash
echo '[]' | python scripts/validate-findings.py          # smoke-test the harness FIRST
python scripts/validate-findings.py --fill-ids block.json > <report>.json.tmp \
  && mv <report>.json.tmp <report>.json || rm -f <report>.json.tmp   # exit 0 = valid
python scripts/validate-findings.py --check-quotes <report>.json   # every quote is the file's own text
```

如果检查找不到引文，就把发现退回原审读者一次。引文仍无法对应时，在裁决前丢弃该发现，并记为 `quote not in source`（`orchestration-schemas.md` §1）。

**投入审读成本前，先做冒烟测试。**如果一次运行派发十个审读器，最后却无法写出合法报告，整轮工作都会浪费。

校验器要求审读者必须提供：一条被违反的 `rule`，没有引用成文规则的发现只是意见；一个 `failing_case`，不能只写「这里可以更清楚」；一个根据自身坐标推导的 `id`，由 `--fill-ids` 填入，审读者不得自行提供；以及一个 `mechanical` 标记。如果改动涉及估计目标、假设、设定、推断程序、样本定义或报告语言，mechanical **永远**不能为 true。

**核验阶段应优先尝试反驳。**审读者提出发现后，另一轮独立核验要尝试*推翻*每条发现，只发布 `verdict: "confirmed"` 的发现。核验者找不到依据时，必须**丢弃**该发现，不能把它降级为警告。核验*之前*，先应用 [`orchestration-schemas.md` §7](../references/orchestration-schemas.md) 为每个透镜规定的证据负担和「不算数」过滤器，避免已知误报进入裁决。

### 6. 筛选型扇出

**筛选**是从一组候选项中找出少数值得深入处理的对象。它输出*判定*，而不是审查发现，因此主要风险与审读相反：审读可能凭空制造缺陷，筛选则可能悄悄把所有候选项都纳入。筛选必须在启动前明确规则。

- **启动前写好评分细则。**评分标准必须依据 [`templates/screening-rubric.md`](../../templates/screening-rubric.md) 写入磁盘。为每个候选项临时编造评分细则，等于把筛选者的个人偏好重复应用 N 次。
- **声明默认判定，并把它当作一项决定。**精确优先的筛选会生成一份直接据以行动的候选清单，此时 EXCLUDE 是正确的默认值：除非有引证证据支持纳入，否则排除候选项。**召回优先**的筛选包括文献扫读、既有技术检索，以及任何追问*我们漏了什么*的任务。此时，上述默认值会悄悄丢弃相关证据，下游也无法发现这种损失，因此应反转默认值，或增加第三种判定。选择标准是**哪种错误以后仍能发现**。把选择写入评分细则，把确实无法判定的候选项交给 **NEEDS-HUMAN**，不要为了让结果整齐而强行归入某一侧。
- **逐候选提供证据。**每个判定都要指明决定结果的字段、行或段落。没有证据的判定必须重新筛选，不能直接记录。
- **派发方抽查。**根据这批结果采取行动前，按同一份评分细则手工重筛一个样本。出现分歧时，整批结果作废，不能只作废单个候选项。
- **整批裁定。**提前返回的结果只是**状态，不是输入**。必须等每个代理都返回，再通过一次归并按 `id` 把判定与候选项对应起来；在此之前，不能确定任何结果。

→ [`research-agent-laws.md`](../references/research-agent-laws.md) 法则 21；派发侧要求见 [`templates/executor-contract.md`](../../templates/executor-contract.md)。

### RUN_CONFIG：在启动*之前*收集交互输入

独立子代理无法暂停下来询问用户。因此，扇出需要的所有交互式选择，包括目标期刊、抽样的审稿取向、挑剔点预算（peeve budget）、N 位审稿人、独立上下文标记、跨产物／新颖性开关，都必须在生成代理组**之前**收集完毕。系统先把它们回显为**起飞前报告**，再启动运行。Schema 见 [`orchestration-schemas.md` §5](../references/orchestration-schemas.md)。必填字段如果悬而未决，例如目标期刊未知，运行会在启动*之前*中止，绝不会中途暂停。因此，即使运行时不接受输入，`--peer`、`--variance` 与 `editor` 的消歧仍能保留交互性。

## 运行时在哪里实现

| 技能 | 原语 | 备注 |
|-------|-----------|-------|
| `/commit` | verify（Step 2）、score（Step 6） | 失败即中止；`.githooks/pre-commit` 在每次提交时强制同样的门禁 |
| `/seven-pass-review` | 扇出（7 个透镜）→ 归并 → 裁决 **+ 幻觉门禁** | 投稿就绪／R&R 论文 |
| `/slide-excellence` | 条件扇出 → 归并 | 只生成能产出东西的透镜；不自动修复 |
| `/qa-quarto` | 批评 → 修复 → 重审，**空轮收敛** | Beamer↔Quarto 一致性；硬门禁 = CRITICAL 汇总 |
| `/review-paper --adversarial` | 批评 → 修复 → 重审，**空轮收敛** | 稿件审读（与 qa-quarto 同一原语） |
| `/review-paper --peer` / `--variance` | RUN_CONFIG → 编辑 → 扇出审稿人 → 编辑综合 **+ 幻觉门禁** | 跨产物起飞前检查作为 Phase 0 |
| `/deep-audit` | 分解 → 扇出（每个组件一个查找者）→ 裁决 → 归并 → 修复 → 再核验，**空轮收敛** | 对任何产物（证明、论文、代码库、断言集）的对抗式审计；全仓一致性是其中一个应用（机械检查 → 4 个透镜，见 `references/repo-infrastructure-audit.md`） |
| `/create-lecture`、`/data-analysis` | 起飞前检查 → 起草 → 核验 | 起飞前检查为必需 |

## 不自动的部分

- **没有计划批准后的触发器，也没有守护进程。**退出计划模式不会启动修复循环，任何后台服务也不会在无人看管时自动审读或修复某个产物。让无人监督的多代理修复循环处理投稿、共享数据或合作者草稿，正是本协议拒绝的失败模式。循环只能由用户或技能发起。**这是明确记录的非目标，不是缺失功能。**
- **没有全仓编排器链式调用。**技能只在各自范围内组合这些原语；没有明确调用，技能不会互相唤起。
- **质量门禁的强制执行。**`quality_score.py` 在 `/commit` 内运行。运行过 `./scripts/install-hooks.sh` 后，`.githooks/pre-commit` 钩子还会在每次提交时运行门禁总检套件和质量门禁。只有钩子、钩子设置或套件本身被暂存时，才运行钩子电池组；CI 总是全部运行。因此，直接 `git commit` 不能再绕过审读，只有显式使用 `SKIP_QUALITY_GATE=1` 或 `--no-verify` 才能绕过。

## 「直接做」模式

用户说「直接做」或「你处理」时，如果已经调用技能：

- 跳过当前技能最后的批准停顿，但仍要完整执行扇出 → 归并 → 裁决 → 空轮收敛，并呈现摘要。
- **不要把这句话当作提交授权。**提交需要明确的 `/commit` 或毫无歧义的要求，见 [`.codebuddy/skills/commit/SKILL.md`](../skills/commit/SKILL.md)。

## 交叉引用

- [`.codebuddy/references/orchestration-schemas.md`](../references/orchestration-schemas.md) —— FINDING／SCORECARD／RUN_CONFIG／幻觉门禁的契约。
- [`.codebuddy/references/agent-fleet.md`](../references/agent-fleet.md) —— 审读器代理组与模型档位。
- [`.codebuddy/rules/plan-first-workflow.md`](plan-first-workflow.md) —— 调用技能前何时进入计划模式。
- [`.codebuddy/rules/quality-gates.md`](quality-gates.md) —— 阈值定义 + pre-commit 钩子。
- [`.codebuddy/rules/post-flight-verification.md`](post-flight-verification.md) —— 幻觉门禁复用的独立上下文核验机制。
- [`.codebuddy/rules/cross-artifact-review.md`](cross-artifact-review.md) —— 论文 ↔ 代码依赖图模式。
