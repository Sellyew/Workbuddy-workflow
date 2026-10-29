# 平台事实台账

**这个文件只有一个用途：让每一句「本平台支持 / 不支持 X」都钉在可重跑的证据上。**

它存在的理由是一次事故。v3.0.0 依据 `P1_migration_verification.md` 的 T13 一行
（「`plansDirectory` / `statusLine` 暂不支持」）删掉了 `.codebuddy/settings.json` 的
`permissions` 块，然后仓库里写了四份文档解释它为什么该被删。复测结果：`permissions`
引擎读、`statusLine` 引擎也读（渲染层不消费），只有 `plansDirectory` 是真的零命中。
**错误起点不是判断失误，是没有出处的判断被当成事实继承了四次。**

## 使用规约

1. 写「本平台不支持 X」之前，先查这张表。表里没有 → **先测**，测完加行，再写文档。
2. 不许从审计报告、CHANGELOG 或项目记忆里继承结论。只认这张表和它的证据命令。
3. 行上带 ⏳ 的，文档里不能写「支持」，只能写「引擎实现存在，运行时未观测到」。
4. 平台升级后，带 ⏳ 和 L2 的行必须重测——事实有保质期，日期就是保质期。

## 观测级别

| 级别 | 判据 | 能支撑的措辞 |
|---|---|---|
| **L0 零命中** | 在**正确的包**里搜不到，且换过引号形态与大小写变体 | 「不支持」「没有这个键」 |
| **L1 键存在** | 出现在白名单 / schema / 枚举里 | 「引擎认这个键」（仅此而已） |
| **L2 代码路径** | 找到读它、或发射它的那个函数 | 「会读」「会触发」 |
| **L3 运行时** | 本机真实触发过，留下可引用的输出 | 「生效」 |
| **⏳** | 只到 L2，没有运行时观测 | 「实现存在，未观测到」 |

**L1 与 L2 的区别是这道台账的核心。** `statusLine` 在引擎字符串里出现 8 次（L1 充分），
但没有一处消费它（L2 不成立）；`effort` 在 schema 里根本没有位置（L0），而在会话配置里
出现 6 次（那是另一个东西）。只看命中数会得出相反的结论。

## 环境

本机 `WB=/d/workbuddy/resources`，客户端版本 `37.10.3-42`（2026-10-27 构建）。
事实分居三个包，**搜错包会得到假的零命中**：

| 问题类型 | 该去哪个文件找 |
|---|---|
| 设置键、桌面端渲染 | `$WB/app.asar` |
| 钩子发射、子代理派发、模型解析 | `$WB/app.asar.unpacked/node_modules/@genie/agent-harness/cli/dist-server/shared.cjs`、`$WB/app.asar.unpacked/cli/dist/codebuddy-lite-wb.mjs` |
| 事件枚举、agent 元数据 schema | `$H/lib/runtime/component-protocol.js`、`$H/lib/agent-registry/schemas.js`（`H=$WB/app.asar.unpacked/node_modules/@genie/agent-harness`） |

## 事实表

### 配置与权限

| 键 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| `permissions` | 顶层键被读；`deny` 经 `extractWholeToolRules` 过滤工具调用 | L2 | `grep -a -o permissions "$WB/app.asar" \| wc -l` → 695 | 2026-10-30 |
| `permissions.allow` | 生效（放行清单） | L2 | 同上；`settingsManager.get("permissions")` | 2026-10-30 |
| `plansDirectory` | **不支持**。计划固定落 `~/.workbuddy/plans/`，没有可配置项 | L0 | `grep -a -o plansDirectory "$WB/app.asar" \| wc -l` → 0 | 2026-10-30 |
| `statusLine` | 引擎认这个键，**桌面渲染层不消费**。8 次命中全是 `statusLine: 'HTTP/1.1 204 No Content'`（CORS 头） | L1 | `grep -a -o '.\{60\}statusLine.\{60\}' "$WB/app.asar"` | 2026-10-30 |
| 权限档位 | 界面只有两档：`sandbox.defaultPermission`（默认权限）/ `sandbox.fullAccessPermission`（完全访问权限）。`Shift+Tab` 与 `--permission-mode` 不存在 | L3 | 模式选择器可见；命令在包内零命中 | 2026-10-30 |

### 钩子

