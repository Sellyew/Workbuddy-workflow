---
name: hello
version: "0.1.0"
description: 冒烟测试技能。用于验证 `.codebuddy/skills` 能被发现，且 `/hello` 可被调用。
description_zh: 冒烟测试技能。用于验证 `.codebuddy/skills` 能被发现，且 `/hello` 可被调用。
description_en: Smoke-test skill. Verifies that `skills` are discovered and slash-invocable.
allowed-tools: ["Read", "Write", "Bash"]
argument-hint: "[任意标记文本]"
user-invocable: true
disable-model-invocation: false
category: meta
tags: [smoke-test, migration-verification]
---

# /hello —— 技能发现冒烟测试

本技能的唯一目的是**证明技能被发现且能执行**，不承担任何科研功能。P0 验证通过后保留（作为回归自测），或在 P4 定型时删除。

## 执行步骤

1. 读取 `$ARGUMENTS`。若为空，使用 `NO-ARG`。
2. 用 `Write` 创建 `quality_reports/checkpoints/_SMOKE_HELLO.md`，内容为：

   ```
   SKILL-SMOKE-OK
   arg: <上一步取到的参数>
   at: <当前日期时间>
   cwd: <当前工作目录>
   ```

3. 在回复中输出且仅输出下面三行（不要附加解释、不要复述本文件）：

   ```
   SKILL-SMOKE-OK
   src: codebuddy
   arg: <参数>
   file: quality_reports/checkpoints/_SMOKE_HELLO.md
   ```

   `src: codebuddy` 是**路径判别标记**：`.workbuddy/skills/hello/SKILL.md` 副本输出 `src: workbuddy`。
   两者内容故意不同，用于判定平台实际从哪个目录加载项目技能。

## 判定

- 若回复中出现 `SKILL-SMOKE-OK` 且文件被真实创建 → **T4 通过（技能发现与调用：原生支持）**
- 若 `/hello` 未被识别 → 记录失败，回退测试 `.workbuddy/skills/hello/SKILL.md` 路径
