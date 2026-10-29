---
name: permission-check
description: 诊断本平台（WorkBuddy）为什么（或者为什么不）弹出一个动作的批准请求、以及为什么某个动作被直接拦下。默认只读仓库本地层（`.codebuddy/settings.json` 的 `permissions` 规则与 PreToolUse 钩子链、`.codebuddy/settings.local.json` 的本地覆盖）。宿主全局层（`~/.workbuddy/`）**只在用户明确确认后**才读 —— 那里可能含有无关的路径或密钥。当用户说 "why is it asking me to approve?"、"permission check"、"why am I getting prompts?"、"bypass isn't working"、"check my permissions" 时使用。只读诊断。本平台读 `permissions.allow` / `permissions.deny`；权限档位在界面里选（默认权限 / 完全访问权限）。本技能把规则、钩子与档位三处摊开。
description_zh: 诊断本平台（WorkBuddy）为什么（或者为什么不）弹出一个动作的批准请求、以及为什么某个动作被直接拦下。默认只读仓库本地层（`.codebuddy/settings.json` 的 `permissions` 规则与 PreToolUse 钩子链、`.codebuddy/settings.local.json` 的本地覆盖）。宿主全局层（`~/.workbuddy/`）**只在用户明确确认后**才读 —— 那里可能含有无关的路径或密钥。当用户说 "why is it asking me to approve?"、"permission check"、"why am I getting prompts?"、"bypass isn't working"、"check my permissions" 时使用。只读诊断。本平台读 `permissions.allow` / `permissions.deny`；权限档位在界面里选（默认权限 / 完全访问权限）。本技能把规则、钩子与档位三处摊开。
argument-hint: "(no arguments)"
allowed-tools: ["Read", "Bash", "Glob"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# 权限检查

## 目的

把本平台上**真正会拦下、或询问一个动作**的东西摊开，让用户一眼看出它为什么触发。本平台有三处会发声，彼此独立：

1. **`permissions` 规则** —— `.codebuddy/settings.json` 里的 `allow` / `deny` 会被逐条匹配到工具上。本模板自带七条通配 `allow`（`Edit(**)`、`Write(**)`、`MultiEdit(**)`、`Bash(*)`、`WebFetch(*)`、`WebSearch`、`Read(**)`）与空 `deny`。
2. **PreToolUse 钩子** —— `.codebuddy/hooks/` 下的守卫可以直接 `deny`，而钩子**不看**权限规则。
3. **界面上的档位选择器** —— 只有两档：**默认权限** 与 **完全访问权限**（界面对应的键是 `sandbox.defaultPermission` / `sandbox.fullAccessPermission`）。

上游 Claude Code 那套「六层文件层栈解析出一个起始模式」在本平台**没有对应物**：没有 `claudeCode.*` 那一层，也没有第三档以上的档位。下面第二节把上游层栈照抄下来只作**对照表** —— 它回答的是「按上游文档去改配置为什么一点反应都没有」。第三节起才是本平台真读得到的东西。

## 六个层（上游对照表；本平台只实现第 3–5 层）

1. **VSCode 用户设置** —— `~/Library/Application Support/Code/User/settings.json`（macOS）、`%APPDATA%/Code/User/settings.json`（Windows）、`~/.config/Code/User/settings.json`（Linux）。键：`claudeCode.initialPermissionMode`。（上游 VS Code 扩展的层，本平台不读）
2. **VSCode 工作区设置** —— `<repo>/.vscode/settings.json`。同一个键。胜过用户层。（上游扩展层，本平台不读。本仓库不再提供这个文件；若你从上游 fork 里保留了它，本技能仍会读，但里面没有本平台会消费的开关）
3. **CLI 用户设置** —— `~/.workbuddy/settings.json`（旧版为 `~/.codebuddy/settings.json`）。本平台**读这个文件**：`hooks` 与 `permissions` 都生效；`permissions.defaultMode` 只在无头路径里作回退，桌面端以选择器为准。
4. **CLI 项目设置** —— `<repo>/.codebuddy/settings.json`。胜过用户层。本平台**读 `hooks` 与 `permissions`** —— 本模板的七条通配 `allow` 就在这一层。
5. **CLI 项目本地设置** —— `<repo>/.codebuddy/settings.local.json`（已 gitignore）。胜过项目层，同样读 `hooks` 与 `permissions`。
6. **会话内档位** —— 上游是会话启动时由第 1–5 层设定，之后 `Shift+Tab` 循环切换。**本平台换成了界面里的选择器**，只有「默认权限」与「完全访问权限」两档，没有 `Shift+Tab`，也没有第三档。

**上游那两条覆盖整个层栈的规则**（Anthropic 的 permission-modes 文档，2026-09-26 复核）在本平台**都不适用**，因为它们约束的是本平台没有的那几层：

- 上游第 4、5 层不把 `auto` 或 `bypassPermissions` 当起始模式 —— 本平台的起始档位由选择器决定，与文件里写什么无关。
- VS Code 扩展不读第 4–5 层来定起始模式，改用 `claudeCode.initialPermissionMode` 加 *Allow dangerously skip permissions* 开关 —— 本平台没有这个扩展层。

所以先查「你要找的那个开关在本平台根本不存在」这种情况 —— 再查下面那种被钩子直接拦下的动作。

**关键洞见：** 上游那句「文件层设置是对的、运行时模式却不一样」的困惑，在本平台换了个形状，但不是消失了。三个真实来源：

- 有人照上游文档把 `claudeCode.initialPermissionMode` 写进 VS Code 设置 —— 本平台不读那一层，什么都不会变。
- 有人把 `bypassPermissions` 写进 `.codebuddy/settings.json` —— 本平台的档位来自选择器，项目文件里的模式值不会有可观察的效果。
- 动作其实是被 PreToolUse 钩子 deny 掉的，而钩子根本不看权限规则 —— 改 `permissions` 怎么改都没用，得改命令。

三者的修法不同，但都能从文件里看出来 —— 只要先读对文件。

## 隐私契约

宿主全局设置文件（`~/.workbuddy/settings.json`）可能含有：

- 无关项目的路径与密钥
- 本仓库之外加入的 API 密钥、令牌或服务商凭据
- 用户所在组织或雇主设定的权限策略

本技能是按纵深防御设计的：**阶段 A 自动运行，只读仓库本地文件。** 阶段 B **只在用户明确确认之后**才读宿主全局文件 —— 绝不偷偷读。报告宿主全局层时，凡与 `hooks`、`permissions.*`、`claudeCode.*` 不直接相关的键一律打码。

## 协议

### 阶段 A：仓库本地层（自动运行）

立刻读这些 —— 它们被提交进仓库（或在仓库内被 gitignore），不越过信任边界：

```bash
VSCODE_WS="${CODEBUDDY_PROJECT_DIR}/.vscode/settings.json"
CLI_PROJECT="${CODEBUDDY_PROJECT_DIR}/.codebuddy/settings.json"
CLI_LOCAL="${CODEBUDDY_PROJECT_DIR}/.codebuddy/settings.local.json"
```

对每个存在的文件，抽取：

- **VSCode 工作区：** 看到 `claudeCode.*` 时，标为**本平台不读的上游键**——包括连上游都会静默忽略的错写 `claudeCode.allowDangerouslySkipPermissions`
- **CLI 项目 / 项目本地：** `hooks` 链（哪个事件、哪个 matcher、指向哪个脚本）；`permissions.allow` 与 `permissions.deny` **逐条列出**（这两项确实会被匹配到工具上）；`permissions.defaultMode` 若存在，标为「桌面端无可观察效果」

文件缺失没关系 —— 报告「不存在」，而不是报错。

把这三层里**实际存在**的东西打印出来：钩子链（事件 → matcher → 脚本）、`permissions` 的 allow/deny 规则、`.codebuddy/settings.local.json` 的覆盖、以及任何 `claudeCode.*` 键（后者标为**不生效**）。如果问题其实只是「某个具体动作被拦了」，就停在这里，点名是哪个守卫脚本拒的、拒的是哪条命令：破坏性 git 操作由 `.codebuddy/hooks/git-guardrails.py` 拒，对 `.codebuddy/` 的写入由 `root-of-trust-guard.py` 拒，绕过 `scripts/file-issue.py` 查重直接建 issue 的 `gh` 命令由 `issue-guard.py` 拒。

### 阶段 B：宿主全局层（需要用户明确确认）

如果阶段 A 还没有结论 —— 例如仓库本地层没有挂任何钩子、`permissions` 也是空的，而用户仍然被请求 —— 问用户：

> 「为完成诊断，我需要读本仓库之外的一个文件：`~/.workbuddy/settings.json`（用户级设置，旧版在 `~/.codebuddy/settings.json`）。
> 它可能含有无关的路径或密钥。我会给任何不在 `hooks`、`permissions.*`、`claudeCode.*` 里的键打码。继续吗？」

只在用户确认之后，才读：

```bash
CLI_USER="${HOME}/.workbuddy/settings.json"
```

报告它的内容时，**只抽取相关键**：

- `hooks`、`permissions.defaultMode`、`permissions.allow`、`permissions.deny`（`defaultMode` 在桌面端无可观察效果；另两项照常列出）
- 任何以 `claudeCode.` 开头的键（标为不生效）

绝不打印整个文件。其余一律打码为 `(other keys redacted)`。

### 步骤 2 —— 计算解析出的状态

把三处合成一遍再下结论：

- **规则层：** `permissions.deny` 里的任何匹配都会拦住该工具，不管 `allow` 怎么写；`allow` 里的通配（本模板的 `Bash(*)` 一类）让常规动作不再询问。项目本地层覆盖项目层。
- **钩子层：** 哪个事件的哪些 matcher 挂了钩子，覆盖哪些工具；同一事件上多个钩子的顺序，以及一个事实：任一钩子 deny 就拦下，后续钩子不能把它改回 allow。
- **档位层：** 选择器当前是哪一档。这一层压过前面两层 —— 档位在「默认权限」时，`allow` 里的通配仍然会放行常规动作；档位在「完全访问权限」时，跳过的是询问与安全检查，但 `deny` 与钩子仍然生效。

### 步骤 3 —— 报告运行时状态

本平台没有状态行可看：引擎实现了 `statusLine`，桌面渲染层却不消费它（2026-10-30 核查：客户端包里 `statusLine` 的 8 次命中全是 HTTP 状态行）。所以不要用模式徽标做判据，也不要指向 `statusline.sh`。档位直接问用户，或者读选择器的位置：

> 「你的界面上只有两档：**默认权限** 与 **完全访问权限**。先告诉我停在哪一档。然后换成一个更硬的问题：这条命令是被**某个钩子**拒的，还是被**平台**问的？前者能在 `.codebuddy/settings.json` 里指到具体脚本与具体命令；后者不会在任何配置文件里留下痕迹 —— 重开一个新任务，看它还发不发生。」

### 步骤 4 —— 标出常见失败模式

检查并显式指出：

1. **照上游文档设 `claudeCode.*` 或把 `bypassPermissions` 写进项目文件：** 前者本平台不读那一层；后者的档位由选择器决定，写进文件不会有可观察的效果。修法：从 `.codebuddy/settings.json` 里删掉这些值，用选择器切档 —— 留着一个不生效的开关，会让下一个读文件的人以为限制已经设上了。
2. **把钩子的 deny 当成权限提示：** `git-guardrails.py` 对破坏性 git 命令直接输出 `permissionDecision: deny`，那不是「等你批准」，是「不许」。修法是改命令，不是改配置。
3. **信任根守卫拦下改配置本身：** `root-of-trust-guard.py` 拒绝**用 Bash 往** `.codebuddy/` 写。要改配置就用 Edit / Write 工具，那样留下可审读的 diff —— 这是安全机制，不是 bug。
4. **钩子静默失效：** `hook-runner.sh` 探测不到可用解释器时钩子不执行，同一条命令这次就过了。别把「这次没拦」读成「策略允许」——先确认钩子真的跑了（它是唯一入口，手工喂一次同样的输入看有没有输出）。
5. **过期会话：** 设置是对的，但用户报告行为没变 → 几乎总是一个早于该改动的会话。建议开一个新任务再试。
6. **`deny` 胜出：** 任一钩子 deny 都会拦下该动作，不论别处写了什么，也不论档位停在哪 —— 这正是受限数据项目用钩子守 `.git` 与受限路径的原因。

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

如果某个文件里的 `permissions` 段是空的、而用户以为它设了限制，就把诊断第一行换成那件事（「`permissions` 段为空，本模板之外没有任何规则在放行或拒绝」）。

## 备注

- 本技能是只读的。它从不修改设置。
- 如果 `$CODEBUDDY_PROJECT_DIR` 未设置，退回 `git rev-parse --show-toplevel`。
- 平台感知：路径检测要分 macOS / Linux / Windows；但「读哪些键」与操作系统无关 —— `permissions` 与 `hooks` 在三个平台上都被读，`claudeCode.*` 在三个平台上都不被读。
