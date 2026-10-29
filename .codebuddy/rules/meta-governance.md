---
paths:
  - "CODEBUDDY.md"
  - "MEMORY.md"
  - "README.md"
  - "CHANGELOG.md"
  - "TROUBLESHOOTING.md"
  - "CITATION.cff"
  - "guide/**"
  - "docs/**"
  - "templates/**"
  - ".codebuddy/**"
  - ".github/**"
  - "scripts/*.sh"
  - "scripts/*.py"
---

# 元治理：本仓库的双重身份

**本仓库既是一个在用的项目，也是给别人用的模板。**

理解这个区别，对决定提交什么、记录什么、把经验存到哪里都很关键。

---

## 两个身份

### 身份一：在用项目
- 我们持续开发讲义幻灯片、指南与文档
- 我们积累针对自身环境与工作流的经验
- 我们试验新功能，迭代基础设施
- 我们有机构语境（Emory、计量经济学、特定工具）

### 身份二：公开模板
- 别人 fork 本仓库来启动自己的学术工作流
- 他们的领域不同（生物学、物理学、计算机，不只是经济学）
- 他们用的工具不同（纯 LaTeX、纯 R、Python、Jupyter）
- 他们需要通用模式，而不是我们的具体决定

---

## 决策框架

创建或修改内容时，先问：

### 「这是通用的还是特定的？」

**通用（提交进仓库，对所有用户有帮助）：**
- 工作流模式（先规格后计划、质量门禁、编排器）
- 设计原则（面向框架、渐进披露）
- 模板（需求规格、宪制治理、技能模板）
- 文档标准（同时更新 README 与指南）
- 随用户语境调整的规则（按路径作用域的规则）

**特定（留在本机，或写进 gitignore）：**
- 机器相关的路径（macOS 上的 `TEXINPUTS=../Preambles`）
- 工具版本（`Quarto 1.3.x vs 1.4.x`）
- 机构要求（Emory 学位论文格式）
- 个人偏好（本项目 90/100 的质量门禁）
- API 密钥、凭据、本地变通做法

### 「它是否规定了一种 owner 尚未审核过的方法？」

> **Owner 裁定，2026-08-23。**v2.5 对未经审核的倍差法内容的否决，
> **扩大到一般的实证因果方法**——断点回归、合成控制、工具变量、
> 事件研究，以及把匹配当作识别策略。在 owner 审核相关文字之前，
> 本仓库里的任何东西——技能、规则、代理、参考、模板——都不告诉用户
> *如何使用*这些方法中的任何一种。理由用 owner 的原话：避免在未经审核
> 的情况下对指南作出强断言，而 owner 现在还没准备好审核。

**仍然发布**（以下都不是规定）：

- **中性的分类法**——方法名作为类别清单（论文类型、学科卡片、期刊画像）。
- **期刊与领域内容的描述**——某个发表场合发表什么，而不是你该跑什么。
- **有条件的标准包指针**——「如果论文自身的设计要用那个包，就驱动它，绝不重新实现该估计量。」
- **对 owner 已发表工作的引用。**
- **明确拒绝裁断的立场**——「识别策略是否站得住，是 `/review-paper` 的问题。」
- **历史记录**——CHANGELOG 条目与 backlog 从不修改。`MEMORY.md` 里的一条教训可以用带日期的补记来*扩展*，也可以为了守住文件体积上限而**压缩或合并**，前提是这条教训、它的事故证据、它的日期在改动后仍然存在；绝不允许发生的是，一条教训悄悄丢掉了它当初付出代价才换来的东西。

**没有现行的签核就不发布：**跑哪些诊断或检验、核验哪些假设、
选哪个估计量、设定或调参、要求方法专属产物的审稿人与编辑人格、
以及逐条列举方法专属分叉或敏感性统计量的目录章节。某节被删掉
的地方，会在原位留一行说明——缺失应当是看得见的，
而不是神秘的。

这道门禁是 owner 对**当前文本的、带日期的现行签核**。签核附着于
它审过的内容，而不是附着于表面的名字。

---

## 记忆管理：两层系统

### MEMORY.md（根目录，已提交）

**用途：**对所有用户都有帮助的通用经验

**放什么：**
- 工作流改进：`[LEARN:workflow] Spec-then-plan reduces rework 30-50%`
- 设计原则：`[LEARN:design] Framework-oriented > prescriptive rules`
- 文档模式：`[LEARN:documentation] Update README+guide together`
- 质量标准：`[LEARN:quality] 80/90/95 thresholds work across domains`

**复查节奏：**每次重要会话之后（计划获批、功能实现）

**体积上限：**保持在 200 行以内**且**在 25KB 以内。

