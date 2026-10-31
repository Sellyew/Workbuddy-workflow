---
paths:
  - ".codebuddy/skills/**/SKILL.md"
  - ".codebuddy/agents/**/*.md"
  - ".codebuddy/references/orchestration-schemas.md"
  - ".codebuddy/references/finding-schema.json"
  - ".codebuddy/references/agent-fleet.md"
---

# 编排器协议：审读运行时

**审读—修复循环是一份真实的运行时契约，用每个 WorkBuddy 会话都具备的原语表达：`Agent` 子代理。** 技能扇出到分叉出的审读器，把它们的*结构化*审查发现（[`orchestration-schemas.md`](../references/orchestration-schemas.md)）经确定性门禁归并，用幻觉防线裁决，并循环至空轮收敛。*不*自动的是**触发**：没有任何东西会自行启动这个循环 —— 由用户（或一次技能调用）启动它。这条边界是有意为之（见「不自动的部分」）。

## 相称性 —— 让流程与利害相称

**请在读下面这套机器之前先读这一段。** 后面的一切都是一套重量级装置，而让它一文不值的最快办法，就是把它对准所有事。一位审读本模板的外部审稿人把反对意见说得很直白：它*「把太多探索性和协作性的状态当成发布工程来对待」*。预测的失败不是谨慎的部分遵从 —— 而是敷衍了事的产物、绕开定义玩的措辞游戏、全局打开的逃生口，或者为了探索性工作干脆弃用整个模板。这里把该建议采纳为运行时自己的信条：

| 场景 | 恰当姿态 |
|---|---|
| 破坏性的 git 操作；对控制机制本身的改动 | 硬门禁，或明确的外部授权 |
| 进入公开论文、发布或交接的断言 | 可复现的溯源与具名的核验 |
| 提升某个默认值；预注册评估 | 预先写定的通过／失败／升级规则 |
| 探索性分析与阶段性协作 | 精确的状态报告，**最小仪式** |
| 高召回的发现型筛选 | 保留歧义，不用默认判定去消解它 |

这张表里有两条读法承担着分量。**精确的状态报告是唯一永远不能省掉的东西** —— 说出你实际到达的状态（[`research-agent-laws.md`](../references/research-agent-laws.md) 法则 19）不花任何成本，而正是它让一次轻量探索性运行至少还值得信任。并且**一个场景在它的产出升级的那一刻就向上移动**：一次探索性运行，只要它的数字即将进入论文，就不再是探索性的，它要在数字被引用*之前*取得上一行，而不是之后。

## 循环（契约）

