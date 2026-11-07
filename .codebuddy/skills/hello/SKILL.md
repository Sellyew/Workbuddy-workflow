---
name: hello
version: "0.1.0"
description: 冒烟测试技能。用于测试技能是否可用，验证 `.codebuddy/skills` 能被发现，且 `/hello` 可被调用。
description_zh: 冒烟测试技能。用于测试技能是否可用，验证 `.codebuddy/skills` 能被发现，且 `/hello` 可被调用。
allowed-tools: ["Read", "Write", "Bash"]
argument-hint: "[任意标记文本]"
user-invocable: true
category: meta
tags: [smoke-test, migration-verification]
---

# /hello —— 技能发现冒烟测试

本技能只负责提供外部可核验的证据，证明系统能发现并执行技能，不承担科研功能。技能自身不能判定测试通过，必须由调用方核验。P0 验证通过后，可保留它做回归自测，也可在 P4 定型时删除。

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

1. 调用方先生成本次运行独有的随机标记，记录预期工作目录，再调用 `/hello <随机标记>`。调用前必须确认 `quality_reports/checkpoints/_SMOKE_HELLO.md` **不存在**。若文件已经存在，本次测试无效；旧文件不能充当新证据，也不能靠覆盖旧文件凑出通过结果。
2. 调用后，调用方独立读取目标文件，确认它确实由本次调用创建，并逐项核对：`SKILL-SMOKE-OK` 存在；`arg:` 与随机标记逐字一致；`cwd:` 等于预期工作目录；`at:` 是本次运行的时间。聊天回复只能作为辅助信号，不能代替文件核验。
3. 调用方分别记录失败原因：`/hello` 未识别属于**调用失败**；目标文件未创建属于**执行失败**；`arg:` 与随机标记不符属于**参数传递失败**；`cwd:` 或其他内容不符属于**执行环境/内容失败**。只有全部外部检查通过，才能判 **T4 通过（项目技能发现与显式调用）**。

`src: codebuddy` 只是技能写出的固定文本，**不能证明来源**。不要依赖技能内部无法到达的失败分支，也不要只凭固定标记或技能自报结果判定通过。
