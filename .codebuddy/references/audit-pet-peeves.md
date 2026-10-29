# 审查洁癖清单 —— 审查机器人抓到、而我们的深度审计一直漏掉的那几类缺陷

**目的。** 一份持续生长的漂移模式目录，收录 Copilot / Codex / 人类审阅者在近期 PR 上标出过的问题。深度审计代理把它读作额外的提示词上下文，从而继承过去若干轮积累下来的知识。

**原则。** 审读中我们见到的每一类缺陷 = 一条条目。让文件生长，不要重写它。机械检查（在 `scripts/check-skill-integrity.py` 里）堵住明显的洞；本文件堵住那些需要判断的更隐蔽的洞。

**怎么用。** 写深度审计代理的提示词时，说「读 `.codebuddy/references/audit-pet-peeves.md`，报告干净之前逐类显式检查一遍」。分诊一条 Copilot/Codex 的发现时，判断：这是新的一类（加条目），还是已有类别的重现（给证据清单加一条）？

---

## 1. Frontmatter ↔ 正文的工具一致性（`allowed-tools` 里缺 `Task`）

**例子：** PR #92。`/lit-review`、`/research-ideation`、`/respond-to-referees`、`/interview-me` 各自在正文里写了「用 `Agent` 工具以 `context=fork` 派生 `claim-verifier`」，但没有一个在 `allowed-tools` 里有 `Task`。Codex + Copilot 都抓到了；深度审计漏了。

**怎么抓。** 已由 `scripts/check-skill-integrity.py` 自动化（检查 1：`Agent` 派生模式，`Task` 作为遗留别名保留）。对其他工具（Edit、Write、MultiEdit、NotebookEdit），脚本有更窄的模式。WebSearch / WebFetch / Read / Grep / Glob / Bash 是有意排除的——散文里的误报太多。

**深度审计为什么漏了。** 3 号代理的提示词写的是「allowed-tools 的取值合理」——没有对着正文里的调用做交叉核对。

**何时适用。** 任何新技能，或任何会派生子代理的改动过的技能。当某个技能新增一节正文、调用了它此前没用的工具时，也会触发。

---

## 2. `argument-hint` ↔ 正文旗标一致性

**例子：** PR #92（Copilot）。技能在正文里加了 `--no-verify` 这个退出开关，却没在 `argument-hint` 里公布。用户从那一行提示里不会发现这个有文档记录的退出开关。

**怎么抓。** 已由 `scripts/check-skill-integrity.py` 自动化（检查 2）。它在（a）markdown 表格首格、（b）列表项、（c）带明确退出措辞的行里检测旗标。会漏掉自由散文式的旗标描述——这是有意的；散文里提一句并不代表存在一个真正支持的选项。

**深度审计为什么漏了。** 没人把 `argument-hint` 当作一块覆盖面来看。

**何时适用。** 只要正文里写了 `--flag foo` 这种话。

---

## 3. 断掉的内链 markdown 锚点

**例子：** PR #87。`r-code-conventions.md` 链接到 `r-reviewer.md#category-11-numerical-discipline`，但实际标题是 `### 11. NUMERICAL DISCIPLINE` → GitHub 锚点是 `11-numerical-discipline`。Copilot 抓到了。

**怎么抓。** 已由 `scripts/check-skill-integrity.py` 自动化（检查 3）。对每个 `[text](path#anchor)` 链接，解析 `path`，把 `anchor` 与目标文件里每个标题按 GitHub 风格 markdown 规则算出的锚点逐一比对。

**深度审计为什么漏了。** 1 号代理检查了「交叉引用与锚点都能解析」，但并没有真的实现「标题 → 锚点」的转换。

**何时适用。** 改文档时永远适用。尤其是重命名标题之后（`## Foo Bar` → `## Foo Baz` 会改变锚点）。

---

## 4. 文档里承诺了却没实现的旗标

**例子：** PR #87。`beamer-quarto-sync.md` 建议运行 `/translate-to-quarto --diff [file]`，但该技能没有 `--diff` 选项。`cross-artifact-review.md` 提到 `--with-scripts`，同样不存在。两处都是 Copilot 抓到的。

**怎么抓。** 更难自动化——脚本得解析每个技能的参数解析，再与任何规则或其他技能里提到的每一个旗标比对。目前：写一份提到某技能旗标的文档时，去 grep 该技能的 SKILL.md 与 argument-hint，确认这个旗标真的存在。

