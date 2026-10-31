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
但没有一处消费它（L2 不成立）。反过来，`effort` 在代理**列表** schema 里没有位置，
却在加载器、`--effort` 旗标与 `/effort` 命令里各有一条消费路径——**只看命中数、
或者只查一个 schema，都会得出与事实相反的结论**，两种错法这道台账都犯过。

## 环境

本机 `WB=/d/workbuddy/resources`，客户端版本 `37.10.3-42`（2026-10-27 构建）。
事实分居三个包，**搜错包会得到假的零命中**：

| 问题类型 | 该去哪个文件找 |
|---|---|
| 设置键、桌面端渲染 | `$WB/app.asar` |
| 钩子发射、子代理派发、模型解析 | `$WB/app.asar.unpacked/node_modules/@genie/agent-harness/cli/dist-server/shared.cjs`、`$WB/app.asar.unpacked/cli/dist/codebuddy-lite-wb.mjs` |
| 事件枚举、agent 元数据 schema | `$H/lib/runtime/component-protocol.js`、`$H/lib/agent-registry/schemas.js`（`H=$WB/app.asar.unpacked/node_modules/@genie/agent-harness`） |

### 宿主工具链

下面几条不是 WorkBuddy 的事实，是**这台机器能不能把工作流跑起来**的事实——同一类坑：
装好了、命令存在、错误信息却在说别的事。

| 事实 | 观测级别 | 证据 | 日期 |
|---|---|---|---|
| kpathsea 的路径分隔符**平台相关**：POSIX `:`，**Windows 版 TeX Live `;`**。且 `TEXINPUTS` / `BIBINPUTS` **必须以分隔符结尾**——否则默认搜索路径（含 `.`）被整个替换掉 | L3 | Windows 上 `TEXINPUTS="../Preambles:"` → `! I can't find file 'HelloWorld.tex'`（文件就在）；`TEXINPUTS="../Preambles;"` → 4 页；`TEXINPUTS="../Preambles"` 同样失败；`TEXINPUTS=""` → 4 页 | 2026-10-31 |
| 本机 `xelatex` = TeX Live 2026（Windows 构建），`quarto`、`pdftotext`（poppler）在 PATH；**没有 R / Rscript** | L3 | `xelatex --version`；`which Rscript R` → not found | 2026-10-31 |
| `quarto render` 会去取 Google Fonts。代理不通时它打印 `ProxyConnectException … 502`，但**仍然产出 HTML** | L3 | 本次渲染：`(ProxyConnectException "fonts.googleapis.com" 443 … 502)` 之后紧接 `Output created: workflow-guide.html` | 2026-10-31 |

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
| `PreCompact` | **会自动触发**，`trigger` 为 `auto`。2026-10-30 本机两次真实压缩各写出一份 `pre-compact-state.json`（06:25:55 / 06:30:34），`plan_path` 为 `null` 是因为那两个会话确实没有在用的计划 | **L3** | `cat ~/.workbuddy/sessions/*/pre-compact-state.json`；文件带 `"trigger": "auto"` 与 ISO 时间戳 | 2026-10-30 |
| `Notification` | 有发射点（`SESSION_LIFECYCLE` 分支），**但仓库这一侧到 2026-10-30 为止从未真正执行过**：`notify.sh` 是 shell 脚本，而 `hook-runner.sh` 当时对一切钩子都 `exec $PY`，于是每次都是 `SyntaxError: unmatched ')'`。已改为按扩展名分派 | 发射 L2 ⏳／handler 已修 | `bash .codebuddy/hooks/lib/hook-runner.sh notify.sh <<< '{"message":"x"}'` → exit 0 且写出 `notifications.log` | 2026-10-30 |
| 可用但未接 | `SessionEnd` · `SubagentStart` · `SubagentStop` · `PostToolUseFailure` · `FileChanged` · `PermissionDenied` · `FinalStop` · `PostCompact` · `ConfigChange` · `CwdChanged` · `InstructionsLoaded` · `WorktreeCreate/Remove` | L2 | 同上 | 2026-10-30 |

**⏳ 的含义要说清**：`PreCompact` 与 `Notification` 此前被记为「尚未验证」，读起来像
「可能不支持」。实际是发射点明确存在、只是没在本机触发过——这两件事在文档里必须区别对待。
2026-10-30 的两次真实压缩把 `PreCompact` 抬到了 L3；`Notification` 仍是 ⏳，但它现在会落盘
（`quality_reports/session_logs/notifications.log`），下一次触发就能自己证明，不必再靠猜。

