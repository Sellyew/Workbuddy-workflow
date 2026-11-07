# 定时与后台例程

工作流中「循环优先」的那一半：那些应当*按计划*运行、并且只在找到东西时才现身的反复性学术
杂务——而不是在你想起来去跑它们的时候才现身。

**核心原则：失败时推送、成功时沉默；无人值守任务只提出动作，不替人执行不可逆操作。**
机制断言及其证据级别见 [`platform-facts.md`](platform-facts.md) 的「调度」节。

## 三种原语，先分清再选

| | `CronCreate`（默认） | `CronCreate`（`durable: true`） | automation |
|---|---|---|---|
| 日程写法 | 5 段 cron，**本地时间**，如 `30 6 * * *` | 同上 | RFC 5545 RRULE，或一次性 `scheduledAt` |
| 跑在哪 | 当前会话里 | 一个**专用任务会话** | 你指定的工作目录（`cwds`，绝对路径） |
| 挺过会话结束 | **否**（默认不落盘） | **是**——落 `.codebuddy/scheduled_tasks.json` | 是（平台侧持久） |
| 挺过客户端重启 | 否 | 是 | 是 |
| 到期后 | 随会话消失 | 循环任务 3 天后自动过期；一次性任务触发即删 | 按 `validUntil` / 手动暂停 |
| 谁能看见它 | 你，在会话里 | 你，在会话里；任务文件位于工作目录且默认被忽略 | 界面里的自动化列表 |
| 观测级别 | L2 | L2 | **L3**（实测见下） |

三条选择规则：

- **会话内的短延时轮询**（「我干活的时候每 5 分钟查一次构建」）→ `CronCreate` 默认模式。
- **必须活过今晚、但日程简单** → `CronCreate(durable: true)`。它落盘在
  `.codebuddy/scheduled_tasks.json`。那个文件是**本机状态**（它是这台机器的绝对路径加上
  一个人的作息），本仓库已把它加进 `.gitignore`；你 fork 时如果换了 `.gitignore`，记得补回去，
  否则「我每天早上 6 点扫一遍」会提交给所有 fork 的人。
- **需要给人看的日程、指定目录、指定权限档位或连接器** → automation（`automation_update`）。

### 实测：automation 跑在真实工作树上

可重跑探针：在 `<repo>` 中创建一个**未被 git 跟踪、也未被 gitignore** 的临时文件，建一条
一次性 automation，让它在指定工作目录执行 `pwd`、读取该文件、运行 `git status --short`、
`git rev-parse HEAD` 与 `git rev-parse --is-shallow-repository`，把输出写入本机记录。运行后删除
临时文件。脱敏结果摘要：

```text
pwd                                      → <repo>
Read(<probe-file>)                        → 成功，读到完整内容
git status --short                       → 可见未跟踪文件与未提交修改
git rev-parse HEAD                       → <commit>（与本地一致）
git rev-parse --is-shallow-repository    → false
```

这证明 automation **不是全新克隆，不是隔离沙箱，而是当前真实工作树**。无人值守作业能读到
`data/` 下未提交的内容，也能看到工作树中的未提交修改——这是后文数据护栏的依据。

## 持久化与本地可见性

`CronCreate` 默认随会话结束；`durable: true` 则把作业落盘，由专用任务会话执行并挺过重启。
三种原语都运行在本机，选择时必须考虑以下后果：

1. **任务能访问本地工作树。** 它们看得见未提交文件，不能把「任务够不到数据目录」当作数据防线。
2. **本地可见性要求机器与客户端保持运行。** 需要持久执行时必须启用相应的 durable 或 automation
   机制，并接受其运行环境要求。
3. **受限数据需要显式护栏。** 无人值守作业能读到 `data/` 下的微观数据，因此必须遵守
   [`confidential-data.md`](../rules/confidential-data.md)：无人值守不碰受限数据，除非有人把关。

## 无人值守时人不在场——这是本平台最要紧的一条

无人值守关卡由平台强制执行，其实现方式与会话内交互不同：

- **Automation 会话里问不到人。** 引擎对 `CODEBUDDY_SESSION_TYPE=automation` 的会话直接把
  双通道交互判为 `automation session synthesises an instant deny`——不是「等人二十分钟」，
  是**立即拒绝**。任何靠 `AskUserQuestion` 停顿等确认的技能，在无人值守时会立刻失败或被绕过。
- **需要审批的工具在后台跑不了。** 引擎把这个状态叫 `background-automation-no-approval-ui`：
  没有批准界面，所以依赖审批的能力被禁用。要提权就在**创建任务时**用 `permissionMode` 定好，
  不能指望运行到一半弹个窗。

这两条合起来给出一个设计约束，`/triage-inbox` 早就在遵守：

> **关卡不能是「问一句」，关卡必须是「不做出不可逆的动作」。**

