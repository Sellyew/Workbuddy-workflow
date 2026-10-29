# 编排 Schema（审读运行时的数据契约）

那些扇出到审读子代理的技能（`/seven-pass-review`、`/slide-excellence`、`/qa-quarto`、`/deep-audit`、`/review-paper --adversarial` 与 `--peer`）过去把它们的发现描述成自由格式的 markdown，再由综合器用眼睛重新解析。本文件是它们改为归并其上的**共享结构化契约**——这样综合器数的是带类型的对象，门禁谓词是一次确定性检查，同一套严重度词汇在每个技能里含义相同。

审读器输出一个符合 [`finding-schema.json`](finding-schema.json) 的 JSON **数组**，写进散文报告旁边的 `.json` 文件，并在综合器归并**之前**用 `scripts/validate-findings.py` 校验（要求退出码 0）。那个校验器就是运行时；本文件是它外面那层可读的契约。关于扇出 → 归并 → 裁决 → 空轮收敛这套运行时如何使用它们，见 [`.codebuddy/rules/orchestrator-protocol.md`](../rules/orchestrator-protocol.md)。

---

## 1. `FINDING` —— 审读人提出的一条问题

每个向归并型技能供料的审读子代理（透镜、审稿人、批评者、审计者）都以**一个 JSON 数组**的形式输出发现，符合 [`finding-schema.json`](finding-schema.json)——那份机器校验的契约。（`claim-verifier` 与 `humanize-auditor` 保留各自的逐断言与只检测报告格式——没有归并型技能消费它们。）下面这份草图是该 schema 的一份可读呈现，不是第二份契约（它曾经是，然后两份漂移了——Codex 抓到一个生产者按旧形状排序，而校验器要求新形状）：

```json
[
  {
    "id": "<sha1 of 'file:line:locus'>",
    "file": "main.tex",
    "line": 214,
    "locus": "Table 2, col 3",
    "lens": "methods",
    "severity": "blocker",
    "rule": "conditional PT must be stated when covariates enter the estimand",
    "claim": "Identification rests on conditional PT but the text claims unconditional.",
    "evidence": "p.11 states the assumption unconditionally vs Eq.(4) conditions on X_i.",
    "failing_case": "covariate-dependent treatment timing: Eq.(4) fails while the text's claim stands",
    "suggested_fix": "State the conditional PT assumption explicitly, or drop the covariates.",
    "mechanical": false,
    "confidence": "high"
  }
]
```

- **`id` 是算出来的，绝不是编出来的**：`python scripts/validate-findings.py --id FILE LINE LOCUS`。确定且与透镜无关，所以两个透镜发现的同一个缺陷会去重成一条。
- **报告是裸数组** —— 没有 `findings:` 包装。
- **归并之前先校验**：`python scripts/validate-findings.py <report>.json`（要求退出码 0）。报告没通过校验的审读器等于没审。
- **谁写文件。** 审读代理是只读的——它们不能写 `.json`，也不能跑 id 脚本。每个审读器**以响应末尾的一个 `json` 围栏块结束**：那个数组，除 `id` 之外的每个必填 schema 字段（`verdict` 留空——由偏向反驳的核验遍设置它；见 §7），块的正上方是一行 `Scorecard: N/10`。派发的技能抽取那个块，运行 `python scripts/validate-findings.py --fill-ids block.json > <report>.json.tmp && mv <report>.json.tmp <report>.json`（它算出每个 `id` 并校验；只保留合法的数组——一次失败的运行不得留下一个空的 `<report>.json`），并把散文报告存在旁边。没什么可报的审读器返回 `[]`——一个显性的空数组，而不是省略块。每个 `file:line:locus` 在一个数组里只出现一次：同一处的两个问题要么合并，要么给不同的 locus，因为相同坐标意味着相同 id，而重复 id 会让校验失败。
- **引文要对着源文件校验。** `--fill-ids` 之后，技能运行 `python scripts/validate-findings.py --check-quotes <report>.json`：`evidence` 里每个 12 字符以上的双引号片段，都必须出现于该发现的 `file`，或该证据按路径点名的另一个文件（一条一致性发现会引用 Beamer 源，而引的是 Quarto 文件）。比较时会把 LaTeX 标记、破折号、空白与大小写归一——但含反斜杠的引文必须与源文件逐字一致；反引号里的命令与输出不做检查；PDF 通过 `pdftotext` 读取，无法作为文本读取的文件，其引文留作未检查而不是判失败。对不上的会退回给它的审读器一次，附上检查器的输出；引文仍然对不上的发现，在裁决前被丢弃并记为 `quote not in source`。编造引文是伤害最大的审读错误，也正是字符串匹配能抓到的那一个。
- 旧的散文字段按 §7 的表格映射：`location`→`file`+`line`+`locus`，`finding`→`claim`，`recommendation`→`suggested_fix`，`CRITICAL`→`blocker`。`change_my_mind` 背后的那个概念活在 `failing_case` 里——陈述具体的配置或缺失的假设，而那也恰好正是会翻转这条发现的东西。

