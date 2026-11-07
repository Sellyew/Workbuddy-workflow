---
name: permission-check
description: 诊断本平台（WorkBuddy）为什么（或者为什么不）弹出一个动作的批准请求、以及为什么某个动作被直接拦下。默认只读仓库本地层（`.codebuddy/settings.json` 的 `permissions` 规则与 PreToolUse 钩子链、`.codebuddy/settings.local.json` 的本地覆盖）。宿主全局层（`~/.workbuddy/`）**只在用户明确确认后**才读 —— 那里可能含有无关的路径或密钥。当用户说 "why is it asking me to approve?"、"permission check"、"why am I getting prompts?"、"bypass isn't working"、"check my permissions" 时使用。只读诊断。本平台读 `permissions.allow` / `permissions.deny`；权限档位在界面里选（默认权限 / 完全访问权限）。本技能把规则、钩子与档位三处摊开。
description_zh: 诊断本平台（WorkBuddy）为什么（或者为什么不）弹出一个动作的批准请求、以及为什么某个动作被直接拦下。默认只读仓库本地层（`.codebuddy/settings.json` 的 `permissions` 规则与 PreToolUse 钩子链、`.codebuddy/settings.local.json` 的本地覆盖）。宿主全局层（`~/.workbuddy/`）**只在用户明确确认后**才读 —— 那里可能含有无关的路径或密钥。当用户说 "why is it asking me to approve?"、"permission check"、"why am I getting prompts?"、"bypass isn't working"、"check my permissions" 时使用。只读诊断。本平台读 `permissions.allow` / `permissions.deny`；权限档位在界面里选（默认权限 / 完全访问权限）。本技能把规则、钩子与档位三处摊开。
argument-hint: "(no arguments)"
allowed-tools: ["Read", "Bash", "Glob"]
---

# 权限检查

## 目的

找出本平台上**真正会拒绝动作或请求批准**的机制，并解释触发原因。以下三处彼此独立，都可能影响结果：

1. **`permissions` 规则**：`.codebuddy/settings.json` 中的 `allow` / `deny` 会逐条匹配工具。本模板自带七条通配 `allow`（`Edit(**)`、`Write(**)`、`MultiEdit(**)`、`Bash(*)`、`WebFetch(*)`、`WebSearch`、`Read(**)`），`deny` 为空。
2. **PreToolUse 钩子**：`.codebuddy/hooks/` 下的守卫可以直接 `deny`，而且**不读取**权限规则。
3. **界面上的档位选择器**：只有**默认权限**与**完全访问权限**两档，对应的界面键是 `sandbox.defaultPermission` / `sandbox.fullAccessPermission`。

上游 Claude Code 通过六层文件解析起始模式，本平台**没有这套机制**：既不读取 `claudeCode.*` 层，也没有第三档或更多档位。下一节保留上游层栈，仅作**对照**，用来解释为什么按上游文档修改配置可能没有反应。再往后才是本平台实际读取的内容。

## 六个层（上游对照表；本平台只实现第 3–5 层）

1. **VSCode 用户设置** —— `~/Library/Application Support/Code/User/settings.json`（macOS）、`%APPDATA%/Code/User/settings.json`（Windows）、`~/.config/Code/User/settings.json`（Linux）。键：`claudeCode.initialPermissionMode`。这是上游 VS Code 扩展的层，本平台不读取。
2. **VSCode 工作区设置** —— `<repo>/.vscode/settings.json`。使用同一个键，优先于用户层。这也是本平台不读取的上游扩展层。本仓库不再提供该文件；如果你从上游 fork 中保留了它，本技能仍会读取，但其中没有本平台会使用的开关。
3. **CLI 用户设置** —— `~/.workbuddy/settings.json`（旧版为 `~/.codebuddy/settings.json`）。本平台**读取此文件**，`hooks` 与 `permissions` 都会生效；`permissions.defaultMode` 只在无头路径中作为回退，桌面端以选择器为准。
4. **CLI 项目设置** —— `<repo>/.codebuddy/settings.json`。优先于用户层。本平台**读取 `hooks` 与 `permissions`**，本模板的七条通配 `allow` 就位于这一层。
5. **CLI 项目本地设置** —— `<repo>/.codebuddy/settings.local.json`（已 gitignore）。优先于项目层，同样读取 `hooks` 与 `permissions`。
6. **会话内档位** —— 上游在会话启动时由第 1–5 层设定，之后用 `Shift+Tab` 循环切换。**桌面端改为界面选择器**，只有「默认权限」与「完全访问权限」两档。桌面选择器不提供 `Shift+Tab` 循环或 `--permission-mode` 启动标志，后两者属于 CodeBuddy Code CLI。

**上游那两条覆盖整个层栈的规则**（Anthropic 的 permission-modes 文档，2026-09-26 复核）在本平台**均不适用**，因为它们约束的是本平台没有的层：