**一条更贵的教训**：L2「有发射点」不等于 L3，但 L2 也不保证 handler 能跑。`Notification`
的发射点一直在，而它的**处理器**从未成功执行过——中间隔着 `hook-runner.sh` 的解释器分派。
判断「这个钩子在工作吗」要连着看两段：平台发射了没有，注册的命令到没到达钩子文件。后者由
`scripts/check-hooks.py` 的 `check_wiring()` 检查，它对每条注册命令都要求「跑到、且留下痕迹」。

### 技能 / 规则 / 代理

| 项 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| `.codebuddy/skills/` | 原生发现，`/name` 可调 | L3 | `P1` T4；本会话技能列表来源即此目录 | 2026-10-29 |
| `$ARGUMENTS` | 原样带入技能正文 | L3 | `P1` T5 | 2026-10-29 |
| `.codebuddy/agents/` | 目录**实时加载**，会话内新建即可派发 | L3 | `P1` T6（`ping` 新建即通） | 2026-10-29 |
| `rules` 的 `paths:` | 按路径条件注入；只碰 `*.md` 时不注入 | L3 | `P1` T2 | 2026-10-29 |
| agent 的 `model:` | **会被解析并用于子代理会话**：`resolveAgentModel` 依次读 `CODEBUDDY_CODE_SUBAGENT_MODEL` → 元数据 `model` → `agentManager.resolveModel`；`default` / `inherit` 表示继承。合法值就是 `default` / `lite` / `reasoning` | L2 | `grep -ao 'async resolveAgentModel(t){.\{0,700\}' "$WB/app.asar.unpacked/cli/dist/codebuddy-lite-wb.mjs"`；`agentMetadataSchema` 含 `model` | 2026-10-30 |
| agent 的 `effort:` | **被读、被归一化、并施加到子会话**。取值 `minimal`/`low`/`medium`/`high`/`xhigh`/`max`，非法值当场告警并忽略。加载器 `parseAgentFile()` 把它写进代理定义（`...effort:eF`），子代理启动时经 `setOverrideThinking(subSessionId,{reasoningEffort})` 落到会话思考预算 | L2 | `grep -ao 'let eF=(0,tF.normalizeReasoningEffort)(eI.effort)' "$H/cli/dist-server/shared.cjs"`；`grep -ao '\.\.\.eF&&{effort:eF}' 同文件`；`grep -ao 'setOverrideThinking(.\{0,80\}' 同文件` | 2026-10-30 |
| `/effort` 命令 | **存在且已实现**：`Set the model effort level (low, medium, high, xhigh, max, ultracode)`，带 `execute()` / `parseLevel()` / `resolveEffectiveLevel()` | L2 | `grep -ao '{name:"/effort".\{0,300\}' "$H/cli/dist-server/shared.cjs"` | 2026-10-30 |
| `maxEffortLevel` | **不存在**。努力度的天花板不是这个键（三处零命中） | L0 | `grep -ao maxEffortLevel "$WB/app.asar" \| wc -l` → 0；`grep -rao maxEffortLevel "$H/" \| wc -l` → 0 | 2026-10-30 |
| 钩子载荷里的 `effort.level` | **不出现**。`effort.level` 两包均零命中。它是**会话状态**的形态——`.codebuddy/scripts/statusline.sh` 读的是会话 JSON，不是钩子输入 | L0 | `grep -ao 'effort\.level' "$WB/app.asar" \| wc -l` → 0 | 2026-10-30 |
| agent 的 `maxTurns:` | **被读**，须为正整数；非法值告警并忽略 | L2 | `grep -ao 'parsePositiveIntField(eI.maxTurns)' "$H/cli/dist-server/shared.cjs"` | 2026-10-30 |
| agent 的 `isolation:` | **只认 `worktree`**，其它值告警并忽略 | L2 | `grep -ao '.\{60\}"worktree"===eI.isolation.\{60\}' "$H/cli/dist-server/shared.cjs"` | 2026-10-30 |
| agent 的 `background:` / `memory:` / `initialPrompt:` / `skills:` | 均被读。`memory` 只认 `user`/`project`/`local`；`background` 是布尔 | L2 | 同 `parseAgentFile()` | 2026-10-30 |
| 技能 frontmatter 的 `model:` | **被读，并对模型目录校验**（先按 id 匹配，再按 name 回查）。项目级与插件级两个加载器都携带它 | L2 | `grep -ao 'let eO=eI.model?.trim().\{0,200\}' "$H/cli/dist-server/shared.cjs"` | 2026-10-30 |
| 技能 frontmatter 的 `effort:` | **不被读**。`parseSkillFile` 返回 `context`/`agent`/`model` 等字段，其中没有 `effort` | L0 | `grep -ao 'async parseSkillFile(.\{0,2200\}' "$H/cli/dist-server/shared.cjs" \| grep -c effort` → 0 | 2026-10-30 |

