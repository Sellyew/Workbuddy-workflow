# 平台事实台账

**这个文件只有一个用途：让每一句「本平台支持 / 不支持 X」都钉在可重跑的证据上。**

每条结论都必须标注观测级别、核查日期和可重跑证据。没有证据的判断不得继承为平台事实；
「引擎未证实」「桌面端未证实」与「不支持」是不同结论。

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

**L1 与 L2 的区别是这道台账的核心。** `statusLine` 的 8 次命中全是 HTTP 头，
既不能支撑 L1，也不能支撑 L2；已核实的只是桌面渲染层不消费，引擎读取设置键未证实。
反过来，`effort` 在代理**列表** schema 里没有位置，却在加载器、`--effort` 旗标与
`/effort` 命令里各有一条消费路径。只看命中数或只查一个 schema，都不足以判断字段是否生效。

## 环境

复核者先按自己的安装位置设置变量，不要把某台机器的绝对路径当成公共命令：

```bash
export WB="<你的 WorkBuddy resources 目录>"
export H="$WB/app.asar.unpacked/node_modules/@genie/agent-harness"
export S="$H/cli/dist-server/shared.cjs"
```

下列观测使用客户端版本 `37.10.3-42`（2026-10-27 构建）；其他版本必须重新核查。事实分居三个包，**搜错包会得到假的零命中**：

| 问题类型 | 该去哪个文件找 |
|---|---|
| 设置键、桌面端渲染 | `$WB/app.asar` |
| 钩子发射、子代理派发、模型解析 | `$WB/app.asar.unpacked/node_modules/@genie/agent-harness/cli/dist-server/shared.cjs`、`$WB/app.asar.unpacked/cli/dist/codebuddy-lite-wb.mjs` |
| 事件枚举、agent 元数据 schema | `$H/lib/runtime/component-protocol.js`、`$H/lib/agent-registry/schemas.js`（`H=$WB/app.asar.unpacked/node_modules/@genie/agent-harness`） |

### 宿主工具链

| 事实 | 观测级别 | 可复现证据 | 日期 |
|---|---|---|---|
| kpathsea 的路径分隔符**平台相关**：POSIX `:`，**Windows 版 TeX Live `;`**。且 `TEXINPUTS` / `BIBINPUTS` **必须以分隔符结尾**——否则默认搜索路径（含 `.`）被整个替换掉 | L3 | 在 Windows 最小 TeX 项目中分别设置 `TEXINPUTS="../Preambles;"` 与 `TEXINPUTS="../Preambles"` 后运行 `xelatex`；前者可找到 preamble，后者报文件缺失。POSIX 环境将分号改为冒号重跑 | 2026-10-31 |

## 事实表

### 配置与权限