- 上游第 4、5 层不把 `auto` 或 `bypassPermissions` 当作起始模式；本平台的起始档位由选择器决定，与文件内容无关。
- VS Code 扩展不读第 4–5 层来确定起始模式，而是使用 `claudeCode.initialPermissionMode` 和 *Allow dangerously skip permissions* 开关；本平台没有这个扩展层。

因此，先排除「所需开关在本平台不存在」的情况，再检查动作是否被钩子直接拒绝。

**关键洞见：** 上游常见的困惑是「文件设置正确，运行时模式却不同」。本平台仍有类似问题，但原因只有以下三类：

- 用户按上游文档把 `claudeCode.initialPermissionMode` 写入 VS Code 设置，但本平台不读取该层，因此不会有变化。
- 用户把 `bypassPermissions` 写入 `.codebuddy/settings.json`，但档位来自选择器，项目文件中的模式值不会产生可观察效果。
- 动作实际被 PreToolUse 钩子 deny，而钩子不读取权限规则。此时修改 `permissions` 无效，必须修改命令。

三者的处理方式不同，但只要读取正确的文件，就能区分。

## 隐私契约

宿主全局设置文件（`~/.workbuddy/settings.json`）可能包含：

- 无关项目的路径与密钥
- 在本仓库之外添加的 API 密钥、令牌或服务商凭据
- 用户所在组织或雇主设定的权限策略

本技能采用纵深防御：**阶段 A 自动运行，只读仓库本地文件。** 阶段 B **只有用户明确确认后**才能读取宿主全局文件，绝不擅自读取。报告宿主全局层时，与 `hooks`、`permissions.*`、`claudeCode.*` 无直接关系的键一律打码。

## 协议

### 阶段 A：仓库本地层（自动运行）

立即读取以下路径。这些文件要么提交在仓库中，要么在仓库内被 gitignore，不会越过信任边界：

```bash
VSCODE_WS="${CODEBUDDY_PROJECT_DIR}/.vscode/settings.json"
CLI_PROJECT="${CODEBUDDY_PROJECT_DIR}/.codebuddy/settings.json"
CLI_LOCAL="${CODEBUDDY_PROJECT_DIR}/.codebuddy/settings.local.json"
```

对每个存在的文件，提取以下内容：

- **VSCode 工作区：** 遇到 `claudeCode.*` 时，标为**本平台不读取的上游键**，包括上游也会静默忽略的错误写法 `claudeCode.allowDangerouslySkipPermissions`。
- **CLI 项目 / 项目本地：** 列出 `hooks` 链，包括事件、matcher 和脚本；**逐条列出** `permissions.allow` 与 `permissions.deny`，因为它们确实会匹配工具；如果有 `permissions.defaultMode`，标为「桌面端无可观察效果」。

文件不存在不属于错误，报告「不存在」即可。

打印这三层中**实际存在**的配置：钩子链（事件 → matcher → 脚本）、`permissions` 的 allow/deny 规则、`.codebuddy/settings.local.json` 的覆盖，以及所有 `claudeCode.*` 键，后者标为**不生效**。如果问题只是某个具体动作被拒绝，可以在此停止，并指出拒绝它的守卫脚本和命令：破坏性 git 操作由 `.codebuddy/hooks/git-guardrails.py` 拒绝，对 `.codebuddy/` 的写入由 `root-of-trust-guard.py` 拒绝，绕过 `scripts/file-issue.py` 查重直接创建 issue 的 `gh` 命令由 `issue-guard.py` 拒绝。

### 阶段 B：宿主全局层（需要用户明确确认）

如果阶段 A 仍不能解释问题，例如仓库本地层没有钩子、`permissions` 为空，但用户仍收到批准请求，就询问：

> 「为完成诊断，我需要读本仓库之外的一个文件：`~/.workbuddy/settings.json`（用户级设置，旧版在 `~/.codebuddy/settings.json`）。
> 它可能含有无关的路径或密钥。我会给任何不在 `hooks`、`permissions.*`、`claudeCode.*` 里的键打码。继续吗？」

只有用户确认后，才读取：

```bash
CLI_USER="${HOME}/.workbuddy/settings.json"
```

报告时**只提取相关键**：

- `hooks`、`permissions.defaultMode`、`permissions.allow`、`permissions.deny`。`defaultMode` 在桌面端没有可观察效果，另两项照常列出。
- 任何以 `claudeCode.` 开头的键，标为不生效。

绝不能打印整个文件，其余内容一律打码为 `(other keys redacted)`。

### 步骤 2 —— 计算解析出的状态

综合三处信息后再下结论：