**深度审计为什么漏了。** 跨文件的旗标引用超出了 3 号代理逐文件的范围。

**何时适用。** 当某条规则或另一个技能引用了某个技能的旗标时（例如「把 `--foo` 传给 `/skill-name`」）。去 grep 目标技能的 argument-hint 与正文找这个旗标。

---

## 5. 过期的 docstring 与代码行为不符

**例子：** PR #87。`.codebuddy/hooks/log-reminder.py` 的 docstring 说「阻止 Claude 停止」，但代码已被改写成只往 stderr 写提示。Copilot 抓到了。

**怎么抓。** 难以机械化。找出 docstring 里的关键行为断言（blocks、fails、exits、returns），与真实的代码控制流交叉核对。改变一个函数的行为时，永远重读它的 docstring。

**深度审计为什么漏了。** 2 号代理专注钩子退出码与 import；没有把 docstring 与行为比对过。

**何时适用。** 任何改动过钩子退出路径、或函数返回／副作用行为之后。

---

## 6. 规则 ↔ 技能实现一致性

**例子：** PR #92。`post-flight-verification.md` 在它的 `paths:` 里列了 `/interview-me`，声称该技能会跑落地后检查。但 `/interview-me/SKILL.md` 没有落地后检查这一节——规则与实现之间静默漂移。

**怎么抓。** 已由 `scripts/check-skill-integrity.py` 自动化（检查 4）。对每条规则，有一张关键词映射表声明技能正文必须包含哪些关键词（例如 `post-flight-verification.md` → 正文必须提到 `claim-verifier` 或 `Post-Flight`）。每发布一条新规则就更新这张映射表。

**深度审计为什么漏了。** 3 号代理检查了「规则的 paths: 引用了存在的目录」，但没检查那些路径下的技能是否真的实现了该规则。

**何时适用。** 每当某条规则扩大它的 `paths:`，或有技能被加入某条规则的范围时。

---

## 7. 枚举式总结段落与正文漂移（打地鼠）

**例子：** PR #88–#90。每次 Copilot 标出 v1.6.1 CHANGELOG 开头的一句话（「无新技能、规则、钩子」→「无新目录」→「27/22/13/6」→「枚举里没有代理」），那处外科手术式的修补就在同一段的别处引入了新的漂移。打了三轮补丁，还是同一段。

**怎么抓。** 不是机械的——这是一个判断模式。规则 `.codebuddy/rules/summary-parity.md` 把编码了它：同一段总结被抓到两次 = 从结构上重写（往上抽象），不要打补丁。

**深度审计为什么漏了。** 枚举式总结在每一个版本上都是「技术上正确」的——漂移发生在总结与正文之间、跨时间。

**何时适用。** CHANGELOG 导语、README 标语、PR 的 `## Summary` 块、技能／规则／代理 frontmatter 的 `description:` 字段、指南章节摘要、MEMORY.md 的 `[LEARN]` 标题行。

---

## 8. 非规范顺序的计数简写

**例子：** PR #89。我写了 `27/22/13/6`，把规范约定（`27 skills / 13 agents / 22 rules / 6 hooks`——代理在规则之前）的顺序打乱了，还丢了标签。Copilot 抓到了。

**怎么抓。** 只用带标签的规范形式 `N skills / M agents / K rules / L hooks`。避免 `27/13/22/6` 这种裸数字简写——只要有人重排一次，它们就漂移一次。

**深度审计为什么漏了。** 表面同步检查的是计数与磁盘一致，不是措辞是否规范。

**何时适用。** 任何提到全部四个计数的总结。只提单个计数时，有标签就够。

---

## 9. 代理 ↔ 技能范围自相矛盾

**例子：** PR #87。`domain-reviewer.md` 的范围说明写「用于讲义幻灯片，不用于稿件」，却又把 `/seven-pass-review`（一个稿件技能）列为使用者。内部自相矛盾。Copilot 抓到了。

**怎么抓。** 给代理文件加范围说明时，逐个核对列出的使用者技能，确认这个范围断言在它们身上都成立。如果一个多产物代理把自己描述成「单产物」，那就是这个缺陷。

**深度审计为什么漏了。** 3 号代理检查了文件存在，但没检查交叉引用的语义一致性。

**何时适用。** 代理文件上的范围说明。当某个技能的描述声称排他性（「只用于幻灯片」）却同时被面向稿件的调用方使用时，也适用。

---

## 10. 把不是守护进程的模式说成守护进程