**严重度是唯一的跨技能词汇。** 把每个技能的本地用语映射到它上面：

| 本地术语（代理或技能） | JSON `severity` | 门禁读法 |
|---|---|---|
| FATAL / desk-reject-worthy / hard-gate failure / Critical / CRITICAL / HIGH-WARN (fabricated citation) | `blocker` | CRITICAL |
| Major Concern / "blocks submission" / Visual-Regression / High / MAJOR / ADDRESSABLE (weighty) | `major`（若它阻断产物则为 `blocker`） | MAJOR |
| Minor Concern / Medium / MED / Low / MINOR / ADDRESSABLE (light) / MED-WARN / LOW-WARN (retrieval problems, not defects) | `minor` | MINOR |
| TASTE / polish / style with no rule behind it | `nit` | ——（从不设门禁） |

- 旧的 `change_my_mind` 字段**已取消**——它的内容活在 `failing_case` 里，而后者是每条发现的必填项：能打破该断言的具体配置，也恰好正是会翻转这条发现的东西。
- `confidence` 是给裁决者／核验者的，不是给作者的——一条 `low` 置信度的 CRITICAL 是幻觉门禁（§4）的首要候选。

## 2. `SCORECARD` —— 审读人的汇总

派发的技能为每个审读人构建一份记分卡——计数来自审读人那份已通过校验的数组，`score` 来自它的 `Scorecard: N/10` 行——然后综合器把它们堆叠起来：

```yaml
scorecard:
  lens: methods
  critical: 1         # count of `blocker` findings
  major: 3
  minor: 5
  score: 6            # 0–10, the reviewer's holistic read of its own lens (referees who score 0–100 report composite ÷ 10)
  verdict: REVISE-MAJOR   # SUBMIT | REVISE-MINOR | REVISE-MAJOR | REJECT  (artifact-level lenses)
```

对一致性／门禁型技能（`qa-quarto`），透镜判定就是硬门禁汇总：当且仅当每个硬门禁都通过（零 CRITICAL）时 `APPROVED`，否则 `BLOCKED`。

## 3. 门禁谓词（`reduce` 如何决定）

综合器的判定是**带类型发现的一个确定性函数**，不是一次再判断：

| 谓词 | 规则 |
|---|---|
| **PASS / APPROVED** | 所有透镜上 `sum(CRITICAL) == 0`（对门禁型技能，还要求每个硬门禁为真） |
| **REVISE** | `sum(CRITICAL) == 0` 且 `sum(MAJOR) > 0` |
| **BLOCK / FAIL** | `sum(CRITICAL) > 0` |
| **已收敛（loop-until-dry）** | **连续 2 轮**每轮都产出 **0 条新** blocker/major 发现（按确定性的 `id` 去重），**并且**每个透镜在两轮里都返回了合法的发现数组；某一轮缺了某个透镜（重新派发一次后仍无合法数组）就不算空轮，也不计入（[`orchestrator-protocol.md`](../rules/orchestrator-protocol.md) §4） |

「新」是相对整个已见发现的运行集来衡量的：轮内按 **`id`**（`sha1(file:line:locus)`——精确、与透镜无关），**跨轮按 `file` + `locus`**，因为修复者的编辑会挪动行号，从而给它下面一个未修的缺陷一个新的 `id`。`file` + `locus` 已经见过的发现不算新——所以批评者重新标出一个未修的问题不算进展，而修复者悄悄重新引入一个问题也藏不住。

## 4. 裁决后的幻觉门禁（综合器不能凭空造出 CRITICAL）