- **规则层：** 只要匹配 `permissions.deny`，工具就会被拒绝，无论 `allow` 如何配置。`allow` 中的通配规则（如本模板的 `Bash(*)`）可让常规动作不再询问。项目本地层覆盖项目层。
- **钩子层：** 说明各事件的 matcher 挂了哪些钩子、覆盖哪些工具，以及同一事件多个钩子的顺序。任一钩子 deny 都会拒绝动作，后续钩子不能将其改回 allow。
- **档位层：** 确认选择器当前档位。这一层优先于前两层：选择「默认权限」时，`allow` 通配仍会放行常规动作；选择「完全访问权限」时，会跳过询问与安全检查，但 `deny` 和钩子仍然生效。

### 步骤 3 —— 报告运行时状态

桌面端没有可依据的状态行。已经核实桌面渲染层不消费 `statusLine`，但引擎是否读取该键尚未证实。2026-10-30 核查时，客户端包中 `statusLine` 的 8 次命中全部指 HTTP 状态行，不能作为引擎读取证据。因此，不要用模式徽标判断，也不要指向 `statusline.sh`。直接询问用户档位，或查看选择器位置：

> 「你的界面上只有两档：**默认权限** 与 **完全访问权限**。先告诉我停在哪一档。然后换成一个更硬的问题：这条命令是被**某个钩子**拒的，还是被**平台**问的？前者能在 `.codebuddy/settings.json` 里指到具体脚本与具体命令；后者不会在任何配置文件里留下痕迹 —— 重开一个新任务，看它还发不发生。」

### 步骤 4 —— 标出常见失败模式

逐项检查并明确指出：

1. **照上游文档设 `claudeCode.*` 或把 `bypassPermissions` 写进项目文件：** 前者所在层不被本平台读取；后者的档位由选择器决定，写入文件没有可观察效果。处理方式是从 `.codebuddy/settings.json` 删除这些值，再用选择器切档。保留无效开关会误导后来者，让他们以为限制已经设置。
2. **把钩子的 deny 当成权限提示：** `git-guardrails.py` 会对破坏性 git 命令直接输出 `permissionDecision: deny`。这表示「不许」，不是「等待批准」。应修改命令，而不是配置。
3. **信任根守卫拦下改配置本身：** `root-of-trust-guard.py` 拒绝**用 Bash 往** `.codebuddy/` 写。要修改配置，应使用 Edit / Write 工具并留下可审读的 diff。这是安全机制，不是 bug。
4. **钩子静默失效：** `hook-runner.sh` 找不到可用解释器时，钩子不会执行，同一条命令可能因此通过。不要把「这次没拦」理解为「策略允许」。先确认钩子确实运行：它是唯一入口，可以手工输入同样的数据，观察是否有输出。
5. **过期会话：** 设置正确但行为没有变化，通常因为会话早于改动。建议打开新任务再试。
6. **`deny` 胜出：** 任一钩子 deny 都会拒绝动作，无论其他配置如何，也无论当前档位。这正是受限数据项目使用钩子保护 `.git` 和受限路径的原因。

## 输出格式

```
=== CONFIG SURFACE ===

.codebuddy/settings.json       permissions.allow: Edit(**), Write(**), MultiEdit(**), Bash(*),
                                               WebFetch(*), WebSearch, Read(**)
                               permissions.deny:  (empty)
                               hooks: PreToolUse(Bash|Write|Edit|MultiEdit -> git-guardrails.py)
                                      PreToolUse(Bash -> root-of-trust-guard.py, issue-guard.py)
                                      Stop: log-reminder.py
.codebuddy/settings.local.json (absent)
.vscode/settings.json          (absent)

claudeCode.* keys found:       none — upstream-only, not read here

=== BLOCKERS ===

(none observed in config) — a refusal at run time points at one of these:
  git-guardrails.py      deny  destructive git command
  root-of-trust-guard.py deny  Bash write to .codebuddy/ (root of trust)
  issue-guard.py         deny  gh issue create that skips scripts/file-issue.py

=== DIAGNOSIS ===

Rules and hooks above are what this repo actually enforces; the UI toggle
(默认权限 / 完全访问权限) overrides prompts, not deny rules. If an action was still refused:
  1. A PreToolUse hook denied it — the command is quoted above; change the command, not a setting.
  2. A permissions.deny rule matched it — the tool name is quoted above.
  3. The hook did not run — start it by hand through .codebuddy/hooks/lib/hook-runner.sh.
  4. Session is stale (started before settings were applied) — start a new one.
```

如果某文件的 `permissions` 段为空，而用户以为其中设有限制，就把诊断第一行改为说明这一点：「`permissions` 段为空，本模板之外没有任何规则在放行或拒绝」。

## 备注

- 本技能只读，绝不修改设置。
- 如果 `$CODEBUDDY_PROJECT_DIR` 未设置，回退到 `git rev-parse --show-toplevel`。
- 路径检测需要区分 macOS / Linux / Windows，但读取哪些键与操作系统无关：三个平台都会读取 `permissions` 与 `hooks`，都不会读取 `claudeCode.*`。
