---
name: init-research-project
description: 把一个 fork 下来的模板初始化成一个真实的科研项目——逐项收齐项目信息、替换全部占位符、按学科裁剪规则与代理、跑通环境自检，最后交出一份可执行的起步计划。用户说 "init"、"初始化项目"、"开一个新项目"、"start a new project"、"把这个模板变成我的项目" 时使用。NOT for 给已经在跑的项目加功能——那用对应的技能（`/create-lecture`、`/preregister` 等）。
description_zh: 把一个 fork 下来的模板初始化成一个真实的科研项目——逐项收齐项目信息、替换全部占位符、按学科裁剪规则与代理、跑通环境自检，最后交出一份可执行的起步计划。用户说 "init"、"初始化项目"、"开一个新项目"、"start a new project"、"把这个模板变成我的项目" 时使用。NOT for 给已经在跑的项目加功能——那用对应的技能（`/create-lecture`、`/preregister` 等）。
argument-hint: "[可选：项目简称]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
user-invocable: true
---

# 初始化科研项目

把模板的**占位符状态**变成一个能干活的项目状态。这不是一次「欢迎页」，而是一次**受控的填充作业**：每一处改动都能被说出理由，没问清的东西不猜。

## 为什么要有这一步

模板里到处是 `[YOUR PROJECT NAME]`、`[你的单位]`、`[your-env]` 这类占位符，以及一套**通用**的规则与代理。不初始化就直接开工，结果是：

- 规则按 `paths:` 匹配上了，但里面的示例是你的主题之外的例子；
- 代理被派去审一个它不知道学科规范的稿子；
- 半年后你自己也分不清哪条规则是你写的、哪条是模板带来的。

这个技能把这三件事一次做完，并且在 `quality_reports/` 留下记录。

## 阶段 0 —— 起飞前检查（不通过就不往下走）

按顺序确认，任何一项失败就停下并报告，不要「先跳过后面再补」：

1. **这是不是一个干净的项目？** 读 `CODEBUDDY.md` 的第一段。若占位符已被填过（`[你的项目名称]` 不见了），说明初始化过了——问用户是要**重新初始化**还是**只补缺项**，不要覆盖已有内容。
2. **环境自检。** 跑 `./scripts/validate-setup.sh`（Windows 下用 `bash scripts/validate-setup.sh`，或按它报告的缺失项逐条确认）。把它的输出原样贴给用户，不要总结成「一切正常」。
3. **门禁基线。** 跑 `python scripts/backtest.py`。**要求全绿**再开始改东西——一个开始就红的仓库，初始化之后你分不清哪处红是模板的、哪处是你弄的。

## 阶段 1 —— 收齐信息（一次问完，不要挤牙膏）

按下面的清单向用户提问。**已经能从仓库里读出来的，不要问**（比如从 `CITATION.cff`、`README.md`、已有的 `Slides/` 推断）。一次把问题列全，等一轮回答。

| 项 | 落到哪里 | 说明 |
|---|---|---|
| 项目名称 | `CODEBUDDY.md`、`README.md`、`CITATION.cff` | 论文/课程的真名，不是代号 |
| 单位与作者 | `CODEBUDDY.md`、`CITATION.cff` | |
| 学科 | `.codebuddy/references/journal-profiles.md`、`.codebuddy/agents/domain-reviewer.md` | 决定目标期刊集合与领域审读透镜 |
| 主要交付物 | `CODEBUDDY.md` 的「当前项目状态」表 | 讲义？论文？两者都有？ |
| 目标期刊 / 会议 | `.codebuddy/references/journal-profiles.md` | 直接决定 `--peer` 的校准 |
| 数据是否有访问限制 | `.codebuddy/rules/confidential-data.md`、`TROUBLESHOOTING.md` | 有就**必须先**配拒绝规则再放任何数据进来 |
| 是否用 Stata / R / Python | 对应 `*-conventions.md` | 不用的那套留着不碍事，但要告诉用户它存在 |
| 语言 | 中文写作还是英文写作 | 决定 `/humanize`、`/proofread` 的判据 |

**遇到用户说「你先按常见的来」**：可以代填，但必须把每一处代填**列出来**并标注「这是我替你定的，改起来是一行」。不要静默代填。

## 阶段 2 —— 填充（按这个顺序，逐项留痕）

1. **`CODEBUDDY.md`** —— 换掉项目名、单位，删掉 `HelloWorld` 样例行，把「当前项目状态」表换成真实的第一行。
2. **`CITATION.cff`** —— 标题、作者、年份。
3. **学科裁剪**：
   - `journal-profiles.md`：保留用户学科相关的画像，其余标注为「本学科未用」而不是删除（上游同步时好合并）。
   - `domain-reviewer.md`：把通用透镜换成用户学科的审读透镜，并写清「这一条为什么是本学科特有的」。
4. **受限数据**（仅当阶段 1 回答「有」）：先在 `.codebuddy/settings.json` 里加 **deny 规则**，再继续别的。顺序不能反。
5. **`README.md`** —— 只改「这个项目是什么」，不要重写模板的说明部分（那是上游的，改了会让同步变成人工合并整份文件）。
6. **`MEMORY.md`** —— 清掉模板自带的示例 `[LEARN]` 条目（如果它们不是你的教训），保留格式。

## 阶段 3 —— 验证（做了才算完）

按顺序跑，任一条红就修到绿再报完成：

```bash
python scripts/backtest.py            # 门禁全绿
python scripts/backtest.sh            # 上游原件（POSIX bash 环境下）
./scripts/validate-setup.sh           # 环境自检
```

再人工确认三件事：

- `CODEBUDDY.md` 里**再没有** `[方括号占位符]`（`grep -n '\[.*\]' CODEBUDDY.md` 逐条看，允许保留的只有示例表格里标了「删掉」的那几行）；
- 改过的规则文件仍然通过 `python scripts/check-skill-integrity.py`（改了标题就要同步锚点）；
- **没有任何计数断言被你改坏**：`python scripts/verify-count-gates.py` 应当 12/12 变红。

## 阶段 4 —— 交出起步计划

不要在初始化结束时说「好了，你可以开始了」。要给出**下一步的三个具体动作**，例如：

1. 第一份真材料放进 `master_supporting_docs/`，然后跑 `/create-lecture` 或 `/preregister`；
2. 用 `/interview-me` 把研究问题问清楚（如果还没有）；
3. 跑一次 `/commit`，让质量门禁在**第一次**提交时就生效。

把这份计划写进 `quality_reports/plans/`，并在 `MEMORY.md` 追加一条 `[LEARN:project] 初始化于 YYYY-MM-DD：学科=…，交付物=…` —— 半年后的你会需要这一行。

## 边界（不要做的事）

- **不要 `git commit`。** 初始化不是提交；提交由用户用 `/commit` 决定。
- **不要删规则或技能。** 用不上就标注，不要删——删掉的东西在上游同步时会静默回来，而你以为它没了。
- **不要为了「看起来整洁」重排目录。** 目录结构本身是被门禁检查的契约。
- **不要在阶段 0 门禁还是红的时候开始填。** 那会把「模板的问题」和「你的问题」混成一片，之后谁也说不清。
