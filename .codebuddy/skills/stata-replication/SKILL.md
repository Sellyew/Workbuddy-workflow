---
name: stata-replication
description: 搭建并执行端到端 Stata 复现流水线：在 `scripts/stata/` 创建带编号的 `.do` 文件，通过 Bash 后台调用本机 Stata 运行，把日志和输出保存到 `output/`，并用 esttab 和 graph export 生成可发表的表格与图形。它是 `/data-analysis` 在 R 优先项目中的对应技能。用户说 "stata replication"、"set up Stata pipeline"、"scaffold the .do files"、"run Stata analysis"、"AEA replication package in Stata"、"搭建 Stata 复现流程"、"运行 Stata 分析" 时，或项目使用 Stata 而非 R 进行分析时使用。
description_zh: 搭建并执行端到端 Stata 复现流水线：在 `scripts/stata/` 创建带编号的 `.do` 文件，通过 Bash 后台调用本机 Stata 运行，把日志和输出保存到 `output/`，并用 esttab 和 graph export 生成可发表的表格与图形。它是 `/data-analysis` 在 R 优先项目中的对应技能。用户说 "stata replication"、"set up Stata pipeline"、"scaffold the .do files"、"run Stata analysis"、"AEA replication package in Stata"、"搭建 Stata 复现流程"、"运行 Stata 分析" 时，或项目使用 Stata 而非 R 进行分析时使用。
argument-hint: "[paper-or-data-pointer] [--from-r] [--no-execute]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent", "TaskOutput"]
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# `/stata-replication` —— Stata 流水线脚手架 + 执行

在 `scripts/stata/` 搭建完整的 Stata 复现流水线。带编号的 `.do` 文件遵循 [`.codebuddy/rules/stata-code-conventions.md`](../../rules/stata-code-conventions.md)，通过 Bash 后台调用本机 Stata 批处理入口执行，输出保存到 `output/`。

## 何时使用

- 项目使用 **Stata** 而非 R 进行分析。经济学田野实验、RCT 研究，以及原始复现包就是 Stata 的 AEA 投稿，常属于这种情况。
- 需要把 R 优先项目转成 Stata，以投 AEA。
- 需要为 R 优先论文增加 Stata 稳健性检验。
- 希望用一条命令运行完整流程：`do scripts/stata/99_run_all.do`。

## 何时不要使用

- 项目是 R 优先时，使用 [`/data-analysis`](../data-analysis/SKILL.md)。
- 项目是 Python 优先时，本技能和 `/data-analysis` 都不合适。可以考虑扩展对应约定规则以支持 Python，或把其中一个技能移植到 Python。
- 快速探索性工作不需要带编号的流水线脚手架；它面向复现包，不是草稿笔记本。

## 前置条件：本机 Stata 批处理入口可用

本技能通过 Bash 调用本机 Stata，不依赖 MCP 服务器。Phase 0 必须确认可执行文件及其非交互批处理参数：POSIX 环境通常是 `stata -b do`，Windows 环境使用本机 Stata 可执行文件及其 `/e do` 参数。实际命令以本机安装为准，不要猜可执行文件名；批处理入口必须在脚本结束后退出，并把退出状态传回 Bash。

如果找不到 Stata 或批处理入口不能运行，技能会在 Phase 0 停下并报告缺失项。

## 工作流

### Phase 0：开始前检查

1. 确认本机 Stata 批处理命令可运行，并输出 Stata 版本；无法确认时停下。
2. 确认 `scripts/stata/` 与 `output/` 已存在或可以创建。
3. 阅读 [`.codebuddy/rules/stata-code-conventions.md`](../../rules/stata-code-conventions.md)，所有生成的 `.do` 文件都要遵守。
4. 如果指定 `--from-r`，找到 `scripts/R/` 下的现有 R 流水线作为转译源，并反向套用 `replication-protocol.md` 中的 Stata → R 陷阱表。

### Phase 1：搭建流水线

在 `scripts/stata/` 创建或更新以下文件，每份都符合 `stata-code-conventions.md` 的头部约定：

```
scripts/stata/
├── 00_install.do        # ssc install, set globals, paths, sessionInfo capture
├── 01_clean.do          # raw → cleaned panel
├── 02_descriptive.do    # summary tables, balance (iebaltab), attrition
├── 03_analyze.do        # 遵循论文设计与现行签核的主要估计设定
├── 04_robustness.do     # alt specs, sensitivity
├── 05_tables_figures.do # esttab .tex outputs + graph export PDFs
└── 99_run_all.do        # do "01_clean.do" / do "02_..." / ...
```

**[待 owner 签核] 本技能不预设 DiD、IV 或 RD 的估计量与扩展包，也不替研究者选择推断方式。** `03_analyze.do` 只能遵循论文自身设计、带日期的现行 owner 签核和项目已批准的包。任一项缺失时，在该脚本和运行摘要中留下 `[CLARIFY: 缺少论文设计、现行签核或已批准包]`，暂停相应估计步骤，不猜测或另行推荐。

### Phase 2：执行（除非指定 `--no-execute`）

按编号顺序处理每个脚本。每个脚本都走同一条后台主路径，不按预估耗时切换工具：