| 键 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| `permissions` | 顶层键被读；`deny` 经 `extractWholeToolRules` 过滤工具调用 | L2 | `grep -a -o permissions "$WB/app.asar" \| wc -l` → 695 | 2026-10-30 |
| `permissions.allow` | 生效（放行清单） | L2 | 同上；`settingsManager.get("permissions")` | 2026-10-30 |
| `plansDirectory` | **不支持**。计划固定落 `~/.workbuddy/plans/`，没有可配置项 | L0 | `grep -a -o plansDirectory "$WB/app.asar" \| wc -l` → 0 | 2026-10-30 |
| `statusLine` | **桌面渲染层不消费已核实；引擎读取设置键未证实**。8 次命中全是 `statusLine: 'HTTP/1.1 204 No Content'`（CORS 头），这些无关命中不能支撑 L1 / L2 | 桌面已核实；引擎未证实 | `grep -a -o '.\{60\}statusLine.\{60\}' "$WB/app.asar"`；命中仅为 HTTP 头 | 2026-10-30 |
| 权限档位 | 桌面选择器只有两档：`sandbox.defaultPermission`（默认权限）/ `sandbox.fullAccessPermission`（完全访问权限）。桌面选择器不提供 `Shift+Tab` 与 `--permission-mode`；后两者属于 CodeBuddy Code CLI | 桌面 L3；CLI 官方文档 | 模式选择器可见；[CLI Permission Modes](https://www.workbuddy.ai/docs/cli/permission-modes) 的 “Switch During a Session: Shift+Tab” 与 “Specify at Startup: --permission-mode” | 2026-10-30（桌面）/ 2026-11-07（CLI） |

### 钩子

| 项 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| 事件集合 | 引擎认 **28 个**事件，不是上游那 9 个 | L2 | `grep -ao 'HOOK_EVENT_NAMES=new Map(\[.\{300,1200\}' "$H/lib/runtime/component-protocol.js"` | 2026-10-30 |
| 已注册的 7 个 | `PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `SessionStart` / `PreCompact` / `Stop` / `Notification` **全部有发射点** | L2 | `grep -ao 'executeHooks([A-Za-z_]*\.mb\.[A-Z_]*)' "$H/cli/dist-server/shared.cjs" \| sort -u` | 2026-10-30 |
| `PreCompact` | **会自动触发**，`trigger` 为 `auto`；真实压缩会写出 `pre-compact-state.json` | **L3** | 触发一次自动压缩后运行 `cat ~/.workbuddy/sessions/*/pre-compact-state.json`；核对文件含 `"trigger": "auto"` 与 ISO 时间戳 | 2026-10-30 |
| `Notification` | 有发射点（`SESSION_LIFECYCLE` 分支）；注册的 shell handler 经 `hook-runner.sh` 按扩展名分派后可执行并落盘 | 发射 L2 ⏳／handler L3 | `bash .codebuddy/hooks/lib/hook-runner.sh notify.sh <<< '{"message":"x"}'` → exit 0 且写出 `notifications.log` | 2026-10-30 |
| 可用但未接 | `SessionEnd` · `SubagentStart` · `SubagentStop` · `PostToolUseFailure` · `FileChanged` · `PermissionDenied` · `FinalStop` · `PostCompact` · `ConfigChange` · `CwdChanged` · `InstructionsLoaded` · `WorktreeCreate/Remove` | L2 | 同上 | 2026-10-30 |

**⏳ 的含义要说清**：它表示代码路径存在而平台运行时触发尚未观测，不表示「可能不支持」。
`PreCompact` 已有 L3 运行时证据；`Notification` 的发射点仍为 L2 ⏳，其 handler 已单独验证会落盘
（`quality_reports/session_logs/notifications.log`）。

L2「有发射点」不等于 L3，也不保证 handler 能跑。判断「这个钩子在工作吗」要连着看两段：
平台是否发射，注册的命令是否到达钩子文件。后者由 `scripts/check-hooks.py` 的 `check_wiring()`
检查，它对每条注册命令都要求「跑到、且留下痕迹」。

### 技能 / 规则 / 代理

| 项 | 事实 | 级别 | 证据 | 核查 |
|---|---|---|---|---|
| 项目与用户技能库 | `.codebuddy/skills/` 是官方支持的项目技能目录，随仓库共享；项目级优先于用户级，用户技能库跨项目。市场安装、上传与通用创建默认进入用户技能库，随仓库共享须显式放进项目目录 | L2（目录契约）＋L3（项目目录发现） | 官方目录约定；在项目目录放置最小技能，确认引擎发现并显式调用成功 | 2026-11-07 |
| 技能发现与显式调用 | 项目技能可被引擎发现，显式 `/name` 可调。**这项证据不自动覆盖自动调用或 UI 可见性** | L3（仅限发现与显式调用） | 创建只返回固定标记的最小项目技能，另开会话用 `/name` 调用并核对标记 | 2026-10-29 |
| 技能加载 | 元数据用于匹配，正文在触发时加载，附属材料按需读取；不能改写为「每轮从磁盘读取所有描述」 | L2 | `$S` 中的技能元数据解析与触发加载路径；复核时分别记录匹配、正文加载、附属读取 | 2026-11-07 |
| 技能热重载 | **未证实**，不得写「无需重启」。若未按新正文运行，记录客户端与技能版本，新开会话复测 | 未验证 | 没有足以支撑热重载的运行时证据 | 2026-11-07 |
| 动态命令注入 `` !`command` `` | 该语法是否在技能加载时执行并注入输出**尚未实测**，不得断言命令必然运行；确需使用时先用无副作用命令探针，记录客户端与技能版本及实际结果 | 未验证 | 没有运行时探针结果；`$ARGUMENTS` 的实测不能外推到命令注入 | 2026-11-07 |
| 技能 `allowed-tools` | **官方语义是工具白名单 / 限制**：只列技能允许使用的工具，未列出的工具不在白名单内。不是绝对安全边界，模型行为、权限规则与钩子仍须核验；当前没有桌面端相反行为的 L3 证据。若某版本实测不同，须单列客户端版本、最小探针与实际输出 | 官方文档 | [WorkBuddy 开放平台](https://open.workbuddy.cn/docs/skill)：「工具白名单（逗号分隔）」；[CodeBuddy Code CLI](https://www.workbuddy.ai/docs/cli/skills)：“Allowlist of permitted tools” / “Restrict which tools a Skill can use”；`check-skill-integrity.py` 只检查文档对齐 | 2026-11-07 |
| `$ARGUMENTS` | 原样带入技能正文 | L3 | 最小技能输出 `$ARGUMENTS`；传入含空格的标记字符串并核对逐字输出 | 2026-10-29 |
| `.codebuddy/agents/` | 目录**实时加载**，会话内新建即可派发 | L3 | 在会话内创建返回固定标记的最小 agent，立即派发并核对标记 | 2026-10-29 |
| `rules` 的 `paths:` | 按路径条件注入；只碰 `*.md` 时不注入 | L3 | 用最小规则分别读取匹配与不匹配 `paths:` 的文件，核对规则是否进入上下文 | 2026-10-29 |
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
| 技能 frontmatter 的 `context: fork` | **被读，而且会让技能失去 `Agent`**。写了它，技能经 `executeSkillInForkContext` 变成 `subagent_type: general-purpose` 的 **detached 任务**；那个子会话的工具集里**没有 `Agent`**——`allowed-tools` 里写了也拿不到。需要多透镜并行独立审读的技能不能使用此字段，否则会退化成同一会话依次执行 | L3 | 最小探针的脱敏输出：直接工具含 `Skill` / `TaskCreate` / `TaskStop`，**无 `Agent`**；多透镜技能未派发其声明的审读代理。复跑时创建含 `context: fork` 与 `allowed-tools: Agent` 的最小技能，列出实际工具并尝试派发。代码：`grep -ao '"fork"===e_.context.\{0,120\}' "$H/cli/dist-server/shared.cjs"` | 2026-10-31 |

**创建入口与界面证据也要分开。** 本仓库的 `/new-skill` 是项目技能，按本仓库约定生成项目技能；WorkBuddy 内置 `/skill-creator` 是通用创建器（GUI：技能 → 添加技能 → 创建技能）。UI/菜单不显示不等于引擎未发现或 `/name` 不可调用。自动调用要用匹配探针另测，显式调用要用 `/name` 另测，UI 可见性要查看界面；三者不能由一次 T4 互相推导。

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
| automation **跑在真实工作树** | `pwd` 为仓库根，能读到未跟踪文件与未提交修改，HEAD 与本地一致，非浅克隆。**不是全新克隆，不是隔离沙箱** | **L3** | 可重跑探针与脱敏输出见 [`scheduled-routines.md`](scheduled-routines.md)「实测」节 | 2026-10-30 |
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
| `/goal` | **CodeBuddy Code CLI 有官方支持；WorkBuddy 桌面端未证实。** 官方 CLI 文档要求 `@tencent-ai/codebuddy-code` 含 `GoalService`，并描述 Web UI / ACP 面板；本机桌面共享引擎存在 `name:"/goal"` 命令注册与 `GoalService` 实现，但尚无桌面运行时观测，不能写成桌面可用 | CLI 官方文档；桌面共享引擎 L2 ⏳ | [官方 `/goal` 文档](https://www.workbuddy.cn/docs/cli/goal)；`grep -ao 'name:"/goal".\{0,180\}' "$S"`；`grep -ao 'Symbol("GoalService")' "$WB/app.asar.unpacked/cli/dist/codebuddy-lite-wb.mjs"`。2026-11-07 只读探针：`$S` 中 `/goal` 19 处、桌面 `codebuddy-lite-wb.mjs` 中 22 处 | 2026-11-07 |
| 高级代理配置含 `maxTurns`、隔离、工具限制 | **成立，但都在 agent frontmatter 里**，不是设置键。逐条见「技能 / 规则 / 代理」表 | L2 | 同上表 | 2026-10-30 |

## 复核方法

1. **零命中要先怀疑探针。** `grep -o "\"permissions\"" app.asar` 与 `grep -o permissions app.asar`
   测量的是不同字面量。至少覆盖引号形态与大小写变体，不能把单一搜索的零命中写成「不支持」。
2. **在正确的包里找。** 设置管理器在 `app.asar`，不能用在 harness 中的零命中否定设置键。
   搜错包得到的零命中，和真的不存在长得一模一样。
3. **无关命中 ≠ 键存在，更 ≠ 它被用。** HTTP 状态行里的 `statusLine` 不能支撑 L1 或 L2；
   `agentMetadataSchema` 不含 `effort` 也只说明名录不显示。白名单 / schema / 枚举里的键命中支撑 L1，
   读取或发射路径支撑 L2。
4. **搜索范围必须覆盖实际加载器。** 判断某字段是否被消费，先定位读写它的函数，例如
   `parseAgentFile` 与子代理启动路径，再核对消费链；包名正确而子目录过窄仍会产生假零命中。
5. **区分子串与精确路径。** 统计 `loop.md` 时会同时命中 `agent-loop.md`；记录命中数之前先检查
   实际上下文，避免把测量方式的问题写成平台缺陷。