所以那些无人值守的技能把产物写成一份**提议**（草稿、待确认的动作清单、待发的回复），
把执行留给你回来点。这不是保守，这是这个平台唯一能成立的做法。

## 常驻例程

| 例程 | 间隔 | 它做什么 | 何时惊动你 |
|---|---|---|---|
| **可复现性漂移** | 每晚 | 对着护照重跑 `/audit-reproducibility`；对过期的断言做差异 | 任何 FAIL（非 EXPLAINED） |
| **文献增量** | 每周 | 对你保存的题目跑 `/lit-review` 扫读；与上周做差异 | 出现新的直接相关工作 |
| **记忆提升** | 每月——**一个提醒，不是例程** | 你在本地会话里自己跑 `/promote-memory`：它由用户调用，候选住在自动记忆里，定时任务看不到 | 有条目升级进 MEMORY.md |
| **收件箱分诊** | 每日／工作日 | `/triage-inbox`——审稿请求、R&R 截止日、合作者的事。只起草、不发送，所以适合无人值守 | 提出一个动作（始终由人把关） |

**定时任务无法触发一个由用户调用的技能。** 标了 `disable-model-invocation: true` 的技能
（例如 `/triage-inbox`、`/promote-memory`）不会因为一个定时任务的提示词里点了它的名字就运行
——定时任务跑的是模型。对这类技能，把提示词写成「读 `.codebuddy/skills/<name>/SKILL.md` 并
照它做」，或者你自己手动跑。

## 设置一个

**普通例程用 automation**，两条入口等价：界面里新建，或者让我在建任务时调 `automation_update`。
下面是每晚可复现性检查的样子——注意它的提示词里写清了三件事：跑什么、什么算失败、
以及不许动什么。

```text
每天 06:00 跑一次可复现性漂移检查：
读 quality_reports/passport.*，对每一条 claim 核对 source_file / output_file 的 mtime
是否新于 last_verified_on。有 FAIL（非 EXPLAINED）就列出受影响的表并写明复现命令；
全部通过就只写一行日志，不要报告。

不要提交、不要 push、不要修改任何 claim 的 last_verified_on——那是我的判断，不是你的。
```

**会话内的轮询用 `CronCreate`**，因为你不希望它活过这个会话：

```text
CronCreate(cron: "*/5 * * * *", prompt: "查一次构建状态，只在失败时报告")
```

`durable: true` 只在你要它挺过重启时才加，理由见上一节。

`scripts/nightly-repro-check.sh` 仍然有用：它是这条检查的**零依赖**版本，不经过任何会话，
跑在真正的机器 cron 或 systemd timer 上。要「机器关着也不管」，就它是唯一选择。

## 失败时推送，成功时沉默

**一个每晚报「一切正常」的作业，训练你忽略它。** 等它真报出什么的时候，它已经当了一个月的
噪音，你一眼扫过去就略过了。

定时检查**只在需要人时**通知：失败 → 带上失败的门禁、产物路径、复现命令；成功 → 写日志，
什么都不说；**没跑 → 这是失败，不是沉默**。一个静默死掉的调度器，与一个报告干净的调度器
无法区分，所以心跳缺失要像红灯门禁一样大声告警。

推送通道需要显式配置：

- 引擎里有 `automation.run.failure_detail` 遥测事件，以及两个**企业微信 webhook** 设置键
  （`automation.wecomWebhookUrl`、`automation.wecomPushConfig.webhookUrl`）。
- 也就是说：**不配 webhook，就没有推送**。产物只落在那次运行的会话记录里，等你自己去翻。
- 这既是限制也是好事——「没配就没人被打扰」比「默认推送但没人看」更容易想清楚。

## 事件驱动，不只是定时

每晚的可复现性作业是*兜底*。*即时*信号是 [`claim-reconcile`](../hooks/claim-reconcile.py)
这个 PostToolUse 钩子：一个分析脚本或 `output/` 产物一改，它就把依赖它的稿件断言标记为
可能过期，并把你指向 `/audit-reproducibility`——这样你在分析过程中就抓到漂移，而不是第二天
早上。对*外部*的重新生成（你在 WorkBuddy 之外跑了 `Rscript`），harness 的 `FileChanged`
钩子事件可以驱动同一项检查——引擎支持它（`platform-facts.md` 的「钩子」节），但本仓库**还没
接**；如果你的工作流在工具层之外重新生成输出，这是值得接的一个。

## 交叉引用

- [`platform-facts.md`](platform-facts.md) —— 上面每一条机制断言的出处与观测级别。
- [`.codebuddy/hooks/claim-reconcile.py`](../hooks/claim-reconcile.py) —— 事件驱动的对账钩子。
- [`.codebuddy/rules/replication-protocol.md`](../rules/replication-protocol.md) —— 可复现性例程检查什么。
- [`.codebuddy/rules/confidential-data.md`](../rules/confidential-data.md) —— 为什么受限数据附近的无人值守运行仍要人的关卡。