1. 为本次调用重新构造 `.do` 文件和控制台日志的绝对路径，用 **Bash** 启动本机 Stata 批处理命令，并设置 `run_in_background: true`。把 stdout 与 stderr 重定向到 `output/NN_console.log`；POSIX 示例命令如下，可执行文件名与参数仍以 Phase 0 的本机探测为准：

   ```bash
   stata -b do "<ABSOLUTE_DO_FILE>" > "<ABSOLUTE_REPO>/output/NN_console.log" 2>&1
   ```

   不要在命令末尾加 `&`，也不要用 `nohup` 脱离任务管理。收到后台任务的**完成通知**后，用 **TaskOutput** 读取该任务的结果，核对退出码与完整控制台日志；不要用 `sleep` 轮询。
2. 捕获生成的 `.dta` / `.tex` / `.pdf` 输出；按头部约定，Stata 自身日志写入 `output/NN_log.smcl`，Bash 重定向的控制台日志不能替代它。只有当前任务成功结束且当前日志、产物都存在时，才把该脚本记为成功。
3. 如果脚本失败，先把设定追加到台账（第 4 步），Status 记为 `failed`，Why 写入错误，然后停下。**不要**自动修复，除非失败只是 Stata 在解析阶段发现的拼写错误等琐碎问题。观测不足、矩阵奇异、协变量缺失等实质性失败要交给用户。
4. 把每个估计型 `.do` 文件运行过的所有设定，无论保留、丢弃还是失败，都追加到 `quality_reports/spec-ledger.md`。列、提交戳和只追加区块与 [`/data-analysis`](../data-analysis/SKILL.md) Phase 3 的「设定台账」相同。失败运行也占一行，Status 记为 `failed`，Why 写入错误。

### Phase 3：核验

1. 确认所有预期输出都存在于 `output/`。
2. 确认已捕获 `output/sessionInfo_stata.txt`，其中记录包版本。
3. 如果有稿件，运行 `/audit-reproducibility`，它会通过 `haven`/`pyreadstat` 读取 Stata 的 `.dta` 输出。
4. 报告运行了哪些脚本、生成了哪些输出，以及 Stata 给出的所有警告。

### Phase 4（可选）：R 交叉核对

指定 `--from-r` 时，运行同一分析的 R 版本，假定位于 `scripts/R/`，再比较：

- 点估计：按 `replication-protocol.md` 的容差，应吻合到约 0.01。
- 标准误：按论文设计、现行签核和已批准实现比较，容差沿用 `replication-protocol.md`；本技能不指定推断层级或选项。
- 样本量：必须完全一致。

如果不一致，交给用户排查。不要自行更改估计量、推断层级或扩展包；缺失的设计或签核信息按 Phase 1 的可见 `[CLARIFY:]` 说明处理。

## 配套技能

- [`/data-analysis`](../data-analysis/SKILL.md) —— R 版对应技能，流水线形态相同，语言不同。
- [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) —— 同时读取 `.rds` 和 `.dta` 输出，交叉核对稿件断言与实际数值。
- [`/review-paper`](../review-paper/SKILL.md) —— 论文存在且引用本流水线生成的表图时，按 `cross-artifact-review.md` 自动调用 `/audit-reproducibility`。

## 反模式

- **手工编辑 `.dta` 文件。** 永远不要。所有变换都通过 `.do` 文件完成；`.dta` 输出是可复现的派生物。
- **跳过 `99_run_all.do`。** 这是 AEA 要求的单命令入口，项目再小也要创建。
- **[待 owner 签核] 推断方式未确认就直接估计。** 本技能不给出稳健标准误、聚类层级或自助法的默认操作指示；必须遵循论文设计、现行签核和已批准包，缺失时留下 `[CLARIFY: 推断设计或签核未提供]` 并暂停相应步骤。
- **在 LaTeX 中手工排表格。** 使用 `esttab` 和 `\input{}`，见 `stata-code-conventions.md` §4。
- **只在一个 .do 文件中固定 Stata 版本。** 按约定，每个 `.do` 文件都以 `version 18` 开头。

## 参数

| 参数 | 作用 |
|---|---|
| `--from-r` | 把 `scripts/R/` 下既有的 R 流水线当转译源，并在 Phase 4 跑 R 交叉核对。 |
| `--no-execute` | 只搭出并检查 `.do` 文件，不通过 Bash 调用 Stata 执行任何脚本（Phase 2 跳过）。 |

## 交叉引用

- [`.codebuddy/rules/stata-code-conventions.md`](../../rules/stata-code-conventions.md) —— 纪律契约。
- [`.codebuddy/rules/replication-protocol.md`](../../rules/replication-protocol.md) —— 容差阈值（跨 R / Stata / Python 适用）。
- [AEA Data Editor checklist](https://aeadataeditor.github.io/) —— 复现包标准。

## 长跑拟合 / 批量重跑：后台完成通知

长跑与短跑都使用 Phase 2 的 Bash `run_in_background: true` 主路径。启动前确认控制台日志与 Stata 自身日志的位置，启动后等待任务完成通知，再用 TaskOutput 读取结果并核对两类日志和预期产物。后台任务结束不等于估计成功：只有退出码、当前日志与产物共同通过检查，才进入下一个脚本；失败时按 Phase 2 记录并停止。
