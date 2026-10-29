---
name: permission-check
description: 诊断本平台（WorkBuddy）为什么（或者为什么不）弹出一个动作的批准请求、以及为什么某个动作被直接拦下。默认只读仓库本地层（`.codebuddy/settings.json` 的 PreToolUse 钩子链、`.codebuddy/settings.local.json` 的本地覆盖、`.vscode/settings.json`）。宿主全局层（`~/.workbuddy/`、VSCode 用户设置）**只在用户明确确认后**才读 —— 那些文件里可能含有无关的路径或密钥。当用户说 "why is it asking me to approve?"、"permission check"、"why am I getting prompts?"、"bypass isn't working"、"check my permissions" 时使用。只读诊断。本平台没有 `permissions.allow` 那套分层权限配置，本技能不假装检查它。
description_zh: 诊断本平台（WorkBuddy）为什么（或者为什么不）弹出一个动作的批准请求、以及为什么某个动作被直接拦下。默认只读仓库本地层（`.codebuddy/settings.json` 的 PreToolUse 钩子链、`.codebuddy/settings.local.json` 的本地覆盖、`.vscode/settings.json`）。宿主全局层（`~/.workbuddy/`、VSCode 用户设置）**只在用户明确确认后**才读 —— 那些文件里可能含有无关的路径或密钥。当用户说 "why is it asking me to approve?"、"permission check"、"why am I getting prompts?"、"bypass isn't working"、"check my permissions" 时使用。只读诊断。本平台没有 `permissions.allow` 那套分层权限配置，本技能不假装检查它。
argument-hint: "(no arguments)"
allowed-tools: ["Read", "Bash", "Glob"]
disallowed-tools: ["Edit", "MultiEdit"]
---

# 权限检查

## 目的

把本平台上**真正会拦下、或询问一个动作**的东西摊开，让用户一眼看出它为什么触发。**本平台没有上游 Claude Code 那套从层栈里解析 `defaultMode` 的权限模式系统**：`.codebuddy/settings.json` 只认 `hooks`，`permissions.allow` / `permissions.deny` / `permissions.defaultMode` / `claudeCode.initialPermissionMode` 在本平台不被读取，写进任何一层都不产生行为。所以这个技能读**存在的**东西——钩子链、守卫脚本、本地覆盖文件——并明说哪些开关在本平台**没有对应机制**。下面第二节把上游的层栈照抄下来只作**对照表**，用来解释「按上游文档去改配置为什么一点反应都没有」；第三节起才是本平台真能读到的地方。

## 六个层（优先级：越靠下越赢）

1. **VSCode 用户设置** —— `~/Library/Application Support/Code/User/settings.json`（macOS）、`%APPDATA%/Code/User/settings.json`（Windows）、`~/.config/Code/User/settings.json`（Linux）。键：`claudeCode.initialPermissionMode`。（上游 Claude Code 的层，本平台不读）
2. **VSCode 工作区设置** —— `<repo>/.vscode/settings.json`。同一个键。胜过用户层。（上游层，本平台不读；这个文件本技能仍然会看，但看的是别的设置）
3. **CLI 用户设置** —— `~/.workbuddy/settings.json`。键：`permissions.defaultMode`。（上游层，本平台不读）
4. **CLI 项目设置** —— `<repo>/.codebuddy/settings.json`。同一个键。胜过用户层。（本平台读这个文件，但只读 `hooks`；这里的 `permissions.*` 不生效）
5. **CLI 项目本地设置** —— `<repo>/.codebuddy/settings.local.json`。同一个键。胜过项目层。（本平台读这个文件，同样只有 `hooks` 有意义；`permissions.*` 不生效）
6. **会话内模式** —— 会话启动时由第 1-5 层设定，之后可通过 `Shift+Tab`（CLI）或模式指示器（VS Code / Desktop）变更；`/permissions` 管的是 allow/deny 规则，不是模式。（上游机制；本平台没有可切换的权限模式档位，也没有 `permissions.*` 规则表）

**两条覆盖整个层栈的规则**（Anthropic 的 permission-modes 文档，2026-09-26 复核）：

- 第 4、5 层**不**把 `auto` 或 `bypassPermissions` 当起始模式。那里的 `bypassPermissions` 会被忽略，终端会话以 Manual（`default`）启动；那里的 `auto` 会被忽略，改用内置默认。其他任何模式值从任何一层都生效。
- VS Code 扩展**不**读第 4–5 层来定起始模式；它用 `claudeCode.initialPermissionMode`（该键不接受 `auto`），而要 bypass 值需要打开扩展的*Allow dangerously skip permissions* 开关。无任何覆盖时，上游自 2.1.283 起以 auto 模式启动——**本平台无对应机制**：没有可设的起始权限模式。