> **2026-08-21 更正。**这里原先写的是「留在 Claude 的系统提示里」。
> 本文件的加载方式**不是**那样：`CODEBUDDY.md` 只是用 markdown 链接指向 `MEMORY.md`，
> 并没有用 `@` 导入它，所以没有任何东西会把它自动放进系统提示——它是按需
> 读取的。两个后果：(1) 体积上限保护的是可读性，不是上下文预算；
> (2) `[LEARN]` 条目只有在文件真被读到的时候才进入会话。如果我们想要
> 文档里写的那种行为，就在 `CODEBUDDY.md` 里加 `@MEMORY.md`——但请注意，
> 这个文件已经超过了 25KB 这个尾部内容会被丢弃的阈值，得先做删减。
> **已在 v2.5.0（2026-08-23）解决：**`MEMORY.md` 保持只链接不导入，
> 上限靠删减来守住——发布过程中该文件已被压到 25KB 以下。

---

### 本机层：原生自动记忆（v2.5——取代 `personal-memory.md`）

**用途：**机器相关与用户相关的经验。

**现在住在哪里：**WorkBuddy 原生提供这项能力。它**默认开启**，写入
`~/.workbuddy/projects/<project>/memory/`——一个 `MEMORY.md` 索引，加上每条
记忆一个主题文件，各自标为 `user` / `feedback` / `project` / `reference`。
本机存放、永不提交、不参与转录清理，并记录一个 `modified` 时间戳，
让你看得出某条事实有多新。

**Owner 裁定（2026-08-21）：保持自动记忆开启。**两层的想法是对的；
手工搭的那套管线已经过时。`.codebuddy/state/personal-memory.md` 已**退役**——
如果你有旧版本留下的这一份，它仍可作为普通文件使用，但没有东西往里写，
`/promote-memory` 也不再读它。

**唯一值得知道的告诫：**自动记忆是一种*未记录的上下文输入*。它能在
复现者看不见的情况下影响一个会话。对于会产出**被报告的数字**的会话，
要么在分析日志里注明自动记忆当时是开着的，要么为那次会话关掉它
（`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`）。这是关于可审计性的判断取舍，
不是正确性缺陷——见 [`replication-protocol.md`](replication-protocol.md)。

**放什么：**
- 机器设置：`[LEARN:latex] XeLaTeX on macOS requires TEXINPUTS=../Preambles`
- 工具怪癖：`[LEARN:quarto] Version 1.4.x has nested div bug, use 1.3.x`
- 本地路径：`[LEARN:files] Bibliography at ~/Dropbox/References/main.bib`
- 个人工作流：`[LEARN:workflow] I prefer 90/100 for lecture slides, 80/100 for explorations`

**复查节奏：**按需（不必逼着自己形式化）

**体积上限：**自动记忆的 `MEMORY.md` 索引保持简短。WorkBuddy 会把它自动载入每个会话，而一个长的索引只有开头部分会被载入。每一行都要花上下文，还能不留痕迹地影响一个会话，所以细节留在主题文件里。

---

## 跨机器访问

### 场景：用户在多台机器上工作

**机器 A（办公室台式机）：**
- 克隆仓库 → 得到带有通用经验的 MEMORY.md ✓
- 得到全部基础设施（技能、代理、规则、模板）✓
- 得到最新的指南与文档 ✓
- 为台式机这套环境积累自己的原生自动记忆

**机器 B（笔记本）：**
- 克隆同一个仓库 → 得到同一份 MEMORY.md ✓
- 得到同样的基础设施 ✓
- 为笔记本这套环境积累**不同**的原生自动记忆（它按设计就是本机的）

**关键洞见：**通用模式通过 git 同步，个人模式留在本机（真有必要时手工拷贝）。

---

## 自食其用：照自己的指南办事

**我们必须遵守自己推荐给用户的模式。**

### 计划先行
✅ 要：对不简单的任务（>3 个文件、>1 小时、多步）进入计划模式
✅ 要：把计划存到 `quality_reports/plans/YYYY-MM-DD_description.md`
❌ 不要：为「快速修一下」跳过计划，结果变成几小时的任务

### 先规格后计划
✅ 要：为复杂/含糊的任务写需求规格
✅ 要：使用 MUST/SHOULD/MAY 框架，并标明清晰度状态
❌ 不要：需求还一团模糊就直接进计划

### 质量门禁
✅ 要：提交前跑质量打分
✅ 要：低于 80/100 的东西不发布
❌ 不要：没做质量核验就提交「半成品」代码

### 文档标准
✅ 要：加功能时同时更新 README 与指南
✅ 要：日期保持最新（frontmatter、「Last Updated」字段）
❌ 不要：让文档与实现脱节

### 上下文存活
✅ 要：会话结束后往 MEMORY.md 写 [LEARN] 条目
✅ 要：压缩之前把在用的计划存到磁盘
✅ 要：会话日志保持最新（最近 10 分钟）
❌ 不要：只依赖对话历史（它会被压缩）