综合器／编辑／裁决者归并各透镜的发现——它不得**引入**任何透镜没提过的阻断性断言。（那次审计发现 `editor.md` 能凭一个两位审稿人都没给的理由直接拒稿。）门禁是：

1. 裁决者产出判定之后，把它给出的 CRITICAL／拒稿理由与各透镜 `findings` 的并集做差异比对。
2. 裁决者引入的、**追溯不到**任何透镜发现的 CRITICAL，是**候选幻觉**。
3. 在一个**独立上下文**里重新核验每个候选——按 [`post-flight-verification.md`](../rules/post-flight-verification.md) 派生 `claim-verifier`（一次具名的 `Agent` 调用，绝不是对话分叉，这样它永远看不到初稿），带上断言 + 它所引的产物位置。
   - 核验者确认（有引文／位置支撑）→ 保留这条 CRITICAL；标注 `[JUDGE-ADDED, verified]`。
   - 核验者给不出依据 → **把它降为一条标记备注**，打上 `[JUDGE-HALLUCINATED]`，并按 §3 在不含它的情况下**重算判定**。
4. 裁决者随时可以自由地*降级*或*去重*各透镜的发现；它只能*引入*能通过门禁的阻断性发现。

这很便宜（只对裁决者引入的 CRITICAL 运行，通常 0–2 条），而且是在可信度敏感的产物附近信任一次自主审读时最重要的单条防线。

## 5. `RUN_CONFIG` —— 运行前的输入契约

扇出型运行时在启动**之前**收集每一项交互式选择，这样没有子代理会在运行中停下来等用户（子代理无法提问）。见 `orchestrator-protocol.md` →「RUN_CONFIG」。

```yaml
run_config:
  artifact: path/to/manuscript.tex        # what is being reviewed
  mode: peer                              # default | adversarial | peer | seven-pass | excellence | audit
  journal: QJE                            # --peer: resolved against journal-profiles.md (else null)
  dispositions: [SKEPTIC, MEASUREMENT]    # --peer/--variance: sampled before launch (else null)
  n_referees: 3                           # --variance N (else null)
  peeves: { critical: 2, constructive: 1 }# referee peeve budget (stress doubles critical)
  fresh_context: true                     # re-audit rounds run in a fresh Agent context (never a fork)
  max_rounds: 5                           # loop-until-dry FALLBACK cap (not the primary stop)
  cross_artifact: true                    # auto-invoke /review-r + /audit-reproducibility
  novelty_check: true                     # editor WebSearch probe (Post-Flight-verified)
  spend_cap_tokens: 500000                # warn-and-ask ceiling, not a context limit
```

收集它，把它回显成**起飞前报告**，然后才生成船队。任何未解决的必填字段（例如一个未知的 `journal`）会在启动前中止——绝不中途停下。

---

## 交叉引用

- [`.codebuddy/rules/orchestrator-protocol.md`](../rules/orchestrator-protocol.md) —— 消费这些 schema 的运行时。
- [`.codebuddy/references/agent-fleet.md`](agent-fleet.md) —— 哪个代理填哪个透镜，在哪个模型层级。
- [`.codebuddy/rules/post-flight-verification.md`](../rules/post-flight-verification.md) —— §4 门禁复用的独立上下文核验机制。
- [`.codebuddy/rules/summary-parity.md`](../rules/summary-parity.md) —— 循环对反复被标出的发现复用的两振出局规则。


---

## 7. FINDING 契约是机器校验的（v2.5）

上面那份 schema 不再是散文。它现在是 [`finding-schema.json`](finding-schema.json)，由 [`scripts/validate-findings.py`](../../scripts/validate-findings.py) 用退出码强制执行。

### 把它与上面的散文 schema 对齐（Codex 审读，PR #140）

§1 的可读草图与这份 JSON schema 是**同一份契约的两种序列化**，而在加进 §7 时它们并不一致。JSON schema 现在是**权威**的；§1 仍作为人类可读的草图保留。映射如下：

| §1 散文字段 | Schema 字段 | 备注 |
|---|---|---|
| `location` | `file` + `line` + `locus` | 拆开，好让去重精确 |
| `finding` | `claim` | 一句话，含义不变 |
| `recommendation` | `suggested_fix` | 只改名字 |
| `severity: CRITICAL \| MAJOR \| MINOR` | `severity: blocker \| major \| minor \| nit` | **`CRITICAL` 映射为 `blocker`**；`nit` 是新的 |
| —— | `rule`、`evidence`、`failing_case`、`mechanical`、`confidence` | 新增的必填字段 |
| `findings:` 包装 | **裸数组** | 报告就是数组 |

