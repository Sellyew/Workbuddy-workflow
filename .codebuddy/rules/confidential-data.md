---
paths:
  - "data/**"
  - "**/*.dta"
  - "**/*.sav"
  - "**/raw/**"
  - "**/restricted/**"
  - "**/confidential/**"
---

# 保密与受限数据规程

**有些数据永远不能离开获批使用的机器，有些结果永远不能离开数据中心。**经济学家经常处理受限数据，包括 Census FSRDC、IRS、行政登记数据、健康记录、专有企业面板和受 IRB 管辖的人类受试者数据。本规则统一约束这类数据的处理，并按路径限定于数据目录和受限格式，因此只在相关时加载。

这是一份**模板**。请用数据使用协议的实际条款替换占位阈值和提供方。

---

## 三条硬规则

1. **永不提交原始保密数据。**原始微观数据、标识符和提供方交付的文件都不得进入 git，私有仓库也不行，一次也不行。`.gitignore` 必须覆盖 `data/raw/`、`data/restricted/`、含微观数据的 `*.dta`/`*.sav`，以及 DUA 点名的任何路径。只能提交*代码*和*经披露审查放行的派生*产物。
2. **没有披露放行，任何东西都不出去。**基于受限数据生成的任何表格、图、系数或计数，在进入草稿、幻灯片、提交或邮件*之前*，都必须通过防披露审查。先用 [`/disclosure-check`](../skills/disclosure-check/SKILL.md) 预筛，但数据提供方的正式审查仍然强制，并且是最终审查。
3. **访问权限按人、按协议授予。**没有 DUA 的合作者不得接收数据、标识符或不符合披露规则的产物。交接时，[`/coauthor-brief`](../skills/coauthor-brief/SKILL.md) 只传递*申请访问权限的说明*，绝不传递数据。

## 让受限数据不进入模型

WorkBuddy 读取的任何内容都会发送给模型提供方，所以「永不离开本机」也包括不得进入模型上下文。WorkBuddy 只编写*在*数据上运行的代码，不读取数据。

- **拒绝规则在每一种权限模式下都生效，包括 bypass。**为受限路径配置 `Read`/`Edit` 拒绝规则，可直接粘贴的块见 [TROUBLESHOOTING.md →「让受限数据不进入模型」](../../TROUBLESHOOTING.md#让受限数据不进入模型)。这些规则覆盖 WorkBuddy 的文件工具，但不覆盖每一条 shell 命令，因此只能补强本规则，不能替代本规则。
- **外部采集工具会记录会话。**记忆与可观测性插件，例如 ai-memory、MemPalace、claude-mem、托管式追踪，会保存提示词，有些还保存工具输出和 shell 输出。处理受限数据项目时，要么完全不使用这些工具，要么只使用带显式白名单的工具，并确保白名单排除这些路径，同时查清数据存储位置。
- **WorkBuddy 自己保留会话记录。**转录包括逐字的工具输出，保存在 `~/.workbuddy/projects/<project>/`；被编辑文件的早期副本保存在 `~/.workbuddy/file-history/`，直到 WorkBuddy 清理为止。清理由 `cleanupPeriodDays` 控制，默认 30 天；来自 Claude Desktop 或 Cowork 的会话则没有保留时限，除非设置 `desktopSessionCleanupPeriodDays`。有两处存储永不清扫：一是你在 `~/.workbuddy/history.jsonl` 中键入和粘贴的提示词，大段粘贴还会进入 `~/.workbuddy/paste-cache/`；二是项目在 `~/.workbuddy/projects/<project>/memory/` 中的自动记忆。如果受限内容进入过某个会话，不要续接该会话，因为续接会把旧转录重新读入上下文，也不要对它执行 `/checkpoint`。应执行 `claude project purge <path>`，这是**上游命令**，本平台没有对应机制；先用 `--dry-run` 预览。该命令会删除项目转录、文件历史、自动记忆以及 `history.jsonl` 中的相关行，但不会处理 `paste-cache/` 和会话草稿区，这两处必须自行清理。数据使用协议中的销毁条款覆盖上述所有副本。
- **外部模型咨询会上传附加文件。**[`/oracle-review`](../skills/oracle-review/SKILL.md) 会把附加文件发送给另一家厂商。自己的论文和代码可以发送；替期刊或资助方评审的稿件或申请书不得发送；未通过披露审查的受限微观数据或产物也不得发送。

## 防披露（简版）

把提供方执行的阈值写入 `/disclosure-check` 的配置：

- **最小单元格计数**：例如压制任何 n < 10 的单元格。FSRDC 与 IRS 的要求不同，必须使用自己的那套要求。
- **主导性 / 集中度**：针对机构数据的 p-percent 规则与 (n,k) 规则。
- **互补压制**：压制一个单元格后，行/列合计仍可能泄露信息，因此还要一并压制互补单元格。
- **不给精确极值，不给未取整的敏感统计量，不给小群体标识符，不给细粒度地理。**

数值断言基于受限数据时，其护照条目（[`replication-protocol.md`](replication-protocol.md)）应注明披露状态。复现包（[`/replication-package`](../skills/replication-package/SKILL.md)）只保存已放行的产物和数据*访问说明*，绝不保存数据本身；这正是 AEA Data Editor 的「受限数据」存档路径。

## 人类受试者 / IRB

数据涉及人类受试者时，在项目规格中记录 IRB 方案编号、获批用途和任何知情同意限制，不得分析超出获批范围的内容。[`/data-management-plan`](../skills/data-management-plan/SKILL.md) 会记录存储、保留和销毁条款。

## 多作者 git 拓扑（受限数据安全的协作方式）

- **每位作者使用一条特性分支**，通过 PR 合并，与模板其余部分采用同一流程。任何作者都不得强推共享历史。[`git-guardrails`](../hooks/git-guardrails.py) 钩子会拦截 `--force` 和 `git add -A`，后者正是原始数据误入提交的常见途径。
- **`MEMORY.md` 通过 git 同步；原生自动记忆（`~/.workbuddy/projects/<project>/memory/`）留在本机**，见 `meta-governance.md`。机器相关的受限数据*路径*放在原生自动记忆中，永远不得放入已提交文件。
- 加入受限数据项目的合作者只获得 [`/coauthor-brief`](../skills/coauthor-brief/SKILL.md)，其中包括环境搭建说明和**申请访问的步骤**，环境搭建使用 [`/capture-environment`](../skills/capture-environment/SKILL.md) 的 lockfile，不包括任何数据。
- 在受限目录中启用严格的路径泄露防护：`CLAUDE_STRICT_PATHS=1` 让 `git-guardrails` 对代码中硬编码的机器路径*拒绝*，而不只是警告。

## 交叉引用

- [`/disclosure-check`](../skills/disclosure-check/SKILL.md)：按这些阈值预筛产物。
- [`/data-management-plan`](../skills/data-management-plan/SKILL.md)：本约定面向资助方的版本。
- [`/replication-package`](../skills/replication-package/SKILL.md)：受限数据存档路径，只含已放行产物和访问说明。
- [`.codebuddy/rules/replication-protocol.md`](replication-protocol.md)：护照条目注明披露状态。
- [`.codebuddy/rules/meta-governance.md`](meta-governance.md)：本规则依托的「已提交 vs 本机」两层模型。
