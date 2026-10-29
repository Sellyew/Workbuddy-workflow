---
paths:
  - "**/*.sh"
  - "**/*.py"
  - "**/*.R"
  - "**/*.do"
---

# 代理写出的代码——缺陷通常出在我们这边

在 367 小时有记录的会话里，最常出现的摩擦点是**有缺陷的代码**，而它们大多
**并不在既有代码库里**。这些代码是代理在会话过程中写出来的：批量正则、监控循环、
自动生成的运行脚本。

这些都不是离奇的故障。它们就是同样的那四类，一遍又一遍。

---

## 1. 没做过试运行，就不要做全仓库范围的改写

一条在你测试用的例子上看起来没问题的正则，到第 40 个文件上会干出别的事。

**任何批量改写之前——`sed -i`、Python 重写循环、`replace_all`：**

1. 打印将要改动文件的**数量**，以及**前三处 diff**。
2. 确认这些 diff 就是你要的——逐条读，不要扫一眼。
3. 确认之后才动手。
4. **改完核对输出**，而不是核对退出码。一条跑成功了却改错文字的正则，
   退出码是 0。

*事故：*一条 `Task` → `Agent` 迁移正则把多余的反引号留在了 **14 个文件**里，因为
一个可选的尾部 `` `? `` 没有吃掉作者以为它会吃掉的东西。脚本报告成功。这次污染
是后来被一个无关的链接检查器发现的。

*事故：*同一次迁移把 `["Read", "Task"]` 变成了 `["Read", "Agent, Task"]`，
出现在 **33 个技能**里——那是一个名字里带逗号的工具，不是两个工具。只有读输出
才能抓到。

> **规则：**批量改写不是脚本退出码为 0 就算完成。你读过结果的样本，
> 才算完成。

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

一个从仓库根目录调用时正常、换个地方就悄悄出错的脚本，比一个直接失败的脚本更糟，
因为它会产出结果。

---

## 3. 用 PID 文件监控，绝不用 `pgrep` 模式

```bash
# WRONG — the watcher's own command line contains the pattern, so it waits on itself, forever
while pgrep -f "run_simulation" > /dev/null; do sleep 60; done

# RIGHT — the job records its PID; the watcher checks that specific process
nohup Rscript run_simulation.R > sim.log 2>&1 & echo $! > sim.pid
while kill -0 "$(cat sim.pid)" 2>/dev/null; do sleep 60; done
```

*事故：*一条监控链匹配到了自己的 `pgrep` 模式，于是在那里等自己，等到了截止时间
耗尽。

**而且要覆盖每一种终态。**只 grep 成功那一行的监控器，在整个崩溃过程中一声不响——
而**沉默看起来和「还在跑」一模一样**。要检查完成、失败，*以及*进程消失却
两者皆无。

---

## 4. 长跑任务：`nohup` + 心跳文件 + 写下来的运行手册

任何数小时的运行之前，先把**收尾运行手册**写进受版本控制的文件：
续跑命令、产物路径、要核对的判定。上下文会被压缩；
磁盘不会。

任务写出心跳（一个时间戳、一个完成计数），由监视器轮询。
**ETA 要用产物时间戳算，不要凭印象。**

---

## 宁可用提交进仓库的脚本，也不用临时现编的

一个循环只要写过两次，就该放进 `scripts/`，并且带上：

- 在任何 `cd` **之前**解析绝对路径；
- 基于 **PID 文件**的监控；
- 一个 **`--dry-run`** 开关；
- 失败时非零退出，并给出一条指明哪里失败的讯息。

每一个会话里，调用一个已知可用的脚本，都胜过现场现编一个脆弱脚本。

---

## 关于代码的断言都要带版本

任何关于代码当前行为的陈述——「门禁会拒绝未登记的 fixture」「这个函数返回六个
元素」「那个 bug 已修」——都要写明它是在哪个版本上读出来的：读取时执行
`git rev-parse --short HEAD`，把这个短 SHA 和断言一起带上。**不带版本戳的断言会
静默过期**——没有任何东西能区分一句现在仍为真的话，和一句描述三个提交之前文件的
话。[`issue-ledger.md`](issue-ledger.md) 已经要求缺陷报告写明确切的源码版本；
这是同一条标准，适用于关于代码状态的每一条断言，
而不只是那些最终变成 issue 的。

---

## 交叉引用

- [`.codebuddy/rules/simulation-conventions.md`](simulation-conventions.md) —— 按任务播种，不按 worker 播种；证明运行形态无关性
- [`.codebuddy/rules/repo-hygiene.md`](repo-hygiene.md) —— 这些产出的草稿脚本不能变成主文件
- [`issue-ledger.md`](issue-ledger.md) —— 同一条版本戳标准，每份缺陷报告都必须遵守
- [`.codebuddy/references/research-agent-laws.md`](../references/research-agent-laws.md) —— 法则 1、10
