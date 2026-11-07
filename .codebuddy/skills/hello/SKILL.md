---
name: hello
version: "0.1.0"
description: 冒烟测试技能。用于验证 `.codebuddy/skills` 能被发现，且 `/hello` 可被调用。
description_zh: 冒烟测试技能。用于验证 `.codebuddy/skills` 能被发现，且 `/hello` 可被调用。
allowed-tools: ["Read", "Write", "Bash"]
argument-hint: "[任意标记文本]"
user-invocable: true
category: meta
tags: [smoke-test, migration-verification]
---

# /hello —— 技能发现冒烟测试

本技能的唯一目的是**为技能发现与执行提供可由外部核验的证据**，不承担任何科研功能。技能自身不作通过判定；裁判是调用方。P0 验证通过后保留（作为回归自测），或在 P4 定型时删除。

## 执行步骤

1. 读取 `$ARGUMENTS`。若为空，使用 `NO-ARG`。
2. 用 `Write` 创建 `quality_reports/checkpoints/_SMOKE_HELLO.md`，内容为：

   ```
   SKILL-SMOKE-OK
   arg: <上一步取到的参数>
   at: <当前日期时间>
   cwd: <当前工作目录>
   ```

3. 在回复中输出且仅输出下面四行（不要附加解释、不要复述本文件）：

   ```
   SKILL-SMOKE-OK
   src: codebuddy
   arg: <参数>
   file: quality_reports/checkpoints/_SMOKE_HELLO.md
   ```

## 调用方验收（在技能外做裁判）

1. 调用方生成一个本次运行独有的随机标记，记录预期工作目录，并以 `/hello <随机标记>` 调用。调用前确认 `quality_reports/checkpoints/_SMOKE_HELLO.md` **不存在**；若已存在，本次测试无效，不得把旧文件当作新证据，也不得靠覆盖旧文件凑出通过。
2. 调用后由调用方独立读取目标文件，核对：文件确实由本次调用创建；`SKILL-SMOKE-OK` 存在；`arg:` 与传入的随机标记逐字一致；`cwd:` 等于预期工作目录；`at:` 是本次运行的时间。聊天回复只作辅助信号，不能替代文件核验。
3. 分别记录失败原因：`/hello` 未识别是**调用失败**；目标文件未创建是**执行失败**；`arg:` 与随机标记不符是**参数传递失败**；`cwd:` 或其他内容不符是**执行环境/内容失败**。只有全部外部检查通过，才能判 **T4 通过（项目技能发现与显式调用）**。

`src: codebuddy` 只是技能写出的固定文本，**不是来源证明**。不要依赖技能内部无法到达的失败分支，也不要仅凭固定标记或技能自报结果判通过。