**`agentMetadataSchema` 是名录，不是定义。** 它只有
`name`/`description`/`path`/`source`/`model`/`tools`/`color` 七个字段，因为它是
「列出有哪些代理」这个 RPC 的传输 schema（还有 94 KB/cwd 的编码上限，也只有列表才需要）。
判断某个 frontmatter 字段会不会生效，要读 `parseAgentFile()` 的返回值，
那里面还有 `effort` / `maxTurns` / `background` / `memory` / `isolation` / `skills` /
`initialPrompt`。**代理与技能的结论在这里正好相反**：同一个 `effort:`，代理读、技能不读。

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
| `.codebuddy/routines/` | **没有实现**。全树唯一一处真实出现，是引擎写给模型的一句「自我修改」安全说明：它枚举「agent 启动时会加载的配置」，把 `routines/` 与 `loop.md` 并列写进这个清单。那是提示词里的一个路径名，不是发现逻辑 | L1 | `grep -ao '.\{500\}\.codebuddy/routines/.\{300\}' "$H/cli/dist-server/shared.cjs"`；`app.asar` 的 3 次命中全是噪音（英文散文 "recurring routines"、正则解析器的 `subroutines`、Emacs 符号 `dlwave-routines`） | 2026-10-30 |
| `.codebuddy/loop.md` | **没有实现**。原记录的「4 次命中」是测量缺陷——那 4 次全是 `agent-loop.md`（另一个文件）。排除该前缀后零命中，唯一真实出现同样在上面那句安全说明里 | L0 | `grep -aoF "loop.md" "$WB/app.asar" \| wc -l` → 4；`grep -aoF "agent-loop.md" …` → 4；`grep -aoF ".codebuddy/loop.md" …` → 0 | 2026-10-30 |

### 其它上游断言（README「2026 年的能力」逐条落表）

| 上游断言 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| `worktree.baseRef` 控制新 worktree 用 `fresh`（远端默认分支）还是 `head`（本地 HEAD） | **没有这个设置键**。带引号的 `"worktree"` 零命中；`baseRef` 的 15 次命中全在 `addWorktree({repoCwd,worktreePath,newBranch,baseRef})` 一个函数里——那是 `git worktree add -b <branch> <path> <baseRef>` 的实参，不是可配置项。包内也没有 `fresh`/`head` 这对枚举 | L0 | `grep -ao '"worktree"' "$WB/app.asar" \| wc -l` → 0；`grep -ao baseRef "$WB/app.asar" \| wc -l` → 15；`grep -rao baseRef "$H/" \| wc -l` → 0 | 2026-10-30 |
| 内置技能 `/fewer-permission-prompts` · `/team-onboarding` · `/autofix-pr` · `/powerup` · Ultraplan | **五个都不存在**。两个包、大小写两种写法，全部零命中 | L0 | 对六个串名逐个 `grep -aoF`，`app.asar` 与 `$H/` 均返回 0 | 2026-10-30 |
| `/loop`（自我调速） | **没有命令实现**。38 次命中全在「预设任务卡」的 `command` 字段里（如「每日 AI 新闻推送」的示例写 `/loop 1d 关注…`），是给用户填空的文案。命令注册表里没有 `loop` | L0 | `grep -ao '"/loop"' "$H/cli/dist-server/shared.cjs" \| wc -l` → 0；`grep -ao 'name:"loop"' …` → 0 | 2026-10-30 |
| 高级代理配置含 `maxTurns`、隔离、工具限制 | **成立，但都在 agent frontmatter 里**，不是设置键。逐条见「技能 / 规则 / 代理」表 | L2 | 同上表 | 2026-10-30 |

## 已知不一致

### 已处理

