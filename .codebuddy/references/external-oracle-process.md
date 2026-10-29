# 外部裁判流程 —— Claude Code → 一位外部的边界模型审稿人

**2026-09-26 对 Oracle CLI 0.21.3 核对。** 如何为一篇论文、一个证明，或一份估计量实现，请到一位独立的前沿模型审稿人；以及——更重要的是——如何*裁定*它返回的东西。

> **有两样不同的东西都叫「oracle」。** 把它们分开。
>
> | 含义 | 它是什么 | 谁是它的真值 |
> |---|---|---|
> | **参考 oracle** | 一份规范实现的*固定检出版本*（例如某个发行提交上的 R `did`，摆在你移植版旁边） | **数字** |
> | **外部模型 oracle** | 另一家供应商的前沿模型充当审稿人 | **判断**——仅供参考 |
>
> 本文件讲的是第二种。第一种在 [`provenance-and-ground-truth.md`](provenance-and-ground-truth.md)。

---

## 1. 为什么要费这个劲

1. **一种你从自己的分叉里拿不到的独立性。** 另一家供应商的模型有不同的训练、不同的先验、不同的失败模式。分叉出的子代理共享你的那一套。
2. **它逼出一个证据门槛。** 下面的提示词契约要求审稿人给出一个*失败案例*，而不是一个观点。失败案例你可以裁定；对一种感觉，你只能同意或不同意。
3. **覆盖率变成一份清单，而不是一个样本。** 「检查几个证明」让覆盖率变成随机的。每轮指派若干命题，并集覆盖率才能到 100%。
4. **经济性。** 浏览器引擎跑在 ChatGPT 订阅上，不是 API 计费。正是这一点让几十次咨询变得负担得起。

**以及那条限制，同样大声地说出来：** *一致不等于确认。* 两个模型会在同一个错误答案上相互印证。外部裁判是**参考性的**；一条机械检查的优先级高于它。

---

## 2. 一次性配置