**例子：** PR #87。`TROUBLESHOOTING.md` 写「走一遍 orchestrator」，好像 orchestrator 是一个你可以调用的运行时服务。但 orchestrator 是具体技能实现的一个*模式*——不是守护进程。我们刚为 v1.6.1 重写过这个说法，Copilot 又标了出来。

**怎么抓。** grep 文档里那些用在非守护进程对象上的、像守护进程的动词：「invoke the X」「X activates when」「X runs after Y」。当「X」是模式／规则／协议时，这些说法是错的。当「X」是钩子／服务／技能时，它们可能正确。

**深度审计为什么漏了。** 框架诚实性审计能抓住大部分，但会漏掉文件级 TROUBLESHOOTING 章节里零散的守护进程措辞。

**何时适用。** 任何描述 orchestrator、协议或模式的地方。尤其是重构措辞之后（例如 v1.6.1 的「orchestrator 是模式，不是守护进程」）。

---

## 11. 表面同步正则之外的过期散文计数

**例子：** PR #92 第 1 轮。README.md 与指南里有四处写「13 个专项代理」／「13 个聚焦代理」／「由 13 个专项代理审读」，即使计数已经变成 14。表面同步没抓到，因为它的正则只匹配规范的 `N agents, M skills, K rules, L hooks` 形式。机器人把四处全抓到了。

**怎么抓。** 用旧计数去 grep 一切修饰语境：`N specialized`、`N focused`、`reviewed by N`、`template's N`。也可以考虑扩宽表面同步去匹配更多措辞——但要当心无关数字的误报。

**深度审计为什么漏了。** 1 号代理的「计数与现实一致」检查依赖表面同步。

**何时适用。** 任何计数变化。对整个仓库树 grep **旧**值，而不只是规范措辞。

---

## 12. 历史 CHANGELOG 条目——**不要**更新

**例子：** 大多数 PR。过去版本标题下的 CHANGELOG 条目是那个版本发布时的快照。计数变化时**不**应更新它们。一个审计代理说 v1.5.x 条目「CHANGELOG 第 122 行的计数 22 过期了」是错的——那个版本发布时就是 22 条规则，记录必须如实反映。

**怎么抓。** 当表面同步脚本或审计代理标出 CHANGELOG.md 里的某个计数时，看它上面的版本标题。如果标题是过去的版本，那就是历史快照——跳过。

**深度审计为什么漏了。** 代理有时分不清「当前表面」与「历史记录」。

**何时适用。** CHANGELOG 审计。

---

---

## 13. docstring 契约 ↔ 实现漂移

**例子：** PR #93（Copilot + Codex）。`check-skill-integrity.py` 的 docstring 把旗标一致性描述成「argument-hint ↔ 正文旗标一致性……反之亦然」，但实现只报告了正文→提示这一个方向。两个机器人各自独立标出。另一个独立例子：退出码 docstring 说「1 = P0 失败」，但代码在 P0 或 P1 时都返回 1。

**怎么抓。** 读一个函数的 docstring 时，把每一条行为断言抽出来（双向、fail-open、在 X 时退出 1、当 Z 时返回 Y），核实实现与之一致。契约会以省略的方式说谎：如果 docstring 说「X……反之亦然」，代码就必须真的两个方向都做。

**深度审计为什么漏了。** 2 号代理原本的范围只有 `.codebuddy/hooks/`。`scripts/` 里的新代码完全绕过了审计。即使范围正确，「docstring 声称 X 而代码做 Y」也是需要把两边都仔细读的一类——扫读时很容易漏。

**何时适用。** 任何 docstring 带有行为断言的函数或脚本。对即将作为审计基础设施本身发布的代码尤其关键——这里的 bug 会瓦解这段代码本该检查的一切。

---

## 14. 被窄 `except` 破坏的 Python fail-open 承诺

**例子：** PR #93（Copilot）。`check-skill-integrity.py` 承诺「解析器出错时 fail-open：损坏／无法解析的文件打印一条 P2 警告，但不让构建失败」。实现只在 `read_text()` 上捕获了 `OSError`——`UnicodeDecodeError` 会冒到 `main()` 顶层的 `except Exception` 并退出 2，与 docstring 相反地让门禁失败。

**怎么抓。** 当一个 Python 脚本记录 fail-open 行为时，检查每个 `read_text()` / `open()` / `json.loads()` 是否捕获了现实的失败模式（`OSError`、`UnicodeError`、`json.JSONDecodeError`）。更好的做法：显式写 `encoding="utf-8"`，并一起捕获 `(OSError, UnicodeError)`。

