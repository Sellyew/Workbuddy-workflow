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

**本仓库是 Sellyew 正在维护和使用的非官方 WorkBuddy 中文移植，也是供他人 fork 的公开模板。**

只有分清这两种身份，才能正确决定要提交什么、记录什么，以及把经验保存在哪里。

---

## 两个身份

### 身份一：Sellyew 正在维护和使用的移植项目
- Sellyew 在这里翻译和校订文档，适配 WorkBuddy，并改进日常使用的基础设施
- 在日常使用中试验新功能，积累与自己的环境和工作流有关的经验
- 记录移植决策，把本机状态留在 `.workbuddy/memory/`；只把通用改进整理进公开模板
- 涉及 Sant'Anna、Emory 和上游项目的内容只作历史背景，不写成 Sellyew 的亲身经历

### 身份二：公开模板
- 采用者可以 fork 本仓库，用它启动自己的学术工作流
- 他们可能来自不同领域（生物学、物理学、计算机，不只是经济学）
- 也可能使用不同工具（纯 LaTeX、纯 R、Python、Jupyter）
- 他们需要通用模式，不必照搬 Sellyew、上游项目或其他采用者的具体决定

---

## 决策框架

创建或修改内容时，先问：

### 「这是通用的还是特定的？」

**通用内容应提交到仓库，因为它能帮助所有用户：**
- 工作流模式（任务要求先于计划、质量门禁、编排器）
- 设计原则（面向框架、渐进披露）
- 模板（需求说明、宪制治理、技能模板）
- 文档标准（同时更新 README 与指南）
- 随用户语境调整的规则（按路径作用域的规则）

**特定内容应留在本机，或写入 gitignore：**
- 本机工具链的安装路径（TeX Live / Quarto 的 bin 目录在哪）
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

**以下内容仍可发布，因为它们不构成方法规定：**

- **中性的分类法**——方法名作为类别清单（论文类型、学科卡片、期刊画像）。
- **期刊与领域内容的描述**——某个发表场合发表什么，而不是你该跑什么。
- **有条件的标准包指针**——「如果论文自身的设计要用那个包，就驱动它，绝不重新实现该估计量。」
- **对 owner 已发表工作的引用。**
- **明确拒绝裁断的立场**——「识别策略是否站得住，是 `/review-paper` 的问题。」
- **历史与当前公开文件**——不改写历史事实；CHANGELOG、backlog 与 MEMORY.md 的当前公开内容可以裁剪、压缩或合并，原文留在 git tags/history。公开 MEMORY.md 保留通用理由、适用边界和当前可复核证据即可；单次事故、个人裁定和本机细节留在 git 历史或本机，不是公开条目的必需组成。

**没有现行签核，就不得发布以下内容：**运行哪些诊断或检验、核验哪些假设、选择哪个估计量、如何设定或调参、要求方法专属产物的审稿人与编辑人格，以及逐条列举方法专属分叉或敏感性统计量的目录章节。删除某节后，必须在原位留一行说明，让读者清楚看到缺失内容，而不是无从得知这里曾有内容。

这道门禁要求 owner 对**当前文本给出带日期的现行签核**。签核只适用于实际审过的内容，不能仅凭表面名称沿用。

---

## 记忆管理：三层系统

### MEMORY.md（根目录，人工筛选、可提交）

**用途：**保存经人工筛选、能帮助所有用户的通用经验。

**放什么：**
- 工作流改进：`[LEARN:workflow] Requirements-then-plan reduces rework 30-50%`
- 设计原则：`[LEARN:design] Framework-oriented > prescriptive rules`
- 文档模式：`[LEARN:documentation] Update README+guide together`
- 质量标准：`[LEARN:quality] 80/90/95 thresholds work across domains`

**复查节奏：**每次重要会话结束后复查，例如计划获批或功能实现之后。

**体积上限：**同时控制在 200 行以内并严格小于 25KB。

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

**用途：**保存与机器和用户有关的经验。

**目前存放在哪里：**WorkBuddy 原生提供这项能力，并**默认开启**。记忆写入 `~/.workbuddy/projects/<project>/memory/`，其中包括一个 `MEMORY.md` 索引和每条记忆各自的主题文件，分别标为 `user` / `feedback` / `project` / `reference`。这些记忆只保存在本机，永不提交，也不参与转录清理。系统会记录 `modified` 时间戳，便于判断事实的新旧。

**Owner 裁定（2026-08-21）：保持自动记忆开启。**通用经验与本机记录分离的想法是对的；
手工搭的那套管线已经过时。`.codebuddy/state/personal-memory.md` 已**退役**——
如果你有旧版本留下的这一份，它仍可作为普通文件使用，但没有东西往里写，
`/promote-memory` 也不再读它。

**唯一需要注意的是：**自动记忆属于*未记录的上下文输入*，可能在复现者看不见的情况下影响会话。对于会生成**拟报告数字**的会话，必须在分析日志中注明自动记忆当时处于开启状态。这是可审计性方面的取舍，不是正确性缺陷，详见 [`replication-protocol.md`](replication-protocol.md)。

**放什么：**
- 机器设置：`[LEARN:files] TeX Live 装在这里，PATH 要加上它的 bin 目录`
- 工具怪癖：`[LEARN:quarto] Version 1.4.x has nested div bug, use 1.3.x`
- 本地路径：`[LEARN:files] Bibliography at ~/Dropbox/References/main.bib`
- 个人工作流：`[LEARN:workflow] I prefer 90/100 for lecture slides, 80/100 for explorations`

**复查节奏：**按需复查，不必强行形式化。

**体积上限：**自动记忆的 `MEMORY.md` 索引应保持简短。WorkBuddy 会在每个会话中自动加载它，但索引过长时只加载开头部分。每一行都会占用上下文，还可能在不留痕迹的情况下影响会话，所以细节应放在主题文件中。

