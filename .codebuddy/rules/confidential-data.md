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

**有些数据永远不能离开它获批所在的那台机器，有些结果永远不能离开数据中心。**经济学家天天和受限数据打交道——Census FSRDC、IRS、行政登记数据、健康记录、专有企业面板、受 IRB 管辖的人类受试者数据。本规则是处理这类数据的一贯约定；它按路径作用域限定在数据目录与受限格式上，所以恰好在相关时加载。

这是一份**模板**——把占位阈值和提供方换成你数据使用协议的实际条款。

---

## 三条硬规则

1. **永不提交原始保密数据。**原始微观数据、标识符、提供方交付的文件都不该进 git——私有仓库也不行，一次也不行。`.gitignore` 必须覆盖 `data/raw/`、`data/restricted/`、含微观数据的 `*.dta`/`*.sav`，以及你的 DUA 点名的任何路径。只提交*代码*和*经披露审查放行的派生*产物。
2. **没有披露放行，任何东西都不出去。**基于受限数据做出的任何表格、图、系数或计数，在进入草稿、幻灯片、提交或邮件*之前*必须通过防披露审查。先用 [`/disclosure-check`](../skills/disclosure-check/SKILL.md) 预筛；数据提供方的正式审查仍是强制且最终的。
3. **访问权限按人、按协议授予。**没有 DUA 的合作者不能收到数据、标识符，或不合披露规则的产物。交接（[`/coauthor-brief`](../skills/coauthor-brief/SKILL.md)）传递的是*申请访问权限的说明*，绝不是数据。

## 让受限数据不进入模型

Claude 读到的任何东西都会被送到模型提供方，所以「永不离开本机」也包括模型的上下文。Claude 写的是*在*数据上运行的代码；它不读数据。

- **拒绝规则在每一种权限模式下都生效，包括 bypass。**为你的受限路径加上 `Read`/`Edit` 拒绝规则——可直接粘贴的块在 [TROUBLESHOOTING.md →「让受限数据不进入模型」](../../TROUBLESHOOTING.md#keep-restricted-data-off-the-model)。它们覆盖的是 Claude 的文件工具，不是每一条 shell 命令，所以它们是对本规则的补强，而不是替代。
- **外部采集工具会记录你的会话。**记忆与可观测性插件（例如 ai-memory、MemPalace、claude-mem、托管式追踪）会存下提示词，有些还会存工具输出和 shell 输出。在受限数据项目上，要么一个都不用，要么只用一个带显式白名单、且白名单排除这些路径的——并且查清它的存储落在哪里。
- **WorkBuddy 自己保留会话记录。**转录（包括逐字的工具输出）存放在 `~/.workbuddy/projects/<project>/`，被编辑文件的早期副本存放在 `~/.workbuddy/file-history/`，直到 WorkBuddy 清理为止（`cleanupPeriodDays`，默认 30 天；来自 Claude Desktop 或 Cowork 的会话不论多久都保留，除非设置了 `desktopSessionCleanupPeriodDays`）。有两处存储永不被清扫：你在 `~/.workbuddy/history.jsonl` 里键入和粘贴的提示词（大段粘贴还会落到 `~/.workbuddy/paste-cache/`），以及项目在 `~/.workbuddy/projects/<project>/memory/` 里的自动记忆。如果受限内容进过某个会话，不要对它用 `--resume` 或 `/checkpoint`：执行 `claude project purge <path>`（**上游命令**，本平台无对应机制；先用 `--dry-run` 预览），它会删掉该项目的转录、文件历史、自动记忆，以及 `history.jsonl` 里的相关行；然后你还要自己清掉 `paste-cache/` 和会话草稿区，这两处它不碰。你的数据使用协议里的销毁条款覆盖上述所有副本。
- **外部模型咨询会上传你附上的文件。**[`/oracle-review`](../skills/oracle-review/SKILL.md) 把你附上的文件发到另一家厂商——你自己的论文和代码可以发；你替期刊或资助方评审的稿件或申请书不行，未通过披露审查的受限微观数据或产物也不行。

## 防披露（简版）

你的提供方所执行的阈值——把它们写进 `/disclosure-check` 的配置：

- **最小单元格计数**（例如压制任何 n < 10 的单元格；FSRDC 与 IRS 各不相同——用你自己那套）。
- **主导性 / 集中度**（针对机构数据的 p-percent 规则与 (n,k) 规则）。
- **互补压制**（压制一个单元格可能通过行/列合计泄露——把互补单元格一并压制）。
- **不给精确极值，不给未取整的敏感统计量，不给小群体标识符，不给细粒度地理。**

当一条数值断言建立在受限数据上时，它的护照条目（[`replication-protocol.md`](replication-protocol.md)）应注明披露状态，复现包（[`/replication-package`](../skills/replication-package/SKILL.md)）只存入已放行的产物，加上数据的*访问说明*——绝不是数据本身（这正是 AEA Data Editor 的「受限数据」存档路径）。

## 人类受试者 / IRB

如果数据涉及人类受试者：在项目规格里记录 IRB 方案编号、获批用途、以及任何知情同意的限制。不要分析超出获批范围的内容。[`/data-management-plan`](../skills/data-management-plan/SKILL.md) 会记录存储、保留与销毁条款。

## 多作者 git 拓扑（受限数据安全的协作方式）

- **每位作者一条特性分支**，通过 PR 合并——与模板其余部分同一套流程；没有作者强推共享历史（[`git-guardrails`](../hooks/git-guardrails.py) 钩子会拦下 `--force` 和 `git add -A`，后者正是原始数据漏进提交的常见途径）。
- **`MEMORY.md` 通过 git 同步；原生自动记忆（`~/.workbuddy/projects/<project>/memory/`）留在本机**（`meta-governance.md`）。机器相关的受限数据*路径*放在原生自动记忆里，永远不放进已提交的文件。
- 加入受限数据项目的合作者拿到的是 [`/coauthor-brief`](../skills/coauthor-brief/SKILL.md)，里面有环境搭建（[`/capture-environment`](../skills/capture-environment/SKILL.md) 的 lockfile）和**申请访问的步骤**，而不是一堆数据。
- 在受限目录里开启严格的路径泄露防护：`CLAUDE_STRICT_PATHS=1` 让 `git-guardrails` 对代码里硬编码的机器路径*拒绝*（不只是警告）。

## 交叉引用

- [`/disclosure-check`](../skills/disclosure-check/SKILL.md) —— 按这些阈值预筛产物。
- [`/data-management-plan`](../skills/data-management-plan/SKILL.md) —— 本约定面向资助方的版本。
- [`/replication-package`](../skills/replication-package/SKILL.md) —— 受限数据存档路径（已放行的产物 + 访问说明）。
- [`.codebuddy/rules/replication-protocol.md`](replication-protocol.md) —— 护照条目注明披露状态。
- [`.codebuddy/rules/meta-governance.md`](meta-governance.md) —— 本规则所依托的「已提交 vs 本机」两层模型。