```
Skill invoked (with a RUN_CONFIG)
  │
  Step 1: IMPLEMENT / DRAFT
  │
  Step 2: VERIFY — compile, render, check outputs   (retry ≤ 2)
  │
  Step 3: FAN-OUT REVIEW — parallel forked reviewers, each returns FINDINGs
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

这些原语就是运行时。每个扇出型技能都是它们的组合；任何一个都不应在散文里重新描述它们 —— 它们引用本节和 [`orchestration-schemas.md`](../references/orchestration-schemas.md)。

### 1. 扇出

**在一条消息里并行**生成审读器 —— N 次 `Agent` 调用，每一次都在自己的独立上下文中（绝不是对话分叉），这样主线程保持干净，每个审读器都能拿到自己那个透镜的完整预算。`Agent` 子代理是**可移植的原语**：它们存在于每一个 WorkBuddy 安装中，所以模板依赖它们，而不依赖受会话门控的 Workflow 工具。*（在 Workflow 工具可用的地方 —— 例如 `ultracode`／动态工作流会话 —— 技能可以用它实现同样的扇出→归并→裁决形态；把那当作可选的加速器，永远不是必需项。）*

> **[本平台适配 · 2026-10-31] 扇出只在主线程可用，`context: fork` 的技能里拿不到。**
> 声明了 `context: fork` 的技能会被送进一个 detached 子会话，而那个子会话的工具集里
> **没有 `Agent`**（`allowed-tools` 里申请了也不行）——所以本节描述的 N 次并行派发在那里面
> 根本无法发生，透镜会退化成同一会话依次扮演。实测证据见
> [`platform-facts.md`](../references/platform-facts.md) 的技能一节。
> **判据**：先问这个技能是否依赖扇出。依赖就不写 `context: fork`（`qa-quarto`、
> `slide-excellence`、`translate-to-quarto` 三个已按此办理）；不依赖、且中间过程确实
> 会撑爆主上下文的，才 fork。

哪个代理填哪个透镜、用哪个模型层级，见 [`agent-fleet.md`](../references/agent-fleet.md)。当某个透镜的判断可能被审读者看得见的东西污染时 —— 先前的判定、修订标记、作者自己的摘要 —— 就把它运行的环境围栏起来：[`review-fencing.md`](review-fencing.md)。

### 2. 归并（按类型，不靠肉眼）

每个审读器按共享 schema 返回 `FINDING` 和一个 `SCORECARD`。综合器**堆叠这些带类型的对象**并施加**门禁谓词** —— `CRITICAL>0 → BLOCK`，`MAJOR>0 → REVISE`，否则 `PASS`。判定是审查发现的确定性函数，不是对产物的再判断。

### 3. 裁决 + 幻觉门禁

综合器／编辑可以自由地*降级*或*去重*各透镜的审查发现，但它**引入的、没有任何透镜提出过的 CRITICAL** 必须通过裁决后的幻觉门禁（[`orchestration-schemas.md` §4](../references/orchestration-schemas.md)）：用一个独立上下文的 `claim-verifier` 重新核验它（一次具名的 `Agent` 调用，而不是对话分叉 —— 分叉会继承裁决者看到的东西）；如果无法给它找到依据，就降为 `[JUDGE-HALLUCINATED]` 并重新计算。这正是让自主审读在面对可信度敏感的产物时仍然可信的原因。

### 4. 空轮收敛

把定制的「最多 5 轮」停止逻辑换成**收敛**：在**连续 2 个空轮**之后停止（空轮指一轮下来新增 0 条 CRITICAL/MAJOR）。**去重是精确的，不是模糊的（v2.5）：** 每条发现都携带 `id = sha1("<file>:<line>:<locus>")`，所以在一轮之内，同一个缺陷会得到同一个 id，**即使它是由另一个透镜重新发现的**。跨轮次时，修复者的编辑会挪动行号，因此「新」按 `file` + `locus` 判定（[`orchestration-schemas.md`](../references/orchestration-schemas.md) §3）。一轮没有产出任何带新 `file` + `locus` 的发现，就是空轮。护栏：

- **兜底上限** —— `RUN_CONFIG.max_rounds`（默认 5）为一个不收敛的循环设界。
- **缺一个透镜不算空轮** —— 任何一轮中，只要有某个透镜没有完成审读（重新派发一次后仍没有合法的 findings 数组），这一轮就不是空轮，也不计入那两轮；一个始终不返回的透镜会把循环带到兜底上限，报告要点名它。
- **两次命中** —— *同一条*发现（同样的 `file` + `locus` —— 可机械检查，不靠肉眼）在第 N 轮和第 N+2 轮都还在，就升级给用户，而不是第三次去打补丁（[`summary-parity.md`](summary-parity.md)）。
- **花费上限** —— `RUN_CONFIG.spend_cap_tokens`（默认约 500k）先警告再询问；它是花费天花板，不是上下文上限（每次重审都是全新的）。
- **失控兜底** —— 绝不超过 harness 的子代理硬上限；任何 ≥7× 的扇出，先在一个小节上做成本试点，再全量扫描。

### 5. 校验审查发现（v2.5）

`FINDING` 契约是**机器校验的**，不是散文。审读器是只读的：每个都在响应末尾给出一个不带 id 的 JSON **数组**（见 `orchestration-schemas.md` §1，「谁写文件」），由派发的技能填入 id 并校验：

```bash
echo '[]' | python scripts/validate-findings.py          # smoke-test the harness FIRST
python scripts/validate-findings.py --fill-ids block.json > <report>.json.tmp \
  && mv <report>.json.tmp <report>.json || rm -f <report>.json.tmp   # exit 0 = valid
