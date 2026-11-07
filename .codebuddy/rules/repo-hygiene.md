# 仓库卫生——草稿不能变成主干

代理会试错。Claude 和 Codex 可能分别围绕一个问题探索五条路径，其中四条会留下文件。**这四条不能留下来。**如果仓库保留每次放弃的尝试，真正的工作就会被噪声淹没，项目也会在代码尚好时显得无人维护。

`scripts/check-repo-hygiene.py` 强制执行本规则，并随 `./scripts/backtest.sh` 运行。因此，**只要运行过 `./scripts/install-hooks.sh`**，每次提交都会检查一遍；在此之前，新克隆中的钩子不会生效。CI 则无条件执行检查。

## 规则

> **任何你不会在代码评审里为之辩护的东西，都不要作为主文件提交。**

每样东西只能去以下三个去处之一：

| 去处 | 用于 | 提交？ |
|---|---|---|
| **草稿区**（仓库之外，或 `explorations/`） | 试东西；你还不知道它行不行 | `explorations/` 是**被跟踪的**，但豁免于草稿命名检查；其协议允许带版本、带日期的文件，探索结束时必须清理干净 |
| **工作树**（`Slides/`、`Quarto/`、`scripts/`、`.codebuddy/`） | 你选定并愿意为之辩护的那条路径 | 是 |
| **归档**（`master_supporting_docs/`、`explorations/` 下某个带日期的子目录） | 被取代但值得留档的工作 | 是，**并附一份说明原因的 README** |

## 各类文件放在哪里

这套布局遵循 AEA Data Editor 对复现包的建议：输入、代码和结果分开存放，并用一条命令重建全部结果。如果项目的 `CODEBUDDY.md` 目录树另有规定，以它为准；这里只提供默认布局。

| 类别 | 位置 | 提交？ |
|---|---|---|
| 原始输入 | `data/raw/`：只读，代码永不写入此处 | 仅当许可证允许；受限数据绝不提交，见 [`confidential-data.md`](confidential-data.md) |
| 分析代码 | `scripts/<lang>/`：编号阶段（`01_load.R`、…）加一个主脚本（`00_run_all.R`、`99_run_all.do`） | 是 |
| 包式函数与测试 | `R/`、`tests/testthat/`，见 [`r-package-conventions.md`](r-package-conventions.md) | 是 |
| 生成的结果 | 顶层 `output/`，绝不放在 `scripts/` 内；按项目划分子目录，如 `tables/`、`figures/`，或按分析划分 | 表格、图、日志、`sessionInfo*.txt`：是，但受限数据必须先通过披露审查。可再生的中间产物（`.rds`、`.parquet`、`.dta`、…）：否 |
| 钩子 | `.codebuddy/hooks/` | 是，前提是 `.codebuddy/settings.json` 会调用它们，否则克隆会坏；个人钩子放在 `settings.local.json` |
| 计划、会话日志 | `quality_reports/plans/`、`quality_reports/session_logs/` | 依项目的 `.gitignore` 而定；本模板忽略它们，因为这是 owner 的工作，不是模板内容。协作者需要某一份时，可用 `git add -f` |
| 草稿 | 会话草稿区，或按[其协议](exploration-folder-protocol.md)放在 `explorations/` | 草稿区：否；`explorations/`：是，探索结束时清理干净 |

## 检查器拒绝什么

- **根目录杂物。**仓库根目录中不在允许清单内的文件。顶层只保留新人必须先看到的内容，其余文件都放进目录。
- **草稿命名。**`untitled`、`tmp`、`temp`、`scratch`、`foo`、`bar`、`baz`、`asdf`、`test123` 用作完整文件名，或用作以分隔符收尾的前缀，都会被拒绝。`scratch_x.py`、`tmp.R`、`scratch-notes.md` 算；`scratchpad-notes.md` 和 `template.md` 不算，因为该词后面必须跟一个非字母数字字符。
- **被取代的副本。**例如 `analysis_old.R`、`deck_backup.tex`、`notes_copy.md`。值得保留就附理由归档，否则删除，**git 已经保存历史。**
- **文件名里带版本号。**例如 `model_v2.R`、`paper_final.tex`、`script_fixed.py`。版本由 git 管理，而且 `_final` 从来不是终版。*豁免：`explorations/`，其[协议](exploration-folder-protocol.md)有意允许 `_v1`/`_v2` 迭代。*
- **意外重复。**`notes 2.md` **且 `notes.md` 同时存在**才是副本的特征；单看 `Lecture 2.tex`，它只是普通的学术文件名，不会被标记。`data(1).csv` 也属于意外重复。
- **被跟踪的构建产物。**例如 `.aux`、`.log`、`.synctex.gz`、`.pyc`。可再生的输出不属于版本控制。
- **被改写的只追加记录。**某个提交编辑或删除 `quality_reports/replication-log.md` 或 `quality_reports/spec-ledger.md` 中已经提交的行，就会被拒绝。pre-commit 对照上一次提交检查，CI 对照基础分支检查。更正必须新增条目；披露性删改使用 `ALLOW_LOG_REWRITE=1` 提交，并在提交信息中写明理由。
- **没有说明的归档。**没有 README 的归档目录无法与废弃杂物区分。*检查器只对指定的归档根目录执行此条，即 `explorations/`、`master_supporting_docs/`，不会检查树中的每一个目录。*

*编号的流水线阶段不受此限*：`01_explore.R`、`02_clean.R`、`03_analyze.R` 是惯例用法，不是草稿。

## 归档，而不是删除

工作已被取代但记录仍然重要时，例如先前的设定、因有趣原因失败的路径或上学期的一套幻灯片，应当归档：

1. 移到**带日期**的子目录，例如 `explorations/2026-08_did-alternative-weighting/`。
2. 添加一份 README，用**三行**说明这是什么、为什么被取代、什么取代了它。
3. 此后不再修改。会继续变化的归档不叫归档。

> **一条失败的路径是证据。**它告诉下一个人，往往是你自己，哪些路已经封了。只要标注清楚，就值得保留；没有标注的死路，代价高于收益。

## 专门给代理的话

- 把实验写在会话草稿区，**不要**写进仓库。草稿文件必须位于仓库才能运行时，把它放进 `explorations/`，完成后删除。
- **绝不**为了试东西，在 `foo.R` 旁边创建 `foo_v2.R`。直接修改 `foo.R`，git 就是撤销键。
- 放弃某条路径时，**在落地所选路径的同一个提交中删除它的文件**。不要同时保留两者，让读者猜测哪个仍然有效。
- 不确定某个东西是否算草稿时，在它通过某道门禁之前，都按草稿处理。

## 交叉引用

- [`.codebuddy/rules/exploration-folder-protocol.md`](exploration-folder-protocol.md)：`explorations/` 如何组织。
- [`.codebuddy/rules/meta-governance.md`](meta-governance.md)：什么进提交、什么留在本地。
- [`progress-reports.md`](progress-reports.md)：*工作*记录保存在哪里，文件因此不必自行承担记录功能。
