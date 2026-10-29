# 应用：审计本仓库自身的基础设施

`SKILL.md` 里的通用方法，用在模板自身——技能、代理、规则、钩子、脚本与文档。当审计目标是仓库而不是一篇论文时，读这一份。

对整个仓库跑一次全面的一致性审计，修好所有发现的问题，循环到干净为止。

## 何时使用

- 大范围改动之后（新增技能、规则、钩子、指南修改）
- 发布或大提交之前
- 用户要求 "find inconsistencies"、"audit" 或 "check everything" 时

## 工作流

### PHASE 0：机械检查（最先跑，便宜，确定性）

在派出代理之前，先跑完整的机械检查组，然后单独跑技能完整性门禁以看逐项细节：

```bash
./scripts/backtest.sh
python scripts/check-skill-integrity.py --verbose   # backtest gate 2, verbose
```

`check-skill-integrity.py` 能抓住基于代理的审计历来漏掉的五类 bug：

1. frontmatter 的 `allowed-tools` ↔ 正文工具调用的一致性（例如正文里派发了 `Task`，而 `allowed-tools` 里没有 `Task`——v1.7.0 PR #92 的那次漏检）。
2. `argument-hint` ↔ 正文参数的一致性（参数写了但没声明，或反之）。
3. 内部 markdown 锚点可解析（没有断掉的 `[text](path#anchor)` 链接——PR #87 上 `#category-11-numerical-discipline` 的那次漏检）。
4. 规则 `paths:` ↔ 技能实现的一致性（规则声称某技能遵循某协议，而技能正文一个协议关键词都没有——PR #92 上 `/interview-me` 的那次漏检）。
5. 规则关键词注册表的完整性（检查 4 只看得到登记在 `RULE_KEYWORDS` 里的规则，所以任何把自己限定到 `.codebuddy/skills/` 的规则都必须登记，或给出关键词，或显式写 `[]` 并说明为何无法做关键词检查）。

若 PHASE 0 报出 P0 或 P1 发现，先修（若属误报就调正则），**再**启动那 4 个代理。对这些类别，机械层比代理提示词更便宜也更精确。

### PHASE 1：启动 4 个并行审计代理

用 `Agent` 加 `subagent_type=general-purpose` 同时启动这 4 个代理。每个代理的提示词**必须**要求它读 `.codebuddy/references/audit-pet-peeves.md`，并在报告干净之前逐类显式检查。那份 pet-peeves 文件是审查机器人抓到的漂移模式的活目录；每个 PR 都在往里加。

#### Agent 1：指南内容准确性
关注：`guide/workflow-guide.qmd`
- 所有数值断言与现实一致（技能数、代理数、规则数、钩子数）
- 提到的所有文件路径确实存在于磁盘上
- 所有技能/代理/规则名与实际目录名一致
- 代码示例语法正确
- 交叉引用与锚点可解析
- 没有上一版本遗留的过期计数

#### Agent 2：可执行代码质量
关注：仓库里**全部**可执行代码——`.codebuddy/hooks/*.py`、`.codebuddy/hooks/*.sh`、`scripts/*.py`、`scripts/*.sh`、`.codebuddy/scripts/*.sh`、`.githooks/pre-commit`。不只是 `.codebuddy/hooks/`——PR #93 在 `scripts/` 下新增代码时，原先较窄的范围意味着 Copilot + Codex 抓住了 5 个审计漏掉的 bug。

钩子专属检查（Stop/PreToolUse/SessionStart 协议、`CODEBUDDY_PROJECT_DIR` 的用法、哈希长度一致性）只适用于 `.codebuddy/hooks/`。以下各项适用于全部可执行代码：

- 管理状态的任何东西里都不再残留 `/tmp/` 用法（应使用 `~/.workbuddy/sessions/`）
- 哈希长度一致（所有钩子统一 `[:8]`）[仅钩子]
- 恰当的错误处理——凡 docstring 承诺之处，就落实 **fail-open 模式**（顶层 `try/except` 配 `sys.exit(0)`）。若脚本被承诺对损坏文件 fail-open，Python 的 `read_text()` 必须捕 `UnicodeError`（不只是 `OSError`）。Bash 里只有 `set -u` 而没有 `set -e` 或显式的命令后检查，**不能**抓住命令失败——去核实。
- **docstring 声称 ↔ 实现的一致性。** 若某函数的 docstring 描述"双向一致"/"fail-open"/"在 X 时退出 1"，实现必须对得上。常见漂移：声称是双向契约却只实现一个方向；退出码文档写一套、实际返回另一套。
- **配置映射的条目指向活目标。** 关键词字典、路径映射与规则注册表不应含死条目（例如不存在的规则文件、脚本实际并不读取的字段）。死条目会误导维护者。
- JSON 输入/输出的正确性（输入走 stdin，输出走 stdout/stderr）[仅钩子]
- 退出码正确性。阻断协议按钩子事件不同：
  - **Stop：**（a）**exit 2 + 原因写到 stderr**——旧式，仍受支持；（b）**exit 0 + stdout 上输出 JSON `{"decision": "block", "reason": "..."}`**——现代式；`log-reminder.py` 用的就是这个，工作正常
  - **PreToolUse：**（a）**exit 2 + 原因写到 stderr**——旧式，仍受支持；（b）**exit 0 + stdout 上输出 JSON `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`**——现代式；`git-guardrails.py` 与 `root-of-trust-guard.py` 用的就是它。在 PreToolUse 钩子上写顶层 `{"decision": "block"}` 是被弃用的形制，不是现代形制
  - 非阻断钩子总是 exit 0。在 PreCompact 上，exit 2 会**阻断压缩**——只有阻断本身就是目的时才用它；纯 stdout 会进调试日志，所以面向用户的提示要以 JSON `systemMessage` 发出，诊断信息走 stderr
