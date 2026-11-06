# 技能 frontmatter 字段参考

技能文件 `.codebuddy/skills/<name>/SKILL.md` 的 YAML frontmatter 决定技能行为。本文件是**字段语义的单一真源**：下面三张标记表格由 `scripts/check-field-docs.py` 校验，与机器真源 `scripts/check-spec-conformance.py`（`WB_FIELDS` / `INERT_FIELDS`）保持一致——任一漂移都会让门禁变红。字段是否被 WorkBuddy 读取的判据见 [`platform-facts.md`](platform-facts.md)。

## 会读的字段（可用）

<!-- BEGIN skill-fields-valid -->
| 字段 | 用途 |
|---|---|
| `name` | 技能名，小写连字符，须与目录名一致（必填） |
| `description` | 决定何时自动加载（必填，≤1024 字符） |
| `description_zh` / `description_en` | 中/英文描述，与 `description` 同义 |
| `category` | 所属类别（技能市场） |
| `tags` | 标签 |
| `version` | 版本号（技能市场/版本管理） |
| `agent_created` | 技能市场来源标记 |
| `allowed-tools` | 预先批准清单（**不是沙箱**，见下） |
| `argument-hint` | `/name` 之后的参数占位符提示 |
| `user-invocable` | 是否允许 `/name` 直接调用 |
| `disable-model-invocation` | 阻止自动触发，只能 `/name` 调用 |
| `agent` | 链接到 `.codebuddy/agents/` 里的代理定义 |
| `model` | 指定模型档位 `default` / `lite` / `reasoning` |
<!-- END skill-fields-valid -->

## 写了不生效的字段（别写）

这些字段在 WorkBuddy 里**没有对应语义**，写了不报错、但也不会起作用：

<!-- BEGIN skill-fields-inert -->
| 字段 | 说明 |
|---|---|
| `effort` | 代理读、技能不读（调思考预算的是代理 frontmatter） |
| `when_to_use` | 无对应语义 |
| `arguments` | 无对应语义 |
| `disallowed-tools` | WorkBuddy 没有技能级工具黑名单 |
| `background` | 无对应语义 |
| `hooks` | 技能级不生效（钩子只有 settings 级） |
| `paths` | 技能级不生效（路径作用域是 rules 的 `paths:`） |
| `shell` | 无对应语义 |
<!-- END skill-fields-inert -->

## 被读但有害的字段

<!-- BEGIN skill-fields-hazardous -->
| 字段 | 说明 |
|---|---|
| `context` | `context: fork` **会被读**，但把技能送进 detached 子会话、工具集里没有 `Agent`（多透镜扇出退化成串行）。需要扇出的技能别写它 |
<!-- END skill-fields-hazardous -->

## 动态内容

技能正文里可用的替换项：

- `$ARGUMENTS` —— 完整参数字符串（例如 `/skill-name Lecture01` → `Lecture01`）【已实测生效】
- `` !`command` `` —— 技能加载时注入命令输出【未实测，谨慎使用】

上游的 `${CLAUDE_SKILL_DIR}`、`${CLAUDE_SESSION_ID}`、`$0`/`$1`/`$N` 在 WorkBuddy 里没有对应物，别用。

## 只读约束

`allowed-tools` 只做「预先批准」，不做「限制」：列出的工具免询问，没列出的仍可按你的权限设置调用。WorkBuddy **没有**技能级工具黑名单（`disallowed-tools` 不生效）。要让一个技能「只读」，只有两条软约束：`allowed-tools` 只列只读工具（`Read`/`Grep`/`Glob`）+ 正文声明「不修改被审文件」。这两条是意图声明、不是硬保证——真正要紧的写入保护靠项目级 `permissions.deny` 规则或 PreToolUse 钩子（见 `permission-check`）。