**深度审计为什么漏了。** 范围缺口（scripts/）加上没有对编码错误处理做显式检查。

**何时适用。** 任何读文件并声称 fail-open 行为的 Python 脚本。尤其是审计／门禁脚本——那里一次假的硬失败会挡住提交。

---

## 15. Bash 的 `set -u` 抓不住命令失败

**例子：** PR #93（Copilot）。`check-surface-sync.sh` 用了 `set -u`（未设变量视为错误），但没用 `set -e`（命令失败即退出）。如果 `SCRIPT_DIR="$(cd ... && pwd)"` 这条命令失败了（例如脚本被移动、`cd` 出错），`SCRIPT_DIR` 会是空的，后续 `python "$SCRIPT_DIR/..."` 调用就会带着一个假路径去跑。

**怎么抓。** 在 bash 脚本里，`set -u` 只防未设变量，**不**防命令失败。如果你不能用 `set -e`（因为你希望后续命令在先前命令失败时仍然运行——例如顺序跑两个门禁、两个输出都要），那你必须在每条关键命令之后显式检查返回码，或用 `|| { ...; exit 2; }`。

**深度审计为什么漏了。** 范围缺口（scripts/）加上 2 号代理以钩子为中心的检查，除退出码协议外不覆盖 bash 安全惯用法。

**何时适用。** 任何做路径解析、变量推导或顺序命令分发的 bash 脚本。尤其当脚本作为 git 钩子或提交门禁运行时。

---

## 16. 误导维护者的死配置映射条目

**例子：** PR #93（Copilot）。`check-skill-integrity.py` 里有针对 `cross-artifact-review.md` 与 `content-invariants.md` 的 `RULE_KEYWORDS` 条目，但两条规则的范围 frontmatter（其中一条当时用的是 Cursor 风格的 `globs:` 键，两者都指向 `.tex`/`.qmd` 文件而非 `.codebuddy/skills/*`）实际上都不会触发这项检查。这些条目是空转的。将来读代码的维护者会理所当然地以为这项检查在考这些规则。

**怎么抓。** 往配置映射、关键词字典或注册表里加条目时，核实至少有一条执行路径真的能到达这个条目。死条目会原地腐烂——它们比省略更糟，因为它们暗示了一种并不存在的覆盖。

**深度审计为什么漏了。** 没有「配置条目能到达其指涉对象」的检查。范围缺口让它更严重。

**何时适用。** 编辑任何带 `{key: config}` 映射、路径模式清单或规则引用注册表的文件时。做一次快速追踪：给定这个输入，条目会被用到吗？不会的话，删掉它，或写明为什么把它搁置。

---

## 17. 用 `CronCreate` 做长延时的自主工作

**例子：** 2026-04-16。用户的用量即将被限流，而他们需要自主工作在约 1 小时后触发。我们用了带 `durable: true` 的 `CronCreate`，但 cron 依附于 Claude Code REPL 自己的事件循环——会话一死（限流 + 用户离开 + VSCode 关掉面板），cron 跟着没了。计划还在磁盘上；定时触发器没有。用户回来时只能手动调用。

**怎么抓。** 任何时候你用 `CronCreate` 且延迟 > 10 分钟，问一句：「触发时 Claude Code 会话一定还在运行吗？」如果不是，换成 **Claude Code Routines**（2026 年 4 月 14 日发布）——它们跑在 Anthropic 的 web 基础设施上，不依赖本地 REPL。Routines 才是过夜工作、定时审计、用户不在时的自主运行的合适原语。`CronCreate` 用于活跃会话内的短延时轮询。

**深度审计为什么漏了。** 不是代码质量问题——是原语选择问题。加进洁癖清单，因为这类隐蔽的坑恰好在你承受不起的时候咬你（用户不在、会话正在死）。

**何时适用。** 任何调度决定。经验法则：分钟级用 `CronCreate`，小时级用 Routines。用户在盯着看时，两者都行；他们不在时，用 Routines。

---

## 18. 枚举表漂移（表面同步的盲区）