1. **【更正，撤回 2026-10-30 当日早些时候的相反判断】`effort` 不是死字段。**
   那份判断说「代理元数据 schema 里没有 `effort`，Effect Struct 会剥掉它」，据此把
   18 个代理文件的 `effort:` 全删了，还把四份文档改成「本平台没有 effort 轴」。
   **错在搜错了目录**：`lib/agent-registry/schemas.js` 里的 `agentMetadataSchema`
   是代理**列表**的传输 schema（给界面列名录用的），不是 spawn 用的定义。真正的加载器
   与消费链都在 `cli/dist-server/shared.cjs`：`parseAgentFile()` 读
   `normalizeReasoningEffort(frontmatter.effort)`、非法值当场告警、合法值经
   `...effort:eF` 进代理定义，子代理启动时由
   `setOverrideThinking(subSessionId,{reasoningEffort})` 落地。同一条链上还有
   `--effort` 旗标与 `/effort` 命令（`low|medium|high|xhigh|max|ultracode`）。
   **已恢复** 18 个字段的原值（10 `high` / 7 `medium` / 1 `low`，取自 `b68584f^`），
   `normalize-model-tiers.py` 改为只对技能删 `effort`。连带更正 `model-routing.md`、
   `model-versions.md`、`agent-fleet.md`、`README.md`、`CODEBUDDY.md`、`TROUBLESHOOTING.md`、
   `MEMORY.md`、`UPSTREAM.md`、`check-spec-conformance.py` 的 `INERT_FIELDS`。
   **教训**：`grep -rao effort "$H/lib/"` 返回 6 —— 那个 6 **是真的**，而这个目录
   **不包含加载器**。台账第 2 条方法教训（「在正确的包里找」）写着「搜错包得到的零命中
   和真的不存在长得一模一样」，这次错的是**收窄了子目录**而不是包。搜索范围越窄，
   零命中越像结论。

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

3. ~~README「2026 年的能力」还剩三条未核的上游断言~~ —— **2026-10-30 已逐条落表**。
   `worktree.baseRef` 的 `fresh`/`head` **是 L0**：没有这个设置键，`baseRef` 只是
   `addWorktree()` 的实参。五个内置技能（`/fewer-permission-prompts`、`/team-onboarding`、
   `/autofix-pr`、`/powerup`、Ultraplan）**是 L0**，两个包零命中。`/loop` **没有实现**，
   命中全在预设任务卡的示例文案里。`maxTurns` / 隔离 / 工具限制**成立**，但都在 agent
   frontmatter 里，不是设置键。逐行证据见上面新增的「其它上游断言」表；README 对应四条已改。

4. ~~技能级 `model:` 两处说法相反~~ —— **2026-10-30 已定，`model-routing.md` 是对的**。
   无需运行时实测：两个 `parseSkillFile`（项目级与插件级）都返回 `model: eB.model`，
   命令转换器还会拿它**对模型目录校验**（先按 id 匹配，再按 name 回查 id）。
   `check-spec-conformance.py` 的 `INERT_FIELDS` 已把 `model` 移出；`effort` 留在里面
   是对的——技能加载器确实不读它（代理读，技能不读，这个差别写进了脚本注释）。

5. ~~`.codebuddy/routines/` 与 `.codebuddy/loop.md` 是两条悬着的字符串~~ —— **2026-10-30 已定**。
   两者都没有实现。它们共同出现在引擎给模型的一句「自我修改」安全说明里——那是一份
   「agent 启动时会加载的配置」路径清单，是提示词文本，不是发现逻辑。`loop.md` 原来的
   「4 次命中」是子串误计：4 次全是 `agent-loop.md`。**已在文档里明说它们没有实现**，
   而不是留着 ⏳ 让人读成「可能有」。

### 未处理

（空。2026-10-30 清空——上面五条是这一轮的完整清单，新条目请按规约先测再写。）

## 方法教训（下次还会犯，所以写下来）

1. **零命中要先怀疑探针。** `grep -o "\"permissions\"" app.asar` 返回 0，`grep -o permissions`
   返回 695。只测一种引号形态，就会把「支持」写成「不支持」。
2. **在正确的包里找。** 在 harness 里搜 `permissions` 得 0，不能推出「不支持」——设置管理器
   在 `app.asar` 里。搜错包得到的零命中，和真的不存在长得一模一样。
3. **键存在 ≠ 它被用。** `statusLine` 8 次命中，全是 HTTP 状态行；`agentMetadataSchema`
   里有 `model` 而列表里没有 `effort`，但这只能说明「名录上不显示」，推不出「不被读」。
   命中数是 L1 证据，不是 L2。
4. **收窄搜索范围会让零命中更像结论。** 「在 `$H/lib/` 里搜 `effort` 得 6，全在会话配置」
   这句话每个字都是真的，结论却是错的——因为加载器不在 `lib/`。第 2 条说的是别搜错包，
   这一条更隐蔽：**包对了，子目录错了**。判断某字段是否被消费，先定位**读写它的那个函数**
   （这里是 `parseAgentFile` / `spawn`），再回头数命中，而不是先数命中再猜。
5. **测量方式的缺陷会被写成平台的缺陷。** P0 判 agent `model:` 为「部分支持」，真实原因是
   模型不自报身份；`.codebuddy/loop.md` 的「4 次命中」实际是 `agent-loop.md` 的子串。
   结论一旦写进表格，就没人再回头问「这是平台的问题还是探针的问题」。
