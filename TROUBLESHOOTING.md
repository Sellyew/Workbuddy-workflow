# 故障排查

新手最常撞上的失败模式，附带修复办法。若你卡在别处，跑 `./scripts/validate-setup.sh`——它会精确报告缺什么。

## 环境 / 安装

### WorkBuddy 客户端没装

WorkBuddy 没装。装好客户端（安装入口在客户端自己的发布渠道里，本仓库不代管产品安装链接），然后重跑 `./scripts/validate-setup.sh`。

### Windows 上一个钩子都不运行（`[WinError 2] 系统找不到指定的文件`）

WorkBuddy 在 Windows 上**强制用 Git Bash** 执行钩子命令（不支持 cmd.exe / PowerShell），而 `.codebuddy/settings.json` 里每条注册都长这样：

```json
"command": "bash \"${CODEBUDDY_PROJECT_DIR:-.}/.codebuddy/hooks/lib/hook-runner.sh\" git-guardrails.py"
```

那个 `bash` 来自 Git for Windows。没装它（或安装时没勾 Git Bash 组件），`scripts/check-hooks.py` 这类直接 `python scripts/xxx.py` 的冒烟测试照样全绿，但**真实会话里 11 个钩子一个都不会启动**——守卫不拦、日志提醒不出现、上下文进度条不动。失败方向是安静的，所以不要用冒烟测试的绿灯推断钩子在生效。

修复：装 Git for Windows 后确认 `where bash` 有输出，重开会话；`/hooks` 面板里能看到已注册的钩子才算真的挂上。

### `xelatex: command not found`

系统上没有 TeX Live。安装 MacTeX（macOS）或 TeX Live（Linux/Windows）。在装好之前，`/compile-latex` 与 `/extract-tikz` 不可用；`/deploy`（Quarto）仍可用。

### `quarto: command not found`