**例子：** v1.8.0 深度审计。导语计数说「30 个技能、14 个代理」，`check-surface-sync.py` 确认全部 26 条数字计数断言都与磁盘一致。但指南附录的「All Skills」表列了 28 行（缺 `/checkpoint` + `/preregister`），「All Agents」表列了 11 行（缺 v1.5.0 的同行评审三件套 editor / domain-referee / methods-referee——一个跨 3 个版本继承下来的既有漂移）。表面同步门禁对这一类视而不见，因为它是去找 `"30 skills, 14 agents"` 这样的措辞模式，而不是看枚举表里实际有没有 N 项。

**怎么抓。** 新增技能／代理／规则／钩子时，审计**所有**这些表面，而不只是计数措辞：
- `guide/workflow-guide.qmd` 的「All Skills」／「All Agents」／「All Rules」附录表（数行数 = 期望的 N）。
- `CODEBUDDY.md` 的「Skills Quick Reference」表（行数 = N）。
- `README.md` 的技能／代理表。
- `docs/index.html` 里逐一枚举技能的正文项目符号清单。
v2.0.0 已发布：`check-surface-sync.py` 的 TABLE-ROW 断言会校验带 `<!-- surface-sync-table: ... -->` 标记的表。不带标记的表（例如指南附录）对它仍然不可见——深度审计代理仍必须显式检查那些行数（v2.5 发布了 60 行附录里的 58 行，直到一次语义扫描才抓到）。

**深度审计为什么漏了（直到 v1.8.0）。** 1 号代理的提示词问的是计数，不是行数。4 号代理的提示词问的是各文档之间的功能计数是否一致，而不是枚举表列出的集合是否与计数断言相同。两个代理都看了导语计数（那些是对的）然后停了。

**何时适用。** 任何新增或删除技能／代理／规则／钩子的发布。表面同步干净 ≠ 枚举表是最新的。对附录表跑一次 `wc -l` 式的快速检查，对比 `ls .codebuddy/skills/ | wc -l`。

---

## 19. `Task` 之外的工具名一致性（推广洁癖 #1）

**例子：** v1.8.0 深度审计。两个技能（`/data-analysis`、`/audit-reproducibility`）的正文里新增了「使用 Monitor 工具」的指引，但没把 `Monitor` 加进 `allowed-tools`。这与 v1.7.0 里 PR #92 的 `Task` 一致性缺陷（洁癖 #1）是同一类，但换了个工具，所以 `check-skill-integrity.py` 的正则（专门找 `Task` 模式）没抓到。

**怎么抓。** 把一致性检查推广开：对技能正文里提到的**每一个**工具名（`Task`、`Bash`、`Edit`、`Write`、`Read`、`Grep`、`Glob`、`WebFetch`、`WebSearch`、`Monitor`、`NotebookEdit`、`TodoWrite` 等），核实它出现在 `allowed-tools` 里。脚本应当维护一份已知工具名清单，而不是只硬编码 `Task`。Anthropic 的新工具（2026 年第 15 周的 Monitor）发布得比审计脚本更快。

**深度审计为什么漏了（直到 v1.8.0）。** `check-skill-integrity.py` 第 0 阶段检查 1 只匹配一份固定的工具清单（`Agent`、遗留的 `Task`、`Edit`、`Write`、`MultiEdit`、`NotebookEdit`）；`Monitor` 不在其中。像「use the Monitor tool」这种正文读起来就是英文；脚本不会对它做模式匹配。审计 3 号代理的提示词现在也会显式检查非 `Agent` 的工具引用——但正确的修法是给机械脚本扩一份已知工具清单。

**何时适用。** 往正文里加对任何 Anthropic 发布工具的引用时，写正文的同时就把这个工具加进技能的 `allowed-tools` 数组。扩展 `check-skill-integrity.py` 时，只要 Anthropic 发布新的工具原语，就把新工具名加进一致性检查。

---

## 元 —— 本文件如何维护

- 任何一次「审查机器人抓到了深度审计漏掉的东西」的 PR 之后，追加一条新条目（或用新证据扩展现有条目）。
- 当某条目的类别已被 `scripts/check-skill-integrity.py` 或其他机械检查自动化时，注明它——但条目要保留，它对审阅者仍是有用的上下文。
- 目标 ≤ 20 条；如果到了 25 条，复查并合并相关类别，或把已解决的归档到一个 `_resolved.md` 兄弟文件。
- 从 `.codebuddy/skills/deep-audit/references/repo-infrastructure-audit.md`（启动 4 个审计代理的那一步）引用本文件，好让 4 个代理都加载它。
- 当某条具体教训与这里的一条条目相关时，从 MEMORY.md 的 `[LEARN:audit]` 条目链接过来。
