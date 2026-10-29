---
name: learn
description: |
  把本次会话中可复用的知识萃成一个持久技能。
  当你发现某件并不显然的事、造了一个变通方案，或摸索出一套
  未来的会话会受益的多步工作流时使用。
description_zh: |
  把本次会话中可复用的知识萃成一个持久技能。
  当你发现某件并不显然的事、造了一个变通方案，或摸索出一套
  未来的会话会受益的多步工作流时使用。
argument-hint: "[skill-name (kebab-case)]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep"]
disable-model-invocation: true
metadata:
  author: Claude Code Academic Workflow
  version: 1.0.0
---

# /learn —— 技能萃取工作流

把并不显然的发现萃取成可复用的技能，让它跨会话留存。

## 何时使用本技能

遇到下列情形时调用 `/learn`：

- **并不显然的排错** —— 花了不少功夫的调查，文档里没有
- **误导性的报错** —— 错误信息是错的，你找到了真正的原因
- **变通方案** —— 碰到一个限制，用有创意的办法绕过
- **工具集成** —— 没有文档记录的 API 用法或配置
- **反复试错** —— 试了好几次才成功
- **可重复的流程** —— 你会再做一次的多步任务
- **面向用户的自动化** —— 用户会来要的报告、检查或流程

## 工作流阶段

### PHASE 1：评估（自评）

创建技能之前，先回答这几个问题：

1. 「我刚刚学到了什么，是刚开始时并不显然的？」
2. 「把它写下来，将来的我会不会受益？」
3. 「光看文档，这个解法是不是就不显然？」
4. 「这是我愿意再做一次的多步工作流吗？」

**至少有一个问题答 YES 才继续。**

### PHASE 2：检查已有技能

搜索相关技能，避免重复：

```bash
# Check project skills
ls .codebuddy/skills/ 2>/dev/null

# Search for keywords
grep -r -i "KEYWORD" .codebuddy/skills/ 2>/dev/null
```

**三种结果：**
- 没有相关的 → 新建技能（继续 PHASE 3）
- 触发条件与解法都相同 → 更新已有技能（升版本号）
- 部分重叠 → 作为新变体更新进去

### PHASE 3：创建技能

把技能文件建在 `.codebuddy/skills/[skill-name]/SKILL.md`：

```yaml
---
name: descriptive-kebab-case-name
description: |
  [What the skill does, then the situations it applies to — the key use first.
   Include an exact error string only when that string is the trigger.]
  - What the skill does
  - Trigger conditions (symptoms; an exact error message when that is the trigger)
  - When to use it (contexts, scenarios)
metadata:
  author: [you]
  version: "1.0"
argument-hint: "[expected arguments]"  # Optional
---

# Skill Name

## Problem
[Clear problem description — what situation triggers this skill]

## Context / Trigger Conditions
[When to use — exact error messages, symptoms, scenarios]
[Be specific enough that you'd recognize it again]

## Solution
[Step-by-step solution]
[Include commands, code snippets, or workflows]

## Verification
[How to verify it worked]
[Expected output or state]

## Example
[Concrete example of the skill in action]

## References
[Documentation links, related files, or prior discussions]
```

### PHASE 4：质量门禁

定稿之前，逐项确认：

- [ ] description 写明了具体触发条件（不含糊）
- [ ] 解法已验证可用（实测过）
- [ ] 内容足够具体，能照着做
- [ ] 内容足够通用，能复用
- [ ] 没有敏感信息（凭据、个人数据）
- [ ] 技能名有描述性，且用 kebab-case

## 输出

创建完技能后，报告：

```
✓ Skill created: .codebuddy/skills/[name]/SKILL.md
  Trigger: [when to use]
  Problem: [what it solves]
```

## 示例：创建一个技能

用户发现某个 R 包会静默丢弃观测：

```markdown
---
name: fixest-missing-covariate-handling
description: |
  Handle silent observation dropping in fixest when covariates have missing values.
  Use when: estimates seem wrong, sample size unexpectedly small, or comparing
  results between packages.
metadata:
  author: [you]
  version: "1.0"
---

# fixest Missing Covariate Handling

## Problem
The fixest package silently drops observations when covariates have NA values,
which can produce unexpected results when comparing to other packages.

## Context / Trigger Conditions
- Sample size in fixest is smaller than expected
- Results differ from Stata or other R packages
- Model has covariates with potential missing values

## Solution
1. Check for NA patterns before regression:
   ```r
   summary(complete.cases(data[, covariates]))
   ```
2. Explicitly handle NA values or use `na.action` parameter
3. Document the expected sample size in comments

## Verification
Compare `nobs(model)` with `nrow(data)` — difference indicates dropped obs.

## References
- fixest documentation on missing values
- [LEARN:r-code] entry in MEMORY.md
```