所以先查「你要找的那个开关在本平台根本不存在」这种情况 —— 再查下面那种被钩子直接拦下的动作。

**关键洞见：** 上游那句「文件层设置是对的、运行时模式却不一样」的困惑，在本平台没有对应物——没有运行时权限模式可解析，所以也不会漂移。本平台的两个真正常见来源换了：一是有人照上游文档把 `bypassPermissions` 或 `defaultMode` 写进 `.codebuddy/settings.json`，然后奇怪行为为什么没变——本平台不读这些键；二是动作其实是被 PreToolUse 钩子 deny 掉的，而钩子根本不看权限模式。两者的修法不同，但都能从文件里看出来。

## 隐私契约

宿主全局设置文件（`~/.workbuddy/settings.json`、VSCode 用户设置）可能含有：
- 无关项目的路径与密钥
- 本仓库之外加入的 API 密钥、令牌或服务商凭据
- 用户所在组织或雇主设定的权限策略

本技能是按纵深防御设计的：**阶段 A 自动运行，只读仓库本地文件。** 阶段 B **只在用户明确确认之后**才读宿主全局文件 —— 绝不偷偷读。报告宿主全局层时，凡与 `hooks`、`permissions.*`、`claudeCode.*` 或 `allowDangerouslySkipPermissions` 不直接相关的键一律打码。

## 协议

### 阶段 A：仓库本地层（自动运行）

立刻读这些 —— 它们被提交进仓库（或在仓库内被 gitignore），不越过信任边界：

```bash
VSCODE_WS="${CODEBUDDY_PROJECT_DIR}/.vscode/settings.json"
CLI_PROJECT="${CODEBUDDY_PROJECT_DIR}/.codebuddy/settings.json"
CLI_LOCAL="${CODEBUDDY_PROJECT_DIR}/.codebuddy/settings.local.json"
```

对每个存在的文件，抽取：
- **VSCode 工作区：** 与本技能相关的东西；看到 `claudeCode.initialPermissionMode` 或 `allowDangerouslySkipPermissions` 时，把它标为**本平台不读的上游键**——包括连上游都会静默忽略的错写 `claudeCode.allowDangerouslySkipPermissions`
- **CLI 项目 / 项目本地：** `hooks` 链（哪个事件、哪个 matcher、指向哪个脚本）；`permissions.defaultMode`、`permissions.allow`、`permissions.deny` 若存在，标为**本平台不读**

文件缺失没关系 —— 报告「不存在」，而不是报错。

把这三层里**实际存在**的东西打印出来：钩子链（事件 → matcher → 脚本）、`.codebuddy/settings.local.json` 的覆盖、以及任何 `permissions.*` / `claudeCode.*` 键——后者标为**不生效**，而不是解析出的模式。如果问题其实只是「某个具体动作被拦了」，就停在这里，点名是哪个守卫脚本拒的、拒的是哪条命令：破坏性 git 操作由 `.codebuddy/hooks/git-guardrails.py` 拒，对 `.codebuddy/` 的写入由 `root-of-trust-guard.py` 拒，绕过 `scripts/file-issue.py` 查重直接建 issue 的 `gh` 命令由 `issue-guard.py` 拒。

### 阶段 B：宿主全局层（需要用户明确确认）

如果阶段 A 还没有结论 —— 例如仓库本地层没有挂任何钩子，而用户仍然被请求 —— 问用户：

> 「为完成诊断，我需要读本仓库之外的两个文件：
> - `~/.workbuddy/settings.json`（CLI 用户级）
> - 你的 VSCode 用户设置（macOS 上是 `~/Library/Application Support/Code/User/settings.json`；Linux/Windows 各有不同）
>
> 这些文件可能含有无关的路径或密钥。我会给任何不在 `hooks`、`permissions.*`、`claudeCode.*` 或 `allowDangerouslySkipPermissions` 里的键打码。继续吗？」

只在用户确认之后，才读：

```bash
# VSCode user (platform-dependent path; try all three)
case "$(uname -s)" in
    Darwin)  VSCODE_USER="${HOME}/Library/Application Support/Code/User/settings.json" ;;
    Linux)   VSCODE_USER="${HOME}/.config/Code/User/settings.json" ;;
    MINGW*|MSYS*|CYGWIN*) VSCODE_USER="${APPDATA}/Code/User/settings.json" ;;
    *)       VSCODE_USER="" ;;
esac

CLI_USER="${HOME}/.workbuddy/settings.json"
```

报告它们的内容时，**只抽取相关键**：
- CLI 用户：`hooks`、`permissions.defaultMode`、`permissions.allow`、`permissions.deny`（后三项读到就标为**本平台不读**）
- VSCode 用户：任何以 `claudeCode.` 开头的键

