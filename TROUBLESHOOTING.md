# 故障排查

这里列出新手常见的故障及修复方法。遇到本文没有涵盖的问题，请运行 `./scripts/validate-setup.sh`，它会明确指出缺少什么。

## 环境 / 安装

### WorkBuddy 客户端没装

如果尚未安装 WorkBuddy，请先通过客户端自身的发布渠道安装，本仓库不提供产品安装链接。安装后重新运行 `./scripts/validate-setup.sh`。

### Windows 上一个钩子都不运行（`[WinError 2] 系统找不到指定的文件`）

在 Windows 上，WorkBuddy **只使用 Git Bash** 执行钩子命令，不支持 cmd.exe / PowerShell。`.codebuddy/settings.json` 中的钩子命令均按以下格式注册：

```json
"command": "bash \"${CODEBUDDY_PROJECT_DIR:-.}/.codebuddy/hooks/lib/hook-runner.sh\" git-guardrails.py"
```

命令中的 `bash` 由 Git for Windows 提供。如果未安装 Git for Windows，或安装时未选择 Git Bash 组件，`scripts/check-hooks.py` 这类直接运行 `python scripts/xxx.py` 的冒烟测试仍可能全部通过，但**真实会话中的 11 个钩子都不会启动**：守卫不会拦截，日志提醒不会出现，上下文进度条也不会更新。这种故障不会给出明显提示，因此不能根据冒烟测试通过就认定钩子已经生效。

修复方法：安装 Git for Windows，确认 `where bash` 有输出，然后重开会话。只有 `/hooks` 面板显示已注册的钩子，才能确认钩子已接入。

### `xelatex: command not found`

这说明系统未安装 TeX Live。请安装 MacTeX（macOS）或 TeX Live（Linux/Windows）。安装完成前，`/compile-latex` 与 `/extract-tikz` 不可用，`/deploy`（Quarto）仍可使用。

### `quarto: command not found`

