---
name: stata-replication
description: 端到端 Stata 复现流水线——在 `scripts/stata/` 下搭出带编号的 `.do` 文件，通过 `stata-mcp` MCP 服务器执行，把日志与输出捕获到 `output/`，并产出可直接发表的表格（esttab）与图形（graph export）。它是 `/data-analysis` 在 R 优先项目里的镜像。当用户说 "stata replication"、"set up Stata pipeline"、"scaffold the .do files"、"run Stata analysis"、"AEA replication package in Stata"，或当项目的分析语言是 Stata 而非 R 时使用。
description_zh: 端到端 Stata 复现流水线——在 `scripts/stata/` 下搭出带编号的 `.do` 文件，通过 `stata-mcp` MCP 服务器执行，把日志与输出捕获到 `output/`，并产出可直接发表的表格（esttab）与图形（graph export）。它是 `/data-analysis` 在 R 优先项目里的镜像。当用户说 "stata replication"、"set up Stata pipeline"、"scaffold the .do files"、"run Stata analysis"、"AEA replication package in Stata"，或当项目的分析语言是 Stata 而非 R 时使用。
argument-hint: "[paper-or-data-pointer] [--from-r] [--no-execute]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent", "Task"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/stata-replication` —— Stata 流水线脚手架 + 执行

在 `scripts/stata/` 里搭一条完整的 Stata 复现流水线：按 [`.codebuddy/rules/stata-code-conventions.md`](../../rules/stata-code-conventions.md) 写出的带编号 `.do` 文件，经 [`stata-mcp`](https://github.com/SepineTam/stata-mcp) MCP 服务器执行，输出落到 `output/`。

## 何时使用

- 你的项目分析语言是 **Stata**（不是 R）。这在经济学田野实验、RCT 研究、以及任何原始复现包就是 Stata 的 AEA 投稿中很常见。
- 你要把一个 R 优先的项目转成 Stata，以投 AEA。
- 你要给一篇 R 优先的论文加一项 Stata 稳健性检验。
- 你想要一条命令就能全跑：`do scripts/stata/99_run_all.do`。

## 何时不要使用

- 你的项目是 R 优先的。用 [`/data-analysis`](../data-analysis/SKILL.md)。
- 你的项目是 Python 优先的。本技能和 `/data-analysis` 都不合适；考虑扩展那份约定规则以支持 Python，或把这两个技能之一移植过去。
- 你在做快速的探索性工作。带编号的流水线脚手架是给复现包用的，不是给草稿笔记本用的。

## 前置条件：已安装 `stata-mcp`

本技能需要 `stata-mcp` MCP 服务器。每个用户装一次：

```bash
claude mcp add stata-mcp --scope user -- uvx stata-mcp
```

该 MCP 服务器提供带命令守卫的 Stata 执行（拒绝 `!/shell/erase` 这类破坏性操作）、内存监控，以及与 Stata Language Server 的配对。由 SepineTam 维护。

若 `stata-mcp` 未安装，技能会在 Phase 0 停下并给出安装说明。

## 工作流

### Phase 0：起飞前检查

1. 确认 `stata-mcp` 已注册在用户的 MCP 配置中。若没有 → 停下并给出安装说明。
2. 确认本机已安装 Stata（缺了它 MCP 服务器跑不起来）。输出 Stata 版本以确认。
3. 确认 `scripts/stata/` 目录存在或可以创建。
4. 读 [`.codebuddy/rules/stata-code-conventions.md`](../../rules/stata-code-conventions.md)——每一份产出的 `.do` 文件都遵守这份约定。
5. 若设了 `--from-r` 参数，定位 `scripts/R/` 下既有的 R 流水线，把它当作转译源。把 `replication-protocol.md` 里那张 Stata → R 陷阱表反向套用。

### Phase 1：搭建流水线

在 `scripts/stata/` 下产出（或更新）这些文件，每一份都符合 `stata-code-conventions.md` 的头部约定：

```
scripts/stata/
├── 00_install.do        # ssc install, set globals, paths, sessionInfo capture
├── 01_clean.do          # raw → cleaned panel
├── 02_descriptive.do    # summary tables, balance (iebaltab), attrition
├── 03_analyze.do        # main regression specs (reghdfe / ivreg2 as needed)
├── 04_robustness.do     # alt specs, sensitivity
├── 05_tables_figures.do # esttab .tex outputs + graph export PDFs
└── 99_run_all.do        # do "01_clean.do" / do "02_..." / ...
```

若论文或数据源暗示了特定设定（例如用 `reghdfe` 做 DiD、用 `ivreg2` 做 IV、用 `rdrobust` 做 RD），就据此定制 `03_analyze.do`。

### Phase 2：执行（除非指定 `--no-execute`）

按编号顺序，对每个脚本：

1. 派发给 `stata-mcp` 执行该 `.do` 文件。
2. 捕获日志（按头部约定，Stata 写到 `output/NN_log.smcl`）以及产出的 `.dta` / `.tex` / `.pdf` 输出。
3. 若某脚本失败，先把它的设定追加进台账（第 4 步），Status 记为 `failed`、Why 里写错误，然后停下——**不要**自动修复，除非该失败是琐碎的（Stata 在解析阶段就报出的拼写错误）。对实质性失败（观测不足、矩阵奇异、协变量缺失），呈现给用户。
4. 把每个估计型 `.do` 文件跑过的每一项设定——保留的、丢弃的、失败的——都追加到 `quality_reports/spec-ledger.md`，列、提交戳与只追加区块都与 [`/data-analysis`](../data-analysis/SKILL.md) Phase 3（「设定台账」）相同。失败的一次运行也是一行，Status 记 `failed`、Why 里写错误。

对长时间运行的脚本（> 2 分钟），用 **Monitor 工具**流式读取 stdout——与 `/data-analysis` 和 `/audit-reproducibility` 中记录的同一套做法。

### Phase 3：核验

1. 确认每个预期输出都存在于 `output/`。
2. 检查 `output/sessionInfo_stata.txt` 已被捕获（包版本）。
3. 若有稿件，跑 `/audit-reproducibility`——它通过 `haven`/`pyreadstat` 读取 Stata 的 `.dta` 输出。
4. 报告跑了哪些脚本、产出了哪些输出、Stata 给出的任何警告。

### Phase 4（可选）：R 交叉核对

若设了 `--from-r`，跑同一套分析的 R 版本（假定位于 `scripts/R/`）并比较：

- 点估计：应吻合到约 0.01（按 `replication-protocol.md` 的容差）。
- 标准误：应吻合到约 0.05（聚类自由度调整在 Stata 与 R 之间可能略有差异）。
- 样本量：必须完全一致。

不一致会呈现给用户去查——常见元凶：聚类自由度、默认选项（PS 用 logit 还是 probit）、bootstrap 种子的处理。

## 配套技能

- [`/data-analysis`](../data-analysis/SKILL.md) —— R 版对应物。同样的流水线形态，不同的语言。
- [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) —— 既读 `.rds` 也读 `.dta` 输出。把稿件里的断言与实际产出的数值交叉核对。
- [`/review-paper`](../review-paper/SKILL.md) —— 若论文存在且引用了本流水线产出的表图，`/review-paper` 会自动调用 `/audit-reproducibility`（按 `cross-artifact-review.md`）。

## 反模式

- **手工编辑 `.dta` 文件。** 永远不要。所有变换都通过 `.do` 文件发生；`.dta` 输出是派生的、可复现的。
- **跳过 `99_run_all.do`。** 这是 AEA 要求的单命令入口。项目再小也要建。
- **默认用 `, robust`。** 在合适的层级上用 `, cluster(id)`——见 `stata-code-conventions.md` §6。
- **在 LaTeX 里手工排表格。** 用 `esttab` 与 `\input{}`——见 `stata-code-conventions.md` §4。
- **只在一个 .do 文件里钉 Stata 版本。** 按约定，每个 `.do` 文件都以 `version 18` 开头。

## 参数

| 参数 | 作用 |
|---|---|
| `--from-r` | 把 `scripts/R/` 下既有的 R 流水线当转译源，并在 Phase 4 跑 R 交叉核对。 |
| `--no-execute` | 只搭出并检查 `.do` 文件，不通过 `stata-mcp` 执行任何脚本（Phase 2 跳过）。 |

## 交叉引用

- [`.codebuddy/rules/stata-code-conventions.md`](../../rules/stata-code-conventions.md) —— 纪律契约。
- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 容差阈值（跨 R / Stata / Python 适用）。
- [stata-mcp on GitHub](https://github.com/SepineTam/stata-mcp) —— 本技能依赖的 MCP 服务器。
- [AEA Data Editor checklist](https://aeadataeditor.github.io/) —— 复现包标准。

## 长跑拟合 / 批量重跑：用 Monitor 工具（2026 年 4 月）

长时间的 Stata 拟合（带 `cluster bootstrap` 的数小时 bootstrap、数百万观测的大型 `reghdfe`、模拟研究）应当后台启动，并用 Monitor 工具跟踪——与 `/data-analysis` 和 `/audit-reproducibility` 在 R / Python 上的做法相同。`.do` 文件把日志写进 SMCL（`output/NN_log.smcl`）。Monitor 不会附着到后台作业或它的 stderr：只有你给它的那条命令的 stdout 才会变成事件。所以要把 Monitor 跑在一条跟踪日志、并过滤进度行与 Stata 错误的命令上，例如 `tail -f output/NN_log.smcl | grep --line-buffered -E '\{err\}|r\([0-9]+\);|<your progress marker>'`，这样 Claude 能在中途对错误作出反应（数小时的运行需要 `persistent: true`，作业结束后再 TaskStop）。