门禁谓词在含义上不变：**`blocker` > 0 → BLOCK**，`major` > 0 → REVISE，否则 PASS。旧文本里写 `CRITICAL` 的地方，读作 `blocker`。

**报告是发现对象的数组**——不是 `{"findings": [...]}` 包装。

```bash
echo '[]' | python scripts/validate-findings.py            # smoke-test the harness first
python scripts/validate-findings.py review-report.json     # validate a real report
python scripts/validate-findings.py --id paper.tex 42 thm:main
```

### 确定性的发现 id —— 去重如何不再是模糊的

```
id = sha1("<file>:<line>:<locus>")
```

**在文件未改动期间**，同一个缺陷从每个透镜、每个会话都得到同一个 id——所以一轮内跨透镜去重是精确的。跨轮时修复者会编辑文件，从而挪动行号、也挪动 id；那就改按 `file` + `locus`（那个被命名之物——一个定理标签、幻灯片标题、函数）跨轮匹配（§3）。这让 `loop-until-dry` 保持诚实（当每个透镜都审过、且没有产出 `file` + `locus` 为新的发现时，一轮就是空轮），也让两振出局规则可检查——同一个 `file` + `locus` 熬过第 N 轮与第 N+2 轮，就升级给人，而不是被打第三次补丁。校验器重算每个 id 并拒绝任何与自身坐标不符的，所以 id 无法被编造。

### 每条发现都必须引用一条规则

`rule` 是必填的。**一条不引用任何成文规则或标准的发现只是意见**，而意见不能给提交设门禁。这是针对「被要求找漏洞的审阅者会在健全的工作里找出漏洞」这一实测倾向最便宜的一道防线。

### `failing_case` 是必填的

一个能打破该断言的具体配置，或那个确切缺失的假设。*「这里可以更清楚」*不能通过校验。

### `mechanical` 白名单

`mechanical: true` **仅**允许用于不会改变结果的修复：

- 一个错字、一个断掉的交叉引用、一个格式错误的引文键
- 一处格式或溢出修复
- 加一个缺失的标签或 docstring
- 一次没有外部调用方的重命名

**永远不是 mechanical：** 任何触及**估计目标**、**假设**、**设定**、**推断程序**、**样本定义**或**报告语言**的东西。那些交还给研究者。这与既有的升级规则是同一条边界。

### 两阶段，偏向反驳

审读遍提出；一个**独立的、偏向反驳的核验遍**裁决。只有 `verdict: "confirmed"` 的发现才发布。核验者给不出依据的发现被丢弃，而不是降级成警告。

### 在花掉审读成本之前先冒烟测试骨架

每个环境跑一次 `echo '[]' | python scripts/validate-findings.py`。一次量了一切、然后写不出一份合法报告的审读运行，等于把整轮白费了。

### 每个透镜的证据负担

一句泛泛的「提供证据」太弱。每个透镜都欠一份具体的证明：

| 透镜 | 负担 |
|---|---|
| `identification` | 点名那个假设，以及一个让它失败的设定 |
| `estimation` | 点名估计量，以及偏离其定义的那个确切步骤 |
| `inference` | 点名方差通道——聚类层级、bootstrap、自由度 |
| `numeric-claim` | 稿件里的值、输出里的值，以及容差 |
| `reproducibility` | 跑的命令及其输出 |
| `citation` | 支持或不支持该断言的那段引文 |
| `measurement` | 构念、代理变量，以及两者之间的落差 |
| `parity` | 两个产物，以及那个具体不同的元素 |
| `code-quality` | file:line，加上触发该缺陷的输入 |

### 「不算数」——压掉已知的误报

在核验之前施加：

- 一个**有文档、站得住脚的替代做法**是 `EXPLAINED`，不是缺陷。一个不同但有名字的选择（一种聚类小样本校正；一条带宽选择规则；一个 MC 种子）只记录，绝不「修复」。
- **为教学而做的刻意简化**不是实质错误。
- **散文口味**不是发现，除非它改变含义。
- 一条已被 `claim-reconcile` 标出的**过期断言**是一条发现，不是每个表面各一条。
- **HELD 清单**上的任何东西只记录，不处理。