绝不打印整个文件。其余一律打码为 `(other keys redacted)`。

### 步骤 2 —— 计算解析出的状态

本平台没有 `defaultMode` 可解析，所以这一步报告的是**钩子链的合成效果**：

- 哪个事件的哪些 matcher 挂了钩子，覆盖哪些工具。
- 同一事件上多个钩子的顺序，以及一个事实：任一钩子 deny 就拦下，后续钩子不能把它改回 allow。
- `.codebuddy/settings.local.json` 覆盖了 `.codebuddy/settings.json` 的哪几条。
- 文件里出现了 `permissions.*` 或 `claudeCode.*` 而用户以为它在生效 —— 这是一个该标出来的误解，不是一层配置。

### 步骤 3 —— 报告运行时状态

本平台不在状态行里暴露权限模式（`statusline.sh` 读的 `permission_mode` 字段在这里恒为空，那是上游的载荷），所以「会话内模式」这一项**没有对应机制**。告诉用户：

> 「你的状态行不会给你模式徽标（`[AUTO]`、`[BYPASS]`、`[PLAN]`、`[AUTO-EDIT]`、`[PROMPT]`）——那是上游 Claude Code 的显示，本平台没有可显示的模式档位。判据换成一个更硬的问题：这条命令是被**某个钩子**拒的，还是被**平台**问的？前者能在 `.codebuddy/settings.json` 里指到具体脚本与具体命令；后者不会在任何配置文件里留下痕迹——重开一个会话，看它还发不发生。」

如果状态行没有配置，发出一个警告并指向 `.codebuddy/scripts/statusline.sh`。

### 步骤 4 —— 标出常见失败模式

检查并显式指出：

1. **照上游文档设 `permissions.defaultMode` 或 `bypassPermissions`：** 本平台不读这些键，所以什么都不会变。修法：从 `.codebuddy/settings.json` 里删掉它们——留着就是假开关，还会让下一个读文件的人以为限制已经设上了。
2. **把钩子的 deny 当成权限提示：** `git-guardrails.py` 对破坏性 git 命令直接输出 `permissionDecision: deny`，那不是「等你批准」，是「不许」。修法是改命令，不是改配置。
3. **信任根守卫拦下改配置本身：** `root-of-trust-guard.py` 拒绝对 `.codebuddy/` 的写入。要改钩子就自己动手改文件，别指望代理代劳——这是安全机制，不是 bug。
4. **钩子静默失效：** `hook-runner.sh` 探测不到可用解释器时钩子不执行，同一条命令这次就过了。别把「这次没拦」读成「策略允许」——先确认钩子真的跑了（它是唯一入口，手工喂一次同样的输入看有没有输出）。
5. **过期会话：** 设置是对的，但用户报告行为没变 → 几乎总是一个早于该改动的会话。建议开一个新会话再试。
6. **`deny` 胜出：** 任一钩子 deny 都会拦下该动作，不论别处写了什么，也不论上游那套 bypass 语义——这正是受限数据项目用钩子守 `.git` 与受限路径的原因。

## 输出格式

```
=== CONFIG SURFACE ===

.codebuddy/settings.json       hooks: PreToolUse(Bash|Write|Edit|MultiEdit -> git-guardrails.py)
                                      PreToolUse(Bash -> root-of-trust-guard.py, issue-guard.py)
                                      Stop: log-reminder.py
.codebuddy/settings.local.json (absent)
.vscode/settings.json          (absent)

permissions.* keys found:      none — and they would not be read on this platform
claudeCode.* keys found:       none — upstream-only

=== BLOCKERS ===

(none observed in config) — a refusal at run time points at one of these:
  git-guardrails.py      deny  destructive git command
  root-of-trust-guard.py deny  write to .codebuddy/ (root of trust)
  issue-guard.py         deny  gh issue create that skips scripts/file-issue.py

=== DIAGNOSIS ===

No unread permission keys found. If an action was still refused:
  1. A PreToolUse hook denied it — the command is quoted above; change the command, not a setting.
  2. The hook did not run — start it by hand through .codebuddy/hooks/lib/hook-runner.sh.
  3. Session is stale (started before settings were applied) — start a new one.
```

如果某个文件里有 `permissions.*` 或 `claudeCode.*` 键，就把「No unread permission keys found」那一行替换成具体的标记问题（键名 + 「本平台不读」）。

## 备注

- 本技能是只读的。它从不修改设置。
- 如果 `$CODEBUDDY_PROJECT_DIR` 未设置，退回 `git rev-parse --show-toplevel`。
- 平台感知：为 VSCode 用户路径检测 macOS、Linux 还是 Windows；本平台无分层权限配置这一点与操作系统无关。