从 [quarto.org/docs/get-started](https://quarto.org/docs/get-started/) 安装 Quarto。在装好之前，`/deploy` 与 `/qa-quarto` 不可用；Beamer 相关工作流仍然可用。

### `pdf2svg: command not found`

`/extract-tikz` 需要它。`brew install pdf2svg`（macOS）/ `apt install pdf2svg`（Debian/Ubuntu）/ `dnf install pdf2svg`（Fedora）。

### `/stata-replication` 停在「stata-mcp not registered」

Stata 流水线技能需要 [`stata-mcp`](https://github.com/SepineTam/stata-mcp) MCP 服务器。每个用户装一次：

```bash
claude mcp add stata-mcp --scope user -- uvx stata-mcp
```

`uvx` 是 `uv` 的包运行器（没装就 `brew install uv`）。该 MCP 服务器需要本地装有 Stata——它是桥，不是替代品。装好后重启 WorkBuddy 会话，让 MCP 服务器注册上。

用 `claude mcp list` 核验——`stata-mcp` 应以 `connected` 状态出现。若 Stata 本身不在 `PATH` 上，该技能同样会停；[`/stata-replication`](.codebuddy/skills/stata-replication/SKILL.md) Phase 0 里记录的安装说明覆盖了这两项起飞前检查。

### Claude 为每个工具反复询问权限

在手动模式下，多数未被允许清单覆盖的编辑与 shell 命令，Claude 都会先问。从监管最多到最少，选项中（见指南的[权限模式一节](https://psantanna.com/claude-code-my-workflow/workflow-guide.html#settings---permissions-and-hooks)）：

- **自动模式**——新的会话默认就以它启动：分类器批准常规操作，拦住或询问有风险的操作。
- **接受编辑**——`Shift+Tab`，或 `claude --permission-mode acceptEdits`：自动批准文件编辑与工作目录内的常见文件系统命令。
- **Bypass**——`claude --permission-mode bypassPermissions` 跳过权限询问与安全检查（拒绝规则仍然生效）。Anthropic 把它限定在隔离容器与虚拟机内，它从 CLI 参数、`--settings` 或用户/托管设置生效——写在项目 `.codebuddy/settings.json` 里的 `bypassPermissions` 不被承认，会话以手动模式启动。（在 VS Code 里，bypass 是用户设置层面的选择：在你的 VS Code *用户*设置里把 `claudeCode.initialPermissionMode` 设为 `bypassPermissions`，并打开 `claudeCode.allowDangerouslySkipPermissions`。两者都是机器作用域的，所以扩展忽略工作区里的值，本模板的 `.vscode/settings.json` 不会改变起始模式。）

本模板的 `.codebuddy/settings.json` 附带宽泛的放行规则（`Edit(**)`、`Write(**)`、`Bash(*)`、……），且不设默认模式，所以在手动模式下多数常规工作都不询问就能跑。自动模式会撤掉一刀切的 `Bash(*)` 规则，改为把 shell 命令送进它的分类器。要在任何模式下都把受限数据挡在模型之外，就加上拒绝规则——见下方[「让受限数据不进入模型」](#keep-restricted-data-off-the-model)。

## 模型与 API

### `/model` 里的档位没生效，或钉死的模型 ID 失败

本平台只有**三个档位**——`default` / `lite` / `reasoning`——没有按型号点版本的阵容，也没有 effort 轴。各档职责、上游层级怎么映射过来，都在 [`model-versions.md`](.codebuddy/references/model-versions.md) 里。配置出错常见两种形态：

- **档位没落到配置上。** 代理或技能的 frontmatter 里还写着上游的层级名（`opus` / `sonnet` / `haiku` / `inherit`）：它们不会报错，但也不会起作用，留着等于给自己一个假开关。跑 `python scripts/normalize-model-tiers.py --dry-run`，它应当报 0 个文件需要改；有输出就照着它的清单改成三档之一。
- **钉死的模型 ID 失败。** 把 `model:` 钉成具体型号既不会让结果更可复现，也会在某次更新后静默失效——型号名、最低 CLI 版本与退役日期都属于上游，本平台没有对应物。先找出这些钉法：
  - **设置：** `.codebuddy/settings.json`、`.codebuddy/settings.local.json` 或 `~/.workbuddy/settings.json` 里的 `model` 键。
  - **代理与技能：** `grep -rn "^model:" .codebuddy/agents/ .codebuddy/skills/`——本模板里只该出现 `default` / `lite` / `reasoning` 三个值，别的都算漂移。
  - **CI：** 任何在流水线里显式传 `--model <id>` 的工作流。

要为某条可复现性断言冻结快照，就在报告里写下当时的档位、日期与结果——不要靠钉死型号 ID 来「锁」它。

### 一次更新在截止日中途把东西搞坏了

客户端默认从 `latest` 通道自我更新。截止周请在 `~/.workbuddy/settings.json` 里改跟更慢的通道：

```json
{ "autoUpdatesChannel": "stable" }
```

`minimumVersion` 能阻止自动更新安装低于你已知可用版本的任何东西。优先用这两项，而不是把更新器关掉——更新带着安全修复与新模型支持（新模型可能要求最低版本）。

### 订阅套餐上无头的 `claude -p` 运行从单独额度池计费

自 **2026-06-15** 起，订阅套餐上的无头子进程调用（`claude -p`、Agent SDK）从一个**单独的 Agent SDK 额度池**扣除，与交互式额度解耦。在本模板里，这影响 `scripts/run-skill-eval.sh` 以及你添加的任何定时或脚本化的 `claude -p`（例如一个 `/triage-inbox` 例行任务）。若某次无头运行因额度耗尽报错、而你的交互式会话正常，请单独检查 Agent SDK 余额。各套餐层级的当前配额以你账号里的订阅页为准——本仓库不代管上游产品的额度说明。

## 编译 / 渲染

### Beamer 里的 `Undefined citation`

`.bib` 的键不在 `Bibliography_base.bib` 里。跑 `/validate-bib` 把引用与 bib 文件交叉核对。`/compile-latex` 里的 3 遍 XeLaTeX + bibtex 序列能解析存在的键；它没法凭空造出键。

### `Overfull \hbox` 警告

文字超出了幻灯片的可打印宽度。要么把出问题的内容写短，要么把它包进 `text width=...` 的节点（TikZ 的情形），要么改用 `\resizebox`。`/visual-audit` 会标出这些；`/proofread` 也会。

### Quarto 渲染失败并报 `No valid input files`

你大概是在错的当前工作目录下调用了 `quarto render`。请在仓库根目录跑。`/deploy` 会自动处理这一点。

### HelloWorld.tex 编译不过

先跑 `./scripts/validate-setup.sh`。若 XeLaTeX 已装，就重新 fork 一份干净的副本——你可能无意中改过这份示例讲义。HelloWorld 是刻意极简的，在全新克隆上应当永远能编译。

### `/extract-tikz` 停在预防检查上

好事——预检抓到了一处 P3（裸 `scale=`）或 P4（边标签上缺方位关键词）违规。修掉 Beamer 源码里那一行再重跑。见 `.codebuddy/rules/tikz-prevention.md`。

### 幻灯片 QA「跑不起来」（退出码 2）

`scripts/slide-qa.py` 在无头 Chrome 里度量一套渲染好的 Quarto 幻灯片，退出码 2 意味着它什么都没度量到——此时技能退回到读源码。报错信息会点出原因：

- **缺 Playwright。** Homebrew 或系统 Python 会拒绝普通的 `pip install`，所以在虚拟环境里装一次，并让技能指向它：`python3 -m venv ~/.venvs/slide-qa && ~/.venvs/slide-qa/bin/pip install playwright`，然后 `export SLIDE_QA_PYTHON=~/.venvs/slide-qa/bin/python`（把这条 export 加进你的 shell 配置）。`./scripts/validate-setup.sh` 会检查它。
- **没有浏览器。** 它用的是你已安装的 Google Chrome；没有的话，跑 `$SLIDE_QA_PYTHON -m playwright install chromium`。
- **渲染过期。** `.qmd` 比它的 `.html` 新——先重新渲染，否则数字描述的是旧讲义。
- **报告里出现「Math was not typeset」**（不是退出码 2）：MathJax 或 KaTeX 没加载，通常是离线，于是公式被当成裸 TeX 来度量。

## Git / 钩子 / CI

### 钩子脚本 permission denied

`chmod +x .codebuddy/hooks/*.py .codebuddy/hooks/*.sh`。`./scripts/validate-setup.sh` 也会报告不可执行的钩子。

### 压缩前的钩子没把计划存下来

PreCompact 钩子（`.codebuddy/hooks/pre-compact.py`）把状态写到 `~/.workbuddy/sessions/<hash>/`。若压缩之后状态不在那儿：

- 检查钩子的退出码：`echo '{}' | python3 .codebuddy/hooks/pre-compact.py` 应当以 0 退出。
- 检查 `~/.workbuddy/sessions/` 的权限。
- 检查会话哈希是否对得上——压缩会记录该哈希。

### 会话启动时冒出一份交接

`session-handoff.py` 会把最近 7 天内写下的最新 `/checkpoint` 或 `/compress-session` 文件交给新会话，并标注为「待核验的笔记」。一旦你在该会话里敲了一条提示词，它就记为已用过，所以只会出现一次。想跳过它，设 `CLAUDE_HANDOFF=off`（shell 里，或 settings 的 `env` 下）；想改窗口，用 `CLAUDE_HANDOFF_MAX_AGE_DAYS`。无头的 `claude -p` 运行永远收不到它。如果另一个记忆工具也在启动时注入上下文，就关掉其中一个。

### `/commit` 因 `quality_score.py` 低于阈值而失败

脚本在改动的文件里检出了问题。要么修掉（推荐），要么重跑 `/commit` 并明确告诉 Claude **「commit anyway」** 或 **「skip quality gate」** 并给出理由——这次覆盖会记进提交信息里。（没有 `--skip-quality-gate` 这个 CLI 参数；覆盖是对技能发出的一句自然语言信号。）

## 调色板 / 主题

### Beamer 与 Quarto 的渲染配色不一致

调色板契约断了。跑 `./scripts/check-palette-sync.sh`——它会报告哪些颜色名在某一面缺失。把 `Preambles/header.tex` **与** `Quarto/theme-template.scss` 两处的 HEX 值改成一致。完整契约见 `Preambles/README.md`。

## R / 数据分析

### `here::here()` 解析到了错误的目录

`here` 需要一个项目根标记（`.here`、`.git`、`DESCRIPTION` 或 `.Rproj`）。若你看到错误路径，就在仓库根目录建一个空的 `.here` 文件。

### 分析改动之后 `sessionInfo.txt` 没更新

你直接跑了 `03_analyze.R`，而不是 `00_run_all.R`。重跑 `00_run_all.R`（例如经 `/data-analysis` 技能或你惯用的流水线运行器）——那个入口会在最后一步写出会话快照。

## 权限 / bypass / 状态栏（v1.6.0 / v1.8.0）

### 「明明设了 `bypassPermissions` 还是弹询问」

三个原因，按常见程度排序：

1. **这项设置在项目设置里。** 写在 `.codebuddy/settings.json` 或 `.codebuddy/settings.local.json` 里的 `defaultMode: "bypassPermissions"` 不被承认，会话以手动模式启动（那里的 `"auto"` 同样会退回内置默认值）。把它从项目文件里删掉，然后在 `~/.workbuddy/settings.json` 里设 bypass、或传 `--permission-mode bypassPermissions`、或（VS Code）在你的 VS Code **用户**设置里设 `claudeCode.initialPermissionMode`，同时打开扩展的 *Allow dangerously skip permissions* 开关（`claudeCode.allowDangerouslySkipPermissions`）——两者都是机器作用域的，所以工作区 `.vscode/settings.json` 里的值被忽略。VS Code 扩展在起始模式上根本不读项目设置。
2. **会话中途的切换。** `Shift+Tab`（CLI）或模式指示器（VS Code）会覆盖文件设置，直到会话结束。
3. **过期的会话。** 设置在会话启动之后才改；开一个新会话。

跑 `/permission-check`——它会读**钩子链**（`.codebuddy/settings.json` 的 `hooks` 段）、
本地覆盖（`settings.local.json`、`.vscode/settings.json`）与三个守卫脚本，告诉你这个动作是被
哪条守卫拦下的、还是被平台自己问的；并明确指出哪些照上游文档写进去的开关（`permissions.*`、
`claudeCode.initialPermissionMode`）在本平台**根本不生效**——这类配置不会报错，只会静默地什么都不做。

### Keep restricted data off the model

Claude 读的每个文件都会被送到模型供应商那里。[`confidential-data.md`](.codebuddy/rules/confidential-data.md) 规定受限微观数据永不离开本机，而**拒绝规则在每一种权限模式下都生效，包括 bypass**。若你的项目有受限目录，就加拒绝规则——加在 `.codebuddy/settings.json` 里保护每一位合作者，或加在 `.codebuddy/settings.local.json` 里只保护你这台机器——并写清你的数据使用协议覆盖的路径：

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

`**/` 能匹配任意深度，但只在项目之内：相对模式够不到存放在别处的数据。对检出目录之外的数据，用 `//`（绝对）或 `~/`（家目录）给模式定锚——`Read(//Volumes/secure-dua/**)`、`Read(~/Dropbox/ProjectX-DUA/**)`——并把这类机器相关的行放进 `.codebuddy/settings.local.json` 或 `~/.workbuddy/settings.json`，绝不要放进已提交的 `settings.json`。单个前导 `/` 不是绝对路径：在 `.codebuddy/settings.json` 或 `.codebuddy/settings.local.json` 里它锚定在会话的工作目录（你从项目根启动时就是项目根），在 `~/.workbuddy/settings.json` 里它锚定在 `~/.workbuddy/`——所以要用 `//` 才是真正绝对的路径。从 `confidential-data.md` 加载的那些模式出发（`data/**`、`**/raw/**`、`**/*.dta`、`**/*.sav`、`**/restricted/**`、`**/confidential/**`），保留你的数据使用协议覆盖的那些——把 `data/**` 整个拒掉，也会挡住你可能想让 Claude 读的公开数据。Read/Edit 拒绝规则覆盖 Claude 的文件工具、WorkBuddy 在 Bash 里认得的那几个文件命令（`cat`、`head`、`tail`、`sed`、`tee`）以及重定向目标，但不覆盖一个不点名就读文件的命令（`grep -r pattern .`），也不覆盖自己打开文件的脚本——所以它们是一道防线，不是一份证明：要把它们与本规则的纪律搭配（Claude 写的是*作用于*数据的代码，它不读数据），并在任何基于这些数据的产物离开本机之前配上 `/disclosure-check`。

### `/permission-check` 读 `~/.workbuddy/` 之前会先问

这是刻意的。宿主全局配置里可能含无关的路径与密钥。Phase A（仓库本地）是自动的；Phase B（宿主全局，带密钥脱敏）需要明确确认。背景见 [CHANGELOG v1.6.0——隐私边界](CHANGELOG.md)。

### 权限询问太多了？

**本平台没有「允许清单」这个旋钮。** 上游那套 `permissions.allow` / `defaultMode` 的分层配置在这里不生效
（写进去不报错，也什么都不做），所以上游的 `/fewer-permission-prompts` 那种「扫描转录、生成允许清单」的补救办法
**在这里不存在**——不要照它的说明去改配置，那只会得到一份假开关。

本平台能真正减少询问的只有三条：

1. **让钩子放行明确的只读操作。** 询问多半来自「这条命令要不要动文件」这件事本身；把反复出现的只读命令
   写进钩子的判定里，比加一条允许规则更可靠（因为钩子真的会被执行）。
2. **把一个反复出现的操作变成一个技能。** 一条 `/foo` 比每次手打五条命令少五次判断。
3. **收窄一次动作的范围。** 一次 `Edit` 比一次批量脚本少一次询问；批量改动经脚本走，反而更容易被守卫拦。

先跑 `/permission-check` 弄清是「守卫拦的」还是「平台问的」——两者的补救方式完全不同，混在一起改只会越改越乱。

### 状态栏显示 `?` 或是空的

会话 JSON 解析失败。检查 `.codebuddy/scripts/statusline.sh` 可执行（`chmod +x`），且 `python3` 在 `PATH` 上。退路输出是 `? @ <branch>`（没有模式徽标，模型显示 `?`）——若你看到的是这个，说明脚本解析不了会话 JSON。重启 WorkBuddy。

### 状态栏显示 `gate:off`

仓库自带一个 pre-commit 门禁（`.githooks/pre-commit`），但 git 没指向它，所以一次普通的 `git commit` 会跳过所有检查——只有 `/commit` 会跑它们。每个克隆跑一次 `./scripts/install-hooks.sh`（它把 `core.hooksPath` 设为 `.githooks`），徽标就消失了。

### 改 `.codebuddy/`、`.git/`、`.vscode/` 会弹询问（或被送进分类器）

这**不是 bug**。写入*受保护路径*——`.git`、`.vscode`、`.idea`、`.husky`、`.devcontainer`、`.codebuddy`（`.codebuddy/worktrees` 除外）、shell 的 rc 文件、`.mcp.json` 以及另外几个——永远不会被放行规则自动批准。会发生什么取决于模式：手动与接受编辑下**弹询问**，自动模式下**送进分类器**，dontAsk 下**被拒**，只有 bypass 下才**放行**（以及开着 bypass 的终端计划模式会话）。当询问针对项目的 `.codebuddy/` 目录弹出时，它会给一个会话作用域的选项：「允许编辑本项目 `.codebuddy` 目录里的文件」。

要在 `.codebuddy/rules/`、`.codebuddy/references/`、`.codebuddy/skills/` 或 `.codebuddy/agents/` 下做批量编辑，经 Bash 工具跑一次脚本化的编辑，可以免掉每个文件一次询问。本模板自带的 `root-of-trust-guard.py` 钩子**拒绝**写入 `.codebuddy/settings*.json`、`.codebuddy/hooks/` 与 `.githooks/` 的 shell 写操作——在那几处用 Edit/Write，这样每一次对门禁的改动都留下可审读的 diff。

### VS Code：bypass 模式无法从 `.vscode/settings.json` 生效

VS Code 扩展读的是 **`claudeCode.allowDangerouslySkipPermissions`**，带 `claudeCode.` 前缀；裸的 `allowDangerouslySkipPermissions` 键永远不会被读到。这一项把「Bypass permissions」加进模式选择器，而它关着的时候扩展会把 `bypassPermissions` 的启动降级为手动模式，于是写入受保护路径仍然弹询问。它和 `claudeCode.initialPermissionMode` 都是机器作用域的：VS Code 只从你的**用户**设置里读它们，忽略工作区 `.vscode/settings.json` 里的值。想让新对话以 bypass 启动，打开用户设置（`Cmd+,` → Extensions → 本平台的扩展），把 `"claudeCode.allowDangerouslySkipPermissions": true` 与 `"claudeCode.initialPermissionMode": "bypassPermissions"` 设上，然后重载窗口。只在没有联网的沙箱里用 bypass。

## 同行评审流水线（v1.5.0）

### `/review-paper --peer AER` 报「journal not found」

目标期刊必须在 [`.codebuddy/references/journal-profiles.md`](.codebuddy/references/journal-profiles.md) 里。自带 8 份画像：AER / QJE / JPE / ECMA / ReStud（经济学）与 APSR / AJPS / JOP（政治学）。要加你领域的期刊，把 [`templates/journal-profile-template.md`](templates/journal-profile-template.md) 复制进 `journal-profiles.md`，填好 7 个 schema 小节（关注点、门槛、领域调整、方法调整、典型关切、审稿人池权重、可选表格格式）。

### 审稿人交回的报告几乎一模一样

它们没有被分派审稿取向。编辑代理应当从六路分类（STRUCTURAL / CREDIBILITY / MEASUREMENT / POLICY / THEORY / SKEPTIC）里选出**两种不同**的取向。若报告是克隆体，说明编辑把选择塌缩了——通常是因为论文足够窄，只有一个分类适用。试 `--peer <journal> --stress`，强制配对对抗式取向。

### R&R 跟进丢掉了上一轮的上下文

用 `--peer <journal> --r2` / `--r3` 续接一次既有审读。编辑会跳过新的初审，重新载入上一轮的报告（`quality_reports/peer_review_<paper>/desk_review.md`、`referee_domain.md`、`referee_methods.md`），并沿用同一批审稿取向与忌讳；随后每位审稿人把上一轮的每条主要关切标为 Resolved / Partial / Not addressed。若那些上一轮报告缺失或被改名，链条就断了——用 `--peer` 从头开始。

## 表面同步门禁（v1.6.0）

### `/commit` 在 Step 0b 失败并报「DRIFT DETECTED」

Step 0b 会跑 `./scripts/backtest.sh`。它的表面同步门禁（`scripts/check-surface-sync.py`）发现文档里声称的某个计数，或某张 `<!-- surface-sync-table -->` 表格的行数，与磁盘上的实际情况（技能 / 代理 / 规则 / 钩子）不符。它会把每个过期的表面列成 `file:line  asserts N <kind> (actual: M)`。逐条修掉它标出的表面，再重跑 `./scripts/backtest.sh`（或只跑 `python3 scripts/check-surface-sync.py`）。若是别的门禁红了，去读那个门禁自己的输出。**不要绕过**——这道门禁之所以存在，是因为手工 `replace_all` 已经三次漏掉同族的其他说法（v1.5.x 里的 PR #70/#76/#78）。

### 加一个新技能 / 代理 / 规则就把门禁弄红了

意料之中。门禁会把磁盘上 `.codebuddy/skills/` 的数量与散文里的断言相比，并要求 README.md 里每张 `<!-- surface-sync-table: ... -->` 表格对磁盘上的每一项恰好只有一行。加完一个技能后，把它的行加进 README.md 的技能表（若是代理，就加进代理表），然后更新 README.md、CODEBUDDY.md（若提到）、`guide/workflow-guide.qmd` 与两份渲染副本（`guide/workflow-guide.html`、`docs/workflow-guide.html`）、`docs/index.html`（og:description 与「What you get」一节）、`templates/skill-template.md` 以及 `.codebuddy/skills/commit/SKILL.md` 里的计数。脚本会告诉你哪些过期了；重跑直到它以 0 退出。

## 起飞前报告（v1.6.0）

### 技能停在「Pre-Flight Report failed — inputs not readable」

该技能读不到它需要的某个输入（数据集、期刊画像、记号登记表、`r-code-conventions.md` 等）。检查报错里给出的文件路径、确认权限，并确认全新 fork 出来时有该有的文件（例如 `/create-lecture` 对记号登记表有全新 fork 的退路；其他技能没有）。**不要**为了跳过起飞前检查去改技能——这件事的意义，就是在真正开工之前抓住编造的变量名与缺失的约定。

### 起飞前检查通过了，代理还是在编

开一个 issue，把起飞前报告附上。要么是输入 schema 不全，要么是代理无视了报告。两者都是值得提的 bug。

## 决策记录（v1.6.0）

### ADR 该存哪儿？

`quality_reports/decisions/YYYY-MM-DD_short-description.md`，用 [`templates/decision-record.md`](templates/decision-record.md)。该目录和 `plans/`、`specs/` 一样被 gitignore——只有当你希望这份记录被别人看见时才提交。（多数 forker 把决策留在本地。）

## 降落后核验 / 链式核验（v1.7.0）

### `/verify-claims` 超时或报错

被 fork 出来的 `claim-verifier` 代理按设计是保守的：没有证据它就不会把一条断言标为已核验。若它中途超时或报错，技能会浮出一个警告块，而不是静默把草稿发出去（失败关闭，和起飞前检查一样）。草稿以**暂定**状态返回——就当它未核验。下一步：

- **重试**时把来源范围收窄。`/verify-claims --source <specific-paper.pdf>` 比让代理去猜更快也更可靠。
- **从 WebSearch 换成直接抓取。** 若代理卡在网上检索上，就把 PDF 下到 `master_supporting_docs/`，再用 `--source` 传进去。
- **降级为只警告**，用 `--no-fail-closed`，前提是你自己正在读那份来源，只想要一份报告。

### 核验者对你确信正确的断言说「cannot-verify」

这是核验者在诚实，不是固执。它意味着：

- 源材料取不到（付费墙、坏掉的 URL、受限数据集的 codebook 未公开）。
- 这条断言的措辞映射不到一个具体的可核验问题（例如「这是个有前途的方向」是观点，不是事实性断言）。
- 证据存在，但在代理够不到的场合（会议论文集在登录墙后、工作论文不在 arXiv 上）。

解决：给一个规范的来源（DOI / arXiv / 仓库路径），或者在最终输出里接受 `cannot-verify` 标记、自己人工确认。

### 集成技能（例如 `/lit-review`）卡在降落后检查这一步

若调用方技能在启动 `claim-verifier` 之后不返回，检查：

1. `Agent` 工具（旧别名 `Task`）对调用方技能可用（在 `SKILL.md` 里看它的 `allowed-tools`）。
2. 代理在 `.codebuddy/agents/<name>.md` 里的 `tools:` frontmatter 包含它需要的东西（`WebFetch`、`WebSearch`、`Read`）。
3. 网络可达：WebSearch + WebFetch 需要联网；在离线的 fork 上必须禁用它们，或把核验者放在某个检查之后。

若确实卡住，本次运行可以用 `--no-verify` 绕过。若卡顿持续，提一个 issue。

### 退出降落后核验

除 `/review-paper` 之外，每个受影响的技能都接受 `--no-verify` 来跳过降落后这一步。`/review-paper` 没有 `--no-verify`：传 `--no-novelty-check` 关掉 `--peer` 的新颖性探针，这同时会去掉它的降落后步骤（只要探针跑，降落后检查就是强制的）。适用于：

- 你在快速迭代，并且自己核验。
- 你已经人工核查过来源。
- CoVe 额外约 2× 的 token 成本挡住了紧张的预算。

以下情形**不要**退出：

- 为外部读者产出交付物（给委员会看的文献综述、给编辑的 R&R 回复、项目申请书的文献勘察）。
- 草稿里有 >5 条你本人没核验过的引用。
- `/lit-review` 刚刚返回结果——那是整个模板里最常见的幻觉载体。

## `check-skill-integrity` 失败

表面同步门禁现在在计数同步检查之后串上 `check-skill-integrity.py`。它跑五项机械检查（frontmatter↔正文的工具、argument-hint↔正文的旗标、内部锚点解析、规则↔技能的关键词一致、以及 `RULE_KEYWORDS` 登记的完整性——每条作用于 `.codebuddy/skills/` 的规则都必须登记在册），并逐文件报告 P0/P1/P2 发现。

### P0：正文调用了工具 X，但 frontmatter 的 allowed-tools 是 [...]

技能的 Steps/Workflow 一节说要使用某个工具（通常是 `Agent`，或它的旧别名 `Task`，用来派生子代理；或 `Edit`/`Write`/`MultiEdit`/`NotebookEdit`），但 frontmatter 的 `allowed-tools` 数组没列它。运行时表现：技能会撞上工具权限错误，或静默跳过那一步。修法：把缺的工具加进 `allowed-tools`。

### P1：在 path/to/file.md 里找不到锚点 `#foo`

一条内部 markdown 链接 `[text](path#anchor)` 指向了不存在的标题。要么标题被改名了，要么锚点 slug 是手打的、与标题经 GitHub 风格 markdown 变换后的结果不符，要么链接的目标文件错了。修法：要么把锚点改成与某个既有标题匹配，要么补上缺的那个标题。

### P2：正文把 `--foo` 记为选项旗标，但 argument-hint 是 '...'

某个旗标在技能正文里有描述（表格里、列表里，或带退出说明的文字里），但没出现在单行的 `argument-hint` 里。用户无法从提示里发现这个旗标。修法：把该旗标追加到 `argument-hint`（或者，若它根本不是真的选项，就从正文里删掉）。

### P0：规则 foo.md 在 paths: 里列了这个技能，但技能正文里一条都不含 [...]

某条规则的 `paths:` 声称该技能遵守这条规则的协议，但技能正文没提该协议的关键词。要么把协议加进技能（推荐），要么从规则的 `paths:` 里去掉这个技能。关键词映射在 `scripts/check-skill-integrity.py` 的 `RULE_KEYWORDS` 下——新规则需要在那里加一条。

### 误报与正则调优

若某条发现看着不对（例如把一个 shell 命令的旗标当成技能旗标，或把一个示例链接当成真链接），那么 `scripts/check-skill-integrity.py` 里的正则需要调。共用的辅助函数：`strip_code()` 会把行内代码跨度与围栏代码块置空。对新的误报类别，在相关检查里加一条排除，并在行内写明。

## 可移植性回归集（门禁第 11 门）

`scripts/portability-tests.py` 跑 `tests/portability/` 下的用例：路径分隔符、代码页、
行尾、BOM、git 对非 ASCII 与含引号文件名的输出、大小写不敏感磁盘上的路径。它有三种
结果：PASS（每条用例都跑到了）、PARTIAL（跑完了，但有一部分用例因本机缺机制跳过）、
FAIL（有用例失败，或一条都没跑到）。

### 门 11 报 PARTIAL，上限写着「N of M cases not exercised on this host」

这是**通过**，但只钉住了跑到的那些用例。汇总里它单列，不并进 PASS。要判断要不要管，
读它上面打印的逐条原因：

- `需要 POSIX shell（bash 或 /bin/sh）` —— 本机没装 Git for Windows。装它即可，
  顺带修好钩子在 Windows 上不运行的问题（见上面那节）。
- `本机不允许 os.symlink` —— Windows 需要开发者模式或提权；开了就会跑。
- 其余原因大多写着「本类在 POSIX 宿主上用 ntpath 模拟 Windows」：真 Windows 上
  这些用例由 `NativeTest` 覆盖，模拟层在真 Windows 上会自我失真，跳过是设计。

**不要为了让上限变小，把用例改写成「跳过也算过」。** 一条没跑到却记为通过的用例，
比一条明明跳过的用例糟得多——它把上限变成了谎言。修复方向永远是把机制装上，或者
在真机上跑一遍。

### `portability-tests: CANNOT RUN — every one of N cases was skipped`

退出码 2。这句的意思是**一条用例都没跑到**，所以这次运行什么都没证明。它和
「空扫描报绿」是同一个缺陷家族，因此不允许按 PASS 处理。先查上面逐条跳过原因；
若全部是「缺机制」，说明这台机器缺的不止一样。

### 加了一条新用例，它在旧代码上也是绿的

那它就不是 PIN（钉住缺陷的用例），只是一条 CONTROL。两者都要有：PIN 证明检查会红，
CONTROL 证明它不是「拒绝一切」。但如果一条用例你以为是 PIN、实际在旧代码上就绿，
它钉的不是你以为的那件事——把它改成真的会红，或者如实标成 CONTROL。

## 调度自主工作

### 会话一关 `CronCreate` 就死

按设计如此。`CronCreate` 在本平台 REPL 自己的事件循环里调度——REPL 一退出（你关了窗口、客户端崩了、你的用量撞上限额导致会话终止），这个 cron 也随之而去。即便 `durable: true` 也救不了你，只要触发时没有 REPL 在跑。

对**活动会话内的短延时轮询**（例如「我干活的时候每 5 分钟查一次构建」），`CronCreate` 没问题。对任何必须**挺过会话终止**的东西，改用**云端 Routines**（2026 年 4 月）。Routines 跑在平台的网页基础设施上——每次触发时不需要你的电脑在线。用 Routines 来做：定时审计、过夜批处理、你不在时的自主执行。完整对比见 `.codebuddy/references/audit-pet-peeves.md` 第 17 条。

### 我批准了计划，PreCompact 还是不停阻断

你环境里大概设了 `CLAUDE_PRECOMPACT_BLOCK_ON_DRAFT=1`。这个钩子对每一份 DRAFT 计划最多阻断**一次**——同一份计划的后续压缩正常进行。若它反复阻断，要么是计划的 status 行没从 DRAFT 更新为 APPROVED/IN_PROGRESS（看计划文件的头部），要么是你每次拿到的都是一份不同的 DRAFT 计划（钩子按计划路径跟踪）。想彻底关掉这道防线，就取消该环境变量：`unset CLAUDE_PRECOMPACT_BLOCK_ON_DRAFT`。

## 还是卡住？

- 读[指南的故障排查一节](https://psantanna.com/claude-code-my-workflow/workflow-guide.html#troubleshooting)，有更长的恢复场景。
- 到 <https://github.com/pedrohcgs/claude-code-my-workflow/issues> 开个 issue——缺陷报告模板会问我们要的那些环境细节。