- `from __future__ import annotations` 以兼容 Python 3.8+
- 钩子输入 schema 的字段名正确（SessionStart 用 `source` 而不是 `type`）

#### Agent 3：技能与规则一致性
关注：`.codebuddy/skills/*/SKILL.md` 与 `.codebuddy/rules/*.md`
- 所有文件里的 YAML frontmatter 合法
- `disable-model-invocation: true` 只出现在用户主动调用的技能上（有副作用、运行时间长或需要交互）——并且没有别的技能正文会*调用*这样的技能（它做不到；它必须 Read 那份 `SKILL.md` 并照做）
- `allowed-tools` 的取值合理
- **`allowed-tools` 实际覆盖技能正文调用的每一个工具。** 对技能 Steps / Phases / Workflow 正文里提到的每一次 `Agent` 派生、`Bash` 命令、`Write`/`Edit` 调用，核实该工具出现在 `allowed-tools` 数组里。常见漏法：技能正文说"用 `Agent` 工具以 `context=fork` 派生 `agent-X`"，而 `allowed-tools` 里没有 `Agent`（别名 `Task`）——运行期权限报错或静默绕过。Codex/Copilot 在 PR #92 上点出后抓到的就是这一类（4 个技能在 Post-Flight 段承诺了 `Task`，而 4 个里有 3 个没有 `Task` 权限）。
- **规则 `paths:` 的范围与技能实现相符。** 若规则 X 在 `paths:` 里列了技能 Y，核实技能 Y 是否真的实现了规则 X 强制的协议。一条声称某技能遵循某协议的规则，在技能并不遵循时毫无意义。
- 规则 `paths:` 引用的目录存在
- 规则之间没有矛盾
- README.md 的技能表与技能目录 1:1 对应（`check-surface-sync.py` 强制），且 CODEBUDDY.md 快速索引里点到的每个技能都存在
- `.codebuddy/rules/*.md` 与指南（`guide/workflow-guide.qmd`）里引用的所有模板都存在于 `templates/`

#### Agent 4：跨文档一致性
关注：`README.md`、`docs/index.html`、`docs/workflow-guide.html`
- 所有功能计数在 3 份文档之间一致
- 所有链接指向有效目标
- 许可证段落与 LICENSE 文件一致
- 目录树与实际结构一致
- 没有上一版本遗留的过期计数

### PHASE 2：分诊发现

给每条发现归类：
- **真 bug**：立即修
- **误报**：丢弃（记下它为何是误报，供后续轮次参考）

常见需留意的误报：
- `:::` div 里的 Quarto callout `## Title`——这是标准语法，**不是**标题 bug
- `allowed-tools` 的 linter 警告——已知 linter bug（Claude Code issue #25380），该字段**是**合法的
- 旧会话日志里的计数——那是历史记录，不是面向用户的文档
- `CHANGELOG.md` 里过去版本标题下的计数——那是快照；**不要**改
- `log-reminder.py` 输出 `{"decision": "block"}` 配 `sys.exit(0)`——这**就是** WorkBuddy 的 Stop 钩子阻断协议，**不是** bug

**专门盯计数漂移：把每一种措辞变体都搜一遍。** 常见的失手方式是：只对一种措辞做 `replace_all`（例如 `"26 skills"`），漏掉同一仓库里的兄弟措辞。检查计数时，下列**全部**都要 grep：
- `"N skills"`、`"N skill "`（带空格）
- `"N slash commands"`
- `"N specialized"`（如 "N specialized agents"）
- `"template's N"`（散文里的非正式计数）
- 逗号/连词：`"skills,"` 与 `"skills, and"` 在 `replace_all` 眼里是两个不同字符串
宣布干净之前，先确认整个树里对**旧**数字的匹配为零。

### PHASE 3：修好所有问题

尽可能并行地施加修复。对每一处修复：
1. 先读文件（Edit 工具要求）
2. 施加修复
3. 验证修复（grep 过期值、检查语法）

### PHASE 4：指南有改动则重新渲染

若 `guide/workflow-guide.qmd` 被改过：
```bash
quarto render guide/workflow-guide.qmd
cp guide/workflow-guide.html docs/workflow-guide.html
./scripts/stamp-render.sh   # re-stamp .render-stamp, or the staleness gate fails
```