| 项 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| 事件集合 | 引擎认 **28 个**事件，不是上游那 9 个 | L2 | `grep -ao 'HOOK_EVENT_NAMES=new Map(\[.\{300,1200\}' "$H/lib/runtime/component-protocol.js"` | 2026-10-30 |
| 已注册的 7 个 | `PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `SessionStart` / `PreCompact` / `Stop` / `Notification` **全部有发射点** | L2 | `grep -ao 'executeHooks([A-Za-z_]*\.mb\.[A-Z_]*)' "$H/cli/dist-server/shared.cjs" \| sort -u` | 2026-10-30 |
| `PreCompact` | 有发射点，两条路径：`executeManualPreCompactHooks`（手动压缩）与 `executeClassicPreCompactHooks`；压缩后另有 `PostCompact` | L2 ⏳ | 同上；手动 `/compact` 可复现 | 2026-10-30 |
| `Notification` | 有发射点（`SESSION_LIFECYCLE` 分支） | L2 ⏳ | 同上 | 2026-10-30 |
| 可用但未接 | `SessionEnd` · `SubagentStart` · `SubagentStop` · `PostToolUseFailure` · `FileChanged` · `PermissionDenied` · `FinalStop` · `PostCompact` · `ConfigChange` · `CwdChanged` · `InstructionsLoaded` · `WorktreeCreate/Remove` | L2 | 同上 | 2026-10-30 |

**⏳ 的含义要说清**：`PreCompact` 与 `Notification` 此前被记为「尚未验证」，读起来像
「可能不支持」。实际是发射点明确存在、只是没在本机触发过——这两件事在文档里必须区别对待。

### 技能 / 规则 / 代理

| 项 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| `.codebuddy/skills/` | 原生发现，`/name` 可调 | L3 | `P1` T4；本会话技能列表来源即此目录 | 2026-10-29 |
| `$ARGUMENTS` | 原样带入技能正文 | L3 | `P1` T5 | 2026-10-29 |
| `.codebuddy/agents/` | 目录**实时加载**，会话内新建即可派发 | L3 | `P1` T6（`ping` 新建即通） | 2026-10-29 |
| `rules` 的 `paths:` | 按路径条件注入；只碰 `*.md` 时不注入 | L3 | `P1` T2 | 2026-10-29 |
| agent 的 `model:` | **会被解析并用于子代理会话**：`resolveAgentModel` 依次读 `CODEBUDDY_CODE_SUBAGENT_MODEL` → 元数据 `model` → `agentManager.resolveModel`；`default` / `inherit` 表示继承。合法值就是 `default` / `lite` / `reasoning` | L2 | `grep -ao 'async resolveAgentModel(t){.\{0,700\}' "$WB/app.asar.unpacked/cli/dist/codebuddy-lite-wb.mjs"`；`agentMetadataSchema` 含 `model` | 2026-10-30 |
| agent 的 `effort:` | **不被读**。元数据 schema（`name`/`description`/`path`/`source`/`model`/`tools`/`color`）里没有它，Effect Struct 会把未知键剥掉；harness 中 `effort` 的 6 次命中全在会话级 `server-config.js`。`check-spec-conformance.py` 也已把它列进 `INERT_FIELDS` | L0 | `grep -ao 'agentMetadataSchema=e.Struct({.\{0,600\}' "$H/lib/agent-registry/schemas.js"`；`grep -rao effort "$H/lib/" \| wc -l` → 6 | 2026-10-30 |

### 调度

`$H` = `$WB/app.asar.unpacked/node_modules/@genie/agent-harness`，`$S` = `$H/cli/dist-server/shared.cjs`。

| 项 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| `CronCreate` / `CronList` / `CronDelete` | **存在**。`CronCreate` 取 5 段 cron（**本地时间**，`M H DoM Mon DoW`）、`prompt`、`recurring`（默认 true）、`durable`（默认 false）。循环任务「触发到删除、或 3 天后自动过期」；`recurring: false` 触发一次即自删 | L2 | `grep -ao "describe('Standard 5-field cron expression.\{0,1400\}" "$S"` | 2026-10-30 |
| `durable: true` | **落盘并挺过重启**：`Persisted to {project}/.codebuddy/scheduled_tasks.json and executed in a dedicated task session`；默认 `false` 为 `Session-only (not written to disk, dies when session exits)` | L2 | `grep -ao 'Persisted to.\{0,150\}' "$S"` | 2026-10-30 |
| automation 是**一次正常会话** | 运行时置 `CODEBUDDY_SESSION_TYPE=automation`；会话类型枚举里有独立的 `Automation` 项 | L2 | `grep -ao 'function isAutomationSession.\{0,80\}' "$S"` | 2026-10-30 |
| automation 参数白名单 | `prompt` · `scheduleType` · `rrule` · `scheduledAt` · `validFrom` · `validUntil` · `cwds` · `permissionMode` · `connectorIds` · `skills` · `expertId` · `modelId` | L2 | `grep -ao 'let eX=\["prompt","scheduleType".\{0,160\}' "$S"` | 2026-10-30 |
| `cwds` | 必须是**绝对路径**（引擎校验 `each cwd must be an absolute path`），且有数量上限 | L2 | `grep -ao 'each cwd must be an absolute path.\{0,30\}' "$S"` | 2026-10-30 |
| 无人值守**问不到人** | automation 会话的双通道交互返回 `automation session synthesises an instant deny`——**立即拒绝，不是等待** | L2 | `grep -ao 'automation session synthesises an instant deny' "$S"` | 2026-10-30 |
| 后台自动化**没有批准界面** | 需审批的能力在后台 automation 里以 `background-automation-no-approval-ui` 为由被禁用；提权只能创建时用 `permissionMode` | L2 | `grep -ao 'background-automation-no-approval-ui' "$S"` | 2026-10-30 |
| automation **跑在真实工作树** | `pwd` = 仓库根、读到未跟踪文件、`git status` 里出现 `?? probe/` 与当次未提交的 ` M`、HEAD 与本地一致、非浅克隆。**不是全新克隆，不是隔离沙箱** | **L3** | 探针输出全文见 [`scheduled-routines.md`](scheduled-routines.md)「实测」节 | 2026-10-30 |
| 失败上报 | 有 `automation.run.failure_detail` 遥测事件；推送通道是**企业微信 webhook**，设置键 `automation.wecomWebhookUrl` / `automation.wecomPushConfig.webhookUrl`。不配 = 没有推送 | L1 | `grep -ao 'automation\.wecom[A-Za-z.]*' "$S"` | 2026-10-30 |
| `/schedule` 斜杠命令 | **不存在**。29 次命中全是 API 路由（`/v2/as/scheduler/tasks`、`/schedule/todo-source`）与打包文件名（`schedule-host-*.js`）；带引号的 `"/schedule"` 零命中 | L0 | `grep -aoF "/schedule" "$WB/app.asar" \| wc -l` → 29；`grep -aoF '"/schedule"' "$WB/app.asar" \| wc -l` → 0 | 2026-10-30 |
| 云端 Routines | **不存在**：`Routines` 在 `app.asar` 与 `$S` 均零命中；`claude.ai` 连接器语义在 `$S` 零命中 | L0 | `grep -acF "Routines" "$WB/app.asar"` → 0 | 2026-10-30 |
| `.codebuddy/routines/` | 只在一份「agent 启动时加载的配置路径」清单里出现 2 次；`$H/lib/` 与 `app.asar` 均零命中，未见发现逻辑 | ⏳ | `grep -rao routines "$H/lib/" \| wc -l` → 0 | 2026-10-30 |
| `.codebuddy/loop.md` | `app.asar` 有 4 次命中，语义未核（可能是 `/loop` 的状态文件） | ⏳ | `grep -aoF "loop.md" "$WB/app.asar" \| wc -l` → 4 | 2026-10-30 |

## 已知不一致

### 已处理

1. ~~18 个 agent 文件带 `effort:`~~ —— **2026-10-30 已删**。`normalize-model-tiers.py`
   现在对代理与技能一视同仁（此前代理走 `drop_effort=False` 分支，留着这个字段）。
   同时重写了 [`agent-fleet.md`](agent-fleet.md)：四节标题从「Opus 层 / Sonnet 层，effort: X」
   改成三档，删掉「投入」一列，并写明 `default` 内没有强度旋钮、审读与应用两组现在同档。
   一并修掉三处把它当活字段用的地方：`templates/skill-template.md` 的字段表、
   `new-skill` 的 frontmatter 清单、`deep-audit` 的模型分工（那段还提到本平台没有的
   「Fable 层」与「先加努力度」）。**教训**：`model-routing.md` 早在迁移时就写对了
   （「本平台没有 effort 字段」），错的是它周围没人去删字段——一条正确的规则，挡不住
   三个仍然照旧写的文件。


2. ~~[`scheduled-routines.md`](scheduled-routines.md) 整篇指向不存在的机制~~ —— **2026-10-30 已重写**。
   重写前先把「上游那三件套到底哪几件在这里存在」逐条落回引擎，结果推翻了原来的判断：
   `CronCreate` / `CronList` / `CronDelete` **是存在的**（5 段 cron、本地时间；`durable: true`
   落 `.codebuddy/scheduled_tasks.json` 并挺过重启，由专用任务会话执行）；`/schedule` 斜杠命令
   **不存在**（29 次命中全是 API 路由与打包文件名）；云端 `Routines` **不存在**（两个包均零命中）。
   上一版写「本平台没有对应入口」，把三件事判成了一件事，而且当时**根本没搜过**——
   `CronCreate` 有 12 次命中。实测补上最后一块：automation 跑在真实工作树，看得见未跟踪与
   **当次未提交**的文件（L3，探针输出见 `scheduled-routines.md` 的「实测」节）。
   连带改了 `TROUBLESHOOTING.md` 的同一条错断言（原文「即便 `durable: true` 也救不了你」）、
   `README.md`、`MEMORY.md` 的 `[LEARN:scheduling]`、`triage-inbox` 的三处、指南的「无人值守
   运行」一条、`audit-pet-peeves.md` 第 17 条、`nightly-repro-check.sh` 的头注释。
   **教训**：「没搜过」和「搜过没有」必须分开写。原来的措辞是「尚未在引擎内定位」——它诚实地
   描述了「我没查」，却被下一层读成了「查了，没有」，与 T13 那次是同一种误读。

### 未处理

2. **`README.md`「2026 年的能力」还剩三条未核的上游断言**：`worktree.baseRef` 的
   `fresh` / `head`、内置技能清单（`/fewer-permission-prompts`、`/team-onboarding`、
   `/autofix-pr`、`/powerup`、Ultraplan、`/loop`）、以及「高级代理配置」里的 `maxTurns`。
   其中 `effort`、`effort.level` 与五档权限三处已在 2026-10-30 按本台账改正。
   **待办**：逐条落到 L0–L3，核不了就删。
3. **技能级 `model:` 两处说法相反。** [`model-routing.md`](../rules/model-routing.md)
   说「技能用同样的字段在 `SKILL.md` 的 frontmatter 里设定」，而
   `check-spec-conformance.py` 把 `model` 列在 `INERT_FIELDS` 里、会对写了它的技能发
   「无对应语义」告警。目前没人被坑到——63 个技能里 0 个写 `model:`——但两处必须统一。
   **待办**：用一次带 `model:` 的技能实测它是否影响运行时，再改错的那一边。
4. **`.codebuddy/routines/` 与 `.codebuddy/loop.md` 是两条悬着的字符串**（见「调度」节的 ⏳ 行）。
   前者只出现在一份配置路径清单里、无发现逻辑；后者在 `app.asar` 有 4 次命中、语义未核。
   **待办**：要么找到消费点升到 L2，要么在文档里明说它们没有实现。

## 方法教训（下次还会犯，所以写下来）

1. **零命中要先怀疑探针。** `grep -o "\"permissions\"" app.asar` 返回 0，`grep -o permissions`
   返回 695。只测一种引号形态，就会把「支持」写成「不支持」。
2. **在正确的包里找。** 在 harness 里搜 `permissions` 得 0，不能推出「不支持」——设置管理器
   在 `app.asar` 里。搜错包得到的零命中，和真的不存在长得一模一样。
3. **键存在 ≠ 它被用。** `statusLine` 8 次命中，全是 HTTP 状态行；`effort` 有 6 次命中，
   全在会话级配置里，跟逐代理字段无关。命中数是 L1 证据，不是 L2。
4. **测量方式的缺陷会被写成平台的缺陷。** P0 判 agent `model:` 为「部分支持」，真实原因是
   模型不自报身份。结论一旦写进表格，就没人再回头问「这是平台的问题还是探针的问题」。