python scripts/validate-findings.py --check-quotes <report>.json   # every quote is the file's own text
```

检查找不到的引文会被退回给它的审读者一次；仍然对不上，这条发现在裁决前被丢弃，并记为 `quote not in source`（`orchestration-schemas.md` §1）。

**在投入审读成本之前先做冒烟测试。** 一次运行扇出十个审读器、然后写不出一份合法报告，等于把整轮白费了。

校验器强制审读者必须产出：一条被违反的 `rule`（一条没有引用任何成文规则的发现只是意见）、一个 `failing_case`（而不是「这里可以更清楚」）、一个由自身坐标推导出的 `id`（由 `--fill-ids` 填入，从不自行提供），以及一个 `mechanical` 标记 —— 对估计目标、假设、设定、推断程序、样本定义或报告语言的改动，它**永远**不为 true。

**核验这一遍是偏向反驳的。** 审读者提出，另一遍独立核验试图*打掉*每一条发现。只有 `verdict: "confirmed"` 的才会发布。核验者找不到依据的发现会被**丢弃**，而不是降级成警告。在核验*之前*先施加 [`orchestration-schemas.md` §7](../references/orchestration-schemas.md) 中每个透镜的证据负担和「不算数」过滤器，这样已知的误报根本到不了裁决者面前。

### 6. 筛选型扇出

**筛选** —— 把一组候选项分诊到少数几个值得真正动手的 —— 是一种输出*判定*而非发现的扇出，它的失败方向与审读相反：不是凭空造出缺陷，而是悄悄把一切都收进来。所以筛选在启动之前就要立约。

- **成文评分细则，启动之前。** 标准要落在磁盘上，来自 [`templates/screening-rubric.md`](../../templates/screening-rubric.md)。为每个候选项现编一份评分细则，等于把筛选者的口味应用 N 遍。
- **默认判定要声明出来，而且它是一个决定。** 在精确优先的筛选上（一份你会据以行动的候选清单），EXCLUDE 是正确的默认：除非有引证证据把它放进来，否则候选项出局。在**召回优先**的筛选上 —— 一次文献扫读、一次既有技术检索、任何在问*我们漏了什么*的任务 —— 这个默认会悄悄丢掉相关证据，而下游永远不会把这个损失翻出来，所以默认应当反过来，或者落在第三种判定上。选择的方式是问**哪个错误你日后还抓得住**，把选择写进评分细则，并把任何确实无法判定的东西交给 **NEEDS-HUMAN**，而不是把它推向更齐整的那一边。
- **逐候选证据。** 每个判定都要点名决定它的字段、行或段落。一个光秃秃的判定要被重新筛选，而不是被记录。
- **派发方抽查。** 在依据这一波行动之前，按同一份评分细则手工重筛一个样本；出现分歧时，作废的是这一波，而不是那一个候选项。
- **整波裁定。** 早到的返回是**状态，不是输入** —— 在每个代理都返回、并且用一次归并把这一波对齐（按 `id` 把判定接到候选项上）之前，什么都不算定下。

→ [`research-agent-laws.md`](../references/research-agent-laws.md) 法则 21；派发一侧见 [`templates/executor-contract.md`](../../templates/executor-contract.md)。

### RUN_CONFIG：在启动*之前*收集交互输入

被分叉出的子代理无法停下来问用户问题。所以一次扇出所需的每一项交互式选择 —— 目标期刊、抽样的审稿取向、挑剔点预算（peeve budget）、N 位审稿人、独立上下文标记、跨产物／新颖性开关 —— 都在船队生成**之前**收集好，回显为**起飞前报告**，然后才启动。Schema：[`orchestration-schemas.md` §5](../references/orchestration-schemas.md)。一个悬而未决的必填字段（例如未知的期刊）会在启动*之前*中止，绝不中途停下。正因如此，`--peer`、`--variance` 与 `editor` 的消歧才能在「运行中不接受输入」的运行时里保有交互性。

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

- **没有计划批准后的触发器／没有守护进程。** 退出计划模式不会启动修复循环，也没有任何后台服务会在无人看管时把运行时对准某个产物。一个没有人在环内的多代理修复循环，跑在投稿、共享数据或合作者的草稿上，正是我们拒绝的失败模式 —— 循环永远由用户／技能发起。**这是成文记录的非目标，不是缺失的功能。**
- **没有全仓编排器链式调用。** 技能在各自范围内组合这些原语；没有明确调用，它们不会互相唤起。
- **质量门禁的强制执行。** `quality_score.py` 在 `/commit` 内运行，**并且** —— 一旦运行过 `./scripts/install-hooks.sh` —— `.githooks/pre-commit` 钩子会在每次提交时运行门禁总检套件（只有在某个钩子、它的设置或套件本身被暂存时才跑钩子电池组；CI 总是全跑）外加质量门禁，所以直接 `git commit` 不再能绕过审读（绕过是显式的：`SKIP_QUALITY_GATE=1` / `--no-verify`）。

## 「直接做」模式

当用户说「直接做」／「你处理」（在已经调用的技能之内）：

- 跳过当前技能最后的批准停顿；仍然跑完整的扇出 → 归并 → 裁决 → 空轮收敛；仍然呈现摘要。
- **不要把这句话当作提交授权。** 提交需要明确的 `/commit` 或毫无歧义的要求 —— 见 [`.codebuddy/skills/commit/SKILL.md`](../skills/commit/SKILL.md)。

## 交叉引用

- [`.codebuddy/references/orchestration-schemas.md`](../references/orchestration-schemas.md) —— FINDING／SCORECARD／RUN_CONFIG／幻觉门禁的契约。
- [`.codebuddy/references/agent-fleet.md`](../references/agent-fleet.md) —— 审读器船队 + 模型层级。
- [`.codebuddy/rules/plan-first-workflow.md`](plan-first-workflow.md) —— 调用技能前何时进入计划模式。
- [`.codebuddy/rules/quality-gates.md`](quality-gates.md) —— 阈值定义 + pre-commit 钩子。
- [`.codebuddy/rules/post-flight-verification.md`](post-flight-verification.md) —— 幻觉门禁复用的独立上下文核验机制。
- [`.codebuddy/rules/cross-artifact-review.md`](cross-artifact-review.md) —— 论文 ↔ 代码依赖图模式。
