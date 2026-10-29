# 仓库卫生——草稿不能变成主干

代理会试错。Claude 和 Codex 各自会对一个问题探索五条路径，其中四条会留下文件。**这四条不能活下来。** 一个把每次放弃的尝试都留在原地的仓库，不是工作的记录——它是噪声，会让真正的工作无处可寻；它也是让一个项目在代码尚好时显得无人维护的最快办法。

由 `scripts/check-repo-hygiene.py` 强制执行，它跑在 `./scripts/backtest.sh` 里——因此**只要 `./scripts/install-hooks.sh` 跑过**，每次提交都会走一遍（在那之前，新克隆里的钩子是哑的），此外在 CI 中无条件执行。

## 规则

> **任何你不会在代码评审里为之辩护的东西，都不要作为主文件提交。**

三个去处，每样东西只去其中一个：

| 去处 | 用于 | 提交？ |
|---|---|---|
| **草稿区**（仓库之外，或 `explorations/`） | 试东西；你还不知道它行不行 | `explorations/` 是**被跟踪的**，但豁免于草稿命名检查——它自己的协议允许在那里放带版本、带日期的文件；探索结束时清理干净 |
| **工作树**（`Slides/`、`Quarto/`、`scripts/`、`.codebuddy/`） | 你选定的、愿意为之辩护的那条路径 | 是 |
| **归档**（`master_supporting_docs/`、`explorations/` 下某个带日期的子目录） | 被取代但值得留档的工作 | 是，**并附一份说明原因的 README** |

## 各类文件放在哪里

这套布局遵循 AEA Data Editor 对复现包的建议：输入、代码、结果分处三地，并用一条命令重建全部结果。若某项目的 `CODEBUDDY.md` 目录树另有规定，以它为准；这里是默认。

| 类别 | 位置 | 提交？ |
|---|---|---|
| 原始输入 | `data/raw/`——只读；代码永不写入此处 | 仅当许可证允许；受限数据绝不（[`confidential-data.md`](confidential-data.md)） |
| 分析代码 | `scripts/<lang>/`——编号阶段（`01_load.R`、…）加一个主脚本（`00_run_all.R`、`99_run_all.do`） | 是 |
| 包式函数与测试 | `R/`、`tests/testthat/`（[`r-package-conventions.md`](r-package-conventions.md)） | 是 |
| 生成的结果 | 顶层 `output/`，绝不在 `scripts/` 以内；按项目分子目录（`tables/`、`figures/`，或按分析分） | 表格、图、日志、`sessionInfo*.txt`：是——前提是受限数据已过披露审查。可再生的中间产物（`.rds`、`.parquet`、`.dta`、…）：否 |
| 钩子 | `.codebuddy/hooks/` | 是，前提是 `.codebuddy/settings.json` 会调用它们——否则克隆会坏；个人钩子放 `settings.local.json` |
| 计划、会话日志 | `quality_reports/plans/`、`quality_reports/session_logs/` | 依项目的 `.gitignore` 而定；本模板忽略它们（这是 owner 的工作，不是模板内容）——协作者需要的某一份可 `git add -f` |
| 草稿 | 会话草稿区，或按[其协议](exploration-folder-protocol.md)放在 `explorations/` | 草稿区：否；`explorations/`：是，探索结束时清理干净 |

## 检查器拒绝什么

- **根目录杂物。** 仓库根目录下不在允许清单里的文件。顶层空间留给新人必须先看到的东西；其余一切住在目录里。
- **草稿命名。** `untitled`、`tmp`、`temp`、`scratch`、`foo`、`bar`、`baz`、`asdf`、`test123`——作为整个文件名，或作为以分隔符收尾的前缀（`scratch_x.py`、`tmp.R`、`scratch-notes.md` 算；`scratchpad-notes.md` 和 `template.md` 不算——该词后面必须跟一个非字母数字字符）。
- **被取代的副本。** `analysis_old.R`、`deck_backup.tex`、`notes_copy.md`。值得留就带理由归档；否则删掉——**git 已经有历史了。**
- **文件名里带版本号。** `model_v2.R`、`paper_final.tex`、`script_fixed.py`。那是 git 的活，而且 `_final` 从来不是终版。*（豁免：`explorations/`——它的[协议](exploration-folder-protocol.md)有意允许在那里出现 `_v1`/`_v2` 迭代。）*
- **意外重复。** `notes 2.md` **且 `notes.md` 同时存在**（这才是副本的真特征——单看 `Lecture 2.tex` 是普通的学术文件名，不会被标记），以及 `data(1).csv`。
- **被跟踪的构建产物。** `.aux`、`.log`、`.synctex.gz`、`.pyc`。可再生的输出不属于版本控制。
- **被改写的只追加记录。** 某个提交编辑或删除了 `quality_reports/replication-log.md` 或 `quality_reports/spec-ledger.md` 中已提交的一行——在 pre-commit 时对照上一次提交检查，在 CI 中对照基础分支检查。更正是一条新条目；披露性删改以 `ALLOW_LOG_REWRITE=1` 提交，并在提交信息里写明理由。
- **没有说明的归档。** 没有 README 的归档目录与废弃杂物无从区分。*（检查器只对指定的归档根目录执行此条——`explorations/`、`master_supporting_docs/`——不是对树里每一个目录。）*

*编号的流水线阶段属豁免*——`01_explore.R`、`02_clean.R`、`03_analyze.R` 是惯例用法，不是草稿。

## 归档，而不是删除

当工作被取代、但记录本身要紧时——一个先前的设定、一条因为有趣原因而失败的路径、上学期的一套幻灯片：

1. 把它移到**带日期**的子目录：`explorations/2026-08_did-alternative-weighting/`。
2. 加一份 README，写**三行**：这是什么、为什么被取代、什么取代了它。
3. 之后再也不要改它。会变的归档不叫归档。

> **一条失败的路径是证据。** 它告诉下一个人——往往是你自己——哪些路已经封了。它值得保留，但前提是有标注。一条没有标注的死路，代价高于收益。

## 专门给代理的话

- 把实验写到会话草稿区，**不是**仓库。若某个草稿文件必须放在仓库里才能运行，就放在 `explorations/` 下，做完删掉。
- **绝不**在 `foo.R` 旁边建 `foo_v2.R` 来试东西。改 `foo.R`；git 就是撤销键。
- 某条路径被放弃时，**在落地所选路径的同一个提交里删掉它的文件**。不要两个都留着，让读者猜哪个是活的。
- 如果你不确定某个东西算不算草稿：在它通过某道门禁之前，它就是草稿。

## 交叉引用

- [`.codebuddy/rules/exploration-folder-protocol.md`](exploration-folder-protocol.md) — `explorations/` 如何组织
- [`.codebuddy/rules/meta-governance.md`](meta-governance.md) — 什么进提交、什么留在本地
- [`progress-reports.md`](progress-reports.md) — *工作*的记录住在哪里，这样文件不必自己扛着它