---

## 模板维护原则

### 保持通用

**坏（太具体）：**
```markdown
# Beamer Compilation Rule
Always use XeLaTeX with TEXINPATHS=../Preambles for Emory slides.
```

**好（面向框架）：**
```markdown
# LaTeX Compilation Rule
Use project-specific TEXINPATHS if preambles are in separate directory.
Configure in CODEBUDDY.md for your setup.
```

### 例子要覆盖多个领域

**坏（单一用例）：**
```markdown
Example: Econometric panel data analysis
```

**好（多样用例）：**
```markdown
Examples:
- Econometrics: Panel regression with fixed effects
- Biology: Lab protocol validation
- Physics: Numerical simulation workflow
```

### 用模板，不用规定

**坏（说教式）：**
```markdown
Your bibliography MUST be named Bibliography_base.bib and live in root.
```

**好（带占位符的模板）：**
```markdown
Configure bibliography location in CODEBUDDY.md:
[YOUR_BIB_FILE] (e.g., Bibliography_base.bib, refs.bib, ../library.bib)
```

---

## 何时可以破例

### 模板可以展示具体例子

README 和指南这样写是可以的：
> 「这套工作流是为 Emory University 的 Econ 730 开发的……」

只要清楚这是其中一个例子，而不是必需条件。

### CODEBUDDY.md 可以有占位符

模板 CODEBUDDY.md 里有 `[YOUR PROJECT NAME]`、`[YOUR INSTITUTION]`——这是对的。用户自己填。

### 文档可以引用最初的使用场景

展示真实例子在教学上有价值：
> 「案例研究：6 次课、800+ 张幻灯片、Beamer + Quarto + R 复现」

这展示的是可能性，不是必需条件。

---

## 修订流程

随着本仓库演进，元治理可能需要更新。

**何时修订本文件：**
- 我们发现更好的办法区分通用与特定
- 跨机器工作流变了（例如 WorkBuddy 加了云同步）
- 记忆系统演进了（例如自动提取 [LEARN]）
- 用户反馈显示大家对「模板 vs 在用项目」感到困惑

**修订步骤：**
1. 在会话日志或计划里提出改动
2. 讨论影响（什么会坏？什么会变好？）
3. 更新本文件
4. 在 MEMORY.md 里用 [LEARN:meta-governance] 条目记录这次改动

---

## 速查表

| 内容类型 | 提交进仓库？ | 放在哪里 | 跨机器同步？ |
|--------------|----------------|---------------|----------------------|
| 工作流模式（通用） | ✅ 是 | MEMORY.md | ✅ 是（通过 git） |
| 机器相关设置 | ❌ 否 | 原生自动记忆（`~/.workbuddy/projects/<project>/memory/`） | ❌ 否（本机存放） |
| 模板（通用） | ✅ 是 | templates/ | ✅ 是 |
| 技能（通用） | ✅ 是 | .codebuddy/skills/ | ✅ 是 |
| 规则（按路径作用域，通用） | ✅ 是 | .codebuddy/rules/ | ✅ 是 |
| 代理（通用） | ✅ 是 | .codebuddy/agents/ | ✅ 是 |
| 钩子（通用行为） | ✅ 是 | .codebuddy/hooks/ | ✅ 是 |
| 会话日志 | ❌ 否（自 v2.0 起被 gitignore——这是 owner 的工作，不是模板内容；若某份日志记录了模板历史，可强制添加） | quality_reports/session_logs/ | ❌ 否 |
| 计划 | ❌ 否（自 v2.0 起被 gitignore，理由同上） | quality_reports/plans/ | ❌ 否 |
| 本地设置 | ❌ 否 | .codebuddy/settings.local.json | ❌ 否（已 gitignore） |
| 会话状态 | ❌ 否 | .codebuddy/state/ | ❌ 否（已 gitignore） |
| 构建产物 | ❌ 否 | .aux, .log, .synctex.gz | ❌ 否（已 gitignore） |

---

## 小结

**本仓库服务两位主人：**
1. 我们在用的项目（特定的、有语境的、演进的）
2. 给别人用的模板（通用的、面向框架的、稳定的）

**办法：**
- 提交对所有人都有帮助的通用模式（MEMORY.md、模板、基础设施）
- 把特定经验留在本机（原生自动记忆——本机存放，永不提交）
- 自食其用自己的工作流（计划先行、先规格后计划、质量门禁）
- 写文档时用多领域例子（不只是我们的用例）
- 每季度复查：把通用的模式提升上来，把特定的细化

**拿不准时：**问一句「一个 fork 本仓库来做实验室规程的生物学博士生，会从这条知识里受益吗？」会 → MEMORY.md。不会 → 原生自动记忆。