请从 [quarto.org/docs/get-started](https://quarto.org/docs/get-started/) 安装 Quarto。安装完成前，`/deploy` 与 `/qa-quarto` 不可用，Beamer 相关工作流仍可使用。

### `pdf2svg: command not found`

`/extract-tikz` 需要该命令。请按系统选择安装命令：`brew install pdf2svg`（macOS）、`apt install pdf2svg`（Debian/Ubuntu）或 `dnf install pdf2svg`（Fedora）。

### `/stata-replication` 停在「stata-mcp not registered」

Stata 流水线技能依赖 [`stata-mcp`](https://github.com/SepineTam/stata-mcp) MCP 服务器。每位用户只需安装一次，可通过**左侧「插件 → MCP 服务器 → 配置 MCP」**安装，也可直接写入 `~/.workbuddy/mcp.json`：

```json
{ "mcpServers": { "stata-mcp": { "command": "uvx", "args": ["stata-mcp"] } } }
```

`uvx` 是 `uv` 提供的包运行器；尚未安装时，可运行 `brew install uv`。该 MCP 服务器只负责连接 Stata，本机仍须安装 Stata，它不能替代 Stata。保存配置后返回 MCP 列表查看状态：绿色表示已连接，红色表示配置有误。

如果 Stata 本身不在 `PATH` 中，该技能也会停止。[`/stata-replication`](.codebuddy/skills/stata-replication/SKILL.md) Phase 0 的安装说明包含这两项起飞前检查。上游使用 `claude mcp list` 核验，但本平台没有这条命令，请根据列表中的状态圆点判断。

### WorkBuddy 为每个工具反复询问权限

先检查权限档位。桌面端只有两档，详见指南的[权限一节](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#settings---permissions-and-hooks)：

- **默认权限**：常规编辑与 shell 命令根据 `.codebuddy/settings.json` 的 `permissions.allow` 直接放行；写入受保护路径、安装软件、联网等操作仍会逐项询问。
- **完全访问权限**：跳过询问与安全检查，但 `deny` 规则与钩子仍然生效。界面会显示确认框，勾选后才会开启。Anthropic 将同类能力限制在隔离容器与虚拟机内，这里也应遵循同样的原则：只在信任的仓库中使用，并确认自己清楚它会执行哪些操作。

上游指南还列出自动、接受编辑、Plan、dontAsk 等档位，但桌面端未提供这些选项。桌面选择器也不支持 `Shift+Tab` 循环与 `--permission-mode` 启动标志；后两者属于 CodeBuddy Code CLI，见官方 [Permission Modes](https://www.workbuddy.ai/docs/cli/permission-modes)。

本模板的 `.codebuddy/settings.json` 包含多条宽泛的放行规则（`Edit(**)`、`Write(**)`、`Bash(*)` 等），且 `deny` 为空。因此，在默认档位下，大多数常规操作无需询问即可执行。如果要在任何档位下都阻止模型访问受限数据，请添加拒绝规则，见下方[「让受限数据不进入模型」](#让受限数据不进入模型)。

## 模型与 API

### `/model` 里的档位没生效，或钉死的模型 ID 失败

本平台只有 `default` / `lite` / `reasoning` **三个档位**，不提供按具体型号选择版本的列表。`effort` 是独立的思考预算维度：代理可以设置，技能不能设置。各档职责以及上游层级的映射关系见 [`model-versions.md`](.codebuddy/references/model-versions.md)。配置问题通常有两种：

- **配置未使用有效档位。** 代理或技能的 frontmatter 仍使用上游层级名（`opus` / `sonnet` / `haiku` / `inherit`）时，这些值既不报错，也不生效，会让配置看似可调、实际无效。运行 `python scripts/normalize-model-tiers.py --dry-run`，正常结果应是 0 个文件需要修改；如有输出，请按清单改为三个有效档位之一。
- **固定的模型 ID 失效。** 将 `model:` 固定为具体型号既不能提高可复现性，也可能在某次更新后无提示地失效。型号名、最低 CLI 版本与退役日期都由上游定义，本平台没有对应配置。请检查以下位置：
  - **设置：** `.codebuddy/settings.json`、`.codebuddy/settings.local.json` 或 `~/.workbuddy/settings.json` 里的 `model` 键。
  - **代理与技能：** 运行 `grep -rn "^model:" .codebuddy/agents/ .codebuddy/skills/`。本模板只应出现 `default` / `lite` / `reasoning` 三个值，其他值都属于漂移。
  - **CI：** 任何在流水线中显式传入 `--model <id>` 的工作流。

如需为某条可复现性断言保留快照，请在报告中记录当时的档位、日期与结果，不要通过固定型号 ID 来锁定它。

### 一次更新在截止日中途把东西搞坏了

客户端默认通过 `latest` 通道自动更新。截止周可在 `~/.workbuddy/settings.json` 中切换到更新较慢的通道：

```json
{ "autoUpdatesChannel": "stable" }
```

使用 `minimumVersion` 可确保自动更新不会安装低于已知可用版本的版本。应优先使用这两项设置，不要直接关闭更新器；更新包含安全修复与新模型支持，而新模型可能要求最低版本。

### 无头运行：桌面客户端没有命令行

WorkBuddy 桌面客户端不提供命令行入口。如需在脚本、cron 或例行任务中运行，必须另装独立产品 **CodeBuddy Code CLI**：安装命令为 `npm i -g @tencent-ai/codebuddy-code`，命令为 `codebuddy` / `cbc`，配置目录为 `~/.codebuddy`，文档见 <https://www.workbuddy.cn/docs/cli/headless>。非交互调用必须带 `-y`。它与桌面端共用引擎，但**使用不同的配置目录**。安装前请先阅读官方关于「与 WorkBuddy 共存时避免配置冲突」的说明。

本仓库只有 `scripts/run-skill-eval.sh` 依赖它，用于技能 A/B 评测。脚本按 `EVAL_CLI` → `codebuddy` → `cbc` → `claude` 的顺序探测；如果都找不到，会打印安装命令并以 `2` 退出。**该脚本不属于任何门禁**，因此未安装 CLI 不影响模板正常使用。

还要注意，`session-handoff.py` 与 `open-issues.py` 通过 `CLAUDE_CODE_ENTRYPOINT` 判断是否处于无头模式，并据此决定「无头时不递交接 / 不自动开 issue」。桌面端引擎**不会设置**该变量。若要在 cron 中稳定禁用这两个行为，请显式导出 `CODEBUDDY_HANDOFF=off` 与 `CODEBUDDY_ISSUES_AT_START=off`。

## 技能发现、安装与更新

### 市场安装的技能没有出现在项目目录

市场安装或上传的技能，以及通用创建器生成的技能，默认保存在**用户技能库**中，以便跨项目复用，不会自动写入当前项目的 `.codebuddy/skills/`。因此，项目目录中没有该技能，并不表示项目技能发现失败。`.codebuddy/skills/` 是官方支持的项目技能目录，其中的技能随仓库共享，项目级技能优先于用户级技能。如需随仓库共享，必须显式把技能放进这个目录。

两个创建入口的用途不同：本仓库的 `/new-skill` 按本仓库约定生成项目技能；WorkBuddy 内置的 `/skill-creator` 是通用创建器，GUI 入口为**技能 → 添加技能 → 创建技能**。

### 菜单里看不到技能，或修改后没有按新正文运行

请分别核验四件事：引擎能否发现技能、能否自动调用、能否通过 `/name` 显式调用、UI/菜单是否可见。菜单不显示不等于引擎无法发现或调用；自动匹配失败也不等于显式调用失败。元数据用于匹配，触发后加载正文，附属材料按需读取；引擎不会每轮从磁盘读取所有描述。

技能修改后是否会热重载**尚未得到证实**，不要假定无需重启。如果运行行为未反映新正文，请记录客户端版本与技能版本，在新会话中复测，并分别记录自动调用与显式调用的结果。

### 技能需要某个工具，但 `allowed-tools` 没列它

按照官方定义，`allowed-tools` 是白名单，用于限制技能可用的工具。请把实际需要的工具加入白名单，并检查工具名与模式是否拼写正确。即使桌面端某个版本在实测中允许调用未列出的工具，也不能据此推断这是通用行为；必须单独记录客户端版本、最小探针与实际输出。目前尚无此类 L3 反证。该白名单可用于只读限制，但不是绝对安全边界。仍须核验模型实际调用、`permissions.allow` / `permissions.deny` 与 PreToolUse 等钩子；高风险场景还应添加拒绝规则或钩子。

## 编译 / 渲染

### Beamer 里的 `Undefined citation`

`.bib` 的引用键不在 `Bibliography_base.bib` 中。请运行 `/validate-bib`，交叉核对引用与 bib 文件。`/compile-latex` 的 3 遍 XeLaTeX + bibtex 序列可以解析已存在的键，但无法生成缺失的键。

### `Overfull \hbox` 警告

文字超出了幻灯片的可打印宽度。可以缩短超出的内容；对于 TikZ，可将其放入带 `text width=...` 的节点；也可以改用 `\resizebox`。`/visual-audit` 和 `/proofread` 都会标出这些问题。

### Quarto 渲染失败并报 `No valid input files`

通常是当前工作目录不对。请在仓库根目录运行 `quarto render`；`/deploy` 会自动处理工作目录。

### HelloWorld.tex 编译不过

先运行 `./scripts/validate-setup.sh`。如果已安装 XeLaTeX，请重新 fork 一份干净的副本，因为你可能无意中修改过示例讲义。HelloWorld 特意保持极简，在全新克隆中应始终能够编译。

### `/extract-tikz` 停在预防检查上

这说明预检正常生效：它发现了一处 P3（裸 `scale=`）或 P4（边标签缺少方位关键词）违规。请修正 Beamer 源码中的对应行，再重新运行。规则见 `.codebuddy/rules/tikz-prevention.md`。

### 幻灯片 QA「跑不起来」（退出码 2）

`scripts/slide-qa.py` 在无头 Chrome 中度量一套已渲染的 Quarto 幻灯片。退出码 2 表示它未完成任何度量，此时技能会改为读取源码。报错信息会说明具体原因：

- **缺 Playwright。** Homebrew 或系统 Python 会拒绝普通的 `pip install`，因此需要在虚拟环境中安装一次，并让技能使用该环境：`python3 -m venv ~/.venvs/slide-qa && ~/.venvs/slide-qa/bin/pip install playwright`，然后运行 `export SLIDE_QA_PYTHON=~/.venvs/slide-qa/bin/python`，并把这条 export 命令写入 shell 配置。`./scripts/validate-setup.sh` 会检查该环境。
- **没有浏览器。** 脚本使用本机已安装的 Google Chrome；如果尚未安装，请运行 `$SLIDE_QA_PYTHON -m playwright install chromium`。
- **渲染过期。** `.qmd` 比对应的 `.html` 新。请先重新渲染，否则度量结果仍属于旧版讲义。
- **报告里出现「Math was not typeset」**，但不是退出码 2：MathJax 或 KaTeX 未加载，常见原因是离线，公式因此被当作裸 TeX 度量。

## Git / 钩子 / CI

### 桌面通知不出现

先确认钩子是否触发过：

```bash
tail -5 quality_reports/session_logs/notifications.log
```

如果文件中有记录，说明钩子已运行，每行都包含时间与原始 title/message，问题出在终端或通知中心。如果文件为空或不存在，说明钩子未运行，请按顺序检查两层：

1. **命令是否到达钩子文件。** `python scripts/check-hooks.py` 末尾会打印
   `[OK] 注册接线：…（12 条）`。断言失败时，它会指出具体事件与命令。这一步检查
   `hook-runner.sh` 的仓库根与解释器分派。2026-10-30 之前，这部分存在故障，而 `notify.sh` 又被
   `check_wiring()` 跳过，因此两类故障都未被发现。
2. **平台是否发送 `Notification`。** 这一层目前仍需运行时证据，`platform-facts.md` 的钩子表
   记录了它的证据级别。

如果只想单独验证而不弹窗，可设置 `NOTIFY_DRY_RUN=1`：它会跳过桌面通知，但保留日志记录。

### 钩子脚本 permission denied

请运行 `chmod +x .codebuddy/hooks/*.py .codebuddy/hooks/*.sh`。`./scripts/validate-setup.sh` 也会报告不可执行的钩子。

### 第 10 门为什么显示 PARTIAL，第 3 门为什么 SKIPPED

门禁清单位于 `scripts/gate-manifest.py`，该文件是唯一真源。每道门都声明自身的运行前提：

- **第 3 门 SKIPPED**：`check-model-versions.sh` 是 Bash 脚本，而本机 PATH 中没有
  bash。脚本没有执行，汇总会单独列出这一状态，不记作通过。
- **第 10 门 PARTIAL**：钩子测试组依赖 POSIX 宿主机制，包括 symlink 夹具、`timeout(1)`，
  以及解释器能否解析事件 JSON 中的 POSIX 路径。Windows 无法运行全量测试，本机改为运行
  `check-hooks.py`，即迁移关键子集，并直接在门禁结果中说明能力上限。

这两种状态都不影响退出码，但都会在汇总中单独列出。**部分检查未运行时，不得将结果显示为普通 PASS。**

### Windows 上「钩子可运行」与「第 11 门宿主边界」是两件事

先检查实际安装结果。在 WorkBuddy 能继承的环境中运行 `where bash`，确认输出指向
要使用的 Git Bash，然后重开会话。`C:\Program Files\Git\bin`、`D:\Git\bin` 等标准安装
位置只能作为示例，不能代替 `where bash` 的结果。如果没有输出，请修复 Git for Windows / Git Bash
安装，或让 WorkBuddy 进程的 PATH 包含实际安装目录。不要为了规避门禁而把 bash 移出 PATH。

这里需要分别判断两件事：

- **钩子能否运行**：钩子命令直接以 `bash` 启动，因此 WorkBuddy 进程必须能找到它。第 3 门在
  找不到 bash 时记为 SKIPPED，找到后才真正执行。再用 `/hooks` 面板确认注册钩子已接入。
- **第 11 门的宿主前提**：这批用例用「有 POSIX shell」判断是否跳过，但实际要求是
  「**宿主是 POSIX**」。Windows + Git Bash 只满足前者，因此用例仍会执行，并可能因 Windows 的
  路径、符号链接与 git 行为而失败，2026-10-29 本机实测有 26 条失败。CI（Linux）不受影响。

因此，修好钩子并不等于消除第 11 门的宿主边界，也不要为了让该门通过而修改断言。报告时应
分别说明 bash/钩子检查结果与 Windows 宿主限制。

### 压缩前的钩子没把计划存下来

PreCompact 钩子（`.codebuddy/hooks/pre-compact.py`）会将状态写入 `~/.workbuddy/sessions/<hash>/`。如果压缩后状态不在那里，请检查：

- 钩子的退出码：`echo '{}' | python3 .codebuddy/hooks/pre-compact.py` 应当以 0 退出。
- `~/.workbuddy/sessions/` 的权限。
- 会话哈希是否匹配，压缩过程会记录该哈希。

### 会话启动时冒出一份交接

`session-handoff.py` 会把最近 7 天内最新的 `/checkpoint` 或 `/compress-session` 文件交给新会话，并标记为「待核验的笔记」。你在该会话输入第一条提示词后，系统就会将这份交接记为已使用，因此它只出现一次。如需跳过，请在 shell 或 settings 的 `env` 中设置 `CODEBUDDY_HANDOFF=off`；如需调整时间窗口，请使用 `CODEBUDDY_HANDOFF_MAX_AGE_DAYS`。另装 CLI 后，通过 `-p` 进行的无头调用不会收到交接，但这项判断依赖的 `CLAUDE_CODE_ENTRYPOINT` 在本平台不会被设置，因此在 cron 中仍应显式设置 `CODEBUDDY_HANDOFF=off`。如果另一个记忆工具也在启动时注入上下文，请关闭其中一个。

### `/commit` 因 `quality_score.py` 低于阈值而失败

脚本在改动的文件中发现了问题。建议修复后重跑；如确需跳过，也可重跑 `/commit`，明确告诉 WorkBuddy **「commit anyway」** 或 **「skip quality gate」**，并给出理由。此次覆盖会记录在提交信息中。这里没有 `--skip-quality-gate` 这个 CLI 参数；覆盖是对技能发出的自然语言指令。

## 调色板 / 主题

### Beamer 与 Quarto 的渲染配色不一致

这说明两处调色板未同步。请运行 `./scripts/check-palette-sync.sh`，它会报告哪一侧缺少哪些颜色名。请同时修改 `Preambles/header.tex` **与** `Quarto/theme-template.scss`，使两处的 HEX 值一致。完整约定见 `Preambles/README.md`。

## R / 数据分析

### R 装了但不在 PATH

`./scripts/validate-setup.sh` 会打印 `R found ... but NOT on PATH`，并给出应加入 PATH 的目录，Windows 下通常是 `C:\Program Files\R\R-<版本>\bin`。技能直接以 `Rscript` 调用 R；如果不把它加入 PATH，`/data-analysis`、`/review-r`、`/audit-reproducibility` 等技能会因 `Rscript: command not found` 而失败。Windows 安装器默认不勾选「加入 PATH」，请手动添加，然后重启 WorkBuddy 或新开终端。

### `here::here()` 解析到了错误的目录

`here` 通过项目根标记确定项目根，包括 `.here`、`.git`、`DESCRIPTION` 或 `.Rproj`。如果解析出的路径有误，请在仓库根目录创建一个空的 `.here` 文件。

### 分析改动之后 `sessionInfo.txt` 没更新

这说明你直接运行了 `03_analyze.R`，而没有运行 `00_run_all.R`。请重跑 `00_run_all.R`，例如通过 `/data-analysis` 技能或常用的流水线运行器。该入口会在最后一步写出会话快照。

## 权限 / 状态栏（v1.6.0 / v1.8.0）

### 「明明想减少询问，桌面端还是弹提示」

请根据桌面端实际提供的控件与配置排查：

1. **看输入框旁的权限选择器。** 桌面端只有**默认权限**与**完全访问权限**。默认权限下，超出允许范围的操作仍会询问；完全访问权限会跳过询问与安全检查，但 `deny` 规则与钩子仍然生效。如果确实需要后者，请切换到**完全访问权限**，不要寻找 Bypass。
2. **不要套用上游设置。** `defaultMode: "bypassPermissions"`、`Shift+Tab`、VS Code 的 `claudeCode.*` 键属于上游 CLI / 扩展产品线，不是桌面端的操作步骤。无论在项目设置还是 `~/.workbuddy/settings.json` 中配置 bypass，都不能在桌面端开启完全访问权限。
3. **检查过期会话。** 如果权限相关设置在会话启动后才修改，请新建会话复测。

运行 `/permission-check`。它会读取**钩子链**（`.codebuddy/settings.json` 的 `hooks` 段）、
本地覆盖配置（`settings.local.json`，以及若存在的 `.vscode/settings.json`）与三个守卫脚本，判断操作是被
哪条守卫拦截，还是由平台发起询问。它还会指出哪些来自上游文档的开关在桌面端**完全不生效**，例如
`claudeCode.initialPermissionMode`。这类配置不会报错，也不会产生任何效果。

### 让受限数据不进入模型

WorkBuddy 读取的每个文件都会发送给模型供应商。[`confidential-data.md`](.codebuddy/rules/confidential-data.md) 规定受限微观数据永不离开本机，而**拒绝规则在桌面端两种权限档位下都生效，包括完全访问权限**。如果项目包含受限目录，请添加拒绝规则，并写清数据使用协议覆盖的路径。将规则写入 `.codebuddy/settings.json` 可保护每位合作者；写入 `.codebuddy/settings.local.json` 则只保护本机：

```json
{
  "permissions": {
    "deny": [
      "Read(**/restricted/**)",
      "Read(**/confidential/**)",
      "Edit(**/restricted/**)",
      "Edit(**/confidential/**)"
    ]
  }
}
```

- **路径模式。** `**/` 能匹配任意深度，但只在项目之内；相对模式无法覆盖存放在别处的数据。对于检出目录之外的数据，请用 `//`（绝对）或 `~/`（家目录）为模式定锚，例如 `Read(//Volumes/secure-dua/**)`、`Read(~/Dropbox/ProjectX-DUA/**)`。单个前导 `/` 不表示绝对路径：在 `.codebuddy/settings.json` 或 `.codebuddy/settings.local.json` 中，它锚定到会话的工作目录，从项目根启动时就是项目根；在 `~/.workbuddy/settings.json` 中，它锚定到 `~/.workbuddy/`。因此，真正绝对的路径必须使用 `//`。可以从 `confidential-data.md` 加载的模式开始，包括 `data/**`、`**/raw/**`、`**/*.dta`、`**/*.sav`、`**/restricted/**`、`**/confidential/**`，只保留数据使用协议覆盖的模式。如果拒绝整个 `data/**`，也会阻止 WorkBuddy 读取你可能希望它读取的公开数据。
- **本机规则存放。** 这类与机器相关的规则应写入 `.codebuddy/settings.local.json` 或 `~/.workbuddy/settings.json`，绝不能写入已提交的 `settings.json`。
- **覆盖范围。** Read/Edit 拒绝规则覆盖 WorkBuddy 的文件工具、WorkBuddy 在 Bash 中能够识别的文件命令（`cat`、`head`、`tail`、`sed`、`tee`）以及重定向目标。
- **无法覆盖的情况与后续核验。** 规则不覆盖未指定文件名就读取文件的命令（`grep -r pattern .`），也不覆盖自行打开文件的脚本。因此，这些规则只是一道防线，不能当作证明。还应遵守 `confidential-data.md` 的要求：WorkBuddy 编写*作用于*数据的代码，但不读取数据；任何基于这些数据生成的产物离开本机前，都必须配合 `/disclosure-check`。

### `/permission-check` 读 `~/.workbuddy/` 之前会先问

这是有意设计的，因为宿主全局配置可能包含无关路径与密钥。Phase A 自动检查仓库本地配置；Phase B 检查宿主全局配置并进行密钥脱敏，但需要明确确认。背景见 [CHANGELOG v1.6.0——隐私边界](CHANGELOG.md)。

### 权限询问太多了？

先确认询问来自哪里。本平台有三个彼此独立的来源：

1. **`permissions` 规则**：`.codebuddy/settings.json` 的 `allow` / `deny` 会逐条匹配工具操作，上面「让受限数据不进入模型」一节使用的就是这套机制。本模板自带七条通配 `allow`，`deny` 为空。
2. **界面上的档位选择器**：只有**默认权限**与**完全访问权限**两档（`sandbox.defaultPermission` / `sandbox.fullAccessPermission`）。
3. **PreToolUse 钩子**：钩子可以直接拒绝操作，且**不检查**权限规则。

因此，「每次都问」不一定是配置错误。请按以下顺序排查：

1. **先确认是否由钩子拒绝。** 守卫拒绝时会指出具体脚本；平台询问则不会在任何配置文件中留下记录。两者的处理方法完全不同。
2. **再检查权限档位。** 选择器处于「默认权限」时，写入受保护路径、安装软件、联网等操作仍会询问。这是预期行为，不是配置遗漏。
3. **最后才添加规则。** 如果确实是反复出现的常规操作，再将其写入 `permissions.allow`，格式与上游一致，例如 `"Bash(git status:*)"`。不要一次添加大量 `Bash(*)` 之外的宽泛规则；规则越多，越难判断具体操作由哪条规则放行。

上游的 `/fewer-permission-prompts` 可以扫描转录并自动生成允许清单，本平台**没有对应工具**。规则文件需要人工阅读和审核，不应自动生成。如需添加规则，请自行编写并检查 diff。

遇到权限询问时，先运行 `/permission-check`，分清是「守卫拦截」还是「平台询问」。两者的补救方式不同，不能混为一谈。

### 状态栏什么都不显示（包括 `gate:off` 徽标）

**这是预期行为，不是故障。** 已核实桌面渲染层不会使用 `statusLine`；引擎是否读取该设置键尚未证实。2026-10-30 核查本机客户端包时，`statusLine` 的 8 次命中全是 HTTP 状态行，不能作为引擎读取该键的证据。`.codebuddy/scripts/statusline.sh` 保留给 CodeBuddy Code CLI 使用；桌面端不会显示它，也无需修复。

这会带来两项影响，可分别这样处理：

- **看不到模式徽标**：直接查看界面上的档位选择器（默认权限 / 完全访问权限）。
- **看不到 `gate:off` 徽标**：使用该徽标原本要提醒你的命令自查。`git config --get core.hooksPath` 应输出 `.githooks`；如果不是，请运行一次 `./scripts/install-hooks.sh`。未配置它时，普通的 `git commit` 会跳过全部门禁。

### 改 `.codebuddy/`、`.git/` 会弹询问

这**不是 bug**。受保护路径包括 `.git`、`.vscode`、`.idea`、`.husky`、`.devcontainer`、`.codebuddy`（`.codebuddy/worktrees` 除外）、shell 的 rc 文件、`.mcp.json` 以及其他几个路径。写入这些路径时，放行规则永远不会自动批准，即使 `allow` 中包含 `Bash(*)` 也一样。具体行为取决于档位：**默认权限**下会询问，**完全访问权限**下会放行。当询问涉及项目的 `.codebuddy/` 目录时，界面会提供一个会话作用域的选项：「允许编辑本项目 `.codebuddy` 目录里的文件」。

如需批量编辑 `.codebuddy/rules/`、`.codebuddy/references/`、`.codebuddy/skills/` 或 `.codebuddy/agents/` 下的文件，可通过 Bash 工具运行一次脚本完成，避免逐文件询问。但本模板自带的 `root-of-trust-guard.py` 钩子会**拒绝**通过 shell 写入 `.codebuddy/settings*.json`、`.codebuddy/hooks/` 与 `.githooks/`。这些位置请使用 Edit/Write，确保每次门禁修改都留下可审读的 diff。

### 本仓库为什么不再提供 `.vscode/settings.json`

上游模板包含这个文件，其中设置了 Claude Code VS Code 扩展的两个键：`claudeCode.initialPermissionMode`、`claudeCode.allowDangerouslySkipPermissions`。本平台的桌面客户端不读取 VS Code 工作区设置，本机也没有对应扩展，因此这两个键不会产生任何效果。保留该文件会误导读者，使其以为已开启完全访问；当写入受保护路径仍被询问时，又会误以为存在 bug。

如果桌面端确需跳过权限询问，请通过输入框旁的权限选择器切换到**完全访问权限**。上游 CLI / VS Code 的 bypass 设置属于另一产品线，不要将这些设置写成桌面端的操作步骤。如需确认某个动作由谁拦截，请运行 [`/permission-check`](.codebuddy/skills/permission-check/SKILL.md)。它读取钩子链与守卫脚本，不读取不存在的配置文件。

## 同行评审流水线（v1.5.0）

### `/review-paper --peer AER` 报「journal not found」

目标期刊必须列在 [`.codebuddy/references/journal-profiles.md`](.codebuddy/references/journal-profiles.md) 中。模板自带 8 份画像：AER / QJE / JPE / ECMA / ReStud（经济学）与 APSR / AJPS / JOP（政治学）。如需添加所在领域的期刊，请将 [`templates/journal-profile-template.md`](templates/journal-profile-template.md) 复制到 `journal-profiles.md`，填写 7 个 schema 小节：关注点、门槛、领域调整、方法调整、典型关切、审稿人池权重、可选表格格式。

### 审稿人交回的报告几乎一模一样

这说明审稿取向未得到正确分配。编辑代理应从六类取向（STRUCTURAL / CREDIBILITY / MEASUREMENT / POLICY / THEORY / SKEPTIC）中选择**两种不同**的取向。如果报告雷同，通常是论文范围较窄，编辑只选择了一个适用分类。可尝试 `--peer <journal> --stress`，强制配对对抗式取向。

### R&R 跟进丢掉了上一轮的上下文

使用 `--peer <journal> --r2` / `--r3` 继续一次已有审读。编辑会跳过新的初审，重新读取上一轮的报告（`quality_reports/peer_review_<paper>/desk_review.md`、`referee_domain.md`、`referee_methods.md`），并沿用同一批审稿取向与忌讳。随后，每位审稿人会将上一轮的每条主要关切标记为 Resolved / Partial / Not addressed。如果上一轮报告缺失或被改名，续接链条就会中断，请使用 `--peer` 从头开始。

## 表面同步门禁（v1.6.0）

### `/commit` 在 Step 0b 失败并报「DRIFT DETECTED」

Step 0b 会运行 `./scripts/backtest.sh`。其中的表面同步门禁（`scripts/check-surface-sync.py`）发现文档声称的某个计数，或某张 `<!-- surface-sync-table -->` 表格的行数，与磁盘上的实际情况（技能 / 代理 / 规则 / 钩子）不符。脚本会用 `file:line  asserts N <kind> (actual: M)` 逐条列出过期的表面。请修正所有标出的表面，再重跑 `./scripts/backtest.sh`，也可只运行 `python3 scripts/check-surface-sync.py`。如果是其他门禁失败，请阅读该门禁自身的输出。**不要绕过这道门禁**。手工 `replace_all` 曾三次遗漏同类表述，对应 v1.5.x 中的 PR #70/#76/#78，因此需要这项检查。

### 加一个新技能 / 代理 / 规则就把门禁弄红了

这是预期结果。门禁会比较磁盘上 `.codebuddy/skills/` 的数量与正文中的计数断言，并要求 README.md 中每张 `<!-- surface-sync-table: ... -->` 表格对磁盘上的每一项恰好只有一行。新增技能后，请将它的行加入 README.md 的技能表；如果新增的是代理，则加入代理表。然后更新 README.md、CODEBUDDY.md（若提到）、`guide/workflow-guide.qmd` 与两份渲染副本（`guide/workflow-guide.html`、`docs/workflow-guide.html`）、`docs/index.html`（og:description 与「What you get」一节）、`templates/skill-template.md` 以及 `.codebuddy/skills/commit/SKILL.md` 中的计数。脚本会指出哪些内容已过期，请重跑直到它以 0 退出。

## 起飞前报告（v1.6.0）

### 技能停在「Pre-Flight Report failed — inputs not readable」

技能无法读取某个必需输入，例如数据集、期刊画像、记号登记表或 `r-code-conventions.md`。请检查报错给出的文件路径与权限，并确认全新 fork 应包含的文件确实存在。`/create-lecture` 对记号登记表提供了全新 fork 下的后备方案，其他技能没有。**不要**为了跳过起飞前检查而修改技能。这项检查的作用是在开始工作前发现编造的变量名与缺失的约定。

### 起飞前检查通过了，代理还是在编

请创建一个 issue 并附上起飞前报告。原因可能是输入 schema 不完整，也可能是代理无视了报告；两种情况都应作为 bug 报告。

## 决策记录（v1.6.0）

### ADR 该存哪儿？

请使用 [`templates/decision-record.md`](templates/decision-record.md)，将 ADR 保存为 `quality_reports/decisions/YYYY-MM-DD_short-description.md`。该目录与 `plans/`、`specs/` 一样已被 gitignore，只有希望他人看到这份记录时才提交。多数 fork 本仓库的用户会将决策留在本地。

## 降落后核验 / 链式核验（v1.7.0）

### `/verify-claims` 超时或报错

`claim-verifier` 在独立子会话中运行时采用保守策略：没有证据，就不会将断言标记为已核验。如果它中途超时或报错，技能会显示警告块，不会静默发出草稿；这与起飞前检查一样采用失败关闭。草稿以**暂定**状态返回，应视为未核验。下一步可以：

- **重试时缩小来源范围。** `/verify-claims --source <specific-paper.pdf>` 比让代理自行寻找来源更快，也更可靠。
- **改用直接抓取，不再依赖 WebSearch。** 如果代理卡在网络检索上，请将 PDF 下载到 `master_supporting_docs/`，再通过 `--source` 传入。
- **降级为只警告。** 如果你正在亲自阅读来源且只需要一份报告，可以使用 `--no-fail-closed`。

### 核验者对你确信正确的断言说「cannot-verify」

这表示核验者如实报告了证据状态，可能有以下原因：

- 无法获取源材料，例如付费墙、失效的 URL、受限数据集的 codebook 未公开。
- 断言的措辞无法转化为具体的可核验问题。例如「这是个有前途的方向」是观点，不是事实性断言。
- 证据存在，但位于代理无法访问的位置，例如会议论文集在登录墙后、工作论文不在 arXiv 上。

处理方法：提供规范的来源（DOI / arXiv / 仓库路径）；或者保留最终输出中的 `cannot-verify` 标记，并由人工确认。

### 集成技能（例如 `/lit-review`）卡在降落后检查这一步

如果调用方技能启动 `claim-verifier` 后一直没有返回，请检查：

1. 调用方技能是否可以使用 `Agent` 工具（旧别名 `Task`），请在 `SKILL.md` 中查看它的 `allowed-tools`。
2. 代理在 `.codebuddy/agents/<name>.md` 中的 `tools:` frontmatter 是否包含所需工具（`WebFetch`、`WebSearch`、`Read`）。
3. 网络是否可达。WebSearch + WebFetch 需要联网；在离线的 fork 上必须禁用它们，或将核验者放在某个检查之后。

如果本次运行确实卡住，可以使用 `--no-verify` 绕过。如果问题持续存在，请创建一个 issue。

### 退出降落后核验

除 `/review-paper` 外，每个受影响的技能都接受 `--no-verify`，用于跳过降落后核验。`/review-paper` 没有 `--no-verify`。传入 `--no-novelty-check` 可关闭 `--peer` 的新颖性探针，同时去掉它的降落后步骤；只要探针运行，降落后检查就是强制的。以下情况可以退出：

- 你正在快速迭代，并自行核验。
- 你已经人工核查过来源。
- CoVe 额外约 2× 的 token 成本超出紧张的预算。

以下情形**不要**退出：

- 为外部读者制作交付物，例如给委员会看的文献综述、给编辑的 R&R 回复、项目申请书的文献勘察。
- 草稿中有 >5 条你本人未核验过的引用。
- `/lit-review` 刚刚返回结果，它是整个模板中最常见的幻觉来源。

## `check-skill-integrity` 失败

表面同步门禁会在计数同步检查之后运行 `check-skill-integrity.py`。它执行五项机械检查：frontmatter 与正文中的工具是否一致、argument-hint 与正文中的旗标是否一致、内部锚点能否解析、规则与技能的关键词是否一致，以及 `RULE_KEYWORDS` 登记是否完整。每条作用于 `.codebuddy/skills/` 的规则都必须登记在册。检查结果按文件报告 P0/P1/P2 发现。

### P0：正文调用了工具 X，但 frontmatter 的 allowed-tools 是 [...]

技能的 Steps/Workflow 一节要求使用某个工具，但 frontmatter 的 `allowed-tools` 数组没有列出它。该工具通常是用于派生子代理的 `Agent` 或其旧别名 `Task`，也可能是 `Edit`/`Write`/`MultiEdit`/`NotebookEdit`。这表示仓库的**文档一致性检查**失败，同时说明正文所需工具不在官方定义的白名单内。如果正文确实需要该工具，请将其加入 `allowed-tools`；如果不需要，请修正正文。白名单不是绝对安全边界，仍须核验模型实际调用、权限规则与钩子。

### P1：在 path/to/file.md 里找不到锚点 `#foo`

内部 markdown 链接 `[text](path#anchor)` 指向了不存在的标题。可能原因包括标题已改名、手工填写的锚点 slug 不符合标题经 GitHub 风格 markdown 变换后的结果，或链接目标文件错误。请将锚点改为与某个既有标题匹配，或补上缺失的标题。

### P2：正文把 `--foo` 记为选项旗标，但 argument-hint 是 '...'

技能正文通过表格、列表或退出说明描述了某个旗标，但单行的 `argument-hint` 没有列出它，因此用户无法从提示中发现该旗标。请将该旗标追加到 `argument-hint`；如果它并非真正的选项，请从正文中删除。

### P0：规则 foo.md 在 paths: 里列了这个技能，但技能正文里一条都不含 [...]

某条规则的 `paths:` 声称该技能遵守这条规则的协议，但技能正文没有提到该协议的任何关键词。请将协议加入技能（推荐），或从规则的 `paths:` 中删除该技能。关键词映射位于 `scripts/check-skill-integrity.py` 的 `RULE_KEYWORDS` 下，新增规则需要在那里添加一条映射。

### 误报与正则调优

如果某项发现明显不正确，例如将 shell 命令的旗标当成技能旗标，或将示例链接当成真实链接，可能需要调整 `scripts/check-skill-integrity.py` 中的正则。共用的辅助函数 `strip_code()` 会将行内代码跨度与围栏代码块置空。对于新的误报类别，请在相关检查中添加排除规则，并用行内注释说明。

## 可移植性回归集（门禁第 11 门）

`scripts/portability-tests.py` 运行 `tests/portability/` 下的用例，覆盖路径分隔符、代码页、
行尾、BOM、git 对非 ASCII 与含引号文件名的输出，以及大小写不敏感磁盘上的路径。结果分为
三种：PASS 表示每条用例都已运行；PARTIAL 表示运行完成，但部分用例因本机缺少机制而跳过；
FAIL 表示有用例失败，或一条用例都未运行。

### 门 11 报 PARTIAL，上限写着「N of M cases not exercised on this host」

已运行用例通过，但整体是覆盖有上限的 PARTIAL。汇总会将它单独列出，不并入 PASS。是否需要处理，
请根据上方打印的逐条原因判断：

- `需要 POSIX shell（bash 或 /bin/sh）`：本机未安装 Git for Windows。安装后即可运行，
  同时解决钩子在 Windows 上不运行的问题，见上面相关章节。
- `本机不允许 os.symlink`：Windows 需要开发者模式或提权，满足条件后即可运行。
- 其余原因大多写着「本类在 POSIX 宿主上用 ntpath 模拟 Windows」：在真正的 Windows 环境中，
  这些用例由 `NativeTest` 覆盖。模拟层在 Windows 上会产生失真，因此按设计跳过。

**不要为了让未覆盖用例的数量看起来更少，把跳过也算作通过。** 未运行却记为通过的用例，
比明确标记为跳过的用例更糟，因为它会掩盖能力上限。正确的修复方法是安装所需机制，
或在真实目标机器上运行一遍。

### `portability-tests: CANNOT RUN — every one of N cases was skipped`

退出码为 2，表示**一条用例都未运行**，本次运行没有验证任何内容。它与
「空扫描报绿」属于同一类缺陷，因此不能按 PASS 处理。请先查看上面的逐条跳过原因；
如果全部是因为「缺机制」，说明这台机器缺少多项机制。

### 加了一条新用例，它在旧代码上也是绿的

这条用例就不是 PIN（用于暴露缺陷的用例），只是 CONTROL。两类用例都需要：PIN 证明检查会失败，
CONTROL 证明检查不会「拒绝一切」。如果你原以为一条用例是 PIN，但它在旧代码上也能通过，
说明它验证的不是你以为的缺陷。请将它改为在旧代码上确实会失败，或如实标为 CONTROL。

## 调度自主工作

### 会话一关 `CronCreate` 就死

**默认模式确实如此，但这是参数选择导致的，不是平台缺陷。** 2026-10-30 已根据引擎实测更正：
此前这一节称「即便 `durable: true` 也救不了你」，该说法在本平台不成立。

- `CronCreate(cron, prompt)`：仅保存在内存中，会话结束即消失。适合活动会话内的短延时轮询，
  例如「我干活的时候每 5 分钟查一次构建」。
- `CronCreate(cron, prompt, durable: true)`：写入 `.codebuddy/scheduled_tasks.json`，
  **重启后仍保留**，由专用任务会话执行。过夜工作与定时审计应使用它。
- 如需指定工作目录、权限档位、连接器，或希望在界面中查看和暂停日程，请使用
  automation（`automation_update`）。

**本平台没有云端例程。** 三种原语都在本机运行，因此合上笔记本后无法继续运行。要保留本地文件
可见性，就必须让机器保持开机。完整对比见
[`.codebuddy/references/scheduled-routines.md`](.codebuddy/references/scheduled-routines.md)。

### 我批准了计划，PreCompact 还是不停阻断

环境中可能设置了 `CODEBUDDY_PRECOMPACT_BLOCK_ON_DRAFT=1`。该钩子对每份 DRAFT 计划最多阻断**一次**，同一份计划的后续压缩会正常进行。如果它反复阻断，可能是计划的 status 行没有从 DRAFT 更新为 APPROVED/IN_PROGRESS，请查看计划文件头部；也可能是每次拿到不同的 DRAFT 计划，钩子按计划路径跟踪。如需彻底关闭这道防线，请取消该环境变量：`unset CODEBUDDY_PRECOMPACT_BLOCK_ON_DRAFT`。

## 还是卡住？

- 请阅读[指南的故障排查一节](https://sellyew.github.io/Workbuddy-workflow/workflow-guide.html#troubleshooting)，其中有更完整的故障恢复步骤。
- 请前往 <https://github.com/Sellyew/Workbuddy-workflow/issues> 创建 issue，缺陷报告模板会要求提供诊断所需的环境细节。