### PHASE 5：空轮收敛，或宣布干净

修完之后，另起一整套新的 4 个代理去验证。这就是**空轮收敛**（loop-until-dry）原语（[`orchestrator-protocol.md`](../../../rules/orchestrator-protocol.md)）：
- 在**连续 2 轮**都浮出**0 个新真问题**（按 file+issue 去重）之后**收敛**——宣布干净并报告摘要。
- 若发现新问题 → 修好后再循环。
- **兜底上限：5 轮**，为不收敛的审计封顶（防止无限循环）；一条在轮次 N 与 N+2 都存活的发现升级给用户，而不是再打一次补丁（[`summary-parity.md`](../../../rules/summary-parity.md)）。

## 过往审计的关键教训

这些是跨 7 轮真被抓到的 bug——专门查这些：

| bug 模式 | 去哪儿查 | 出过错 |
|-------------|---------------|-----------------|
| 过期计数（"19 skills" → "21"） | 指南、README、落地页 | 加了技能却没更新所有提及处 |
| 钩子退出码 | 所有 Python 钩子 | PreCompact 里 exit 2 会静默丢弃 stdout |
| 钩子字段名 | post-compact-restore.py | SessionStart 用 `source`，不是 `type` |
| 状态存放在 /tmp/ | 所有 Python 钩子 | 应使用 `~/.workbuddy/sessions/<hash>/` |
| 哈希长度不一致 | 所有 Python 钩子 | 有的用 `[:12]`，有的用 `[:8]` |
| 缺少 fail-open | Python 钩子 `__main__` | 未捕获异常 → exit 1 → 行为令人困惑 |
| Python 3.10+ 语法 | 像 `dict | None` 的类型注解 | 需要 `from __future__ import annotations` |
| 缺失目录 | quality_reports/specs/ | 规则里引用了却从未创建 |
| 常开规则清单 | 指南 + README | meta-governance 被从清单里漏掉 |
| 仅 macOS 可用的命令 | 技能、规则 | `open` 没有 `xdg-open` 兜底 |
| 过期的钩子引用 | 规则、指南、CHANGELOG、settings.json | 已删除的钩子在某处仍被提到 |

## 输出格式

每轮之后，报告：

```
## Round N Audit Results

### Issues Found: X genuine, Y false alarms

| # | Severity | File | Issue | Status |
|---|----------|------|-------|--------|
| 1 | Critical | file.py:42 | Description | Fixed |
| 2 | Medium | file.qmd:100 | Description | Fixed |

### Verification
- [ ] No stale counts (grep confirms)
- [ ] All hooks have fail-open + future annotations
- [ ] Guide renders successfully
- [ ] docs/ updated

### Result: [CLEAN | N issues remaining]
```

## 发现要经过验证，而不只是写下来（v2.5）

本技能的审查者按 [`finding-schema.json`](../../../references/finding-schema.json) 里的机器校验契约产出发现。报告是 JSON **数组**。

**在花审查力气之前，先冒烟测一遍夹具**——一次扇出了一堆审查者、最后却写不出一份合法报告的运行，把整趟都浪费了：

```bash
echo '[]' | python scripts/validate-findings.py
```

审查代理是只读的，所以**由本技能来写文件**。对每个审查者的最终回复：把散文报告存到本技能为该审查者规定的报告路径，把它结尾的 `json` 围栏块复制到草稿区文件，并在校验时补齐 id：

```bash
python scripts/validate-findings.py --fill-ids block.json > <report>.json.tmp \
  && mv <report>.json.tmp <report>.json || rm -f <report>.json.tmp   # exit 0 required; a failed run keeps no file
python scripts/validate-findings.py --check-quotes <report>.json   # each quote must be the file's own text (orchestration-schemas.md §1)
```

没返回 `json` 块、或返回的块通不过校验的审查者，等于没有审查：带上校验器的报错文本重新派发一次，然后把这个透镜报告为缺失，而不是在没有它的情况下继续归并。

契约强制了什么，为什么：

- **`rule`**——所违反的成文规则或标准。不引任何规则的发现只是意见，而意见不给提交设门。
- **`failing_case`**——让该主张崩掉的具体配置，或确切缺失的那条假设。*"This could be clearer"* 通不过校验。
- **`id = sha1("<file>:<line>:<locus>")`**——确定性的，所以跨轮去重是精确的，"两振出局"规则可机器检查而不是靠肉眼。
- **`mechanical`**——只有不会改变结果的修复（错字、交叉引用、格式、标签）才为 `true`。对估计目标、假设、设定、推断程序、样本定义或报告措辞，**永远不是**：那些要退回研究者。

在验证*之前*先套用 [`orchestration-schemas.md` §7](../../../references/orchestration-schemas.md) 里的**逐透镜证据负担**与**「不算数」过滤器**，让已知误报根本到不了裁判者手上。验证这一遍是**偏向反驳**的，并由它设置每条发现的 `verdict`（审查者留空不填）：只有 `verdict: "confirmed"` 的发现能出货；它无法落地的任何发现都被丢弃，而不是降级为警告。