---

### 项目层：`.workbuddy/memory/`（本仓库工作日志与本机状态）

**用途：**保存这个工作副本的按日工作日志，例如 `YYYY-MM-DD.md`，以及本机状态。它记录本仓库正在进行的工作，既不是用户级原生自动记忆，也不是人工筛选后的通用经验。

整个 `.workbuddy/` 都已加入 gitignore。这些文件**保留在本机、不要删除、不要提交**，不会随 fork 或普通 `git clone` 复制。需要跨项目复用的经验，应先由人工判断，再提升到根目录的 `MEMORY.md`，不能直接把整份日志当作通用经验发布。

---

## 跨机器访问

### 场景：用户在多台机器上工作

**机器 A（办公室台式机）：**
- 克隆仓库后，获得包含通用经验的 MEMORY.md ✓
- 获得全部基础设施（技能、代理、规则、模板）✓
- 获得最新的指南和文档 ✓
- 针对台式机环境积累自己的原生自动记忆和 `.workbuddy/memory/` 工作日志

**机器 B（笔记本）：**
- 克隆同一仓库后，获得同一份 MEMORY.md ✓
- 获得同样的基础设施 ✓
- 针对笔记本环境积累**不同**的原生自动记忆和项目工作日志，两者按设计都保存在本机

**关键在于：**通用模式通过 git 同步，原生自动记忆和项目工作日志则留在本机，确有必要时再手工复制。

---

## 自食其用：照自己的指南办事

**我们必须遵守自己向用户推荐的模式。**

### 计划先行
✅ 要：遇到不简单的任务（>3 个文件、>1 小时、多步）时进入计划模式
✅ 要：把计划保存到 `quality_reports/plans/YYYY-MM-DD_description.md`
❌ 不要：以「快速修一下」为由跳过计划，最后却把任务做成几个小时

### 任务要求先于计划
✅ 要：为复杂或含糊的任务编写需求说明，把任务要求写清楚
✅ 要：使用 MUST/SHOULD/MAY 框架，并标明清晰度状态
❌ 不要：需求仍然模糊就直接进入计划

### 质量门禁
✅ 要：提交前运行质量打分
✅ 要：不发布低于 80/100 的内容
❌ 不要：未经质量核验就提交「半成品」代码

### 文档标准
✅ 要：添加功能时同步更新 README 和指南
✅ 要：及时更新日期（frontmatter、「Last Updated」字段）
❌ 不要：让文档与实现脱节

### 上下文存活
✅ 要：会话结束后记录 [LEARN] 候选，通用条目经人工筛选后写入根目录 MEMORY.md
✅ 要：压缩前把正在使用的计划保存到磁盘
✅ 要：及时更新会话日志（最近 10 分钟）
❌ 不要：只依赖会被压缩的对话历史

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

README 和指南可以这样写：
> 「这套工作流是为 Emory University 的 Econ 730 开发的……」

只要明确说明这是一个例子，而不是必需条件即可。

### CODEBUDDY.md 可以有占位符

模板 CODEBUDDY.md 中使用 `[YOUR PROJECT NAME]`、`[YOUR INSTITUTION]` 是正确的，由用户自行填写。

### 文档可以引用最初的使用场景

真实例子具有教学价值：
> 「案例研究：6 次课、800+ 张幻灯片、Beamer + Quarto + R 复现」

这里展示的是可以实现什么，而不是要求用户必须这样做。

---

## 修订流程

随着本仓库演进，元治理规则也可能需要更新。

**何时修订本文件：**
- 我们找到更好的方法来区分通用内容与特定内容
- 跨机器工作流发生变化，例如 WorkBuddy 增加云同步
- 记忆系统发生演进，例如支持自动提取 [LEARN]
- 用户反馈表明，大家仍然混淆「模板与在用项目」

**修订步骤：**
1. 在会话日志或计划中提出改动
2. 讨论影响：什么会坏？什么会变好？
3. 更新本文件
4. 在 MEMORY.md 中用 [LEARN:meta-governance] 条目记录这次改动

---

## 速查表

| 内容类型 | 提交进仓库？ | 放在哪里 | 跨机器同步？ |
|--------------|----------------|---------------|----------------------|
| 工作流模式（通用） | ✅ 是 | MEMORY.md | ✅ 是（通过 git） |
| 机器相关设置 | ❌ 否 | 原生自动记忆（`~/.workbuddy/projects/<project>/memory/`） | ❌ 否（本机存放） |
| 本仓库按日工作日志与本机状态 | ❌ 否（已 gitignore，保留本机） | `.workbuddy/memory/` | ❌ 否 |
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

**本仓库有两类用途：**
1. Sellyew 在这里维护和使用中文移植，记录移植决策，本机状态则留在本机
2. 他人可以 fork 公开模板，获得通用、面向框架且稳定的基础设施

**处理方法：**
- 把能帮助所有人的通用模式提交到 MEMORY.md、模板和基础设施
- 把机器和用户经验保存在用户级原生自动记忆，把本仓库的按日工作日志与本机状态保存在已 gitignore 的 `.workbuddy/memory/`
- 按自己的工作流执行：计划先行、任务要求先于计划、质量门禁
- 写文档时选用多个领域的例子，不只重复上游原项目的用例
- 每季度复查一次，把通用模式提升上来，并细化特定内容

**拿不准时，就问：**「一个 fork 本仓库来制定实验室规程的生物学博士生，会从这条知识中受益吗？」如果会，就经人工筛选后写入根目录 `MEMORY.md`。如果属于机器或用户经验，就写入原生自动记忆；如果记录的是本仓库的工作过程，就写入 `.workbuddy/memory/`。
