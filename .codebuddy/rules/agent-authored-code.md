---
paths:
  - "**/*.sh"
  - "**/*.py"
  - "**/*.R"
  - "**/*.do"
---

# 代理写出的代码——缺陷通常出在我们这边

在 367 小时有记录的会话中，**有缺陷的代码**是最常见的摩擦来源，而且大多**不在既有代码库里**。代理会在会话中临时编写批量正则、监控循环和运行脚本，问题通常就出在这里。

这些故障并不稀奇，以下四类问题会反复出现。

---

## 1. 没做过试运行，就不要做全仓库范围的改写

一条正则在测试样例上看似正确，处理到第 40 个文件时却可能产生完全不同的结果。

**使用 `sed -i`、Python 重写循环或 `replace_all` 做任何批量改写之前：**

1. 打印将要改动的文件**数量**和**前三处 diff**。
2. 逐条阅读这些 diff，确认它们正是预期改动，不要只扫一眼。
3. 确认后再执行改写。
4. **改完后核对输出**，不要只看退出码。正则即使改错了文字，也可能以 0 退出。

*事故：*一条用于把 `Task` 迁移为 `Agent` 的正则，在 **14 个文件**中留下了多余的反引号。可选的尾部 `` `? `` 没有匹配作者预期的内容，脚本却报告成功。后来，一个无关的链接检查器才发现这些污染。

*事故：*同一次迁移把 **33 个技能**中的 `["Read", "Task"]` 改成了 `["Read", "Agent, Task"]`。后者表示一个名称含逗号的工具，不是两个工具。只有阅读输出才能发现这个问题。

> **规则：**批量改写不能以脚本退出码为 0 作为完成标准。只有读过结果样本，才算完成。

---

## 2. 路径要在任何 `cd` 之前解析，不是之后

```bash
# WRONG — $0 is RELATIVE when invoked as ./run.sh, so after any cd the
# saved path points at the wrong place (or nowhere)
SCRIPT_DIR="$(dirname "$0")"     # e.g. "."
cd /tmp/workdir
source "$SCRIPT_DIR/lib.sh"      # resolves against /tmp/workdir — breaks

# RIGHT — resolve to an ABSOLUTE path before any cd
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd /tmp/workdir
source "$SCRIPT_DIR/lib.sh"      # still correct from anywhere
```

有些脚本从仓库根目录调用时正常，换到其他位置就会悄悄出错。这样的脚本比直接失败的脚本更危险，因为它仍会产出结果。

---

## 3. 用 PID 文件监控，绝不用 `pgrep` 模式

```bash
# WRONG — the watcher's own command line contains the pattern, so it waits on itself, forever
while pgrep -f "run_simulation" > /dev/null; do sleep 60; done

# RIGHT — the job records its PID; the watcher checks that specific process
nohup Rscript run_simulation.R > sim.log 2>&1 & echo $! > sim.pid
while kill -0 "$(cat sim.pid)" 2>/dev/null; do sleep 60; done
```

*事故：*一条监控链的 `pgrep` 模式匹配到了监控链自身，于是它一直等待自己结束，直到时限耗尽。

**监控还必须覆盖所有终态。**只用 grep 查找成功信息的监控器，在任务崩溃时不会发出任何信号，而**沉默看起来与「仍在运行」完全一样**。监控器必须区分任务完成、任务失败，以及进程消失但两者都未发生的情况。

---

## 4. 长跑任务：`nohup` + 心跳文件 + 写下来的运行手册

任务如果需要运行数小时，开始前就要把**收尾运行手册**写入受版本控制的文件，列明续跑命令、产物路径和需要核对的判定。上下文会被压缩，磁盘记录不会。

任务应写出心跳，包括时间戳和完成计数，供监视器轮询。**ETA 必须根据产物时间戳计算，不能凭印象估计。**

---

## 宁可用提交进仓库的脚本，也不用临时现编的

同一个循环写过两次，就应把它放进 `scripts/`，并满足以下要求：

- 在任何 `cd` **之前**解析绝对路径；
- 使用 **PID 文件**监控；
- 提供 **`--dry-run`** 开关；
- 失败时以非零状态退出，并明确指出失败位置。

每次会话都应优先调用已经验证可用的脚本，不要临时编写脆弱脚本。

---

## 关于代码的断言都要带版本

陈述代码当前行为时，必须注明阅读代码所用的版本。例如，「门禁会拒绝未登记的 fixture」「这个函数返回六个元素」「那个 bug 已修」都属于这类断言。应优先在干净检出中核验，读取代码时执行 `git rev-parse --short HEAD`，并在断言中附上这个短 SHA，用它标识代码版本。若必须在脏工作树中核验，必须记录 `git status --short` 与实际所读文件的内容哈希（或等价的内容标识），未跟踪文件也必须纳入；不得只用 HEAD 或可能为空的 `git diff` 哈希冒充实际代码版本。**没有版本戳的断言会悄悄过期**，因为读者无法区分它描述的是当前代码，还是三个提交之前的代码。[`issue-ledger.md`](issue-ledger.md) 已要求缺陷报告注明确切的源码版本；同一条标准也适用于所有关于代码状态的断言，不限于最终登记为 issue 的问题。

---

## 交叉引用

- [`.codebuddy/rules/simulation-conventions.md`](simulation-conventions.md) —— 按任务播种，不按 worker 播种；证明运行形态无关性
- [`.codebuddy/rules/repo-hygiene.md`](repo-hygiene.md) —— 这些产出的草稿脚本不能变成主文件
- [`issue-ledger.md`](issue-ledger.md) —— 同一条版本戳标准，每份缺陷报告都必须遵守
- [`.codebuddy/references/research-agent-laws.md`](../references/research-agent-laws.md) —— 法则 1、10