[Oracle CLI](https://github.com/steipete/oracle)（`@steipete/oracle`，MIT）把提示词加文件打包，驱动一个**专用浏览器配置**对 ChatGPT 操作——不需要 API key。

```bash
brew install steipete/tap/oracle        # or: npm install -g @steipete/oracle@latest
```

要求 Oracle ≥ 0.21、Node ≥ 24；用 `oracle --version` 检查。只用一种安装方式，不要两个都用。Oracle ≥ 0.18 不再复制你日常 Chrome 的 cookie——下面那个专用的 `--browser-manual-login` 配置文件是受支持的路径，它能挺过 ChatGPT 的 token 轮换，而不会把你从正常浏览器里登出。

首次运行会创建自动化配置文件，并等你登录：

```bash
oracle --engine browser --browser-manual-login \
       --browser-keep-browser --browser-input-timeout 120000 -p "HI"
```

然后在 `~/.oracle/config.json` 里一次性设好默认值：

```json
{ "engine": "browser",
  "model": "gpt-6-pro",
  "browser": {
    "manualLogin": true,
    "manualLoginProfileDir": "~/.oracle/browser-profile",
    "thinkingTime": "pro",
    "attachmentTimeoutMs": 900000,
    "inputTimeoutMs": 900000,
    "autoReattachDelayMs": 5000,
    "autoReattachIntervalMs": 3000,
    "autoReattachTimeoutMs": 60000,
    "archiveConversations": "never"
  } }
```

`thinkingTime: "pro"` 选中 ChatGPT 的 **Pro 投入档**，并且**失败即关闭（fails closed）**——如果选择器里确认不了 Pro，本次运行就中止，而不是悄悄用更便宜的档位提交。其他可接受的档位：ChatGPT 当前的标签 `instant | medium | high | extra-high`，以及旧名 `light | standard | extended | heavy`。`archiveConversations: "never"` 让会话线程活着以便追问。

### 目标（2026-09-26 核对——ChatGPT 的选择器变了就重新核对）

裁判模型是**随账号而异的**；每次咨询点名它，并记录实际跑的是哪个。

| 次序 | 目标 | 旗标 | 何时用 |
|---|---|---|---|
| 1 | **GPT-6 Pro** | `--model gpt-6-pro`（ChatGPT 在 Pro 投入下的「Latest」条目） | 你的 ChatGPT 账号在模型选择器里显示 **Latest**——即上面那份配置 |
| 2 | **GPT-5.6 Sol Pro** | `--model gpt-5.6-sol --browser-thinking-time pro` | Latest 不可用；这是模板自己 2026-08-23 那次门禁设计咨询跑的目标 |
| 3 | **API** | `--engine api --model gpt-6-astra --reasoning-mode pro` | 没有 ChatGPT 订阅。**按 token 计费——需要用户明确同意**；先跑 `oracle doctor --providers` |
| 4 | **手工** | `--copy-markdown --render` | 浏览器自动化不可用（见 §3） |

不要依赖遗留别名：自 0.18 起，`gpt-5.4-pro` 之类的旧 Pro 名会静默重路由到 GPT-5.6 Sol Pro。`--dry-run summary` 会在你花掉一次 30 分钟咨询之前打印解析出的 `target=`。

**依赖它之前先做冒烟检查：** `oracle -s smoke-check-now -p "Reply with OK."`——一次没有产出会话 URL 的运行从未发生过。对 API 运行，`oracle doctor --providers` 报告 key 与路由就绪度，且不打印机密。

---

## 3. 跑一次咨询

配置就位之后：

```bash
oracle -s did-proof-audit-r1 -p "$(cat prompt.md)" -f main.tex supplement.tex --files-report
```

| 旗标 | 用途 |
|---|---|
| `--files-report` | 每个附加文件的 token 成本——**永远用它**；浏览器 composer 有一道载荷悬崖（约 35k token），超过它什么都发不出去 |
| `--followup <slug>` | 重开那个确切的已保存会话；继承配置文件、模型，并校验之前的轮次 |
| `--browser-follow-up "..."` | 一次运行内多轮：回答 → *「质疑你的建议」* → *「最终决定，最小的安全下一步」* |
| `--models "gpt-6-astra,gemini-3.1-pro"` | 并行询问多家供应商（API 引擎；计费）；加上 `--allow-partial`，这样一个模型失败不会拖垮整次运行 |
| `--copy-markdown --render` | 组装好整包、手工粘进 ChatGPT——**浏览器自动化不可用**时的降级路径（没有自动化配置、登录过期、抓取坏了）。完全没有 CLI 时，退路是*契约*而不是工具：按 §4 拼好提示词，手工粘贴 |
| `oracle session <slug> --render` | 重新接上并取回一个已完成的回答 |
| `oracle session <slug> --harvest` | 在抓取失败或 Chrome 被关掉时，重读绑定的 ChatGPT 标签页并保存最新回答（`--live` 用来尾随一次仍在生成的运行） |
| `oracle status --hours 72` | 在断定任何东西丢失之前，列出近期会话及其状态 |
| `--browser-capture-provider-native` | 同时保存 ChatGPT 的逐字会话记录——这是「抓到的回答就是 ChatGPT 给出的回答」的证据 |

### 产物——证据住在哪里

```
~/.oracle/sessions/<slug>/
├── meta.json                 # status, model, full prompt, file list,
│                             # browser.runtime.tabUrl + conversationId
├── output.log
└── artifacts/transcript.md   # prompt, final answer, conversation URL
```

`browser.runtime.tabUrl` 是**发送已提交的信号**。没有 URL → 这次运行从未发生。

> **记录实际作答的是哪个模型。** 选择器随账号而异，而且会在你脚下变化；请求的别名不是证据。把运行里解析出的模型与投入（`--dry-run` 的 `target=` 行、会话的 `meta.json`，或对话头部）抄进归档的 `meta.json`，写成 `oracle.model`、`oracle.effort`、`oracle.transport` 与 `oracle.cli`——这正是 2026-08-23 那次咨询已经记录的字段。

> **把逐字记录归档进仓库——会话目录不是记录。** `~/.oracle/sessions/` 是本机的、未纳入版本控制，而且再来一次 `--force` 重启就会被覆盖。把每次咨询的 `artifacts/transcript.md` 与它的 `meta.json`（里面带着确切的提示词、文件清单、会话 URL）复制进一个带日期的目录：`quality_reports/oracle_audits/YYYY-MM-DD_<topic>/`。此后**任何依赖某次咨询的断言都引用归档的逐字记录**，绝不是从会话记忆里回忆出的「oracle 说过」——§5 的断言记录会点明那个路径。一次没人能重开的咨询是轶事，后来的读者分不清一条已裁定的发现与一条凭记忆复述的发现。

---

## 4. 提示词契约——逼出证据，而不是结论

每一条异议都必须带上：

- **确切的位置**（章节／公式／页码 + 一小段引文），
- **一句话的缺陷**，
- **一个失败案例**——一个能打破该断言的具体设置，或那个确切缺失的假设。

要求审稿人给每条发现**分类**——*false statement · proof gap · overclaim · scope/consistency · exposition*——并标*致命 · 重大 · 次要*。要求它说明这条发现关乎**哪一个可信度问题**（§6）。指示它**算可算的东西**：在小规模的对抗式设计（截断、原子、设定错误）上评估总体对象，并给出算术。那是对一篇计量经济学论文产出最高的一类攻击。

另有两款与其余同样重要：

> **被堵死的路线要诚实。** 如果从所给的东西里得不出结论，就确切说出缺什么——绝不说「这是标准的」。

> **不做产出表演。** 「没有新的已确认缺陷」是一个有效且有用的答案。为了显得有产出而臆造一条边缘发现，比沉默更糟。

第二条之所以存在，是因为一个被要求找漏洞的审阅者，会在健全的工作里也找出漏洞。

### 覆盖清单——绝不让审稿人抽样

维护一份**命题清单**（每个定理／命题／引理按标签）和一份跨轮的**覆盖率台账**。每一轮*指派*要审计什么，并要求审稿人列出它实际核验了什么。轮换，使并集达到 100%，权重向最新／覆盖最少／风险最高的倾斜。**先在内部做穷尽覆盖**，这样外部裁判是*确认，而不是发现*——更便宜也更锋利。

### HELD 清单

把既有决定带进每一份提示词：*「不要重新争辩上面已定的判定、类别架构、R 一致性约定或行数。」* 重新提起 HELD 项的发现**只记录，不处理**。

---

## 5. 裁定——绝不直接吞下

Oracle 的发现是**候选**，不是判定。

1. **拿每一条发现去对照真实文本。** 打开被引的位置。那个假设在别处出现过吗？那个失败案例在所述条件下真的会发生吗？判定：**CONFIRMED / REFUTED / DOWNGRADED**。
2. **先做机械检查。** 如果一条发现是可算的——一个积分、一个恒等式、一个反例、一次模拟——就算它。*Oracle 同意你自己的读法不算独立确认。*
3. **过滤 HELD 清单。**
4. **成批修复。** 一次性应用**全部**已确认的修复，重新核验，然后跑**至多一轮**确认。不要每条发现一轮地滴灌。
5. **断言记录**每一个循环：修了什么（位置 + 证据）、什么被 REFUTED 及原因、什么仍未解决、哪些决定是你的。

**收敛：** 当一次确认运行没有返回新的已确认正确性缺陷——只有 HELD 项和表达口味——循环就结束了。停止发新轮。

---

## 6. 把五个可信度问题分开

一个问题的证据**永远不能**为另一个问题结清：

| 问题 | 由谁回答 | *不*能确立 |
|---|---|---|
| **可复现性**——代码能跑并产出报告的数字吗？ | `/audit-reproducibility`、护照 | 估计量是对的 |
| **实现保真度**——代码实现的是它声称的估计量吗？ | 对一个固定的参考 oracle 做差异审计 | 估计量表现良好 |
| **统计表现**——它在有限样本里表现如何？ | `/simulation-study`、覆盖率对真值 | 度量是有效的 |
| **度量效度**——变量捕捉到了那个构念吗？ | 领域审读、数据文档 | 因果断言成立 |
| **识别／因果凭据** | 设计、敏感性统计量、伪证检验 | 关于代码的任何事 |

把一次绿色的可复现性检查读成一个已验证的因果断言，是 AI 辅助实证工作最常见的一种出错方式。

---

## 7. 血泪换来的机械细节

| 失败 | 防线 |
|---|---|
| 云同步文件（Dropbox/iCloud）读到一半脱水，上传出**损坏**的副本 | 在**同一次 shell 调用**里复制到**本地**草稿区，然后核验 `pdfinfo` 页数 + 对最后一页做 `pdftotext` |
| 载荷超过 composer 悬崖 → 什么都没发出去 | `--files-report`；拆成聚焦的单一决策运行（回答本来也更锋利） |
| 抓取超时 ≠ 运行丢失 | 自动重连会恢复到 `artifacts/transcript.md`——**宣布失败之前先看产物** |
| 重复的提示词已在运行 | 除非 `--force` 否则阻止；**优先重连而不是重启** |
| 分离运行上的 CLI 超时 | `oracle session <slug>`——**不要**重跑 |
| 抓错标签页 | 读内容**之前**先核实线程身份；对可疑抓取加一条警告头做隔离 |
| 并发 | 每个配置文件最多 3 个 ChatGPT 标签页的软上限；第 4 个调用方等待。WorkBuddy 与 Codex 同时咨询时这一点很要紧 |
| 一个能看见改动内容的裁判会给那份 diff 打分 | **把裁判蒙上眼**——做独立上下文比较之前，剥掉修订标记 |

---

## 交叉引用

- [`verification-ladder.md`](verification-ladder.md) —— 外部裁判在其他检查之间所处的位置
- [`provenance-and-ground-truth.md`](provenance-and-ground-truth.md) —— 参考 oracle、固定的 SHA、净室边界
- [`orchestration-schemas.md`](orchestration-schemas.md) —— FINDING / SCORECARD 契约
- [`.codebuddy/rules/orchestrator-protocol.md`](../rules/orchestrator-protocol.md) —— 由 oracle 来确认的那套内部循环
